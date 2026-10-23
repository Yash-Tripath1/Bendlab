"""Pre-registered twin-refinement identification study (v3).

The original shape method, confirmed on a fresh population: among a
plant's behavioural twins in tip-angle space, identify the plant by
shape. Pre-registration is docs/SHAPE_EXTENSION_RESULTS.md section 8
(written before this run); the protocol and threshold were informed by
the section-7 exploratory probe, and the fresh population (new seeds) is
the guard against over-fitting to that exploration.

Population: n = 10,000, four-parameter uniform box at seed 101,
c ~ Uniform[0, 1] (seed 102), zeta ~ Uniform[0, 1] (seed 103).
Protocol unchanged: static light, 24 h, 0.5 h records, n_seg = 5,
zeta-gradient model (sim_multiseg).

Primary protocol: standardise tip features (6) and shape features (8)
separately; for each plant take its 20 nearest neighbours in tip space;
refine to the one nearest in shape space. Error per parameter = median
|parameter difference| / full population range.

Hypothesis (v3): refinement reduces that error by >= 25 per cent
relative to the plain tip nearest neighbour for >= 2 of the four
original parameters (k, tau, max_rate, phi0). Falsification: fewer than
two. Secondary outputs (oracle, three-arm nearest-neighbour recovery,
ExtraTrees CV R2, extension parameters) are reported without entering
the verdict.

Outputs: results/shape_identification_v3.csv,
results/shape_identification_v3_summary.json,
results/figures/twin_refinement_v3.png

Run: python shape_identification_v3.py
"""

from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

import features as F
import features_shape as FS
import sweep
from generate_plants import PARAM_NAMES, uniform_population
from sim_multiseg import batch_simulate_static, tip_angle

T_END = 24.0
RECORD_DT = 0.5
N_SEG = 5
N_PLANTS = 10_000
SEED = 101           # fresh population: never used in the exploration
C_SEED = 102
ZETA_SEED = 103
C_BOUNDS = (0.0, 1.0)
ZETA_BOUNDS = (0.0, 1.0)
N_TWINS = 20
THRESHOLD_PCT = 25.0          # pre-registered: >= 25% error reduction
VERDICT_PARAMS = PARAM_NAMES  # k, tau, max_rate, phi0

ALL_PARAMS = PARAM_NAMES + ("c", "zeta")
TIP_COLS = list(F.STATIC_FEATURES)
SHAPE_COLS = list(FS.SHAPE_FEATURES)
ARMS = {"tip": TIP_COLS, "shape": SHAPE_COLS,
        "combined": TIP_COLS + SHAPE_COLS}


def main() -> None:
    # --- fresh population ---
    four = uniform_population(N_PLANTS, seed=SEED)
    rng_c = np.random.default_rng(C_SEED)
    c = C_BOUNDS[0] + rng_c.random(N_PLANTS) * (C_BOUNDS[1] - C_BOUNDS[0])
    rng_z = np.random.default_rng(ZETA_SEED)
    zeta = ZETA_BOUNDS[0] + rng_z.random(N_PLANTS) \
        * (ZETA_BOUNDS[1] - ZETA_BOUNDS[0])
    df = pd.DataFrame(four, columns=PARAM_NAMES)
    df["c"] = c
    df["zeta"] = zeta

    t_s, th_s = batch_simulate_static(
        df["k"].to_numpy(), df["tau"].to_numpy(), df["max_rate"].to_numpy(),
        df["phi0"].to_numpy(), df["c"].to_numpy(),
        T_END, record_dt=RECORD_DT, n_seg=N_SEG, zeta=df["zeta"].to_numpy())
    print("fresh population: %d plants, seeds %d/%d/%d (pop/c/zeta)"
          % (N_PLANTS, SEED, C_SEED, ZETA_SEED))

    feat = sweep.feature_frame(t_s, tip_angle(th_s), df, "static")
    for name in ("c", "zeta"):
        feat[f"param_{name}"] = df[name].to_numpy()
    shape = FS.shape_batch(t_s, th_s)
    for j, name in enumerate(SHAPE_COLS):
        feat[name] = shape[:, j]

    P = {name: feat[f"param_{name}"].to_numpy(float) for name in ALL_PARAMS}
    full_range = {name: float(P[name].max() - P[name].min())
                  for name in ALL_PARAMS}
    scaled = {arm: StandardScaler().fit_transform(feat[cols].to_numpy())
              for arm, cols in ARMS.items()}

    rows = []

    # --- PRIMARY: twin refinement ---
    nn_tip = NearestNeighbors(n_neighbors=N_TWINS + 1).fit(scaled["tip"])
    _, idx = nn_tip.kneighbors(scaled["tip"])
    cand = idx[:, 1:]                                  # (N, N_TWINS)
    Xs = scaled["shape"]
    d_shape = np.linalg.norm(Xs[:, None, :] - Xs[cand], axis=2)
    refined = cand[np.arange(N_PLANTS), d_shape.argmin(axis=1)]

    print("\n=== PRIMARY: twin refinement (20 tip twins -> nearest in shape) ===")
    print("%-9s %9s %9s %9s %10s" % ("param", "tip-NN", "refined",
                                     "oracle", "reduction"))
    reductions = {}
    for name in ALL_PARAMS:
        d = np.abs(P[name][cand] - P[name][:, None])    # (N, N_TWINS)
        e_twin = 100.0 * np.median(d[:, 0]) / full_range[name]
        e_ref = 100.0 * np.median(np.abs(P[name][refined] - P[name])
                                  ) / full_range[name]
        e_oracle = 100.0 * np.median(d.min(axis=1)) / full_range[name]
        red = 100.0 * (e_twin - e_ref) / e_twin if e_twin > 0 else 0.0
        reductions[name] = red
        for tag, v in (("tip_nn", e_twin), ("refined", e_ref),
                       ("oracle", e_oracle)):
            rows.append({"probe": "twin_refinement", "arm": tag,
                         "param": name, "value": v})
        rows.append({"probe": "twin_refinement", "arm": "reduction_pct",
                     "param": name, "value": red})
        print("%-9s %8.2f%% %8.2f%% %8.2f%% %9.1f%%"
              % (name, e_twin, e_ref, e_oracle, red))

    improved = [n for n in VERDICT_PARAMS if reductions[n] >= THRESHOLD_PCT]
    supported = len(improved) >= 2
    print("\n=== v3 verdict (criterion: >=%.0f%% reduction for >=2 of the "
          "four original params) ===" % THRESHOLD_PCT)
    print("qualifying original params: %s" % (improved if improved else "none"))
    print("v3 %s" % ("SUPPORTED" if supported else
                      "NOT SUPPORTED (falsified as specified)"))

    # --- SECONDARY 1: nearest-neighbour recovery per arm ---
    print("\n=== secondary: NN recovery (median |diff| / full range) ===")
    print("%-9s %8s %8s %8s" % ("param", "tip", "shape", "combined"))
    nn_err = {arm: {} for arm in ARMS}
    for arm in ARMS:
        nn = NearestNeighbors(n_neighbors=2).fit(scaled[arm])
        _, idx2 = nn.kneighbors(scaled[arm])
        twin = idx2[:, 1]
        for name in ALL_PARAMS:
            e = 100.0 * np.median(np.abs(P[name][twin] - P[name])
                                  ) / full_range[name]
            nn_err[arm][name] = e
            rows.append({"probe": "nn_recovery", "arm": arm,
                         "param": name, "value": e})
    for name in ALL_PARAMS:
        print("%-9s %7.2f%% %7.2f%% %7.2f%%"
              % (name, nn_err["tip"][name], nn_err["shape"][name],
                 nn_err["combined"][name]))

    # --- SECONDARY 2: flexible decoder ---
    print("\n=== secondary: ExtraTrees 5-fold CV R2 ===")
    print("%-9s %8s %8s %8s" % ("param", "tip", "shape", "combined"))
    cv = KFold(5, shuffle=True, random_state=SEED)
    r2 = {arm: {} for arm in ARMS}
    for arm in ARMS:
        X = scaled[arm]
        for name in ALL_PARAMS:
            model = ExtraTreesRegressor(n_estimators=60, max_depth=12,
                                        random_state=SEED, n_jobs=-1)
            score = float(np.mean(cross_val_score(model, X, P[name],
                                                  cv=cv, n_jobs=-1)))
            r2[arm][name] = score
            rows.append({"probe": "cv_r2", "arm": arm,
                         "param": name, "value": score})
    for name in ALL_PARAMS:
        print("%-9s %8.3f %8.3f %8.3f"
              % (name, r2["tip"][name], r2["shape"][name],
                 r2["combined"][name]))

    # --- outputs ---
    out = pd.DataFrame(rows)
    out.to_csv("results/shape_identification_v3.csv", index=False)
    with open("results/shape_identification_v3_summary.json", "w") as fh:
        json.dump({
            "seed": SEED, "c_seed": C_SEED, "zeta_seed": ZETA_SEED,
            "n_plants": N_PLANTS, "n_twins": N_TWINS,
            "threshold_pct": THRESHOLD_PCT,
            "criterion": ">=25% twin-refinement error reduction for >=2 "
                         "of the 4 original params",
            "improved_params": improved, "supported": bool(supported),
            "reductions_pct": reductions,
            "nn_recovery_pct": nn_err, "cv_r2": r2,
        }, fh, indent=2)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        x = np.arange(len(ALL_PARAMS))
        w = 0.27
        fig, ax = plt.subplots(figsize=(8.5, 4.5))
        ax.bar(x - w, [rows_lookup(rows, "twin_refinement", "tip_nn", n)
                       for n in ALL_PARAMS], w, label="tip twin",
               color="#4C72B0")
        ax.bar(x, [rows_lookup(rows, "twin_refinement", "refined", n)
                   for n in ALL_PARAMS], w, label="refined by shape",
               color="#DD8452")
        ax.bar(x + w, [rows_lookup(rows, "twin_refinement", "oracle", n)
                       for n in ALL_PARAMS], w, label="oracle (of 20)",
               color="#55A868")
        ax.set_xticks(x, list(ALL_PARAMS))
        ax.set_ylabel("median |parameter difference| / full range (%)")
        ax.set_title("Twin refinement v3: identify the plant among its "
                     "curve twins")
        ax.legend()
        fig.tight_layout()
        fig.savefig("results/figures/twin_refinement_v3.png", dpi=150)
        plt.close(fig)
        print("\nsaved results/figures/twin_refinement_v3.png")
    except Exception as exc:
        print("figure skipped: %s" % exc)

    print("saved results/shape_identification_v3.csv, "
          "results/shape_identification_v3_summary.json")


def rows_lookup(rows, probe, arm, param):
    for r in rows:
        if r["probe"] == probe and r["arm"] == arm and r["param"] == param:
            return r["value"]
    return 0.0


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    os.makedirs("results/figures", exist_ok=True)
    main()
