"""Supporting Phase E partial-Spearman associations from the archive.

This script performs no dynamical model fitting. It joins the frozen
trajectory and length files, derives per-plant outcomes, and estimates
rank-based partial correlations with plant-level bootstrap intervals.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parents[1]
TRAJECTORY_FILE = (
    PKG_ROOT / "growth_phase" / "data" / "00_Data" / "uni_trajectories.csv"
)
LENGTH_FILE = (
    PKG_ROOT / "growth_phase" / "data" / "07_Supplementary" / "length_est_data.csv"
)
OUTPUT_DIR = HERE / "outputs"
SEED = 7
N_BOOT = 1000


def derive_trajectory_outcomes(path):
    trajectories = pd.read_csv(path)
    rows = []
    for plant_id, group in trajectories.sort_values(["real_id", "dt"]).groupby(
        "real_id", sort=True
    ):
        if group["light_i"].nunique() != 1:
            raise ValueError(f"Plant {plant_id} has multiple trajectory intensities")
        t = group["dt"].to_numpy(float)
        theta = group["theta"].to_numpy(float)
        initial = np.isclose(t, 0.0)
        plateau = (t >= 16.0) & (t <= 21.0)
        if not initial.any() or not plateau.any():
            raise ValueError(f"Plant {plant_id} lacks a required angle window")
        rows.append({
            "real_id": plant_id,
            "intensity_w_m2": float(group["light_i"].iloc[0]),
            "theta0_deg": float(theta[initial][0]),
            "plateau_16_21_deg": float(theta[plateau].mean()),
            "trajectory_duration_h": float(t.max()),
        })
    return pd.DataFrame(rows), trajectories


def join_length_data(trajectory_outcomes, path):
    raw = pd.read_csv(path)
    identity_columns = [c for c in raw.columns if c != "Unnamed: 0"]
    duplicate_ids = sorted(
        raw.loc[raw["real_id"].duplicated(keep=False), "real_id"].unique().tolist()
    )
    for plant_id in duplicate_ids:
        variants = raw.loc[raw["real_id"] == plant_id, identity_columns].drop_duplicates()
        if len(variants) != 1:
            raise ValueError(f"Duplicate length rows differ for {plant_id}")
    lengths = raw.drop_duplicates(subset=identity_columns).copy()
    merged = trajectory_outcomes.merge(lengths, on="real_id", how="inner", validate="one_to_one")
    if not np.allclose(merged["light_intens"] / 100.0,
                       merged["intensity_w_m2"], rtol=0.0, atol=1e-12):
        raise ValueError("Length and trajectory intensity values do not match")
    if (merged["dt"] <= 0).any():
        raise ValueError("Length interval must be positive")
    merged["L0_mm"] = merged["length_start"].astype(float)
    merged["elongation_rate_mm_h"] = (
        merged["length_finish"].astype(float) - merged["length_start"].astype(float)
    ) / merged["dt"].astype(float)
    if (merged[["L0_mm", "intensity_w_m2"]] <= 0).any().any():
        raise ValueError("Log-transformed covariates must be positive")
    merged["log_intensity"] = np.log(merged["intensity_w_m2"])
    merged["log_L0"] = np.log(merged["L0_mm"])
    return merged, raw, duplicate_ids


def partial_spearman(data, predictor, outcome, controls):
    """Rank variables, residualize predictor and outcome, then correlate."""
    ranked_x = rankdata(data[predictor].to_numpy(float), method="average")
    ranked_y = rankdata(data[outcome].to_numpy(float), method="average")
    ranked_controls = [
        rankdata(data[column].to_numpy(float), method="average")
        for column in controls
    ]
    design = np.column_stack([np.ones(len(data)), *ranked_controls])
    resid_x = ranked_x - design @ np.linalg.lstsq(design, ranked_x, rcond=None)[0]
    resid_y = ranked_y - design @ np.linalg.lstsq(design, ranked_y, rcond=None)[0]
    if np.std(resid_x) == 0.0 or np.std(resid_y) == 0.0:
        return float("nan")
    return float(np.corrcoef(resid_x, resid_y)[0, 1])


def bootstrap_partial_spearman(data, predictor, outcome, controls, rng):
    estimate = partial_spearman(data, predictor, outcome, controls)
    draws = np.empty(N_BOOT, dtype=float)
    n = len(data)
    for b in range(N_BOOT):
        sampled = data.iloc[rng.integers(0, n, size=n)].reset_index(drop=True)
        draws[b] = partial_spearman(sampled, predictor, outcome, controls)
    ci = np.nanpercentile(draws, [2.5, 97.5])
    return {
        "estimate": estimate,
        "ci95_percentile": [float(ci[0]), float(ci[1])],
        "bootstrap_replicates": N_BOOT,
        "bootstrap_valid_replicates": int(np.isfinite(draws).sum()),
        "controls": controls,
        "method": "partial Spearman via ranked-variable OLS residualization",
    }


def main():
    started = time.perf_counter()
    outcomes, trajectories = derive_trajectory_outcomes(TRAJECTORY_FILE)
    paired, raw_lengths, duplicate_ids = join_length_data(outcomes, LENGTH_FILE)
    if len(paired) != 213:
        raise RuntimeError(f"Expected 213 matched plants, found {len(paired)}")

    rng = np.random.default_rng(SEED)
    outcome = "plateau_16_21_deg"
    results = {
        "elongation_rate_vs_plateau": bootstrap_partial_spearman(
            paired,
            "elongation_rate_mm_h",
            outcome,
            ["theta0_deg", "log_intensity", "log_L0"],
            rng,
        ),
        "starting_length_vs_plateau": bootstrap_partial_spearman(
            paired,
            "log_L0",
            outcome,
            ["theta0_deg", "log_intensity", "elongation_rate_mm_h"],
            rng,
        ),
    }
    runtime = time.perf_counter() - started
    result = {
        "analysis": "Phase E supporting partial-Spearman associations",
        "trajectory_file": str(TRAJECTORY_FILE.relative_to(PKG_ROOT)),
        "length_file": str(LENGTH_FILE.relative_to(PKG_ROOT)),
        "trajectory_plants": int(outcomes["real_id"].nunique()),
        "trajectory_rows": int(len(trajectories)),
        "length_rows_raw": int(len(raw_lengths)),
        "length_unique_ids": int(raw_lengths["real_id"].nunique()),
        "matched_plants": int(len(paired)),
        "exact_duplicate_length_ids_removed": duplicate_ids,
        "intensity_conversion_verified": True,
        "outcome_definition": "mean theta from 16 through 21 hours inclusive, degrees",
        "elongation_definition": "(length_finish - length_start) / length dt, mm per hour",
        "starting_length_definition": "length_start, mm",
        "seed": SEED,
        "runtime_seconds": float(runtime),
        "results": results,
        "limitations": [
            "length_est_data provides one net elongation over the full measurement interval, not a time-resolved growth rate",
            "the paired analysis is limited to plants with a length record",
            "associations are conditional and do not establish causation or mechanism",
        ],
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paired.sort_values("real_id").to_csv(
        OUTPUT_DIR / "phase_e_supporting_associations_plants.csv", index=False
    )
    (OUTPUT_DIR / "phase_e_supporting_associations.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
