"""Preregistered Phase E evaluation of an intensity-dependent restoring term.

W3 keeps the physical light angle fixed at 90 degrees and the response gain
shared across intensity. The restoring coefficient follows

gamma(I) = exp(c0 + c1 * ln(I))

and is used in the sim_gamma.py dynamics. Existing benchmark functions are
imported read-only for W1, W2, B1, B1r, and B2 comparisons.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq, least_squares
from scipy.stats import t as student_t

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parents[1]
sys.path.insert(0, str(PKG_ROOT))
sys.path.insert(0, str(HERE))

import sim_gamma  # noqa: E402
import phase_b0_kempinski_benchmark as bench  # noqa: E402

SEED = 42
N_FOLDS = 5
SUB = 4
FIT_DT = 1.0 / 60.0
PHI_LIGHT = 90.0
BASELINE_THRESHOLD_DEG = 9.73
BASELINE_REPRO_TOL_DEG = 0.05
MAX_NFEV = 120

MODEL_NAMES = {
    "W1_bendlab_kI_phi90": "W1",
    "W2_bendlab_kI_phiI_diagnostic": "W2",
    "W3_gammaI_phiLight90": "W3",
    "B1_group_mean_curve": "B1",
    "B1r_group_mean_recentered": "B1r",
    "B2_saturating": "B2",
}

# The optimizer uses logs for positive parameters and natural log gamma(I).
X0 = np.array([np.log(2.0), np.log(2.0), np.log(20.0), np.log(0.15), 0.0])
LOWER = np.array([
    np.log(0.01), np.log(0.05), np.log(0.5), np.log(0.001), -2.0
])
UPPER = np.array([
    np.log(80.0), np.log(40.0), np.log(60.0), np.log(5.0), 2.0
])
PARAMETER_NAMES = ("log_k", "log_tau", "log_max_rate", "c0", "c1")


# Match the existing benchmark's observation subsampling protocol.
bench.SUB = SUB


def unpack(x):
    """Return physical parameters for optimizer vector x."""
    return {
        "k": float(np.exp(x[0])),
        "tau": float(np.exp(x[1])),
        "max_rate": float(np.exp(x[2])),
        "c0": float(x[3]),
        "c1": float(x[4]),
    }


def gamma_of_intensity(intensity, x):
    """Compute gamma in inverse hours from W3 parameters."""
    params = unpack(x)
    intensity = np.asarray(intensity, dtype=float)
    return np.exp(params["c0"] + params["c1"] * np.log(intensity))


def simulate_indices(indices, plants, x):
    """Simulate plants at their own observation times using W3."""
    selected = [plants[i] for i in indices]
    if not selected:
        return []
    params = unpack(x)
    t_end = max(float(p["t"].max()) for p in selected)
    intensities = np.asarray([p["I"] for p in selected], dtype=float)
    gamma = gamma_of_intensity(intensities, x)
    times, theta = sim_gamma.batch_simulate(
        k=np.full(len(selected), params["k"]),
        tau=np.full(len(selected), params["tau"]),
        max_rate=np.full(len(selected), params["max_rate"]),
        phi0=np.full(len(selected), PHI_LIGHT),
        t_end=t_end,
        dt=FIT_DT,
        theta0=np.asarray([p["theta"][0] for p in selected], dtype=float),
        gamma=gamma,
    )
    return [np.interp(p["t"], times, theta[:, j])
            for j, p in enumerate(selected)]


def residual_blocks(x, plants, indices, fitting=True):
    """Return one residual vector per plant, preserving cluster structure."""
    preds = simulate_indices(indices, plants, x)
    blocks = []
    for i, pred in zip(indices, preds):
        observed = plants[i]["theta"]
        if fitting:
            pred = pred[::SUB]
            observed = observed[::SUB]
        blocks.append(np.asarray(pred - observed, dtype=float))
    return blocks


def fit_w3(train_idx, plants):
    """Fit W3 to training plants only with the preregistered bounds."""
    def objective(x):
        return np.concatenate(residual_blocks(x, plants, train_idx, fitting=True))

    result = least_squares(
        objective,
        X0,
        bounds=(LOWER, UPPER),
        x_scale="jac",
        max_nfev=MAX_NFEV,
    )
    return {
        "x": result.x,
        "success": bool(result.success),
        "status": int(result.status),
        "nfev": int(result.nfev),
        "cost": float(result.cost),
        "message": str(result.message),
    }


def predict_w3(model, test_idx, plants):
    """Return W3 predictions keyed by plant ID."""
    preds = simulate_indices(test_idx, plants, model["x"])
    return {plants[i]["id"]: pred for i, pred in zip(test_idx, preds)}


def heldout_fold_predictions(plants):
    """Run the fixed five-fold evaluation for all preregistered models."""
    folds = bench.stratified_folds(plants, n_folds=N_FOLDS, seed=SEED)
    held_rows = []
    fold_fits = []
    for fold_number, test_idx in enumerate(folds, start=1):
        train_idx = [i for j, fold in enumerate(folds) if j != fold_number - 1
                     for i in fold]
        print(f"Primary fold {fold_number}/{N_FOLDS}: fitting W1, W2, W3, B2",
              flush=True)

        w1 = bench.fit_wrapper(train_idx, plants, "fixed90")
        w2 = bench.fit_wrapper(train_idx, plants, "phi_of_I")
        w3 = fit_w3(train_idx, plants)
        b2 = bench.fit_saturating(train_idx, plants)
        means = bench.group_mean_curves(train_idx, plants)

        fold_predictions = {
            "W1_bendlab_kI_phi90": bench.predict_wrapper(w1, test_idx, plants),
            "W2_bendlab_kI_phiI_diagnostic": bench.predict_wrapper(w2, test_idx, plants),
            "W3_gammaI_phiLight90": predict_w3(w3, test_idx, plants),
            "B1_group_mean_curve": bench.predict_group_mean(means, test_idx, plants),
            "B1r_group_mean_recentered": bench.predict_group_mean(
                means, test_idx, plants, recenter=True
            ),
            "B2_saturating": bench.predict_saturating(b2, test_idx, plants),
        }
        for name, predictions in fold_predictions.items():
            held_rows.extend(bench.per_plant_metrics(
                predictions, test_idx, plants, name
            ))
        fold_fits.append({
            "fold": fold_number,
            "n_train": len(train_idx),
            "n_test": len(test_idx),
            "w1": {k: float(v) for k, v in w1.items()
                   if isinstance(v, (float, int, np.floating, np.integer))},
            "w2": {k: (None if v is None else [float(z) for z in v])
                   if k == "phi_params" else float(v)
                   for k, v in w2.items()
                   if k in ("a", "b", "tau", "max_rate", "phi_params")},
            "w3": {
                **unpack(w3["x"]),
                "gamma_at_1w_m2": float(np.exp(w3["x"][3])),
                "nfev": w3["nfev"],
                "success": w3["success"],
            },
            "b2": {k: float(v) for k, v in b2.items()},
        })
        print(f"Primary fold {fold_number}/{N_FOLDS}: complete", flush=True)
    return pd.DataFrame(held_rows), fold_fits


def leave_one_intensity_out(plants):
    """Evaluate every model with each intensity group held out in turn."""
    intensities = sorted({float(p["I"]) for p in plants})
    endpoint_values = {intensities[0], intensities[-1]}
    rows = []
    for group_number, intensity in enumerate(intensities, start=1):
        test_idx = [i for i, p in enumerate(plants) if p["I"] == intensity]
        train_idx = [i for i, p in enumerate(plants) if p["I"] != intensity]
        print(f"LOIO group {group_number}/{len(intensities)}: I={intensity:g}",
              flush=True)

        w1 = bench.fit_wrapper(train_idx, plants, "fixed90")
        w2 = bench.fit_wrapper(train_idx, plants, "phi_of_I")
        w3 = fit_w3(train_idx, plants)
        b2 = bench.fit_saturating(train_idx, plants)
        means = bench.group_mean_curves(train_idx, plants)
        predictions = {
            "W1_bendlab_kI_phi90": bench.predict_wrapper(w1, test_idx, plants),
            "W2_bendlab_kI_phiI_diagnostic": bench.predict_wrapper(w2, test_idx, plants),
            "W3_gammaI_phiLight90": predict_w3(w3, test_idx, plants),
            "B1_group_mean_curve": bench.predict_group_mean(means, test_idx, plants),
            "B1r_group_mean_recentered": bench.predict_group_mean(
                means, test_idx, plants, recenter=True
            ),
            "B2_saturating": bench.predict_saturating(b2, test_idx, plants),
        }
        for name, pred in predictions.items():
            group_rows = bench.per_plant_metrics(pred, test_idx, plants, name)
            for row in group_rows:
                row["endpoint_extrapolation"] = intensity in endpoint_values
                rows.append(row)
    return pd.DataFrame(rows)


def cluster_sandwich_intervals(model, plants):
    """Compute approximate plant-cluster sandwich Wald intervals for W3."""
    all_idx = list(range(len(plants)))
    x = np.asarray(model["x"], dtype=float)
    base_blocks = residual_blocks(x, plants, all_idx, fitting=True)
    derivative_blocks = [[None] * len(plants) for _ in range(len(x))]

    for parameter_index in range(len(x)):
        step = 1e-5 * max(1.0, abs(float(x[parameter_index])))
        can_go_low = x[parameter_index] - step >= LOWER[parameter_index]
        can_go_high = x[parameter_index] + step <= UPPER[parameter_index]
        if can_go_low and can_go_high:
            x_low = x.copy()
            x_high = x.copy()
            x_low[parameter_index] -= step
            x_high[parameter_index] += step
            low_blocks = residual_blocks(x_low, plants, all_idx, fitting=True)
            high_blocks = residual_blocks(x_high, plants, all_idx, fitting=True)
            diffs = [(hi - lo) / (2.0 * step)
                     for lo, hi in zip(low_blocks, high_blocks)]
        elif can_go_high:
            x_high = x.copy()
            x_high[parameter_index] += step
            high_blocks = residual_blocks(x_high, plants, all_idx, fitting=True)
            diffs = [(hi - base) / step
                     for base, hi in zip(base_blocks, high_blocks)]
        elif can_go_low:
            x_low = x.copy()
            x_low[parameter_index] -= step
            low_blocks = residual_blocks(x_low, plants, all_idx, fitting=True)
            diffs = [(base - lo) / step
                     for base, lo in zip(base_blocks, low_blocks)]
        else:
            diffs = [np.full_like(block, np.nan) for block in base_blocks]
        derivative_blocks[parameter_index] = diffs

    jacobians = []
    scores = []
    for plant_index, residual in enumerate(base_blocks):
        jacobian = np.column_stack([
            derivative_blocks[j][plant_index] for j in range(len(x))
        ])
        jacobians.append(jacobian)
        scores.append(jacobian.T @ residual)

    stacked = np.vstack(jacobians)
    _, singular_values, vh = np.linalg.svd(stacked, full_matrices=False)
    if singular_values.size:
        rank_cutoff = singular_values[0] * max(stacked.shape) * np.finfo(float).eps
        rank = int(np.sum(singular_values > rank_cutoff))
        row_basis = vh[:rank]
        projection = row_basis.T @ row_basis if rank else np.zeros((len(x), len(x)))
    else:
        rank = 0
        projection = np.zeros((len(x), len(x)))
    identifiable = np.diag(projection) >= (1.0 - 1e-6)

    bread = np.linalg.pinv(stacked.T @ stacked, rcond=1e-12)
    meat = sum(np.outer(score, score) for score in scores)
    n_plants = len(plants)
    n_params = len(x)
    correction = n_plants / (n_plants - n_params)
    covariance = correction * bread @ meat @ bread
    covariance = (covariance + covariance.T) / 2.0
    diagonal = np.diag(covariance)
    standard_errors = np.sqrt(np.maximum(diagonal, 0.0))
    critical = float(student_t.ppf(0.975, df=n_plants - 1))

    physical = unpack(x)
    intervals = {}
    for j, name in enumerate(PARAMETER_NAMES):
        is_identifiable = bool(identifiable[j])
        se = float(standard_errors[j]) if is_identifiable else None
        if not is_identifiable or not np.isfinite(standard_errors[j]):
            ci_optimizer = None
        else:
            ci_optimizer = [
                float(x[j] - critical * standard_errors[j]),
                float(x[j] + critical * standard_errors[j]),
            ]
        if name == "log_k":
            estimate = physical["k"]
            ci = None if ci_optimizer is None else [float(np.exp(v)) for v in ci_optimizer]
            units = "degrees per hour"
        elif name == "log_tau":
            estimate = physical["tau"]
            ci = None if ci_optimizer is None else [float(np.exp(v)) for v in ci_optimizer]
            units = "hours"
        elif name == "log_max_rate":
            estimate = physical["max_rate"]
            ci = None if ci_optimizer is None else [float(np.exp(v)) for v in ci_optimizer]
            units = "degrees per hour"
        elif name == "c0":
            estimate = physical["c0"]
            ci = ci_optimizer
            units = "log inverse-hours at 1 W/m^2"
        else:
            estimate = physical["c1"]
            ci = ci_optimizer
            units = "log-gamma exponent per natural-log intensity"
        at_bound = bool(
            abs(float(x[j]) - float(LOWER[j])) <= 1e-5
            or abs(float(x[j]) - float(UPPER[j])) <= 1e-5
        )
        intervals[name] = {
            "estimate": float(estimate),
            "ci95": ci,
            "standard_error_optimizer_scale": se,
            "units": units,
            "identifiable_from_local_jacobian": is_identifiable,
            "at_bound": at_bound,
        }

    gamma1_ci = intervals["c0"]["ci95"]
    intervals["gamma_at_1w_m2"] = {
        "estimate": float(np.exp(physical["c0"])),
        "ci95": None if gamma1_ci is None else [float(np.exp(v)) for v in gamma1_ci],
        "units": "inverse hours",
        "derived_from": "exp(c0)",
    }
    return {
        "parameters": intervals,
        "method": (
            "Approximate two-sided 95 percent Wald intervals from a numerical "
            "plant-cluster sandwich covariance, finite-cluster correction "
            "G/(G-p), t critical value with G-1 degrees of freedom"
        ),
        "n_clusters": n_plants,
        "n_parameters": n_params,
        "jacobian_rank": rank,
        "jacobian_columns": len(x),
        "singular_values": [float(v) for v in singular_values],
        "c1_distinguishable_from_zero": (
            None if intervals["c1"]["ci95"] is None
            else not (intervals["c1"]["ci95"][0] <= 0.0
                      <= intervals["c1"]["ci95"][1])
        ),
    }


def equilibrium_angle(k, gamma):
    """Solve the W3 torque balance for the model-implied fixed point."""
    def balance(theta):
        return k * np.sin(np.deg2rad(PHI_LIGHT - theta)) - gamma * theta
    return float(brentq(balance, 1e-9, PHI_LIGHT - 1e-9))


def summarize_primary(held):
    primary = (held.groupby("model", sort=False)
               .agg(n_plants=("plant", "nunique"),
                    median_rmse_deg=("rmse_deg", "median"),
                    p25_rmse_deg=("rmse_deg", lambda v: v.quantile(0.25)),
                    p75_rmse_deg=("rmse_deg", lambda v: v.quantile(0.75)))
               .reset_index())
    by_intensity = (held.groupby(["model", "I"], sort=True)
                    .agg(n_plants=("plant", "nunique"),
                         median_rmse_deg=("rmse_deg", "median"))
                    .reset_index())
    return primary, by_intensity


def check_baselines(primary):
    reference_path = HERE / "outputs" / "benchmark_summary.json"
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    reference_by_model = {
        row["model"]: float(row["median_rmse_deg"])
        for row in reference["plant_heldout"]
    }
    actual_by_model = {
        row["model"]: float(row["median_rmse_deg"])
        for row in primary.to_dict("records")
    }
    rows = []
    for model_name in MODEL_NAMES:
        if model_name == "W3_gammaI_phiLight90":
            continue
        expected = reference_by_model[model_name]
        actual = actual_by_model[model_name]
        delta = actual - expected
        rows.append({
            "model": MODEL_NAMES[model_name],
            "existing_benchmark_median_rmse_deg": expected,
            "reproduced_median_rmse_deg": actual,
            "delta_deg": delta,
            "within_tolerance": abs(delta) <= BASELINE_REPRO_TOL_DEG,
        })
    failures = [r for r in rows if not r["within_tolerance"]]
    if failures:
        raise RuntimeError(
            "Existing benchmark baselines were not reproduced within "
            f"{BASELINE_REPRO_TOL_DEG} degrees: {failures}"
        )
    return rows


def main():
    started = time.perf_counter()
    data_path = Path(bench.DATA)
    df, plants = bench.load_plants(data_path)
    audit = bench.audit(df, plants)
    if len(plants) != 268:
        raise RuntimeError(f"Expected 268 plants, found {len(plants)}")

    held, fold_fits = heldout_fold_predictions(plants)
    primary, primary_by_intensity = summarize_primary(held)
    baseline_checks = check_baselines(primary)
    held["model_label"] = held["model"].map(MODEL_NAMES)
    primary["model_label"] = primary["model"].map(MODEL_NAMES)
    primary_by_intensity["model_label"] = primary_by_intensity["model"].map(MODEL_NAMES)

    loio = leave_one_intensity_out(plants)
    loio["model_label"] = loio["model"].map(MODEL_NAMES)
    loio_by_intensity = (loio.groupby(["model", "I", "endpoint_extrapolation"],
                                      sort=True)
                         .agg(n_plants=("plant", "nunique"),
                              median_rmse_deg=("rmse_deg", "median"))
                         .reset_index())
    loio_by_intensity["model_label"] = loio_by_intensity["model"].map(MODEL_NAMES)

    print("Fitting all-data W3 for global parameter intervals", flush=True)
    all_fit = fit_w3(list(range(len(plants))), plants)
    intervals = cluster_sandwich_intervals(all_fit, plants)
    params = unpack(all_fit["x"])
    intensity_levels = sorted({float(p["I"]) for p in plants})
    equilibrium_rows = []
    for intensity in intensity_levels:
        gamma = float(gamma_of_intensity([intensity], all_fit["x"])[0])
        equilibrium_rows.append({
            "intensity_w_m2": intensity,
            "gamma_per_h": gamma,
            "model_implied_equilibrium_deg": equilibrium_angle(params["k"], gamma),
        })

    w3_primary = float(primary.loc[
        primary["model"] == "W3_gammaI_phiLight90", "median_rmse_deg"
    ].iloc[0])
    runtime = time.perf_counter() - started
    outputs = HERE / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    held.to_csv(outputs / "phase_e_w3_heldout_per_plant.csv", index=False)
    primary_by_intensity.to_csv(
        outputs / "phase_e_w3_primary_by_intensity.csv", index=False
    )
    loio.to_csv(outputs / "phase_e_w3_loio_per_plant.csv", index=False)
    loio_by_intensity.to_csv(
        outputs / "phase_e_w3_loio_by_intensity.csv", index=False
    )

    summary = {
        "analysis": "Phase E preregistered W3 intensity-dependent restoring term",
        "data_path": str(data_path.relative_to(PKG_ROOT)),
        "data_audit": audit,
        "seed": SEED,
        "n_folds": N_FOLDS,
        "fit_subsample_every_nth_observation": SUB,
        "integration_dt_h": FIT_DT,
        "physical_light_angle_deg": PHI_LIGHT,
        "baseline_success_threshold_deg": BASELINE_THRESHOLD_DEG,
        "primary_success": bool(w3_primary < BASELINE_THRESHOLD_DEG),
        "primary_median_rmse_deg": [
            {"model": MODEL_NAMES[row["model"]],
             "model_id": row["model"],
             "n_plants": int(row["n_plants"]),
             "median_rmse_deg": float(row["median_rmse_deg"]),
             "p25_rmse_deg": float(row["p25_rmse_deg"]),
             "p75_rmse_deg": float(row["p75_rmse_deg"])}
            for row in primary.to_dict("records")
        ],
        "baseline_reproduction_checks": baseline_checks,
        "primary_by_intensity": [
            {"model": MODEL_NAMES[row["model"]],
             "model_id": row["model"],
             "intensity_w_m2": float(row["I"]),
             "n_plants": int(row["n_plants"]),
             "median_rmse_deg": float(row["median_rmse_deg"])}
            for row in primary_by_intensity.to_dict("records")
        ],
        "loio_by_intensity": [
            {"model": MODEL_NAMES[row["model"]],
             "model_id": row["model"],
             "intensity_w_m2": float(row["I"]),
             "endpoint_extrapolation": bool(row["endpoint_extrapolation"]),
             "n_plants": int(row["n_plants"]),
             "median_rmse_deg": float(row["median_rmse_deg"])}
            for row in loio_by_intensity.to_dict("records")
        ],
        "fold_fits": fold_fits,
        "all_data_w3_fit": {
            "parameters_optimizer_scale": {
                name: float(value) for name, value in zip(PARAMETER_NAMES, all_fit["x"])
            },
            "parameters_physical": params,
            "gamma_at_1w_m2": float(np.exp(all_fit["x"][3])),
            "nfev": all_fit["nfev"],
            "success": all_fit["success"],
            "cost": all_fit["cost"],
            "confidence_intervals": intervals,
            "implied_by_intensity": equilibrium_rows,
        },
        "runtime_seconds": float(runtime),
        "runtime_minutes": float(runtime / 60.0),
    }
    summary_path = outputs / "phase_e_w3_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n",
                            encoding="utf-8")
    print(json.dumps({
        "seed": SEED,
        "runtime_seconds": runtime,
        "primary_success": summary["primary_success"],
        "primary_median_rmse_deg": summary["primary_median_rmse_deg"],
        "baseline_reproduction_checks": baseline_checks,
        "all_data_w3_parameters": params,
        "c1_ci95": intervals["parameters"]["c1"]["ci95"],
        "c1_distinguishable_from_zero": intervals["c1_distinguishable_from_zero"],
        "summary_path": str(summary_path.relative_to(PKG_ROOT)),
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
