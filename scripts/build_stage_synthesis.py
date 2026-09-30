#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.utils import read_jsonl, write_json  # noqa: E402


SYSTEMS = {
    "B0": {
        "label": "Direct LLM",
        "status": "accepted_development_run",
        "report": "reports/b0_deepseek_preregistered30_v1_2_report_evidence_ids_v2.json",
        "resource_report": "reports/b0_deepseek_preregistered30_v1_2_report.json",
        "log": "logs/b0_deepseek_preregistered30_v1_2.jsonl",
    },
    "B1": {
        "label": "Tool-Augmented Single Agent",
        "status": "accepted_development_run",
        "report": "reports/b1_deepseek_preregistered30_v1_2_report.json",
        "resource_report": "reports/b1_deepseek_preregistered30_v1_2_report.json",
        "log": "logs/b1_deepseek_preregistered30_v1_2.jsonl",
    },
    "B2-v1": {
        "label": "Fixed-Role Multi-Agent v1",
        "status": "failed_development_run",
        "report": "reports/b2_deepseek_full_preregistered30_v1_report.json",
        "resource_report": "reports/b2_deepseek_full_preregistered30_v1_report.json",
        "log": "logs/b2_deepseek_full_preregistered30_v1.jsonl",
    },
    "B2-v1.1": {
        "label": "Fixed-Role Multi-Agent v1.1",
        "status": "failed_development_run",
        "report": "reports/b2_deepseek_full_preregistered30_v1_1_report.json",
        "resource_report": "reports/b2_deepseek_full_preregistered30_v1_1_report.json",
        "log": "logs/b2_deepseek_full_preregistered30_v1_1.jsonl",
    },
}


def load_json(path: str) -> dict[str, Any]:
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


def paired_correctness(
    left: dict[str, dict[str, Any]], right: dict[str, dict[str, Any]]
) -> dict[str, int]:
    if set(left) != set(right):
        raise ValueError("paired reports do not contain identical sample IDs")
    counts = {"both_correct": 0, "left_only": 0, "right_only": 0, "both_wrong": 0}
    for sample_id in left:
        left_correct = bool(left[sample_id]["answer_correct"])
        right_correct = bool(right[sample_id]["answer_correct"])
        if left_correct and right_correct:
            counts["both_correct"] += 1
        elif left_correct:
            counts["left_only"] += 1
        elif right_correct:
            counts["right_only"] += 1
        else:
            counts["both_wrong"] += 1
    return counts


def main() -> int:
    systems: dict[str, Any] = {}
    result_rows: dict[str, dict[str, dict[str, Any]]] = {}
    for system_id, spec in SYSTEMS.items():
        evaluation = load_json(spec["report"])
        resource = load_json(spec["resource_report"])
        records = list(read_jsonl(PROJECT_ROOT / spec["log"]))
        summary = evaluation["summary"]
        run = resource["run"]
        correct = sum(bool(item["answer_correct"]) for item in evaluation["results"])
        model_calls = (
            run.get("model_calls")
            if run.get("model_calls") is not None
            else run.get("successful_calls", 0) + run.get("failed_calls", 0)
        )
        tool_calls = run.get("tool_calls", 0)
        reasoning_tokens = sum(
            int((record.get("token_usage") or {}).get("reasoning") or 0)
            for record in records
        )
        token_usage = dict(run["token_usage"])
        token_usage["reasoning"] = reasoning_tokens
        systems[system_id] = {
            "label": spec["label"],
            "status": spec["status"],
            "sample_count": summary["total"],
            "successful_samples": run.get("successful_samples", run.get("successful_calls")),
            "failed_samples": run.get("failed_samples", run.get("failed_calls")),
            "correct_answers": correct,
            "metrics": {
                key: summary[key]
                for key in (
                    "coverage",
                    "final_answer_accuracy",
                    "selective_accuracy",
                    "program_accuracy",
                    "execution_accuracy",
                    "execution_coverage",
                    "evidence_macro_precision",
                    "evidence_macro_recall",
                    "evidence_macro_f1",
                )
            },
            "resources": {
                "model_calls": model_calls,
                "tool_calls": tool_calls,
                "input_tokens": token_usage["input"],
                "output_tokens": token_usage["output"],
                "reasoning_tokens": reasoning_tokens,
                "total_tokens": token_usage["total"],
                "latency_ms": run["latency_ms"],
            },
            "efficiency": {
                "total_tokens_per_sample": token_usage["total"] / summary["total"],
                "latency_ms_per_sample": run["latency_ms"] / summary["total"],
                "total_tokens_per_correct_answer": token_usage["total"] / correct,
                "latency_ms_per_correct_answer": run["latency_ms"] / correct,
                "model_calls_per_correct_answer": model_calls / correct,
                "tool_calls_per_correct_answer": tool_calls / correct,
            },
            "source_artifacts": {
                "report": spec["report"],
                "resource_report": spec["resource_report"],
                "log": spec["log"],
            },
        }
        result_rows[system_id] = {
            item["sample_id"]: item for item in evaluation["results"]
        }

    paired = {
        "B0_vs_B1": paired_correctness(result_rows["B0"], result_rows["B1"]),
        "B1_vs_B2_v1": paired_correctness(result_rows["B1"], result_rows["B2-v1"]),
        "B1_vs_B2_v1_1": paired_correctness(
            result_rows["B1"], result_rows["B2-v1.1"]
        ),
    }
    output = {
        "schema_version": "1.0",
        "generated_from_frozen_local_artifacts": True,
        "api_calls": 0,
        "interpretation_boundary": {
            "sample_set": "the repeatedly used 30-item FinQA development diagnostic set",
            "reportable_as_final_test_performance": False,
            "inferential_claims_permitted": False,
            "B2_runs_passed_structural_gate": False,
        },
        "systems": systems,
        "paired_correctness": paired,
    }
    output_path = PROJECT_ROOT / "reports" / "b0_b1_b2_stage_metrics.json"
    write_json(output_path, output)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
