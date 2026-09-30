from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from .program import execute_finqa_program
from .retrieval import search_sample


FINQA_OPERATIONS = (
    "add",
    "subtract",
    "multiply",
    "divide",
    "exp",
    "greater",
    "table_average",
    "table_sum",
    "table_max",
    "table_min",
)


B1_TOOL_DEFINITIONS_V1: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "search_document",
        "description": (
            "Search only the allowed financial document for evidence. Returns exact source "
            "labels that must be reused in the final evidence array."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 1, "maxLength": 500},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 12},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "calculate_finqa",
        "description": (
            "Execute a FinQA-style deterministic program using add, subtract, multiply, "
            "divide, exp, greater, table_average, table_sum, table_max, or table_min. "
            "Earlier results may be referenced as #0, #1, and so on."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "program": {"type": "string", "minLength": 1, "maxLength": 1000}
            },
            "required": ["program"],
            "additionalProperties": False,
        },
    },
]


B1_TOOL_DEFINITIONS_V1_1: list[dict[str, Any]] = [
    B1_TOOL_DEFINITIONS_V1[0],
    {
        "type": "function",
        "name": "calculate_finqa",
        "description": (
            "Execute deterministic FinQA calculation steps. Each step has exactly one "
            "operation and exactly two string arguments. Use #0, #1, and so on to refer "
            "to earlier step results. Never nest operations. For table operations, the "
            "first argument is the row name shown after ROW: and the second is none. "
            "Example: steps=[{operation: subtract, arguments: [3547, 3173]}, "
            "{operation: divide, arguments: [#0, 3173]}]."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 8,
                    "items": {
                        "type": "object",
                        "properties": {
                            "operation": {"type": "string", "enum": list(FINQA_OPERATIONS)},
                            "arguments": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                        },
                        "required": ["operation", "arguments"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["steps"],
            "additionalProperties": False,
        },
    },
]


B1_TOOL_DEFINITIONS = B1_TOOL_DEFINITIONS_V1_1


def _validate_keys(arguments: dict[str, Any], allowed: set[str], required: set[str]) -> None:
    missing = required - arguments.keys()
    extra = arguments.keys() - allowed
    if missing:
        raise ValueError(f"missing arguments: {', '.join(sorted(missing))}")
    if extra:
        raise ValueError(f"unexpected arguments: {', '.join(sorted(extra))}")


def _program_from_structured_steps(steps: Any) -> str:
    if not isinstance(steps, list) or not 1 <= len(steps) <= 8:
        raise ValueError("steps must be an array containing 1 to 8 operations")
    expressions: list[str] = []
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            raise ValueError(f"step {index} must be an object")
        _validate_keys(step, {"operation", "arguments"}, {"operation", "arguments"})
        operation = step["operation"]
        arguments = step["arguments"]
        if operation not in FINQA_OPERATIONS:
            raise ValueError(f"step {index} has unsupported operation: {operation}")
        if not isinstance(arguments, list) or len(arguments) != 2:
            raise ValueError(f"step {index} must have exactly two arguments")
        tokens: list[str] = []
        for argument_index, argument in enumerate(arguments):
            if isinstance(argument, bool) or not isinstance(argument, (str, int, float)):
                raise ValueError(f"step {index} arguments must be strings or numbers")
            token = str(argument).strip()
            if not token:
                raise ValueError(f"step {index} arguments must be non-empty strings")
            is_table_row_label = operation.startswith("table_") and argument_index == 0
            if is_table_row_label:
                if "," in token:
                    raise ValueError(
                        f"step {index} table row label contains reserved punctuation: {token}"
                    )
                parenthesis_depth = 0
                for character in token:
                    if character == "(":
                        parenthesis_depth += 1
                    elif character == ")":
                        parenthesis_depth -= 1
                        if parenthesis_depth < 0:
                            break
                if parenthesis_depth != 0:
                    raise ValueError(
                        f"step {index} table row label has unbalanced parentheses: {token}"
                    )
            elif any(character in token for character in ",()"):
                raise ValueError(f"step {index} argument contains reserved punctuation: {token}")
            tokens.append(token)
        if operation.startswith("table_"):
            if tokens[1].casefold() != "none":
                raise ValueError(f"step {index} table operation must use none as argument 2")
        expressions.append(f"{operation}({tokens[0]}, {tokens[1]})")
    return ", ".join(expressions)


def execute_b1_tool(
    name: str, arguments_json: str, sample: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    started = time.monotonic()
    parsed_arguments: dict[str, Any] | None = None
    error: str | None = None
    try:
        value = json.loads(arguments_json)
        if not isinstance(value, dict):
            raise ValueError("tool arguments must be a JSON object")
        parsed_arguments = value
        if name == "search_document":
            _validate_keys(value, {"query", "top_k"}, {"query"})
            query = value["query"]
            top_k = value.get("top_k", 12)
            result: dict[str, Any] = {
                "ok": True,
                "query": query,
                "top_k": top_k,
                "results": search_sample(sample, query, top_k=top_k),
            }
        elif name == "calculate_finqa":
            if set(value) == {"steps"}:
                program = _program_from_structured_steps(value["steps"])
            elif set(value) == {"program"}:
                # Legacy v1 compatibility for replay and frozen tests. The v1.1 tool
                # schema exposes only structured steps to the model.
                program = value["program"]
                if not isinstance(program, str) or not program.strip():
                    raise ValueError("program must be a non-empty string")
            else:
                raise ValueError("calculate_finqa requires exactly one steps field")
            documents = sample.get("documents") or []
            table = documents[0].get("table") if documents else None
            execution = execute_finqa_program(program, table)
            result = {
                "ok": True,
                "program": program,
                "value": execution.value,
                "steps": [
                    {
                        "operation": step.operation,
                        "arguments": list(step.arguments),
                        "result": step.result,
                    }
                    for step in execution.steps
                ],
            }
        else:
            raise ValueError(f"unknown tool: {name}")
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        error = str(exc)
        result = {"ok": False, "error_type": type(exc).__name__, "error": error}
    output = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
    trace = {
        "name": name,
        "arguments": parsed_arguments,
        "raw_arguments_sha256": hashlib.sha256(arguments_json.encode("utf-8")).hexdigest(),
        "output": result,
        "latency_ms": round((time.monotonic() - started) * 1000),
        "error": error,
    }
    return output, trace
