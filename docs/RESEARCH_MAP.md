# Research map

This map describes the current checkout and the evidence routes between the paper-facing numbers, saved sources, and code. The numbered project sequence is 01 to 07. Entry 01 is retired from the current tree and retained in Git history; entries 02 to 07 remain as directories. The unnumbered `growth_phase/` programme predates that numbering convention.

## Directory and section map

| Area | Contents and status |
|---|---|
| `01_canonical_bendlab/` | Retired canonical snapshot, removed from the current checkout. The tree is recoverable from Git history. Its provenance and unique moved document are recorded in [`archive/SNAPSHOT_INDEX_2026-10-16.md`](archive/SNAPSHOT_INDEX_2026-10-16.md). |
| `02_workstream_A_external_benchmark/` | External unilateral-light benchmark, Phase B0 and Phase E reports, source code, tests, and saved outputs. Use its reports for benchmark-specific model and split definitions. |
| `03_workstream_B_shape_extension_audit/` | Archived sub-project retained as evidence, not a paper claim. Contains the audit of the submitted multi-segment shape extension and corrected audit artifacts. |
| `04_shape_extension_branch/` | Archived sub-project retained as evidence, not a paper claim. Preserves the submitted shape-extension branch for provenance. |
| `05_data_external/` | Packaged external unilateral-light trajectory archive used by the benchmark and growth-aware work. |
| `06_growth_coupling/` | Growth-coupling preregistration, analysis code, and observational results with endpoint and measurement-geometry qualifications. |
| `07_evidence_pack/` | Paper data sheet, outline, quantitative-claim audit, figure captions, reproducibility notes, figure sources, and saved evidence outputs. |
| `growth_phase/` | Growth-aware photophase programme. It predates the numbering convention and has its own `SHA256SUMS.txt` manifest and preregistrations. It is a separate row, not a numbered project directory. |
| `data/` | Measured PLOS Biology workbook under `data/real/`. Its source, handling rules, and checksum are documented in [`DATA_CONTRACT.md`](DATA_CONTRACT.md). |
| `docs/` | Current project documentation, indexes, guides, and historical material under `docs/archive/`. The longer former README is preserved in [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md). |
| `results/` | Committed result tables, summaries, fitted-model assets, inverse-model datasets, and figures. File paths and source claims are documented by the relevant reports. |
| `tests/` | Regression suite for model contracts, data/checksum rules, site parity, JSON validity, and documentation links. |

Directories 03 and 04 are archived sub-projects retained as evidence, not paper claims. They must not be presented as additional evidence for the canonical paper results.

## Root Python-script inventory

Classification follows the output cited by each script, not its imports. The supplied baseline inventory had 33 root scripts. After the two approved publication-tool retirements, 31 Python scripts remain at the root. The category headings preserve the exact baseline labels and counts; the retired entries are marked once below.

### 1. Model core (5)

- `sim.py`
- `sim_gamma.py`
- `sim_clock_gamma.py`
- `check_model_contract.py`
- `check_model_v2.py`

### 2. Fitting and identifiability (9)

- `fit_real.py`
- `data_real.py`
- `features.py`
- `phase_a.py`
- `audit_followup.py`
- `audit_round1.py`
- `gamma_zt9_test.py`
- `zt9_diagnostics.py`
- `clock_validation.py`

### 3. Simulation studies (12)

- `generate_plants.py`
- `round1.py`
- `sweep.py`
- `sweep_weighted.py`
- `big_sweep.py`
- `mega_sweep.py`
- `exp_design.py`
- `exp_design_model_selection.py`
- `real_seedling_sim.py`
- `vector_stimulus.py`
- `vector_batch.py`
- `vector_grand_atlas.py`

### 4. Inverse models and legacy experiments (4)

- `train_inverse_model.py`
- `train_inverse_model_v2.py`
- `train_inverse_model_v3.py`
- `probe_claude.py`

### 5. Publication and site tooling (3)

- `build_site.py` (retained)
- `make_explainer_figures.py` (removed in commit 3)
- `make_print_edition.py` (removed in commit 3)

The three inverse-model training versions, their evaluation and weight files, and all four renamed `results/adaptation_*.csv` datasets remain intact. The probe experiment and its saved outputs, [`results/probe_claude_summary.json`](../results/probe_claude_summary.json) and [`results/figures/probe_claude_dashboard.png`](../results/figures/probe_claude_dashboard.png), are retained as legacy experiments. These tools were trained or evaluated on synthetic data; they do not establish performance on real plants.

The requested `results/explainer_summary.json` is absent from the repository, and no tracked generator produced or referenced it. The retired Explainer figure generator wrote only `results/figures/explainer2_dashboard.png`. That PNG is retained because the Explainer material remains cited in [`INDEX.md`](INDEX.md) and the dashboard is linked by [`EXPLAINER_PART2.md`](EXPLAINER_PART2.md).

## Routes through the evidence

### Check a number

1. Find the claim and its definition in [`07_evidence_pack/PAPER_DATA.md`](../07_evidence_pack/PAPER_DATA.md).
2. Follow the cited path to the saved CSV, JSON, workbook, or source report.
3. Read the referenced method section and source implementation for the sample, model, metric, and fold definition.
4. Check [`07_evidence_pack/CLAIM_AUDIT.md`](../07_evidence_pack/CLAIM_AUDIT.md) and the Discrepancies section before treating values from separate analyses as comparable.

### Reproduce the paper-facing evidence

1. Read the evidence-pack [`README.md`](../07_evidence_pack/README.md) and [`REPRODUCIBILITY.md`](../07_evidence_pack/REPRODUCIBILITY.md) for scope and commands.
2. Create the environment using the requirements file named in that guide.
3. Run only the listed audit and figure commands from the repository root; the guide distinguishes saved-output checks from new fits.
4. Verify the saved evidence checksums and compare generated artifacts before replacing any committed file.

### Extend the work

1. Start with [`PROBLEM_STATEMENT.md`](../PROBLEM_STATEMENT.md) and [`CURRENT_STATUS.md`](CURRENT_STATUS.md) to identify the claim boundary and open question.
2. Check [`DATA_CONTRACT.md`](DATA_CONTRACT.md) and the relevant directory's source report before choosing inputs.
3. For prospective work, read the matching preregistration before implementing or running an analysis.
4. Add regression coverage, document the source and outputs, and preserve the relevant checksum manifests.
