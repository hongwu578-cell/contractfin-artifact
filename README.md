
# ContractFin reproducibility artifact (v1.0-rc5)

This is a local release candidate for the study **“Tool Use Before Teamwork? A Preregistered, Cost-Aware Evaluation of LLM Architectures for Financial Numerical Reasoning.”** It has not been uploaded or assigned a DOI.

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
python3 scripts/audit_sci_primary_structure.py
python3 scripts/audit_sci_stability_structure.py
```

Live model commands require an explicitly configured provider key and may incur charges. They are not part of local validation and must not be run merely to inspect this artifact.

## Integrity

`reproducibility/MANIFEST.sha256` covers every packaged file except the manifest itself. `reproducibility/public_release_audit.json` records the local release checks.

## Release status

Original ContractFin code and documentation are released under the MIT License. The candidate is ready for author review before upload; the repository URL/DOI remains to be assigned. Third-party terms and exclusions are documented in `THIRD_PARTY_NOTICES.md` and `LICENSE_SCOPE.md`.
