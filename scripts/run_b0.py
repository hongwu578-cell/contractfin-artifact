#!/usr/bin/env python3
from __future__ import annotations

import argparse
import functools
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.b0 import B0RunPaths, PROVIDERS, call_responses_api, run_b0  # noqa: E402
from contractfin.preregistration import load_preregistered_samples  # noqa: E402
from contractfin.utils import read_jsonl  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the ContractFin B0 Direct LLM baseline")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default="openai")
    parser.add_argument("--model", required=True, help="exact model ID frozen for this run")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--limit", type=int, default=None)
    selection.add_argument(
        "--sample-manifest",
        type=Path,
        help="frozen preregistration manifest; selects its exact IDs and execution order",
    )
    parser.add_argument(
        "--artifact-stem",
        help="output filename stem; defaults to provider smoke or preregistered30",
    )
    parser.add_argument("--protocol-id", help="frozen protocol identifier recorded in logs")
    parser.add_argument("--max-output-tokens", type=int, default=1024)
    parser.add_argument("--request-timeout-seconds", type=int, default=120)
    args = parser.parse_args()
    limit = 1 if args.limit is None else args.limit
    if limit < 1:
        raise SystemExit("--limit must be at least 1")
    if args.request_timeout_seconds < 1:
        raise SystemExit("--request-timeout-seconds must be at least 1")

    root = args.root.resolve()
    input_path = root / "data" / "normalized" / "finqa_dev.jsonl"
    if not input_path.exists():
        raise SystemExit("normalized FinQA development data is missing; run normalize first")
    if args.sample_manifest:
        manifest_path = args.sample_manifest
        if not manifest_path.is_absolute():
            manifest_path = root / manifest_path
        samples = load_preregistered_samples(input_path, manifest_path)
    else:
        samples = list(read_jsonl(input_path))[:limit]
        if len(samples) < limit:
            raise SystemExit(f"requested {limit} samples, found {len(samples)}")

    artifact_stem = args.artifact_stem or (
        f"b0_{args.provider}_preregistered30"
        if args.sample_manifest
        else f"b0_{args.provider}_smoke"
    )
    paths = B0RunPaths(
        gold=root / "reports" / f"{artifact_stem}_gold.jsonl",
        predictions=root / "reports" / f"{artifact_stem}_predictions.jsonl",
        log=root / "logs" / f"{artifact_stem}.jsonl",
        report=root / "reports" / f"{artifact_stem}_report.json",
    )
    provider = PROVIDERS[args.provider]
    api_caller = functools.partial(
        call_responses_api,
        api_key_env=provider.api_key_env,
        url=provider.responses_url,
        timeout=args.request_timeout_seconds,
    )
    report = run_b0(
        samples,
        model=args.model,
        paths=paths,
        provider=args.provider,
        protocol_id=args.protocol_id,
        max_output_tokens=args.max_output_tokens,
        request_timeout_seconds=args.request_timeout_seconds,
        strict_schema=provider.strict_schema,
        api_caller=api_caller,
    )
    print(json.dumps(report["run"], ensure_ascii=False, indent=2))
    return 0 if report["run"]["failed_calls"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
