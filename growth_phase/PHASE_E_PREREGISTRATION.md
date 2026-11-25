# Phase E preregistration: intensity-dependent restoring balance

Written and committed before fitting the Phase E model. This plan is fixed before the W3 fit and evaluation. If an outcome is unexpected, it will be reported without changing the model, threshold, or analysis.

## Question and scope

The question is whether an intensity-dependent restoring coefficient in the scalar tip-angle model improves plant-held-out trajectory prediction on the 268-plant unilateral-light archive. The archive reports an approximately flat peak-rate association with intensity and a positive association between intensity and late-window angle. W3 therefore places intensity in the restoring term, not in the response gain.

This is a predictive analysis of one archive, one species, and one protocol family. It does not test a physiological mechanism. Circadian gating, wet-lab claims, and mechanism claims about auxin, proprioception, or growth zones are explicitly out of scope.

## Data and fixed evaluation protocol

The analysis uses the tracked `05_data_external/uni_trajectories.csv` file. The pre-existing data audit records 88,504 observations from 268 plants, ten intensity groups from 0.7 to 5.8 W/m², and one intensity per plant. Plant identities will remain intact across folds.

The primary endpoint is the median per-plant trajectory RMSE in degrees over all observed times for predictions made while each plant is held out. The five plant-level folds will be the existing intensity-stratified assignment from `phase_b0_kempinski_benchmark.py`, with seed 42. Each candidate is fitted on the other four folds. The fitting protocol will match the existing benchmark: every fourth observation is used in fitting, the simulator uses a one-minute integration step, each plant starts at its observed `theta(0)` with rate zero, and predictions are evaluated at every observed time.

The evaluation will reproduce W1, W2, B1, B1r, and B2 from the existing benchmark functions, without modifying that benchmark. It will report their reproduced primary endpoint values as a harness check. B1 is the fixed success threshold: W3 must have a median RMSE strictly below 9.73 degrees. A value of 9.73 degrees or greater is a negative result under this preregistration, including values that round to 9.73.

## Candidate W3 model

W3 uses the `sim_gamma.py` dynamics with a shared response gain and an intensity-dependent restoring coefficient. The physical direction of the side light is fixed at `phi_light = 90 degrees`; it is not fitted or replaced by an effective light direction. Let intensity `I` be in W/m² and define

`gamma(I) = exp(c0 + c1 * ln(I))`.

For angle `theta` in degrees and rate `r` in degrees per hour, the continuous-time equations are

`tau * dr/dt = k * sin(pi * (phi_light - theta) / 180) - gamma(I) * theta - r`

`dtheta/dt = r`, with `r` clipped to `[-max_rate, +max_rate]` after each lag update.

The model-implied equilibrium `theta_eq(I)` is the root in `(0, 90 degrees)` of

`k * sin(pi * (phi_light - theta_eq) / 180) = gamma(I) * theta_eq`.

Thus intensity changes the restoring balance and its model-implied equilibrium through `gamma(I)`, while `k` is shared across intensities. `gamma` is a phenomenological restoring coefficient, not a claim about a specific biological process. W3 will not use `phi_eff` as a biological equilibrium angle. In W2, `phi_eff(I)` remains the existing effective target-angle diagnostic only.

The global fit parameters are `k`, `tau`, `max_rate`, `c0`, and `c1`. `exp(c0)` is `gamma` at 1 W/m², and `c1` is its log-intensity exponent. Bounds will be `k` in `[0.01, 80]` degrees per hour, `tau` in `[0.05, 40]` hours, `max_rate` in `[0.5, 60]` degrees per hour, `exp(c0)` in `[0.001, 5]` per hour, and `c1` in `[-2, 2]`. The fitting initialization, optimizer, and maximum function evaluations will be specified in the new script and held fixed across folds.

For the global-parameter confidence intervals, W3 will also be fitted once to all 268 plants with the same fitting protocol. Approximate two-sided 95% Wald intervals will use a plant-cluster sandwich covariance in optimizer coordinates, with plants as the independent clusters and a finite-cluster correction `G / (G - p)`, where `G` is the number of plants and `p` is the number of fitted parameters. Intervals for exponentiated parameters will be transformed back to the original scale. `c1` will be called distinguishable from zero only if its 95% interval excludes zero. The all-data fit is for parameter reporting and does not replace the held-out primary evaluation.

## Comparisons and secondary endpoints

The primary results table will show W1, W2, W3, B1, B1r, and B2 median held-out RMSE side by side. It will also give the median held-out RMSE of each model within each intensity group, so the pooled result cannot conceal a group-level failure.

A leave-one-intensity-group-out evaluation will fit without each of the ten groups and predict the omitted group. Results at 0.7 and 5.8 W/m² will be flagged separately as endpoint extrapolation; the eight interior groups are interpolation. Per-intensity-group values and a pooled median will be reported for W1, W2, W3, B1, B1r, and B2.

The report will include the all-data W3 global parameters and confidence intervals, the implied `gamma(I)` and model-implied equilibrium by observed intensity group, the random seed, and measured script runtime. The success rule remains the fixed B1 threshold above; no alternate threshold will be selected after seeing results.

## Falsification and interpretation rules

The directional proposal is that the late-window angle rises with intensity because the restoring balance changes, rather than because response gain rises. Under this W3 parameterization, that direction corresponds to `c1 < 0` and an increasing model-implied equilibrium across intensity. A `c1` interval containing zero, a fitted direction that does not imply increasing model-implied equilibrium, or a W3 primary RMSE at or above 9.73 degrees will be reported as evidence against the proposal or its predictive success. No parameter or threshold will be retuned in response.

Even if W3 beats B1, the result will be limited to this archive, this species, and this protocol family. A held-out prediction that beats a mean-curve baseline is not evidence for a mechanism. `gamma` is phenomenological. No biological equilibrium, circadian, growth-zone, auxin, or proprioceptive mechanism will be inferred.

## Conditional supporting association analysis

Only if the W3 analysis runs to completion will a separate, non-dynamical association analysis be run. It will join the frozen trajectory and length-supplement files by `real_id`, remove only exact duplicate length rows, and use the 213 matched plants. The angle outcome is each plant's mean `theta` from 16 through 21 hours inclusive. Interval-average elongation rate is `(length_finish - length_start) / dt` in mm/h, and starting length is `length_start` in mm. Intensity is checked by comparing `light_intens / 100` with the trajectory `light_i`.

Both associations will use partial Spearman correlations. Variables will be converted to average ranks; partial correlations will be Pearson correlations between residuals after linear adjustment for ranked nuisance covariates. The elongation-rate association will adjust for ranked `theta(0)`, log intensity, and log starting length. The starting-length association will adjust for ranked `theta(0)`, log intensity, and ranked elongation rate. Two-sided 95% percentile intervals will use 1,000 plant-level bootstrap resamples with seed 7. The previously reported approximate magnitudes, elongation partial rho near `+0.60` and starting-length partial rho near `0.00`, are checks only. If they are not reproduced within sampling noise, the result will be reported without forcing agreement.

The length supplement provides one net elongation over the whole measurement interval, not a time-resolved growth rate. It will be treated as a proxy for growth vigour, not as a measured temporal rate profile. No dynamical model will be fitted in this supporting analysis.
