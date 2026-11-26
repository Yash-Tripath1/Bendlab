# Preregistration: growth and angular-response coupling

**Status:** This document is committed before any new overlap, simulation, or within-group analysis described below. It is not an analysis result. The commit containing this file alone will not be amended.

## Task 1 finding: measurement geometry is not documented

The repository does not establish whether `length_start` and `length_finish` are stem-axis length, vertical tip height, hypocotyl length, or another measurement.

The packaged `growth_phase/data/07_Supplementary/length_est.py` computes:

```python
growth_speed = (length_df["length_finish"] - length_df["length_start"]) / length_df["dt"]
```

It labels the derived rate `[mm/hour]` and the start and finish summaries `[mm]`, but describes no measurement procedure or geometry. `growth_phase/PHASE_A_DATA_AUDIT.md` verifies the units with the exact wording: “Units verified from source code, not from column names: mm and mm/h per `length_est.py`.” It also states: “Whether `length_start` was measured exactly at trajectory t = 0 cannot be verified from the archive files alone and is flagged as an assumption, consistent with the supplementary script's design.” The packaged CSV supplies values and column names but no measurement metadata. `02_workstream_A_external_benchmark/PHASE_E_SUPPORTING_ANALYSIS.md` describes one net elongation over the full interval, not a geometric measurement definition.

Therefore Task 4 will be run under both candidate interpretations below. Neither is asserted to be the archive's actual measurement.

## Question and candidate explanations

The question is: **does interval-average elongation predict the late-window angle after accounting for the plant's own angular response?**

The three candidate explanations are:

1. **Algebraic or measurement coupling:** if the recorded length is vertical height, the angle changes the measured projection; or, under either interpretation, elongation may largely track the plant's total angular response.
2. **A genuine biological association between growth vigour and bending:** elongation carries information about late-window angle beyond overall angular response and the measured covariates.
3. **A statistical artefact of shared covariates:** the association is induced or materially altered by common dependence on initial angle, light intensity, or starting length.

These are competing explanations, not causal or mechanistic claims. No outcome will be described as establishing mechanism or causality.

## Data, variables, and fixed association method

Use the existing matched sample of 213 plants, joined by `real_id`, after the exact duplicate length row is removed as in the committed Phase E supporting analysis. Do not change or overwrite any source file or saved result.

- Late-window angle: each plant's mean observed tip angle from 16 through 21 hours inclusive.
- Interval-average elongation: `(length_finish - length_start) / dt`, in the archive's stated units of mm/h.
- Starting length: `length_start`, in the archive's stated units of mm.
- Total angle change: the last observed tip angle minus the first observed tip angle for each plant. The last recorded time is retained per plant; it is not replaced by the 16-21 hour mean.
- Peak angle for reproducing the exploratory check: the maximum observed tip angle in that plant's trajectory.
- Covariates: observed `theta(0)`, natural log of light intensity, and natural log of starting length. The overlap test adds total angle change as a fourth covariate.

Use the existing partial-Spearman procedure: average-rank the predictor, outcome, and each covariate; regress the ranked predictor and ranked outcome separately on an intercept and the ranked covariates by ordinary least squares; correlate the two residual vectors. For two-sided partial-correlation p values, use the residual-correlation t approximation with degrees of freedom `n - number_of_covariates - 2`. Report it as an approximation, not an exact permutation test. Percentile intervals use 1,000 plant-level bootstrap resamples with replacement, recomputing ranks and residuals within every resample.

## Task 3: overlap test, run before the simulation

Estimate the following on the observed 213-plant data:

1. Partial Spearman of interval-average elongation with late-window angle, controlling for `theta(0)`, log intensity, log starting length, and total angle change. Report the estimate, two-sided t-approximation p value, and 95% percentile interval from 1,000 plant-level bootstrap resamples.
2. Partial Spearman of log starting length with late-window angle, controlling for `theta(0)`, log intensity, interval-average elongation, and total angle change, with the same p-value and interval methods.
3. Raw Spearman and partial Spearman associations of elongation with total angle change. For the partial estimate, control for `theta(0)`, log intensity, and log starting length, and report its two-sided t-approximation p value. Also report raw Spearman checks against total angle change and peak angle to reproduce the exploratory values supplied in the task.

Operational interpretation of the primary overlap estimate:

- **Collapse toward zero:** absolute estimate at most 0.10 and its 95% interval includes zero. Treat the original late-angle association as explained by angular-response overlap for this predictive question.
- **Material positive remainder:** estimate at least +0.20 and the lower 95% interval bound is above zero. Treat it as surviving this overlap test.
- **Otherwise:** ambiguous. Report the values without calling the result collapse or survival.

The +0.20 threshold defines a material remainder as about one third of the previously reported +0.603 association. The interval and estimate will both be shown, regardless of category.

## Task 4: measurement-geometry null

Run 1,000 replicate datasets for each geometry interpretation. Use the committed `02_workstream_A_external_benchmark/workstream_a/outputs/per_plant_fullfit_diagnostic.csv`, `mode=phi_free`, joined by plant ID. Its full-curve fit parameters were fitted to each plant's own observed trajectory by the committed benchmark fitting code; no fit is rerun. The available output has a fit row for each archive plant, including the 213 matched plants. First generate one trajectory per matched plant with that plant's own fit vector `(k_fit, tau_fit, max_rate_fit, phi_fit_deg)` and its observed `theta(0)`. Then, in each replicate, permute the 213 length records relative to those fitted trajectories within exact light-intensity groups. Each trajectory and each length record is used once per replicate. This retains the fitted response distribution by intensity and breaks the same-plant pairing between fitted angular response and length record, as required for a null with no plant-level growth-bending association. In each permuted row, `theta(0)` comes from the fitted trajectory, while light intensity is shared by construction and length covariates come from the permuted length record.

Generate trajectories with the unmodified repository-root `sim.py` `batch_simulate`, using each fitted plant's observed `theta(0)`, static `phi_fit_deg`, and a one-minute integration step (`dt=1/60` hour). Simulate through the largest length interval, rounded up to the next minute. Use the simulated mean tip angle from 16 through 21 hours as the outcome. For each replicate and interpretation, recompute partial Spearman using the original-analysis covariates: trajectory `theta(0)`, log intensity, and log starting length. The central 95% null interval is the 2.5th and 97.5th percentiles using linear sample quantiles. Report the fraction of simulated estimates at or below the observed original partial rho and the number above it.

- **Axial-length interpretation:** treat the observed `length_start` and interval-average elongation as axial length and axial growth. Synthetic axial length changes linearly from `length_start` at the measured rate over the observed length `dt`; bending does not alter the measured length or rate.
- **Vertical-height interpretation:** assume a straight organ whose axis angle is measured from vertical, so projected tip height is `H(t) = L_axis(t) * cos(theta(t))`. For this sensitivity case only, infer the axial start and finish lengths as observed height divided by the cosine of the observed tip angle at the corresponding measurement time. Interpolate the observed trajectory angle at the recorded length `dt`; if `dt` exceeds that plant's final trajectory time, hold the last observed angle constant for this inversion. Assume linear axial growth between the inferred endpoints. In each replicate, project these axial lengths using the synthetic angle trajectory to obtain synthetic start and finish heights, then recompute interval-average height change. Use synthetic start height in the log-starting-length covariate. This is an explicit geometric sensitivity model, not a claim about the archive protocol.

The simulation seed is `20261113`; use `numpy.random.default_rng` and record the seed, replicate count, fit source, runtime, and both null distributions. Save the per-replicate rho values under `06_growth_coupling/outputs/`. Classify an observed estimate inside the inclusive null interval as consistent with measurement coupling under that interpretation. An estimate above the upper bound is above that geometry-only null; below the lower bound is below it and must be reported as surprising. Report both interpretations because Task 1 was indeterminate.

## Task 5: within-group check if needed

Run only if Task 3 is ambiguous, Task 4 is inconclusive, or the overlap and geometry results conflict, including disagreement between the two geometry interpretations. Sort plants by total angle change, breaking ties by `real_id`, and split into three equal-sized consecutive groups. Within each group estimate the partial Spearman of elongation with late-window angle, controlling for `theta(0)`, log intensity, and log starting length. Use 1,000 plant-level percentile-bootstrap resamples per group with seed `20261114`. Report group sizes and the total-angle-change range in each group. Treat this as a diagnostic, not a new causal test. A pattern is called robust within strata only if all three point estimates are positive and at least two of the three intervals exclude zero; otherwise report it as not robust or ambiguous, without treating nonsignificance as proof of no association.

## Seeds and reproducibility

- Task 3 bootstrap: 1,000 plant-level resamples, seed `20261112`.
- Task 4 measurement-geometry null: 1,000 replicate datasets per interpretation, seed `20261113`.
- Task 5, only if triggered: 1,000 plant-level bootstrap resamples per stratum, seed `20261114`.

The new analysis script must print every numeric result reported in `RESULTS.md`, write only within `06_growth_coupling/outputs/`, and record its runtime. It must not edit or regenerate any existing output.

## Overall verdict rule

- **Explained by coupling:** Task 3 meets the collapse rule. State whether the observed effect is also inside the axial and/or height null intervals. If Task 4 is above a geometry null, do not call geometry alone sufficient; the overlap conclusion still means elongation did not add material late-angle information after total response was accounted for.
- **Survives:** Task 3 meets the material-positive rule and the observed original partial rho is above the upper null bound under both geometry interpretations. If Task 5 is triggered, its within-stratum pattern must not contradict this conclusion.
- **Ambiguous:** every other combination, including disagreement between geometry interpretations or estimates in the pre-defined middle ranges.

## Task 7 consistency checks

Without changing source documents, calculate the median W1 held-out RMSE from the committed per-plant held-out output and report the value as a recommendation for paper text. Scan working documents for a statement that presents 0.7 to 7 W/m2 as the archive's measured unilateral range; distinguish a paper-reported range from the tracked archive range, which ends at 5.8 W/m2. Do not edit any existing source document.

## Amendments after the initial Task 4 run

**Chronology:** This amendment is added in a separate commit after the initial Task 4 simulation and before the amended Task 4 rerun. It does not alter or retroactively preregister the initial run. The original preregistration commit remains unchanged. The additional work below is explicitly post-registration.

### Correction to Task 1 source wording

The sentence quoted in the original first draft was a paraphrase presented as verbatim. The exact Phase A wording is: “Whether `length_start` was measured exactly at trajectory t = 0 cannot be verified from the archive files alone and is flagged as an assumption, consistent with the supplementary script's design.” This establishes uncertainty about timing, not measurement geometry. The repository still does not establish whether the length columns are axial lengths or vertical heights.

### Conditional interpretation of vertical height

`sim.py` defines `theta` in degrees from vertical and uses the light direction in the same angular frame. For a vertical-height interpretation only, the projection is `H(t) = L_axis(t) * cos(theta(t))`; as `theta` bends away from vertical toward 90 degrees, the cosine and projected vertical height decrease. Do not assign this direction to the archive's recorded `length_start` or `length_finish`, because their geometry is undocumented. The axial-length case is unaffected by this projection. Both interpretations remain in the analysis.

### Clarification and extension of Task 4 nulls

Keep the original fitted-trajectory, within-intensity permutation null. It breaks the same-plant pairing between observed growth records and fitted angular response while preserving intensity-group structure. It therefore asks whether the association exceeds a no-same-plant-pairing null under the fitted response distribution. In the vertical-height case the projection is applied too, so this null combines a pairing test with a geometry sensitivity; it does not isolate the projection effect on its own.

Add a cheaper empirical-angle projection null with 1,000 replicates and seed `20261115`. Keep each record's observed axial starting length and interval-average axial growth fixed. In each replicate resample only empirical angle trajectories within exact intensity groups, and apply the same trajectory draws to both the axial and vertical-height interpretations. For the vertical-height interpretation, infer axial endpoints from each observed height record and that plant's observed endpoint angles, then project those endpoints using the resampled angle trajectory. Report the axial-versus-height contrast under the identical draws as the geometry-only contrast conditional on the observed growth records and intensity structure. State that trajectory resampling still breaks plant-specific pairing; it is not a causal test. This null complements, and does not replace, the fitted-trajectory permutation null.

### Degenerate fitted-equilibrium rule

Before the amended simulation, report the distribution of `phi_fit_deg` among the 213 matched plants and compare each fitted equilibrium with that plant's observed `theta(0)`. Flag a fit when `phi_fit_deg < theta(0)`. Exclude flagged plants from the primary fitted-trajectory Task 4 analysis and report the count and excluded-sample results; do not silently drop them. Define “more than a small fraction” as more than 5 percent of the original matched sample. Show the full-sample result as well if this threshold is exceeded. For transparency, the amended report will show both full and excluded results regardless of whether the threshold is exceeded. Do not refit any source fit.

The original Task 4 seed remains `20261113` for the fitted-trajectory permutation null. The empirical-angle projection null uses seed `20261115`. Each null uses the fixed count of 1,000 replicates per geometry and sample definition.

### Simulator call details

Use `sim.batch_simulate` with the per-plant arrays `(k_fit, tau_fit, max_rate_fit, phi_fit_deg)` passed positionally, the per-plant observed `theta0` array, and the default light function. Do not pass the one-argument `static_light` helper as `light_fn`. This uses the fitted `phi_fit_deg` as each `phi_free` trajectory's effective target. The original collapse and survival thresholds, 0.10 absolute and 0.20 material positive remainder, remain unchanged; the original rationale that 0.20 is about one third of 0.603 remains in force.
