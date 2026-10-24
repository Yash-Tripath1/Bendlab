"""Plots for Phase B0 Workstream A (run after the benchmark script).
Reads outputs/*.csv and the archive CSV; fits one all-data wrapper of each
kind for the mean-trajectory overlay. Writes PNGs into outputs/."""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from phase_b0_kempinski_benchmark import (  # noqa: E402
    DATA, OUT, fit_wrapper, load_plants, predict_wrapper)

df, plants = load_plants(DATA)
idx = list(range(len(plants)))

# --- Figure 1: observed mean trajectories vs all-data W1 prediction
m1 = fit_wrapper(idx, plants, "fixed90")
p1 = predict_wrapper(m1, idx, plants)
m2 = fit_wrapper(idx, plants, "phi_of_I")
p2 = predict_wrapper(m2, idx, plants)
print("all-data W1:", {k: round(v, 3) for k, v in m1.items()
                       if k != "phi_params"}, m1["phi_params"])
print("all-data W2:", {k: round(v, 3) for k, v in m2.items()
                       if k != "phi_params"}, m2["phi_params"])
np.save(os.path.join(OUT, "all_data_W1_params.npy"),
        np.array([m1["a"], m1["b"], m1["tau"], m1["max_rate"]]))
np.save(os.path.join(OUT, "all_data_W2_params.npy"),
        np.array([m2["a"], m2["b"], m2["tau"], m2["max_rate"],
                  m2["phi_params"][0], m2["phi_params"][1]]))

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
for ax, pred, title in ((axes[0], p1, "W1: BendLab + k(I)=aI^b, phi=90 deg"),
                        (axes[1], p2, "W2 diagnostic: phi_eff(I) also fitted")):
    for I, g in df.groupby("light_i"):
        gm = g.groupby("dt")["theta"].agg(["mean", "std", "count"])
        ax.plot(gm.index, gm["mean"], lw=1.2, alpha=0.55)
        sub = [p for p in plants if p["I"] == I]
        tref = sub[0]["t"]
        mat = np.array([np.interp(tref, p["t"], pred[p["id"]]) for p in sub])
        ax.plot(tref, mat.mean(axis=0), lw=2.0, alpha=0.9)
    ax.set_xlabel("time [h]"); ax.set_title(title, fontsize=10)
    ax.grid(alpha=0.3)
axes[0].set_ylabel("tip angle [deg]")
axes[0].text(0.98, 0.04, "thin: observed group mean\nthick: model mean",
             transform=axes[0].transAxes, ha="right", fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig1_mean_trajectories.png"), dpi=150); plt.close(fig)

# --- Figure 2: plant-held-out median RMSE by intensity
held = pd.read_csv(os.path.join(OUT, "plant_heldout_per_plant.csv"))
order = ["W1_bendlab_kI_phi90", "W2_bendlab_kI_phiI_diagnostic",
         "B1_group_mean_curve", "B2_saturating"]
labels = ["W1 BendLab\nphi=90", "W2 diagnostic\nphi_eff(I)", "B1 group\nmean curve", "B2 saturating\nexponential"]
tab = held.groupby(["model", "I"])["rmse_deg"].median().unstack(0)
x = np.arange(len(tab)); w = 0.2
fig, ax = plt.subplots(figsize=(9, 4.2))
for j, name in enumerate(order):
    ax.bar(x + (j - 1.5) * w, tab[name], w, label=labels[j])
ax.set_xticks(x, [f"{v:g}" for v in tab.index])
ax.set_xlabel("held-out plant intensity [W/m^2]"); ax.set_ylabel("median per-plant RMSE [deg]")
ax.set_title("Plant-held-out benchmark (5-fold, stratified by intensity)")
ax.legend(fontsize=7, ncol=4); ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig2_heldout_by_intensity.png"), dpi=150); plt.close(fig)

# --- Figure 3: LOIO median RMSE by held intensity
loio = pd.read_csv(os.path.join(OUT, "loio_per_plant.csv"))
tab = loio.groupby(["model", "I"])["rmse_deg"].median().unstack(0)
x = np.arange(len(tab))
fig, ax = plt.subplots(figsize=(9, 4.2))
for j, name in enumerate(order):
    if name in tab:
        ax.bar(x + (j - 1.5) * w, tab[name], w, label=labels[j])
ax.axvspan(-0.5, 0.5, color="grey", alpha=0.15)
ax.axvspan(len(tab) - 0.5, len(tab) - 0.5 + 1, color="grey", alpha=0.15)
ax.text(0, tab.max().max() * 1.02, "extrapolation", ha="center", fontsize=8)
ax.text(len(tab) - 1, tab.max().max() * 1.02, "extrapolation", ha="center", fontsize=8)
ax.set_xticks(x, [f"{v:g}" for v in tab.index])
ax.set_xlabel("entirely held-out intensity [W/m^2]"); ax.set_ylabel("median per-plant RMSE [deg]")
ax.set_title("Leave-one-intensity-group-out (held group untouched in fitting)")
ax.legend(fontsize=7, ncol=4); ax.grid(axis="y", alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig3_loio_by_intensity.png"), dpi=150); plt.close(fig)

# --- Figure 4: per-plant calibration vs population forecast; phi_free diag
cal = pd.read_csv(os.path.join(OUT, "per_plant_calibration.csv"))
diag = pd.read_csv(os.path.join(OUT, "per_plant_fullfit_diagnostic.csv"))
free = diag[diag["mode"] == "phi_free"]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
axes[0].hist(cal["rmse_forecast_4_22h_deg"], bins=25, color="#DD8452")
axes[0].axvline(cal["rmse_forecast_4_22h_deg"].median(), color="k", lw=1.5)
axes[0].set_xlabel("forecast RMSE 4-22 h [deg]"); axes[0].set_ylabel("plants")
axes[0].set_title("Per-plant calibration (fit 0-4 h, phi=90): forecast error")
for I, g in free.groupby("I"):
    axes[1].scatter(np.full(len(g), I) + np.random.default_rng(1).normal(0, 0.03, len(g)),
                    g["phi_fit_deg"], s=12, alpha=0.6)
axes[1].axhline(90, color="red", lw=1.5)
axes[1].text(5.8, 92, "known lamp geometry: 90 deg", ha="right", fontsize=8, color="red")
axes[1].set_xlabel("intensity [W/m^2]"); axes[1].set_ylabel("fitted phi_free [deg]")
axes[1].set_title("Full-curve per-plant fits: effective angle phi_free")
for ax in axes: ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig4_calibration_and_phi.png"), dpi=150); plt.close(fig)
print("plots saved to", OUT)
