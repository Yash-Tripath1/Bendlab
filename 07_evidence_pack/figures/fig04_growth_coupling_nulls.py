#!/usr/bin/env python3
"""Generate conditional amended-null intervals for growth-angle coupling."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "07_evidence_pack"
SUMMARY = ROOT / "06_growth_coupling/outputs/analysis_results_amended.json"
DRAWS = ROOT / "06_growth_coupling/outputs/amended_task4_null_rhos.csv"
OUTPUT = EVIDENCE / "figures/fig04_growth_coupling_nulls.png"
GROUPS = [
    ("Fitted / axial", "fitted_eligible_rho_axial_length", "#0072B2"),
    ("Fitted / height", "fitted_eligible_rho_vertical_height", "#56B4E9"),
    ("Empirical / axial", "empirical_eligible_rho_axial_length", "#D55E00"),
    ("Empirical / height", "empirical_eligible_rho_vertical_height", "#E69F00"),
]


def main() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    draws = pd.read_csv(DRAWS)
    if len(draws) != 1000:
        raise RuntimeError(f"Expected 1000 amended null rows, found {len(draws)}")
    fit_sample = summary["task4_amendment"]["fitted_trajectory_pairing_null"]["eligible_excluded"]
    fit_simulation = fit_sample["simulation"]
    empirical = summary["task4_amendment"]["empirical_angle_projection_null"]["eligible_excluded"]
    n_fit = fit_sample["fit_metadata"]["matched_fit_rows"]
    n_empirical = empirical["n_plants"]
    if n_fit != 209 or n_empirical != 209:
        raise RuntimeError(f"Expected eligible sample n=209, found {n_fit} and {n_empirical}")
    observed = float(fit_simulation["axial_length"]["observed_rho"])
    if abs(observed - float(empirical["observed_partial_rho"])) > 1e-12:
        raise RuntimeError("Fitted and empirical null summaries have different observed rho")

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 7.0,
        "axes.labelsize": 7.1,
        "xtick.labelsize": 6.5,
        "ytick.labelsize": 6.4,
        "legend.fontsize": 6.2,
        "axes.linewidth": 0.8,
    })
    fig, ax = plt.subplots(figsize=(85 / 25.4, 72 / 25.4))
    positions = [3, 2, 1, 0]
    for position, (label, column, color) in zip(positions, GROUPS):
        values = draws[column].to_numpy(float)
        low, median, high = np.quantile(values, [0.025, 0.5, 0.975])
        ax.hlines(position, low, high, color=color, linewidth=2.0, linestyle="-", zorder=2)
        ax.plot(median, position, marker="o", markersize=4.0, color=color,
                markeredgecolor="white", markeredgewidth=0.35, linestyle="none", zorder=3)
    ax.axvline(observed, color="#333333", linewidth=1.0, linestyle="-", zorder=1)
    ax.set_yticks(positions, [group[0] for group in GROUPS])
    ax.set_xlim(-0.43, 0.73)
    ax.set_ylim(-0.55, 3.55)
    ax.set_xlabel("Partial Spearman rho")
    ax.tick_params(direction="out", length=2.5, width=0.7, pad=2)
    handles = [
        Line2D([0], [0], color="#555555", marker="o", markersize=3.5,
               linewidth=2.0, linestyle="-", label="Median and central 95% null interval"),
        Line2D([0], [0], color="#333333", linewidth=1.0, linestyle="-",
               label=f"Observed rho = {observed:+.3f}"),
    ]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.99),
               ncol=2, frameon=False, handlelength=1.35, columnspacing=0.8)
    fig.subplots_adjust(left=0.35, right=0.97, bottom=0.20, top=0.82)
    fig.savefig(OUTPUT, dpi=300, facecolor="white")
    plt.close(fig)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} at 300 dpi and 85 mm width")


if __name__ == "__main__":
    main()
