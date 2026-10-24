"""Probes suggested by external review (Oct 2026), all phototropism-only.

Probe 1 - is the stall locked to stimulus onset or to the clock?
    Reuses results/zt9_stall_times.csv (operational stall detector v2).
    Elapsed-time clustering is measured by IQR; clock-phase clustering
    by circular statistics (resultant length R, circular SD). Two
    permutation tests (10,000 shuffles):
      (a) shuffle stimulus-start times across plants, keeping elapsed
          stall times -> null distribution of phase concentration;
      (b) shuffle elapsed stall times across plants, keeping starts ->
          null distribution of elapsed IQR.

Probe 2 - is fitted phi0 just a plateau knob, and do curves overshoot?
    (a) Overshoot census: per curve, peak angle minus final angle.
    (b) Correlation of fitted phi0 with observed final angle.
    (c) Harsh refit: phi0 fixed at 60/75/90 deg for all 48 plants;
        compare median RMSE with the free-phi0 fits (headline 1.80 deg).
"""

from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

import fit_real
from data_real import curves, load_long

rng = np.random.default_rng(20261015)
NPERM = 10_000


def circ_stats(phase_h):
    ang = 2 * np.pi * np.asarray(phase_h) / 24.0
    R = float(np.abs(np.mean(np.exp(1j * ang))))
    csd = float(np.sqrt(-2 * np.log(max(R, 1e-12))) * 24.0 / (2 * np.pi))
    return R, csd


def probe1():
    stall = pd.read_csv("results/zt9_stall_times.csv").dropna(
        subset=["stall_elapsed"])
    el = stall.stall_elapsed.to_numpy(float)
    starts = stall.t_start.to_numpy(float)
    phase = (starts + el) % 24.0
    iqr_el = float(np.quantile(el, .75) - np.quantile(el, .25))
    R_obs, csd = circ_stats(phase)

    # (a) clock-lock null: phases are meaningful, starts exchangeable
    R_perm = np.empty(NPERM)
    for i in range(NPERM):
        R_perm[i], _ = circ_stats((rng.permutation(starts) + el) % 24.0)
    p_phase = float((R_perm >= R_obs).mean())

    # (b) stimulus-lock null: elapsed times exchangeable across plants
    iqr_perm = np.empty(NPERM)
    for i in range(NPERM):
        e = rng.permutation(el)
        iqr_perm[i] = np.quantile(e, .75) - np.quantile(e, .25)
    # IQR of the pooled elapsed values is start-independent, so instead
    # test block structure: variance of block medians under label shuffle
    blocks = stall.block.to_numpy()
    med_obs = stall.groupby("block").stall_elapsed.median()
    spread_obs = float(med_obs.max() - med_obs.min())
    spread_perm = np.empty(NPERM)
    for i in range(NPERM):
        s = pd.Series(rng.permutation(el)).groupby(
            pd.Series(blocks)).median()
        spread_perm[i] = s.max() - s.min()
    p_block = float((spread_perm <= spread_obs).mean())

    return {
        "n_stalling_of_48": int(len(stall)),
        "stall_elapsed_median_h": float(np.median(el)),
        "stall_elapsed_IQR_h": iqr_el,
        "stall_phase_resultant_R": R_obs,
        "stall_phase_circular_SD_h": csd,
        "perm_p_phase_concentration": p_phase,
        "block_median_elapsed_spread_h": spread_obs,
        "perm_p_block_spread_this_small": p_block,
    }, stall


def probe2():
    df = load_long(sheet="Fig1C")
    allc = curves(df)
    fits = pd.read_csv("results/fit_fig1c.csv").set_index("plant")
    rows = []
    for key, (t, y) in allc.items():
        label = key.split("/")[1]
        peak = float(y.max())
        final = float(np.mean(y[-3:]))
        rows.append({"plant": label, "block": fits.loc[label, "block"],
                     "peak_deg": peak, "final_deg": final,
                     "overshoot_deg": peak - final,
                     "phi0_fit": float(fits.loc[label, "phi0"])})
    ov = pd.DataFrame(rows)
    corr = float(np.corrcoef(ov.phi0_fit, ov.final_deg)[0, 1])

    LO3 = fit_real.LO[:3]
    HI3 = fit_real.HI[:3]
    fixed = {}
    for phi_fix in (60.0, 75.0, 90.0):
        rmses = []
        for key, (t, y) in allc.items():
            te = t - t[0]
            x0 = np.array([1.0, 1.0, 30.0])

            def resid(x, pf=phi_fix):
                return fit_real.run_model(x[0], x[1], x[2], pf, te) - y

            res = least_squares(resid, x0, bounds=(LO3, HI3),
                                xtol=1e-6, ftol=1e-8)
            rmses.append(float(np.sqrt(np.mean(res.fun ** 2))))
        fixed[phi_fix] = {"median_rmse_deg": float(np.median(rmses)),
                          "max_rmse_deg": float(np.max(rmses))}
        print("fixed phi0=%g: median RMSE %.2f" % (phi_fix, np.median(rmses)),
              flush=True)

    return {
        "curves_overshoot_gt3deg": int((ov.overshoot_deg > 3).sum()),
        "curves_overshoot_gt5deg": int((ov.overshoot_deg > 5).sum()),
        "median_overshoot_deg": float(ov.overshoot_deg.median()),
        "max_overshoot_deg": float(ov.overshoot_deg.max()),
        "corr_phi0_vs_final_angle": corr,
        "phi0_fit_range": [float(ov.phi0_fit.min()), float(ov.phi0_fit.max())],
        "fixed_phi0_refits": {str(k): v for k, v in fixed.items()},
        "free_phi0_median_rmse_deg": 1.80,
    }, ov


def main():
    os.makedirs("results/figures", exist_ok=True)
    p1, stall = probe1()
    p2, ov = probe2()
    out = {"probe1_stall_locking": p1, "probe2_phi0_overshoot": p2}
    with open("results/probe_claude_summary.json", "w") as fh:
        json.dump(out, fh, indent=2)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6))
    fig.suptitle("BendLab probes: stall locking, overshoot, and the phi0 "
                 "plateau question")
    ax = axes[0]
    ax.scatter(stall.t_start, stall.stall_elapsed, s=28)
    ax.set_xlabel("stimulus onset (ZT, h)")
    ax.set_ylabel("stall time after onset (h)")
    ax.set_title("If stalls were clock-locked,\nthis would slope downward")
    ax = axes[1]
    bins = np.arange(0, max(12, ov.overshoot_deg.max() + 2), 2)
    ax.hist(ov.overshoot_deg, bins=bins, color="tab:orange")
    ax.axvline(3, color="red", ls="--", lw=1)
    ax.set_xlabel("peak minus final angle (deg)")
    ax.set_ylabel("curves")
    ax.set_title("Overshoot census (48 curves)")
    ax = axes[2]
    names = ["free\n(1.80)"] + ["phi0=%g" % float(k)
                                for k in p2["fixed_phi0_refits"]]
    vals = [1.80] + [v["median_rmse_deg"]
                     for v in p2["fixed_phi0_refits"].values()]
    ax.bar(names, vals, color=["tab:green"] + ["tab:grey"] * 3)
    ax.set_ylabel("median fit RMSE (deg)")
    ax.set_title("Harsh test: fixing the light angle for everyone")
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig("results/figures/probe_claude_dashboard.png", dpi=170)
    print(json.dumps(out, indent=2))
    print("saved results/figures/probe_claude_dashboard.png")


if __name__ == "__main__":
    main()
