# Quantitative-claim audit

**Review date:** 2026-11-11

**Scope:** all material numerical result claims in root `README.md`,
`docs/CURRENT_STATUS.md`, and `06_growth_coupling/RESULTS.md`.

**Method:** compare the stated definitions, rounded values, sample sizes, and
interpretations with the repository's committed tables, machine-readable
summaries, analysis code, and cross-workstream reports. This is an evidence
review, not a refit or a second full reproduction of every historical
pipeline. Source documents were not edited.

## Executive findings

1. **The 47/48 `max_rate` statement is reproducible as written when its
   estimand is named.** Phase A reports 47 non-finite relative standard errors
   from its residual-Jacobian sensitivity rule. A distinct raw observed-peak
   comparison gives **40/48 fitted caps above** each plant's maximum absolute
   adjacent-sample observed rate and **8/48 at or below** it. The second count
   neither invalidates nor replaces the first, and it does not by itself prove
   whether the fitted cap was active in the model trajectory. Phase E's
   smoothed-gradient peak-rate check is another, distinct procedure.
2. **The canonical fit, clock, design, model-selection, benchmark, growth-phase,
   and Phase E figures in the three documents match the saved evidence within
   their stated rounding.** The sources and important qualifications are
   itemized below.
3. **Keep benchmark generations distinct.** B0 W2 is 9.9707 degrees; the
   separate Phase E baseline harness reproduces W2 at 9.9781 degrees (delta
   0.00739, within its saved 0.05-degree tolerance). B0 W1 is 14.4072145335;
   the Phase E reproduction is 14.4072145385. These are separately labeled
   saved analyses, not conflicting estimates to average together.
4. **Simulation and inverse-model results require their conditions.** The
   approximately 44% neural-network `max_rate` error is from the
   12,000-sample `full_heldout_clean` evaluation; the 400,000-plant sweep
   supplies separate population-simulation evidence. Neither is an estimate
   of error on measured plants. The stem-shape gains are also model-class
   simulation results, not validation on measured stem curvature.
5. **Growth-angle analyses are conditional associations.** The length
   measurement geometry is not established by the archive. Task 4 nulls are
   pairing/projection sensitivities under stated assumptions, not causal
   tests. The report's 0.028-second setup timing is explicitly described as
   supplied/review-verified and not separately re-tested; the amended run time
   of 6.807 seconds is recorded in its saved JSON.

## Root `README.md`

Line references are to the checked-out root document.

| Location | Quantitative claim | Audit result and primary evidence |
|---|---|---|
| L50-L53 | Within-cluster parameter range retention is about 25-50%; Phase A flags `max_rate` for 47/48 Fig1C plants. | **Confirmed with definition.** The 400,000-plant summary reports median within-cluster IQR/full-range ratios: k 0.2495, tau 0.3542, `max_rate` 0.5021, phi0 0.2430. These round to roughly 25%, 35%, 50%, and 24% (the prose's 25-50% is approximate). The 47/48 count is the saved Phase A Jacobian/relative-SE criterion. See `01_canonical_bendlab/results/mega_sweep_summary.json`, `phaseA_summary.json`, and `phaseA_fit_uncertainty.csv`; the new two-criterion reconciliation is `outputs/identifiability_count.json`. |
| L57-L61 | 48 curves; median in-sample RMSE 1.80 degrees; median across-plant spread 8.58 degrees; LOBO median 11.75 degrees; six held-out ZT9 plants improve from 2.42 to 1.44 degrees. | **Confirmed.** Recalculation from `fit_fig1c.csv` gives medians 1.8011198 and 8.5824090 degrees, with 48 rows and 44 `at_bound == "[]"`. `phaseA_summary.json` gives LOBO median 11.7539055 degrees. `clock_validation_summary.json` gives static 2.4197848 and shared-clock held-out 1.4391919 degrees; all six per-plant rows improve. The shared clock is fitted without ZT9; this supports a held-out candidate, not a biological mechanism. |
| L73-L81 | B0 archive: 268 plants, 10 intensity groups from 0.7 to 5.8 W/m²; W1 14.41, B1 9.73, W2 9.97 degrees; late-window plateaus about 18-37 degrees. | **Confirmed as B0 values.** `benchmark_summary.json` and `PHASE_B0_REPORT.md` support the plant-held-out medians; the report's archived data audit lists the ten observed intensities and operational late-window range. The tracked CSV has maximum `light_i=5.8`; it contains no 7 W/m² group. W1's 14.41 and W2's 9.97 are rounded B0 figures. |
| L95-L99 | Five-segment model reduces to scalar at zeta=0; shape refinement cuts k error 46.8%, with `max_rate` error changing by about 1.1%. | **Confirmed with simulation-only scope.** The Workstream B audit reports exact reduction at zeta=0, 46.8% k reduction under its leakage-safe reference/query split, and about 1.1% change in `max_rate` error. Corrected in-population result is k 49.2%, tau -6.4%, `max_rate` +1.1%, phi0 +45.9%; with phi0 fixed, k reductions are 33.4% (60 degrees) and 36.7% (90 degrees). The report limits the result to simulated plants and this model class; it is not validation of real curvature measurements. See `03_workstream_B_shape_extension_audit/SHAPE_EXTENSION_AUDIT.md`. |
| L108-L114 | n=213 starting-length records among 268; early rate +2.12 deg/h per log unit (95% CI [0.66, 3.62]); latency HR 1.42 (95% CI [0.97, 2.06], p=0.068) on 190 at-risk plants; held-out ODE RMSE M0 10.25, M1a 10.41, M1d 10.35, M1c 10.29 degrees. | **Confirmed.** These match the current Phases B-C results and the censoring-aware Phase C latency addendum. They describe the historical starting-length/early-rate, latency, and model-comparison analyses, not the separate Task 3/4 interval-average-elongation analysis in `06_growth_coupling/RESULTS.md`. The associations do not establish mechanism. |
| L121-L125 | Phase D 80% power N: A 753, B 745, C 411; 90% target not reached by N=900 in A/B and is 569 in C. | **Confirmed.** These are the prudent half-pilot-slope simulation results in `growth_phase/PHASE_D_DESIGN_SIMULATION_RESULTS.md`, not observed sample sizes or a laboratory guarantee. |
| L131-L140 | Phase E W3 9.9968 degrees vs strict <9.73-degree primary threshold; B1 9.7347; W3-B1 median +0.0509 and mean -0.0419 degrees; c1 -0.484 (95% CI [-0.572, -0.396]). | **Confirmed.** `PHASE_E_RESULTS.md` and the saved W3 summary support all values. The fixed primary threshold was not met. The paired analysis does not distinguish W3 from B1; it is not a formal TOST equivalence test. The c1 interval supports a trend only within the fitted parameterization, not a mechanism. |
| L214 | Python 3.10 or later. | **Environment requirement, not a scientific result.** It is consistent with the project setup guidance; this evidence-pack run used Python 3.11.2. |

## `docs/CURRENT_STATUS.md`

| Location | Quantitative claim | Audit result and primary evidence |
|---|---|---|
| L25-L29 | `max_rate` uncertainty flag 47/48; 400,000-plant sweep; neural-network median error about 44% while other parameters are about 1-4%. | **Confirmed with evaluation conditions.** 47/48 is the Phase A Jacobian flag. The sweep's `median_within_cluster_iqr_frac_of_range` is 0.2495 (k), 0.3542 (tau), 0.5021 (`max_rate`), 0.2430 (phi0). The distinct `inverse_model_v2_eval.csv` `full_heldout_clean` row has n=12,000 and median relative errors k 2.07%, tau 1.62%, `max_rate` 44.69%, phi0 1.76%. At 1- and 2-degree noise the other parameters' errors rise substantially, so the 1-4% comparison must be understood as the clean held-out row. The sweep does not itself report the neural-network 44% metric. |
| L30-L38 | 48 fits, median RMSE 1.80, 44/48 not bound-pinned, LOBO 11.75; six ZT9 plants improve 2.42 to 1.44. | **Confirmed.** Same saved-fit, Phase A summary, and held-out clock sources as the README audit above. |
| L39-L46 | H1-H8 verdict summary; H4 ARI 0.442; H3 rare cliff edges; H8 adaptive policies do not beat random. | **Confirmed under the corrected follow-up criteria.** The H4 reproduction in `outputs/committed_number_audit.json` gives ARI 0.4416816743, rounded 0.442, below the 0.5 persistence threshold (6,000 simulated vectors; 6 clusters; population seed 21; KMeans seed 13). H3 uses a 64x64 grid: 20 of 8,064 adjacent edges (0.248%) exceed 5x the median adjacent behavioural distance; the maximum is 6.68x. H8 fixed-policy simulation reports success per 100 (n=500 per policy): random 89.4, fixed 83.4, greedy 88.6, Thompson 63.2. H1 range-retention medians are k 0.766, tau 0.976, `max_rate` 0.999, phi0 0.835; H2 reductions on the range basis are k +21.6 percentage points, tau -2.2, `max_rate` 0.0, phi0 -7.9, so only k improves. See `audit_followup_summary.json`. These are simulation/hypothesis verdicts, not observed-plant mechanism claims. |
| L48-L51 | 20 seedlings, 160-degree separation, 2:1 intensity ratio, about 96% correct mechanism selection. | **Confirmed.** Saved results give 72/75 = 96% pooled (25 simulated datasets for each true mechanism; correct fractions 1.00 physical, 0.88 transduced-source, 1.00 circumference). This is a simulation result. The control geometry is a chance-level control; this should not be read as a laboratory guarantee. See `exp_design_model_selection.csv` and `outputs/committed_number_audit.json`. |
| L52-L64 | External benchmark medians, 268 plants, 10 groups, 0.7-5.8 W/m², phi=90 degrees, LOIO 10.4-16.5 degrees, late plateaus 18-37 degrees, free-phi median 28.8, W2 9.97. | **Confirmed as B0 Workstream A.** Evidence is in `benchmark_summary.json`, `per_plant_calibration.csv`, and `PHASE_B0_REPORT.md`. It evaluates a declared W1 wrapper and empirical baselines on one tracked archive; it does not recover ground-truth parameters. The archived unilateral maximum is 5.8 W/m², not 7. |
| L65-L72 | Five segments; zeta=0 reduction; k reductions 46.8%, 49.2%, 33.4-36.7%; `max_rate` change about 1.1%. | **Confirmed with scope.** See the Workstream B audit. The 46.8% value is the leakage-safe split; 49.2% is the in-population corrected v3 result; 33.4% and 36.7% are fixed-phi simulation tests. These results do not establish real-plant curvature identifiability. |
| L73-L83 | n=213/268; +2.12 (95% CI [0.66, 3.62]); HR 1.42 (95% CI [0.97, 2.06], p=.068; n=190); ODE RMSE 10.25/10.41/10.35/10.29. | **Confirmed.** Same historical Phases B-C sources as the README row; not the later interval-average-elongation endpoint. |
| L84-L90 | Phase D 80% and 90% simulated power sample sizes. | **Confirmed.** See the README Phase D row; design simulation only. |
| L91-L100 | Phase E W3/B1 threshold, paired differences, c1 and interval. | **Confirmed.** See the README Phase E row; threshold result is negative and no equivalence or biological mechanism is established. |

## `06_growth_coupling/RESULTS.md`

### Task 1: match, fits, and measurement geometry (L5-L15)

**Confirmed from the amended JSON and source files.** The matched set is 213
of 268 trajectory plants. The saved fit table contains 536 rows: 268 `phi90`
and 268 `phi_free`; 213 matched plants have `phi_free` rows. Four fitted
`phi_free` targets are below their own observed starting angle and are excluded
from the eligible fitted-trajectory sample: 4/213 = 1.8779%, below the 5%
small-fraction threshold. The target distribution is min 0.000000003 degrees
(rounded in the report to approximately zero), p05 8.2744, q25 21.7566,
median 29.0155, q75 39.3883, p95 52.1025, max 95.0000 degrees. Observed
starting angles span -15 to +15 degrees, median +1 degree. The archived length
fields establish mm and mm/h, but not whether the measure is axial, vertical,
or another geometry; the report correctly presents geometry-dependent cases
as conditional. `analysis_results_amended.json` records `fit_refit=false`.

### Task 3: primary association and endpoint sensitivities (L19-L38)

The +0.10 absolute collapse cutoff, +0.20 material-positive-remainder cutoff,
and “about one-third of +0.603” comparison are operational analysis criteria,
not biological thresholds. The original association recomputes to rho
**+0.6025935**, with the source-reported 95% interval **[+0.521, +0.672]**
and two-sided residual-correlation t-approximation p **3.8096e-22**. The
source wording distinguishes the carried-forward interval from the new
recomputed estimate.

The preregistered total-angle-change-controlled table is confirmed (n=213;
plant-level 1,000-resample percentile bootstrap intervals):

| Association | rho | t-approximation p | 95% bootstrap interval |
|---|---:|---:|---:|
| Elongation vs late angle, controlling for theta(0), log intensity, log L0, and last-minus-first total angle change | +0.3419 | 4.0478e-7 | [+0.2008, +0.4646] |
| Starting length vs late angle with the same angle-change control | +0.0451 | 0.5167 | [-0.0766, +0.1797] |

The post-registration endpoint sensitivities also agree with `outputs/analysis_results.json`:

- Last-minus-first total-angle-change endpoint: elongation raw Spearman +0.4422,
  partial rho +0.5349 (p=6.0836e-17).
- Historical Phase C plateau-minus-start endpoint: raw +0.4874, partial +0.5956
  (p=1.4904e-21).
- Peak-excursion endpoint: raw +0.3720, partial +0.4731 (p=4.1422e-13);
  raw association with peak angle +0.4146.
- Post-registration controls: controlling for Phase C plateau-minus-start gives
  rho +0.1260 (p=0.0691; 95% interval [-0.0110, +0.2662]); controlling for peak
  excursion gives +0.4237 (p=1.6426e-10; [+0.2909, +0.5385]); starting length
  with peak excursion added gives -0.1233 (p=0.0754; [-0.2463, +0.0015]).

The reported p-values use the stated residual-correlation t approximation;
percentile intervals are plant-level bootstraps with ranks and OLS refit per
resample. Endpoint sensitivities were added after registration and do not
replace the primary endpoint. The two materially different endpoint controls
lead to different categories, which is why the report retains an overall
ambiguous verdict.

### Task 4: original and amended nulls (L42-L77)

The saved original run uses 213 matched trajectories, 1,557 recorded samples,
`dt=1/60` hour, end time 25.933 hours, seed 20261113, and 1,000 replicates per
geometry. The observed rho is +0.6025935. Its two null intervals match the
saved `analysis_results.json`:

| Original fitted-trajectory pairing null | Median rho | Central 95% interval | Replicates at/below observed |
|---|---:|---:|---:|
| Axial length | +0.0571 | [-0.0758, +0.1873] | 1,000/1,000 |
| Projected vertical height | -0.2481 | [-0.3602, -0.1261] | 1,000/1,000 |

The amended results in `analysis_results_amended.json` and
`amended_task4_null_rhos.csv` also match the report (1,000 draws per geometry):

| Null series | Sample | n | Observed rho | Axial median [2.5%, 97.5%] | Height median [2.5%, 97.5%] |
|---|---|---:|---:|---:|---:|
| Fitted-trajectory pairing | Full | 213 | +0.6026 | +0.0571 [-0.0758, +0.1873] | -0.2481 [-0.3602, -0.1261] |
| Fitted-trajectory pairing | Degenerate fits excluded | 209 | +0.6043 | +0.0593 [-0.0675, +0.1825] | -0.2420 [-0.3486, -0.1259] |
| Empirical-angle projection | Full | 213 | +0.6026 | +0.0602 [-0.0736, +0.1953] | -0.2156 [-0.3264, -0.0931] |
| Empirical-angle projection | Degenerate fits excluded | 209 | +0.6043 | +0.0623 [-0.0696, +0.1946] | -0.2073 [-0.3289, -0.0786] |

The fitted-pairing null uses seed 20261113; the empirical-angle null uses
20261115. All 1,000 values in each comparison are at or below the observed
rho in the saved summaries. The amended simulation runtime is 6.8068 seconds
(rounded in the report to 6.807). The report's 0.028-second single-batch setup
benchmark and “under one minute” estimate are explicitly marked as supplied
and not separately re-tested; they are not independently established by the
saved analysis JSON.

These are no-same-plant-pairing and conditional projection sensitivities under
an undocumented measurement geometry. They do not demonstrate a causal growth
mechanism. In particular, the empirical-angle resampling breaks plant-specific
pairing by design. The null comparison is not a pure measurement-geometry test.

### Task 5 and consistency notes (L81-L101)

The three equal-sized total-angle-change strata are each n=71. Their partial
rho and bootstrap intervals match the saved initial results:

| Stratum | Angle-change range (degrees) | rho | 95% bootstrap interval |
|---|---:|---:|---:|
| 1 | [-9.4, 20.3] | +0.1179 | [-0.1387, +0.3787] |
| 2 | [20.3, 32.7] | +0.5799 | [+0.3750, +0.7240] |
| 3 | [32.8, 59.7] | +0.3453 | [+0.1094, +0.5452] |

Task 5 was triggered by the post-registration endpoint-definition conflict,
not by the preregistered Task 3/Task 4 conditions alone. All three point
estimates are positive and two intervals exclude zero; the first remains
imprecise.

The W1 consistency number is the B0 per-plant held-out median
14.4072145335 degrees, rounding to 14.41 (two decimals) or 14.4072 (four
decimals). The separate Phase E harness gives 14.4072145385, a 4.98e-9-degree
difference. The archive contains 268 plants and ten intensities ending at
5.8 W/m²; the paper/archive upper-range discrepancy is noted in the B0 report.

## Audit boundary

The review checked committed numeric outputs and source documents; it did not
rerun model fitting or revise any of the three audited documents. Values in the
three source documents that are dates, H-labels, section numbers, DOI strings,
file names, or code/environment version requirements are not research-result
claims and are not scored as such. Where a source report itself says a timing
or performance fact was supplied and not retested, that limitation is retained
rather than upgrading it to a reproduced result.
