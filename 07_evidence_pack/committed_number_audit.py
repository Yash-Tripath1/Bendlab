#!/usr/bin/env python3
"""Print and save numbers derived from committed outputs, without refitting.

The only fresh numerical calculation is the documented H4 simulation and
clustering reproduction, because no dedicated machine-readable H4 output is
committed. It reuses the committed fit parameters, population generator,
simulator, features, and round1.py settings. It does not call a fit optimizer.
A small deterministic simulator convention check also runs from the committed
root sim.py. All artifacts are written under 07_evidence_pack/outputs/.

Run from any directory with:
    python 07_evidence_pack/committed_number_audit.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT
sys.path.insert(0, str(CANONICAL))

import round1  # noqa: E402
from generate_plants import PARAM_NAMES, weighted_population  # noqa: E402

FIT_FILE = CANONICAL / "results/fit_fig1c.csv"
MODEL_SELECTION_FILE = CANONICAL / "results/exp_design_model_selection.csv"
PHASE_E_FILE = ROOT / "02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json"
B0_FILE = ROOT / "02_workstream_A_external_benchmark/workstream_a/outputs/benchmark_summary.json"
IDENTIFIABILITY_FILE = ROOT / "07_evidence_pack/outputs/identifiability_count.json"
OUTPUT_FILE = ROOT / "07_evidence_pack/outputs/committed_number_audit.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_module(path: Path, alias: str):
    spec = importlib.util.spec_from_file_location(alias, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reproduce_h4_ari(clean_fits: pd.DataFrame) -> dict:
    """Reproduce round1.py H4 ARI only, with no parameter fitting."""
    population_seed = round1.SEED_BASE + 8
    pop_values = weighted_population(round1.H4_POP, population_seed, clean_fits)
    population = round1.pop_frame(pop_values)

    def labels_for(light_fn, regime: str) -> np.ndarray:
        times, theta = round1.batch_simulate(
            population["k"], population["tau"], population["max_rate"],
            population["phi0"], light_fn, round1.T_END,
            record_dt=round1.RECORD_DT,
        )
        features = round1.feature_frame(times, theta, population, regime)
        values = features[round1.FEAT_COLS].to_numpy(float)
        standardized = StandardScaler().fit_transform(values)
        return KMeans(
            round1.N_CLUSTERS,
            n_init=10,
            random_state=round1.SEED_BASE,
        ).fit_predict(standardized)

    static_labels = labels_for(round1.light_static, "static")
    sweep_labels = labels_for(round1.light_sweep12, "sweep")
    ari = float(adjusted_rand_score(static_labels, sweep_labels))
    require(round(population.shape[0]) == 6000,
            f"H4 population size is {population.shape[0]}, expected 6000")
    return {
        "ari_static_vs_sweep": ari,
        "n_simulated_parameter_vectors": int(len(population)),
        "n_clusters": int(round1.N_CLUSTERS),
        "population_seed": int(population_seed),
        "kmeans_seed": int(round1.SEED_BASE),
        "kmeans_n_init": 10,
        "duration_hours": float(round1.T_END),
        "record_interval_hours": float(round1.RECORD_DT),
        "persistence_threshold": float(round1.H4_ARI_PERSIST),
        "reported_ari_three_decimals": round(ari, 3),
        "source_code": "01_canonical_bendlab/round1.py::run_h4_h6",
        "reproduction_scope": (
            "H4 static-versus-sweep simulation and clustering only; H6 is not run"
        ),
    }


def main() -> None:
    fits = pd.read_csv(FIT_FILE)
    require(len(fits) == 48, f"Expected 48 saved Fig1C fit rows, found {len(fits)}")
    clean = fits.loc[fits["at_bound"] == "[]"].copy()
    require(len(clean) == 44, f"Expected 44 clean fits, found {len(clean)}")

    model_selection = pd.read_csv(MODEL_SELECTION_FILE)
    selected = model_selection.loc[
        (model_selection["separation_deg"] == 160.0)
        & (model_selection["intensity_ratio"] == 2.0)
        & (model_selection["n_seedlings"] == 20)
    ].copy()
    require(len(selected) == 3, "Expected one model-selection row per true mechanism")
    replicate_total = int(selected["reps"].sum())
    success_total = float((selected["p_correct"] * selected["reps"]).sum())
    require(abs(success_total - round(success_total)) < 1e-10,
            "Model-selection success count is not integral")
    model_selection_result = {
        "separation_degrees": 160,
        "intensity_ratio": 2.0,
        "seedlings_per_dataset": 20,
        "true_mechanism_rows": [
            {
                "true_model": str(row.true_model),
                "replicates": int(row.reps),
                "correct_selection_fraction": float(row.p_correct),
            }
            for row in selected.itertuples()
        ],
        "correct_selections": int(round(success_total)),
        "datasets_total": replicate_total,
        "pooled_correct_fraction": success_total / replicate_total,
        "source_output": str(MODEL_SELECTION_FILE.relative_to(ROOT)),
        "producer": "01_canonical_bendlab/exp_design_model_selection.py",
    }
    require(replicate_total == 75 and round(success_total) == 72,
            "The committed 20-seedling model-selection result changed")

    h4 = reproduce_h4_ari(clean)
    require(h4["reported_ari_three_decimals"] == 0.442,
            f"Reproduced H4 ARI is {h4['reported_ari_three_decimals']}, expected 0.442")

    canonical_fit_result = {
        "n_saved_fits": int(len(fits)),
        "median_in_sample_rmse_degrees": float(fits["rmse"].median()),
        "median_across_plant_spread_degrees": float(fits["spread"].median()),
        "fits_not_at_any_optimization_bound": int((fits["at_bound"] == "[]").sum()),
        "source_output": str(FIT_FILE.relative_to(ROOT)),
        "producer": "01_canonical_bendlab/fit_real.py::main and plant_spread",
        "derivation_note": (
            "The in-sample RMSE and spread medians are recomputed from the saved "
            "per-plant CSV because no separate overall summary field is stored."
        ),
    }

    phase_e = json.loads(PHASE_E_FILE.read_text(encoding="utf-8"))
    b0 = json.loads(B0_FILE.read_text(encoding="utf-8"))
    baseline_checks = phase_e["baseline_reproduction_checks"]
    require(len(baseline_checks) == 5, "Expected five Phase E baseline checks")
    require(all(bool(row["within_tolerance"]) for row in baseline_checks),
            "At least one Phase E baseline reproduction check fails its saved tolerance")
    w1_b0 = next(row["median_rmse_deg"] for row in b0["plant_heldout"]
                 if row["model"] == "W1_bendlab_kI_phi90")
    w1_phase_e = next(row["reproduced_median_rmse_deg"] for row in baseline_checks
                      if row["model"] == "W1")
    phase_e_result = {
        "primary_success": bool(phase_e["primary_success"]),
        "fixed_threshold_degrees": float(phase_e["baseline_success_threshold_deg"]),
        "w3_primary_median_rmse_degrees": float(
            next(row["median_rmse_deg"] for row in phase_e["primary_median_rmse_deg"]
                 if row["model"] == "W3")
        ),
        "baseline_reproduction_checks": baseline_checks,
        "all_five_baselines_within_tolerance": True,
        "w1_b0_median_degrees": float(w1_b0),
        "w1_phase_e_reproduced_median_degrees": float(w1_phase_e),
        "w1_cross_run_delta_degrees": float(w1_phase_e - w1_b0),
        "w1_rounding": {
            "two_decimals": round(float(w1_b0), 2),
            "four_decimals": round(float(w1_b0), 4),
        },
        "phase_e_source_output": str(PHASE_E_FILE.relative_to(ROOT)),
        "b0_source_output": str(B0_FILE.relative_to(ROOT)),
    }
    require(round(float(w1_b0), 2) == 14.41 and round(float(w1_b0), 4) == 14.4072,
            "W1 rounding audit did not reproduce the documented values")

    # The check uses the committed root simulator and its default static-light
    # function. The old prose did not preserve k, tau, or max_rate, so those
    # explicit test values are recorded rather than implied to be historical.
    root_sim = load_module(ROOT / "sim.py", "bendlab_root_sim_for_evidence")
    start_angles = np.array([5.0, 40.0])
    sim_times, sim_theta = root_sim.batch_simulate(
        np.array([10.0, 10.0]),
        np.array([2.2, 2.2]),
        np.array([200.0, 200.0]),
        np.array([90.0, 90.0]),
        t_end=24.0,
        dt=1.0 / 60.0,
        theta0=start_angles,
    )
    terminal_angles = sim_theta[-1].astype(float).tolist()
    require(len(sim_times) == 1441, "Expected 24 hours at one-minute simulator steps")
    require(abs(terminal_angles[0] - 90.7) < 0.1,
            f"phi=90, theta0=5 check ended at {terminal_angles[0]}, not near 90.7")
    require(np.all(sim_theta[0] == start_angles),
            "The simulator did not preserve the two supplied theta0 values")
    simulator_check = {
        "source_code": "sim.py::batch_simulate",
        "static_light_interface": "default light_fn uses each supplied phi0",
        "phi_degrees": [90.0, 90.0],
        "theta0_degrees": start_angles.tolist(),
        "k_degrees_per_hour": [10.0, 10.0],
        "tau_hours": [2.2, 2.2],
        "max_rate_degrees_per_hour": [200.0, 200.0],
        "dt_hours": 1.0 / 60.0,
        "duration_hours": 24.0,
        "terminal_theta_degrees": terminal_angles,
        "theta0_5_terminal_rounded_1dp": round(terminal_angles[0], 1),
        "test_values_are_explicitly_chosen": True,
        "fit_or_parameter_optimization_run": False,
    }

    identifiability = json.loads(IDENTIFIABILITY_FILE.read_text(encoding="utf-8"))
    reconciliation = {
        "phase_a_jacobian_flag_count": int(
            identifiability["historical_phase_a_jacobian_criterion"]["saved_uncertainty_table_count"]
        ),
        "direct_observed_peak_cap_above_count": int(
            identifiability["direct_observed_peak_rate_criterion"][
                "fitted_cap_above_observed_peak_count"
            ]
        ),
        "direct_observed_peak_cap_at_or_below_count": int(
            identifiability["direct_observed_peak_rate_criterion"][
                "cap_at_or_below_observed_peak_count"
            ]
        ),
        "source_output": str(IDENTIFIABILITY_FILE.relative_to(ROOT)),
    }

    result = {
        "analysis": "Derived committed-output audit and no-fit checks",
        "model_fits_rerun": False,
        "canonical_fig1c_aggregate": canonical_fit_result,
        "model_selection_20_seedlings": model_selection_result,
        "h4_ari_reproduction": h4,
        "phase_e_baseline_and_w1_rounding": phase_e_result,
        "max_rate_identifiability_reconciliation": reconciliation,
        "root_simulator_frame_check": simulator_check,
        "input_files": [
            str(FIT_FILE.relative_to(ROOT)),
            str(MODEL_SELECTION_FILE.relative_to(ROOT)),
            str(PHASE_E_FILE.relative_to(ROOT)),
            str(B0_FILE.relative_to(ROOT)),
            str(IDENTIFIABILITY_FILE.relative_to(ROOT)),
        ],
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        "Saved-fit medians: in-sample RMSE "
        f"{canonical_fit_result['median_in_sample_rmse_degrees']:.4f} deg; "
        "spread "
        f"{canonical_fit_result['median_across_plant_spread_degrees']:.4f} deg."
    )
    print(
        "Model selection: "
        f"{model_selection_result['correct_selections']}/"
        f"{model_selection_result['datasets_total']} = "
        f"{model_selection_result['pooled_correct_fraction']:.1%}."
    )
    print(
        f"H4 ARI reproduced: {h4['ari_static_vs_sweep']:.6f} "
        f"(reported to three decimals: {h4['reported_ari_three_decimals']:.3f})."
    )
    print(
        "Static phi=90 check terminals: "
        + ", ".join(f"{value:.6f}" for value in terminal_angles)
        + " degrees."
    )
    print(f"Wrote {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
