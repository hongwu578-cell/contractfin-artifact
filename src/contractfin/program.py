from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

from .utils import normalize_text


@dataclass(frozen=True, slots=True)
class ExecutionStep:
    operation: str
    arguments: tuple[Any, ...]
    result: float | str


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    value: float | str
    steps: tuple[ExecutionStep, ...]


def _split_top_level(value: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    for index, char in enumerate(value):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced closing parenthesis")
        elif char == "," and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    if depth != 0:
        raise ValueError("unbalanced parenthesis")
    final = value[start:].strip()
    if final:
        parts.append(final)
    return parts


def _parse_number(value: str) -> float:
    token = value.strip().replace(",", "")
    if token.startswith("const_"):
        constant = token[6:]
        if constant == "m1":
            return -1.0
        return float(constant)
    negative = token.startswith("(") and token.endswith(")")
    percent = "%" in token
    token = token.strip("()").replace("$", "").replace("%", "")
    result = float(token)
    if percent:
        result /= 100.0
    return -result if negative else result


def _cell_number(value: Any) -> float | None:
    text = str(value).strip()
    if not text or text in {"-", "—", "–", "none", "n/a", "nm"}:
        return None
    cleaned = text.replace(",", "")
    match = re.search(r"[-+]?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    result = float(match.group(0))
    prefix = cleaned[: match.start()].replace("$", "").replace("£", "").replace("€", "").strip()
    negative = result >= 0 and prefix.endswith("(")
    if negative:
        result = -result
    return result / 100.0 if "%" in cleaned else result


def _table_rows(table: Any) -> dict[str, list[float]]:
    rows: dict[str, list[float]] = {}
    if not isinstance(table, list):
        return rows
    for row in table:
        if not isinstance(row, list) or len(row) < 2:
            continue
        label = normalize_text(row[0])
        numbers = [number for cell in row[1:] if (number := _cell_number(cell)) is not None]
        if label and numbers:
            rows[label] = numbers
    return rows


def _resolve_argument(token: str, previous: list[float | str]) -> float | str | None:
    token = token.strip()
    if token.casefold() == "none":
        return None
    if token.startswith("#"):
        try:
            return previous[int(token[1:])]
        except (ValueError, IndexError) as exc:
            raise ValueError(f"invalid reference: {token}") from exc
    try:
        return _parse_number(token)
    except ValueError:
        return token


def _require_numeric(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} requires numeric arguments")
    return float(value)


def execute_finqa_program(program: str, table: Any = None) -> ExecutionResult:
    expressions = _split_top_level(program)
    if not expressions:
        raise ValueError("program is empty")
    previous: list[float | str] = []
    steps: list[ExecutionStep] = []
    rows = _table_rows(table)
    for expression in expressions:
        match = re.fullmatch(r"([A-Za-z_]+)\((.*)\)", expression.strip())
        if not match:
            raise ValueError(f"invalid expression: {expression}")
        operation = match.group(1).casefold()
        argument_tokens = _split_top_level(match.group(2))
        arguments = tuple(_resolve_argument(token, previous) for token in argument_tokens)
        if operation.startswith("table_"):
            if not argument_tokens:
                raise ValueError(f"{operation} requires a row label")
            label = normalize_text(argument_tokens[0])
            values = rows.get(label)
            if not values:
                raise ValueError(f"table row not found: {argument_tokens[0]}")
            if operation == "table_average":
                result: float | str = sum(values) / len(values)
            elif operation == "table_sum":
                result = sum(values)
            elif operation == "table_max":
                result = max(values)
            elif operation == "table_min":
                result = min(values)
            else:
                raise ValueError(f"unsupported table operation: {operation}")
        else:
            if len(arguments) != 2:
                raise ValueError(f"{operation} requires exactly two arguments")
            left = _require_numeric(arguments[0], operation)
            right = _require_numeric(arguments[1], operation)
            if operation == "add":
                result = left + right
            elif operation == "subtract":
                result = left - right
            elif operation == "multiply":
                result = left * right
            elif operation == "divide":
                if right == 0:
                    raise ValueError("division by zero")
                result = left / right
            elif operation == "exp":
                result = left**right
            elif operation == "greater":
                result = "yes" if left > right else "no"
            else:
                raise ValueError(f"unsupported operation: {operation}")
        if isinstance(result, float) and not math.isfinite(result):
            raise ValueError("program produced a non-finite result")
        previous.append(result)
        steps.append(ExecutionStep(operation, arguments, result))
    return ExecutionResult(previous[-1], tuple(steps))


def execution_values_match(predicted: float | str, gold: Any) -> bool:
    if isinstance(predicted, str):
        return normalize_text(predicted) == normalize_text(gold)
    try:
        gold_value = float(gold)
    except (TypeError, ValueError):
        return False
    return math.isclose(predicted, gold_value, rel_tol=1e-4, abs_tol=1e-4)
