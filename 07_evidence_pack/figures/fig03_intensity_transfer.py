#!/usr/bin/env python3
"""Generate the intensity-stratified W1, W3, and B1 comparison."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_primary_by_intensity.csv"
OUTPUT = ROOT / "07_evidence_pack/figures/fig03_intensity_transfer.png"
MODELS = ["W1", "W3", "B1"]
STYLE = {
    "W1": {"color": "#0072B2", "marker": "o", "label": "W1"},
    "W3": {"color": "#D55E00", "marker": "^", "label": "W3"},
    "B1": {"color": "#009E73", "marker": "s", "label": "B1"},
}


def main() -> None:
    data = pd.read_csv(SOURCE)
    data = data.loc[data["model_label"].isin(MODELS)].copy()
    intensities = sorted(data["I"].unique())
    if len(intensities) != 10:
        raise RuntimeError(f"Expected 10 intensity groups, found {len(intensities)}")
    for model in MODELS:
        group = data.loc[data["model_label"] == model]
        if len(group) != 10 or group["n_plants"].sum() != 268:
            raise RuntimeError(f"Unexpected primary-by-intensity rows for {model}")

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 7.2,
        "axes.labelsize": 7.2,
        "xtick.labelsize": 6.4,
        "ytick.labelsize": 6.7,
        "legend.fontsize": 6.5,
        "axes.linewidth": 0.8,
    })
    fig, ax = plt.subplots(figsize=(85 / 25.4, 70 / 25.4))
    for model in MODELS:
        group = data.loc[data["model_label"] == model].sort_values("I")
        style = STYLE[model]
        ax.plot(
            group["I"], group["median_rmse_deg"],
            color=style["color"], marker=style["marker"], markersize=3.6,
            markeredgecolor="white", markeredgewidth=0.35, linewidth=1.2,
            linestyle="-", label=style["label"], zorder=3,
        )
    ax.axhline(
        9.73, color="#4D4D4D", linewidth=0.9, linestyle="-",
        label="Fixed threshold (9.73 degrees)", zorder=1,
    )
    ticks = [0.7, 1.4, 2.25, 3.2, 4.4, 5.8]
    ax.set_xticks(ticks, [f"{value:g}" for value in ticks])
    ax.set_xlim(0.45, 6.05)
    ax.set_ylim(0, 19)
    ax.set_xlabel("Light intensity (W m$^{-2}$)")
    ax.set_ylabel("Median held-out RMSE (degrees)")
    ax.tick_params(direction="out", length=2.5, width=0.7, pad=2)
    ax.legend(loc="upper left", ncol=2, frameon=False, columnspacing=0.9,
              handlelength=1.4, borderaxespad=0.25)
    fig.tight_layout(pad=0.55)
    fig.savefig(OUTPUT, dpi=300, facecolor="white")
    plt.close(fig)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} at 300 dpi and 85 mm width")


if __name__ == "__main__":
    main()
