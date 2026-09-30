# B1-v1.1 DeepSeek two-item interface gate result

## Decision

Protocol `contractfin-b1-finqa-dev2-interface-v1.1` passed every preregistered
interface criterion. The structured calculator schema works with the live
DeepSeek Responses API for both multi-step arithmetic and table aggregation.
B1-v1.1 is technically ready for a separately authorized registered30 rerun.

## Run identity

- Run ID: `b1-ad25e277-a336-4455-a29f-4eaf83fe8b8d`
- Provider/model: `deepseek/deepseek-flash`
- Samples: 2, with zero overlap with the registered30 set
- Model calls: 6 of the allowed 12
- Local tool calls: 4 of the allowed 16
- Automatic retries: 0
- Sample substitutions: 0

## Gate result

| Criterion | Required | Observed | Passed |
|---|---:|---:|---|
| Structured completions | 2 | 2 | Yes |
| Samples using document search | 2 | 2 | Yes |
| Samples using effective `top_k=12` | 2 | 2 | Yes |
| Samples using structured calculation | 2 | 2 | Yes |
| Failed tool calls | 0 | 0 | Yes |
| Invalid final JSON samples | 0 | 0 | Yes |
| Output-ceiling failures | 0 | 0 | Yes |
| Transport timeouts | 0 | 0 | Yes |
| Log completeness | 100% | 100% | Yes |

Overall gate result: **passed**.

## Structured-tool observations

The four-step item used one search followed by the exact structured sequence:

`subtract(920, 95), subtract(469, 77), subtract(#1, #0), divide(#2, #0)`

The table item used one search followed by:

`table_average(settlements, none)`

Both calls succeeded on the first calculator attempt. Both final responses
copied the canonical program, parsed as raw JSON, and passed deterministic
execution.

## Evaluation outside the gate

| Metric | Result |
|---|---:|
| Final-answer accuracy | 1/2 (50%) |
| Exact program accuracy | 2/2 (100%) |
| Execution accuracy | 2/2 (100%) |
| Evidence macro-F1 | 0.7333 |
| Schema-valid rate | 2/2 (100%) |

Answer accuracy was deliberately not an interface criterion. The table-average
prediction was `-11.33`, whereas the gold string is `-11.33333`. Its exact
program and execution result are correct, but the rounded string falls outside
the evaluator's already frozen numeric tolerance. The tolerance was not changed
after observing this item.

## Resource use

- Input tokens: 12,025
- Output tokens, including reasoning: 2,295
- Reasoning tokens: 1,836
- Total tokens: 14,320
- Aggregate measured latency: 19,906 ms

## Frozen artifact hashes

| Artifact | SHA-256 |
|---|---|
| Gold | `826d205f2b6dddfbd364a7aa098a9acbeb9355a73429fb3233c5ad09b96b41ca` |
| Predictions | `44a8c0d14bf641d4532c2ac058e4921bc6fba695d7cb2952a4254ce908d4a3dd` |
| Evaluation report | `899cf413c7bf526969969ab1414b3878c437069375e0cf62fd3dd5d9f92ab667` |
| Replay log | `f16a858a8740a04e6fe3fd09065eab3c261ccf78ddb6dc3701078e7295f06d8c` |

The conditional registered30 v1.1 rerun may make at most 180 paid model calls
and requires separate explicit authorization.
