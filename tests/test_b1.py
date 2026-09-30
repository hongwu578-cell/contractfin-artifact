from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from contractfin.b1 import B1RunPaths, build_b1_payload, build_initial_conversation, run_b1


def sample() -> dict:
    return {
        "sample_id": "finqa:dev:b1-example",
        "dataset": "FinQA",
        "split": "dev",
        "question": "What is revenue divided by transactions?",
        "documents": [
            {
                "document_id": "report-1",
                "pre_text": ["intro"],
                "table": [["metric", "value"], ["revenue", "10"], ["transactions", "2"]],
                "post_text": ["footer"],
            }
        ],
        "gold_answer": "5",
        "gold_program": "divide(10, 2)",
        "gold_evidence": [{"id": "table_1"}, {"id": "table_2"}],
    }


def tool_response(index: int, call_id: str, name: str, arguments: dict) -> dict:
    return {
        "id": f"resp_{index}",
        "status": "completed",
        "model": "test-model-snapshot",
        "output": [
            {
                "type": "function_call",
                "call_id": call_id,
                "name": name,
                "arguments": json.dumps(arguments),
            }
        ],
        "usage": {
            "input_tokens": 100,
            "output_tokens": 20,
            "output_tokens_details": {"reasoning_tokens": 10},
            "total_tokens": 120,
        },
    }


def final_response() -> dict:
    value = {
        "sample_id": "finqa:dev:b1-example",
        "answer": "5",
        "evidence": ["table_1", "table_2"],
        "status": "answered",
        "program": "divide(10, 2)",
        "unit": None,
    }
    return {
        "id": "resp_3",
        "status": "completed",
        "model": "test-model-snapshot",
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": json.dumps(value)}],
            }
        ],
        "usage": {
            "input_tokens": 120,
            "output_tokens": 20,
            "output_tokens_details": {"reasoning_tokens": 5},
            "total_tokens": 140,
        },
    }


class PayloadTests(unittest.TestCase):
    def test_initial_prompt_does_not_include_gold(self) -> None:
        conversation = build_initial_conversation(sample())
        text = json.dumps(conversation)
        self.assertNotIn("gold_answer", text)
        self.assertNotIn("divide(10, 2)", text)

    def test_final_turn_disables_tools_but_keeps_the_schema(self) -> None:
        payload = build_b1_payload(
            build_initial_conversation(sample()),
            "test-model",
            max_output_tokens=100,
            allow_tools=False,
            strict_schema=False,
        )
        self.assertEqual(payload["tool_choice"], "none")
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")
        self.assertNotIn("strict", payload["text"]["format"])


class RunTests(unittest.TestCase):
    def test_single_agent_runs_tool_loop_with_a_cumulative_budget(self) -> None:
        responses = [
            tool_response(1, "call_search", "search_document", {"query": "revenue transactions"}),
            tool_response(2, "call_calc", "calculate_finqa", {"program": "divide(10, 2)"}),
            final_response(),
        ]
        payloads: list[dict] = []

        def caller(payload: dict) -> dict:
            payloads.append(payload)
            return responses[len(payloads) - 1]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = B1RunPaths(
                gold=root / "gold.jsonl",
                predictions=root / "predictions.jsonl",
                log=root / "run.jsonl",
                report=root / "report.json",
            )
            report = run_b1(
                [sample()],
                model="test-model",
                paths=paths,
                provider="deepseek",
                protocol_id="b1-test-v1",
                total_output_budget=100,
                max_model_calls=4,
                max_tool_calls=4,
                request_timeout_seconds=300,
                strict_schema=False,
                api_caller=caller,
            )
            self.assertEqual([item["max_output_tokens"] for item in payloads], [100, 80, 60])
            self.assertEqual(report["run"]["successful_samples"], 1)
            self.assertEqual(report["run"]["model_calls"], 3)
            self.assertEqual(report["run"]["tool_calls"], 2)
            self.assertEqual(report["run"]["tool_call_counts"]["search_document"], 1)
            self.assertEqual(report["run"]["tool_call_counts"]["calculate_finqa"], 1)
            self.assertEqual(report["run"]["samples_with_search_top_k_12"], 1)
            self.assertEqual(report["run"]["failed_tool_calls"], 0)
            self.assertEqual(report["run"]["token_usage"]["total"], 380)
            log = json.loads(paths.log.read_text(encoding="utf-8"))
            self.assertEqual(log["model"], "test-model-snapshot")
            self.assertEqual(len(log["tool_calls"]), 2)
            self.assertEqual(log["output"]["answer"], "5")

    def test_incomplete_call_preserves_partial_usage(self) -> None:
        incomplete = {
            "id": "resp_incomplete",
            "status": "incomplete",
            "model": "test-model-snapshot",
            "incomplete_details": {"reason": "max_output_tokens"},
            "output": [],
            "usage": {
                "input_tokens": 100,
                "output_tokens": 50,
                "output_tokens_details": {"reasoning_tokens": 50},
                "total_tokens": 150,
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = B1RunPaths(
                gold=root / "gold.jsonl",
                predictions=root / "predictions.jsonl",
                log=root / "run.jsonl",
                report=root / "report.json",
            )
            report = run_b1(
                [sample()],
                model="test-model",
                paths=paths,
                total_output_budget=100,
                api_caller=lambda payload: incomplete,
            )
            self.assertEqual(report["run"]["failed_samples"], 1)
            self.assertEqual(report["run"]["token_usage"]["total"], 150)
            log = json.loads(paths.log.read_text(encoding="utf-8"))
            self.assertEqual(log["model_calls"][0]["incomplete_reason"], "max_output_tokens")

    def test_invalid_final_json_records_visible_output_not_reasoning(self) -> None:
        malformed = {
            "id": "resp_malformed",
            "status": "completed",
            "model": "test-model-snapshot",
            "output": [
                {"type": "reasoning", "summary": [{"text": "DO_NOT_RETAIN"}]},
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "```json\n{bad}\n```"}],
                },
            ],
            "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = B1RunPaths(
                gold=root / "gold.jsonl",
                predictions=root / "predictions.jsonl",
                log=root / "run.jsonl",
                report=root / "report.json",
            )
            report = run_b1(
                [sample()],
                model="test-model",
                paths=paths,
                total_output_budget=100,
                api_caller=lambda payload: malformed,
            )
            self.assertEqual(report["run"]["failed_samples"], 1)
            log = json.loads(paths.log.read_text(encoding="utf-8"))
            diagnostic = log["final_output_diagnostic"]
            self.assertEqual(diagnostic["visible_text"], "```json\n{bad}\n```")
            self.assertFalse(diagnostic["reasoning_text_retained"])
            self.assertNotIn("DO_NOT_RETAIN", json.dumps(log))


if __name__ == "__main__":
    unittest.main()
