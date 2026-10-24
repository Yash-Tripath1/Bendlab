"""Figure for Gate 2 v2: winner selection vs the Phase C adoption rule."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
df = pd.read_csv(OUT / "gate2_v2_replicates.csv")
S = json.loads((OUT / "phase_b_gate2_v2.json").read_text())["scenarios"]

fig, axes = plt.subplots(1, 2, figsize=(13, 4.6),
                         gridspec_kw={"width_ratios": [1, 2.2]})
# Panel A: under M0, winner-take-all vs adoption rule
ax = axes[0]
null = S["M0:none"]
cands = ["M0", "M1a", "M1c", "M1d"]
win = [null["winner_counts"][c] for c in cands]
sup = [0] + [null[f"supported_{m}"]["count"] for m in ["M1a", "M1c", "M1d"]]
x = np.arange(4); w = 0.38
ax.bar(x - w / 2, np.array(win) / null["n_datasets"], w,
       label="lowest CV RMSE (winner)")
ax.bar(x + w / 2, np.array(sup) / null["n_datasets"], w,
       label="supported (Phase C rule)")
ax.set_xticks(x, cands)
ax.set_ylabel("fraction of 24 null data sets")
ax.set_title("Under M0 (no length effect):\nselection cries wolf, adoption does not")
ax.legend(fontsize=7); ax.grid(axis="y", alpha=0.3); ax.set_ylim(0, 0.5)

# Panel B: per non-null scenario, correct-winner / true-support / wrong-support
ax = axes[1]
order = [("M1a", "alpha=0.2"), ("M1a", "alpha=0.4"), ("M1a", "alpha=0.8"),
         ("M1d", "delta=0.3"), ("M1d", "delta=0.6"), ("M1d", "delta=1.0"),
         ("M1c", "v=40 (c=0.025)"), ("M1c", "v=20 (c=0.05)"),
         ("M1c", "v=8 (c=0.125)")]
labels, correct_win, true_sup, wrong_sup = [], [], [], []
for gen, lab in order:
    sub = df[(df.generator == gen) & (df.effect_label == lab)]
    n = len(sub)
    labels.append(f"{gen}\n{lab}")
    correct_win.append((sub.winner_lowest_median_rmse == gen).mean())
    true_sup.append(sub[f"supported_{gen}"].mean())
    wrong = np.zeros(n, dtype=bool)
    for m in ["M1a", "M1c", "M1d"]:
        if m != gen:
            wrong |= sub[f"supported_{m}"].to_numpy()
    wrong_sup.append(wrong.mean())
x = np.arange(len(labels)); w = 0.27
ax.bar(x - w, correct_win, w, label="winner = true mechanism")
ax.bar(x, true_sup, w, label="true variant supported")
ax.bar(x + w, wrong_sup, w, label="a wrong variant supported")
ax.set_xticks(x, labels, fontsize=7)
ax.set_ylabel("fraction of 12 data sets")
ax.set_title("Across effect sizes: adoption is conservative and, for "
             "gain vs opposing,\nnot mechanism-specific (the mirror "
             "variant is also supported)")
ax.legend(fontsize=7); ax.grid(axis="y", alpha=0.3); ax.set_ylim(0, 1.12)
fig.tight_layout()
fig.savefig(OUT / "fig_gate2_v2.png", dpi=150)
print("saved", OUT / "fig_gate2_v2.png")
