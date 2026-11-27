#!/usr/bin/env python3
"""Generate per-plant Phase E held-out RMSE distributions."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_heldout_per_plant.csv"
OUTPUT = ROOT / "07_evidence_pack/figures/fig02_external_benchmark_rmse.png"
ORDER = ["W1", "W2", "W3", "B1", "B1r", "B2"]
PALETTE = ["#0072B2", "#56B4E9", "#D55E00", "#009E73", "#E69F00", "#CC79A7"]


def main() -> None:
    data = pd.read_csv(SOURCE)
    groups = [data.loc[data["model_label"] == model, "rmse_deg"].to_numpy(float)
              for model in ORDER]
    counts = [len(values) for values in groups]
    if counts != [268] * 6:
        raise RuntimeError(f"Expected 268 held-out plants per model, found {counts}")

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 7.2,
        "axes.labelsize": 7.2,
        "xtick.labelsize": 6.8,
        "ytick.labelsize": 6.6,
        "legend.fontsize": 6.3,
        "axes.linewidth": 0.8,
    })
    fig, ax = plt.subplots(figsize=(85 / 25.4, 70 / 25.4))
    artists = ax.boxplot(
        groups,
        positions=range(1, len(ORDER) + 1),
        widths=0.58,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "#222222", "linewidth": 1.0, "linestyle": "-"},
        whiskerprops={"color": "#555555", "linewidth": 0.8, "linestyle": "-"},
        capprops={"color": "#555555", "linewidth": 0.8, "linestyle": "-"},
        boxprops={"edgecolor": "#444444", "linewidth": 0.8},
    )
    for patch, color in zip(artists["boxes"], PALETTE):
        patch.set_facecolor(color)
        patch.set_alpha(0.9)
    threshold = ax.axhline(
        9.73, color="#333333", linewidth=1.0, linestyle="-",
        label="Fixed threshold (9.73 degrees)", zorder=0,
    )
    ax.set_xticks(range(1, len(ORDER) + 1), ORDER)
    ax.set_xlim(0.45, 6.55)
    ax.set_ylim(0, 38)
    ax.set_xlabel("Model")
    ax.set_ylabel("Per-plant held-out RMSE (degrees)")
    ax.tick_params(direction="out", length=2.5, width=0.7, pad=2)
    ax.legend(handles=[threshold], loc="upper right", frameon=False,
              handlelength=1.6, borderaxespad=0.25)
    fig.tight_layout(pad=0.55)
    fig.savefig(OUTPUT, dpi=300, facecolor="white")
    plt.close(fig)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} at 300 dpi and 85 mm width")


if __name__ == "__main__":
    main()
