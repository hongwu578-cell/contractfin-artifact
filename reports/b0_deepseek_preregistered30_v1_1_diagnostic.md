# DeepSeek B0 preregistered-30 v1.1 diagnostic

## Run identity

- Protocol: `contractfin-b0-finqa-dev30-v1.1`
- Run ID: `b0-f43ed65b-2964-4c73-b242-9615e49f494d`
- Provider/model request: `deepseek/deepseek-flash`
- Prompt version: `b0-direct-v1`
- Frozen output ceiling: `8192` tokens
- Paid API attempts: `30` (no retries and no sample substitutions)

## Preregistered gate result

| Criterion | Required | Observed | Passed |
|---|---:|---:|---|
| Attempted calls | 30 | 30 | Yes |
| Structured completions | at least 29 | 29 | Yes |
| `max_output_tokens` failures | 0 | 1 | **No** |
| Log completeness | 100% | 100% | Yes |
| Exact sample identity and order | required | verified | Yes |

Overall gate result: **not passed**. Post-hoc relaxation of the zero-truncation
criterion is not permitted.

## Completion and resource summary

| Measure | Result |
|---|---:|
| Successful structured responses | 29/30 (96.67%) |
| Failed responses | 1/30 (3.33%) |
| Input tokens | 44,456 |
| Output tokens, including reasoning | 46,642 |
| Reasoning tokens | 44,597 |
| Non-reasoning output tokens by subtraction | 2,045 |
| Total tokens | 91,098 |
| Aggregate measured latency | 237,215 ms |
| Median successful-call latency | 5,627 ms |
| Run-log completeness | 100% |

The sole failure was registered item 10,
`finqa:dev:CB/2010/page_200.pdf-4` (`single_divide`). It returned
`status=incomplete`, `incomplete_reason=max_output_tokens`, and 8,192 output
tokens, all reported as reasoning tokens. It produced no visible `output_text`.
The same item also reached the 1,024-token ceiling in the parent run.

Among the 29 completed responses, median output usage was 944 tokens, median
reasoning usage was 885 tokens, and the largest completed response used 4,535
output tokens. This isolates the remaining failure to one recurring pathological
generation rather than a broad 8,192-token insufficiency across the set.

## Evaluation with explicit denominators

| Measure | Result | Interpretation |
|---|---:|---|
| Full-set final-answer accuracy | 10/30 (33.33%) | Includes the one interface failure |
| Selective accuracy | 10/29 (34.48%) | Accuracy among completed responses |
| Full-set evidence macro-F1 | 0.5933 | Registered 30-item denominator |
| Completed-response evidence macro-F1 | 0.6138 | Conditional on completion |
| Exact program accuracy | 3/26 (11.54%) | Among responses supplying a program |
| Execution accuracy | 8/26 (30.77%) | Among responses supplying an attempted FinQA program |
| Execution coverage | 26/30 (86.67%) | Registered 30-item denominator |
| Persisted-record schema-valid rate | 30/30 (100%) | Includes the valid local `status=error` record |

The 100% persisted-record schema rate is an artifact-integrity measure. Model
structured-output success is 29/30.

## Comparison with the parent interface run

| Measure | v1 (1,024) | v1.1 (8,192) |
|---|---:|---:|
| Structured completions | 14/30 | 29/30 |
| Ceiling/parse failures | 16/30 | 1/30 |
| Full-set final-answer accuracy | 7/30 | 10/30 |
| Selective accuracy | 7/14 | 10/29 |
| Full-set evidence macro-F1 | 0.2189 | 0.5933 |
| Total tokens | 69,128 | 91,098 |
| Aggregate measured latency | 151,922 ms | 237,215 ms |

Accuracy changes must not be attributed solely to the output ceiling because
the provider-default model generation is stochastic. The defensible conclusion
is limited to the large improvement in interface completion.

## Decision boundary

This run is retained as strong interface-diagnostic evidence, but the frozen
gate did not pass. Do not proceed to B1/B2 as if B0 were fully stabilized, do
not count the censored item as a reasoning error, and do not change the sample
or prompt around that item.

Any further run requires a separately versioned protocol decision and new user
authorization. Existing artifacts must not be overwritten.

## Frozen artifact hashes

| Artifact | SHA-256 |
|---|---|
| Gold slice | `b6ac633d53f78e4ffd66e6507b6dfcaddf33eec70acd7e8e8cb98f19af757e40` |
| Predictions | `4b74c9510b44452e3ab711fdfb389ca3ffa60adf2d2d34784534bbec668940d1` |
| Evaluation report | `72932a68c6fee4be38214270fd02a738ba58ede6fce0e4885d6303107c7cf035` |
| Replay log | `e1b9d76593d6c32d01c45ab558b2d5f34b18980dcc9294c92f828f27676c9de0` |
