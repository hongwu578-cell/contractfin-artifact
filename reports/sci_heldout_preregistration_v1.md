# ContractFin SCI held-out preregistration v1

- Protocol: `contractfin-sci-finqa-test500-v1`
- Date: `2026-09-29`
- Current live API authorization: **0 calls**
- Confirmatory comparison: B1 tool-augmented single agent versus B0 direct LLM
- B2 status: exploratory development failure analysis only

## Research claim

Does deterministic tool augmentation improve paired held-out financial numerical reasoning performance over direct generation under matched provider, model alias, item set, and output ceiling?

The primary test is two-sided even though the development evidence motivates a directional expectation in favor of B1.

## Sample and isolation

A deterministic, minimum-quota stratified sample of 500 items is frozen from the 1,147-item FinQA test pool. The inference JSONL contains only sample identity, question, documents, and schema metadata. The separate gold evaluation JSONL contains reference labels plus the table context required to execute predicted programs. Neither inference runtime contains a gold key or path.

A 100-item deterministic subset is frozen for two additional stability replicates; those replicates are not pooled into the primary test. Within each additional replicate, first-system order is balanced 50:50, and it flips for every item between replicates 2 and 3.

## Primary analysis

The primary outcome is item-level final-answer correctness under intention-to-test scoring. Missing, abstained, and error outputs are incorrect. The primary inferential test is the two-sided exact conditional McNemar test at alpha 0.05. The paired accuracy difference receives a 95% paired bootstrap interval using 10,000 resamples and seed 20260929.

## Secondary and resource analyses

Program ITT correctness, execution ITT correctness, item-level evidence F1, and coverage form one Holm-corrected secondary family. The three binary outcomes use exact McNemar tests; evidence F1 uses a paired 100,000-draw sign-flip test with seed 20260930. Model calls, tool calls, tokens, latency, and resources per correct answer are descriptive cost outcomes. Because rare strata are deliberately oversampled, the preregistered unweighted estimand is complemented by a FinQA-test-prevalence-weighted secondary estimate.

## Failure and stopping rules

No automatic retry, semantic retry, item substitution, or item-specific tuning is allowed. There is no sequential significance testing. Provider/network failures are distinguished from schema-invalid or semantically wrong model outputs. If infrastructure failures or returned-model drift exceed the frozen threshold, analysis stops before unblinding until a dated amendment is written.

## Local verification

All `31` leakage, identity, hash, schedule, and count checks passed with `0` API calls.

The future live command is intentionally blocked and requires a separate dated authorization file bound to the frozen runtime hash; the frozen runtime itself is never edited.
