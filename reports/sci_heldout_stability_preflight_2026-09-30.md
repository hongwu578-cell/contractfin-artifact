# SCI held-out stability experiment preflight

- Status: **PASS — live execution not authorized**
- Protocol: `contractfin-sci-finqa-test500-v1`
- Frozen runtime SHA-256: `c839a885a7b1fb21af8e1fb638f3e2e8ea2337524e7f94920ffdf4b464c9e077`
- Frozen schedule SHA-256: `e9988a8a45fb11d78f08f39a76a8142492df63bae643bca92cdaca72560428b4`
- Freeze-lock SHA-256: `090d7b4e71be4cbdf9fe41e9dd614953a2f7fe56de7a28c4d3b470f5f6414b40`
- Model API calls during preflight: **0**

## Registered scope

- Stability subset: 100 primary-run items.
- Additional replicates: R2 and R3.
- Tasks: 400 system-item runs (B0=200; B1=200).
- Per replicate: 100 B0 and 100 B1 tasks.
- First-system balance: 50 B0-first and 50 B1-first in each replicate.
- First system flips for every item between R2 and R3.
- Expected provider model calls: 827.
- Hard authorization ceiling: 1,400 provider model calls.
- Primary and stability observations remain separate; additional runs are not pooled into the primary McNemar test.

## Checks completed

- Runtime and schedule hashes match their frozen declarations.
- All 400 schedule records are present and balanced.
- All intended output paths are clear.
- No-network dry-run passed with three representative payloads and zero API calls.
- All 62 unit tests passed.
- The 34-file freeze lock passed with no hash mismatch.
- `DEEPSEEK_API_KEY` is available to an interactive zsh session; its value was not displayed.

## Execution boundary

The following are prohibited: automatic retries, semantic retries, selected-item reruns, sample substitution, prompt changes, runtime changes, and pooling the stability runs into the primary test.

Live execution requires a separate explicit authorization. Use exactly:

> 同意执行SCI held-out稳定性实验100题两轮附加重复，共400个系统任务，最多1400次模型调用。

The current template is `config/authorizations/sci_heldout_stability_authorization_2026-09-30.template.json` and remains inactive (`authorized=false`).
