# DeepSeek B2-v1 three-item live interface gate

## Decision

Protocol `contractfin-b2-finqa-dev3-interface-v1` **passed every
preregistered interface criterion**. The full four-role B2 pipeline is
technically ready for a separately authorized registered30 development run.

The run used exactly the authorized 18 model calls. It made no retries,
substituted no samples, and changed no parameter during execution.

## Run identity

- Run ID: `b2-f9f708dd-ecf0-4036-82ed-51c066a2b035`
- Provider/model request: `deepseek/deepseek-flash`
- Samples: 3 unique frozen interface items
- Model calls: 18/18
- Tool calls: 6/6
- Automatic retries: 0
- Sample substitutions: 0

## Gate result

| Criterion | Required | Observed | Passed |
|---|---:|---:|---|
| Structured pipeline completions | 3 | 3 | Yes |
| Valid task contracts | 3 | 3 | Yes |
| Evidence searches | 3 | 3 | Yes |
| Explicit `top_k=12` searches | 3 | 3 | Yes |
| Deterministic calculations | 3 | 3 | Yes |
| Valid verifier verdicts | 3 | 3 | Yes |
| Failed tool calls | 0 | 0 | Yes |
| Invalid structured stage outputs | 0 | 0 | Yes |
| Output-ceiling failures | 0 | 0 | Yes |
| Transport timeouts | 0 | 0 | Yes |
| Log completeness | 100% | 100% | Yes |
| Exact sample identity/order | required | verified | Yes |

All 18 provider calls reported `completed`. No provider error, incomplete
response, or transport normalization occurred.

## Role execution and resource use

| Role | Calls | Input tokens | Output tokens | Reasoning tokens | Total tokens | Latency ms |
|---|---:|---:|---:|---:|---:|---:|
| Task Contract Agent | 3 | 2,398 | 4,504 | 3,555 | 6,902 | 24,591 |
| Evidence Agent | 6 | 8,619 | 2,092 | 561 | 10,711 | 14,958 |
| Solver Agent | 6 | 8,895 | 13,914 | 13,477 | 22,809 | 71,482 |
| Verifier Agent | 3 | 3,856 | 2,871 | 2,727 | 6,727 | 16,959 |
| **Total** | **18** | **23,768** | **23,381** | **20,320** | **47,149** | **128,010** |

The solver was the largest cost center, accounting for 48.4% of total tokens
and 55.8% of measured latency. This observation will be retained for later
quality-cost analysis; it does not justify changing the frozen development
protocol.

## Verifier behavior

The verifier accepted two candidates and routed one to `human_review`. The
reviewed table-aggregation item received four reason codes:

- `incorrect_total`
- `double_counted_components`
- `answer_evidence_mismatch`
- `direct_total_available`

This demonstrates that the conservative disagreement path is operational. The
human-review rate was explicitly not an interface criterion, and the outcome
will not trigger item-specific prompt or evaluator changes.

## Diagnostic outcomes

| Measure | Result |
|---|---:|
| Answer coverage | 2/3 |
| Final-answer accuracy | 1/3 |
| Selective accuracy | 1/2 |
| Execution coverage | 3/3 |
| Execution accuracy | 1/3 |
| Evidence macro-F1 | 0.6889 |

These three items were deliberately selected for interface coverage—five-step
arithmetic, table aggregation, and comparison. They are not a performance
sample, so the values above are diagnostic only.

## Next authorization boundary

The next eligible action is the frozen full-B2 registered30 development run.
It can make at most 180 model calls and requires separate explicit
authorization. Neither ablation is authorized by that approval.

To authorize only the full-B2 registered30 run, reply exactly:

> 同意执行B2-v1完整架构预注册30题测试，最多180次模型调用。

The words “继续” or “开始下一阶段” alone do not authorize a paid API call.

## Frozen artifact hashes

| Artifact | SHA-256 |
|---|---|
| Gold | `778765502767f374124c876465fc7e0ab5baa48673f0d523b23cc494e80b20a0` |
| Predictions | `b8b83ab3cfb5892ac8599de507010f9ebdba0d7524eb06a58e520871f4e39cce` |
| Evaluation report | `55308a375f10ac56cf4258ea09815adbd40a52a2ca45c5b63baf4bcdd53e972c` |
| Replay log | `f783196de98206a23a7dc269614ebec6503a312a785f7204bb293467421b22ff` |
