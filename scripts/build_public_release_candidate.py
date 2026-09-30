#!/usr/bin/env python3
"""Build a security-scanned ContractFin release candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "releases" / "contractfin_artifact_v1_0_rc6"
REPOSITORY_URL = "https://github.com/hongwu578-cell/contractfin-artifact"

EXCLUDED_REPORT_PREFIXES = (
    "sci_applied_",
    "sci_manuscript_",
    "sci_methods_",
    "sci_public_release_candidate_",
    "sci_target_",
    "sci_verified_",
)

TEXT_SUFFIXES = {
    ".cfg",
    ".cff",
    ".csv",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

SECRET_PATTERNS = {
    "openai_or_deepseek_style_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9._~-]{20,}", re.IGNORECASE),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "quoted_secret_assignment": re.compile(
        r"(?:api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*[\"'][^\"']{12,}[\"']",
        re.IGNORECASE,
    ),
    "local_home_path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_file(relative: str, output: Path) -> None:
    source = ROOT / relative
    target = output / relative
    if not source.is_file():
        raise FileNotFoundError(relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_tree(relative: str, output: Path, *, include=None) -> None:
    source_root = ROOT / relative
    for source in sorted(source_root.rglob("*")):
        if not source.is_file() or "__pycache__" in source.parts or source.suffix == ".pyc":
            continue
        rel = source.relative_to(ROOT)
        if include is not None and not include(rel):
            continue
        copy_file(rel.as_posix(), output)


def write_text(output: Path, relative: str, content: str) -> None:
    target = output / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def build_authorization_manifest(output: Path) -> None:
    records = []
    for source in sorted((ROOT / "config" / "authorizations").glob("*.json")):
        if source.name.endswith(".template.json"):
            continue
        data = json.loads(source.read_text(encoding="utf-8"))
        record = {
            "source_file": source.relative_to(ROOT).as_posix(),
            "source_sha256": sha256(source),
            "schema_version": data.get("schema_version"),
            "protocol_id": data.get("protocol_id"),
            "scope": data.get("scope"),
            "authorized": data.get("authorized"),
            "date": data.get("authorization_date") or data.get("amendment_date"),
            "authorization_id": data.get("authorization_id") or data.get("amendment_id"),
            "call_budget": data.get("call_budget"),
            "execution": data.get("execution"),
            "external_data_transfer_authorized": bool(data.get("external_data_transfer_authorization")),
            "privacy_note": "Exact user-authored authorization text is intentionally omitted from the public artifact.",
        }
        records.append({key: value for key, value in record.items() if value is not None})
    write_text(
        output,
        "reproducibility/authorization_manifest.json",
        json.dumps({"schema_version": "1.0", "records": records}, indent=2, ensure_ascii=False),
    )


def write_release_documents(output: Path) -> None:
    readme = """
# ContractFin reproducibility artifact (v1.0-rc6)

This reproducibility artifact accompanies the study **“Tool Use Before Teamwork? A Preregistered, Cost-Aware Evaluation of LLM Architectures for Financial Numerical Reasoning.”** The public repository is https://github.com/hongwu578-cell/contractfin-artifact. No DOI has been assigned.

## Contents

- `src/`, `scripts/`, `tests/`, and `schemas/`: evaluation and experiment code.
- `config/`: preregistration, runtime, schedules, manifests, amendments, and freeze lock. Exact user-authored authorization text is replaced by a privacy-preserving manifest.
- `data/normalized/finqa_dev.jsonl`, `data/normalized/finqa_test.jsonl`, and `data/heldout/`: FinQA-derived inputs needed for development and held-out reproduction.
- `logs/` and `reports/`: development, confirmatory, stability, and mechanism artifacts.
- `paper/`: frozen V4 manuscript source, verified references, and deterministic figures.
- `reproducibility/`: release inventory, authorization summary, audit report, and SHA-256 manifest.

## Deliberate exclusions

- API keys, `.env` files, private keys, and local absolute paths.
- Exact user-authored API/data-transfer authorization text.
- FinanceBench raw or normalized data because the upstream repository does not provide an explicit root license file.
- Full upstream FinQA raw files; only the normalized development/test data and registered held-out subset needed for reproduction are included.
- Journal submission forms, cover letters, postal address, and journal-production files.

## Quick validation

Python 3.10 or newer is required. The core package uses only the Python standard library.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q
python3 scripts/freeze_sci_heldout.py --verify
python3 scripts/audit_sci_primary_structure.py \
  --artifact-stem sci_finqa_test500_primary_v1_rerun1 \
  --output-json /tmp/contractfin_primary_gate.json \
  --output-md /tmp/contractfin_primary_gate.md
python3 scripts/audit_sci_stability_structure.py \
  --artifact-stem sci_finqa_stability100_v1 \
  --output-json /tmp/contractfin_stability_gate.json \
  --output-md /tmp/contractfin_stability_gate.md
```

Live model commands require an explicitly configured provider key and may incur charges. They are not part of local validation and must not be run merely to inspect this artifact.

## Integrity

`reproducibility/MANIFEST.sha256` covers every packaged file except the manifest itself. `reproducibility/public_release_audit.json` records the local release checks.

## Release status

Original ContractFin code and documentation are released under the MIT License. The canonical repository is https://github.com/hongwu578-cell/contractfin-artifact; a DOI has not yet been assigned. Third-party terms and exclusions are documented in `THIRD_PARTY_NOTICES.md` and `LICENSE_SCOPE.md`.
"""
    reproducibility = """
# Reproducibility guide

## 1. Verify the frozen protocol

```bash
python3 scripts/freeze_sci_heldout.py --verify
```

The expected result is 34 locked files, no hash mismatches, and no failed review checks.

## 2. Run unit tests

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -q
```

The expected result is 62 passing tests.

## 3. Recompute confirmatory analyses without API calls

```bash
PYTHONPATH=src python3 scripts/analyze_sci_primary_results.py
PYTHONPATH=src python3 scripts/analyze_sci_primary_mechanisms.py
PYTHONPATH=src python3 scripts/analyze_sci_stability_results.py
```

These scripts operate on frozen local predictions, logs, and gold records. Back up the release directory or work in a copy if you want to preserve byte-for-byte hashes after regenerating reports.

## 4. Interpret the architecture boundary

B0 and B1 are the preregistered held-out systems. B2 is development-only and did not pass the structural acceptance gate. B2 artifacts must not be interpreted as a confirmatory held-out comparison.

## 5. Dataset reconstruction

`data/dataset_manifest.json` records pinned upstream commits and SHA-256 hashes. `scripts/fetch_data.py` can reconstruct the upstream working data, subject to current network availability and upstream terms. FinanceBench content is deliberately absent from this release candidate.
"""
    third_party = """
# Third-party data and software notices

## FinQA

The included FinQA-derived records originate from the `czyssrs/FinQA` repository at commit `0f16e2867befa6840783e58be38c9efb9229d742`.

- Upstream repository: https://github.com/czyssrs/FinQA
- License page: https://github.com/czyssrs/FinQA/blob/main/LICENSE
- License: MIT, copyright (c) 2021 Zhiyu Chen
- Local license copy: `third_party/FinQA_LICENSE.txt`

The ContractFin release keeps the upstream dataset identity and citation in its manifest and manuscript materials.

## FinanceBench

The source workspace used the public sample from `patronus-ai/financebench` at commit `cc39aeb4afdf33909ee1412188bf89035950c2eb` during infrastructure development. The upstream README describes the sample as open source, but the repository root did not expose an explicit `LICENSE` file when this release candidate was prepared on 2026-09-30. Therefore, this package redistributes **no FinanceBench questions, answers, evidence, metadata, PDFs, raw files, or normalized records**.

- Upstream repository: https://github.com/patronus-ai/financebench
- Reconstruction metadata only: `data/dataset_manifest.json`

This is a conservative release-engineering decision rather than a legal conclusion.
"""
    license_scope = """
# License scope

Original ContractFin code and documentation are released under the MIT License, copyright (c) 2026 Wang Hongwu and Xu Hui. See `LICENSE`.

The separate upstream MIT license in `third_party/FinQA_LICENSE.txt` applies to FinQA-originated material. It does not replace the ContractFin license or change the attribution requirements for the FinQA dataset.

FinanceBench content is not redistributed. Other third-party names, citations, and links are provided for scholarly attribution and remain subject to their respective terms.
"""
    citation = """
cff-version: 1.2.0
message: "If you use this artifact, please cite the associated manuscript."
title: "ContractFin reproducibility artifact: Tool Use Before Teamwork?"
type: software
version: "1.0.0-rc6"
license: MIT
date-released: 2026-09-30
authors:
  - family-names: Wang
    given-names: Hongwu
    affiliation: Beijing University of Financial Technology
  - family-names: Xu
    given-names: Hui
    affiliation: Beijing University of Financial Technology
repository-code: "https://github.com/hongwu578-cell/contractfin-artifact"
abstract: >-
  Code, frozen configurations, registered FinQA inputs, predictions, logs,
  and analyses for a preregistered cost-aware comparison of direct generation,
  deterministic tool augmentation, and development-stage multi-agent designs.
"""
    finqa_license = """
MIT License

Copyright (c) 2021 Zhiyu Chen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    gitignore = """
.DS_Store
.env
.env.*
*.key
*.pem
*.p12
*.pfx
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
venv/
dist/
build/
"""

    write_text(output, "README.md", readme)
    write_text(output, "REPRODUCIBILITY.md", reproducibility)
    write_text(output, "THIRD_PARTY_NOTICES.md", third_party)
    write_text(output, "LICENSE_SCOPE.md", license_scope)
    write_text(output, "CITATION.cff", citation)
    write_text(output, "third_party/FinQA_LICENSE.txt", finqa_license)
    write_text(output, ".gitignore", gitignore)


def copy_release_files(output: Path) -> None:
    copy_file("pyproject.toml", output)
    copy_file("LICENSE", output)
    copy_tree("src", output)
    copy_tree("schemas", output)
    copy_tree("tests", output)

    copy_tree(
        "scripts",
        output,
        include=lambda rel: not rel.name.startswith("build_applied_intelligence_"),
    )

    copy_tree("config", output, include=lambda rel: "authorizations" not in rel.parts)

    for relative in (
        "data/dataset_manifest.json",
        "data/normalized/finqa_dev.jsonl",
        "data/normalized/finqa_test.jsonl",
        "data/heldout/finqa_test500_inference_v1.jsonl",
        "data/heldout/finqa_test500_gold_v1.jsonl",
    ):
        copy_file(relative, output)

    copy_tree("logs", output, include=lambda rel: rel.suffix == ".jsonl")
    copy_tree(
        "reports",
        output,
        include=lambda rel: rel.name != ".gitkeep"
        and not rel.name.startswith(EXCLUDED_REPORT_PREFIXES),
    )

    for relative in (
        "manuscript/contractfin_sci_full_v4.md",
        "manuscript/references_verified_v1.bib",
    ):
        source = ROOT / relative
        destination = "paper/" + source.name
        target = output / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for source in sorted((ROOT / "manuscript" / "figures").iterdir()):
        if source.is_file():
            target = output / "paper" / "figures" / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def normalize_local_paths(output: Path) -> None:
    """Replace source-workspace absolute paths with release-relative paths."""
    prefix = ROOT.as_posix() + "/"
    redactions = []
    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        count = content.count(prefix)
        if count:
            path.write_text(content.replace(prefix, ""), encoding="utf-8")
            redactions.append(
                {
                    "path": path.relative_to(output).as_posix(),
                    "replacement_count": count,
                    "replacement": "project-relative path",
                }
            )
    write_text(
        output,
        "reproducibility/path_normalization.json",
        json.dumps(
            {
                "schema_version": "1.0",
                "reason": "Remove local usernames and absolute workspace paths from public artifacts.",
                "files": redactions,
                "total_replacements": sum(item["replacement_count"] for item in redactions),
            },
            indent=2,
        ),
    )


def scan_release(output: Path) -> dict:
    findings = []
    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append({"type": name, "path": path.relative_to(output).as_posix()})
    forbidden_paths = [
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
        and (
            path.name.startswith(".env")
            or path.suffix.lower() in {".key", ".pem", ".p12", ".pfx"}
            or "__pycache__" in path.parts
            or path.suffix.lower() == ".pyc"
            or path.name.startswith("sci_public_release_candidate_")
            or "financebench" in path.as_posix().lower()
            and path.as_posix() != "data/dataset_manifest.json"
        )
    ]
    return {
        "passed": not findings and not forbidden_paths,
        "secret_or_local_path_findings": findings,
        "forbidden_paths": sorted(forbidden_paths),
    }


def write_inventory_and_audit(output: Path) -> None:
    files = sorted(path for path in output.rglob("*") if path.is_file())
    by_top_level: dict[str, int] = {}
    for path in files:
        top = path.relative_to(output).parts[0]
        by_top_level[top] = by_top_level.get(top, 0) + 1
    inventory = {
        "schema_version": "1.0",
        "release_candidate": "contractfin_artifact_v1_0_rc6",
        "file_count_before_manifest": len(files),
        "total_bytes_before_manifest": sum(path.stat().st_size for path in files),
        "files_by_top_level": dict(sorted(by_top_level.items())),
        "included_data": [
            "FinQA normalized development split",
            "FinQA normalized test split required by the 34-file freeze lock",
            "registered 500-item answer-stripped inference input",
            "registered 500-item gold record",
        ],
        "excluded_data": [
            "all FinanceBench raw and normalized records",
            "full raw FinQA train/dev/test downloads",
            "normalized FinQA training split",
        ],
        "excluded_sensitive_material": [
            "API keys and environment files",
            "exact user-authored authorization text",
            "journal submission and correspondence files",
            "local absolute paths",
        ],
    }
    write_text(output, "reproducibility/release_inventory.json", json.dumps(inventory, indent=2))

    scan = scan_release(output)
    audit = {
        "schema_version": "1.0",
        "release_candidate": "contractfin_artifact_v1_0_rc6",
        "audit_scope": "local_prepublication_validation",
        "local_only": True,
        "external_upload_performed_at_audit_time": False,
        "license_selected_for_original_code": True,
        "original_code_license": "MIT",
        "copyright_holders": ["Wang Hongwu", "Xu Hui"],
        "finqa_license_included": True,
        "financebench_content_included": False,
        "authorization_text_redacted": True,
        "local_paths_normalized": True,
        **scan,
    }
    write_text(output, "reproducibility/public_release_audit.json", json.dumps(audit, indent=2))
    if not audit["passed"]:
        raise RuntimeError(f"release scan failed: {audit}")


def write_manifest(output: Path) -> None:
    manifest = output / "reproducibility" / "MANIFEST.sha256"
    rows = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path != manifest:
            rows.append(f"{sha256(path)}  {path.relative_to(output).as_posix()}")
    write_text(output, "reproducibility/MANIFEST.sha256", "\n".join(rows))


def create_zip(output: Path) -> Path:
    archive = output.with_suffix(".zip")
    if archive.exists():
        raise FileExistsError(f"refusing to overwrite existing archive: {archive}")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(output.rglob("*")):
            if not path.is_file():
                continue
            relative = Path(output.name) / path.relative_to(output)
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(2026, 9, 30, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            zf.writestr(info, path.read_bytes())
    return archive


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing directory: {output}")
    output.mkdir(parents=True)

    copy_release_files(output)
    normalize_local_paths(output)
    build_authorization_manifest(output)
    write_release_documents(output)
    write_inventory_and_audit(output)
    write_manifest(output)
    archive = create_zip(output)

    print(
        json.dumps(
            {
                "output": str(output),
                "archive": str(archive),
                "archive_sha256": sha256(archive),
                "file_count": sum(1 for path in output.rglob("*") if path.is_file()),
                "directory_bytes": sum(path.stat().st_size for path in output.rglob("*") if path.is_file()),
                "archive_bytes": archive.stat().st_size,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
