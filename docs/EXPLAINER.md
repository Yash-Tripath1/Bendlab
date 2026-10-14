# BendLab project overview

## Summary

BendLab examines whether the parameters of a minimal phototropic bending
model can be identified from observed stem-angle trajectories. A
four-parameter model is used to generate populations of simulated plants,
simulate their responses under defined light regimes, and cluster the
resulting trajectories by behaviour. The central question is whether
plants with similar bending behaviour necessarily have similar underlying
parameters.

The current results indicate that they do not. Behaviourally similar
simulated plants can retain a substantial proportion of the full parameter
range, and one parameter, the maximum bend rate, can be exactly
unidentifiable when the observed trajectory never reaches that limit.

## Model parameters

| Parameter | Symbol | Interpretation |
|---|---|---|
| Response gain | `k` | Strength of the response to the angular difference between the stem and the light direction |
| Sensing lag | `tau` | Time constant with which the bend rate approaches its stimulus-dependent value |
| Maximum bend rate | `max_rate` | Upper bound on the rate of change of stem angle, in degrees per hour |
| Light angle | `phi0` | Direction of the incident light under the static-light regime, in degrees |

The simulator integrates a two-state model for stem angle and bend rate.
Its purpose is not to reproduce the complete physiology of phototropism,
but to provide a controlled system in which known parameter values can be
compared with the information recoverable from observed behaviour.

## Rationale for simulation

A measured plant provides a trajectory but not the internal parameter
values that generated it. Simulation provides both. Large simulated
populations therefore allow the mapping from parameters to behaviour to
be examined directly, including whether that mapping is one-to-one.

Simulation alone is insufficient, however, because conclusions may apply
only to the model. For that reason, the model is also fitted to measured
sunflower trajectories in the published PLOS Biology dataset. Those fits
define the empirically plausible parameter region used for the weighted
simulation experiments.

## Parameter degeneracy

Parameter degeneracy occurs when different parameter combinations produce
trajectories that cannot be distinguished at the available measurement
resolution. BendLab provides both approximate and exact examples.

The exact example is provided by plant ZT0-1. Refitting that measured
curve after removing the maximum-rate limit gives an RMSE of 1.894
degrees, identical to the fit obtained with the limit included. The
trajectory never reaches the fitted cap; consequently, the cap leaves no
observable trace and cannot be recovered from that curve, regardless of
measurement precision within the stated model.

## Principal findings

**Model adequacy.** Across 48 measured sunflower trajectories, the
median per-plant RMSE is 1.80 degrees, compared with a median
across-plant standard deviation of 8.58 degrees. The model error is
therefore smaller than the variation among measured plants in all six
stimulus-start-time groups.

**Behaviour does not uniquely identify parameters.** Among 10,000
uniformly sampled simulated plants clustered into six behavioural
groups, the largest cluster contains 2,859 plants and spans nearly the
complete ranges of response gain, maximum bend rate and light angle.
Across clusters, approximately 25–50 per cent of each parameter range
is retained within behaviourally similar groups.

**Clusters primarily separate response magnitude.** The behavioural
clusters distinguish stronger from weaker responders more clearly than
they identify distinct parameter combinations.

**A mid-course change in light direction did not improve recovery under
the initial metric.** A 45-degree change in light angle at hour 8 did not
consistently reduce within-cluster parameter spread. This result is
interpreted as a limitation of the cluster-retention metric as much as a
property of the light regime.

## Implications

These results caution against treating parameters fitted to a single
trajectory as direct measurements when the underlying model contains
unidentifiable or weakly identifiable directions. They also motivate the
subsequent experimental-design question addressed by BendLab: which
light protocols provide additional information that separates plants
whose behaviour is indistinguishable under static light?

## Recommended reading order

1. `PROBLEM_STATEMENT.md` — research question, model and hypotheses
2. `docs/RESULTS_ROUND0.md` — model fitting and degeneracy results
3. `docs/RESULTS_ROUND1.md` — protocol, connectivity and identification analyses
4. `docs/RESULTS_ROUND2_ZT9.md` — diagnostic analysis of the remaining ZT9 model limitation
5. `docs/DATA_SOURCES.md` and `docs/DATA_CONTRACT.md` — data provenance and handling rules
