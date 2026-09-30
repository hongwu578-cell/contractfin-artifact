#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.b0 import PROMPT_VERSION, SYSTEM_PROMPT  # noqa: E402
from contractfin.b1 import B1_PROMPT_VERSION, B1_SYSTEM_PROMPT  # noqa: E402
from contractfin.heldout import (  # noqa: E402
    HELDOUT_PROTOCOL_ID,
    REGISTRATION_DATE,
    audit_heldout_artifacts,
    build_heldout_manifest,
    build_interleaved_schedule,
    build_power_sensitivity,
    build_stability_schedule,
    split_selected_records,
)
from contractfin.utils import (  # noqa: E402
    atomic_write_text,
    read_jsonl,
    sha256_file,
    write_json,
    write_jsonl,
)


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def render_power_markdown(power: dict[str, Any]) -> str:
    lines = [
        "# Exact McNemar power sensitivity",
        "",
        "This is a design-sensitivity table, not an observed-result analysis.",
        "Power is computed for the two-sided exact conditional McNemar test at alpha = 0.05.",
        "",
        "| Scenario | n | Total discordance | B1−B0 net difference | Exact power |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in power["rows"]:
        lines.append(
            f"| {row['scenario']} | {row['n']} | {row['total_discordance']:.3f} | "
            f"{row['net_accuracy_difference_B1_minus_B0']:.3f} | {row['exact_unconditional_power']:.4f} |"
        )
    return "\n".join(lines) + "\n"


def render_manifest_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# FinQA held-out 500-item manifest",
        "",
        f"- Protocol: `{manifest['protocol_id']}`",
        f"- Registration date: `{manifest['registration_date']}`",
        f"- Source test SHA-256: `{manifest['source']['normalized_file_sha256']}`",
        f"- Primary items: `{manifest['selection_rule']['selected_count']}`",
        f"- Stability items: `{manifest['stability_subset']['selected_count']}`",
        "- Substitution: prohibited",
        "- Gold answers and programs are intentionally omitted from this review document.",
        "",
        "## Frozen allocation",
        "",
        "| Stratum | Eligible | Minimum | Final |",
        "|---|---:|---:|---:|",
    ]
    pools = manifest["selection_rule"]["eligible_pool_counts"]
    minima = manifest["selection_rule"]["minimum_quotas"]
    quotas = manifest["selection_rule"]["final_quotas"]
    for stratum in sorted(pools):
        lines.append(f"| `{stratum}` | {pools[stratum]} | {minima.get(stratum, 0)} | {quotas[stratum]} |")
    lines.extend(
        [
            "",
            "## Frozen execution list",
            "",
            "| Order | Sample ID | Stratum | Steps | Stability | Question |",
            "|---:|---|---|---:|:---:|---|",
        ]
    )
    for item in sorted(manifest["samples"], key=lambda value: value["run_order"]):
        question = str(item["question"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {item['run_order']} | `{item['sample_id']}` | `{item['stratum']}` | "
            f"{item['step_count']} | {'yes' if item['in_stability_subset'] else ''} | {question} |"
        )
    return "\n".join(lines) + "\n"


def power_csv(power: dict[str, Any]) -> str:
    buffer = io.StringIO(newline="")
    fieldnames = list(power["rows"][0])
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(power["rows"])
    return buffer.getvalue()


def main() -> int:
    root = PROJECT_ROOT
    source_path = root / "data" / "normalized" / "finqa_test.jsonl"
    manifest_path = root / "config" / "sci_finqa_test500_manifest_v1.json"
    inference_path = root / "data" / "heldout" / "finqa_test500_inference_v1.jsonl"
    gold_path = root / "data" / "heldout" / "finqa_test500_gold_v1.jsonl"
    schedule_path = root / "config" / "sci_finqa_test500_interleaved_schedule_v1.jsonl"
    stability_schedule_path = root / "config" / "sci_finqa_stability100_interleaved_schedule_v1.jsonl"
    runtime_path = root / "config" / "sci_heldout_runtime_v1.json"
    stability_runtime_path = root / "config" / "sci_heldout_stability_runtime_v1.json"
    prereg_path = root / "config" / "sci_heldout_preregistration_v1.json"
    manifest_review_path = root / "reports" / "sci_finqa_test500_manifest_v1.md"
    prereg_review_path = root / "reports" / "sci_heldout_preregistration_v1.md"
    power_json_path = root / "reports" / "sci_exact_mcnemar_power_v1.json"
    power_csv_path = root / "reports" / "sci_exact_mcnemar_power_v1.csv"
    power_md_path = root / "reports" / "sci_exact_mcnemar_power_v1.md"
    audit_path = root / "reports" / "sci_heldout_local_audit_v1.json"

    samples = list(read_jsonl(source_path))
    source_sha = sha256_file(source_path)
    manifest = build_heldout_manifest(samples, dataset_sha256=source_sha)
    inference, gold = split_selected_records(samples, manifest)
    schedule = build_interleaved_schedule(manifest)
    stability_schedule = build_stability_schedule(manifest)
    write_jsonl(inference_path, inference)
    write_jsonl(gold_path, gold)
    write_jsonl(schedule_path, schedule)
    write_jsonl(stability_schedule_path, stability_schedule)

    runtime = {
        "schema_version": "1.0",
        "protocol_id": HELDOUT_PROTOCOL_ID,
        "status": "frozen_confirmed_no_live_api_authorization",
        "live_api_authorized": False,
        "requested_provider": "deepseek",
        "requested_model": "deepseek-flash",
        "inference_artifact": {
            "path": str(inference_path.relative_to(root)),
            "sha256": sha256_file(inference_path),
            "record_count": len(inference),
        },
        "schedule_artifact": {
            "path": str(schedule_path.relative_to(root)),
            "sha256": sha256_file(schedule_path),
            "task_count": len(schedule),
        },
        "B0": {
            "label": "Direct LLM",
            "prompt_version": PROMPT_VERSION,
            "system_prompt_sha256": text_sha256(SYSTEM_PROMPT),
            "max_output_tokens": 32768,
            "request_timeout_seconds": 300,
            "automatic_retries": 0,
        },
        "B1": {
            "label": "Tool-Augmented Single Agent",
            "prompt_version": B1_PROMPT_VERSION,
            "system_prompt_sha256": text_sha256(B1_SYSTEM_PROMPT),
            "total_output_budget": 32768,
            "max_model_calls": 6,
            "max_tool_calls": 8,
            "request_timeout_seconds": 300,
            "automatic_retries": 0,
        },
        "execution_policy": {
            "strict_schedule_order": True,
            "store_provider_responses": False,
            "semantic_retries": 0,
            "evaluation_in_inference_process": False,
            "resume_only_skips_already_logged_tasks": True,
        },
    }
    write_json(runtime_path, runtime)
    stability_runtime = json.loads(json.dumps(runtime))
    stability_runtime["status"] = "frozen_confirmed_stability_no_live_api_authorization"
    stability_runtime["schedule_artifact"] = {
        "path": str(stability_schedule_path.relative_to(root)),
        "sha256": sha256_file(stability_schedule_path),
        "task_count": len(stability_schedule),
    }
    stability_runtime["execution_policy"]["replicates"] = [2, 3]
    stability_runtime["execution_policy"]["primary_results_pooled"] = False
    write_json(stability_runtime_path, stability_runtime)

    manifest["artifacts"] = {
        "inference": {"path": str(inference_path.relative_to(root)), "sha256": sha256_file(inference_path)},
        "gold": {"path": str(gold_path.relative_to(root)), "sha256": sha256_file(gold_path)},
        "schedule": {"path": str(schedule_path.relative_to(root)), "sha256": sha256_file(schedule_path)},
        "runtime_config": {"path": str(runtime_path.relative_to(root)), "sha256": sha256_file(runtime_path)},
        "stability_schedule": {"path": str(stability_schedule_path.relative_to(root)), "sha256": sha256_file(stability_schedule_path)},
        "stability_runtime_config": {"path": str(stability_runtime_path.relative_to(root)), "sha256": sha256_file(stability_runtime_path)},
    }
    write_json(manifest_path, manifest)
    atomic_write_text(manifest_review_path, render_manifest_markdown(manifest))

    power = build_power_sensitivity()
    write_json(power_json_path, power)
    atomic_write_text(power_csv_path, power_csv(power))
    atomic_write_text(power_md_path, render_power_markdown(power))

    prereg = {
        "schema_version": "1.0",
        "protocol_id": HELDOUT_PROTOCOL_ID,
        "registration_date": REGISTRATION_DATE,
        "status": "frozen_confirmed_no_live_api_authorization",
        "paper_title": "Tool Use Before Teamwork: A Cost-Aware and Auditable Evaluation of LLM Architectures for Financial Numerical Reasoning",
        "research_question": "Does deterministic tool augmentation improve paired held-out financial numerical reasoning performance over direct generation under matched provider, model alias, item set, and output ceiling?",
        "confirmatory_hypothesis": "B1 and B0 have unequal item-level final-answer correctness; the expected direction is B1 greater than B0, but the primary test is two-sided.",
        "exploratory_boundary": "B2-v1 and B2-v1.1 are frozen development failures used only for mechanism-oriented error analysis; they are excluded from confirmatory held-out testing.",
        "artifacts": {
            "source_test": {"path": str(source_path.relative_to(root)), "sha256": source_sha, "record_count": len(samples)},
            "manifest": {"path": str(manifest_path.relative_to(root)), "sha256": sha256_file(manifest_path)},
            "inference": manifest["artifacts"]["inference"],
            "gold": manifest["artifacts"]["gold"],
            "schedule": manifest["artifacts"]["schedule"],
            "runtime_config": manifest["artifacts"]["runtime_config"],
            "stability_schedule": manifest["artifacts"]["stability_schedule"],
            "stability_runtime_config": manifest["artifacts"]["stability_runtime_config"],
            "power_table": {"path": str(power_json_path.relative_to(root)), "sha256": sha256_file(power_json_path)},
        },
        "sampling": manifest["selection_rule"],
        "stability_subset": manifest["stability_subset"],
        "systems": {
            "primary_runtime": runtime,
            "stability_runtime": stability_runtime,
        },
        "blinding": {
            "inference_process_reads": ["runtime_config", "answer-stripped inference JSONL", "interleaved schedule JSONL"],
            "inference_process_never_reads": ["gold JSONL", "normalized source test JSONL", "development outcomes"],
            "evaluation_starts_only_after": ["all prediction files are immutable", "prediction SHA-256 values are recorded", "sample identity and uniqueness gates pass"],
            "gold_evaluation_contents": "reference answers, programs, evidence identifiers, and document tables required for deterministic program execution; never loaded by either inference runtime",
        },
        "outcomes": {
            "primary": "paired final-answer correctness with missing, abstain, and error outputs scored incorrect",
            "secondary_family": {
                "program_itt_correctness": "exact program match; missing or invalid program is false; denominator is all 500 registered items",
                "execution_itt_correctness": "predicted program executes to the gold answer; missing, invalid, or non-executing program is false; denominator is all 500 registered items",
                "evidence_item_f1": "official evidence-identifier F1 computed per item, including zero values",
                "coverage": "status equals answered; denominator is all 500 registered items",
            },
            "resource": ["model calls", "tool calls", "input/output/reasoning/total tokens", "latency", "tokens and latency per correct answer"],
            "stability": ["item-level success frequency over three total replicates", "token dispersion", "latency dispersion"],
        },
        "statistical_analysis": {
            "primary_test": "two-sided exact conditional McNemar test at alpha 0.05",
            "primary_effect": "paired B1-minus-B0 accuracy difference with 95% paired bootstrap CI",
            "bootstrap": {"replicates": 10000, "seed": 20260929, "resampling_unit": "paired item"},
            "secondary_tests": {
                "program_itt_correctness": "two-sided exact McNemar",
                "execution_itt_correctness": "two-sided exact McNemar",
                "coverage": "two-sided exact McNemar",
                "evidence_item_f1": "paired Monte Carlo sign-flip test with 100,000 draws and seed 20260930",
            },
            "secondary_multiplicity": "Holm correction across the four frozen secondary p-values",
            "stratified_reporting": "descriptive operation-stratum estimates; no underpowered stratum significance claims",
            "population_weighted_secondary": "weight each registered stratum by its prevalence in all 1,147 FinQA test items",
            "development_p_values": "prohibited",
            "sequential_testing": "none",
        },
        "failure_policy": {
            "automatic_retries": 0,
            "semantic_retries": 0,
            "item_specific_prompt_changes": "prohibited",
            "sample_substitution": "prohibited",
            "errors_in_primary_itt": "scored incorrect",
            "infrastructure_failure_definition": "no HTTP response, provider 5xx/429, connection failure, or provider-side timeout before a completed response; schema-invalid and semantically wrong model outputs are system failures, not infrastructure failures",
            "structural_invalidation": "if either system has more than 2% infrastructure failures or the between-system infrastructure-failure-rate difference exceeds 1 percentage point, stop before unblinding; any rerun requires a dated amendment and reruns the full paired primary schedule, never selected items",
            "returned_model_drift": "record every returned model identifier; any within-pair identifier mismatch is a protocol deviation reported before unblinding, and more than 1% mismatched pairs triggers the same structural-invalidation rule",
        },
        "acceptance_gates_before_unblinding": {
            "unique_predictions_per_system": 500,
            "duplicate_predictions": 0,
            "schedule_tasks_logged": 1000,
            "first_system_balance": {"B0": 250, "B1": 250},
            "sample_identity_match": True,
            "runtime_hash_match": True,
            "prediction_files_hashed": True,
            "accuracy_is_a_structural_gate": False,
        },
        "call_budget_not_authorized": {
            "primary_expected": 2067,
            "primary_ceiling": 3500,
            "stability_two_additional_replicates_expected": 827,
            "stability_two_additional_replicates_ceiling": 1400,
            "grand_expected": 2894,
            "grand_ceiling": 4900,
            "current_authorization": 0,
        },
        "commands": {
            "rebuild_and_verify_local_artifacts": "PYTHONPATH=src python3 scripts/prepare_sci_heldout.py",
            "local_no_network_dry_run": "PYTHONPATH=src python3 scripts/run_sci_heldout.py --runtime-config config/sci_heldout_runtime_v1.json --mode dry-run",
            "future_primary_live_run_blocked": "PYTHONPATH=src python3 scripts/run_sci_heldout.py --runtime-config config/sci_heldout_runtime_v1.json --mode live --artifact-stem sci_finqa_test500_primary_v1 --authorization-amendment <dated-primary-authorization.json>",
            "future_stability_live_run_blocked": "PYTHONPATH=src python3 scripts/run_sci_heldout.py --runtime-config config/sci_heldout_stability_runtime_v1.json --mode live --artifact-stem sci_finqa_stability100_v1 --authorization-amendment <dated-stability-authorization.json>",
            "future_live_command_status": "blocked until a separate dated authorization file binds explicit scope to the frozen runtime SHA-256 after explicit user authorization; the frozen runtime itself is never edited",
        },
    }
    write_json(prereg_path, prereg)

    audit = audit_heldout_artifacts(
        manifest_path=manifest_path,
        inference_path=inference_path,
        gold_path=gold_path,
        schedule_path=schedule_path,
        runtime_config_path=runtime_path,
        stability_schedule_path=stability_schedule_path,
        stability_runtime_config_path=stability_runtime_path,
        source_dataset_path=source_path,
    )
    write_json(audit_path, audit)
    if not audit["passed"]:
        raise SystemExit(f"held-out audit failed: {audit['failures']}")

    prereg_lines = [
        "# ContractFin SCI held-out preregistration v1",
        "",
        f"- Protocol: `{HELDOUT_PROTOCOL_ID}`",
        f"- Date: `{REGISTRATION_DATE}`",
        "- Current live API authorization: **0 calls**",
        "- Confirmatory comparison: B1 tool-augmented single agent versus B0 direct LLM",
        "- B2 status: exploratory development failure analysis only",
        "",
        "## Research claim",
        "",
        prereg["research_question"],
        "",
        "The primary test is two-sided even though the development evidence motivates a directional expectation in favor of B1.",
        "",
        "## Sample and isolation",
        "",
        "A deterministic, minimum-quota stratified sample of 500 items is frozen from the 1,147-item FinQA test pool. "
        "The inference JSONL contains only sample identity, question, documents, and schema metadata. The separate gold evaluation JSONL contains reference labels plus the table context required to execute predicted programs. "
        "Neither inference runtime contains a gold key or path.",
        "",
        "A 100-item deterministic subset is frozen for two additional stability replicates; those replicates are not pooled into the primary test. "
        "Within each additional replicate, first-system order is balanced 50:50, and it flips for every item between replicates 2 and 3.",
        "",
        "## Primary analysis",
        "",
        "The primary outcome is item-level final-answer correctness under intention-to-test scoring. Missing, abstained, and error outputs are incorrect. "
        "The primary inferential test is the two-sided exact conditional McNemar test at alpha 0.05. "
        "The paired accuracy difference receives a 95% paired bootstrap interval using 10,000 resamples and seed 20260929.",
        "",
        "## Secondary and resource analyses",
        "",
        "Program ITT correctness, execution ITT correctness, item-level evidence F1, and coverage form one Holm-corrected secondary family. "
        "The three binary outcomes use exact McNemar tests; evidence F1 uses a paired 100,000-draw sign-flip test with seed 20260930. "
        "Model calls, tool calls, tokens, latency, and resources per correct answer are descriptive cost outcomes. "
        "Because rare strata are deliberately oversampled, the preregistered unweighted estimand is complemented by a FinQA-test-prevalence-weighted secondary estimate.",
        "",
        "## Failure and stopping rules",
        "",
        "No automatic retry, semantic retry, item substitution, or item-specific tuning is allowed. There is no sequential significance testing. "
        "Provider/network failures are distinguished from schema-invalid or semantically wrong model outputs. If infrastructure failures or returned-model drift exceed the frozen threshold, analysis stops before unblinding until a dated amendment is written.",
        "",
        "## Local verification",
        "",
        f"All `{len(audit['checks'])}` leakage, identity, hash, schedule, and count checks passed with `{audit['api_calls']}` API calls.",
        "",
        "The future live command is intentionally blocked and requires a separate dated authorization file bound to the frozen runtime hash; the frozen runtime itself is never edited.",
    ]
    atomic_write_text(prereg_review_path, "\n".join(prereg_lines) + "\n")

    summary = {
        "protocol_id": HELDOUT_PROTOCOL_ID,
        "primary_items": len(inference),
        "schedule_tasks": len(schedule),
        "stability_items": len(manifest["stability_subset"]["sample_ids"]),
        "audit_checks": len(audit["checks"]),
        "audit_passed": audit["passed"],
        "api_calls": 0,
        "preregistration": str(prereg_path.relative_to(root)),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
