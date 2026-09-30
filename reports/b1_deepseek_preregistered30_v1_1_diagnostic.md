# DeepSeek B1 preregistered-30 v1.1 diagnostic

## Decision

Protocol `contractfin-b1-finqa-dev30-v1.1` **failed its strict preregistered
interface gate**. It completed 29 of 30 samples and recorded one failed local
tool call; the requirement was 30 structured completions with zero failed tool
calls. This run is preserved as diagnostic evidence and must not be reported as
the final B1 result.

The run made no retries, substituted no samples, and used 97 of the authorized
maximum 180 model calls.

## Run identity and integrity

- Run ID: `b1-c9077ae3-d5c5-4741-845b-7f34214582c8`
- Provider/model: `deepseek/deepseek-flash`
- Registered samples: 30 unique items
- Gold, predictions, and logs: exact registered identity and order
- Model calls: 97
- Tool calls: 67
- Automatic retries: 0
- Sample substitutions: 0

## Gate result

| Criterion | Required | Observed | Passed |
|---|---:|---:|---|
| Structured completions | 30 | 29 | No |
| Samples using document search | 30 | 30 | Yes |
| Samples using effective `top_k=12` | 30 | 30 | Yes |
| Samples using deterministic calculation | 30 | 30 | Yes |
| Failed tool calls | 0 | 1 | No |
| Invalid final JSON samples | 0 | 1 | No |
| Output-ceiling failures | 0 | 0 | Yes |
| Transport timeouts | 0 | 0 | Yes |
| Log completeness | 100% | 100% | Yes |
| Exact sample identity/order | required | verified | Yes |

Overall gate result: **failed**.

## Exact failure diagnosis

The only failed sample, `finqa:dev:SNPS/2006/page_69.pdf-2`, completed its
search, calculation, and final model call. DeepSeek returned a valid JSON object
followed by three provider-specific DSML closing tags. The strict parser rejected
the suffix. The retained visible output has SHA-256
`500c81b1e63cdfaa0dd965e82ed2845a203100b3329cf9a17587abb71f409c3b`.

The sole failed tool call occurred on
`finqa:dev:JPM/2018/page_110.pdf-1`. The calculator rejected the actual table row
label `available-for-sale ( 201cafs 201d ) investment securities ( average )`
because v1.1 treated every parenthesis as reserved syntax. The model recovered
with scalar arithmetic, so this sample still produced a structured answer.

Both defects are deterministic local interface defects. They are not caused by
the retriever, answer evaluator, output-token ceiling, timeout, or lack of model
turns.

## Diagnostic metrics and denominator warning

| Measure | Result |
|---|---:|
| Structured model completions | 29/30 (96.67%) |
| Final-answer accuracy | 12/30 (40.00%) |
| Selective accuracy | 12/29 (41.38%) |
| Evidence macro-F1 | 0.8267 |
| Exact program accuracy | 0.3103 |
| Execution accuracy | 0.4138 |

The generated report's 100% schema-valid rate includes the locally generated
`status=error` replay record. It does not mean the model completed 30 structured
outputs. Because the interface gate failed, these values are diagnostic and are
not the final B1 performance estimate.

## Local repair verification

The exact two failing inputs were replayed after a narrowly scoped local patch:

1. a valid leading JSON object is accepted only when the remainder consists
   exclusively of known DeepSeek DSML closing tags; arbitrary trailing prose is
   still rejected;
2. the first argument of a table operation accepts balanced parentheses in an
   actual row label; commas, unbalanced parentheses, and nested syntax in normal
   calculation arguments remain rejected.

Both exact replays passed. All 50 automated tests and bytecode compilation also
passed. The B1 system prompt and exposed tool definitions are byte-for-byte
unchanged.

## Resource accounting

- Input tokens: 207,401
- Output tokens, including reasoning: 23,689
- Reasoning tokens: 16,666
- Total tokens: 231,090
- Aggregate measured latency: 288,172 ms

## Required next step

Register B1-v1.2 as a runtime-only amendment and rerun the same registered 30
items under a new artifact stem. The rerun requires separate explicit user
authorization and may make at most 180 model calls.

## Frozen artifact hashes

| Artifact | SHA-256 |
|---|---|
| Gold | `b6ac633d53f78e4ffd66e6507b6dfcaddf33eec70acd7e8e8cb98f19af757e40` |
| Predictions | `f8911284f144ac85f66b1fcc7b9ac5f60ffc25c79e06644f598fafde03f6b6fb` |
| Evaluation report | `2a1a0a0bf55f5452c661c35409828521897ae01aac849ba3bcc77f4eb3c89312` |
| Replay log | `c8ef97e2ccc94ea237e917dae83d2e1ad83fbdc9ae3008838cbbed935690787b` |
