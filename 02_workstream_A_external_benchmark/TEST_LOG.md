# Phase B0 audit fixes: test log (2026-10-23)

Environment: fresh clone of github.com/Yash-Tripath1/Bendlab at
7f4e1481bc252fb88374f3d923ae6adac3e503a9, branch `phase-b0-audit-fixes`.
All commands run from the packaged layout with packaged files only.
No private paths, no symlinks, canonical main untouched, nothing pushed.

| # | Command (from repo root) | Outcome |
|---|---|---|
| 1 | `python 02_workstream_A_external_benchmark/tests_phase_b0.py` | PASS: 268 plants each with exactly one intensity; folds disjoint and stratified; corrected/buggy shape-feature semantics as expected |
| 2 | `python 04_shape_extension_branch/check_multiseg.py` | ALL CHECKS PASSED (exact reduction to sim.py, batch/single ~7e-15, determinism, cap contract) |
| 3 | `python 03_workstream_B_shape_extension_audit/workstream_b/shape_audit_corrected_v2.py` | PASS in ~12 s; primary results identical to v1 (k +49.2%, phi0 +45.9%); fixed-phi0 cases: 60 deg k +33.4 / tau +13.1 / max_rate −0.8; 90 deg k +36.7 / tau +5.2 / max_rate −0.3; no NaN in JSON (zero-range metrics serialised as null with note) |
| 4 | `python 02_workstream_A_external_benchmark/workstream_a/phase_b0_kempinski_benchmark.py` | PASS, 7.5 min approx. Reproduces the published headline numbers (W1 median held-out RMSE 14.41 deg; B1 9.73; W2 9.97); adds B1r (10.03), stratified bootstrap CI (3.64–4.72), and the common 4–22 h window population value (15.14 deg) |
| 5 | `python 02_workstream_A_external_benchmark/workstream_a/sensitivity_all_observations.py` | PASS, ~23 s. Every-observation refits match every-4th fits (W1 tau remains at its 0.05 h bound at both densities) |
| 6 | `git diff --stat 7f4e148 -- sim.py docs/ '*.html' docs/*.html` | Shows changes ONLY in 02_*, 03_* and PACKAGE_README.md. Root sim.py, site HTML and live docs/ unchanged on this branch |

Notes:
- Test A1 now asserts the actual condition: every `real_id` has exactly
  one unique `light_i`.
- The benchmark default `--fit-subsample` is 4 (as originally run);
  `--fit-subsample 1` and test 5 cover the all-observations case.
- Shape audit v2 supersedes v1 (unchanged on record): portable paths,
  added shared-phi0 = 90 deg case, null instead of NaN for zero-range
  parameters.
