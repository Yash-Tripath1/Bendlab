# Analysis-plan deviations and provenance

This document lists every known place where the executed analyses
differ from the dated plan documents, and what can and cannot be
verified about timing. It exists so that no deviation has to be
discovered by a reviewer. Companion to `PHASE_B_PREREGISTRATION.md`
(unchanged) and `PHASE_BC_RESULTS.md` (version 3).

## Deviations

### D1. Large-N simulation: planned N = 10,000; executed N = 2,000 check

The pre-registration says mechanisms are to be assessed "at
N = 213 and N = 10,000". `phase_b_simulation.py` implements the
N = 213 assessment (16 replicates) and a large-N CHECK at N = 2,000
with 3 replicates, not a full N = 10,000 selection study. This was
a runtime decision taken during execution and not documented until
now. Consequence: no claim in any report rests on N = 10,000; the
N = 2,000 rows in `outputs/phase_b_identifiability.json` are a
sanity check only (at N = 2,000 winner selection was again correct
for the three M1 generators, 3/3 each, and poor for M0, 2/3).
Gate 2 v2 and v3 are N = 213 studies and do not change this.

### D2. Gate 2 covariate sampling (v2) and the paired-covariate sensitivity (v3)

`phase_b_gate2_v2.py` sampled L0 and intensity independently from
their marginal distributions and drew initial angles from clipped
N(0, 5). The archive covariates are not independent: in the 213
paired plants, intensity groups account for 8.4% of L0 variance
(one-way eta squared, verified), and initial angles have mean
1.35 deg and SD 6.80 deg with 10.8% (23/213) already at or above
10 deg, versus SD about 4.98 deg and about 2.3% at or above 10 deg
under the v2 sampling. `phase_b_gate2_v3_pairedcov.py` therefore
repeats the v2 design with (L0, intensity, initial angle) resampled
jointly from the 213 paired rows. Results are reported side by side
in `PHASE_BC_RESULTS.md` v3; the v2 rates must not be quoted as
archive-calibrated without this caveat, and the exact rates differ
between the two samplings (the broad conclusions do not).

### D3. Phase C residual thinning: every 12th observation; all-observation sensitivity

`phase_c_historical.py` fits on every 12th observation of each
trajectory (sampling is about 4 min, so fits used roughly hourly
points). This was a computational choice, not a pre-registered one,
and was undocumented in the original report.
`phase_c_allobs_sensitivity.py` repeats the identical folds and
models with all observations: median RMSE M0 10.239 deg (vs 10.252
committed), M1a 10.407, M1d 10.357, M1c 10.310; every model moves by
at most 0.15% and no supported / not-supported status changes.
The thinning is therefore documented and immaterial to the
conclusion; the thinned fits remain the primary record.

### D4. Latency endpoint coding (superseded; see latency addendum)

The pre-registered outcome "latency to 10 deg" was implemented in
the primary Phase C script by assigning exactly 22 h to the 5
plants that never reach 10 deg and 0 h to the 23 plants already at
or above 10 deg at baseline, then using ordinary regression. That
implementation mishandles right-censoring and the at-risk
population. It is superseded by the censoring-aware Cox reanalysis
defined in `PHASE_C_LATENCY_ADDENDUM.md` and implemented in
`phase_c_latency_cox.py` (at-risk n = 190, 185 events, 5 censored;
HR for log L0 1.42, 95% CI [0.97, 2.06], p = 0.068). Under the
corrected analysis no latency association is detected, so the
original decision to keep M1c out of the primary comparison stands;
M1c remains reported as a sensitivity either way. The flawed
original estimate stays in `outputs/phase_c_results.json` for
provenance and must not be quoted as evidence.

### D5. M1c parameterisation differs between scripts (same mechanism)

The pre-registration and the original Phase B simulation
parameterise transport by a speed v (tau = tau0 + (L0 - Lref)/v).
Gate 2 v2/v3 candidates and the Phase C M1c sensitivity parameterise
it by the lag slope c = 1/v in h/mm (tau = tau0 + c*(L0 - Lref)),
because the adoption rule's sign-stability criterion is vacuous for
a parameter constrained positive (v > 0). The mechanism (response
lag scales with L0) is unchanged; the parameterisation change and
its reason are documented in each script.

### D6. M1c in Phase C: conditional inclusion, revisited transparently

The pre-registration included M1c in the primary prediction
comparison only if a latency signal appeared. The original (flawed)
latency analysis showed none, so M1c was excluded from the primary;
it was then fitted as a post-audit sensitivity (Gate 3 revision),
and the inclusion decision was re-examined under the corrected Cox
analysis (D4), which also detects no latency association. M1c's
status is therefore: not a pre-registered primary comparison;
reported sensitivity; conclusion unchanged (not supported:
10.29 deg vs M0 10.25 deg).

## Provenance: what the branch can and cannot prove

The branch that carries this package adds the dated
pre-registration and the results in a single commit, by packaging
necessity. The branch history therefore CANNOT by itself verify
that the pre-registration predates outcome fitting, and no such
claim is made for it. What can be verified:

- `PHASE_B_PREREGISTRATION.md` is byte-identical to the file as
  written on 2026-10-23, before Phase B/C outcome fitting in the
  working record; its SHA-256 is recorded in `SHA256SUMS.txt`, so
  any future change is detectable from this package onward.
- The internal chronology (pre-registration timestamp in the
  working session record, Phase A audit preceding outcome scripts,
  scripts preceding outputs) is consistent with pre-registration,
  but it rests on the authors' records, not on cryptographic proof.

For future phases, a pre-registration should be committed on its
own, or timestamped in an external registry, BEFORE any outcome
script is run, so that the ordering is independently verifiable.
That recommendation is carried into the Phase D design.
