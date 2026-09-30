from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from contractfin.b2 import B2_ROLE_OUTPUT_TOKEN_CAPS, B2RunPaths, build_b2_payload, run_b2
from contractfin.retrieval import search_sample


def sample() -> dict:
    return {
        "sample_id": "finqa:dev:b2-example",
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


def contract() -> dict:
    return {
        "task_id": "finqa:dev:b2-example",
        "dataset": "FinQA",
        "question": "What is revenue divided by transactions?",
        "target_entities": ["revenue", "transactions"],
        "reporting_period": [],
        "allowed_documents": ["report-1"],
        "answer_type": "number",
        "unit_scale": {"unit": None, "scale": None},
        "required_evidence": {"minimum_items": 2, "must_support_answer": True},
        "allowed_operations": ["divide"],
        "rounding_rule": {"decimal_places": None, "mode": "preserve"},
        "output_schema": {"name": "contractfin_prediction", "version": "1.0"},
        "validation_rules": ["use only selected evidence", "execute the program"],
        "abstention_conditions": ["required values are absent"],
        "max_retries": 0,
    }


def message_response(index: int, value: dict) -> dict:
    return {
        "id": f"resp_{index}",
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
            "input_tokens": 100,
            "output_tokens": 20,
            "output_tokens_details": {"reasoning_tokens": 5},
            "total_tokens": 120,
        },
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
            "output_tokens_details": {"reasoning_tokens": 5},
            "total_tokens": 120,
        },
    }


def response_sequence(*, verifier_accepts: bool = True) -> list[dict]:
    query = "revenue transactions"
    results = search_sample(sample(), query, top_k=12)
    by_label = {item["label"]: item["text"] for item in results}
    packet = {
        "sample_id": "finqa:dev:b2-example",
        "search_queries": [query],
        "evidence": [
            {"label": "table_1", "text": by_label["table_1"]},
            {"label": "table_2", "text": by_label["table_2"]},
        ],
        "extracted_values": [
            {"name": "revenue", "value": "10", "unit": None, "source_label": "table_1"},
            {
                "name": "transactions",
                "value": "2",
                "unit": None,
                "source_label": "table_2",
            },
        ],
        "sufficient": True,
    }
    candidate = {
        "sample_id": "finqa:dev:b2-example",
        "answer": "5",
        "evidence": ["table_1", "table_2"],
        "status": "answered",
        "program": "divide(10, 2)",
        "unit": None,
    }
    checks = {
        "contract_compliant": verifier_accepts,
        "evidence_supported": True,
        "program_executed": True,
        "answer_consistent": True,
    }
    verdict = {
        "decision": "accept" if verifier_accepts else "human_review",
        "checks": checks,
        "reason_codes": [] if verifier_accepts else ["contract_check_failed"],
    }
    return [
        message_response(1, contract()),
        tool_response(2, "call_search", "search_document", {"query": query, "top_k": 12}),
        message_response(3, packet),
        tool_response(
            4,
            "call_calculate",
            "calculate_finqa",
            {"steps": [{"operation": "divide", "arguments": ["10", "2"]}]},
        ),
        message_response(5, candidate),
        message_response(6, verdict),
    ]


class PayloadTests(unittest.TestCase):
    def test_no_tool_role_omits_tool_fields(self) -> None:
        payload = build_b2_payload(
            system_prompt="role",
            user_input={"question": "q"},
            conversation_tail=[],
            model="test-model",
            output_name="output",
            output_schema={"type": "object"},
            tools=[],
            allow_tools=False,
            max_output_tokens=100,
            strict_schema=False,
        )
        self.assertNotIn("tools", payload)
        self.assertNotIn("tool_choice", payload)
        self.assertFalse(payload["store"])


class RunTests(unittest.TestCase):
    def _run(self, responses: list[dict], *, variant: str = "full") -> tuple[dict, list[dict], dict]:
        payloads: list[dict] = []

        def caller(payload: dict) -> dict:
            payloads.append(payload)
            return responses[len(payloads) - 1]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = B2RunPaths(
                gold=root / "gold.jsonl",
                predictions=root / "predictions.jsonl",
                log=root / "run.jsonl",
                report=root / "report.json",
            )
            report = run_b2(
                [sample()],
                model="test-model",
                paths=paths,
                provider="deepseek",
                variant=variant,
                protocol_id="b2-test-v1",
                total_output_budget=32768,
                max_model_calls=6,
                max_tool_calls=2,
                request_timeout_seconds=300,
                strict_schema=False,
                api_caller=caller,
            )
            log = json.loads(paths.log.read_text(encoding="utf-8"))
            return report, payloads, log

    def test_full_pipeline_is_replayable_and_does_not_leak_gold(self) -> None:
        report, payloads, log = self._run(response_sequence())
        run = report["run"]
        self.assertEqual(run["successful_samples"], 1)
        self.assertEqual(run["model_calls"], 6)
        self.assertEqual(run["tool_calls"], 2)
        self.assertEqual(run["samples_with_contract"], 1)
        self.assertEqual(run["samples_with_verifier"], 1)
        self.assertEqual(run["verifier_accepts"], 1)
        self.assertEqual(log["output"]["answer"], "5")
        self.assertEqual(log["output"]["metadata"]["local_gate_passed"], True)
        self.assertNotIn("DO_NOT_LEAK", json.dumps(payloads))
        self.assertNotIn("DO_NOT_LEAK", json.dumps(log["coordination"]))

    def test_verifier_can_route_candidate_to_human_review(self) -> None:
        report, _, log = self._run(response_sequence(verifier_accepts=False))
        self.assertEqual(report["run"]["human_review_outputs"], 1)
        self.assertEqual(log["output"]["status"], "human_review")
        self.assertIsNone(log["output"]["answer"])
        self.assertEqual(
            log["coordination"]["verifier_verdict"]["reason_codes"],
            ["contract_check_failed"],
        )

    def test_inconsistent_accept_is_conservatively_normalized(self) -> None:
        responses = response_sequence()
        responses[-1] = message_response(
            6,
            {
                "decision": "accept",
                "checks": {
                    "contract_compliant": False,
                    "evidence_supported": True,
                    "program_executed": True,
                    "answer_consistent": True,
                },
                "reason_codes": ["contract_check_failed"],
            },
        )
        report, _, log = self._run(responses)
        self.assertEqual(report["run"]["successful_samples"], 1)
        self.assertEqual(report["run"]["failed_samples"], 0)
        self.assertEqual(report["run"]["verifier_accepts"], 0)
        self.assertEqual(report["run"]["verifier_normalizations"], 1)
        self.assertEqual(log["output"]["status"], "human_review")
        self.assertIsNone(log["output"]["answer"])
        self.assertEqual(log["coordination"]["verifier_raw_verdict"]["decision"], "accept")
        self.assertEqual(log["coordination"]["verifier_verdict"]["decision"], "human_review")
        self.assertEqual(
            log["coordination"]["verifier_normalization"]["rule"],
            "conservative_verifier_normalization_v1_1",
        )

    def test_each_role_turn_has_a_fixed_output_cap(self) -> None:
        _, payloads, log = self._run(response_sequence())
        expected = [
            *B2_ROLE_OUTPUT_TOKEN_CAPS["contract_agent"],
            *B2_ROLE_OUTPUT_TOKEN_CAPS["evidence_agent"],
            *B2_ROLE_OUTPUT_TOKEN_CAPS["solver_agent"],
            *B2_ROLE_OUTPUT_TOKEN_CAPS["verifier_agent"],
        ]
        self.assertEqual(sum(expected), 32768)
        self.assertEqual([payload["max_output_tokens"] for payload in payloads], expected)
        self.assertEqual(
            [call["requested_max_output_tokens"] for call in log["agent_calls"]],
            expected,
        )

    def test_total_budget_below_fixed_allocation_is_rejected(self) -> None:
        payloads: list[dict] = []

        def caller(payload: dict) -> dict:
            payloads.append(payload)
            return response_sequence()[len(payloads) - 1]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = B2RunPaths(
                gold=root / "gold.jsonl",
                predictions=root / "predictions.jsonl",
                log=root / "run.jsonl",
                report=root / "report.json",
            )
            report = run_b2(
                [sample()],
                model="test-model",
                paths=paths,
                provider="deepseek",
                variant="full",
                protocol_id="b2-test-v1.1-insufficient-budget",
                total_output_budget=32767,
                max_model_calls=6,
                max_tool_calls=2,
                request_timeout_seconds=300,
                strict_schema=False,
                api_caller=caller,
            )
        self.assertEqual(report["run"]["successful_samples"], 0)
        self.assertEqual(report["run"]["failed_samples"], 1)
        self.assertEqual(report["run"]["model_calls"], 0)
        self.assertEqual(payloads, [])

    def test_no_verifier_ablation_uses_local_gate(self) -> None:
        responses = response_sequence()[:-1]
        report, _, log = self._run(responses, variant="no_verifier")
        self.assertEqual(report["run"]["successful_samples"], 1)
        self.assertEqual(report["run"]["model_calls"], 5)
        self.assertEqual(report["run"]["samples_with_verifier"], 0)
        self.assertEqual(log["output"]["status"], "answered")

    def test_no_contract_ablation_skips_contract_role(self) -> None:
        responses = response_sequence()[1:]
        report, _, log = self._run(responses, variant="no_contract")
        self.assertEqual(report["run"]["successful_samples"], 1)
        self.assertEqual(report["run"]["model_calls"], 5)
        self.assertEqual(report["run"]["samples_with_contract"], 0)
        self.assertEqual(report["run"]["samples_with_verifier"], 1)
        self.assertIsNone(log["coordination"]["task_contract"])


if __name__ == "__main__":
    unittest.main()
