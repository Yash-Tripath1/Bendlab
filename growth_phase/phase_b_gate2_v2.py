"""Gate 2 v2: conditional identifiability, effect-size sweep, and the
false-support rate under the Phase C adoption rule.

Post-audit extension (2026-10-24). It does NOT replace the original
Phase B run (phase_b_simulation.py); it answers the audit point that
the original 16/16 result was a winner-take-all selection at one
substantial effect size under one set of simulation assumptions.

What is new here:
  1. Generators span a range of effect sizes, not only the original
     substantial ones:
       M1a gain:      alpha in {0.2, 0.4, 0.8}   (0.8 = original)
       M1d opposing:  delta in {0.3, 0.6, 1.0}   (1.0 = original)
       M1c transport: v in {40, 20, 8} mm/h, i.e. lag slope
                      c = 1/v in {0.025, 0.05, 0.125} h/mm (v=8 original)
     plus the null M0 with more replicates (24) than the original (16).
  2. Every simulated data set is judged by the SAME adoption rule that
     Phase C used on the historical data (PHASE_B_PREREGISTRATION.md):
     5-fold plant-held-out CV stratified by intensity; an M1 variant is
     "supported" only if its median held-out RMSE improves on M0 by
     >= 5% AND the sign of its L0 parameter is stable across all 5
     folds. Under M0 this gives the false-support rate of that rule;
     under each M1 generator it gives the true-support rate, the
     wrong-variant support rate, and the no-support rate.
  3. Winner-take-all selection (lowest median CV RMSE, the original
     Gate 2 criterion) is also recorded per data set, so the two rules
     can be compared on identical data.

Candidate parameterisation matches Phase C for M0/M1a/M1d. M1c is
parameterised by the lag slope c (tau = tau0 + c*(L0 - Lref), c in
[-0.05, 0.30] h/mm) instead of by v, so that the sign-stability part of
the adoption rule is meaningful for it (v > 0 by construction would
make sign stability vacuous). This is a documented deviation in
parameterisation only; the mechanism (latency scales with L0) is the
pre-registered one.

Dynamics (all candidates and generators):
    tau dr/dt = k(I) sin(phi - theta) - gamma * theta - r
    dtheta/dt = clip(r, -60, 60), phi = 90 deg, k(I) = a * I**b
Generators add the archive-calibrated plant random effects and
observation process of phase_b_simulation.py (lognormal random effects
on k, tau, gamma; per-plant circumnutation-scale sinusoid; Gaussian
noise). N = 213 throughout. Seeds fixed.

Outputs: outputs/gate2_v2_replicates.csv (one row per simulated data
set), outputs/phase_b_gate2_v2.json (per-scenario summary with counts
and Wilson 95% intervals for support rates).
Runtime: several minutes.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
PHI = 90.0
T_END, DT_GEN, DT_FIT = 22.0, 0.05, 0.1
A0, B0, TAU0, GAM0 = 3.4, 0.3, 1.5, 0.12
LREF = 14.0
CANDS = ["M0", "M1a", "M1c", "M1d"]
M1S = ["M1a", "M1c", "M1d"]

SCENARIOS = [
    # (generator, effect label, effect value, replicates)
    ("M0", "none", 0.0, 24),
    ("M1a", "alpha=0.2", 0.2, 12),
    ("M1a", "alpha=0.4", 0.4, 12),
    ("M1a", "alpha=0.8", 0.8, 12),   # original Phase B size
    ("M1d", "delta=0.3", 0.3, 12),
    ("M1d", "delta=0.6", 0.6, 12),
    ("M1d", "delta=1.0", 1.0, 12),   # original Phase B size
    ("M1c", "v=40 (c=0.025)", 40.0, 12),
    ("M1c", "v=20 (c=0.05)", 20.0, 12),
    ("M1c", "v=8 (c=0.125)", 8.0, 12),  # original Phase B size
]


def simulate_pop(mech, effect, L0, I, th0, rng, dt=DT_GEN):
    n = len(L0)
    k = A0 * I ** B0 * np.exp(rng.normal(0, 0.25, n))
    tau = np.full(n, TAU0) * np.exp(rng.normal(0, 0.15, n))
    gam = np.full(n, GAM0) * np.exp(rng.normal(0, 0.15, n))
    if mech == "M1a":
        k = k * (L0 / LREF) ** effect
    elif mech == "M1c":
        tau = np.clip(TAU0 + (L0 - LREF) / effect, 0.3, None) \
            * np.exp(rng.normal(0, 0.15, n))
    elif mech == "M1d":
        gam = gam * (L0 / LREF) ** effect
    steps = int(T_END / dt)
    th = th0.copy(); r = np.zeros(n)
    traj = np.empty((steps + 1, n)); traj[0] = th
    for i in range(steps):
        target = k * np.sin(np.deg2rad(PHI - th)) - gam * th
        r += (target - r) * (dt / tau)
        np.clip(r, -60, 60, out=r)
        th = th + r * dt
        traj[i + 1] = th
    return traj


def observe(traj, rng):
    idx = np.arange(0, traj.shape[0], int(0.25 / DT_GEN))
    t = idx * DT_GEN
    obs = traj[idx].copy()
    n = traj.shape[1]
    for j in range(n):
        amp = rng.uniform(1.0, 3.5); per = rng.uniform(1.5, 3.5)
        ph = rng.uniform(0, 2 * np.pi)
        obs[:, j] += amp * np.sin(2 * np.pi * t / per + ph)
    obs += rng.normal(0, 1.2, obs.shape)
    return t, obs


def fit_candidate(mech, t, obs, L0, I, train_idx):
    """Population fit on training plants, residuals on a 1 h grid.

    Bounds as in Phase C (phase_c_historical.py). Returns a predict
    function and the fitted L0 parameter (alpha / c / delta).
    """
    fit_t_idx = np.arange(0, len(t), 4)
    y = obs[np.ix_(fit_t_idx, train_idx)]
    th0 = obs[0, train_idx]
    Ltr, Itr = L0[train_idx], I[train_idx]

    def unpack(x):
        return np.exp(x[0]), x[1], np.exp(x[2]), np.exp(x[3]), x[4]

    def predict(x, Ls, Is, starts):
        a, b, tau0, gam0, extra = unpack(x)
        k = a * Is ** b
        tau = np.full(len(Ls), tau0); gam = np.full(len(Ls), gam0)
        if mech == "M1a":
            k = k * (Ls / LREF) ** extra
        elif mech == "M1c":
            tau = np.clip(tau0 + extra * (Ls - LREF), 0.2, None)
        elif mech == "M1d":
            gam = gam * (Ls / LREF) ** extra
        steps = int(T_END / DT_FIT)
        th = starts.copy(); r = np.zeros(len(Ls))
        out = np.empty((steps + 1, len(Ls))); out[0] = th
        for i in range(steps):
            target = k * np.sin(np.deg2rad(PHI - th)) - gam * th
            r += (target - r) * (DT_FIT / tau)
            np.clip(r, -60, 60, out=r)
            th = th + r * DT_FIT
            out[i + 1] = th
        tt = np.arange(steps + 1) * DT_FIT
        return np.array([np.interp(t, tt, out[:, j])
                         for j in range(len(Ls))]).T

    def resid(x):
        return (predict(x, Ltr, Itr, th0)[fit_t_idx] - y).ravel()

    x0 = [np.log(A0), B0, np.log(TAU0), np.log(GAM0), 0.5]
    lo = [np.log(0.01), -0.5, np.log(0.05), np.log(0.001), -2.0]
    hi = [np.log(80.0), 2.0, np.log(40.0), np.log(3.0), 2.0]
    if mech == "M1c":
        x0[4], lo[4], hi[4] = 0.02, -0.05, 0.30
    sol = least_squares(resid, x0, bounds=(lo, hi), x_scale="jac",
                        max_nfev=80)
    extra = float(unpack(sol.x)[4])
    return (lambda Ls, Is, starts: predict(sol.x, Ls, Is, starts)), extra


def make_folds(I, rng):
    """5 folds, stratified by intensity value (Phase C procedure)."""
    fold_id = np.empty(len(I), dtype=int)
    for val in np.unique(I):
        idx = np.where(I == val)[0]
        idx = idx[rng.permutation(len(idx))]
        for j, i in enumerate(idx):
            fold_id[i] = j % 5
    return fold_id


def run_dataset(gen, effect, L0, I, th0, rng):
    traj = simulate_pop(gen, effect, L0, I, th0, rng)
    t, obs = observe(traj, rng)
    fold_id = make_folds(I, rng)
    per_plant = {c: [] for c in CANDS}
    extras = {m: [] for m in M1S}
    for f in range(5):
        test_idx = np.where(fold_id == f)[0]
        train_idx = np.where(fold_id != f)[0]
        for cand in CANDS:
            pred_fn, extra = fit_candidate(cand, t, obs, L0, I, train_idx)
            pred = pred_fn(L0[test_idx], I[test_idx], obs[0, test_idx])
            rmse = np.sqrt(np.mean((pred - obs[:, test_idx]) ** 2, axis=0))
            per_plant[cand].extend(rmse.tolist())
            if cand in extras:
                extras[cand].append(extra)
    med = {c: float(np.median(per_plant[c])) for c in CANDS}
    row = {"generator": gen, "effect": effect,
           **{f"median_rmse_{c}": med[c] for c in CANDS},
           "winner_lowest_median_rmse": min(med, key=med.get)}
    any_supported = False
    for m in M1S:
        signs = [int(np.sign(e)) for e in extras[m]]
        stable = len(set(signs)) == 1 and signs[0] != 0
        imp = 100.0 * (med["M0"] - med[m]) / med["M0"]
        supported = bool(imp >= 5.0 and stable)
        any_supported = any_supported or supported
        row[f"improvement_pct_{m}"] = float(imp)
        row[f"sign_stable_{m}"] = bool(stable)
        row[f"extra_median_{m}"] = float(np.median(extras[m]))
        row[f"supported_{m}"] = supported
    row["any_M1_supported"] = bool(any_supported)
    return row


def wilson(x, n, z=1.959964):
    if n == 0:
        return [None, None]
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [float(c - h), float(c + h)]


def main():
    paired = pd.read_csv(HERE / "outputs" / "paired_plants.csv")
    paired = paired[paired.has_length]
    L0_pool = paired["L0_mm"].to_numpy()
    I_pool = paired["light_i"].to_numpy()
    master = np.random.default_rng(20261024)
    rows = []
    t_start = time.time()
    for gen, label, effect, reps in SCENARIOS:
        for rep in range(reps):
            rng = np.random.default_rng(master.integers(1 << 31))
            N = 213
            L0 = rng.choice(L0_pool, size=N, replace=True)
            I = rng.choice(I_pool, size=N, replace=True)
            th0 = np.clip(rng.normal(0, 5, N), -15, 15)
            row = run_dataset(gen, effect, L0, I, th0, rng)
            row.update({"scenario": f"{gen}:{label}", "effect_label": label,
                        "rep": rep})
            rows.append(row)
            print(f"{gen} {label} rep {rep + 1}/{reps}: "
                  f"winner={row['winner_lowest_median_rmse']} "
                  f"any_supported={row['any_M1_supported']} "
                  f"({time.time() - t_start:.0f}s)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "gate2_v2_replicates.csv", index=False)

    summary = {"design": {
        "N_per_dataset": 213, "seeds": "master 20261024",
        "adoption_rule": ("median held-out RMSE improvement >= 5% over "
                          "M0 AND L0-parameter sign stable across 5 "
                          "folds (Phase C rule)"),
        "note": ("M1c candidate parameterised by lag slope c (h/mm); "
                 "generator uses v, c = 1/v.")},
        "scenarios": {}}
    for (gen, label), g in df.groupby(["generator", "effect_label"]):
        n = len(g)
        entry = {"n_datasets": int(n),
                 "winner_counts": {c: int((g.winner_lowest_median_rmse
                                            == c).sum()) for c in CANDS},
                 "any_M1_supported": {
                     "count": int(g.any_M1_supported.sum()), "of": int(n),
                     "wilson95": wilson(int(g.any_M1_supported.sum()), n)}}
        for m in M1S:
            x = int(g[f"supported_{m}"].sum())
            entry[f"supported_{m}"] = {"count": x, "of": int(n),
                                       "wilson95": wilson(x, n)}
            entry[f"median_improvement_pct_{m}"] = float(
                g[f"improvement_pct_{m}"].median())
        summary["scenarios"][f"{gen}:{label}"] = entry
    (OUT / "phase_b_gate2_v2.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
