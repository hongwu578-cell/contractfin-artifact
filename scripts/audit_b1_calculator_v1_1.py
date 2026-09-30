#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.b1_tools import execute_b1_tool  # noqa: E402
from contractfin.program import _split_top_level, execution_values_match  # noqa: E402
from contractfin.utils import read_jsonl, write_json  # noqa: E402


def structured_steps(program: str) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for expression in _split_top_level(program):
        match = re.fullmatch(r"([A-Za-z_]+)\((.*)\)", expression.strip())
        if match is None:
            raise ValueError(f"invalid gold expression: {expression}")
        arguments = _split_top_level(match.group(2))
        if len(arguments) != 2:
            raise ValueError(f"gold expression does not have two arguments: {expression}")
        steps.append(
            {
                "operation": match.group(1).casefold(),
                "arguments": [str(argument).strip() for argument in arguments],
            }
        )
    return steps


def main() -> int:
    dataset_path = PROJECT_ROOT / "data" / "normalized" / "finqa_dev.jsonl"
    rows = list(read_jsonl(dataset_path))
    parsed = 0
    tool_success = 0
    execution_correct = 0
    operation_counts: Counter[str] = Counter()
    failures: list[dict[str, Any]] = []
    for row in rows:
        try:
            steps = structured_steps(str(row["gold_program"]))
            parsed += 1
            operation_counts.update(step["operation"] for step in steps)
            output, trace = execute_b1_tool(
                "calculate_finqa",
                json.dumps({"steps": steps}, ensure_ascii=False),
                row,
            )
            result = json.loads(output)
            if result.get("ok"):
                tool_success += 1
            else:
                raise ValueError(str(result.get("error")))
            if execution_values_match(result["value"], row["gold_answer"]):
                execution_correct += 1
            else:
                raise ValueError(
                    f"execution mismatch: value={result['value']!r}, gold={row['gold_answer']!r}"
                )
            if trace["error"] is not None:
                raise ValueError(str(trace["error"]))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            failures.append({"sample_id": row.get("sample_id"), "error": str(exc)})
    total = len(rows)
    report = {
        "schema_version": "1.0",
        "mode": "development_gold_program_interface_audit",
        "warning": "Gold programs are used only for aggregate local interface validation and are never exposed at runtime.",
        "dataset": str(dataset_path),
        "samples": total,
        "gold_programs_parsed": parsed,
        "structured_tool_successes": tool_success,
        "execution_correct": execution_correct,
        "operation_counts": dict(sorted(operation_counts.items())),
        "failures": failures,
        "acceptance": {
            "required_parse_rate": 1.0,
            "required_tool_success_rate": 1.0,
            "required_execution_accuracy": 1.0,
            "observed_parse_rate": parsed / total if total else 0.0,
            "observed_tool_success_rate": tool_success / total if total else 0.0,
            "observed_execution_accuracy": execution_correct / total if total else 0.0,
            "passed": parsed == tool_success == execution_correct == total and not failures,
        },
    }
    write_json(PROJECT_ROOT / "reports" / "b1_calculator_v1_1_audit.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["acceptance"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
