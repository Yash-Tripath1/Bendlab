"""Shape features from multi-segment bending trajectories.

These features are defined here, before any results exist, so they cannot
be chosen to flatter a result (same rule as features.py). All angles in
degrees, all times in hours.

Input is one trajectory of segment angles: thetas with shape (T, n_seg),
index 0 = base, n_seg-1 = tip (see sim_multiseg.py). Joint curvatures
kappa_j = theta_{j+1} - theta_j are defined in sim_multiseg.joint_curvatures.

SHAPE_FEATURES is the fixed-order vector used for clustering in
shape_degeneracy.py. Tip-only features for comparison come from
features.static_vector applied to the tip angle, so the two clustering
arms differ only by the presence of shape information.

Feature definitions (T = final recorded time):

  curv_final_abs        mean_j |kappa_j(T)|
                        Overall curvature of the stem at the end.
  curv_peak_abs         max_t mean_j |kappa_j(t)|
                        Most curved the stem ever gets.
  curv_dispersion       mean_t std_j( kappa_j(t) )
                        Spread of signed curvature along the stem at each
                        time; large when bending is unevenly distributed.
  bend_centroid         mean_t [ sum_j s_j |kappa_j(t)| / sum_j |kappa_j(t)| ]
                        Height (0 base, 1 tip) of the curvature-magnitude
                        centroid, averaged over time. Times with no
                        curvature (sum < 1e-12) contribute 0.5 (neutral
                        midpoint, declared in advance).
  curv_profile_slope    slope of |kappa_j(T)| against joint height s_j,
                        least squares. Positive: curvature concentrated
                        toward the tip; negative: toward the base.
  tip_base_bias         mean |kappa_j(T)| over joints above mid-height
                        minus mean over joints below. Signed summary of
                        tip-heavy vs base-heavy bending at the end.
  s_shape_sign_changes  mean_t number of sign changes in kappa_j along the
                        stem. Zero for a simple C-bend; positive when the
                        stem takes an S-shape.
  onset_gap             onset_bottom - onset_top, where onset of a region
                        is the first time its mean |kappa| crosses 10 per
                        cent of its own peak (t_end + 1 if never). Positive
                        when bending starts near the tip and propagates
                        downward, which is the expected phototropic order.

onset_gap is the only feature that mixes regions over time; the others are
per-time summaries or end-state summaries.
"""

from __future__ import annotations

import numpy as np

from sim_multiseg import joint_curvatures, joint_heights

SHAPE_FEATURES = (
    "curv_final_abs",
    "curv_peak_abs",
    "curv_dispersion",
    "bend_centroid",
    "curv_profile_slope",
    "tip_base_bias",
    "s_shape_sign_changes",
    "onset_gap",
)

_ONSET_FRAC = 0.10      # fraction of own peak for onset detection
_ZERO_CURV = 1e-12      # below this a stem counts as straight


def _onset_time(series: np.ndarray, times: np.ndarray) -> np.ndarray:
    """First time each row of `series` (T, N) crosses 10% of its own peak.

    Returns shape (N,); rows that never cross return t_end + 1, matching
    features.time_to_threshold.
    """
    peak = series.max(axis=0)
    hit = series >= (_ONSET_FRAC * peak)[None, :]
    any_hit = hit.any(axis=0)
    idx = np.where(any_hit, hit.argmax(axis=0), len(times))
    return times[np.minimum(idx, len(times) - 1)] + \
        np.where(any_hit, 0.0, 1.0)


def shape_vector(times: np.ndarray, thetas: np.ndarray) -> np.ndarray:
    """Fixed-order shape feature vector for ONE trajectory.

    thetas has shape (T, n_seg). Returns shape (len(SHAPE_FEATURES),),
    in the declared SHAPE_FEATURES order.
    """
    return shape_batch(times, thetas[None, :, :])[0]


def shape_batch(times: np.ndarray, thetas: np.ndarray) -> np.ndarray:
    """Shape features for a population: thetas (T, N, n_seg) -> (N, F).

    Vectorised over plants; identical definitions to shape_vector.
    """
    if thetas.ndim != 3:
        raise ValueError("thetas must have shape (T, n_plants, n_seg)")
    kappa = joint_curvatures(thetas)              # (T, N, J)
    abs_k = np.abs(kappa)
    heights = joint_heights(thetas.shape[2])      # (J,)

    mean_abs = abs_k.mean(axis=2)                 # (T, N) overall curvature
    curv_final_abs = mean_abs[-1]
    curv_peak_abs = mean_abs.max(axis=0)
    curv_dispersion = kappa.std(axis=2).mean(axis=0)

    total = abs_k.sum(axis=2)                     # (T, N)
    centroid_num = (abs_k * heights[None, None, :]).sum(axis=2)
    centroid_t = np.where(
        total > _ZERO_CURV,
        centroid_num / np.maximum(total, _ZERO_CURV),
        0.5)
    bend_centroid = centroid_t.mean(axis=0)

    # Least-squares slope of final |kappa| against joint height.
    x = heights - heights.mean()
    y = abs_k[-1]                                 # (N, J)
    curv_profile_slope = (y * x[None, :]).sum(axis=1) / float((x ** 2).sum())

    top = heights > 0.5
    bot = heights < 0.5
    top_mean = y[:, top].mean(axis=1) if top.any() \
        else np.zeros(thetas.shape[1])
    bot_mean = y[:, bot].mean(axis=1) if bot.any() \
        else np.zeros(thetas.shape[1])
    tip_base_bias = top_mean - bot_mean

    signs = np.sign(kappa)                        # (T, N, J)
    changes = (signs[1:] * signs[:-1] < 0).sum(axis=2)  # (T-1, N)
    s_shape_sign_changes = changes.mean(axis=0).astype(float)

    top_series = abs_k[:, :, top].mean(axis=2) if top.any() \
        else np.zeros((len(times), thetas.shape[1]))
    bot_series = abs_k[:, :, bot].mean(axis=2) if bot.any() \
        else np.zeros((len(times), thetas.shape[1]))
    onset_gap = _onset_time(bot_series, times) - _onset_time(top_series, times)

    return np.column_stack([
        curv_final_abs, curv_peak_abs, curv_dispersion, bend_centroid,
        curv_profile_slope, tip_base_bias, s_shape_sign_changes, onset_gap,
    ])
