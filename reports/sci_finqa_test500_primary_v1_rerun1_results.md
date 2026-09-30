# SCI held-out B0/B1 primary results

- Generated at: `2026-09-29T13:36:04.365015+00:00`
- Run ID: `sci-heldout-9d2c37d5-bc3e-473f-b8af-7630be75e31e`
- Registered paired items: 500
- B0 accuracy: 0.4200 (210/500)
- B1 accuracy: 0.4700 (235/500)
- B1 minus B0: +0.0500 (95% paired bootstrap CI +0.0140 to +0.0880)
- Exact McNemar: B1-only=58, B0-only=33, p=0.0114563

## Secondary family (Holm corrected)

| Outcome | B0 | B1 | Difference | Raw p | Holm p | Reject |
|---|---:|---:|---:|---:|---:|:---:|
| program_itt_correctness | 0.1860 | 0.3900 | +0.2040 | 4.74093e-24 | 1.42228e-23 | yes |
| execution_itt_correctness | 0.2480 | 0.5160 | +0.2680 | 2.08181e-29 | 8.32723e-29 | yes |
| coverage | 0.9900 | 0.9820 | -0.0080 | 0.34375 | 0.545255 | no |
| evidence_item_f1 | 0.8367 | 0.8260 | -0.0107 | 0.272627 | 0.545255 | no |

## Resources

- B0 model calls: 500
- B1 model calls: 1610
- B0 total tokens: 1603138
- B1 total tokens: 3856862

All error, abstain, and missing outputs are retained as incorrect under the registered ITT rule.
