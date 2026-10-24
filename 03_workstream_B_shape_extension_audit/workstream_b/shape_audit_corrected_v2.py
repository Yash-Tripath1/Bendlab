"""Phase B0 Workstream B audit reruns (VERSIONED, separate from the
submitted code; nothing in the submitted branch is modified).

Questions:
  Q1 Does the submitted `s_shape_sign_changes` implement its documentation
     (sign changes across neighbouring JOINTS at each time), or something
     else? If corrected, does the v3 verdict change?
  Q2 How similar are v3's "curve twins" in the FULL tip-angle trajectory
     (v3 selects them with six tip summary features)?
  Q3 Does the twin-refinement result survive a reference/query split
     (scalers and neighbour pools fitted on the reference half only)?
  Q4 What remains if phi0 is treated as a KNOWN shared assay input
     (fixed for every plant) instead of a per-plant sampled parameter?
     Two fixed cases: 60 deg (sensitivity case, v1) and 90 deg (the
     assay-matched horizontal side-light angle). Metrics whose normalising
     parameter range is zero in a fixed case are UNDEFINED: they are
     serialised as null with an explanation, never as NaN.

Run from anywhere:  python shape_audit_corrected_v2.py
Paths resolve relative to this file (packaged layout 03_.../workstream_b
next to 04_shape_extension_branch). Outputs:
corrected_audit_results_v2.json next to this script.
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from pathlib import Path

_HERE = Path(__file__).resolve().parent
_BRANCH = _HERE.parents[1] / "04_shape_extension_branch"
sys.path.insert(0, str(_BRANCH))

import features as F
import features_shape as FS
import sweep
from generate_plants import PARAM_NAMES, uniform_population
from sim_multiseg import batch_simulate_static, joint_curvatures, tip_angle

T_END, RECORD_DT, N_SEG = 24.0, 0.5, 5
N_PLANTS = 10_000
SEEDS = (101, 102, 103)
N_TWINS = 20
ALL_PARAMS = list(PARAM_NAMES) + ["c", "zeta"]
OUT = _HERE / "corrected_audit_results_v2.json"


def corrected_s_shape(thetas: np.ndarray) -> np.ndarray:
    """Sign changes across neighbouring JOINTS, per time, averaged over time.

    thetas: (T, N, n_seg) -> (N,). This is what the features_shape.py
    docstring describes ('number of sign changes in kappa_j along the stem').
    """
    kappa = joint_curvatures(thetas)                    # (T, N, J)
    signs = np.sign(kappa)
    changes = (signs[:, :, 1:] * signs[:, :, :-1] < 0).sum(axis=2)  # (T, N)
    return changes.mean(axis=0).astype(float)


def buggy_s_shape(thetas: np.ndarray) -> np.ndarray:
    """What the submitted code computes: sign changes across consecutive
    TIME steps for each joint (signs[1:] vs signs[:-1] on a (T, N, J)
    array slices axis 0 = time)."""
    kappa = joint_curvatures(thetas)
    signs = np.sign(kappa)
    changes = (signs[1:] * signs[:-1] < 0).sum(axis=2)  # (T-1, N) : over time
    return changes.mean(axis=0).astype(float)


def build_population(phi_fixed: float | None):
    four = uniform_population(N_PLANTS, seed=SEEDS[0])
    df = pd.DataFrame(four, columns=PARAM_NAMES)
    if phi_fixed is not None:
        df["phi0"] = phi_fixed
    rng_c = np.random.default_rng(SEEDS[1])
    df["c"] = rng_c.random(N_PLANTS)
    rng_z = np.random.default_rng(SEEDS[2])
    df["zeta"] = rng_z.random(N_PLANTS)
    t_s, th_s = batch_simulate_static(
        df["k"].to_numpy(), df["tau"].to_numpy(), df["max_rate"].to_numpy(),
        df["phi0"].to_numpy(), df["c"].to_numpy(),
        T_END, record_dt=RECORD_DT, n_seg=N_SEG, zeta=df["zeta"].to_numpy())
    feat = sweep.feature_frame(t_s, tip_angle(th_s), df, "static")
    for name in ("c", "zeta"):
        feat[f"param_{name}"] = df[name].to_numpy()
    shape = FS.shape_batch(t_s, th_s)
    for j, name in enumerate(FS.SHAPE_FEATURES):
        feat[name] = shape[:, j]
    feat["s_shape_corrected"] = corrected_s_shape(th_s)
    return df, feat, t_s, tip_angle(th_s)


def twin_refinement(feat: pd.DataFrame, shape_col_buggy: str,
                    query_idx=None, ref_idx=None):
    """Primary v3 protocol; optional reference/query split (scalers and
    neighbour pool from reference only when ref_idx is given)."""
    tip_cols = list(F.STATIC_FEATURES)
    shape_cols = [c if c != "s_shape_sign_changes" else shape_col_buggy
                  for c in FS.SHAPE_FEATURES]
    P = {n: feat[f"param_{n}"].to_numpy(float) for n in ALL_PARAMS}
    rng_full = {n: float(P[n].max() - P[n].min()) for n in ALL_PARAMS}
    if ref_idx is None:
        ref_idx = query_idx = np.arange(len(feat))
    Xs_tip_ref = StandardScaler().fit(feat.iloc[ref_idx][tip_cols])
    Xs_shp_ref = StandardScaler().fit(feat.iloc[ref_idx][shape_cols])
    tip_ref = Xs_tip_ref.transform(feat.iloc[ref_idx][tip_cols])
    tip_q = Xs_tip_ref.transform(feat.iloc[query_idx][tip_cols])
    shp_ref = Xs_shp_ref.transform(feat.iloc[ref_idx][shape_cols])
    shp_q = Xs_shp_ref.transform(feat.iloc[query_idx][shape_cols])
    nn = NearestNeighbors(n_neighbors=N_TWINS + (1 if ref_idx is query_idx
                                                 else 0)).fit(tip_ref)
    _, idx = nn.kneighbors(tip_q)
    if ref_idx is query_idx:
        cand_local, first_local = idx[:, 1:], idx[:, 1]
    else:
        cand_local, first_local = idx[:, :N_TWINS], idx[:, 0]
    cand = ref_idx[cand_local]
    first = ref_idx[first_local]
    d_shape = np.linalg.norm(shp_q[:, None, :] - shp_ref[cand_local], axis=2)
    refined = cand[np.arange(len(query_idx)), d_shape.argmin(axis=1)]
    res = {}
    for n in ALL_PARAMS:
        e_twin = 100 * np.median(np.abs(P[n][first] - P[n][query_idx])) / rng_full[n]
        e_ref = 100 * np.median(np.abs(P[n][refined] - P[n][query_idx])) / rng_full[n]
        res[n] = {"tip_nn_pct": float(e_twin), "refined_pct": float(e_ref),
                  "reduction_pct": float(100 * (e_twin - e_ref) / e_twin)}
    return res, first, refined, cand


def trajectory_rmse(tip: np.ndarray, query_idx, cand_first, cand_refined):
    """Full tip-trajectory RMSE (deg) between query plants and their picks."""
    out = {}
    for tag, pick in (("tip_nn", cand_first), ("refined", cand_refined)):
        diff = tip[:, query_idx].T - tip[:, pick].T          # (Q, T)
        rmse = np.sqrt((diff ** 2).mean(axis=1))
        out[tag] = {"median_rmse_deg": float(np.median(rmse)),
                    "p75_rmse_deg": float(np.percentile(rmse, 75)),
                    "median_max_abs_deg": float(np.median(np.abs(diff).max(axis=1)))}
    return out


def main():
    results = {}
    df, feat, t_s, tip = build_population(phi_fixed=None)

    # --- Q1: what does the submitted feature actually measure?
    ks = joint_curvatures(batch_simulate_static(
        df["k"].to_numpy()[:50], df["tau"].to_numpy()[:50],
        df["max_rate"].to_numpy()[:50], df["phi0"].to_numpy()[:50],
        df["c"].to_numpy()[:50], T_END, record_dt=RECORD_DT, n_seg=N_SEG,
        zeta=df["zeta"].to_numpy()[:50])[1])
    results["q1_feature_check"] = {
        "submitted_matches_its_own_shape_batch": bool(np.allclose(
            feat["s_shape_sign_changes"].to_numpy(), buggy_s_shape(
                batch_simulate_static(
                    df["k"].to_numpy(), df["tau"].to_numpy(),
                    df["max_rate"].to_numpy(), df["phi0"].to_numpy(),
                    df["c"].to_numpy(), T_END, record_dt=RECORD_DT,
                    n_seg=N_SEG, zeta=df["zeta"].to_numpy())[1]))),
        "buggy_feature_stats": {
            "mean": float(feat["s_shape_sign_changes"].mean()),
            "std": float(feat["s_shape_sign_changes"].std()),
            "max": float(feat["s_shape_sign_changes"].max())},
        "corrected_feature_stats": {
            "mean": float(feat["s_shape_corrected"].mean()),
            "std": float(feat["s_shape_corrected"].std()),
            "max": float(feat["s_shape_corrected"].max())},
        "corr_buggy_vs_corrected": float(np.corrcoef(
            feat["s_shape_sign_changes"], feat["s_shape_corrected"])[0, 1]),
        "frac_plants_corrected_zero": float(
            (feat["s_shape_corrected"] == 0).mean()),
        "frac_plants_buggy_zero": float(
            (feat["s_shape_sign_changes"] == 0).mean()),
    }

    # --- Q2 + primary reruns (in-population, as v3)
    for tag, col in (("submitted_feature", "s_shape_sign_changes"),
                     ("corrected_feature", "s_shape_corrected")):
        res, first, refined, _ = twin_refinement(feat, col)
        results[f"primary_{tag}"] = res
        if tag == "submitted_feature":
            results["q2_full_trajectory_similarity"] = trajectory_rmse(
                tip, np.arange(N_PLANTS), first, refined)

    # --- Q3: reference/query split (seed 7, half/half)
    rng = np.random.default_rng(7)
    perm = rng.permutation(N_PLANTS)
    ref_idx, query_idx = np.sort(perm[: N_PLANTS // 2]), np.sort(perm[N_PLANTS // 2:])
    for tag, col in (("submitted_feature", "s_shape_sign_changes"),
                     ("corrected_feature", "s_shape_corrected")):
        res, first, refined, _ = twin_refinement(feat, col, query_idx, ref_idx)
        results[f"refquery_{tag}"] = res
        if tag == "submitted_feature":
            results["q3_full_trajectory_similarity"] = trajectory_rmse(
                tip, query_idx, first, refined)

    # --- Q4: phi0 as known shared input (two fixed cases)
    for fixed in (60.0, 90.0):
        dfF, featF, _, _ = build_population(phi_fixed=fixed)
        resF, _, _, _ = twin_refinement(featF, "s_shape_sign_changes")
        tag = f"primary_phi0_known_fixed{int(fixed)}"
        results[tag] = resF
        results[tag + "_undefined_note"] = (
            "phi0 has zero range in this fixed case, so phi0 normalised "
            "errors are undefined and serialised as null")

    def _clean(o):
        if isinstance(o, float) and not np.isfinite(o):
            return None
        if isinstance(o, dict):
            return {k: _clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [_clean(v) for v in o]
        return o

    with open(OUT, "w") as fh:
        json.dump(_clean(results), fh, indent=2)
    print(json.dumps(results, indent=2))
    print("saved", OUT)


if __name__ == "__main__":
    main()
