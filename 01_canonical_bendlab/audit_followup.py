#!/usr/bin/env python3
"""Audit follow-up analyses (external audit, 2026-10-16).

Implements the checks the audit asked for, as written:

  H1  within-cluster parameter RANGES (not IQRs) vs the stated 20% rule
  H2  flip-vs-static spread reduction in percentage points of full range
  H3  behavioural-distance cliffs: adjacent pairs above 5x the median
      adjacent behavioural distance on the dense (k, tau) grid
  H7  protocol ranking at the full duration and at a matched 6 h budget,
      across three population seeds
  W   weighted-population sensitivity to the treatment of max_rate
      (point estimate / profile lower bound / independent prior / no cap)
  H6  crossover with phi0 held fixed (corrected round1.run_h4_h6)
  H8  fixed policy as specified (corrected round1.run_h8)

Outputs: results/audit_followup_summary.json and per-part CSV files.
"""
from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

import features as F
import round1
from generate_plants import PARAM_NAMES, weighted_population
from sim import batch_simulate, batch_simulate_static
from sweep import degeneracy_report, feature_frame

OUT = {}


def log(name, obj):
    OUT[name] = obj
    print(f"[{name}] {obj}", flush=True)


# --------------------------------------------------------------------- H1/H2
def h1_h2():
    feat = pd.read_csv("results/sweep_features.csv.gz")
    cols = list(F.STATIC_FEATURES)
    res = {}
    reports = {}
    for regime, extra in (("static", []), ("flip", ["reversal"])):
        sub = feat[feat["regime"] == regime]
        cl, _ = degeneracy_report(sub, cols + extra)
        reports[regime] = cl
        full = {n: float(sub[f"param_{n}"].max() - sub[f"param_{n}"].min())
                for n in PARAM_NAMES}
        res[regime] = {}
        for n in PARAM_NAMES:
            res[regime][n] = {
                "range_retention_median": float(
                    (cl[f"{n}_range"] / full[n]).median()),
                "iqr_retention_median": float(
                    (cl[f"{n}_iqr"] / full[n]).median()),
            }
    n_pass = sum(res["static"][n]["range_retention_median"] >= 0.20
                 for n in PARAM_NAMES)
    h2 = {n: (res["static"][n]["range_retention_median"]
              - res["flip"][n]["range_retention_median"]) * 100.0
          for n in PARAM_NAMES}
    log("H1_as_written", {
        "median_within_cluster_range_retention": {
            n: round(res["static"][n]["range_retention_median"], 3)
            for n in PARAM_NAMES},
        "params_retaining_>=20pct": int(n_pass),
        "criterion": "at least 3 of 4 parameters retain >= 20%",
        "supported_as_written": bool(n_pass >= 3)})
    log("H2_as_written", {
        "spread_reduction_percentage_points_range_basis": {
            n: round(v, 1) for n, v in h2.items()},
        "any_param_reduction_>=10pp": bool(any(v >= 10 for n, v in h2.items())),
        "all_params_reduced": bool(all(v > 0 for v in h2.values()))})
    rows = []
    for regime in res:
        for n in PARAM_NAMES:
            rows.append({"regime": regime, "parameter": n, **res[regime][n]})
    pd.DataFrame(rows).to_csv("results/audit_followup_h1h2.csv", index=False)


# ------------------------------------------------------------------------ H3
def h3():
    ks = np.linspace(*round1.H3_K, round1.H3_N)
    taus = np.linspace(*round1.H3_TAU, round1.H3_N)
    K, T = np.meshgrid(ks, taus)
    pop = round1.pop_frame(np.column_stack(
        [K.ravel(), T.ravel(), np.full(K.size, round1.H3_CAP),
         np.full(K.size, round1.H3_PHI0)]))
    t, th = batch_simulate(pop["k"], pop["tau"], pop["max_rate"], pop["phi0"],
                           round1.light_static, round1.T_END,
                           record_dt=round1.RECORD_DT)
    feat = feature_frame(t, th, pop, "static")
    X = StandardScaler().fit_transform(feat[list(F.STATIC_FEATURES)].to_numpy())
    Xg = X.reshape(round1.H3_N, round1.H3_N, -1)
    d_k = np.sqrt(((Xg[1:] - Xg[:-1]) ** 2).sum(axis=2)).ravel()
    d_t = np.sqrt(((Xg[:, 1:] - Xg[:, :-1]) ** 2).sum(axis=2)).ravel()
    d = np.concatenate([d_k, d_t])
    med = float(np.median(d))
    frac = float((d > 5 * med).mean())
    log("H3_as_written", {
        "grid": f"{round1.H3_N}x{round1.H3_N}",
        "median_adjacent_behavioural_distance": round(med, 4),
        "edges_above_5x_median": int((d > 5 * med).sum()),
        "edge_fraction": round(frac, 5),
        "max_over_median": round(float(d.max() / med), 2),
        "criterion": "any adjacent pair above 5x median supports H3",
        "supported_as_written": bool((d > 5 * med).any())})


# ------------------------------------------------------------------------ H7
def h7():
    clean = round1.clean_fits()
    rows = []
    for seed in (101, 202, 303):
        pop = round1.pop_frame(weighted_population(
            round1.H7_POP, seed, clean))
        params = pop[list(PARAM_NAMES)].to_numpy()
        span = (np.percentile(params, 95, axis=0)
                - np.percentile(params, 5, axis=0))
        rng = np.random.default_rng(seed + 1)
        for name, (dur, _) in round1.PROTOCOLS.items():
            t, th = round1.run_protocol(pop, name)
            obs = th + rng.normal(0.0, round1.SIGMA_OBS, th.shape)
            for budget, m in (("full", np.ones(len(t), bool)),
                              ("matched_6h", t <= 6.0 + 1e-9)):
                o = obs[m]
                nn = NearestNeighbors(n_neighbors=2).fit(o.T)
                _, idx = nn.kneighbors(o.T)
                rec = params[idx[:, 1]]
                rel = np.abs(params - rec) / span
                rows.append({"seed": seed, "protocol": name,
                             "cost_h": dur, "budget": budget,
                             "mean_rel_err": float(rel.mean())})
        print(f"[H7] seed {seed} done", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv("results/audit_followup_h7.csv", index=False)
    piv = (df.groupby(["protocol", "budget"])["mean_rel_err"]
             .agg(["mean", "std"]).reset_index())
    log("H7_matched_budget", piv.round(4).to_dict("records"))


# ------------------------------------------------------- weighted sensitivity
def weighted_sensitivity():
    clean = round1.clean_fits()
    # profile lower bound for max_rate: peak bend rate demanded by each
    # fitted plant when the cap is removed
    _, th = batch_simulate_static(
        clean["k"].to_numpy(), clean["tau"].to_numpy(),
        np.full(len(clean), 1e9), clean["phi0"].to_numpy(),
        24.0, record_dt=1.0 / 60.0)
    peak = np.abs(np.diff(th, axis=0)).max(axis=0) * 60.0
    variants = {}
    v = clean.copy(); variants["point_estimate"] = v
    v = clean.copy(); v["max_rate"] = np.maximum(peak, 0.5)
    variants["profile_lower_bound"] = v
    v = clean.copy()
    v["max_rate"] = np.random.default_rng(5).uniform(2.0, 40.0, len(v))
    variants["independent_prior"] = v
    v = clean.copy(); v["max_rate"] = 200.0
    variants["no_cap"] = v

    rows = []
    for name, frame in variants.items():
        pop = weighted_population(4000, seed=777, fit_frame=frame)
        pdf = round1.pop_frame(pop)
        t, th = batch_simulate_static(pop[:, 0], pop[:, 1], pop[:, 2],
                                      pop[:, 3], 24.0, record_dt=0.5)
        feat = feature_frame(t, th, pdf, "static")
        cl, labels = degeneracy_report(feat, list(F.STATIC_FEATURES))
        X = StandardScaler().fit_transform(
            feat[list(F.STATIC_FEATURES)].to_numpy())
        nn = NearestNeighbors(n_neighbors=2).fit(X)
        _, idx = nn.kneighbors(X)
        j = idx[:, 1]
        curve_rmse = np.sqrt((((th - th[:, j]) ** 2).mean(axis=0)))
        rel = (np.abs(pop - pop[j])
               / np.maximum(np.abs(pop), 1e-9))
        twin = curve_rmse < 0.5
        rows.append({
            "variant": name,
            "twin_frac_rmse<0.5deg": float(twin.mean()),
            "twin_and_param_differs>50pct_frac": float(
                (twin & (rel.max(axis=1) > 0.5)).mean()),
            **{f"{n}_iqr_retention": float(
                (cl[f"{n}_iqr"] / (pop[:, i].max() - pop[:, i].min())).median())
               for i, n in enumerate(PARAM_NAMES)},
        })
        print(f"[W] {name} done", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv("results/audit_followup_weighted.csv", index=False)
    log("weighted_maxrate_sensitivity", df.round(4).to_dict("records"))


def main():
    t0 = time.time()
    h1_h2()
    h3()
    h7()
    weighted_sensitivity()
    clean = round1.clean_fits()
    h46 = round1.run_h4_h6(clean)
    log("H6_phi_fixed", {k: h46[k] for k in
                         ("keep_same", "keep_diff_first", "keep_diff_any",
                          "n_same", "n_diff")})
    best = pd.read_csv("results/round1_h7_protocols.csv").iloc[0]["protocol"]
    h8 = round1.run_h8(clean, str(best))
    log("H8_fixed_policy", h8.to_dict("records"))
    with open("results/audit_followup_summary.json", "w") as fh:
        json.dump(OUT, fh, indent=2)
    print(f"done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
