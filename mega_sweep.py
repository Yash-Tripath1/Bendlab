"""Mega-scale uniform-population sweep.

This is the heavy companion to big_sweep.py: 400,000 simulated plants,
five light regimes, cross-regime cluster agreement, nearest-neighbour
parameter recovery, and an exact trajectory-twin search for 20,000 query
plants. It writes incremental progress to the console/log.
"""

from __future__ import annotations

import json
import os
import time

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

import big_sweep as B
import features as F
from generate_plants import PARAM_NAMES, uniform_population
from sim import batch_simulate, batch_simulate_static
from sweep import feature_frame

SEED = 20261014
N = 400_000
TWIN_QUERIES = 20_000
NN_QUERIES = 10_000

OUT_CLUSTERS = "results/mega_sweep_clusters.csv"
OUT_PROTOCOLS = "results/mega_sweep_protocol_agreement.csv"
OUT_NN = "results/mega_sweep_nearest_neighbour.csv"
OUT_TWINS = "results/mega_sweep_twins.csv"
OUT_SUMMARY = "results/mega_sweep_summary.json"


def nn_recovery(static, X, rng):
    params = static[[f"param_{p}" for p in PARAM_NAMES]].to_numpy(float)
    spans = np.quantile(params, 0.95, axis=0) - np.quantile(params, 0.05, axis=0)
    query_idx = rng.choice(len(static), size=NN_QUERIES, replace=False)
    nn = NearestNeighbors(n_neighbors=7).fit(X)
    dist, idx = nn.kneighbors(X[query_idx])
    rows = []
    for qi, plant in enumerate(query_idx):
        neigh = [j for j in idx[qi] if j != plant][:5]
        ds = [dist[qi][list(idx[qi]).index(j)] for j in neigh]
        for rank, (j, dd) in enumerate(zip(neigh, ds), start=1):
            rel = np.abs(params[plant] - params[j]) / spans
            row = {"plant_id": int(plant), "neighbour_id": int(j),
                   "rank": rank, "behaviour_distance": float(dd),
                   "mean_rel_param_error": float(rel.mean()),
                   "max_rel_param_error": float(rel.max())}
            for p, val in zip(PARAM_NAMES, rel):
                row[f"rel_err_{p}"] = float(val)
            rows.append(row)
    return pd.DataFrame(rows)


def twin_search(times, thetas, pop, rng):
    curves = thetas.T.astype(np.float32)
    params = pop[list(PARAM_NAMES)].to_numpy(float)
    spans = params.max(axis=0) - params.min(axis=0)
    query_idx = rng.choice(len(pop), size=TWIN_QUERIES, replace=False)
    norms = np.sum(curves * curves, axis=1)
    best_j = np.empty(len(query_idx), dtype=int)
    best_d2 = np.empty(len(query_idx), dtype=float)
    chunk = 50
    for start in range(0, len(query_idx), chunk):
        qidx = query_idx[start:start + chunk]
        q = curves[qidx]
        d2 = norms[None, :] + np.sum(q * q, axis=1)[:, None] - 2.0 * (q @ curves.T)
        for r, plant in enumerate(qidx):
            d2[r, plant] = np.inf
        j = np.argmin(d2, axis=1)
        best_j[start:start + len(qidx)] = j
        best_d2[start:start + len(qidx)] = d2[np.arange(len(qidx)), j]
        if start % 1000 == 0:
            print("  twin search %d/%d" % (start, len(query_idx)), flush=True)
    rows = []
    final = thetas[-1]
    for plant, j, d2 in zip(query_idx, best_j, best_d2):
        rel = np.abs(params[plant] - params[j]) / spans
        row = {"plant_id": int(plant), "twin_id": int(j),
               "trajectory_rmse_deg": float(np.sqrt(max(d2, 0.0) / curves.shape[1])),
               "mean_rel_param_diff": float(rel.mean()),
               "max_rel_param_diff": float(rel.max()),
               "plant_final_angle": float(final[plant]),
               "twin_final_angle": float(final[j])}
        for p, a, b, rr in zip(PARAM_NAMES, params[plant], params[j], rel):
            row[f"{p}_plant"] = float(a)
            row[f"{p}_twin"] = float(b)
            row[f"rel_diff_{p}"] = float(rr)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("trajectory_rmse_deg")


def main():
    os.makedirs("results/figures", exist_ok=True)
    t0 = time.time()
    rng = np.random.default_rng(SEED + 777)

    pop_vals = uniform_population(N, seed=SEED)
    pop = pd.DataFrame(pop_vals, columns=PARAM_NAMES)
    pop.insert(0, "plant_id", np.arange(N))
    print("mega population n=%d seed=%d" % (N, SEED), flush=True)

    labels_by_regime = {}
    static = None
    static_times = static_thetas = None

    for i, (regime, fn) in enumerate(B.REGIMES.items()):
        print("regime %s ..." % regime, flush=True)
        if fn is None:
            times, thetas = batch_simulate_static(
                pop["k"], pop["tau"], pop["max_rate"], pop["phi0"],
                B.T_END, record_dt=B.RECORD_DT)
        else:
            times, thetas = batch_simulate(
                pop["k"], pop["tau"], pop["max_rate"], pop["phi0"],
                fn, B.T_END, record_dt=B.RECORD_DT)
        feat = feature_frame(times, thetas, pop, regime)
        feat.insert(0, "plant_id", np.arange(N))
        labels, _, _ = B.cluster_labels(feat, seed_offset=i)
        labels_by_regime[regime] = labels
        if regime == "static":
            static = feat
            static_times = times
            static_thetas = thetas.astype(np.float32)
            del thetas
        print("  done (%.1fs)" % (time.time() - t0), flush=True)

    static_labels = labels_by_regime["static"]
    clus = B.cluster_summary(static, static_labels)
    clus.to_csv(OUT_CLUSTERS, index=False)
    proto = pd.DataFrame([{
        "regime": regime,
        "ari_vs_static": float(adjusted_rand_score(static_labels, labels)),
    } for regime, labels in labels_by_regime.items()])
    proto.to_csv(OUT_PROTOCOLS, index=False)
    print("cluster summaries done (%.1fs)" % (time.time() - t0), flush=True)

    X = StandardScaler().fit_transform(static[list(F.STATIC_FEATURES)].to_numpy(float))
    nn = nn_recovery(static, X, rng)
    nn.to_csv(OUT_NN, index=False)
    print("nearest-neighbour recovery done (%.1fs)" % (time.time() - t0), flush=True)

    twins = twin_search(static_times, static_thetas, pop, rng)
    twins.to_csv(OUT_TWINS, index=False)
    print("twin search done (%.1fs)" % (time.time() - t0), flush=True)

    candidates = twins[(twins.trajectory_rmse_deg < 0.5)
                       & (twins.mean_rel_param_diff > 0.20)
                       & (twins.plant_final_angle > 20)
                       & (twins.twin_final_angle > 20)]
    if len(candidates) < 3:
        candidates = twins[(twins.plant_final_angle > 20)].nsmallest(20, "trajectory_rmse_deg")
    examples = [(int(r.plant_id), int(r.twin_id), float(r.trajectory_rmse_deg))
                for r in candidates.head(3).itertuples()]

    B.OUT_FIG = "results/figures/mega_sweep_dashboard.png"
    B.make_dashboard(static, static_labels, clus, proto, nn, twins,
                     static_times, static_thetas, examples)

    rank1 = nn[nn["rank"] == 1]
    summary = {
        "n_plants": N,
        "seed": SEED,
        "runtime_seconds": round(time.time() - t0, 1),
        "ari_vs_static": {r.regime: float(r.ari_vs_static) for r in proto.itertuples()},
        "median_within_cluster_iqr_frac_of_range": {
            p: float(clus[f"{p}_iqr_frac_of_range"].median()) for p in PARAM_NAMES},
        "nearest_neighbour_rank1_median_rel_error": {
            p: float(rank1[f"rel_err_{p}"].median()) for p in PARAM_NAMES},
        "twin_queries": int(len(twins)),
        "twin_median_rmse_deg": float(twins.trajectory_rmse_deg.median()),
        "twin_p95_rmse_deg": float(twins.trajectory_rmse_deg.quantile(0.95)),
        "nontrivial_twins_rmse_below_1deg_and_mean_param_diff_above_025": int(
            ((twins.plant_final_angle > 20) & (twins.twin_final_angle > 20)
             & (twins.trajectory_rmse_deg < 1.0)
             & (twins.mean_rel_param_diff > 0.25)).sum()),
        "dashboard_examples": [
            {"plant_id": p, "twin_id": t, "trajectory_rmse_deg": r}
            for p, t, r in examples],
    }
    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    print("\n=== MEGA SWEEP SUMMARY ===")
    print(json.dumps(summary, indent=2), flush=True)
    print("saved results/figures/mega_sweep_dashboard.png", flush=True)


if __name__ == "__main__":
    main()
