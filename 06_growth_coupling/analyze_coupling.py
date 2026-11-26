#!/usr/bin/env python3
"""Read-only overlap and measurement-geometry analysis for Task 6.

All inputs are committed source data or committed diagnostic outputs. This
script writes only new artifacts under 06_growth_coupling/outputs/.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr, t as student_t

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "outputs"
TRAJECTORY_FILE = ROOT / "growth_phase/data/00_Data/uni_trajectories.csv"
LENGTH_FILE = ROOT / "growth_phase/data/07_Supplementary/length_est_data.csv"
FIT_FILE = ROOT / "02_workstream_A_external_benchmark/workstream_a/outputs/per_plant_fullfit_diagnostic.csv"
W1_FILE = ROOT / "02_workstream_A_external_benchmark/workstream_a/outputs/plant_heldout_per_plant.csv"
MODEL_DT = 1.0 / 60.0
N_BOOT = 1000
N_NULL = 1000
TASK3_SEED = 20261112
TASK4_SEED = 20261113
TASK5_SEED = 20261114

sys.path.insert(0, str(ROOT))
import sim  # noqa: E402


def json_number(value):
    value = float(value)
    return value if np.isfinite(value) else None


def derive_outcomes(trajectory_path: Path) -> tuple[pd.DataFrame, dict[str, tuple[np.ndarray, np.ndarray]]]:
    trajectories = pd.read_csv(trajectory_path)
    rows = []
    by_plant = {}
    for plant_id, group in trajectories.sort_values(["real_id", "dt"]).groupby("real_id", sort=True):
        if group["light_i"].nunique() != 1:
            raise ValueError(f"Plant {plant_id} has multiple light intensities")
        times = group["dt"].to_numpy(float)
        theta = group["theta"].to_numpy(float)
        initial = np.flatnonzero(np.isclose(times, 0.0))
        plateau = (times >= 16.0) & (times <= 21.0)
        if len(initial) == 0 or not plateau.any():
            raise ValueError(f"Plant {plant_id} lacks a required angle window")
        theta0 = float(theta[initial[0]])
        rows.append({
            "real_id": plant_id,
            "intensity_w_m2": float(group["light_i"].iloc[0]),
            "theta0_deg": theta0,
            "plateau_16_21_deg": float(theta[plateau].mean()),
            "phase_c_total_change_deg": float(theta[plateau].mean() - theta0),
            "theta_last_deg": float(theta[-1]),
            "total_angle_change_deg": float(theta[-1] - theta0),
            "peak_angle_deg": float(np.max(theta)),
            "peak_excursion_deg": float(np.max(theta) - theta0),
            "trajectory_end_h": float(times[-1]),
        })
        by_plant[plant_id] = (times, theta)
    return pd.DataFrame(rows), by_plant


def join_data(outcomes: pd.DataFrame, length_path: Path) -> tuple[pd.DataFrame, int]:
    raw = pd.read_csv(length_path)
    identity_columns = [column for column in raw.columns if column != "Unnamed: 0"]
    duplicate_ids = sorted(
        raw.loc[raw["real_id"].duplicated(keep=False), "real_id"].unique().tolist()
    )
    for plant_id in duplicate_ids:
        variants = raw.loc[raw["real_id"] == plant_id, identity_columns].drop_duplicates()
        if len(variants) != 1:
            raise ValueError(f"Non-identical duplicate length rows for {plant_id}")
    lengths = raw.drop_duplicates(subset=identity_columns).copy()
    paired = outcomes.merge(lengths, on="real_id", how="inner", validate="one_to_one")
    if len(paired) != 213:
        raise ValueError(f"Expected 213 paired plants, found {len(paired)}")
    if not np.allclose(paired["light_intens"] / 100.0,
                       paired["intensity_w_m2"], rtol=0.0, atol=1e-12):
        raise ValueError("Length and trajectory intensities do not match")
    if (paired["dt"] <= 0).any() or (paired["length_start"] <= 0).any():
        raise ValueError("Non-positive measurement interval or starting length")
    paired = paired.sort_values("real_id").reset_index(drop=True)
    paired["L0_mm"] = paired["length_start"].astype(float)
    paired["elongation_rate_mm_h"] = (
        paired["length_finish"].astype(float) - paired["length_start"].astype(float)
    ) / paired["dt"].astype(float)
    paired["log_intensity"] = np.log(paired["intensity_w_m2"].astype(float))
    paired["log_L0"] = np.log(paired["L0_mm"])
    return paired, len(duplicate_ids)


def partial_spearman(data: pd.DataFrame, predictor: str, outcome: str,
                     controls: list[str]) -> float:
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


def partial_with_t_p(data: pd.DataFrame, predictor: str, outcome: str,
                     controls: list[str]) -> dict:
    rho = partial_spearman(data, predictor, outcome, controls)
    df = len(data) - len(controls) - 2
    if not np.isfinite(rho):
        p_value = float("nan")
        statistic = float("nan")
    elif abs(rho) >= 1.0:
        p_value = 0.0
        statistic = float(np.copysign(np.inf, rho))
    else:
        statistic = rho * np.sqrt(df / (1.0 - rho * rho))
        p_value = float(2.0 * student_t.sf(abs(statistic), df=df))
    return {
        "rho": json_number(rho),
        "two_sided_t_approx_p": json_number(p_value),
        "t_statistic": json_number(statistic),
        "degrees_freedom": int(df),
        "controls": controls,
        "method": "average ranks, OLS residual correlation, residual-correlation t approximation",
    }


def bootstrap_interval(data: pd.DataFrame, predictor: str, outcome: str,
                       controls: list[str], rng: np.random.Generator) -> dict:
    estimate = partial_spearman(data, predictor, outcome, controls)
    draws = np.empty(N_BOOT, dtype=float)
    n = len(data)
    for index in range(N_BOOT):
        sampled = data.iloc[rng.integers(0, n, size=n)].reset_index(drop=True)
        draws[index] = partial_spearman(sampled, predictor, outcome, controls)
    valid = draws[np.isfinite(draws)]
    if len(valid) == 0:
        raise RuntimeError(f"All bootstrap replicates invalid for {predictor} vs {outcome}")
    ci = np.quantile(valid, [0.025, 0.975], method="linear")
    return {
        "rho": json_number(estimate),
        "ci95_percentile": [json_number(ci[0]), json_number(ci[1])],
        "bootstrap_replicates": int(N_BOOT),
        "bootstrap_valid_replicates": int(len(valid)),
        "controls": controls,
        "method": "plant-level percentile bootstrap; ranks and OLS refit in each resample",
    }


def raw_spearman(data: pd.DataFrame, x: str, y: str) -> dict:
    result = spearmanr(data[x].to_numpy(float), data[y].to_numpy(float))
    return {"rho": json_number(result.statistic),
            "two_sided_p": json_number(result.pvalue),
            "n": int(len(data)),
            "method": "raw Spearman rank correlation with SciPy two-sided p value"}


def interp_columns(times: np.ndarray, theta: np.ndarray,
                   query_times: np.ndarray, columns: np.ndarray) -> np.ndarray:
    hi = np.searchsorted(times, query_times, side="right")
    hi = np.clip(hi, 1, len(times) - 1)
    lo = hi - 1
    fraction = (query_times - times[lo]) / (times[hi] - times[lo])
    return theta[lo, columns] + fraction * (theta[hi, columns] - theta[lo, columns])


def fit_trajectory_pool(paired: pd.DataFrame, by_plant: dict,
                        fit_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    fits_all = pd.read_csv(fit_path)
    fits = fits_all.loc[fits_all["mode"] == "phi_free"].set_index("plant")
    ids = paired["real_id"].tolist()
    missing = sorted(set(ids) - set(fits.index))
    if missing:
        raise ValueError(f"Missing phi_free fits for matched plants: {missing[:5]}")
    fits = fits.loc[ids]
    if not np.allclose(fits["I"].to_numpy(float), paired["intensity_w_m2"].to_numpy(float),
                       rtol=0.0, atol=1e-12):
        raise ValueError("Per-plant fit intensity differs from the matched archive intensity")
    theta0 = paired["theta0_deg"].to_numpy(float)
    params = [fits[column].to_numpy(float)
              for column in ("k_fit", "tau_fit", "max_rate_fit", "phi_fit_deg")]
    if not all(np.isfinite(array).all() for array in params):
        raise ValueError("Non-finite per-plant fit parameter")
    max_dt = float(paired["dt"].max())
    t_end = float(np.ceil(max_dt / MODEL_DT) * MODEL_DT)
    times, theta = sim.batch_simulate(
        params[0], params[1], params[2], params[3],
        t_end=t_end, dt=MODEL_DT, theta0=theta0,
    )
    result = {
        "fit_file": str(fit_path.relative_to(ROOT)),
        "fit_mode": "phi_free",
        "archive_fit_rows": int(len(fits_all.loc[fits_all["mode"] == "phi_free"])),
        "matched_fit_rows": int(len(fits)),
        "integrator": "repository-root sim.py batch_simulate",
        "integration_step_hours": float(MODEL_DT),
        "simulation_end_hours": float(t_end),
        "trajectory_count": int(theta.shape[1]),
        "trajectory_sample_count": int(theta.shape[0]),
        "fit_per_plant_description": (
            "committed full-curve phi_free fits; each source parameter vector was fitted to its source plant"
        ),
    }
    return times, theta, np.asarray(params[3], dtype=float), result


def make_height_latent_lengths(paired: pd.DataFrame,
                               by_plant: dict[str, tuple[np.ndarray, np.ndarray]]) -> tuple[np.ndarray, np.ndarray, dict]:
    n = len(paired)
    observed_theta0 = np.empty(n, dtype=float)
    observed_theta_dt = np.empty(n, dtype=float)
    for index, row in paired.iterrows():
        times, theta = by_plant[row["real_id"]]
        observed_theta0[index] = theta[np.flatnonzero(np.isclose(times, 0.0))[0]]
        observed_theta_dt[index] = np.interp(float(row["dt"]), times, theta)
    cos_start = np.cos(np.deg2rad(observed_theta0))
    cos_finish = np.cos(np.deg2rad(observed_theta_dt))
    if np.any(cos_start <= 0.0) or np.any(cos_finish <= 0.0):
        bad = paired.loc[(cos_start <= 0.0) | (cos_finish <= 0.0), "real_id"].tolist()
        raise ValueError(f"Vertical-height inversion has non-positive cosine for: {bad[:5]}")
    axial_start = paired["length_start"].to_numpy(float) / cos_start
    axial_finish = paired["length_finish"].to_numpy(float) / cos_finish
    if np.any(axial_start <= 0.0) or np.any(axial_finish <= 0.0):
        raise ValueError("Vertical-height inversion produced a non-positive axial length")
    return axial_start, axial_finish, {
        "assumed_projection": "vertical tip height = axial organ length * cos(angle from vertical)",
        "observed_endpoint_angle_rule": (
            "linear interpolation within the observed trajectory; np.interp holds its final value if length dt is longer"
        ),
        "positive_cosine_rows": int(np.sum((cos_start > 0.0) & (cos_finish > 0.0))),
        "inferred_positive_axial_endpoint_rows": int(np.sum((axial_start > 0.0) & (axial_finish > 0.0))),
    }


def classify_null(observed: float, values: np.ndarray) -> dict:
    quantiles = np.quantile(values, [0.025, 0.975], method="linear")
    if observed < quantiles[0]:
        classification = "below"
    elif observed > quantiles[1]:
        classification = "above"
    else:
        classification = "inside"
    return {
        "median": json_number(np.median(values)),
        "percentile_2_5": json_number(quantiles[0]),
        "percentile_97_5": json_number(quantiles[1]),
        "observed_rho": json_number(observed),
        "observed_percentile_empirical": json_number(100.0 * np.mean(values <= observed)),
        "simulated_values_at_or_below_observed": int(np.sum(values <= observed)),
        "simulated_values_above_observed": int(np.sum(values > observed)),
        "replicates": int(len(values)),
        "classification": classification,
        "quantile_method": "numpy linear sample quantiles",
    }


def run_null_simulation(paired: pd.DataFrame, times: np.ndarray, theta: np.ndarray,
                        by_plant: dict[str, tuple[np.ndarray, np.ndarray]],
                        observed_rho: float) -> tuple[dict, pd.DataFrame, dict]:
    n = len(paired)
    rng = np.random.default_rng(TASK4_SEED)
    intensity = paired["intensity_w_m2"].to_numpy(float)
    dt = paired["dt"].to_numpy(float)
    theta0_donor = theta[0, :]
    plateau_donor = theta[(times >= 16.0) & (times <= 21.0), :].mean(axis=0)
    angle_dt = np.empty((N_NULL, n), dtype=float)
    rho_axial = np.empty(N_NULL, dtype=float)
    rho_height = np.empty(N_NULL, dtype=float)
    axial_length_start = paired["length_start"].to_numpy(float)
    axial_growth_rate = paired["elongation_rate_mm_h"].to_numpy(float)
    latent_height_start, latent_height_finish, height_geometry = make_height_latent_lengths(paired, by_plant)
    group_indices = [np.asarray(indices, dtype=int)
                     for indices in paired.groupby("intensity_w_m2", sort=True).indices.values()]

    for replicate in range(N_NULL):
        donor_for_record = np.arange(n, dtype=int)
        for indices in group_indices:
            donor_for_record[indices] = rng.permutation(indices)
        donors = donor_for_record
        theta_at_interval_end = interp_columns(times, theta, dt, donors)
        simulated_plateau = plateau_donor[donors]
        simulated_theta0 = theta0_donor[donors]
        log_intensity = np.log(intensity)

        axial_start_measure = axial_length_start.copy()
        axial_rate_measure = axial_growth_rate.copy()
        axial_frame = pd.DataFrame({
            "elongation": axial_rate_measure,
            "late_angle": simulated_plateau,
            "theta0": simulated_theta0,
            "log_intensity": log_intensity,
            "log_start_length": np.log(axial_start_measure),
        })
        rho_axial[replicate] = partial_spearman(
            axial_frame, "elongation", "late_angle",
            ["theta0", "log_intensity", "log_start_length"],
        )

        height_start_measure = latent_height_start * np.cos(np.deg2rad(simulated_theta0))
        height_finish_measure = latent_height_finish * np.cos(np.deg2rad(theta_at_interval_end))
        if np.any(height_start_measure <= 0.0):
            raise ValueError("Synthetic projected starting height is non-positive")
        height_rate_measure = (height_finish_measure - height_start_measure) / dt
        height_frame = pd.DataFrame({
            "elongation": height_rate_measure,
            "late_angle": simulated_plateau,
            "theta0": simulated_theta0,
            "log_intensity": log_intensity,
            "log_start_length": np.log(height_start_measure),
        })
        rho_height[replicate] = partial_spearman(
            height_frame, "elongation", "late_angle",
            ["theta0", "log_intensity", "log_start_length"],
        )
        angle_dt[replicate] = theta_at_interval_end

    if not np.isfinite(rho_axial).all() or not np.isfinite(rho_height).all():
        raise RuntimeError("At least one geometry-null replicate produced a non-finite rho")
    results = {
        "seed": int(TASK4_SEED),
        "replicates_per_interpretation": int(N_NULL),
        "fit_source": str(FIT_FILE.relative_to(ROOT)),
        "within_intensity_pairing": "random permutation of length records relative to fitted trajectories; fixed points are allowed",
        "axial_length": classify_null(observed_rho, rho_axial),
        "vertical_height": classify_null(observed_rho, rho_height),
        "height_geometry": height_geometry,
    }
    draws = pd.DataFrame({
        "replicate": np.arange(1, N_NULL + 1, dtype=int),
        "rho_axial_length": rho_axial,
        "rho_vertical_height": rho_height,
    })
    return results, draws, {"simulated_angle_at_length_dt": angle_dt}


def overlap_category(result: dict) -> str:
    estimate = float(result["rho"])
    lo, hi = map(float, result["ci95_percentile"])
    if abs(estimate) <= 0.10 and lo <= 0.0 <= hi:
        return "collapse"
    if estimate >= 0.20 and lo > 0.0:
        return "survives"
    return "ambiguous"


def run_within_group(paired: pd.DataFrame) -> list[dict]:
    ordered = paired.sort_values(["total_angle_change_deg", "real_id"], kind="mergesort")
    index_groups = np.array_split(np.arange(len(ordered)), 3)
    rng = np.random.default_rng(TASK5_SEED)
    results = []
    for group_number, indices in enumerate(index_groups, start=1):
        subset = ordered.iloc[indices].reset_index(drop=True)
        estimate = bootstrap_interval(
            subset,
            "elongation_rate_mm_h",
            "plateau_16_21_deg",
            ["theta0_deg", "log_intensity", "log_L0"],
            rng,
        )
        estimate.update({
            "stratum": int(group_number),
            "n": int(len(subset)),
            "total_angle_change_min_deg": json_number(subset["total_angle_change_deg"].min()),
            "total_angle_change_max_deg": json_number(subset["total_angle_change_deg"].max()),
        })
        results.append(estimate)
    return results


def scan_range_mentions() -> dict:
    try:
        paths = subprocess.check_output(["git", "ls-files", "-z", "*.md"], cwd=ROOT).decode().split("\0")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("Could not enumerate tracked Markdown files for Task 7 scan") from exc
    pattern = re.compile(r"0\.7\s*(?:to|[-\u2013\u2014])\s*7(?:\.0)?\s*W\s*/\s*m(?:\^?2|²)", re.IGNORECASE)
    upper_pattern = re.compile(r"(?<![\d.])7(?:\.0)?\s*W\s*/\s*m(?:\^?2|²)", re.IGNORECASE)
    frozen_prefixes = ("01_canonical_bendlab/", "04_shape_extension_branch/", "05_data_external/")
    mentions = []
    upper_mentions = []
    for relative in paths:
        if not relative or relative.startswith(frozen_prefixes) or relative.startswith("06_growth_coupling/"):
            continue
        path = ROOT / relative
        if not path.is_file():
            continue
        for line_number, text in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            entry = {"path": relative, "line": int(line_number), "text": text.strip()}
            if pattern.search(text):
                mentions.append(entry)
            if upper_pattern.search(text):
                upper_mentions.append(entry)
    trajectory = pd.read_csv(TRAJECTORY_FILE)
    intensities = sorted(float(value) for value in trajectory["light_i"].unique())
    return {
        "working_markdown_scope": "tracked Markdown excluding frozen snapshot directories and the new 06_growth_coupling deliverables",
        "exact_0_7_to_7_w_m2_mentions": mentions,
        "mention_count": int(len(mentions)),
        "seven_w_m2_mentions": upper_mentions,
        "seven_w_m2_mention_count": int(len(upper_mentions)),
        "tracked_unilateral_archive_intensity_min_w_m2": float(min(intensities)),
        "tracked_unilateral_archive_intensity_max_w_m2": float(max(intensities)),
        "tracked_unilateral_archive_intensity_groups": intensities,
    }


def main() -> None:
    started = time.perf_counter()
    outcomes, by_plant = derive_outcomes(TRAJECTORY_FILE)
    paired, duplicate_id_count = join_data(outcomes, LENGTH_FILE)
    paired["total_angle_change_deg"] = paired["total_angle_change_deg"].astype(float)

    baseline = partial_with_t_p(
        paired,
        "elongation_rate_mm_h",
        "plateau_16_21_deg",
        ["theta0_deg", "log_intensity", "log_L0"],
    )
    baseline["source_reported_rho"] = 0.603
    baseline["source_reported_ci95"] = [0.521, 0.672]

    task3_rng = np.random.default_rng(TASK3_SEED)
    overlap_elongation = partial_with_t_p(
        paired,
        "elongation_rate_mm_h",
        "plateau_16_21_deg",
        ["theta0_deg", "log_intensity", "log_L0", "total_angle_change_deg"],
    )
    overlap_elongation.update(bootstrap_interval(
        paired,
        "elongation_rate_mm_h",
        "plateau_16_21_deg",
        ["theta0_deg", "log_intensity", "log_L0", "total_angle_change_deg"],
        task3_rng,
    ))
    overlap_starting_length = partial_with_t_p(
        paired,
        "log_L0",
        "plateau_16_21_deg",
        ["theta0_deg", "log_intensity", "elongation_rate_mm_h", "total_angle_change_deg"],
    )
    overlap_starting_length.update(bootstrap_interval(
        paired,
        "log_L0",
        "plateau_16_21_deg",
        ["theta0_deg", "log_intensity", "elongation_rate_mm_h", "total_angle_change_deg"],
        task3_rng,
    ))

    # Post-registration definition sensitivities. The preregistered primary
    # remains last-observed minus first-observed angle. These reproduce and
    # diagnose alternative angular-response definitions in repository/review notes.
    phase_c_change_overlap = partial_with_t_p(
        paired,
        "elongation_rate_mm_h",
        "plateau_16_21_deg",
        ["theta0_deg", "log_intensity", "log_L0", "phase_c_total_change_deg"],
    )
    phase_c_change_overlap.update(bootstrap_interval(
        paired,
        "elongation_rate_mm_h",
        "plateau_16_21_deg",
        ["theta0_deg", "log_intensity", "log_L0", "phase_c_total_change_deg"],
        task3_rng,
    ))
    peak_excursion_overlap = partial_with_t_p(
        paired,
        "elongation_rate_mm_h",
        "plateau_16_21_deg",
        ["theta0_deg", "log_intensity", "log_L0", "peak_excursion_deg"],
    )
    peak_excursion_overlap.update(bootstrap_interval(
        paired,
        "elongation_rate_mm_h",
        "plateau_16_21_deg",
        ["theta0_deg", "log_intensity", "log_L0", "peak_excursion_deg"],
        task3_rng,
    ))
    peak_excursion_starting_length = partial_with_t_p(
        paired,
        "log_L0",
        "plateau_16_21_deg",
        ["theta0_deg", "log_intensity", "elongation_rate_mm_h", "peak_excursion_deg"],
    )
    peak_excursion_starting_length.update(bootstrap_interval(
        paired,
        "log_L0",
        "plateau_16_21_deg",
        ["theta0_deg", "log_intensity", "elongation_rate_mm_h", "peak_excursion_deg"],
        task3_rng,
    ))
    partial_growth_change = partial_with_t_p(
        paired,
        "elongation_rate_mm_h",
        "total_angle_change_deg",
        ["theta0_deg", "log_intensity", "log_L0"],
    )
    partial_growth_phase_c_change = partial_with_t_p(
        paired,
        "elongation_rate_mm_h",
        "phase_c_total_change_deg",
        ["theta0_deg", "log_intensity", "log_L0"],
    )
    exploratory = {
        "primary_endpoint_total_change_definition": "last observed tip angle minus first observed tip angle",
        "elongation_vs_total_angle_change_raw": raw_spearman(
            paired, "elongation_rate_mm_h", "total_angle_change_deg"),
        "elongation_vs_total_angle_change_partial": partial_growth_change,
        "existing_phase_c_total_change_definition": "mean tip angle from 16 through 21 hours minus theta(0), as in growth_phase/phase_c_historical.py",
        "elongation_vs_existing_phase_c_total_change_raw": raw_spearman(
            paired, "elongation_rate_mm_h", "phase_c_total_change_deg"),
        "elongation_vs_existing_phase_c_total_change_partial": partial_growth_phase_c_change,
        "peak_excursion_definition": "maximum observed tip angle minus theta(0)",
        "elongation_vs_peak_excursion_raw": raw_spearman(
            paired, "elongation_rate_mm_h", "peak_excursion_deg"),
        "elongation_vs_peak_excursion_partial": partial_with_t_p(
            paired, "elongation_rate_mm_h", "peak_excursion_deg",
            ["theta0_deg", "log_intensity", "log_L0"]),
        "elongation_vs_peak_angle_raw": raw_spearman(
            paired, "elongation_rate_mm_h", "peak_angle_deg"),
    }

    fit_times, fit_theta, phi_fit, fit_metadata = fit_trajectory_pool(paired, by_plant, FIT_FILE)
    null_results, null_draws, _ = run_null_simulation(
        paired, fit_times, fit_theta, by_plant, float(baseline["rho"]),
    )
    null_draws_path = OUT / "simulation_null_rhos.csv"

    task3_class = overlap_category(overlap_elongation)
    sensitivity_categories = {
        "existing_phase_c_total_change_control": overlap_category(phase_c_change_overlap),
        "peak_excursion_control": overlap_category(peak_excursion_overlap),
    }
    sensitivity_conflict = any(category != task3_class for category in sensitivity_categories.values())
    geometry_classes = [null_results["axial_length"]["classification"],
                        null_results["vertical_height"]["classification"]]
    task4_inconclusive = len(set(geometry_classes)) > 1 or "below" in geometry_classes
    task3_task4_conflict = (
        (task3_class == "survives" and any(category != "above" for category in geometry_classes))
        or (task3_class == "collapse" and len(set(geometry_classes)) > 1)
    )
    task5_triggered = (
        task3_class == "ambiguous" or task4_inconclusive
        or task3_task4_conflict or sensitivity_conflict
    )
    within_group = run_within_group(paired) if task5_triggered else []
    if task5_triggered:
        within_pattern = (
            all(float(row["rho"]) > 0.0 for row in within_group)
            and sum(float(row["ci95_percentile"][0]) > 0.0 for row in within_group) >= 2
        )
    else:
        within_pattern = None

    if task3_class == "collapse" and not sensitivity_conflict:
        verdict = "explained by coupling"
        verdict_reason = "The preregistered overlap estimate meets the collapse rule, with no definition-sensitivity conflict."
    elif (
        task3_class == "survives"
        and all(category == "above" for category in geometry_classes)
        and (not task5_triggered or within_pattern is True)
        and not sensitivity_conflict
    ):
        verdict = "survives"
        verdict_reason = "The overlap estimate survives, the observed rho is above both geometry-only null bounds, and no definition-sensitivity conflict remains."
    else:
        verdict = "ambiguous"
        verdict_reason = "The preregistered estimate, geometry null, and/or post-registration total-response definition sensitivity do not yield one consistent classification."

    w1 = pd.read_csv(W1_FILE)
    w1_rows = w1.loc[w1["model"] == "W1_bendlab_kI_phi90", "rmse_deg"].astype(float)
    if len(w1_rows) == 0:
        raise ValueError("No W1 rows found in committed per-plant held-out output")
    w1_median = float(w1_rows.median())
    range_scan = scan_range_mentions()

    elapsed = time.perf_counter() - started
    results = {
        "analysis": "growth and angular-response coupling sensitivity",
        "task1_measurement_geometry": {
            "finding": "cannot be determined from the repository",
            "source_evidence": [
                "length_est.py computes (length_finish - length_start) / dt and labels the result mm/hour; it does not define measurement geometry",
                "PHASE_A_DATA_AUDIT.md verifies units mm and mm/h, but says timing of length_start relative to trajectory time zero cannot be verified from archive files alone",
                "length_est_data.csv contains numeric length_start and length_finish fields without a measurement protocol",
            ],
            "both_interpretations_run": True,
        },
        "inputs": {
            "trajectory_file": str(TRAJECTORY_FILE.relative_to(ROOT)),
            "length_file": str(LENGTH_FILE.relative_to(ROOT)),
            "per_plant_fit_file": str(FIT_FILE.relative_to(ROOT)),
            "matched_plants": int(len(paired)),
            "trajectory_plants": int(len(outcomes)),
            "length_rows_raw": int(len(pd.read_csv(LENGTH_FILE))),
            "duplicate_length_ids_removed": int(duplicate_id_count),
            "matched_intensity_values_w_m2": sorted(float(x) for x in paired["intensity_w_m2"].unique()),
            "late_window_hours_inclusive": [16, 21],
            "total_angle_change_definition": "last observed tip angle minus first observed tip angle",
            "peak_angle_definition": "maximum observed tip angle in the trajectory",
            "partial_spearman_method": "average ranks, separate OLS residualization, Pearson correlation of residuals",
            "p_value_method": "two-sided residual-correlation t approximation; df = n - covariate count - 2",
        },
        "task3_seed": int(TASK3_SEED),
        "task3_bootstrap_replicates": int(N_BOOT),
        "task3": {
            "original_association_recomputed": baseline,
            "elongation_vs_late_angle_with_total_change_control": overlap_elongation,
            "starting_length_vs_late_angle_with_total_change_control": overlap_starting_length,
            "elongation_total_change_and_peak_reproduction": exploratory,
            "post_registration_definition_sensitivity": {
                "status": "added after the preregistered endpoint definition failed to match the approximate review check; not used to overwrite the primary estimate",
                "existing_phase_c_total_change_control": phase_c_change_overlap,
                "peak_excursion_control": peak_excursion_overlap,
                "peak_excursion_starting_length_control": peak_excursion_starting_length,
            },
            "overlap_decision_category": task3_class,
        },
        "task4_fit_and_simulation": fit_metadata,
        "task4_seed": int(TASK4_SEED),
        "task4_replicates_per_interpretation": int(N_NULL),
        "task4_null": null_results,
        "task4_null_draws_file": str(null_draws_path.relative_to(ROOT)),
        "task5": {
            "triggered": bool(task5_triggered),
            "trigger_reason": {
                "task3_category": task3_class,
                "geometry_categories": geometry_classes,
                "task4_inconclusive": bool(task4_inconclusive),
                "task3_task4_conflict": bool(task3_task4_conflict),
                "post_registration_definition_sensitivity_categories": sensitivity_categories,
                "definition_sensitivity_conflict": bool(sensitivity_conflict),
            },
            "seed": int(TASK5_SEED) if task5_triggered else None,
            "bootstrap_replicates_per_stratum": int(N_BOOT) if task5_triggered else None,
            "strata": within_group,
            "robust_positive_within_strata": within_pattern,
        },
        "overall_verdict": verdict,
        "overall_verdict_reason": verdict_reason,
        "task7_consistency": {
            "w1_heldout_rows": int(len(w1_rows)),
            "w1_median_rmse_deg_from_committed_per_plant_output": w1_median,
            "recommended_paper_rounding_2dp": round(w1_median, 2),
            "working_document_archive_range_scan": range_scan,
        },
        "runtime_seconds": float(elapsed),
        "no_existing_outputs_modified": True,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    null_draws.to_csv(null_draws_path, index=False)
    (OUT / "analysis_results.json").write_text(
        json.dumps(results, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
