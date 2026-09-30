#!/usr/bin/env python3
"""Generate publication-ready grayscale figures for the ContractFin SCI paper."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "manuscript" / "figures"


def setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.2,
            "axes.titlesize": 9.5,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.linewidth": 0.8,
            "savefig.dpi": 300,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def box(ax, x, y, w, h, label, *, fill="white", edge="0.2", lw=1.0, fs=8.0, style="round,pad=0.012"):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=style,
        linewidth=lw,
        edgecolor=edge,
        facecolor=fill,
        transform=ax.transAxes,
        clip_on=False,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs, transform=ax.transAxes)
    return patch


def arrow(ax, x1, y1, x2, y2, *, style="-|>", color="0.25", lw=1.0, mutation=9, dashed=False):
    patch = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle=style,
        mutation_scale=mutation,
        linewidth=lw,
        color=color,
        linestyle="--" if dashed else "-",
        transform=ax.transAxes,
        clip_on=False,
    )
    ax.add_patch(patch)
    return patch


def save_all(fig, stem: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg", "pdf"):
        fig.savefig(OUTPUT_DIR / f"{stem}.{suffix}", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def figure1_architecture_ladder() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.65), gridspec_kw={"wspace": 0.12})
    panel_titles = [
        ("A", "B0: direct LLM"),
        ("B", "B1: tool-augmented agent"),
        ("C", "B2: fixed-role multi-agent"),
    ]
    for ax, (letter, title) in zip(axes, panel_titles):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.text(0.01, 0.97, letter, ha="left", va="top", weight="bold", fontsize=9.2, transform=ax.transAxes)
        ax.text(0.57, 0.97, title, ha="center", va="top", weight="bold", fontsize=7.5, transform=ax.transAxes)

    ax = axes[0]
    box(ax, 0.17, 0.69, 0.66, 0.13, "Question +\nfull context", fill="0.94", fs=7.5)
    box(ax, 0.22, 0.42, 0.56, 0.15, "Model-controlled\nreasoning")
    box(ax, 0.17, 0.15, 0.66, 0.14, "Answer + evidence\n+ program", fill="0.94")
    arrow(ax, 0.5, 0.69, 0.5, 0.57)
    arrow(ax, 0.5, 0.42, 0.5, 0.29)
    ax.text(0.5, 0.055, "1 model call / item", ha="center", va="center", fontsize=7.7, transform=ax.transAxes)

    ax = axes[1]
    box(ax, 0.16, 0.75, 0.68, 0.11, "Question + full context", fill="0.94", fs=7.1)
    box(ax, 0.27, 0.49, 0.46, 0.14, "Single\nmodel agent")
    box(ax, 0.02, 0.22, 0.42, 0.13, "Document\nsearch", fill="0.86", fs=7.2)
    box(ax, 0.56, 0.22, 0.42, 0.13, "Constrained\nexecutor", fill="0.86", fs=7.2)
    arrow(ax, 0.5, 0.75, 0.5, 0.63)
    arrow(ax, 0.39, 0.49, 0.24, 0.35)
    arrow(ax, 0.61, 0.49, 0.77, 0.35)
    arrow(ax, 0.24, 0.35, 0.39, 0.49, style="->", dashed=True)
    arrow(ax, 0.77, 0.35, 0.61, 0.49, style="->", dashed=True)
    box(ax, 0.16, 0.03, 0.68, 0.12, "Held-out comparison\nPASS", fill="0.78", lw=1.2, fs=7.2)
    arrow(ax, 0.5, 0.49, 0.5, 0.15)

    ax = axes[2]
    box(ax, 0.08, 0.77, 0.84, 0.10, "Task contract", fill="white")
    box(ax, 0.03, 0.55, 0.42, 0.11, "Evidence /\nsolver", fill="white", fs=7.0)
    box(ax, 0.55, 0.55, 0.42, 0.11, "Candidate\nchecker", fill="white", fs=7.0)
    box(ax, 0.26, 0.33, 0.48, 0.11, "Final verifier", fill="white")
    arrow(ax, 0.5, 0.77, 0.24, 0.66)
    arrow(ax, 0.5, 0.77, 0.76, 0.66)
    arrow(ax, 0.24, 0.55, 0.42, 0.44)
    arrow(ax, 0.76, 0.55, 0.58, 0.44)
    box(ax, 0.10, 0.06, 0.80, 0.15, "Development only\nstructural gate: FAIL", fill="0.90", lw=1.2)
    arrow(ax, 0.5, 0.33, 0.5, 0.21)

    fig.suptitle("Architecture ladder and evidential boundary", y=1.015, fontsize=10.2, weight="bold")
    save_all(fig, "figure1_architecture_ladder_v1")


def figure2_preregistered_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.25))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    xs = [0.02, 0.19, 0.36, 0.53, 0.70, 0.87]
    widths = [0.12, 0.12, 0.12, 0.12, 0.12, 0.11]
    labels = [
        "FinQA test\n1,147 items",
        "Frozen\nstratified sample\nn=500",
        "Answer-stripped\ninference\ninputs",
        "Interleaved\npaired B0/B1\nschedule",
        "Immutable\npredictions\n+ hashes",
        "Delayed gold\nevaluation",
    ]
    fills = ["0.96", "0.90", "0.90", "0.90", "0.82", "0.90"]
    for x, w, label, fill in zip(xs, widths, labels, fills):
        box(ax, x, 0.58, w, 0.18, label, fill=fill, fs=6.35)
    for i in range(len(xs) - 1):
        arrow(ax, xs[i] + widths[i], 0.67, xs[i + 1], 0.67)

    box(ax, 0.02, 0.24, 0.19, 0.16, "Freeze package\ninputs + configs + schedule\n+ failure rules", fill="0.94", fs=6.7)
    arrow(ax, 0.115, 0.40, 0.25, 0.58)

    box(ax, 0.40, 0.24, 0.20, 0.16, "Structural gate\ncompleteness + hashes\n+ order + model ID", fill="0.80", fs=7.4, lw=1.2)
    arrow(ax, 0.76, 0.58, 0.55, 0.40)
    arrow(ax, 0.60, 0.32, 0.925, 0.58)
    ax.text(0.68, 0.40, "PASS", ha="center", va="center", fontsize=7.2, weight="bold", transform=ax.transAxes)

    box(ax, 0.69, 0.08, 0.28, 0.17, "FAIL: stop or dated amendment\nFull paired schedule rerun\nNo selective item reruns", fill="0.96", fs=7.4)
    arrow(ax, 0.60, 0.29, 0.69, 0.19, dashed=True)
    ax.text(0.635, 0.21, "FAIL", ha="center", va="center", fontsize=7.2, weight="bold", transform=ax.transAxes)

    box(ax, 0.23, 0.05, 0.32, 0.11, "Registered stability subset: n=100\nR1 + order-reversed R2/R3", fill="0.94", fs=7.3)
    arrow(ax, 0.42, 0.58, 0.39, 0.16, dashed=True)

    ax.text(0.5, 0.93, "Inference and evaluation remain isolated until structural acceptance", ha="center", va="center", fontsize=10.0, weight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.86, "Solid arrows: confirmatory path   |   Dashed arrows: prespecified branch or descriptive stability path", ha="center", va="center", fontsize=7.5, transform=ax.transAxes)
    save_all(fig, "figure2_preregistered_pipeline_v1")


def figure3_quality_cost_profile() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1.05, 1.0], "wspace": 0.35})

    tokens_m = [1.603138, 3.856862]
    accuracy = [42.0, 47.0]
    ax1.plot(tokens_m, accuracy, color="0.35", linewidth=1.1, zorder=1)
    ax1.scatter(tokens_m[0], accuracy[0], marker="o", s=55, facecolor="white", edgecolor="0.1", linewidth=1.2, label="B0 direct LLM", zorder=3)
    ax1.scatter(tokens_m[1], accuracy[1], marker="s", s=55, facecolor="0.35", edgecolor="0.1", linewidth=1.0, label="B1 tool-augmented", zorder=3)
    ax1.annotate("+5.0 pp", xy=(3.856862, 47.0), xytext=(2.55, 45.0), arrowprops={"arrowstyle": "->", "color": "0.25", "lw": 0.9}, fontsize=8.2)
    ax1.set_xlabel("Total tokens (millions)")
    ax1.set_ylabel("Final-answer accuracy (%)")
    ax1.set_xlim(1.25, 4.15)
    ax1.set_ylim(39.5, 49.0)
    ax1.set_xticks([1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
    ax1.grid(axis="both", color="0.88", linewidth=0.6)
    ax1.legend(loc="lower right", frameon=False)
    ax1.set_title("A  Observed quality–token profile", loc="left", weight="bold")
    ax1.text(0.01, -0.23, "Two observed systems; not an efficiency frontier", transform=ax1.transAxes, fontsize=7.4)

    labels = ["Accuracy", "Model calls", "Tokens", "Latency"]
    ratios = [47.0 / 42.0, 3.22, 2.41, 1.12]
    y = list(range(len(labels)))
    bars = ax2.barh(y, ratios, color=["0.72", "0.35", "0.50", "0.82"], edgecolor="0.15", linewidth=0.7)
    hatches = ["//", "xx", "..", "\\\\"]
    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)
    ax2.axvline(1.0, color="0.15", linewidth=0.9, linestyle="--")
    ax2.set_yticks(y, labels)
    ax2.invert_yaxis()
    ax2.set_xlim(0, 3.55)
    ax2.set_xlabel("B1 / B0 ratio")
    ax2.grid(axis="x", color="0.88", linewidth=0.6)
    ax2.set_title("B  Resource change relative to B0", loc="left", weight="bold")
    value_labels = ["1.12× (+5.0 pp)", "3.22×", "2.41×", "1.12×"]
    for bar, label in zip(bars, value_labels):
        ax2.text(bar.get_width() + 0.06, bar.get_y() + bar.get_height() / 2, label, va="center", fontsize=7.8)

    fig.suptitle("Held-out quality and resource profile (n=500 paired items)", y=1.02, fontsize=10.2, weight="bold")
    save_all(fig, "figure3_quality_cost_profile_v1")


def main() -> int:
    setup_style()
    figure1_architecture_ladder()
    figure2_preregistered_pipeline()
    figure3_quality_cost_profile()
    for path in sorted(OUTPUT_DIR.glob("figure*_v1.*")):
        print(path.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
