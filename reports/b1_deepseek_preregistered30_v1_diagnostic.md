# DeepSeek B1 preregistered-30 v1 diagnostic

## Decision

Protocol `contractfin-b1-finqa-dev30-v1` **failed its preregistered interface
gate**. This run is retained as development-interface diagnostic evidence and
must not be presented as the final B1 performance result.

The run made no retries, substituted no samples and stayed below the authorized
120-call ceiling. All original records are preserved.

## Run identity and integrity

- Run ID: `b1-81337a19-ea61-4f81-badc-781b2032db51`
- Provider/model: `deepseek/deepseek-flash`
- Registered samples: 30 unique items
- Gold, predictions and logs: exact registered identity and order
- Model calls: 109
- Tool calls: 93
- Automatic retries: 0
- Sample substitutions: 0

## Preregistered gate result

| Criterion | Required | Observed | Passed |
|---|---:|---:|---|
| Structured completions | 30 | 16 | No |
| Samples using document search | 30 | 30 | Yes |
| Samples using effective `top_k=12` | 30 | 30 | Yes |
| Samples using deterministic calculation | 30 | 26 | No |
| Failed tool calls | 0 | 21 | No |
| Output-ceiling failures | 0 | 0 | Yes |
| Transport timeouts | 0 | 0 | Yes |
| Log completeness | 100% | 100% | Yes |
| Exact sample identity/order | required | verified | Yes |

Overall gate result: **failed**.

## Failure structure

All 109 provider calls reported `completed`; there were no output-ceiling or
transport failures. The failure therefore lies in the B1 interaction contract,
not API availability.

The calculator received 38 calls, 21 of which failed deterministically:

| Failure category | Count |
|---|---:|
| Non-flat separators, assignments or infix syntax | 10 |
| Nested operations unsupported by the flat FinQA parser | 5 |
| Table-aggregate argument mismatch | 5 |
| Operation-arity mismatch | 1 |

Examples include semicolon-separated operations, explicit `= #0`
assignments, nested `divide(add(...), 3)`, table evidence labels passed where a
row name was expected, and three-argument `add`. These patterns show that the
tool description did not specify its accepted grammar precisely enough.

Nineteen samples reached the fourth and final model-call limit. Fourteen of
those returned visible final text that could not be decoded as JSON. The
current trace records status, output-item type and usage but deliberately does
not retain invalid visible response text; the exact syntax defects therefore
cannot be reconstructed from this run.

Four arithmetic samples used document search but never reached the calculator,
mainly because repeated searches consumed the permitted interaction turns.

## Diagnostic metrics and denominator warning

| Measure | Result | Denominator |
|---|---:|---:|
| Structured model completions | 16/30 (53.33%) | all registered samples |
| Final-answer accuracy | 7/30 (23.33%) | all registered samples |
| Selective accuracy | 7/16 (43.75%) | structured completions only |
| Evidence macro-F1 | 0.4878 | all 30; errors contribute zero |
| Evidence macro-F1 | 0.9146 | 16 structured completions only |
| Exact program accuracy | 4/15 (26.67%) | completed responses supplying a program |
| Execution accuracy | 7/15 (46.67%) | completed responses supplying a program |

The generated report shows a persisted-record schema-valid rate of 100%
because locally generated `status=error` records are valid replay records. It
must not be confused with model structured-output success, which was 16/30.

These are diagnostic development observations. Because the registered
interface gate failed, none should be used as the final B1-vs-B0 comparison.

## Resource accounting

- Input tokens: 213,820
- Output tokens, including reasoning: 15,937
- Reasoning tokens: 8,595
- Total tokens: 229,757
- Aggregate measured latency: 213,390 ms

## Required next step

Do not repeat v1 unchanged. Prepare a versioned B1 amendment and validate it
locally before any further paid run. The amendment should address only systemic
development-interface failures, including:

1. make the calculator's flat program grammar, separators, references and
   table-row convention explicit, with valid and invalid examples;
2. decide whether the deterministic calculator should safely normalize common
   equivalent forms or intentionally reject them;
3. add safe diagnostics for invalid visible final output without retaining
   reasoning text or credentials;
4. reassess the model/tool turn limit using the aggregate v1 evidence rather
   than any individual answer.

Any rerun must use a new artifact stem, rerun the full registered 30-item set,
and receive separate authorization.

## Frozen artifact hashes

| Artifact | SHA-256 |
|---|---|
| Gold | `b6ac633d53f78e4ffd66e6507b6dfcaddf33eec70acd7e8e8cb98f19af757e40` |
| Predictions | `e88ab4f4c784593721c7420c8d8d632072b9c8365930b15ab63356c5e8e40ebf` |
| Evaluation report | `cb28610d326345a0b192d363e57d44189ee36d00fd5288f6592174196b12b356` |
| Replay log | `6e542ab34b8c44da3cc8787757c0edc7f2b77f81a30fdd83c534b3dff01b5591` |
