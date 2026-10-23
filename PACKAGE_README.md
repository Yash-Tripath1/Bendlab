# BendLab complete code package

Built 2026-10-23. Contents map (workstreams kept separate, as specified):

## 01_canonical_bendlab/
The BendLab repository (scalar tip-angle model in sim.py, measured-data
fitter, simulation sweeps, inverse-model demos, documentation, website
sources). Identical to the public repository except one housekeeping
change pending commit: docs/CHANGES_15OCT_UMAID.md renamed to
docs/CHANGES_2026-10-15_VALIDATION_RUN.md (file naming by date and
subject; attribution is retained inside the document and in git history).

## 02_workstream_A_external_benchmark/
Phase B0 Workstream A: external benchmark of the scalar model.
PHASE_B0_REPORT.md (data audit, methods, held-out results, limitations,
transfer recommendation), workstream_a/phase_b0_kempinski_benchmark.py,
workstream_a/make_plots.py, workstream_a/outputs/ (per-plant metrics,
benchmark_summary.json, four figures), tests_phase_b0.py.
Run: python workstream_a/phase_b0_kempinski_benchmark.py [--data PATH]
(PATH optional; default is the packaged 05_data_external/uni_trajectories.csv.
About 7.5 min), then python workstream_a/make_plots.py

## 03_workstream_B_shape_extension_audit/
Phase B0 Workstream B: audit of the shape-extension submission.
SHAPE_EXTENSION_AUDIT.md, workstream_b/shape_audit_corrected_v2.py
(current portable corrected rerun; v1 retained on record unchanged),
workstream_b/corrected_audit_results_v2.json,
workstream_b/submitted_outputs/ (submitted v3 outputs, preserved).

## 04_shape_extension_branch/
The shape-extension study as submitted, preserved verbatim for
provenance: sim_multiseg.py, features_shape.py, check_multiseg.py,
shape_degeneracy.py, shape_degeneracy_v2.py,
shape_probe_exploratory.py, shape_identification_v3.py,
docs/SHAPE_EXTENSION.md, docs/SHAPE_EXTENSION_RESULTS.md,
docs/RESEARCH_NOTE_SHAPE_EXTENSION.md, shape result files.
Run: python check_multiseg.py ; python shape_identification_v3.py

## 05_data_external/
uni_trajectories.csv (unilateral-light trajectories, 2.1 MB). External
dataset, CC-BY-4.0. The full Zenodo archive ZIP is not tracked; this
single extracted CSV IS tracked in the repository, deliberately, so the
benchmark reproduces from a clean checkout.

## Provenance
- Canonical repository: github.com/Yash-Tripath1/Bendlab.
  b09ea5aa6003082b41d726b2b8499ded313dcb21 is the canonical SOURCE
  SNAPSHOT used for the Phase B0 analyses. The repository main has
  since advanced: 7f4e1481bc252fb88374f3d923ae6adac3e503a9
  (2026-10-23) added this Phase B0 package, and
  384e6881a14c5e167170098d4f65a0befacd4607 (2026-10-23) added the
  audit fixes, and documentation corrections have followed (main tip
  8860865 at the time of writing). Main is a moving target: this
  snapshot statement, not the tip hash, is the provenance claim.
- Shape-extension branch: github.com/umaidsiddiqui10/Bendlab,
  branch shape-extension,
  commit 494687940c3490d1af6e4ac36abf4a4a59adc7e5.
- External data: Kempinski et al. (2026), PNAS
  doi.org/10.1073/pnas.2614473123; archive Zenodo record 21206480,
  doi 10.5281/zenodo.21206480, md5 06d911cc56c6cf92d66af15304bb93f9.
- Measured-data context: Brooks J., Atamian S. H. & Harmer S. L.
  (2023), PLOS Biology, doi.org/10.1371/journal.pbio.3002344.
- Contributors: see 01_canonical_bendlab/README.md (Contributors) and
  01_canonical_bendlab/PROBLEM_STATEMENT.md (Authors), and the git
  histories of the repositories above.

## Separation of conclusions
Workstream A externally tests scalar tip-angle prediction on real
tip-angle data. Workstream B tests parameter identification inside the
shape-extension model class, in simulation. Neither is evidence for the
other; neither tests local curvature kappa(s,t) in real plants,
autostraightening, or zeitgeber-time gating.
