# Growth-aware phototropism: Phases A-C, audit revision v3 (branch package)

This folder contains the growth-aware phototropism analysis for
chamber-grown sunflower seedlings under fixed unilateral blue light:
the paired length/trajectory audit (Phase A), the simulation
identifiability study (Phase B, Gate 2), and the historical checks
on 213 paired plants (Phase C, Gate 3), revised through two
external audit rounds (report versions 1 and 2 preserved).

Status: prepared for upload on a dedicated branch for review. It
is not a `main` update and makes no change to the published
simulator, the website, or any Phase B0 workstream.

- Intended branch: `growth-phase-audit-v2` (or a successor branch
  if version 2 of this package is already pushed there; do not
  rewrite a pushed branch, add a new commit or a new branch)
- Base repository: `Yash-Tripath1/Bendlab`
- Base commit on `main`: `8860865` (short SHA, as reported
  2026-10-23; verify locally with `git rev-parse --short HEAD`
  before branching, and record the new branch commit SHA in the
  pull-request description after pushing)
- Package date: 2026-10-24 (version 3)

## Labels: pre-registered, post-audit, preserved

PRE-REGISTERED AND PRIMARY (unchanged):

- `PHASE_B_PREREGISTRATION.md`: model family, comparisons, and the
  adoption rule, written before any response outcome was fitted.
  Byte-identical to the original.
- `phase_b_simulation.py`: original Gate 2 simulation (single-split
  winner selection, 16 replicates). Its "large-N" run is a check at
  N = 2,000, not the planned N = 10,000 (deviation D1 in
  `DEVIATIONS_AND_PROVENANCE.md`).
- `phase_c_historical.py`: Phase C primary comparison (M0 vs M1a
  vs M1d) and association analysis. Primary fits use every 12th
  observation (deviation D3, sensitivity-tested, conclusion
  unchanged). Its latency coding is superseded (D4).

POST-AUDIT (each file labelled; none may be cited as
pre-registered):

- `phase_b_gate2_v2.py`: effect-size sweep judged by the Phase C
  adoption rule, including the null false-support rate. Samples
  covariates independently (assumption flagged, see v3).
- `phase_b_gate2_v3_pairedcov.py`: the same design with
  (L0, intensity, initial angle) resampled jointly from the paired
  archive rows (deviation D2 sensitivity).
- `phase_c_m1c_sensitivity.py`: the M1c transport variant on the
  primary folds (model-coverage closure; deviation D6).
- `PHASE_C_LATENCY_ADDENDUM.md` and `phase_c_latency_cox.py`:
  censoring-aware Cox reanalysis of the latency endpoint on the
  190 at-risk plants, definitions fixed before the run; the M1c
  exclusion stands under it (deviation D4).
- `phase_c_allobs_sensitivity.py`: Phase C refits on all
  observations; no adoption status changes (deviation D3).

PRESERVED UNCHANGED: `PHASE_A_DATA_AUDIT_v1.md`,
`PHASE_BC_RESULTS_v1.md`, `PHASE_BC_RESULTS_v2.md`,
`outputs/phase_a_audit_v1.json`. `PHASE_BC_RESULTS.md` is the
current (version 3) report. All known deviations D1-D6 and the
provenance limits of this package (including that a single-commit
branch cannot cryptographically prove the pre-registration
predates outcome fitting) are in `DEVIATIONS_AND_PROVENANCE.md`.

Not fitted anywhere in Phase C: M1b (geometry) and M2
(growth-generated bending; simulation fingerprint only by design).

## Headline result

Starting stem length is associated with faster bending in the
first 2 h (+2.12 deg/h per log unit, 95% CI [0.66, 3.62],
adjusted). No L0 association is detected at 8 h, at the 16-21 h
plateau, or in latency under a censoring-aware Cox analysis
(at-risk n = 190: HR 1.42 per log unit, 95% CI [0.97, 2.06],
p = 0.068). The tested length-aware models do not improve
held-out prediction over M0 (10.25 deg vs M1a 10.41, M1d 10.35,
M1c 10.29 deg), so M0 is retained and no mechanism is claimed.
Gate 2 v2/v3: the adoption rule has a low false-support rate
under the null, is conservative at small effects, is not
mechanism-specific between gain and opposing, and is insensitive
to transport effects scored on whole-trajectory RMSE. See
`PHASE_BC_RESULTS.md`.

## Data included

Only the archive files the scripts use: `data/00_Data/`
`uni_trajectories.csv`, `data/07_Supplementary/`
`length_est_data.csv`, `length_est.py`. Source (external):
Kempinski et al. (2026), Zenodo record 21206480, doi
10.5281/zenodo.21206480, archive md5
06d911cc56c6cf92d66af15304bb93f9. Packaged text files are
normalised to LF line endings (values unchanged; this normalises
the CRLF endings of the upstream CSVs so checksums are stable).

## Checksums

`SHA256SUMS.txt` holds SHA-256 digests of the exact packaged
bytes. Version 2 of this package had a manifest that failed on
clean checkouts for three upstream inputs: the recorded digests
were of CRLF bytes while checked-out files were LF. Fixed here by
(1) LF-normalising every packaged text file, (2) generating the
manifest from the packaged files themselves, and (3) adding
`.gitattributes` (`* -text`) in this folder so Git performs no
line-ending conversion on these files in future checkouts. Verify
after checkout with, from this folder: `sha256sum -c
SHA256SUMS.txt` (or `shasum -a 256 -c SHA256SUMS.txt`).

## Dependencies

Python 3.11 or later (tested 3.13.16); numpy, scipy, pandas,
matplotlib (all scripts), lifelines (`phase_c_latency_cox.py`
only; tested 0.30.3).

```bash
pip install numpy scipy pandas matplotlib lifelines
```

## Exact run commands

From the repository root; all paths relative.

```bash
cd growth_phase
python3 phase_a_join.py
python3 phase_b_simulation.py
python3 phase_b_gate2_v2.py
python3 phase_b_gate2_v3_pairedcov.py
python3 phase_c_historical.py
python3 phase_c_m1c_sensitivity.py
python3 phase_c_latency_cox.py
python3 phase_c_allobs_sensitivity.py
python3 make_growth_figures_v3.py
python3 make_gate2_v2_figure.py
python3 make_gate2_v3_figure.py
```

Outputs: Phase A merge/audit in `outputs/`; Gate 2 results in
`phase_b_identifiability.json`, `phase_b_gate2_v2.json`,
`phase_b_gate2_v3_pairedcov.json` with per-dataset replicate CSVs;
Phase C in `phase_c_results.json`, `phase_c_m1c_sensitivity.json`,
`phase_c_latency_cox.json`, `phase_c_allobs_sensitivity.json`;
figures `fig_growth_summary_v3.png`, `fig_gate2_v2.png`,
`fig_gate2_v3_comparison.png`. Recorded replication checks:
frozen merge byte-identical on re-run (md5
e1564a8efb5e93bdea026209d1f0e087); rebuilt-fold M0 RMSE matches
the committed 10.2518865 deg exactly; all-observation refits move
every median RMSE by at most 0.15%. Independent reproduction from
this branch is the intended verification step.
