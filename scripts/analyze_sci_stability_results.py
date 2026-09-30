#!/usr/bin/env python3
"""Evaluate the preregistered 100-item, three-run SCI stability experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from contractfin.evaluation import aggregate_results, evaluate_one


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ("B0", "B1")
REPLICATES = (1, 2, 3)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def distribution(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    q1, median, q3 = np.quantile(array, [0.25, 0.5, 0.75], method="linear")
    return {
        "mean": float(np.mean(array)),
        "standard_deviation": float(np.std(array, ddof=1)) if len(array) > 1 else 0.0,
        "minimum": float(np.min(array)),
        "q1": float(q1),
        "median": float(median),
        "q3": float(q3),
        "maximum": float(np.max(array)),
    }


def within_item_cv(values: list[float]) -> float:
    array = np.asarray(values, dtype=float)
    mean = float(np.mean(array))
    if mean == 0.0:
        return 0.0 if np.all(array == 0.0) else float("nan")
    return float(np.std(array, ddof=1) / mean)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# SCI held-out stability results",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Stability items: {report['registered_items']}",
        f"- Total observations: {report['registered_items'] * 3 * 2}",
        "- Interpretation: descriptive; additional replicates are not pooled into the primary test.",
        "",
        "## Replicate accuracies",
        "",
        "| System | R1 | R2 | R3 |",
        "|---|---:|---:|---:|",
    ]
    for system in SYSTEMS:
        per_rep = report["systems"][system]["replicate_accuracy"]
        lines.append(
            f"| {system} | {per_rep['R1']['correct']}/100 ({per_rep['R1']['accuracy']:.1%}) | "
            f"{per_rep['R2']['correct']}/100 ({per_rep['R2']['accuracy']:.1%}) | "
            f"{per_rep['R3']['correct']}/100 ({per_rep['R3']['accuracy']:.1%}) |"
        )
    lines.extend(
        [
            "",
            "## Three-run stability",
            "",
            "| Outcome | B0 | B1 |",
            "|---|---:|---:|",
        ]
    )
    for successes in range(4):
        lines.append(
            f"| Items correct in {successes}/3 runs | "
            f"{report['systems']['B0']['success_frequency'][str(successes)]} | "
            f"{report['systems']['B1']['success_frequency'][str(successes)]} |"
        )
    for field, label in (
        ("items_with_any_correctness_change", "Items with any correctness change"),
        ("token_cv", "Median within-item token CV (IQR)"),
        ("latency_cv", "Median within-item latency CV (IQR)"),
    ):
        if field == "items_with_any_correctness_change":
            b0 = report["systems"]["B0"][field]
            b1 = report["systems"]["B1"][field]
            b0_text = f"{b0['count']} ({b0['proportion']:.1%})"
            b1_text = f"{b1['count']} ({b1['proportion']:.1%})"
        else:
            b0 = report["systems"]["B0"]["within_item_dispersion"][field]
            b1 = report["systems"]["B1"]["within_item_dispersion"][field]
            b0_text = f"{b0['median']:.3f} ({b0['q1']:.3f}–{b0['q3']:.3f})"
            b1_text = f"{b1['median']:.3f} ({b1['q1']:.3f}–{b1['q3']:.3f})"
        lines.append(f"| {label} | {b0_text} | {b1_text} |")
    lines.extend(
        [
            "",
            "CV is the sample standard deviation across R1–R3 divided by the three-run mean for each item; the table reports the median and interquartile range across 100 items.",
            "",
            "## System-output failures in the two additional replicates",
            "",
        ]
    )
    for system in SYSTEMS:
        lines.append(f"- {system}: {report['systems'][system]['additional_replicate_errors']} errors across R2–R3.")
    lines.append("")
    return "\n".join(lines)


def analyze(root: Path, stability_gate_rel: str, primary_gate_rel: str) -> dict[str, Any]:
    stability_gate_path = root / stability_gate_rel
    primary_gate_path = root / primary_gate_rel
    stability_gate = json.loads(stability_gate_path.read_text(encoding="utf-8"))
    primary_gate = json.loads(primary_gate_path.read_text(encoding="utf-8"))
    if stability_gate.get("decision", {}).get("unblinding_permitted") is not True:
        raise RuntimeError("stability structural gate did not permit unblinding")
    if primary_gate.get("decision", {}).get("passed") is not True:
        raise RuntimeError("primary structural gate is not valid")

    manifest_path = root / "config/sci_finqa_test500_manifest_v1.json"
    gold_path = root / "data/heldout/finqa_test500_gold_v1.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sample_ids = list(manifest["stability_subset"]["sample_ids"])
    if len(sample_ids) != 100 or len(set(sample_ids)) != 100:
        raise RuntimeError("registered stability subset is not 100 unique items")

    primary_prediction_paths = {
        system: root / "reports" / f"sci_finqa_test500_primary_v1_rerun1_{system}_predictions.jsonl"
        for system in SYSTEMS
    }
    stability_prediction_paths = {
        (system, replicate): root / "reports" / f"sci_finqa_stability100_v1_{system}_R{replicate}_predictions.jsonl"
        for system in SYSTEMS
        for replicate in (2, 3)
    }
    for system, path in primary_prediction_paths.items():
        if sha256_file(path) != primary_gate["prediction_files"][system]["sha256"]:
            raise RuntimeError(f"{system} primary prediction hash changed")
    for (system, replicate), path in stability_prediction_paths.items():
        key = f"{system}_R{replicate}"
        if sha256_file(path) != stability_gate["prediction_files"][key]["sha256"]:
            raise RuntimeError(f"{key} stability prediction hash changed")

    # Gold is opened only after both structural decisions and all prediction-hash checks.
    gold_by_id = {item["sample_id"]: item for item in read_jsonl(gold_path)}
    if not set(sample_ids).issubset(gold_by_id):
        raise RuntimeError("one or more stability IDs are absent from gold")

    predictions: dict[tuple[str, int], dict[str, dict[str, Any]]] = {}
    for system in SYSTEMS:
        primary_items = read_jsonl(primary_prediction_paths[system])
        predictions[(system, 1)] = {item["sample_id"]: item for item in primary_items if item.get("sample_id") in set(sample_ids)}
        for replicate in (2, 3):
            items = read_jsonl(stability_prediction_paths[(system, replicate)])
            predictions[(system, replicate)] = {item["sample_id"]: item for item in items}

    evaluations: dict[tuple[str, int], dict[str, Any]] = {}
    evaluation_paths: dict[tuple[str, int], Path] = {}
    for system in SYSTEMS:
        for replicate in REPLICATES:
            group_predictions = predictions[(system, replicate)]
            if set(group_predictions) != set(sample_ids):
                raise RuntimeError(f"{system}_R{replicate} prediction identities do not match the subset")
            results = [evaluate_one(gold_by_id[sample_id], group_predictions[sample_id]) for sample_id in sample_ids]
            evaluation = {
                "schema_version": "1.0",
                "system": system,
                "replicate": replicate,
                "subset": "registered_stability100",
                "summary": aggregate_results(results),
                "results": results,
            }
            path = root / "reports" / f"sci_finqa_stability100_v1_{system}_R{replicate}_evaluation.json"
            write_json(path, evaluation)
            evaluations[(system, replicate)] = evaluation
            evaluation_paths[(system, replicate)] = path

    primary_log_path = root / "logs/sci_finqa_test500_primary_v1_rerun1_tasks.jsonl"
    stability_log_path = root / "logs/sci_finqa_stability100_v1_tasks.jsonl"
    records: dict[tuple[str, int, str], dict[str, Any]] = {}
    subset = set(sample_ids)
    for record in read_jsonl(primary_log_path):
        if record.get("sample_id") in subset:
            records[(record["system"], 1, record["sample_id"])] = record
    for record in read_jsonl(stability_log_path):
        records[(record["system"], int(record["replicate"]), record["sample_id"])] = record
    if len(records) != 600:
        raise RuntimeError(f"expected 600 system-replicate-item resource records, found {len(records)}")

    systems: dict[str, Any] = {}
    item_level: dict[str, dict[str, Any]] = {system: {} for system in SYSTEMS}
    for system in SYSTEMS:
        correctness_by_rep: dict[int, dict[str, bool]] = {}
        replicate_accuracy: dict[str, Any] = {}
        for replicate in REPLICATES:
            group_results = evaluations[(system, replicate)]["results"]
            correctness_by_rep[replicate] = {
                item["sample_id"]: bool(item["answer_correct"]) for item in group_results
            }
            correct = sum(correctness_by_rep[replicate].values())
            replicate_accuracy[f"R{replicate}"] = {"correct": correct, "total": 100, "accuracy": correct / 100}

        success_frequency: Counter[int] = Counter()
        changed = 0
        token_cvs: list[float] = []
        latency_cvs: list[float] = []
        for sample_id in sample_ids:
            correctness = [correctness_by_rep[replicate][sample_id] for replicate in REPLICATES]
            successes = sum(correctness)
            success_frequency[successes] += 1
            changed += int(len(set(correctness)) > 1)
            tokens = [float(records[(system, replicate, sample_id)]["token_usage"]["total"]) for replicate in REPLICATES]
            latency = [float(records[(system, replicate, sample_id)]["latency_ms"]) for replicate in REPLICATES]
            token_cv = within_item_cv(tokens)
            latency_cv = within_item_cv(latency)
            token_cvs.append(token_cv)
            latency_cvs.append(latency_cv)
            item_level[system][sample_id] = {
                "correctness_R1_R2_R3": correctness,
                "successes": successes,
                "tokens_R1_R2_R3": [int(value) for value in tokens],
                "latency_ms_R1_R2_R3": [int(value) for value in latency],
                "token_cv": token_cv,
                "latency_cv": latency_cv,
            }

        additional_records = [
            records[(system, replicate, sample_id)]
            for replicate in (2, 3)
            for sample_id in sample_ids
        ]
        systems[system] = {
            "replicate_accuracy": replicate_accuracy,
            "success_frequency": {str(value): success_frequency[value] for value in range(4)},
            "items_with_any_correctness_change": {"count": changed, "proportion": changed / 100},
            "within_item_dispersion": {
                "definition": "sample standard deviation across R1-R3 divided by the three-run mean, summarized across items",
                "token_cv": distribution(token_cvs),
                "latency_cv": distribution(latency_cvs),
            },
            "additional_replicate_errors": sum(record.get("error") is not None for record in additional_records),
            "additional_replicate_model_calls": sum(
                1 if system == "B0" else len(record.get("model_calls", [])) for record in additional_records
            ),
            "additional_replicate_total_tokens": sum(int(record["token_usage"]["total"]) for record in additional_records),
        }

    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "protocol_id": manifest["protocol_id"],
        "registered_items": 100,
        "analysis_policy": {
            "descriptive_only": True,
            "primary_results_pooled": False,
            "errors_abstentions_and_missing_scored_incorrect": True,
            "replicates": [1, 2, 3],
            "cv_definition": "sample standard deviation across three runs divided by the three-run mean",
        },
        "systems": systems,
        "item_level": item_level,
        "artifacts": {
            "stability_structural_gate": {"path": stability_gate_rel, "sha256": sha256_file(stability_gate_path)},
            "primary_structural_gate": {"path": primary_gate_rel, "sha256": sha256_file(primary_gate_path)},
            "manifest": {"path": str(manifest_path.relative_to(root)), "sha256": sha256_file(manifest_path)},
            "gold": {"path": str(gold_path.relative_to(root)), "sha256": sha256_file(gold_path)},
            "primary_log": {"path": str(primary_log_path.relative_to(root)), "sha256": sha256_file(primary_log_path)},
            "stability_log": {"path": str(stability_log_path.relative_to(root)), "sha256": sha256_file(stability_log_path)},
            "evaluations": {
                f"{system}_R{replicate}": {
                    "path": str(evaluation_paths[(system, replicate)].relative_to(root)),
                    "sha256": sha256_file(evaluation_paths[(system, replicate)]),
                }
                for system in SYSTEMS
                for replicate in REPLICATES
            },
        },
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--stability-structural-gate",
        default="reports/sci_finqa_stability100_v1_structural_gate.json",
    )
    parser.add_argument(
        "--primary-structural-gate",
        default="reports/sci_finqa_test500_primary_v1_rerun1_structural_gate.json",
    )
    parser.add_argument("--output-json", default="reports/sci_finqa_stability100_v1_results.json")
    parser.add_argument("--output-md", default="reports/sci_finqa_stability100_v1_results.md")
    args = parser.parse_args()

    root = args.root.resolve()
    report = analyze(root, args.stability_structural_gate, args.primary_structural_gate)
    json_path = root / args.output_json
    md_path = root / args.output_md
    write_json(json_path, report)
    md_path.write_text(make_markdown(report), encoding="utf-8")
    print(json.dumps({system: report["systems"][system] for system in SYSTEMS}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
