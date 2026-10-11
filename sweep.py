"""H1/H2 sweep: run a synthetic population and map its behaviour space.

Uniform population, static light and a mid-run flip, features extracted with
the fixed definitions in features.py, then two measurements:

  - how much behaviour there is (feature range, cluster structure)
  - how well behaviour predicts parameters, which is the degeneracy question

Clustering uses a criterion fixed in advance, not a number chosen to look
good. Everything is seeded from declared integers.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import features as F
from generate_plants import PARAM_NAMES, splits, uniform_population
from sim import batch_simulate, batch_simulate_static

T_END = 24.0      # hours, matches the longest Fig1C window
FLIP_T = 8.0      # hours, light flips here
FLIP_DELTA = 45.0  # degrees, flip magnitude
RECORD_DT = 0.5   # hours, matches the measurement cadence
SEED = 1


def half_rise_batch(times, thetas):
    """Vectorised half-rise time: first crossing of half each plant's peak."""
    peak = thetas.max(axis=0)
    half = peak / 2.0
    crossed = thetas >= half[None, :]
    idx = np.where(crossed.any(axis=0), crossed.argmax(axis=0), len(times))
    idx = np.minimum(idx, len(times) - 1)
    return times[idx]


def feature_frame(times, thetas, pop, regime):
    """Build the feature table for one regime."""
    peak = thetas.max(axis=0)
    final = thetas[-1]
    overshoot = peak - final
    rate = np.abs(np.diff(thetas, axis=0)).max(axis=0) / (times[1] - times[0])
    auroc = np.trapezoid(thetas, times, axis=0) / (times[-1] - times[0])
    out = pd.DataFrame({
        "half_rise_time": half_rise_batch(times, thetas),
        "peak_angle": peak,
        "final_angle": final,
        "overshoot": overshoot,
        "max_rate": rate,
        "auroc": auroc,
    })
    for name in PARAM_NAMES:
        out[name] = pop[name].to_numpy()
    out["regime"] = regime
    return out


def degeneracy_report(feat, feat_cols, n_clusters=6):
    """Cluster on features, then measure how much parameter variety sits
    inside each behavioural cluster. Wide parameters inside one cluster means
    the behaviour does not determine the parameters."""
    X = StandardScaler().fit_transform(feat[feat_cols].to_numpy())
    labels = KMeans(n_clusters=n_clusters, n_init=10, random_state=SEED
                    ).fit_predict(X)
    rows = []
    for c in range(n_clusters):
        m = labels == c
        if m.sum() < 50:
            continue
        row = {"cluster": c, "n": int(m.sum())}
        for name in PARAM_NAMES:
            v = feat.loc[m, name]
            row[f"{name}_range"] = float(v.max() - v.min())
            row[f"{name}_iqr"] = float(v.quantile(.75) - v.quantile(.25))
        rows.append(row)
    return pd.DataFrame(rows), labels


def main() -> None:
    n = 10_000
    pop = uniform_population(n, seed=SEED)
    df = population_frame_with_id(pop)

    # Static light, each plant under its own phi0.
    t_s, th_s = batch_simulate_static(df["k"], df["tau"], df["max_rate"],
                                      df["phi0"], T_END, record_dt=RECORD_DT)
    static = feature_frame(t_s, th_s, df, "static")

    # Flip: same plants, light steps by FLIP_DELTA at FLIP_T. One continuous
    # integration with a time-dependent light function, so the rate state r
    # carries across the flip instead of being reset.
    def flip_light(t, phi0, flip_t=FLIP_T, delta=FLIP_DELTA):
        return phi0 + (delta if t >= flip_t else 0.0)

    t_f, th_f = batch_simulate(df["k"], df["tau"], df["max_rate"], df["phi0"],
                               flip_light, T_END, record_dt=RECORD_DT)
    flip = feature_frame(t_f, th_f, df, "flip")
    flip["reversal"] = th_f.max(axis=0) - th_f[-1]
    print("flip sanity: mean angle drop in the 2h after the flip = %.2f deg"
          % np.mean(th_f[-1] - th_f[int(FLIP_T / RECORD_DT)]))

    feat_cols = list(F.STATIC_FEATURES)
    cl, _ = degeneracy_report(static, feat_cols)
    print("\n=== behaviour-space clusters, static light, n=%d ===" % n)
    print(cl.round(2).to_string(index=False))

    print("\n=== degeneracy read-out ===")
    for name in PARAM_NAMES:
        col = f"{name}_iqr"
        print("%-9s median within-cluster IQR %.3f | full-range %.3f "
              "| cluster retains %.0f%% of the range"
              % (name, cl[col].median(), float(df[name].max() - df[name].min()),
                 100 * cl[col].median() / (df[name].max() - df[name].min())))

    print("\n=== parameter spread inside the largest cluster ===")
    big = cl.loc[cl["n"].idxmax()]
    print("cluster %d, n=%d" % (int(big["cluster"]), int(big["n"])))
    for name in PARAM_NAMES:
        print("  %-9s range %.3f (IQR %.3f)"
              % (name, big[f"{name}_range"], big[f"{name}_iqr"]))

    cl_f, _ = degeneracy_report(flip, feat_cols + ["reversal"])
    print("\n=== H2 probe: flip-regime clusters (static features + reversal) ===")
    print(cl_f.round(2).to_string(index=False))

    pd.concat([static, flip], ignore_index=True).to_csv(
        "results/sweep_features.csv.gz", index=False, compression="gzip")
    cl.to_csv("results/sweep_clusters_static.csv", index=False)
    cl_f.to_csv("results/sweep_clusters_flip.csv", index=False)
    print("\nsaved results/sweep_features.csv.gz, "
          "results/sweep_clusters_static.csv, results/sweep_clusters_flip.csv")


def population_frame_with_id(pop):
    df = pd.DataFrame(pop, columns=PARAM_NAMES)
    df.insert(0, "plant_id", np.arange(len(df)))
    return df


if __name__ == "__main__":
    import os
    os.makedirs("results", exist_ok=True)
    main()
