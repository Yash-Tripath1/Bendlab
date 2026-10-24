"""ZT9 diagnostic analysis: origin of the lower-bound lag estimates in four of six ZT9 plants.

Declared before running (13 Oct 2026), three questions, three verdicts:

  A. Residual shape. Where, in elapsed time, does the fitted curve miss
     the ZT9 measurements? Systematic = same-sign segment residuals in
     at least 5 of 6 plants.
  B. Lower-bound sensitivity. Refit ZT9 with the tau lower bound at
     0.05 (current), 0.01 and 0.001 h, everything else identical.
     Verdict rule: if the 0.001 h floor cuts median RMSE by >= 30% and
     no refit then pins another bound, the lower bound is the main
     driver. A cut under 10% means the bound is not the driver.
     Between the two: partial.
  C. Stall alignment (descriptive only; no causal interpretation). A curve
     is classified as stalled if its 2.5 h-smoothed bend rate reaches a minimum
     in elapsed 3-20 h (a window every curve covers) and then
     re-accelerates by >= 1 deg/h within 8 h. Do stall timings line up
     better across blocks in ELAPSED hours, or in circadian PHASE
     (absolute ZT mod 24)? Compared via the spread of block medians.
     (A first pass without the re-acceleration rule and common window
     was discarded: it mostly detected end-of-observation slowdown.)

Outputs: results/zt9_residuals.csv, results/zt9_tau_sensitivity.csv,
results/zt9_stall_times.csv, results/figures/zt9_diagnostic_dashboard.png
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import least_squares

from data_real import load_long
from fit_real import run_model, LO, HI, NAMES

FITS = pd.read_csv("results/fit_fig1c.csv").set_index("plant")
DF = load_long(sheet="Fig1C")
SEGMENTS = [(0, 1), (1, 4), (4, 8), (8, 16), (16, 99)]
TAU_FLOORS = [0.05, 0.01, 0.001]


def curve_of(plant):
    g = DF[DF["plant"] == plant].sort_values("t")
    t_abs = g["t"].to_numpy(float)
    return t_abs, t_abs - t_abs[0], g["angle"].to_numpy(float)


def fitted(plant, t_elapsed):
    fr = FITS.loc[plant]
    return run_model(fr.k, fr.tau, fr.max_rate, fr.phi0, t_elapsed)


# --------------------------------------------------------------- A. residuals
res_rows, resid_curves = [], {}
for plant in [p for p in FITS.index if p.startswith("ZT9-")]:
    t_abs, t_el, y = curve_of(plant)
    resid = y - fitted(plant, t_el)
    resid_curves[plant] = (t_el, resid, y)
    row = {"plant": plant, "rmse_saved": float(FITS.loc[plant, "rmse"]),
           "max_abs_resid": float(np.abs(resid).max()),
           "angle_1h": float(y[np.argmin(abs(t_el - 1))]),
           "angle_2h": float(y[np.argmin(abs(t_el - 2))])}
    for a, b in SEGMENTS:
        m = (t_el >= a) & (t_el < b)
        row[f"resid_{a}_{b if b < 90 else 'end'}"] = float(resid[m].mean())
    res_rows.append(row)
resid_df = pd.DataFrame(res_rows)
resid_df.to_csv("results/zt9_residuals.csv", index=False)
seg_cols = [c for c in resid_df if c.startswith("resid_")]
print("=== A. ZT9 segment residuals (measured - fitted, deg) ===")
print(resid_df[["plant", "rmse_saved", "angle_1h"] + seg_cols].round(2)
      .to_string(index=False))
same_sign = {c: int((np.sign(resid_df[c]) == np.sign(resid_df[c].median())).sum())
             for c in seg_cols}
print("plants sharing the median sign, per segment:", same_sign)

# ------------------------------------------------------ B. tau-floor refits
def refit(t_el, y, tau_lo):
    lo, hi = LO.copy(), HI.copy()
    lo[1] = tau_lo
    phi_init = float(np.clip(np.median(y[-3:]), 10.0, 110.0))
    res = least_squares(lambda x: run_model(*x, t_el) - y,
                        [1.0, 1.0, 30.0, phi_init], bounds=(lo, hi),
                        xtol=1e-6, ftol=1e-8)
    pinned = [NAMES[i] for i in range(4)
              if res.x[i] <= lo[i] * 1.01 or res.x[i] >= hi[i] * 0.99]
    return res.x, float(np.sqrt(np.mean(res.fun ** 2))), pinned


sens_rows = []
for plant, (t_abs, t_el, y) in [(p, curve_of(p)) for p in resid_curves]:
    for floor in TAU_FLOORS:
        x, rmse, pinned = refit(t_el, y, floor)
        sens_rows.append({"plant": plant, "tau_floor": floor,
                          "k": x[0], "tau": x[1], "max_rate": x[2],
                          "phi0": x[3], "rmse": rmse,
                          "at_bound": str(pinned)})
sens = pd.DataFrame(sens_rows)
sens.to_csv("results/zt9_tau_sensitivity.csv", index=False)
print("\n=== B. sensitivity to the tau lower bound (median RMSE over six ZT9 plants) ===")
print(sens.groupby("tau_floor")["rmse"].agg(["median", "max"]).round(3)
      .to_string())
print(sens[sens.tau_floor == 0.001][["plant", "k", "tau", "max_rate",
                                    "phi0", "rmse", "at_bound"]]
      .round(3).to_string(index=False))

# ---------------------------------------------------------- C. stall timing
def stall_time(t_el, y):
    """Identify an operationally defined stall in a stem-angle trajectory.

    The criterion is a minimum in the smoothed bend rate within elapsed
    3-20 h followed by re-acceleration of at least 1 deg/h within 8 h. The
    common observation window excludes terminal slowing near the end of
    the recording. Returns (stall_elapsed, min_rate, rebound), or NaN
    values when the re-acceleration criterion is not met.
    """
    if len(y) < 20:
        return np.nan, np.nan, np.nan
    smooth = np.convolve(y, np.ones(5) / 5, "valid")
    t_s = t_el[2:-2]
    rate = np.diff(smooth) / np.diff(t_s)
    t_r = 0.5 * (t_s[1:] + t_s[:-1])
    win = (t_r >= 3.0) & (t_r <= 20.0)
    if not win.any():
        return np.nan, np.nan, np.nan
    idx = np.flatnonzero(win)
    k = idx[int(np.argmin(rate[win]))]
    later = rate[(t_r > t_r[k]) & (t_r <= t_r[k] + 8.0)]
    rebound = float(later.max() - rate[k]) if len(later) else 0.0
    if rebound < 1.0:
        return np.nan, np.nan, np.nan
    return float(t_r[k]), float(rate[k]), rebound


stall_rows = []
for plant in FITS.index:
    t_abs, t_el, y = curve_of(plant)
    st, rmin, rebound = stall_time(t_el, y)
    stall_rows.append({"plant": plant, "block": plant.split("-")[0],
                       "t_start": float(t_abs[0]), "stall_elapsed": st,
                       "stall_ZT": float(t_abs[0]) + st if st == st else np.nan,
                       "stall_phase": (float(t_abs[0]) + st) % 24.0
                       if st == st else np.nan,
                       "min_rate": rmin, "rebound_deg_h": rebound})
stall_all = pd.DataFrame(stall_rows)
stall = stall_all.dropna(subset=["stall_elapsed"])
stall_all.to_csv("results/zt9_stall_times.csv", index=False)
print("\ncurves satisfying the stall criterion (of 48): %d" % len(stall))
med = stall.groupby("block")[["stall_elapsed", "stall_phase"]].median()
print("\n=== C. stall timing, block medians (stalling plants only) ===")
print(med.round(2).to_string())
print("spread of block medians: elapsed IQR %.2f h | circadian-phase "
      "IQR %.2f h"
      % (med["stall_elapsed"].quantile(.75) - med["stall_elapsed"].quantile(.25),
         med["stall_phase"].quantile(.75) - med["stall_phase"].quantile(.25)))
print(stall[stall["block"] == "ZT9"][["plant", "stall_elapsed",
      "stall_phase", "min_rate", "rebound_deg_h"]].round(2).to_string(index=False))

# ------------------------------------------------------------------- figure
fig, ax = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle("ZT9 diagnostic analysis: residuals, lower-bound sensitivity "
             "and stall timing (13 October 2026)", fontsize=13, weight="bold")

for plant, (t_el, resid, y) in resid_curves.items():
    ax[0, 0].plot(t_el, y, lw=1.2, alpha=.8)
ax[0, 0].set_title("1. ZT9 measured curves (elapsed time)", fontsize=11)
ax[0, 0].set_xlabel("hours since stimulus onset"); ax[0, 0].set_ylabel("stem angle (deg)")

for plant, (t_el, resid, y) in resid_curves.items():
    ax[0, 1].plot(t_el, resid, lw=1.2, alpha=.8, label=plant)
ax[0, 1].axhline(0, color="k", lw=.8)
ax[0, 1].set_title("2. Residuals: measured − fitted", fontsize=11)
ax[0, 1].set_xlabel("hours since stimulus onset"); ax[0, 1].set_ylabel("deg")
ax[0, 1].legend(fontsize=7, ncol=2)

piv = sens.pivot(index="plant", columns="tau_floor", values="rmse")
for plant in piv.index:
    ax[0, 2].plot([str(c) for c in piv.columns], piv.loc[plant], "o-", alpha=.7)
ax[0, 2].plot([str(c) for c in piv.columns], piv.median(), "k--", lw=2, label="median")
ax[0, 2].set_title("3. Sensitivity of fit error to the tau lower bound", fontsize=11)
ax[0, 2].set_xlabel("tau lower bound (h)"); ax[0, 2].set_ylabel("fit RMSE (deg)")
ax[0, 2].legend(fontsize=8)

seg_labels = [c.replace("resid_", "") for c in seg_cols]
for _, r in resid_df.iterrows():
    ax[1, 0].plot(seg_labels, [r[c] for c in seg_cols], "o-", alpha=.7)
ax[1, 0].axhline(0, color="k", lw=.8)
ax[1, 0].set_title("4. Mean residual by segment, per plant", fontsize=11)
ax[1, 0].set_xlabel("elapsed segment (h)"); ax[1, 0].set_ylabel("deg")

ax[1, 1].scatter(stall["stall_elapsed"], stall["stall_phase"],
                 c=stall["block"].astype("category").cat.codes, cmap="tab10", s=28)
for b, g in stall.groupby("block"):
    ax[1, 1].annotate(b, (g["stall_elapsed"].median(), g["stall_phase"].median()),
                      fontsize=9, weight="bold")
ax[1, 1].axhline(16, color="red", ls="--", lw=1)
ax[1, 1].set_title("5. Stall timing in elapsed time and circadian phase\n(red line: ZT16)", fontsize=11)
ax[1, 1].set_xlabel("hours since onset"); ax[1, 1].set_ylabel("ZT phase (h, mod 24)")

zt9only = sens[sens.tau_floor.isin([0.05, 0.001])]
ax[1, 2].bar(["standard lower bound\n0.05 h", "lower bound\n0.001 h"],
             [zt9only[zt9only.tau_floor == f]["rmse"].median() for f in (0.05, 0.001)],
             color=["tab:orange", "tab:green"], width=.5)
ax[1, 2].set_title("6. Median ZT9 RMSE by tau lower bound", fontsize=11)
ax[1, 2].set_ylabel("deg")

fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig("results/figures/zt9_diagnostic_dashboard.png", dpi=140)
print("\nsaved results/figures/zt9_diagnostic_dashboard.png")
