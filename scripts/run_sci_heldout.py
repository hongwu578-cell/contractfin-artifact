#!/usr/bin/env python3
from __future__ import annotations

import argparse
import functools
import hashlib
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.b0 import (  # noqa: E402
    PROMPT_VERSION,
    PROVIDERS,
    build_request_payload,
    call_responses_api,
    extract_prediction,
)
from contractfin.b1 import (  # noqa: E402
    B1_PROMPT_VERSION,
    B1SampleFailure,
    execute_b1_sample,
)
from contractfin.heldout import FORBIDDEN_INFERENCE_KEYS, FORBIDDEN_PAYLOAD_KEYS  # noqa: E402
from contractfin.run_logging import append_log, utc_now  # noqa: E402
from contractfin.utils import read_jsonl, sha256_file, write_json, write_jsonl  # noqa: E402


def walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.add(str(key))
            keys.update(walk_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.update(walk_keys(nested))
    return keys


def usage(response: dict[str, Any]) -> dict[str, int]:
    raw = response.get("usage") or {}
    details = raw.get("output_tokens_details") or {}
    return {
        "input": int(raw.get("input_tokens") or 0),
        "output": int(raw.get("output_tokens") or 0),
        "reasoning": int(details.get("reasoning_tokens") or 0),
        "total": int(raw.get("total_tokens") or 0),
    }


def error_prediction(sample_id: str, system: str, error: Exception) -> dict[str, Any]:
    return {
        "sample_id": sample_id,
        "answer": None,
        "evidence": [],
        "status": "error",
        "program": None,
        "unit": None,
        "metadata": {
            "baseline": system,
            "error_type": type(error).__name__,
            "error": str(error),
        },
    }


def fake_response(sample_id: str, *, tool_call: bool = False) -> dict[str, Any]:
    if tool_call:
        output = [
            {
                "type": "function_call",
                "call_id": "dry_call_search",
                "name": "search_document",
                "arguments": json.dumps({"query": "financial values", "top_k": 12}),
            }
        ]
    else:
        value = {
            "sample_id": sample_id,
            "answer": None,
            "evidence": [],
            "status": "abstain",
            "program": None,
            "unit": None,
        }
        output = [
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": json.dumps(value)}],
            }
        ]
    return {
        "id": "dry_response",
        "status": "completed",
        "model": "local-dry-run-no-api",
        "output": output,
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 0,
        },
    }


def load_runtime(root: Path, path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    runtime = json.loads(path.read_text(encoding="utf-8"))
    if any("gold" in key.casefold() for key in walk_keys(runtime)):
        raise ValueError("runtime configuration must not contain any gold key or path")
    inference_path = root / runtime["inference_artifact"]["path"]
    schedule_path = root / runtime["schedule_artifact"]["path"]
    if sha256_file(inference_path) != runtime["inference_artifact"]["sha256"]:
        raise ValueError("inference artifact hash does not match runtime configuration")
    if sha256_file(schedule_path) != runtime["schedule_artifact"]["sha256"]:
        raise ValueError("schedule artifact hash does not match runtime configuration")
    inference = list(read_jsonl(inference_path))
    schedule = list(read_jsonl(schedule_path))
    if len(inference) != runtime["inference_artifact"]["record_count"]:
        raise ValueError("inference record count does not match runtime configuration")
    if len(schedule) != runtime["schedule_artifact"]["task_count"]:
        raise ValueError("schedule task count does not match runtime configuration")
    for sample in inference:
        forbidden = walk_keys(sample) & FORBIDDEN_INFERENCE_KEYS
        if forbidden:
            raise ValueError(f"inference sample contains forbidden keys: {sorted(forbidden)}")
    return runtime, inference, schedule


def dry_run(runtime: dict[str, Any], inference: list[dict[str, Any]], schedule: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {sample["sample_id"]: sample for sample in inference}
    first_pair = schedule[:2]
    systems_completed: list[str] = []
    payloads_checked = 0
    for task in first_pair:
        sample = by_id[task["sample_id"]]
        if task["system"] == "B0":
            payload = build_request_payload(
                sample,
                runtime["requested_model"],
                max_output_tokens=runtime["B0"]["max_output_tokens"],
                strict_schema=False,
            )
            if walk_keys(payload) & FORBIDDEN_PAYLOAD_KEYS:
                raise ValueError("B0 dry-run payload contains a forbidden key")
            prediction = extract_prediction(
                fake_response(sample["sample_id"]),
                sample["sample_id"],
                provider=runtime["requested_provider"],
            )
            payloads_checked += 1
        else:
            call_index = 0

            def caller(payload: dict[str, Any]) -> dict[str, Any]:
                nonlocal call_index, payloads_checked
                if walk_keys(payload) & FORBIDDEN_PAYLOAD_KEYS:
                    raise ValueError("B1 dry-run payload contains a forbidden key")
                payloads_checked += 1
                call_index += 1
                return fake_response(sample["sample_id"], tool_call=call_index == 1)

            prediction, _, tool_traces = execute_b1_sample(
                sample,
                model=runtime["requested_model"],
                provider=runtime["requested_provider"],
                total_output_budget=runtime["B1"]["total_output_budget"],
                max_model_calls=runtime["B1"]["max_model_calls"],
                max_tool_calls=runtime["B1"]["max_tool_calls"],
                strict_schema=False,
                api_caller=caller,
            )
            if not any(trace.get("name") == "search_document" for trace in tool_traces):
                raise AssertionError("B1 dry run did not exercise search_document")
        if prediction["sample_id"] != sample["sample_id"]:
            raise AssertionError("dry-run prediction identity mismatch")
        systems_completed.append(task["system"])
    return {
        "schema_version": "1.0",
        "protocol_id": runtime["protocol_id"],
        "mode": "dry-run",
        "systems_completed": sorted(systems_completed),
        "payloads_checked": payloads_checked,
        "api_calls": 0,
        "passed": set(systems_completed) == {"B0", "B1"},
    }


def run_live(
    root: Path,
    runtime_path: Path,
    runtime: dict[str, Any],
    inference: list[dict[str, Any]],
    schedule: list[dict[str, Any]],
    artifact_stem: str,
    authorization: dict[str, Any] | None = None,
) -> dict[str, Any]:
    runtime_hash = sha256_file(runtime_path)
    if not authorization or authorization.get("authorized") is not True:
        raise PermissionError(
            "live execution is blocked: a dated authorization amendment is required after explicit user authorization"
        )
    if authorization.get("protocol_id") != runtime["protocol_id"]:
        raise PermissionError("authorization amendment protocol_id does not match the frozen runtime")
    if authorization.get("runtime_config_sha256") != runtime_hash:
        raise PermissionError("authorization amendment does not bind to this frozen runtime hash")
    if authorization.get("scope") not in {"primary", "stability"}:
        raise PermissionError("authorization amendment has no valid execution scope")
    provider_name = runtime["requested_provider"]
    provider = PROVIDERS[provider_name]
    log_path = root / "logs" / f"{artifact_stem}_tasks.jsonl"
    summary_path = root / "reports" / f"{artifact_stem}_inference_summary.json"
    existing = list(read_jsonl(log_path)) if log_path.exists() else []
    for record in existing:
        if record.get("protocol_id") != runtime["protocol_id"] or record.get("runtime_config_sha256") != runtime_hash:
            raise ValueError("existing task log belongs to a different protocol or runtime config")
    completed = {record["task_id"] for record in existing}
    run_id = existing[0]["run_id"] if existing else f"sci-heldout-{uuid.uuid4()}"
    by_id = {sample["sample_id"]: sample for sample in inference}
    api_caller = functools.partial(
        call_responses_api,
        api_key_env=provider.api_key_env,
        url=provider.responses_url,
        timeout=max(runtime["B0"]["request_timeout_seconds"], runtime["B1"]["request_timeout_seconds"]),
    )

    for task in schedule:
        if task["task_id"] in completed:
            continue
        sample = by_id[task["sample_id"]]
        system = task["system"]
        started_at = utc_now()
        started = time.monotonic()
        error: Exception | None = None
        tool_traces: list[dict[str, Any]] = []
        model_traces: list[dict[str, Any]] = []
        token_usage = {"input": 0, "output": 0, "reasoning": 0, "total": 0}
        actual_model = runtime["requested_model"]
        input_metadata: dict[str, Any]
        try:
            if system == "B0":
                payload = build_request_payload(
                    sample,
                    runtime["requested_model"],
                    max_output_tokens=runtime["B0"]["max_output_tokens"],
                    strict_schema=provider.strict_schema,
                )
                response = api_caller(payload)
                token_usage = usage(response)
                actual_model = response.get("model") or actual_model
                prediction = extract_prediction(
                    response,
                    sample["sample_id"],
                    provider=provider_name,
                )
                input_metadata = {
                    "prompt_version": PROMPT_VERSION,
                    "payload_sha256": hashlib.sha256(
                        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
                    ).hexdigest(),
                    "max_output_tokens": runtime["B0"]["max_output_tokens"],
                }
            else:
                prediction, model_traces, tool_traces = execute_b1_sample(
                    sample,
                    model=runtime["requested_model"],
                    provider=provider_name,
                    total_output_budget=runtime["B1"]["total_output_budget"],
                    max_model_calls=runtime["B1"]["max_model_calls"],
                    max_tool_calls=runtime["B1"]["max_tool_calls"],
                    strict_schema=provider.strict_schema,
                    api_caller=api_caller,
                )
                for key in token_usage:
                    token_usage[key] = sum(trace["token_usage"][key] for trace in model_traces)
                actual_models = [trace.get("model") for trace in model_traces if trace.get("model")]
                actual_model = actual_models[-1] if actual_models else actual_model
                input_metadata = {
                    "prompt_version": B1_PROMPT_VERSION,
                    "total_output_budget": runtime["B1"]["total_output_budget"],
                    "max_model_calls": runtime["B1"]["max_model_calls"],
                    "max_tool_calls": runtime["B1"]["max_tool_calls"],
                }
        except B1SampleFailure as exc:
            error = exc
            model_traces = exc.model_traces
            tool_traces = exc.tool_traces
            for key in token_usage:
                token_usage[key] = sum(trace["token_usage"][key] for trace in model_traces)
            prediction = error_prediction(sample["sample_id"], system, exc)
            input_metadata = {"prompt_version": B1_PROMPT_VERSION}
        except Exception as exc:
            error = exc
            prediction = error_prediction(sample["sample_id"], system, exc)
            input_metadata = {"prompt_version": PROMPT_VERSION if system == "B0" else B1_PROMPT_VERSION}
        record = {
            "run_id": run_id,
            "protocol_id": runtime["protocol_id"],
            "runtime_config_sha256": runtime_hash,
            "task_id": task["task_id"],
            "schedule_sequence": task["sequence"],
            "replicate": task.get("replicate", 1),
            "sample_id": sample["sample_id"],
            "system": system,
            "model": actual_model,
            "started_at": started_at,
            "finished_at": utc_now(),
            "input": input_metadata,
            "output": prediction,
            "tool_calls": tool_traces,
            "model_calls": model_traces,
            "token_usage": token_usage,
            "latency_ms": round((time.monotonic() - started) * 1000),
            "error": None if error is None else {"type": type(error).__name__, "message": str(error)},
        }
        append_log(log_path, record)
        existing.append(record)

    replicates = sorted({int(record.get("replicate", 1)) for record in existing})
    groups = {
        (system, replicate): [
            record["output"]
            for record in existing
            if record["system"] == system and int(record.get("replicate", 1)) == replicate
        ]
        for system in ("B0", "B1")
        for replicate in replicates
    }
    prediction_paths: dict[tuple[str, int], Path] = {}
    for (system, replicate), predictions in groups.items():
        replicate_suffix = "" if replicates == [1] else f"_R{replicate}"
        path = root / "reports" / f"{artifact_stem}_{system}{replicate_suffix}_predictions.jsonl"
        prediction_paths[(system, replicate)] = path
        write_jsonl(path, predictions)
    summary = {
        "schema_version": "1.0",
        "protocol_id": runtime["protocol_id"],
        "run_id": run_id,
        "runtime_config_sha256": runtime_hash,
        "evaluation_deferred": True,
        "gold_loaded": False,
        "task_count": len(existing),
        "expected_task_count": len(schedule),
        "completed": len(existing) == len(schedule),
        "prediction_groups": {
            f"{system}_R{replicate}": {
                "system": system,
                "replicate": replicate,
                "predictions": len(groups[(system, replicate)]),
                "errors": sum(
                    record["error"] is not None
                    for record in existing
                    if record["system"] == system and int(record.get("replicate", 1)) == replicate
                ),
                "prediction_file": str(prediction_paths[(system, replicate)].relative_to(root)),
                "prediction_sha256": sha256_file(prediction_paths[(system, replicate)]),
            }
            for system in ("B0", "B1")
            for replicate in replicates
        },
    }
    write_json(summary_path, summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the isolated ContractFin SCI held-out protocol")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--runtime-config", type=Path, required=True)
    parser.add_argument("--mode", choices=("dry-run", "live"), required=True)
    parser.add_argument("--artifact-stem", default="sci_finqa_test500_primary_v1")
    parser.add_argument("--authorization-amendment", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    runtime_path = args.runtime_config
    if not runtime_path.is_absolute():
        runtime_path = root / runtime_path
    runtime, inference, schedule = load_runtime(root, runtime_path)
    if args.mode == "dry-run":
        result = dry_run(runtime, inference, schedule)
    else:
        authorization = None
        if args.authorization_amendment:
            authorization_path = args.authorization_amendment
            if not authorization_path.is_absolute():
                authorization_path = root / authorization_path
            authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
        result = run_live(
            root,
            runtime_path,
            runtime,
            inference,
            schedule,
            args.artifact_stem,
            authorization,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("passed", result.get("completed", False)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
