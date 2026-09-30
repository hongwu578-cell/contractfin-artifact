#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.evaluation import evaluate_files  # noqa: E402
from contractfin.evidence_ids import migrate_prediction_evidence_ids  # noqa: E402
from contractfin.utils import read_jsonl, sha256_file, write_json, write_jsonl  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministically migrate legacy B0 FinQA text evidence IDs and rescore"
    )
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--source-stem", default="b0_deepseek_preregistered30_v1_2"
    )
    parser.add_argument(
        "--destination-suffix", default="evidence_ids_v2"
    )
    args = parser.parse_args()
    root = args.root.resolve()
    reports = root / "reports"
    source_gold = reports / f"{args.source_stem}_gold.jsonl"
    source_predictions = reports / f"{args.source_stem}_predictions.jsonl"
    source_report = reports / f"{args.source_stem}_report.json"
    destination_predictions = reports / (
        f"{args.source_stem}_predictions_{args.destination_suffix}.jsonl"
    )
    destination_report = reports / (
        f"{args.source_stem}_report_{args.destination_suffix}.json"
    )
    audit_path = reports / f"{args.source_stem}_{args.destination_suffix}_migration.json"
    outputs = (destination_predictions, destination_report, audit_path)
    existing = [path for path in outputs if path.exists()]
    if existing:
        raise FileExistsError(
            "refusing to overwrite migration artifacts: "
            + ", ".join(str(path) for path in existing)
        )

    gold_rows = list(read_jsonl(source_gold))
    samples = {row["sample_id"]: row for row in gold_rows}
    predictions = list(read_jsonl(source_predictions))
    migrated_predictions: list[dict[str, Any]] = []
    changed_items = 0
    changed_samples = 0
    changes: list[dict[str, Any]] = []
    for prediction in predictions:
        sample_id = prediction["sample_id"]
        if sample_id not in samples:
            raise ValueError(f"prediction has no matching gold sample: {sample_id}")
        migrated, count = migrate_prediction_evidence_ids(prediction, samples[sample_id])
        migrated_predictions.append(migrated)
        changed_items += count
        changed_samples += count > 0
        if count:
            changes.append(
                {
                    "sample_id": sample_id,
                    "before": prediction.get("evidence", []),
                    "after": migrated.get("evidence", []),
                    "changed_items": count,
                }
            )

    write_jsonl(destination_predictions, migrated_predictions)
    corrected = evaluate_files(source_gold, destination_predictions, destination_report)
    original = json.loads(source_report.read_text(encoding="utf-8"))
    invariant_metrics = (
        "coverage",
        "final_answer_accuracy",
        "selective_accuracy",
        "schema_valid_rate",
        "program_accuracy",
        "execution_accuracy",
        "execution_coverage",
        "unit_scale_error_rate",
        "unsupported_claim_rate",
    )
    for metric in invariant_metrics:
        if corrected["summary"].get(metric) != original["summary"].get(metric):
            raise RuntimeError(f"non-evidence metric changed during migration: {metric}")

    audit = {
        "schema_version": "1.0",
        "migration": "legacy_pre_post_to_official_text_v1",
        "classification": "deterministic_identifier_correction_no_model_rerun",
        "source_artifacts": {
            "gold": str(source_gold),
            "gold_sha256": sha256_file(source_gold),
            "predictions": str(source_predictions),
            "predictions_sha256": sha256_file(source_predictions),
            "report": str(source_report),
            "report_sha256": sha256_file(source_report),
        },
        "derived_artifacts": {
            "predictions": str(destination_predictions),
            "predictions_sha256": sha256_file(destination_predictions),
            "report": str(destination_report),
            "report_sha256": sha256_file(destination_report),
        },
        "counts": {
            "predictions": len(predictions),
            "changed_samples": changed_samples,
            "changed_evidence_items": changed_items,
        },
        "metric_comparison": {
            "original": original["summary"],
            "corrected": corrected["summary"],
        },
        "non_evidence_metrics_unchanged": True,
        "changes": changes,
    }
    write_json(audit_path, audit)
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
