# SCI held-out primary-run final local preflight

Date: 2026-09-29  
Protocol: `contractfin-sci-finqa-test500-v1`  
Scope checked: primary B0/B1 paired run only  
Live model API calls during preflight: **0**

## Decision

**PASS — ready for a separate explicit live-run authorization.**

The frozen runtime, inference artifact, and 1,000-task schedule passed all local checks. The inactive authorization template cannot start a live run. Stability replicates remain outside the proposed authorization.

## Check results

| Check | Result | Evidence |
|---|---|---|
| Frozen file integrity | Pass | 34 locked files; zero hash mismatches; lock SHA-256 `090d7b4e71be4cbdf9fe41e9dd614953a2f7fe56de7a28c4d3b470f5f6414b40` |
| Unit and integration tests | Pass | 62/62 tests passed with `PYTHONPATH=src` |
| No-network runtime dry-run | Pass | B0 and B1 completed; three payloads checked; API calls `0` |
| Gold leakage audit | Pass | 31 local audit checks passed; no forbidden inference or payload keys |
| Inference and schedule counts | Pass | 500 inference records and 1,000 scheduled tasks |
| Schedule structure | Pass | Unique, complete, strictly interleaved, and first-system order balanced 250:250 |
| Output collision check | Pass | No primary task log, summary, or prediction artifact currently exists |
| Output-directory access | Pass | `logs/`, `reports/`, and `config/` are writable |
| Resume behavior | Pass by inspection and frozen tests | Completed task IDs are skipped from the append-only task log; no automatic or semantic retry is enabled |
| Live-run safety gate | Pass | A live invocation without an authorization amendment exited with `PermissionError` before any provider call |
| DeepSeek key presence | Conditional pass | Absent from the current non-interactive shell; present after interactive `zsh` loads `~/.zshrc` |
| Disk capacity | Pass with caution | Approximately 11.4 GiB available; filesystem is 95% utilized |
| File-descriptor limit | Pass | Soft limit 1,048,575 |
| Existing authorization | Correctly absent | Template has `authorized=false`; current authorized model-call count is zero |

## Frozen execution scope

- Systems: B0 direct LLM and B1 tool-augmented single agent.
- Items: 500 registered FinQA test items.
- Scheduled system tasks: 1,000.
- Expected model calls: 2,067.
- Hard model-call ceiling: 3,500.
- Automatic retries: 0.
- Semantic retries: 0.
- Stability runs: not authorized.
- B2 runs: not authorized.
- Evaluation: deferred until prediction artifacts are complete, hashed, and structurally accepted.

## Environment requirement for the later live run

The desktop process does not currently inherit `DEEPSEEK_API_KEY`, while an interactive `zsh` does. The authorized execution must therefore load `~/.zshrc` in the same shell immediately before the frozen runner starts. The key must remain an environment variable and must never be written to an authorization file, report, task log, or command argument.

## Operational cautions

1. The filesystem has adequate free space for the expected logs, but total utilization is already 95%. Do not start unrelated large downloads or builds during the run.
2. Do not delete or edit a partial task log after interruption. The frozen runner resumes only by skipping task IDs already present in that log.
3. Network/provider failures are recorded as ITT failures; they are not retried. If the preregistered infrastructure-failure threshold is exceeded, stop before unblinding and use a dated full-run amendment rather than selectively rerunning items.
4. Do not open the gold evaluation artifact or run evaluation while inference is active.

## Inactive authorization template

`config/authorizations/sci_heldout_primary_authorization_2026-09-29.template.json`

Required exact reply for activation:

> 同意执行SCI held-out主实验B0/B1配对500题测试，最多3500次模型调用。

Receiving that sentence authorizes creation of a separate active authorization file and execution of the primary schedule only. It does not authorize the stability experiment.
