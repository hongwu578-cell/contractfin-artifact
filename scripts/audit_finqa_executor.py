#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.program import execute_finqa_program, execution_values_match  # noqa: E402
from contractfin.utils import read_jsonl, write_json  # noqa: E402


def main() -> int:
    source = PROJECT_ROOT / "data" / "normalized" / "finqa_test.jsonl"
    failures: list[dict] = []
    total = 0
    executed = 0
    correct = 0
    for sample in read_jsonl(source):
        total += 1
        try:
            table = sample["documents"][0].get("table")
            result = execute_finqa_program(sample["gold_program"], table)
            executed += 1
            if execution_values_match(result.value, sample["gold_answer"]):
                correct += 1
            else:
                failures.append(
                    {
                        "sample_id": sample["sample_id"],
                        "kind": "value_mismatch",
                        "actual": result.value,
                        "expected": sample["gold_answer"],
                        "program": sample["gold_program"],
                    }
                )
        except ValueError as exc:
            failures.append(
                {
                    "sample_id": sample["sample_id"],
                    "kind": "execution_error",
                    "error": str(exc),
                    "program": sample["gold_program"],
                }
            )
    report = {
        "schema_version": "1.0",
        "dataset": "FinQA official public test",
        "total": total,
        "execution_coverage": executed / total if total else 0.0,
        "execution_accuracy": correct / total if total else 0.0,
        "failures": failures,
        "passed": total == 1147 and executed == total and correct == total,
    }
    write_json(PROJECT_ROOT / "reports" / "finqa_executor_audit.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

