from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from contractfin.evaluation import (
    answers_match,
    evidence_scores,
    evaluate_files,
    parse_single_numeric,
    unit_scale_error,
)
from contractfin.evidence_ids import (
    migrate_legacy_finqa_evidence_id,
    migrate_prediction_evidence_ids,
)
from contractfin.program import execute_finqa_program, execution_values_match
from contractfin.utils import write_jsonl


class NumericEvaluationTests(unittest.TestCase):
    def test_exact_text(self) -> None:
        self.assertTrue(answers_match("Net income", " net   income "))

    def test_currency_and_commas(self) -> None:
        self.assertTrue(answers_match("$1,250", "1250"))

    def test_percent_fraction_equivalence(self) -> None:
        self.assertTrue(answers_match("12%", "0.12"))

    def test_parentheses_negative(self) -> None:
        parsed = parse_single_numeric("($1,250 million)")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.value, -1_250_000_000.0)

    def test_multiple_numbers_are_not_guessed(self) -> None:
        self.assertFalse(answers_match("between 10 and 12", "11"))

    def test_numeric_mismatch(self) -> None:
        self.assertFalse(answers_match("11%", "12%"))

    def test_unit_error_is_separate_from_numeric_equivalence(self) -> None:
        self.assertTrue(answers_match("0.12", "12%"))
        self.assertTrue(unit_scale_error("0.12", "12%"))


class EvidenceEvaluationTests(unittest.TestCase):
    def test_evidence_identity_metrics(self) -> None:
        result = evidence_scores(
            [{"id": "doc:p1"}, {"id": "doc:p2"}],
            [{"id": "doc:p2"}, {"id": "doc:p3"}],
        )
        self.assertEqual(result["precision"], 0.5)
        self.assertEqual(result["recall"], 0.5)
        self.assertEqual(result["f1"], 0.5)

    def test_empty_evidence_is_perfect_only_when_both_empty(self) -> None:
        self.assertEqual(evidence_scores([], ["required"])["f1"], 0.0)
        self.assertEqual(evidence_scores([], [])["f1"], 1.0)

    def test_legacy_finqa_text_ids_map_to_official_merged_sequence(self) -> None:
        self.assertEqual(
            migrate_legacy_finqa_evidence_id(
                "pre_2", pre_text_count=3, post_text_count=4
            ),
            ("text_2", True),
        )
        self.assertEqual(
            migrate_legacy_finqa_evidence_id(
                "post_2", pre_text_count=3, post_text_count=4
            ),
            ("text_5", True),
        )
        self.assertEqual(
            migrate_legacy_finqa_evidence_id(
                "table_2", pre_text_count=3, post_text_count=4
            ),
            ("table_2", False),
        )

    def test_prediction_migration_does_not_mutate_source(self) -> None:
        prediction = {"evidence": ["pre_0", "post_1", "table_2"]}
        sample = {
            "documents": [{"pre_text": ["a"], "post_text": ["b", "c"]}]
        }
        migrated, changed = migrate_prediction_evidence_ids(prediction, sample)
        self.assertEqual(migrated["evidence"], ["text_0", "text_2", "table_2"])
        self.assertEqual(changed, 2)
        self.assertEqual(prediction["evidence"], ["pre_0", "post_1", "table_2"])


class ProgramExecutionTests(unittest.TestCase):
    def test_chained_arithmetic_and_reference(self) -> None:
        result = execute_finqa_program("subtract(153.7, 139.9), divide(#0, 139.9)")
        self.assertTrue(execution_values_match(result.value, 0.09864))

    def test_constants_and_comparison(self) -> None:
        self.assertEqual(execute_finqa_program("divide(455, const_7)").value, 65.0)
        self.assertEqual(execute_finqa_program("greater(10, 5)").value, "yes")

    def test_table_aggregate(self) -> None:
        table = [["year", "2021", "2022", "2023"], ["net change", "10", "20", "30"]]
        self.assertEqual(execute_finqa_program("table_average(net change, none)", table).value, 20.0)

    def test_invalid_reference_fails(self) -> None:
        with self.assertRaises(ValueError):
            execute_finqa_program("add(#2, 1)")


class FileEvaluationTests(unittest.TestCase):
    def test_end_to_end_file_scoring(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gold = root / "gold.jsonl"
            predictions = root / "predictions.jsonl"
            report = root / "report.json"
            write_jsonl(
                gold,
                [
                    {
                        "sample_id": "sample-1",
                        "gold_answer": "12%",
                        "gold_program": "divide(12,100)",
                        "gold_evidence": [{"id": "doc:p1"}],
                    }
                ],
            )
            write_jsonl(
                predictions,
                [
                    {
                        "sample_id": "sample-1",
                        "answer": "12%",
                        "evidence": [{"id": "doc:p1"}],
                        "status": "answered",
                        "program": "divide(12,100)",
                    }
                ],
            )
            result = evaluate_files(gold, predictions, report)
            self.assertEqual(result["summary"]["final_answer_accuracy"], 1.0)
            self.assertEqual(result["summary"]["schema_valid_rate"], 1.0)
            self.assertEqual(json.loads(report.read_text())["summary"]["program_accuracy"], 1.0)
            self.assertEqual(result["summary"]["program_itt_accuracy"], 1.0)
            self.assertEqual(result["summary"]["execution_itt_accuracy"], 0.0)


if __name__ == "__main__":
    unittest.main()
