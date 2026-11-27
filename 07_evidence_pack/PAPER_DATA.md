# Paper data sheet

## 1. Data

### External unilateral-light archive

- The tracked archive contains 88,504 trajectory rows from 268 plants. Intensity groups and plant counts: 0.7 watts per square metre, 29 plants; 1.1, 32; 1.4, 28; 1.9, 33; 2.25, 15; 3.0, 33; 3.2, 22; 3.85, 20; 4.4, 25; 5.8, 31. Source: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `data_audit`.
- Median sampling interval: 0.07 hours. Missing values: 0. Duplicated plant-time rows: 0. Plants with multiple intensities: 0. Source: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `data_audit`.
- Range discrepancy: the earlier paper-stated unilateral range is 0.7 to 7.0 watts per square metre, but the tracked archive maximum is 5.8 watts per square metre. Whether a higher-intensity group was measured and excluded or never run cannot be determined. Sources: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `data_audit`; `02_workstream_A_external_benchmark/PHASE_B0_REPORT.md`.

### Canonical Fig1C curves

- Saved Fig1C fit rows: 48 plants. Source: `01_canonical_bendlab/results/fit_fig1c.csv`; measured source workbook: `01_canonical_bendlab/data/real/stem_angles_plosbiol2023_s13.xlsx`, sheet `Fig1C`.

### Growth length-paired subset

- Length-paired sample: 213 plants from 268 archive trajectories. Raw length rows: 246. Exact duplicate rows removed: 1. Unique length identifiers after deduplication: 245. Source: `growth_phase/outputs/phase_a_audit.json`; matched and trajectory counts also recorded in `06_growth_coupling/outputs/analysis_results.json`.

## 2. Model

- Rate equation: `tau * dr/dt = k * sin(deg2rad(phi(t) - theta)) - r`.
- Angle equation with rate saturation: `dtheta/dt = r_clipped`, where `r_clipped = clip(r, -max_rate, +max_rate)`. Source for both equations and the update order: `sim.py`.
- `k`: response gain, degrees per hour. Source: `sim.py`.
- `tau`: sensing lag, hours. Source: `sim.py`.
- `max_rate`: rate cap, degrees per hour. Source: `sim.py`.
- `phi0`: supplied static light direction, degrees, in the same angular frame as `theta`. Source: `sim.py`, `batch_simulate` interface and default light function.
- `theta` is measured in degrees from vertical and `phi` is the light direction in the same frame. The static-light check used phi = 90 degrees, initial angles theta0 = 5 and 40 degrees, k = 10 degrees per hour, tau = 2.2 hours, max_rate = 200 degrees per hour, dt = 1/60 hour, and duration 24 hours. The terminal angles were 90.687 and 90.376 degrees, respectively; the first rounds to 90.7 degrees. Sources: `sim.py`; `02_workstream_A_external_benchmark/PHASE_B0_REPORT.md`; `07_evidence_pack/outputs/committed_number_audit.json`.

Read-only command, with all numeric settings loaded from `07_evidence_pack/outputs/committed_number_audit.json` and the simulator imported from `sim.py`:

```bash
.venv/bin/python - <<'PY'
import json
import numpy as np
import sim

check = json.load(open("07_evidence_pack/outputs/committed_number_audit.json"))["root_simulator_frame_check"]
_, theta = sim.batch_simulate(
    np.array(check["k_degrees_per_hour"]),
    np.array(check["tau_hours"]),
    np.array(check["max_rate_degrees_per_hour"]),
    np.array(check["phi_degrees"]),
    t_end=check["duration_hours"],
    dt=check["dt_hours"],
    theta0=np.array(check["theta0_degrees"]),
)
print(theta[-1].tolist())
PY
```

## 3. Identifiability

- Jacobian criterion: 47 of 48 saved fits have non-finite `max_rate_se` and `max_rate_rel_se` values. `phase_a.py` sets the standard error to infinity when the residual-Jacobian column norm is below 1e-9. Sources: `01_canonical_bendlab/results/phaseA_fit_uncertainty.csv`; `01_canonical_bendlab/phase_a.py`; `01_canonical_bendlab/results/phaseA_summary.json`.
- Direct observed-peak criterion: in 40 of 48 plants, the fitted cap is above that plant's maximum absolute adjacent-sample observed rate; 8 of 48 are at or below the observed peak. Source: `07_evidence_pack/outputs/identifiability_count.json`; rate definition: `01_canonical_bendlab/features.py`, `peak_rate`.
- These criteria answer different questions. The paper will use the Jacobian count because it concerns local estimability, not merely the fitted cap's position relative to the observed peak. Sources: `01_canonical_bendlab/phase_a.py`; `01_canonical_bendlab/results/phaseA_fit_uncertainty.csv`; `07_evidence_pack/outputs/identifiability_count.json`.
- Median within-cluster range-retention fractions: k = 0.766, tau = 0.976, max_rate = 0.999, phi0 = 0.835. The criterion is at least 3 of 4 parameters retaining at least 20 per cent. Source: `01_canonical_bendlab/results/audit_followup_summary.json`, `H1_as_written`.
- The max_rate retention fraction of 0.999 follows from the cap not binding and is a consequence of that condition, not an independent finding. Sources: `01_canonical_bendlab/results/audit_followup_summary.json`; `01_canonical_bendlab/results/phaseA_summary.json`; `01_canonical_bendlab/docs/CURRENT_STATUS.md`; `01_canonical_bendlab/phase_a.py`.

## 4. In-sample fit and transfer

- Saved Fig1C median per-plant RMSE: 1.8011 degrees. Median between-plant spread: 8.5824 degrees. Source for both saved per-plant columns and their aggregation: `01_canonical_bendlab/results/fit_fig1c.csv`; derived aggregate check: `07_evidence_pack/outputs/committed_number_audit.json`.
- Leave-one-block-out median curve RMSE: 11.7539 degrees. Mean band coverage: 0.88065. Source: `01_canonical_bendlab/results/phaseA_summary.json`; related audit record: `docs/AUDIT_FOLLOWUP_RESULTS.md`.
- Held-out ZT9 transfer: median RMSE was 2.4198 degrees for the static base model and 1.4392 degrees for the shared-clock model across 6 plants; all 6 per-plant errors decreased. The shared clock was fitted without ZT9. Sources: `01_canonical_bendlab/results/clock_validation_summary.json`; `01_canonical_bendlab/results/clock_validation_shared_heldout.csv`.

## 5. External benchmark

- Phase E held-out medians, in degrees, across 268 plants per model: W1 = 14.4072, W2 = 9.9781, W3 = 9.9968, B1 = 9.7347, B1r = 10.0258, B2 = 10.9166. Source: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `primary_median_rmse_deg`.
- Evaluation settings: 268 plants, 5 folds, seed 42, runtime 224.2 seconds. Source: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`.
- Generation comparison: B0 W2 median = 9.9707 degrees and B1 median = 9.7347 degrees. The Phase E harness reproduces W2 at 9.9781 degrees, a delta of 0.00739 degrees within the saved 0.05-degree tolerance. These are results from two saved analyses of the same models; retain both with their generation labels and do not average them. Sources: `02_workstream_A_external_benchmark/workstream_a/outputs/benchmark_summary.json`; `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `baseline_reproduction_checks`; `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`.

## 6. Phase E

- Preregistered primary criterion: W3 median held-out RMSE must be strictly below 9.73 degrees. The threshold was fixed in advance; `primary_success` is false. Verdict: negative under this criterion. Sources: `growth_phase/PHASE_E_PREREGISTRATION.md`; `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`; `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`.
- Paired held-out differences, in degrees: W3 minus B1 median = +0.0509; 95 per cent bootstrap interval = [-0.1954, +0.2798], using 2,000 resamples; two-sided Wilcoxon p = 0.9185; W3 has higher RMSE for 141 of 268 plants. Source: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `paired_equivalence.W3_minus_B1`.
- W2 minus B1: median difference = -0.1766 degrees; two-sided Wilcoxon p = 0.1537. Source: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `paired_equivalence.W2_minus_B1`.
- W3 minus W1: median difference = -4.5256 degrees; two-sided Wilcoxon p = 1.3316e-26. Source: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `paired_equivalence.W3_minus_W1`.

### All-data W3 fit

Although the JSON keys are named `log_k`, `log_tau`, and `log_max_rate`, their saved estimates and intervals are transformed back to physical parameter scale; the accompanying `units` fields give the physical units. Intervals are approximate two-sided 95 per cent Wald intervals from a numerical plant-cluster sandwich covariance with finite-cluster correction and a t critical value; the saved fit has 268 clusters and Jacobian rank 5. Sources: `02_workstream_A_external_benchmark/workstream_a/phase_e_w3_equilibrium.py`, interval-construction code; `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `all_data_w3_fit.confidence_intervals`.

| Parameter | Estimate and 95 per cent interval | Units | Source |
|---|---:|---|---|
| k | 13.044 [11.859, 14.347] | degrees per hour | `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `all_data_w3_fit.confidence_intervals.parameters.log_k` |
| tau | 2.620 [2.307, 2.976] | hours | `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `all_data_w3_fit.confidence_intervals.parameters.log_tau` |
| max_rate | 9.121 [5.815, 14.307] | degrees per hour | `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `all_data_w3_fit.confidence_intervals.parameters.log_max_rate` |
| c0 | -0.433 [-0.574, -0.292] | log inverse hours at 1 watt per square metre | `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `all_data_w3_fit.confidence_intervals.parameters.c0` |
| c1 | -0.484 [-0.572, -0.396] | exponent per natural-log intensity | `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `all_data_w3_fit.confidence_intervals.parameters.c1` |
| gamma at 1 watt per square metre | 0.6485 [0.563, 0.747] | inverse hours | `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `all_data_w3_fit.confidence_intervals.parameters.gamma_at_1w_m2` |

- Model-implied equilibrium angle theta_eq: 16.25 degrees at 0.7 watts per square metre to 37.41 degrees at 5.8 watts per square metre. These are model-implied values, not measured equilibrium angles. Source: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `all_data_w3_fit.implied_by_intensity`; interpretation: `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`.
- Leave-one-intensity-out pooled median RMSE, in degrees: W1 = 14.4360, W2 = 10.1423, W3 = 10.1127, B1 = 10.4385, B1r = 10.1174, B2 = 10.8361. The 0.7 and 5.8 watts per square metre endpoint groups are extrapolations; interior groups are interpolation. Sources: `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`; `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_loio_per_plant.csv`; group-level results: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_loio_by_intensity.csv`.

## 7. The rate-limit anomaly

- W3 fitted max_rate: 9.1209 degrees per hour. Observed median peak smoothed rate: 19.1849 degrees per hour; 90th percentile: 35.3154 degrees per hour; maximum: 66.5714 degrees per hour. Smoothing uses a centred rolling mean over 5 observations, with nominal duration 20 minutes, followed by a time-based numerical gradient. Source: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_peak_rate_check.json`.
- Plants whose observed peak smoothed rate exceeds fitted max_rate: 266 of 268. Source: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_peak_rate_check.json`.
- Paper interpretation: treat W3 max_rate as an effective fitted smoothing rate, not as a physiological maximum. This describes what the fitted parameter represents in this model and is not a defect to correct. Sources: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_peak_rate_check.json`; `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`; `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`.

## 8. Growth coupling

- Original partial association: rho = +0.6026, with source-reported 95 per cent interval [+0.521, +0.672]. Source: `06_growth_coupling/outputs/analysis_results.json`, `task3.original_association_recomputed`; source-reported interval also documented in `06_growth_coupling/RESULTS.md`.
- Primary overlap test on n = 213 matched plants: rho = +0.3419, 95 per cent plant-bootstrap interval [+0.2008, +0.4646], two-sided residual-correlation t-approximation p = 4.05e-7. Sources: `06_growth_coupling/outputs/analysis_results.json`, `task3.elongation_vs_late_angle_with_total_change_control`; `growth_phase/outputs/phase_a_audit.json`, `matched_plants`.
- Original fitted-trajectory pairing null, n = 213 matched plants and 1,000 replicates per geometry: axial-length median rho = +0.0571, central 95 per cent interval [-0.0758, +0.1873]; projected vertical-height median rho = -0.2481, interval [-0.3602, -0.1261]. Source: `06_growth_coupling/outputs/analysis_results.json`, `task4_null`.
- Amended eligible-sample fitted-trajectory pairing null, n = 209: axial median rho = +0.0593, interval [-0.0675, +0.1825]; projected-height median rho = -0.2420, interval [-0.3486, -0.1259]. Source: `06_growth_coupling/outputs/analysis_results_amended.json`, `task4_amendment.fitted_trajectory_pairing_null.eligible_excluded`.
- Amended eligible-sample empirical-angle projection null, n = 209: axial median rho = +0.0623, interval [-0.0696, +0.1946]; projected-height median rho = -0.2073, interval [-0.3289, -0.0786]. Source: `06_growth_coupling/outputs/analysis_results_amended.json`, `task4_amendment.empirical_angle_projection_null.eligible_excluded`.
- Full-sample amendment sensitivities, n = 213: fitted-trajectory axial median rho = +0.0571, interval [-0.0758, +0.1873]; fitted-trajectory projected-height median rho = -0.2481, interval [-0.3602, -0.1261]; empirical-angle axial median rho = +0.0602, interval [-0.0736, +0.1953]; empirical-angle projected-height median rho = -0.2156, interval [-0.3264, -0.0931]. Source: `06_growth_coupling/outputs/analysis_results_amended.json`, full-sample fitted and empirical null summaries.

| Total-angle-change stratum | n | Partial rho | 95 per cent bootstrap interval | Source |
|---|---:|---:|---:|---|
| Lower | 71 | +0.1179 | [-0.1387, +0.3787] | `06_growth_coupling/outputs/analysis_results.json`, `task5.strata` |
| Middle | 71 | +0.5799 | [+0.3750, +0.7240] | `06_growth_coupling/outputs/analysis_results.json`, `task5.strata` |
| Upper | 71 | +0.3453 | [+0.1094, +0.5452] | `06_growth_coupling/outputs/analysis_results.json`, `task5.strata` |

- Overall verdict: ambiguous. A post-registration sensitivity controlling for the Phase C plateau-minus-start quantity gives rho = +0.1260, p = 0.0691, and 95 per cent interval [-0.0110, +0.2662]; this control contains the late-window outcome itself. The competing post-registration peak-excursion control gives rho = +0.4237, p = 1.64e-10, and interval [+0.2909, +0.5385]. Sources: `06_growth_coupling/RESULTS.md`; `06_growth_coupling/outputs/analysis_results.json`, `task3.post_registration_definition_sensitivity`.

## 9. Supporting analyses

- Phase C early bending rate: +2.12 degrees per hour per log L0 unit, 95 per cent interval [+0.66, +3.62]. Source: `growth_phase/outputs/phase_c_results.json`, `associations.rate02`.
- Phase C latency: Cox proportional-hazards estimate HR = 1.42 per log L0 unit, 95 per cent interval [0.97, 2.06], p = 0.068, with 185 events among 190 at-risk plants. Source: `growth_phase/outputs/phase_c_latency_cox.json`, primary at-risk adjusted model and counts.
- Phase C cross-validated median RMSE, in degrees: M0 = 10.2519, M1a = 10.4094, M1d = 10.3511; M0 is retained. Sources: `growth_phase/outputs/phase_c_results.json`, `cv_median_rmse_deg`; `growth_phase/PHASE_BC_RESULTS.md`.
- Phase D archive-like Design A interpolated sample size for 80 per cent power: N = 193.72 at beta_L = 2.12; N = 752.88 at beta_L = 1.06. These are design-simulation interpolations, not observed enrollment requirements. Source: `growth_phase/outputs/phase_d_power_early_rate.json`, `required_N_interpolated.A_archive_joint`.

## 10. What the paper must not claim

- No biological mechanism or causal direction for the growth-angle association. Sources: `06_growth_coupling/RESULTS.md`; `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`.
- No auxin, proprioception, circadian, or other mechanistic conclusion from these predictive or model-class analyses. Source: `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`.
- Do not state that W3 beats the B1 primary baseline or met the preregistered threshold. Sources: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`; `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`.
- Do not claim the archive's length measurement is axial length or vertical tip height; the geometry is undocumented. Source: `06_growth_coupling/RESULTS.md`, `task1_measurement_geometry`.
- Do not claim tracked unilateral-light data above 5.8 watts per square metre; the archived data audit records 5.8 watts per square metre as the maximum. Source: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `data_audit`.
- Do not describe fitted W3 max_rate as a physiological maximum. Sources: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_peak_rate_check.json`; `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`.
- Do not frame Phase E as a primary-threshold success. Source: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `primary_success`.

## Discrepancies

- **Unilateral intensity range:** the earlier paper-stated range extends to 7.0 watts per square metre, while the tracked archive maximum is 5.8 watts per square metre. The committed audit cannot establish whether a higher-intensity group was measured and excluded or never run. Keep the source documents unchanged and limit archive-based claims to the observed 0.7 to 5.8 watts per square metre. Sources: `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `data_audit`; `02_workstream_A_external_benchmark/PHASE_B0_REPORT.md`.
- **B0 versus Phase E W2:** the B0 plant-held-out W2 median is 9.9707 degrees, while the Phase E harness result is 9.9781 degrees, a difference of 0.00739 degrees within the saved 0.05-degree reproduction tolerance. These are separately saved analysis generations, not values to average or replace. Sources: `02_workstream_A_external_benchmark/workstream_a/outputs/benchmark_summary.json`; `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `baseline_reproduction_checks`; `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`.
- **Latency model label:** the paper request's phrase "conditional-logit latency" does not match the committed producer. `growth_phase/outputs/phase_c_latency_cox.json` and `growth_phase/PHASE_C_LATENCY_ADDENDUM.md` identify the analysis as a Cox proportional-hazards model. The HR, confidence interval, p value, risk-set size, and event count above come from that Cox output; use the Cox label unless the authors identify another analysis file.

No numerical entry in this sheet remains UNSOURCED.
