"""Gate 2 v3 (post-audit sensitivity): paired-covariate resampling.

Gate 2 v2 (phase_b_gate2_v2.py) sampled L0 and light intensity
independently from their marginal distributions and drew initial
angles from clipped N(0, 5). The archive covariates are not
independent and do not match that angle distribution: in the 213
paired plants, intensity groups account for about 8.4% of L0
variance, and initial angles have mean about 1.35 deg, SD about
6.80 deg, with about 10.8% already at or above 10 deg (the v2 angle
distribution has SD about 4.98 deg and about 2.3% at or above
10 deg). This script repeats the Gate 2 v2 design exactly (same
scenarios, replicates, candidates, 5-fold adoption rule, seeds
stream otherwise) with ONE change: each simulated plant's
(L0, intensity, initial angle) triple is resampled jointly from the
213 paired archive rows, preserving the empirical covariate joint
distribution. It tests whether the v2 rates are artefacts of the
independent-sampling assumption.

All other machinery (generators, observation process, candidate
fitting, adoption rule) is imported unchanged from
phase_b_gate2_v2.py. Master seed 20261025 (v2 used 20261024, so the
random streams differ; comparisons are of rates, not paired data
sets).

Outputs: outputs/gate2_v3_pairedcov_replicates.csv,
         outputs/phase_b_gate2_v3_pairedcov.json
Runtime: several minutes.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from phase_b_gate2_v2 import SCENARIOS, run_dataset, wilson, CANDS, M1S

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"


def main():
    paired = pd.read_csv(HERE / "outputs" / "paired_plants.csv")
    paired = paired[paired.has_length].reset_index(drop=True)
    L0_pool = paired["L0_mm"].to_numpy()
    I_pool = paired["light_i"].to_numpy()
    TH0_pool = paired["theta0_deg"].to_numpy()
    master = np.random.default_rng(20261025)
    rows = []
    t_start = time.time()
    for gen, label, effect, reps in SCENARIOS:
        for rep in range(reps):
            rng = np.random.default_rng(master.integers(1 << 31))
            N = 213
            take = rng.integers(0, len(paired), size=N)  # joint rows
            row = run_dataset(gen, effect, L0_pool[take], I_pool[take],
                              TH0_pool[take], rng)
            row.update({"scenario": f"{gen}:{label}",
                        "effect_label": label, "rep": rep})
            rows.append(row)
            print(f"{gen} {label} rep {rep + 1}/{reps}: "
                  f"winner={row['winner_lowest_median_rmse']} "
                  f"any_supported={row['any_M1_supported']} "
                  f"({time.time() - t_start:.0f}s)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "gate2_v3_pairedcov_replicates.csv", index=False)

    summary = {"design": {
        "differs_from_v2_only_in": ("(L0, intensity, initial angle) "
                                    "resampled jointly from the 213 "
                                    "paired archive rows"),
        "N_per_dataset": 213, "seeds": "master 20261025",
        "adoption_rule": ("median held-out RMSE improvement >= 5% "
                          "over M0 AND L0-parameter sign stable across "
                          "5 folds (Phase C rule)")},
        "scenarios": {}}
    for (gen, label), g in df.groupby(["generator", "effect_label"]):
        n = len(g)
        entry = {"n_datasets": int(n),
                 "winner_counts": {c: int((g.winner_lowest_median_rmse
                                            == c).sum()) for c in CANDS},
                 "any_M1_supported": {
                     "count": int(g.any_M1_supported.sum()),
                     "of": int(n),
                     "wilson95": wilson(int(g.any_M1_supported.sum()), n)}}
        for m in M1S:
            x = int(g[f"supported_{m}"].sum())
            entry[f"supported_{m}"] = {"count": x, "of": int(n),
                                       "wilson95": wilson(x, n)}
            entry[f"median_improvement_pct_{m}"] = float(
                g[f"improvement_pct_{m}"].median())
        summary["scenarios"][f"{gen}:{label}"] = entry
    (OUT / "phase_b_gate2_v3_pairedcov.json").write_text(
        json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
