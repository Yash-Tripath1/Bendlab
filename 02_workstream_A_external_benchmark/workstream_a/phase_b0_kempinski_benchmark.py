"""Phase B0 Workstream A: external benchmark of BendLab's scalar tip-angle
model on the Kempinski et al. (2026) unilateral-light archive.

Standalone analysis. It imports the canonical model read-only from the
packaged snapshot (01_canonical_bendlab/sim.py; falls back to the
repository-root sim.py, which is the same model) and does NOT modify it.
The published model has
no light-intensity input: intensity enters only through a clearly
separated wrapper fitted here on training data only,

    k(I) = a * I**b        (wrapper intensity law, this file only)
    phi  = 90 deg          (fixed horizontal side light, shared, known)
    tau, max_rate shared;  theta(0) = each plant's observed initial angle

A second diagnostic wrapper (W2) additionally lets an effective target
angle phi_eff(I) vary with intensity. W2 is a structural diagnostic, not
a candidate published model: it shows what the scalar model must absorb
into phi0 to represent intensity-dependent steady states.

Evaluation is leakage-safe: plants are never split across train/test;
plant-held-out folds are stratified by intensity; leave-one-intensity-
group-out (LOIO) fits never see the held group. Endpoints (0.7, 5.8
W/m^2) are extrapolation and are reported separately.

Run:  python phase_b0_kempinski_benchmark.py [path_to_uni_trajectories.csv]
Outputs land in ./outputs/ next to this script.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parents[1]                      # repository/package root
_MODEL_DIR = PKG_ROOT / "01_canonical_bendlab"  # packaged canonical snapshot
if not (_MODEL_DIR / "sim.py").exists():
    _MODEL_DIR = PKG_ROOT                       # plain repository checkout
sys.path.insert(0, str(_MODEL_DIR))             # canonical model, read-only
from sim import batch_simulate                    # noqa: E402

_ap = argparse.ArgumentParser(description=__doc__)
_ap.add_argument("--data", type=Path, default=PKG_ROOT / "05_data_external"
                 / "uni_trajectories.csv",
                 help="path to uni_trajectories.csv (default: packaged copy)")
_ap.add_argument("--fit-subsample", type=int, default=4,
                 help="fit on every Nth observation (default 4, about "
                      "16-minute spacing; 1 = every observation)")
_ARGS = _ap.parse_args()
DATA = _ARGS.data
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
SEED = 42
PHI_LIGHT = 90.0          # horizontal side light, degrees from vertical
FIT_DT = 1.0 / 60.0       # model contract step (1 min)
SUB = _ARGS.fit_subsample    # fit subsampling (see --fit-subsample); eval on all points


# ---------------------------------------------------------------- data ----
def load_plants(path):
    df = pd.read_csv(path)
    plants = []
    for pid, g in df.sort_values(["real_id", "dt"]).groupby("real_id"):
        g = g.reset_index(drop=True)
        plants.append({
            "id": pid, "I": float(g["light_i"].iloc[0]),
            "t": g["dt"].to_numpy(float), "theta": g["theta"].to_numpy(float),
            "side": pid.split("_")[2]})
    return df, plants


def audit(df, plants):
    sizes = df.groupby("real_id").size()
    per_plant_I = df.groupby("real_id")["light_i"].nunique()
    intervals = df.sort_values(["real_id", "dt"]).groupby("real_id")["dt"].diff()
    t0 = df[df["dt"] == 0]
    a = {
        "rows": int(len(df)), "plants": int(df["real_id"].nunique()),
        "columns": list(df.columns), "missing_values": int(df.isna().sum().sum()),
        "duplicated_plant_time": int(df.duplicated(["real_id", "dt"]).sum()),
        "intensity_groups_W_m2": sorted(df["light_i"].unique().tolist()),
        "plants_per_intensity": {str(k): int(v) for k, v in
                                 df.groupby("light_i")["real_id"].nunique().items()},
        "plants_with_multiple_intensities": int((per_plant_I > 1).sum()),
        "rows_per_plant_min_med_max": [int(sizes.min()), float(sizes.median()),
                                       int(sizes.max())],
        "time_range_h": [float(df["dt"].min()), float(df["dt"].max())],
        "sampling_interval_h_median": float(intervals.median()),
        "theta_range_deg": [float(df["theta"].min()), float(df["theta"].max())],
        "initial_theta_deg_mean_min_max": [float(t0["theta"].mean()),
                                           float(t0["theta"].min()),
                                           float(t0["theta"].max())],
        "archive_light_max_W_m2": float(df["light_i"].max()),
        "paper_stated_unilateral_range_W_m2": [0.7, 7.0],
        "discrepancy_flag": ("paper states unilateral intensities up to "
                             "7 W/m^2; archive light_i tops out at 5.8 W/m^2"),
    }
    return a


# --------------------------------------------------------------- model ----
def simulate_population(plants_idx, plants, k_per_plant, tau, max_rate,
                        phi_per_plant):
    """Predict on each plant's own observed times (1-min integration)."""
    sub = [plants[i] for i in plants_idx]
    t_end = max(p["t"].max() for p in sub)
    k = np.array([k_per_plant[p["id"]] for p in sub])
    phi = np.array([phi_per_plant[p["id"]] for p in sub])
    th0 = np.array([p["theta"][0] for p in sub])
    times, thetas = batch_simulate(k, np.full(len(sub), tau),
                                   np.full(len(sub), max_rate), phi,
                                   t_end=t_end, dt=FIT_DT, theta0=th0)
    return {p["id"]: np.interp(p["t"], times, thetas[:, j])
            for j, p in enumerate(sub)}


def fit_wrapper(train_idx, plants, phi_mode):
    """Fit (a, b, tau, max_rate[, phi_eff params]) on training plants only.

    phi_mode 'fixed90': phi=90 for all. 'phi_of_I': phi_eff(I)=clip(c0+c1*logI)
    shared law fitted on train only (LOIO interpolates by construction).
    """
    train = [plants[i] for i in train_idx]
    use = [(p, slice(None, None, SUB)) for p in train]

    def unpack(x):
        a, b, tau, mr = np.exp(x[0]), x[1], np.exp(x[2]), np.exp(x[3])
        if phi_mode == "phi_of_I":
            return a, b, tau, mr, (x[4], x[5])
        return a, b, tau, mr, None

    def residuals(x):
        a, b, tau, mr, phip = unpack(x)
        kpp = {p["id"]: a * p["I"] ** b for p in train}
        if phip is None:
            php = {p["id"]: PHI_LIGHT for p in train}
        else:
            php = {p["id"]: float(np.clip(phip[0] + phip[1] * np.log(p["I"]),
                                          5, 95)) for p in train}
        pred = simulate_population(train_idx, plants, kpp, tau, mr, php)
        return np.concatenate([pred[p["id"]][sl] - p["theta"][sl]
                               for p, sl in use])

    x0 = [np.log(2.0), 0.3, np.log(2.0), np.log(20.0)]
    lo = [np.log(0.01), -0.5, np.log(0.05), np.log(0.5)]
    hi = [np.log(80.0), 2.0, np.log(40.0), np.log(60.0)]
    if phi_mode == "phi_of_I":
        x0 += [30.0, 5.0]; lo += [0.0, -40.0]; hi += [90.0, 40.0]
    sol = least_squares(residuals, x0, bounds=(lo, hi), x_scale="jac",
                        max_nfev=120)
    a, b, tau, mr, phip = unpack(sol.x)
    return {"a": a, "b": b, "tau": tau, "max_rate": mr, "phi_params": phip,
            "train_cost": float(sol.cost)}


def predict_wrapper(model, test_idx, plants):
    kpp, php = {}, {}
    for i in test_idx:
        p = plants[i]
        kpp[p["id"]] = model["a"] * p["I"] ** model["b"]
        if model["phi_params"] is None:
            php[p["id"]] = PHI_LIGHT
        else:
            c0, c1 = model["phi_params"]
            php[p["id"]] = float(np.clip(c0 + c1 * np.log(p["I"]), 5, 95))
    return simulate_population(test_idx, plants, kpp, model["tau"],
                               model["max_rate"], php)


# ------------------------------------------------------------ baselines ----
GRID = np.round(np.arange(0, 22.0001, 1 / 15), 4)


def group_mean_curves(train_idx, plants):
    curves = {}
    for i in train_idx:
        p = plants[i]
        curves.setdefault(p["I"], []).append(np.interp(GRID, p["t"], p["theta"]))
    return {I: np.mean(v, axis=0) for I, v in curves.items()}


def predict_group_mean(means, test_idx, plants, recenter=False):
    out = {}
    Is = sorted(means)
    for i in test_idx:
        p = plants[i]
        if p["I"] in means:
            curve = means[p["I"]]
        else:  # interpolate in log I; endpoints clamp (extrapolation)
            li = np.log(p["I"])
            lIs = np.log(Is)
            w = np.clip((li - lIs[0]) / (lIs[-1] - lIs[0]), 0, 1)
            lo_I, hi_I = Is[0], Is[-1]
            for a_, b_ in zip(Is[:-1], Is[1:]):
                if a_ <= p["I"] <= b_:
                    lo_I, hi_I = a_, b_
                    w = (li - np.log(a_)) / (np.log(b_) - np.log(a_))
                    break
            curve = (1 - w) * means[lo_I] + w * means[hi_I]
        pred = np.interp(p["t"], GRID, curve)
        if recenter:
            base = np.interp(p["t"][0], GRID, curve)
            pred = pred + (p["theta"][0] - base)
        out[p["id"]] = pred
    return out


def fit_saturating(train_idx, plants):
    train = [plants[i] for i in train_idx]

    def resid(x):
        A, b, tau_s = np.exp(x[0]), x[1], np.exp(x[2])
        r = []
        for p in train:
            inf = min(88.0, A * p["I"] ** b)
            pred = p["theta"][0] + (inf - p["theta"][0]) * (
                1 - np.exp(-p["t"][::SUB] / tau_s))
            r.append(pred - p["theta"][::SUB])
        return np.concatenate(r)

    sol = least_squares(resid, [np.log(15.0), 0.3, np.log(6.0)],
                        bounds=([np.log(1.0), -0.5, np.log(0.2)],
                                [np.log(120.0), 2.0, np.log(60.0)]),
                        x_scale="jac", max_nfev=100)
    return {"A": float(np.exp(sol.x[0])), "b": float(sol.x[1]),
            "tau_s": float(np.exp(sol.x[2]))}


def predict_saturating(m, test_idx, plants):
    out = {}
    for i in test_idx:
        p = plants[i]
        inf = min(88.0, m["A"] * p["I"] ** m["b"])
        out[p["id"]] = p["theta"][0] + (inf - p["theta"][0]) * (
            1 - np.exp(-p["t"] / m["tau_s"]))
    return out


# -------------------------------------------------------------- metrics ----
def per_plant_metrics(pred, plants_idx_list, plants, pred_name):
    by_id = {p["id"]: p for p in plants}
    rows = []
    for pid, pr in pred.items():
        p = by_id[pid]
        err = pr - p["theta"]
        row = {"plant": pid, "I": p["I"], "model": pred_name,
               "rmse_deg": float(np.sqrt(np.mean(err ** 2))),
               "mae_deg": float(np.mean(np.abs(err))),
               "final_err_deg": float(pr[-1] - p["theta"][-1])}
        for lo, hi in ((0, 2), (2, 6), (6, 12), (12, 22.01), (4, 22.01)):
            m = (p["t"] >= lo) & (p["t"] < hi)
            row[f"rmse_{lo:g}_{min(hi,22):g}h"] = float(
                np.sqrt(np.mean(err[m] ** 2))) if m.any() else np.nan
        rows.append(row)
    return rows


def summarise(rows, name):
    d = pd.DataFrame(rows)
    return {"model": name, "n_plants": int(len(d)),
            "median_rmse_deg": float(d["rmse_deg"].median()),
            "p25_rmse_deg": float(d["rmse_deg"].quantile(.25)),
            "p75_rmse_deg": float(d["rmse_deg"].quantile(.75)),
            "median_final_err_deg": float(d["final_err_deg"].median()),
            "mean_final_err_deg": float(d["final_err_deg"].mean())}


def stratified_folds(plants, n_folds=5, seed=SEED):
    rng = np.random.default_rng(seed)
    by_I = {}
    for i, p in enumerate(plants):
        by_I.setdefault(p["I"], []).append(i)
    folds = [[] for _ in range(n_folds)]
    for I, idxs in sorted(by_I.items()):
        idxs = list(idxs); rng.shuffle(idxs)
        for j, i in enumerate(idxs):
            folds[j % n_folds].append(i)
    return folds


# ------------------------------------------------------------------ main ----
def main():
    df, plants = load_plants(DATA)
    report = {"data_audit": audit(df, plants)}
    idx_by_id = {p["id"]: i for i, p in enumerate(plants)}
    all_rows = []

    # ---- plant-held-out, stratified by intensity (5-fold)
    folds = stratified_folds(plants)
    held_rows = []
    for f in range(len(folds)):
        test_idx = folds[f]
        train_idx = [i for j, fo in enumerate(folds) if j != f for i in fo]
        for name, fit_fn, pred_fn in (
                ("W1_bendlab_kI_phi90", lambda tr: fit_wrapper(tr, plants, "fixed90"),
                 lambda m, te: predict_wrapper(m, te, plants)),
                ("W2_bendlab_kI_phiI_diagnostic", lambda tr: fit_wrapper(tr, plants, "phi_of_I"),
                 lambda m, te: predict_wrapper(m, te, plants)),
                ("B2_saturating", lambda tr: fit_saturating(tr, plants),
                 lambda m, te: predict_saturating(m, te, plants))):
            m = fit_fn(train_idx)
            held_rows += per_plant_metrics(pred_fn(m, test_idx), test_idx,
                                           plants, name)
        means = group_mean_curves(train_idx, plants)
        held_rows += per_plant_metrics(
            predict_group_mean(means, test_idx, plants), test_idx, plants,
            "B1_group_mean_curve")
        held_rows += per_plant_metrics(
            predict_group_mean(means, test_idx, plants, recenter=True),
            test_idx, plants, "B1r_group_mean_recentered")
        pers = {plants[i]["id"]: np.full(len(plants[i]["t"]),
                                         plants[i]["theta"][0])
                for i in test_idx}
        held_rows += per_plant_metrics(pers, test_idx, plants, "B0_persistence")
    held = pd.DataFrame(held_rows)
    held.to_csv(str(OUT / "plant_heldout_per_plant.csv"), index=False)
    report["plant_heldout"] = [summarise(held[held.model == m], m)
                               for m in held.model.unique()]
    report["plant_heldout_by_intensity"] = (
        held.groupby(["model", "I"])["rmse_deg"].median().round(3)
        .unstack(0).reset_index().to_dict("records"))

    # plant-level bootstrap: W1 minus B1 median RMSE
    piv = held.pivot_table(index="plant", columns="model", values="rmse_deg")
    rng = np.random.default_rng(SEED)
    diffs = []
    vals = (piv["W1_bendlab_kI_phi90"] - piv["B1_group_mean_curve"]).to_numpy()
    for _ in range(2000):
        diffs.append(np.median(rng.choice(vals, size=len(vals), replace=True)))
    report["bootstrap_W1_minus_B1_median_rmse_deg"] = {
        "design": "unstratified plant bootstrap (batch structure unknown)",
        "point": float(np.median(vals)),
        "ci95": [float(np.percentile(diffs, 2.5)),
                 float(np.percentile(diffs, 97.5))]}
    # stratified sensitivity: resample plants within each intensity stratum
    piv_i = held.pivot_table(index="plant", columns="model",
                             values="rmse_deg")
    I_of = {p["id"]: p["I"] for p in plants}
    piv_i["I"] = [I_of[i] for i in piv_i.index]
    strata = [g["W1_bendlab_kI_phi90"].to_numpy()
              - g["B1_group_mean_curve"].to_numpy()
              for _, g in piv_i.groupby("I")]
    sdiffs = []
    for _ in range(2000):
        pooled = np.concatenate([rng.choice(v, size=len(v), replace=True)
                                 for v in strata])
        sdiffs.append(np.median(pooled))
    report["bootstrap_stratified_W1_minus_B1_median_rmse_deg"] = {
        "design": "plant bootstrap stratified by intensity group",
        "point": float(np.median(np.concatenate(strata))),
        "ci95": [float(np.percentile(sdiffs, 2.5)),
                 float(np.percentile(sdiffs, 97.5))]}

    # ---- leave-one-intensity-group-out
    intensities = sorted({p["I"] for p in plants})
    loio_rows = []
    for I in intensities:
        test_idx = [i for i, p in enumerate(plants) if p["I"] == I]
        train_idx = [i for i, p in enumerate(plants) if p["I"] != I]
        m1 = fit_wrapper(train_idx, plants, "fixed90")
        loio_rows += per_plant_metrics(predict_wrapper(m1, test_idx, plants),
                                       test_idx, plants, "W1_bendlab_kI_phi90")
        m2 = fit_wrapper(train_idx, plants, "phi_of_I")
        loio_rows += per_plant_metrics(predict_wrapper(m2, test_idx, plants),
                                       test_idx, plants, "W2_bendlab_kI_phiI_diagnostic")
        means = group_mean_curves(train_idx, plants)
        loio_rows += per_plant_metrics(predict_group_mean(means, test_idx, plants),
                                       test_idx, plants, "B1_group_mean_curve")
        ms = fit_saturating(train_idx, plants)
        loio_rows += per_plant_metrics(predict_saturating(ms, test_idx, plants),
                                       test_idx, plants, "B2_saturating")
    loio = pd.DataFrame(loio_rows)
    loio.to_csv(str(OUT / "loio_per_plant.csv"), index=False)
    loio_sum = (loio.groupby(["model", "I"])["rmse_deg"].median()
                .unstack(0).reset_index())
    loio_sum["endpoint_extrapolation"] = loio_sum["I"].isin(
        [intensities[0], intensities[-1]])
    report["loio_median_rmse_deg"] = loio_sum.round(3).to_dict("records")

    # ---- per-plant calibration: fit on t<=4 h, forecast t>4 h
    calib_rows = []
    for i, p in enumerate(plants):
        early = p["t"] <= 4.0

        def resid(x, p=p, early=early):
            k, tau = np.exp(x[0]), np.exp(x[1])
            times, th = batch_simulate([k], [tau], [40.0], [PHI_LIGHT],
                                       t_end=float(p["t"].max()), dt=1 / 15,
                                       theta0=[p["theta"][0]])
            pred = np.interp(p["t"], times, th[:, 0])
            return (pred - p["theta"])[early]

        sol = least_squares(resid, [np.log(3.0), np.log(2.0)],
                            bounds=([np.log(0.01), np.log(0.05)],
                                    [np.log(80.0), np.log(40.0)]),
                            max_nfev=60)
        k, tau = float(np.exp(sol.x[0])), float(np.exp(sol.x[1]))
        times, th = batch_simulate([k], [tau], [40.0], [PHI_LIGHT],
                                   t_end=float(p["t"].max()), dt=1 / 15,
                                   theta0=[p["theta"][0]])
        pred = np.interp(p["t"], times, th[:, 0])
        late = ~early
        calib_rows.append({
            "plant": p["id"], "I": p["I"], "k_fit": k, "tau_fit": tau,
            "rmse_forecast_4_22h_deg": float(np.sqrt(
                np.mean((pred[late] - p["theta"][late]) ** 2))),
            "final_err_deg": float(pred[-1] - p["theta"][-1])})
    calib = pd.DataFrame(calib_rows)
    calib.to_csv(str(OUT / "per_plant_calibration.csv"), index=False)
    report["per_plant_calibration_4h_to_22h"] = {
        "median_forecast_rmse_deg": float(calib["rmse_forecast_4_22h_deg"].median()),
        "median_final_err_deg": float(calib["final_err_deg"].median())}
    # population-model forecast error on the same 4-22 h window, from the
    # plant-held-out predictions (fair, same plants/window):
    late_rows = held[held.model == "W1_bendlab_kI_phi90"]
    report["population_W1_forecast_rmse_12_22h_median_deg"] = float(
        late_rows["rmse_12_22h"].median())
    report["population_W1_rmse_4_22h_common_window_median_deg"] = float(
        late_rows["rmse_4_22h"].median())

    # ---- diagnostic: per-plant full-curve fits, phi fixed 90 vs phi free
    diag = []
    for i, p in enumerate(plants):
        for mode in ("phi90", "phi_free"):
            def resid(x, p=p, mode=mode):
                if mode == "phi90":
                    k, tau, mr, phi = np.exp(x[0]), np.exp(x[1]), np.exp(x[2]), PHI_LIGHT
                else:
                    k, tau, mr, phi = np.exp(x[0]), np.exp(x[1]), np.exp(x[2]), x[3]
                times, th = batch_simulate([k], [tau], [mr], [phi],
                                           t_end=float(p["t"].max()), dt=1 / 15,
                                           theta0=[p["theta"][0]])
                pred = np.interp(p["t"], times, th[:, 0])
                return (pred - p["theta"])[::SUB]

            x0 = [np.log(3.0), np.log(2.0), np.log(20.0)]
            lo = [np.log(0.01), np.log(0.05), np.log(0.5)]
            hi = [np.log(80.0), np.log(40.0), np.log(60.0)]
            if mode == "phi_free":
                x0 += [30.0]; lo += [0.0]; hi += [95.0]
            sol = least_squares(resid, x0, bounds=(lo, hi), max_nfev=80)
            phi_fit = PHI_LIGHT if mode == "phi90" else float(sol.x[3])
            times, th = batch_simulate(
                [float(np.exp(sol.x[0]))], [float(np.exp(sol.x[1]))],
                [float(np.exp(sol.x[2]))], [phi_fit],
                t_end=float(p["t"].max()), dt=1 / 15, theta0=[p["theta"][0]])
            pred = np.interp(p["t"], times, th[:, 0])
            diag.append({"plant": p["id"], "I": p["I"], "mode": mode,
                         "rmse_deg": float(np.sqrt(np.mean((pred - p["theta"]) ** 2))),
                         "phi_fit_deg": phi_fit,
                         "k_fit": float(np.exp(sol.x[0])),
                         "tau_fit": float(np.exp(sol.x[1])),
                         "max_rate_fit": float(np.exp(sol.x[2]))})
    diag = pd.DataFrame(diag)
    diag.to_csv(str(OUT / "per_plant_fullfit_diagnostic.csv"), index=False)
    free = diag[diag["mode"] == "phi_free"]
    report["per_plant_fullfit_diagnostic"] = {
        "median_rmse_phi90_deg": float(diag[diag["mode"] == "phi90"]["rmse_deg"].median()),
        "median_rmse_phi_free_deg": float(free["rmse_deg"].median()),
        "phi_free_median_deg": float(free["phi_fit_deg"].median()),
        "phi_free_p25_p75_deg": [float(free["phi_fit_deg"].quantile(.25)),
                                 float(free["phi_fit_deg"].quantile(.75))],
        "note": "phi_free is an effective equilibrium/target angle per plant, "
                "not the known 90 deg lamp geometry"}

    with open(str(OUT / "benchmark_summary.json"), "w") as fh:
        json.dump(report, fh, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
