# Growth-aware phototropism: Phase B (simulation) and Phase C (historical) results

Version 3, revised 2026-10-24 in response to the second external
audit round. Version 1 is preserved as `PHASE_BC_RESULTS_v1.md` and
version 2 as `PHASE_BC_RESULTS_v2.md`. The pre-registration
(`PHASE_B_PREREGISTRATION.md`) is unchanged. Deviations from the
plan documents, and the provenance limits of this package, are
listed in full in `DEVIATIONS_AND_PROVENANCE.md` (items D1-D6);
the changes in this version are the latency reanalysis (D4, under
`PHASE_C_LATENCY_ADDENDUM.md`), the paired-covariate Gate 2
sensitivity (D2), the all-observation Phase C sensitivity (D3),
and the explicit deviation/provenance record (D1, D5, D6).

Data: Phase A frozen merge, 213 paired plants
(`PHASE_A_DATA_AUDIT.md`, version 2). Scope: fixed unilateral blue
light only. Workstream separation from Phase B0 is unchanged.

**Narrow conclusion (unchanged in substance):** recorded starting
length is associated with faster early bending in this archive, but
the tested length-aware variants do not improve whole-trajectory
prediction enough to replace M0. That is "an early size-related
signal, no selected mechanism". It is not "length has no effect",
and it is not "length causes faster bending".

## Phase B: can these mechanisms be distinguished at all?

### Original run (pre-registered design, single-split selection)

Simulation with archive-calibrated variability, candidates fitted
as population models and selected by held-out-plant RMSE on a
single 70/30 split, at substantial effect sizes (gain exponent
alpha = 0.8, transport v = 8 mm/h, opposing exponent delta = 1.0).
With an L0 effect present the correct mechanism was selected in
16 of 16 replicates for each of M1a, M1c, M1d at N = 213; with no
length effect M0 was chosen in only 5 of 16. Median held-out RMSE
ratio M0/oracle with L0 ignored was 1.06. The M2 fingerprint result
also stands: bend-elongation correlation discriminates
growth-generated bending in simulation (r = 0.65 vs 0.10), ratio
stability does not (CV 0.51 both).

Large-N deviation (D1): the plan specified N = 10,000; the executed
"large-N" run is a check at N = 2,000 with 3 replicates, not a full
N = 10,000 study. No claim rests on N = 10,000.

This 16/16 result is a conditional statement about those effect
sizes, that selection rule, and those simulation assumptions.

### Gate 2 v2 and v3: effect-size sweep, adoption rule, covariate sampling

Gate 2 v2 (`phase_b_gate2_v2.py`, 132 simulated data sets of
N = 213) varied the effect size and judged every data set by the
Phase C adoption rule (5-fold plant-held-out CV stratified by
intensity; supported requires at least 5% median RMSE improvement
over M0 AND a stable L0-parameter sign across folds). Gate 2 v2
sampled L0 and intensity independently and drew initial angles
from clipped N(0, 5). That sampling is NOT archive-calibrated
(D2): in the paired archive, intensity groups account for 8.4% of
L0 variance, and initial angles have mean 1.35 deg, SD 6.80 deg,
with 10.8% already at or above 10 deg (v2 angles: SD about
4.98 deg, about 2.3% at or above 10 deg). Gate 2 v3
(`phase_b_gate2_v3_pairedcov.py`) repeats the identical design
with (L0, intensity, initial angle) resampled jointly from the 213
paired archive rows. Exact rates move between the two samplings;
quote them only with their design attached.

Results (winner = lowest median CV RMSE; "any supported" counts a
data set once if any M1 variant met the adoption rule):

| Generator | Winner true, v2 | Winner true, v3 | Any supported, v2 | Any supported, v3 |
|---|---|---|---|---|
| M0 (null) | M0 5/24 | M0 7/24 | 0/24 | 0/24 |
| M1a alpha = 0.2 | 8/12 | 5/12 | 2/12 | 5/12 |
| M1a alpha = 0.4 | 11/12 | 12/12 | 10/12 | 11/12 |
| M1a alpha = 0.8 | 12/12 | 12/12 | 12/12 | 12/12 |
| M1d delta = 0.3 | 9/12 | 8/12 | 3/12 | 2/12 |
| M1d delta = 0.6 | 10/12 | 10/12 | 11/12 | 10/12 |
| M1d delta = 1.0 | 12/12 | 12/12 | 12/12 | 12/12 |
| M1c v = 40 (c = 0.025) | 2/12 | 6/12 | 0/12 | 0/12 |
| M1c v = 20 (c = 0.05) | 4/12 | 5/12 | 1/12 | 1/12 |
| M1c v = 8 (c = 0.125) | 10/12 | 9/12 | 0/12 | 0/12 |

Under the null, winner-take-all picks a length model in most data
sets under both samplings (19/24 in v2, 17/24 in v3), while the
adoption rule supports none in ours; an independent paired-design
run by the auditor found 1/24 false supports, so the honest summary
is that the adoption rule's false-support rate is low but not
proven zero (0/24 has a Wilson 95% upper bound of 13.8%; exact
small counts are seed-dependent).

Three conclusions survive both samplings:

1. **Support is not selection.** For gain vs opposing, the adoption
   rule frequently supports both the true variant and its mirror
   (in v3, at alpha = 0.8 the opposing variant is also supported in
   11/12; at delta = 1.0 the gain variant is also supported in
   12/12, via a stable opposite-sign exponent). Passing the rule
   would not by itself have identified a mechanism; relative winner
   selection is the discriminating step, and it is reliable mainly
   at the larger simulated effect sizes.
2. **The adoption rule is blind to transport scored on
   whole-trajectory RMSE.** At v = 8, M1c is the winner in 10/12
   (v2) and 9/12 (v3) and its lag slope is recovered accurately,
   yet it is supported in 0/12 under both samplings because the
   median whole-trajectory RMSE improvement is only 1-2%. The one
   "any supported" case at v = 20 in both versions is support for a
   WRONG variant, not for M1c. Transport must be judged on latency
   endpoints, not this rule.
3. **Small effects are mostly invisible at N = 213**: at
   alpha = 0.2 / delta = 0.3 true-variant support ranges from
   2/12 to 5/12 depending on variant and sampling design.

**Gate 2 verdict, revised:** a conditional, preliminary
identifiability result. M1a/M1c/M1d are mutually distinguishable by
relative selection at N = 213 if effects near the originally
simulated sizes exist and the simulation assumptions hold. The
Phase C adoption rule has a low false-support rate under the null
in these simulations but is conservative, non-specific between
gain and opposing, and insensitive to transport.

## Phase C: what the 213 paired plants actually say

Associations (per log unit of L0, controlling log intensity and
initial angle; plant-bootstrap 95% CI):

| Outcome | Coef per log L0 | 95% CI |
|---|---:|---|
| Early bending rate, 0-2 h | **+2.12 deg/h** | **[0.66, 3.62]** |
| Angle at 8 h | +0.23 deg | [-4.76, 5.48] |
| Late-window plateau, 16-21 h | -1.62 deg | [-5.46, 2.19] |
| Total angular change | -1.62 deg | [-5.82, 2.09] |

The latency outcome is NOT in this table. Its original
implementation (exactly 22 h assigned to the 5 never-crossing
plants; 0 h for the 23 plants already at or above 10 deg at
baseline; ordinary regression) mishandled censoring and the
at-risk population, and its estimate (-0.75 h [-2.02, 0.38],
retained in `phase_c_results.json`) must not be quoted as
evidence. It is superseded by the reanalysis below (D4).

### Latency, reanalysed with censoring handled (post-audit)

Definitions were fixed in `PHASE_C_LATENCY_ADDENDUM.md` before
`phase_c_latency_cox.py` was run. Primary: the 190 plants with
theta(0) < 10 deg (at risk of a first crossing), event = first
observed theta >= 10 deg, 185 events and 5 right-censored at last
observation; Cox model on log L0, log intensity, theta(0).

- **Primary result: hazard ratio for log L0 = 1.42 per log unit,
  95% CI [0.97, 2.06], p = 0.068.** HR above 1 would mean longer
  seedlings cross sooner; the direction matches the early-rate
  association, but the interval includes 1, so no latency
  association is detected under the corrected analysis. The
  Schoenfeld check for log L0 itself is clean (p = 0.85); the
  adjustment covariates theta(0) (p < 0.001) and log intensity
  (p = 0.02) show non-proportionality, a stated limitation of the
  adjusted model.
- Sensitivities (pre-declared, not decision-bearing): without
  theta(0), HR 1.36 [0.93, 1.99], p = 0.109; log L0 alone,
  HR 1.32 [0.91, 1.92], p = 0.146. A revised endpoint on all 213
  plants (time to rise 10 deg above each plant's own start) gives
  HR 1.43 [1.01, 2.03], p = 0.044; that endpoint answers a
  different question and is exploratory only.
- **M1c inclusion, revisited per the addendum's decision rule:**
  no latency signal is detected in the primary corrected analysis,
  so the original exclusion of M1c from the primary Phase C
  comparison STANDS under the corrected analysis as well. M1c
  remains a reported sensitivity, unchanged.
- Contrast with the auditor's exploratory check: including the
  baseline-at-threshold plants as zero-time events gave them
  HR about 1.56 [1.09, 2.22]. The at-risk restriction (the
  defensible population) weakens it to the inconclusive primary
  result above. This is exactly the sensitivity the original
  coding was hiding.

Interval-average elongation rate correlates with total angular
change after accounting for intensity (partial r = 0.48).
Suggestive only: start/finish lengths over a window typically
about 0.9 h longer than the angle record cannot show that local
differential growth caused the bend. The correlation fingerprint
is the M2 diagnostic to carry into future designs, with aligned
windows and controls.

### Model coverage, stated explicitly

Primary pre-registered comparison: M0 vs M1a vs M1d. Post-audit
sensitivities reported alongside: M1c (transport), the Cox latency
reanalysis, and the all-observation refits. Not fitted anywhere in
Phase C: M1b (geometry; no candidate and no geometry variables in
the archive) and M2 (simulation fingerprint only by design). The
conclusion covers exactly the tested variants.

Held-out prediction (5-fold, stratified; adoption rule as above):

| Model | Median held-out RMSE | vs M0 |
|---|---:|---|
| M0 (no length) | **10.25 deg** | reference |
| M1a (gain) | 10.41 deg | -1.5% (worse) |
| M1d (opposing) | 10.35 deg | -1.0% (worse) |
| M1c (transport, sensitivity) | 10.29 deg | -0.4% (worse) |

No variant is supported; M0 is retained. The M1c sensitivity's lag
slope was stable in sign but negative in all 5 folds, opposite to
a transport lag. All-observation sensitivity (D3): refitting every
model on all observations (instead of every 12th) gives M0 10.239,
M1a 10.407, M1d 10.357, M1c 10.310 deg; all within 0.15% of the
committed numbers and no adoption status changes, so the residual
thinning is documented and immaterial. Rebuilding the primary
folds reproduces the committed M0 RMSE exactly (10.2518865 deg).

## Interpretation, kept narrow

1. Longer seedlings bend faster in the first two hours in this
   archive (association, adjusted). No L0 association is detected
   at 8 h, at the plateau, or, under the corrected analysis, in
   latency; the intervals are wide and do not establish exact
   zeros. The pattern is directionally consistent with the
   gain/geometry family, but Phase C does not select a mechanism:
   every predictive test failed, and Gate 2 shows that passing the
   adoption rule would not have separated gain from its opposing
   mirror in any case.
2. The simulations explain the coexistence: an early-rate L0
   signature can sit inside dominant plant-level variability, and
   whole-trajectory RMSE is a blunt score for lag-type effects.
3. Nothing here bears on local curvature, growth-zone location,
   time-resolved elongation, ZT effects, or autostraightening;
   these data contain no ZT contrast and no resolved recovery
   phase, so that separate question remains entirely open.

**Gate 3 verdict:** no model is called supported. Defensible
statement: *initial stem length is associated with the early rate
of phototropic bending in this dataset; the tested length-aware
models (M1a, M1d; M1c in sensitivity) do not improve held-out
trajectory prediction, and no latency association with L0 is
detected under a censoring-aware analysis.* For the next
fixed-light study: keep L0 as a pre-registered continuous
predictor (do not force one seedling length), prespecify
time-to-event endpoints with an explicit at-risk population,
treat any growth-restricting agent as a secondary perturbation
with modelled side-effects, and commit the analysis plan
separately, before outcomes, so its timing is verifiable (see
`DEVIATIONS_AND_PROVENANCE.md`).

## Reproducibility

The pre-registration and the primary scripts are unchanged by this
revision. Exact commands (from the repository root; all paths
relative):

```
cd growth_phase
pip install numpy scipy pandas matplotlib lifelines
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

Outputs per script are listed in the package README. Replication
checks already recorded: `outputs/paired_plants.csv` reproduces
byte-identically (md5 e1564a8efb5e93bdea026209d1f0e087); the
rebuilt-fold M0 RMSE matches the committed value exactly; the
all-observation refits independently reproduce the conclusion.
Independent reproduction from the branch by a reviewer remains the
outstanding verification step.
