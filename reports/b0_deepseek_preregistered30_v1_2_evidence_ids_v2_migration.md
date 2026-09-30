# B0 v1.2 FinQA evidence-identifier correction

This is a deterministic scoring correction, not a model rerun and not a prompt
tuning iteration.

The executed B0 prompt displayed narrative evidence as `pre_n` and `post_n`,
while normalized FinQA gold evidence uses one merged sequence named `text_n`:

- `pre_i` maps to `text_i`;
- `post_j` maps to `text_(number_of_pre_text_items + j)`;
- `table_i` is unchanged.

The original B0 v1.2 artifacts remain unchanged. A derived prediction file and
report were created under new names. The migration changed 12 evidence IDs in
11 of 30 predictions. It did not change answers, programs, statuses or units.

| Metric | Original scoring | Corrected scoring |
|---|---:|---:|
| Final-answer accuracy | 0.4000 | 0.4000 |
| Exact program accuracy | 0.1111 | 0.1111 |
| Execution accuracy | 0.1852 | 0.1852 |
| Evidence macro-precision | 0.6278 | 0.9056 |
| Evidence macro-recall | 0.6667 | 0.9500 |
| Evidence macro-F1 | 0.6411 | 0.9211 |

The authoritative audit, complete per-sample before/after mapping and file
hashes are stored in
`reports/b0_deepseek_preregistered30_v1_2_evidence_ids_v2_migration.json`.
