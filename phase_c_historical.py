"""Phase C: limited historical checks on the 213 paired plants.

Implements PHASE_B_PREREGISTRATION.md section "Pre-registered
comparisons". Association language only; no mechanism claims.

1. Per-plant outcomes vs log L0 (covariates: log intensity, theta0),
   plant-bootstrap 95% CIs (1,000 resamples).
2. M0 vs M1a vs M1d population fits, 5-fold plant-held-out CV
   stratified by intensity. Adoption rule from the pre-registration:
   >=5% median RMSE improvement AND stable sign across folds.
3. Interval-average elongation vs total angular change (partial on
   intensity).

Candidate dynamics (all with the Phase B opposing term):
    tau dr/dt = k(I) sin(90 - theta) - gamma * theta - r
M0: k = a I^b | M1a: k *= (L0/Lref)^alpha | M1d: gamma *= (L0/Lref)^delta
max_rate fixed non-binding at 60 deg/h. Integration dt = 5 min.

Outputs: outputs/phase_c_results.json, outputs/phase_c_folds.csv
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
PHI, DT, T_END = 90.0, 1 / 12, 22.0


def load():
    paired = pd.read_csv(OUT / "paired_plants.csv")
    U = pd.read_csv(HERE / "data" / "00_Data" / "uni_trajectories.csv")
    plants = {}
    for pid, g in U.sort_values("dt").groupby("real_id"):
        plants[pid] = (g["dt"].to_numpy(float), g["theta"].to_numpy(float))
    return paired, plants


def outcomes(paired, plants):
    rows = []
    for _, r in paired[paired.has_length].iterrows():
        t, th = plants[r.real_id]
        plateau = th[(t >= 16) & (t <= 21)].mean()
        hit = np.where(th >= 10)[0]
        rows.append({
            "real_id": r.real_id, "I": r.light_i, "L0": r.L0_mm,
            "theta0": r.theta0_deg,
            "latency10_h": float(t[hit[0]]) if len(hit) else 22.0,
            "rate02": float(np.polyfit(t[t <= 2], th[t <= 2], 1)[0]),
            "angle8": float(np.interp(8, t, th)),
            "plateau1621": float(plateau),
            "total_change": float(plateau - r.theta0_deg),
            "growth_speed": r.growth_speed_mm_h})
    return pd.DataFrame(rows)


def assoc(df):
    res = {}
    rng = np.random.default_rng(7)
    X0 = np.column_stack([np.ones(len(df)), np.log(df.I), df.theta0])
    for y in ["latency10_h", "rate02", "angle8", "plateau1621", "total_change"]:
        X = np.column_stack([np.log(df.L0), X0])
        beta, *_ = np.linalg.lstsq(X, df[y], rcond=None)
        boots = []
        for _ in range(1000):
            idx = rng.integers(0, len(df), len(df))
            b, *_ = np.linalg.lstsq(X[idx], df[y].to_numpy()[idx], rcond=None)
            boots.append(b[0])
        res[y] = {"coef_logL0": float(beta[0]),
                  "ci95": [float(np.percentile(boots, 2.5)),
                           float(np.percentile(boots, 97.5))]}
    # partial correlation: growth speed vs total change given log I
    def resid_on(v, X):
        b, *_ = np.linalg.lstsq(X, v, rcond=None)
        return v - X @ b
    Xc = np.column_stack([np.ones(len(df)), np.log(df.I)])
    rx = resid_on(df.growth_speed.to_numpy(), Xc)
    ry = resid_on(df.total_change.to_numpy(), Xc)
    res["partial_corr_growth_vs_change_given_I"] = float(np.corrcoef(rx, ry)[0, 1])
    return res


def simulate(params, mech, I, L0, th0, times_out):
    a, b, tau, gam, extra = params
    k = a * I ** b
    if mech == "M1a":
        k = k * (L0 / 14.0) ** extra
    g = gam * (L0 / 14.0) ** extra if mech == "M1d" else np.full(len(I), gam)
    steps = int(T_END / DT)
    th = th0.copy(); r = np.zeros(len(I))
    traj = np.empty((steps + 1, len(I))); traj[0] = th
    for i in range(steps):
        target = k * np.sin(np.deg2rad(PHI - th)) - g * th
        r += (target - r) * (DT / tau)
        np.clip(r, -60, 60, out=r)
        th = th + r * DT
        traj[i + 1] = th
    tt = np.arange(steps + 1) * DT
    return np.array([np.interp(times_out, tt, traj[:, j])
                     for j in range(len(I))]).T


def fit(mech, dfsub, plants):
    idx = dfsub.index.to_numpy()
    Is = dfsub.I.to_numpy(); Ls = dfsub.L0.to_numpy()
    series = [plants[pid] for pid in dfsub.real_id]
    th0 = np.array([s[1][0] for s in series])

    def resid(x):
        p = (np.exp(x[0]), x[1], np.exp(x[2]), np.exp(x[3]), x[4])
        # batch-simulate all training plants on plant 0's time base,
        # then interpolate each plant onto its own observed times
        tref = series[0][0]
        traj = simulate(p, mech, Is, Ls, th0, tref)      # (Tref, N)
        errs = []
        for j, (t, th) in enumerate(series):
            pred = np.interp(t, tref, traj[:, j])
            errs.append((pred - th)[::12])
        return np.concatenate(errs)

    sol = least_squares(resid, [np.log(3.4), 0.3, np.log(1.5),
                                np.log(0.12), 0.0],
                        bounds=([np.log(0.01), -0.5, np.log(0.05),
                                 np.log(0.001), -2.0],
                                [np.log(80), 2.0, np.log(40), np.log(3), 2.0]),
                        x_scale="jac", max_nfev=60)
    return (np.exp(sol.x[0]), sol.x[1], np.exp(sol.x[2]),
            np.exp(sol.x[3]), sol.x[4])


def predict(params, mech, dfsub, plants):
    Is = dfsub.I.to_numpy(); Ls = dfsub.L0.to_numpy()
    out = {}
    for j, pid in enumerate(dfsub.real_id):
        t, th = plants[pid]
        out[pid] = simulate(params, mech, Is[j:j+1], Ls[j:j+1],
                            np.array([th[0]]), t)[:, 0]
    return out


def cv(df, plants):
    rng = np.random.default_rng(42)
    folds = [[] for _ in range(5)]
    for I, g in df.groupby("I"):
        idx = list(g.index); rng.shuffle(idx)
        for j, i in enumerate(idx):
            folds[j % 5].append(i)
    rows = []
    signs = {m: [] for m in ("M1a", "M1d")}
    for f in range(5):
        test = df.loc[folds[f]]
        train = df.drop(index=folds[f])
        for mech in ("M0", "M1a", "M1d"):
            p = fit(mech, train, plants)
            if mech in signs:
                signs[mech].append(np.sign(p[4]))
            pred = predict(p, mech, test, plants)
            for pid, pr in pred.items():
                t, th = plants[pid]
                rows.append({"plant": pid, "model": mech,
                             "rmse": float(np.sqrt(np.mean((pr - th) ** 2)))})
    res = pd.DataFrame(rows)
    summ = {m: float(res[res.model == m].rmse.median())
            for m in ("M0", "M1a", "M1d")}
    return summ, signs, res


def main():
    paired, plants = load()
    df = outcomes(paired, plants)
    df.to_csv(OUT / "phase_c_outcomes.csv", index=False)
    results = {"associations": assoc(df)}
    summ, signs, res = cv(df, plants)
    res.to_csv(OUT / "phase_c_folds.csv", index=False)
    results["cv_median_rmse_deg"] = summ
    results["L0_param_signs_by_fold"] = {k: [int(x) for x in v]
                                         for k, v in signs.items()}
    base = summ["M0"]
    results["adoption"] = {
        m: {"improvement_pct": float(100 * (base - summ[m]) / base),
            "sign_stable": bool(len(set(signs[m])) == 1),
            "supported": bool(100 * (base - summ[m]) / base >= 5
                              and len(set(signs[m])) == 1)}
        for m in ("M1a", "M1d")}
    (OUT / "phase_c_results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
