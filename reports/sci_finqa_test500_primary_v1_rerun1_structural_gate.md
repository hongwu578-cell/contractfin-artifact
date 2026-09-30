# SCI held-out primary structural gate report

- Generated at: `2026-09-29T13:30:57.835434+00:00`
- Artifact stem: `sci_finqa_test500_primary_v1_rerun1`
- Run ID: `sci-heldout-9d2c37d5-bc3e-473f-b8af-7630be75e31e`
- Gold loaded: **false**
- Structural gate: **PASS**
- Unblinding permitted: **true**

## Counts and integrity

- Logged tasks: 1000 / 1000
- B0 predictions: 500 (duplicates: 0)
- B1 predictions: 500 (duplicates: 0)
- First-system balance: B0=250, B1=250
- Within-pair returned-model mismatches: 0 / 500 (0.00%)

## Failures

- B0: system=0, infrastructure=0
- B1: system=7, infrastructure=0
- Infrastructure rates: B0=0.00%, B1=0.00%
- Absolute infrastructure-rate difference: 0.00%

## Resources

- Completed provider model calls: 2110 / 3500
- Total tokens: 5460000

## Frozen prediction hashes

- B0: `ab9bcf0252ccee773e7d9c3a6b938892c91788a3a057422f93fb954be554eed3`
- B1: `bee83fe075fedfdf3ee6a06d529cef3dfc8f5316837615ea0b06a3cf6de10cee`

## Checks

- PASS — `task_count_is_1000`
- PASS — `schedule_and_log_are_identical_in_order`
- PASS — `schedule_sequences_are_1_through_1000`
- PASS — `single_run_id`
- PASS — `protocol_id_matches_runtime`
- PASS — `runtime_hash_matches_all_records`
- PASS — `inference_summary_is_complete`
- PASS — `gold_was_not_loaded`
- PASS — `B0_has_500_unique_predictions`
- PASS — `B1_has_500_unique_predictions`
- PASS — `prediction_sample_id_sets_match`
- PASS — `prediction_files_match_logged_outputs`
- PASS — `prediction_hashes_match_inference_summary`
- PASS — `first_system_balance_is_250_250`
- PASS — `infrastructure_rate_each_system_at_most_2_percent`
- PASS — `infrastructure_rate_difference_at_most_1_point`
- PASS — `returned_model_mismatch_rate_at_most_1_percent`
- PASS — `every_pair_has_returned_model_identifiers`
- PASS — `completed_model_calls_within_authorized_ceiling`

No gold file was opened or evaluated by this audit.
