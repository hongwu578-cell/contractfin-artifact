from __future__ import annotations

import copy
import re
from typing import Any


_LEGACY_TEXT_ID = re.compile(r"^(pre|post)_(\d+)$")


def migrate_legacy_finqa_evidence_id(
    evidence_id: str,
    *,
    pre_text_count: int,
    post_text_count: int,
) -> tuple[str, bool]:
    """Map prompt-local FinQA text labels to the dataset's official text_N labels."""
    match = _LEGACY_TEXT_ID.fullmatch(evidence_id)
    if match is None:
        return evidence_id, False
    section, raw_index = match.groups()
    index = int(raw_index)
    section_count = pre_text_count if section == "pre" else post_text_count
    if index >= section_count:
        raise ValueError(
            f"legacy evidence id {evidence_id!r} is outside the {section} section "
            f"(count={section_count})"
        )
    official_index = index if section == "pre" else pre_text_count + index
    return f"text_{official_index}", True


def migrate_prediction_evidence_ids(
    prediction: dict[str, Any], sample: dict[str, Any]
) -> tuple[dict[str, Any], int]:
    """Return a copied prediction with only legacy evidence identifiers migrated."""
    documents = sample.get("documents") or []
    if len(documents) != 1:
        raise ValueError("legacy B0 evidence migration requires exactly one FinQA document")
    document = documents[0]
    pre_count = len(document.get("pre_text", []))
    post_count = len(document.get("post_text", []))
    migrated = copy.deepcopy(prediction)
    changed = 0
    evidence_items: list[Any] = []
    for item in migrated.get("evidence", []):
        if isinstance(item, str):
            mapped, did_change = migrate_legacy_finqa_evidence_id(
                item,
                pre_text_count=pre_count,
                post_text_count=post_count,
            )
            evidence_items.append(mapped)
            changed += did_change
            continue
        if isinstance(item, dict):
            copied = dict(item)
            key = "id" if "id" in copied else "evidence_id" if "evidence_id" in copied else None
            if key is not None and isinstance(copied[key], str):
                copied[key], did_change = migrate_legacy_finqa_evidence_id(
                    copied[key],
                    pre_text_count=pre_count,
                    post_text_count=post_count,
                )
                changed += did_change
            evidence_items.append(copied)
            continue
        evidence_items.append(item)
    migrated["evidence"] = evidence_items
    metadata = migrated.setdefault("metadata", {})
    metadata["evidence_id_migration"] = "legacy_pre_post_to_official_text_v1"
    return migrated, changed
