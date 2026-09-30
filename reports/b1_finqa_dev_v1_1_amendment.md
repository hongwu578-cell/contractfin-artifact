# B1 FinQA development protocol amendment v1.1

## Decision

B1-v1.1 is prepared locally but has not made any API request. It addresses the
systemic interaction failures observed in B1-v1 while preserving the same
single-agent research boundary, data, model request, retriever, deterministic
operations, output schema, evaluator and cumulative output budget.

Because this amendment changes several coupled interface elements, a new
two-item live gate must pass before any 30-item rerun.

## Triggering evidence

Run `b1-81337a19-ea61-4f81-badc-781b2032db51` produced only 16/30 structured
completions. It recorded 21 failed calculator calls, 19 samples reaching the
fourth-turn limit, and 14 invalid final JSON responses. All provider calls
completed, so the problem was the local model-tool contract rather than API
availability, transport timeout or output ceiling.

## Versioned changes

### Structured calculator steps

The exposed `calculate_finqa` schema no longer accepts a free-form program
string. It accepts 1–8 steps, each containing one enumerated operation and
exactly two arguments. Earlier values are referenced with `#0`, `#1`, and so
on. Table operations use the actual row name and `none`.

The semantic operation set is unchanged. The revision changes representation,
not mathematical capability. The tool returns a canonical FinQA program that
the agent is instructed to copy into its final result. Legacy free-form input
remains implemented only for replay of frozen v1 tests and is not exposed to
the v1.1 model.

### Explicit interaction rules

The prompt now states the structured-step grammar, prohibits nested operations,
infix arithmetic, assignments and semicolons, distinguishes table evidence
labels from row names, limits unnecessary repeated searches, and requires one
raw JSON object without Markdown fences or commentary.

### Bounded turn expansion

The model-call limit increases from 4 to 6 and the tool-call limit from 6 to 8.
The cumulative output allowance remains 32,768 tokens per sample, so this does
not increase the per-sample output-token ceiling. It increases the possible
number of paid model requests from 4 to 6 per sample.

### Failure observability

If final output is invalid, the log may retain at most 8,192 characters of
visible final answer text, plus its length and SHA-256. Reasoning text and
credentials are never retained. This is diagnostic-only and does not affect
model behavior.

## Local validation

- 47 unit tests passed;
- bytecode compilation passed;
- all 883 FinQA development gold programs were converted through the new
  structured tool interface with 100% parse rate, tool success and execution
  accuracy;
- a mocked registered-30 tool loop completed 30/30 with zero tool failures and
  100% log completeness;
- the original v1 prompt and tool definitions remain available in code and
  reproduce their frozen hashes;
- no live API request was made.

The calculator audit is `reports/b1_calculator_v1_1_audit.json`.

## Required live interface gate

Two development items outside the registered30 set are frozen:

1. a four-step arithmetic item that exercises `#0` references;
2. a table-average item that exercises the row-name convention.

```bash
PYTHONPATH=src python3 scripts/run_b1.py \
  --provider deepseek \
  --model deepseek-flash \
  --sample-manifest config/b1_finqa_dev_v1_1_interface_manifest.json \
  --protocol-id contractfin-b1-finqa-dev2-interface-v1.1 \
  --total-output-budget 32768 \
  --max-model-calls 6 \
  --max-tool-calls 8 \
  --request-timeout-seconds 300 \
  --artifact-stem b1_deepseek_interface2_v1_1
```

This gate may make at most 12 paid model calls. It requires 2/2 structured
completions, both tools on both samples, effective `top_k=12`, zero tool and
JSON failures, no timeout or ceiling failure, and complete logs. Accuracy is
observed but is not an interface criterion.

## Conditional registered30 rerun

Only after the two-item gate passes and a second authorization is given may the
full registered set be rerun under `contractfin-b1-finqa-dev30-v1.1`. The rerun
may make at most 180 paid model calls and 240 local tool calls. It must use a
new artifact stem and the exact original 30 sample IDs and order.

The machine-readable amendment is
`config/b1_finqa_dev_v1_1_amendment.json`.
