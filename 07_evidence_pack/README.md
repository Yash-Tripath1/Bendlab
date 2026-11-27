# BendLab evidence pack

This directory contains a no-refit evidence audit, reproducibility instructions,
and five figures regenerated from committed outputs. It was assembled on
2026-11-11. No source report, model, fit, legacy result, or input data outside
this directory was changed.

## Start here

- [`CLAIM_AUDIT.md`](CLAIM_AUDIT.md): quantitative-claim audit of the root
  [`README.md`](../README.md), [`docs/CURRENT_STATUS.md`](../docs/CURRENT_STATUS.md),
  and [`06_growth_coupling/RESULTS.md`](../06_growth_coupling/RESULTS.md).
- [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md): environment, commands, inputs,
  scope, and figure notes.
- [`requirements-evidence.txt`](requirements-evidence.txt): exact Python
  package versions used for this pack's audit and plots.

## Key reconciliation

The two `max_rate` counts answer different questions:

- **47/48** have a non-finite Phase A relative standard error under the saved
  residual-Jacobian sensitivity rule. This historical count is reproduced by
  the committed uncertainty output; it is not an erroneous count.
- **40/48** saved fitted caps exceed their own plant's largest raw adjacent-sample
  observed rate; **8/48** are at or below that descriptive rate. This is a
  separate observed-peak comparison, not the Phase A Jacobian test and not a
  proof that the fitted cap was active in the model trajectory.

The full per-plant reconciliation is in
[`outputs/identifiability_count.json`](outputs/identifiability_count.json).
The saved-fit, model-selection, Phase E harness, H4, and explicit simulator
checks are summarized in
[`outputs/committed_number_audit.json`](outputs/committed_number_audit.json).
No plant fit was rerun. The H4 reproduction is a simulation-and-clustering
reproduction only.

## Figures

All five PNGs are 300 dpi. Each has a matching source script in `figures/`.

| Figure | Contents | Main source |
|---|---|---|
| Figure | Contents | Main source |
|---|---|---|
| [`fig01_identifiability_rate_cap.png`](figures/fig01_identifiability_rate_cap.png) ([script](figures/fig01_identifiability_rate_cap.py)) | Saved `max_rate` fit versus each plant's raw observed adjacent-sample peak rate; 40 caps above and 8 at/below | Evidence-pack identifiability JSON; saved Fig1C fits and S13 angles |
| [`fig02_external_benchmark_rmse.png`](figures/fig02_external_benchmark_rmse.png) ([script](figures/fig02_external_benchmark_rmse.py)) | Phase E per-plant held-out RMSE distributions for W1, W2, W3, B1, B1r, and B2 (268 plants/model); the preregistered 9.73-degree reference is shown | `phase_e_w3_heldout_per_plant.csv` |
| [`fig03_intensity_transfer.png`](figures/fig03_intensity_transfer.png) ([script](figures/fig03_intensity_transfer.py)) | Median held-out RMSE for W1, W3, and B1 across the ten observed intensity groups; the fixed 9.73-degree reference is shown | `phase_e_w3_primary_by_intensity.csv` |
| [`fig04_growth_coupling_nulls.png`](figures/fig04_growth_coupling_nulls.png) ([script](figures/fig04_growth_coupling_nulls.py)) | Central 95% intervals and medians for four amended Task 4 null distributions in the eligible sample (n=209), against observed partial rho | `analysis_results_amended.json`, `amended_task4_null_rhos.csv` |
| [`fig05_zt9_transfer.png`](figures/fig05_zt9_transfer.png) ([script](figures/fig05_zt9_transfer.py)) | Paired per-plant held-out RMSE for six ZT9 plants: base scalar versus shared-clock model fitted without ZT9 | `clock_validation_shared_heldout.csv` |

Figure 2 boxplot fliers are hidden; boxes show the interquartile range and
whiskers use Matplotlib's 1.5-IQR convention. Figure 3 joins the ten group
medians with lines and does not show uncertainty intervals. Figure 4 is a
conditional null sensitivity, not a causal test. Figure 5 does not plot the
per-plant free-clock refit comparator (median 1.105 degrees); that is not the
same held-out comparison as the shared-clock model. Generated PNG and JSON
hashes are recorded in [`SHA256SUMS.txt`](SHA256SUMS.txt).
