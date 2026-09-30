from __future__ import annotations

import unittest

from contractfin.heldout import (
    allocate_stratified_quotas,
    build_heldout_manifest,
    build_interleaved_schedule,
    build_stability_schedule,
    exact_mcnemar_power,
    split_selected_records,
)


def sample(sample_id: str, program: str) -> dict:
    return {
        "sample_id": sample_id,
        "dataset": "FinQA",
        "split": "test",
        "question": f"Question {sample_id}?",
        "documents": [{"document_id": sample_id, "table": [["value", "1"]]}],
        "gold_answer": "1",
        "gold_program": program,
        "gold_evidence": [{"id": "table_0"}],
        "metadata": {"raw_answer": "DO_NOT_COPY"},
        "schema_version": "1.0",
    }


class QuotaTests(unittest.TestCase):
    def test_allocates_minima_then_residual_proportionally(self) -> None:
        quotas = allocate_stratified_quotas(
            {"a": 10, "b": 30},
            sample_size=20,
            minimum_quotas={"a": 5},
        )
        self.assertEqual(sum(quotas.values()), 20)
        self.assertGreaterEqual(quotas["a"], 5)
        self.assertLessEqual(quotas["a"], 10)


class ManifestTests(unittest.TestCase):
    def test_manifest_and_split_are_deterministic_and_gold_isolated(self) -> None:
        rows = [sample(f"s{index}", "divide(10, 2)") for index in range(8)]
        manifest = build_heldout_manifest(
            rows,
            dataset_sha256="abc",
            sample_size=4,
            stability_size=2,
            minimum_quotas={},
            protocol_id="test-heldout",
        )
        reversed_manifest = build_heldout_manifest(
            reversed(rows),
            dataset_sha256="abc",
            sample_size=4,
            stability_size=2,
            minimum_quotas={},
            protocol_id="test-heldout",
        )
        ids = [item["sample_id"] for item in manifest["samples"]]
        self.assertEqual(ids, [item["sample_id"] for item in reversed_manifest["samples"]])
        inference, gold = split_selected_records(rows, manifest)
        self.assertEqual([item["sample_id"] for item in inference], ids)
        self.assertNotIn("gold_answer", inference[0])
        self.assertNotIn("metadata", inference[0])
        self.assertNotIn("question", gold[0])
        self.assertIn("documents", gold[0])

        schedule = build_interleaved_schedule(manifest)
        self.assertEqual(len(schedule), 8)
        for index in range(0, len(schedule), 2):
            self.assertEqual(schedule[index]["sample_id"], schedule[index + 1]["sample_id"])
            self.assertEqual({schedule[index]["system"], schedule[index + 1]["system"]}, {"B0", "B1"})
        self.assertEqual(
            [schedule[index]["system"] for index in range(0, len(schedule), 2)].count("B0"),
            2,
        )

        stability_schedule = build_stability_schedule(manifest)
        self.assertEqual(len(stability_schedule), 8)
        first = {
            (item["replicate"], item["sample_id"]): item["system"]
            for item in stability_schedule
            if item["within_pair_order"] == 1
        }
        for sample_id in manifest["stability_subset"]["sample_ids"]:
            self.assertNotEqual(first[(2, sample_id)], first[(3, sample_id)])


class PowerTests(unittest.TestCase):
    def test_exact_power_increases_materially_with_sample_size(self) -> None:
        small = exact_mcnemar_power(100, total_discordance=0.2, net_difference=0.1)
        large = exact_mcnemar_power(500, total_discordance=0.2, net_difference=0.1)
        self.assertGreater(large, small)
        self.assertGreater(large, 0.8)


if __name__ == "__main__":
    unittest.main()
