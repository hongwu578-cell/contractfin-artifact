from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

from .b0 import PREDICTION_OUTPUT_SCHEMA
from .b1_tools import B1_TOOL_DEFINITIONS, FINQA_OPERATIONS, execute_b1_tool
from .evaluation import evaluate_files
from .run_logging import append_log, log_completeness, utc_now
from .schemas import validate_prediction, validate_task_contract
from .utils import atomic_write_text, write_json, write_jsonl


B2_PROMPT_VERSION = "b2-fixed-role-pipeline-v1.1"
B2_VARIANTS = ("full", "no_contract", "no_verifier")

CONTRACT_PROMPT_VERSION = "b2-contract-agent-v1.1"
EVIDENCE_PROMPT_VERSION = "b2-evidence-agent-v1"
SOLVER_PROMPT_VERSION = "b2-solver-agent-v1.1"
VERIFIER_PROMPT_VERSION = "b2-verifier-agent-v1.1"

B2_ROLE_OUTPUT_TOKEN_CAPS: dict[str, tuple[int, ...]] = {
    "contract_agent": (8192,),
    "evidence_agent": (1024, 2048),
    "solver_agent": (8192, 2048),
    "verifier_agent": (11264,),
}

CONTRACT_SYSTEM_PROMPT = """You are the Task Contract Agent in a financial QA study.
Convert the supplied question and allowed document identifiers into a precise task contract.
You cannot search documents, calculate an answer, or access gold data. Set max_retries to 0.
Use only the enumerated FinQA operations when calculation may be needed. Do not guess the
answer. Populate the schema directly and concisely; do not narrate or prolong analysis.
Return exactly one raw JSON object matching the supplied schema."""

EVIDENCE_SYSTEM_PROMPT = """You are the Evidence Agent in a fixed multi-agent financial QA pipeline.
Use only search_document and only the allowed document. Make exactly one search with explicit
top_k=12. Select evidence only from returned labels and copy its text exactly. Do not calculate
or answer the question. Return exactly one raw JSON object matching the supplied schema, with
no prose outside it."""

SOLVER_SYSTEM_PROMPT = """You are the Solver Agent in a fixed multi-agent financial QA pipeline.
Use only the task contract and evidence packet supplied by the controller. For every FinQA
calculation, comparison, or table aggregation, call calculate_finqa exactly once with 1-8
structured steps. Each step has one operation and exactly two string arguments; use #0, #1,
and so on for prior results and never nest operations. For table operations, argument 1 is
the row name and argument 2 is none. Copy the successful tool's canonical program into the
candidate. On the tool-enabled turn, call calculate_finqa directly without narrated or
extended analysis. Evidence labels must come only from the evidence packet. Return exactly
one raw JSON object matching the supplied schema, with no prose outside it."""

VERIFIER_SYSTEM_PROMPT = """You are the independent Verifier Agent in a fixed multi-agent financial QA pipeline.
You cannot search, calculate, or rewrite the candidate. Inspect only the task contract,
evidence packet, candidate, and deterministic audit supplied by the controller. Evaluate the
four Boolean checks first. Set decision=accept and reason_codes=[] if and only if all four
checks are true. If any check is false, set decision=human_review and include at least one
short machine-readable reason code. Do not narrate analysis or add prose. Return exactly one
raw JSON object matching the supplied schema."""


TASK_CONTRACT_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "task_id": {"type": "string"},
        "dataset": {"type": "string", "enum": ["FinQA", "FinanceBench", "TAT-QA"]},
        "question": {"type": "string"},
        "target_entities": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "reporting_period": {"type": "array", "items": {"type": "string"}},
        "allowed_documents": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "answer_type": {
            "type": "string",
            "enum": ["number", "percent", "boolean", "text", "abstain"],
        },
        "unit_scale": {
            "type": "object",
            "properties": {
                "unit": {"type": ["string", "null"]},
                "scale": {"type": ["string", "null"]},
            },
            "required": ["unit", "scale"],
            "additionalProperties": False,
        },
        "required_evidence": {
            "type": "object",
            "properties": {
                "minimum_items": {"type": "integer", "minimum": 1, "maximum": 12},
                "must_support_answer": {"type": "boolean"},
            },
            "required": ["minimum_items", "must_support_answer"],
            "additionalProperties": False,
        },
        "allowed_operations": {
            "type": "array",
            "items": {"type": "string", "enum": list(FINQA_OPERATIONS)},
        },
        "rounding_rule": {
            "type": "object",
            "properties": {
                "decimal_places": {"type": ["integer", "null"], "minimum": 0, "maximum": 10},
                "mode": {"type": "string"},
            },
            "required": ["decimal_places", "mode"],
            "additionalProperties": False,
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
            },
            "required": ["name", "version"],
            "additionalProperties": False,
        },
        "validation_rules": {"type": "array", "items": {"type": "string"}},
        "abstention_conditions": {"type": "array", "items": {"type": "string"}},
        "max_retries": {"type": "integer", "enum": [0]},
    },
    "required": [
        "task_id",
        "dataset",
        "question",
        "target_entities",
        "reporting_period",
        "allowed_documents",
        "answer_type",
        "unit_scale",
        "required_evidence",
        "allowed_operations",
        "rounding_rule",
        "output_schema",
        "validation_rules",
        "abstention_conditions",
        "max_retries",
    ],
    "additionalProperties": False,
}

EVIDENCE_PACKET_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "sample_id": {"type": "string"},
        "search_queries": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 1,
        },
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "text": {"type": "string"},
                },
                "required": ["label", "text"],
                "additionalProperties": False,
            },
            "maxItems": 12,
        },
        "extracted_values": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "string"},
                    "unit": {"type": ["string", "null"]},
                    "source_label": {"type": "string"},
                },
                "required": ["name", "value", "unit", "source_label"],
                "additionalProperties": False,
            },
            "maxItems": 24,
        },
        "sufficient": {"type": "boolean"},
    },
    "required": ["sample_id", "search_queries", "evidence", "extracted_values", "sufficient"],
    "additionalProperties": False,
}

VERDICT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "decision": {"type": "string", "enum": ["accept", "human_review"]},
        "checks": {
            "type": "object",
            "properties": {
                "contract_compliant": {"type": "boolean"},
                "evidence_supported": {"type": "boolean"},
                "program_executed": {"type": "boolean"},
                "answer_consistent": {"type": "boolean"},
            },
            "required": [
                "contract_compliant",
                "evidence_supported",
                "program_executed",
                "answer_consistent",
            ],
            "additionalProperties": False,
        },
        "reason_codes": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 8,
        },
    },
    "required": ["decision", "checks", "reason_codes"],
    "additionalProperties": False,
}


_TASK_CONTRACT_KEYS = set(TASK_CONTRACT_OUTPUT_SCHEMA["required"])
_EVIDENCE_PACKET_KEYS = set(EVIDENCE_PACKET_SCHEMA["required"])
_PREDICTION_KEYS = {"sample_id", "answer", "evidence", "status", "program", "unit"}
_VERDICT_KEYS = set(VERDICT_SCHEMA["required"])
_DEEPSEEK_DSML_SUFFIX = re.compile(
    r"(?:\s*</｜｜DSML｜｜\s+(?:parameter|invoke|calls)>\s*)+\Z"
)


class B2Error(RuntimeError):
    """Base class for safe, replayable B2 failures."""


class B2SampleFailure(B2Error):
    def __init__(
        self,
        message: str,
        model_traces: list[dict[str, Any]],
        tool_traces: list[dict[str, Any]],
        coordination: dict[str, Any],
        final_output_diagnostic: dict[str, Any] | None = None,
    ):
        self.model_traces = list(model_traces)
        self.tool_traces = list(tool_traces)
        self.coordination = dict(coordination)
        self.final_output_diagnostic = final_output_diagnostic
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class B2RunPaths:
    gold: Path
    predictions: Path
    log: Path
    report: Path


@dataclass(slots=True)
class _ExecutionState:
    total_output_budget: int
    max_model_calls: int
    max_tool_calls: int
    consumed_output: int = 0
    model_traces: list[dict[str, Any]] = field(default_factory=list)
    tool_traces: list[dict[str, Any]] = field(default_factory=list)
    coordination: dict[str, Any] = field(default_factory=dict)


def _tool_definition(name: str) -> dict[str, Any]:
    return next(item for item in B1_TOOL_DEFINITIONS if item["name"] == name)


SEARCH_TOOLS = [_tool_definition("search_document")]
CALCULATOR_TOOLS = [_tool_definition("calculate_finqa")]


def _allowed_document_ids(sample: dict[str, Any]) -> list[str]:
    return [
        str(item.get("document_id") or item.get("filename") or "unknown_document")
        for item in sample.get("documents", [])
    ]


def _base_task_input(sample: dict[str, Any]) -> dict[str, Any]:
    return {
        "sample_id": sample["sample_id"],
        "dataset": sample["dataset"],
        "question": sample["question"],
        "allowed_documents": _allowed_document_ids(sample),
    }


def build_b2_payload(
    *,
    system_prompt: str,
    user_input: dict[str, Any],
    conversation_tail: list[dict[str, Any]],
    model: str,
    output_name: str,
    output_schema: dict[str, Any],
    tools: list[dict[str, Any]],
    allow_tools: bool,
    max_output_tokens: int,
    strict_schema: bool,
) -> dict[str, Any]:
    output_format: dict[str, Any] = {
        "type": "json_schema",
        "name": output_name,
        "schema": output_schema,
    }
    if strict_schema:
        output_format["strict"] = True
    payload: dict[str, Any] = {
        "model": model,
        "input": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(user_input, ensure_ascii=False, separators=(",", ":")),
            },
            *conversation_tail,
        ],
        "text": {"format": output_format},
        "max_output_tokens": max_output_tokens,
        "store": False,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto" if allow_tools else "none"
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


def _response_items(response: dict[str, Any]) -> list[dict[str, Any]]:
    output = response.get("output") or []
    if not isinstance(output, list):
        raise B2Error("Responses API output must be an array")
    return [item for item in output if isinstance(item, dict)]


def _function_calls(response: dict[str, Any]) -> list[dict[str, str]]:
    calls: list[dict[str, str]] = []
    for item in _response_items(response):
        if item.get("type") != "function_call":
            continue
        values = (item.get("call_id"), item.get("name"), item.get("arguments"))
        if not all(isinstance(value, str) and value for value in values):
            raise B2Error("function call is missing call_id, name, or arguments")
        calls.append({"call_id": values[0], "name": values[1], "arguments": values[2]})
    return calls


def _output_text(response: dict[str, Any]) -> str:
    texts: list[str] = []
    for item in _response_items(response):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if (
                isinstance(content, dict)
                and content.get("type") == "output_text"
                and isinstance(content.get("text"), str)
            ):
                texts.append(content["text"])
    return "".join(texts)


def _visible_output(response: dict[str, Any], limit: int = 8192) -> dict[str, Any]:
    combined = _output_text(response)
    return {
        "output_text_items": sum(
            1
            for item in _response_items(response)
            if item.get("type") == "message"
            for content in item.get("content", [])
            if isinstance(content, dict)
            and content.get("type") == "output_text"
            and isinstance(content.get("text"), str)
        ),
        "character_count": len(combined),
        "sha256": hashlib.sha256(combined.encode("utf-8")).hexdigest(),
        "visible_text": combined[:limit],
        "truncated": len(combined) > limit,
        "reasoning_text_retained": False,
    }


def _extract_object(response: dict[str, Any], provider: str) -> tuple[dict[str, Any], str | None]:
    diagnostic = _visible_output(response)
    raw_text = _output_text(response)
    if diagnostic["output_text_items"] < 1 or not raw_text:
        raise B2Error("agent response contained no complete output_text")
    normalization: str | None = None
    try:
        value = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        if provider != "deepseek":
            raise B2Error("agent structured output was not valid JSON") from exc
        stripped = raw_text.lstrip()
        try:
            value, end = json.JSONDecoder().raw_decode(stripped)
        except json.JSONDecodeError as raw_exc:
            raise B2Error("agent structured output was not valid JSON") from raw_exc
        remainder = stripped[end:]
        if not remainder or _DEEPSEEK_DSML_SUFFIX.fullmatch(remainder) is None:
            raise B2Error("agent structured output was not valid JSON") from exc
        normalization = "removed_deepseek_dsml_closing_suffix_v1"
    if not isinstance(value, dict):
        raise B2Error("agent structured output was not an object")
    return value, normalization


def _model_trace(
    response: dict[str, Any],
    *,
    role: str,
    role_call_index: int,
    global_call_index: int,
    latency_ms: int,
    request_sha256: str,
    requested_max_output_tokens: int,
) -> dict[str, Any]:
    incomplete = response.get("incomplete_details") or {}
    error = response.get("error") or {}
    return {
        "role": role,
        "role_call_index": role_call_index,
        "global_call_index": global_call_index,
        "response_id": response.get("id"),
        "model": response.get("model"),
        "status": response.get("status"),
        "incomplete_reason": incomplete.get("reason"),
        "provider_error_code": error.get("code"),
        "output_item_types": [item.get("type") for item in _response_items(response)],
        "token_usage": _usage(response),
        "latency_ms": latency_ms,
        "request_sha256": request_sha256,
        "requested_max_output_tokens": requested_max_output_tokens,
    }


def _run_stage(
    *,
    sample: dict[str, Any],
    role: str,
    system_prompt: str,
    user_input: dict[str, Any],
    output_name: str,
    output_schema: dict[str, Any],
    tools: list[dict[str, Any]],
    allowed_tool_names: set[str],
    role_max_model_calls: int,
    role_max_tool_calls: int,
    role_output_token_caps: tuple[int, ...],
    model: str,
    provider: str,
    strict_schema: bool,
    api_caller: Callable[[dict[str, Any]], dict[str, Any]],
    state: _ExecutionState,
) -> dict[str, Any]:
    if len(role_output_token_caps) != role_max_model_calls or any(
        value < 1 for value in role_output_token_caps
    ):
        raise ValueError(f"invalid output-token caps for {role}")
    conversation_tail: list[dict[str, Any]] = []
    role_tool_calls = 0
    for role_call_index in range(1, role_max_model_calls + 1):
        if len(state.model_traces) >= state.max_model_calls:
            raise B2Error("maximum global model call count exceeded")
        remaining_output = state.total_output_budget - state.consumed_output
        if remaining_output < 1:
            raise B2Error("cumulative model output budget was exhausted")
        requested_max_output_tokens = min(
            remaining_output,
            role_output_token_caps[role_call_index - 1],
        )
        allow_tools = bool(tools) and role_call_index < role_max_model_calls
        payload = build_b2_payload(
            system_prompt=system_prompt,
            user_input=user_input,
            conversation_tail=conversation_tail,
            model=model,
            output_name=output_name,
            output_schema=output_schema,
            tools=tools,
            allow_tools=allow_tools,
            max_output_tokens=requested_max_output_tokens,
            strict_schema=strict_schema,
        )
        request_sha256 = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()
        started = time.monotonic()
        response = api_caller(payload)
        latency_ms = round((time.monotonic() - started) * 1000)
        trace = _model_trace(
            response,
            role=role,
            role_call_index=role_call_index,
            global_call_index=len(state.model_traces) + 1,
            latency_ms=latency_ms,
            request_sha256=request_sha256,
            requested_max_output_tokens=requested_max_output_tokens,
        )
        state.model_traces.append(trace)
        state.consumed_output += trace["token_usage"]["output"]
        if response.get("status") != "completed":
            raise B2Error(
                "model call did not complete "
                f"(role={role}, status={response.get('status')}, "
                f"reason={trace['incomplete_reason']})"
            )
        conversation_tail.extend(_response_items(response))
        calls = _function_calls(response)
        if not calls:
            try:
                value, normalization = _extract_object(response, provider)
            except B2Error as exc:
                raise B2SampleFailure(
                    str(exc),
                    state.model_traces,
                    state.tool_traces,
                    state.coordination,
                    _visible_output(response),
                ) from exc
            if normalization is not None:
                trace["transport_normalization"] = normalization
            return value
        if not allow_tools:
            raise B2Error(f"{role} attempted a tool call on its forced final turn")
        if role_tool_calls + len(calls) > role_max_tool_calls:
            raise B2Error(f"{role} exceeded its tool-call limit")
        if len(state.tool_traces) + len(calls) > state.max_tool_calls:
            raise B2Error("maximum global tool call count exceeded")
        for call in calls:
            if call["name"] not in allowed_tool_names:
                raise B2Error(f"{role} attempted disallowed tool: {call['name']}")
            output, tool_trace = execute_b1_tool(call["name"], call["arguments"], sample)
            tool_trace.update(
                {
                    "call_id": call["call_id"],
                    "actor": role,
                    "global_model_call_index": len(state.model_traces),
                }
            )
            state.tool_traces.append(tool_trace)
            role_tool_calls += 1
            conversation_tail.append(
                {
                    "type": "function_call_output",
                    "call_id": call["call_id"],
                    "output": output,
                }
            )
    raise B2Error(f"{role} reached its model-call limit without structured output")


def _require_exact_keys(value: dict[str, Any], expected: set[str], name: str) -> None:
    missing = expected - value.keys()
    extra = value.keys() - expected
    if missing:
        raise B2Error(f"{name} missing fields: {', '.join(sorted(missing))}")
    if extra:
        raise B2Error(f"{name} has unexpected fields: {', '.join(sorted(extra))}")


def _validate_contract(contract: dict[str, Any], sample: dict[str, Any]) -> None:
    _require_exact_keys(contract, _TASK_CONTRACT_KEYS, "task contract")
    errors = validate_task_contract(contract)
    if errors:
        raise B2Error("task contract validation failed: " + "; ".join(errors))
    if contract["task_id"] != sample["sample_id"]:
        raise B2Error("task contract task_id does not match the sample")
    if contract["dataset"] != sample["dataset"] or contract["question"] != sample["question"]:
        raise B2Error("task contract changed the dataset or question")
    if contract["allowed_documents"] != _allowed_document_ids(sample):
        raise B2Error("task contract changed the allowed document set")
    if contract["max_retries"] != 0:
        raise B2Error("task contract max_retries must be zero")
    if not set(contract["allowed_operations"]) <= set(FINQA_OPERATIONS):
        raise B2Error("task contract contains an unsupported operation")


def _validate_evidence_packet(
    packet: dict[str, Any], sample: dict[str, Any], state: _ExecutionState
) -> None:
    _require_exact_keys(packet, _EVIDENCE_PACKET_KEYS, "evidence packet")
    if packet.get("sample_id") != sample["sample_id"]:
        raise B2Error("evidence packet sample_id does not match the input")
    searches = [item for item in state.tool_traces if item.get("actor") == "evidence_agent"]
    if len(searches) != 1:
        raise B2Error("evidence agent must make exactly one search")
    if searches[0].get("name") != "search_document":
        raise B2Error("evidence agent's first tool call must be search_document")
    first_arguments = searches[0].get("arguments") or {}
    if first_arguments.get("top_k") != 12:
        raise B2Error("evidence agent's first search must explicitly use top_k=12")
    queries = [(item.get("arguments") or {}).get("query") for item in searches]
    if packet.get("search_queries") != queries:
        raise B2Error("evidence packet search_queries do not match executed searches")
    available: dict[str, str] = {}
    for search in searches:
        if search.get("error") is not None:
            raise B2Error("evidence agent search failed")
        for result in (search.get("output") or {}).get("results", []):
            if isinstance(result, dict) and isinstance(result.get("label"), str):
                available[result["label"]] = str(result.get("text", ""))
    evidence = packet.get("evidence")
    if not isinstance(evidence, list) or len(evidence) > 12:
        raise B2Error("evidence packet evidence must be an array of at most 12 items")
    selected_labels: set[str] = set()
    for item in evidence:
        if not isinstance(item, dict) or set(item) != {"label", "text"}:
            raise B2Error("evidence packet item is malformed")
        label = item.get("label")
        if label not in available or item.get("text") != available[label]:
            raise B2Error("evidence packet contains evidence not returned by search")
        selected_labels.add(label)
    if packet.get("sufficient") is True and not evidence:
        raise B2Error("a sufficient evidence packet must contain evidence")
    values = packet.get("extracted_values")
    if not isinstance(values, list) or len(values) > 24:
        raise B2Error("extracted_values must be an array of at most 24 items")
    for item in values:
        if not isinstance(item, dict) or set(item) != {"name", "value", "unit", "source_label"}:
            raise B2Error("extracted value is malformed")
        if item.get("source_label") not in selected_labels:
            raise B2Error("extracted value refers to unselected evidence")


def _validate_candidate(
    candidate: dict[str, Any], sample: dict[str, Any], packet: dict[str, Any], state: _ExecutionState
) -> None:
    _require_exact_keys(candidate, _PREDICTION_KEYS, "solver candidate")
    errors = validate_prediction(candidate)
    if errors:
        raise B2Error("solver candidate validation failed: " + "; ".join(errors))
    if candidate.get("sample_id") != sample["sample_id"]:
        raise B2Error("solver candidate sample_id does not match the input")
    packet_labels = {item["label"] for item in packet["evidence"]}
    if not set(candidate.get("evidence") or []) <= packet_labels:
        raise B2Error("solver candidate cites evidence outside the evidence packet")
    calculations = [item for item in state.tool_traces if item.get("actor") == "solver_agent"]
    if len(calculations) != 1 or calculations[0].get("name") != "calculate_finqa":
        raise B2Error("solver agent must make exactly one calculate_finqa call")
    calculation = calculations[0]
    if calculation.get("error") is not None or not (calculation.get("output") or {}).get("ok"):
        raise B2Error("solver calculator call failed")
    if candidate.get("program") != calculation["output"].get("program"):
        raise B2Error("solver candidate program does not match the executed canonical program")
    if candidate.get("status") == "answered" and candidate.get("answer") is None:
        raise B2Error("answered solver candidate must contain an answer")


def _candidate_audit(
    *,
    candidate: dict[str, Any],
    packet: dict[str, Any],
    contract: dict[str, Any] | None,
    variant: str,
    state: _ExecutionState,
) -> dict[str, Any]:
    packet_labels = {item["label"] for item in packet["evidence"]}
    calculation = next(
        (item for item in state.tool_traces if item.get("actor") == "solver_agent"), None
    )
    calculation_output = (calculation or {}).get("output") or {}
    return {
        "contract_requirement_satisfied": contract is not None or variant == "no_contract",
        "candidate_schema_valid": not validate_prediction(candidate),
        "candidate_evidence_within_packet": set(candidate.get("evidence") or []) <= packet_labels,
        "calculator_succeeded": bool(calculation_output.get("ok"))
        and (calculation or {}).get("error") is None,
        "program_matches_executed_canonical": candidate.get("program")
        == calculation_output.get("program"),
        "no_failed_tools": all(item.get("error") is None for item in state.tool_traces),
        "execution_value": calculation_output.get("value"),
    }


def _validate_verdict(verdict: dict[str, Any]) -> None:
    _require_exact_keys(verdict, _VERDICT_KEYS, "verifier verdict")
    if verdict.get("decision") not in {"accept", "human_review"}:
        raise B2Error("verifier decision is invalid")
    checks = verdict.get("checks")
    expected_checks = {
        "contract_compliant",
        "evidence_supported",
        "program_executed",
        "answer_consistent",
    }
    if not isinstance(checks, dict) or set(checks) != expected_checks:
        raise B2Error("verifier checks are malformed")
    if any(not isinstance(value, bool) for value in checks.values()):
        raise B2Error("verifier checks must be booleans")
    reasons = verdict.get("reason_codes")
    if not isinstance(reasons, list) or len(reasons) > 8 or any(
        not isinstance(item, str) or not item for item in reasons
    ):
        raise B2Error("verifier reason_codes are malformed")


def _normalize_verdict(
    verdict: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    normalized = {
        "decision": verdict["decision"],
        "checks": dict(verdict["checks"]),
        "reason_codes": list(verdict["reason_codes"]),
    }
    triggers: list[str] = []
    if verdict["decision"] == "accept":
        false_checks = [name for name, passed in verdict["checks"].items() if not passed]
        if false_checks:
            triggers.extend(f"false_check:{name}" for name in sorted(false_checks))
        if verdict["reason_codes"]:
            triggers.append("accept_with_reason_codes")
        if triggers:
            normalized["decision"] = "human_review"
            reason_code = "controller_downgraded_inconsistent_accept"
            if reason_code not in normalized["reason_codes"] and len(normalized["reason_codes"]) < 8:
                normalized["reason_codes"].append(reason_code)
    elif not normalized["reason_codes"]:
        triggers.append("human_review_without_reason_code")
        normalized["reason_codes"].append("verifier_unspecified_review_reason")
    if not triggers:
        return normalized, None
    return normalized, {
        "rule": "conservative_verifier_normalization_v1_1",
        "original_decision": verdict["decision"],
        "effective_decision": normalized["decision"],
        "triggers": triggers,
    }


def _finalize_prediction(
    *,
    candidate: dict[str, Any],
    verdict: dict[str, Any] | None,
    audit: dict[str, Any],
    variant: str,
    provider: str,
    state: _ExecutionState,
) -> dict[str, Any]:
    local_checks = [value for key, value in audit.items() if key != "execution_value"]
    accepted = all(local_checks)
    verifier_decision: str | None = None
    if verdict is not None:
        verifier_decision = verdict["decision"]
        accepted = accepted and verifier_decision == "accept" and all(verdict["checks"].values())
    prediction = dict(candidate)
    if not accepted:
        prediction.update({"answer": None, "status": "human_review"})
    prediction["metadata"] = {
        "baseline": "B2_fixed_role_multi_agent",
        "variant": variant,
        "provider": provider,
        "prompt_version": B2_PROMPT_VERSION,
        "model_calls": len(state.model_traces),
        "tool_calls": len(state.tool_traces),
        "verifier_decision": verifier_decision,
        "verifier_normalized": state.coordination.get("verifier_normalization") is not None,
        "local_gate_passed": all(local_checks),
    }
    return prediction


def execute_b2_sample(
    sample: dict[str, Any],
    *,
    model: str,
    provider: str,
    variant: str,
    total_output_budget: int,
    max_model_calls: int,
    max_tool_calls: int,
    strict_schema: bool,
    api_caller: Callable[[dict[str, Any]], dict[str, Any]],
) -> tuple[
    dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]
]:
    if variant not in B2_VARIANTS:
        raise ValueError(f"unsupported B2 variant: {variant}")
    if total_output_budget < 1 or max_model_calls < 1 or max_tool_calls < 1:
        raise ValueError("B2 budgets must be positive")
    active_roles = ["evidence_agent", "solver_agent"]
    if variant != "no_contract":
        active_roles.insert(0, "contract_agent")
    if variant != "no_verifier":
        active_roles.append("verifier_agent")
    required_output_budget = sum(
        sum(B2_ROLE_OUTPUT_TOKEN_CAPS[role]) for role in active_roles
    )
    if total_output_budget < required_output_budget:
        raise ValueError(
            "total output budget is below the B2-v1.1 fixed role allocation "
            f"({total_output_budget} < {required_output_budget})"
        )
    state = _ExecutionState(total_output_budget, max_model_calls, max_tool_calls)
    base_input = _base_task_input(sample)
    try:
        contract: dict[str, Any] | None = None
        if variant != "no_contract":
            contract = _run_stage(
                sample=sample,
                role="contract_agent",
                system_prompt=CONTRACT_SYSTEM_PROMPT,
                user_input=base_input,
                output_name="contractfin_task_contract",
                output_schema=TASK_CONTRACT_OUTPUT_SCHEMA,
                tools=[],
                allowed_tool_names=set(),
                role_max_model_calls=1,
                role_max_tool_calls=0,
                role_output_token_caps=B2_ROLE_OUTPUT_TOKEN_CAPS["contract_agent"],
                model=model,
                provider=provider,
                strict_schema=strict_schema,
                api_caller=api_caller,
                state=state,
            )
            _validate_contract(contract, sample)
        state.coordination["task_contract"] = contract

        packet = _run_stage(
            sample=sample,
            role="evidence_agent",
            system_prompt=EVIDENCE_SYSTEM_PROMPT,
            user_input={**base_input, "task_contract": contract},
            output_name="contractfin_evidence_packet",
            output_schema=EVIDENCE_PACKET_SCHEMA,
            tools=SEARCH_TOOLS,
            allowed_tool_names={"search_document"},
            role_max_model_calls=2,
            role_max_tool_calls=1,
            role_output_token_caps=B2_ROLE_OUTPUT_TOKEN_CAPS["evidence_agent"],
            model=model,
            provider=provider,
            strict_schema=strict_schema,
            api_caller=api_caller,
            state=state,
        )
        _validate_evidence_packet(packet, sample, state)
        state.coordination["evidence_packet"] = packet

        candidate = _run_stage(
            sample=sample,
            role="solver_agent",
            system_prompt=SOLVER_SYSTEM_PROMPT,
            user_input={
                **base_input,
                "task_contract": contract,
                "evidence_packet": packet,
            },
            output_name="contractfin_solver_candidate",
            output_schema=PREDICTION_OUTPUT_SCHEMA,
            tools=CALCULATOR_TOOLS,
            allowed_tool_names={"calculate_finqa"},
            role_max_model_calls=2,
            role_max_tool_calls=1,
            role_output_token_caps=B2_ROLE_OUTPUT_TOKEN_CAPS["solver_agent"],
            model=model,
            provider=provider,
            strict_schema=strict_schema,
            api_caller=api_caller,
            state=state,
        )
        _validate_candidate(candidate, sample, packet, state)
        state.coordination["solver_candidate"] = candidate
        audit = _candidate_audit(
            candidate=candidate,
            packet=packet,
            contract=contract,
            variant=variant,
            state=state,
        )
        state.coordination["deterministic_audit"] = audit

        verdict: dict[str, Any] | None = None
        if variant != "no_verifier":
            raw_verdict = _run_stage(
                sample=sample,
                role="verifier_agent",
                system_prompt=VERIFIER_SYSTEM_PROMPT,
                user_input={
                    **base_input,
                    "task_contract": contract,
                    "evidence_packet": packet,
                    "solver_candidate": candidate,
                    "deterministic_audit": audit,
                },
                output_name="contractfin_verifier_verdict",
                output_schema=VERDICT_SCHEMA,
                tools=[],
                allowed_tool_names=set(),
                role_max_model_calls=1,
                role_max_tool_calls=0,
                role_output_token_caps=B2_ROLE_OUTPUT_TOKEN_CAPS["verifier_agent"],
                model=model,
                provider=provider,
                strict_schema=strict_schema,
                api_caller=api_caller,
                state=state,
            )
            state.coordination["verifier_raw_verdict"] = raw_verdict
            _validate_verdict(raw_verdict)
            verdict, normalization = _normalize_verdict(raw_verdict)
            state.coordination["verifier_normalization"] = normalization
        state.coordination["verifier_verdict"] = verdict
        prediction = _finalize_prediction(
            candidate=candidate,
            verdict=verdict,
            audit=audit,
            variant=variant,
            provider=provider,
            state=state,
        )
        return prediction, state.model_traces, state.tool_traces, state.coordination
    except B2SampleFailure:
        raise
    except Exception as exc:
        raise B2SampleFailure(
            str(exc),
            state.model_traces,
            state.tool_traces,
            state.coordination,
        ) from exc


def _error_prediction(sample_id: str, provider: str, variant: str, error: Exception) -> dict[str, Any]:
    return {
        "sample_id": sample_id,
        "answer": None,
        "evidence": [],
        "status": "error",
        "program": None,
        "unit": None,
        "metadata": {
            "baseline": "B2_fixed_role_multi_agent",
            "variant": variant,
            "provider": provider,
            "prompt_version": B2_PROMPT_VERSION,
            "error_type": type(error).__name__,
            "error": str(error),
        },
    }


def run_b2(
    samples: Iterable[dict[str, Any]],
    *,
    model: str,
    paths: B2RunPaths,
    provider: str = "openai",
    variant: str = "full",
    protocol_id: str | None = None,
    total_output_budget: int = 32768,
    max_model_calls: int = 6,
    max_tool_calls: int = 2,
    request_timeout_seconds: int | None = None,
    strict_schema: bool = True,
    api_caller: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    selected = list(samples)
    if not selected:
        raise ValueError("at least one sample is required")
    if variant not in B2_VARIANTS:
        raise ValueError(f"unsupported B2 variant: {variant}")
    existing = [path for path in (paths.gold, paths.predictions, paths.log, paths.report) if path.exists()]
    if existing:
        raise FileExistsError(
            "refusing to overwrite existing B2 artifacts: "
            + ", ".join(str(path) for path in existing)
        )
    run_id = f"b2-{uuid.uuid4()}"
    atomic_write_text(paths.log, "")
    write_jsonl(paths.gold, selected)
    predictions: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []

    for sample in selected:
        started_at = utc_now()
        started = time.monotonic()
        model_traces: list[dict[str, Any]] = []
        tool_traces: list[dict[str, Any]] = []
        coordination: dict[str, Any] = {}
        final_output_diagnostic: dict[str, Any] | None = None
        error: Exception | None = None
        try:
            prediction, model_traces, tool_traces, coordination = execute_b2_sample(
                sample,
                model=model,
                provider=provider,
                variant=variant,
                total_output_budget=total_output_budget,
                max_model_calls=max_model_calls,
                max_tool_calls=max_tool_calls,
                strict_schema=strict_schema,
                api_caller=api_caller,
            )
        except B2SampleFailure as exc:
            error = exc
            model_traces = exc.model_traces
            tool_traces = exc.tool_traces
            coordination = exc.coordination
            final_output_diagnostic = exc.final_output_diagnostic
            prediction = _error_prediction(sample["sample_id"], provider, variant, exc)
        except Exception as exc:
            error = exc
            prediction = _error_prediction(sample["sample_id"], provider, variant, exc)
        finished_at = utc_now()
        actual_models = [item.get("model") for item in model_traces if item.get("model")]
        record = {
            "run_id": run_id,
            "protocol_id": protocol_id,
            "sample_id": sample["sample_id"],
            "system": "B2_fixed_role_multi_agent",
            "model": actual_models[-1] if actual_models else model,
            "started_at": started_at,
            "finished_at": finished_at,
            "input": {
                "dataset": sample["dataset"],
                "split": sample["split"],
                "question": sample["question"],
                "variant": variant,
                "prompt_version": B2_PROMPT_VERSION,
                "provider": provider,
                "initial_input_sha256": hashlib.sha256(
                    json.dumps(
                        _base_task_input(sample),
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest(),
                "total_output_budget": total_output_budget,
                "role_output_token_caps": {
                    role: list(caps) for role, caps in B2_ROLE_OUTPUT_TOKEN_CAPS.items()
                },
                "max_model_calls": max_model_calls,
                "max_tool_calls": max_tool_calls,
                "request_timeout_seconds": request_timeout_seconds,
                "store": False,
            },
            "output": prediction,
            "coordination": coordination,
            "agent_calls": model_traces,
            "tool_calls": tool_traces,
            "token_usage": {
                key: sum(item["token_usage"][key] for item in model_traces)
                for key in ("input", "output", "reasoning", "total")
            },
            "latency_ms": round((time.monotonic() - started) * 1000),
            "error": None if error is None else {"type": type(error).__name__, "message": str(error)},
            "final_output_diagnostic": final_output_diagnostic,
        }
        predictions.append(prediction)
        records.append(record)
        append_log(paths.log, record)

    write_jsonl(paths.predictions, predictions)
    evaluation = evaluate_files(paths.gold, paths.predictions, paths.report)
    role_names = ("contract_agent", "evidence_agent", "solver_agent", "verifier_agent")
    evaluation["run"] = {
        "run_id": run_id,
        "system": "B2_fixed_role_multi_agent",
        "variant": variant,
        "provider": provider,
        "requested_model": model,
        "prompt_version": B2_PROMPT_VERSION,
        "protocol_id": protocol_id,
        "sample_count": len(selected),
        "successful_samples": sum(item["error"] is None for item in records),
        "failed_samples": sum(item["error"] is not None for item in records),
        "model_calls": sum(len(item["agent_calls"]) for item in records),
        "role_model_call_counts": {
            role: sum(
                call.get("role") == role
                for item in records
                for call in item["agent_calls"]
            )
            for role in role_names
        },
        "tool_calls": sum(len(item["tool_calls"]) for item in records),
        "tool_call_counts": {
            name: sum(
                call.get("name") == name
                for item in records
                for call in item["tool_calls"]
            )
            for name in ("search_document", "calculate_finqa")
        },
        "samples_with_contract": sum(
            item.get("coordination", {}).get("task_contract") is not None for item in records
        ),
        "samples_with_verifier": sum(
            item.get("coordination", {}).get("verifier_verdict") is not None for item in records
        ),
        "verifier_accepts": sum(
            (item.get("coordination", {}).get("verifier_verdict") or {}).get("decision")
            == "accept"
            for item in records
        ),
        "human_review_outputs": sum(item["output"].get("status") == "human_review" for item in records),
        "verifier_normalizations": sum(
            item.get("coordination", {}).get("verifier_normalization") is not None
            for item in records
        ),
        "samples_with_search_document": sum(
            any(call.get("name") == "search_document" for call in item["tool_calls"])
            for item in records
        ),
        "samples_with_search_top_k_12": sum(
            any(
                call.get("name") == "search_document"
                and (call.get("output") or {}).get("top_k") == 12
                for call in item["tool_calls"]
            )
            for item in records
        ),
        "samples_with_calculate_finqa": sum(
            any(call.get("name") == "calculate_finqa" for call in item["tool_calls"])
            for item in records
        ),
        "failed_tool_calls": sum(
            call.get("error") is not None
            for item in records
            for call in item["tool_calls"]
        ),
        "total_output_budget_per_sample": total_output_budget,
        "role_output_token_caps": {
            role: list(caps) for role, caps in B2_ROLE_OUTPUT_TOKEN_CAPS.items()
        },
        "max_model_calls_per_sample": max_model_calls,
        "max_tool_calls_per_sample": max_tool_calls,
        "request_timeout_seconds": request_timeout_seconds,
        "log_completeness": log_completeness(records),
        "token_usage": {
            key: sum(item["token_usage"][key] for item in records)
            for key in ("input", "output", "reasoning", "total")
        },
        "latency_ms": sum(item["latency_ms"] for item in records),
    }
    write_json(paths.report, evaluation)
    return evaluation
