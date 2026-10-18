"""Experimental-design power analysis for the BendLab stimulus models.

Question
--------
The vector-stimulus comparison (vector_stimulus.py, vector_batch.py) found
two-source light conditions where three candidate stimulus models --
physical vector sum, transduced-source vector sum (Kempinski et al. 2026),
and a circumference-integrated model -- predict visibly different bending.
This script asks the follow-up a real laboratory would need answered:

    If an experiment were run at those conditions, how many seedlings,
    measured with realistic angle noise, would be needed to tell the
    models apart with 80% statistical power?

Method
------
1.  Draw a population of 4,000 plants from the empirically weighted
    population (bootstrap resamples of the 44 clean real-seedling fits
    with pre-specified jitter), so plant-to-plant variability matches
    measured seedlings rather than an arbitrary parameter box.
2.  For each candidate two-source condition and each stimulus model,
    simulate the full 24 h BendLab trajectory once per plant.
3.  Define three readouts a laboratory could measure: stem angle at 2 h
    (early, direction-dominated), angle at 24 h (final), and the mean
    angle over 12/18/24 h (trajectory readout).
4.  Monte-Carlo power analysis: repeatedly draw n seedlings per group
    from the simulated distributions, add Gaussian measurement noise of
    sigma degrees to each observation, and run a Welch two-sample t-test
    between each pair of models. Power is the fraction of repetitions
    significant at p < 0.05. A 60-degree, equal-intensity control
    condition, where the models nearly agree, should give power near
    0.05 and validates the Monte-Carlo machinery.

Caution (added after external review): the Welch calculation measures
separation between simulated outcome distributions under two candidate
mechanisms. It is NOT the probability that a real experiment, analysed
with a model-selection procedure, would identify the correct mechanism,
because a laboratory observes one group of seedlings and must select
among models while also fitting their parameters. Sample sizes from
this script should be treated as an optimistic screening bound only.
A valid design study must simulate full datasets under each mechanism,
apply the actual planned selection procedure (with parameter-fitting
uncertainty and biological variation), and report the probability of
correct selection.
"""

from __future__ import annotations

import itertools
import json
import os
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from generate_plants import weighted_population
from vector_stimulus import MODELS, simulate_population, stimulus

SEED = 20261014
N_POP = 4_000
REPS = 2_000
N_GRID = [5, 10, 15, 20, 30, 40, 60]
SIGMA_GRID = [0.5, 1.0, 2.0, 3.0, 5.0]
rng = np.random.default_rng(SEED + 4242)

# (separation_deg, intensity_ratio): the strongest discriminators found by
# vector_batch.py, one mid-range condition, and one near-agreement control.
CONDITIONS = [
    (160.0, 2.0),
    (170.0, 1.5),
    (150.0, 2.5),
    (150.0, 3.0),
    (140.0, 3.0),
    (120.0, 2.0),
    (90.0, 2.0),
    (60.0, 1.0),   # control: models nearly agree
]
PAIRS = list(itertools.combinations(MODELS, 2))
READOUTS = ("early_2h", "final_24h", "traj_mean")


def welch_power(a, b, n, sigma):
    """Vectorised Monte-Carlo power of a Welch t-test between samples
    drawn (with replacement) from population arrays a and b."""
    ia = rng.integers(0, len(a), size=(REPS, n))
    ib = rng.integers(0, len(b), size=(REPS, n))
    xa = a[ia] + rng.normal(0.0, sigma, size=(REPS, n))
    xb = b[ib] + rng.normal(0.0, sigma, size=(REPS, n))
    m1, m2 = xa.mean(axis=1), xb.mean(axis=1)
    v1, v2 = xa.var(axis=1, ddof=1), xb.var(axis=1, ddof=1)
    se2 = v1 / n + v2 / n
    tstat = (m1 - m2) / np.sqrt(se2)
    df = se2 ** 2 / ((v1 / n) ** 2 / (n - 1) + (v2 / n) ** 2 / (n - 1))
    p = 2.0 * stats.t.sf(np.abs(tstat), df)
    return float((p < 0.05).mean())


def main():
    os.makedirs("results/figures", exist_ok=True)
    t0 = time.time()

    fits = pd.read_csv("results/fit_fig1c.csv")
    clean = fits[fits["at_bound"] == "[]"].copy()
    pop = weighted_population(N_POP, seed=SEED, fit_frame=clean)
    print("weighted population n=%d from %d clean fits" % (N_POP, len(clean)),
          flush=True)

    # ---- simulate every condition x model once --------------------------
    # readouts[condition][model][readout] -> per-plant array
    store = {}
    for sep, ratio in CONDITIONS:
        sources = [(-sep / 2.0, 1.0), (sep / 2.0, float(ratio))]
        store[(sep, ratio)] = {}
        for model in MODELS:
            phi, g = stimulus(sources, model)
            n_steps = int(round(24.0 / (1.0 / 60.0)))
            phi_s = np.full(n_steps + 1, phi)
            g_s = np.full(n_steps + 1, g)
            times, th = simulate_population(pop, phi_s, g_s, record_dt=0.5)
            store[(sep, ratio)][model] = {
                "early_2h": th[4],                    # t = 2 h
                "final_24h": th[-1],                  # t = 24 h
                "traj_mean": th[[24, 36, 48]].mean(axis=0),  # 12/18/24 h
            }
        print("simulated sep=%.0f ratio=%.2f (%.1fs)"
              % (sep, ratio, time.time() - t0), flush=True)

    # ---- Monte-Carlo power analysis -------------------------------------
    rows = []
    for (sep, ratio) in CONDITIONS:
        for readout in READOUTS:
            dists = {m: store[(sep, ratio)][m][readout] for m in MODELS}
            for m1, m2 in PAIRS:
                a, b = dists[m1], dists[m2]
                pooled = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2.0)
                d = abs(a.mean() - b.mean()) / pooled if pooled > 0 else 0.0
                for sigma in SIGMA_GRID:
                    for n in N_GRID:
                        rows.append({
                            "separation_deg": sep, "intensity_ratio": ratio,
                            "readout": readout, "model_a": m1, "model_b": m2,
                            "cohens_d_noiseless": d,
                            "sigma_deg": sigma, "n_per_group": n,
                            "power": welch_power(a, b, n, sigma),
                        })
        print("power analysis sep=%.0f ratio=%.2f done (%.1fs)"
              % (sep, ratio, time.time() - t0), flush=True)

    power = pd.DataFrame(rows)
    power.to_csv("results/exp_design_power.csv", index=False)

    # ---- minimum n for 80% power (final-angle readout) ------------------
    rec_rows = []
    fin = power[power.readout == "final_24h"]
    for (sep, ratio, m1, m2, sigma), grp in fin.groupby(
            ["separation_deg", "intensity_ratio", "model_a", "model_b",
             "sigma_deg"]):
        hit = grp[grp.power >= 0.80].n_per_group.min()
        rec_rows.append({
            "separation_deg": sep, "intensity_ratio": ratio,
            "model_a": m1, "model_b": m2, "sigma_deg": sigma,
            "min_n_for_80pct_power": (None if pd.isna(hit) else int(hit)),
            "power_at_n60": float(grp[grp.n_per_group == 60].power.iloc[0]),
        })
    rec = pd.DataFrame(rec_rows)
    rec.to_csv("results/exp_design_recommendations.csv", index=False)

    ctrl = fin[(fin.separation_deg == 60.0) & (fin.sigma_deg == 2.0)
               & (fin.n_per_group == 20)]
    best = rec[(rec.separation_deg == 160.0) & (rec.intensity_ratio == 2.0)
               & (rec.sigma_deg == 2.0)]
    summary = {
        "n_population": N_POP, "repetitions_per_cell": REPS,
        "runtime_seconds": round(time.time() - t0, 1),
        "control_power_at_alpha_should_be_near_0.05": {
            "%s vs %s" % (r.model_a, r.model_b): round(float(r.power), 3)
            for r in ctrl.itertuples()},
        "best_condition_160deg_ratio2_min_n_sigma2": {
            "%s vs %s" % (r.model_a, r.model_b):
                r.min_n_for_80pct_power for r in best.itertuples()},
    }
    with open("results/exp_design_summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    # ---- dashboard -------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("BendLab experimental design: telling the stimulus models "
                 "apart (weighted population, n=%d plants)" % N_POP)

    ax = axes[0, 0]
    sub = fin[(fin.separation_deg == 160.0) & (fin.intensity_ratio == 2.0)
              & (fin.sigma_deg == 2.0)]
    for (m1, m2), grp in sub.groupby(["model_a", "model_b"]):
        ax.plot(grp.n_per_group, grp.power, "o-",
                label="%s vs %s" % (m1, m2))
    ax.axhline(0.80, color="grey", ls="--", lw=1)
    ax.axhline(0.05, color="red", ls=":", lw=1)
    ax.set_xlabel("seedlings per group (n)")
    ax.set_ylabel("power (final angle, noise sigma = 2 deg)")
    ax.set_title("Best condition: 160 deg separation, 2:1 ratio")
    ax.legend(fontsize=7)

    ax = axes[0, 1]
    piv = best.set_index(["model_a", "model_b"]) if False else None
    r2 = rec[rec.sigma_deg == 2.0]
    conds = ["%g/%g" % (s, r) for s, r in CONDITIONS]
    mat = np.full((len(CONDITIONS), len(PAIRS)), np.nan)
    for i, (sep, ratio) in enumerate(CONDITIONS):
        for j, (m1, m2) in enumerate(PAIRS):
            sel = r2[(r2.separation_deg == sep)
                     & (r2.intensity_ratio == ratio)
                     & (r2.model_a == m1) & (r2.model_b == m2)]
            if len(sel) and pd.notna(sel.min_n_for_80pct_power.iloc[0]):
                mat[i, j] = sel.min_n_for_80pct_power.iloc[0]
    im = ax.imshow(np.where(np.isnan(mat), 70, mat), cmap="viridis_r",
                   vmin=5, vmax=70)
    ax.set_xticks(range(len(PAIRS)),
                  ["%s\nvs %s" % (a.replace("_source", ""), b.replace("_source", ""))
                   for a, b in PAIRS], fontsize=6)
    ax.set_yticks(range(len(conds)), conds, fontsize=8)
    ax.set_ylabel("separation / ratio")
    ax.set_title("Min n for 80% power (dark = >60), sigma=2 deg", fontsize=10)
    for i in range(len(CONDITIONS)):
        for j in range(len(PAIRS)):
            if not np.isnan(mat[i, j]):
                ax.text(j, i, "%d" % mat[i, j], ha="center", va="center",
                        color="white", fontsize=8)
    fig.colorbar(im, ax=ax, shrink=0.85, label="n per group")

    ax = axes[1, 0]
    sub = fin[(fin.separation_deg == 160.0) & (fin.intensity_ratio == 2.0)
              & (fin.n_per_group == 20)]
    for (m1, m2), grp in sub.groupby(["model_a", "model_b"]):
        ax.plot(grp.sigma_deg, grp.power, "o-", label="%s vs %s" % (m1, m2))
    ax.axhline(0.80, color="grey", ls="--", lw=1)
    ax.set_xlabel("measurement noise sigma (deg)")
    ax.set_ylabel("power at n = 20 per group")
    ax.set_title("Robustness to measurement noise (160 deg, 2:1)")
    ax.legend(fontsize=7)

    ax = axes[1, 1]
    sub = power[(power.sigma_deg == 2.0) & (power.n_per_group == 20)]
    labels = {"early_2h": "angle at 2 h", "final_24h": "angle at 24 h",
              "traj_mean": "mean 12/18/24 h"}
    x = np.arange(len(CONDITIONS))
    for k, readout in enumerate(READOUTS):
        vals = []
        for sep, ratio in CONDITIONS:
            s = sub[(sub.separation_deg == sep)
                    & (sub.intensity_ratio == ratio)
                    & (sub.readout == readout)]
            vals.append(s.power.min())  # hardest pair governs
        ax.bar(x + (k - 1) * 0.27, vals, width=0.27, label=labels[readout])
    ax.axhline(0.80, color="grey", ls="--", lw=1)
    ax.set_xticks(x, conds, rotation=30, fontsize=7)
    ax.set_ylabel("power of hardest model pair (n=20, sigma=2 deg)")
    ax.set_title("Which readout separates all three models?")
    ax.legend(fontsize=7)

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig("results/figures/exp_design_dashboard.png", dpi=170)
    print("\n=== EXP DESIGN SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print("saved results/figures/exp_design_dashboard.png")


if __name__ == "__main__":
    main()
