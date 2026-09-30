from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class UnifiedSample:
    sample_id: str
    dataset: str
    split: str
    question: str
    documents: list[dict[str, Any]]
    gold_answer: str | int | float | bool | None
    gold_program: str | list[Any] | None = None
    gold_evidence: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0"

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not isinstance(self.sample_id, str) or not self.sample_id.strip():
            errors.append("sample_id must be a non-empty string")
        if self.dataset not in {"FinQA", "FinanceBench", "TAT-QA"}:
            errors.append("dataset is not supported")
        if not isinstance(self.split, str) or not self.split.strip():
            errors.append("split must be a non-empty string")
        if not isinstance(self.question, str) or not self.question.strip():
            errors.append("question must be a non-empty string")
        if not isinstance(self.documents, list) or not self.documents:
            errors.append("documents must be a non-empty list")
        if not isinstance(self.gold_evidence, list):
            errors.append("gold_evidence must be a list")
        if not isinstance(self.metadata, dict):
            errors.append("metadata must be an object")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "UnifiedSample":
        return cls(
            sample_id=value["sample_id"],
            dataset=value["dataset"],
            split=value["split"],
            question=value["question"],
            documents=value["documents"],
            gold_answer=value.get("gold_answer"),
            gold_program=value.get("gold_program"),
            gold_evidence=value.get("gold_evidence", []),
            metadata=value.get("metadata", {}),
            schema_version=value.get("schema_version", "1.0"),
        )

