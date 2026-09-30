# DeepSeek B0 preregistered-30 v1.2 diagnostic

## Run identity

- Protocol: `contractfin-b0-finqa-dev30-v1.2`
- Run ID: `b0-f72a2ba2-9883-49fb-839f-8a79a7909fad`
- Provider/model request: `deepseek/deepseek-flash`
- Prompt version: `b0-direct-v1`
- Frozen output ceiling: `32768` tokens
- Client timeout: `300` seconds
- Paid API attempts: `30` (no retries and no sample substitutions)

## Preregistered gate result

| Criterion | Required | Observed | Passed |
|---|---:|---:|---|
| Attempted calls | 30 | 30 | Yes |
| Structured completions | 30 | 30 | Yes |
| `max_output_tokens` failures | 0 | 0 | Yes |
| Client transport timeouts | 0 | 0 | Yes |
| Log completeness | 100% | 100% | Yes |
| Exact sample identity and order | required | verified | Yes |

Overall gate result: **passed**.

## Completion and resource summary

| Measure | Result |
|---|---:|
| Successful structured responses | 30/30 (100%) |
| Failed responses | 0/30 |
| Input tokens | 44,456 |
| Output tokens, including reasoning | 47,969 |
| Reasoning tokens | 45,930 |
| Non-reasoning output tokens by subtraction | 2,039 |
| Total tokens | 92,425 |
| Aggregate measured latency | 246,270 ms |
| Median call latency | 5,536 ms |
| Maximum call latency | 55,082 ms |
| Run-log completeness | 100% |

The recurrent item `finqa:dev:CB/2010/page_200.pdf-4` completed normally. It
used 13,205 output tokens, of which 13,113 were reported as reasoning tokens,
and took 55,082 ms. This directly verifies that the earlier 1,024- and
8,192-token failures were output-ceiling censoring rather than an unsupported
sample or persistent API error.

Across all 30 calls, median output use was 909 tokens and median reasoning use
was 852 tokens. The recurrent item is therefore a long-tail outlier rather than
representative resource consumption.

## Development-smoke evaluation

| Measure | Result | Denominator |
|---|---:|---:|
| Final-answer accuracy | 12/30 (40.00%) | all registered samples |
| Evidence macro-precision | 0.6278 | all registered samples |
| Evidence macro-recall | 0.6667 | all registered samples |
| Evidence macro-F1 | 0.6411 | all registered samples |
| Exact program accuracy | 3/27 (11.11%) | responses supplying a program |
| Execution accuracy | 5/27 (18.52%) | responses supplying an attempted FinQA program |
| Execution coverage | 27/30 (90.00%) | all registered samples |
| Persisted-record schema-valid rate | 30/30 (100%) | all registered samples |

These figures are development-smoke observations. They validate the B0
interface and expose weaknesses for later hypothesis formation; they are not
final held-out test performance and must not trigger item-specific prompt or
evaluator changes.

## Three-run interface progression

| Measure | v1 (1,024) | v1.1 (8,192) | v1.2 (32,768) |
|---|---:|---:|---:|
| Structured completions | 14/30 | 29/30 | 30/30 |
| Ceiling/parse failures | 16 | 1 | 0 |
| Final-answer accuracy | 7/30 | 10/30 | 12/30 |
| Evidence macro-F1 | 0.2189 | 0.5933 | 0.6411 |
| Total tokens | 69,128 | 91,098 | 92,425 |
| Aggregate measured latency | 151,922 ms | 237,215 ms | 246,270 ms |

The defensible causal conclusion is limited to interface completion: increasing
the ceiling eliminated truncation. Accuracy changes across runs must not be
attributed solely to the ceiling because provider-default generation is
stochastic.

## Decision boundary

B0 development infrastructure and request configuration are now frozen. Do not
run another B0 development iteration or tune against these 30 answers. The next
research implementation stage may begin with B1 under a separately registered
single-agent protocol, while preserving B0 artifacts unchanged.

## Frozen artifact hashes

| Artifact | SHA-256 |
|---|---|
| Gold slice | `b6ac633d53f78e4ffd66e6507b6dfcaddf33eec70acd7e8e8cb98f19af757e40` |
| Predictions | `19cf98b4017bedee042c475a8eeb8bea7aec9bd0b00b640bbc9e6b2733452f47` |
| Evaluation report | `2bbc5c895164f907dd320fd78a87012ecede7cb8b587be7c00bda64c46677551` |
| Replay log | `a08495a87f89e5f148003a1908220c5bfecdeb9ecb4c878fc1ffdd94d7491bf3` |
