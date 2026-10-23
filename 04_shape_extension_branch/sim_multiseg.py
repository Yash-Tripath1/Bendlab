"""Multi-segment phototropic bending simulator (shape extension).

This module extends the rigid one-angle model of sim.py to a chain of n
rigid segments, so that the stem has a measurable SHAPE: the angle between
each segment and the vertical can differ along the stem. The motivation is
identifiability: a single tip angle cannot distinguish a plant that bends
at the tip from one that bends at the base, but a shape profile can.

Model. Segment i has absolute angle theta_i (degrees, relative to
vertical) and bend rate r_i (degrees/hour). Each segment senses the
light locally and is elastically coupled to its neighbours:

    stim_i  = k_i * sin(phi(t) - theta_i)               (local tropic drive)
    lap_i   = theta_{i+1} - 2 theta_i + theta_{i-1}     (discrete curvature;
              free ends: one-sided difference)              straightness torque)
    tau * dr_i/dt = stim_i + c * lap_i - r_i            (rate relaxes to drive)
    r_i     = clip(r_i, -max_rate, +max_rate)           (saturation, after lag)
    dtheta_i/dt = r_i

Sensitivity gradient (zeta, dimensionless; "sensitivity concentration"):

    k_i = k * (1 - zeta + 2 * zeta * s_i),   s_i = i / (n_seg - 1)

so the base gain is k(1 - zeta) and the tip gain is k(1 + zeta).
zeta = 0 (default) gives a uniform chain; zeta > 0 represents an
elongation-zone-like gradient in which upper tissue responds more
strongly. zeta is part of the v2 shape extension (see
docs/SHAPE_EXTENSION_RESULTS.md section 4); v1 is zeta = 0.

Units and conventions follow sim.py: k in degrees/hour, tau and t in
hours, max_rate in degrees/hour, c (coupling) in 1/hour so that c*lap is
a target bend rate. Angles are stored in degrees; sine arguments are
converted to radians. Integration is explicit Euler at dt (default 1 min),
and the rate cap is applied AFTER the lag update, matching the model
contract in PROBLEM_STATEMENT.md and check_model_contract.py.

Segment indexing: 0 = base (bottom, attached), n_seg-1 = tip (top).
The observable "stem angle" of the rigid model is the tip segment angle
theta[-1].

Reduction properties (checked in check_multiseg.py):
  1. zeta = 0 and c = 0: each segment is an independent sim.py plant;
     with equal initial conditions all segments stay equal and the
     trajectory equals sim.simulate to machine precision (exact).
  2. Uniform initial state with zeta = 0, any c: the discrete Laplacian
     is identically zero, so the uniform solution is invariant and again
     equals sim.simulate exactly.
  3. zeta > 0 breaks the uniform subspace: curvature develops whenever
     the stem bends, and the shape becomes a measurable observable.

Note on v1 (zeta = 0): the uniform state is not only invariant but
attracting (tropic drive and coupling both restore curvature to zero),
so a uniform chain rotates rigidly and its shape features are constants.
This structural property motivated zeta; see docs/SHAPE_EXTENSION_RESULTS.md.

`simulate` and `batch_simulate` are pure functions of their arguments: no
randomness anywhere, so a rerun is bit-identical.
"""

from __future__ import annotations

import numpy as np

DEFAULT_DT = 1.0 / 60.0  # one minute, matches sim.py


def gain_profile(k: float, zeta: float, n_seg: int) -> np.ndarray:
    """Per-segment gains k_i, shape (n_seg,). zeta = 0 -> uniform k."""
    s = np.arange(n_seg, dtype=float) / (n_seg - 1)
    return k * (1.0 - zeta + 2.0 * zeta * s)


def simulate(k: float, tau: float, max_rate: float, c: float, phi_fn,
             t_end: float, n_seg: int = 5, dt: float = DEFAULT_DT,
             theta0: float = 0.0, r0: float = 0.0,
             zeta: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """Integrate one multi-segment plant under a time-varying light angle.

    phi_fn(t) returns the light angle in degrees at time t. Initial state
    is uniform along the stem: every segment starts at angle theta0 with
    bend rate r0 (defaults: vertical and still, matching sim.py). zeta is
    the sensitivity-gradient parameter (0 = uniform chain).

    Returns (times, thetas) with thetas shape (n_times, n_seg);
    thetas[:, -1] is the tip angle.
    """
    if n_seg < 2:
        raise ValueError("n_seg must be >= 2")
    n = int(round(t_end / dt))
    times = np.linspace(0.0, n * dt, n + 1)
    thetas = np.empty((n + 1, n_seg))
    gains = gain_profile(k, zeta, n_seg)
    theta = np.full(n_seg, float(theta0))
    r = np.full(n_seg, float(r0))
    thetas[0] = theta
    for i in range(n):
        # Same per-segment operation order as sim.simulate: stimulus,
        # lag update, cap, position update.
        stimulus = gains * np.sin(np.deg2rad(phi_fn(times[i]) - theta))
        lap = np.empty(n_seg)
        lap[0] = theta[1] - theta[0]
        lap[-1] = theta[-2] - theta[-1]
        lap[1:-1] = theta[2:] - 2.0 * theta[1:-1] + theta[:-2]
        target = stimulus + c * lap
        r += (target - r) * (dt / tau)
        np.clip(r, -max_rate, max_rate, out=r)
        theta = theta + r * dt
        thetas[i + 1] = theta
    return times, thetas


def batch_simulate(k, tau, max_rate, phi0, c, light_fn=None,
                   t_end: float = 24.0, dt: float = DEFAULT_DT,
                   record_dt: float | None = None, n_seg: int = 5,
                   theta0=None, r0=None, zeta=0.0):
    """Vectorised simulation for a whole population, stepped in lockstep.

    k, tau, max_rate, phi0, c are 1-D arrays of equal length. zeta is a
    scalar or an equal-length array (sensitivity gradient, 0 = uniform
    chain). light_fn(t, phi0) returns the per-plant light angle at time
    t; the default is static light at each plant's own phi0. Initial
    states are uniform along each stem: theta0/r0 default to zero (whole
    plant vertical and still) and may be scalars or (n_plants,) arrays.

    Integration is the same scheme as `simulate`. Under static light with
    uniform initial state, `simulate` and this function agree to within
    floating-point round-off (checked in check_multiseg.py).

    Returns (times, thetas) with thetas shape (n_records, n_plants, n_seg).
    """
    k = np.asarray(k, float)
    tau = np.asarray(tau, float)
    max_rate = np.asarray(max_rate, float)
    phi0 = np.asarray(phi0, float)
    c = np.asarray(c, float)
    if light_fn is None:
        light_fn = lambda t, p0: p0
    n_plants = len(k)
    if not (len(tau) == len(max_rate) == len(phi0) == len(c) == n_plants):
        raise ValueError("parameter arrays must have equal length")
    if n_seg < 2:
        raise ValueError("n_seg must be >= 2")
    zeta_arr = np.broadcast_to(np.asarray(zeta, float), (n_plants,))
    n = int(round(t_end / dt))
    rec = max(1, int(round(record_dt / dt))) if record_dt else 1
    thetas = np.empty((n // rec + 1, n_plants, n_seg))
    theta = np.zeros((n_plants, n_seg)) if theta0 is None \
        else np.broadcast_to(np.asarray(theta0, float),
                             (n_plants, n_seg)).copy()
    r = np.zeros((n_plants, n_seg)) if r0 is None \
        else np.broadcast_to(np.asarray(r0, float), (n_plants, n_seg)).copy()
    thetas[0] = theta
    # Per-plant, per-segment gains: (n_plants, n_seg). zeta = 0 -> exactly k.
    s_row = np.arange(n_seg, dtype=float) / (n_seg - 1)
    gains = k[:, None] * (1.0 - zeta_arr[:, None]
                          + 2.0 * zeta_arr[:, None] * s_row[None, :])
    j = 1
    for i in range(n):
        phi_rad = np.deg2rad(light_fn(i * dt, phi0))
        theta_rad = np.deg2rad(theta)
        # sin(phi - theta) expanded as in sim.batch_simulate.
        stimulus = gains * (np.sin(phi_rad)[:, None] * np.cos(theta_rad)
                            - np.cos(phi_rad)[:, None] * np.sin(theta_rad))
        lap = np.empty_like(theta)
        lap[:, 0] = theta[:, 1] - theta[:, 0]
        lap[:, -1] = theta[:, -2] - theta[:, -1]
        lap[:, 1:-1] = theta[:, 2:] - 2.0 * theta[:, 1:-1] + theta[:, :-2]
        target = stimulus + c[:, None] * lap
        r += (target - r) * (dt / tau)[:, None]
        np.clip(r, -max_rate[:, None], max_rate[:, None], out=r)
        theta = theta + r * dt
        if (i + 1) % rec == 0:
            thetas[j] = theta
            j += 1
    times = np.arange(thetas.shape[0]) * (dt * rec)
    return times, thetas


def batch_simulate_static(k, tau, max_rate, phi0, c, t_end: float,
                          dt: float = DEFAULT_DT,
                          record_dt: float | None = None, n_seg: int = 5,
                          zeta=0.0):
    """Static-light convenience wrapper around `batch_simulate`."""
    return batch_simulate(k, tau, max_rate, phi0, c, None, t_end, dt,
                          record_dt, n_seg, zeta=zeta)


def joint_curvatures(thetas: np.ndarray) -> np.ndarray:
    """Angle differences between adjacent segments, degrees per segment.

    For thetas of shape (..., n_seg) returns shape (..., n_seg - 1). Joint j
    sits between segments j and j+1; kappa_j = theta_{j+1} - theta_j.
    Positive kappa means the stem bends toward increasing segment angle.
    This is the discrete curvature the elastic coupling acts on.
    """
    return np.diff(thetas, axis=-1)


def tip_angle(thetas: np.ndarray) -> np.ndarray:
    """Angle of the topmost segment relative to vertical, degrees.

    For thetas of shape (..., n_seg) returns shape (...). This is the
    observable of the rigid sim.py model, so tip-only comparisons between
    the two models are like-for-like.
    """
    return thetas[..., -1]


def joint_heights(n_seg: int) -> np.ndarray:
    """Normalised heights of the joints, base 0.0 to tip 1.0.

    Segments sit at s_i = i / (n_seg - 1); joint j (between segments j and
    j+1) is assigned the midpoint s_j = (j + 0.5) / (n_seg - 1).
    """
    return (np.arange(n_seg - 1) + 0.5) / (n_seg - 1)
