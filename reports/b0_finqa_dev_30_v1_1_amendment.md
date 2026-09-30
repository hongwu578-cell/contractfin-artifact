# B0 FinQA development-set protocol amendment v1.1

## Decision

The parent run is preserved as interface-diagnostic evidence. A full 30-item
rerun is proposed under protocol `contractfin-b0-finqa-dev30-v1.1`. The only
request-behavior change is:

| Parameter | Parent run | v1.1 |
|---|---:|---:|
| `max_output_tokens` | 1,024 | 8,192 |

DeepSeek documents that `max_output_tokens` includes both reasoning tokens and
visible output tokens, and that a response becomes `incomplete` when this limit
is reached. The current model supports an output ceiling substantially above
8,192 tokens. A maximum is an allowance rather than a required generation
length, so completed responses may stop earlier.

Official basis:

- [DeepSeek Responses API reference](https://api-docs.deepseek.com/api/create-response/)
- [DeepSeek Responses API guide](https://api-docs.deepseek.com/guides/responses_api/)
- [DeepSeek models and limits](https://api-docs.deepseek.com/quick_start/pricing/)

## Triggering evidence

- Parent protocol: `contractfin-b0-finqa-dev30-v1`
- Parent run: `b0-f8beac55-fd32-4358-bada-9c002a38bbc0`
- Successful structured responses: 14/30
- Failures: 16/30
- Failed responses ending at exactly 1,024 output tokens: 16/16
- Incomplete/no-output-text failures: 15
- Truncated invalid-JSON failures: 1

This pattern establishes a systemic interface ceiling. It does not justify
changing the prompt, selecting easier samples or counting the censored items as
semantic errors.

## Frozen factors

- Provider endpoint: `https://api.deepseek.com/responses`
- Requested model alias: `deepseek-flash`
- Prompt: `b0-direct-v1`, unchanged
- Structured-output schema: unchanged
- Reasoning and temperature: provider defaults, unchanged and not explicitly sent
- Sample manifest: unchanged, SHA-256
  `3afaa34852cdf799e1993952a6326d8b1ca6ead9a4798acb0d7ed9f889542ba3`
- Dataset SHA-256:
  `91237413e337148faf0ae58c06539d8c428fbf2f06ef84dc335cdd0616032739`
- All 30 sample IDs and execution order: unchanged
- Retries: zero
- Evaluator and metrics: unchanged

The rerun must cover all 30 registered items. Rerunning only the 16 failures
would create non-comparable, conditionally selected results.

## Instrumentation-only improvements

These changes do not alter the request seen by the model:

- log protocol ID and output ceiling;
- retain response status and incomplete reason without storing reasoning text;
- retain the provider-reported reasoning-token count;
- refuse to overwrite prior artifacts.

## Acceptance gate

- exactly 30 calls, one per registered sample;
- at least 29/30 successfully parsed structured responses;
- zero failures attributable to `max_output_tokens`;
- 100% log completeness;
- exact sample-ID and execution-order match;
- accuracy is observed but is not an interface-gate criterion.

If this gate fails, preserve the run and diagnose the new systemic failure. Do
not tune against individual answers.

## Planned outputs

- `reports/b0_deepseek_preregistered30_v1_1_gold.jsonl`
- `reports/b0_deepseek_preregistered30_v1_1_predictions.jsonl`
- `reports/b0_deepseek_preregistered30_v1_1_report.json`
- `logs/b0_deepseek_preregistered30_v1_1.jsonl`

No paid API call is included in preparation of this amendment. Execution
requires separate user authorization for 30 DeepSeek requests.
