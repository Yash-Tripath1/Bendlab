# Shape extension: multi-segment stem, shape features, and a degeneracy study

**Date:** 18 October 2026
**Branch:** `shape-extension`
**Status:** v1 specified here in advance and run; falsified as specified
and diagnosed (empty shape channel). The corrected v2 model and its
pre-registration are in `docs/SHAPE_EXTENSION_RESULTS.md` sections 3–4
(specified before the v2 run); all results are in that document.
**Related:** `PROBLEM_STATEMENT.md` (H1), `docs/RESULTS_ROUND0.md` (degeneracy),
`sweep.py` (retention metric)

---

## 1. Motivation

The central result of experiment series 1 is that behavioural similarity
under one observable (the stem angle) does not imply parameter
similarity: within-cluster parameter ranges retain 25–50 per cent of the
full sampled range. Two simulated plants can therefore bend to the same
angle curve while differing in gain, lag, rate cap and target angle.

This raises a measurement question. The model records ONE angle per
plant: the deviation of the stem from vertical. A real stem, however, has
a shape: it can bend at the tip, at the base, or in an S. Two plants with
the same tip-angle trajectory may reach it with different curvature
distributions along the stem. If the curvature profile carries parameter
information that the tip angle discards, then measuring it — angles
between the vertical and several points of the stem — should reduce
degeneracy.

Within the rigid sim.py model this idea is vacuous by construction:
every point of the stem shares the angle theta. The idea therefore
requires (a) a model with spatial structure and (b) features of the
resulting shape. Both are defined here.

## 2. Model

`sim_multiseg.py` extends the two-state model to a chain of n_seg rigid
segments. Segment i has absolute angle theta_i (degrees from vertical;
index 0 = base, n_seg-1 = tip) and bend rate r_i:

    stim_i = k * sin(phi(t) - theta_i)                (local light sensing)
    lap_i  = theta_{i+1} - 2 theta_i + theta_{i-1}    (free ends: one-sided)
    tau * dr_i/dt = stim_i + c * lap_i - r_i          (rate relaxes to drive)
    r_i    = clip(r_i, -max_rate, +max_rate)          (cap AFTER the lag)
    dtheta_i/dt = r_i

Parameters k, tau, max_rate, phi0 keep their sim.py meanings and units.
The new parameter c (coupling, hour^-1) sets the elastic resistance to
curvature: a straight, uniformly angled stem is torque-free, and any
curvature produces a restoring target-rate term c * lap_i. Free-end
boundaries mean the stem carries no bending moment at base or tip.

Declared properties, both exact and both checked in `check_multiseg.py`:

1. **c = 0 reduces to sim.py exactly.** Each segment becomes an
   independent sim.py plant; with equal initial conditions all segments
   stay equal and the trajectory equals `sim.simulate` to machine
   precision.
2. **The uniform solution is invariant for any c.** If every segment
   starts at the same angle and rate, lap is identically zero and the
   chain follows sim.py exactly.

Consequently the tip angle theta_{n-1}(t) is directly comparable with the
sim.py stem angle, and every tip-only result of series 1 has a defined
counterpart here.

**Design choices declared in advance:**

- n_seg = 5 (4 joints) for the study. Sensitivity to n_seg is not
  analysed in this round.
- Coupling range c ~ Uniform[0, 1] hour^-1. Calibration: over the
  curvature range the model actually reaches (joint differences of a few
  to tens of degrees), c * lap is on the same scale as the k * sin(...)
  stimulus, so the range spans "no coupling" to "coupling as strong as
  the tropic drive". c is a model parameter of the extension only; it is
  not fitted to measured data and has no measured counterpart yet.
- Static light, each plant under its own phi0, 24 h, record every 0.5 h:
  the protocol and window of the H1 sweep, so comparability is maximal.
- Population: uniform in the 4-parameter box of `generate_plants.py`
  extended with c. Same sampler philosophy, declared seed.

## 3. Features

Tip-only arm: the six `features.STATIC_FEATURES` computed on the tip
angle, exactly as in `sweep.py` (same vectorised definitions).

Shape arm: those six plus the eight shape features in
`features_shape.SHAPE_FEATURES`, defined in that module before any result
existed:

| Feature | What it measures |
|---|---|
| `curv_final_abs` | overall curvature at the end |
| `curv_peak_abs` | maximum overall curvature reached |
| `curv_dispersion` | how unevenly curvature is spread along the stem |
| `bend_centroid` | height of the curvature centroid (0 base – 1 tip) |
| `curv_profile_slope` | tip-heavy (+) vs base-heavy (−) curvature at the end |
| `tip_base_bias` | end curvature above minus below mid-height |
| `s_shape_sign_changes` | S-shape incidence along the stem |
| `onset_gap` | bottom-minus-top curvature onset time: downward propagation of bending |

All are deterministic functions of the recorded shape theta(s, t);
none is chosen after inspecting outcomes.

## 4. Study and pre-registered hypothesis

`shape_degeneracy.py` runs one population through both feature arms and
applies the **identical** clustering criterion of `sweep.py`:
StandardScaler, KMeans(n_clusters=6, n_init=10, random_state=1), clusters
with fewer than 50 plants skipped. Degeneracy is quantified with the
series-1 retention metric: median within-cluster IQR divided by the full
population range, per parameter.

**H-SHAPE (pre-registered).** Clustering with the shape arm reduces
median within-cluster IQR retention by at least 10 percentage points,
relative to the tip-only arm, for at least two of the five parameters
(k, tau, max_rate, phi0, c).

**Falsification.** Fewer than two parameters show a reduction of at
least 10 percentage points.

The threshold matches the 10-point margin of H2, so "materially better
than tip-only" means the same thing here as it did there. The comparison
is within-population: both arms see the same plants, so any difference is
attributable to the features alone.

## 5. What this study is not

- It is not a claim about living plants. As in series 1, results describe
  the simulator class unless measured data are explicitly used.
- Measurement noise is not yet included. Five noisy angle measurements
  are not automatically better than one clean one; the noise-robust
  version of this comparison is a declared follow-up, not a
  post-hoc excuse.
- The shape arm adds no new observable to the rigid model. Any gain here
  comes from the multi-segment extension, and it is a property of that
  model class that must later be checked against real shape data
  (image-derived stem tracing is the natural source).
- c is not identified against data here. Whether real stems show the
  coupling regime the extension assumes is an open empirical question.

## 6. Files

| Path | Role |
|---|---|
| `sim_multiseg.py` | multi-segment simulator; reduces exactly to `sim.py` (zeta = 0 is v1; zeta > 0 is the v2 sensitivity gradient) |
| `features_shape.py` | shape feature definitions (fixed before results) |
| `check_multiseg.py` | regression checks: exact reduction, uniform invariance, batch/single agreement, determinism, cap contract, zeta behaviour |
| `shape_degeneracy.py` | H-SHAPE v1: the pre-registered tip-only vs shape comparison |
| `shape_degeneracy_v2.py` | H-SHAPE-v2: the corrected comparison (pre-registered in the results document) |
| `docs/SHAPE_EXTENSION_RESULTS.md` | numerical results, diagnosis, v2 pre-registration and outcome |

Reproduction (from the repository root):

```
python check_multiseg.py
python shape_degeneracy.py
```

Both scripts use declared integer seeds; no unseeded randomness and no
wall-clock values enter the simulation path.
