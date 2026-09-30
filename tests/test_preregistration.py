from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from contractfin.preregistration import (
    build_preregistration_manifest,
    classify_operations,
    load_preregistered_samples,
)
from contractfin.utils import sha256_file, write_json, write_jsonl


def sample(sample_id: str, program: str) -> dict:
    return {
        "sample_id": sample_id,
        "dataset": "FinQA",
        "split": "dev",
        "question": f"Question for {sample_id}?",
        "documents": [{"document_id": sample_id, "table": []}],
        "gold_answer": "1",
        "gold_program": program,
        "gold_evidence": [{"id": "table_1"}],
    }


class ClassificationTests(unittest.TestCase):
    def test_assigns_exclusive_coverage_strata(self) -> None:
        self.assertEqual(classify_operations(("divide",)), "single_divide")
        self.assertEqual(classify_operations(("subtract", "divide")), "multi_2_step")
        self.assertEqual(classify_operations(("table_average",)), "table_average")
        self.assertEqual(
            classify_operations(("table_average", "table_max", "subtract")),
            "table_average",
        )
        self.assertEqual(classify_operations(("divide", "exp", "multiply")), "contains_exp")
        self.assertEqual(classify_operations(("subtract", "greater")), "comparison")


class ManifestTests(unittest.TestCase):
    def test_selection_is_deterministic_and_independent_of_input_order(self) -> None:
        rows = [sample(f"s{index}", "divide(10, 2)") for index in range(5)]
        first = build_preregistration_manifest(
            rows,
            dataset_sha256="abc",
            quotas={"single_divide": 3},
            exclusions={},
            protocol_id="test-protocol",
        )
        second = build_preregistration_manifest(
            reversed(rows),
            dataset_sha256="abc",
            quotas={"single_divide": 3},
            exclusions={},
            protocol_id="test-protocol",
        )
        self.assertEqual(
            [item["sample_id"] for item in first["samples"]],
            [item["sample_id"] for item in second["samples"]],
        )
        self.assertEqual(len(first["samples"]), 3)

    def test_loader_enforces_dataset_hash_and_run_order(self) -> None:
        rows = [sample("s1", "divide(10, 2)"), sample("s2", "divide(8, 2)")]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset_path = root / "dev.jsonl"
            manifest_path = root / "manifest.json"
            write_jsonl(dataset_path, rows)
            manifest = build_preregistration_manifest(
                rows,
                dataset_sha256=sha256_file(dataset_path),
                quotas={"single_divide": 2},
                exclusions={},
                protocol_id="test-protocol",
            )
            write_json(manifest_path, manifest)
            loaded = load_preregistered_samples(dataset_path, manifest_path)
            expected = [item["sample_id"] for item in manifest["samples"]]
            self.assertEqual([item["sample_id"] for item in loaded], expected)

            value = json.loads(dataset_path.read_text(encoding="utf-8").splitlines()[0])
            value["question"] = "Changed after registration"
            write_jsonl(dataset_path, [value, rows[1]])
            with self.assertRaisesRegex(ValueError, "hash"):
                load_preregistered_samples(dataset_path, manifest_path)


if __name__ == "__main__":
    unittest.main()
