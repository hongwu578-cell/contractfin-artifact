#!/usr/bin/env python3
"""Audit a completed SCI held-out primary run before any gold access."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify_error(error: dict[str, Any] | None) -> str:
    if error is None:
        return "none"
    error_type = str(error.get("type", ""))
    message = str(error.get("message", ""))
    text = f"{error_type} {message}".casefold()

    # The frozen protocol defines infrastructure failure as no HTTP response,
    # provider 5xx/429, connection failure, or provider-side timeout before a
    # completed response. Completed but malformed/incomplete model output is a
    # system failure.
    completed_system_markers = (
        "structured output was not valid json",
        "produced no output_text (status=completed)",
        "status=incomplete",
        "max_output_tokens",
        "schema validation",
    )
    if any(marker in text for marker in completed_system_markers):
        return "system"

    infrastructure_markers = (
        "gaierror",
        "network_error",
        "connection refused",
        "connection reset",
        "connection aborted",
        "remote end closed",
        "timed out",
        "timeout",
        "urlerror",
        "no http response",
    )
    status_codes = [int(value) for value in re.findall(r"(?<!\d)(\d{3})(?!\d)", text)]
    if any(marker in text for marker in infrastructure_markers):
        return "infrastructure"
    if any(code == 429 or 500 <= code <= 599 for code in status_codes):
        return "infrastructure"
    return "system"


def returned_models(record: dict[str, Any]) -> set[str]:
    models = {
        str(trace["model"])
        for trace in record.get("model_calls", [])
        if trace.get("model")
    }
    if record.get("system") == "B0" and record.get("model"):
        models.add(str(record["model"]))
    return models


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def make_markdown(report: dict[str, Any]) -> str:
    decision = report["decision"]
    counts = report["counts"]
    failures = report["failure_classification"]
    resources = report["resources"]
    lines = [
        "# SCI held-out primary structural gate report",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Artifact stem: `{report['artifact_stem']}`",
        f"- Run ID: `{report['run_id']}`",
        f"- Gold loaded: **{str(report['gold_loaded']).lower()}**",
        f"- Structural gate: **{'PASS' if decision['passed'] else 'FAIL'}**",
        f"- Unblinding permitted: **{str(decision['unblinding_permitted']).lower()}**",
        "",
        "## Counts and integrity",
        "",
        f"- Logged tasks: {counts['logged_tasks']} / {counts['expected_tasks']}",
        f"- B0 predictions: {counts['predictions_by_system']['B0']} (duplicates: {counts['duplicate_sample_ids_by_system']['B0']})",
        f"- B1 predictions: {counts['predictions_by_system']['B1']} (duplicates: {counts['duplicate_sample_ids_by_system']['B1']})",
        f"- First-system balance: B0={counts['first_system_balance']['B0']}, B1={counts['first_system_balance']['B1']}",
        f"- Within-pair returned-model mismatches: {counts['returned_model_mismatch_pairs']} / 500 ({percent(counts['returned_model_mismatch_rate'])})",
        "",
        "## Failures",
        "",
        f"- B0: system={failures['B0']['system']}, infrastructure={failures['B0']['infrastructure']}",
        f"- B1: system={failures['B1']['system']}, infrastructure={failures['B1']['infrastructure']}",
        f"- Infrastructure rates: B0={percent(failures['B0']['infrastructure_rate'])}, B1={percent(failures['B1']['infrastructure_rate'])}",
        f"- Absolute infrastructure-rate difference: {percent(failures['absolute_rate_difference'])}",
        "",
        "## Resources",
        "",
        f"- Completed provider model calls: {resources['completed_provider_model_calls']} / {resources['authorized_call_ceiling']}",
        f"- Total tokens: {resources['total_tokens']}",
        "",
        "## Frozen prediction hashes",
        "",
        f"- B0: `{report['prediction_files']['B0']['sha256']}`",
        f"- B1: `{report['prediction_files']['B1']['sha256']}`",
        "",
        "## Checks",
        "",
    ]
    for name, passed in report["checks"].items():
        lines.append(f"- {'PASS' if passed else 'FAIL'} — `{name}`")
    lines.extend(["", "No gold file was opened or evaluated by this audit.", ""])
    return "\n".join(lines)


def audit(root: Path, stem: str, runtime_rel: str, schedule_rel: str, call_ceiling: int) -> dict[str, Any]:
    runtime_path = root / runtime_rel
    schedule_path = root / schedule_rel
    log_path = root / "logs" / f"{stem}_tasks.jsonl"
    summary_path = root / "reports" / f"{stem}_inference_summary.json"
    prediction_paths = {
        system: root / "reports" / f"{stem}_{system}_predictions.jsonl"
        for system in ("B0", "B1")
    }

    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    schedule = read_jsonl(schedule_path)
    records = read_jsonl(log_path)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    predictions = {system: read_jsonl(path) for system, path in prediction_paths.items()}

    expected_runtime_hash = sha256_file(runtime_path)
    records_by_system: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        records_by_system[record["system"]].append(record)

    duplicate_counts = {}
    for system in ("B0", "B1"):
        ids = [item.get("sample_id") for item in predictions[system]]
        duplicate_counts[system] = len(ids) - len(set(ids))

    first_system_balance = Counter(
        schedule[index]["system"] for index in range(0, len(schedule), 2)
    )
    schedule_matches_log = len(schedule) == len(records) and all(
        record.get("task_id") == task.get("task_id")
        and record.get("schedule_sequence") == task.get("sequence")
        and record.get("sample_id") == task.get("sample_id")
        and record.get("system") == task.get("system")
        for record, task in zip(records, schedule)
    )

    paired_records: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        paired_records[record["sample_id"]][record["system"]] = record
    mismatch_samples: list[str] = []
    missing_model_identifier_samples: list[str] = []
    for sample_id, pair in paired_records.items():
        if set(pair) != {"B0", "B1"}:
            continue
        b0_models = returned_models(pair["B0"])
        b1_models = returned_models(pair["B1"])
        if not b0_models or not b1_models:
            missing_model_identifier_samples.append(sample_id)
        elif b0_models != b1_models:
            mismatch_samples.append(sample_id)

    failure_counts: dict[str, Counter[str]] = {"B0": Counter(), "B1": Counter()}
    failure_details: list[dict[str, Any]] = []
    for record in records:
        classification = classify_error(record.get("error"))
        if classification != "none":
            failure_counts[record["system"]][classification] += 1
            failure_details.append(
                {
                    "schedule_sequence": record["schedule_sequence"],
                    "task_id": record["task_id"],
                    "system": record["system"],
                    "classification": classification,
                    "error": record["error"],
                }
            )

    infrastructure_rates = {
        system: failure_counts[system]["infrastructure"] / 500 for system in ("B0", "B1")
    }
    infrastructure_difference = abs(infrastructure_rates["B0"] - infrastructure_rates["B1"])

    completed_calls = 0
    returned_model_counts: Counter[str] = Counter()
    for record in records:
        if record["system"] == "B0":
            if record.get("model"):
                returned_model_counts[str(record["model"])] += 1
            if record.get("error") is None:
                completed_calls += 1
        else:
            for trace in record.get("model_calls", []):
                if trace.get("model"):
                    returned_model_counts[str(trace["model"])] += 1
                if trace.get("status") in {"completed", "incomplete"}:
                    completed_calls += 1

    prediction_hashes = {system: sha256_file(path) for system, path in prediction_paths.items()}
    prediction_outputs_match_log = {
        system: predictions[system] == [record["output"] for record in records_by_system[system]]
        for system in ("B0", "B1")
    }
    summary_groups = summary.get("prediction_groups", {})
    summary_hashes_match = all(
        summary_groups.get(f"{system}_R1", {}).get("prediction_sha256") == prediction_hashes[system]
        for system in ("B0", "B1")
    )

    checks = {
        "task_count_is_1000": len(records) == 1000 == len(schedule),
        "schedule_and_log_are_identical_in_order": schedule_matches_log,
        "schedule_sequences_are_1_through_1000": [r.get("schedule_sequence") for r in records] == list(range(1, 1001)),
        "single_run_id": len({r.get("run_id") for r in records}) == 1,
        "protocol_id_matches_runtime": all(r.get("protocol_id") == runtime.get("protocol_id") for r in records),
        "runtime_hash_matches_all_records": all(r.get("runtime_config_sha256") == expected_runtime_hash for r in records),
        "inference_summary_is_complete": summary.get("completed") is True and summary.get("task_count") == 1000,
        "gold_was_not_loaded": summary.get("gold_loaded") is False and summary.get("evaluation_deferred") is True,
        "B0_has_500_unique_predictions": len(predictions["B0"]) == 500 and duplicate_counts["B0"] == 0,
        "B1_has_500_unique_predictions": len(predictions["B1"]) == 500 and duplicate_counts["B1"] == 0,
        "prediction_sample_id_sets_match": {p.get("sample_id") for p in predictions["B0"]} == {p.get("sample_id") for p in predictions["B1"]},
        "prediction_files_match_logged_outputs": all(prediction_outputs_match_log.values()),
        "prediction_hashes_match_inference_summary": summary_hashes_match,
        "first_system_balance_is_250_250": first_system_balance == {"B0": 250, "B1": 250},
        "infrastructure_rate_each_system_at_most_2_percent": all(rate <= 0.02 for rate in infrastructure_rates.values()),
        "infrastructure_rate_difference_at_most_1_point": infrastructure_difference <= 0.01,
        "returned_model_mismatch_rate_at_most_1_percent": len(mismatch_samples) / 500 <= 0.01,
        "every_pair_has_returned_model_identifiers": not missing_model_identifier_samples,
        "completed_model_calls_within_authorized_ceiling": completed_calls <= call_ceiling,
    }
    passed = all(checks.values())
    run_ids = {r.get("run_id") for r in records}
    total_tokens = sum(int(r.get("token_usage", {}).get("total", 0)) for r in records)
    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_stem": stem,
        "run_id": next(iter(run_ids)) if len(run_ids) == 1 else sorted(str(value) for value in run_ids),
        "gold_loaded": False,
        "decision": {
            "passed": passed,
            "unblinding_permitted": passed,
            "reason": "all preregistered structural gates passed" if passed else "one or more preregistered structural gates failed",
        },
        "checks": checks,
        "counts": {
            "expected_tasks": len(schedule),
            "logged_tasks": len(records),
            "predictions_by_system": {system: len(predictions[system]) for system in ("B0", "B1")},
            "duplicate_sample_ids_by_system": duplicate_counts,
            "first_system_balance": {system: first_system_balance[system] for system in ("B0", "B1")},
            "returned_model_mismatch_pairs": len(mismatch_samples),
            "returned_model_mismatch_rate": len(mismatch_samples) / 500,
            "missing_model_identifier_pairs": len(missing_model_identifier_samples),
        },
        "failure_classification": {
            system: {
                "system": failure_counts[system]["system"],
                "infrastructure": failure_counts[system]["infrastructure"],
                "infrastructure_rate": infrastructure_rates[system],
            }
            for system in ("B0", "B1")
        }
        | {"absolute_rate_difference": infrastructure_difference, "details": failure_details},
        "models": {
            "returned_identifier_counts": dict(returned_model_counts),
            "mismatch_sample_ids": mismatch_samples,
            "missing_identifier_sample_ids": missing_model_identifier_samples,
        },
        "resources": {
            "completed_provider_model_calls": completed_calls,
            "authorized_call_ceiling": call_ceiling,
            "total_tokens": total_tokens,
            "tokens_by_system": {
                system: sum(int(r.get("token_usage", {}).get("total", 0)) for r in records_by_system[system])
                for system in ("B0", "B1")
            },
        },
        "prediction_files": {
            system: {
                "path": str(prediction_paths[system].relative_to(root)),
                "sha256": prediction_hashes[system],
                "bytes": prediction_paths[system].stat().st_size,
            }
            for system in ("B0", "B1")
        },
        "source_files": {
            "runtime_config": str(runtime_path.relative_to(root)),
            "runtime_config_sha256": expected_runtime_hash,
            "schedule": str(schedule_path.relative_to(root)),
            "schedule_sha256": sha256_file(schedule_path),
            "task_log": str(log_path.relative_to(root)),
            "task_log_sha256": sha256_file(log_path),
            "inference_summary": str(summary_path.relative_to(root)),
            "inference_summary_sha256": sha256_file(summary_path),
        },
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--artifact-stem", required=True)
    parser.add_argument("--runtime-config", default="config/sci_heldout_runtime_v1.json")
    parser.add_argument("--schedule", default="config/sci_finqa_test500_interleaved_schedule_v1.jsonl")
    parser.add_argument("--call-ceiling", type=int, default=3500)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    report = audit(root, args.artifact_stem, args.runtime_config, args.schedule, args.call_ceiling)
    json_path = root / args.output_json
    md_path = root / args.output_md
    write_json(json_path, report)
    md_path.write_text(make_markdown(report), encoding="utf-8")
    print(json.dumps(report["decision"], ensure_ascii=False))
    return 0 if report["decision"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
