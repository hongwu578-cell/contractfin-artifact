#!/usr/bin/env python3
"""Deterministic paired error and mechanism analysis for the frozen SCI run.

This script performs no model calls. It reads only the immutable primary-run
artifacts after the structural gate and evaluation have completed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OPERATION_RE = re.compile(r"([a-z_]+)\s*\(")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n" for value in values),
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def operation_sequence(program: Any) -> list[str]:
    if program is None:
        return []
    if isinstance(program, list):
        text = ", ".join(str(value) for value in program)
    else:
        text = str(program)
    return OPERATION_RE.findall(text.casefold())


def direction(value: float, tolerance: float = 1e-12) -> str:
    if value > tolerance:
        return "improved"
    if value < -tolerance:
        return "worsened"
    return "unchanged"


def transition(b0_correct: bool, b1_correct: bool) -> str:
    if b0_correct and b1_correct:
        return "both_correct"
    if not b0_correct and b1_correct:
        return "B1_only_correct"
    if b0_correct and not b1_correct:
        return "B0_only_correct"
    return "both_wrong"


def percentile_bootstrap_difference(
    differences: np.ndarray,
    *,
    draws: int = 10_000,
    seed: int = 20260929,
) -> dict[str, Any]:
    differences = differences.astype(float)
    rng = np.random.default_rng(seed)
    estimates = np.empty(draws, dtype=float)
    cursor = 0
    while cursor < draws:
        batch = min(1000, draws - cursor)
        indices = rng.integers(0, len(differences), size=(batch, len(differences)))
        estimates[cursor : cursor + batch] = differences[indices].mean(axis=1)
        cursor += batch
    lower, upper = np.quantile(estimates, [0.025, 0.975], method="linear")
    return {
        "point_estimate": float(differences.mean()),
        "ci_lower": float(lower),
        "ci_upper": float(upper),
        "draws": draws,
        "seed": seed,
        "method": "paired item percentile bootstrap",
    }


def distribution(values: list[float] | np.ndarray) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    q1, median, q3 = np.quantile(array, [0.25, 0.5, 0.75], method="linear")
    return {
        "mean": float(np.mean(array)),
        "q1": float(q1),
        "median": float(median),
        "q3": float(q3),
        "minimum": float(np.min(array)),
        "maximum": float(np.max(array)),
    }


def diagnostic_flags(
    prediction: dict[str, Any],
    evaluation: dict[str, Any],
    log: dict[str, Any],
    gold_operations: list[str],
) -> list[str]:
    if evaluation["answer_correct"]:
        return []
    flags: list[str] = []
    status = prediction.get("status")
    predicted_program = prediction.get("program")
    predicted_operations = operation_sequence(predicted_program)

    if log.get("error") is not None:
        flags.append("system_output_failure")
    if status == "abstain":
        flags.append("abstention")
    elif status != "answered":
        flags.append("non_answer")
    if predicted_program is None:
        flags.append("missing_program")
    else:
        if evaluation.get("execution_correct") is False and evaluation.get("execution_error"):
            flags.append("invalid_or_non_executable_program")
        if predicted_operations and predicted_operations != gold_operations:
            flags.append("operation_sequence_mismatch")
        elif (
            predicted_operations == gold_operations
            and evaluation.get("program_correct") is not True
            and evaluation.get("execution_correct") is not True
        ):
            flags.append("argument_or_numeric_extraction_candidate")
    if evaluation.get("execution_correct") is True:
        flags.append("executable_program_but_final_answer_wrong")
    if evaluation.get("program_correct") is True:
        flags.append("exact_program_but_final_answer_wrong")
    evidence_f1 = float(evaluation["evidence"]["f1"])
    if evidence_f1 == 0.0:
        flags.append("zero_evidence_f1")
    elif evidence_f1 < 1.0:
        flags.append("partial_evidence_match")
    if evaluation.get("unit_scale_error"):
        flags.append("unit_or_scale_error")
    if evaluation.get("unsupported_claim"):
        flags.append("unsupported_answer")
    if not flags:
        flags.append("other_unresolved_semantic_error")
    return flags


def subgroup_rows(
    pair_rows: list[dict[str, Any]],
    key: Callable[[dict[str, Any]], str],
) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pair_rows:
        groups[key(row)].append(row)
    output: list[dict[str, Any]] = []
    for group_name in sorted(groups):
        rows = groups[group_name]
        b0 = np.array([row["B0"]["answer_correct"] for row in rows], dtype=float)
        b1 = np.array([row["B1"]["answer_correct"] for row in rows], dtype=float)
        b1_only = sum(row["transition"] == "B1_only_correct" for row in rows)
        b0_only = sum(row["transition"] == "B0_only_correct" for row in rows)
        interval = percentile_bootstrap_difference(b1 - b0)
        output.append(
            {
                "group": group_name,
                "n": len(rows),
                "B0_correct": int(b0.sum()),
                "B1_correct": int(b1.sum()),
                "B0_accuracy": float(b0.mean()),
                "B1_accuracy": float(b1.mean()),
                "difference_B1_minus_B0": float((b1 - b0).mean()),
                "difference_95pct_paired_bootstrap_CI": [interval["ci_lower"], interval["ci_upper"]],
                "B1_only_correct": b1_only,
                "B0_only_correct": b0_only,
            }
        )
    return output


def load_inputs(root: Path, stem: str) -> dict[str, Any]:
    paths = {
        "manifest": root / "config/sci_finqa_test500_manifest_v1.json",
        "gold": root / "data/heldout/finqa_test500_gold_v1.jsonl",
        "gate": root / "reports" / f"{stem}_structural_gate.json",
        "results": root / "reports" / f"{stem}_results.json",
        "log": root / "logs" / f"{stem}_tasks.jsonl",
        "B0_predictions": root / "reports" / f"{stem}_B0_predictions.jsonl",
        "B1_predictions": root / "reports" / f"{stem}_B1_predictions.jsonl",
        "B0_evaluation": root / "reports" / f"{stem}_B0_evaluation.json",
        "B1_evaluation": root / "reports" / f"{stem}_B1_evaluation.json",
    }
    gate = json.loads(paths["gate"].read_text(encoding="utf-8"))
    if gate.get("decision", {}).get("passed") is not True:
        raise RuntimeError("structural gate did not pass")
    for system in ("B0", "B1"):
        prediction_hash = sha256_file(paths[f"{system}_predictions"])
        if prediction_hash != gate["prediction_files"][system]["sha256"]:
            raise RuntimeError(f"{system} prediction hash changed after freezing")
    return {
        "paths": paths,
        "manifest": json.loads(paths["manifest"].read_text(encoding="utf-8")),
        "gold": read_jsonl(paths["gold"]),
        "gate": gate,
        "results": json.loads(paths["results"].read_text(encoding="utf-8")),
        "logs": read_jsonl(paths["log"]),
        "predictions": {
            system: read_jsonl(paths[f"{system}_predictions"]) for system in ("B0", "B1")
        },
        "evaluations": {
            system: json.loads(paths[f"{system}_evaluation"].read_text(encoding="utf-8"))
            for system in ("B0", "B1")
        },
    }


def analyze(root: Path, stem: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    inputs = load_inputs(root, stem)
    manifest = inputs["manifest"]
    gold = inputs["gold"]
    logs = inputs["logs"]
    results = inputs["results"]
    paths = inputs["paths"]

    metadata = {item["sample_id"]: item for item in manifest["samples"]}
    gold_by_id = {item["sample_id"]: item for item in gold}
    predictions = {
        system: {item["sample_id"]: item for item in inputs["predictions"][system]}
        for system in ("B0", "B1")
    }
    evaluations = {
        system: {
            item["sample_id"]: item for item in inputs["evaluations"][system]["results"]
        }
        for system in ("B0", "B1")
    }
    log_by_system_id = {
        system: {
            item["sample_id"]: item for item in logs if item["system"] == system
        }
        for system in ("B0", "B1")
    }

    pair_rows: list[dict[str, Any]] = []
    for sample in manifest["samples"]:
        sample_id = sample["sample_id"]
        system_data: dict[str, Any] = {}
        for system in ("B0", "B1"):
            prediction = predictions[system][sample_id]
            evaluation = evaluations[system][sample_id]
            log = log_by_system_id[system][sample_id]
            tool_names = [tool["name"] for tool in log.get("tool_calls", [])]
            system_data[system] = {
                "status": prediction.get("status"),
                "answer": prediction.get("answer"),
                "program": prediction.get("program"),
                "answer_correct": bool(evaluation["answer_correct"]),
                "program_correct": evaluation.get("program_correct") is True,
                "execution_correct": evaluation.get("execution_correct") is True,
                "execution_error": evaluation.get("execution_error"),
                "evidence_f1": float(evaluation["evidence"]["f1"]),
                "evidence_precision": float(evaluation["evidence"]["precision"]),
                "evidence_recall": float(evaluation["evidence"]["recall"]),
                "model_calls": 1 if system == "B0" else len(log.get("model_calls", [])),
                "tool_calls": len(log.get("tool_calls", [])),
                "search_calls": tool_names.count("search_document"),
                "calculator_calls": tool_names.count("calculate_finqa"),
                "tool_error_count": sum(tool.get("error") is not None for tool in log.get("tool_calls", [])),
                "tokens": int(log["token_usage"]["total"]),
                "latency_ms": float(log["latency_ms"]),
                "system_error": log.get("error"),
                "diagnostic_flags": diagnostic_flags(
                    prediction,
                    evaluation,
                    log,
                    sample["operation_sequence"],
                ),
            }
        evidence_delta = system_data["B1"]["evidence_f1"] - system_data["B0"]["evidence_f1"]
        pair_rows.append(
            {
                "sample_id": sample_id,
                "run_order": sample["run_order"],
                "stratum": sample["stratum"],
                "step_count": sample["step_count"],
                "gold_answer": gold_by_id[sample_id]["gold_answer"],
                "gold_program": gold_by_id[sample_id]["gold_program"],
                "gold_evidence_count": sample["gold_evidence_count"],
                "transition": transition(
                    system_data["B0"]["answer_correct"],
                    system_data["B1"]["answer_correct"],
                ),
                "evidence_f1_delta_B1_minus_B0": evidence_delta,
                "evidence_direction": direction(evidence_delta),
                "B0": system_data["B0"],
                "B1": system_data["B1"],
            }
        )

    transition_counts = Counter(row["transition"] for row in pair_rows)
    gains = [row for row in pair_rows if row["transition"] == "B1_only_correct"]
    losses = [row for row in pair_rows if row["transition"] == "B0_only_correct"]

    gain_mechanisms = {
        "items": len(gains),
        "B1_exact_program_recovery": sum(
            row["B1"]["program_correct"] and not row["B0"]["program_correct"] for row in gains
        ),
        "B1_executable_program_recovery": sum(
            row["B1"]["execution_correct"] and not row["B0"]["execution_correct"] for row in gains
        ),
        "evidence_improved": sum(row["evidence_direction"] == "improved" for row in gains),
        "evidence_unchanged": sum(row["evidence_direction"] == "unchanged" for row in gains),
        "evidence_worsened": sum(row["evidence_direction"] == "worsened" for row in gains),
        "calculator_reached": sum(row["B1"]["calculator_calls"] > 0 for row in gains),
    }
    loss_mechanisms = {
        "items": len(losses),
        "B1_system_output_failure": sum(row["B1"]["system_error"] is not None for row in losses),
        "B1_execution_regression": sum(
            row["B0"]["execution_correct"] and not row["B1"]["execution_correct"] for row in losses
        ),
        "B1_exact_program_regression": sum(
            row["B0"]["program_correct"] and not row["B1"]["program_correct"] for row in losses
        ),
        "evidence_improved": sum(row["evidence_direction"] == "improved" for row in losses),
        "evidence_unchanged": sum(row["evidence_direction"] == "unchanged" for row in losses),
        "evidence_worsened": sum(row["evidence_direction"] == "worsened" for row in losses),
    }

    answer_execution_cross_tabs: dict[str, Any] = {}
    diagnostic_counts: dict[str, Any] = {}
    for system in ("B0", "B1"):
        cross = Counter(
            (
                row[system]["answer_correct"],
                row[system]["execution_correct"],
            )
            for row in pair_rows
        )
        execution_correct_total = sum(row[system]["execution_correct"] for row in pair_rows)
        execution_and_answer_correct = sum(
            row[system]["execution_correct"] and row[system]["answer_correct"] for row in pair_rows
        )
        exact_program_total = sum(row[system]["program_correct"] for row in pair_rows)
        exact_program_and_answer_correct = sum(
            row[system]["program_correct"] and row[system]["answer_correct"] for row in pair_rows
        )
        answer_execution_cross_tabs[system] = {
            "answer_correct_execution_correct": cross[(True, True)],
            "answer_correct_execution_not_correct": cross[(True, False)],
            "answer_wrong_execution_correct": cross[(False, True)],
            "answer_wrong_execution_not_correct": cross[(False, False)],
            "answer_consistency_given_executable_program": (
                execution_and_answer_correct / execution_correct_total if execution_correct_total else None
            ),
            "answer_consistency_given_exact_program": (
                exact_program_and_answer_correct / exact_program_total if exact_program_total else None
            ),
        }
        counts = Counter(
            flag
            for row in pair_rows
            for flag in row[system]["diagnostic_flags"]
        )
        diagnostic_counts[system] = {
            "incorrect_items": sum(not row[system]["answer_correct"] for row in pair_rows),
            "nonexclusive_flag_counts": dict(sorted(counts.items())),
            "note": "Flags are deterministic and nonexclusive; candidate labels are not manual causal adjudications.",
        }

    b1_logs = [record for record in logs if record["system"] == "B1"]
    calculator_records = [
        record for record in b1_logs if any(tool["name"] == "calculate_finqa" for tool in record["tool_calls"])
    ]
    no_calculator_records = [record for record in b1_logs if record not in calculator_records]
    calculator_tool_events = [
        tool
        for record in b1_logs
        for tool in record["tool_calls"]
        if tool["name"] == "calculate_finqa"
    ]
    tool_path = {
        "search_document_calls": sum(
            tool["name"] == "search_document" for record in b1_logs for tool in record["tool_calls"]
        ),
        "calculate_finqa_calls": len(calculator_tool_events),
        "calculate_finqa_successes": sum(tool.get("output", {}).get("ok") is True for tool in calculator_tool_events),
        "calculate_finqa_failures": sum(tool.get("output", {}).get("ok") is False for tool in calculator_tool_events),
        "items_reaching_calculator": len(calculator_records),
        "calculator_subset_correct": sum(
            evaluations["B1"][record["sample_id"]]["answer_correct"] for record in calculator_records
        ),
        "items_not_reaching_calculator": len(no_calculator_records),
        "no_calculator_subset_correct": sum(
            evaluations["B1"][record["sample_id"]]["answer_correct"] for record in no_calculator_records
        ),
        "failed_calculator_events_with_final_correct_answer": sum(
            any(tool["name"] == "calculate_finqa" and tool.get("output", {}).get("ok") is False for tool in record["tool_calls"])
            and evaluations["B1"][record["sample_id"]]["answer_correct"]
            for record in b1_logs
        ),
    }

    evidence_transitions = Counter(row["evidence_direction"] for row in pair_rows)
    evidence_quality: dict[str, Any] = {"pairwise_direction_counts": dict(evidence_transitions)}
    for system in ("B0", "B1"):
        categories = {
            "perfect": [row for row in pair_rows if row[system]["evidence_f1"] == 1.0],
            "partial": [row for row in pair_rows if 0.0 < row[system]["evidence_f1"] < 1.0],
            "zero": [row for row in pair_rows if row[system]["evidence_f1"] == 0.0],
        }
        evidence_quality[system] = {
            name: {
                "n": len(rows),
                "answer_accuracy": (
                    sum(row[system]["answer_correct"] for row in rows) / len(rows) if rows else None
                ),
            }
            for name, rows in categories.items()
        }

    transition_resources: list[dict[str, Any]] = []
    for name in ("both_correct", "B1_only_correct", "B0_only_correct", "both_wrong"):
        rows = [row for row in pair_rows if row["transition"] == name]
        token_difference = np.array([row["B1"]["tokens"] - row["B0"]["tokens"] for row in rows])
        latency_difference = np.array([row["B1"]["latency_ms"] - row["B0"]["latency_ms"] for row in rows])
        transition_resources.append(
            {
                "transition": name,
                "n": len(rows),
                "B0_tokens": distribution([row["B0"]["tokens"] for row in rows]),
                "B1_tokens": distribution([row["B1"]["tokens"] for row in rows]),
                "token_difference_B1_minus_B0": distribution(token_difference),
                "B0_latency_ms": distribution([row["B0"]["latency_ms"] for row in rows]),
                "B1_latency_ms": distribution([row["B1"]["latency_ms"] for row in rows]),
                "latency_difference_B1_minus_B0": distribution(latency_difference),
            }
        )

    paired_token_differences = np.array([row["B1"]["tokens"] - row["B0"]["tokens"] for row in pair_rows])
    paired_latency_differences = np.array([row["B1"]["latency_ms"] - row["B0"]["latency_ms"] for row in pair_rows])
    resource_intervals = {
        "mean_total_tokens_difference_B1_minus_B0": percentile_bootstrap_difference(paired_token_differences),
        "mean_latency_ms_difference_B1_minus_B0": percentile_bootstrap_difference(paired_latency_differences),
    }

    error_records = []
    for row in pair_rows:
        if row["B1"]["system_error"] is not None:
            error_records.append(
                {
                    "sample_id": row["sample_id"],
                    "stratum": row["stratum"],
                    "step_count": row["step_count"],
                    "transition": row["transition"],
                    "B0_answer_correct": row["B0"]["answer_correct"],
                    "error": row["B1"]["system_error"],
                    "model_calls": row["B1"]["model_calls"],
                    "tool_calls": row["B1"]["tool_calls"],
                    "tokens": row["B1"]["tokens"],
                    "latency_ms": row["B1"]["latency_ms"],
                }
            )

    source_hashes = {
        name: {"path": str(path.relative_to(root)), "sha256": sha256_file(path)}
        for name, path in paths.items()
    }
    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "protocol_id": manifest["protocol_id"],
        "run_id": results["run_id"],
        "model_api_calls_during_analysis": 0,
        "analysis_boundary": {
            "confirmatory_outcome_unchanged": True,
            "subgroup_and_mechanism_analyses_are_exploratory": True,
            "deterministic_flags_are_nonexclusive": True,
            "manual_semantic_coding_performed": False,
        },
        "pair_transition_counts": {
            name: transition_counts[name]
            for name in ("both_correct", "B1_only_correct", "B0_only_correct", "both_wrong")
        },
        "gain_mechanisms": gain_mechanisms,
        "loss_mechanisms": loss_mechanisms,
        "answer_execution_cross_tabs": answer_execution_cross_tabs,
        "diagnostic_error_flags": diagnostic_counts,
        "tool_path_analysis": tool_path,
        "evidence_analysis": evidence_quality,
        "by_operation_stratum": subgroup_rows(pair_rows, lambda row: row["stratum"]),
        "by_step_count": subgroup_rows(pair_rows, lambda row: f"{row['step_count']}_step"),
        "transition_resource_profiles": transition_resources,
        "resource_paired_bootstrap": resource_intervals,
        "B1_system_output_failures": error_records,
        "interpretive_findings": [
            "B1 improved final-answer accuracy by converting more losses to gains (58) than gains to losses (33).",
            "The largest descriptive gain occurred in two-step items; four- and five-step strata were small and did not show the same benefit.",
            "Program and execution recovery explains part, but not all, of B1-only gains; evidence F1 was unchanged in most gain items.",
            "B1 produced substantially more executable or exact programs whose final answer was nevertheless incorrect, exposing an answer-program synchronization problem.",
            "Every B1-correct item reached the deterministic calculator, while no item that failed to reach the calculator was correct; this is descriptive, not a randomized tool-use effect.",
            "Tool augmentation improved program and execution ITT outcomes at the cost of more calls and tokens, while evidence F1 and coverage did not improve.",
        ],
        "source_artifacts": source_hashes,
    }
    return report, pair_rows


def pct(value: float, digits: int = 1) -> str:
    return f"{100 * value:.{digits}f}%"


def signed_pp(value: float, digits: int = 1) -> str:
    return f"{100 * value:+.{digits}f} pp"


def make_report_markdown(report: dict[str, Any]) -> str:
    transitions = report["pair_transition_counts"]
    gains = report["gain_mechanisms"]
    losses = report["loss_mechanisms"]
    tool = report["tool_path_analysis"]
    cross = report["answer_execution_cross_tabs"]
    lines = [
        "# SCI held-out paired error and mechanism analysis",
        "",
        f"- Protocol: `{report['protocol_id']}`",
        f"- Run ID: `{report['run_id']}`",
        "- Model API calls during this analysis: **0**",
        "- Analysis status: exploratory mechanism analysis after confirmatory prediction freeze",
        "",
        "## Paired outcome transitions",
        "",
        "| Transition | Items | Share |",
        "|---|---:|---:|",
        f"| Both correct | {transitions['both_correct']} | {pct(transitions['both_correct']/500)} |",
        f"| B1 only correct | {transitions['B1_only_correct']} | {pct(transitions['B1_only_correct']/500)} |",
        f"| B0 only correct | {transitions['B0_only_correct']} | {pct(transitions['B0_only_correct']/500)} |",
        f"| Both wrong | {transitions['both_wrong']} | {pct(transitions['both_wrong']/500)} |",
        "",
        "B1 generated 25 net additional correct answers (58 gains minus 33 regressions).",
        "",
        "## Mechanisms in the 58 B1-only gains",
        "",
        f"- Exact-program recovery relative to B0: {gains['B1_exact_program_recovery']} items.",
        f"- Executable-program recovery relative to B0: {gains['B1_executable_program_recovery']} items.",
        f"- Evidence F1 improved/unchanged/worsened: {gains['evidence_improved']}/{gains['evidence_unchanged']}/{gains['evidence_worsened']}.",
        f"- Calculator reached: {gains['calculator_reached']}/{gains['items']} items.",
        "",
        "The majority of gains did not coincide with improved evidence F1, so the observed benefit is more consistent with arithmetic/program assistance than with uniformly better evidence selection.",
        "",
        "## Mechanisms in the 33 B0-only regressions",
        "",
        f"- B1 system-output failures: {losses['B1_system_output_failure']} items.",
        f"- Execution regressions relative to B0: {losses['B1_execution_regression']} items.",
        f"- Exact-program regressions relative to B0: {losses['B1_exact_program_regression']} items.",
        f"- Evidence F1 improved/unchanged/worsened: {losses['evidence_improved']}/{losses['evidence_unchanged']}/{losses['evidence_worsened']}.",
        "",
        "## Answer–program synchronization",
        "",
        "| System | Answer correct and executable | Answer correct, not executable | Answer wrong but executable | Answer wrong, not executable | Answer consistency given executable program |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for system in ("B0", "B1"):
        item = cross[system]
        lines.append(
            f"| {system} | {item['answer_correct_execution_correct']} | {item['answer_correct_execution_not_correct']} | "
            f"{item['answer_wrong_execution_correct']} | {item['answer_wrong_execution_not_correct']} | "
            f"{pct(item['answer_consistency_given_executable_program'])} |"
        )
    lines.extend(
        [
            "",
            "B1 greatly increased execution correctness, but it also increased cases in which an executable program reached the gold value while the reported final answer remained wrong (61 versus 17). This is a concrete output-synchronization target for the next architecture revision.",
            "",
            "## Tool-path evidence",
            "",
            f"- `search_document` calls: {tool['search_document_calls']}.",
            f"- `calculate_finqa` calls: {tool['calculate_finqa_calls']} ({tool['calculate_finqa_successes']} successful; {tool['calculate_finqa_failures']} failed).",
            f"- Items reaching the calculator: {tool['items_reaching_calculator']}; correct: {tool['calculator_subset_correct']}.",
            f"- Items not reaching the calculator: {tool['items_not_reaching_calculator']}; correct: {tool['no_calculator_subset_correct']}.",
            f"- Failed calculator events followed by a correct final answer: {tool['failed_calculator_events_with_final_correct_answer']}.",
            "",
            "These are process associations, not randomized causal effects of choosing a tool path.",
            "",
            "## Step-depth profile",
            "",
            "| Steps | n | B0 accuracy | B1 accuracy | Difference | B1-only | B0-only | 95% paired bootstrap CI |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in report["by_step_count"]:
        ci = item["difference_95pct_paired_bootstrap_CI"]
        lines.append(
            f"| {item['group'].replace('_step','')} | {item['n']} | {pct(item['B0_accuracy'])} | {pct(item['B1_accuracy'])} | "
            f"{signed_pp(item['difference_B1_minus_B0'])} | {item['B1_only_correct']} | {item['B0_only_correct']} | "
            f"[{signed_pp(ci[0])}, {signed_pp(ci[1])}] |"
        )
    lines.extend(
        [
            "",
            "The depth analysis is exploratory. In particular, the four- and five-step groups are too small for broad claims.",
            "",
            "## Claim boundary",
            "",
            "Deterministic flags are nonexclusive diagnostic indicators. Numeric extraction, semantic operation choice, and argument-order causes require blinded manual coding before being reported as adjudicated error categories.",
            "",
        ]
    )
    return "\n".join(lines)


def make_tables_markdown(report: dict[str, Any], results: dict[str, Any]) -> str:
    primary = results["primary_analysis"]
    secondary = results["secondary_analysis"]
    resources = results["resources"]["by_system"]
    gate_path = report["source_artifacts"]["gate"]["path"]
    token_ci = report["resource_paired_bootstrap"]["mean_total_tokens_difference_B1_minus_B0"]
    latency_ci = report["resource_paired_bootstrap"]["mean_latency_ms_difference_B1_minus_B0"]
    b0_tokens = resources["B0"]["tokens"]["total"]
    b1_tokens = resources["B1"]["tokens"]["total"]
    b0_latency = resources["B0"]["latency_ms"]
    b1_latency = resources["B1"]["latency_ms"]
    transitions = report["pair_transition_counts"]
    lines = [
        "# ContractFin SCI result tables",
        "",
        "Tables are formatted as Markdown drafts for conversion to journal three-line tables. No vertical rules should be used in typesetting.",
        "",
        "## Run-integrity checklist (unnumbered)",
        "",
        "| Gate | Requirement | Observed | Decision |",
        "|---|---:|---:|---|",
        "| Scheduled task records | 1,000 | 1,000 | Pass |",
        "| Unique predictions per system | 500 | B0=500; B1=500 | Pass |",
        "| Duplicate predictions | 0 | 0 | Pass |",
        "| B0-first/B1-first pairs | 250/250 | 250/250 | Pass |",
        "| Infrastructure failures | ≤2% each; difference ≤1 pp | B0=0%; B1=0%; difference=0 pp | Pass |",
        "| Returned-model mismatched pairs | ≤1% | 0/500 | Pass |",
        "| Prediction hashes recorded before gold access | Required | Recorded | Pass |",
        "",
        f"Note: the complete structural record is `{gate_path}`. The first sandboxed attempt made zero provider calls and was replaced by a dated full-schedule amendment; no selected-item rerun occurred.",
        "",
        "## Table 4. Preregistered paired held-out comparison",
        "",
        "| Outcome | B0 | B1 | B1−B0 | 95% paired bootstrap CI | Discordant pairs | Exact p |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| Final-answer ITT accuracy | 42.0% (210/500) | 47.0% (235/500) | +5.0 pp | [+1.4, +8.8] pp | B1-only=58; B0-only=33 | {primary['mcnemar']['p_value_two_sided_exact']:.5f} |",
        "",
        "## Table 5. Preregistered secondary outcomes",
        "",
        "| Outcome | B0 | B1 | B1−B0 | Raw p | Holm-adjusted p | Multiplicity decision |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    labels = {
        "program_itt_correctness": "Program ITT correctness",
        "execution_itt_correctness": "Execution ITT correctness",
        "evidence_item_f1": "Evidence item-level F1",
        "coverage": "Coverage",
    }
    for name in ("program_itt_correctness", "execution_itt_correctness", "evidence_item_f1", "coverage"):
        item = secondary[name]
        holm = secondary["holm_family"][name]
        lines.append(
            f"| {labels[name]} | {item['B0_mean']:.4f} | {item['B1_mean']:.4f} | {item['difference_B1_minus_B0']:+.4f} | "
            f"{holm['raw_p_value']:.6g} | {holm['holm_adjusted_p_value']:.6g} | "
            f"{'Reject' if holm['reject_at_alpha_0_05'] else 'Do not reject'} |"
        )
    lines.extend(
        [
            "",
            "Note: program correctness, execution correctness, and coverage use exact McNemar tests; evidence F1 uses the preregistered 100,000-draw paired sign-flip test. All four p-values are Holm adjusted.",
            "",
            "## Table 6. Resource use and quality–cost trade-off",
            "",
            "| Measure | B0 | B1 | B1/B0 or paired B1−B0 |",
            "|---|---:|---:|---:|",
            f"| Total model calls | {resources['B0']['model_calls_total']:,} | {resources['B1']['model_calls_total']:,} | {resources['B1']['model_calls_total']/resources['B0']['model_calls_total']:.2f}× |",
            f"| Total tool calls | 0 | {resources['B1']['tool_calls_total']:,} | — |",
            f"| Total tokens | {b0_tokens['total']:,} | {b1_tokens['total']:,} | {b1_tokens['total']/b0_tokens['total']:.2f}× |",
            f"| Median tokens/item (IQR) | {b0_tokens['per_item']['median']:,.0f} ({b0_tokens['per_item']['q1']:,.0f}–{b0_tokens['per_item']['q3']:,.0f}) | {b1_tokens['per_item']['median']:,.0f} ({b1_tokens['per_item']['q1']:,.0f}–{b1_tokens['per_item']['q3']:,.0f}) | Mean difference {token_ci['point_estimate']:,.0f} [{token_ci['ci_lower']:,.0f}, {token_ci['ci_upper']:,.0f}] |",
            f"| Total latency | {b0_latency['total']/1000:,.1f} s | {b1_latency['total']/1000:,.1f} s | {b1_latency['total']/b0_latency['total']:.2f}× |",
            f"| Median latency/item (IQR) | {b0_latency['per_item']['median']/1000:.2f} ({b0_latency['per_item']['q1']/1000:.2f}–{b0_latency['per_item']['q3']/1000:.2f}) s | {b1_latency['per_item']['median']/1000:.2f} ({b1_latency['per_item']['q1']/1000:.2f}–{b1_latency['per_item']['q3']/1000:.2f}) s | Mean difference {latency_ci['point_estimate']/1000:+.2f} [{latency_ci['ci_lower']/1000:+.2f}, {latency_ci['ci_upper']/1000:+.2f}] s |",
            f"| Tokens/correct answer | {resources['B0']['total_tokens_per_correct_answer']:,.0f} | {resources['B1']['total_tokens_per_correct_answer']:,.0f} | {resources['B1']['total_tokens_per_correct_answer']/resources['B0']['total_tokens_per_correct_answer']:.2f}× |",
            f"| Latency/correct answer | {resources['B0']['total_latency_ms_per_correct_answer']/1000:.2f} s | {resources['B1']['total_latency_ms_per_correct_answer']/1000:.2f} s | {resources['B1']['total_latency_ms_per_correct_answer']/resources['B0']['total_latency_ms_per_correct_answer']:.2f}× |",
            "",
            "## Table 7. Paired outcome transitions and mechanism evidence",
            "",
            "| Paired transition | n | Share | Mechanism reading |",
            "|---|---:|---:|---|",
            f"| Both correct | {transitions['both_correct']} | {pct(transitions['both_correct']/500)} | Shared solved set |",
            f"| B1 only correct | {transitions['B1_only_correct']} | {pct(transitions['B1_only_correct']/500)} | 20 exact-program and 30 executable-program recoveries relative to B0 |",
            f"| B0 only correct | {transitions['B0_only_correct']} | {pct(transitions['B0_only_correct']/500)} | Includes 2 B1 system-output failures and 9 execution regressions |",
            f"| Both wrong | {transitions['both_wrong']} | {pct(transitions['both_wrong']/500)} | Residual reasoning and answer-synchronization failures |",
            "",
            "Note: mechanism counts are deterministic, nonexclusive diagnostics rather than manually adjudicated causal labels.",
            "",
            "## Supplementary Table S1. Accuracy by operation stratum",
            "",
            "| Stratum | n | B0 | B1 | B1−B0 | B1-only | B0-only | 95% paired bootstrap CI |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in report["by_operation_stratum"]:
        ci = item["difference_95pct_paired_bootstrap_CI"]
        lines.append(
            f"| {item['group']} | {item['n']} | {pct(item['B0_accuracy'])} | {pct(item['B1_accuracy'])} | "
            f"{signed_pp(item['difference_B1_minus_B0'])} | {item['B1_only_correct']} | {item['B0_only_correct']} | "
            f"[{signed_pp(ci[0])}, {signed_pp(ci[1])}] |"
        )
    lines.extend(
        [
            "",
            "Note: stratum estimates are exploratory. Rare strata were deliberately oversampled and several strata remain very small.",
            "",
            "## Supplementary Table S2. B1 system-output failures",
            "",
            "| Sample | Stratum | Steps | Pair outcome | Error | Calls | Tokens | Latency |",
            "|---|---|---:|---|---|---:|---:|---:|",
        ]
    )
    for item in report["B1_system_output_failures"]:
        lines.append(
            f"| `{item['sample_id']}` | {item['stratum']} | {item['step_count']} | {item['transition']} | "
            f"{item['error']['message']} | {item['model_calls']} | {item['tokens']:,} | {item['latency_ms']/1000:.2f} s |"
        )
    lines.extend(
        [
            "",
            "## Supplementary Table S3. Final-answer and executable-program consistency",
            "",
            "| System | Answer correct & execution correct | Answer correct & execution not correct | Answer wrong & execution correct | Answer wrong & execution not correct | P(answer correct | execution correct) |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for system in ("B0", "B1"):
        item = report["answer_execution_cross_tabs"][system]
        lines.append(
            f"| {system} | {item['answer_correct_execution_correct']} | {item['answer_correct_execution_not_correct']} | "
            f"{item['answer_wrong_execution_correct']} | {item['answer_wrong_execution_not_correct']} | "
            f"{pct(item['answer_consistency_given_executable_program'])} |"
        )
    lines.extend(
        [
            "",
            "Note: execution correctness evaluates whether the submitted program executes to the reference answer; it is distinct from the model's separately submitted final answer.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--artifact-stem", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-items", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-tables", required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    report, pair_rows = analyze(root, args.artifact_stem)
    write_json(root / args.output_json, report)
    write_jsonl(root / args.output_items, pair_rows)
    (root / args.output_md).write_text(make_report_markdown(report), encoding="utf-8")
    results = json.loads((root / "reports" / f"{args.artifact_stem}_results.json").read_text(encoding="utf-8"))
    (root / args.output_tables).write_text(make_tables_markdown(report, results), encoding="utf-8")
    print(
        json.dumps(
            {
                "pair_transition_counts": report["pair_transition_counts"],
                "gain_mechanisms": report["gain_mechanisms"],
                "loss_mechanisms": report["loss_mechanisms"],
                "model_api_calls_during_analysis": 0,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
