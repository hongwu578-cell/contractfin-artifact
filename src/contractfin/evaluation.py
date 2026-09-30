from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .schemas import validate_prediction
from .program import execute_finqa_program, execution_values_match
from .utils import normalize_text, read_jsonl, write_json


NUMBER_RE = re.compile(r"(?<![A-Za-z0-9])[-+]?\(?\d[\d,]*(?:\.\d+)?\)?")


@dataclass(frozen=True, slots=True)
class NumericValue:
    value: float
    unit: str | None
    scale: str | None


def _unit_and_scale(text: str) -> tuple[str | None, str | None, float]:
    normalized = normalize_text(text)
    unit: str | None = None
    scale: str | None = None
    multiplier = 1.0
    if "%" in normalized or "percent" in normalized or "percentage" in normalized:
        unit = "percent"
        multiplier /= 100.0
    elif "$" in normalized or "usd" in normalized or "dollar" in normalized:
        unit = "usd"
    scale_words = [
        ("trillion", "trillion", 1_000_000_000_000.0),
        ("billion", "billion", 1_000_000_000.0),
        ("million", "million", 1_000_000.0),
        ("thousand", "thousand", 1_000.0),
    ]
    for word, label, factor in scale_words:
        if word in normalized:
            scale = label
            multiplier *= factor
            break
    return unit, scale, multiplier


def parse_single_numeric(value: Any) -> NumericValue | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        numeric = float(value)
        return NumericValue(numeric, None, None) if math.isfinite(numeric) else None
    text = str(value)
    matches = list(NUMBER_RE.finditer(text))
    if len(matches) != 1:
        return None
    token = matches[0].group(0)
    stripped_text = text.strip()
    negative_parentheses = (
        (token.startswith("(") and token.endswith(")"))
        or (stripped_text.startswith("(") and stripped_text.endswith(")") and not token.startswith("-"))
    )
    token = token.strip("()").replace(",", "")
    try:
        numeric = float(token)
    except ValueError:
        return None
    if negative_parentheses:
        numeric = -numeric
    unit, scale, multiplier = _unit_and_scale(text)
    numeric *= multiplier
    return NumericValue(numeric, unit, scale)


def answers_match(
    predicted: Any,
    gold: Any,
    *,
    absolute_tolerance: float = 1e-6,
    relative_tolerance: float = 1e-4,
) -> bool:
    if predicted is None or gold is None:
        return predicted is gold
    if isinstance(predicted, bool) or isinstance(gold, bool):
        return predicted is gold or normalize_text(predicted) == normalize_text(gold)
    predicted_text = normalize_text(predicted)
    gold_text = normalize_text(gold)
    if predicted_text == gold_text:
        return True
    predicted_numeric = parse_single_numeric(predicted)
    gold_numeric = parse_single_numeric(gold)
    if predicted_numeric is None or gold_numeric is None:
        return False
    return math.isclose(
        predicted_numeric.value,
        gold_numeric.value,
        rel_tol=relative_tolerance,
        abs_tol=absolute_tolerance,
    )


def unit_scale_error(predicted: Any, gold: Any, explicit_unit: str | None = None) -> bool:
    predicted_text = f"{predicted} {explicit_unit or ''}"
    gold_numeric = parse_single_numeric(gold)
    predicted_numeric = parse_single_numeric(predicted_text)
    if gold_numeric is None or predicted_numeric is None:
        return False
    if gold_numeric.unit and predicted_numeric.unit != gold_numeric.unit:
        return True
    if gold_numeric.scale and predicted_numeric.scale != gold_numeric.scale:
        return True
    return False


def _evidence_key(item: Any) -> str:
    if isinstance(item, str):
        return normalize_text(item)
    if not isinstance(item, dict):
        return normalize_text(item)
    for key in ("id", "evidence_id"):
        if item.get(key) is not None:
            return normalize_text(item[key])
    document = item.get("document_id", item.get("doc_name"))
    page = item.get("page", item.get("page_number"))
    if document is not None and page is not None:
        return normalize_text(f"{document}:p{page}")
    if item.get("text") is not None:
        return normalize_text(item["text"])
    return normalize_text(item)


def evidence_scores(predicted: Iterable[Any], gold: Iterable[Any]) -> dict[str, float | int]:
    predicted_keys = {_evidence_key(item) for item in predicted if _evidence_key(item)}
    gold_keys = {_evidence_key(item) for item in gold if _evidence_key(item)}
    true_positive = len(predicted_keys & gold_keys)
    if not predicted_keys and not gold_keys:
        precision = recall = f1 = 1.0
    else:
        precision = true_positive / len(predicted_keys) if predicted_keys else 0.0
        recall = true_positive / len(gold_keys) if gold_keys else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "true_positive": true_positive,
        "predicted_count": len(predicted_keys),
        "gold_count": len(gold_keys),
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def _program_key(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(normalize_text(token) for token in value)
    return normalize_text(value)


def evaluate_one(gold: dict[str, Any], prediction: dict[str, Any] | None) -> dict[str, Any]:
    if prediction is None:
        return {
            "sample_id": gold["sample_id"],
            "schema_valid": False,
            "schema_errors": ["prediction is missing"],
            "answered": False,
            "answer_correct": False,
            "program_correct": None,
            "unit_scale_error": False,
            "unsupported_claim": False,
            "evidence": evidence_scores([], gold.get("gold_evidence", [])),
        }
    schema_errors = validate_prediction(prediction)
    status = prediction.get("status")
    answered = status == "answered"
    answer_correct = answered and answers_match(prediction.get("answer"), gold.get("gold_answer"))
    predicted_program = prediction.get("program")
    gold_program = gold.get("gold_program")
    program_correct: bool | None = None
    execution_correct: bool | None = None
    execution_error: str | None = None
    if predicted_program is not None and gold_program is not None:
        program_correct = _program_key(predicted_program) == _program_key(gold_program)
        if isinstance(predicted_program, str) and gold.get("dataset") == "FinQA":
            try:
                documents = gold.get("documents") or []
                table = documents[0].get("table") if documents else None
                execution = execute_finqa_program(predicted_program, table)
                execution_correct = execution_values_match(execution.value, gold.get("gold_answer"))
            except ValueError as exc:
                execution_correct = False
                execution_error = str(exc)
    evidence = evidence_scores(prediction.get("evidence", []), gold.get("gold_evidence", []))
    return {
        "sample_id": gold["sample_id"],
        "schema_valid": not schema_errors,
        "schema_errors": schema_errors,
        "answered": answered,
        "answer_correct": answer_correct,
        "program_correct": program_correct,
        "execution_correct": execution_correct,
        "execution_error": execution_error,
        "unit_scale_error": unit_scale_error(
            prediction.get("answer"), gold.get("gold_answer"), prediction.get("unit")
        ),
        "unsupported_claim": answered and bool(gold.get("gold_evidence")) and not prediction.get("evidence"),
        "evidence": evidence,
    }


def aggregate_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    answered = sum(bool(item["answered"]) for item in results)
    correct = sum(bool(item["answer_correct"]) for item in results)
    schema_valid = sum(bool(item["schema_valid"]) for item in results)
    unit_errors = sum(bool(item["unit_scale_error"]) for item in results)
    unsupported = sum(bool(item["unsupported_claim"]) for item in results)
    program_results = [item["program_correct"] for item in results if item["program_correct"] is not None]
    execution_results = [
        item["execution_correct"] for item in results if item.get("execution_correct") is not None
    ]
    evidence_precision = sum(item["evidence"]["precision"] for item in results) / total if total else 0.0
    evidence_recall = sum(item["evidence"]["recall"] for item in results) / total if total else 0.0
    evidence_f1 = sum(item["evidence"]["f1"] for item in results) / total if total else 0.0
    return {
        "total": total,
        "coverage": answered / total if total else 0.0,
        "final_answer_accuracy": correct / total if total else 0.0,
        "selective_accuracy": correct / answered if answered else 0.0,
        "schema_valid_rate": schema_valid / total if total else 0.0,
        "program_accuracy": (
            sum(bool(value) for value in program_results) / len(program_results)
            if program_results
            else None
        ),
        "program_itt_accuracy": (
            sum(item.get("program_correct") is True for item in results) / total
            if total
            else 0.0
        ),
        "execution_accuracy": (
            sum(bool(value) for value in execution_results) / len(execution_results)
            if execution_results
            else None
        ),
        "execution_itt_accuracy": (
            sum(item.get("execution_correct") is True for item in results) / total
            if total
            else 0.0
        ),
        "execution_coverage": len(execution_results) / total if total else 0.0,
        "evidence_macro_precision": evidence_precision,
        "evidence_macro_recall": evidence_recall,
        "evidence_macro_f1": evidence_f1,
        "unit_scale_error_rate": unit_errors / total if total else 0.0,
        "unsupported_claim_rate": unsupported / total if total else 0.0,
    }


def evaluate_files(gold_path: Path, prediction_path: Path, report_path: Path) -> dict[str, Any]:
    gold_records = list(read_jsonl(gold_path))
    predictions: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for prediction in read_jsonl(prediction_path):
        sample_id = prediction.get("sample_id")
        if isinstance(sample_id, str):
            if sample_id in predictions:
                duplicates.append(sample_id)
            predictions[sample_id] = prediction
    results = [evaluate_one(gold, predictions.get(gold["sample_id"])) for gold in gold_records]
    report = {
        "schema_version": "1.0",
        "gold_file": str(gold_path),
        "prediction_file": str(prediction_path),
        "duplicates": sorted(set(duplicates)),
        "summary": aggregate_results(results),
        "results": results,
    }
    write_json(report_path, report)
    return report
