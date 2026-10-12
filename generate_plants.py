"""Seeded generator for synthetic plant populations.

A 'plant' is a parameter vector. Nothing here pretends to be a real organism.
Every draw comes from a single generator seeded from a declared integer, so a
population is reproducible from its seed alone and nothing else.

Two sampling modes, because they answer different questions:

  uniform  — explore the box. Every region gets equal weight. Use this to find
             what the parameter space contains, including regions that are
             biologically silly. This is the right default for H1-H4.

  weighted — concentrate draws where real plants were measured, by
             bootstrap-resampling the clean fits from fit_real.py with
             declared jitter. Use this once the fit defines the plausible
             region (done 12 Oct: see results/fit_fig1c.csv, clean fits only).
"""

from __future__ import annotations

import numpy as np

# Parameter names, bounds and units. Bounds are deliberately wider than any
# real plant, so the uniform population includes behaviour no plant shows.
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
    """Draw n parameter vectors where real plants were actually measured.

    fit_frame: one row per fitted real plant, columns = PARAM_NAMES. Callers
    must pass only clean fits (no parameter pinned at a bound); a bound-pinned
    fit is an artifact of the optimizer's wall, not a measurement, and must
    not define the plausible region.

    Method: bootstrap-resample the fitted plants with replacement, then apply
    multiplicative lognormal jitter (declared 0.15, chosen once, never tuned)
    to represent fit and measurement uncertainty.

    Jitter is deliberately unclipped, and no global bounds are applied. The
    plausible region is defined by the measured plants and nothing else:
    clipping to the uniform box would put probability mass at the box walls
    where no plant was ever measured. The trade-off, stated plainly, is that
    a few draws land outside the uniform box.

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

    Split by plant, not by row, so no plant appears in two splits. Mirrors the
    world-level split in the matching hackathon, where the unit was the pool.
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
