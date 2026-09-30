# DeepSeek B0 preregistered-30 diagnostic

## Run identity

- Protocol: `contractfin-b0-finqa-dev30-v1`
- Run ID: `b0-f8beac55-fd32-4358-bada-9c002a38bbc0`
- Provider/model request: `deepseek/deepseek-flash`
- Prompt version: `b0-direct-v1`
- Frozen output ceiling: `1024` tokens
- Paid API attempts: `30` (no retries and no sample substitutions)

## Completion and resource summary

| Measure | Result |
|---|---:|
| Successful structured responses | 14/30 (46.67%) |
| Failed responses | 16/30 (53.33%) |
| Incomplete responses with no `output_text` | 15 |
| Invalid JSON response | 1 |
| Failures ending at exactly 1,024 output tokens | 16/16 |
| Input tokens | 44,456 |
| Output tokens | 24,672 |
| Total tokens | 69,128 |
| Aggregate measured latency | 151,922 ms |
| Run-log completeness | 100% |

All 16 failed calls consumed exactly the configured maximum of 1,024 output
tokens. Fifteen returned `status=incomplete` without `output_text`; the remaining
response was not valid JSON. This is strong run-level evidence of output-ceiling
censoring, not evidence that those 16 items were answered incorrectly.

## Evaluation with explicit denominators

| Measure | Result | Interpretation |
|---|---:|---|
| Full-set final-answer accuracy | 7/30 (23.33%) | Includes 16 interface failures in the denominator |
| Selective accuracy | 7/14 (50.00%) | Accuracy among successfully parsed, answered responses |
| Full-set evidence macro-F1 | 0.2189 | Interface failures contribute zero evidence |
| Successful-response evidence macro-F1 | 0.4690 | Diagnostic only; conditional on completion |
| Exact program accuracy | 2/11 (18.18%) | Among responses that supplied an executable-form program field |
| Execution accuracy | 4/11 (36.36%) | Among responses with an attempted FinQA program |
| Execution coverage | 11/30 (36.67%) | Full registered set denominator |
| Persisted-record schema-valid rate | 30/30 (100%) | Includes locally generated, valid `status=error` records |

The 100% schema-valid rate describes the replayable artifact schema. It must not
be reported as a 100% model structured-output success rate; the latter is 14/30
for this run.

## Completion by preregistered stratum

| Stratum | Successful | Failed |
|---|---:|---:|
| `single_divide` | 1 | 4 |
| `single_subtract` | 3 | 1 |
| `single_add` | 1 | 1 |
| `single_multiply` | 2 | 0 |
| `table_average` | 1 | 1 |
| `table_sum` | 0 | 1 |
| `table_max` | 1 | 0 |
| `table_min` | 0 | 1 |
| `comparison` | 2 | 0 |
| `contains_exp` | 0 | 1 |
| `multi_2_step` | 2 | 2 |
| `multi_3_step` | 1 | 1 |
| `multi_4_step` | 0 | 1 |
| `multi_5_step` | 0 | 2 |

## Decision boundary

This run is retained as valid interface-diagnostic evidence, but it is not a
usable final B0 performance estimate because more than half of the registered
items were censored by the output ceiling. The prompt, evaluator, sample IDs and
execution order were not changed during the run.

Before any further paid call, create a versioned protocol amendment that changes
only the output-token ceiling and preserves every other experimental factor.
Any rerun must use new artifact filenames and must not overwrite this run.

## Frozen artifact hashes

| Artifact | SHA-256 |
|---|---|
| Gold slice | `b6ac633d53f78e4ffd66e6507b6dfcaddf33eec70acd7e8e8cb98f19af757e40` |
| Predictions | `2b53991710353a562dcad32c6dfbacb9de6e11a691c19308951a4341ffc037a3` |
| Evaluation report | `0c3e1c0ab5ae323ffc33d13743addfb37aff81dd550283bc87b828a343244d4d` |
| Replay log | `8b64e56f1351efbd76fb005fa1bcd88e288b0e9a81874d0c2b34724423a27da6` |
