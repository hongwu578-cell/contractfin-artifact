# B1 FinQA development protocol v1

## Decision

B1 is implemented as a **single tool-augmented agent**. It may call the same
document retriever and deterministic FinQA calculator that later B2 and
ContractFin systems will receive. It does not receive a task contract, multiple
roles, inter-agent conflict handling, or a model-visible final verification
gate. This preserves B1's research purpose: measuring tool-access gain before
multi-agent coordination is introduced.

No real API call was made while preparing this protocol.

## Frozen configuration

| Item | Frozen value |
|---|---|
| Provider/model request | `deepseek/deepseek-flash` |
| Prompt | `b1-tool-single-agent-v1` |
| Tools | `search_document`, `calculate_finqa` |
| First search | `top_k=12` |
| Output budget | 32,768 tokens cumulatively per sample |
| Model-call limit | 4 per sample |
| Tool-call limit | 6 per sample |
| Client timeout | 300 seconds per model call |
| Retry policy | zero automatic retries |
| Reasoning/temperature | provider defaults; neither field is sent |
| Response storage | disabled |

The output budget is cumulative across all model turns for a sample. The last
allowed model turn has tools disabled and must return the same structured
prediction schema used by B0. Reasoning items returned by the Responses API are
passed back during the stateless tool loop as required, but reasoning text is
not retained in the research logs.

The implementation follows DeepSeek's documented Responses API function-call
flow: receive `function_call`, execute the local tool, append
`function_call_output`, and resend the full history. References:

- [Responses API reference](https://api-docs.deepseek.com/api/create-response/)
- [Responses API guide](https://api-docs.deepseek.com/guides/responses_api/)
- [Tool Calls guide](https://api-docs.deepseek.com/guides/tool_calls/)

## Tool boundary

`search_document` searches only the current sample's allowed document. It
returns official FinQA evidence labels and cannot read gold answers, programs,
or evidence. `calculate_finqa` executes only the program supplied by the model;
it likewise receives no gold result. Every call records arguments, output,
latency, errors and model-turn association for replay.

The development retriever audit passed. On the frozen registered 30-item set,
`top_k=12` achieved 43/44 evidence-item recall (97.73%) and full gold-evidence
coverage on 29/30 questions (96.67%). Gold evidence was used only for this
aggregate development audit and is never exposed at runtime. The audit is
recorded in `reports/b1_retriever_audit.json`.

## Two-level execution gate

### Gate 1: one-item live interface test

The first normalized FinQA development item,
`finqa:dev:V/2008/page_17.pdf-1`, is reused from the B0 interface test. It is
excluded from the registered 30-item set. Its arithmetic form exercises both
retrieval and calculation.

```bash
PYTHONPATH=src python3 scripts/run_b1.py \
  --provider deepseek \
  --model deepseek-flash \
  --limit 1 \
  --protocol-id contractfin-b1-finqa-dev1-interface-v1 \
  --total-output-budget 32768 \
  --max-model-calls 4 \
  --max-tool-calls 6 \
  --request-timeout-seconds 300 \
  --artifact-stem b1_deepseek_interface1_v1
```

This test makes at most four paid model calls and at most six local tool calls.
It passes only if the sample returns a valid structured result, uses both tools,
uses effective `top_k=12`, has no tool/ceiling/timeout failure and records a
complete log. Answer correctness is observed but is not an interface criterion.

### Gate 2: registered 30-item development run

Only after Gate 1 passes and a separate authorization is given may the frozen
30-item run execute:

```bash
PYTHONPATH=src python3 scripts/run_b1.py \
  --provider deepseek \
  --model deepseek-flash \
  --sample-manifest config/b0_finqa_dev_30_manifest.json \
  --protocol-id contractfin-b1-finqa-dev30-v1 \
  --total-output-budget 32768 \
  --max-model-calls 4 \
  --max-tool-calls 6 \
  --request-timeout-seconds 300 \
  --artifact-stem b1_deepseek_preregistered30_v1
```

The run can make up to 120 paid model calls (30 samples times four turns) and
180 local tool calls. Acceptance requires 30/30 structured completions, both
tools used on all 30 samples, effective `top_k=12` on all samples, zero tool,
ceiling and timeout failures, complete logs, and an exact sample/order match.
Accuracy remains an outcome, not an interface gate.

## B0 evidence-identifier correction

During B1 retriever validation, a systemic B0 prompt-label mismatch was found:
the official FinQA labels concatenate `pre_text` and `post_text` as `text_n`,
whereas the executed B0 prompt displayed `pre_n` and `post_n`. The 30 original
B0 predictions and report remain immutable. A deterministic identifier-only
migration changed 12 evidence labels across 11 samples, without another model
call.

Final-answer accuracy, program accuracy and execution accuracy are unchanged.
Corrected evidence macro-F1 is 0.9211 rather than the original misaligned
0.6411. The complete before/after map and hashes are in
`reports/b0_deepseek_preregistered30_v1_2_evidence_ids_v2_migration.json`.
Future runs expose official `text_n` labels directly.

## Local verification completed

- 44 unit tests passed;
- Python bytecode compilation passed;
- a 30-item mocked tool-loop replay completed 30/30 samples, with 90 simulated
  model turns, 60 tool calls and 100% log completeness;
- no live API request was made.

The machine-readable frozen protocol is
`config/b1_finqa_dev_v1_protocol.json`.
