# Phase E supporting associations: elongation and late-window angle

## Question and data

This non-dynamical supporting analysis estimated the association of interval-average stem elongation rate and starting length with the late-window tip angle. It followed the conditional analysis plan in `growth_phase/PHASE_E_PREREGISTRATION.md` and did not fit a simulator or other dynamical model.

The script joined the frozen unilateral trajectory file to the frozen length supplement by `real_id`. It removed one exact duplicate length row (`11_11_L_5`) after confirming that its values matched, then retained 213 plants with paired measurements from the 268-plant trajectory set. The conversion `light_intens / 100` matched trajectory intensity for every joined plant.

The outcome was each plant's mean angle from 16 through 21 hours inclusive. Interval-average elongation was `(length_finish - length_start) / dt` in mm/h. Starting length was `length_start` in mm. Each association was estimated as a partial Spearman correlation by ranking the variables, linearly residualizing predictor and outcome on the ranked covariates, and correlating the residuals. Two-sided 95% percentile intervals used 1,000 plant-level bootstrap samples with seed 7.

## Results

| Association with late-window angle | Partial rho | 95% bootstrap CI | Covariates |
|---|---:|---:|---|
| Interval-average elongation rate | +0.603 | [+0.521, +0.672] | `theta(0)`, log intensity, log starting length |
| Starting length | -0.002 | [-0.136, +0.125] | `theta(0)`, log intensity, interval-average elongation rate |

The estimates are consistent with the pre-stated approximate checks of elongation partial rho near +0.60 and starting-length partial rho near 0.00. The interval for the starting-length association includes zero. These are conditional associations in the matched subset and do not establish direction of causality or mechanism.

## Previously measured intensity trend

As a consistency check on the interpretation of `c1`, the script also recomputed the previously measured association between log intensity and late-window angle in the 213 length-paired plants. The partial Spearman rho was +0.498, with a two-sided t-approximation p value of 1.44e-14, controlling for ranked `theta(0)`, interval-average elongation rate, and log starting length. This contextual archive association is not a new result from the W3 fit.

For the full 268-plant archive, the per-intensity medians of the 16-21 hour angle mean were:

| Intensity (W/m²) | Plants | Median angle (degrees) |
|---:|---:|---:|
| 0.70 | 29 | 18.56 |
| 1.10 | 32 | 22.41 |
| 1.40 | 28 | 23.85 |
| 1.90 | 33 | 24.22 |
| 2.25 | 15 | 22.84 |
| 3.00 | 33 | 27.72 |
| 3.20 | 22 | 28.06 |
| 3.85 | 20 | 24.77 |
| 4.40 | 25 | 34.54 |
| 5.80 | 31 | 33.60 |

The exact endpoint medians under this definition are 18.56 and 33.60 degrees, rather than the earlier approximate summary of about 22 to 30 degrees. The intensity-specific medians are not strictly monotonic. The positive adjusted association and the endpoint increase are retained as observed; no grouping or outcome definition was changed to force the earlier approximation.

## Limitations and scope

The length supplement gives one net elongation over the full measurement interval. It does not provide a time-resolved growth rate, so the calculated value is an interval average and a proxy for growth vigour. The length interval may differ from the angle trajectory window. The analysis applies only to plants with a length record and does not resolve growth-zone location, auxin, proprioception, circadian effects, or other mechanisms.

The committed script is `02_workstream_A_external_benchmark/workstream_a/phase_e_supporting_associations.py`. Its machine-readable output and joined per-plant table are `workstream_a/outputs/phase_e_supporting_associations.json` and `workstream_a/outputs/phase_e_supporting_associations_plants.csv`.
