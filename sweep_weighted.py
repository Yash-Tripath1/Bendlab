"""Weighted population sweep: the same experiment as sweep.py, but parameter vectors are
drawn from the region supported by measured sunflower fits rather than uniformly over the parameter box.

Population source: the clean fits in results/fit_fig1c.csv (parameter not
pinned at any bound; 44 plants from all six blocks ZT0-ZT16 after the
clock-corrected refit of 13 Oct). Only the four ZT9 plants pinned at the
tau lower bound are excluded. (The 12 Oct version of this population used
28 morning-only fits because a time-base bug in fit_real.py made every
ZT12/ZT16 fit pin tau at its upper bound; see RESULTS_ROUND0 bug log.)

Same regimes, features, clustering and degeneracy metric as sweep.py, same
seed rule. Run sweep.py first, or at least fit_real.py, so the inputs exist.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import features as F
from generate_plants import PARAM_NAMES, weighted_population
from sim import batch_simulate, batch_simulate_static
from sweep import T_END, FLIP_T, FLIP_DELTA, RECORD_DT, feature_frame, \
    degeneracy_report

SEED = 2  # declared, distinct from the uniform sweep's seed
N = 10_000
FIT_CSV = "results/fit_fig1c.csv"


def load_clean_fits(path: str = FIT_CSV) -> pd.DataFrame:
    fits = pd.read_csv(path)
    clean = fits[fits["at_bound"] == "[]"].copy()
    return clean


def main() -> None:
    clean = load_clean_fits()
    print("=== population source: clean fits ===")
    print("clean fits: %d/48 | blocks: %s"
          % (len(clean), sorted(clean["block"].unique())))
    print(clean.groupby("block")[list(PARAM_NAMES)].median().round(2).to_string())

    pop = weighted_population(N, SEED, clean)
    df = pd.DataFrame(pop, columns=PARAM_NAMES)
    df.insert(0, "plant_id", np.arange(N))
    print("\nweighted population parameter ranges (min..max):")
    for name in PARAM_NAMES:
        print("  %-9s %8.2f .. %8.2f" % (name, df[name].min(), df[name].max()))

    # Static light, same as the uniform sweep.
    t_s, th_s = batch_simulate_static(df["k"], df["tau"], df["max_rate"],
                                      df["phi0"], T_END, record_dt=RECORD_DT)
    static = feature_frame(t_s, th_s, df, "static_weighted")

    # Maximum-rate check: frequency with which the rate limit constrains trajectories in the empirically supported region
    obs_rate = np.abs(np.diff(th_s, axis=0)).max(axis=0) / (t_s[1] - t_s[0])
    binding = (obs_rate >= 0.99 * df["max_rate"].to_numpy()).mean()
    print("\nmaximum-rate limit constrains %.2f%% of weighted-population "
          "trajectories (uniform population: approximately 0.05%%)" % (100 * binding))

    # Flip regime, same protocol as the uniform sweep.
    def flip_light(t, phi0, flip_t=FLIP_T, delta=FLIP_DELTA):
        return phi0 + (delta if t >= flip_t else 0.0)

    t_f, th_f = batch_simulate(df["k"], df["tau"], df["max_rate"], df["phi0"],
                               flip_light, T_END, record_dt=RECORD_DT)
    flip = feature_frame(t_f, th_f, df, "flip_weighted")
    flip["reversal"] = th_f.max(axis=0) - th_f[-1]

    feat_cols = list(F.STATIC_FEATURES)
    cl, _ = degeneracy_report(static, feat_cols)
    print("\n=== behaviour clusters, weighted population, static light ===")
    print(cl.round(2).to_string(index=False))

    print("\n=== parameter-retention summary (weighted population) ===")
    for name in PARAM_NAMES:
        full = float(df[name].max() - df[name].min())
        print("%-9s median within-cluster IQR %.3f | weighted range %.3f "
              "| retains %.0f%%"
              % (name, cl[f"{name}_iqr"].median(), full,
                 100 * cl[f"{name}_iqr"].median() / full))

    print("\n=== comparison with the uniform population (sweep.py) ===")
    print("uniform retention: k 25% | tau 36% | max_rate 50% | phi0 25%")
    print("corr(final_angle, phi0), weighted = %.3f"
          % static["final_angle"].corr(static["param_phi0"]))
    print("median final_angle in the weighted population: %.2f deg"
          % static["final_angle"].median())

    pd.concat([static, flip], ignore_index=True).to_csv(
        "results/sweep_weighted_features.csv.gz", index=False,
        compression="gzip")
    cl.to_csv("results/sweep_weighted_clusters_static.csv", index=False)
    print("\nsaved results/sweep_weighted_features.csv.gz, "
          "results/sweep_weighted_clusters_static.csv")


if __name__ == "__main__":
    import os
    os.makedirs("results", exist_ok=True)
    main()
