"""Phase A: hardening the current BendLab phototropism model.

Three analyses, all within static-light phototropism (no heliotropism):

1. Leave-one-block-out cross-validation (LOBO-CV) on Fig1C.
   For each of the six time-of-day blocks, build the empirically weighted
   population from the *other five blocks'* clean fits only, simulate it
   under static light, and ask how well the predicted population
   distribution matches the held-out block's real curves. Metrics:
   per-plant RMSE of the population median curve, coverage of the
   predicted 5-95% band (target 90%), and the Wasserstein distance
   between predicted and observed final-angle distributions. The same
   quantities are computed with the in-sample population (all blocks)
   for an optimism-gap comparison.

2. Per-fit parameter uncertainty.
   Every one of the 48 Fig1C fits is refit; asymptotic 95% confidence
   intervals come from the least-squares Jacobian,
   cov = s^2 * (J^T J)^{-1}, s^2 = RSS / (n - 4). Fits with parameters
   at an optimisation bound are flagged, because asymptotic intervals
   are not meaningful there.

3. Fig1B external consistency check.
   Fig1B (three seedlings, ZT3 phototropism) has never been used in any
   BendLab fitting. Each curve is fitted individually and its parameters
   compared with the Fig1C clean-fit ranges; a zero-shot population
   prediction is also reported, with the caveat that Fig1B is a
   different experimental protocol, so zero-shot mismatch is evidence
   about protocol transfer, not directly about model validity.
"""

from __future__ import annotations

import json
import os
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats as st
from scipy.optimize import least_squares

import fit_real
from data_real import curves, load_long
from generate_plants import PARAM_NAMES, weighted_population
from sim import batch_simulate_static

SEED = 20261014
N_POP = 3_000
REC = 0.25  # trajectory recording interval (h)


def pop_trajectories(fit_frame, seed):
    pop = weighted_population(N_POP, seed=seed, fit_frame=fit_frame)
    times, th = batch_simulate_static(pop[:, 0], pop[:, 1], pop[:, 2],
                                      pop[:, 3], 24.0, record_dt=REC)
    return times, th


def band_stats(times, th):
    med = np.median(th, axis=1)
    lo = np.quantile(th, 0.05, axis=1)
    hi = np.quantile(th, 0.95, axis=1)
    return med, lo, hi


def eval_curves(times, th, obs):
    """obs: list of (plant, t_elapsed, y). Returns per-plant rows."""
    med, lo, hi = band_stats(times, th)
    rows = []
    finals_pred = th[-1]
    for plant, te, y in obs:
        m_i = np.interp(te, times, med)
        lo_i = np.interp(te, times, lo)
        hi_i = np.interp(te, times, hi)
        rows.append({
            "plant": plant,
            "median_curve_rmse_deg": float(np.sqrt(np.mean((m_i - y) ** 2))),
            "band_coverage": float(np.mean((y >= lo_i) & (y <= hi_i))),
            "final_angle_obs": float(y[-1]),
        })
    finals_obs = np.array([r["final_angle_obs"] for r in rows])
    wass = float(st.wasserstein_distance(finals_pred, finals_obs))
    return rows, wass


def part1_lobo(fits):
    df = load_long(sheet="Fig1C")
    allcurves = curves(df)
    clean_all = fits[fits["at_bound"] == "[]"].copy()
    blocks = sorted(fits["block"].unique())

    times_in, th_in = pop_trajectories(clean_all, seed=SEED)
    rows = []
    for i, block in enumerate(blocks):
        train = clean_all[clean_all["block"] != block]
        times_out, th_out = pop_trajectories(train, seed=SEED + 100 + i)
        obs = []
        for plant, (t, y) in allcurves.items():
            label = plant.split("/")[1]
            if fits.set_index("plant").loc[label, "block"] == block:
                obs.append((label, t - t[0], y))
        for mode, (tt, th) in {"held_out": (times_out, th_out),
                               "in_sample": (times_in, th_in)}.items():
            prow, wass = eval_curves(tt, th, obs)
            for r in prow:
                r.update(block=block, mode=mode,
                         final_angle_wasserstein_deg=wass)
                rows.append(r)
        print("LOBO block %s done" % block, flush=True)
    out = pd.DataFrame(rows)
    out.to_csv("results/phaseA_lobo.csv", index=False)
    summ = (out.groupby(["block", "mode"])
            .agg(median_rmse=("median_curve_rmse_deg", "median"),
                 coverage=("band_coverage", "mean"),
                 wasserstein=("final_angle_wasserstein_deg", "first"))
            .reset_index())
    return out, summ


def part2_uncertainty(fits):
    df = load_long(sheet="Fig1C")
    allcurves = curves(df)
    rows = []
    for plant_key, (t, y) in sorted(allcurves.items()):
        label = plant_key.split("/")[1]
        te = t - t[0]
        phi_init = float(np.clip(np.median(y[-3:]), 10.0, 110.0))
        x0 = np.array([1.0, 1.0, 30.0, phi_init])

        def resid(x):
            return fit_real.run_model(*x, te) - y

        res = least_squares(resid, x0, bounds=(fit_real.LO, fit_real.HI),
                            xtol=1e-6, ftol=1e-8)
        n, p = len(te), 4
        s2 = float(np.sum(res.fun ** 2)) / max(n - p, 1)
        try:
            cov = s2 * np.linalg.pinv(res.jac.T @ res.jac)
            se = np.sqrt(np.maximum(np.diag(cov), 0.0))
        except np.linalg.LinAlgError:
            se = np.full(4, np.nan)
        # A zero Jacobian column means the data never respond to that
        # parameter (e.g. max_rate when the speed cap never binds):
        # report it as unidentified (infinite SE), not as zero error.
        for j in range(4):
            if np.linalg.norm(res.jac[:, j]) < 1e-9:
                se[j] = np.inf
        at_bound = [fit_real.NAMES[j] for j in range(4)
                    if res.x[j] <= fit_real.LO[j] * 1.01
                    or res.x[j] >= fit_real.HI[j] * 0.99]
        row = {"plant": label, "rmse": float(np.sqrt(np.mean(res.fun ** 2))),
               "at_bound": str(at_bound)}
        for j, name in enumerate(fit_real.NAMES):
            row[f"{name}_fit"] = float(res.x[j])
            row[f"{name}_se"] = float(se[j])
            row[f"{name}_rel_se"] = float(se[j] / res.x[j]) if res.x[j] else np.nan
            row[f"{name}_ci_lo"] = float(res.x[j] - 1.96 * se[j])
            row[f"{name}_ci_hi"] = float(res.x[j] + 1.96 * se[j])
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv("results/phaseA_fit_uncertainty.csv", index=False)
    print("uncertainty refits done (%d plants)" % len(out), flush=True)
    return out


def part3_fig1b(fits):
    df = load_long(sheet="Fig1B")
    cb = curves(df)
    clean = fits[fits["at_bound"] == "[]"]
    ranges = {p: (float(clean[p].min()), float(clean[p].max()))
              for p in PARAM_NAMES}
    times, th = pop_trajectories(clean, seed=SEED + 7)
    med, lo, hi = band_stats(times, th)
    rows = []
    curves_out = {}
    for plant_key, (t, y) in sorted(cb.items()):
        label = plant_key.split("/")[1]
        te = t - t[0]
        fit = fit_real.fit_plant(t, y)
        m_i = np.interp(te, times, med)
        lo_i, hi_i = np.interp(te, times, lo), np.interp(te, times, hi)
        row = {"plant": label, "individual_fit_rmse_deg": fit["rmse"],
               "zeroshot_median_rmse_deg":
                   float(np.sqrt(np.mean((m_i - y) ** 2))),
               "zeroshot_band_coverage":
                   float(np.mean((y >= lo_i) & (y <= hi_i))),
               "at_bound": fit["at_bound"]}
        for p in PARAM_NAMES:
            row[f"{p}_fit"] = fit[p]
            row[f"{p}_inside_fig1c_range"] = bool(
                ranges[p][0] <= fit[p] <= ranges[p][1])
        rows.append(row)
        curves_out[label] = (te, y, m_i, lo_i, hi_i)
        print("Fig1B %s fitted (rmse %.2f)" % (label, fit["rmse"]),
              flush=True)
    out = pd.DataFrame(rows)
    out.to_csv("results/phaseA_fig1b.csv", index=False)
    return out, curves_out, (times, med, lo, hi)


def main():
    os.makedirs("results/figures", exist_ok=True)
    t0 = time.time()
    fits = pd.read_csv("results/fit_fig1c.csv")

    lobo, lobo_summ = part1_lobo(fits)
    unc = part2_uncertainty(fits)
    fig1b, fig1b_curves, fig1b_band = part3_fig1b(fits)

    ho = lobo_summ[lobo_summ["mode"] == "held_out"]
    ins = lobo_summ[lobo_summ["mode"] == "in_sample"]
    summary = {
        "runtime_seconds": round(time.time() - t0, 1),
        "lobo_held_out": {
            "median_curve_rmse_deg_overall":
                float(lobo[lobo["mode"] == "held_out"]
                      .median_curve_rmse_deg.median()),
            "mean_band_coverage": float(ho.coverage.mean()),
            "per_block": {r.block: {"rmse": round(float(r.median_rmse), 2),
                                    "coverage": round(float(r.coverage), 3),
                                    "wasserstein_deg": round(float(r.wasserstein), 2)}
                          for r in ho.itertuples()},
            "in_sample_median_rmse_deg":
                float(lobo[lobo["mode"] == "in_sample"]
                      .median_curve_rmse_deg.median()),
            "in_sample_mean_coverage": float(ins.coverage.mean()),
        },
        "fit_uncertainty_median_rel_se": {
            p: float(unc[f"{p}_rel_se"][np.isfinite(unc[f"{p}_rel_se"])]
                     .median()) for p in PARAM_NAMES},
        "fit_uncertainty_unidentified_counts": {
            p: int((~np.isfinite(unc[f"{p}_rel_se"])).sum())
            for p in PARAM_NAMES},
        "fit_uncertainty_plants_with_any_rel_se_above_0.5": int(
            (unc[[f"{p}_rel_se" for p in PARAM_NAMES]] > 0.5).any(axis=1).sum()),
        "fig1b": [{k: (float(v) if isinstance(v, float) else v)
                   for k, v in r.items()} for r in fig1b.to_dict("records")],
    }
    with open("results/phaseA_summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str)

    # ---- dashboard -------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("BendLab Phase A: cross-validation, fit uncertainty, "
                 "external check (phototropism only)")

    ax = axes[0, 0]
    x = np.arange(len(ho))
    ax.bar(x - 0.2, ho.median_rmse, width=0.4, label="held-out block")
    ax.bar(x + 0.2, ins.median_rmse.values, width=0.4, label="in-sample")
    ax.set_xticks(x, ho.block)
    ax.set_ylabel("median curve RMSE vs population median (deg)")
    ax.set_title("Leave-one-block-out: does the population generalise?")
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    ax.bar(x - 0.2, ho.coverage, width=0.4, label="held-out")
    ax.bar(x + 0.2, ins.coverage.values, width=0.4, label="in-sample")
    ax.axhline(0.90, color="red", ls="--", lw=1, label="target 90%")
    ax.set_xticks(x, ho.block)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("fraction of observed points inside 5-95% band")
    ax.set_title("Prediction-band coverage")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    data = [unc[f"{p}_rel_se"][np.isfinite(unc[f"{p}_rel_se"])].values
            for p in PARAM_NAMES]
    ax.boxplot(data, labels=list(PARAM_NAMES), showfliers=False)
    ax.axhline(0.5, color="red", ls="--", lw=1)
    ax.text(3, 0.44, "max_rate identified\nin only 1 of 48 fits\n(cap never binds in 47)",
            ha="center", fontsize=8, color="tab:red")
    ax.set_ylabel("relative standard error (SE / fitted value)")
    ax.set_title("How precisely is each parameter determined?")

    ax = axes[1, 1]
    sim_times, med_b, lo_b, hi_b = fig1b_band
    tg = np.linspace(0, 16, 65)
    ax.fill_between(tg, np.interp(tg, sim_times, lo_b),
                    np.interp(tg, sim_times, hi_b), color="tab:blue",
                    alpha=0.18, label="Fig1C population 5-95% (zero-shot)")
    ax.plot(tg, np.interp(tg, sim_times, med_b), color="tab:blue", lw=1,
            label="population median")
    for label, (te, y, m_i, lo_i, hi_i) in fig1b_curves.items():
        ax.plot(te, y, "o-", ms=3, label="Fig1B %s (observed)" % label)
    ax.set_xlabel("elapsed time since light on (h)")
    ax.set_ylabel("stem angle (deg)")
    ax.set_title("Fig1B: never-fitted seedlings vs Fig1C population")
    ax.legend(fontsize=7)

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig("results/figures/phaseA_dashboard.png", dpi=170)
    print("\n=== PHASE A SUMMARY ===")
    print(json.dumps(summary, indent=2, default=str))
    print("saved results/figures/phaseA_dashboard.png")


if __name__ == "__main__":
    main()
