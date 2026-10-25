"""Phase C sensitivity (post-audit): fitting on ALL observations.

The primary Phase C fits (phase_c_historical.py) compute residuals on
every 12th observation of each trajectory (the trajectories are
sampled about every 4 min, so fits used roughly hourly points). That
thinning was a computational choice, not a pre-registered one, and
was not documented in the original report. This script repeats the
identical 5-fold comparison (same folds, rebuilt with seed 42; same
models, bounds, and adoption rule) with residuals on ALL
observations, and compares the outcome against the committed primary
numbers in phase_c_results.json.

Verdict criterion stated in advance of running: the thinning choice
is considered immaterial if (a) no variant changes its supported /
not-supported status under the adoption rule and (b) median RMSE
values move by less than 5% for every model.

Models: M0, M1a, M1d (the pre-registered primary set), plus M1c
under its post-audit sensitivity parameterisation
(tau = tau0 + c*(L0 - 14 mm), c in [-0.05, 0.30] h/mm).

Outputs: outputs/phase_c_allobs_sensitivity.json,
         outputs/phase_c_allobs_folds.csv
Runtime: a few minutes (residual vectors are about 12x larger).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

import phase_c_historical as pc

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
PHI, DT, T_END = pc.PHI, pc.DT, pc.T_END
LREF = 14.0
MECHS = ("M0", "M1a", "M1d", "M1c")


def simulate(params, mech, I, L0, th0, times_out):
    a, b, tau0, gam, extra = params
    k = a * I ** b
    if mech == "M1a":
        k = k * (L0 / LREF) ** extra
    g = gam * (L0 / LREF) ** extra if mech == "M1d" \
        else np.full(len(I), gam)
    if mech == "M1c":
        tau = np.clip(tau0 + extra * (L0 - LREF), 0.2, None)
    else:
        tau = np.full(len(I), tau0)
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
    Is = dfsub.I.to_numpy(); Ls = dfsub.L0.to_numpy()
    series = [plants[pid] for pid in dfsub.real_id]
    th0 = np.array([s[1][0] for s in series])

    def resid(x):
        p = (np.exp(x[0]), x[1], np.exp(x[2]), np.exp(x[3]), x[4])
        tref = series[0][0]
        traj = simulate(p, mech, Is, Ls, th0, tref)
        errs = []
        for j, (t, th) in enumerate(series):
            pred = np.interp(t, tref, traj[:, j])
            errs.append(pred - th)  # ALL observations (primary: [::12])
        return np.concatenate(errs)

    x0 = [np.log(3.4), 0.3, np.log(1.5), np.log(0.12), 0.0]
    lo = [np.log(0.01), -0.5, np.log(0.05), np.log(0.001), -2.0]
    hi = [np.log(80), 2.0, np.log(40), np.log(3), 2.0]
    if mech == "M1c":
        x0[4], lo[4], hi[4] = 0.02, -0.05, 0.30
    sol = least_squares(resid, x0, bounds=(lo, hi), x_scale="jac",
                        max_nfev=60)
    return (np.exp(sol.x[0]), sol.x[1], np.exp(sol.x[2]),
            np.exp(sol.x[3]), sol.x[4])


def predict(params, mech, dfsub, plants):
    Is = dfsub.I.to_numpy(); Ls = dfsub.L0.to_numpy()
    out = {}
    for j, pid in enumerate(dfsub.real_id):
        t, th = plants[pid]
        out[pid] = simulate(params, mech, Is[j:j + 1], Ls[j:j + 1],
                            np.array([th[0]]), t)[:, 0]
    return out


def main():
    paired, plants = pc.load()
    df = pc.outcomes(paired, plants)
    rng = np.random.default_rng(42)  # identical folds to the primary
    folds = [[] for _ in range(5)]
    for I, g in df.groupby("I"):
        idx = list(g.index); rng.shuffle(idx)
        for j, i in enumerate(idx):
            folds[j % 5].append(i)
    rows = []
    extras = {m: [] for m in ("M1a", "M1d", "M1c")}
    for f in range(5):
        test = df.loc[folds[f]]
        train = df.drop(index=folds[f])
        for mech in MECHS:
            p = fit(mech, train, plants)
            if mech in extras:
                extras[mech].append(p[4])
            pred = predict(p, mech, test, plants)
            for pid, pr in pred.items():
                t, th = plants[pid]
                rows.append({"plant": pid, "fold": f, "model": mech,
                             "rmse": float(np.sqrt(
                                 np.mean((pr - th) ** 2)))})
        print(f"fold {f + 1}/5 done", flush=True)
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "phase_c_allobs_folds.csv", index=False)
    med = {m: float(res[res.model == m].rmse.median()) for m in MECHS}
    primary = json.loads((OUT / "phase_c_results.json").read_text())
    m1c_primary = json.loads(
        (OUT / "phase_c_m1c_sensitivity.json").read_text())
    committed = dict(primary["cv_median_rmse_deg"])
    committed["M1c"] = m1c_primary["cv_median_rmse_deg"]["M1c"]
    base = med["M0"]
    adoption = {}
    for m in ("M1a", "M1d", "M1c"):
        signs = [int(np.sign(x)) for x in extras[m]]
        imp = 100.0 * (base - med[m]) / base
        adoption[m] = {
            "improvement_pct_vs_M0_allobs": float(imp),
            "extra_by_fold": [float(x) for x in extras[m]],
            "sign_stable": bool(len(set(signs)) == 1 and signs[0] != 0),
            "supported_allobs": bool(
                imp >= 5.0 and len(set(signs)) == 1 and signs[0] != 0)}
    out = {
        "status": "POST-AUDIT sensitivity; primary remains "
                  "phase_c_historical.py (every-12th-observation fits)",
        "cv_median_rmse_deg_allobs": med,
        "cv_median_rmse_deg_committed_thinned": committed,
        "pct_change_vs_committed": {
            m: float(100 * (med[m] - committed[m]) / committed[m])
            for m in MECHS},
        "adoption_allobs": adoption,
        "verdict": {
            "any_status_change": bool(any(
                v["supported_allobs"] for v in adoption.values())),
            "note": ("criterion fixed in this docstring: thinning is "
                     "immaterial if no supported status changes and "
                     "all median RMSEs move by less than 5%")}}
    (OUT / "phase_c_allobs_sensitivity.json").write_text(
        json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
