# Growth-aware phototropism: Phase B (simulation) and Phase C (historical) results

Version 2, revised 2026-10-24 in response to external audit. Version 1
is preserved as `PHASE_BC_RESULTS_v1.md`. The pre-registration
(`PHASE_B_PREREGISTRATION.md`) is unchanged. Two analyses in this
version are new and are labelled post-audit where they appear:
Gate 2 v2 (`phase_b_gate2_v2.py`) and the Phase C M1c sensitivity
(`phase_c_m1c_sensitivity.py`). Neither alters any pre-registered
primary result.

Data: Phase A frozen merge, 213 paired plants
(`PHASE_A_DATA_AUDIT.md`, version 2). Scope: fixed unilateral blue
light only. Workstream separation from Phase B0 is unchanged: nothing
here validates or is validated by Workstream A (external tip-angle
benchmark) or Workstream B (shape-extension parameter recovery).

**Narrow conclusion (unchanged in substance, tightened in scope):**
recorded starting length is associated with faster early bending in
this archive, but the tested length-aware variants do not improve
whole-trajectory prediction enough to replace M0. That is "an early
size-related signal, no selected mechanism". It is not "length has no
effect", and it is not "length causes faster bending".

## Phase B: can these mechanisms be distinguished at all?

### Original run (pre-registered design, single-split selection)

Simulation with archive-calibrated variability (empirical L0 and
intensity distributions, plant random effects, circumnutation-scale
noise), candidates fitted as population models and selected by
held-out-plant RMSE on a single 70/30 split. Effect sizes were
substantial (gain exponent alpha = 0.8, transport v = 8 mm/h,
opposing exponent delta = 1.0).

- With an L0 effect present, the correct mechanism was selected in
  16 of 16 replicates for each of M1a (gain), M1c (transport),
  M1d (opposing) at N = 213 using tip trajectories + L0.
- With NO length effect (M0 true), M0 was chosen in only 5 of 16
  replicates; the rest scattered across M1 variants.
- Ignoring L0 entirely (tip only) costs little prediction: median
  held-out RMSE ratio M0/oracle = 1.06.
- M2 fingerprint: correlation between final bend and cumulative
  elongation discriminated growth-generated bending in simulation
  (r = 0.65 under M2 vs 0.10 under gain-modulated bending). The
  "stable bend-per-unit-elongation" version did NOT discriminate
  (coefficient of variation 0.51 under both): the fingerprint to
  carry forward is the correlation, not ratio stability.

Per the audit, the 16/16 result is a conditional statement about
those particular effect sizes, that selection rule, and those
simulation assumptions. It is not a general distinguishability pass.

### Gate 2 v2 (post-audit): effect-size sweep and the Phase C adoption rule

Gate 2 v2 (`phase_b_gate2_v2.py`, 132 simulated data sets of N = 213,
seeds fixed) varies the effect size and, crucially, judges every data
set by the SAME rule Phase C applied to the historical data: 5-fold
plant-held-out CV stratified by intensity, with an M1 variant
"supported" only if its median held-out RMSE improves on M0 by at
least 5% AND its L0-parameter sign is stable across all 5 folds.
Winner-take-all (lowest median CV RMSE) is recorded on the same data
sets for comparison. M1c is parameterised by lag slope
c = 1/v (h/mm) so that sign stability is meaningful for it.

Under the null (M0 true, 24 data sets):

| Rule | Result under M0 |
|---|---|
| Winner-take-all | M0 wins only 5/24; an M1 variant wins 19/24 (M1a 6, M1c 8, M1d 5) |
| Phase C adoption rule | 0/24 false supports for every variant (Wilson 95% interval for the any-variant rate: 0 to 0.138) |

Winner selection therefore cries wolf under the null at about the
rate the original run suggested (5/16 then, 5/24 now), while the
stricter adoption rule did not falsely support any variant in these
24 null data sets. 0/24 does not prove a zero false-support rate in
general; it bounds it under these simulation assumptions
(upper 95% bound 13.8%).

Across effect sizes (12 data sets per scenario):

| Generator | Winner = true | True variant supported | Wrong variant supported | Median improvement, true variant |
|---|---|---|---|---|
| M1a alpha = 0.2 | 8/12 | 2/12 | 0/12 | +2.4% |
| M1a alpha = 0.4 | 11/12 | 10/12 | M1d 7/12 | +9.5% |
| M1a alpha = 0.8 | 12/12 | 12/12 | M1d 12/12 | +27.6% |
| M1d delta = 0.3 | 9/12 | 3/12 | M1a 2/12 | +2.4% |
| M1d delta = 0.6 | 10/12 | 11/12 | M1a 9/12 | +9.6% |
| M1d delta = 1.0 | 12/12 | 12/12 | M1a 12/12 | +20.2% |
| M1c v = 40 (c = 0.025) | 2/12 | 0/12 | 0/12 | -0.1% |
| M1c v = 20 (c = 0.05) | 4/12 | 0/12 | M1a 1/12 | +0.2% |
| M1c v = 8 (c = 0.125) | 10/12 | 0/12 | 0/12 | +1.9% |

Three consequences, each narrowing the original Gate 2 statement:

1. **Support is not selection.** For gain vs opposing, the adoption
   rule frequently supports BOTH the true variant and its mirror:
   when M1a is true, M1d is also supported by fitting a stable
   negative opposing exponent (median fitted delta = -1.08 at
   alpha = 0.8), and when M1d is true, M1a is also supported via a
   negative gain exponent (median fitted alpha = -0.52 at
   delta = 1.0). "Longer plants gain up" and "longer plants opposing
   down" improve whole-trajectory prediction in the same direction.
   So even if a variant had passed the rule in Phase C, that alone
   would not have identified the mechanism; relative winner selection
   is the discriminating step, and it only discriminates reliably at
   the larger simulated effect sizes (small effects: true variant
   supported in only 2-3 of 12 data sets).
2. **The adoption rule is blind to transport effects scored this
   way.** Even at the original v = 8 mm/h, the M1c lag slope is
   recovered accurately (median fitted c = 0.137 vs true 0.125
   h/mm, sign stable in 12/12, winner in 10/12), yet the median
   whole-trajectory RMSE improvement is only 1.9% (maximum 4.3% in
   12 data sets), so the 5% rule supports it 0/12. A lag mechanism
   must be judged on latency-type endpoints, not on this
   whole-trajectory adoption rule.
3. **Small effects are mostly invisible to both rules** at N = 213:
   at alpha = 0.2 / delta = 0.3 the true variant is supported in
   2-3 of 12 data sets, although the winner is already correct in
   8-9 of 12.

**Gate 2 verdict, revised:** Gate 2 is a conditional, preliminary
identifiability result. M1a/M1c/M1d are mutually distinguishable by
relative selection at N = 213 IF effects near the originally
simulated sizes exist and the simulation assumptions hold. The
Phase C adoption rule has a low false-support rate under the null in
these simulations (0/24, upper bound 13.8%) but is conservative,
non-specific between gain and opposing, and insensitive to transport.
Phase C was therefore licensed to test the M1 variants for
prediction, with "retain M0 on ambiguity" the expected honest
outcome for small or lag-type effects.

## Phase C: what the 213 paired plants actually say

Associations (per log unit of L0, controlling log intensity and
initial angle; plant-bootstrap 95% CI):

| Outcome | Coef per log L0 | 95% CI |
|---|---:|---|
| Early bending rate, 0-2 h | **+2.12 deg/h** | **[0.66, 3.62]** |
| Latency to 10 deg | -0.75 h | [-2.02, 0.38] |
| Angle at 8 h | +0.23 deg | [-4.76, 5.48] |
| Late-window plateau, 16-21 h | -1.62 deg | [-5.46, 2.19] |
| Total angular change | -1.62 deg | [-5.82, 2.09] |

Later-window wording, per the audit: an L0 association is DETECTED
for early rate and NOT DETECTED at 8 h or at the plateau. The later
intervals include zero but are fairly wide, so the data do not
establish that a later effect is exactly zero.

Interval-average elongation rate correlates with total angular change
after accounting for intensity (partial r = 0.48). This is
suggestive, not mechanism proof: it uses start/finish lengths over a
window that is typically about 0.9 h longer than the angle record,
so it does not show that local differential growth caused the bend.
The simulation correlation fingerprint remains the diagnostic to
carry into a future design, to be tested there with aligned
measurement windows and appropriate controls.

### Model coverage, stated explicitly

- **Primary, pre-registered comparison:** M0 vs M1a vs M1d
  (`phase_c_historical.py`). The pre-registration included M1c only
  if a latency signal appeared; none was detected (latency CI above
  includes zero), so M1c was correctly absent from the primary table.
- **Post-audit sensitivity:** M1c has now also been fitted on the
  identical folds (`phase_c_m1c_sensitivity.py`), so its result is
  reported rather than omitted. It is not a pre-registered test.
- **Not fitted anywhere in Phase C:** M1b (geometry) has no fitted
  candidate in the pre-registered family and this archive holds no
  diameter or growth-zone geometry; M2 (growth-generated bending) is
  by design a simulation fingerprint only, and start/finish lengths
  cannot fit it. The Phase C conclusion below therefore covers
  exactly the tested variants: M1a and M1d (primary), M1c
  (sensitivity).

Held-out prediction (5-fold, stratified; pre-registered adoption
rule: >= 5% median RMSE improvement and stable L0-parameter sign):

| Model | Median held-out RMSE | vs M0 |
|---|---:|---|
| M0 (no length) | **10.25 deg** | reference |
| M1a (gain x (L0/Lref)^alpha) | 10.41 deg | -1.5% (worse) |
| M1d (opposing x (L0/Lref)^delta) | 10.35 deg | -1.0% (worse) |
| M1c (transport, post-audit sensitivity) | 10.29 deg | -0.4% (worse) |

Neither primary variant is supported under the rule. The gain
exponent's sign was stable across folds (+ in all 5) yet prediction
did not improve; the opposing exponent's sign was not stable. The
M1c sensitivity likewise does not meet the rule descriptively: its
lag slope c was stable in sign but NEGATIVE in all 5 folds
(-0.050, -0.022, -0.033, -0.050, -0.024 h/mm; two folds at the
-0.05 bound), which is the opposite direction from a transport lag
(c > 0), with no predictive gain. As a replication check, refitting
M0 on the rebuilt folds reproduces the primary M0 median RMSE
exactly (10.2518865 deg, difference 0.0). **M0 is retained.**

## Interpretation, kept narrow

1. In this archive, longer seedlings bend faster in the first two
   hours (association, intensity- and posture-adjusted). No L0
   association is detected at 8 h or at the late-window plateau,
   with the wide-interval caveat above. The early-rate pattern is
   directionally consistent with the gain/geometry family
   (M1a/M1b) and not with a length-dependent opposing term (M1d),
   but Phase C cannot and does not select a mechanism: the
   predictive tests that could have supported M1a, M1d, or (in
   sensitivity) M1c all failed, and Gate 2 v2 shows that passing
   the adoption rule would not by itself have separated gain from
   its opposing mirror.
2. The simulations explain why both can be true: a real early-rate
   L0 signature can coexist with negligible whole-trajectory
   predictive gain, because most trajectory variance is plant-level
   variability unrelated to L0, and because whole-trajectory RMSE
   is a blunt score for lag-type effects in particular.
3. Nothing here bears on local curvature, growth-zone location,
   time-resolved elongation, ZT effects, or autostraightening.
   These data contain no ZT contrast and no resolved recovery
   phase, so the separate ZT/autostraightening question remains
   entirely open. The elongation correlation uses start/finish
   lengths only.
4. The duplicate, window-mismatch, and missing-data caveats of
   Phase A (version 2) apply throughout; 55 unmatched plants remain
   a selection caveat.

**Gate 3 verdict:** no model is called supported. The defensible
statement is: *initial stem length is associated with the early rate
of phototropic bending in this dataset; the tested length-aware
population models (M1a, M1d, and in sensitivity M1c) do not improve
held-out trajectory prediction.* Practical implication for the next
fixed-light study: keep L0 as a pre-registered continuous predictor
rather than forcing all seedlings to one length; treat any
growth-restricting agent as a secondary perturbation with its own
side-effects modelled, not as a pure height control. The
discriminating measurements remain those of the action plan's
Phase D (time-lapse centreline + length under fixed light), with
the elongation-correlation fingerprint, not ratio stability, as the
M2 diagnostic to design around, and with latency-type endpoints
(not only whole-trajectory RMSE) if transport is to be tested.

## Reproducibility

All numbers above are generated by scripts in this folder; the
pre-registration and the primary scripts are unchanged by this
revision. An auditor can reproduce every reported value with:

```
python3 phase_a_join.py              # Phase A merge + audit JSON
python3 phase_b_simulation.py        # original Gate 2 (16 reps)
python3 phase_b_gate2_v2.py          # Gate 2 v2 (132 data sets)
python3 phase_c_historical.py        # Phase C primary (M0/M1a/M1d)
python3 phase_c_m1c_sensitivity.py   # Phase C M1c sensitivity
python3 make_gate2_v2_figure.py      # outputs/fig_gate2_v2.png
python3 make_growth_figures.py       # outputs/fig_growth_summary.png
```

Replication checks already run for this revision: re-running
`phase_a_join.py` reproduces `outputs/paired_plants.csv`
byte-identically (md5 e1564a8efb5e93bdea026209d1f0e087 before and
after the coverage/missingness label fix); the M1c sensitivity
script's M0 refit matches the primary M0 median RMSE exactly;
Gate 2 v2 writes one row per simulated data set to
`outputs/gate2_v2_replicates.csv` (132 rows) with per-scenario
counts and Wilson intervals in `outputs/phase_b_gate2_v2.json`.
Independent reproduction by the auditor from these scripts is still
the outstanding step; nothing in this report should be treated as
externally verified until that is done.
