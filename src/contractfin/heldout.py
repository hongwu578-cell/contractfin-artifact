from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

from .b0 import build_request_payload
from .b1 import build_initial_conversation
from .preregistration import classify_operations, operation_sequence
from .utils import read_jsonl, sha256_file


HELDOUT_PROTOCOL_ID = "contractfin-sci-finqa-test500-v1"
REGISTRATION_DATE = "2026-09-29"
PRIMARY_SAMPLE_SIZE = 500
STABILITY_SAMPLE_SIZE = 100

# These lower bounds increase coverage of rare operations without turning the
# primary comparison into a collection of hand-picked examples. The remaining
# slots are allocated in proportion to residual pool capacity.
DEFAULT_MINIMUM_QUOTAS: dict[str, int] = {
    "comparison": 10,
    "contains_exp": 3,
    "multi_4_step": 8,
    "multi_5_step": 10,
    "table_average": 8,
    "table_max": 6,
    "table_min": 4,
    "table_sum": 6,
}

INFERENCE_KEYS = (
    "sample_id",
    "dataset",
    "split",
    "question",
    "documents",
    "schema_version",
)
GOLD_KEYS = (
    "sample_id",
    "dataset",
    "split",
    "documents",
    "gold_answer",
    "gold_program",
    "gold_evidence",
)
FORBIDDEN_INFERENCE_KEYS = {
    "gold_answer",
    "gold_program",
    "gold_evidence",
    "answer",
    "program",
    "raw_answer",
    "execution_answer",
}
FORBIDDEN_PAYLOAD_KEYS = {
    "gold_answer",
    "gold_program",
    "gold_evidence",
    "raw_answer",
    "execution_answer",
}


def _rank_hash(namespace: str, protocol_id: str, dataset_sha256: str, sample_id: str) -> str:
    material = f"{namespace}|{protocol_id}|{dataset_sha256}|{sample_id}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def allocate_stratified_quotas(
    pool_counts: Mapping[str, int],
    *,
    sample_size: int,
    minimum_quotas: Mapping[str, int] = DEFAULT_MINIMUM_QUOTAS,
) -> dict[str, int]:
    if sample_size < 1:
        raise ValueError("sample_size must be positive")
    if sample_size > sum(pool_counts.values()):
        raise ValueError("sample_size exceeds the eligible pool")
    unknown = set(minimum_quotas) - set(pool_counts)
    if unknown:
        raise ValueError(f"minimum quotas reference unknown strata: {sorted(unknown)}")

    quotas: dict[str, int] = {}
    for stratum in sorted(pool_counts):
        pool = int(pool_counts[stratum])
        minimum = int(minimum_quotas.get(stratum, 0))
        if pool < 0 or minimum < 0:
            raise ValueError("pool counts and quotas must be non-negative")
        if minimum > pool:
            raise ValueError(f"minimum quota for {stratum} exceeds its pool")
        quotas[stratum] = minimum

    remaining = sample_size - sum(quotas.values())
    if remaining < 0:
        raise ValueError("minimum quotas exceed the requested sample size")
    residual = {name: pool_counts[name] - quotas[name] for name in quotas}
    residual_total = sum(residual.values())
    if remaining > residual_total:
        raise ValueError("insufficient residual pool for requested sample size")
    if remaining == 0:
        return quotas

    raw = {
        name: remaining * residual[name] / residual_total
        for name in quotas
    }
    floors = {name: math.floor(value) for name, value in raw.items()}
    for name, value in floors.items():
        quotas[name] += value
    left = sample_size - sum(quotas.values())
    ranked_remainders = sorted(
        raw,
        key=lambda name: (-(raw[name] - floors[name]), name),
    )
    for name in ranked_remainders:
        if left == 0:
            break
        if quotas[name] < pool_counts[name]:
            quotas[name] += 1
            left -= 1
    if left:
        raise AssertionError("largest-remainder allocation did not reach the sample size")
    return quotas


def build_heldout_manifest(
    samples: Iterable[dict[str, Any]],
    *,
    dataset_sha256: str,
    sample_size: int = PRIMARY_SAMPLE_SIZE,
    stability_size: int = STABILITY_SAMPLE_SIZE,
    minimum_quotas: Mapping[str, int] = DEFAULT_MINIMUM_QUOTAS,
    protocol_id: str = HELDOUT_PROTOCOL_ID,
) -> dict[str, Any]:
    rows = list(samples)
    if stability_size < 1 or stability_size > sample_size:
        raise ValueError("stability_size must be between one and sample_size")
    seen: set[str] = set()
    pools: dict[str, list[dict[str, Any]]] = {}
    source_positions: dict[str, int] = {}
    for position, sample in enumerate(rows, start=1):
        sample_id = str(sample.get("sample_id", ""))
        if not sample_id:
            raise ValueError(f"source position {position} has no sample_id")
        if sample_id in seen:
            raise ValueError(f"duplicate sample_id: {sample_id}")
        seen.add(sample_id)
        source_positions[sample_id] = position
        operations = operation_sequence(sample.get("gold_program"))
        stratum = classify_operations(operations)
        pools.setdefault(stratum, []).append(
            {
                "sample": sample,
                "operations": operations,
                "selection_hash": _rank_hash(
                    "primary-selection", protocol_id, dataset_sha256, sample_id
                ),
            }
        )

    pool_counts = {name: len(pool) for name, pool in sorted(pools.items())}
    quotas = allocate_stratified_quotas(
        pool_counts,
        sample_size=sample_size,
        minimum_quotas=minimum_quotas,
    )
    selected: list[dict[str, Any]] = []
    for stratum in sorted(pools):
        pool = sorted(
            pools[stratum],
            key=lambda item: (item["selection_hash"], item["sample"]["sample_id"]),
        )
        for stratum_rank, item in enumerate(pool[: quotas[stratum]], start=1):
            sample = item["sample"]
            sample_id = sample["sample_id"]
            selected.append(
                {
                    "sample_id": sample_id,
                    "source_position": source_positions[sample_id],
                    "stratum": stratum,
                    "stratum_rank": stratum_rank,
                    "selection_hash": item["selection_hash"],
                    "execution_order_hash": _rank_hash(
                        "primary-order", protocol_id, dataset_sha256, sample_id
                    ),
                    "operation_sequence": list(item["operations"]),
                    "step_count": len(item["operations"]),
                    "gold_evidence_count": len(sample.get("gold_evidence", [])),
                    "document_id": sample["documents"][0].get("document_id"),
                    "question": sample["question"],
                }
            )

    selected.sort(key=lambda item: (item["execution_order_hash"], item["sample_id"]))
    for order, item in enumerate(selected, start=1):
        item["run_order"] = order
        item["system_order_hash"] = _rank_hash(
            "system-order", protocol_id, dataset_sha256, item["sample_id"]
        )
        item["stability_hash"] = _rank_hash(
            "stability", protocol_id, dataset_sha256, item["sample_id"]
        )

    stability = sorted(
        selected,
        key=lambda item: (item["stability_hash"], item["sample_id"]),
    )[:stability_size]
    stability_ids = {item["sample_id"] for item in stability}
    for item in selected:
        item["in_stability_subset"] = item["sample_id"] in stability_ids

    return {
        "schema_version": "1.0",
        "protocol_id": protocol_id,
        "registration_date": REGISTRATION_DATE,
        "purpose": "confirmatory held-out B1 versus B0 paired comparison",
        "reportable_performance_estimate": True,
        "source": {
            "dataset": "FinQA",
            "split": "test",
            "record_count": len(rows),
            "normalized_file_sha256": dataset_sha256,
        },
        "selection_rule": {
            "method": "minimum-quota stratification followed by residual proportional largest-remainder allocation and deterministic SHA-256 ranking",
            "minimum_quotas": dict(sorted(minimum_quotas.items())),
            "eligible_pool_counts": pool_counts,
            "final_quotas": quotas,
            "selected_count": sample_size,
            "sample_substitution": False,
            "selection_rank_material": "primary-selection|{protocol_id}|{normalized_file_sha256}|{sample_id}",
            "execution_order_material": "primary-order|{protocol_id}|{normalized_file_sha256}|{sample_id}",
            "notes": [
                "Gold programs are used only for stratum assignment and are absent from inference artifacts.",
                "The primary unweighted estimand applies to this preregistered stress-aware sample mix.",
                "A population-stratum-weighted effect is reported as a secondary estimand.",
                "No selected sample may be substituted after registration.",
            ],
        },
        "stability_subset": {
            "selected_count": stability_size,
            "selection": "lowest deterministic stability hashes among the primary sample",
            "additional_replicates": 2,
            "sample_ids": [item["sample_id"] for item in stability],
        },
        "selected_stratum_counts": dict(Counter(item["stratum"] for item in selected)),
        "samples": selected,
    }


def build_interleaved_schedule(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    selected = sorted(manifest["samples"], key=lambda item: item["run_order"])
    system_ranked = sorted(
        selected,
        key=lambda item: (item["system_order_hash"], item["sample_id"]),
    )
    b0_first_ids = {
        item["sample_id"] for item in system_ranked[: len(system_ranked) // 2]
    }
    schedule: list[dict[str, Any]] = []
    sequence = 0
    for pair_index, item in enumerate(selected, start=1):
        first = "B0" if item["sample_id"] in b0_first_ids else "B1"
        second = "B1" if first == "B0" else "B0"
        for within_pair_order, system in enumerate((first, second), start=1):
            sequence += 1
            schedule.append(
                {
                    "sequence": sequence,
                    "task_id": f"{system}:{item['sample_id']}",
                    "pair_index": pair_index,
                    "within_pair_order": within_pair_order,
                    "sample_id": item["sample_id"],
                    "system": system,
                }
            )
    return schedule


def build_stability_schedule(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    stability_ids = set(manifest["stability_subset"]["sample_ids"])
    selected = [
        item
        for item in sorted(manifest["samples"], key=lambda value: value["run_order"])
        if item["sample_id"] in stability_ids
    ]
    system_ranked = sorted(
        selected,
        key=lambda item: (item["system_order_hash"], item["sample_id"]),
    )
    replicate_two_b0_first = {
        item["sample_id"] for item in system_ranked[: len(system_ranked) // 2]
    }
    schedule: list[dict[str, Any]] = []
    sequence = 0
    for replicate in (2, 3):
        for pair_index, item in enumerate(selected, start=1):
            b0_first = item["sample_id"] in replicate_two_b0_first
            if replicate == 3:
                b0_first = not b0_first
            first = "B0" if b0_first else "B1"
            second = "B1" if first == "B0" else "B0"
            for within_pair_order, system in enumerate((first, second), start=1):
                sequence += 1
                schedule.append(
                    {
                        "sequence": sequence,
                        "task_id": f"R{replicate}:{system}:{item['sample_id']}",
                        "replicate": replicate,
                        "pair_index": pair_index,
                        "within_pair_order": within_pair_order,
                        "sample_id": item["sample_id"],
                        "system": system,
                    }
                )
    return schedule


def split_selected_records(
    samples: Iterable[dict[str, Any]], manifest: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_id = {item["sample_id"]: item for item in samples}
    selected = sorted(manifest["samples"], key=lambda item: item["run_order"])
    inference: list[dict[str, Any]] = []
    gold: list[dict[str, Any]] = []
    for registered in selected:
        sample_id = registered["sample_id"]
        if sample_id not in by_id:
            raise ValueError(f"selected sample is absent from the source dataset: {sample_id}")
        sample = by_id[sample_id]
        inference.append({key: sample[key] for key in INFERENCE_KEYS if key in sample})
        gold.append({key: sample[key] for key in GOLD_KEYS if key in sample})
    return inference, gold


def _logsumexp(values: list[float]) -> float:
    if not values:
        return -math.inf
    maximum = max(values)
    if maximum == -math.inf:
        return maximum
    return maximum + math.log(sum(math.exp(value - maximum) for value in values))


def _binomial_cdf(k: int, n: int, p: float) -> float:
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if p == 0.0:
        return 1.0
    if p == 1.0:
        return 0.0
    logs = [
        math.lgamma(n + 1)
        - math.lgamma(x + 1)
        - math.lgamma(n - x + 1)
        + x * math.log(p)
        + (n - x) * math.log1p(-p)
        for x in range(k + 1)
    ]
    return min(1.0, math.exp(_logsumexp(logs)))


def _exact_mcnemar_lower_cutoff(discordant: int, alpha: float) -> int:
    if discordant == 0:
        return -1
    cutoff = -1
    threshold = alpha / 2.0
    if discordant <= 1022:
        probability = math.ldexp(1.0, -discordant)
        cumulative = 0.0
        for lower in range(discordant // 2 + 1):
            cumulative += probability
            if cumulative <= threshold:
                cutoff = lower
            else:
                break
            probability *= (discordant - lower) / (lower + 1)
        return cutoff

    # 2**(-discordant) underflows above 1,074. Maintain the same exact-tail
    # definition in log space for these remote discordance counts.
    log_probability = -discordant * math.log(2.0)
    log_cumulative = -math.inf
    log_threshold = math.log(threshold)
    for lower in range(discordant // 2 + 1):
        log_cumulative = _logsumexp([log_cumulative, log_probability])
        if log_cumulative <= log_threshold:
            cutoff = lower
        else:
            break
        log_probability += math.log(discordant - lower) - math.log(lower + 1)
    return cutoff


def exact_mcnemar_power(
    n: int,
    *,
    total_discordance: float,
    net_difference: float,
    alpha: float = 0.05,
) -> float:
    if n < 1:
        raise ValueError("n must be positive")
    if not 0.0 < total_discordance < 1.0:
        raise ValueError("total_discordance must be between zero and one")
    if not 0.0 < abs(net_difference) < total_discordance:
        raise ValueError("absolute net_difference must be positive and below discordance")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between zero and one")

    theta = (total_discordance + abs(net_difference)) / (2.0 * total_discordance)
    power = 0.0
    for discordant in range(n + 1):
        probability_d = math.exp(
            math.lgamma(n + 1)
            - math.lgamma(discordant + 1)
            - math.lgamma(n - discordant + 1)
            + discordant * math.log(total_discordance)
            + (n - discordant) * math.log1p(-total_discordance)
        )
        cutoff = _exact_mcnemar_lower_cutoff(discordant, alpha)
        if cutoff < 0:
            continue
        conditional_rejection = _binomial_cdf(cutoff, discordant, theta) + _binomial_cdf(
            cutoff, discordant, 1.0 - theta
        )
        power += probability_d * min(1.0, conditional_rejection)
    return min(1.0, max(0.0, power))


def build_power_sensitivity(
    *,
    sample_sizes: Iterable[int] = (100, 155, 300, 470, 500, 750, 1147),
    scenarios: Iterable[tuple[str, float, float]] = (
        ("small_effect_low_discordance", 0.15, 0.05),
        ("moderate_effect", 0.20, 0.075),
        ("ten_point_effect", 0.20, 0.10),
        ("ten_point_high_discordance", 0.30, 0.10),
    ),
    alpha: float = 0.05,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for scenario, discordance, difference in scenarios:
        b1_only = (discordance + difference) / 2.0
        b0_only = (discordance - difference) / 2.0
        for n in sample_sizes:
            rows.append(
                {
                    "scenario": scenario,
                    "n": n,
                    "total_discordance": discordance,
                    "net_accuracy_difference_B1_minus_B0": difference,
                    "probability_B1_correct_B0_wrong": b1_only,
                    "probability_B0_correct_B1_wrong": b0_only,
                    "two_sided_alpha": alpha,
                    "exact_unconditional_power": exact_mcnemar_power(
                        n,
                        total_discordance=discordance,
                        net_difference=difference,
                        alpha=alpha,
                    ),
                }
            )
    return {
        "schema_version": "1.0",
        "method": "unconditional power of the two-sided exact conditional McNemar test",
        "assumptions": [
            "Each paired item belongs to B1-only correct, B0-only correct, both correct, or both wrong.",
            "The number of discordant pairs is Binomial(n, total_discordance).",
            "Conditional on discordance, B1-only counts are Binomial(D, theta).",
            "Rejection uses the doubled smaller exact Binomial(D, 0.5) tail at alpha=0.05.",
        ],
        "rows": rows,
    }


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.add(str(key))
            keys.update(_walk_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.update(_walk_keys(nested))
    return keys


def audit_heldout_artifacts(
    *,
    manifest_path: Path,
    inference_path: Path,
    gold_path: Path,
    schedule_path: Path,
    runtime_config_path: Path,
    stability_schedule_path: Path,
    stability_runtime_config_path: Path,
    source_dataset_path: Path,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    runtime = json.loads(runtime_config_path.read_text(encoding="utf-8"))
    stability_runtime = json.loads(stability_runtime_config_path.read_text(encoding="utf-8"))
    inference = list(read_jsonl(inference_path))
    gold = list(read_jsonl(gold_path))
    schedule = list(read_jsonl(schedule_path))
    stability_schedule = list(read_jsonl(stability_schedule_path))
    checks: dict[str, bool] = {}

    checks["source_dataset_hash_matches"] = (
        sha256_file(source_dataset_path) == manifest["source"]["normalized_file_sha256"]
    )
    artifact_paths = {
        "inference": inference_path,
        "gold": gold_path,
        "schedule": schedule_path,
        "runtime_config": runtime_config_path,
        "stability_schedule": stability_schedule_path,
        "stability_runtime_config": stability_runtime_config_path,
    }
    for name, path in artifact_paths.items():
        checks[f"{name}_hash_matches"] = (
            sha256_file(path) == manifest["artifacts"][name]["sha256"]
        )

    registered_ids = [
        item["sample_id"]
        for item in sorted(manifest["samples"], key=lambda item: item["run_order"])
    ]
    inference_ids = [item.get("sample_id") for item in inference]
    gold_ids = [item.get("sample_id") for item in gold]
    checks["primary_count_is_500"] = len(registered_ids) == PRIMARY_SAMPLE_SIZE
    checks["inference_ids_match_registered_order"] = inference_ids == registered_ids
    checks["gold_ids_match_registered_order"] = gold_ids == registered_ids
    checks["sample_ids_are_unique"] = len(registered_ids) == len(set(registered_ids))
    checks["inference_top_level_schema_is_allowlisted"] = all(
        set(item) <= set(INFERENCE_KEYS) for item in inference
    )
    checks["inference_has_no_forbidden_keys"] = all(
        not (_walk_keys(item) & FORBIDDEN_INFERENCE_KEYS) for item in inference
    )
    checks["gold_has_required_execution_context"] = all(
        isinstance(item.get("documents"), list) and item["documents"] for item in gold
    )
    checks["gold_schema_is_allowlisted"] = all(set(item) <= set(GOLD_KEYS) for item in gold)
    checks["runtime_config_contains_no_gold_keys"] = not any(
        "gold" in key.casefold() for key in _walk_keys(runtime)
    )
    checks["runtime_authorizes_zero_live_calls"] = runtime.get("live_api_authorized") is False
    checks["stability_runtime_contains_no_gold_keys"] = not any(
        "gold" in key.casefold() for key in _walk_keys(stability_runtime)
    )
    checks["stability_runtime_authorizes_zero_live_calls"] = (
        stability_runtime.get("live_api_authorized") is False
    )

    task_ids = [item.get("task_id") for item in schedule]
    expected_tasks = {f"{system}:{sample_id}" for sample_id in registered_ids for system in ("B0", "B1")}
    checks["schedule_has_1000_tasks"] = len(schedule) == PRIMARY_SAMPLE_SIZE * 2
    checks["schedule_tasks_are_unique_and_complete"] = set(task_ids) == expected_tasks and len(task_ids) == len(set(task_ids))
    checks["schedule_is_strictly_interleaved_by_pair"] = all(
        schedule[index]["sample_id"] == schedule[index + 1]["sample_id"]
        and {schedule[index]["system"], schedule[index + 1]["system"]} == {"B0", "B1"}
        for index in range(0, len(schedule), 2)
    )
    primary_first_counts = Counter(schedule[index]["system"] for index in range(0, len(schedule), 2))
    checks["primary_first_system_is_exactly_balanced"] = primary_first_counts == {"B0": 250, "B1": 250}
    stability_ids = manifest["stability_subset"]["sample_ids"]
    checks["stability_count_is_100"] = len(stability_ids) == STABILITY_SAMPLE_SIZE
    checks["stability_ids_are_unique_primary_ids"] = (
        len(stability_ids) == len(set(stability_ids)) and set(stability_ids) <= set(registered_ids)
    )
    checks["stability_schedule_has_400_tasks"] = len(stability_schedule) == STABILITY_SAMPLE_SIZE * 2 * 2
    stability_tasks = [item.get("task_id") for item in stability_schedule]
    expected_stability_tasks = {
        f"R{replicate}:{system}:{sample_id}"
        for replicate in (2, 3)
        for system in ("B0", "B1")
        for sample_id in stability_ids
    }
    checks["stability_tasks_are_unique_and_complete"] = (
        set(stability_tasks) == expected_stability_tasks
        and len(stability_tasks) == len(set(stability_tasks))
    )
    checks["stability_schedule_is_strictly_interleaved_by_pair"] = all(
        stability_schedule[index]["sample_id"] == stability_schedule[index + 1]["sample_id"]
        and stability_schedule[index]["replicate"] == stability_schedule[index + 1]["replicate"]
        and {stability_schedule[index]["system"], stability_schedule[index + 1]["system"]} == {"B0", "B1"}
        for index in range(0, len(stability_schedule), 2)
    )
    stability_first_counts = {
        replicate: Counter(
            stability_schedule[index]["system"]
            for index in range(0, len(stability_schedule), 2)
            if stability_schedule[index]["replicate"] == replicate
        )
        for replicate in (2, 3)
    }
    checks["stability_first_system_is_balanced_each_replicate"] = all(
        counts == {"B0": 50, "B1": 50} for counts in stability_first_counts.values()
    )
    first_by_replicate = {
        (item["replicate"], item["sample_id"]): item["system"]
        for item in stability_schedule
        if item["within_pair_order"] == 1
    }
    checks["stability_first_system_flips_within_item"] = all(
        first_by_replicate[(2, sample_id)] != first_by_replicate[(3, sample_id)]
        for sample_id in stability_ids
    )

    # Build every model-visible initial payload from inference-only records.
    # The audit checks field-level isolation, not accidental equality between a
    # document number and the correct numerical answer.
    payload_key_violations: list[str] = []
    for sample in inference:
        b0_payload = build_request_payload(
            sample, runtime["requested_model"], max_output_tokens=runtime["B0"]["max_output_tokens"], strict_schema=False
        )
        b1_conversation = build_initial_conversation(sample)
        if _walk_keys(b0_payload) & FORBIDDEN_PAYLOAD_KEYS:
            payload_key_violations.append(f"B0:{sample['sample_id']}")
        if _walk_keys(b1_conversation) & FORBIDDEN_PAYLOAD_KEYS:
            payload_key_violations.append(f"B1:{sample['sample_id']}")
    checks["all_initial_payloads_pass_key_leakage_audit"] = not payload_key_violations

    failures = sorted(name for name, passed in checks.items() if not passed)
    return {
        "schema_version": "1.0",
        "protocol_id": manifest["protocol_id"],
        "api_calls": 0,
        "checks": checks,
        "payload_key_violations": payload_key_violations,
        "passed": not failures,
        "failures": failures,
    }
