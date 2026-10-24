# Phase B0 audit fixes: change summary (2026-10-23)

**Base:** canonical main `7f4e1481bc252fb88374f3d923ae6adac3e503a9`
(verified current on 2026-10-23; it advances the analysis snapshot
`b09ea5aa6003082b41d726b2b8499ded313dcb21` by the Phase B0 package
commit). **Work location:** branch `phase-b0-audit-fixes` in a fresh
clone. **Status update:** those fixes are now ON main as commit
`384e6881a14c5e167170098d4f65a0befacd4607` (2026-10-23); the earlier
"prepared on a branch, not merged" wording is superseded. Live site
and published simulator/model remain untouched (verified, test log
item 6). A short documentation-corrections commit follows this one.

## Files changed
- `02_workstream_A_external_benchmark/workstream_a/phase_b0_kempinski_benchmark.py`
  Portable pathlib paths (packaged `01_canonical_bendlab` snapshot with
  repository-root fallback), `--data` and `--fit-subsample` arguments;
  adds the common 4–22 h metric window, the recentered group-mean
  comparator (B1r), and a stratified-by-intensity bootstrap sensitivity.
- `02_workstream_A_external_benchmark/workstream_a/sensitivity_all_observations.py` (new)
  Every-observation refit sensitivity; W1/W2 results unchanged, tau
  bound persists at full observation density.
- `02_workstream_A_external_benchmark/workstream_a/make_plots.py`
  Unchanged code; verified working against the portable benchmark module.
- `02_workstream_A_external_benchmark/tests_phase_b0.py`
  Portable paths; `test_each_plant_has_one_intensity` now actually
  asserts one unique `light_i` per `real_id`.
- `02_workstream_A_external_benchmark/PHASE_B0_REPORT.md`
  W1 corrections: wrapper stated as an addition, not the published
  model; max_rate 20 deg/h described as inactive/unidentified (left at
  its initial value, cap never binds at k(I) peak about 2.8 deg/h),
  not a boundary solution; tau bound labelled unresolved model-fit
  behaviour with the 16-minute fit spacing stated; equilibrium stated
  as theta = phi with the precise overshoot limitation (cannot turn
  back below 90 deg); "steady state" replaced by operational
  late-window (16–21 h) plateau; common-window forecast comparison
  (calibration 51.1 vs population 15.1 deg on 4–22 h); diagnostic
  described as downsampled; bootstrap labelled unstratified with
  stratified sensitivity; conclusion narrowed to the tested wrapper on
  this assay and explicitly not invalidating the earlier Brooks-assay
  fits.
- `03_workstream_B_shape_extension_audit/workstream_b/shape_audit_corrected_v2.py` (new; v1 preserved)
  Portable paths, added shared-phi0 = 90 deg known-input case (60 deg
  retained as sensitivity), zero-range metrics serialised as JSON null
  with explanation instead of NaN.
- `03_workstream_B_shape_extension_audit/SHAPE_EXTENSION_AUDIT.md`
  Added the 90 deg case (k +36.7%, tau +5.2%, max_rate −0.3%);
  k/tau/max_rate reporting separated from phi0 throughout.
- `02_workstream_A_external_benchmark/TEST_LOG.md` (new), this file.
- `PACKAGE_README.md`: build date corrected to 2026-10-23; provenance
  now distinguishes the b09ea5a analysis snapshot from current main;
  data tracking corrected (full Zenodo ZIP untracked; the 2.1 MB
  extracted CSV is tracked for reproducibility).

## Remaining limitations
- The Kempinski archive remains cleaned tip-angle data only: no raw
  marker coordinates, undocumented `real_id` batch fields, and the
  paper-vs-archive intensity discrepancy (stated up to 7 W/m2; archived
  maximum 5.8 W/m2) is unresolved and still flagged for the authors.
- No image-derived centerlines exist in either workstream; nothing here
  tests kappa(s,t), ZT gating, or autostraightening, and the corrected
  reports state this.
- Benchmark fits still default to every-4th-observation fitting for
  runtime; the sensitivity check shows this does not drive any result.

## Package size / duplication (for approval)
Clone size 88 MB, of which: canonical results 26 MB, duplicated
canonical snapshot `01_canonical_bendlab` 28 MB (the repository already
contains the same code at root), shape branch snapshot 2.5 MB, packaged
dataset 2.1 MB. Recommendation: keep reports, scripts and tests in the
repository (small); move the duplicated canonical snapshot (01_), the
shape-branch snapshot (04_) and the dataset (05_) to a versioned
GitHub Release asset or archive repository at the next release, and
reference them by commit SHA/DOI from the README. Nothing was deleted:
this decision needs approval.

## Decision status
(a) Merging the audit fixes to main: DONE (commit 384e688, above).
(b) The release/archive relocation above: still open, needs approval.
Nothing has been deleted.
