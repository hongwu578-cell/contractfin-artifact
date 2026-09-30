#!/usr/bin/env python3
"""Evaluate and analyze the frozen SCI held-out B0/B1 primary predictions."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from contractfin.evaluation import evaluate_files


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_mcnemar(b0: np.ndarray, b1: np.ndarray) -> dict[str, Any]:
    b0 = b0.astype(bool)
    b1 = b1.astype(bool)
    b1_only = int(np.sum(~b0 & b1))
    b0_only = int(np.sum(b0 & ~b1))
    discordant = b1_only + b0_only
    if discordant == 0:
        p_value = 1.0
    else:
        smaller = min(b1_only, b0_only)
        tail = sum(math.comb(discordant, k) for k in range(smaller + 1)) / (2**discordant)
        p_value = min(1.0, 2.0 * tail)
    return {
        "B1_correct_B0_wrong": b1_only,
        "B0_correct_B1_wrong": b0_only,
        "discordant_pairs": discordant,
        "p_value_two_sided_exact": p_value,
    }


def paired_bootstrap_difference(
    b0: np.ndarray,
    b1: np.ndarray,
    *,
    draws: int,
    seed: int,
) -> dict[str, Any]:
    differences = b1.astype(float) - b0.astype(float)
    rng = np.random.default_rng(seed)
    estimates = np.empty(draws, dtype=float)
    batch_size = 1000
    cursor = 0
    while cursor < draws:
        batch = min(batch_size, draws - cursor)
        indices = rng.integers(0, len(differences), size=(batch, len(differences)))
        estimates[cursor : cursor + batch] = differences[indices].mean(axis=1)
        cursor += batch
    lower, upper = np.quantile(estimates, [0.025, 0.975], method="linear")
    return {
        "method": "paired item percentile bootstrap",
        "draws": draws,
        "seed": seed,
        "point_estimate": float(differences.mean()),
        "ci_level": 0.95,
        "ci_lower": float(lower),
        "ci_upper": float(upper),
    }


def paired_sign_flip(
    b0: np.ndarray,
    b1: np.ndarray,
    *,
    draws: int,
    seed: int,
) -> dict[str, Any]:
    differences = b1.astype(float) - b0.astype(float)
    observed = float(differences.mean())
    rng = np.random.default_rng(seed)
    extreme = 0
    batch_size = 2000
    cursor = 0
    while cursor < draws:
        batch = min(batch_size, draws - cursor)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(batch, len(differences)))
        permuted = (signs * differences).mean(axis=1)
        extreme += int(np.sum(np.abs(permuted) >= abs(observed) - 1e-15))
        cursor += batch
    p_value = (extreme + 1) / (draws + 1)
    monte_carlo_se = math.sqrt(p_value * (1.0 - p_value) / (draws + 1))
    return {
        "method": "paired Monte Carlo sign-flip test",
        "draws": draws,
        "seed": seed,
        "point_estimate_B1_minus_B0": observed,
        "extreme_draws": extreme,
        "p_value_two_sided": p_value,
        "monte_carlo_standard_error": monte_carlo_se,
    }


def holm_adjust(raw_p_values: dict[str, float], alpha: float = 0.05) -> dict[str, dict[str, Any]]:
    ordered = sorted(raw_p_values.items(), key=lambda item: (item[1], item[0]))
    adjusted: dict[str, float] = {}
    running_max = 0.0
    m = len(ordered)
    for index, (name, p_value) in enumerate(ordered):
        candidate = min(1.0, (m - index) * p_value)
        running_max = max(running_max, candidate)
        adjusted[name] = running_max
    return {
        name: {
            "raw_p_value": raw_p_values[name],
            "holm_adjusted_p_value": adjusted[name],
            "reject_at_alpha_0_05": adjusted[name] <= alpha,
        }
        for name in raw_p_values
    }


def distribution(values: np.ndarray) -> dict[str, float]:
    q1, median, q3 = np.quantile(values.astype(float), [0.25, 0.5, 0.75], method="linear")
    return {
        "mean": float(np.mean(values)),
        "standard_deviation": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
        "minimum": float(np.min(values)),
        "q1": float(q1),
        "median": float(median),
        "q3": float(q3),
        "maximum": float(np.max(values)),
    }


def metric_arrays(results: list[dict[str, Any]]) -> dict[str, np.ndarray]:
    return {
        "final_answer_correctness": np.array([bool(item["answer_correct"]) for item in results]),
        "program_itt_correctness": np.array([item.get("program_correct") is True for item in results]),
        "execution_itt_correctness": np.array([item.get("execution_correct") is True for item in results]),
        "coverage": np.array([bool(item["answered"]) for item in results]),
        "evidence_item_f1": np.array([float(item["evidence"]["f1"]) for item in results]),
    }


def summarize_resources(
    records: list[dict[str, Any]],
    correctness: dict[str, dict[str, bool]],
) -> dict[str, Any]:
    by_system: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_system[record["system"]].append(record)

    result: dict[str, Any] = {}
    item_values: dict[str, dict[str, np.ndarray]] = {}
    for system in ("B0", "B1"):
        system_records = by_system[system]
        model_calls = np.array(
            [1 if system == "B0" else len(record.get("model_calls", [])) for record in system_records],
            dtype=float,
        )
        tool_calls = np.array([len(record.get("tool_calls", [])) for record in system_records], dtype=float)
        latency = np.array([float(record["latency_ms"]) for record in system_records])
        token_fields = {
            field: np.array([float(record["token_usage"][field]) for record in system_records])
            for field in ("input", "output", "reasoning", "total")
        }
        correct_count = sum(correctness[system][record["sample_id"]] for record in system_records)
        total_tokens = int(token_fields["total"].sum())
        total_latency = float(latency.sum())
        result[system] = {
            "items": len(system_records),
            "correct_answers": correct_count,
            "model_calls_total": int(model_calls.sum()),
            "model_calls_per_item": distribution(model_calls),
            "tool_calls_total": int(tool_calls.sum()),
            "tool_calls_per_item": distribution(tool_calls),
            "tokens": {
                field: {"total": int(values.sum()), "per_item": distribution(values)}
                for field, values in token_fields.items()
            },
            "latency_ms": {"total": total_latency, "per_item": distribution(latency)},
            "total_tokens_per_correct_answer": total_tokens / correct_count if correct_count else None,
            "total_latency_ms_per_correct_answer": total_latency / correct_count if correct_count else None,
        }
        item_values[system] = {
            "model_calls": model_calls,
            "tool_calls": tool_calls,
            "total_tokens": token_fields["total"],
            "latency_ms": latency,
        }

    paired_differences = {
        metric: distribution(item_values["B1"][metric] - item_values["B0"][metric])
        for metric in ("model_calls", "tool_calls", "total_tokens", "latency_ms")
    }
    return {"by_system": result, "paired_item_differences_B1_minus_B0": paired_differences}


def make_markdown(report: dict[str, Any]) -> str:
    primary = report["primary_analysis"]
    b0 = report["system_summaries"]["B0"]
    b1 = report["system_summaries"]["B1"]
    mcnemar = primary["mcnemar"]
    ci = primary["paired_bootstrap"]
    lines = [
        "# SCI held-out B0/B1 primary results",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Run ID: `{report['run_id']}`",
        f"- Registered paired items: {report['registered_items']}",
        f"- B0 accuracy: {b0['final_answer_accuracy']:.4f} ({b0['correct_answers']}/{report['registered_items']})",
        f"- B1 accuracy: {b1['final_answer_accuracy']:.4f} ({b1['correct_answers']}/{report['registered_items']})",
        f"- B1 minus B0: {ci['point_estimate']:+.4f} (95% paired bootstrap CI {ci['ci_lower']:+.4f} to {ci['ci_upper']:+.4f})",
        f"- Exact McNemar: B1-only={mcnemar['B1_correct_B0_wrong']}, B0-only={mcnemar['B0_correct_B1_wrong']}, p={mcnemar['p_value_two_sided_exact']:.6g}",
        "",
        "## Secondary family (Holm corrected)",
        "",
        "| Outcome | B0 | B1 | Difference | Raw p | Holm p | Reject |",
        "|---|---:|---:|---:|---:|---:|:---:|",
    ]
    for name in ("program_itt_correctness", "execution_itt_correctness", "coverage", "evidence_item_f1"):
        item = report["secondary_analysis"][name]
        holm = report["secondary_analysis"]["holm_family"][name]
        lines.append(
            f"| {name} | {item['B0_mean']:.4f} | {item['B1_mean']:.4f} | {item['difference_B1_minus_B0']:+.4f} | "
            f"{holm['raw_p_value']:.6g} | {holm['holm_adjusted_p_value']:.6g} | {'yes' if holm['reject_at_alpha_0_05'] else 'no'} |"
        )
    lines.extend(
        [
            "",
            "## Resources",
            "",
            f"- B0 model calls: {report['resources']['by_system']['B0']['model_calls_total']}",
            f"- B1 model calls: {report['resources']['by_system']['B1']['model_calls_total']}",
            f"- B0 total tokens: {report['resources']['by_system']['B0']['tokens']['total']['total']}",
            f"- B1 total tokens: {report['resources']['by_system']['B1']['tokens']['total']['total']}",
            "",
            "All error, abstain, and missing outputs are retained as incorrect under the registered ITT rule.",
            "",
        ]
    )
    return "\n".join(lines)


def analyze(root: Path, stem: str, structural_gate_path: Path) -> dict[str, Any]:
    gate = json.loads(structural_gate_path.read_text(encoding="utf-8"))
    if gate.get("decision", {}).get("passed") is not True or gate.get("decision", {}).get("unblinding_permitted") is not True:
        raise RuntimeError("structural gate did not permit unblinding")

    gold_path = root / "data/heldout/finqa_test500_gold_v1.jsonl"
    manifest_path = root / "config/sci_finqa_test500_manifest_v1.json"
    log_path = root / "logs" / f"{stem}_tasks.jsonl"
    prediction_paths = {
        system: root / "reports" / f"{stem}_{system}_predictions.jsonl" for system in ("B0", "B1")
    }
    evaluation_paths = {
        system: root / "reports" / f"{stem}_{system}_evaluation.json" for system in ("B0", "B1")
    }

    # Reconfirm the frozen prediction hashes before opening gold.
    for system in ("B0", "B1"):
        expected = gate["prediction_files"][system]["sha256"]
        actual = sha256_file(prediction_paths[system])
        if actual != expected:
            raise RuntimeError(f"{system} prediction hash changed after the structural gate")

    evaluations = {
        system: evaluate_files(gold_path, prediction_paths[system], evaluation_paths[system])
        for system in ("B0", "B1")
    }
    by_system_id = {
        system: {item["sample_id"]: item for item in evaluations[system]["results"]}
        for system in ("B0", "B1")
    }
    gold_order = [item["sample_id"] for item in read_jsonl(gold_path)]
    if any(set(by_system_id[system]) != set(gold_order) for system in ("B0", "B1")):
        raise RuntimeError("evaluation sample identities do not match the registered gold set")
    ordered_results = {
        system: [by_system_id[system][sample_id] for sample_id in gold_order] for system in ("B0", "B1")
    }
    metrics = {system: metric_arrays(ordered_results[system]) for system in ("B0", "B1")}

    primary_mcnemar = exact_mcnemar(
        metrics["B0"]["final_answer_correctness"], metrics["B1"]["final_answer_correctness"]
    )
    primary_bootstrap = paired_bootstrap_difference(
        metrics["B0"]["final_answer_correctness"],
        metrics["B1"]["final_answer_correctness"],
        draws=10_000,
        seed=20260929,
    )

    secondary: dict[str, Any] = {}
    raw_p_values: dict[str, float] = {}
    for name in ("program_itt_correctness", "execution_itt_correctness", "coverage"):
        test = exact_mcnemar(metrics["B0"][name], metrics["B1"][name])
        raw_p_values[name] = test["p_value_two_sided_exact"]
        secondary[name] = {
            "B0_mean": float(np.mean(metrics["B0"][name])),
            "B1_mean": float(np.mean(metrics["B1"][name])),
            "difference_B1_minus_B0": float(np.mean(metrics["B1"][name]) - np.mean(metrics["B0"][name])),
            "test": test,
        }
    evidence_test = paired_sign_flip(
        metrics["B0"]["evidence_item_f1"],
        metrics["B1"]["evidence_item_f1"],
        draws=100_000,
        seed=20260930,
    )
    raw_p_values["evidence_item_f1"] = evidence_test["p_value_two_sided"]
    secondary["evidence_item_f1"] = {
        "B0_mean": float(np.mean(metrics["B0"]["evidence_item_f1"])),
        "B1_mean": float(np.mean(metrics["B1"]["evidence_item_f1"])),
        "difference_B1_minus_B0": evidence_test["point_estimate_B1_minus_B0"],
        "test": evidence_test,
    }
    secondary["holm_family"] = holm_adjust(raw_p_values)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    stratum_by_id = {item["sample_id"]: item["stratum"] for item in manifest["samples"]}
    strata = sorted(manifest["selection_rule"]["eligible_pool_counts"])
    stratified: dict[str, Any] = {}
    weighted_metrics = {
        metric: {"B0": 0.0, "B1": 0.0} for metric in metrics["B0"]
    }
    population_total = sum(manifest["selection_rule"]["eligible_pool_counts"].values())
    for stratum in strata:
        indices = np.array([index for index, sample_id in enumerate(gold_order) if stratum_by_id[sample_id] == stratum])
        population_count = manifest["selection_rule"]["eligible_pool_counts"][stratum]
        weight = population_count / population_total
        metric_means: dict[str, Any] = {}
        for metric in metrics["B0"]:
            b0_mean = float(np.mean(metrics["B0"][metric][indices]))
            b1_mean = float(np.mean(metrics["B1"][metric][indices]))
            metric_means[metric] = {
                "B0": b0_mean,
                "B1": b1_mean,
                "difference_B1_minus_B0": b1_mean - b0_mean,
            }
            weighted_metrics[metric]["B0"] += weight * b0_mean
            weighted_metrics[metric]["B1"] += weight * b1_mean
        stratified[stratum] = {
            "registered_n": int(len(indices)),
            "FinQA_test_population_n": population_count,
            "population_weight": weight,
            "metrics": metric_means,
        }
    population_weighted = {
        metric: {
            "B0": values["B0"],
            "B1": values["B1"],
            "difference_B1_minus_B0": values["B1"] - values["B0"],
        }
        for metric, values in weighted_metrics.items()
    }

    records = read_jsonl(log_path)
    correctness = {
        system: {
            item["sample_id"]: bool(item["answer_correct"]) for item in ordered_results[system]
        }
        for system in ("B0", "B1")
    }
    resource_summary = summarize_resources(records, correctness)
    resource_parts = resource_summary["by_system"]
    paired_resource_records = []
    by_sample_record: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        by_sample_record[record["sample_id"]][record["system"]] = record
    for sample_id in gold_order:
        paired_resource_records.extend([by_sample_record[sample_id]["B0"], by_sample_record[sample_id]["B1"]])
    paired_resources = summarize_resources(
        paired_resource_records,
        correctness,
    )["paired_item_differences_B1_minus_B0"]

    run_ids = {record["run_id"] for record in records}
    system_summaries = {}
    for system in ("B0", "B1"):
        summary = evaluations[system]["summary"]
        system_summaries[system] = {
            **summary,
            "correct_answers": int(sum(metrics[system]["final_answer_correctness"])),
        }

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "protocol_id": manifest["protocol_id"],
        "run_id": next(iter(run_ids)) if len(run_ids) == 1 else sorted(run_ids),
        "registered_items": len(gold_order),
        "analysis_policy": {
            "intention_to_test": True,
            "errors_abstentions_and_missing_scored_incorrect": True,
            "primary_alpha": 0.05,
            "primary_bootstrap_draws": 10_000,
            "primary_bootstrap_seed": 20260929,
            "evidence_sign_flip_draws": 100_000,
            "evidence_sign_flip_seed": 20260930,
            "secondary_adjustment": "Holm across four frozen outcomes",
        },
        "system_summaries": system_summaries,
        "primary_analysis": {
            "outcome": "final_answer_correctness",
            "B0_accuracy": float(np.mean(metrics["B0"]["final_answer_correctness"])),
            "B1_accuracy": float(np.mean(metrics["B1"]["final_answer_correctness"])),
            "mcnemar": primary_mcnemar,
            "paired_bootstrap": primary_bootstrap,
            "significant_at_alpha_0_05": primary_mcnemar["p_value_two_sided_exact"] <= 0.05,
        },
        "secondary_analysis": secondary,
        "stratified_descriptive": stratified,
        "FinQA_test_population_weighted_secondary": {
            "population_n": population_total,
            "metrics": population_weighted,
        },
        "resources": {
            "by_system": resource_parts,
            "paired_item_differences_B1_minus_B0": paired_resources,
        },
        "error_type_counts": {
            system: dict(Counter(
                record["error"]["message"]
                for record in records
                if record["system"] == system and record.get("error")
            ))
            for system in ("B0", "B1")
        },
        "artifacts": {
            "structural_gate": str(structural_gate_path.relative_to(root)),
            "structural_gate_sha256": sha256_file(structural_gate_path),
            "gold": str(gold_path.relative_to(root)),
            "gold_sha256": sha256_file(gold_path),
            "manifest": str(manifest_path.relative_to(root)),
            "manifest_sha256": sha256_file(manifest_path),
            "predictions": {
                system: {
                    "path": str(prediction_paths[system].relative_to(root)),
                    "sha256": sha256_file(prediction_paths[system]),
                }
                for system in ("B0", "B1")
            },
            "evaluations": {
                system: {
                    "path": str(evaluation_paths[system].relative_to(root)),
                    "sha256": sha256_file(evaluation_paths[system]),
                }
                for system in ("B0", "B1")
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--artifact-stem", required=True)
    parser.add_argument("--structural-gate", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    structural_gate_path = root / args.structural_gate
    report = analyze(root, args.artifact_stem, structural_gate_path)
    json_path = root / args.output_json
    md_path = root / args.output_md
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(make_markdown(report), encoding="utf-8")
    print(json.dumps(report["primary_analysis"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
