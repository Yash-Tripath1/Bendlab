"""Phase B: simulation identifiability for the growth-aware model family.

Implements PHASE_B_PREREGISTRATION.md. Generators M0 / M1a (gain) /
M1c (transport lag) / M1d (opposing) share the form

    tau dr/dt = k(I) sin(phi - theta) - gamma * theta - r
    dtheta/dt = clip(r, -60, 60),  phi = 90 deg,
    k(I) = a * I**b

with plant lognormal random effects, empirical L0 / intensity /
initial-angle distributions from the Phase A paired set, Gaussian
observation noise plus per-plant circumnutation-scale sinusoids.
Candidates are fitted as population models (no per-plant random
effects; theta(0) = first observed value) on training plants and
selected by held-out-plant RMSE. Views: (i) tip angle only (candidates
may not use L0: M0 only, so mechanism selection is impossible by
construction and we report RMSE inflation), (ii) tip + L0 (full
candidate set), (iii) tip + L0 + start/finish length (same candidate
set for these mechanisms; the extra view matters for the M2
fingerprint, reported separately).

Also simulates the M2 growth-generated fingerprint (bend per unit
cumulative elongation) under M2 vs M1a generation.

Outputs: outputs/phase_b_identifiability.json, outputs/confusion_N213.csv
Runtime: a few minutes. Seeds fixed.
"""

from __future__ import annotations

import json
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
MECHS = ["M0", "M1a", "M1c", "M1d"]
TRUE_PARAM = {"M0": 0.0, "M1a": 0.8, "M1c": 8.0, "M1d": 1.0}  # alpha, v, delta


def simulate_pop(mech, L0, I, th0, rng, dt=DT_GEN):
    n = len(L0)
    k = A0 * I ** B0 * np.exp(rng.normal(0, 0.25, n))
    tau = np.full(n, TAU0) * np.exp(rng.normal(0, 0.15, n))
    gam = np.full(n, GAM0) * np.exp(rng.normal(0, 0.15, n))
    if mech == "M1a":
        k = k * (L0 / LREF) ** TRUE_PARAM["M1a"]
    elif mech == "M1c":
        tau = np.clip(TAU0 + (L0 - LREF) / TRUE_PARAM["M1c"], 0.3, None) \
            * np.exp(rng.normal(0, 0.15, n))
    elif mech == "M1d":
        gam = gam * (L0 / LREF) ** TRUE_PARAM["M1d"]
    steps = int(T_END / dt)
    th = th0.copy(); r = np.zeros(n)
    traj = np.empty((steps + 1, n)); traj[0] = th
    for i in range(steps):
        target = k * np.sin(np.deg2rad(PHI - th)) - gam * th
        r += (target - r) * (dt / tau)
        np.clip(r, -60, 60, out=r)
        th = th + r * dt
        traj[i + 1] = th
    return traj  # (steps+1, n) at dt


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
    """Population fit of one candidate on training plants (1 h grid)."""
    fit_t_idx = np.arange(0, len(t), 4)
    y = obs[np.ix_(fit_t_idx, train_idx)]
    th0 = obs[0, train_idx]
    Ltr, Itr = L0[train_idx], I[train_idx]

    def unpack(x):
        a, b, tau0, gam0 = np.exp(x[0]), x[1], np.exp(x[2]), np.exp(x[3])
        extra = x[4]
        return a, b, tau0, gam0, extra

    def predict(x, idxs, Ls, Is, starts):
        a, b, tau0, gam0, extra = unpack(x)
        k = a * Is ** b; tau = np.full(len(idxs), tau0); gam = np.full(len(idxs), gam0)
        if mech == "M1a":
            k = k * (Ls / LREF) ** extra
        elif mech == "M1c":
            tau = np.clip(tau0 + (Ls - LREF) / max(extra, 0.5), 0.2, None)
        elif mech == "M1d":
            gam = gam * (Ls / LREF) ** extra
        steps = int(T_END / DT_FIT)
        th = starts.copy(); r = np.zeros(len(idxs))
        out = np.empty((steps + 1, len(idxs))); out[0] = th
        for i in range(steps):
            target = k * np.sin(np.deg2rad(PHI - th)) - gam * th
            r += (target - r) * (DT_FIT / tau)
            np.clip(r, -60, 60, out=r)
            th = th + r * DT_FIT
            out[i + 1] = th
        tt = np.arange(steps + 1) * DT_FIT
        return np.array([np.interp(t, tt, out[:, j]) for j in range(len(idxs))]).T

    def resid(x):
        return (predict(x, train_idx, Ltr, Itr, th0)[fit_t_idx] - y).ravel()

    x0 = [np.log(A0), B0, np.log(TAU0), np.log(GAM0), 0.5]
    lo = [np.log(0.05), -0.5, np.log(0.1), np.log(0.005), -2.0]
    hi = [np.log(60.0), 2.0, np.log(30.0), np.log(3.0), 2.0]
    if mech == "M1c":
        x0[4], lo[4], hi[4] = 10.0, 0.6, 200.0
    sol = least_squares(resid, x0, bounds=(lo, hi), x_scale="jac", max_nfev=80)
    return (lambda idxs, Ls, Is, starts: predict(sol.x, idxs, Ls, Is, starts),
            float(unpack(sol.x)[4]))


def run_setting(N, reps, seed0, paired):
    rng_master = np.random.default_rng(seed0)
    confusion = {g: {c: 0 for c in MECHS} for g in MECHS}
    rmse_ratio_tiponly = []
    param_rows = []
    for rep in range(reps):
        rng = np.random.default_rng(rng_master.integers(1 << 31))
        L0 = rng.choice(paired["L0_mm"].to_numpy(), size=N, replace=True)
        I = rng.choice(paired["light_i"].to_numpy(), size=N, replace=True)
        th0 = np.clip(rng.normal(0, 5, N), -15, 15)
        perm = rng.permutation(N)
        n_train = int(0.7 * N)
        train_idx, test_idx = perm[:n_train], perm[n_train:]
        for gen in MECHS:
            traj = simulate_pop(gen, L0, I, th0, rng)
            t, obs = observe(traj, rng)
            scores = {}
            fitted_extra = {}
            for cand in MECHS:
                pred_fn, extra = fit_candidate(cand, t, obs, L0, I, train_idx)
                pred = pred_fn(test_idx, L0[test_idx], I[test_idx], obs[0, test_idx])
                scores[cand] = float(np.sqrt(np.mean((pred - obs[:, test_idx]) ** 2)))
                fitted_extra[cand] = extra
            pick = min(scores, key=scores.get)
            confusion[gen][pick] += 1
            rmse_ratio_tiponly.append(scores["M0"] / scores[gen])
            param_rows.append({"rep": rep, "generator": gen, "pick": pick,
                               "extra_M1a": fitted_extra["M1a"],
                               "extra_M1c": fitted_extra["M1c"],
                               "extra_M1d": fitted_extra["M1d"]})
        print(f"  rep {rep + 1}/{reps} done", flush=True)
    return confusion, float(np.median(rmse_ratio_tiponly)), param_rows


def m2_fingerprint(paired, seed=5):
    """Bend per unit cumulative elongation: M2 generation vs M1a."""
    rng = np.random.default_rng(seed)
    N = 213
    L0 = rng.choice(paired["L0_mm"].to_numpy(), size=N, replace=True)
    I = rng.choice(paired["light_i"].to_numpy(), size=N, replace=True)
    th0 = np.clip(rng.normal(0, 5, N), -15, 15)
    # M2: elongation G_i total, bending rate proportional to growth rate
    G = np.exp(rng.normal(np.log(9.0), 0.35, N))          # mm over ~22 h
    steps = int(T_END / DT_GEN); th = th0.copy()
    for i in range(steps):
        tt = i * DT_GEN
        dL = G / 9.0 * np.exp(-tt / 9.0)                  # mm/h
        r = 6.0 * dL * np.sin(np.deg2rad(PHI - th)) - GAM0 * th
        th = th + np.clip(r, -60, 60) * DT_GEN
    ratio_m2 = (th - th0) / G
    # M1a generation with independent elongation of the same distribution
    traj = simulate_pop("M1a", L0, I, th0, rng)
    G2 = np.exp(rng.normal(np.log(9.0), 0.35, N))
    ratio_m1a = (traj[-1] - th0) / G2
    return {
        "corr_thetaFinal_vs_elongation_M2": float(np.corrcoef(th - th0, G)[0, 1]),
        "corr_thetaFinal_vs_elongation_M1a": float(np.corrcoef(traj[-1] - th0, G2)[0, 1]),
        "CV_bend_per_elongation_M2": float(np.std(ratio_m2) / np.mean(ratio_m2)),
        "CV_bend_per_elongation_M1a": float(np.std(ratio_m1a) / np.mean(ratio_m1a)),
    }


def main():
    paired = pd.read_csv(HERE / "outputs" / "paired_plants.csv")
    paired = paired[paired.has_length]
    results = {}
    print("N=213 setting...")
    conf, ratio, rows = run_setting(213, 16, 101, paired)
    results["N213"] = {"confusion": conf, "median_RMSE_M0_over_oracle": ratio}
    pd.DataFrame(rows).to_csv(OUT / "confusion_N213.csv", index=False)
    print("N=2000 (large-N check) ...")
    conf2, ratio2, _ = run_setting(2000, 3, 202, paired)
    results["N2000"] = {"confusion": conf2, "median_RMSE_M0_over_oracle": ratio2}
    results["M2_fingerprint"] = m2_fingerprint(paired)
    (OUT / "phase_b_identifiability.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
