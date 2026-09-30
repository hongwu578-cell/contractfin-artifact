from __future__ import annotations

import unittest

from contractfin.run_logging import REQUIRED_LOG_FIELDS, log_completeness
from contractfin.schemas import validate_prediction, validate_task_contract


class PredictionSchemaTests(unittest.TestCase):
    def test_valid_prediction(self) -> None:
        self.assertEqual(
            validate_prediction(
                {"sample_id": "x", "answer": 1, "evidence": [], "status": "answered"}
            ),
            [],
        )

    def test_missing_and_extra_fields(self) -> None:
        errors = validate_prediction({"sample_id": "x", "extra": True})
        self.assertTrue(any("missing required" in error for error in errors))
        self.assertTrue(any("unexpected fields" in error for error in errors))


class TaskContractSchemaTests(unittest.TestCase):
    def test_valid_task_contract(self) -> None:
        contract = {
            "task_id": "finqa-test-1",
            "dataset": "FinQA",
            "question": "What is the change?",
            "target_entities": ["revenue"],
            "reporting_period": ["2023", "2024"],
            "allowed_documents": ["report-1"],
            "answer_type": "percent",
            "unit_scale": {"unit": "%"},
            "required_evidence": {"minimum": 1},
            "allowed_operations": ["subtract", "divide"],
            "rounding_rule": {"precision": 2},
            "output_schema": {"name": "prediction"},
            "validation_rules": ["period_match", "recompute"],
            "abstention_conditions": ["missing_evidence"],
            "max_retries": 2,
        }
        self.assertEqual(validate_task_contract(contract), [])

    def test_retry_limit_is_enforced(self) -> None:
        self.assertTrue(any("max_retries" in error for error in validate_task_contract({
            "task_id": "x",
            "dataset": "FinQA",
            "question": "q",
            "target_entities": ["x"],
            "reporting_period": [],
            "allowed_documents": ["d"],
            "answer_type": "number",
            "unit_scale": {},
            "required_evidence": {},
            "allowed_operations": [],
            "rounding_rule": {},
            "output_schema": {},
            "validation_rules": [],
            "abstention_conditions": [],
            "max_retries": 3,
        })))


class LoggingTests(unittest.TestCase):
    def test_log_completeness(self) -> None:
        complete = {field: None for field in REQUIRED_LOG_FIELDS}
        incomplete = dict(complete)
        incomplete.pop("model")
        self.assertEqual(log_completeness([complete, incomplete]), 0.5)


if __name__ == "__main__":
    unittest.main()

