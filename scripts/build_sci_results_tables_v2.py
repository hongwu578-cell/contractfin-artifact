#!/usr/bin/env python3
"""Build the round-two main and supplementary table inventory."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"expected one match for {old!r}, found {count}")
    return text.replace(old, new, 1)


def extract_markdown_table(text: str, caption: str) -> str:
    start = text.find(caption)
    if start < 0:
        raise ValueError(f"missing caption: {caption}")
    table_start = text.find("\n|", start)
    if table_start < 0:
        raise ValueError(f"missing table rows after: {caption}")
    end = text.find("\n\n", table_start)
    if end < 0:
        end = len(text)
    return text[start:end].rstrip()


def build(source_path: Path, manuscript_path: Path) -> str:
    source = source_path.read_text(encoding="utf-8")
    manuscript = manuscript_path.read_text(encoding="utf-8")

    source = replace_once(source, "# ContractFin SCI result tables", "# ContractFin SCI result tables: round-two inventory")
    replacements = {
        "## Table 4. Preregistered paired held-out comparison": "## Table 2. Preregistered paired held-out comparison",
        "## Table 5. Preregistered secondary outcomes": "## Table 3. Preregistered secondary outcomes",
        "## Table 6. Resource use and quality–cost trade-off": "## Table 4. Resource use and quality–cost trade-off",
        "## Table 7. Descriptive three-run stability on the registered 100-item subset": "## Table 5. Descriptive three-run stability on the registered 100-item subset",
        "## Table 8. Paired outcome transitions and mechanism evidence": "## Table 6. Paired outcome transitions and mechanism evidence",
        "## Supplementary Table S1. Accuracy by operation stratum": "## Supplementary Table S3. Accuracy by operation stratum",
        "## Supplementary Table S2. B1 system-output failures": "## Supplementary Table S4. B1 system-output failures",
        "## Supplementary Table S3. Final-answer and executable-program consistency": "## Supplementary Table S5. Final-answer and executable-program consistency",
    }
    for old, new in replacements.items():
        source = replace_once(source, old, new)

    s1 = extract_markdown_table(
        manuscript,
        "**Supplementary Table S1. Frozen held-out allocation by operation stratum**",
    ).replace("**Supplementary Table S1.", "## Supplementary Table S1.", 1).replace("**\n", "\n", 1)
    s2 = extract_markdown_table(
        manuscript,
        "**Supplementary Table S2. Formative development evidence for the architecture ladder**",
    ).replace("**Supplementary Table S2.", "## Supplementary Table S2.", 1).replace("**\n", "\n", 1)

    supplement_anchor = "## Supplementary Table S3. Accuracy by operation stratum"
    index = source.find(supplement_anchor)
    if index < 0:
        raise ValueError("supplement insertion anchor missing")
    inventory_note = (
        "The main manuscript contains six numbered tables. Sampling allocation and formative architecture evidence are moved to the supplement so that confirmatory outcomes remain visually primary.\n\n"
    )
    s2_note = (
        "† B0 evidence scores use the deterministic migration to official evidence identifiers; answer and program results are unchanged. "
        "Execution accuracy in this formative table follows the historical selective denominator and must not be compared as though it were the frozen held-out ITT execution outcome. "
        "B2 error records are included for diagnosis."
    )
    source = source[:index] + inventory_note + s1 + "\n\n" + s2 + "\n\n" + s2_note + "\n\n" + source[index:]
    provenance = (
        f"<!-- Source table draft SHA-256: {sha256_file(source_path)}; "
        f"source manuscript SHA-256: {sha256_file(manuscript_path)}. -->\n\n"
    )
    return source.replace("\n\n", "\n\n" + provenance, 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="manuscript/contractfin_sci_results_tables_v1.md")
    parser.add_argument("--manuscript", default="manuscript/contractfin_sci_full_v4.md")
    parser.add_argument("--output", default="manuscript/contractfin_sci_results_tables_v2.md")
    args = parser.parse_args()
    source_path = (PROJECT_ROOT / args.source).resolve()
    manuscript_path = (PROJECT_ROOT / args.manuscript).resolve()
    output_path = (PROJECT_ROOT / args.output).resolve()
    output_path.write_text(build(source_path, manuscript_path), encoding="utf-8")
    print(f"wrote {output_path.relative_to(PROJECT_ROOT)} sha256={sha256_file(output_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
