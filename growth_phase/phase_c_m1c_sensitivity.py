"""Phase C sensitivity (post-audit): the M1c transport variant.

The pre-registration put M1c in the Phase C prediction comparison
"only if latency signal appears". No latency association was detected
on the 213 paired plants (coefficient per log L0 -0.75 h, 95% CI
[-2.02, 0.38], phase_c_results.json), so M1c was correctly absent from
the primary comparison (M0 vs M1a vs M1d). This script runs M1c anyway,
as a clearly labelled POST-AUDIT SENSITIVITY, so that the model
coverage of the Phase C conclusion is explicit and complete for the
pre-registered ODE family. It does not change the primary result and
must not be cited as pre-registered.

M1b (geometry) is not run here or anywhere in Phase C: it has no
fitted candidate in the pre-registered family (no diameter or
growth-zone geometry exists in this archive). M2 is likewise not
fitted: by design it has only a simulation fingerprint, and the
archive holds start/finish lengths only. The Phase C conclusion
therefore covers exactly: M0, M1a, M1d (primary) and M1c (this
sensitivity).

Parameterisation: tau = tau0 + c * (L0 - Lref), c in [-0.05, 0.30]
h/mm, so sign stability of c across folds is meaningful. The same
5-fold stratified split as phase_c_historical.py is rebuilt (seed 42)
and M0 is refitted on it as a replication check: it must reproduce
the primary M0 median RMSE (10.25 deg) before the M1c number is read.

Adoption rule applied descriptively (not as a pre-registered test):
>= 5% median RMSE improvement over M0 AND stable sign of c.

Outputs: outputs/phase_c_m1c_sensitivity.json,
         outputs/phase_c_m1c_folds.csv
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


def simulate(params, mech, I, L0, th0, times_out):
    a, b, tau0, gam, extra = params
    k = a * I ** b
    if mech == "M1a":
        k = k * (L0 / LREF) ** extra
    g = gam * (L0 / LREF) ** extra if mech == "M1d" else np.full(len(I), gam)
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
            errs.append((pred - th)[::12])
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
    # rebuild the exact primary folds (phase_c_historical.cv, seed 42)
    rng = np.random.default_rng(42)
    folds = [[] for _ in range(5)]
    for I, g in df.groupby("I"):
        idx = list(g.index); rng.shuffle(idx)
        for j, i in enumerate(idx):
            folds[j % 5].append(i)
    rows = []
    extras_c = []
    fitted = {}
    for f in range(5):
        test = df.loc[folds[f]]
        train = df.drop(index=folds[f])
        for mech in ("M0", "M1c"):
            p = fit(mech, train, plants)
            fitted[(f, mech)] = p
            if mech == "M1c":
                extras_c.append(p[4])
            pred = predict(p, mech, test, plants)
            for pid, pr in pred.items():
                t, th = plants[pid]
                rows.append({"plant": pid, "fold": f, "model": mech,
                             "rmse": float(np.sqrt(np.mean((pr - th) ** 2)))})
    res = pd.DataFrame(rows)
    res.to_csv(OUT / "phase_c_m1c_folds.csv", index=False)
    med = {m: float(res[res.model == m].rmse.median())
           for m in ("M0", "M1c")}
    primary = json.loads((OUT / "phase_c_results.json").read_text())
    m0_check = abs(med["M0"] - primary["cv_median_rmse_deg"]["M0"])
    imp = 100.0 * (med["M0"] - med["M1c"]) / med["M0"]
    signs = [int(np.sign(x)) for x in extras_c]
    out = {
        "status": ("POST-AUDIT SENSITIVITY, not pre-registered; primary "
                   "Phase C comparison remains M0 vs M1a vs M1d"),
        "why_M1c_was_not_primary": (
            "pre-registration included M1c only if a latency signal "
            "appeared; latency coefficient per log L0 -0.75 h, 95% CI "
            "[-2.02, 0.38], i.e. not detected"),
        "M1c_parameterisation": "tau = tau0 + c*(L0 - 14 mm), c in h/mm",
        "folds_rebuilt_from": "phase_c_historical.py cv() seed 42",
        "M0_replication_check_deg": {
            "refit_median_rmse": med["M0"],
            "primary_median_rmse": primary["cv_median_rmse_deg"]["M0"],
            "abs_diff": float(m0_check)},
        "cv_median_rmse_deg": med,
        "M1c_improvement_pct_vs_M0": float(imp),
        "M1c_c_by_fold_h_per_mm": [float(x) for x in extras_c],
        "M1c_c_signs_by_fold": signs,
        "M1c_sign_stable": bool(len(set(signs)) == 1 and signs[0] != 0),
        "adoption_rule_descriptive": {
            "improvement_ge_5pct": bool(imp >= 5.0),
            "supported": bool(imp >= 5.0
                              and len(set(signs)) == 1 and signs[0] != 0)},
        "not_fitted_anywhere_in_Phase_C": {
            "M1b_geometry": ("no fitted candidate; no diameter or "
                             "growth-zone geometry in this archive"),
            "M2_growth_generated": ("simulation fingerprint only by "
                                    "design; archive has start/finish "
                                    "lengths only")},
    }
    (OUT / "phase_c_m1c_sensitivity.json").write_text(
        json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
