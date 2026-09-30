
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
