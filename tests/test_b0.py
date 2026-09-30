from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from contractfin.b0 import (
    B0Error,
    B0RunPaths,
    PREDICTION_OUTPUT_SCHEMA,
    build_request_payload,
    build_user_prompt,
    extract_prediction,
    run_b0,
)


def sample() -> dict:
    return {
        "sample_id": "finqa:dev:example",
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
        "gold_answer": "DO_NOT_LEAK_GOLD_ANSWER",
        "gold_program": "DO_NOT_LEAK_GOLD_PROGRAM",
        "gold_evidence": [{"id": "DO_NOT_LEAK_GOLD_EVIDENCE"}],
    }


def response_for(value: dict) -> dict:
    return {
        "id": "resp_test",
        "status": "completed",
        "model": "test-model-snapshot",
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": json.dumps(value)}],
            }
        ],
        "usage": {
            "input_tokens": 100,
            "output_tokens": 20,
            "output_tokens_details": {"reasoning_tokens": 12},
            "total_tokens": 120,
        },
    }


class PromptTests(unittest.TestCase):
    def test_prompt_assigns_evidence_labels_without_gold_leakage(self) -> None:
        prompt = build_user_prompt(sample())
        self.assertIn("[table_1] revenue | 10", prompt)
        self.assertIn("[text_1] footer", prompt)
        self.assertIn("[text_0] intro", prompt)
        self.assertNotIn("DO_NOT_LEAK_GOLD", prompt)

    def test_request_freezes_strict_structured_output(self) -> None:
        payload = build_request_payload(sample(), "test-model")
        output_format = payload["text"]["format"]
        self.assertTrue(output_format["strict"])
        self.assertEqual(output_format["schema"], PREDICTION_OUTPUT_SCHEMA)
        self.assertFalse(payload["store"])

    def test_deepseek_request_omits_undocumented_strict_flag(self) -> None:
        payload = build_request_payload(sample(), "deepseek-flash", strict_schema=False)
        self.assertNotIn("strict", payload["text"]["format"])


class ResponseTests(unittest.TestCase):
    def test_extracts_valid_prediction(self) -> None:
        value = {
            "sample_id": "finqa:dev:example",
            "answer": "5",
            "evidence": ["table_1", "table_2"],
            "status": "answered",
            "program": "divide(10, 2)",
            "unit": None,
        }
        prediction = extract_prediction(response_for(value), value["sample_id"])
        self.assertEqual(prediction["answer"], "5")
        self.assertEqual(prediction["metadata"]["response_id"], "resp_test")

    def test_rejects_mismatched_sample_id(self) -> None:
        value = {
            "sample_id": "wrong",
            "answer": "5",
            "evidence": [],
            "status": "answered",
            "program": None,
            "unit": None,
        }
        with self.assertRaisesRegex(RuntimeError, "sample_id"):
            extract_prediction(response_for(value), "finqa:dev:example")

    def test_deepseek_exact_dsml_closing_suffix_is_normalized(self) -> None:
        value = {
            "sample_id": "finqa:dev:example",
            "answer": "5",
            "evidence": ["table_1", "table_2"],
            "status": "answered",
            "program": "divide(10, 2)",
            "unit": None,
        }
        response = response_for(value)
        response["output"][0]["content"][0]["text"] += (
            "</｜｜DSML｜｜ parameter>\n"
            "</｜｜DSML｜｜ invoke>\n"
            "</｜｜DSML｜｜ calls>"
        )
        prediction = extract_prediction(
            response, value["sample_id"], provider="deepseek"
        )
        self.assertEqual(prediction["answer"], "5")
        self.assertEqual(
            prediction["metadata"]["transport_normalization"],
            "removed_deepseek_dsml_closing_suffix_v1",
        )

    def test_deepseek_arbitrary_trailing_text_is_rejected(self) -> None:
        value = {
            "sample_id": "finqa:dev:example",
            "answer": "5",
            "evidence": [],
            "status": "answered",
            "program": None,
            "unit": None,
        }
        response = response_for(value)
        response["output"][0]["content"][0]["text"] += " explanatory prose"
        with self.assertRaisesRegex(B0Error, "not valid JSON"):
            extract_prediction(response, value["sample_id"], provider="deepseek")


class RunTests(unittest.TestCase):
    def test_run_writes_replayable_artifacts(self) -> None:
        value = {
            "sample_id": "finqa:dev:example",
            "answer": "5",
            "evidence": ["table_1", "table_2"],
            "status": "answered",
            "program": "divide(10, 2)",
            "unit": None,
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = B0RunPaths(
                gold=root / "gold.jsonl",
                predictions=root / "predictions.jsonl",
                log=root / "run.jsonl",
                report=root / "report.json",
            )
            report = run_b0(
                [sample()],
                model="test-model",
                paths=paths,
                provider="deepseek",
                protocol_id="test-v1",
                request_timeout_seconds=300,
                strict_schema=False,
                api_caller=lambda payload: response_for(value),
            )
            self.assertEqual(report["run"]["successful_calls"], 1)
            self.assertEqual(report["run"]["provider"], "deepseek")
            self.assertEqual(report["run"]["protocol_id"], "test-v1")
            self.assertEqual(report["run"]["max_output_tokens"], 1024)
            self.assertEqual(report["run"]["request_timeout_seconds"], 300)
            self.assertEqual(report["run"]["token_usage"]["total"], 120)
            log_record = json.loads(paths.log.read_text(encoding="utf-8"))
            self.assertEqual(log_record["token_usage"]["reasoning"], 12)
            self.assertEqual(log_record["response_diagnostics"]["status"], "completed")
            self.assertEqual(log_record["input"]["request_timeout_seconds"], 300)
            self.assertTrue(paths.gold.exists())
            self.assertTrue(paths.predictions.exists())
            self.assertTrue(paths.log.exists())
            self.assertTrue(paths.report.exists())

    def test_incomplete_response_keeps_non_sensitive_diagnostics(self) -> None:
        incomplete = {
            "id": "resp_incomplete",
            "status": "incomplete",
            "model": "test-model-snapshot",
            "incomplete_details": {"reason": "max_output_tokens"},
            "output": [],
            "usage": {
                "input_tokens": 100,
                "output_tokens": 1024,
                "output_tokens_details": {"reasoning_tokens": 1024},
                "total_tokens": 1124,
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = B0RunPaths(
                gold=root / "gold.jsonl",
                predictions=root / "predictions.jsonl",
                log=root / "run.jsonl",
                report=root / "report.json",
            )
            report = run_b0(
                [sample()],
                model="test-model",
                paths=paths,
                api_caller=lambda payload: incomplete,
            )
            self.assertEqual(report["run"]["failed_calls"], 1)
            log_record = json.loads(paths.log.read_text(encoding="utf-8"))
            diagnostics = log_record["response_diagnostics"]
            self.assertEqual(diagnostics["response_id"], "resp_incomplete")
            self.assertEqual(diagnostics["incomplete_reason"], "max_output_tokens")
            self.assertEqual(log_record["token_usage"]["reasoning"], 1024)

    def test_existing_artifact_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = B0RunPaths(
                gold=root / "gold.jsonl",
                predictions=root / "predictions.jsonl",
                log=root / "run.jsonl",
                report=root / "report.json",
            )
            paths.predictions.write_text("preserve me", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                run_b0(
                    [sample()],
                    model="test-model",
                    paths=paths,
                    api_caller=lambda payload: response_for({}),
                )
            self.assertEqual(paths.predictions.read_text(encoding="utf-8"), "preserve me")


if __name__ == "__main__":
    unittest.main()
