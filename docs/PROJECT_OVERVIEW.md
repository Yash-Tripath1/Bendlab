# BendLab

**Parameter identifiability in a minimal model of phototropic stem bending**

BendLab asks what stem-angle trajectories can reveal about a plant's
internal parameters. Its canonical model is a two-state, four-parameter
phenomenological simulator. The project combines simulation experiments,
fitting to published sunflower trajectories, external benchmarking,
shape-aware parameter-identification tests, and growth-aware analyses.

## Where to start

1. Read this overview, then the canonical cross-workstream summary in
   [`docs/CURRENT_STATUS.md`](CURRENT_STATUS.md).
2. Use [`docs/INDEX.md`](INDEX.md) for the document inventory and
   [`docs/IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) for
   implementation and evidence status.
3. See [`PROBLEM_STATEMENT.md`](../PROBLEM_STATEMENT.md) for the original
   research question and H1-H8 criteria, and [`sim.py`](../sim.py) for the
   canonical model implementation.
4. Follow the verified newcomer workflow in
   [`docs/QUICKSTART.md`](QUICKSTART.md).

## Canonical model

The model tracks stem angle `theta` and bend rate `r` under light direction
`phi(t)`:

```text
tau * dr/dt = k * sin(phi(t) - theta) - r
r_clipped   = clip(r, -max_rate, +max_rate)
dtheta/dt   = r_clipped
```

The four parameters are response gain `k` (degrees/hour), sensing lag `tau`
(hours), maximum bend-rate parameter `max_rate` (degrees/hour), and light or
effective target angle `phi0` (degrees). In the numerical update, the rate
first relaxes toward the stimulus, is then clipped, and the angle is updated.
`phi0` is not automatically the physical lamp angle when the scalar model is
used as an empirical fit. The model is a minimal phenomenological
representation, not a physiological model of auxin transport, growth zones,
or whole-plant structure. See [`sim.py`](../sim.py),
[`PROBLEM_STATEMENT.md`](../PROBLEM_STATEMENT.md), and the data contract in
[`docs/DATA_CONTRACT.md`](DATA_CONTRACT.md).

## Experiment Series 1

Experiment Series 1 studies identifiability in the scalar model and tests
hypotheses H1-H8. The results support parameter-behaviour degeneracy: within
behavioural clusters, parameter ranges retain 25-50 per cent of the full
sampled range. The rate parameter `max_rate` is unidentifiable when its cap
does not bind; the per-fit analysis flags this for 47 of 48 measured
`Fig1C` plants. These are model and dataset-specific findings, not claims
that the same parameters or mechanism have been established in living
plants.

The model fits the 48 measured trajectories in-sample with median RMSE
1.80 degrees, compared with 8.58 degrees median across-plant spread, while
leave-one-block-out median RMSE is 11.75 degrees. A shared circadian-gating
candidate improves all six held-out ZT9 curves from median RMSE 2.42 to
1.44 degrees; this is a candidate extension supported by a held-out test,
not a confirmed biological mechanism. In the post-audit H1-H8 record, H1,
H3, H4, and H5 are supported with their stated qualifications; H2, H7, and
H8 are not supported as specified; the global connectivity claim H6 was
withdrawn. See [`docs/CURRENT_STATUS.md`](CURRENT_STATUS.md),
[`docs/RESULTS_ROUND0.md`](RESULTS_ROUND0.md),
[`docs/RESULTS_ROUND1.md`](RESULTS_ROUND1.md),
[`docs/RESULTS_ROUND2_ZT9.md`](RESULTS_ROUND2_ZT9.md), and
[`docs/AUDIT_FOLLOWUP_RESULTS.md`](AUDIT_FOLLOWUP_RESULTS.md).

## Phase B0 external benchmark

Phase B0 Workstream A evaluates the scalar model on 268 independent
unilateral-light trajectories from the Kempinski et al. (2026) archive,
covering 10 intensities from 0.7 to 5.8 W/m2. In the benchmark, W1 fixes the
lamp direction at 90 degrees and puts intensity in an added gain wrapper.
Its median held-out RMSE is 14.41 degrees, versus 9.73 degrees for the B1
intensity-group-mean baseline. The W2 intensity-dependent effective-angle
model is a structural diagnostic, not a proposed mechanism; its median is
9.97 degrees. The report notes that measured late-window plateaus are around
18-37 degrees, so the scalar `phi0` acts as an empirical effective angle in
this assay rather than identifying the physical lamp direction. This is a
benchmark of the stated wrappers on this archive, not evidence for a
biological mechanism or a claim about other species and protocols.

The later Phase E W3 comparison and its fixed-threshold result are described
separately below and in
[`02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`](../02_workstream_A_external_benchmark/PHASE_E_RESULTS.md).
See the full Phase B0 report at
[`02_workstream_A_external_benchmark/PHASE_B0_REPORT.md`](../02_workstream_A_external_benchmark/PHASE_B0_REPORT.md).

## Phase B0 Workstream B: stem-shape extension

Workstream B audits a five-segment coupled-chain extension in simulation.
The extension reduces to the scalar model at `zeta = 0`. Under the
leakage-safe reference/query split, using curvature to refine tip-matched
twins reduces `k` error by 46.8 per cent; `max_rate` error changes by at
most about 1.1 per cent. This is parameter identification within the
shape-extension model class, not validation of curvature measurements in
real plants. The submitted branch snapshot remains preserved under
[`04_shape_extension_branch/`](../04_shape_extension_branch/), and the audit
is documented in
[`03_workstream_B_shape_extension_audit/SHAPE_EXTENSION_AUDIT.md`](../03_workstream_B_shape_extension_audit/SHAPE_EXTENSION_AUDIT.md).

## Growth-aware phototropism, Phases A to E

Phases A-C use the archive's paired length and trajectory records. Phase A
found starting-length records for 213 of 268 unilateral plants. In the
historical analysis, starting length `L0` is associated with the early
0-2 hour bending rate at +2.12 degrees/hour per log-length unit (95% CI
[0.66, 3.62]). The censoring-aware latency result on 190 at-risk plants is
HR 1.42 per log unit (95% CI [0.97, 2.06], p = 0.068). Length-aware ODE
variants do not improve held-out trajectory RMSE over length-blind M0:
10.25 degrees for M0, 10.41 for M1a, 10.35 for M1d, and 10.29 for M1c.
These associations and model comparisons do not establish a mechanism. See
the [Phase A-C results](../growth_phase/PHASE_BC_RESULTS.md) and the
[censoring-aware latency addendum](../growth_phase/PHASE_C_LATENCY_ADDENDUM.md)
for source detail and endpoint definitions.

Phase D is design simulation only; it adds no plants or biological result.
For the prudent half-pilot early-rate slope, the simulated 80 per cent
power requirements are 753 analysed plants for archive-like Design A, 745
for balanced-intensity Design B, and 411 for wider-natural-length Design C.
The corresponding 90 per cent target was not reached by 900 in A or B and
was 569 in C. Latency remains an exploratory secondary endpoint under the
plan. See the fixed plan and results in
[`growth_phase/PHASE_D_DESIGN_SIMULATION_PLAN.md`](../growth_phase/PHASE_D_DESIGN_SIMULATION_PLAN.md)
and
[`growth_phase/PHASE_D_DESIGN_SIMULATION_RESULTS.md`](../growth_phase/PHASE_D_DESIGN_SIMULATION_RESULTS.md).

Phase E preregistered W3, an intensity-dependent restoring-coefficient
model, on the same 268-plant external archive. Its primary median held-out
RMSE is 9.9968 degrees, above the fixed success criterion of strictly below
9.73 degrees, so the primary threshold result is negative. The B1
comparator's median RMSE is 9.7347 degrees. The paired W3-minus-B1 median
difference is +0.0509 degrees and mean difference is -0.0419 degrees; the
paired analysis does not distinguish the difference from zero and is not a
formal TOST equivalence test. The report describes parity with the B1
baseline and a substantial improvement over W1, not a demonstrated
mechanism. The fitted `max_rate` is an effective model parameter, not a
measured physiological limit. See
[`growth_phase/PHASE_E_PREREGISTRATION.md`](../growth_phase/PHASE_E_PREREGISTRATION.md),
[`02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`](../02_workstream_A_external_benchmark/PHASE_E_RESULTS.md), and
[`02_workstream_A_external_benchmark/PHASE_E_SUPPORTING_ANALYSIS.md`](../02_workstream_A_external_benchmark/PHASE_E_SUPPORTING_ANALYSIS.md).

## Current status

The canonical model and Experiment Series 1 findings are documented, and
the Phase B0 benchmark, shape-extension audit, and Growth-aware
Phototropism Phases A-E are recorded. Phase D is a prospective design
simulation; Phase E's preregistered predictive threshold was not met.
No wet-lab validation or biological mechanism is established by these
analyses. The cross-workstream status, withdrawals, and remaining questions
are maintained in [`docs/CURRENT_STATUS.md`](CURRENT_STATUS.md).

## Repository map

| Path | Purpose |
|---|---|
| `sim.py`, `features.py`, `generate_plants.py` | Canonical scalar model, feature extraction, and seeded population generation |
| `PROBLEM_STATEMENT.md` | Research question, H1-H8 hypotheses, and falsification criteria |
| `fit_real.py`, `phase_a.py`, `round1.py`, `audit_followup.py` | Experiment Series 1 fitting and analysis workflow |
| `02_workstream_A_external_benchmark/` | Phase B0 external benchmark and Phase E W3 reports, scripts, and saved outputs |
| `03_workstream_B_shape_extension_audit/` | Phase B0 Workstream B audit and corrected analysis artifacts |
| `04_shape_extension_branch/` | Preserved five-segment shape-extension snapshot |
| `05_data_external/` | Packaged unilateral-light archive used by the external benchmark |
| `growth_phase/` | Growth-aware phototropism Phases A-E, source documents, and checksummed inputs |
| `results/` | Saved analysis outputs; provenance and dead references for legacy inverse-model data are documented in `docs/DATA_CONTRACT.md` |
| `docs/` | Current status, data documentation, analysis notes, index, implementation status, and newcomer guide |

For the full document inventory, see [`docs/INDEX.md`](INDEX.md). For
installation, tests, and the verified one-command figure/results check, see
[`docs/QUICKSTART.md`](QUICKSTART.md).

## Interactive figure and site

The interactive browser figure of the BendLab model was built with
[Anima](https://github.com/Garinmckayl/anima) by Natnael Getenew. Its
integrator was reviewed against `sim.py`; the stem outline is schematic,
and the angle, bend rate, and trajectory chart are the model outputs. The
figure is available at
[Anima's sunflower-bend example](https://anima.arcumet.com/examples/sunflower-bend/sunflower-bend.html).
The standalone project overview, visual simulator, model demo, and curve
fitter are linked from the site built from `docs/`.

## Data and attribution

Measured stem-angle data are from S13 Data accompanying *Multiple light
signaling pathways control solar tracking in sunflowers*, PLOS Biology
(2023), doi
[10.1371/journal.pbio.3002344](https://doi.org/10.1371/journal.pbio.3002344).
The article is published under CC BY. The file is included with attribution;
its download date, byte size, and SHA-256 are recorded in
[`docs/DATA_CONTRACT.md`](DATA_CONTRACT.md).

The external unilateral-light archive is Kempinski et al. (2026), PNAS,
doi [10.1073/pnas.2614473123](https://doi.org/10.1073/pnas.2614473123),
Zenodo record 21206480, doi [10.5281/zenodo.21206480](https://doi.org/10.5281/zenodo.21206480).
The packaged dataset is subject to its CC-BY-4.0 terms. Data scope and
limits are documented with the benchmark and growth-phase sources.

## Authors and contributions

- **Anadi Tripathi** ([@Yash-Tripath1](https://github.com/Yash-Tripath1)) - project lead; model implementation, analyses, and repository.
- **Umaid Siddiqui** - collaborator; code review and crossover connectivity analysis.
- The interactive figure was built with Anima by **Natnael Getenew**, as credited above.

AI-assisted tools (Arena.ai Agent Mode) were used for ideation, code
development, debugging, and drafting. Data sources, licenses, and checksums
are recorded in this document and in `docs/`.

## Reproduction and license

Python 3.10 or later is required. Run commands from the repository root;
see [`docs/QUICKSTART.md`](QUICKSTART.md) for commands verified from
a fresh clone. Code is released under the MIT license; see
[`LICENSE`](../LICENSE). Data in `data/real/` remain subject to the CC BY terms
of the source article.
