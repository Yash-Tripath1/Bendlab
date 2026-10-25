"""Phase D design figure: power curves for the early-rate test and
the latency (Cox) test, from the design simulations."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
E = pd.read_csv(OUT / "phase_d_power_early_rate.csv")
L = pd.read_csv(OUT / "phase_d_power_latency.csv")

fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
ax = axes[0]
styles = {"A_archive_joint": ("-", "o", "archive-like covariates"),
          "B_balanced_intensity": ("--", "s", "balanced intensity"),
          "C_wider_L0_range": (":", "^", "wider natural L0 range")}
for design, (ls, mk, lab) in styles.items():
    s = E[(E.design == design) & (E.beta_L_true == 1.06)]
    ax.plot(s.N, s.power_or_typeI, ls, marker=mk, label=f"{lab}")
s = E[(E.design == "A_archive_joint") & (E.beta_L_true == 2.12)]
ax.plot(s.N, s.power_or_typeI, "-", marker="x", color="grey",
        label="archive-like, pilot effect 2.12 (optimistic)")
ax.axhline(0.8, color="k", lw=0.8, alpha=0.5)
ax.axhline(0.05, color="r", lw=0.8, alpha=0.5)
ax.set_xlabel("plants enrolled")
ax.set_ylabel("power for beta_L (two-sided 0.05)")
ax.set_title("Primary early-rate test\n(prudent effect beta_L = 1.06 "
             "unless grey)")
ax.legend(fontsize=7); ax.grid(alpha=0.3); ax.set_ylim(0, 1.02)

ax = axes[1]
for scen, lab in [("HR1.42_pilot", "pilot HR 1.42"),
                  ("HR1.21_prudent", "prudent HR 1.21")]:
    s = L[L.scenario == scen]
    ax.plot(s.N_enrolled, s.power_or_typeI, "-o", label=lab)
null = L[L.scenario == "HR1.00_null"]
ax.plot(null.N_enrolled, null.power_or_typeI, "rx", ms=10,
        label="null HR 1.00 (type I, at N=213)")
ax.axhline(0.8, color="k", lw=0.8, alpha=0.5)
ax.axhline(0.05, color="r", lw=0.8, alpha=0.5)
ax.set_xlabel("plants enrolled (about 89% enter the at-risk set)")
ax.set_ylabel("power for log-L0 hazard ratio")
ax.set_title("Secondary latency test (Cox, at-risk plants)")
ax.legend(fontsize=7); ax.grid(alpha=0.3); ax.set_ylim(0, 1.02)
fig.tight_layout()
fig.savefig(OUT / "fig_phase_d_power.png", dpi=150)
print("saved", OUT / "fig_phase_d_power.png")
