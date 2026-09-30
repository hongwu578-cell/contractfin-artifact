# B2 FinQA development protocol v1

## Decision

B2 is frozen as a **four-role, fixed-topology multi-agent system**:

`Task Contract Agent → Evidence Agent → Solver Agent → Verifier Agent → deterministic final gate`

The controller is deterministic and does not call a model. All four roles use
the same requested model, `deepseek-flash`, but each role begins with a fresh
conversation and receives only a validated structured artifact from the prior
stage. No chain-of-thought or hidden reasoning is shared or retained.

This protocol has been implemented and validated locally. **No live API call
was made.**

## Research boundary

B0 measured direct generation. B1 added retrieval and deterministic calculation
to one agent. B2 is intended to measure the next increment: whether explicit
role separation, a task contract, and an independent verifier change quality
after tool access is already available.

The registered 30-item FinQA development set has already supported B0/B1
development. Consequently, B2 results on these 30 items will be descriptive
engineering evidence only. They cannot support final performance, statistical
significance, or causal claims. A separate held-out test preregistration will be
required after B2 is frozen.

## Architecture and permissions

| Role | Model calls | Allowed tool | Output | Key restriction |
|---|---:|---|---|---|
| Task Contract Agent | 1 | none | Structured task contract | Cannot search, calculate, or answer |
| Evidence Agent | 2 | `search_document` once | Evidence packet | Exactly one explicit `top_k=12` search; cannot calculate |
| Solver Agent | 2 | `calculate_finqa` once | Candidate prediction | Cannot search; evidence must come from the packet |
| Verifier Agent | 1 | none | Accept/human-review verdict | Cannot rewrite the candidate or call tools |

Full B2 therefore has a hard ceiling of six model calls and two tool calls per
sample. This matches B1-v1.2's six-model-call ceiling and cumulative 32,768
output-token budget. Actual calls, tokens, and latency will also be reported so
quality improvements cannot be discussed without their cost.

### Conflict resolution

The verifier never generates a replacement answer. A candidate is returned
only when:

1. the task contract, evidence packet, candidate schema, evidence membership,
   and canonical executed program all pass deterministic checks; and
2. the verifier returns `accept` with all four checks true.

If either condition fails, the controller clears the answer and changes the
status to `human_review`. There is no repair call or automatic retry. This
prevents a verifier from introducing unsearched evidence or an unexecuted
program.

## Frozen variants and ablations

| Variant | Removed component | Maximum calls/sample | Registered30 ceiling |
|---|---|---:|---:|
| Full B2 | none | 6 | 180 |
| B2 minus task contract | Task Contract Agent | 5 | 150 |
| B2 minus verifier | Verifier Agent | 5 | 150 |

Frozen B1-v1.2 is the single-agent comparator and will not be rerun. The two
B2 ablations isolate the contribution of the contract and verifier. Each live
run requires a separate authorization; approval for one run does not authorize
the others.

## Measures

Primary descriptive outcomes are final-answer accuracy, execution accuracy,
and evidence macro-F1. Secondary outcomes are answer and execution coverage,
program accuracy, human-review rate, unit/scale errors, unsupported claims, and
schema validity. Efficiency outcomes include model/tool calls, input/output/
reasoning/total tokens, and latency.

Development differences will be reported as counts, rates, and absolute
differences only. No development-set p-values or confidence intervals will be
presented.

## Local validation completed

- 56 unit tests passed;
- Python bytecode compilation passed;
- the full four-role pipeline completed a mocked replay of all 30 registered
  samples;
- 180 mocked model turns and 60 local tool calls completed;
- task-contract, evidence, solver, verifier, conservative rejection, and both
  ablation code paths were exercised;
- failed samples: 0;
- failed tool calls: 0;
- replay-log completeness: 100%;
- live API calls: 0;
- model request payloads containing `gold_answer`, `gold_program`, or
  `gold_evidence` fields: 0.

The mocked audit uses gold programs and answers only to synthesize local oracle
responses. Its scores are not research performance and its temporary
predictions are discarded. The audit record is
`reports/b2_local_orchestration_audit.json`.

## Three-item live interface gate

Before any registered30 B2 or ablation run, the full system must pass a
three-item interface gate. The three items do not overlap the registered30 set
or earlier interface gates. They cover five-step arithmetic, table aggregation,
and comparison.

```bash
PYTHONPATH=src python3 scripts/run_b2.py \
  --provider deepseek \
  --model deepseek-flash \
  --variant full \
  --sample-manifest config/b2_finqa_dev_v1_interface_manifest.json \
  --protocol-id contractfin-b2-finqa-dev3-interface-v1 \
  --total-output-budget 32768 \
  --max-model-calls 6 \
  --max-tool-calls 2 \
  --request-timeout-seconds 300 \
  --artifact-stem b2_deepseek_full_interface3_v1
```

The command can make at most 18 paid model calls and six local tool calls. It
passes only when:

- all three samples produce structured pipeline outputs;
- all three task contracts, evidence packets, solver candidates, and verifier
  verdicts are valid;
- all three samples use one explicit `top_k=12` search and one successful
  deterministic calculation;
- there are no tool, schema, ceiling, or transport failures;
- log completeness is 100%; and
- sample identity and order exactly match the frozen interface manifest.

Answer accuracy and the human-review rate are observed but are not interface
criteria.

## Execution sequence and authorization boundary

1. Run the three-item full-B2 interface gate: maximum 18 model calls.
2. Only if it passes, separately authorize the full-B2 registered30 run:
   maximum 180 calls.
3. Only after the full run, separately authorize the no-contract ablation:
   maximum 150 calls.
4. Separately authorize the no-verifier ablation: maximum 150 calls.
5. Freeze B2, then design and preregister a held-out FinQA test evaluation.

No step after the local validation is currently authorized.

## Next exact reply

To authorize only the three-item interface gate, reply exactly:

> 同意执行B2-v1三题真实接口测试，最多18次模型调用。

The words “继续” or “开始下一阶段” alone do not authorize a paid API call.

## Frozen files

- Machine-readable protocol: `config/b2_finqa_dev_v1_protocol.json`
- Three-item manifest: `config/b2_finqa_dev_v1_interface_manifest.json`
- B2 implementation: `src/contractfin/b2.py`
- CLI runner: `scripts/run_b2.py`
- Local audit: `reports/b2_local_orchestration_audit.json`
