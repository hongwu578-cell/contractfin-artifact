from __future__ import annotations

import json
import unittest

from contractfin.b1_tools import B1_TOOL_DEFINITIONS, execute_b1_tool
from contractfin.retrieval import search_sample


def sample() -> dict:
    return {
        "sample_id": "finqa:dev:tool-example",
        "dataset": "FinQA",
        "split": "dev",
        "question": "What is revenue divided by transactions?",
        "documents": [
            {
                "document_id": "report-1",
                "pre_text": ["The company reports operating statistics."],
                "table": [
                    ["metric", "value"],
                    ["revenue", "10"],
                    ["transactions", "2"],
                ],
                "post_text": ["Other information is omitted."],
            }
        ],
        "gold_answer": "DO_NOT_LEAK_ANSWER",
        "gold_program": "DO_NOT_LEAK_PROGRAM",
        "gold_evidence": [{"id": "DO_NOT_LEAK_EVIDENCE"}],
    }


class RetrievalTests(unittest.TestCase):
    def test_search_is_deterministic_and_uses_exact_source_labels(self) -> None:
        first = search_sample(sample(), "revenue transactions", top_k=2)
        second = search_sample(sample(), "revenue transactions", top_k=2)
        self.assertEqual(first, second)
        self.assertEqual({item["label"] for item in first}, {"table_1", "table_2"})
        self.assertNotIn("DO_NOT_LEAK", json.dumps(first))

    def test_text_labels_follow_official_merged_text_index(self) -> None:
        results = search_sample(sample(), "other information omitted", top_k=1)
        self.assertEqual(results[0]["label"], "text_1")


class ToolTests(unittest.TestCase):
    def test_search_tool_returns_evidence(self) -> None:
        output, trace = execute_b1_tool(
            "search_document",
            json.dumps({"query": "revenue", "top_k": 2}),
            sample(),
        )
        value = json.loads(output)
        self.assertTrue(value["ok"])
        self.assertEqual(value["top_k"], 2)
        self.assertEqual(value["results"][0]["label"], "table_1")
        self.assertIsNone(trace["error"])

    def test_calculator_executes_without_gold_access(self) -> None:
        output, trace = execute_b1_tool(
            "calculate_finqa",
            json.dumps(
                {
                    "steps": [
                        {"operation": "subtract", "arguments": ["12", "2"]},
                        {"operation": "divide", "arguments": ["#0", "2"]},
                    ]
                }
            ),
            sample(),
        )
        value = json.loads(output)
        self.assertEqual(value["value"], 5.0)
        self.assertEqual(value["program"], "subtract(12, 2), divide(#0, 2)")
        self.assertIsNone(trace["error"])
        self.assertNotIn("DO_NOT_LEAK", output)

    def test_exposed_calculator_schema_requires_structured_steps(self) -> None:
        calculator = next(item for item in B1_TOOL_DEFINITIONS if item["name"] == "calculate_finqa")
        parameters = calculator["parameters"]
        self.assertEqual(parameters["required"], ["steps"])
        self.assertNotIn("program", parameters["properties"])

    def test_structured_steps_reject_nested_syntax(self) -> None:
        output, trace = execute_b1_tool(
            "calculate_finqa",
            json.dumps(
                {
                    "steps": [
                        {
                            "operation": "divide",
                            "arguments": ["add(10, 2)", "2"],
                        }
                    ]
                }
            ),
            sample(),
        )
        self.assertFalse(json.loads(output)["ok"])
        self.assertIn("reserved punctuation", trace["error"])

    def test_table_row_label_allows_balanced_parentheses(self) -> None:
        table_sample = sample()
        table_sample["documents"][0]["table"] = [
            ["metric", "2018", "2019", "2020"],
            [
                "available-for-sale ( afs ) investment securities ( average )",
                "3",
                "6",
                "9",
            ],
        ]
        output, trace = execute_b1_tool(
            "calculate_finqa",
            json.dumps(
                {
                    "steps": [
                        {
                            "operation": "table_average",
                            "arguments": [
                                "available-for-sale ( afs ) investment securities ( average )",
                                "none",
                            ],
                        }
                    ]
                }
            ),
            table_sample,
        )
        value = json.loads(output)
        self.assertTrue(value["ok"])
        self.assertEqual(value["value"], 6.0)
        self.assertIsNone(trace["error"])

    def test_table_row_label_rejects_unbalanced_parentheses(self) -> None:
        output, trace = execute_b1_tool(
            "calculate_finqa",
            json.dumps(
                {
                    "steps": [
                        {
                            "operation": "table_average",
                            "arguments": ["revenue ( average", "none"],
                        }
                    ]
                }
            ),
            sample(),
        )
        self.assertFalse(json.loads(output)["ok"])
        self.assertIn("unbalanced parentheses", trace["error"])

    def test_invalid_tool_arguments_return_a_replayable_error(self) -> None:
        output, trace = execute_b1_tool("calculate_finqa", "not-json", sample())
        value = json.loads(output)
        self.assertFalse(value["ok"])
        self.assertEqual(value["error_type"], "JSONDecodeError")
        self.assertIsNotNone(trace["error"])


if __name__ == "__main__":
    unittest.main()
