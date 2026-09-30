# B0 FinQA development-set protocol amendment v1.2

## Decision

A full 30-item rerun is proposed under protocol
`contractfin-b0-finqa-dev30-v1.2`. The only change to the model request body is:

| Request parameter | v1.1 | v1.2 |
|---|---:|---:|
| `max_output_tokens` | 8,192 | 32,768 |

The client-only request timeout changes from 120 to 300 seconds. This timeout is
not sent to DeepSeek and does not affect model generation; it only prevents the
local client from abandoning a legitimately longer response.

## Triggering evidence

- Parent run: `b0-f43ed65b-2964-4c73-b242-9615e49f494d`
- Parent completions: 29/30
- Sole failure: `finqa:dev:CB/2010/page_200.pdf-4`
- Failure status: `incomplete`
- Failure reason: `max_output_tokens`
- Failure output tokens: 8,192
- Failure reasoning tokens: 8,192
- Visible answer: none

The same registered item reached both the 1,024-token v1 ceiling and the
8,192-token v1.1 ceiling. In v1.1, the largest completed response used 4,535
tokens and the other 29 items completed. The 32,768 allowance targets this
remaining recurrent long-tail generation without changing the prompt or model
reasoning mode.

The allowance is not a generation target: normally completed responses stop
earlier. The theoretical worst case is 983,040 output tokens if every call were
to consume the entire ceiling, although prior observations make that outcome
unlikely.

Official basis:

- [DeepSeek Responses API reference](https://api-docs.deepseek.com/api/create-response/)
- [DeepSeek Responses API guide](https://api-docs.deepseek.com/guides/responses_api/)
- [DeepSeek models and limits](https://api-docs.deepseek.com/quick_start/pricing/)

## Frozen factors

- provider endpoint and requested `deepseek-flash` alias;
- `b0-direct-v1` prompt and structured-output schema;
- provider-default reasoning and temperature, with neither explicitly sent;
- all 30 sample IDs and their execution order;
- sample-manifest SHA-256
  `3afaa34852cdf799e1993952a6326d8b1ca6ead9a4798acb0d7ed9f889542ba3`;
- normalized-data SHA-256
  `91237413e337148faf0ae58c06539d8c428fbf2f06ef84dc335cdd0616032739`;
- zero retries;
- evaluator, metrics and response diagnostics.

The full registered set must be rerun. Rerunning only the known failure would
not produce a comparable B0 result.

## Acceptance gate

- exactly 30 attempted calls and no retry;
- 30/30 successfully parsed structured responses;
- zero `max_output_tokens` failures;
- zero client transport timeouts;
- 100% log completeness;
- exact registered sample identity and order;
- accuracy observed but not used as an interface-gate criterion.

The 30/30 criterion is intentionally strict. It may not be relaxed after seeing
the result.

## Planned outputs

- `reports/b0_deepseek_preregistered30_v1_2_gold.jsonl`
- `reports/b0_deepseek_preregistered30_v1_2_predictions.jsonl`
- `reports/b0_deepseek_preregistered30_v1_2_report.json`
- `logs/b0_deepseek_preregistered30_v1_2.jsonl`

No API call is included in preparation of this amendment. Execution requires
separate authorization for 30 paid DeepSeek requests.
