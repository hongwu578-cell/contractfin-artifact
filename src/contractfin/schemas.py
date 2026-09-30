from __future__ import annotations

from typing import Any


PREDICTION_REQUIRED = {"sample_id", "answer", "evidence", "status"}
PREDICTION_ALLOWED = PREDICTION_REQUIRED | {"program", "unit", "metadata"}
PREDICTION_STATUSES = {"answered", "abstain", "error", "human_review"}

TASK_CONTRACT_REQUIRED = {
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
}


def validate_prediction(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["prediction must be an object"]
    errors: list[str] = []
    missing = sorted(PREDICTION_REQUIRED - value.keys())
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")
    extra = sorted(value.keys() - PREDICTION_ALLOWED)
    if extra:
        errors.append(f"unexpected fields: {', '.join(extra)}")
    if "sample_id" in value and (not isinstance(value["sample_id"], str) or not value["sample_id"].strip()):
        errors.append("sample_id must be a non-empty string")
    if "answer" in value and not (
        value["answer"] is None or isinstance(value["answer"], (str, int, float, bool))
    ):
        errors.append("answer must be a scalar or null")
    if "evidence" in value:
        evidence = value["evidence"]
        if not isinstance(evidence, list):
            errors.append("evidence must be an array")
        else:
            for index, item in enumerate(evidence):
                if not isinstance(item, (str, dict)):
                    errors.append(f"evidence[{index}] must be a string or object")
    if "status" in value and value["status"] not in PREDICTION_STATUSES:
        errors.append("status is invalid")
    if "program" in value and not (
        value["program"] is None or isinstance(value["program"], (str, list))
    ):
        errors.append("program must be a string, array, or null")
    if "unit" in value and not (value["unit"] is None or isinstance(value["unit"], str)):
        errors.append("unit must be a string or null")
    if "metadata" in value and not isinstance(value["metadata"], dict):
        errors.append("metadata must be an object")
    return errors


def validate_task_contract(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["task contract must be an object"]
    errors: list[str] = []
    missing = sorted(TASK_CONTRACT_REQUIRED - value.keys())
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")
        return errors
    if value["dataset"] not in {"FinQA", "FinanceBench", "TAT-QA"}:
        errors.append("dataset is invalid")
    if value["answer_type"] not in {"number", "percent", "boolean", "text", "abstain"}:
        errors.append("answer_type is invalid")
    for field in (
        "target_entities",
        "reporting_period",
        "allowed_documents",
        "allowed_operations",
        "validation_rules",
        "abstention_conditions",
    ):
        if not isinstance(value[field], list):
            errors.append(f"{field} must be an array")
    if isinstance(value["target_entities"], list) and not value["target_entities"]:
        errors.append("target_entities must not be empty")
    if isinstance(value["allowed_documents"], list) and not value["allowed_documents"]:
        errors.append("allowed_documents must not be empty")
    for field in ("unit_scale", "required_evidence", "rounding_rule", "output_schema"):
        if not isinstance(value[field], dict):
            errors.append(f"{field} must be an object")
    retries = value["max_retries"]
    if isinstance(retries, bool) or not isinstance(retries, int) or not 0 <= retries <= 2:
        errors.append("max_retries must be an integer from 0 to 2")
    return errors

