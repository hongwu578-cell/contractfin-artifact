from __future__ import annotations

import unittest

from contractfin.data import normalize_financebench_record, normalize_finqa_record


class FinQANormalizationTests(unittest.TestCase):
    def test_normalizes_official_shape(self) -> None:
        sample = normalize_finqa_record(
            {
                "id": "report-1",
                "filename": "report.pdf",
                "pre_text": ["before"],
                "table": [["Year", "2024"], ["Revenue", "10"]],
                "post_text": ["after"],
                "qa": {
                    "question": "What was revenue?",
                    "answer": "10",
                    "exe_ans": 10,
                    "program": "table_1",
                    "gold_inds": {"table_1": "Revenue | 10"},
                },
            },
            "test",
        )
        self.assertEqual(sample.sample_id, "finqa:test:report-1")
        self.assertEqual(sample.gold_answer, 10)
        self.assertEqual(sample.gold_evidence[0]["id"], "table_1")
        self.assertEqual(sample.documents[0]["table"][1][1], "10")

    def test_missing_question_fails(self) -> None:
        with self.assertRaises(ValueError):
            normalize_finqa_record({"id": "x", "qa": {}}, "test")


class FinanceBenchNormalizationTests(unittest.TestCase):
    def test_normalizes_evidence_and_document_metadata(self) -> None:
        sample = normalize_financebench_record(
            {
                "financebench_id": 5,
                "question": "What was revenue?",
                "answer": "$10 million",
                "doc_name": "ACME_2024_10K",
                "evidence": [{"evidence_text": "Revenue was $10 million.", "evidence_page_num": 7}],
                "question_type": "domain-relevant",
            },
            {"ACME_2024_10K": {"doc_type": "10K", "company": "ACME"}},
        )
        self.assertEqual(sample.sample_id, "financebench:open:5")
        self.assertEqual(sample.documents[0]["company"], "ACME")
        self.assertEqual(sample.gold_evidence[0]["id"], "ACME_2024_10K:p7")


if __name__ == "__main__":
    unittest.main()
