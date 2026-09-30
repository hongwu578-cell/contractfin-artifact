#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.b2 import (  # noqa: E402
    B2_ROLE_OUTPUT_TOKEN_CAPS,
    B2RunPaths,
    CONTRACT_SYSTEM_PROMPT,
    EVIDENCE_SYSTEM_PROMPT,
    SOLVER_SYSTEM_PROMPT,
    VERIFIER_SYSTEM_PROMPT,
    run_b2,
)
from contractfin.preregistration import load_preregistered_samples  # noqa: E402
from contractfin.program import _split_top_level  # noqa: E402
from contractfin.utils import write_json  # noqa: E402


def structured_steps(program: str) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for expression in _split_top_level(program):
        match = re.fullmatch(r"([A-Za-z_]+)\((.*)\)", expression.strip())
        if match is None:
            raise ValueError(f"invalid oracle expression: {expression}")
        arguments = _split_top_level(match.group(2))
        if len(arguments) != 2:
            raise ValueError(f"oracle expression does not have two arguments: {expression}")
        steps.append(
            {
                "operation": match.group(1).casefold(),
                "arguments": [str(argument).strip() for argument in arguments],
            }
        )
    return steps


def _message_response(index: int, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": f"mock_b2_{index}",
        "status": "completed",
        "model": "local-oracle-no-api",
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps(value, ensure_ascii=False, separators=(",", ":")),
                    }
                ],
            }
        ],
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 0,
        },
    }


def _tool_response(
    index: int, call_id: str, name: str, arguments: dict[str, Any]
) -> dict[str, Any]:
    return {
        "id": f"mock_b2_{index}",
        "status": "completed",
        "model": "local-oracle-no-api",
        "output": [
            {
                "type": "function_call",
                "call_id": call_id,
                "name": name,
                "arguments": json.dumps(arguments, ensure_ascii=False, separators=(",", ":")),
            }
        ],
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 0,
        },
    }


class LocalOracleCaller:
    def __init__(self, samples: list[dict[str, Any]]):
        self.by_id = {item["sample_id"]: item for item in samples}
        self.calls = 0
        self.payloads: list[dict[str, Any]] = []

    def __call__(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls += 1
        self.payloads.append(payload)
        system_prompt = payload["input"][0]["content"]
        task_input = json.loads(payload["input"][1]["content"])
        sample = self.by_id[task_input["sample_id"]]

        if system_prompt == CONTRACT_SYSTEM_PROMPT:
            operations = list(dict.fromkeys(step["operation"] for step in structured_steps(sample["gold_program"])))
            answer_text = str(sample["gold_answer"]).casefold()
            answer_type = "boolean" if answer_text in {"yes", "no"} else "number"
            contract = {
                "task_id": sample["sample_id"],
                "dataset": sample["dataset"],
                "question": sample["question"],
                "target_entities": ["financial_metric"],
                "reporting_period": [],
                "allowed_documents": [item["document_id"] for item in sample["documents"]],
                "answer_type": answer_type,
                "unit_scale": {"unit": None, "scale": None},
                "required_evidence": {
                    "minimum_items": max(1, min(12, len(sample.get("gold_evidence", [])))),
                    "must_support_answer": True,
                },
                "allowed_operations": operations,
                "rounding_rule": {"decimal_places": None, "mode": "preserve"},
                "output_schema": {"name": "contractfin_prediction", "version": "1.0"},
                "validation_rules": ["use selected evidence", "execute the canonical program"],
                "abstention_conditions": ["required values are absent"],
                "max_retries": 0,
            }
            return _message_response(self.calls, contract)

        outputs = [item for item in payload["input"] if item.get("type") == "function_call_output"]
        if system_prompt == EVIDENCE_SYSTEM_PROMPT:
            if not outputs:
                return _tool_response(
                    self.calls,
                    f"search_{self.calls}",
                    "search_document",
                    {"query": sample["question"], "top_k": 12},
                )
            search_output = json.loads(outputs[-1]["output"])
            selected = search_output["results"][:2]
            packet = {
                "sample_id": sample["sample_id"],
                "search_queries": [search_output["query"]],
                "evidence": [
                    {"label": item["label"], "text": item["text"]} for item in selected
                ],
                "extracted_values": [],
                "sufficient": True,
            }
            return _message_response(self.calls, packet)

        if system_prompt == SOLVER_SYSTEM_PROMPT:
            if not outputs:
                return _tool_response(
                    self.calls,
                    f"calculate_{self.calls}",
                    "calculate_finqa",
                    {"steps": structured_steps(sample["gold_program"])},
                )
            calculation = json.loads(outputs[-1]["output"])
            packet = task_input["evidence_packet"]
            candidate = {
                "sample_id": sample["sample_id"],
                "answer": str(sample["gold_answer"]),
                "evidence": [item["label"] for item in packet["evidence"]],
                "status": "answered",
                "program": calculation["program"],
                "unit": None,
            }
            return _message_response(self.calls, candidate)

        if system_prompt == VERIFIER_SYSTEM_PROMPT:
            verdict = {
                "decision": "accept",
                "checks": {
                    "contract_compliant": True,
                    "evidence_supported": True,
                    "program_executed": True,
                    "answer_consistent": True,
                },
                "reason_codes": [],
            }
            return _message_response(self.calls, verdict)
        raise AssertionError("unexpected B2 system prompt")


def main() -> int:
    dataset_path = PROJECT_ROOT / "data" / "normalized" / "finqa_dev.jsonl"
    manifest_path = PROJECT_ROOT / "config" / "b0_finqa_dev_30_manifest.json"
    samples = load_preregistered_samples(dataset_path, manifest_path)
    caller = LocalOracleCaller(samples)
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        paths = B2RunPaths(
            gold=root / "gold.jsonl",
            predictions=root / "predictions.jsonl",
            log=root / "run.jsonl",
            report=root / "report.json",
        )
        run_report = run_b2(
            samples,
            model="local-oracle-no-api",
            paths=paths,
            provider="deepseek",
            variant="full",
            protocol_id="contractfin-b2-local-orchestration-audit-v1.1",
            total_output_budget=32768,
            max_model_calls=6,
            max_tool_calls=2,
            request_timeout_seconds=300,
            strict_schema=False,
            api_caller=caller,
        )

    run = run_report["run"]
    payload_text = json.dumps(caller.payloads, ensure_ascii=False)
    forbidden_keys = ["gold_answer", "gold_program", "gold_evidence"]
    leaked_keys = [key for key in forbidden_keys if f'"{key}"' in payload_text]
    expected_caps = [
        *B2_ROLE_OUTPUT_TOKEN_CAPS["contract_agent"],
        *B2_ROLE_OUTPUT_TOKEN_CAPS["evidence_agent"],
        *B2_ROLE_OUTPUT_TOKEN_CAPS["solver_agent"],
        *B2_ROLE_OUTPUT_TOKEN_CAPS["verifier_agent"],
    ]
    cap_sequences = [
        [payload["max_output_tokens"] for payload in caller.payloads[index : index + 6]]
        for index in range(0, len(caller.payloads), 6)
    ]
    fixed_role_caps_passed = (
        sum(expected_caps) == 32768
        and len(cap_sequences) == 30
        and all(sequence == expected_caps for sequence in cap_sequences)
    )
    passed = (
        run["sample_count"] == 30
        and run["successful_samples"] == 30
        and run["failed_samples"] == 0
        and run["model_calls"] == 180
        and run["role_model_call_counts"]
        == {
            "contract_agent": 30,
            "evidence_agent": 60,
            "solver_agent": 60,
            "verifier_agent": 30,
        }
        and run["tool_calls"] == 60
        and run["failed_tool_calls"] == 0
        and run["samples_with_contract"] == 30
        and run["samples_with_verifier"] == 30
        and run["verifier_accepts"] == 30
        and run["human_review_outputs"] == 0
        and run["verifier_normalizations"] == 0
        and run["log_completeness"] == 1.0
        and not leaked_keys
        and fixed_role_caps_passed
    )
    report = {
        "schema_version": "1.0",
        "mode": "local_oracle_orchestration_audit_no_api",
        "warning": (
            "Gold programs and answers generate mocked agent responses only to validate local "
            "routing. They are never exposed to model request payloads and these scores are not "
            "research performance."
        ),
        "dataset": str(dataset_path),
        "sample_manifest": str(manifest_path),
        "sample_count": len(samples),
        "api_calls": 0,
        "mocked_model_calls": run["model_calls"],
        "mocked_tool_calls": run["tool_calls"],
        "role_model_call_counts": run["role_model_call_counts"],
        "successful_samples": run["successful_samples"],
        "failed_samples": run["failed_samples"],
        "failed_tool_calls": run["failed_tool_calls"],
        "samples_with_contract": run["samples_with_contract"],
        "samples_with_verifier": run["samples_with_verifier"],
        "verifier_accepts": run["verifier_accepts"],
        "human_review_outputs": run["human_review_outputs"],
        "verifier_normalizations": run["verifier_normalizations"],
        "role_output_token_caps": {
            role: list(caps) for role, caps in B2_ROLE_OUTPUT_TOKEN_CAPS.items()
        },
        "fixed_role_caps_sum": sum(expected_caps),
        "fixed_role_caps_passed": fixed_role_caps_passed,
        "log_completeness": run["log_completeness"],
        "runtime_gold_field_keys_exposed": leaked_keys,
        "acceptance": {
            "required_successful_samples": 30,
            "required_failed_tool_calls": 0,
            "required_log_completeness": 1.0,
            "required_runtime_gold_field_keys_exposed": 0,
            "passed": passed,
        },
    }
    output_path = PROJECT_ROOT / "reports" / "b2_v1_1_local_orchestration_audit.json"
    write_json(output_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
