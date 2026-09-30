#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.preregistration import load_preregistered_samples  # noqa: E402
from contractfin.retrieval import search_sample  # noqa: E402
from contractfin.utils import read_jsonl, write_json  # noqa: E402


def audit(rows: list[dict[str, Any]], top_k: int) -> dict[str, Any]:
    evidence_hits = 0
    evidence_total = 0
    fully_covered = 0
    macro_recall = 0.0
    for row in rows:
        gold = {
            str(item["id"])
            for item in row.get("gold_evidence", [])
            if item.get("id") is not None
        }
        retrieved = {
            item["label"] for item in search_sample(row, row["question"], top_k=top_k)
        }
        hits = len(gold & retrieved)
        evidence_hits += hits
        evidence_total += len(gold)
        fully_covered += gold <= retrieved
        macro_recall += hits / len(gold) if gold else 1.0
    count = len(rows)
    return {
        "samples": count,
        "top_k": top_k,
        "gold_evidence_items": evidence_total,
        "retrieved_gold_items": evidence_hits,
        "micro_recall": evidence_hits / evidence_total if evidence_total else 0.0,
        "macro_recall": macro_recall / count if count else 0.0,
        "full_gold_coverage": fully_covered / count if count else 0.0,
    }


def text_label_mapping(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = 0
    matched = 0
    for row in rows:
        document = row["documents"][0]
        merged = [str(item) for item in document.get("pre_text", [])] + [
            str(item) for item in document.get("post_text", [])
        ]
        for evidence in row.get("gold_evidence", []):
            evidence_id = str(evidence.get("id", ""))
            if not evidence_id.startswith("text_"):
                continue
            total += 1
            index = int(evidence_id.split("_", 1)[1])
            expected = " ".join(str(evidence.get("text", "")).casefold().split())
            actual = " ".join(merged[index].casefold().split()) if index < len(merged) else ""
            matched += actual == expected
    return {
        "text_evidence_items": total,
        "matched_items": matched,
        "match_rate": matched / total if total else 0.0,
    }


def main() -> int:
    root = PROJECT_ROOT
    dataset_path = root / "data" / "normalized" / "finqa_dev.jsonl"
    manifest_path = root / "config" / "b0_finqa_dev_30_manifest.json"
    development = list(read_jsonl(dataset_path))
    registered = load_preregistered_samples(dataset_path, manifest_path)
    result = {
        "schema_version": "1.0",
        "mode": "development_retriever_audit",
        "warning": "Uses development gold evidence for aggregate audit only; never exposed to tools.",
        "text_label_mapping": text_label_mapping(development),
        "development": [audit(development, top_k) for top_k in (4, 8, 12)],
        "registered30": [audit(registered, top_k) for top_k in (4, 8, 12)],
    }
    selected = result["registered30"][-1]
    result["acceptance"] = {
        "default_top_k": 12,
        "minimum_registered30_micro_recall": 0.95,
        "minimum_registered30_full_gold_coverage": 0.95,
        "passed": (
            result["text_label_mapping"]["match_rate"] == 1.0
            and selected["micro_recall"] >= 0.95
            and selected["full_gold_coverage"] >= 0.95
        ),
    }
    write_json(root / "reports" / "b1_retriever_audit.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["acceptance"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
