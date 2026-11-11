# BendLab project overview: experiment series and validation

> **Status note, 16 October 2026.** Following the external audit (`docs/AUDIT_RESPONSE_2026-10-16.md` and `docs/AUDIT_FOLLOWUP_RESULTS.md`), H3 is **supported** under the literal `PROBLEM_STATEMENT.md` criterion (>5x median neighbour feature distance: 20/8,064 edges), the H6 global connectivity claim is **withdrawn** (when `phi0` is held fixed during recombination, same-cluster retention drops near the cross-cluster control), H7's matched-budget spread shrinks to 0.021, and H8's fixed policy was corrected (neither adaptive policy beat random selection in v1). Sections 4 and 5 and `results/figures/explainer2_dashboard.png` reflect these post-audit updates; see `docs/CURRENT_STATUS.md` for the canonical summary across all phases.

This document summarises the completed simulation experiments, the audit
of those experiments, and two analysis errors that materially affected
earlier conclusions. The corresponding six-panel summary figure is
`results/figures/explainer2_dashboard.png`.

## 1. Behavioural degeneracy

The summary figure compares two simulated plants whose maximum bend
rates differ by approximately an order of magnitude (251 and 24 degrees
per hour), while their remaining parameters are similar. Their stem-angle
trajectories agree within 1.3 degrees over 24 hours. Neither trajectory
approaches its maximum-rate limit, so that limit has no observable effect
on the measured behaviour.

This example illustrates the broader result quantified in the results
documents: behavioural clusters retain substantial ranges of all four
model parameters, particularly in the uniform parameter population.

## 2. Comparison with measured sunflower trajectories

The model was fitted independently to 48 sunflower stem-angle
trajectories from Brooks et al. (2023). The median per-plant RMSE after
correction of the time-base error is 1.80 degrees, compared with a median
across-plant standard deviation of 8.58 degrees in the measured data.

An earlier analysis incorrectly interpreted midday and afternoon
treatments as poorly represented by the model. That conclusion has been
retracted. The source data use zeitgeber time (ZT), and each treatment
group was first exposed to unilateral blue light at a different ZT.
Fitting elapsed time since each plant's stimulus onset, rather than
absolute ZT, gives acceptable fits for all six treatment groups.

The remaining systematic limitation concerns four ZT9 plants. Their
curves show a rapid rise, a reduction in bend rate, and a subsequent
second rise. The single-lag model cannot reproduce that two-phase rate
profile. The diagnostic analysis is reported in
`docs/RESULTS_ROUND2_ZT9.md`.

## 3. Adaptive identification experiment

The H8 experiment asks whether adaptive selection of light protocols
improves identification relative to random or fixed protocol selection.
Identification is scored by prediction of a held-out light-ramp
trajectory, not by recovery of the exact parameter vector.

Three reference levels were obtained:

- no plant-specific measurement: 30 per cent successful prediction;
- one noisy six-hour static-light trajectory: 44 per cent;
- the full 24-hour protocol budget: 89 per cent.

Within the full-budget condition, random protocol selection achieved
89.4 successful predictions per 100 plants, compared with 88.6 for the
greedy adaptive policy. The experiment therefore does not support an
advantage for the implemented adaptive policies at that budget. A more
demanding version has been specified in advance in
`docs/ADAPTIVE_IDENTIFICATION.md`.

## 4. Crossover connectivity analysis (withdrawn after audit)

H6 examined whether the set of parameter combinations producing similar
behaviour is connected. In the initial analysis, pairs of behaviourally
equivalent simulated plants were recombined parameter by parameter, with
mutation, and 57.3 per cent of recombinants remained in the source
cluster compared with 29.5 per cent for cross-cluster controls.

Subsequent external audit (`docs/AUDIT_FOLLOWUP_RESULTS.md`, Section 6)
showed that averaging `phi0` across source pairs confounded plant-trait
recombination with light-angle averaging: when `phi0` is held fixed at
the first parent's light angle, same-cluster retention drops to 41.3 per
cent against a 36.1 per cent cross-cluster control (5.2 percentage-point
excess). Midpoints of closely matched curve-equivalent pairs (`max |Δθ|
< 3 deg`) retain local proximity (24/40 within 3 deg), so local near-equivalence
holds while global cluster connectivity is **withdrawn**. The term
"crossover" here denotes recombination of numerical parameter vectors;
it does not simulate biological inheritance.

## 5. Hypothesis status (post-audit canonical)

| Hypothesis | Current status |
|---|---|
| H1: behaviour does not uniquely identify parameters | Supported as written (within-cluster ranges >= 20% of full range) |
| H2: a light-direction change improves parameter recovery | Not supported as written (only `k` narrows; `tau`, `max_rate`, `phi0` widen) |
| H3: behaviour contains discontinuities in parameter space | Supported as written (20/8,064 adjacent grid edges exceed 5x median feature distance; half-rise surface itself has no >2 h jump) |
| H4: behavioural clusters do not persist across light regimes | Supported (ARI = 0.442 < 0.50 on the empirically weighted population) |
| H5: the model reproduces measured sunflower trajectories | Supported in-sample (median RMSE 1.80 deg vs 8.58 deg spread; ZT9 limitation documented; held-out LOBO RMSE 11.75 deg) |
| H6: the degenerate parameter set is connected | Withdrawn (`phi0`-fixed recombinant retention 41.3% vs 36.1% cross-cluster control) |
| H7: protocols can be ranked by identifiability gain | Not supported (raw spread 0.091 < 0.10; matched 6 h budget spread 0.021) |
| H8: adaptive protocol selection improves identification | Not supported in v1 (adaptive <= random under corrected policies; v2 specified) |

## 6. Independent audit and analysis errors

The audit script re-derives the principal numerical results and compares
the simulator with the analytical solution of the equivalent damped
pendulum in limiting regimes. Simulated overshoot and oscillation period
agree with the corresponding closed-form values to the stated tolerances.

Three errors were identified in an earlier version of the audit:

1. omission of the degree-to-radian factor in the analytical natural
   frequency;
2. evaluation of a stronger cluster claim than the one made by the
   project;
3. an incorrect preliminary assertion that one short trajectory was
   sufficient for identification.

A fourth and more consequential error occurred in the fitting pipeline:
use of absolute zeitgeber time as elapsed stimulus time. The initial
audit did not detect that error because its H5 check used the same
time-base convention as the fitting code. Both scripts have been
corrected, and the audit now includes a regression check requiring each
plant's fitted start time to equal the stimulus-onset ZT of its
treatment group.

## Computational cost

The completed experiment suite performs approximately 44 million
fixed-step integration updates. Its short runtime follows from the low
dimensionality of the model (two state variables) and does not indicate
omitted computation. Runtime is not used as evidence for or against any
scientific claim.

## Future directions

The principal next steps are:

1. specify and evaluate a model extension containing circadian
   modulation of response gain and an autostraightening term;
2. test that extension by fitting an initial segment of each measured
   trajectory and forecasting the remainder;
3. obtain an independent curvature dataset for external shape validation;
4. evaluate the pre-specified second version of the adaptive
   identification experiment;
5. extend the model to field heliotropism only after the angle
   conventions and solar trajectory for those data have been specified.

The minimal model will be retained as the reference model. Any extension
will be considered an improvement only if it improves prediction on
held-out data relative to that reference.
