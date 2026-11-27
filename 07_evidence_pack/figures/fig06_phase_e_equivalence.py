#!/usr/bin/env python3
"""Plot paired Phase E W3 and B1 held-out errors without refitting models."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    ROOT
    / "02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_heldout_per_plant.csv"
)
SUMMARY = ROOT / "02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json"
OUTPUT = ROOT / "07_evidence_pack/figures/fig06_phase_e_equivalence.png"

W3 = "W3_gammaI_phiLight90"
B1 = "B1_group_mean_curve"
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 0
TOLERANCE = 1e-6

# Okabe-Ito color-blind safe palette.
BLUE = "#0072B2"
VERMILLION = "#D55E00"
SKY_BLUE = "#56B4E9"
GREEN = "#009E73"
DARK = "#4D4D4D"


def load_and_validate_paired_statistics():
    """Recompute the saved paired median and percentile bootstrap interval."""
    frame = pd.read_csv(SOURCE)
    paired = frame.pivot(index="plant", columns="model", values="rmse_deg").sort_index()
    if W3 not in paired.columns or B1 not in paired.columns:
        raise ValueError(f"Required model columns are absent from {SOURCE}")
    if paired[[W3, B1]].isna().any().any():
        raise ValueError(f"Incomplete W3/B1 plant pairs in {SOURCE}")
    if not np.isfinite(paired[[W3, B1]].to_numpy(float)).all():
        raise ValueError(f"Non-finite W3/B1 RMSE values in {SOURCE}")

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    reference = summary["paired_equivalence"]["paired_rmse_differences"]["W3_minus_B1"]
    if reference["left_model"] != W3 or reference["right_model"] != B1:
        raise ValueError(f"Unexpected paired model order in {SUMMARY}")
    if (
        int(reference["bootstrap_resamples"]) != BOOTSTRAP_RESAMPLES
        or int(reference["bootstrap_seed"]) != BOOTSTRAP_SEED
    ):
        raise ValueError(
            f"Committed bootstrap settings in {SUMMARY} do not match "
            f"the required {BOOTSTRAP_RESAMPLES} resamples and seed {BOOTSTRAP_SEED}"
        )
    differences = paired[W3].to_numpy(float) - paired[B1].to_numpy(float)
    expected_n = int(reference["n_plants"])
    if len(differences) != expected_n or len(paired.index.unique()) != expected_n:
        raise AssertionError(
            f"Expected {expected_n} unique paired plants from {SOURCE}, found {len(differences)}"
        )

    median = float(np.median(differences))
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    bootstrap_medians = np.empty(BOOTSTRAP_RESAMPLES, dtype=float)
    for draw in range(len(bootstrap_medians)):
        sample = rng.choice(differences, size=len(differences), replace=True)
        bootstrap_medians[draw] = np.median(sample)
    interval = np.percentile(bootstrap_medians, [2.5, 97.5])

    expected_median = float(reference["median_difference_deg"])
    expected_interval = np.asarray(reference["bootstrap_median_difference_ci95_deg"], dtype=float)
    median_error = abs(median - expected_median)
    interval_error = float(np.max(np.abs(interval - expected_interval)))
    if not np.isfinite(expected_median) or not np.isfinite(median) or median_error > TOLERANCE:
        raise AssertionError(
            f"W3 minus B1 median mismatch: recomputed {median:.12f}, "
            f"committed {expected_median:.12f}; source {SOURCE}, reference {SUMMARY}"
        )
    if (
        expected_interval.shape != (2,)
        or not np.isfinite(expected_interval).all()
        or not np.isfinite(interval).all()
        or interval_error > TOLERANCE
    ):
        raise AssertionError(
            f"W3 minus B1 bootstrap interval mismatch: recomputed {interval.tolist()}, "
            f"committed {expected_interval.tolist()}; source {SOURCE}, reference {SUMMARY}"
        )

    worse = int(np.sum(differences > 0.0))
    improves = int(np.sum(differences < 0.0))
    if worse != int(reference["left_model_worse_n"]):
        raise AssertionError(
            f"Positive-difference plant count mismatch: recomputed {worse}, "
            f"committed {reference['left_model_worse_n']}"
        )
    if improves != int(reference["left_model_improves_n"]):
        raise AssertionError(
            f"Negative-difference plant count mismatch: recomputed {improves}, "
            f"committed {reference['left_model_improves_n']}"
        )
    return (
        paired[W3].to_numpy(float),
        paired[B1].to_numpy(float),
        differences,
        median,
        interval,
        worse,
        improves,
        reference,
    )


def main() -> None:
    # All statistic checks run before any figure or output file is created.
    (
        w3,
        b1,
        differences,
        median,
        interval,
        worse,
        improves,
        reference,
    ) = load_and_validate_paired_statistics()

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.0,
        "axes.labelsize": 8.2,
        "xtick.labelsize": 7.2,
        "ytick.labelsize": 7.2,
        "legend.fontsize": 7.0,
        "axes.linewidth": 0.8,
    })
    fig, (ax_pair, ax_difference) = plt.subplots(
        1, 2, figsize=(180 / 25.4, 82 / 25.4),
        gridspec_kw={"width_ratios": [1.0, 1.08]},
    )

    w3_better = differences < 0.0
    b1_better = differences > 0.0
    tied = differences == 0.0
    axis_max = max(float(np.max(w3)), float(np.max(b1))) * 1.04
    equal_line, = ax_pair.plot(
        [0.0, axis_max], [0.0, axis_max],
        color=DARK, linewidth=1.0, linestyle="-", zorder=1,
        label="equal performance",
    )
    w3_points = ax_pair.scatter(
        w3[w3_better], b1[w3_better], s=23, marker="o", color=BLUE,
        edgecolor="white", linewidth=0.35, alpha=0.88, zorder=3,
        label=f"W3 lower RMSE (n={improves})",
    )
    b1_points = ax_pair.scatter(
        w3[b1_better], b1[b1_better], s=23, marker="o", color=VERMILLION,
        edgecolor="white", linewidth=0.35, alpha=0.88, zorder=3,
        label=f"B1 lower RMSE (n={worse})",
    )
    handles = [equal_line, w3_points, b1_points]
    if np.any(tied):
        tie_points = ax_pair.scatter(
            w3[tied], b1[tied], s=27, marker="s", color=DARK,
            edgecolor="white", linewidth=0.35, zorder=4,
            label=f"Tied (n={int(tied.sum())})",
        )
        handles.append(tie_points)
    ax_pair.set_xlim(0.0, axis_max)
    ax_pair.set_ylim(0.0, axis_max)
    ax_pair.set_aspect("equal", adjustable="box")
    ax_pair.set_xlabel("W3 per-plant held-out RMSE (degrees)")
    ax_pair.set_ylabel("B1 per-plant held-out RMSE (degrees)")
    ax_pair.tick_params(direction="out", length=2.8, width=0.7, pad=2)
    ax_pair.legend(handles=handles, loc="upper left", frameon=False,
                   handletextpad=0.45, borderaxespad=0.25, labelspacing=0.35)

    counts, _, _ = ax_difference.hist(
        differences, bins="auto", color=SKY_BLUE, edgecolor=DARK,
        linewidth=0.55, alpha=0.88, zorder=2,
    )
    ax_difference.axvline(
        0.0, color=DARK, linewidth=1.0, linestyle="-",
        label="zero difference", zorder=1,
    )
    peak_count = max(float(np.max(counts)), 1.0)
    median_y = peak_count * 1.10
    ax_difference.errorbar(
        median, median_y,
        xerr=np.asarray([[median - interval[0]], [interval[1] - median]]),
        fmt="o", markersize=4.0, color=GREEN, ecolor=GREEN,
        elinewidth=1.5, capsize=3.0, capthick=1.2, linestyle="-",
        label="Median and 95% percentile bootstrap interval", zorder=4,
    )
    x_span = max(float(np.ptp(differences)), float(interval[1] - interval[0]))
    x_pad = 0.06 * x_span
    ax_difference.set_xlim(
        min(float(np.min(differences)), float(interval[0])) - x_pad,
        max(float(np.max(differences)), float(interval[1])) + x_pad,
    )
    ax_difference.set_ylim(0.0, peak_count * 1.35)
    ax_difference.set_xlabel("Paired difference, W3 minus B1 (degrees)")
    ax_difference.set_ylabel("Plants per bin (count)")
    ax_difference.tick_params(direction="out", length=2.8, width=0.7, pad=2)
    ax_difference.legend(loc="upper left", frameon=False,
                         handletextpad=0.45, borderaxespad=0.25, labelspacing=0.35)

    fig.tight_layout(pad=0.8, w_pad=1.5)
    fig.savefig(OUTPUT, dpi=300, facecolor="white")
    plt.close(fig)
    print(
        f"Assertions passed for {len(differences)} paired plants: "
        f"median={median:+.10f} degrees, "
        f"95% percentile bootstrap interval=[{interval[0]:+.10f}, {interval[1]:+.10f}] degrees, "
        f"resamples={BOOTSTRAP_RESAMPLES}, seed={BOOTSTRAP_SEED}; "
        f"matches {SUMMARY.relative_to(ROOT)} within {TOLERANCE:g}."
    )
    print(f"Wrote {OUTPUT.relative_to(ROOT)} at 300 dpi")


if __name__ == "__main__":
    main()
