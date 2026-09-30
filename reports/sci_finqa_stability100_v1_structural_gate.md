# SCI held-out stability structural gate report

- Generated at: `2026-09-29T21:04:00.591853+00:00`
- Artifact stem: `sci_finqa_stability100_v1`
- Run ID: `sci-heldout-65790ede-9ae0-426c-8216-18af915d643a`
- Gold loaded: **false**
- Structural gate: **PASS**
- Unblinding permitted: **true**

## Counts and integrity

- Logged tasks: 400 / 400
- B0_R2: 100 predictions (duplicates: 0)
- B1_R2: 100 predictions (duplicates: 0)
- B0_R3: 100 predictions (duplicates: 0)
- B1_R3: 100 predictions (duplicates: 0)
- First-system balance R2: B0=50, B1=50
- First-system balance R3: B0=50, B1=50
- Cross-replicate first-system flips: 100 / 100
- Returned-model mismatches: 0 / 200 (0.00%)

## Failures

- B0: system=0, infrastructure=0
- B1: system=3, infrastructure=0
- Infrastructure rates: B0=0.00%, B1=0.00%
- Absolute infrastructure-rate difference: 0.00%

## Resources

- Provider model calls: 842 / 1400
- Total tokens: 2344492

## Frozen prediction hashes

- B0_R2: `293a9a19d81bcbdedeb156ac0bf82ed0e459d7f2a26085c8c146287ca25c3062`
- B1_R2: `1188509a4d64a2c5c21378517d2bc9dc2ef7049985c256f7d7a882091d3b065b`
- B0_R3: `1f04e4288f48bd7f249849116e8b5f1f5807eb7da017c37629f3cd77795e3ee6`
- B1_R3: `9dae69d96886137149c74a59869581988adc65cc2a477e38fe88195642d5fa5f`

## Checks

- PASS — `task_count_is_400`
- PASS — `schedule_and_log_are_identical_in_order`
- PASS — `schedule_sequences_are_1_through_400`
- PASS — `single_run_id`
- PASS — `protocol_id_matches_runtime`
- PASS — `runtime_hash_matches_all_records`
- PASS — `inference_summary_is_complete`
- PASS — `gold_was_not_loaded`
- PASS — `each_group_has_100_unique_predictions`
- PASS — `prediction_sample_id_sets_match_across_groups`
- PASS — `prediction_files_match_logged_outputs`
- PASS — `prediction_hashes_match_inference_summary`
- PASS — `first_system_balance_is_50_50_per_replicate`
- PASS — `first_system_order_flips_across_replicates`
- PASS — `infrastructure_rate_each_system_at_most_2_percent`
- PASS — `infrastructure_rate_difference_at_most_1_point`
- PASS — `returned_model_mismatch_rate_at_most_1_percent`
- PASS — `every_pair_has_returned_model_identifiers`
- PASS — `provider_model_calls_within_authorized_ceiling`

No gold file was opened or evaluated by this audit.
