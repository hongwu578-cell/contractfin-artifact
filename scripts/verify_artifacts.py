#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.models import UnifiedSample  # noqa: E402
from contractfin.run_logging import log_completeness  # noqa: E402
from contractfin.utils import read_jsonl, sha256_file, write_json  # noqa: E402


EXPECTED_COUNTS = {
    "finqa_train.jsonl": 6251,
    "finqa_dev.jsonl": 883,
    "finqa_test.jsonl": 1147,
    "financebench_open_source.jsonl": 150,
}


def main() -> int:
    root = PROJECT_ROOT
    checks: list[dict] = []
    manifest_path = root / "data" / "dataset_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for source in manifest["sources"]:
        for item in source["files"]:
            path = root / item["local_path"]
            actual_hash = sha256_file(path) if path.exists() else None
            checks.append(
                {
                    "check": "raw_file_hash",
                    "dataset": source["dataset"],
                    "path": item["local_path"],
                    "expected": item["sha256"],
                    "actual": actual_hash,
                    "passed": actual_hash == item["sha256"],
                }
            )

    all_ids: set[str] = set()
    evidence_items = 0
    located_evidence_items = 0
    for filename, expected_count in EXPECTED_COUNTS.items():
        path = root / "data" / "normalized" / filename
        count = 0
        validation_errors = 0
        duplicate_ids = 0
        for record in read_jsonl(path):
            count += 1
            sample = UnifiedSample.from_dict(record)
            validation_errors += bool(sample.validate())
            if sample.sample_id in all_ids:
                duplicate_ids += 1
            all_ids.add(sample.sample_id)
            if sample.dataset == "FinanceBench":
                for evidence in sample.gold_evidence:
                    evidence_items += 1
                    located_evidence_items += evidence.get("page") is not None
        checks.append(
            {
                "check": "normalized_dataset",
                "path": str(path.relative_to(root)),
                "expected_count": expected_count,
                "actual_count": count,
                "validation_errors": validation_errors,
                "duplicate_ids": duplicate_ids,
                "passed": count == expected_count and validation_errors == 0 and duplicate_ids == 0,
            }
        )

    evidence_coverage = located_evidence_items / evidence_items if evidence_items else 0.0
    checks.append(
        {
            "check": "financebench_evidence_page_coverage",
            "evidence_items": evidence_items,
            "located_items": located_evidence_items,
            "coverage": evidence_coverage,
            "passed": evidence_coverage >= 0.99,
        }
    )

    executor_report_path = root / "reports" / "finqa_executor_audit.json"
    executor_report = (
        json.loads(executor_report_path.read_text(encoding="utf-8"))
        if executor_report_path.exists()
        else {}
    )
    checks.append(
        {
            "check": "finqa_executor_audit",
            "execution_coverage": executor_report.get("execution_coverage", 0.0),
            "execution_accuracy": executor_report.get("execution_accuracy", 0.0),
            "passed": executor_report.get("passed") is True,
        }
    )

    log_path = root / "logs" / "infrastructure_smoke.jsonl"
    log_records = list(read_jsonl(log_path)) if log_path.exists() else []
    completeness = log_completeness(log_records)
    checks.append(
        {
            "check": "smoke_log_completeness",
            "records": len(log_records),
            "completeness": completeness,
            "passed": len(log_records) == 30 and completeness >= 0.99,
        }
    )

    result = {
        "schema_version": "1.0",
        "passed": all(check["passed"] for check in checks),
        "checks": checks,
    }
    write_json(root / "reports" / "artifact_verification.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
