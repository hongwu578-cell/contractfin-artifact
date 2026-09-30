#!/usr/bin/env python3
from __future__ import annotations

import argparse
import functools
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.b0 import PROVIDERS, call_responses_api  # noqa: E402
from contractfin.b1 import B1RunPaths, run_b1  # noqa: E402
from contractfin.preregistration import load_preregistered_samples  # noqa: E402
from contractfin.utils import read_jsonl  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the ContractFin B1 single-agent baseline")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default="deepseek")
    parser.add_argument("--model", required=True)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--sample-manifest",
        type=Path,
    )
    selection.add_argument("--limit", type=int)
    parser.add_argument("--protocol-id", required=True)
    parser.add_argument("--total-output-budget", type=int, default=32768)
    parser.add_argument("--max-model-calls", type=int, default=6)
    parser.add_argument("--max-tool-calls", type=int, default=8)
    parser.add_argument("--request-timeout-seconds", type=int, default=300)
    parser.add_argument("--artifact-stem")
    args = parser.parse_args()
    for name in (
        "total_output_budget",
        "max_model_calls",
        "max_tool_calls",
        "request_timeout_seconds",
    ):
        if getattr(args, name) < 1:
            raise SystemExit(f"--{name.replace('_', '-')} must be at least 1")

    root = args.root.resolve()
    dataset_path = root / "data" / "normalized" / "finqa_dev.jsonl"
    if args.sample_manifest:
        manifest_path = args.sample_manifest
        if not manifest_path.is_absolute():
            manifest_path = root / manifest_path
        samples = load_preregistered_samples(dataset_path, manifest_path)
    else:
        limit = 1 if args.limit is None else args.limit
        if limit < 1:
            raise SystemExit("--limit must be at least 1")
        samples = list(read_jsonl(dataset_path))[:limit]
        if len(samples) < limit:
            raise SystemExit(f"requested {limit} samples, found {len(samples)}")
    stem = args.artifact_stem or (
        "b1_deepseek_preregistered30_v1"
        if args.sample_manifest
        else "b1_deepseek_interface1_v1"
    )
    paths = B1RunPaths(
        gold=root / "reports" / f"{stem}_gold.jsonl",
        predictions=root / "reports" / f"{stem}_predictions.jsonl",
        log=root / "logs" / f"{stem}.jsonl",
        report=root / "reports" / f"{stem}_report.json",
    )
    provider = PROVIDERS[args.provider]
    api_caller = functools.partial(
        call_responses_api,
        api_key_env=provider.api_key_env,
        url=provider.responses_url,
        timeout=args.request_timeout_seconds,
    )
    report = run_b1(
        samples,
        model=args.model,
        paths=paths,
        provider=args.provider,
        protocol_id=args.protocol_id,
        total_output_budget=args.total_output_budget,
        max_model_calls=args.max_model_calls,
        max_tool_calls=args.max_tool_calls,
        request_timeout_seconds=args.request_timeout_seconds,
        strict_schema=provider.strict_schema,
        api_caller=api_caller,
    )
    print(json.dumps(report["run"], ensure_ascii=False, indent=2))
    return 0 if report["run"]["failed_samples"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
