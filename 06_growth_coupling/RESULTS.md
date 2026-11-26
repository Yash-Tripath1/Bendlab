# Growth and angular-response coupling: results

## Task 1 and pre-simulation fit screen

**Measurement geometry is indeterminate from the repository.** The available files establish units but do not establish whether `length_start` and `length_finish` are axial length, vertical tip height, or another measurement. The Task 4 cases below are therefore conditional interpretations, not claims about the archive's actual measurement.

Before the amended Task 4 simulation, the matched `phi_free` fit targets had this distribution: **213 plants; min approximately 0, 5th percentile 8.27, 25th percentile 21.76, median 29.02, 75th percentile 39.39, 95th percentile 52.10, max 95.00 degrees**. Four fit targets were below their own starting angle, `phi_fit_deg < theta(0)`, so those fitted trajectories were flagged as degenerate under the amendment rule. That is **4 of 213, or 1.88%**, below the amendment's 5% “more than a small fraction” threshold. The four plants were excluded from the primary amended fitted-trajectory analysis; full-sample results are also reported. No per-plant fit was refit.

The fit file contains **536 rows**, with **268 plants in each mode** (`phi90` and `phi_free`), and has `phi_free` fits for all **213 matched plants**. The observed `theta(0)` range was **-15 to +15 degrees**, with median **+1 degree**. The fit distribution and flagged plant IDs are recorded in `outputs/analysis_results_amended.json` and were printed before the amended simulator calls.

The source wording is now quoted exactly in the amended preregistration: “Whether `length_start` was measured exactly at trajectory t = 0 cannot be verified from the archive files alone and is flagged as an assumption, consistent with the supplementary script's design.” This concerns timing, not measurement geometry. `length_est.py` computes `(length_finish - length_start) / dt`, reports millimetres and millimetres per hour, and describes no measurement procedure. The length CSV has values and column names but no geometry metadata.

## Question and analysis method

The question is whether interval-average elongation predicts late-window tip angle after accounting for angular response. The matched analysis uses **213 plants** from **268 trajectory plants**. The late window is the mean observed tip angle from **16 through 21 hours**, inclusive. The primary total-angle-change definition is each plant's last observed tip angle minus its first.

Partial Spearman correlation average-ranks variables, separately residualizes predictor and outcome on ranked covariates by OLS, then correlates the residuals. Two-sided p values use the residual-correlation t approximation. Bootstrap intervals are plant-level percentile intervals with ranks and regressions refit in each resample. These p values are approximations, not exact permutation tests.

The preregistered collapse and survival cutoffs remain **0.10 absolute** and **+0.20 material positive remainder**. The preregistration explains that +0.20 is about one third of the previously reported +0.603 association. These are operational decision thresholds, not values imported from a biological mechanism.

## Task 3: primary overlap test

The original partial association was reproduced at **rho = +0.6026**, with source-reported 95% interval `[+0.521, +0.672]`; the script's two-sided t-approximation p value was `3.81e-22`.

| Association with late-window angle | Partial rho | Two-sided p | 95% bootstrap interval | Controls |
|---|---:|---:|---:|---|
| Elongation, preregistered last-minus-first angle change | +0.3419 | `4.05e-7` | `[+0.2008, +0.4646]` | `theta(0)`, log intensity, log starting length, total angle change |
| Starting length, same angle-change control | +0.0451 | `0.5167` | `[-0.0766, +0.1797]` | `theta(0)`, log intensity, elongation, total angle change |

Under the preregistered primary endpoint definition, the elongation estimate **survives** the overlap test. The starting-length estimate is small and its interval includes zero.

### Post-registration endpoint-definition sensitivities

The last-minus-first angle-change definition did not match the supplied approximate review check. Reproduction checks showed that the review values were closer to peak excursion, defined as maximum angle minus `theta(0)`. Those endpoint-definition checks were added after preregistration and did not replace the primary estimate.

For last-minus-first total angle change, elongation's raw Spearman rho was `+0.4422` and its partial rho was `+0.5349` (`p = 6.08e-17`). For the historical Phase C definition, 16-to-21-hour mean angle minus `theta(0)`, the raw rho was `+0.4874` and partial rho `+0.5956` (`p = 1.49e-21`). For peak excursion, raw rho was `+0.3720` and partial rho `+0.4731` (`p = 4.14e-13`); raw Spearman against peak angle was `+0.4146`.

As a further post-registration sensitivity, controlling for the Phase C plateau-minus-start quantity gives elongation rho `+0.1260`, `p = 0.0691`, and 95% interval `[-0.0110, +0.2662]`, an ambiguous category. That control contains the late-window outcome itself. Controlling for peak excursion instead gives rho `+0.4237`, `p = 1.64e-10`, interval `[+0.2909, +0.5385]`, a surviving category. Starting length with peak excursion added gives rho `-0.1233`, `p = 0.0754`, interval `[-0.2463, +0.0015]`.

## Task 4: original fitted-trajectory permutation null

The initial Task 4 run used the committed full-curve `phi_free` fits and unmodified repository `sim.py` `batch_simulate`. It generated a batched trajectory set at a one-minute step (`dt = 1/60` hour), through **25.933 hours**, with **213 trajectories** and **1,557 recorded samples**. The simulation seed was **20261113**, with **1,000 replicates per geometry**. Length records and fitted trajectories were randomly reassigned within exact intensity groups, with fixed points allowed.

This null tests whether the association exceeds a **no-same-plant-pairing** null under the fitted angular-response distribution while preserving intensity-group structure. It also applies the axial or vertical-height measurement rule. It is therefore both a pairing test and a geometry sensitivity, not a geometry-only test. The two geometries were compared against the recomputed original partial rho, `+0.6026`.

| Initial fitted-trajectory null | Null median rho | Central 95% interval | Observed rho | Result |
|---|---:|---:|---:|---|
| Axial length | +0.0571 | `[-0.0758, +0.1873]` | +0.6026 | Above |
| Vertical tip height | -0.2481 | `[-0.3602, -0.1261]` | +0.6026 | Above |

Both nulls had **1,000 of 1,000** simulated values at or below the observed rho. The vertical-height projection is `H = L_axis * cos(theta)`, with `theta` measured from vertical. The cosine decreases as bending moves the tip away from vertical toward 90 degrees. This direction applies only under the height interpretation; the archive does not show that its length field is height. Under the axial interpretation, bending does not alter measured axial length.

The initial output files were preserved unchanged: `outputs/analysis_results.json` and `outputs/simulation_null_rhos.csv`.

## Task 4 amendment and amended nulls

The amendment was committed after the initial Task 4 run and before the amended rerun. It does not retroactively preregister the initial run. The original preregistration commit remains unchanged; the amendment is a later commit. The corrected evidence wording, conditional projection interpretation, degenerate-fit rule, and additional null are recorded in the amendment section of `PREREGISTRATION.md`.

The committed `sim.py` convention measures `theta` from vertical. A review-verified setup check used static physical light `phi = 90` degrees and `theta(0) = 5` degrees, reaching `theta = 90.7` degrees after 24 hours. The `batch_simulate` interface accepts scalar arrays `(k, tau, max_rate, phi0)` positionally and honours a per-plant `theta0` array; `theta(0)` values of 5 and 40 degrees were verified. Its default light function uses the supplied `phi0`. The helper `static_light` takes one argument, while `batch_simulate` expects a two-argument `light_fn(t, phi0)`, so the helper is not passed directly.

For the fitted `phi_free` Task 4 simulation, the committed fit vector is passed as `(k_fit, tau_fit, max_rate_fit, phi_fit_deg)`, with each `phi_fit_deg` treated as an effective equilibrium target, not as a new measurement of the physical lamp direction. The observed `theta(0)` array is also passed. The amended script calls the simulator in batches, not once per plant or per replicate. The review-verified setup benchmark is 0.028 seconds for a batch of 213 plants over 24 hours at `dt = 1/60` hour; 1,000 replicates for both interpretations are under one minute. These setup benchmark facts were supplied for the report and were not separately re-tested.

The fitted-trajectory permutation null was rerun for both the full sample and the eligible sample excluding the four degenerate fits. In addition, the empirical-angle projection null held each growth record fixed and resampled only observed angle trajectories within intensity groups. The same empirical angle draws were used for axial and vertical-height cases. The axial-versus-height contrast under those same draws isolates the projection contribution conditional on the observed growth records and intensity structure. Resampling curve identity still breaks plant-specific growth-angle pairing, so this remains a conditional sensitivity, not a causal test.

| Fitted-trajectory pairing null | n | Observed rho | Axial median (central 95%) | Height median (central 95%) | Result |
|---|---:|---:|---:|---:|---|
| Full sample | 213 | +0.6026 | +0.0571 `[-0.0758, +0.1873]` | -0.2481 `[-0.3602, -0.1261]` | Above in both |
| Degenerate fits excluded | 209 | +0.6043 | +0.0593 `[-0.0675, +0.1825]` | -0.2420 `[-0.3486, -0.1259]` | Above in both |

| Empirical-angle projection null | n | Observed rho | Axial median (central 95%) | Height median (central 95%) | Result |
|---|---:|---:|---:|---:|---|
| Full sample | 213 | +0.6026 | +0.0602 `[-0.0736, +0.1953]` | -0.2156 `[-0.3264, -0.0931]` | Above in both |
| Degenerate fits excluded | 209 | +0.6043 | +0.0623 `[-0.0696, +0.1946]` | -0.2073 `[-0.3289, -0.0786]` | Above in both |

Each amended distribution has **1,000 replicates per geometry**. The fitted-trajectory null retains seed **20261113**; the empirical-angle null uses seed **20261115**. All four amended comparisons are above their null upper bounds. The amended run took **6.807 seconds** total. A review-verified setup benchmark supplied for this work is **0.028 seconds** for one batch of 213 plants over 24 hours at a one-minute step, with 1,000 replicates for both interpretations under one minute; that benchmark was recorded, not rerun as a separate test.

The amended per-replicate values are in `outputs/amended_task4_null_rhos.csv`; the accompanying summary is `outputs/analysis_results_amended.json`. These are additional outputs and do not overwrite the initial Task 4 results.

## Task 5: within-group diagnostic

Task 5 was **not triggered by the preregistered rules alone**: the preregistered Task 3 category was `survives`, and both initial Task 4 geometry classifications were `above`. After preregistration, the endpoint-definition sensitivity extension produced conflicting categories, so Task 5 was run as a post-registration diagnostic, not as a preregistered trigger. Plants were split into three equal-sized groups by last-minus-first total angle change, with ties broken by `real_id`.

| Total-angle-change stratum | n | Total-change range (degrees) | Partial rho | 95% bootstrap interval |
|---|---:|---:|---:|---:|
| 1 | 71 | `[-9.4, 20.3]` | +0.1179 | `[-0.1387, +0.3787]` |
| 2 | 71 | `[20.3, 32.7]` | +0.5799 | `[+0.3750, +0.7240]` |
| 3 | 71 | `[32.8, 59.7]` | +0.3453 | `[+0.1094, +0.5452]` |

All three point estimates are positive, and two intervals exclude zero. This meets the stated robust-positive pattern rule; the first stratum remains imprecise.

## Overall interpretation and limitations

**Overall verdict: ambiguous.** The primary preregistered overlap estimate survives, and the observed rho is above both measurement-geometry null bounds under the original and amended analyses. The overall label remains ambiguous because the post-registration Phase C plateau-minus-start adjustment is ambiguous while the peak-excursion adjustment survives. The disagreement is not because either geometry null contains the observed rho.

These are conditional observational associations. They do not establish that growth causes bending, why the variables covary, or any mechanism. The archive's length geometry is undocumented. The matched sample is **213 of 268** trajectory plants. The outcome is a tip angle, not curvature. The fitted parameters are held fixed, with no refitting or propagation of fit-parameter uncertainty. The vertical-height case is a stylized projection sensitivity. The empirical angle resampling also breaks plant-specific pairing by design. No Phase E source document was edited.

## Task 7 consistency checks

The median W1 held-out RMSE from the committed per-plant held-out output is **14.4072145335 degrees**, which rounds to **14.41 degrees**. Use `14.41` for rounded paper summaries and reserve `14.4072` for a four-decimal table.

The tracked-Markdown scan found one exact `0.7 to 7 W/m2` range mention, in `02_workstream_A_external_benchmark/PHASE_B0_REPORT.md`, line 75. It attributes that range to the paper and immediately distinguishes the tracked archive's unilateral `light_i` range of **0.7 to 5.8 W/m2**. A separate scan found five lines mentioning a standalone `7 W/m2` value. These describe the plotted cutoff, uncertainty about a possible group, the Phase E report's stated upper range, and an archived discrepancy note. They do not claim that the tracked archive measured a unilateral group at 7 W/m2. No existing source document was edited.
