from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

from .evaluation import evaluate_files
from .run_logging import append_log, log_completeness, utc_now
from .schemas import validate_prediction
from .utils import atomic_write_text, write_json, write_jsonl


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEEPSEEK_RESPONSES_URL = "https://api.deepseek.com/responses"
PROMPT_VERSION = "b0-direct-v2-text-evidence-id-fix"

_DEEPSEEK_DSML_SUFFIX = re.compile(
    r"(?:\s*</｜｜DSML｜｜\s+(?:parameter|invoke|calls)>\s*)+\Z"
)

SYSTEM_PROMPT = """You are the Direct LLM baseline for a financial question-answering study.
Use only the supplied document context. Do not use outside knowledge.

Return one object that follows the supplied JSON schema. The answer must be a
scalar string or null. Evidence must contain only exact source labels shown in
square brackets in the context, for example table_3 or text_7. Do not invent
labels. If the question requires calculation, return a FinQA-style program
using only add, subtract, multiply, divide, exp, greater, table_average,
table_sum, table_max, and table_min. Refer to earlier operation results with
#0, #1, and so on. Use program=null when no program is needed.

If the documents do not support an answer, set status=abstain, answer=null,
program=null, and explain nothing outside the structured response."""


PREDICTION_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "sample_id": {"type": "string"},
        "answer": {"type": ["string", "null"]},
        "evidence": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 12,
        },
        "status": {"type": "string", "enum": ["answered", "abstain", "human_review"]},
        "program": {"type": ["string", "null"]},
        "unit": {"type": ["string", "null"]},
    },
    "required": ["sample_id", "answer", "evidence", "status", "program", "unit"],
    "additionalProperties": False,
}


class B0Error(RuntimeError):
    """Base class for safe, reportable B0 failures."""


class APIRequestError(B0Error):
    def __init__(self, status: int | None, error_type: str | None, error_code: str | None):
        self.status = status
        self.error_type = error_type
        self.error_code = error_code
        super().__init__(
            f"Responses API request failed (status={status}, type={error_type}, code={error_code})"
        )


@dataclass(frozen=True, slots=True)
class B0RunPaths:
    gold: Path
    predictions: Path
    log: Path
    report: Path


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    api_key_env: str
    responses_url: str
    strict_schema: bool


PROVIDERS = {
    "openai": ProviderConfig("OPENAI_API_KEY", OPENAI_RESPONSES_URL, True),
    "deepseek": ProviderConfig("DEEPSEEK_API_KEY", DEEPSEEK_RESPONSES_URL, False),
}


def _document_context(document: dict[str, Any]) -> str:
    lines = [f"DOCUMENT {document.get('document_id', document.get('filename', 'unknown'))}"]
    for index, text in enumerate(document.get("pre_text", [])):
        lines.append(f"[text_{index}] {text}")
    for index, row in enumerate(document.get("table", [])):
        cells = " | ".join(str(cell) for cell in row)
        lines.append(f"[table_{index}] {cells}")
    for index, text in enumerate(document.get("post_text", [])):
        text_index = len(document.get("pre_text", [])) + index
        lines.append(f"[text_{text_index}] {text}")
    if document.get("text"):
        lines.append(f"[document_text] {document['text']}")
    return "\n".join(lines)


def build_user_prompt(sample: dict[str, Any]) -> str:
    documents = "\n\n".join(_document_context(item) for item in sample["documents"])
    return (
        f"SAMPLE_ID: {sample['sample_id']}\n"
        f"DATASET: {sample['dataset']}\n"
        f"QUESTION: {sample['question']}\n\n"
        f"DOCUMENT CONTEXT\n{documents}"
    )


def build_request_payload(
    sample: dict[str, Any],
    model: str,
    *,
    max_output_tokens: int = 1024,
    strict_schema: bool = True,
) -> dict[str, Any]:
    output_format = {
        "type": "json_schema",
        "name": "contractfin_prediction",
        "schema": PREDICTION_OUTPUT_SCHEMA,
    }
    if strict_schema:
        output_format["strict"] = True
    return {
        "model": model,
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(sample)},
        ],
        "text": {
            "format": output_format
        },
        "max_output_tokens": max_output_tokens,
        "store": False,
    }


def _safe_api_error(error: urllib.error.HTTPError) -> APIRequestError:
    error_type: str | None = None
    error_code: str | None = None
    try:
        body = json.loads(error.read().decode("utf-8", "replace"))
        details = body.get("error", {}) if isinstance(body, dict) else {}
        error_type = details.get("type")
        error_code = details.get("code")
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass
    return APIRequestError(error.code, error_type, error_code)


def call_responses_api(
    payload: dict[str, Any],
    *,
    api_key: str | None = None,
    api_key_env: str = "OPENAI_API_KEY",
    url: str = OPENAI_RESPONSES_URL,
    timeout: int = 120,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any]:
    key = api_key or os.environ.get(api_key_env)
    if not key:
        raise B0Error(f"{api_key_env} is not configured")
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with opener(request, timeout=timeout) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        raise _safe_api_error(exc) from exc
    except urllib.error.URLError as exc:
        raise APIRequestError(None, "network_error", type(exc.reason).__name__) from exc
    if not isinstance(result, dict):
        raise B0Error("Responses API returned a non-object payload")
    return result


def extract_prediction(
    response: dict[str, Any],
    expected_sample_id: str,
    *,
    provider: str = "openai",
    baseline: str = "B0_direct_llm",
) -> dict[str, Any]:
    if response.get("error"):
        details = response["error"]
        raise B0Error(f"Responses API returned an error object: {details.get('code', 'unknown')}")
    texts: list[str] = []
    for item in response.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            if content.get("type") == "refusal":
                raise B0Error("model refused the sample")
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                texts.append(content["text"])
    if not texts:
        raise B0Error(f"Responses API produced no output_text (status={response.get('status')})")
    raw_text = "".join(texts)
    normalization: str | None = None
    try:
        prediction = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        if provider != "deepseek":
            raise B0Error("structured output was not valid JSON") from exc
        stripped = raw_text.lstrip()
        try:
            prediction, end = json.JSONDecoder().raw_decode(stripped)
        except json.JSONDecodeError as raw_exc:
            raise B0Error("structured output was not valid JSON") from raw_exc
        remainder = stripped[end:]
        if not remainder or _DEEPSEEK_DSML_SUFFIX.fullmatch(remainder) is None:
            raise B0Error("structured output was not valid JSON") from exc
        normalization = "removed_deepseek_dsml_closing_suffix_v1"
    if not isinstance(prediction, dict):
        raise B0Error("structured output was not an object")
    if prediction.get("sample_id") != expected_sample_id:
        raise B0Error("structured output sample_id did not match the input sample")
    errors = validate_prediction(prediction)
    if errors:
        raise B0Error("prediction schema validation failed: " + "; ".join(errors))
    prediction["metadata"] = {
        "baseline": baseline,
        "provider": provider,
        "prompt_version": PROMPT_VERSION,
        "response_id": response.get("id"),
        "response_status": response.get("status"),
    }
    if normalization is not None:
        prediction["metadata"]["transport_normalization"] = normalization
    return prediction


def _token_usage(response: dict[str, Any]) -> dict[str, int]:
    usage = response.get("usage") or {}
    output_details = usage.get("output_tokens_details") or {}
    return {
        "input": int(usage.get("input_tokens") or 0),
        "output": int(usage.get("output_tokens") or 0),
        "reasoning": int(output_details.get("reasoning_tokens") or 0),
        "total": int(usage.get("total_tokens") or 0),
    }


def _response_diagnostics(response: dict[str, Any]) -> dict[str, Any]:
    incomplete = response.get("incomplete_details") or {}
    error = response.get("error") or {}
    return {
        "response_id": response.get("id"),
        "status": response.get("status"),
        "incomplete_reason": incomplete.get("reason"),
        "provider_error_code": error.get("code"),
    }


def _error_prediction(sample_id: str, error: Exception, *, provider: str) -> dict[str, Any]:
    return {
        "sample_id": sample_id,
        "answer": None,
        "evidence": [],
        "status": "error",
        "program": None,
        "unit": None,
        "metadata": {
            "baseline": "B0_direct_llm",
            "provider": provider,
            "prompt_version": PROMPT_VERSION,
            "error_type": type(error).__name__,
            "error": str(error),
        },
    }


def run_b0(
    samples: Iterable[dict[str, Any]],
    *,
    model: str,
    paths: B0RunPaths,
    provider: str = "openai",
    protocol_id: str | None = None,
    max_output_tokens: int = 1024,
    request_timeout_seconds: int | None = None,
    strict_schema: bool = True,
    api_caller: Callable[[dict[str, Any]], dict[str, Any]] = call_responses_api,
) -> dict[str, Any]:
    selected = list(samples)
    if not selected:
        raise ValueError("at least one sample is required")
    existing_paths = [
        path
        for path in (paths.gold, paths.predictions, paths.log, paths.report)
        if path.exists()
    ]
    if existing_paths:
        names = ", ".join(str(path) for path in existing_paths)
        raise FileExistsError(f"refusing to overwrite existing B0 artifacts: {names}")
    run_id = f"b0-{uuid.uuid4()}"
    atomic_write_text(paths.log, "")
    write_jsonl(paths.gold, selected)
    predictions: list[dict[str, Any]] = []
    log_records: list[dict[str, Any]] = []

    for sample in selected:
        payload = build_request_payload(
            sample,
            model,
            max_output_tokens=max_output_tokens,
            strict_schema=strict_schema,
        )
        prompt = payload["input"][1]["content"]
        started_at = utc_now()
        started_clock = time.monotonic()
        response: dict[str, Any] = {}
        error: Exception | None = None
        try:
            response = api_caller(payload)
            prediction = extract_prediction(response, sample["sample_id"], provider=provider)
        except Exception as exc:  # Log every attempted sample before surfacing the failure.
            error = exc
            prediction = _error_prediction(sample["sample_id"], exc, provider=provider)
        finished_at = utc_now()
        latency_ms = round((time.monotonic() - started_clock) * 1000)
        actual_model = response.get("model") or model
        log_record = {
            "run_id": run_id,
            "protocol_id": protocol_id,
            "sample_id": sample["sample_id"],
            "system": "B0_direct_llm",
            "model": actual_model,
            "started_at": started_at,
            "finished_at": finished_at,
            "input": {
                "dataset": sample["dataset"],
                "split": sample["split"],
                "question": sample["question"],
                "prompt_version": PROMPT_VERSION,
                "provider": provider,
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "context_characters": len(prompt),
                "max_output_tokens": max_output_tokens,
                "request_timeout_seconds": request_timeout_seconds,
                "store": False,
            },
            "output": prediction,
            "tool_calls": [],
            "token_usage": _token_usage(response),
            "response_diagnostics": _response_diagnostics(response),
            "latency_ms": latency_ms,
            "error": None if error is None else {"type": type(error).__name__, "message": str(error)},
        }
        predictions.append(prediction)
        log_records.append(log_record)
        append_log(paths.log, log_record)

    write_jsonl(paths.predictions, predictions)
    evaluation = evaluate_files(paths.gold, paths.predictions, paths.report)
    evaluation["run"] = {
        "run_id": run_id,
        "system": "B0_direct_llm",
        "provider": provider,
        "requested_model": model,
        "prompt_version": PROMPT_VERSION,
        "protocol_id": protocol_id,
        "max_output_tokens": max_output_tokens,
        "request_timeout_seconds": request_timeout_seconds,
        "sample_count": len(selected),
        "successful_calls": sum(item["error"] is None for item in log_records),
        "failed_calls": sum(item["error"] is not None for item in log_records),
        "log_completeness": log_completeness(log_records),
        "token_usage": {
            key: sum(item["token_usage"][key] for item in log_records)
            for key in ("input", "output", "total")
        },
        "latency_ms": sum(item["latency_ms"] for item in log_records),
    }
    write_json(paths.report, evaluation)
    return evaluation
