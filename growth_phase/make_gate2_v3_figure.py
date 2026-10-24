"""Gate 2 v2 vs v3: does the covariate sampling design move the rates?

v2 sampled L0, intensity, and initial angle independently (angles
from clipped N(0, 5)); v3 resamples (L0, intensity, initial angle)
jointly from the 213 paired archive rows. Bars show, per scenario,
the fraction of simulated data sets in which the Phase C adoption
rule supported any M1 variant, split by sampling design.
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
v2 = json.loads((OUT / "phase_b_gate2_v2.json").read_text())["scenarios"]
v3 = json.loads((OUT / "phase_b_gate2_v3_pairedcov.json").read_text())["scenarios"]

order = ["M0:none", "M1a:alpha=0.2", "M1a:alpha=0.4", "M1a:alpha=0.8",
         "M1d:delta=0.3", "M1d:delta=0.6", "M1d:delta=1.0",
         "M1c:v=40 (c=0.025)", "M1c:v=20 (c=0.05)", "M1c:v=8 (c=0.125)"]
labels = [k.replace(":", "\n") for k in order]
r2 = [v2[k]["any_M1_supported"]["count"] / v2[k]["any_M1_supported"]["of"]
      for k in order]
r3 = [v3[k]["any_M1_supported"]["count"] / v3[k]["any_M1_supported"]["of"]
      for k in order]
x = np.arange(len(order)); w = 0.38
fig, ax = plt.subplots(figsize=(12, 4.4))
ax.bar(x - w / 2, r2, w, label="v2: independent covariates, N(0,5) angles")
ax.bar(x + w / 2, r3, w, label="v3: paired archive rows (joint)")
ax.set_xticks(x, labels, fontsize=7)
ax.set_ylabel("fraction of data sets with any M1 variant supported")
ax.set_title("Gate 2 adoption-rule support rates: covariate sampling "
             "moves exact rates,\nnot the conclusions (first bar pair "
             "is the null false-support rate)")
ax.legend(fontsize=8); ax.grid(axis="y", alpha=0.3); ax.set_ylim(0, 1.1)
fig.tight_layout()
fig.savefig(OUT / "fig_gate2_v3_comparison.png", dpi=150)
print("saved", OUT / "fig_gate2_v3_comparison.png")
