# BendLab

[Choose a reading path](docs/READING_PATH.md)

**Parameter identifiability in a minimal model of phototropic stem bending**

BendLab asks what stem-angle trajectories can reveal about a plant's internal parameters. It combines a four-parameter simulator, fits to published sunflower trajectories, external benchmarking, shape-extension audits, and growth-aware analyses.

## Read in this order

1. [`docs/CURRENT_STATUS.md`](docs/CURRENT_STATUS.md) for the cross-workstream findings, withdrawals, and open questions.
2. [`docs/RESEARCH_MAP.md`](docs/RESEARCH_MAP.md) to locate evidence, code, data, and extension routes.
3. [`07_evidence_pack/PAPER_DATA.md`](07_evidence_pack/PAPER_DATA.md) to check source-linked paper numbers and qualifications.
4. [`docs/QUICKSTART.md`](docs/QUICKSTART.md) for environment setup, regression tests, and the verified artifact check.
5. [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md) for the preserved full project overview.

## Research at a glance

The canonical model tracks stem angle and bend rate under light direction. Its four fitted settings are response gain, sensing lag, maximum bend-rate parameter, and effective light angle. It is a phenomenological model, not a physiological growth model. See [`PROBLEM_STATEMENT.md`](PROBLEM_STATEMENT.md) and [`sim.py`](sim.py).

Experiment Series 1 finds that similar trajectories can arise from different parameter combinations; the saved Fig1C analysis flags the maximum-rate parameter as locally unidentifiable in 47 of 48 fits. The external benchmark reports W1 median held-out RMSE of 14.41 degrees versus 9.73 degrees for the B1 group-mean baseline. Phase E's preregistered W3 threshold was not met: its median held-out RMSE was 9.9968 degrees against a strict-below-9.73-degree criterion. These are results for stated data and model classes, not biological mechanisms.

Growth-aware Phases A to E report an early-length association, no improvement from the tested length-aware models over M0 in held-out prediction, a design simulation, and a negative Phase E primary threshold result. No wet-lab validation or biological mechanism is established. The Phase C and external benchmark RMSE values use different samples and model/evaluation contexts; see the discrepancy note in [`PAPER_DATA.md`](07_evidence_pack/PAPER_DATA.md).

## Evidence and code

- [`docs/INDEX.md`](docs/INDEX.md) indexes project documents and user-facing pages.
- [`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md) records data handling, provenance, and the inverse-model dataset hashes.
- [`07_evidence_pack/REPRODUCIBILITY.md`](07_evidence_pack/REPRODUCIBILITY.md) documents the evidence-pack commands and outputs.
- Directories 03 and 04 are archived sub-projects retained as evidence, not paper claims. Their scopes and limits are described in the [Research Map](docs/RESEARCH_MAP.md).

Code is released under the MIT license. The measured PLOS data and external archive retain their source licenses and attribution; see [`LICENSE`](LICENSE), [`docs/DATA_CONTRACT.md`](docs/DATA_CONTRACT.md), and [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).
