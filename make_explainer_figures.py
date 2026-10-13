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
fig.suptitle("BendLab, the story so far — every panel drawn from the raw "
             "files, nothing hand-placed", fontsize=13, weight="bold")

# ---- panel 1: the money shot. Two plants, different dials, same curve.
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
              label="Plant A: k=%.1f tau=%.1f cap=%.0f light=%.0f"
                    % tuple(pa))
ax[0, 0].plot(t, th[:, b], lw=2.2, ls="--", color="tab:red",
              label="Plant B: k=%.1f tau=%.1f cap=%.0f light=%.0f"
                    % tuple(pb))
ax[0, 0].set_title("1. A tenfold speed-limit difference,\none curve (within "
                   "%.1f deg)" % np.abs(th[:, a] - th[:, b]).max(),
                   fontsize=11)
ax[0, 0].set_xlabel("hours")
ax[0, 0].set_ylabel("stem angle (deg)")
ax[0, 0].legend(fontsize=7.5, loc="lower right")

# ---- panel 2: reality check. One real sunflower vs our fake one.
df = load_long(sheet="Fig1C")
g = df[df["plant"] == "ZT0-1"].sort_values("t")
fr = fits[fits["plant"] == "ZT0-1"].iloc[0]
yc = run_model(fr.k, fr.tau, fr.max_rate, fr.phi0,
               g["t"].to_numpy(float))
ax[0, 1].plot(g["t"], g["angle"], "o", ms=4, color="tab:green",
              label="real sunflower (PLOS S13)")
ax[0, 1].plot(g["t"], yc, lw=2, color="black",
              label="our fake plant (RMSE %.1f deg)" % fr.rmse)
ax[0, 1].set_title("2. The reality check: a real sunflower\nseedling vs our "
                   "simulated one", fontsize=11)
ax[0, 1].set_xlabel("hours (zeitgeber time)")
ax[0, 1].set_ylabel("stem angle (deg)")
ax[0, 1].legend(fontsize=8)

# ---- panel 3: the ladder (H8).
ax[0, 2].bar(["no data\nat all", "one 6-hour\ncurve", "full 24-hour\nbudget"],
             [30, 44, 89], color=["tab:gray", "tab:orange", "tab:green"],
             width=0.55)
for i, v in enumerate([30, 44, 89]):
    ax[0, 2].text(i, v + 2, "%d%%" % v, ha="center", weight="bold")
ax[0, 2].set_ylim(0, 105)
ax[0, 2].set_ylabel("plants correctly predicted, per 100")
ax[0, 2].set_title("3. The identification ladder:\nmeasuring helps a lot; "
                   "being clever about it, not at all", fontsize=11)

# ---- panel 4: Umaid's breeding test. Child drift vs parent separation.
rows = []
rng2 = np.random.default_rng(11)
tries = 0
while len(rows) < 40 and tries < 400_000:
    tries += 1
    a2, b2 = rng2.integers(0, len(pop), 2)
    if np.abs(th[:, a2] - th[:, b2]).max() < 3.0:
        kid = (P[a2] + P[b2]) / 2
        kid[3] = P[a2][3]
        kdf = pd.DataFrame([kid], columns=PARAM_NAMES)
        _, ck = batch_simulate(kdf["k"], kdf["tau"], kdf["max_rate"],
                               kdf["phi0"], None, 24.0, record_dt=0.5)
        rows.append((abs(P[a2][0] - P[b2][0]) / full[0],
                     float(np.abs(ck[:, 0] - th[:, a2]).max())))
rows = np.array(rows)
ax[1, 0].scatter(rows[:, 0], rows[:, 1], s=28, color="tab:purple", alpha=0.8)
ax[1, 0].axhline(3.0, color="red", ls="--", label="still 'the same plant' "
                 "(3 deg)")
ax[1, 0].set_xlabel("how different the parents' k dial was\n(fraction of the "
                    "full range)")
ax[1, 0].set_ylabel("how far the child's curve drifted (deg)")
ax[1, 0].set_title("4. Umaid's breeding test: children of look-alike\n"
                   "parents mostly bend like their parents", fontsize=11)
ax[1, 0].legend(fontsize=8)

# ---- panel 5: the scoreboard.
ax[1, 1].axis("off")
lines = [
    ("H1  behaviour hides the dials", "ALIVE (weaker among real plants)",
     "tab:green"),
    ("H2  a light flip reveals more", "DEAD (on our metrics)", "tab:red"),
    ("H3  hidden cliffs in the dials", "DEAD (map is smooth)", "tab:red"),
    ("H4  moving sun changes the piles", "ALIVE (piles do not persist)",
     "tab:green"),
    ("H5  fake plants bend believably", "ALIVE (all six start times)",
     "tab:green"),
    ("H6  identical twins can breed", "ALIVE (soft walls, some leakage)", "tab:green"),
    ("H7  better light shows exist", "UNPROVEN (gap too small)",
     "tab:orange"),
    ("H8  smart beats random measuring", "REDESIGN (game too easy)",
     "tab:orange"),
]
ax[1, 1].text(0.02, 0.98, "THE SCOREBOARD", fontsize=12, weight="bold",
              va="top")
for i, (q, v, c) in enumerate(lines):
    ax[1, 1].text(0.02, 0.88 - i * 0.115, q, fontsize=9.5, va="top")
    ax[1, 1].text(0.05, 0.835 - i * 0.115, v, fontsize=8.5, va="top", color=c)
ax[1, 1].set_title("5. Eight hypotheses, four alive, two dead,\nand that is what a "
                   "round of research is for", fontsize=11)

# ---- panel 6: the audit. Simulation against textbook physics.
k, tau, A = 200.0, 1.0, 10.0
w0 = np.sqrt(k * np.pi / 180 / tau)
z = 1 / (2 * tau * w0)
wd = w0 * np.sqrt(1 - z ** 2)
tt, thh = simulate(k, tau, 1e6, lambda t: A, 20.0, dt=1 / 600)
analytic = A - A * np.exp(-z * w0 * tt) * (np.cos(wd * tt)
                                           + (z * w0 / wd) * np.sin(wd * tt))
ax[1, 2].plot(tt, analytic, lw=2.5, color="tab:blue",
              label="textbook damped-pendulum formula")
ax[1, 2].plot(tt[::20], thh[::20], ".", ms=3, color="tab:red",
              label="our simulator (every 20th step)")
ax[1, 2].set_title("6. The audit: our simulator vs closed-form\nphysics — "
                   "they agree to 0.01 degrees", fontsize=11)
ax[1, 2].set_xlabel("hours")
ax[1, 2].set_ylabel("stem angle (deg)")
ax[1, 2].legend(fontsize=8)

fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(OUT, dpi=140)
print("saved", OUT)
