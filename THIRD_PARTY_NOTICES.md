
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
