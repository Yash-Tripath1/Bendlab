#!/usr/bin/env python3
"""Post-registration Task 4 amendment, preserving the original analysis outputs.

This follow-up screens fitted equilibrium angles before its amended simulations,
excludes degenerate phi_free fits from the primary fitted-trajectory null, reports
full-sample sensitivity results, and adds an empirical-angle projection null.
All new artifacts are written to distinct names under 06_growth_coupling/outputs/.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import analyze_coupling as base

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "outputs"
FIT_FILE = base.FIT_FILE
N_REPLICATES = base.N_NULL
EMPIRICAL_ANGLE_SEED = 20261115
SMALL_FRACTION_THRESHOLD = 0.05


def fit_parameter_screen(paired: pd.DataFrame) -> tuple[dict, list[str]]:
    """Summarize phi_free targets and flag targets below observed starting angle."""
    all_fits = pd.read_csv(FIT_FILE)
    mode_counts = {str(mode): int(count) for mode, count in all_fits["mode"].value_counts().items()}
    free = all_fits.loc[all_fits["mode"] == "phi_free"].set_index("plant")
    ids = paired["real_id"].astype(str).tolist()
    missing = sorted(set(ids) - set(free.index.astype(str)))
    if missing:
        raise ValueError(f"Missing phi_free fits for matched plants: {missing[:5]}")
    free.index = free.index.astype(str)
    ordered = free.loc[ids]
    phi = ordered["phi_fit_deg"].to_numpy(float)
    theta0 = paired["theta0_deg"].to_numpy(float)
    if len(phi) != len(paired) or not np.isfinite(phi).all():
        raise ValueError("Invalid matched phi_fit_deg values")
    quantile_probs = [0.05, 0.25, 0.50, 0.75, 0.95]
    quantile_values = np.quantile(phi, quantile_probs, method="linear")
    flagged_mask = phi < theta0
    flagged_ids = sorted(np.asarray(ids, dtype=object)[flagged_mask].tolist())
    fraction = float(flagged_mask.mean())
    hist_edges = [-np.inf, 0, 15, 30, 45, 60, 75, 90, np.inf]
    hist_labels = ["<0", "0_to_lt_15", "15_to_lt_30", "30_to_lt_45",
                   "45_to_lt_60", "60_to_lt_75", "75_to_lt_90", "90_or_more"]
    histogram = {
        label: int(np.sum((phi >= lo) & (phi < hi)))
        for label, lo, hi in zip(hist_labels, hist_edges[:-1], hist_edges[1:])
    }
    diagnostic = {
        "timing": "computed and printed before the amended Task 4 simulations",
        "fit_source": str(FIT_FILE.relative_to(ROOT)),
        "fit_rows_all_modes": int(len(all_fits)),
        "fit_rows_by_mode": mode_counts,
        "matched_phi_free_rows": int(len(paired)),
        "phi_fit_deg_distribution": {
            "min": float(np.min(phi)),
            "p05": float(quantile_values[0]),
            "q25": float(quantile_values[1]),
            "median": float(quantile_values[2]),
            "q75": float(quantile_values[3]),
            "p95": float(quantile_values[4]),
            "max": float(np.max(phi)),
            "mean": float(np.mean(phi)),
            "histogram_degrees": histogram,
        },
        "theta0_deg_distribution": {
            "min": float(np.min(theta0)),
            "median": float(np.median(theta0)),
            "max": float(np.max(theta0)),
        },
        "degenerate_fit_rule": "flag and exclude if phi_fit_deg < that plant's observed theta0_deg",
        "degenerate_fit_count": int(flagged_mask.sum()),
        "degenerate_fit_fraction": fraction,
        "degenerate_fit_ids": flagged_ids,
        "small_fraction_threshold": SMALL_FRACTION_THRESHOLD,
        "more_than_small_fraction": bool(fraction > SMALL_FRACTION_THRESHOLD),
        "primary_fit_based_sample": "exclude all flagged phi_free fits",
        "full_sample_also_reported": True,
        "fit_refit": False,
    }
    return diagnostic, flagged_ids


def observed_partial_rho(paired: pd.DataFrame) -> float:
    return float(base.partial_with_t_p(
        paired,
        "elongation_rate_mm_h",
        "plateau_16_21_deg",
        ["theta0_deg", "log_intensity", "log_L0"],
    )["rho"])


def empirical_angle_pool(
    paired: pd.DataFrame,
    by_plant: dict[str, tuple[np.ndarray, np.ndarray]],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return observed theta0, observed plateau, and receiver-time endpoint angles.

    endpoint_angles[i, j] is donor j's observed angle interpolated at record i's
    length interval. Each replicate samples donor trajectories only; growth
    records and their intensity group remain fixed.
    """
    ids = paired["real_id"].astype(str).tolist()
    dt = paired["dt"].to_numpy(float)
    n = len(paired)
    theta0 = np.empty(n, dtype=float)
    plateau = np.empty(n, dtype=float)
    endpoint_angles = np.empty((n, n), dtype=float)
    for donor_index, plant_id in enumerate(ids):
        times, angles = by_plant[plant_id]
        initial = np.flatnonzero(np.isclose(times, 0.0))
        late = (times >= 16.0) & (times <= 21.0)
        if len(initial) == 0 or not late.any():
            raise ValueError(f"Observed trajectory {plant_id} lacks theta0 or late-window data")
        theta0[donor_index] = float(angles[initial[0]])
        plateau[donor_index] = float(np.mean(angles[late]))
        endpoint_angles[:, donor_index] = np.interp(dt, times, angles)
    return theta0, plateau, endpoint_angles


def run_empirical_angle_projection_null(
    paired: pd.DataFrame,
    by_plant: dict[str, tuple[np.ndarray, np.ndarray]],
    observed_rho: float,
    seed: int = EMPIRICAL_ANGLE_SEED,
) -> tuple[dict, pd.DataFrame]:
    """Resample empirical angle curves while holding each growth record fixed."""
    n = len(paired)
    rng = np.random.default_rng(seed)
    intensity = paired["intensity_w_m2"].to_numpy(float)
    log_intensity = np.log(intensity)
    dt = paired["dt"].to_numpy(float)
    axial_start = paired["length_start"].to_numpy(float)
    axial_growth = paired["elongation_rate_mm_h"].to_numpy(float)
    log_axial_start = np.log(axial_start)
    latent_height_start, latent_height_finish, height_meta = base.make_height_latent_lengths(
        paired, by_plant,
    )
    theta0_pool, plateau_pool, endpoint_angle_matrix = empirical_angle_pool(paired, by_plant)
    group_indices = [np.asarray(indices, dtype=int)
                     for indices in paired.groupby("intensity_w_m2", sort=True).indices.values()]
    row_indices = np.arange(n, dtype=int)
    rho_axial = np.empty(N_REPLICATES, dtype=float)
    rho_height = np.empty(N_REPLICATES, dtype=float)

    for replicate in range(N_REPLICATES):
        donors = np.arange(n, dtype=int)
        for indices in group_indices:
            donors[indices] = rng.permutation(indices)
        sampled_theta0 = theta0_pool[donors]
        sampled_late = plateau_pool[donors]
        sampled_theta_dt = endpoint_angle_matrix[row_indices, donors]

        axial_frame = pd.DataFrame({
            "elongation": axial_growth,
            "late_angle": sampled_late,
            "theta0": sampled_theta0,
            "log_intensity": log_intensity,
            "log_start_length": log_axial_start,
        })
        rho_axial[replicate] = base.partial_spearman(
            axial_frame, "elongation", "late_angle",
            ["theta0", "log_intensity", "log_start_length"],
        )

        height_start = latent_height_start * np.cos(np.deg2rad(sampled_theta0))
        height_finish = latent_height_finish * np.cos(np.deg2rad(sampled_theta_dt))
        if np.any(height_start <= 0.0) or np.any(height_finish <= 0.0):
            raise ValueError("Empirical-angle projection produced a non-positive height")
        height_growth = (height_finish - height_start) / dt
        height_frame = pd.DataFrame({
            "elongation": height_growth,
            "late_angle": sampled_late,
            "theta0": sampled_theta0,
            "log_intensity": log_intensity,
            "log_start_length": np.log(height_start),
        })
        rho_height[replicate] = base.partial_spearman(
            height_frame, "elongation", "late_angle",
            ["theta0", "log_intensity", "log_start_length"],
        )

    if not np.isfinite(rho_axial).all() or not np.isfinite(rho_height).all():
        raise RuntimeError("Empirical-angle null produced a non-finite partial rho")
    result = {
        "seed": int(seed),
        "replicates_per_interpretation": int(N_REPLICATES),
        "n_plants": int(n),
        "observed_partial_rho": float(observed_rho),
        "resampling": (
            "random within-intensity permutation of empirical observed angle trajectories; "
            "each plant's observed growth record remains fixed; fixed points are allowed"
        ),
        "question": (
            "conditional projection sensitivity: compare axial and projected-height estimates "
            "under identical empirical angle-trajectory draws and fixed observed growth records"
        ),
        "pairing_note": (
            "trajectory identity is resampled, so plant-specific growth-angle pairing is not retained; "
            "the axial-versus-height contrast isolates projection conditional on this resampling scheme"
        ),
        "axial_length": base.classify_null(observed_rho, rho_axial),
        "vertical_height": base.classify_null(observed_rho, rho_height),
        "height_geometry": height_meta,
    }
    draws = pd.DataFrame({
        "replicate": np.arange(1, N_REPLICATES + 1, dtype=int),
        "rho_axial_length": rho_axial,
        "rho_vertical_height": rho_height,
    })
    return result, draws


def run_fitted_pairing_null(
    paired: pd.DataFrame,
    by_plant: dict[str, tuple[np.ndarray, np.ndarray]],
) -> tuple[dict, pd.DataFrame, dict]:
    times, theta, phi_fit, metadata = base.fit_trajectory_pool(paired, by_plant, FIT_FILE)
    observed = observed_partial_rho(paired)
    result, draws, _ = base.run_null_simulation(paired, times, theta, by_plant, observed)
    return {"simulation": result, "fit_metadata": metadata, "observed_partial_rho": observed}, draws, metadata


def rename_draw_columns(draws: pd.DataFrame, prefix: str) -> pd.DataFrame:
    return draws.rename(columns={
        "rho_axial_length": f"{prefix}_rho_axial_length",
        "rho_vertical_height": f"{prefix}_rho_vertical_height",
    })


def overall_verdict(initial: dict, amended_task4: dict) -> tuple[str, str]:
    task3_class = initial["task3"]["overlap_decision_category"]
    sensitivity = initial["task3"]["post_registration_definition_sensitivity"]
    sensitivity_categories = [
        base.overlap_category(sensitivity["existing_phase_c_total_change_control"]),
        base.overlap_category(sensitivity["peak_excursion_control"]),
    ]
    sensitivity_conflict = any(category != task3_class for category in sensitivity_categories)
    eligible_fit = amended_task4["fitted_trajectory_pairing_null"]["eligible_excluded"]["simulation"]
    eligible_empirical = amended_task4["empirical_angle_projection_null"]["eligible_excluded"]
    classes = [
        eligible_fit["axial_length"]["classification"],
        eligible_fit["vertical_height"]["classification"],
        eligible_empirical["axial_length"]["classification"],
        eligible_empirical["vertical_height"]["classification"],
    ]
    within_pattern = initial["task5"]["robust_positive_within_strata"]
    if task3_class == "collapse" and not sensitivity_conflict:
        return "explained by coupling", "The preregistered overlap estimate meets the collapse rule."
    if (task3_class == "survives" and all(category == "above" for category in classes)
            and within_pattern is True and not sensitivity_conflict):
        return "survives", "Both amended nulls are above their geometry cases and no endpoint-definition conflict remains."
    return (
        "ambiguous",
        "The overall classification remains ambiguous. The preregistered and post-registration endpoint definitions disagree; amended Task 4 nulls are reported separately and do not overwrite the original run.",
    )


def main() -> None:
    started = time.perf_counter()
    outcomes, by_plant = base.derive_outcomes(base.TRAJECTORY_FILE)
    paired_full, duplicate_count = base.join_data(outcomes, base.LENGTH_FILE)
    paired_full["total_angle_change_deg"] = paired_full["total_angle_change_deg"].astype(float)

    # The screen is emitted before any simulator call in this amended run.
    screen, excluded_ids = fit_parameter_screen(paired_full)
    print("PRE-SIMULATION FIT SCREEN")
    print(json.dumps(screen, indent=2, allow_nan=False))

    excluded_set = set(excluded_ids)
    paired_eligible = paired_full.loc[~paired_full["real_id"].astype(str).isin(excluded_set)].copy()
    paired_eligible = paired_eligible.sort_values("real_id").reset_index(drop=True)
    paired_full = paired_full.sort_values("real_id").reset_index(drop=True)
    if len(paired_eligible) == 0:
        raise ValueError("Degenerate-fit exclusion removed every matched plant")

    fitted_full, fitted_full_draws, fitted_full_meta = run_fitted_pairing_null(paired_full, by_plant)
    fitted_eligible, fitted_eligible_draws, fitted_eligible_meta = run_fitted_pairing_null(
        paired_eligible, by_plant,
    )
    empirical_full_observed = observed_partial_rho(paired_full)
    empirical_eligible_observed = observed_partial_rho(paired_eligible)
    empirical_full, empirical_full_draws = run_empirical_angle_projection_null(
        paired_full, by_plant, empirical_full_observed,
    )
    empirical_eligible, empirical_eligible_draws = run_empirical_angle_projection_null(
        paired_eligible, by_plant, empirical_eligible_observed,
    )

    amended_task4 = {
        "status": (
            "post-registration amendment, added after an initial Task 4 run; "
            "all new distributions are preserved separately"
        ),
        "fit_screen_before_amended_simulation": screen,
        "fitted_trajectory_pairing_null": {
            "question": (
                "does the observed association exceed a no-same-plant-pairing null under the "
                "committed fitted angular-response distribution, with geometry applied as specified"
            ),
            "full_sample": fitted_full,
            "eligible_excluded": fitted_eligible,
            "fit_metadata_full": fitted_full_meta,
            "fit_metadata_eligible": fitted_eligible_meta,
        },
        "empirical_angle_projection_null": {
            "question": (
                "conditional projection sensitivity under fixed observed growth records, using "
                "within-intensity empirical angle-trajectory draws; axial-versus-height contrast isolates projection"
            ),
            "seed": EMPIRICAL_ANGLE_SEED,
            "replicates_per_interpretation": N_REPLICATES,
            "full_sample": empirical_full,
            "eligible_excluded": empirical_eligible,
        },
        "replicates_per_interpretation_and_sample": int(N_REPLICATES),
        "no_fit_refit": True,
        "simulator_call": (
            "one batched sim.batch_simulate call per sample with positional arrays "
            "(k_fit, tau_fit, max_rate_fit, phi_fit_deg), theta0 array, and default light function; "
            "static_light is not passed as light_fn"
        ),
        "review_verified_setup_facts": {
            "static_physical_light_phi_deg": 90.0,
            "static_phi90_theta_start_deg": 5.0,
            "static_phi90_theta_after_24h_deg": 90.7,
            "one_batch_213_plants_24h_dt_1_over_60_runtime_seconds": 0.028,
            "one_thousand_replicates_for_both_interpretations_under_one_minute": True,
            "theta0_array_test_values_deg": [5.0, 40.0],
            "per_plant_fit_rows_total": 536,
            "per_plant_fit_rows_per_mode": 268,
            "matched_phi_free_fit_rows": 213,
            "per_plant_theta0_array_supported": True,
            "static_light_signature": "one argument; do not pass directly as batch_simulate light_fn",
        },
    }

    verdict, verdict_reason = overall_verdict(base_initial_results(), amended_task4)
    combined_draws = pd.DataFrame({"replicate": np.arange(1, N_REPLICATES + 1, dtype=int)})
    for prefix, drawset in (
        ("fitted_full", fitted_full_draws),
        ("fitted_eligible", fitted_eligible_draws),
        ("empirical_full", empirical_full_draws),
        ("empirical_eligible", empirical_eligible_draws),
    ):
        combined_draws = combined_draws.join(rename_draw_columns(drawset, prefix).drop(columns="replicate"))

    elapsed = time.perf_counter() - started
    initial = base_initial_results()
    results = dict(initial)
    results["task4_amendment"] = amended_task4
    results["task4_amended_draws_file"] = "06_growth_coupling/outputs/amended_task4_null_rhos.csv"
    results["overall_verdict"] = verdict
    results["overall_verdict_reason"] = verdict_reason
    results["amended_task4_runtime_seconds"] = float(elapsed)
    results["amended_run_no_existing_outputs_modified"] = True

    OUT.mkdir(parents=True, exist_ok=True)
    amended_draws_path = OUT / "amended_task4_null_rhos.csv"
    amended_results_path = OUT / "analysis_results_amended.json"
    combined_draws.to_csv(amended_draws_path, index=False)
    amended_results_path.write_text(json.dumps(results, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("AMENDED TASK 4 RESULTS")
    print(json.dumps({
        "task4_amendment": amended_task4,
        "overall_verdict": verdict,
        "overall_verdict_reason": verdict_reason,
        "amended_task4_runtime_seconds": elapsed,
        "amended_draws_file": str(amended_draws_path.relative_to(ROOT)),
        "amended_results_file": str(amended_results_path.relative_to(ROOT)),
        "no_existing_outputs_modified": True,
    }, indent=2, allow_nan=False))


def base_initial_results() -> dict:
    path = OUT / "analysis_results.json"
    if not path.is_file():
        raise FileNotFoundError(f"Initial results file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
