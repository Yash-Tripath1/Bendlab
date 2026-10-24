"""Grand vector-stimulus atlas.

A longer background run that expands the first vector-stimulus comparison:

  * 100,000 empirically weighted plants;
  * moving-sun sensitivity over transduction exponent alpha, stem
    transmission T, and diffuse-sky strength;
  * behaviour-cluster agreement between stimulus models;
  * exact trajectory-twin searches under the sun-only and circumference
    stimulus models;
  * population dynamics for the most model-discriminating two-source
    conditions found by vector_batch.py.

Progress is written incrementally to results/vector_atlas_sensitivity.csv so
partial results survive if the run is stopped.
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
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler

import features as F
from generate_plants import PARAM_NAMES
from sweep import feature_frame
from vector_batch import load_weighted_population, moving_series
from vector_stimulus import MODELS, simulate_population, stimulus

SEED = 20261014
N = 100_000
BASE = {"alpha": 0.30, "transmission": 0.10, "diffuse": 0.12}
TWIN_QUERIES = 8_000

OUT_SENS = "results/vector_atlas_sensitivity.csv"
OUT_CLUSTER = "results/vector_atlas_clusters.csv"
OUT_TWINS = "results/vector_atlas_twins.csv"
OUT_TOPPOP = "results/vector_atlas_top_population.csv"
OUT_SUMMARY = "results/vector_atlas_summary.json"
OUT_FIG = "results/figures/vector_atlas_dashboard.png"


def traj_metrics(th, ref):
    final_diff = th[-1] - ref[-1]
    rmse = np.sqrt(np.mean((th - ref) ** 2, axis=0))
    return {
        "final_diff_median_deg": float(np.median(final_diff)),
        "final_diff_p95_abs_deg": float(np.quantile(np.abs(final_diff), 0.95)),
        "traj_rmse_median_deg": float(np.median(rmse)),
        "traj_rmse_p95_deg": float(np.quantile(rmse, 0.95)),
    }


def twin_search(times, th, pop, model_name, rng):
    curves = th.T.astype(np.float32)
    params = pop.astype(float)
    spans = params.max(axis=0) - params.min(axis=0)
    query_idx = rng.choice(len(pop), size=min(TWIN_QUERIES, len(pop)),
                           replace=False)
    norms = np.sum(curves * curves, axis=1)
    best_j = np.empty(len(query_idx), dtype=int)
    best_d2 = np.empty(len(query_idx), dtype=float)
    chunk = 100
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
            print("  twin search %s: %d/%d" % (model_name, start,
                                               len(query_idx)), flush=True)
    rows = []
    for plant, j, d2 in zip(query_idx, best_j, best_d2):
        rmse = float(np.sqrt(max(d2, 0.0) / curves.shape[1]))
        rel = np.abs(params[plant] - params[j]) / spans
        row = {"model": model_name, "plant_id": int(plant), "twin_id": int(j),
               "trajectory_rmse_deg": rmse,
               "mean_rel_param_diff": float(rel.mean()),
               "max_rel_param_diff": float(rel.max())}
        for p, val in zip(PARAM_NAMES, rel):
            row[f"rel_diff_{p}"] = float(val)
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    os.makedirs("results/figures", exist_ok=True)
    t0 = time.time()
    rng = np.random.default_rng(SEED + 4242)

    pop, clean = load_weighted_population(N)
    print("weighted population n=%d from %d clean fits" % (N, len(clean)),
          flush=True)
    pop_df = pd.DataFrame(pop, columns=PARAM_NAMES)
    pop_df.insert(0, "plant_id", np.arange(N))

    # Reference: current sun-only stimulus.
    _, null_series = moving_series()
    _, ref_traj = simulate_population(pop, *null_series["current_sun_only"])
    print("reference sun-only simulation done (%.1fs)" % (time.time() - t0),
          flush=True)

    base_traj = {"current_sun_only": ref_traj}
    sens_rows = []

    # Sensitivity: circumference model over alpha x T x diffuse.
    with open(OUT_SENS, "w", encoding="utf-8") as fh:
        fh.write("alpha,transmission,diffuse_per_source,model,"
                 "final_diff_median_deg,final_diff_p95_abs_deg,"
                 "traj_rmse_median_deg,traj_rmse_p95_deg\n")
        for alpha in [0.15, 0.30, 0.50]:
            for transmission in [0.0, 0.10, 0.25]:
                for diffuse in [0.0, 0.06, 0.12, 0.20, 0.30]:
                    _, series = moving_series(alpha, transmission, diffuse)
                    _, th = simulate_population(pop, *series["circumference"])
                    m = traj_metrics(th, ref_traj)
                    row = {"alpha": alpha, "transmission": transmission,
                           "diffuse_per_source": diffuse,
                           "model": "circumference", **m}
                    sens_rows.append(row)
                    fh.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                        alpha, transmission, diffuse, "circumference",
                        m["final_diff_median_deg"], m["final_diff_p95_abs_deg"],
                        m["traj_rmse_median_deg"], m["traj_rmse_p95_deg"]))
                    fh.flush()
                    if (alpha == BASE["alpha"] and transmission == BASE["transmission"]
                            and diffuse == BASE["diffuse"]):
                        base_traj["circumference"] = th
                    print("circumference a=%.2f T=%.2f d=%.2f rmse=%.2f (%.1fs)"
                          % (alpha, transmission, diffuse,
                             m["traj_rmse_median_deg"], time.time() - t0),
                          flush=True)

        # Physical and transduced models at the base alpha/T across diffuse.
        for diffuse in [0.0, 0.06, 0.12, 0.20, 0.30]:
            _, series = moving_series(BASE["alpha"], BASE["transmission"], diffuse)
            for model in ["physical", "transduced_source"]:
                _, th = simulate_population(pop, *series[model])
                m = traj_metrics(th, ref_traj)
                row = {"alpha": BASE["alpha"], "transmission": BASE["transmission"],
                       "diffuse_per_source": diffuse, "model": model, **m}
                sens_rows.append(row)
                fh.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                    BASE["alpha"], BASE["transmission"], diffuse, model,
                    m["final_diff_median_deg"], m["final_diff_p95_abs_deg"],
                    m["traj_rmse_median_deg"], m["traj_rmse_p95_deg"]))
                fh.flush()
                if diffuse == BASE["diffuse"]:
                    base_traj[model] = th
            print("physical/transduced diffuse=%.2f done (%.1fs)"
                  % (diffuse, time.time() - t0), flush=True)

    sens = pd.DataFrame(sens_rows)
    times = np.arange(ref_traj.shape[0]) * 0.5

    # Cluster agreement at the base condition.
    cluster_rows = []
    labels = {}
    for model in ["current_sun_only", "physical", "transduced_source",
                  "circumference"]:
        feat = feature_frame(times, base_traj[model], pop_df, model)
        X = StandardScaler().fit_transform(feat[list(F.STATIC_FEATURES)].to_numpy())
        labels[model] = KMeans(n_clusters=6, n_init=5,
                               random_state=SEED).fit_predict(X)
        print("clusters: %s done (%.1fs)" % (model, time.time() - t0), flush=True)
    for model in labels:
        cluster_rows.append({
            "model": model,
            "ari_vs_sun_only": float(adjusted_rand_score(
                labels["current_sun_only"], labels[model])),
        })
    clusters = pd.DataFrame(cluster_rows)
    clusters.to_csv(OUT_CLUSTER, index=False)

    # Exact twin searches in recorded trajectory space.
    twin_frames = []
    for model in ["current_sun_only", "circumference"]:
        twin_frames.append(twin_search(times, base_traj[model], pop, model, rng))
        print("twin search %s done (%.1fs)" % (model, time.time() - t0),
              flush=True)
    twins = pd.concat(twin_frames, ignore_index=True)
    twins.to_csv(OUT_TWINS, index=False)

    # Population dynamics for the most discriminating two-source conditions.
    top_rows = []
    top_path = "results/vector_batch_top_conditions.csv"
    if os.path.exists(top_path):
        top = pd.read_csv(top_path).head(8)
        subset = pop[:15_000]
        n_steps = int(round(24 / (1 / 60)))
        for _, r in top.iterrows():
            sources = [(-r.separation_deg / 2, 1.0),
                       (r.separation_deg / 2, float(r.intensity_ratio))]
            finals = {}
            for model in MODELS:
                phi, g = stimulus(sources, model)
                _, th = simulate_population(
                    subset, np.full(n_steps + 1, phi), np.full(n_steps + 1, g))
                finals[model] = th[-1]
            top_rows.append({
                "separation_deg": float(r.separation_deg),
                "intensity_ratio": float(r.intensity_ratio),
                "direction_diff_deg": float(r.max_pairwise_direction_diff_deg),
                "final_physical_median": float(np.median(finals["physical"])),
                "final_transduced_median": float(np.median(finals["transduced_source"])),
                "final_circumference_median": float(np.median(finals["circumference"])),
                "max_final_spread_deg": float(
                    np.max([finals[m] for m in MODELS], axis=0).mean()
                    - np.min([finals[m] for m in MODELS], axis=0).mean()),
            })
            print("top condition sep=%s ratio=%s done (%.1fs)"
                  % (r.separation_deg, r.intensity_ratio, time.time() - t0),
                  flush=True)
    toppop = pd.DataFrame(top_rows)
    toppop.to_csv(OUT_TOPPOP, index=False)

    # Dashboard.
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle("BendLab grand vector-stimulus atlas (n=%s weighted plants)"
                 % f"{N:,}", fontsize=14)

    a = axes[0, 0]
    sub = sens[(sens.model == "circumference") & (sens.transmission == 0.10)]
    piv = sub.pivot(index="diffuse_per_source", columns="alpha",
                    values="traj_rmse_median_deg")
    for alpha in piv.columns:
        a.plot(piv.index, piv[alpha], "o-", label=f"alpha={alpha}")
    a.set_xlabel("diffuse intensity per sky source")
    a.set_ylabel("median trajectory RMSE vs sun-only (deg)")
    a.set_title("Diffuse sky drives the stimulus effect (T=0.10)")
    a.legend(fontsize=8)

    a = axes[0, 1]
    sub = clusters[clusters.model != "current_sun_only"]
    a.bar(sub.model, sub.ari_vs_sun_only, color=["#7f8c8d", "#4c9f70", "#3f6fb5"])
    a.axhline(0.5, color="red", ls="--", lw=1)
    a.set_ylim(0, 1)
    a.set_ylabel("ARI vs sun-only clusters")
    a.set_title("Do moving-sun behaviour clusters survive the stimulus model?")

    a = axes[1, 0]
    for model, grp in twins.groupby("model"):
        a.scatter(grp.trajectory_rmse_deg, grp.mean_rel_param_diff,
                  s=5, alpha=0.35, label=model)
    a.set_xlabel("nearest-twin trajectory RMSE (deg)")
    a.set_ylabel("mean relative parameter difference")
    a.set_title("Trajectory twins under two stimulus models")
    a.legend(fontsize=8)

    a = axes[1, 1]
    if len(toppop):
        x = np.arange(len(toppop))
        labels_x = ["%d°×%s" % (s, r) for s, r in zip(
            toppop.separation_deg.astype(int), toppop.intensity_ratio)]
        a.bar(x - 0.25, toppop.final_physical_median, 0.25, label="physical")
        a.bar(x, toppop.final_transduced_median, 0.25, label="transduced")
        a.bar(x + 0.25, toppop.final_circumference_median, 0.25,
              label="circumference")
        a.set_xticks(x, labels_x, rotation=35, ha="left", fontsize=7)
    a.set_ylabel("median final angle (deg)")
    a.set_title("Most discriminating two-source conditions (population)")
    a.legend(fontsize=8)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT_FIG, dpi=170)
    plt.close(fig)

    summary = {
        "n_plants": N,
        "runtime_seconds": round(time.time() - t0, 1),
        "cluster_ari_vs_sun_only": {
            r.model: float(r.ari_vs_sun_only) for r in clusters.itertuples()},
        "twin_median_rmse_deg": {
            m: float(g.trajectory_rmse_deg.median())
            for m, g in twins.groupby("model")},
        "twin_median_mean_rel_param_diff": {
            m: float(g.mean_rel_param_diff.median())
            for m, g in twins.groupby("model")},
    }
    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print("\n=== GRAND ATLAS SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print("\nsaved %s" % OUT_FIG)


if __name__ == "__main__":
    main()
