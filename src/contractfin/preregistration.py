from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

from .utils import read_jsonl, sha256_file


PROTOCOL_ID = "contractfin-b0-finqa-dev30-v1"
REGISTRATION_DATE = "2026-09-28"

DEFAULT_B0_DEV_QUOTAS: dict[str, int] = {
    "single_divide": 5,
    "single_subtract": 4,
    "single_add": 2,
    "single_multiply": 2,
    "table_average": 2,
    "table_sum": 1,
    "table_max": 1,
    "table_min": 1,
    "comparison": 2,
    "contains_exp": 1,
    "multi_2_step": 4,
    "multi_3_step": 2,
    "multi_4_step": 1,
    "multi_5_step": 2,
}

PRIOR_GATE_EXCLUSIONS: dict[str, str] = {
    "finqa:dev:V/2008/page_17.pdf-1": (
        "Used for the authorized one-item DeepSeek interface gate before preregistration."
    )
}

_ARITHMETIC_OPERATIONS = {"add", "subtract", "multiply", "divide"}
_TABLE_OPERATIONS = {"table_average", "table_sum", "table_max", "table_min"}
_OPERATION_PATTERN = re.compile(r"([A-Za-z_]+)\(")


def operation_sequence(program: Any) -> tuple[str, ...]:
    if not isinstance(program, str) or not program.strip():
        raise ValueError("sample has no FinQA program")
    operations = tuple(item.casefold() for item in _OPERATION_PATTERN.findall(program))
    if not operations:
        raise ValueError(f"could not parse FinQA operations from: {program}")
    return operations


def classify_operations(operations: tuple[str, ...]) -> str:
    if "exp" in operations:
        return "contains_exp"
    if "greater" in operations:
        return "comparison"
    table_operations = [item for item in operations if item in _TABLE_OPERATIONS]
    if table_operations:
        return table_operations[0]
    if len(operations) == 1 and operations[0] in _ARITHMETIC_OPERATIONS:
        return f"single_{operations[0]}"
    if 2 <= len(operations) <= 5 and set(operations) <= _ARITHMETIC_OPERATIONS:
        return f"multi_{len(operations)}_step"
    raise ValueError(f"unsupported operation sequence: {operations}")


def _rank_hash(namespace: str, protocol_id: str, dataset_sha256: str, sample_id: str) -> str:
    material = f"{namespace}|{protocol_id}|{dataset_sha256}|{sample_id}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def build_preregistration_manifest(
    samples: Iterable[dict[str, Any]],
    *,
    dataset_sha256: str,
    quotas: Mapping[str, int] = DEFAULT_B0_DEV_QUOTAS,
    exclusions: Mapping[str, str] = PRIOR_GATE_EXCLUSIONS,
    protocol_id: str = PROTOCOL_ID,
) -> dict[str, Any]:
    rows = list(samples)
    by_stratum: dict[str, list[dict[str, Any]]] = {name: [] for name in quotas}
    source_positions: dict[str, int] = {}
    excluded_rows: list[dict[str, Any]] = []

    for source_position, sample in enumerate(rows, start=1):
        sample_id = str(sample.get("sample_id", ""))
        if not sample_id:
            raise ValueError(f"source position {source_position} has no sample_id")
        if sample_id in source_positions:
            raise ValueError(f"duplicate sample_id: {sample_id}")
        source_positions[sample_id] = source_position
        if sample_id in exclusions:
            excluded_rows.append(
                {
                    "sample_id": sample_id,
                    "source_position": source_position,
                    "reason": exclusions[sample_id],
                }
            )
            continue
        operations = operation_sequence(sample.get("gold_program"))
        stratum = classify_operations(operations)
        if stratum not in by_stratum:
            raise ValueError(f"no quota registered for stratum {stratum}")
        by_stratum[stratum].append(
            {
                "sample": sample,
                "source_position": source_position,
                "operations": operations,
                "selection_hash": _rank_hash(
                    "selection", protocol_id, dataset_sha256, sample_id
                ),
            }
        )

    selected: list[dict[str, Any]] = []
    pool_counts: dict[str, int] = {}
    for stratum, quota in quotas.items():
        if quota < 0:
            raise ValueError(f"quota for {stratum} must not be negative")
        pool = sorted(
            by_stratum[stratum],
            key=lambda item: (item["selection_hash"], item["sample"]["sample_id"]),
        )
        pool_counts[stratum] = len(pool)
        if len(pool) < quota:
            raise ValueError(
                f"stratum {stratum} requires {quota} samples but only {len(pool)} are eligible"
            )
        for stratum_rank, item in enumerate(pool[:quota], start=1):
            sample = item["sample"]
            sample_id = sample["sample_id"]
            document = sample["documents"][0]
            selected.append(
                {
                    "sample_id": sample_id,
                    "source_position": item["source_position"],
                    "stratum": stratum,
                    "stratum_rank": stratum_rank,
                    "selection_hash": item["selection_hash"],
                    "execution_order_hash": _rank_hash(
                        "execution", protocol_id, dataset_sha256, sample_id
                    ),
                    "operation_sequence": list(item["operations"]),
                    "step_count": len(item["operations"]),
                    "gold_evidence_count": len(sample.get("gold_evidence", [])),
                    "document_id": document.get("document_id"),
                    "question": sample["question"],
                }
            )

    selected.sort(key=lambda item: (item["execution_order_hash"], item["sample_id"]))
    for run_order, item in enumerate(selected, start=1):
        item["run_order"] = run_order

    requested_count = sum(quotas.values())
    if len(selected) != requested_count:
        raise AssertionError("selected sample count does not match registered quotas")
    return {
        "schema_version": "1.0",
        "protocol_id": protocol_id,
        "registration_date": REGISTRATION_DATE,
        "purpose": "coverage-oriented FinQA development smoke test",
        "reportable_performance_estimate": False,
        "source": {
            "dataset": "FinQA",
            "split": "dev",
            "record_count": len(rows),
            "normalized_file_sha256": dataset_sha256,
        },
        "selection_rule": {
            "method": "quota-stratified deterministic SHA-256 ranking",
            "selection_rank_material": (
                "selection|{protocol_id}|{normalized_file_sha256}|{sample_id}"
            ),
            "execution_order_material": (
                "execution|{protocol_id}|{normalized_file_sha256}|{sample_id}"
            ),
            "quotas": dict(quotas),
            "eligible_pool_counts": pool_counts,
            "selected_count": requested_count,
            "notes": [
                "Gold programs are used only to assign coverage strata and are never placed in prompts.",
                "The prior one-item interface-gate sample is excluded.",
                "No sample may be substituted after registration.",
                "Individual item errors must not trigger prompt or evaluator tuning.",
            ],
        },
        "exclusions": excluded_rows,
        "selected_stratum_counts": dict(Counter(item["stratum"] for item in selected)),
        "samples": selected,
    }


def load_preregistered_samples(
    dataset_path: Path, manifest_path: Path
) -> list[dict[str, Any]]:
    with manifest_path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    expected_hash = manifest.get("source", {}).get("normalized_file_sha256")
    actual_hash = sha256_file(dataset_path)
    if expected_hash != actual_hash:
        raise ValueError(
            "normalized dataset hash does not match the preregistration manifest"
        )
    all_samples = list(read_jsonl(dataset_path))
    by_id = {item["sample_id"]: item for item in all_samples}
    registered = sorted(manifest.get("samples", []), key=lambda item: item["run_order"])
    sample_ids = [item["sample_id"] for item in registered]
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("preregistration manifest contains duplicate sample IDs")
    missing = [sample_id for sample_id in sample_ids if sample_id not in by_id]
    if missing:
        raise ValueError(f"registered sample IDs are missing from the dataset: {missing}")
    expected_count = manifest.get("selection_rule", {}).get("selected_count")
    if expected_count != len(sample_ids):
        raise ValueError("preregistration manifest sample count is inconsistent")
    return [by_id[sample_id] for sample_id in sample_ids]


def render_manifest_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# B0 FinQA development-set 30-item preregistration",
        "",
        f"- Protocol: `{manifest['protocol_id']}`",
        f"- Registration date: `{manifest['registration_date']}`",
        f"- Dataset SHA-256: `{manifest['source']['normalized_file_sha256']}`",
        f"- Selected items: `{manifest['selection_rule']['selected_count']}`",
        "- Purpose: coverage-oriented interface and pipeline smoke test; not a performance estimate.",
        "- Frozen rule: no sample substitution and no item-specific prompt/evaluator tuning.",
        "",
        "## Registered allocation",
        "",
        "| Stratum | Eligible | Selected |",
        "|---|---:|---:|",
    ]
    quotas = manifest["selection_rule"]["quotas"]
    pools = manifest["selection_rule"]["eligible_pool_counts"]
    for stratum, quota in quotas.items():
        lines.append(f"| `{stratum}` | {pools[stratum]} | {quota} |")
    lines.extend(
        [
            "",
            "## Frozen execution list",
            "",
            "Gold answers and full gold programs are deliberately omitted from this review file.",
            "",
            "| Order | Sample ID | Stratum | Steps | Evidence | Question |",
            "|---:|---|---|---:|---:|---|",
        ]
    )
    for item in manifest["samples"]:
        question = str(item["question"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {item['run_order']} | `{item['sample_id']}` | `{item['stratum']}` | "
            f"{item['step_count']} | {item['gold_evidence_count']} | {question} |"
        )
    lines.extend(
        [
            "",
            "## Prior gate exclusion",
            "",
            "| Sample ID | Source position | Reason |",
            "|---|---:|---|",
        ]
    )
    for item in manifest["exclusions"]:
        lines.append(
            f"| `{item['sample_id']}` | {item['source_position']} | {item['reason']} |"
        )
    return "\n".join(lines) + "\n"
