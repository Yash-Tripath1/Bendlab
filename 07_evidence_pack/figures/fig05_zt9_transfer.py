#!/usr/bin/env python3
"""Generate paired held-out ZT9 errors for the base and shared-clock models."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "results/clock_validation_shared_heldout.csv"
OUTPUT = ROOT / "07_evidence_pack/figures/fig05_zt9_transfer.png"


def main() -> None:
    data = pd.read_csv(SOURCE).sort_values("plant")
    if len(data) != 6 or data["plant"].nunique() != 6:
        raise RuntimeError(f"Expected six unique held-out ZT9 plants, found {len(data)}")
    if not (data["shared_clock_rmse_heldout"] < data["static_rmse"]).all():
        raise RuntimeError("The saved output does not show improvement for all six plants")

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 7.2,
        "axes.labelsize": 7.2,
        "xtick.labelsize": 6.8,
        "ytick.labelsize": 6.5,
        "legend.fontsize": 6.5,
        "axes.linewidth": 0.8,
    })
    fig, ax = plt.subplots(figsize=(85 / 25.4, 66 / 25.4))
    for row in data.itertuples():
        ax.plot(
            [0, 1], [row.static_rmse, row.shared_clock_rmse_heldout],
            color="#888888", linewidth=0.85, linestyle="-", zorder=1,
        )
    ax.scatter([0] * len(data), data["static_rmse"], s=20, marker="o",
               color="#0072B2", edgecolor="white", linewidth=0.35, zorder=3)
    ax.scatter([1] * len(data), data["shared_clock_rmse_heldout"], s=22,
               marker="s", color="#D55E00", edgecolor="white", linewidth=0.35,
               zorder=3)
    ax.set_xticks([0, 1], ["Base scalar", "Shared clock"])
    ax.set_xlim(-0.25, 1.25)
    ax.set_ylim(0, 8)
    ax.set_xlabel("Model")
    ax.set_ylabel("Held-out per-plant RMSE (degrees)")
    ax.tick_params(direction="out", length=2.5, width=0.7, pad=2)
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#0072B2",
               markeredgecolor="white", markersize=4.5, label="Base scalar"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="#D55E00",
               markeredgecolor="white", markersize=4.5, label="Shared clock"),
    ]
    ax.legend(handles=handles, loc="upper right", frameon=False,
              handletextpad=0.4, borderaxespad=0.25)
    fig.tight_layout(pad=0.55)
    fig.savefig(OUTPUT, dpi=300, facecolor="white")
    plt.close(fig)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} at 300 dpi and 85 mm width")


if __name__ == "__main__":
    main()
