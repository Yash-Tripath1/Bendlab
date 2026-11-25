"""Design Simulation 1 (design only): power for the prospective
early-rate test of beta_L.

Implements PHASE_D_DESIGN_SIMULATION_PLAN.md, fixed before this run.
Generates experiments from the pilot early-rate equation

    r_0-2 = beta_0 + beta_L ln(L0/14) + beta_I ln(I/2.25)
            + beta_theta * theta_0 + epsilon

with pilot beta_I, beta_theta and residual SD estimated from the 213
paired archive plants (phase_c_outcomes.csv), beta_L varied over
{0, 1.06, 1.59, 2.12} (null, 50%, 75%, pilot), and three covariate
designs (A archive-like joint resampling; B balanced intensity;
C wider natural ln L0 range). 2,000 simulated experiments per cell
are analysed by the exact planned OLS fit. Common covariate draws
and errors are shared across the beta_L values within a design/N
cell (common random numbers) so power differences between effect
sizes are not swamped by Monte Carlo noise.

Outputs: outputs/phase_d_power_early_rate.csv (one row per
design x effect x N), outputs/phase_d_power_early_rate.json
(pilot fit + interpolated required N for 80% and 90% power).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
LREF, IREF = 14.0, 2.25
REPS = 2000
NGRID = [50, 75, 100, 150, 200, 300, 450, 650, 900]
EFFECTS = [0.0, 1.06, 1.59, 2.12]
DESIGNS = ["A_archive_joint", "B_balanced_intensity",
           "C_wider_L0_range"]


def pilot_fit(df):
    X = np.column_stack([np.ones(len(df)), np.log(df.L0 / LREF),
                         np.log(df.I / IREF), df.theta0])
    y = df.rate02.to_numpy()
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    dof = len(df) - X.shape[1]
    return beta, float(np.sqrt(res @ res / dof))


def draw_covariates(design, df, N, rng):
    R = REPS
    idx = rng.integers(0, len(df), size=(R, N))
    L0 = df.L0.to_numpy()[idx]
    I = df.I.to_numpy()[idx]
    th = df.theta0.to_numpy()[idx]
    if design == "B_balanced_intensity":
        levels = np.sort(df.I.unique())
        ranks = np.argsort(rng.random((R, N)), axis=1)
        assign = np.empty((R, N), dtype=int)
        np.put_along_axis(assign, ranks,
                          np.tile(np.arange(N) % len(levels), (R, 1)),
                          axis=1)
        I = levels[assign]
    elif design == "C_wider_L0_range":
        mu = np.log(df.L0).mean()
        sd = 1.5 * np.log(df.L0).std(ddof=1)
        logL = rng.normal(mu, sd, size=(R, N))
        lo, hi = np.log(4.0), np.log(45.0)
        mask = (logL < lo) | (logL > hi)
        while mask.any():
            logL[mask] = rng.normal(mu, sd, size=int(mask.sum()))
            mask = (logL < lo) | (logL > hi)
        L0 = np.exp(logL)
    return L0, I, th


def analyse(X, y):
    """Batched OLS for y of shape (R, N, E). Returns beta_L, se, p,
    CI half-width arrays of shape (R, E)."""
    R, N, _ = X.shape
    XtX = np.einsum("rni,rnj->rij", X, X)
    XtXinv = np.linalg.inv(XtX)
    rows = []
    for e in range(y.shape[2]):
        ye = y[:, :, e]
        Xty = np.einsum("rni,rn->ri", X, ye)
        beta = np.einsum("rij,rj->ri", XtXinv, Xty)
        fit = np.einsum("rni,ri->rn", X, beta)
        res = ye - fit
        dof = N - X.shape[2]
        s2 = np.einsum("rn,rn->r", res, res) / dof
        se = np.sqrt(s2 * XtXinv[:, 1, 1])
        tstat = beta[:, 1] / se
        p = 2 * stats.t.sf(np.abs(tstat), dof)
        half = stats.t.ppf(0.975, dof) * se
        rows.append((beta[:, 1], se, p, half))
    return rows


def required_N(ns, powers, target):
    ns = np.asarray(ns, float); powers = np.asarray(powers, float)
    for i in range(1, len(ns)):
        if powers[i] >= target:
            if powers[i] == powers[i - 1]:
                return float(ns[i])
            f = (target - powers[i - 1]) / (powers[i] - powers[i - 1])
            return float(ns[i - 1] + f * (ns[i] - ns[i - 1]))
    return None


def main():
    df = pd.read_csv(OUT / "phase_c_outcomes.csv")
    beta_pilot, sd_res = pilot_fit(df)
    b0, _, bI, bth = beta_pilot
    rng_master = np.random.default_rng(20261026)
    rows = []
    req = {}
    for design in DESIGNS:
        for N in NGRID:
            rng = np.random.default_rng(rng_master.integers(1 << 31))
            L0, I, th = draw_covariates(design, df, N, rng)
            zL, zI = np.log(L0 / LREF), np.log(I / IREF)
            X = np.stack([np.ones_like(zL), zL, zI, th], axis=2)
            eps = rng.normal(0, sd_res, size=(REPS, N))
            base = b0 + bI * zI + bth * th + eps
            y = np.stack([base + bL * zL for bL in EFFECTS], axis=2)
            fits = analyse(X, y)
            for e, bL in enumerate(EFFECTS):
                bhat, se, p, half = fits[e]
                sig = p < 0.05
                row = {"design": design, "N": N, "beta_L_true": bL,
                       "reps": REPS,
                       "power_or_typeI": float(sig.mean()),
                       "mc_se": float(np.sqrt(sig.mean()
                                              * (1 - sig.mean()) / REPS)),
                       "coverage95": float(
                           np.mean(np.abs(bhat - bL) <= half)),
                       "mean_CI_width": float(2 * half.mean()),
                       "sign_error_frac_of_significant": float(
                           np.mean(bhat[sig] < 0) if bL > 0 and
                           sig.any() else 0.0),
                       "mean_beta_L_hat": float(bhat.mean())}
                rows.append(row)
            print(f"{design} N={N} done", flush=True)
        sub = pd.DataFrame([r for r in rows if r["design"] == design])
        for bL in EFFECTS:
            if bL == 0:
                continue
            s = sub[sub.beta_L_true == bL].sort_values("N")
            req[f"{design}|beta_L={bL}"] = {
                "N_for_80pct_power": required_N(
                    s.N, s.power_or_typeI, 0.80),
                "N_for_90pct_power": required_N(
                    s.N, s.power_or_typeI, 0.90)}
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "phase_d_power_early_rate.csv", index=False)
    summary = {
        "pilot_fit_from_archive": {
            "beta_0_at_L0_14mm_I_2.25_theta0_0": float(beta_pilot[0]),
            "beta_L_pilot": float(beta_pilot[1]),
            "beta_I": float(beta_pilot[2]),
            "beta_theta_per_deg": float(beta_pilot[3]),
            "residual_SD_deg_per_h": sd_res,
            "n_archive": int(len(df))},
        "designs": DESIGNS, "N_grid": NGRID, "reps_per_cell": REPS,
        "required_N_interpolated": req}
    (OUT / "phase_d_power_early_rate.json").write_text(
        json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
