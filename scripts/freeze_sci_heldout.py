#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from contractfin.utils import atomic_write_text, read_jsonl, sha256_file, write_json  # noqa: E402


LOCK_PATH = Path("config/sci_heldout_freeze_lock_v1.json")
REVIEW_PATH = Path("reports/sci_heldout_freeze_review_v1.md")

LOCKED_PATHS = (
    "pyproject.toml",
    "schemas/prediction.schema.json",
    "config/b0_finqa_dev_30_v1_2_amendment.json",
    "config/b1_finqa_dev_v1_2_amendment.json",
    "config/sci_heldout_preregistration_v1.json",
    "config/sci_finqa_test500_manifest_v1.json",
    "config/sci_finqa_test500_interleaved_schedule_v1.jsonl",
    "config/sci_finqa_stability100_interleaved_schedule_v1.jsonl",
    "config/sci_heldout_runtime_v1.json",
    "config/sci_heldout_stability_runtime_v1.json",
    "data/normalized/finqa_test.jsonl",
    "data/heldout/finqa_test500_inference_v1.jsonl",
    "data/heldout/finqa_test500_gold_v1.jsonl",
    "reports/sci_finqa_test500_manifest_v1.md",
    "reports/sci_exact_mcnemar_power_v1.json",
    "reports/sci_exact_mcnemar_power_v1.csv",
    "reports/sci_exact_mcnemar_power_v1.md",
    "reports/sci_heldout_local_audit_v1.json",
    "reports/sci_heldout_preregistration_v1.md",
    "src/contractfin/b0.py",
    "src/contractfin/b1.py",
    "src/contractfin/b1_tools.py",
    "src/contractfin/evaluation.py",
    "src/contractfin/evidence_ids.py",
    "src/contractfin/heldout.py",
    "src/contractfin/program.py",
    "src/contractfin/retrieval.py",
    "src/contractfin/run_logging.py",
    "src/contractfin/schemas.py",
    "src/contractfin/utils.py",
    "scripts/prepare_sci_heldout.py",
    "scripts/run_sci_heldout.py",
    "scripts/freeze_sci_heldout.py",
    "tests/test_heldout.py",
)


def hash_entry(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise FileNotFoundError(f"freeze artifact is missing: {relative}")
    return {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def review_checks(root: Path) -> dict[str, bool]:
    prereg = json.loads((root / "config/sci_heldout_preregistration_v1.json").read_text())
    audit = json.loads((root / "reports/sci_heldout_local_audit_v1.json").read_text())
    primary_runtime = json.loads((root / "config/sci_heldout_runtime_v1.json").read_text())
    stability_runtime = json.loads((root / "config/sci_heldout_stability_runtime_v1.json").read_text())
    primary_schedule = list(
        read_jsonl(root / "config/sci_finqa_test500_interleaved_schedule_v1.jsonl")
    )
    stability_schedule = list(
        read_jsonl(root / "config/sci_finqa_stability100_interleaved_schedule_v1.jsonl")
    )
    inference = list(read_jsonl(root / "data/heldout/finqa_test500_inference_v1.jsonl"))
    gold = list(read_jsonl(root / "data/heldout/finqa_test500_gold_v1.jsonl"))
    power = json.loads((root / "reports/sci_exact_mcnemar_power_v1.json").read_text())

    primary_first = Counter(primary_schedule[index]["system"] for index in range(0, 1000, 2))
    stability_first = {
        replicate: Counter(
            stability_schedule[index]["system"]
            for index in range(0, len(stability_schedule), 2)
            if stability_schedule[index]["replicate"] == replicate
        )
        for replicate in (2, 3)
    }
    small_effect_power = next(
        row["exact_unconditional_power"]
        for row in power["rows"]
        if row["scenario"] == "small_effect_low_discordance" and row["n"] == 500
    )
    return {
        "preregistration_status_is_frozen": prereg["status"] == "frozen_confirmed_no_live_api_authorization",
        "local_audit_passed": audit["passed"] is True and audit["api_calls"] == 0,
        "primary_sample_is_500": len(inference) == len(gold) == 500,
        "inference_contains_no_gold_fields": all(
            not ({"gold_answer", "gold_program", "gold_evidence"} & set(item))
            for item in inference
        ),
        "gold_contains_execution_documents": all(bool(item.get("documents")) for item in gold),
        "primary_runtime_is_not_authorized": primary_runtime["live_api_authorized"] is False,
        "stability_runtime_is_not_authorized": stability_runtime["live_api_authorized"] is False,
        "primary_first_order_is_250_250": primary_first == {"B0": 250, "B1": 250},
        "stability_first_order_is_50_50_per_replicate": all(
            counts == {"B0": 50, "B1": 50} for counts in stability_first.values()
        ),
        "primary_test_is_two_sided_exact_mcnemar": prereg["statistical_analysis"]["primary_test"].startswith(
            "two-sided exact conditional McNemar"
        ),
        "secondary_itt_denominators_are_frozen": {
            "program_itt_correctness",
            "execution_itt_correctness",
            "evidence_item_f1",
            "coverage",
        }
        == set(prereg["outcomes"]["secondary_family"]),
        "small_effect_power_at_500_is_at_least_80_percent": small_effect_power >= 0.80,
        "B2_is_excluded_from_confirmation": "excluded" in prereg["exploratory_boundary"],
        "current_call_authorization_is_zero": prereg["call_budget_not_authorized"]["current_authorization"] == 0,
    }


def render_review(lock: dict[str, Any], lock_sha256: str) -> str:
    checks = lock["review_checks"]
    lines = [
        "# SCI held-out预注册冻结审阅报告",
        "",
        f"- 协议：`{lock['protocol_id']}`",
        f"- 冻结日期：`{lock['freeze_date']}`",
        f"- 冻结锁SHA-256：`{lock_sha256}`",
        "- 真实模型API调用：`0`",
        "- 结论：**通过冻结审阅，可以作为后续held-out实验的唯一v1依据；当前仍未获得live授权。**",
        "",
        "## 冻结前审阅发现及处理",
        "",
        "1. 原gold评估文件缺少表格上下文，会使表格聚合程序无法复算。现已补入仅供后置评估使用的document/table上下文，推理runtime仍无gold路径。",
        "2. 原主实验首运行系统顺序为244:256。现已改为严格250:250，并保持每题B0/B1相邻执行。",
        "3. 原程序与执行准确率可能采用选择性分母。现已冻结为全500题ITT口径，缺失、无效或不可执行程序均计错。",
        "4. 已补充100题稳定性实验的两轮调度：每轮首系统50:50，同一题在第2、3轮中交换首系统。",
        "5. 已明确基础设施失败、系统输出失败和返回模型漂移的判定边界，并规定越阈值后必须在揭盲前停止。",
        "6. live授权改为独立日期化修订文件，不修改已冻结runtime；授权文件必须绑定runtime哈希和实验范围。",
        "",
        "## 冻结检查",
        "",
        "| 检查项 | 结果 |",
        "|---|:---:|",
    ]
    for name, passed in checks.items():
        lines.append(f"| `{name}` | {'通过' if passed else '失败'} |")
    lines.extend(
        [
            "",
            "## 仍需在论文中主动声明的边界",
            "",
            "- 研究仅使用FinQA，结论不能直接外推到全部金融任务、全部模型或全部多智能体系统。",
            "- `deepseek-flash`是服务别名而非不可变模型快照；成对交错、返回模型记录和漂移阈值只能降低而不能完全消除该风险。",
            "- 500题是带稀有运算最低配额的压力感知样本；未加权主效应对应这一预注册样本组合，FinQA全测试集总体效应仅作加权次要估计。",
            "- B2结果来自开发集失败诊断，只能支持机制假设，不能作为held-out架构优劣的确证性证据。",
            "- 稳定性子集的重复结果不与主实验合并做显著性检验。",
            "",
            "## 变更规则",
            "",
            "冻结锁所列任一文件发生变化，v1锁即失效。后续只能通过日期化、说明理由的修订文件变更；不得静默覆盖、替换样本或按结果调整分析。",
        ]
    )
    return "\n".join(lines) + "\n"


def verify(root: Path) -> dict[str, Any]:
    lock_path = root / LOCK_PATH
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    mismatches: list[dict[str, str]] = []
    for entry in lock["locked_files"]:
        path = root / entry["path"]
        actual = sha256_file(path) if path.is_file() else "missing"
        if actual != entry["sha256"]:
            mismatches.append(
                {"path": entry["path"], "expected": entry["sha256"], "actual": actual}
            )
    checks = review_checks(root)
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    return {
        "schema_version": "1.0",
        "protocol_id": lock["protocol_id"],
        "lock_sha256": sha256_file(lock_path),
        "locked_file_count": len(lock["locked_files"]),
        "hash_mismatches": mismatches,
        "failed_review_checks": failed_checks,
        "api_calls": 0,
        "passed": not mismatches and not failed_checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze or verify the SCI held-out preregistration")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.verify:
        result = verify(root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["passed"] else 1

    lock_path = root / LOCK_PATH
    if lock_path.exists() and not args.replace:
        raise SystemExit("freeze lock already exists; use --verify, or --replace only for an explicit pre-run refreeze")
    checks = review_checks(root)
    failures = sorted(name for name, passed in checks.items() if not passed)
    if failures:
        raise SystemExit(f"freeze review failed: {failures}")
    lock = {
        "schema_version": "1.0",
        "protocol_id": "contractfin-sci-finqa-test500-v1",
        "freeze_date": "2026-09-29",
        "status": "frozen_confirmed_no_live_api_authorization",
        "live_api_calls_at_freeze": 0,
        "review_checks": checks,
        "locked_files": [hash_entry(root, relative) for relative in LOCKED_PATHS],
        "change_policy": "Any hash change invalidates this v1 lock. Use a dated amendment bound to this lock and runtime hash; never silently overwrite or tune from held-out outcomes.",
    }
    write_json(lock_path, lock)
    lock_sha = sha256_file(lock_path)
    review_path = root / REVIEW_PATH
    atomic_write_text(review_path, render_review(lock, lock_sha))
    result = verify(root)
    result["review_report"] = str(REVIEW_PATH)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
