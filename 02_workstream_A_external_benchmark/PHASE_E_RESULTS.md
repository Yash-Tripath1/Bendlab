# Phase E results: intensity-dependent restoring balance

## Preregistered question

The preregistered question was whether an intensity-dependent restoring coefficient could improve plant-held-out trajectory prediction over the B1 group-mean curve on the 268-plant unilateral-light archive. The plan was committed separately in `growth_phase/PHASE_E_PREREGISTRATION.md` before the W3 fitting run (preregistration commit `f06cc44`). The primary success criterion was fixed in advance: W3 must have median held-out per-plant trajectory RMSE strictly below 9.73 degrees. Results at or above 9.73 degrees are negative under that criterion.

## Model

W3 uses the `sim_gamma.py` dynamics with `phi_light = 90 degrees` fixed as physical lamp geometry. The response gain `k` is shared across intensity. Intensity enters through the phenomenological restoring coefficient

`gamma(I) = exp(c0 + c1 * ln(I))`.

The dynamics are

`tau * dr/dt = k * sin(pi * (phi_light - theta) / 180) - gamma(I) * theta - r`,

`dtheta/dt = r`, with the rate clipped to the fitted maximum after the lag update. The model-implied fixed point solves

`k * sin(pi * (phi_light - theta_eq) / 180) = gamma(I) * theta_eq`.

Here `gamma` is a phenomenological restoring coefficient, not a claim about a specific biological mechanism. W2's `phi_eff(I)` remains an effective target-angle diagnostic and is not interpreted as a biological equilibrium angle.

## Data and evaluation

The analysis used the tracked `05_data_external/uni_trajectories.csv`: 88,504 observations from 268 plants, with ten intensity groups from 0.7 to 5.8 W/m². The script reused the existing intensity-stratified five-fold plant assignment, seed 42, every-fourth-observation fitting subsample, one-minute integration step, observed initial angle, and evaluation at every observed time. W1, W2, B1, B1r, and B2 were reproduced with the existing benchmark functions without modifying the benchmark script.

All five reproduced baselines agreed with `benchmark_summary.json` within the preregistered 0.05-degree harness tolerance. The largest difference was 0.0074 degrees for W2. W1, B1, B1r, and B2 were within 0.0001 degrees of their saved values.

The script runtime was 224.2 seconds. The primary and leave-one-intensity-out results were generated with seed 42. The committed machine-readable outputs and per-plant results are in `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_*`.

## Primary results

Median per-plant held-out RMSE over all 268 plants, in degrees:

| Model | Median RMSE | 25th to 75th percentile |
|---|---:|---:|
| W1, intensity-dependent gain and fixed 90-degree light | 14.4072 | 11.5292 to 17.8708 |
| W2, intensity-dependent effective target-angle diagnostic | 9.9781 | 7.1602 to 13.9161 |
| W3, intensity-dependent restoring coefficient | 9.9968 | 7.3886 to 13.8278 |
| B1, group-mean curve | 9.7347 | 7.3516 to 13.9853 |
| B1r, recentered group-mean curve | 10.0258 | 7.5053 to 13.6488 |
| B2, saturating exponential | 10.9166 | 7.8619 to 14.1320 |

Per-intensity-group median held-out RMSE, in degrees:

| Intensity (W/m²) | W1 | W2 | W3 | B1 | B1r | B2 |
|---:|---:|---:|---:|---:|---:|---:|
| 0.70 | 10.31 | 10.16 | 9.48 | 8.94 | 9.54 | 9.49 |
| 1.10 | 12.40 | 9.71 | 10.11 | 9.00 | 11.13 | 9.43 |
| 1.40 | 11.78 | 10.59 | 10.52 | 9.82 | 8.44 | 10.29 |
| 1.90 | 14.28 | 9.51 | 9.85 | 9.71 | 11.11 | 10.00 |
| 2.25 | 15.11 | 12.05 | 11.93 | 12.08 | 11.93 | 11.04 |
| 3.00 | 16.07 | 10.04 | 9.83 | 9.68 | 9.65 | 11.49 |
| 3.20 | 14.32 | 11.80 | 12.29 | 11.89 | 11.63 | 13.32 |
| 3.85 | 15.84 | 9.58 | 9.54 | 8.56 | 10.10 | 10.89 |
| 4.40 | 14.99 | 8.19 | 8.41 | 7.87 | 8.97 | 9.83 |
| 5.80 | 16.42 | 10.65 | 11.13 | 10.52 | 9.60 | 12.48 |

### Decision against the fixed criterion

W3's primary median RMSE was 9.9968 degrees, above the fixed 9.73-degree threshold and 0.27 degrees above it. The criterion was not met. This is a negative result under the preregistered absolute threshold. It is not evidence that W3 has higher held-out error than B1. No parameters or threshold were retuned after evaluation.

### Magnitude of the gap to the baseline

The threshold verdict stands unchanged: W3 is above 9.73 degrees, so the preregistered primary result is negative.

The paired analysis of the 268 held-out plants does not distinguish the W3 minus B1 difference from zero. Positive differences indicate higher RMSE for the first model.

| Paired difference | Median (degrees) | Mean (degrees) | First model worse | Wilcoxon statistic | Two-sided p | Bootstrap 95% interval for median difference (degrees) |
|---|---:|---:|---:|---:|---:|---:|
| W3 minus B1 | +0.0509 | -0.0419 | 141/268 (52.6%) | 17893 | 0.9185 | [-0.1954, +0.2798] |
| W2 minus B1 | -0.1766 | -0.1563 | 127/268 (47.4%) | 16211 | 0.1537 | [-0.4688, +0.1402] |

Differences and two-sided Wilcoxon signed-rank tests were calculated from a plant-by-model pivot of `phase_e_w3_heldout_per_plant.csv`. Each percentile interval uses 2,000 plant-level resamples of the paired differences with NumPy `default_rng` seed 0. The W3 minus B1 interval computed by this committed procedure, [-0.1954, +0.2798], differs from the review's approximate interval of [-0.171, +0.265]; the values above are the recomputed results. The paired test is not a formal TOST equivalence test with a prespecified margin.

Accordingly, the paired held-out errors are described as reaching parity with the nonparametric B1 group-mean baseline, rather than as showing W3 to be beaten by B1. W3 nevertheless substantially improves on W1, the earlier candidate that placed intensity in response gain: the paired median change W3 minus W1 is -4.5256 degrees, and W3 has lower RMSE for 216/268 plants (80.6%). Parity with a mean curve is not evidence of a mechanism.

## Global W3 parameters

The all-data W3 fit used the same subsampling and integration protocol as the held-out fits. Approximate two-sided 95% intervals use the preregistered plant-cluster sandwich covariance with the finite-cluster correction. Positive parameters were transformed back from optimizer log scale.

| Parameter | Estimate | 95% CI | Units or interpretation |
|---|---:|---:|---|
| `k` | 13.044 | [11.859, 14.347] | degrees per hour, shared gain |
| `tau` | 2.620 | [2.307, 2.976] | hours |
| `max_rate` | 9.121 | [5.815, 14.307] | effective fitted rate limit, not physiological |
| `c0` | -0.433 | [-0.574, -0.292] | log gamma at 1 W/m² |
| `gamma(1 W/m²) = exp(c0)` | 0.649 | [0.563, 0.747] | inverse hours |
| `c1` | -0.484 | [-0.572, -0.396] | exponent of intensity in gamma(I) |

The `c1` interval excludes zero. The negative `c1` means the fitted restoring coefficient decreases as intensity increases, which raises the model-implied fixed point from 16.25 degrees at 0.7 W/m² to 37.41 degrees at 5.8 W/m². These are model-implied values, not a measured biological equilibrium.

The measured late-window angle in the same archive also rises with intensity. The supporting analysis script reproduces the previously measured partial Spearman rho of +0.498, with a two-sided t-approximation p value of 1.44e-14 on 213 length-paired plants, controlling for `theta(0)`, interval-average elongation, and starting length. This is contextual evidence from the archive, not a new result from the W3 fit. Using the specified 16-21 hour angle mean, the exact group medians in all 268 plants range from 18.56 degrees at 0.7 W/m² to 33.60 degrees at 5.8 W/m², with non-monotonic interior groups. These endpoints differ from the earlier approximate summary of about 22 to 30 degrees; the computed values and procedure are reported in `PHASE_E_SUPPORTING_ANALYSIS.md` and `phase_e_supporting_associations.json`.

The directional part of the preregistered proposal was therefore supported in sign, while the predictive criterion was not met. A correctly signed trend without predictive gain is the finding.

### Status of the fitted rate limit

For each of the 268 plants, `phase_e_peak_rate_check.py` applies a centred five-observation rolling mean, approximately 20 minutes at the archive cadence, then uses `numpy.gradient` with the observed times in hours. The per-plant peak is the maximum absolute derivative magnitude. The median peak rate is 19.18 degrees per hour, the 90th percentile is 35.32 degrees per hour, and the maximum is 66.57 degrees per hour. For 266 of 268 plants, the smoothed observed peak exceeds the all-data fitted `max_rate` of 9.121 degrees per hour.

Under this stated procedure, the observed median is about 1.8 degrees per hour below the review's approximate value of 21. The 90th percentile and maximum are 35.32 and 66.57 degrees per hour, compared with the review's approximate values of 36 and 70. The values above are the direct recomputation from the committed script and JSON output; no fit was run for this check.

The fitted `max_rate` sits below the median observed peak rate. It therefore acts as a smoothing or effective rate in this fit, not as a measured physiological limit. This is consistent with the existing Phase B0 finding that `max_rate` was inactive and unidentified from the tip-angle trajectories (`PHASE_B0_REPORT.md`, Section 2). The fitted value `max_rate = 9.121 degrees per hour` must not be quoted as a biological maximum bending rate. A pinned-cap sensitivity fit is a reasonable follow-up, but it was not run for this reporting correction.

## Leave-one-intensity-group-out results

Each intensity group was omitted from fitting in turn. The endpoint groups at 0.7 and 5.8 W/m² are extrapolation; interior groups are interpolation. Values are median per-plant RMSE in degrees.

| Held-out intensity (W/m²) | Evaluation | W1 | W2 | W3 | B1 | B1r | B2 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0.70 | Endpoint extrapolation | 10.37 | 9.78 | 9.62 | 10.76 | 10.74 | 9.58 |
| 1.10 | Interpolation | 12.42 | 9.84 | 9.98 | 8.77 | 10.49 | 9.37 |
| 1.40 | Interpolation | 11.82 | 10.64 | 11.00 | 9.74 | 9.14 | 10.69 |
| 1.90 | Interpolation | 14.31 | 9.53 | 9.55 | 9.88 | 10.34 | 10.26 |
| 2.25 | Interpolation | 15.12 | 12.21 | 12.02 | 11.84 | 11.41 | 10.99 |
| 3.00 | Interpolation | 16.33 | 10.25 | 10.37 | 11.19 | 11.07 | 11.65 |
| 3.20 | Interpolation | 14.67 | 11.30 | 11.47 | 11.97 | 10.67 | 12.69 |
| 3.85 | Interpolation | 15.91 | 10.03 | 10.01 | 9.33 | 10.45 | 11.45 |
| 4.40 | Interpolation | 14.69 | 8.01 | 8.43 | 8.35 | 8.66 | 10.04 |
| 5.80 | Endpoint extrapolation | 16.52 | 10.55 | 11.26 | 10.52 | 9.16 | 12.16 |

Across all leave-one-intensity-out plants, the pooled median RMSE was 10.1127 degrees for W3, 10.1423 for W2, 10.4385 for B1, 10.1174 for B1r, 10.8361 for B2, and 14.4360 for W1. This secondary evaluation does not change the pre-fixed primary decision.

## Limitations and interpretation

The archive covers one species and one protocol family. Its tracked unilateral intensities end at 5.8 W/m², so the analysis does not evaluate the stated 7 W/m² upper range. The measurements are tip-segment angles, not whole-stem shape or curvature. The archive does not expose batch structure or ground-truth model parameters. The cluster-sandwich intervals are approximate local Wald intervals and do not include uncertainty from model selection or archive sampling.

W3's negative `c1` interval supports an intensity trend in the restoring coefficient within this parameterization. It does not establish a mechanism, and the fixed-threshold prediction test was negative. The result does not license replacing the group-mean curve for this archive, transferring W3 to other species or protocols, or making claims about auxin, proprioception, growth zones, circadian gating, or any other mechanism. A held-out prediction beating a mean-curve baseline would not establish a mechanism either.
