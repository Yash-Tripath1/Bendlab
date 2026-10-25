# Growth-aware phototropism: Phase B (simulation) and Phase C (historical) results

Pre-registration: `PHASE_B_PREREGISTRATION.md` (written before outcome
fitting). Data: Phase A frozen merge, 213 paired plants. Scope: fixed
unilateral blue light only. Workstream separation from Phase B0 is
unchanged: nothing here validates or is validated by Workstream A
(external tip-angle benchmark) or Workstream B (shape-extension
parameter recovery).

## Phase B: can these mechanisms be distinguished at all?

Simulation with archive-calibrated variability (empirical L0 and
intensity distributions, plant random effects, circumnutation-scale
noise), candidates fitted as population models and selected by
held-out-plant RMSE. Effect sizes used were substantial (gain exponent
alpha = 0.8, transport path effect, opposing exponent delta = 1.0);
smaller true effects will be harder.

- With an L0 effect present, the correct mechanism was selected in
  **16 of 16 replicates** for each of M1a (gain), M1c (transport),
  M1d (opposing) at N = 213 using tip trajectories + L0.
- With NO length effect (M0 true), selection was poor: M0 chosen in
  only 5 of 16 replicates; the rest scattered across M1 variants.
  Proving "no length effect" is much harder than detecting one, at
  least under plant-level random effects of this size.
- Ignoring L0 entirely (tip only) costs little prediction: median
  held-out RMSE ratio M0/oracle = 1.06. Observational consequence:
  the mechanisms are *distinguishable in selection* mainly because
  their L0 signatures differ across the L0 range, not because M0
  predicts badly. Tip-angle-only data without measured L0 cannot run
  this selection at all.
- M2 fingerprint: correlation between final bend and cumulative
  elongation discriminated growth-generated bending in simulation
  (r = 0.65 under M2 vs 0.10 under gain-modulated bending). The
  "stable bend-per-unit-elongation" version did NOT discriminate
  (coefficient of variation 0.51 under both): the fingerprint to carry
  forward is the correlation, not ratio stability.

**Gate 2 verdict:** M1a/M1c/M1d are mutually distinguishable at
N = 213 *if* effects of the simulated size exist; M0-vs-M1 is the weak
direction. Phase C is therefore licensed to test M1 variants, with
"retain M0 on ambiguity" as the expected honest outcome for small
effects.

## Phase C: what the 213 paired plants actually say

Associations (per log unit of L0, controlling log intensity and
initial angle; plant-bootstrap 95% CI):

| Outcome | Coef per log L0 | 95% CI |
|---|---:|---:|
| Early bending rate, 0–2 h | **+2.12 deg/h** | **[0.66, 3.62]** |
| Latency to 10 deg | −0.75 h | [−2.02, 0.38] |
| Angle at 8 h | +0.23 deg | [−4.76, 5.48] |
| Late-window plateau, 16–21 h | −1.62 deg | [−5.46, 2.19] |
| Total angular change | −1.62 deg | [−5.82, 2.09] |

Interval-average elongation rate correlates with total angular change
after accounting for intensity (partial r = 0.48). This is an
association between two whole-plant summaries over slightly different
windows; it is not evidence about local differential growth.

Held-out prediction (5-fold, stratified; pre-registered adoption rule:
>= 5% median RMSE improvement and stable L0-parameter sign):

| Model | Median held-out RMSE |
|---|---:|
| M0 (no length) | **10.25 deg** |
| M1a (gain × (L0/Lref)^alpha) | 10.41 deg (−1.5%) |
| M1d (opposing × (L0/Lref)^delta) | 10.35 deg (−1.0%) |

Neither variant is supported under the rule. The gain exponent's sign
was stable across folds (+ in all 5) yet prediction did not improve;
the opposing exponent's sign was not stable. **M0 is retained.**

## Interpretation, kept narrow

1. In this archive, longer seedlings bend faster in the first two
   hours (association, intensity- and posture-adjusted). The
   association does not persist into angle at 8 h or the late-window
   plateau. That pattern is *directionally consistent* with the
   gain/geometry family (M1a/M1b) and not with a length-dependent
   opposing term (M1d), but Phase C cannot and does not select a
   mechanism: the predictive test that could have supported M1a
   failed its pre-registered threshold.
2. The simulation explains why both can be true: a real early-rate
   L0 signature can coexist with negligible whole-trajectory
   predictive gain, because most trajectory variance is plant-level
   variability unrelated to L0.
3. Nothing here bears on local curvature, growth-zone location,
   time-resolved elongation, ZT effects, or autostraightening. The
   elongation correlation uses start/finish lengths only.
4. The duplicate, window-mismatch, and missingness caveats of Phase A
   apply throughout; 55 unmatched plants remain a selection caveat.

**Gate 3 verdict:** no model is called supported. The defensible
statement is: *initial stem length is associated with the early rate
of phototropic bending in this dataset; length-aware population models
do not yet improve held-out trajectory prediction.* The discriminating
measurements remain those of the action plan's Phase D (time-lapse
centreline + length under fixed light, L0 as a pre-registered
predictor), with the elongation-correlation fingerprint, not ratio
stability, as the M2 diagnostic to design around.
