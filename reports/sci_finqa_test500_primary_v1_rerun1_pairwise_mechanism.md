# SCI held-out paired error and mechanism analysis

- Protocol: `contractfin-sci-finqa-test500-v1`
- Run ID: `sci-heldout-9d2c37d5-bc3e-473f-b8af-7630be75e31e`
- Model API calls during this analysis: **0**
- Analysis status: exploratory mechanism analysis after confirmatory prediction freeze

## Paired outcome transitions

| Transition | Items | Share |
|---|---:|---:|
| Both correct | 177 | 35.4% |
| B1 only correct | 58 | 11.6% |
| B0 only correct | 33 | 6.6% |
| Both wrong | 232 | 46.4% |

B1 generated 25 net additional correct answers (58 gains minus 33 regressions).

## Mechanisms in the 58 B1-only gains

- Exact-program recovery relative to B0: 20 items.
- Executable-program recovery relative to B0: 30 items.
- Evidence F1 improved/unchanged/worsened: 14/38/6.
- Calculator reached: 58/58 items.

The majority of gains did not coincide with improved evidence F1, so the observed benefit is more consistent with arithmetic/program assistance than with uniformly better evidence selection.

## Mechanisms in the 33 B0-only regressions

- B1 system-output failures: 2 items.
- Execution regressions relative to B0: 9 items.
- Exact-program regressions relative to B0: 3 items.
- Evidence F1 improved/unchanged/worsened: 3/21/9.

## Answer–program synchronization

| System | Answer correct and executable | Answer correct, not executable | Answer wrong but executable | Answer wrong, not executable | Answer consistency given executable program |
|---|---:|---:|---:|---:|---:|
| B0 | 107 | 103 | 17 | 273 | 86.3% |
| B1 | 197 | 38 | 61 | 204 | 76.4% |

B1 greatly increased execution correctness, but it also increased cases in which an executable program reached the gold value while the reported final answer remained wrong (61 versus 17). This is a concrete output-synchronization target for the next architecture revision.

## Tool-path evidence

- `search_document` calls: 623.
- `calculate_finqa` calls: 490 (488 successful; 2 failed).
- Items reaching the calculator: 475; correct: 235.
- Items not reaching the calculator: 25; correct: 0.
- Failed calculator events followed by a correct final answer: 1.

These are process associations, not randomized causal effects of choosing a tool path.

## Step-depth profile

| Steps | n | B0 accuracy | B1 accuracy | Difference | B1-only | B0-only | 95% paired bootstrap CI |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 287 | 53.3% | 56.8% | +3.5 pp | 32 | 22 | [-1.4 pp, +8.7 pp] |
| 2 | 167 | 24.0% | 35.9% | +12.0 pp | 25 | 5 | [+6.0 pp, +18.0 pp] |
| 3 | 22 | 45.5% | 45.5% | +0.0 pp | 1 | 1 | [-13.6 pp, +13.6 pp] |
| 4 | 9 | 33.3% | 22.2% | -11.1 pp | 0 | 1 | [-33.3 pp, +0.0 pp] |
| 5 | 15 | 26.7% | 0.0% | -26.7 pp | 0 | 4 | [-46.7 pp, -6.7 pp] |

The depth analysis is exploratory. In particular, the four- and five-step groups are too small for broad claims.

## Claim boundary

Deterministic flags are nonexclusive diagnostic indicators. Numeric extraction, semantic operation choice, and argument-order causes require blinded manual coding before being reported as adjudicated error categories.
