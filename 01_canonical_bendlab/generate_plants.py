"""Seeded generator for synthetic plant populations.

A simulated plant is represented by a parameter vector; no simulated vector
is interpreted as an individual organism. All draws are produced from a
declared integer seed, so each population is reproducible from that seed.

Two sampling modes are provided:

  uniform  — samples the full declared parameter box with equal density.
             This mode characterises the parameter space, including regions
             not represented by the measured sunflower data.

  weighted — concentrates samples in the region supported by measured data
             by bootstrap-resampling the clean fits from fit_real.py and
             applying a declared multiplicative jitter.
"""

from __future__ import annotations

import numpy as np

# Parameter names, bounds and units. The uniform bounds are wider than the
# empirically supported region, so the uniform population includes behaviour
# outside the range represented by the measured plants.
PARAMS = (
    ("k", 0.05, 3.00),    # per hour, response gain
    ("tau", 0.25, 6.00),  # hours, sensing lag
    ("max_rate", 2.0, 40.0),  # degrees per hour, saturation cap
    ("phi0", 5.0, 85.0),  # degrees, light angle under static regime
)

PARAM_NAMES = tuple(p[0] for p in PARAMS)
LOWER = np.array([p[1] for p in PARAMS])
UPPER = np.array([p[2] for p in PARAMS])


def uniform_population(n: int, seed: int) -> np.ndarray:
    """Draw n parameter vectors, uniform in the box. Shape (n, 4)."""
    rng = np.random.default_rng(seed)
    u = rng.random((n, len(PARAMS)))
    return LOWER + u * (UPPER - LOWER)


def population_frame(pop: np.ndarray, seed: int) -> "object":
    """Attach metadata so a saved population records how it was made."""
    import pandas as pd
    df = pd.DataFrame(pop, columns=PARAM_NAMES)
    df.insert(0, "plant_id", np.arange(len(df)))
    df.attrs["seed"] = seed
    df.attrs["sampler"] = "uniform"
    df.attrs["bounds"] = {name: (lo, hi) for name, lo, hi in PARAMS}
    return df


def weighted_population(n: int, seed: int, fit_frame, jitter: float = 0.15
                        ) -> np.ndarray:
    """Draw n parameter vectors from the region supported by measured data.

    fit_frame contains one row per fitted plant, with columns PARAM_NAMES.
    Callers must pass only clean fits (no parameter at an optimisation
    bound). A bound-pinned fit is an optimiser boundary solution rather
    than a measured value and must not define the supported region.

    Method: bootstrap-resample the fitted plants with replacement, then
    apply multiplicative lognormal jitter (0.15, specified in advance and
    not tuned to outcomes) to represent fitting and measurement uncertainty.

    Jitter is unclipped and no additional global bounds are applied, so the
    supported region is determined by the measured plants. Clipping samples
    to the uniform box would place probability mass at boundaries that are
    not represented by measured plants; consequently, some draws fall
    outside the uniform box.

    Returns shape (n, len(PARAM_NAMES)), same column order as PARAM_NAMES.
    """
    rng = np.random.default_rng(seed)
    vals = fit_frame[list(PARAM_NAMES)].to_numpy(float)
    if len(vals) == 0:
        raise ValueError("weighted_population needs at least one clean fit")
    idx = rng.integers(0, len(vals), size=n)
    pop = vals[idx]
    return pop * np.exp(rng.normal(0.0, jitter, size=pop.shape))


def splits(n: int, seed: int, dev_frac: float = 0.7, val_frac: float = 0.15
           ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Disjoint development / validation / test indices.

    Splitting is performed by plant rather than by observation row, so no
    plant appears in more than one partition.
    """
    rng = np.random.default_rng(seed + 777)
    idx = rng.permutation(n)
    n_dev = int(n * dev_frac)
    n_val = int(n * val_frac)
    return idx[:n_dev], idx[n_dev:n_dev + n_val], idx[n_dev + n_val:]


if __name__ == "__main__":
    pop = uniform_population(1000, seed=1)
    df = population_frame(pop, seed=1)
    print(df.head().to_string(index=False))
    print("\nbounds:", df.attrs["bounds"])
    d, v, t = splits(1000, seed=1)
    print(f"split sizes: dev={len(d)} val={len(v)} test={len(t)} "
          f"disjoint={len(set(d) & set(v)) == len(set(d) & set(t)) == 0}")
