#!/usr/bin/env python3
"""Build manuscript v2 by inserting gated primary and stability results."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_section(text: str, heading: str, next_heading: str, replacement: str) -> str:
    pattern = re.compile(
        rf"{re.escape(heading)}\n.*?(?={re.escape(next_heading)}\n)",
        flags=re.DOTALL,
    )
    updated, count = pattern.subn(replacement.rstrip() + "\n\n", text, count=1)
    if count != 1:
        raise ValueError(f"section replacement failed for {heading}")
    return updated


def build(source: Path) -> str:
    text = source.read_text(encoding="utf-8")
    text = text.replace("Methods and Experiments/Results skeleton, version 1", "Methods and Experiments/Results draft, version 2")
    text = text.replace(
        "Live held-out API calls at the time of writing: **0**.",
        "Primary held-out inference: **completed with 2,110 provider calls**; the separately authorized stability experiment completed with **842 provider calls**.",
    )
    text = text.replace(
        "Tokens in the form `RESULT:<key>` used in Section 4 must not be replaced until the corresponding immutable prediction artifacts have passed the preregistered structural gates.",
        "The primary and stability prediction artifacts passed their preregistered structural gates before gold access; the two additional stability replicates are reported descriptively and are not pooled into the primary analysis.",
    )

    replacements = {
        "{{RESULT:PRIMARY_TASK_RECORDS}}": "1,000 (pass)",
        "{{RESULT:B0_UNIQUE_PREDICTIONS}}": "500",
        "{{RESULT:B1_UNIQUE_PREDICTIONS}}": "500",
        "{{RESULT:DUPLICATE_PREDICTIONS}}": "0 (pass)",
        "{{RESULT:FIRST_ORDER_COUNTS}}": "250/250 (pass)",
        "{{RESULT:RUNTIME_HASH_STATUS}}": "Exact match (pass)",
        "{{RESULT:INFRASTRUCTURE_FAILURE_GATE}}": "B0=0%; B1=0%; difference=0 pp (pass)",
        "{{RESULT:MODEL_DRIFT_GATE}}": "0/500 mismatched pairs (pass)",
        "{{RESULT:PREDICTION_FREEZE_STATUS}}": "B0 and B1 SHA-256 recorded before gold access (pass)",
        "{{RESULT:STRUCTURAL_GATE_DECISION}}": "PASS; unblinding permitted",
        "{{RESULT:AMENDMENT_REFERENCE_OR_NONE}}": "`config/authorizations/sci_heldout_primary_rerun1_amendment_2026-09-29.json`",
        "{{RESULT:B0_ANSWER_ACCURACY}}": "42.0% (210/500)",
        "{{RESULT:B1_ANSWER_ACCURACY}}": "47.0% (235/500)",
        "{{RESULT:ANSWER_DIFFERENCE_PP}}": "+5.0 percentage points",
        "{{RESULT:ANSWER_DIFFERENCE_CI}}": "[+1.4, +8.8] percentage points",
        "{{RESULT:N10}}": "58",
        "{{RESULT:N01}}": "33",
        "{{RESULT:MCNEMAR_PRIMARY_P}}": "0.01146",
        "{{RESULT:B0_PROGRAM_ITT}}": "0.1860",
        "{{RESULT:B1_PROGRAM_ITT}}": "0.3900",
        "{{RESULT:PROGRAM_DIFF_PP}}": "+0.2040",
        "{{RESULT:PROGRAM_P}}": "4.7409×10^-24",
        "{{RESULT:PROGRAM_HOLM_P}}": "1.4223×10^-23",
        "{{RESULT:B0_EXECUTION_ITT}}": "0.2480",
        "{{RESULT:B1_EXECUTION_ITT}}": "0.5160",
        "{{RESULT:EXECUTION_DIFF_PP}}": "+0.2680",
        "{{RESULT:EXECUTION_P}}": "2.0818×10^-29",
        "{{RESULT:EXECUTION_HOLM_P}}": "8.3272×10^-29",
        "{{RESULT:B0_EVIDENCE_F1}}": "0.8367",
        "{{RESULT:B1_EVIDENCE_F1}}": "0.8260",
        "{{RESULT:EVIDENCE_F1_DIFF}}": "−0.0107",
        "{{RESULT:EVIDENCE_P}}": "0.27263",
        "{{RESULT:EVIDENCE_HOLM_P}}": "0.54525",
        "{{RESULT:B0_COVERAGE}}": "0.9900",
        "{{RESULT:B1_COVERAGE}}": "0.9820",
        "{{RESULT:COVERAGE_DIFF_PP}}": "−0.0080",
        "{{RESULT:COVERAGE_P}}": "0.34375",
        "{{RESULT:COVERAGE_HOLM_P}}": "0.54525",
        "{{RESULT:WEIGHTED_ANSWER_DIFFERENCE}}": "+5.67 percentage points",
        "{{RESULT:B0_MODEL_CALLS}}": "500",
        "{{RESULT:B1_MODEL_CALLS}}": "1,610",
        "{{RESULT:MODEL_CALL_RATIO}}": "3.22×",
        "{{RESULT:B1_TOOL_CALLS}}": "1,113",
        "{{RESULT:B0_TOTAL_TOKENS}}": "1,603,138",
        "{{RESULT:B1_TOTAL_TOKENS}}": "3,856,862",
        "{{RESULT:TOKEN_RATIO}}": "2.41×",
        "{{RESULT:B0_TOKEN_MEDIAN_IQR}}": "2,552 (2,084–3,303)",
        "{{RESULT:B1_TOKEN_MEDIAN_IQR}}": "5,994 (5,721–6,714)",
        "{{RESULT:TOKEN_PAIRED_CI}}": "mean +4,507 [95% CI +4,083 to +4,963]",
        "{{RESULT:B0_TOTAL_LATENCY}}": "4,444.4 s",
        "{{RESULT:B1_TOTAL_LATENCY}}": "4,981.8 s",
        "{{RESULT:LATENCY_RATIO}}": "1.12×",
        "{{RESULT:B0_LATENCY_MEDIAN_IQR}}": "6.12 (4.41–9.25) s",
        "{{RESULT:B1_LATENCY_MEDIAN_IQR}}": "6.07 (5.45–7.65) s",
        "{{RESULT:LATENCY_PAIRED_CI}}": "mean +1.07 s [95% CI −0.84 to +4.03]",
        "{{RESULT:B0_TOKENS_PER_CORRECT}}": "7,634",
        "{{RESULT:B1_TOKENS_PER_CORRECT}}": "16,412",
        "{{RESULT:TOKENS_PER_CORRECT_RATIO}}": "2.15×",
        "{{RESULT:B0_LATENCY_PER_CORRECT}}": "21.16 s",
        "{{RESULT:B1_LATENCY_PER_CORRECT}}": "21.20 s",
        "{{RESULT:LATENCY_PER_CORRECT_RATIO}}": "1.00×",
    }
    for token, value in replacements.items():
        if token not in text:
            raise ValueError(f"missing expected placeholder: {token}")
        text = text.replace(token, value)

    integrity_template = """This subsection must be completed before any accuracy result is inspected. If a structural threshold fails, report the deviation and amendment status here and do not continue to Sections 4.3–4.6 as confirmatory analyses."""
    integrity_result = """The structural gate was evaluated before any gold access. All 1,000 scheduled records were present, both systems had 500 unique predictions, the 250/250 first-system balance was preserved, infrastructure-failure and model-drift rates were zero, and prediction hashes matched the inference summary. The first sandboxed attempt failed at DNS resolution before provider contact and consumed zero model calls; a dated amendment then authorized a complete full-schedule rerun rather than selected-item retries."""
    if integrity_template not in text:
        raise ValueError("integrity narrative template not found")
    text = text.replace(integrity_template, integrity_result)

    text = text.replace(
        "| Program ITT correctness | 0.1860 | 0.3900 | +0.2040 | 4.7409×10^-24 | 1.4223×10^-23 | Secondary |",
        "| Program ITT correctness | 0.1860 | 0.3900 | +0.2040 | 4.7409×10^-24 | 1.4223×10^-23 | Holm-significant |",
    )
    text = text.replace(
        "| Execution ITT correctness | 0.2480 | 0.5160 | +0.2680 | 2.0818×10^-29 | 8.3272×10^-29 | Secondary |",
        "| Execution ITT correctness | 0.2480 | 0.5160 | +0.2680 | 2.0818×10^-29 | 8.3272×10^-29 | Holm-significant |",
    )
    text = text.replace(
        "| Evidence item-level F1 | 0.8367 | 0.8260 | −0.0107 | 0.27263 | 0.54525 | Secondary |",
        "| Evidence item-level F1 | 0.8367 | 0.8260 | −0.0107 | 0.27263 | 0.54525 | Not significant |",
    )
    text = text.replace(
        "| Coverage | 0.9900 | 0.9820 | −0.0080 | 0.34375 | 0.54525 | Secondary |",
        "| Coverage | 0.9900 | 0.9820 | −0.0080 | 0.34375 | 0.54525 | Not significant |",
    )

    primary_template = """The confirmatory result should be written in the following order: absolute system accuracies, paired difference and interval, discordant-pair counts, exact p-value, and a restrained claim tied to the registered sample. Use one of these pre-specified interpretations:

- If the exact p-value is below 0.05 and the interval excludes zero in favor of B1: “Under the preregistered stress-aware FinQA sample, tool augmentation improved final-answer correctness relative to direct generation.”
- If the exact p-value is not below 0.05: “The held-out comparison did not provide sufficient evidence of a final-answer correctness difference; the estimated effect and uncertainty interval remain the primary quantitative result.”
- If B0 is significantly better: report the direction without redefining outcomes, excluding failed items, or moving a secondary metric into the primary position.
"""
    primary_result = """B0 answered 210 of 500 items correctly (42.0%), whereas B1 answered 235 correctly (47.0%). The paired difference was +5.0 percentage points (95% paired bootstrap CI, +1.4 to +8.8). There were 58 B1-only correct pairs and 33 B0-only correct pairs; the two-sided exact McNemar p-value was 0.01146. Under the preregistered stress-aware FinQA sample, tool augmentation therefore improved final-answer correctness relative to direct generation. The prevalence-weighted descriptive estimate for the full FinQA test composition was similar (+5.67 percentage points)."""
    if primary_template not in text:
        raise ValueError("primary interpretation template not found")
    text = text.replace(primary_template, primary_result + "\n")

    secondary_template = """Report selective program/execution accuracy, schema-valid completion, failed-tool rate, unit/scale errors, and unsupported claims in a compact supplementary table. Do not describe a selective metric as a full-sample system improvement.

The population-prevalence-weighted answer difference is **+5.67 percentage points**, compared with the unweighted preregistered difference of **+5.0 percentage points**. Any material discrepancy should be explained as the consequence of deliberate rare-operation oversampling rather than treated as a robustness failure."""
    secondary_result = """Program ITT correctness increased from 0.1860 to 0.3900, and execution ITT correctness increased from 0.2480 to 0.5160; both differences remained significant after Holm correction. Coverage decreased from 0.9900 to 0.9820 and evidence F1 decreased from 0.8367 to 0.8260; neither difference was significant after correction. The population-prevalence-weighted answer difference was +5.67 percentage points, close to the unweighted preregistered difference of +5.0 points. Selective metrics are retained only as diagnostics and are not substituted for the full-sample ITT outcomes."""
    if secondary_template not in text:
        raise ValueError("secondary narrative template not found")
    text = text.replace(secondary_template, secondary_result)

    resource_template = """The narrative must avoid equating greater accuracy with greater efficiency. If B1 improves quality while increasing tokens, describe a quality–cost trade-off. If B1 also reduces latency, distinguish provider-side parallelism or response-length effects from token consumption rather than claiming universal computational efficiency."""
    resource_result = """B1's accuracy gain required 3.22 times as many model calls and 2.41 times as many tokens as B0. Its median latency per item was similar to B0 (6.07 versus 6.12 s), but total latency was 12% higher and the paired mean-latency difference had a wide interval that included zero because of a 608-s completed-response outlier. Tokens per correct answer increased from 7,634 to 16,412, while latency per correct answer remained nearly unchanged (21.16 versus 21.20 s). The result is therefore a quality–token-cost trade-off, not a general efficiency gain."""
    if resource_template not in text:
        raise ValueError("resource narrative template not found")
    text = text.replace(resource_template, resource_result)

    stability_section = """### 4.6 Stability under repeated calls

The separately authorized stability run completed all 400 scheduled system tasks. Before gold access, its structural audit confirmed four 100-prediction groups without duplicates, exact schedule and runtime-hash agreement, 50:50 first-system balance within each additional replicate, and reversal of first-system order for all 100 items between R2 and R3. All 842 returned calls reported the same provider model identifier. B0 had no system-output failures; B1 had three completed but unusable outputs, all retained as incorrect under the registered ITT rule. Neither system had an infrastructure failure.

Across the registered stability subset, B0 answered 43, 38, and 42 items correctly in R1, R2, and R3, respectively; B1 answered 43, 45, and 46. These replicate accuracies are descriptive and the 200 additional system-item observations per system are not added to the primary denominator.

**Table 7. Descriptive three-run stability on the registered 100-item subset**

| Stability outcome | B0 | B1 |
|---|---:|---:|
| R1/R2/R3 correct | 43/38/42 | 43/45/46 |
| Items correct in 0/3 runs | 53 | 47 |
| Items correct in 1/3 runs | 6 | 8 |
| Items correct in 2/3 runs | 6 | 9 |
| Items correct in 3/3 runs | 35 | 36 |
| Items with any correctness change | 12 (12.0%) | 17 (17.0%) |
| Median within-item token CV (IQR) | 0.156 (0.074–0.253) | 0.019 (0.007–0.235) |
| Median within-item latency CV (IQR) | 0.262 (0.166–0.427) | 0.150 (0.079–0.308) |

For each item, CV is the sample standard deviation across R1–R3 divided by the three-run mean; Table 7 summarizes the 100 item-level CVs by their median and interquartile range. B1 showed lower median token and latency dispersion but more items with a correctness transition (17 versus 12). Thus, resource stability and answer stability were empirically distinct: deterministic tool access did not eliminate output-level stochasticity, and the dynamic provider alias remains a reproducibility limitation.
"""
    text = replace_section(text, "### 4.6 Stability under repeated calls", "### 4.7 Exploratory multi-agent failure analysis", stability_section)

    error_section = """### 4.8 Paired error and mechanism analysis

The frozen paired outcomes comprised 177 items solved by both systems, 58 solved only by B1, 33 solved only by B0, and 232 solved by neither. Thus, the five-point primary gain arose from 25 net additional correct answers rather than uniform superiority. Among the 58 B1-only gains, 20 were exact-program recoveries and 30 were executable-program recoveries relative to B0. Evidence F1 improved in only 14 gains, was unchanged in 38, and worsened in 6, indicating that the dominant mechanism was arithmetic/program assistance rather than uniformly better evidence selection.

**Table 8. Paired outcome transitions and deterministic mechanism evidence**

| Paired transition | n | Share | Deterministic mechanism evidence |
|---|---:|---:|---|
| Both correct | 177 | 35.4% | Shared solved set |
| B1 only correct | 58 | 11.6% | 20 exact-program and 30 executable-program recoveries relative to B0 |
| B0 only correct | 33 | 6.6% | Includes 2 B1 system-output failures and 9 execution regressions |
| Both wrong | 232 | 46.4% | Residual reasoning and answer-synchronization failures |

The execution analysis also revealed a new failure boundary. B1 produced 258 programs that executed to the reference answer, compared with 124 for B0, but 61 of those B1 items still had an incorrect separately reported final answer (B0: 17). Conditional answer consistency among execution-correct items was therefore 76.4% for B1 and 86.3% for B0. Tool augmentation substantially improved executable reasoning while leaving an answer–program synchronization problem at the output boundary.

B1 invoked `search_document` 623 times and `calculate_finqa` 490 times. The calculator was reached on 475 items, including all 235 correct B1 outputs; none of the 25 items that did not reach the calculator was correct. Two calculator calls failed validation, and one of those items recovered to a correct final answer in a later model turn. These associations describe observed control flow and are not randomized causal effects of tool selection.

The descriptive step-depth profile was heterogeneous: B1 improved by 12.0 percentage points on 167 two-step items, showed no difference on 22 three-step items, and performed worse on the small four- and five-step groups. Because the latter groups contain only 9 and 15 items, respectively, these findings motivate targeted architecture work but do not support adequately powered subgroup claims. Complete operation-stratum estimates, the seven B1 system-output failures, nonexclusive deterministic diagnostic flags, and all 500 paired records are provided in the supplementary analysis artifacts.

Deterministic flags are explicitly nonexclusive. Numeric extraction, semantic operation choice, and argument-order causes require blinded manual adjudication before being reported as mutually exclusive causal error categories.
"""
    text = replace_section(text, "### 4.8 Error analysis after held-out evaluation", "### 4.9 Threats to validity", error_section)

    text = text.replace(
        "Main-text tables should be limited to Tables 1–6 above if the target journal permits. If space is restricted, move the complete stratum allocation (Table 2), stability table, and detailed reliability outcomes to the supplement.",
        "Main-text tables should be limited to Tables 1–8 above if the target journal permits. If space is restricted, move the complete stratum allocation (Table 2), stability table, and detailed reliability outcomes to the supplement.",
    )

    if "{{RESULT:" in text:
        raise ValueError("unresolved primary-result placeholder remains in manuscript v2")
    provenance = (
        f"> Derived mechanically from `contractfin_sci_methods_experiments_v1.md` "
        f"(SHA-256 `{sha256_file(source)}`). Primary and stability results were inserted only after their respective structural gates passed.\n"
    )
    marker = "> Working manuscript — Methods and Experiments/Results draft, version 2.  \n"
    text = text.replace(marker, marker + provenance, 1)
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--source",
        default="manuscript/contractfin_sci_methods_experiments_v1.md",
    )
    parser.add_argument(
        "--output",
        default="manuscript/contractfin_sci_methods_experiments_v2.md",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    source = root / args.source
    output = root / args.output
    output.write_text(build(source), encoding="utf-8")
    print(f"wrote {output.relative_to(root)} sha256={sha256_file(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
