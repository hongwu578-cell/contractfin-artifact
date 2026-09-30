from __future__ import annotations

import argparse
import json
from pathlib import Path

from .data import normalize_all
from .evaluation import evaluate_files


def _project_root(value: str | None) -> Path:
    return Path(value).resolve() if value else Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="contractfin")
    parser.add_argument("--root", help="ContractFin project root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("normalize", help="normalize frozen raw datasets")

    evaluate = subparsers.add_parser("evaluate", help="score a JSONL prediction file")
    evaluate.add_argument("--gold", required=True)
    evaluate.add_argument("--predictions", required=True)
    evaluate.add_argument("--report", required=True)

    args = parser.parse_args(argv)
    root = _project_root(args.root)
    if args.command == "normalize":
        result = normalize_all(root)
    else:
        result = evaluate_files(
            Path(args.gold).resolve(),
            Path(args.predictions).resolve(),
            Path(args.report).resolve(),
        )["summary"]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

