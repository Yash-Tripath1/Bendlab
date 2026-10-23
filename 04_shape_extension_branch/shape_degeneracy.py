"""Pre-registered shape-extension degeneracy study (H-SHAPE).

One population of multi-segment plants is simulated under static light and
clustered twice: once on tip-only behaviour (the six features.STATIC_FEATURES
of the tip angle, exactly the H1 feature set) and once on tip plus shape
behaviour (those six plus features_shape.SHAPE_FEATURES). Both arms use the
clustering criterion of sweep.py unchanged: StandardScaler, KMeans(6,
n_init=10, random_state=1), clusters under 50 plants skipped. Degeneracy is
measured with the series-1 retention metric: median within-cluster IQR
divided by the full population range, per parameter.

H-SHAPE (pre-registered, see docs/SHAPE_EXTENSION.md): the shape arm
reduces median within-cluster IQR retention by at least 10 percentage
points relative to the tip-only arm, for at least two of the five
parameters (k, tau, max_rate, phi0, c). Falsification: fewer than two
parameters show a reduction of at least 10 percentage points.

Population construction, declared in advance:
  - the four sim.py parameters are drawn with generate_plants.uniform_population
    at SEED, so the population margins are exactly the H1 population of
    sweep.py and retention numbers are directly comparable;
  - c (coupling, hour^-1) is drawn independently, Uniform[0, 1], at SEED+1.

Outputs: results/shape_degeneracy_features.csv.gz, results/shape_clusters_tip.csv,
results/shape_clusters_full.csv, results/shape_retention_summary.csv,
results/shape_degeneracy_summary.json, results/figures/shape_retention.png

Run: python shape_degeneracy.py
"""

from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import features as F
import features_shape as FS
import sweep
from generate_plants import PARAM_NAMES, uniform_population
from sim_multiseg import batch_simulate_static, tip_angle

T_END = 24.0        # hours, matches the H1 sweep window
RECORD_DT = 0.5     # hours, matches the measurement cadence
N_SEG = 5           # segments in the chain (4 joints)
N_PLANTS = 10_000   # matches the H1 sweep population size
SEED = 1            # population seed (H1 margins) and clustering seed
C_SEED = SEED + 1   # independent seed for the coupling draw
C_BOUNDS = (0.0, 1.0)  # hour^-1, see docs/SHAPE_EXTENSION.md

ALL_PARAMS = PARAM_NAMES + ("c",)
TIP_COLS = list(F.STATIC_FEATURES)
SHAPE_COLS = TIP_COLS + list(FS.SHAPE_FEATURES)

# Guard: a behaviour feature and a parameter must never share a name
# (round-0 bug, see docs/RESULTS_ROUND0.md).
assert not (set(SHAPE_COLS) & set(ALL_PARAMS)), \
    "feature/parameter name collision: %s" % (set(SHAPE_COLS) & set(ALL_PARAMS))


def degeneracy_report(feat, feat_cols, n_clusters=6):
    """Same criterion as sweep.degeneracy_report, extended to the five
    parameters of the shape model."""
    X = StandardScaler().fit_transform(feat[feat_cols].to_numpy())
    labels = KMeans(n_clusters=n_clusters, n_init=10, random_state=SEED
                    ).fit_predict(X)
    rows = []
    for c in range(n_clusters):
        m = labels == c
        if m.sum() < 50:
            continue
        row = {"cluster": c, "n": int(m.sum())}
        for name in ALL_PARAMS:
            v = feat.loc[m, f"param_{name}"]
            row[f"{name}_range"] = float(v.max() - v.min())
            row[f"{name}_iqr"] = float(v.quantile(.75) - v.quantile(.25))
        rows.append(row)
    return pd.DataFrame(rows), labels


def retention(cl, full_range):
    """Median within-cluster IQR as a percentage of the full range, per
    parameter: the series-1 retention metric."""
    out = {}
    for name in ALL_PARAMS:
        out[name] = 100.0 * float(cl[f"{name}_iqr"].median()) / full_range[name]
    return out


def main() -> None:
    # --- population: exactly the H1 margins, plus independent coupling ---
    four = uniform_population(N_PLANTS, seed=SEED)
    rng = np.random.default_rng(C_SEED)
    c = C_BOUNDS[0] + rng.random(N_PLANTS) * (C_BOUNDS[1] - C_BOUNDS[0])
    df = pd.DataFrame(four, columns=PARAM_NAMES)
    df["c"] = c
    df.insert(0, "plant_id", np.arange(N_PLANTS))

    # --- simulate: static light, each plant under its own phi0 ---
    t_s, th_s = batch_simulate_static(
        df["k"].to_numpy(), df["tau"].to_numpy(), df["max_rate"].to_numpy(),
        df["phi0"].to_numpy(), df["c"].to_numpy(),
        T_END, record_dt=RECORD_DT, n_seg=N_SEG)
    print("simulated %d plants x %d segments, T=%.1f h, record_dt=%.2f h"
          % (N_PLANTS, N_SEG, T_END, RECORD_DT))

    # --- feature table: tip arm and shape arm share one table ---
    # Tip features go through sweep.feature_frame so the definitions and
    # names are literally the H1 ones.
    feat = sweep.feature_frame(t_s, tip_angle(th_s), df, "static")
    feat["param_c"] = df["c"].to_numpy()
    shape = FS.shape_batch(t_s, th_s)
    for j, name in enumerate(FS.SHAPE_FEATURES):
        feat[name] = shape[:, j]

    full_range = {name: float(df[name].max() - df[name].min())
                  for name in ALL_PARAMS}

    # --- two clustering arms on the same plants ---
    cl_tip, lab_tip = degeneracy_report(feat, TIP_COLS)
    cl_full, lab_full = degeneracy_report(feat, SHAPE_COLS)
    ret_tip = retention(cl_tip, full_range)
    ret_full = retention(cl_full, full_range)

    print("\n=== retention: median within-cluster IQR / full range ===")
    print("%-9s %10s %10s %10s" % ("param", "tip-only", "tip+shape", "delta pp"))
    reductions = {}
    for name in ALL_PARAMS:
        delta = ret_tip[name] - ret_full[name]
        reductions[name] = delta
        print("%-9s %9.1f%% %9.1f%% %9.1f"
              % (name, ret_tip[name], ret_full[name], delta))

    print("\n=== largest cluster, tip-only arm ===")
    big = cl_tip.loc[cl_tip["n"].idxmax()]
    print("cluster %d, n=%d" % (int(big["cluster"]), int(big["n"])))
    for name in ALL_PARAMS:
        print("  %-9s range %.3f (IQR %.3f)"
              % (name, big[f"{name}_range"], big[f"{name}_iqr"]))

    print("\n=== largest cluster, tip+shape arm ===")
    big = cl_full.loc[cl_full["n"].idxmax()]
    print("cluster %d, n=%d" % (int(big["cluster"]), int(big["n"])))
    for name in ALL_PARAMS:
        print("  %-9s range %.3f (IQR %.3f)"
              % (name, big[f"{name}_range"], big[f"{name}_iqr"]))

    # --- verdict against the pre-registered criterion ---
    improved = [n for n in ALL_PARAMS if reductions[n] >= 10.0]
    supported = len(improved) >= 2
    print("\n=== H-SHAPE verdict (criterion: >=10 pp reduction for >=2 params) ===")
    print("parameters with >=10 pp reduction: %s"
          % (improved if improved else "none"))
    print("H-SHAPE %s" % ("SUPPORTED" if supported else "NOT SUPPORTED "
          "(falsified as specified)" if len(improved) < 2 else "inconclusive"))

    # --- outputs ---
    feat.to_csv("results/shape_degeneracy_features.csv.gz", index=False,
                compression="gzip")
    cl_tip.to_csv("results/shape_clusters_tip.csv", index=False)
    cl_full.to_csv("results/shape_clusters_full.csv", index=False)
    summary = pd.DataFrame({
        "param": ALL_PARAMS,
        "retention_tip_pct": [ret_tip[n] for n in ALL_PARAMS],
        "retention_shape_pct": [ret_full[n] for n in ALL_PARAMS],
        "reduction_pp": [reductions[n] for n in ALL_PARAMS],
    })
    summary.to_csv("results/shape_retention_summary.csv", index=False)
    with open("results/shape_degeneracy_summary.json", "w") as fh:
        json.dump({
            "seed": SEED, "c_seed": C_SEED, "n_plants": N_PLANTS,
            "n_seg": N_SEG, "t_end": T_END, "record_dt": RECORD_DT,
            "c_bounds": C_BOUNDS,
            "criterion": ">=10 pp retention reduction for >=2 of 5 params",
            "improved_params": improved, "supported": bool(supported),
            "retention_tip_pct": ret_tip, "retention_shape_pct": ret_full,
        }, fh, indent=2)

    # figure: retention per parameter, both arms
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        x = np.arange(len(ALL_PARAMS))
        w = 0.38
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.bar(x - w / 2, [ret_tip[n] for n in ALL_PARAMS], w,
               label="tip-only features", color="#4C72B0")
        ax.bar(x + w / 2, [ret_full[n] for n in ALL_PARAMS], w,
               label="tip + shape features", color="#DD8452")
        ax.set_xticks(x, list(ALL_PARAMS))
        ax.set_ylabel("median within-cluster IQR / full range (%)")
        ax.set_title("H-SHAPE: parameter retention inside behavioural clusters")
        ax.legend()
        fig.tight_layout()
        fig.savefig("results/figures/shape_retention.png", dpi=150)
        plt.close(fig)
        print("\nsaved results/figures/shape_retention.png")
    except Exception as exc:  # figure is supplementary; numbers are the result
        print("figure skipped: %s" % exc)

    print("saved results/shape_degeneracy_features.csv.gz, "
          "results/shape_clusters_tip.csv, results/shape_clusters_full.csv, "
          "results/shape_retention_summary.csv, "
          "results/shape_degeneracy_summary.json")


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    os.makedirs("results/figures", exist_ok=True)
    main()
