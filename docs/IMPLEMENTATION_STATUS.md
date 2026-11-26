# Implementation and evidence status

This page separates what is implemented in the repository from what has
been evaluated and what remains unvalidated. It is an index, not a new
analysis. Scientific values and verdicts are taken from the cited source
documents. The canonical cross-workstream summary is
[`CURRENT_STATUS.md`](CURRENT_STATUS.md).

## Workstream status

| Area | Implementation and status | Evidence and limits |
|---|---|---|
| Canonical scalar model | `sim.py` is the reference two-state model with `k`, `tau`, `max_rate`, and `phi0`. | The regression suite checks the rate-cap contract and scalar/batch/fitter parity. The model is phenomenological, not a physiological growth model. See [`../PROBLEM_STATEMENT.md`](../PROBLEM_STATEMENT.md) and [`../sim.py`](../sim.py). |
| Experiment Series 1 | The original simulation, measured-data fit, hypothesis tests, and post-audit corrections are documented. | H1, H3, H4, and H5 are supported with qualifications; H2, H7, and H8 are not supported as specified; the H6 global connectivity claim was withdrawn. H5 is an in-sample fit result and does not imply held-out generalisation. See [`CURRENT_STATUS.md`](CURRENT_STATUS.md), [`RESULTS_ROUND0.md`](RESULTS_ROUND0.md), [`RESULTS_ROUND1.md`](RESULTS_ROUND1.md), and [`AUDIT_FOLLOWUP_RESULTS.md`](AUDIT_FOLLOWUP_RESULTS.md). |
| Circadian-gating candidate | `sim_clock_gamma.py` and `clock_validation.py` implement and evaluate a candidate extension. | A shared clock fitted without ZT9 improves all six held-out ZT9 curves from median RMSE 2.42 to 1.44 degrees. This is a held-out candidate result, not a confirmed mechanism. See [`RESULTS_ROUND2_ZT9.md`](RESULTS_ROUND2_ZT9.md) and [`CHANGES_2026-10-15.md`](CHANGES_2026-10-15.md). |
| Phase B0 Workstream A | The external benchmark script, baselines, saved outputs, and report are present. | The W1 wrapper has median held-out RMSE 14.41 degrees versus 9.73 degrees for B1; W2 is a structural diagnostic. The benchmark is limited to the tested archive and wrappers. See [`../02_workstream_A_external_benchmark/PHASE_B0_REPORT.md`](../02_workstream_A_external_benchmark/PHASE_B0_REPORT.md). |
| Phase B0 Workstream B | The submitted five-segment model is preserved under the frozen `04_shape_extension_branch/` snapshot. The audit and corrected reruns are under `03_workstream_B_shape_extension_audit/`. | Curvature-informed twin refinement reduces `k` error by 46.8 per cent under the leakage-safe split, while `max_rate` remains effectively blind. This is a simulation identification result, not validation on real stem curvature. The v1 audit script path was made repository-relative without changing its analysis logic. See [`../03_workstream_B_shape_extension_audit/SHAPE_EXTENSION_AUDIT.md`](../03_workstream_B_shape_extension_audit/SHAPE_EXTENSION_AUDIT.md). |
| Growth Phases A-C | The paired archive audit, Gate 2 simulation study, Phase C association analysis, and censoring-aware latency addendum are documented. | There are 213 length-paired unilateral plants. The early-rate association is +2.12 degrees/hour per log-length unit (95% CI [0.66, 3.62]); the primary Cox latency estimate is HR 1.42 (95% CI [0.97, 2.06], p = 0.068). Tested length-aware variants do not improve held-out RMSE over M0. No mechanism is established. See [`../growth_phase/PHASE_A_DATA_AUDIT.md`](../growth_phase/PHASE_A_DATA_AUDIT.md), [`../growth_phase/PHASE_BC_RESULTS.md`](../growth_phase/PHASE_BC_RESULTS.md), and [`../growth_phase/PHASE_C_LATENCY_ADDENDUM.md`](../growth_phase/PHASE_C_LATENCY_ADDENDUM.md). |
| Growth Phase D | The prospective sample-size and design simulations are complete and reported. | Design simulation only, with no new plants or biological claim. For the prudent early-rate slope, 80 per cent power requires 753 plants in Design A, 745 in B, or 411 in C; the 90 per cent target is not reached by 900 in A or B and is 569 in C. Latency remains exploratory. See [`../growth_phase/PHASE_D_DESIGN_SIMULATION_PLAN.md`](../growth_phase/PHASE_D_DESIGN_SIMULATION_PLAN.md) and [`../growth_phase/PHASE_D_DESIGN_SIMULATION_RESULTS.md`](../growth_phase/PHASE_D_DESIGN_SIMULATION_RESULTS.md). |
| Growth Phase E | The W3 preregistration, saved benchmark outputs, primary results, and supporting archive analysis are present. | The primary median held-out RMSE is 9.9968 degrees, above the preregistered strictly-below-9.73-degree criterion. This is a negative threshold result. Paired results describe parity with B1, not formal equivalence or a biological mechanism. The fitted `max_rate` is not a measured physiological limit. See [`../growth_phase/PHASE_E_PREREGISTRATION.md`](../growth_phase/PHASE_E_PREREGISTRATION.md), [`../02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`](../02_workstream_A_external_benchmark/PHASE_E_RESULTS.md), and [`../02_workstream_A_external_benchmark/PHASE_E_SUPPORTING_ANALYSIS.md`](../02_workstream_A_external_benchmark/PHASE_E_SUPPORTING_ANALYSIS.md). |
| Browser tools and site | The standalone simulator, inverse-model demo, curve fitter, and generated Pages HTML are present. | The test suite checks source-to-site sync and, when Node.js is available, JavaScript/Python simulator parity. The inverse models are trained on synthetic populations; their use on real curves remains limited by training-range coverage. See [`../build_site.py`](../build_site.py) and [`CURRENT_STATUS.md`](CURRENT_STATUS.md). |
| Legacy inverse-model datasets | The inverse and instruction CSVs remain at their original paths. | `adaption_inverse_dataset.csv` is consumed by `train_inverse_model.py`, but the generation script is absent. `adaption_instruction_dataset.csv` has no current tracked consumer and incomplete provenance. Both are documented in [`DATA_CONTRACT.md`](DATA_CONTRACT.md) and were left unchanged. |

## Current open work

- Wet-lab validation of stimulus, protocol, growth, or mechanism claims.
- Direct testing of mechanistic straightening or equilibrium formulations
  on the multi-intensity external archive while keeping lamp geometry
  physical.
- A held-out head-to-head comparison of circadian gating and the
  biphasic-memory candidate, which is specified but not run.
- The harder H8 v2 adaptive design, which is specified but not run.
- Wider-range inverse-model training with uncertainty quantification for
  real measured curves.

These are open research tasks, not claims of implementation or completed
validation. See [`CURRENT_STATUS.md`](CURRENT_STATUS.md) for the canonical
status and [`INDEX.md`](INDEX.md) for the full document inventory.
