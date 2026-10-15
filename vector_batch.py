"""Batch follow-up to the vector-stimulus comparison.

Three analyses:
  1. Robustness of the moving-sun stimulus effect to the transduction
     exponent alpha, stem transmission T, and diffuse-sky strength.
  2. A model-discrimination map for two-source illumination: where do the
     physical, transduced-source and circumference models predict visibly
     different effective directions?
  3. Population stability under moving sun: do behaviour clusters obtained
     with the current sun-only stimulus survive replacement by the
     circumference vector stimulus?

All runs use the empirically weighted population derived from the 44 clean
measured-data fits. The dynamic update is unchanged from BendLab.
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
from generate_plants import PARAM_NAMES, weighted_population
from sweep import feature_frame
from vector_stimulus import (DT, MODELS, _circ_vector, circumference_stimulus,
                             physical_stimulus, simulate_population,
                             simulate_with_stimulus, stimulus,
                             transduced_source_stimulus)

SEED = 20261014
BASE_ALPHA = 0.30
BASE_T = 0.10
BASE_DIFFUSE = 0.12
N_SENS = 10_000
N_STAB = 20_000

OUT_SENS = "results/vector_batch_sensitivity.csv"
OUT_DISC = "results/vector_batch_discrimination.csv"
OUT_TOP = "results/vector_batch_top_conditions.csv"
OUT_STAB = "results/vector_batch_stability.json"
OUT_FIG = "results/figures/vector_batch_dashboard.png"


def load_weighted_population(n):
    fits = pd.read_csv("results/fit_fig1c.csv")
    clean = fits[fits["at_bound"] == "[]"].copy()
    return weighted_population(n, seed=SEED, fit_frame=clean), clean


def moving_series(alpha=BASE_ALPHA, transmission=BASE_T,
                  diffuse=BASE_DIFFUSE, duration=24.0):
    n = int(round(duration / DT))
    times = np.arange(n + 1) * DT
    diffuse_angles = [-60, -30, 0, 30, 60]
    psi = np.linspace(-np.pi, np.pi, 361, endpoint=False)
    psi_unit = np.stack([np.sin(psi), np.cos(psi)], axis=1)
    raw = {m: ([], []) for m in list(MODELS) + ["current_sun_only"]}

    def circ(sources):
        total = sum(i for _, i in sources)
        if total <= 0:
            return 0.0, 0.0
        vec = _circ_vector(sources, alpha, transmission, psi, psi_unit)
        ref_vec = _circ_vector([(0.0, total)], alpha, transmission, psi, psi_unit)
        ref = float(np.linalg.norm(ref_vec)) or 1.0
        return (float(np.rad2deg(np.arctan2(vec[0], vec[1]))),
                float(np.linalg.norm(vec) / ref))

    for t in times:
        if 0 <= t < 12:
            sun_phi = -60 + 120 * (t / 12)
            sun_i = float(np.sin(np.pi * t / 12)) ** 0.7
            sources = [(sun_phi, sun_i)] + [(a, diffuse) for a in diffuse_angles]
        else:
            sources = []
        for model in MODELS:
            if model == "circumference":
                phi, g = circ(sources)
            elif model == "transduced_source":
                phi, g = transduced_source_stimulus(sources, alpha=alpha)
            else:
                phi, g = physical_stimulus(sources)
            raw[model][0].append(phi)
            raw[model][1].append(g)
        raw["current_sun_only"][0].append(
            -60 + 120 * (t / 12) if 0 <= t < 12 else 0.0)
        raw["current_sun_only"][1].append(1.0 if 0 <= t < 12 else 0.0)

    return times, {m: (np.array(v[0]), np.array(v[1])) for m, v in raw.items()}


def population_metrics(pop, series):
    out = {}
    trajectories = {}
    for model, (phi_s, g) in series.items():
        _, th = simulate_population(pop, phi_s, g)
        trajectories[model] = th
    ref = trajectories["current_sun_only"]
    for model in MODELS:
        th = trajectories[model]
        final_diff = th[-1] - ref[-1]
        traj_rmse = np.sqrt(np.mean((th - ref) ** 2, axis=0))
        out[model] = {
            "final_diff_median_deg": float(np.median(final_diff)),
            "final_diff_p95_abs_deg": float(np.quantile(np.abs(final_diff), 0.95)),
            "traj_rmse_median_deg": float(np.median(traj_rmse)),
            "traj_rmse_p95_deg": float(np.quantile(traj_rmse, 0.95)),
        }
    return out, trajectories


def sensitivity(pop):
    rows = []
    for alpha in [0.15, 0.30, 0.50]:
        for transmission in [0.0, 0.10, 0.25]:
            for diffuse in [0.0, 0.12, 0.30]:
                _, series = moving_series(alpha, transmission, diffuse)
                metrics, _ = population_metrics(pop, series)
                for model, m in metrics.items():
                    rows.append({"alpha": alpha, "transmission": transmission,
                                 "diffuse_per_source": diffuse, "model": model,
                                 **m})
                print("sensitivity alpha=%.2f T=%.2f diffuse=%.2f done"
                      % (alpha, transmission, diffuse), flush=True)
    return pd.DataFrame(rows)


def discrimination():
    rows = []
    rep = {"k": 16.579, "tau": 3.616, "max_rate": 31.145, "phi0": 45.006}
    for sep in range(0, 181, 10):
        for ratio in [1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 7, 10, 15, 20]:
            sources = [(-sep / 2, 1.0), (sep / 2, float(ratio))]
            dirs = {}
            gains = {}
            for model in MODELS:
                dirs[model], gains[model] = stimulus(sources, model)
            vals = np.array([dirs[m] for m in MODELS])
            rows.append({
                "separation_deg": sep, "intensity_ratio": ratio,
                **{f"direction_{m}": dirs[m] for m in MODELS},
                **{f"gain_{m}": gains[m] for m in MODELS},
                "max_pairwise_direction_diff_deg": float(vals.max() - vals.min()),
                "circumference_minus_physical_deg": float(
                    dirs["circumference"] - dirs["physical"]),
                "transduced_minus_physical_deg": float(
                    dirs["transduced_source"] - dirs["physical"]),
            })
    grid = pd.DataFrame(rows)
    top = grid.sort_values("max_pairwise_direction_diff_deg",
                           ascending=False).head(12).copy()
    finals = []
    for _, r in top.iterrows():
        sources = [(-r.separation_deg / 2, 1.0),
                   (r.separation_deg / 2, float(r.intensity_ratio))]
        rec = {"separation_deg": r.separation_deg,
               "intensity_ratio": r.intensity_ratio,
               "max_pairwise_direction_diff_deg":
                   r.max_pairwise_direction_diff_deg}
        for model in MODELS:
            phi, g = stimulus(sources, model)
            n = int(round(24 / DT))
            _, th, _ = simulate_with_stimulus(
                rep, np.full(n + 1, phi), np.full(n + 1, g))
            rec[f"final_{model}"] = float(th[-1])
        finals.append(rec)
    return grid, pd.DataFrame(finals)


def stability(pop, trajectories):
    pop_df = pd.DataFrame(pop, columns=PARAM_NAMES)
    pop_df.insert(0, "plant_id", np.arange(len(pop)))
    feats = {}
    labels = {}
    times = np.arange(trajectories["current_sun_only"].shape[0]) * 0.5
    for name in ["current_sun_only", "circumference"]:
        feat = feature_frame(times, trajectories[name], pop_df, name)
        feats[name] = feat
        X = StandardScaler().fit_transform(feat[list(F.STATIC_FEATURES)].to_numpy())
        labels[name] = KMeans(n_clusters=6, n_init=5,
                              random_state=SEED).fit_predict(X)
    ari = float(adjusted_rand_score(labels["current_sun_only"],
                                    labels["circumference"]))
    final_diff = (trajectories["circumference"][-1]
                  - trajectories["current_sun_only"][-1])
    return {
        "n_plants": int(len(pop)),
        "cluster_ari_sun_only_vs_circumference": ari,
        "final_diff_median_deg": float(np.median(final_diff)),
        "final_diff_p95_abs_deg": float(np.quantile(np.abs(final_diff), 0.95)),
        "cluster_sizes_sun_only": {
            str(int(c)): int((labels["current_sun_only"] == c).sum())
            for c in range(6)},
        "cluster_sizes_circumference": {
            str(int(c)): int((labels["circumference"] == c).sum())
            for c in range(6)},
    }


def make_dashboard(sens, disc, stab, base_traj):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle("BendLab vector-stimulus batch: robustness and discrimination",
                 fontsize=14)

    a = axes[0, 0]
    sub = sens[(sens.model == "circumference") & (sens.transmission == BASE_T)]
    for alpha, grp in sub.groupby("alpha"):
        a.plot(grp.diffuse_per_source, grp.traj_rmse_median_deg, "o-",
               label=f"alpha={alpha:.2f}")
    a.set_xlabel("diffuse intensity per sky source")
    a.set_ylabel("median trajectory RMSE vs sun-only (deg)")
    a.set_title("Circumference model: diffuse-sky sensitivity (T=0.10)")
    a.legend(fontsize=8)

    a = axes[0, 1]
    sub = sens[(sens.model == "circumference") & (sens.diffuse_per_source == BASE_DIFFUSE)]
    for alpha, grp in sub.groupby("alpha"):
        a.plot(grp.transmission, grp.final_diff_p95_abs_deg, "o-",
               label=f"alpha={alpha:.2f}")
    a.set_xlabel("stem transmission T")
    a.set_ylabel("95th-percentile final-angle difference (deg)")
    a.set_title("Circumference model: transmission sensitivity")
    a.legend(fontsize=8)

    a = axes[1, 0]
    piv = disc.pivot(index="intensity_ratio", columns="separation_deg",
                     values="max_pairwise_direction_diff_deg")
    vmax = float(piv.values.max())
    im = a.imshow(piv.values, origin="lower", aspect="auto", cmap="magma",
                  vmin=0, vmax=vmax)
    a.set_xticks(range(len(piv.columns)), [str(c) for c in piv.columns], fontsize=7)
    a.set_yticks(range(len(piv.index)), [str(i) for i in piv.index], fontsize=7)
    a.set_xlabel("source separation (deg)")
    a.set_ylabel("intensity ratio")
    a.set_title("Where do stimulus models disagree most?")
    fig.colorbar(im, ax=a, label="max direction difference (deg)")

    a = axes[1, 1]
    diff = base_traj["circumference"][-1] - base_traj["current_sun_only"][-1]
    a.hist(diff, bins=45, color="#3f6fb5", alpha=0.85)
    a.axvline(0, color="black", lw=1)
    a.set_xlabel("final angle: circumference minus sun-only (deg)")
    a.set_ylabel("plants")
    a.set_title("Moving-sun cluster stability: ARI = %.3f (n=%s)"
                % (stab["cluster_ari_sun_only_vs_circumference"],
                   f"{stab['n_plants']:,}"))

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT_FIG, dpi=170)
    plt.close(fig)


def main():
    os.makedirs("results/figures", exist_ok=True)
    t0 = time.time()

    pop_sens, _ = load_weighted_population(N_SENS)
    sens = sensitivity(pop_sens)
    sens.to_csv(OUT_SENS, index=False)
    print("sensitivity done (%.1fs)" % (time.time() - t0), flush=True)

    disc, top = discrimination()
    disc.to_csv(OUT_DISC, index=False)
    top.to_csv(OUT_TOP, index=False)
    print("discrimination done (%.1fs)" % (time.time() - t0), flush=True)

    pop_stab, _ = load_weighted_population(N_STAB)
    _, base_series = moving_series()
    _, base_traj = population_metrics(pop_stab, base_series)
    # population_metrics returns metrics first; recompute trajectories directly
    trajectories = {}
    for model, (phi_s, g) in base_series.items():
        _, th = simulate_population(pop_stab, phi_s, g)
        trajectories[model] = th
    stab = stability(pop_stab, trajectories)
    stab["runtime_seconds"] = round(time.time() - t0, 1)
    with open(OUT_STAB, "w", encoding="utf-8") as fh:
        json.dump(stab, fh, indent=2)

    make_dashboard(sens, disc, stab, trajectories)

    base = sens[(sens.alpha == BASE_ALPHA) & (sens.transmission == BASE_T)
                & (sens.diffuse_per_source == BASE_DIFFUSE)]
    print("\n=== VECTOR BATCH SUMMARY ===")
    print(base.round(3).to_string(index=False))
    print("\nstability:", json.dumps(stab, indent=2))
    print("\ntop discriminating conditions:")
    print(top.round(2).to_string(index=False))
    print("\nsaved %s" % OUT_FIG)


if __name__ == "__main__":
    main()
