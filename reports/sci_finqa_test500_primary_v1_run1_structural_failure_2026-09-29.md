# SCI held-out primary run 1: structural failure record

Date: 2026-09-29  
Protocol: `contractfin-sci-finqa-test500-v1`  
Run ID: `sci-heldout-da1c5495-3f11-4021-8c6a-bfc2b154315e`  
Artifact stem: `sci_finqa_test500_primary_v1`

## Decision

**Structurally invalid; do not evaluate or unblind.**

All 1,000 scheduled tasks were logged, but every task failed before provider contact with `network_error/gaierror`. The aggregate runtime was 68 ms, model-call traces were zero, token usage was zero, and the inference summary records `gold_loaded=false`. This is an execution-environment failure rather than an observed B0 or B1 model outcome.

## Preserved evidence

- Task records: 1,000.
- B0 error records: 500/500.
- B1 error records: 500/500.
- Completed provider model calls: 0.
- Total tokens: 0.
- B0 prediction SHA-256: `6279c97166cc4d8bd77940c0116fb54fc1d369483c760aec20898739d79641e1`.
- B1 prediction SHA-256: `c9fb33aec88d587ad48aa52f610e642c24d687d4b976795b3c3047035a812b12`.
- Gold artifact loaded: no.
- Evaluation performed: no.

No failed artifact is deleted or overwritten. The full schedule may be rerun only under the dated amendment `config/authorizations/sci_heldout_primary_rerun1_amendment_2026-09-29.json`, using a new artifact stem and an execution environment with network access. Selective item reruns remain prohibited.
