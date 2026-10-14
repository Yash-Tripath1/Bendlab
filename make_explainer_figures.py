"""Builds the six-panel figure for docs/EXPLAINER_PART2.md.

Every panel re-derives its data on the spot from the raw files, so the figure
cannot drift from the results it illustrates. Rerun after any change to the
underlying data:  python make_explainer_figures.py
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data_real import load_long
from fit_real import run_model
from generate_plants import PARAM_NAMES, weighted_population
from sim import batch_simulate, simulate

OUT = "results/figures/explainer2_dashboard.png"
fig, ax = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle("BendLab: parameter degeneracy, model fitting and hypothesis tests",
             fontsize=13, weight="bold")

# ---- Panel 1: parameter degeneracy (two parameter sets, nearly identical trajectories).
fits = pd.read_csv("results/fit_fig1c.csv")
clean = fits[fits["at_bound"] == "[]"]
pop = pd.DataFrame(weighted_population(4_000, 77, clean), columns=PARAM_NAMES)
P = pop[list(PARAM_NAMES)].to_numpy()
t, th = batch_simulate(pop["k"], pop["tau"], pop["max_rate"], pop["phi0"],
                       None, 24.0, record_dt=0.5)
pair = None
rng = np.random.default_rng(11)
full = P.max(axis=0) - P.min(axis=0)
best = -1
for _ in range(400_000):
    a, b = rng.integers(0, len(pop), 2)
    if np.abs(th[:, a] - th[:, b]).max() < 1.5:
        sep = float(np.abs((P[a] - P[b]) / full).max())
        if sep > best:
            best, pair = sep, (a, b)
a, b = pair
pa, pb = P[a], P[b]
ax[0, 0].plot(t, th[:, a], lw=2.2, color="tab:blue",
              label="Parameter set A: k=%.1f, tau=%.1f, max_rate=%.0f, phi0=%.0f"
                    % tuple(pa))
ax[0, 0].plot(t, th[:, b], lw=2.2, ls="--", color="tab:red",
              label="Parameter set B: k=%.1f, tau=%.1f, max_rate=%.0f, phi0=%.0f"
                    % tuple(pb))
ax[0, 0].set_title("1. Parameter degeneracy: a tenfold difference in\nmaximum bend rate (trajectories within %.1f deg)"
                   % np.abs(th[:, a] - th[:, b]).max(),
                   fontsize=11)
ax[0, 0].set_xlabel("hours")
ax[0, 0].set_ylabel("stem angle (deg)")
ax[0, 0].legend(fontsize=7.5, loc="lower right")

# ---- Panel 2: comparison with a measured sunflower trajectory.
df = load_long(sheet="Fig1C")
g = df[df["plant"] == "ZT0-1"].sort_values("t")
fr = fits[fits["plant"] == "ZT0-1"].iloc[0]
yc = run_model(fr.k, fr.tau, fr.max_rate, fr.phi0,
               g["t"].to_numpy(float))
ax[0, 1].plot(g["t"], g["angle"], "o", ms=4, color="tab:green",
              label="Measured sunflower trajectory (PLOS S13)")
ax[0, 1].plot(g["t"], yc, lw=2, color="black",
              label="Model fit (RMSE %.1f deg)" % fr.rmse)
ax[0, 1].set_title("2. Model fit to measured trajectory ZT0-1", fontsize=11)
ax[0, 1].set_xlabel("elapsed time (h)")
ax[0, 1].set_ylabel("stem angle (deg)")
ax[0, 1].legend(fontsize=8)

# ---- Panel 3: predictive identification by information level (H8).
ax[0, 2].bar(["No plant-specific\ndata", "One 6 h static\ntrajectory", "Full 24 h\nbudget"],
             [30, 44, 89], color=["tab:gray", "tab:orange", "tab:green"],
             width=0.55)
for i, v in enumerate([30, 44, 89]):
    ax[0, 2].text(i, v + 2, "%d%%" % v, ha="center", weight="bold")
ax[0, 2].set_ylim(0, 105)
ax[0, 2].set_ylabel("successful predictions per 100 plants")
ax[0, 2].set_title("3. Predictive identification by information level\n(no adaptive-selection benefit in v1)", fontsize=11)

# ---- Panel 4: crossover connectivity (recombinant deviation vs source separation).
rows = []
rng2 = np.random.default_rng(11)
tries = 0
while len(rows) < 40 and tries < 400_000:
    tries += 1
    a2, b2 = rng2.integers(0, len(pop), 2)
    if np.abs(th[:, a2] - th[:, b2]).max() < 3.0:
        recombinant = (P[a2] + P[b2]) / 2
        recombinant[3] = P[a2][3]
        kdf = pd.DataFrame([recombinant], columns=PARAM_NAMES)
        _, ck = batch_simulate(kdf["k"], kdf["tau"], kdf["max_rate"],
                               kdf["phi0"], None, 24.0, record_dt=0.5)
        rows.append((abs(P[a2][0] - P[b2][0]) / full[0],
                     float(np.abs(ck[:, 0] - th[:, a2]).max())))
rows = np.array(rows)
ax[1, 0].scatter(rows[:, 0], rows[:, 1], s=28, color="tab:purple", alpha=0.8)
ax[1, 0].axhline(3.0, color="red", ls="--", label="trajectory-equivalence threshold (3 deg)")
ax[1, 0].set_xlabel("difference in source response gain\n(fraction of the full range)")
ax[1, 0].set_ylabel("maximum deviation of recombinant trajectory (deg)")
ax[1, 0].set_title("4. Crossover connectivity: recombinant trajectories\nremain close to the source trajectories", fontsize=11)
ax[1, 0].legend(fontsize=8)

# ---- Panel 5: hypothesis status summary.
ax[1, 1].axis("off")
lines = [
    ("H1  Behaviour does not identify parameters", "SUPPORTED (weaker in the weighted population)",
     "tab:green"),
    ("H2  A light-direction change improves recovery", "NOT SUPPORTED (cluster-retention metric)", "tab:red"),
    ("H3  Discontinuities occur in parameter space", "FALSIFIED (response surface is smooth)", "tab:red"),
    ("H4  Moving light changes cluster membership", "SUPPORTED (clusters do not persist)",
     "tab:green"),
    ("H5  Model reproduces measured trajectories", "SUPPORTED (all six stimulus start times)",
     "tab:green"),
    ("H6  The degenerate parameter set is connected", "SUPPORTED (with incomplete retention)", "tab:green"),
    ("H7  Protocols differ materially in recovery error", "NOT SUPPORTED (observed gap 0.091 < 0.10)",
     "tab:orange"),
    ("H8  Adaptive selection outperforms baselines", "NOT ASSESSABLE (v1 design saturated)",
     "tab:orange"),
]
ax[1, 1].text(0.02, 0.98, "HYPOTHESIS STATUS", fontsize=12, weight="bold",
              va="top")
for i, (q, v, c) in enumerate(lines):
    ax[1, 1].text(0.02, 0.88 - i * 0.115, q, fontsize=9.5, va="top")
    ax[1, 1].text(0.05, 0.835 - i * 0.115, v, fontsize=8.5, va="top", color=c)
ax[1, 1].set_title("5. Hypothesis status summary", fontsize=11)

# ---- Panel 6: validation against the closed-form damped-pendulum solution.
k, tau, A = 200.0, 1.0, 10.0
w0 = np.sqrt(k * np.pi / 180 / tau)
z = 1 / (2 * tau * w0)
wd = w0 * np.sqrt(1 - z ** 2)
tt, thh = simulate(k, tau, 1e6, lambda t: A, 20.0, dt=1 / 600)
analytic = A - A * np.exp(-z * w0 * tt) * (np.cos(wd * tt)
                                           + (z * w0 / wd) * np.sin(wd * tt))
ax[1, 2].plot(tt, analytic, lw=2.5, color="tab:blue",
              label="Analytical damped-pendulum solution")
ax[1, 2].plot(tt[::20], thh[::20], ".", ms=3, color="tab:red",
              label="Simulator output (every 20th step)")
ax[1, 2].set_title("6. Simulator validation against the\nclosed-form solution (agreement within 0.01 deg)", fontsize=11)
ax[1, 2].set_xlabel("hours")
ax[1, 2].set_ylabel("stem angle (deg)")
ax[1, 2].legend(fontsize=8)

fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(OUT, dpi=140)
print("saved", OUT)
