"""Exploratory probe: can shape measurement improve parameter identification?

EXPLORATORY — NOT a pre-registered test. No hypothesis in this file may be
reported as confirmed. It runs on the saved H-SHAPE-v2 population
(results/shape_degeneracy_v2_features.csv.gz) to decide whether a
confirmatory, pre-registered study on a FRESH population is worth running,
and which protocol that study should use.

Motivation. H-SHAPE-v2 mixed 8 shape features into a KMeans distance
against 6 tip features and scored with cluster retention. That design can
fail even when shape carries parameter information: the shape dimensions
displace the tip dimensions in the metric, and cluster retention is the
blunt instrument already flagged after H2. Three probes separate
"shape has no information" from "the decoder was wrong":

A) Nearest-neighbour recovery (the H7 family of metric). For each plant,
   its nearest neighbour in an arm's feature space is a behavioural twin
   under that observable. The normalised parameter distance to the twin
   is the identification error. Arms: TIP (6 tip features), SHAPE (8
   shape features), COMBINED (all 14).

B) Twin refinement — the original shape method, stated properly. Among a
   plant's 20 nearest TIP-space neighbours (its curve twins), pick the
   one closest in SHAPE space. If curve twins differ in parameters but
   separate by shape, this refined pick must beat the plain tip twin.
   The oracle (best of the 20 in parameter distance, per parameter) is
   reported as the ceiling on any refinement.

C) Flexible decoder (ExtraTrees, 5-fold CV R2 per parameter per arm).
   A regressor weights dimensions instead of averaging them, so it tests
   whether the information is present but unused by clustering.

Run: python shape_probe_exploratory.py
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

import features as F
import features_shape as FS
from generate_plants import PARAM_NAMES

FEATURES_V2 = "results/shape_degeneracy_v2_features.csv.gz"
SEED = 1
N_TWINS = 20          # tip-space neighbours refined by shape

ARMS = {
    "tip": list(F.STATIC_FEATURES),
    "shape": list(FS.SHAPE_FEATURES),
    "combined": list(F.STATIC_FEATURES) + list(FS.SHAPE_FEATURES),
}
PARAMS = list(PARAM_NAMES) + ["c", "zeta"]


def main() -> None:
    feat = pd.read_csv(FEATURES_V2)
    n = len(feat)
    print("loaded %d plants from %s" % (n, FEATURES_V2))
    P = {name: feat[f"param_{name}"].to_numpy(float) for name in PARAMS}
    # Same normalisation as the retention metric: full range of this
    # population draw.
    full_range = {name: float(P[name].max() - P[name].min()) for name in PARAMS}
    scaled = {arm: StandardScaler().fit_transform(feat[cols].to_numpy())
              for arm, cols in ARMS.items()}

    rows = []

    # --- A: nearest-neighbour recovery per arm ---
    print("\n=== A: nearest-neighbour recovery "
          "(median |param difference| / full range, %) ===")
    print("%-9s %8s %8s %8s" % ("param", "tip", "shape", "combined"))
    for arm in ARMS:
        nn = NearestNeighbors(n_neighbors=2).fit(scaled[arm])
        _, idx = nn.kneighbors(scaled[arm])
        twin = idx[:, 1]
        for name in PARAMS:
            err = 100.0 * np.median(np.abs(P[name][twin] - P[name])
                                    / full_range[name])
            rows.append({"probe": "nn_recovery", "arm": arm,
                         "param": name, "value": err})
    for name in PARAMS:
        vals = {r["arm"]: r["value"] for r in rows
                if r["probe"] == "nn_recovery" and r["param"] == name}
        print("%-9s %7.1f%% %7.1f%% %7.1f%%"
              % (name, vals["tip"], vals["shape"], vals["combined"]))

    # --- B: twin refinement (the original shape method) ---
    print("\n=== B: twin refinement — among 20 tip-space twins, pick the "
          "closest in shape ===")
    print("%-9s %8s %8s %8s" % ("param", "tip-NN", "refined", "oracle"))
    nn_tip = NearestNeighbors(n_neighbors=N_TWINS + 1).fit(scaled["tip"])
    _, idx = nn_tip.kneighbors(scaled["tip"])
    cand = idx[:, 1:]                                   # (N, 20)
    Xs = scaled["shape"]
    d_shape = np.linalg.norm(Xs[:, None, :] - Xs[cand], axis=2)
    refined = cand[np.arange(n), d_shape.argmin(axis=1)]
    twin = cand[:, 0]
    for name in PARAMS:
        d = np.abs(P[name][cand] - P[name][:, None])     # (N, 20)
        e_twin = 100.0 * np.median(d[:, 0]) / full_range[name]
        e_ref = 100.0 * np.median(np.abs(P[name][refined] - P[name])
                                  ) / full_range[name]
        e_oracle = 100.0 * np.median(d.min(axis=1)) / full_range[name]
        for tag, v in (("tip_nn", e_twin), ("refined", e_ref),
                       ("oracle", e_oracle)):
            rows.append({"probe": "twin_refinement", "arm": tag,
                         "param": name, "value": v})
        print("%-9s %7.1f%% %7.1f%% %7.1f%%"
              % (name, e_twin, e_ref, e_oracle))

    # --- C: flexible decoder ---
    print("\n=== C: ExtraTrees 5-fold CV R2 per parameter ===")
    print("%-9s %8s %8s %8s" % ("param", "tip", "shape", "combined"))
    cv = KFold(5, shuffle=True, random_state=SEED)
    r2 = {arm: {} for arm in ARMS}
    for arm in ARMS:
        X = scaled[arm]
        for name in PARAMS:
            model = ExtraTreesRegressor(n_estimators=60, max_depth=12,
                                        random_state=SEED, n_jobs=-1)
            score = float(np.mean(cross_val_score(model, X, P[name],
                                                  cv=cv, n_jobs=-1)))
            r2[arm][name] = score
            rows.append({"probe": "cv_r2", "arm": arm,
                         "param": name, "value": score})
    for name in PARAMS:
        print("%-9s %8.3f %8.3f %8.3f"
              % (name, r2["tip"][name], r2["shape"][name],
                 r2["combined"][name]))

    out = pd.DataFrame(rows)
    out.to_csv("results/shape_probe_exploratory.csv", index=False)
    print("\nsaved results/shape_probe_exploratory.csv")
    print("REMINDER: exploratory only; any claim needs a pre-registered "
          "run on a fresh population.")


if __name__ == "__main__":
    main()
