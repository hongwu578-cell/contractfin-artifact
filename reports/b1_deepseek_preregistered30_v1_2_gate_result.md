# DeepSeek B1 preregistered-30 v1.2 gate result

## Decision

Protocol `contractfin-b1-finqa-dev30-v1.2` **passed every preregistered
interface criterion**. This run is accepted as the B1 tool-augmented
single-agent development result. B1 should now be frozen; the 30 development
answers must not be used for another round of B1 item-specific tuning.

## Run identity and integrity

- Run ID: `b1-bb2095c7-deeb-4a70-925e-f8991a8035c3`
- Provider/model request: `deepseek/deepseek-flash`
- Samples: 30 unique registered items, in the frozen order
- Model calls: 94 of the authorized maximum 180
- Local tool calls: 64
- Automatic retries: 0
- Sample substitutions: 0
- All 94 provider responses reported `completed`

## Preregistered gate result

| Criterion | Required | Observed | Passed |
|---|---:|---:|---|
| Structured completions | 30 | 30 | Yes |
| Samples using document search | 30 | 30 | Yes |
| Samples using effective `top_k=12` | 30 | 30 | Yes |
| Samples using deterministic calculation | 30 | 30 | Yes |
| Failed tool calls | 0 | 0 | Yes |
| Invalid final JSON samples | 0 | 0 | Yes |
| Output-ceiling failures | 0 | 0 | Yes |
| Transport timeouts | 0 | 0 | Yes |
| Log completeness | 100% | 100% | Yes |
| Exact sample identity/order | required | verified | Yes |

Overall gate result: **passed**.

No response required the new DeepSeek transport-suffix normalization during
this run. The runtime correction therefore remained dormant rather than
silently altering a normal response. The previously problematic table-label
input remains covered by its retained exact local replay and automated tests.

## Development-set outcomes

| Measure | Result |
|---|---:|
| Final-answer accuracy | 15/30 (50.00%) |
| Exact program accuracy | 13/30 (43.33%) |
| Execution accuracy | 17/30 (56.67%) |
| Execution coverage | 30/30 (100%) |
| Evidence macro-precision | 0.8889 |
| Evidence macro-recall | 0.9500 |
| Evidence macro-F1 | 0.9089 |
| Schema-valid rate | 30/30 (100%) |
| Unit/scale error rate | 0 |
| Unsupported-claim rate | 0 |

These are development-set observations, not held-out performance estimates.
Answer accuracy was an outcome and was not an interface acceptance criterion.

## Descriptive B0 comparison

The corrected B0-v1.2 and B1-v1.2 artifacts use the same 30 samples and order.

| Measure | B0 direct LLM | B1 tool-augmented agent | Difference |
|---|---:|---:|---:|
| Final-answer accuracy | 40.00% | 50.00% | +10.00 percentage points |
| Execution coverage | 90.00% | 100.00% | +10.00 percentage points |
| Execution accuracy | 18.52% | 56.67% | +38.15 percentage points |
| Evidence macro-F1 | 0.9211 | 0.9089 | -0.0122 |

This comparison is descriptive only. It is based on one small development run
per condition with provider-default stochastic generation. It does not support
a causal claim or statistical significance claim. In particular, B1's tools
improved arithmetic execution behavior in this run, while evidence F1 did not
improve over the identifier-corrected B0 record.

## Resource accounting

- Input tokens: 187,432
- Output tokens, including reasoning: 13,129
- Reasoning tokens: 6,401
- Total tokens: 200,561
- Aggregate measured latency: 188,915 ms
- Maximum model calls observed for one sample: 4 of 6
- Maximum tool calls observed for one sample: 3 of 8

## Decision boundary and next stage

B1 is now frozen. The next research step is local and makes no paid API calls:
define and preregister B2's multi-agent roles, message topology, task contract,
verification/conflict-resolution policy, call budget, ablations, and live
interface gate. B2 must not be tested against the API until that protocol has
been reviewed and separately authorized.

## Frozen artifact hashes

| Artifact | SHA-256 |
|---|---|
| Gold | `b6ac633d53f78e4ffd66e6507b6dfcaddf33eec70acd7e8e8cb98f19af757e40` |
| Predictions | `3821dff53acad85ba1c194ca18b3665f548a83d2e4a511cec56ee3731c12bcbe` |
| Evaluation report | `88a285ffc55a10efc0b03d076ea42c428a0f76f55e9a41ac29c6533bca324c83` |
| Replay log | `71c59e861b731930ca6644c453486c10b559841cf05ff434afc30f9ba25a598e` |
