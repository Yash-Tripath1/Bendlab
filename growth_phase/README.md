# Growth-aware phototropism: Phases A-C, audit revision (branch package)

This folder contains the growth-aware phototropism analysis for
chamber-grown sunflower seedlings under fixed unilateral blue light:
the paired length/trajectory audit (Phase A), the simulation
identifiability study (Phase B, Gate 2), and the historical checks on
213 paired plants (Phase C, Gate 3).

Status: prepared for upload on a dedicated branch for review. It is
not a `main` update and makes no change to the published simulator,
the website, or any Phase B0 workstream.

- Intended branch: `growth-phase-audit-v2`
- Base repository: `Yash-Tripath1/Bendlab`
- Base commit on `main`: `8860865` (short SHA, as reported
  2026-10-23; verify locally with `git rev-parse --short HEAD`
  before branching, and record the new branch commit SHA in the
  pull-request description after pushing)
- Package date: 2026-10-24

## What is pre-registered, what is post-audit, what is preserved

Labels are explicit so no post-audit analysis can be mistaken for a
pre-registered one.

PRE-REGISTERED AND PRIMARY (unchanged):

- `PHASE_B_PREREGISTRATION.md`: model family, comparisons, and the
  adoption rule, written before any response outcome was fitted.
  This file is byte-identical to the original.
- `phase_b_simulation.py`: original Gate 2 simulation (single-split
  winner selection, 16 replicates, substantial effect sizes).
- `phase_c_historical.py`: Phase C primary comparison (M0 vs M1a vs
  M1d) and the L0 association analysis.

POST-AUDIT (added 2026-10-24, labelled as such in every file):

- `phase_b_gate2_v2.py`: effect-size sweep (gain, opposing, and
  transport) judged by the Phase C adoption rule, including the
  false-support rate under the null (132 simulated data sets).
- `phase_c_m1c_sensitivity.py`: the M1c transport variant fitted on
  the identical Phase C folds, closing the model-coverage gap. The
  pre-registration had included M1c only if a latency signal
  appeared; none was detected, so this is a sensitivity analysis,
  not a pre-registered test.
- `PHASE_A_DATA_AUDIT.md` version 2 and `PHASE_BC_RESULTS.md`
  version 2: corrected and tightened reports.

PRESERVED UNCHANGED (v1 record):

- `PHASE_A_DATA_AUDIT_v1.md`, `PHASE_BC_RESULTS_v1.md`, and
  `outputs/phase_a_audit_v1.json` are the version 1 documents,
  retained so the revision history is inspectable. SHA-256 checksums
  for all packaged files are in `SHA256SUMS.txt`.

Not fitted anywhere in Phase C: M1b (geometry, no fitted candidate
and no geometry variables in the archive) and M2 (growth-generated
bending, represented by design only through its simulation
fingerprint).

## Headline result

Recorded starting stem length is associated with faster bending in
the first 2 h (plus 2.12 deg/h per log unit of L0, 95% CI
[0.66, 3.62], adjusted for intensity and initial angle). No L0
association is detected at 8 h or at the 16-21 h late-window
plateau, with wide intervals noted. The tested length-aware models
(M1a, M1d, and M1c in sensitivity) do not improve held-out
whole-trajectory prediction over the length-blind model M0
(median RMSE 10.25 deg vs 10.41, 10.35, and 10.29 deg), so M0 is
retained and no mechanism is claimed. Gate 2 v2 additionally shows
that the adoption rule has a low false-support rate under the null
in simulation (0 of 24), is conservative at small effect sizes,
is not mechanism-specific between the gain and opposing variants,
and is insensitive to transport-type effects scored on
whole-trajectory RMSE. Full reasoning: `PHASE_BC_RESULTS.md`.

## Data included

Only the archive files the scripts use, so the branch reproduces
from a clean checkout:

- `data/00_Data/uni_trajectories.csv`
- `data/07_Supplementary/length_est_data.csv`
- `data/07_Supplementary/length_est.py`

Source (external data, not produced by this project):
Kempinski et al. (2026), Zenodo record 21206480,
doi 10.5281/zenodo.21206480, archive md5
06d911cc56c6cf92d66af15304bb93f9. The full archive can be
re-downloaded from that record; this package retains the subset in
use. Generated and frozen analysis outputs are in `outputs/`
(per-plant merges, replicate CSVs, result JSONs, and figures).

## Dependencies

- Python 3.11 or later (tested on Python 3.13.16)
- numpy 2.3.5, scipy 1.17.1, pandas 2.2.3, matplotlib 3.10.9
  (tested versions; the scripts use only standard functionality
  from these packages)

Install with:

```bash
pip install numpy scipy pandas matplotlib
```

## Exact run commands

Run from the repository root. All paths inside the scripts are
relative; no absolute or machine-specific paths are used.

```bash
cd growth_phase

python3 phase_a_join.py
python3 phase_b_simulation.py
python3 phase_b_gate2_v2.py
python3 phase_c_historical.py
python3 phase_c_m1c_sensitivity.py
python3 make_growth_figures.py
python3 make_gate2_v2_figure.py
```

Expected outputs:

- `phase_a_join.py` writes `outputs/paired_plants.csv` and
  `outputs/phase_a_audit.json` (seconds).
- `phase_b_simulation.py` writes `outputs/phase_b_identifiability.json`
  and `outputs/confusion_N213.csv` (a few minutes).
- `phase_b_gate2_v2.py` writes `outputs/gate2_v2_replicates.csv`
  (132 rows) and `outputs/phase_b_gate2_v2.json` (about 7 minutes).
- `phase_c_historical.py` writes `outputs/phase_c_outcomes.csv`,
  `outputs/phase_c_folds.csv`, and `outputs/phase_c_results.json`
  (seconds).
- `phase_c_m1c_sensitivity.py` writes
  `outputs/phase_c_m1c_folds.csv` and
  `outputs/phase_c_m1c_sensitivity.json`, and refits M0 on the same
  folds as a replication check (seconds).
- The two figure scripts write `outputs/fig_growth_summary.png`
  and `outputs/fig_gate2_v2.png`.

Replication checks already recorded: re-running `phase_a_join.py`
reproduces `outputs/paired_plants.csv` byte-identically (md5
e1564a8efb5e93bdea026209d1f0e087 before and after the version 2
label correction), and the M1c sensitivity script's M0 refit matches
the primary Phase C M0 median RMSE exactly (10.2518865 deg).
Independent reproduction from these scripts by a reviewer is the
intended next step; treat no number here as externally verified
until that is done.
