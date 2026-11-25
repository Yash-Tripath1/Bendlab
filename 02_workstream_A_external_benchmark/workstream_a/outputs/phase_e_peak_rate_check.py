"""Measure smoothed observed peak bend rates in the external archive.

Each trajectory is smoothed with a centred five-observation rolling mean,
roughly 20 minutes at the archive sampling cadence. A numerical derivative
uses the observed time values in hours. This script does not fit a model.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

OUTPUT_DIR = Path(__file__).resolve().parent
REPO_ROOT = OUTPUT_DIR.parents[2]
DATA_FILE = REPO_ROOT / "05_data_external" / "uni_trajectories.csv"
W3_SUMMARY_FILE = OUTPUT_DIR / "phase_e_w3_summary.json"
OUTPUT_FILE = OUTPUT_DIR / "phase_e_peak_rate_check.json"
ROLLING_WINDOW_OBSERVATIONS = 5


def per_plant_peak_rates(data):
    rows = []
    for plant_id, group in data.sort_values(["real_id", "dt"]).groupby(
        "real_id", sort=True
    ):
        times = group["dt"].to_numpy(dtype=float)
        theta = group["theta"].to_numpy(dtype=float)
        smoothed = (
            pd.Series(theta)
            .rolling(
                window=ROLLING_WINDOW_OBSERVATIONS,
                center=True,
                min_periods=ROLLING_WINDOW_OBSERVATIONS,
            )
            .mean()
            .to_numpy(dtype=float)
        )
        valid = np.isfinite(smoothed)
        if np.count_nonzero(valid) < 3:
            raise ValueError(f"Too few smoothed points for plant {plant_id}")
        rate_deg_h = np.gradient(smoothed[valid], times[valid])
        rows.append({
            "real_id": str(plant_id),
            "n_observations": int(len(group)),
            "n_smoothed_observations": int(np.count_nonzero(valid)),
            "peak_absolute_rate_deg_h": float(np.max(np.abs(rate_deg_h))),
        })
    return rows


def main():
    data = pd.read_csv(DATA_FILE)
    summary = json.loads(W3_SUMMARY_FILE.read_text(encoding="utf-8"))
    fitted_cap = float(
        summary["all_data_w3_fit"]["parameters_physical"]["max_rate"]
    )
    peaks = per_plant_peak_rates(data)
    values = np.asarray([row["peak_absolute_rate_deg_h"] for row in peaks])
    exceeding = int(np.sum(values > fitted_cap))
    result = {
        "analysis": "Observed per-plant peak bend-rate check",
        "data_file": str(DATA_FILE.relative_to(REPO_ROOT)),
        "n_plants": int(len(peaks)),
        "smoothing": {
            "method": "centred rolling arithmetic mean",
            "window_observations": ROLLING_WINDOW_OBSERVATIONS,
            "nominal_duration_minutes": 20,
            "edge_handling": "incomplete centered windows excluded",
        },
        "derivative": "numpy.gradient of smoothed angle with observed time in hours",
        "peak_definition": "maximum absolute smoothed derivative per plant, degrees per hour",
        "fitted_w3_max_rate_deg_h": fitted_cap,
        "median_peak_rate_deg_h": float(np.median(values)),
        "p90_peak_rate_deg_h": float(np.percentile(values, 90)),
        "maximum_peak_rate_deg_h": float(np.max(values)),
        "plants_exceeding_fitted_max_rate_n": exceeding,
        "plants_exceeding_fitted_max_rate_percent": float(100.0 * exceeding / len(peaks)),
        "per_plant_peak_rates": peaks,
    }
    OUTPUT_FILE.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
