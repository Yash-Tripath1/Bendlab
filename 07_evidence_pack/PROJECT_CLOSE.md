# Project close

## What was asked

Can the parameters of the four-parameter tropism model be recovered from observed stem-angle trajectories, and does adding an intensity-dependent restoring term improve plant-held-out prediction? The model parameters and equations are defined in `PROBLEM_STATEMENT.md` and `sim.py`; the restoring-term question was preregistered in `growth_phase/PHASE_E_PREREGISTRATION.md`.

## What was found

The local Jacobian criterion flags `max_rate` as not estimable in 47 of 48 Fig1C curves (`results/phaseA_summary.json`; `results/phaseA_fit_uncertainty.csv`; `phase_a.py`). In-sample median per-plant RMSE was 1.8011 degrees against a median between-plant spread of 8.5824 degrees (`results/fit_fig1c.csv`; derived check in `07_evidence_pack/outputs/committed_number_audit.json`). Transfer was weaker: leave-one-block-out median curve RMSE was 11.7539 degrees (`results/phaseA_summary.json`). On the plant-held-out external benchmark, W1 had median RMSE 14.4072 degrees and the B1 group-mean baseline 9.7347 degrees across 268 plants (`02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `primary_median_rmse_deg`; `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`).

The preregistered W3 model had median RMSE 9.9968 degrees, above its fixed, strict-below-9.73-degree threshold; the criterion was not met and no parameter or threshold was retuned (`02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`; `growth_phase/PHASE_E_PREREGISTRATION.md`; `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`). Its paired median difference from B1 was +0.0509 degrees, with a 95 per cent percentile-bootstrap interval of [-0.1954, +0.2798] degrees across 268 paired plants. The interval spans zero. The held-out comparison is reported as parity with B1, not superiority or formal equivalence (`02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `paired_equivalence.W3_minus_B1`; `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`).

## What the direction of evidence was

The fitted restoring exponent `c1` was -0.484, with a 95 per cent interval of [-0.572, -0.396], excluding zero. The model-implied equilibrium angle rises from 16.25 degrees at 0.7 watts per square metre to 37.41 degrees at 5.8 watts per square metre (`02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `all_data_w3_fit`; `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`). This directional signature belongs to the fitted parameterization. With parity in prediction, it is not a validated mechanism.

## What was corrected during the work

The preregistered W3 threshold miss is reported as a negative result under its fixed criterion, without retuning (`growth_phase/PHASE_E_PREREGISTRATION.md`; `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`). In the growth-coupling analysis, the original partial association was +0.6026 and the primary overlap estimate was +0.3419 after total angle change was added to the controls. These are adjusted observational associations, not a causal effect (`06_growth_coupling/outputs/analysis_results.json`, `task3`; `06_growth_coupling/RESULTS.md`). An earlier latent growth-mechanism claim is not supported by these outputs and is not carried forward: Phase C did not fit the growth-generated candidate to start/finish lengths, and the coupling report states that its observational analyses establish no mechanism (`growth_phase/PHASE_BC_RESULTS.md`; `06_growth_coupling/RESULTS.md`).

## What is not claimed

The analyses establish no mechanism or causal direction, and support no circadian, auxin, proprioceptive, or growth-zone claim. `max_rate` is not interpreted as a physiological maximum. The tracked unilateral-light archive ends at 5.8 watts per square metre, so no result is claimed above that range. W3 is not claimed to be superior to the group-mean baseline (`02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`; `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `data_audit`; `06_growth_coupling/RESULTS.md`).

## What the next study would need

A next study needs repeated length measurements within each plant, length resolved over time, curvature measurements rather than tip angle alone, and light conditions beyond the archived maximum. These measurements are not present here: the length supplement supplies interval-average start/finish values, the external benchmark contains tip angles rather than curvature or raw marker coordinates, and the tracked intensity maximum is 5.8 watts per square metre. Further analysis of this archive cannot recover measurements that were not collected (`growth_phase/PHASE_A_DATA_AUDIT.md`; `06_growth_coupling/RESULTS.md`; `02_workstream_A_external_benchmark/PHASE_B0_REPORT.md`; `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_summary.json`, `data_audit`).
