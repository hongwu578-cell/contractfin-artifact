#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.evaluation import evaluate_files  # noqa: E402
from contractfin.run_logging import append_log, log_completeness, utc_now  # noqa: E402
from contractfin.utils import atomic_write_text, read_jsonl, write_json, write_jsonl  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the ContractFin evaluation loop")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    root = args.root.resolve()
    gold_path = root / "data" / "normalized" / "finqa_test.jsonl"
    if not gold_path.exists():
        raise SystemExit("normalized FinQA test data is missing; run normalize first")
    samples = list(read_jsonl(gold_path))[: args.limit]
    if len(samples) < args.limit:
        raise SystemExit(f"requested {args.limit} samples, found {len(samples)}")

    run_id = f"infra-{uuid.uuid4()}"
    smoke_gold_path = root / "reports" / "infrastructure_smoke_gold.jsonl"
    prediction_path = root / "reports" / "infrastructure_smoke_predictions.jsonl"
    log_path = root / "logs" / "infrastructure_smoke.jsonl"
    report_path = root / "reports" / "infrastructure_smoke_report.json"
    atomic_write_text(log_path, "")

    write_jsonl(smoke_gold_path, samples)
    predictions: list[dict] = []
    log_records: list[dict] = []
    for sample in samples:
        started_at = utc_now()
        prediction = {
            "sample_id": sample["sample_id"],
            "answer": sample["gold_answer"],
            "evidence": sample.get("gold_evidence", []),
            "status": "answered",
            "program": sample.get("gold_program"),
            "unit": None,
            "metadata": {"mode": "infrastructure_oracle", "reportable_baseline": False},
        }
        finished_at = utc_now()
        log_record = {
            "run_id": run_id,
            "sample_id": sample["sample_id"],
            "system": "infrastructure_oracle",
            "model": "none-gold-copy",
            "started_at": started_at,
            "finished_at": finished_at,
            "input": {"question": sample["question"]},
            "output": prediction,
            "tool_calls": [],
            "token_usage": {"input": 0, "output": 0, "total": 0},
            "latency_ms": 0,
            "error": None,
        }
        predictions.append(prediction)
        log_records.append(log_record)
        append_log(log_path, log_record)

    write_jsonl(prediction_path, predictions)
    evaluation = evaluate_files(smoke_gold_path, prediction_path, report_path)
    completeness = log_completeness(log_records)
    smoke_summary = {
        "mode": "infrastructure_oracle",
        "warning": "This run copies gold outputs and is not a model baseline.",
        "sample_count": len(samples),
        "schema_valid_rate": evaluation["summary"]["schema_valid_rate"],
        "log_completeness": completeness,
        "scoring_loop_passed": (
            evaluation["summary"]["schema_valid_rate"] >= 0.99
            and evaluation["summary"]["final_answer_accuracy"] == 1.0
            and completeness >= 0.99
        ),
    }
    evaluation["infrastructure_smoke"] = smoke_summary
    write_json(report_path, evaluation)
    print(json.dumps(smoke_summary, ensure_ascii=False, indent=2))
    return 0 if smoke_summary["scoring_loop_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
