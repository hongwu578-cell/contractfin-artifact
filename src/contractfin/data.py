from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Iterator

from .models import UnifiedSample
from .utils import read_jsonl, write_json, write_jsonl


def _finqa_evidence(gold_inds: Any) -> list[dict[str, Any]]:
    if isinstance(gold_inds, dict):
        return [
            {"id": str(key), "text": str(text), "source": "gold_inds"}
            for key, text in gold_inds.items()
        ]
    if isinstance(gold_inds, list):
        return [
            {
                "id": str(index),
                "text": str(item.get("text", item)) if isinstance(item, dict) else str(item),
                "source": "gold_inds",
            }
            for index, item in enumerate(gold_inds)
        ]
    return []


def normalize_finqa_record(record: dict[str, Any], split: str) -> UnifiedSample:
    qa = record.get("qa")
    if not isinstance(qa, dict):
        raise ValueError("FinQA record has no qa object")
    source_id = str(record.get("id") or record.get("filename") or "").strip()
    if not source_id:
        raise ValueError("FinQA record has no id")
    question = qa.get("question")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("FinQA record has no question")
    answer = qa.get("exe_ans")
    if answer is None:
        answer = qa.get("answer")
    sample = UnifiedSample(
        sample_id=f"finqa:{split}:{source_id}",
        dataset="FinQA",
        split=split,
        question=question,
        documents=[
            {
                "document_id": source_id,
                "filename": record.get("filename"),
                "pre_text": record.get("pre_text", []),
                "table": record.get("table", []),
                "post_text": record.get("post_text", []),
            }
        ],
        gold_answer=answer,
        gold_program=qa.get("program") or qa.get("program_re"),
        gold_evidence=_finqa_evidence(qa.get("gold_inds")),
        metadata={
            "source_id": source_id,
            "raw_answer": qa.get("answer"),
            "execution_answer": qa.get("exe_ans"),
            "source_format": "official_finqa_json",
        },
    )
    errors = sample.validate()
    if errors:
        raise ValueError("; ".join(errors))
    return sample


def iter_finqa(path: Path, split: str) -> Iterator[UnifiedSample]:
    with path.open(encoding="utf-8") as handle:
        records = json.load(handle)
    if not isinstance(records, list):
        raise ValueError(f"{path}: expected a JSON array")
    for record in records:
        if not isinstance(record, dict):
            raise ValueError(f"{path}: expected every record to be an object")
        yield normalize_finqa_record(record, split)


def _financebench_evidence(items: Any, default_document: str) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        return []
    evidence: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if isinstance(item, dict):
            doc_name = str(item.get("doc_name") or default_document)
            page = item.get("evidence_page_num", item.get("page_number", item.get("page")))
            text = item.get("evidence_text", item.get("text", item.get("evidence", "")))
            locator = f"{doc_name}:p{page}" if page is not None else f"{doc_name}:e{index}"
            evidence.append(
                {
                    "id": locator,
                    "document_id": doc_name,
                    "page": page,
                    "text": str(text),
                }
            )
        else:
            evidence.append(
                {
                    "id": f"{default_document}:e{index}",
                    "document_id": default_document,
                    "text": str(item),
                }
            )
    return evidence


def normalize_financebench_record(
    record: dict[str, Any],
    document_metadata: dict[str, dict[str, Any]] | None = None,
) -> UnifiedSample:
    raw_id = record.get("financebench_id")
    if raw_id is None:
        raise ValueError("FinanceBench record has no financebench_id")
    question = record.get("question")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("FinanceBench record has no question")
    doc_name = str(record.get("doc_name") or "unknown_document")
    metadata = (document_metadata or {}).get(doc_name, {})
    document = {
        "document_id": doc_name,
        "doc_type": record.get("doc_type", metadata.get("doc_type")),
        "doc_period": record.get("doc_period", metadata.get("doc_period")),
        "doc_link": record.get("doc_link", metadata.get("doc_link")),
        "company": record.get("company", metadata.get("company")),
        "local_pdf": None,
    }
    sample = UnifiedSample(
        sample_id=f"financebench:open:{raw_id}",
        dataset="FinanceBench",
        split="open_source",
        question=question,
        documents=[document],
        gold_answer=record.get("answer"),
        gold_program=None,
        gold_evidence=_financebench_evidence(record.get("evidence"), doc_name),
        metadata={
            "source_id": raw_id,
            "question_type": record.get("question_type"),
            "justification": record.get("justification"),
            "dataset_subset_label": record.get("dataset_subset_label"),
            "source_format": "financebench_open_source_jsonl",
            "document_available_locally": False,
        },
    )
    errors = sample.validate()
    if errors:
        raise ValueError("; ".join(errors))
    return sample


def _load_financebench_metadata(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    result: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(path):
        name = row.get("doc_name")
        if name is not None:
            result[str(name)] = row
    return result


def iter_financebench(path: Path, metadata_path: Path | None = None) -> Iterator[UnifiedSample]:
    metadata = _load_financebench_metadata(metadata_path) if metadata_path else {}
    for record in read_jsonl(path):
        yield normalize_financebench_record(record, metadata)


def _normalize_to_file(
    values: Iterable[UnifiedSample],
    output_path: Path,
) -> dict[str, Any]:
    normalized: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    total = 0
    for total, value in enumerate(values, start=1):
        try:
            errors = value.validate()
            if errors:
                raise ValueError("; ".join(errors))
            normalized.append(value.to_dict())
        except Exception as exc:  # retain a failure record instead of silently skipping
            failures.append({"index": total - 1, "error": str(exc)})
    write_jsonl(output_path, normalized)
    success_rate = (len(normalized) / total) if total else 0.0
    return {
        "input_records": total,
        "output_records": len(normalized),
        "failures": failures,
        "success_rate": success_rate,
        "output": str(output_path),
    }


def normalize_all(project_root: Path) -> dict[str, Any]:
    raw = project_root / "data" / "raw"
    normalized = project_root / "data" / "normalized"
    normalized.mkdir(parents=True, exist_ok=True)

    finqa_results: dict[str, Any] = {}
    for split in ("train", "dev", "test"):
        source = raw / "finqa" / "dataset" / f"{split}.json"
        if not source.exists():
            raise FileNotFoundError(f"missing FinQA source: {source}")
        finqa_results[split] = _normalize_to_file(
            iter_finqa(source, split),
            normalized / f"finqa_{split}.jsonl",
        )

    financebench_source = raw / "financebench" / "data" / "financebench_open_source.jsonl"
    financebench_metadata = raw / "financebench" / "data" / "financebench_document_information.jsonl"
    if not financebench_source.exists():
        raise FileNotFoundError(f"missing FinanceBench source: {financebench_source}")
    financebench_result = _normalize_to_file(
        iter_financebench(financebench_source, financebench_metadata),
        normalized / "financebench_open_source.jsonl",
    )

    summary = {
        "schema_version": "1.0",
        "finqa": finqa_results,
        "financebench": financebench_result,
        "acceptance": {
            "minimum_parse_success_rate": 0.99,
            "passed": all(
                result["success_rate"] >= 0.99
                for result in [*finqa_results.values(), financebench_result]
            ),
        },
    }
    write_json(project_root / "reports" / "normalization_summary.json", summary)
    return summary
