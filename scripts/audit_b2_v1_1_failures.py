#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.b2 import (  # noqa: E402
    B2_ROLE_OUTPUT_TOKEN_CAPS,
    _normalize_verdict,
    _validate_verdict,
)
from contractfin.utils import read_jsonl, write_json  # noqa: E402


def normalize_case(verdict: dict[str, Any]) -> dict[str, Any]:
    _validate_verdict(verdict)
    effective, diagnostic = _normalize_verdict(verdict)
    return {
        "raw": verdict,
        "effective": effective,
        "normalization": diagnostic,
    }


def main() -> int:
    parent_log = PROJECT_ROOT / "logs" / "b2_deepseek_full_preregistered30_v1.jsonl"
    records = list(read_jsonl(parent_log))
    failures = [record for record in records if record.get("error") is not None]
    failure_messages: dict[str, int] = {}
    for record in failures:
        message = record["error"]["message"]
        failure_messages[message] = failure_messages.get(message, 0) + 1

    cases = {
        "accept_with_false_check": normalize_case(
            {
                "decision": "accept",
                "checks": {
                    "contract_compliant": False,
                    "evidence_supported": True,
                    "program_executed": True,
                    "answer_consistent": True,
                },
                "reason_codes": [],
            }
        ),
        "accept_with_reason_code": normalize_case(
            {
                "decision": "accept",
                "checks": {
                    "contract_compliant": True,
                    "evidence_supported": True,
                    "program_executed": True,
                    "answer_consistent": True,
                },
                "reason_codes": ["model_reported_uncertainty"],
            }
        ),
        "valid_accept": normalize_case(
            {
                "decision": "accept",
                "checks": {
                    "contract_compliant": True,
                    "evidence_supported": True,
                    "program_executed": True,
                    "answer_consistent": True,
                },
                "reason_codes": [],
            }
        ),
        "human_review_without_reason": normalize_case(
            {
                "decision": "human_review",
                "checks": {
                    "contract_compliant": True,
                    "evidence_supported": True,
                    "program_executed": True,
                    "answer_consistent": True,
                },
                "reason_codes": [],
            }
        ),
    }

    cap_sequence = [
        *B2_ROLE_OUTPUT_TOKEN_CAPS["contract_agent"],
        *B2_ROLE_OUTPUT_TOKEN_CAPS["evidence_agent"],
        *B2_ROLE_OUTPUT_TOKEN_CAPS["solver_agent"],
        *B2_ROLE_OUTPUT_TOKEN_CAPS["verifier_agent"],
    ]
    output_failure = next(
        record
        for record in failures
        if (record.get("error") or {}).get("message", "").endswith(
            "status=incomplete, reason=max_output_tokens)"
        )
    )
    parent_output_usage = [
        {
            "role": call["role"],
            "role_call_index": call["role_call_index"],
            "output_tokens": call["token_usage"]["output"],
            "v1_1_cap": B2_ROLE_OUTPUT_TOKEN_CAPS[call["role"]][
                call["role_call_index"] - 1
            ],
        }
        for call in output_failure["agent_calls"]
    ]

    contradiction_cases_passed = all(
        cases[name]["effective"]["decision"] == "human_review"
        and cases[name]["normalization"] is not None
        for name in ("accept_with_false_check", "accept_with_reason_code")
    )
    valid_accept_unchanged = (
        cases["valid_accept"]["effective"]["decision"] == "accept"
        and cases["valid_accept"]["normalization"] is None
    )
    missing_review_reason_filled = (
        cases["human_review_without_reason"]["effective"]["decision"] == "human_review"
        and cases["human_review_without_reason"]["effective"]["reason_codes"]
        == ["verifier_unspecified_review_reason"]
    )
    parent_failure_classification_passed = (
        len(records) == 30
        and len(failures) == 3
        and failure_messages
        == {
            "an accepting verifier must have all checks true and no reason codes": 2,
            "model call did not complete (role=verifier_agent, status=incomplete, reason=max_output_tokens)": 1,
        }
    )
    fixed_budget_passed = sum(cap_sequence) == 32768 and cap_sequence[-1] == 11264
    passed = (
        parent_failure_classification_passed
        and contradiction_cases_passed
        and valid_accept_unchanged
        and missing_review_reason_filled
        and fixed_budget_passed
    )

    report = {
        "schema_version": "1.0",
        "mode": "b2_v1_1_failure_replay_no_api",
        "api_calls": 0,
        "parent_run_id": records[0]["run_id"],
        "parent_log": str(parent_log),
        "parent_sample_count": len(records),
        "parent_failures": [
            {
                "sample_id": record["sample_id"],
                "error": record["error"],
            }
            for record in failures
        ],
        "failure_message_counts": failure_messages,
        "semantic_verdict_replay": cases,
        "role_output_token_caps": {
            role: list(caps) for role, caps in B2_ROLE_OUTPUT_TOKEN_CAPS.items()
        },
        "full_pipeline_cap_sequence": cap_sequence,
        "full_pipeline_cap_sum": sum(cap_sequence),
        "verifier_reserved_tokens": cap_sequence[-1],
        "parent_output_ceiling_sample_usage": parent_output_usage,
        "acceptance": {
            "parent_failure_classification_passed": parent_failure_classification_passed,
            "contradictory_accepts_route_to_human_review": contradiction_cases_passed,
            "valid_accept_is_unchanged": valid_accept_unchanged,
            "missing_human_review_reason_is_filled": missing_review_reason_filled,
            "fixed_budget_allocation_passed": fixed_budget_passed,
            "passed": passed,
        },
        "residual_risk": (
            "The parent output-ceiling sample used more than the new per-turn caps in its "
            "contract and first solver calls. Local validation proves reservation and safe "
            "failure handling, not live model completion; the exact three parent failures "
            "must pass a separately authorized live interface gate before a registered30 rerun."
        ),
    }
    output_path = PROJECT_ROOT / "reports" / "b2_v1_1_failure_diagnostic.json"
    write_json(output_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
