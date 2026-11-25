"""Paired plant-level comparisons from committed Phase E predictions.

This script reads the committed held-out per-plant CSV. It does not fit or
refit any model. It appends paired comparison statistics to the existing
Phase E machine-readable summary without changing its prior keys.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE / "outputs"
PER_PLANT = OUTPUTS / "phase_e_w3_heldout_per_plant.csv"
SUMMARY = OUTPUTS / "phase_e_w3_summary.json"
BOOTSTRAP_SEED = 0
BOOTSTRAP_RESAMPLES = 2000

W3 = "W3_gammaI_phiLight90"
W2 = "W2_bendlab_kI_phiI_diagnostic"
W1 = "W1_bendlab_kI_phi90"
B1 = "B1_group_mean_curve"


def paired_difference(pivot, left, right):
    difference = pivot[left].to_numpy(float) - pivot[right].to_numpy(float)
    test = wilcoxon(
        difference,
        alternative="two-sided",
        zero_method="wilcox",
        method="auto",
    )
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    bootstrap_medians = np.empty(BOOTSTRAP_RESAMPLES, dtype=float)
    for b in range(BOOTSTRAP_RESAMPLES):
        sample = rng.choice(difference, size=len(difference), replace=True)
        bootstrap_medians[b] = np.median(sample)
    ci = np.percentile(bootstrap_medians, [2.5, 97.5])
    return {
        "left_model": left,
        "right_model": right,
        "difference_definition": f"{left} rmse_deg minus {right} rmse_deg",
        "n_plants": int(len(difference)),
        "median_difference_deg": float(np.median(difference)),
        "mean_difference_deg": float(np.mean(difference)),
        "left_model_worse_n": int(np.sum(difference > 0.0)),
        "left_model_worse_percent": float(100.0 * np.mean(difference > 0.0)),
        "left_model_improves_n": int(np.sum(difference < 0.0)),
        "left_model_improves_percent": float(100.0 * np.mean(difference < 0.0)),
        "wilcoxon_statistic": float(test.statistic),
        "wilcoxon_p_two_sided": float(test.pvalue),
        "bootstrap_median_difference_ci95_deg": [float(ci[0]), float(ci[1])],
        "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "wilcoxon_method": "two-sided signed-rank, zero_method=wilcox, method=auto",
    }


def main():
    frame = pd.read_csv(PER_PLANT)
    pivot = frame.pivot(index="plant", columns="model", values="rmse_deg").sort_index()
    required = [W1, W2, W3, B1]
    missing = [name for name in required if name not in pivot.columns]
    if missing:
        raise ValueError(f"Missing models in per-plant CSV: {missing}")
    if len(pivot) != 268 or pivot[required].isna().any().any():
        raise ValueError("Expected complete paired predictions for 268 plants")

    results = {
        "source_csv": str(PER_PLANT.relative_to(HERE.parent.parent)),
        "n_plants": int(len(pivot)),
        "paired_rmse_differences": {
            "W3_minus_B1": paired_difference(pivot, W3, B1),
            "W2_minus_B1": paired_difference(pivot, W2, B1),
            "W3_minus_W1": paired_difference(pivot, W3, W1),
        },
        "interpretation": (
            "Positive differences indicate higher RMSE for the left model. "
            "Improvement percentages count negative paired differences."
        ),
    }

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    previous_keys = set(summary)
    summary["paired_equivalence"] = results
    SUMMARY.write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    saved = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if set(saved) != previous_keys | {"paired_equivalence"}:
        raise AssertionError("Unexpected summary keys after appending comparisons")
    print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
