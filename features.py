"""Feature extraction from bending trajectories.

Features are defined here, before any results exist, so they cannot be chosen
to flatter a result. All angles in degrees, all times in hours.
"""

from __future__ import annotations

import numpy as np


def time_to_threshold(times, thetas, level: float) -> float:
    """First time theta crosses `level`. Returns t_end + 1 if never reached."""
    hit = np.nonzero(thetas >= level)[0]
    return float(times[hit[0]]) if len(hit) else float(times[-1] + 1.0)


def half_rise_time(times, thetas) -> float:
    """Time to reach half of the trajectory's own peak. Scale-free."""
    peak = float(np.max(thetas))
    if peak <= 0:
        return float(times[-1] + 1.0)
    return time_to_threshold(times, thetas, peak / 2.0)


def peak_angle(times, thetas) -> float:
    return float(np.max(thetas))


def final_angle(times, thetas) -> float:
    return float(thetas[-1])


def terminal_error(times, thetas, phi0: float) -> float:
    """How far the plant ends from the light. Zero is perfect orientation."""
    return float(thetas[-1] - phi0)


def overshoot(times, thetas) -> float:
    """Peak above final value. Captures plants that swing past the light."""
    return float(np.max(thetas) - thetas[-1])


def peak_rate(times, thetas) -> float:
    """Fastest observed bend, in degrees per hour. Named peak_rate, not
    max_rate, because max_rate is the parameter that caps it; the two must
    never share a column name in a feature table."""
    if len(times) < 2:
        return 0.0
    return float(np.max(np.abs(np.diff(thetas))) / (times[1] - times[0]))


def reversal(times, thetas) -> float:
    """Largest drop from peak to end. Detects plants that give up."""
    return float(np.max(thetas) - thetas[-1])


def auroc(times, thetas) -> float:
    """Area under the angle curve, normalised by duration. A single scalar
    summarising 'how bent was this plant, on average, over the run'."""
    if len(times) < 2:
        return 0.0
    span = times[-1] - times[0]
    return float(np.trapezoid(thetas, times) / span) if span > 0 else 0.0


# Tracking features, only meaningful under a moving-light regime.

def tracking_lag(times, thetas, phis) -> float:
    """Mean angle by which the plant trails the light. Only over the window
    where the light is actually moving, so a static stretch does not dilute it."""
    moving = np.abs(np.gradient(phis)) > 1e-9
    if not np.any(moving):
        return float("nan")
    return float(np.mean(phis[moving] - thetas[moving]))


def tracking_rmse(times, thetas, phis) -> float:
    moving = np.abs(np.gradient(phis)) > 1e-9
    if not np.any(moving):
        return float("nan")
    return float(np.sqrt(np.mean((phis[moving] - thetas[moving]) ** 2)))


STATIC_FEATURES = ("half_rise_time", "peak_angle", "final_angle", "overshoot",
                   "peak_rate", "auroc")


def static_vector(times, thetas) -> np.ndarray:
    """The fixed-order feature vector used for clustering under static light."""
    return np.array([
        half_rise_time(times, thetas),
        peak_angle(times, thetas),
        final_angle(times, thetas),
        overshoot(times, thetas),
        peak_rate(times, thetas),
        auroc(times, thetas),
    ])
