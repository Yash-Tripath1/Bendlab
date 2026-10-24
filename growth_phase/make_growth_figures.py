"""Summary figure for the growth-aware phase (Phases B and C)."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
B = json.loads((OUT / "phase_b_identifiability.json").read_text())
C = json.loads((OUT / "phase_c_results.json").read_text())

fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
# Phase B confusion at N=213
mechs = ["M0", "M1a", "M1c", "M1d"]
conf = np.array([[B["N213"]["confusion"][g][c] for c in mechs] for g in mechs], float)
conf = conf / conf.sum(axis=1, keepdims=True)
ax = axes[0]
x = np.arange(4); w = 0.2
for j, c in enumerate(mechs):
    ax.bar(x + (j - 1.5) * w, conf[:, j], w, label=f"pick {c}")
ax.set_xticks(x, [f"true {g}" for g in mechs])
ax.set_ylabel("fraction selected")
ax.set_title("Phase B: selection at N=213 (tip + L0)")
ax.legend(fontsize=7); ax.grid(axis="y", alpha=0.3)
# M2 fingerprint
ax = axes[1]
fp = B["M2_fingerprint"]
ax.bar(["growth-\ngenerated\n(M2)", "gain-modulated\n(M1a)"],
       [fp["corr_thetaFinal_vs_elongation_M2"], fp["corr_thetaFinal_vs_elongation_M1a"]],
       color=["#4C72B0", "#DD8452"])
ax.set_ylabel("corr(final bend, elongation)")
ax.set_title("M2 fingerprint in simulation")
ax.grid(axis="y", alpha=0.3)
# Phase C associations
ax = axes[2]
names = ["latency10_h", "rate02", "angle8", "plateau1621", "total_change"]
labels = ["latency\nto 10 deg", "early rate\n0-2 h", "angle\nat 8 h", "plateau\n16-21 h", "total\nchange"]
coefs = [C["associations"][n]["coef_logL0"] for n in names]
los = [C["associations"][n]["coef_logL0"] - C["associations"][n]["ci95"][0] for n in names]
his = [C["associations"][n]["ci95"][1] - C["associations"][n]["coef_logL0"] for n in names]
ax.errorbar(coefs, range(len(names)), xerr=[los, his], fmt="o", capsize=3)
ax.axvline(0, color="k", lw=1)
ax.set_yticks(range(len(names)), labels, fontsize=8)
ax.set_xlabel("coefficient per log L0 (95% CI)")
ax.set_title("Phase C: L0 associations (n=213)")
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "fig_growth_summary.png", dpi=150)
print("saved", OUT / "fig_growth_summary.png")
