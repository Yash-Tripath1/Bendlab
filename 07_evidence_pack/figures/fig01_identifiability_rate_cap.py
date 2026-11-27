#!/usr/bin/env python3
"""Generate the saved-fit versus observed-peak rate-cap figure."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "07_evidence_pack"
SOURCE = EVIDENCE / "outputs/identifiability_count.json"
OUTPUT = EVIDENCE / "figures/fig01_identifiability_rate_cap.png"
BLUE = "#0072B2"
VERMILLION = "#D55E00"
DARK = "#4D4D4D"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = data["per_plant"]
    if len(rows) != 48:
        raise RuntimeError(f"Expected 48 plants, found {len(rows)}")
    above = [row for row in rows if row["fitted_cap_exceeds_observed_peak"]]
    at_or_below = [row for row in rows if row["cap_at_or_below_observed_peak"]]
    if (len(above), len(at_or_below)) != (40, 8):
        raise RuntimeError("Saved identifiability counts do not match 40 and 8")

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 7.2,
        "axes.labelsize": 7.2,
        "xtick.labelsize": 6.6,
        "ytick.labelsize": 6.6,
        "legend.fontsize": 6.2,
        "axes.linewidth": 0.8,
    })
    fig, ax = plt.subplots(figsize=(85 / 25.4, 70 / 25.4))
    ax.scatter(
        [row["observed_peak_adjacent_rate_deg_h"] for row in above],
        [row["fitted_max_rate_deg_h"] for row in above],
        s=20, marker="o", color=BLUE, edgecolor="white", linewidth=0.35,
        label="Cap above observed peak (n=40)", zorder=3,
    )
    ax.scatter(
        [row["observed_peak_adjacent_rate_deg_h"] for row in at_or_below],
        [row["fitted_max_rate_deg_h"] for row in at_or_below],
        s=25, marker="^", color=VERMILLION, edgecolor="white", linewidth=0.35,
        label="Cap at or below peak (n=8)", zorder=3,
    )
    ax.plot([0, 200], [0, 200], color=DARK, linewidth=0.9,
            linestyle="-", label="1:1 reference", zorder=1)
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 200)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Maximum observed adjacent-sample rate\n(degrees per hour)")
    ax.set_ylabel("Fitted max_rate\n(degrees per hour)")
    ax.tick_params(direction="out", length=2.5, width=0.7, pad=2)
    ax.legend(loc="lower right", frameon=False, handletextpad=0.45,
              borderaxespad=0.3, labelspacing=0.35)
    fig.tight_layout(pad=0.55)
    fig.savefig(OUTPUT, dpi=300, facecolor="white")
    plt.close(fig)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} at 300 dpi and 85 mm width")


if __name__ == "__main__":
    main()
