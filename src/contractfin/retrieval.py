from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any


_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    label: str
    text: str
    document_id: str
    position: int


def _tokens(value: Any) -> list[str]:
    return [item.casefold() for item in _TOKEN_RE.findall(str(value))]


def sample_chunks(sample: dict[str, Any]) -> list[DocumentChunk]:
    documents = sample.get("documents") or []
    chunks: list[DocumentChunk] = []
    multiple_documents = len(documents) > 1
    position = 0
    for document in documents:
        document_id = str(
            document.get("document_id") or document.get("filename") or "unknown_document"
        )
        prefix = f"{document_id}:" if multiple_documents else ""
        for index, text in enumerate(document.get("pre_text", [])):
            chunks.append(DocumentChunk(f"{prefix}text_{index}", str(text), document_id, position))
            position += 1
        table = document.get("table", [])
        header_text = ""
        if isinstance(table, list) and table:
            header = table[0] if isinstance(table[0], list) else [table[0]]
            header_text = " | ".join(str(cell) for cell in header)
        for index, row in enumerate(table):
            cells = row if isinstance(row, list) else [row]
            row_text = " | ".join(str(cell) for cell in cells)
            text = (
                f"HEADER: {header_text} || ROW: {row_text}"
                if index > 0 and header_text
                else row_text
            )
            chunks.append(DocumentChunk(f"{prefix}table_{index}", text, document_id, position))
            position += 1
        for index, text in enumerate(document.get("post_text", [])):
            text_index = len(document.get("pre_text", [])) + index
            chunks.append(
                DocumentChunk(f"{prefix}text_{text_index}", str(text), document_id, position)
            )
            position += 1
        if document.get("text"):
            chunks.append(
                DocumentChunk(f"{prefix}document_text", str(document["text"]), document_id, position)
            )
            position += 1
    return chunks


def search_sample(
    sample: dict[str, Any], query: str, *, top_k: int = 8
) -> list[dict[str, Any]]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if not isinstance(top_k, int) or isinstance(top_k, bool) or not 1 <= top_k <= 12:
        raise ValueError("top_k must be an integer from 1 to 12")
    chunks = sample_chunks(sample)
    if not chunks:
        return []
    query_terms = _tokens(query)
    query_counts = Counter(query_terms)
    document_tokens = [_tokens(chunk.text) for chunk in chunks]
    document_frequency = Counter(
        term for tokens in document_tokens for term in set(tokens)
    )
    average_length = sum(len(tokens) for tokens in document_tokens) / len(document_tokens)
    average_length = average_length or 1.0
    total_documents = len(chunks)
    k1 = 1.5
    b = 0.75
    ranked: list[tuple[float, DocumentChunk]] = []
    for chunk, tokens in zip(chunks, document_tokens):
        counts = Counter(tokens)
        length = len(tokens)
        score = 0.0
        for term, query_frequency in query_counts.items():
            term_frequency = counts.get(term, 0)
            if not term_frequency:
                continue
            df = document_frequency[term]
            idf = math.log(1 + (total_documents - df + 0.5) / (df + 0.5))
            denominator = term_frequency + k1 * (1 - b + b * length / average_length)
            score += query_frequency * idf * (term_frequency * (k1 + 1) / denominator)
        ranked.append((score, chunk))
    ranked.sort(key=lambda item: (-item[0], item[1].position, item[1].label))
    return [
        {
            "label": chunk.label,
            "text": chunk.text,
            "document_id": chunk.document_id,
            "score": round(score, 8),
        }
        for score, chunk in ranked[:top_k]
    ]
