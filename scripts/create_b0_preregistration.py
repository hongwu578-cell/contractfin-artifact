#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.preregistration import (  # noqa: E402
    build_preregistration_manifest,
    load_preregistered_samples,
    render_manifest_markdown,
)
from contractfin.utils import atomic_write_text, read_jsonl, sha256_file, write_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create and verify the frozen 30-item FinQA B0 development manifest"
    )
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    dataset_path = root / "data" / "normalized" / "finqa_dev.jsonl"
    manifest_path = root / "config" / "b0_finqa_dev_30_manifest.json"
    review_path = root / "reports" / "b0_finqa_dev_30_preregistration.md"
    if not dataset_path.exists():
        raise SystemExit("normalized FinQA development data is missing; run normalize first")

    samples = list(read_jsonl(dataset_path))
    manifest = build_preregistration_manifest(
        samples,
        dataset_sha256=sha256_file(dataset_path),
    )
    write_json(manifest_path, manifest)
    atomic_write_text(review_path, render_manifest_markdown(manifest))
    loaded = load_preregistered_samples(dataset_path, manifest_path)
    summary = {
        "protocol_id": manifest["protocol_id"],
        "selected_count": len(loaded),
        "dataset_sha256": manifest["source"]["normalized_file_sha256"],
        "manifest": str(manifest_path),
        "review": str(review_path),
        "verified": True,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
