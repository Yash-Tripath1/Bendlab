"""H5: assessment of the minimal model against measured stem-angle trajectories.

Fits (k, tau, max_rate, phi0) per plant against the PLOS S13 Fig1C data with
bounded least-squares (scipy least_squares), static light.

TIME BASE (corrected 13 Oct 2026). The Fig1C time column is headed ZT:
zeitgeber time, the plant's absolute clock, NOT time since the stimulus.
Each block was first exposed to the unilateral blue light at its own ZT
(ZT0 at lights-on, ZT16 at lights-off; Brooks et al. 2023, Fig 1C legend:
"stimulated with unidirectional blue light starting at different times of
day"). Every fit therefore runs on elapsed time, t - t_first, with the
model at rest (theta = 0, lamp just switched on) at the plant's first
timestamp. The first version of this script integrated with the lamp on
from ZT 0 and scored only from the first timestamp, so a ZT16 plant had
to explain 16 unobserved hours of bending that were not part of the
observed trajectory; the only available compensation was tau at its upper bound. That artifact produced the retracted round-0
claim that "static light fails by time of day" (20/48 fits pinned, all
ZT12/ZT16). On the corrected time base 4/48 fits touch a bound, all of
them ZT9 plants at the tau LOWER bound. See docs/RESULTS_ROUND0.md,
bug log, for the full retraction.

Verdict rule, stated before fitting:
  the model passes H5 for a block if the median per-plant RMSE is at or below
  the median across-plant standard deviation at matched timestamps, i.e. the
  model is wrong by less than plants differ from each other.

The spread measure is conservative in favour of the model because genuine
plant-to-plant differences are included in the denominator; consequently,
satisfying this criterion is a comparatively weak adequacy requirement.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from data_real import load_long

DT = 1.0 / 60.0  # one minute integration step

# Parameter bounds. These are sufficiently wide to contain plausible
# parameter values while preventing numerical overflow. The tau bound was
# increased from 12 to 48 h on 12 October after the initial analysis found
# 20/48 fits at the former upper bound. The time-base correction of
# 13 October showed that those boundary solutions arose from the timestamp
# error rather than from a requirement for a longer lag. The wider bounds
# are retained, and bound-pinned fits are excluded from the definition of
# the empirically supported parameter region.
LO = np.array([1e-3, 0.05, 0.5, 0.0])
HI = np.array([50.0, 48.0, 200.0, 130.0])
NAMES = ("k", "tau", "max_rate", "phi0")


def run_model(k: float, tau: float, max_rate: float, phi0: float,
              t_eval: np.ndarray) -> np.ndarray:
    """Integrate the two-state model under static light, report at t_eval.

    t_eval is ELAPSED time since stimulus onset: the model starts at rest
    at t_eval = 0 with the lamp just switched on. Callers holding absolute
    ZT timestamps must subtract the plant's first timestamp first (see the
    module docstring; passing raw ZT here was the 13 Oct bug).
    """
    t_end = float(t_eval[-1])
    n = int(round(t_end / DT))
    theta, r = 0.0, 0.0
    phi_rad = np.deg2rad(phi0)
    out = np.empty(len(t_eval))
    j = 0
    for i in range(n + 1):
        t = i * DT
        while j < len(t_eval) and t_eval[j] <= t + 1e-9:
            out[j] = theta
            j += 1
        r += (k * np.sin(phi_rad - np.deg2rad(theta)) - r) * (DT / tau)
        if r > max_rate:
            r = max_rate
        elif r < -max_rate:
            r = -max_rate
        theta += r * DT
    while j < len(t_eval):
        out[j] = theta
        j += 1
    return out


def fit_plant(t: np.ndarray, y: np.ndarray) -> dict:
    """Bounded least-squares fit of one curve.

    t may be absolute ZT timestamps; it is shifted to elapsed time since
    the plant's first timestamp (stimulus onset) before fitting.
    """
    t = np.asarray(t, float)
    t_start = float(t[0])
    t_elapsed = t - t_start
    phi_init = float(np.clip(np.median(y[-3:]), 10.0, 110.0))
    x0 = np.array([1.0, 1.0, 30.0, phi_init])

    def resid(x):
        return run_model(*x, t_elapsed) - y

    res = least_squares(resid, x0, bounds=(LO, HI), xtol=1e-6, ftol=1e-8)
    rmse = float(np.sqrt(np.mean(res.fun ** 2)))
    out = dict(zip(NAMES, res.x))
    out.update(rmse=rmse, n_pts=len(t), t_start=t_start,
               duration=float(t_elapsed[-1]),
               at_bound=str([NAMES[i] for i in range(4)
                             if res.x[i] <= LO[i] * 1.01 or res.x[i] >= HI[i] * 0.99]))
    return out


def plant_spread(df: pd.DataFrame) -> dict[str, float]:
    """Median across-plant SD at matched timestamps, per sheet/block."""
    out = {}
    for (sh, block), g in df.groupby(["sheet", "block"]):
        wide = g.pivot_table(index="t", columns="plant", values="angle")
        enough = wide.notna().sum(axis=1) >= 2
        sds = wide.std(axis=1)[enough].dropna()
        out[f"{sh}/{block}"] = float(np.median(sds)) if len(sds) else float("nan")
    return out


def main() -> None:
    df = load_long(sheet="Fig1C")
    spread = plant_spread(df)
    fits = []
    for plant, g in df.groupby("plant"):
        g = g.sort_values("t")
        f = fit_plant(g["t"].to_numpy(float), g["angle"].to_numpy(float))
        f["plant"] = plant
        f["block"] = str(plant).split("-")[0]
        f["spread"] = spread.get(f"Fig1C/{f['block']}", np.nan)
        fits.append(f)
    fits = pd.DataFrame(fits)

    print("=== per-block summary (Fig1C, PLOS S13) ===")
    summ = fits.groupby("block").agg(
        n=("plant", "count"),
        rmse_med=("rmse", "median"),
        spread=("spread", "first"),
        k_med=("k", "median"),
        tau_med=("tau", "median"),
        m_med=("max_rate", "median"),
        phi_med=("phi0", "median"),
    )
    summ["rmse/spread"] = summ["rmse_med"] / summ["spread"]
    summ["H5_pass"] = summ["rmse_med"] <= summ["spread"]
    print(summ.round(2).to_string())
    print("\noverall: median RMSE %.2f deg | median spread %.2f deg | ratio %.2f"
          % (fits["rmse"].median(), fits["spread"].median(),
             fits["rmse"].median() / fits["spread"].median()))
    print("H5 criterion: %d/%d groups satisfy median RMSE <= across-plant spread"
          % (int(summ["H5_pass"].sum()), len(summ)))
    nb = (fits["at_bound"] != "[]").sum()
    print("fits with a parameter at an optimisation bound: %d/%d" % (nb, len(fits)))
    fits.to_csv("results/fit_fig1c.csv", index=False)
    print("saved results/fit_fig1c.csv")


def degeneracy_check() -> None:
    """Two degeneracy probes on ZT0-1.

    1. Fix tau on a grid, refit the rest: if RMSE barely moves, (k, tau) is a
       sloppy direction — the curve cannot tell them apart individually.
    2. Check whether the fitted rate ever touches max_rate: if not, any cap
       above the realised peak rate is behaviourally identical, an exact
       degenerate direction.
    """
    df = load_long(sheet="Fig1C")
    g = df[df["plant"] == "ZT0-1"].sort_values("t")
    t, y = g["t"].to_numpy(float), g["angle"].to_numpy(float)
    t = t - t[0]  # convert timestamps to elapsed time since stimulus onset

    print("\n=== degeneracy check, plant ZT0-1 ===")
    print(" tau fixed |    k  | max_rate |  phi0  |   RMSE")
    base_rmse = None
    for tau_fix in (0.25, 0.5, 1.0, 2.0, 4.0):
        # tau is held out of the free vector; least_squares needs lo < hi
        lo = np.array([LO[0], LO[2], LO[3]])
        hi = np.array([HI[0], HI[2], HI[3]])

        def resid(xf, tau_fix=tau_fix):
            return run_model(xf[0], tau_fix, xf[1], xf[2], t) - y

        res = least_squares(resid, [1.0 * tau_fix, 30.0, 55.0],
                            bounds=(lo, hi), xtol=1e-6, ftol=1e-8)
        rmse = float(np.sqrt(np.mean(res.fun ** 2)))
        if base_rmse is None:
            base_rmse = rmse
        print(f" {tau_fix:9.2f} | {res.x[0]:5.2f} | {res.x[1]:8.2f} "
              f"| {res.x[2]:6.2f} | {rmse:6.3f}")
    print("(The variation in RMSE across this tau grid measures practical parameter sloppiness.)")

    f = fit_plant(t, y)
    th = run_model(f["k"], f["tau"], 1e9, f["phi0"], t)  # cap removed
    print("\nMaximum-rate check: RMSE with fitted max_rate = %.3f; with the limit removed = %.3f"
          % (f["rmse"], float(np.sqrt(np.mean((th - y) ** 2)))))
    print("Interpretation: equality of these values indicates that max_rate "
          "is unidentifiable from this trajectory when it exceeds the "
          "maximum realised bend rate.")


if __name__ == "__main__":
    import os
    os.makedirs("results", exist_ok=True)
    main()
    degeneracy_check()
