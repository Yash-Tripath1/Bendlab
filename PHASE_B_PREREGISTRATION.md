# Growth-aware phototropism: pre-registered model specification

Written 2026-10-23, before any response outcome is fitted to the paired
length/trajectory data (Phase A is data auditing only). Scope: fixed
unilateral blue light, chamber-grown sunflower seedlings. No
heliotropism, moving light, ZT or autostraightening claims in this phase.

## Data allowed
Kempinski et al. (2026) unilateral archive: 213 plants with paired
trajectory + start/finish length (Phase A merge). Brooks data: no
per-plant length, excluded from length analyses.

## Candidate family (one mechanism at a time; no kitchen-sink fits)
All candidates share: phi = 90 deg fixed; per-plant theta(0) = observed
initial angle; intensity enters via k(I) = a * I^b (wrapper, as Phase B0);
a common opposing term -gamma * theta (equilibrium mechanism, required
by the Phase B0 finding); plant random effects are NOT fitted in
population comparisons.

- **M0** length-independent: k, tau, gamma independent of L0.
- **M1a gain:** k multiplied by (L0/Lref)^alpha. Signature: response
  strength/speed scales with L0; plateau (set by gamma) unchanged.
- **M1c transport:** tau = tau0 + max(L0 - Lref, -0.9*tau0*v)/v with
  shared v > 0. Signature: latency scales with L0; amplitude/plateau
  unchanged.
- **M1d opposing:** gamma multiplied by (L0/Lref)^delta. Signature:
  late-window plateau varies with L0; early dynamics near-unchanged.
- **M2 growth-generated (simulation fingerprint only; cannot be fitted
  to start/finish lengths alone):** bend per unit cumulative elongation
  approximately constant across plants under its stated assumptions.

Lref = median L0 of the paired set. Parameter bounds: a in [0.01, 80],
b in [-0.5, 2], tau0 in [0.05, 40] h, gamma in [0, 5] /h, alpha/delta in
[-2, 2], v in [1, 200] mm/h. max_rate fixed non-binding (60 deg/h) in
population fits (Phase B0 showed it is unidentified here).

## Pre-registered comparisons (Phase C, historical, labelled partial)
1. Association: per-plant outcomes (latency to 10 deg, mean rate 0-2 h,
   angle at 8 h, late-window plateau 16-21 h, total angular change)
   regressed on log L0 with intensity (log) and initial angle as
   covariates. Report coefficients with 95% CI; no mechanism language.
2. Prediction: M0 vs M1a vs M1d (M1c included only if latency signal
   appears) by 5-fold plant-held-out CV stratified by intensity, on the
   213 paired plants. Adoption rule: an M1 variant is "supported for
   association-level prediction" only if median held-out RMSE improves
   >= 5% over M0 AND the sign of its L0 coefficient is stable across
   folds. Otherwise report ambiguity and retain M0.
3. Net-growth check: correlation of interval-average elongation rate
   with total angular change, partial on intensity. Labelled
   interval-average (length window about 0.9 h longer than the
   trajectory window at the median).

## Phase B simulation identifiability (before/alongside Phase C)
Generators M0/M1a/M1c/M1d (+M2 fingerprint in silico), plant variability
calibrated to the archive (L0 empirical distribution, intensity mix,
initial-angle spread, circumnutation-scale noise). At N = 213 and
N = 10,000, fit all candidates and report the selection confusion
matrix under three observation views: (i) tip only, (ii) tip + L0,
(iii) tip + L0 + start/finish length. A distinction that cannot be
recovered at N = 213 must be reported as an observational-equivalence
class, not fitted harder.

## Falsification / honesty rules
- No mechanism claim from association alone; language is "consistent
  with / not distinguishable from".
- Brooks data cannot select among these models (no L0) and will not be
  used to do so.
- If Gate 2 (simulation) shows two mechanisms indistinguishable at
  N = 213, Phase C reports them as a class.
