from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

from .b0 import B0Error, PREDICTION_OUTPUT_SCHEMA, extract_prediction
from .b1_tools import B1_TOOL_DEFINITIONS, execute_b1_tool
from .evaluation import evaluate_files
from .run_logging import append_log, log_completeness, utc_now
from .utils import atomic_write_text, write_json, write_jsonl


B1_PROMPT_VERSION = "b1-tool-single-agent-v1.1"

B1_SYSTEM_PROMPT_V1 = """You are the sole tool-augmented agent in a financial question-answering study.
There are no other agents, no task contract, and no hidden verifier.

Use only the allowed document through the supplied tools. Before answering, call
search_document at least once and request top_k=12 on the first search. For
calculations, comparisons, or table aggregations, call calculate_finqa and use
its deterministic result. You may make
follow-up searches when the first evidence is insufficient. Never use outside
knowledge and never invent an evidence label.

Your final response must be one object following the supplied JSON schema. The
answer must be a scalar string or null. Evidence must contain only exact labels
returned by search_document. If calculation is required, include the executed
FinQA-style program. If evidence remains insufficient, abstain. Do not explain
anything outside the structured final response."""


B1_SYSTEM_PROMPT_V1_1 = """You are the sole tool-augmented agent in a financial question-answering study.
There are no other agents, no task contract, and no hidden verifier.

Use only the allowed document through the supplied tools. First call
search_document with top_k=12. If that search contains the needed values, do
not repeat it. Use at most two searches unless neither result contains the
needed evidence. Never use outside knowledge or invent an evidence label.

For every calculation, comparison, or table aggregation, call calculate_finqa
with its structured steps array. Each step has exactly one operation and two
string arguments. Operations cannot be nested: use #0, #1, and so on for prior
results. Do not use semicolons, assignments, infix arithmetic, or a free-form
program string. For a table operation, use the row name shown after ROW: as
argument 1 and the string none as argument 2; do not use a table_N evidence
label as the row name. When calculation succeeds, copy the returned canonical
program into the final response.

Your final response must be exactly one raw JSON object following the supplied
schema, without Markdown fences, preamble, or trailing commentary. The answer
must be a scalar string or null. Evidence must contain only exact labels
returned by search_document. If evidence remains insufficient, abstain."""


B1_SYSTEM_PROMPT = B1_SYSTEM_PROMPT_V1_1


class B1Error(RuntimeError):
    """Safe, reportable B1 execution failure."""


class B1SampleFailure(B1Error):
    def __init__(
        self,
        message: str,
        model_traces: list[dict[str, Any]],
        tool_traces: list[dict[str, Any]],
        final_output_diagnostic: dict[str, Any] | None = None,
    ):
        self.model_traces = list(model_traces)
        self.tool_traces = list(tool_traces)
        self.final_output_diagnostic = final_output_diagnostic
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class B1RunPaths:
    gold: Path
    predictions: Path
    log: Path
    report: Path


def build_initial_conversation(sample: dict[str, Any]) -> list[dict[str, Any]]:
    document_ids = [
        str(item.get("document_id") or item.get("filename") or "unknown_document")
        for item in sample.get("documents", [])
    ]
    user_content = (
        f"SAMPLE_ID: {sample['sample_id']}\n"
        f"DATASET: {sample['dataset']}\n"
        f"ALLOWED_DOCUMENTS: {json.dumps(document_ids, ensure_ascii=False)}\n"
        f"QUESTION: {sample['question']}"
    )
    return [
        {"role": "system", "content": B1_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def build_b1_payload(
    conversation: list[dict[str, Any]],
    model: str,
    *,
    max_output_tokens: int,
    allow_tools: bool,
    strict_schema: bool,
) -> dict[str, Any]:
    output_format: dict[str, Any] = {
        "type": "json_schema",
        "name": "contractfin_prediction",
        "schema": PREDICTION_OUTPUT_SCHEMA,
    }
    if strict_schema:
        output_format["strict"] = True
    payload: dict[str, Any] = {
        "model": model,
        "input": conversation,
        "text": {"format": output_format},
        "tools": B1_TOOL_DEFINITIONS,
        "tool_choice": "auto" if allow_tools else "none",
        "max_output_tokens": max_output_tokens,
        "store": False,
    }
    return payload


def _usage(response: dict[str, Any]) -> dict[str, int]:
    usage = response.get("usage") or {}
    details = usage.get("output_tokens_details") or {}
    return {
        "input": int(usage.get("input_tokens") or 0),
        "output": int(usage.get("output_tokens") or 0),
        "reasoning": int(details.get("reasoning_tokens") or 0),
        "total": int(usage.get("total_tokens") or 0),
    }


def _response_trace(response: dict[str, Any], call_index: int, latency_ms: int) -> dict[str, Any]:
    incomplete = response.get("incomplete_details") or {}
    error = response.get("error") or {}
    return {
        "call_index": call_index,
        "response_id": response.get("id"),
        "model": response.get("model"),
        "status": response.get("status"),
        "incomplete_reason": incomplete.get("reason"),
        "provider_error_code": error.get("code"),
        "output_item_types": [
            item.get("type") for item in response.get("output", []) if isinstance(item, dict)
        ],
        "token_usage": _usage(response),
        "latency_ms": latency_ms,
    }


def _function_calls(response: dict[str, Any]) -> list[dict[str, str]]:
    calls: list[dict[str, str]] = []
    for item in response.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "function_call":
            continue
        call_id = item.get("call_id")
        name = item.get("name")
        arguments = item.get("arguments")
        if not all(isinstance(value, str) and value for value in (call_id, name, arguments)):
            raise B1Error("function call is missing call_id, name, or arguments")
        calls.append({"call_id": call_id, "name": name, "arguments": arguments})
    return calls


def _conversation_output_items(response: dict[str, Any]) -> list[dict[str, Any]]:
    items = response.get("output") or []
    if not isinstance(items, list):
        raise B1Error("Responses API output must be an array")
    return [item for item in items if isinstance(item, dict)]


def _visible_output_diagnostic(response: dict[str, Any], limit: int = 8192) -> dict[str, Any]:
    texts: list[str] = []
    for item in response.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if (
                isinstance(content, dict)
                and content.get("type") == "output_text"
                and isinstance(content.get("text"), str)
            ):
                texts.append(content["text"])
    combined = "".join(texts)
    return {
        "output_text_items": len(texts),
        "character_count": len(combined),
        "sha256": hashlib.sha256(combined.encode("utf-8")).hexdigest(),
        "visible_text": combined[:limit],
        "truncated": len(combined) > limit,
        "reasoning_text_retained": False,
    }


def execute_b1_sample(
    sample: dict[str, Any],
    *,
    model: str,
    provider: str,
    total_output_budget: int,
    max_model_calls: int,
    max_tool_calls: int,
    strict_schema: bool,
    api_caller: Callable[[dict[str, Any]], dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    if total_output_budget < 1:
        raise ValueError("total_output_budget must be positive")
    if max_model_calls < 1 or max_tool_calls < 1:
        raise ValueError("model and tool call limits must be positive")
    conversation = build_initial_conversation(sample)
    model_traces: list[dict[str, Any]] = []
    tool_traces: list[dict[str, Any]] = []
    consumed_output = 0
    try:
        for call_index in range(1, max_model_calls + 1):
            remaining_output = total_output_budget - consumed_output
            if remaining_output < 1:
                raise B1Error("cumulative model output budget was exhausted")
            allow_tools = call_index < max_model_calls
            payload = build_b1_payload(
                conversation,
                model,
                max_output_tokens=remaining_output,
                allow_tools=allow_tools,
                strict_schema=strict_schema,
            )
            started = time.monotonic()
            response = api_caller(payload)
            latency_ms = round((time.monotonic() - started) * 1000)
            trace = _response_trace(response, call_index, latency_ms)
            model_traces.append(trace)
            consumed_output += trace["token_usage"]["output"]
            if response.get("status") != "completed":
                raise B1Error(
                    "model call did not complete "
                    f"(status={response.get('status')}, reason={trace['incomplete_reason']})"
                )
            conversation.extend(_conversation_output_items(response))
            calls = _function_calls(response)
            if not calls:
                try:
                    prediction = extract_prediction(
                        response,
                        sample["sample_id"],
                        provider=provider,
                        baseline="B1_tool_augmented_single_agent",
                    )
                except B0Error as exc:
                    raise B1SampleFailure(
                        str(exc),
                        model_traces,
                        tool_traces,
                        _visible_output_diagnostic(response),
                    ) from exc
                prediction["metadata"].update(
                    {
                        "prompt_version": B1_PROMPT_VERSION,
                        "model_calls": len(model_traces),
                        "tool_calls": len(tool_traces),
                    }
                )
                return prediction, model_traces, tool_traces
            if not allow_tools:
                raise B1Error("model attempted a tool call on the forced final turn")
            if len(tool_traces) + len(calls) > max_tool_calls:
                raise B1Error("maximum tool call count exceeded")
            for call in calls:
                output, tool_trace = execute_b1_tool(call["name"], call["arguments"], sample)
                tool_trace.update(
                    {
                        "call_id": call["call_id"],
                        "model_call_index": call_index,
                        "actor": "single_agent",
                    }
                )
                tool_traces.append(tool_trace)
                conversation.append(
                    {
                        "type": "function_call_output",
                        "call_id": call["call_id"],
                        "output": output,
                    }
                )
        raise B1Error("single agent reached the model call limit without a final answer")
    except B1SampleFailure:
        raise
    except Exception as exc:
        raise B1SampleFailure(str(exc), model_traces, tool_traces) from exc


def _error_prediction(sample_id: str, error: Exception, provider: str) -> dict[str, Any]:
    return {
        "sample_id": sample_id,
        "answer": None,
        "evidence": [],
        "status": "error",
        "program": None,
        "unit": None,
        "metadata": {
            "baseline": "B1_tool_augmented_single_agent",
            "provider": provider,
            "prompt_version": B1_PROMPT_VERSION,
            "error_type": type(error).__name__,
            "error": str(error),
        },
    }


def run_b1(
    samples: Iterable[dict[str, Any]],
    *,
    model: str,
    paths: B1RunPaths,
    provider: str = "openai",
    protocol_id: str | None = None,
    total_output_budget: int = 32768,
    max_model_calls: int = 6,
    max_tool_calls: int = 8,
    request_timeout_seconds: int | None = None,
    strict_schema: bool = True,
    api_caller: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    selected = list(samples)
    if not selected:
        raise ValueError("at least one sample is required")
    existing = [path for path in (paths.gold, paths.predictions, paths.log, paths.report) if path.exists()]
    if existing:
        raise FileExistsError(
            "refusing to overwrite existing B1 artifacts: "
            + ", ".join(str(path) for path in existing)
        )
    run_id = f"b1-{uuid.uuid4()}"
    atomic_write_text(paths.log, "")
    write_jsonl(paths.gold, selected)
    predictions: list[dict[str, Any]] = []
    log_records: list[dict[str, Any]] = []

    for sample in selected:
        started_at = utc_now()
        started = time.monotonic()
        model_traces: list[dict[str, Any]] = []
        tool_traces: list[dict[str, Any]] = []
        final_output_diagnostic: dict[str, Any] | None = None
        error: Exception | None = None
        try:
            prediction, model_traces, tool_traces = execute_b1_sample(
                sample,
                model=model,
                provider=provider,
                total_output_budget=total_output_budget,
                max_model_calls=max_model_calls,
                max_tool_calls=max_tool_calls,
                strict_schema=strict_schema,
                api_caller=api_caller,
            )
        except B1SampleFailure as exc:
            error = exc
            model_traces = exc.model_traces
            tool_traces = exc.tool_traces
            final_output_diagnostic = exc.final_output_diagnostic
            prediction = _error_prediction(sample["sample_id"], exc, provider)
        except Exception as exc:
            error = exc
            prediction = _error_prediction(sample["sample_id"], exc, provider)
        finished_at = utc_now()
        actual_models = [trace.get("model") for trace in model_traces if trace.get("model")]
        log_record = {
            "run_id": run_id,
            "protocol_id": protocol_id,
            "sample_id": sample["sample_id"],
            "system": "B1_tool_augmented_single_agent",
            "model": actual_models[-1] if actual_models else model,
            "started_at": started_at,
            "finished_at": finished_at,
            "input": {
                "dataset": sample["dataset"],
                "split": sample["split"],
                "question": sample["question"],
                "prompt_version": B1_PROMPT_VERSION,
                "provider": provider,
                "initial_prompt_sha256": hashlib.sha256(
                    json.dumps(
                        build_initial_conversation(sample),
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest(),
                "total_output_budget": total_output_budget,
                "max_model_calls": max_model_calls,
                "max_tool_calls": max_tool_calls,
                "request_timeout_seconds": request_timeout_seconds,
                "store": False,
            },
            "output": prediction,
            "tool_calls": tool_traces,
            "model_calls": model_traces,
            "token_usage": {
                key: sum(trace["token_usage"][key] for trace in model_traces)
                for key in ("input", "output", "reasoning", "total")
            },
            "latency_ms": round((time.monotonic() - started) * 1000),
            "error": None if error is None else {"type": type(error).__name__, "message": str(error)},
            "final_output_diagnostic": final_output_diagnostic,
        }
        predictions.append(prediction)
        log_records.append(log_record)
        append_log(paths.log, log_record)

    write_jsonl(paths.predictions, predictions)
    evaluation = evaluate_files(paths.gold, paths.predictions, paths.report)
    evaluation["run"] = {
        "run_id": run_id,
        "system": "B1_tool_augmented_single_agent",
        "provider": provider,
        "requested_model": model,
        "prompt_version": B1_PROMPT_VERSION,
        "protocol_id": protocol_id,
        "sample_count": len(selected),
        "successful_samples": sum(item["error"] is None for item in log_records),
        "failed_samples": sum(item["error"] is not None for item in log_records),
        "model_calls": sum(len(item["model_calls"]) for item in log_records),
        "tool_calls": sum(len(item["tool_calls"]) for item in log_records),
        "samples_with_tool_use": sum(bool(item["tool_calls"]) for item in log_records),
        "samples_with_search_document": sum(
            any(call.get("name") == "search_document" for call in item["tool_calls"])
            for item in log_records
        ),
        "samples_with_search_top_k_12": sum(
            any(
                call.get("name") == "search_document"
                and (call.get("output") or {}).get("top_k") == 12
                for call in item["tool_calls"]
            )
            for item in log_records
        ),
        "samples_with_calculate_finqa": sum(
            any(call.get("name") == "calculate_finqa" for call in item["tool_calls"])
            for item in log_records
        ),
        "tool_call_counts": {
            name: sum(
                call.get("name") == name
                for item in log_records
                for call in item["tool_calls"]
            )
            for name in ("search_document", "calculate_finqa")
        },
        "failed_tool_calls": sum(
            call.get("error") is not None
            for item in log_records
            for call in item["tool_calls"]
        ),
        "total_output_budget_per_sample": total_output_budget,
        "max_model_calls_per_sample": max_model_calls,
        "max_tool_calls_per_sample": max_tool_calls,
        "request_timeout_seconds": request_timeout_seconds,
        "log_completeness": log_completeness(log_records),
        "token_usage": {
            key: sum(item["token_usage"][key] for item in log_records)
            for key in ("input", "output", "reasoning", "total")
        },
        "latency_ms": sum(item["latency_ms"] for item in log_records),
    }
    write_json(paths.report, evaluation)
    return evaluation
