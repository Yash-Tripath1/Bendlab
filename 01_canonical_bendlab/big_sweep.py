"""Large-scale synthetic-population degeneracy sweep.

This run scales the round-0 population experiment to 100,000 simulated
parameter vectors and adds three analyses that were not part of the earlier
10,000-plant sweep:

  1. behavioural clustering under five 24 h light regimes and cross-regime
     cluster agreement (adjusted Rand index against the static regime);
  2. nearest-neighbour parameter recovery in standardised behaviour space;
  3. direct trajectory-twin search: pairs of plants whose static-light
     trajectories are nearly identical while their parameters differ.

The simulator, parameter box and feature definitions are imported from the
existing BendLab modules. No model equations, parameter bounds or feature
definitions are changed here.
"""

from __future__ import annotations

import json
import os
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

import features as F
from generate_plants import PARAM_NAMES, uniform_population
from sim import batch_simulate, batch_simulate_static
from sweep import feature_frame

SEED = 20261014
N_PLANTS = 100_000
N_CLUSTERS = 6
T_END = 24.0
RECORD_DT = 0.5
TWIN_QUERIES = 1_500
FEATURE_NN_QUERIES = 5_000

OUT_FEATURES = "results/big_sweep_features.csv.gz"
OUT_STATIC = "results/big_sweep_static_features.csv"
OUT_CLUSTERS = "results/big_sweep_clusters.csv"
OUT_PROTOCOLS = "results/big_sweep_protocol_agreement.csv"
OUT_NN = "results/big_sweep_nearest_neighbour.csv"
OUT_TWINS = "results/big_sweep_twins.csv"
OUT_SUMMARY = "results/big_sweep_summary.json"
OUT_FIG = "results/figures/big_sweep_dashboard.png"
OUT_TRAJ = "results/big_sweep_static_trajectories.npz"


# --------------------------------------------------------------------------
# Light regimes (vectorised callables used by sim.batch_simulate)
# --------------------------------------------------------------------------

def light_static(t, p0):
    return p0


def light_flip8(t, p0):
    return p0 + (45.0 if t >= 8.0 else 0.0)


def light_sweep12(t, p0):
    return p0 + 45.0 * (2.0 * ((t % 12.0) / 12.0) - 1.0)


def light_dflip(t, p0):
    return p0 + (45.0 if 6.0 <= t < 14.0 else 0.0)


def light_ramp24(t, p0):
    return p0 - 30.0 + 60.0 * (t / 24.0)


REGIMES = {
    "static": None,  # handled by batch_simulate_static
    "flip8": light_flip8,
    "sweep12": light_sweep12,
    "dflip": light_dflip,
    "ramp24": light_ramp24,
}


def cluster_labels(feat: pd.DataFrame, seed_offset: int):
    scaler = StandardScaler()
    X = scaler.fit_transform(feat[list(F.STATIC_FEATURES)].to_numpy(float))
    labels = KMeans(n_clusters=N_CLUSTERS, n_init=5,
                    random_state=SEED + seed_offset).fit_predict(X)
    return labels, X, scaler


def cluster_summary(feat: pd.DataFrame, labels: np.ndarray) -> pd.DataFrame:
    rows = []
    full_range = {}
    full_iqr = {}
    for name in PARAM_NAMES:
        v = feat[f"param_{name}"].to_numpy(float)
        full_range[name] = float(np.max(v) - np.min(v))
        full_iqr[name] = float(np.quantile(v, 0.75) - np.quantile(v, 0.25))
    for c in range(N_CLUSTERS):
        m = labels == c
        if m.sum() < 50:
            continue
        row = {"cluster": int(c), "n": int(m.sum())}
        sub = feat.loc[m]
        for name in PARAM_NAMES:
            v = sub[f"param_{name}"].to_numpy(float)
            row[f"{name}_iqr"] = float(np.quantile(v, 0.75) - np.quantile(v, 0.25))
            row[f"{name}_range"] = float(np.max(v) - np.min(v))
            row[f"{name}_iqr_frac_of_range"] = row[f"{name}_iqr"] / full_range[name]
            row[f"{name}_iqr_frac_of_iqr"] = row[f"{name}_iqr"] / full_iqr[name]
        rows.append(row)
    return pd.DataFrame(rows)


def nearest_neighbour_recovery(static: pd.DataFrame, X: np.ndarray,
                               rng: np.random.Generator) -> pd.DataFrame:
    params = static[[f"param_{p}" for p in PARAM_NAMES]].to_numpy(float)
    spans = np.quantile(params, 0.95, axis=0) - np.quantile(params, 0.05, axis=0)
    query_idx = rng.choice(len(static), size=min(FEATURE_NN_QUERIES, len(static)),
                           replace=False)
    nn = NearestNeighbors(n_neighbors=7).fit(X)
    dist, idx = nn.kneighbors(X[query_idx])
    rows = []
    for qi, plant in enumerate(query_idx):
        neigh = [j for j in idx[qi] if j != plant][:5]
        d = [dist[qi][list(idx[qi]).index(j)] for j in neigh]
        for rank, (j, dd) in enumerate(zip(neigh, d), start=1):
            rel = np.abs(params[plant] - params[j]) / spans
            row = {"plant_id": int(plant), "neighbour_id": int(j),
                   "rank": rank, "behaviour_distance": float(dd),
                   "mean_rel_param_error": float(rel.mean()),
                   "max_rel_param_error": float(rel.max())}
            for p, val in zip(PARAM_NAMES, rel):
                row[f"rel_err_{p}"] = float(val)
            rows.append(row)
    return pd.DataFrame(rows)


def trajectory_twins(times: np.ndarray, thetas: np.ndarray,
                     pop: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Chunked exact nearest-neighbour search in raw trajectory space."""
    curves = thetas.T.astype(np.float32)  # (n_plants, n_times)
    params = pop[list(PARAM_NAMES)].to_numpy(float)
    spans = np.max(params, axis=0) - np.min(params, axis=0)
    query_idx = rng.choice(len(pop), size=min(TWIN_QUERIES, len(pop)), replace=False)
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
        print("  twin search: %d/%d queries" % (min(start + chunk, len(query_idx)),
                                                len(query_idx)), flush=True)
    rows = []
    for plant, j, d2 in zip(query_idx, best_j, best_d2):
        rmse = float(np.sqrt(max(d2, 0.0) / curves.shape[1]))
        rel = np.abs(params[plant] - params[j]) / spans
        row = {"plant_id": int(plant), "twin_id": int(j),
               "trajectory_rmse_deg": rmse,
               "mean_rel_param_diff": float(rel.mean()),
               "max_rel_param_diff": float(rel.max())}
        for p, a, b, rr in zip(PARAM_NAMES, params[plant], params[j], rel):
            row[f"{p}_plant"] = float(a)
            row[f"{p}_twin"] = float(b)
            row[f"rel_diff_{p}"] = float(rr)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("trajectory_rmse_deg")


def make_dashboard(static: pd.DataFrame, labels: np.ndarray,
                   clus: pd.DataFrame, proto: pd.DataFrame,
                   nn: pd.DataFrame, twins: pd.DataFrame,
                   times: np.ndarray, thetas: np.ndarray,
                   example_pairs: list[tuple[int, int, float]]) -> None:
    rng = np.random.default_rng(SEED + 99)
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle("BendLab large-scale degeneracy sweep (n=%s, uniform parameter box)"
                 % f"{len(static):,}", fontsize=14)

    # PCA of behaviour space, coloured by static-regime cluster.
    X = StandardScaler().fit_transform(static[list(F.STATIC_FEATURES)].to_numpy(float))
    sample = rng.choice(len(static), size=min(20_000, len(static)), replace=False)
    pcs = PCA(n_components=2, random_state=SEED).fit_transform(X[sample])
    a = axes[0, 0]
    sc = a.scatter(pcs[:, 0], pcs[:, 1], c=labels[sample], s=2, alpha=0.55,
                   cmap="tab10")
    a.set_xlabel("behaviour PC1")
    a.set_ylabel("behaviour PC2")
    a.set_title("Behaviour space (static light), coloured by cluster")
    fig.colorbar(sc, ax=a, label="cluster", ticks=range(N_CLUSTERS))

    # Parameter retention inside clusters.
    a = axes[0, 1]
    med = [100 * clus[f"{p}_iqr_frac_of_range"].median() for p in PARAM_NAMES]
    a.bar(PARAM_NAMES, med, color="tab:blue", alpha=0.85)
    a.axhline(25, color="gray", ls="--", lw=1)
    a.set_ylabel("median within-cluster IQR (% of full range)")
    a.set_title("How much parameter variety survives inside one behaviour cluster")

    # Cross-regime agreement.
    a = axes[0, 2]
    sub = proto[proto["regime"] != "static"]
    a.bar(sub["regime"], sub["ari_vs_static"], color="tab:orange", alpha=0.9)
    a.axhline(0.5, color="red", ls="--", lw=1, label="persistence threshold 0.50")
    a.set_ylim(0, 1)
    a.set_ylabel("ARI vs static clusters")
    a.set_title("Do behaviour clusters survive a change of light regime?")
    a.legend(fontsize=8)

    # Trajectory twins.
    a = axes[1, 0]
    for plant, twin, rmse in example_pairs:
        a.plot(times, thetas[:, plant], lw=1.4,
               label="plant %d" % plant)
        a.plot(times, thetas[:, twin], lw=1.4, ls="--",
               label="twin %d (%.2f°)" % (twin, rmse))
    a.set_xlabel("time (h)")
    a.set_ylabel("stem angle (deg)")
    a.set_title("Behavioural twins: near-identical curves, different parameters")
    a.legend(fontsize=7)

    # Nearest-neighbour parameter recovery.
    a = axes[1, 1]
    rank1 = nn[nn["rank"] == 1]
    med_err = [rank1[f"rel_err_{p}"].median() for p in PARAM_NAMES]
    a.bar(PARAM_NAMES, med_err, color="tab:green", alpha=0.85)
    a.set_ylabel("median relative parameter error")
    a.set_title("Parameter recovery from the nearest behavioural neighbour")

    # Twin degeneracy scatter.
    a = axes[1, 2]
    a.scatter(twins["trajectory_rmse_deg"], twins["mean_rel_param_diff"],
              s=8, alpha=0.5)
    a.axvline(1.0, color="red", ls="--", lw=1)
    a.set_xlabel("trajectory RMSE between twins (deg)")
    a.set_ylabel("mean relative parameter difference")
    a.set_title("Closest trajectory twins remain parameter-distant")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT_FIG, dpi=170)
    plt.close(fig)


def main() -> None:
    os.makedirs("results/figures", exist_ok=True)
    t0 = time.time()
    rng = np.random.default_rng(SEED + 12345)

    pop_vals = uniform_population(N_PLANTS, seed=SEED)
    pop = pd.DataFrame(pop_vals, columns=PARAM_NAMES)
    pop.insert(0, "plant_id", np.arange(N_PLANTS))
    print("population: n=%d seed=%d" % (N_PLANTS, SEED), flush=True)
    print(pop[list(PARAM_NAMES)].describe().round(3).to_string(), flush=True)

    all_features = []
    labels_by_regime = {}
    static = None
    static_times = static_thetas = None

    for i, (regime, fn) in enumerate(REGIMES.items()):
        print("simulating regime %s ..." % regime, flush=True)
        if fn is None:
            times, thetas = batch_simulate_static(
                pop["k"], pop["tau"], pop["max_rate"], pop["phi0"],
                T_END, record_dt=RECORD_DT)
        else:
            times, thetas = batch_simulate(
                pop["k"], pop["tau"], pop["max_rate"], pop["phi0"],
                fn, T_END, record_dt=RECORD_DT)
        feat = feature_frame(times, thetas, pop, regime)
        feat.insert(0, "plant_id", np.arange(N_PLANTS))
        labels, _, _ = cluster_labels(feat, seed_offset=i)
        feat["cluster"] = labels
        labels_by_regime[regime] = labels
        all_features.append(feat)
        if regime == "static":
            static = feat.copy()
            static_times, static_thetas = times, thetas
        print("  done (%.1fs elapsed)" % (time.time() - t0), flush=True)

    feat_all = pd.concat(all_features, ignore_index=True)
    feat_all.to_csv(OUT_FEATURES, index=False, compression="gzip")
    static.to_csv(OUT_STATIC, index=False)
    np.savez_compressed(OUT_TRAJ, times=static_times,
                        thetas=static_thetas.astype(np.float32))

    static_labels = labels_by_regime["static"]
    clus = cluster_summary(static, static_labels)
    clus.to_csv(OUT_CLUSTERS, index=False)

    proto_rows = []
    for regime, labels in labels_by_regime.items():
        proto_rows.append({
            "regime": regime,
            "ari_vs_static": float(adjusted_rand_score(static_labels, labels)),
        })
    proto = pd.DataFrame(proto_rows)
    proto.to_csv(OUT_PROTOCOLS, index=False)

    X_static = StandardScaler().fit_transform(
        static[list(F.STATIC_FEATURES)].to_numpy(float))
    nn = nearest_neighbour_recovery(static, X_static, rng)
    nn.to_csv(OUT_NN, index=False)

    print("searching for trajectory twins ...", flush=True)
    twins = trajectory_twins(static_times, static_thetas, pop, rng)
    twins.to_csv(OUT_TWINS, index=False)

    # Dashboard twin examples: very close curves, very different parameters,
    # restricted to non-trivial movers so that near-flat trajectories do not
    # dominate the visual examples.
    final_by_id = static.set_index("plant_id")["final_angle"]
    twins["plant_final_angle"] = twins["plant_id"].map(final_by_id)
    twins["twin_final_angle"] = twins["twin_id"].map(final_by_id)
    twins.to_csv(OUT_TWINS, index=False)
    candidates = twins[(twins["trajectory_rmse_deg"] < 0.5)
                       & (twins["mean_rel_param_diff"] > 0.20)
                       & (twins["plant_final_angle"] > 20.0)
                       & (twins["twin_final_angle"] > 20.0)]
    if len(candidates) < 3:
        candidates = twins[(twins["plant_final_angle"] > 20.0)
                           & (twins["twin_final_angle"] > 20.0)].nsmallest(
                               20, "trajectory_rmse_deg")
    examples = [(int(r.plant_id), int(r.twin_id), float(r.trajectory_rmse_deg))
                for r in candidates.head(3).itertuples()]

    make_dashboard(static, static_labels, clus, proto, nn, twins,
                   static_times, static_thetas, examples)

    obs_rate = static["peak_rate"].to_numpy(float)
    cap = static["param_max_rate"].to_numpy(float)
    rank1 = nn[nn["rank"] == 1]
    summary = {
        "n_plants": N_PLANTS,
        "seed": SEED,
        "regimes": list(REGIMES.keys()),
        "runtime_seconds": round(time.time() - t0, 1),
        "static_cap_binding_fraction": float(np.mean(obs_rate >= 0.99 * cap)),
        "median_within_cluster_iqr_frac_of_range": {
            p: float(clus[f"{p}_iqr_frac_of_range"].median()) for p in PARAM_NAMES
        },
        "ari_vs_static": {r.regime: float(r.ari_vs_static)
                          for r in proto.itertuples()},
        "nearest_neighbour_rank1_median_rel_error": {
            p: float(rank1[f"rel_err_{p}"].median()) for p in PARAM_NAMES
        },
        "twins_rmse_below_1deg": int((twins["trajectory_rmse_deg"] < 1.0).sum()),
        "twins_rmse_below_1deg_and_mean_param_diff_above_025": int(
            ((twins["trajectory_rmse_deg"] < 1.0)
             & (twins["mean_rel_param_diff"] > 0.25)).sum()),
        "nontrivial_twin_queries_final_above_20deg": int(
            ((twins["plant_final_angle"] > 20.0)
             & (twins["twin_final_angle"] > 20.0)).sum()),
        "nontrivial_twins_rmse_below_1deg": int(
            ((twins["plant_final_angle"] > 20.0)
             & (twins["twin_final_angle"] > 20.0)
             & (twins["trajectory_rmse_deg"] < 1.0)).sum()),
        "nontrivial_twins_rmse_below_1deg_and_mean_param_diff_above_025": int(
            ((twins["plant_final_angle"] > 20.0)
             & (twins["twin_final_angle"] > 20.0)
             & (twins["trajectory_rmse_deg"] < 1.0)
             & (twins["mean_rel_param_diff"] > 0.25)).sum()),
        "twin_queries": int(len(twins)),
        "dashboard_examples": [
            {"plant_id": p, "twin_id": t, "trajectory_rmse_deg": r}
            for p, t, r in examples
        ],
    }
    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print("\n=== BIG SWEEP SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print("\nsaved %s" % OUT_FIG)
    print("saved %s, %s, %s, %s, %s, %s" % (
        OUT_FEATURES, OUT_CLUSTERS, OUT_PROTOCOLS, OUT_NN, OUT_TWINS,
        OUT_SUMMARY))


if __name__ == "__main__":
    main()
