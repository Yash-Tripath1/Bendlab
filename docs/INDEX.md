# BendLab document index

This index maps the repository's tracked Markdown documents and user-facing
HTML pages. Data files, logs, generated figures, code, and archived binary
outputs are not enumerated individually; the [Research Map](RESEARCH_MAP.md)
identifies their locations and the evidence documents point to specific
sources.

## Start here

| Document | Use |
|---|---|
| [Root README](../README.md) | Concise project entry point and reading order |
| [Research map](RESEARCH_MAP.md) | Directory/section map, categorized root scripts, and evidence routes |
| [Current status](CURRENT_STATUS.md) | Canonical cross-workstream findings, withdrawals, and open questions |
| [Quickstart](QUICKSTART.md) | Fresh-clone installation, tests, and verified artifact regeneration |
| [Implementation status](IMPLEMENTATION_STATUS.md) | Implementation and evidence status by workstream |
| [Problem statement](../PROBLEM_STATEMENT.md) | Research question and H1-H8 criteria |
| [Clock and proprioception technical note](../sim_clock_gamma.md) | Candidate model implementation notes |
| [This index](INDEX.md) | Full tracked-document inventory |

## Working project documentation

| Document | Use |
|---|---|
| [Adaptive identification](ADAPTIVE_IDENTIFICATION.md) | Design specification for adaptive protocol selection |
| [Audit follow-up results](AUDIT_FOLLOWUP_RESULTS.md) | Numerical results and corrections from the external audit follow-up |
| [Audit response](AUDIT_RESPONSE_2026-10-16.md) | Response to the 2026-10-16 external audit |
| [Model v2 changes](CHANGES_2026-10-15.md) | Circadian and proprioception candidate changes and results |
| [Model v2 candidates](MODEL_V2_CANDIDATES.md) | Candidate model descriptions and evaluation status |
| [External validation record](CHANGES_2026-10-15_EXTERNAL_VALIDATION.md) | Historical 15 October validation notes, with contributor attribution retained |
| [Data contract](DATA_CONTRACT.md) | Measured and simulated data handling, legacy dataset provenance, and limitations |
| [Data sources](DATA_SOURCES.md) | Source datasets and candidate external data |
| [Explainer](EXPLAINER.md) | Project overview and reading sequence |
| [Explainer, part 2](EXPLAINER_PART2.md) | Simulation experiments, validation, and corrections |
| [Project briefing](PROJECT_BRIEFING.md) | Expanded project briefing and research context |
| [Full project overview](PROJECT_OVERVIEW.md) | Preserved longer version of the former root README |
| [Results round 0](RESULTS_ROUND0.md) | Model fitting, parameter degeneracy, corrections, and error log |
| [Results round 1](RESULTS_ROUND1.md) | H3-H8 analyses and independent audit |
| [Results round 2, ZT9](RESULTS_ROUND2_ZT9.md) | Diagnostics for the ZT9 model limitation |
| [Consolidation record](CONSOLIDATION_2026-11-26.md) | File changes, verification, deliberate non-fixes, and remaining duplication |

## Phase B0 workstream documents

| Document | Use |
|---|---|
| [Workstream A Phase B0 report](../02_workstream_A_external_benchmark/PHASE_B0_REPORT.md) | External benchmark methods, baselines, results, and limits |
| [Workstream A Phase E results](../02_workstream_A_external_benchmark/PHASE_E_RESULTS.md) | Preregistered W3 results and threshold verdict |
| [Phase E supporting analysis](../02_workstream_A_external_benchmark/PHASE_E_SUPPORTING_ANALYSIS.md) | Contextual archive associations and supporting outputs |
| [Phase B0 test log](../02_workstream_A_external_benchmark/TEST_LOG.md) | Historical commands and outcomes for the audit-fix package |
| [Workstream B shape audit](../03_workstream_B_shape_extension_audit/SHAPE_EXTENSION_AUDIT.md) | Audit of the submitted multi-segment shape extension |

## Growth-aware phototropism, Phases A to E

| Document | Use and preservation status |
|---|---|
| [Growth-phase guide](../growth_phase/README.md) | Historical Phases A-C package guide; Phases D and E are indexed below |
| [Phase A data audit](../growth_phase/PHASE_A_DATA_AUDIT.md) | Paired length and unilateral trajectory archive audit |
| [Phase A data audit v1](../growth_phase/PHASE_A_DATA_AUDIT_v1.md) | Frozen earlier report version; retained unchanged |
| [Phase B preregistration](../growth_phase/PHASE_B_PREREGISTRATION.md) | Gate 2 model family and adoption rule |
| [Phases B-C results](../growth_phase/PHASE_BC_RESULTS.md) | Current Gate 2 and Phase C results |
| [Phases B-C results v1](../growth_phase/PHASE_BC_RESULTS_v1.md) | Frozen earlier report version; retained unchanged |
| [Phases B-C results v2](../growth_phase/PHASE_BC_RESULTS_v2.md) | Frozen earlier report version; retained unchanged |
| [Phase C latency addendum](../growth_phase/PHASE_C_LATENCY_ADDENDUM.md) | Censoring-aware latency reanalysis specification |
| [Deviations and provenance](../growth_phase/DEVIATIONS_AND_PROVENANCE.md) | Audit deviations, provenance limits, and package history |
| [Phase D design plan](../growth_phase/PHASE_D_DESIGN_SIMULATION_PLAN.md) | Preregistered prospective design simulation plan |
| [Phase D design results](../growth_phase/PHASE_D_DESIGN_SIMULATION_RESULTS.md) | Sample-size and design simulation findings |
| [Phase E preregistration](../growth_phase/PHASE_E_PREREGISTRATION.md) | Preregistered W3 model and evaluation criteria |

## Archived packaging notes

| Document | Use |
|---|---|
| [Package inventory, 2026-10-23](archive/PACKAGE_README_2026-10-23.md) | Historical package map and provenance record |
| [Phase B0 fixes, 2026-10-23](archive/PHASE_B0_FIXES_2026-10-23.md) | Historical audit-fix summary and prior duplication recommendation |
| [Retired snapshot index, 2026-10-16](archive/SNAPSHOT_INDEX_2026-10-16.md) | Commit, recoverability, file count, result comparison, and unique-document move |
| [Validation run note](archive/CHANGES_2026-10-15_VALIDATION_RUN.md) | Unique snapshot document retained in the archive |

## Preserved and retired snapshots

The former root snapshot `01_canonical_bendlab/` has been retired from the
current checkout. Its provenance and Git-history recovery point are recorded
in the [retired snapshot index](archive/SNAPSHOT_INDEX_2026-10-16.md). The
`04_shape_extension_branch/` snapshot and `05_data_external/` package remain
present. Under `growth_phase/`, the `_v1` and `_v2` report snapshots remain
frozen. The workstream B v1 report and saved result remain historical
evidence; only the specified v1 script path was made repository-relative.
Audit response files listed above remain unchanged.

### Preserved shape-extension snapshot: `04_shape_extension_branch/`

| Document | Use |
|---|---|
| [Research note](../04_shape_extension_branch/docs/RESEARCH_NOTE_SHAPE_EXTENSION.md) | Preserved shape-extension rationale |
| [Shape extension](../04_shape_extension_branch/docs/SHAPE_EXTENSION.md) | Preserved model specification |
| [Shape extension results](../04_shape_extension_branch/docs/SHAPE_EXTENSION_RESULTS.md) | Preserved submitted results |

`05_data_external/` contains the packaged external trajectory CSV and no
Markdown document. The same trajectory file is also retained under
`growth_phase/data/00_Data/` as part of that package's checksummed inputs.

## User-facing HTML pages

| Page | Use |
|---|---|
| [Standalone project overview](../bendlab_about.html) | Browser-based project overview source |
| [Visual simulator](../bendlab_visual_simulator.html) | Browser-based simulator source |
| [Inverse-model demo](../bendlab_model_demo.html) | Browser-based inverse-model demonstration source |
| [Curve fitter](../bendlab_curve_fitter.html) | Browser-based curve-fitting tool source |
| [Published site index](index.html) | GitHub Pages entry page |
| [Published about page](about.html) | Site overview page |
| [Published model page](model.html) | Site inverse-model page |
| [Published fitter page](fitter.html) | Site curve-fitter page |
