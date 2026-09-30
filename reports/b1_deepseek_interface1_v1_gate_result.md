# B1 DeepSeek one-item interface gate result

## Decision

Protocol `contractfin-b1-finqa-dev1-interface-v1` passed. The B1 single-agent
tool loop is compatible with the live DeepSeek Responses API and is technically
ready for the separately authorized registered 30-item development run.

## Run identity

- Run ID: `b1-558626a3-9760-421a-8479-f90c99cbca15`
- Sample: `finqa:dev:V/2008/page_17.pdf-1`
- Provider/model: `deepseek/deepseek-flash`
- Model calls: 3 of the allowed 4
- Local tool calls: 2 of the allowed 6
- Automatic retries: 0

## Preregistered gate

| Criterion | Required | Observed | Passed |
|---|---:|---:|---|
| Structured completions | 1 | 1 | Yes |
| Samples using document search | 1 | 1 | Yes |
| Samples using effective `top_k=12` | 1 | 1 | Yes |
| Samples using deterministic calculation | 1 | 1 | Yes |
| Failed tool calls | 0 | 0 | Yes |
| Output-ceiling failures | 0 | 0 | Yes |
| Transport timeouts | 0 | 0 | Yes |
| Log completeness | 100% | 100% | Yes |

Overall gate result: **passed**.

## Observed tool sequence

1. The single agent searched for “average payment volume per transaction
   American Express” with `top_k=12`.
2. Retrieval returned official evidence label `table_3`, containing payment
   volume 637 and total transactions 5.0.
3. The agent called the deterministic calculator with
   `divide(637, 5.0)`, which returned 127.4.
4. The agent returned answer `127.4`, evidence `table_3`, and unit
   `dollars per transaction` in the frozen structured schema.

## Evaluation and interpretation

| Metric | Result |
|---|---:|
| Final-answer accuracy | 1.0 |
| Schema-valid rate | 1.0 |
| Evidence macro-F1 | 1.0 |
| Execution accuracy | 1.0 |
| Exact-string program accuracy | 0.0 |
| Unit/scale error rate | 0.0 |

The exact-string program score is zero only because the prediction used
`divide(637, 5.0)` while the gold program uses
`divide(637, const_5)`. Both execute to 127.4. This is a representation
difference, not a calculation failure; execution accuracy is therefore the
appropriate semantic check.

## Resource use

- Input tokens: 4,498
- Output tokens, including reasoning: 264
- Reasoning tokens: 88
- Total tokens: 4,762
- Aggregate measured latency: 5,201 ms

## Frozen artifact hashes

| Artifact | SHA-256 |
|---|---|
| Gold | `97b5722fc597e0d56c1e92768fb4f922535a6044a15667983150bef82cb5ffb1` |
| Predictions | `b5d5f1c4967629a0e5acf715293ea74cb008a1292d16b6af4afaf29dba800bd6` |
| Evaluation report | `aea01bc60e1f13f9e6531aa3bdbf6564e3e0c3dbe6564b732108f9dbff3deb59` |
| Replay log | `4fc5f067f2ef999bea4f2f18617e94a1c9e30dfb3deb7cf3b4023ab7a2757316` |

The next action is the frozen registered 30-item B1 development run. It can
make up to 120 paid model calls and requires separate explicit authorization.
