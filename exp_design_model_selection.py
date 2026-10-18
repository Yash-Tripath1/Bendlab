#!/usr/bin/env python3
"""Model-selection design study for the two-source stimulus experiment.

Replaces the Welch distribution-separation calculation in exp_design.py
with the procedure a laboratory would actually face:

  1. Choose a candidate mechanism as ground truth.
  2. Simulate a full dataset of n seedlings (parameters drawn from the
     empirically weighted population), observed every 2 h for 24 h with
     2-degree measurement noise.
  3. Fit EVERY candidate mechanism to every seedling (coarse grid over
     k, tau, max_rate with the candidate's effective light angle fixed;
     the candidate gain is absorbed into fitted k), and select the
     mechanism with the lowest total squared error over the dataset.
  4. Report how often the selected mechanism is the true one.

Conditions: the best discriminator (160 degrees, 2:1) and a near
agreement control (60 degrees, 1:1). This includes biological variation
(weighted population) and parameter-fitting uncertainty (per-seedling
grid fits), which the Welch screen did not.

Output: results/exp_design_model_selection.csv
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd

from generate_plants import weighted_population
from vector_stimulus import MODELS, stimulus

SEED = 20261016
SIGMA = 2.0
REPS = 25
N_GRID = (10, 20, 40)
CONDITIONS = [(160.0, 2.0), (60.0, 1.0)]
DT = 0.05            # 3-minute integration step for the fitting simulator
K_GRID = (0.3, 0.7, 1.5, 3.0, 6.0, 12.0, 24.0, 48.0)
TAU_GRID = (0.25, 0.6, 1.2, 2.5, 5.0, 10.0)
MAX_GRID = (3.0, 8.0, 20.0, 60.0)


def simulate_batch(params: np.ndarray, phi_deg: float,
                   gain: float = 1.0) -> np.ndarray:
    """params (N,3) = k, tau, max_rate. Returns (N, 13) angles, 2 h grid."""
    k, tau, mr = params[:, 0], params[:, 1], params[:, 2]
    phi = np.deg2rad(phi_deg)
    theta = np.zeros(len(params))
    r = np.zeros(len(params))
    out = np.empty((len(params), 13))
    out[:, 0] = 0.0
    rec_every = int(round(2.0 / DT))
    j = 1
    for i in range(int(round(24.0 / DT))):
        stim = k * gain * np.sin(phi - np.deg2rad(theta))
        r += (stim - r) * (DT / tau)
        np.clip(r, -mr, mr, out=r)
        theta = theta + r * DT
        if (i + 1) % rec_every == 0:
            out[:, j] = theta
            j += 1
    return out


GRID = np.array([[k, t, m] for k in K_GRID for t in TAU_GRID
                  for m in MAX_GRID])


def candidate_sse(obs: np.ndarray, grid_sims: np.ndarray) -> float:
    """Total best-fit SSE of a candidate (pre-simulated grid) over all
    seedlings in obs (n,13)."""
    sse = ((grid_sims ** 2).sum(axis=1)[None, :]
           + (obs ** 2).sum(axis=1)[:, None]
           - 2.0 * obs @ grid_sims.T)
    return float(sse.min(axis=1).sum())


def main():
    t0 = time.time()
    fits = pd.read_csv("results/fit_fig1c.csv")
    clean = fits[fits["at_bound"] == "[]"].copy()
    pop = weighted_population(4000, seed=SEED, fit_frame=clean)
    rng = np.random.default_rng(SEED + 9)
    rows = []
    for sep, ratio in CONDITIONS:
        sources = [(-sep / 2.0, 1.0), (sep / 2.0, float(ratio))]
        eff = {m: stimulus(sources, m) for m in MODELS}  # (phi, gain)
        grid_sims = {m: simulate_batch(GRID, eff[m][0], gain=1.0)
                     for m in MODELS}
        for true_model in MODELS:
            phi_t, g_t = eff[true_model]
            for n in N_GRID:
                correct = 0
                chosen = {m: 0 for m in MODELS}
                for rep in range(REPS):
                    idx = rng.integers(0, len(pop), size=n)
                    params = pop[idx][:, :3] * np.array([g_t, 1.0, 1.0])
                    obs = simulate_batch(params, phi_t, gain=1.0)
                    obs = obs + rng.normal(0.0, SIGMA, obs.shape)
                    obs[:, 0] = 0.0
                    scores = {m: candidate_sse(obs, grid_sims[m])
                              for m in MODELS}
                    best = min(scores.values())
                    tied = [m for m in MODELS
                            if scores[m] <= best * (1 + 1e-6) + 1e-9]
                    pick = str(rng.choice(tied))  # genuine ties: chance
                    chosen[pick] += 1
                    correct += int(pick == true_model)
                rows.append({
                    "separation_deg": sep, "intensity_ratio": ratio,
                    "true_model": true_model, "n_seedlings": n,
                    "reps": REPS, "p_correct": correct / REPS,
                    **{f"p_chose_{m}": chosen[m] / REPS for m in MODELS},
                })
                print(rows[-1], flush=True)
    df = pd.DataFrame(rows)
    df.to_csv("results/exp_design_model_selection.csv", index=False)
    print(df.groupby(["separation_deg", "n_seedlings"])["p_correct"]
            .mean().round(3).to_string())
    print(f"done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
