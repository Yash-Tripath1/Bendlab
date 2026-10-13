"""Run the REAL seedlings through the simulator.

The 48 published sunflower seedlings (PLOS S13) enter the simulator as the
dial sets fitted in H5 (results/fit_fig1c.csv). Only the 44 plants whose fit
did not ride a bound are trusted with predictions under new light regimes;
the other 4 (all ZT9, tau at its lower bound) are shown as raw curves but
not extrapolated. (Before the 13 Oct time-base correction in fit_real.py
the trusted set was 28 morning plants and every ZT12/ZT16 plant was
excluded; that exclusion was a clock artifact and is retracted.)

Protocols are copied verbatim from round1.py so this is the same light menu
the synthetic plants saw. Outputs:

  results/real_seedling_protocols.csv
  results/figures/real_seedlings_dashboard.png
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data_real import load_long
from fit_real import run_model
from sim import batch_simulate

FITS = "results/fit_fig1c.csv"
OUT_CSV = "results/real_seedling_protocols.csv"
OUT_PNG = "results/figures/real_seedlings_dashboard.png"
RECORD_DT = 0.5

# ---- light regimes, verbatim from round1.py -------------------------------
def light_static(t, p0):
    return p0

def light_flip4(t, p0):
    return p0 + (45.0 if t >= 4.0 else 0.0)

def light_flip12(t, p0):
    return p0 + (45.0 if t >= 12.0 else 0.0)

def light_sweep12(t, p0):
    return p0 + 45.0 * (2.0 * ((t % 12.0) / 12.0) - 1.0)

def light_dflip16(t, p0):
    return p0 + (45.0 if 6.0 <= t < 14.0 else 0.0)

def light_ramp24(t, p0):
    return p0 - 30.0 + 60.0 * (t / 24.0)

PROTOCOLS = {
    "static6":   (6.0, light_static),
    "flip4_8":   (8.0, light_flip4),
    "flip12_14": (14.0, light_flip12),
    "sweep12":   (12.0, light_sweep12),
    "dflip16":   (16.0, light_dflip16),
    "ramp24":    (24.0, light_ramp24),
}

# ---- import the real seedlings ---------------------------------------------
raw = load_long()
plants = sorted(raw["plant"].unique())
fits = pd.read_csv(FITS).set_index("plant")
clean = fits[fits["at_bound"] == "[]"]
print("imported %d real seedlings; %d with trustworthy dials"
      % (len(plants), len(clean)))
print("blocks:", raw.groupby("block")["plant"].nunique().to_dict())

MORNING = {"ZT0": "tab:green", "ZT3": "seagreen", "ZT6": "limegreen",
           "ZT9": "darkolivegreen"}
AFTERNOON = {"ZT12": "tab:orange", "ZT16": "tab:red"}

def color_of(block):
    return MORNING.get(block, AFTERNOON.get(block, "gray"))

# ---- run every protocol for the trustworthy seedlings ----------------------
rows = []
curves_by_proto = {}
for name, (dur, fn) in PROTOCOLS.items():
    t, th = batch_simulate(clean["k"], clean["tau"], clean["max_rate"],
                           clean["phi0"], fn, dur, record_dt=RECORD_DT)
    curves_by_proto[name] = (t, th)
    for j, plant in enumerate(clean.index):
        c = th[:, j]
        rate = np.gradient(c, t)
        half = t[np.argmax(c >= 0.5 * c[-1])] if c[-1] > 0 else np.nan
        rows.append({"plant": plant, "block": plant.split("-")[0],
                     "protocol": name, "final_angle": c[-1],
                     "peak_angle": c.max(), "peak_rate": rate.max(),
                     "half_rise_time": half})
frame = pd.DataFrame(rows)
frame.to_csv(OUT_CSV, index=False)
print("wrote %s (%d rows)" % (OUT_CSV, len(frame)))

# ---- dashboard --------------------------------------------------------------
fig, ax = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle("All %d real seedlings in the published file, %d trusted with "
             "predictions" % (len(plants), len(clean)),
             fontsize=13, weight="bold")

# 1: raw import
for plant in plants:
    g = raw[raw["plant"] == plant].sort_values("t")
    b = plant.split("-")[0]
    ax[0, 0].plot(g["t"], g["angle"], lw=1.1, alpha=0.8, color=color_of(b))
ax[0, 0].set_title("1. The raw import: every measured curve;\nZT blocks "
                   "coloured, mutant/depleted sheets grey", fontsize=11)
ax[0, 0].set_xlabel("hours")
ax[0, 0].set_ylabel("stem angle (deg)")

# 2: anchor, real vs its dial set under the fitted condition
g = raw[raw["plant"] == "ZT0-1"].sort_values("t")
fr = fits.loc["ZT0-1"]
yc = run_model(fr.k, fr.tau, fr.max_rate, fr.phi0, g["t"].to_numpy(float))
ax[1, 1].plot(g["t"], g["angle"], "o", ms=4, color="tab:green",
              label="measured")
ax[1, 1].plot(g["t"], yc, "k", lw=2, label="its imported dial set")
ax[1, 1].set_title("2. Anchor: seedling ZT0-1 and the dial set\nthat "
                   "travels with it (RMSE %.1f deg)" % fr.rmse, fontsize=11)
ax[1, 1].set_xlabel("hours")
ax[1, 1].legend(fontsize=8)

# 3-5: predictions under new light
for (r, ccol), name in zip([(0, 1), (0, 2), (1, 0)],
                           ["flip4_8", "sweep12", "dflip16"]):
    t, th = curves_by_proto[name]
    for j, plant in enumerate(clean.index):
        ax[r, ccol].plot(t, th[:, j], lw=0.9, alpha=0.55,
                         color=color_of(plant.split("-")[0]))
    med = np.median(th, axis=1)
    ax[r, ccol].plot(t, med, "k--", lw=2, label="median")
    ax[r, ccol].set_title(
        "PREDICTION under %s\n(same %d seedlings, brand-new light)"
        % (name, len(clean)), fontsize=11)
    ax[r, ccol].set_xlabel("hours")
    ax[r, ccol].set_ylabel("stem angle (deg)")
    ax[r, ccol].legend(fontsize=8)

# 6: do they separate?
f = frame[frame["protocol"] == "flip4_8"]
for b in sorted(f["block"].unique()):
    m = f[f["block"] == b]
    ax[1, 2].scatter(m["final_angle"], m["peak_rate"], s=34,
                     color=color_of(b), label=b, alpha=0.85)
ax[1, 2].set_xlabel("final angle under the flip (deg)")
ax[1, 2].set_ylabel("peak bend rate (deg/h)")
ax[1, 2].set_title("6. Behaviour space under new light:\nseedlings from all "
                   "six start times, one spread", fontsize=11)
ax[1, 2].legend(fontsize=7, ncol=2)

fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(OUT_PNG, dpi=140)
print("saved", OUT_PNG)

# ---- quick read-out ----------------------------------------------------------
for name in ["flip4_8", "sweep12", "dflip16", "ramp24"]:
    s = frame[frame["protocol"] == name]
    print("%-9s final angle: median %5.1f, spread %5.1f deg"
          % (name, s.final_angle.median(),
             s.final_angle.quantile(0.9) - s.final_angle.quantile(0.1)))
