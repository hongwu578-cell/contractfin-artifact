from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_LOG_FIELDS = {
    "run_id",
    "sample_id",
    "system",
    "model",
    "started_at",
    "finished_at",
    "input",
    "output",
    "tool_calls",
    "token_usage",
    "latency_ms",
    "error",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_log(path: Path, record: dict[str, Any]) -> None:
    missing = REQUIRED_LOG_FIELDS - record.keys()
    if missing:
        raise ValueError(f"log record missing fields: {', '.join(sorted(missing))}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()


def log_completeness(records: list[dict[str, Any]]) -> float:
    if not records:
        return 0.0
    complete = sum(REQUIRED_LOG_FIELDS <= record.keys() for record in records)
    return complete / len(records)

