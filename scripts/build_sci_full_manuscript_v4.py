#!/usr/bin/env python3
"""Build the second-round integrated ContractFin SCI manuscript (v4).

The script deliberately transforms the immutable v3 manuscript rather than
reconstructing results from live artifacts.  Every expected edit is checked so
that a source-text drift fails loudly instead of producing a partial revision.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def build(source_path: Path) -> str:
    text = source_path.read_text(encoding="utf-8")
    source_sha = sha256_file(source_path)

    text = replace_once(
        text,
        "# Tool Use Before Teamwork: A Cost-Aware and Auditable Evaluation of LLM Architectures for Financial Numerical Reasoning",
        "# Tool Use Before Teamwork? A Preregistered, Cost-Aware Evaluation of LLM Architectures for Financial Numerical Reasoning",
        "title",
    )
    old_comment_start = "<!-- Integrated working manuscript v3."
    comment_start = text.find(old_comment_start)
    comment_end = text.find("-->", comment_start)
    if comment_start < 0 or comment_end < 0:
        raise ValueError("missing v3 provenance comment")
    provenance = (
        "<!-- Integrated working manuscript v4; second-round reviewer revision. "
        f"Source v3 SHA-256: {source_sha}. Experimental results are unchanged. -->"
    )
    text = text[:comment_start] + provenance + text[comment_end + 3 :]

    text = replace_once(
        text,
        "Both B2 variants failed development-stage structural gates; B2-v1.1's verifier accepted 16 incorrect candidates among 22 accepted outputs. Deterministic tool access therefore improved held-out financial numerical reasoning in this setting, but introduced a clear quality–cost trade-off and did not eliminate answer–program synchronization failures. Additional model-controlled roles should be evaluated as executable system components with explicit failure gates rather than assumed to provide independent verification.",
        "Both B2 variants failed development-stage structural gates; B2-v1.1's verifier accepted 16 incorrect candidates among 22 accepted outputs. Because no B2 implementation passed its gate, this study does not estimate the held-out marginal effect of multi-agent coordination. Deterministic tool access improved held-out financial numerical reasoning in this setting, but introduced a clear quality–cost trade-off and did not eliminate answer–program synchronization failures. Additional model-controlled roles should be evaluated as executable system components with explicit failure gates rather than assumed to provide independent verification.",
        "abstract claim boundary",
    )

    finance_agents = """Finance-specific agent research has begun to move beyond question answering toward end-to-end workflows. FinRobot organizes financial analysis through a multi-agent framework, while InvestorBench evaluates LLM-based investment agents in financial decision-making settings; a recent survey maps the broader design space of finance-oriented agents [@yang2024finrobot; @li-etal-2025-investorbench; @dong-etal-2025-finance-agents]. These studies demonstrate the breadth of possible financial-agent applications. They do not, however, remove the need for matched architectural comparisons: an end-to-end agent framework can differ from a baseline in tools, prompts, roles, interaction turns, and inference budget simultaneously. The present study therefore uses a narrower numerical-reasoning task to isolate the first architectural increment before making any claim about additional coordination.

"""
    anchor = "The same structure introduces dependencies that a single-agent evaluation does not contain."
    if text.count(anchor) != 1:
        raise ValueError("finance-agent insertion anchor missing or duplicated")
    text = text.replace(anchor, finance_agents + anchor, 1)

    evaluation_section = """### 2.5 Agent evaluation as system evaluation

Interactive-agent benchmarks increasingly evaluate complete systems rather than isolated language-model responses. AgentBench tests agents across heterogeneous interactive environments and exposes failures that are invisible in static answer scoring [@liu2024agentbench]. τ-bench extends this perspective to tool-using interactions and evaluates repeated-trial reliability through pass^k-style measures, making clear that a system's success probability across repeated runs is distinct from its one-shot score [@yao2025taubench]. Kapoor et al. further argue that agent evaluations require held-out test sets, cost-controlled comparisons, and reproducible evaluation artifacts because architectural changes often alter both capability and inference budget [@kapoor2025agents].

These principles motivate the unit of analysis in this paper. We evaluate the full executable pipeline, count unsuccessful outputs in the registered denominator, preserve call and token costs, and separate development gates from held-out inference. The three-run stability analysis is descriptive rather than an inflation of the primary sample, and the B2 systems are withheld from confirmatory comparison because an architecture that cannot reliably produce the registered artifact is not yet a valid treatment condition.

### 2.6 Study position"""
    text = replace_once(text, "### 2.5 Study position", evaluation_section, "agent-evaluation section")

    figure1 = """

![Architecture ladder from direct generation to deterministic tools and development-only multi-agent coordination](figures/figure1_architecture_ladder_v1.png)

**Figure 1. Architecture ladder and claim boundary.** B0 and B1 entered the preregistered held-out comparison. B2 remained development-only because its fixed-role implementations failed the structural acceptance gates. Boxes with solid borders are model-controlled components; shaded boxes are deterministic tools or gates.
"""
    fig1_anchor = "Because the provider alias may resolve to changing backend snapshots, all returned model identifiers and timestamps are retained as protocol evidence rather than assuming snapshot immutability."
    text = replace_once(text, fig1_anchor, fig1_anchor + figure1, "Figure 1 insertion")

    figure2 = """

![Preregistered inference and evaluation isolation pipeline](figures/figure2_preregistered_pipeline_v1.png)

**Figure 2. Preregistered inference–evaluation pipeline.** The 500-item sample, answer-stripped inputs, paired schedule, runtime hashes, and failure rules were frozen before live inference. Prediction hashes and structural gates preceded gold access; a failed gate required stopping or a dated full-schedule amendment rather than selective item reruns.
"""
    fig2_anchor = "If more than 1% of pairs contain mismatched returned model identifiers, confirmatory analysis pauses before unblinding and requires a dated amendment."
    text = replace_once(text, fig2_anchor, fig2_anchor + figure2, "Figure 2 insertion")

    figure3 = """

![Observed held-out quality and resource profile for B0 and B1](figures/figure3_quality_cost_profile_v1.png)

**Figure 3. Observed quality–cost profile.** B1 improved final-answer accuracy by 5.0 percentage points while using 3.22× as many model calls and 2.41× as many tokens. The line connects the two evaluated systems for visual comparison; with only two architectures, it is not an estimated efficiency frontier.
"""
    fig3_anchor = "The result is therefore a quality–token-cost trade-off, not a general efficiency gain."
    text = replace_once(text, fig3_anchor, fig3_anchor + figure3, "Figure 3 insertion")

    caption_replacements = {
        "**Table 2. Frozen held-out allocation by operation stratum**": "**Supplementary Table S1. Frozen held-out allocation by operation stratum**",
        "**Table 3. Formative development evidence for the architecture ladder**": "**Supplementary Table S2. Formative development evidence for the architecture ladder**",
        "**Table 4. Preregistered paired held-out comparison of B0 and B1**": "**Table 2. Preregistered paired held-out comparison of B0 and B1**",
        "**Table 5. Preregistered secondary outcomes**": "**Table 3. Preregistered secondary outcomes**",
        "**Table 6. Held-out resource and efficiency results**": "**Table 4. Held-out resource and efficiency results**",
        "**Table 7. Descriptive three-run stability on the registered 100-item subset**": "**Table 5. Descriptive three-run stability on the registered 100-item subset**",
        "**Table 8. Paired outcome transitions and deterministic mechanism evidence**": "**Table 6. Paired outcome transitions and deterministic mechanism evidence**",
    }
    for old, new in caption_replacements.items():
        text = replace_once(text, old, new, f"renumber {old}")
    text = replace_once(
        text,
        "Table 7 summarizes the 100 item-level CVs",
        "Table 5 summarizes the 100 item-level CVs",
        "stability table cross-reference",
    )

    text = replace_once(
        text,
        "The result is therefore better described as a quality–token-cost trade-off than as a general efficiency improvement.",
        "The result is therefore better described as a quality–token-cost trade-off than as a general efficiency improvement. This interpretation follows the broader requirement that agent systems be compared under explicit resource accounting rather than by capability scores alone [@kapoor2025agents].",
        "cost-aware discussion citation",
    )
    text = replace_once(
        text,
        "Repeated evaluation, immutable model snapshots where available, and output-level consistency checks remain necessary even when tool use makes control flow appear more structured.",
        "Repeated evaluation, immutable model snapshots where available, and output-level consistency checks remain necessary even when tool use makes control flow appear more structured. This distinction parallels interactive-agent evaluations in which repeated-trial reliability is treated as a system property rather than inferred from one successful trajectory [@yao2025taubench].",
        "stability literature connection",
    )
    text = replace_once(
        text,
        "Multi-agent evaluation should report how disagreements are resolved, whether verification decisions are correct, which role consumes the shared budget, and whether repeated agents provide independent evidence or merely correlated restatements.",
        "Multi-agent evaluation should report how disagreements are resolved, whether verification decisions are correct, which role consumes the shared budget, and whether repeated agents provide independent evidence or merely correlated restatements. This requirement is consistent with finance-agent research that treats orchestration as an explicit system design choice, but the present evidence does not compare our failed-gate B2 implementations with those broader frameworks [@yang2024finrobot; @dong-etal-2025-finance-agents].",
        "finance-agent discussion boundary",
    )

    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="manuscript/contractfin_sci_full_v3.md")
    parser.add_argument("--output", default="manuscript/contractfin_sci_full_v4.md")
    args = parser.parse_args()
    source_path = (PROJECT_ROOT / args.source).resolve()
    output_path = (PROJECT_ROOT / args.output).resolve()
    output_path.write_text(build(source_path), encoding="utf-8")
    try:
        display_path = output_path.relative_to(PROJECT_ROOT)
    except ValueError:
        display_path = output_path
    print(f"wrote {display_path} sha256={sha256_file(output_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
