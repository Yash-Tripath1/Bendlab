# Prospective fixed-light study: design simulation results

Date: 2026-10-24. Design simulations only, executed exactly as fixed
in advance in `PHASE_D_DESIGN_SIMULATION_PLAN.md`. No new plants and
no new biological claim. The question answered is narrower and more
practical: if a future fixed unilateral blue-light experiment tests
the tentative early-rate equation prospectively, how many plants
does it need, and which design choices actually help?

## The equation being sized

    r_0-2 = beta_0 + beta_L ln(L0 / 14 mm)
            + beta_I ln(I / 2.25 W/m^2) + beta_theta theta_0 + eps

Pilot inputs from the 213 paired archive plants (planning values,
not findings to be re-claimed): beta_L = 2.12 deg/h per log unit
(about 1.47 deg/h per doubling of starting length), beta_I = 0.20,
beta_theta = -0.139 deg/h per degree, residual SD 3.85 deg/h.
Because pilot estimates are optimistic, power is computed at the
pilot value and at 75% and 50% of it; the 50% case (beta_L = 1.06)
is the prudent planning case and drives the recommendation.
Simulation checks behaved as they should: type I error 0.042-0.060
across cells at beta_L = 0, 95% CI coverage about 0.94-0.95, and
essentially no sign errors among significant results.

## Primary endpoint: how many plants?

Plants required (interpolated; 2,000 simulated experiments per
cell; three covariate designs: A archive-like joint resampling,
B balanced intensity across the archive levels, C wider natural
ln L0 range with 1.5x the archive SD, truncated to 4-45 mm):

| True beta_L | Design A: 80% / 90% | Design B: 80% / 90% | Design C: 80% / 90% |
|---|---|---|---|
| 2.12 (pilot) | 194 / 266 | 194 / 265 | 110 / 141 |
| 1.59 (75%) | 341 / 446 | 347 / 446 | 183 / 255 |
| 1.06 (50%, prudent) | **753 / not reached by 900** | **745 / not reached by 900** | **411 / 569** |

Reading of the three designs, against the decision rules fixed in
the plan:

1. **The headline number is about 750 plants, not about 200.** An
   archive-sized study (about 213 plants) has only about 32% power
   if the true early-rate slope is half the pilot estimate. It is
   adequately powered (about 85% at N = 213) only if the pilot
   point estimate is exactly right, which is not a prudent
   assumption. A future single-lab study should therefore either
   commit to roughly 750 enrolled plants under an archive-like
   design, pool across batches or labs, or accept in advance that
   it can only detect pilot-sized effects.
2. **Balanced intensity buys nothing measurable.** Required N under
   Design B is within about 1% of Design A at every effect size
   (the archive L0-intensity correlation is weak and beta_I is
   small). Per the pre-fixed 10% rule, balanced allocation is NOT
   recommended on power grounds; allocate intensity for practical
   or secondary-endpoint reasons instead.
3. **A wider natural length range is the one real lever.** Drawing
   seedlings across a wider natural size range (Design C) cuts the
   prudent-case requirement from about 750 to about 410 plants
   (and to about 570 for 90% power). This changes the population
   the estimate refers to (a broader size distribution), so it is
   an option to state explicitly in the future pre-registration,
   not a free lunch and not a reason to select or force plants to
   particular lengths within the study.
4. Enrolment targets are analysed plants with usable L0 and
   trajectories. Inflate for expected losses: at 10% unusable, 750
   analysed means about 835 enrolled (arithmetic allowance, not a
   simulated quantity).

## Secondary endpoint: latency stays exploratory

Cox latency power (500 experiments per cell; event times generated
from the archive Cox baseline hazard; at-risk plants only enter
the analysis, about 89% of enrolled):

| Enrolled N | Power at pilot HR 1.42 | Power at prudent HR 1.21 |
|---|---|---|
| 213 | 0.43 | 0.18 |
| 450 | 0.73 | 0.26 |
| 650 | 0.86 | 0.40 |
| 900 | 0.98 | 0.49 |

Interpolated, the pilot hazard ratio needs about 560 enrolled for
80% power (about 730 for 90%). The prudent hazard ratio does not
reach even 50% power at 900 enrolled. Under the plan's decision
rule, latency therefore remains a prespecified EXPLORATORY
secondary endpoint in the future pre-registration (at-risk
population and censoring-aware Cox model defined as in the latency
addendum), never a co-primary endpoint and never a gatekeeper for
testing transport-type trajectory models. Null calibration was
clean (type I 0.048 at N = 213).

Note the structural reason latency is weak here: nearly every
at-risk plant eventually crosses 10 deg (about 99% events), so the
Cox test is limited by the modest spread of ln L0, not by
censoring. Lengthening follow-up would not fix that.

## What these simulations do not do

- They do not test any mechanism. M1a/M1c/M1d selection remains a
  Gate 2 question; these simulations size a regression slope and a
  hazard ratio.
- They assume the archive residual noise in the 0-2 h slope. A
  future study with denser or less noisy angle tracking could
  legitimately do better, but that gain must be re-simulated with
  the new endpoint noise, not assumed.
- They do not size ZT contrasts, recovery/autostraightening
  phases, or growth-restricting-agent effects. For the agent, the
  treatment and interaction terms in the discussion equation
  (beta_A, beta_LA) have no pilot effect sizes; the honest
  sequence is to define the agent, dose, vehicle control, and a
  smallest interaction of interest first, then re-run this same
  simulation framework with treatment allocation included. The
  agent must still be modelled as a perturbation with possible
  direct effects on phototropic signalling, with realised
  elongation measured, not as a pure height control.
- Generation of latency times assumed proportional hazards; the
  archive theta_0 term violated it, so latency powers are
  planning approximations.

## Design recommendation carried forward

For the future fixed-light pre-registration: primary test beta_L
in the equation above; enrol about 750 analysed plants archive-like
(or about 410-570 if a wider natural size range is prespecified and
accepted as the study population); keep L0 continuous; record
starting angle and intensity per plant; latency as an exploratory
censoring-aware secondary; and commit the plan on its own before
any outcomes are collected, so that its priority in time is
verifiable from the repository itself.

Scripts: `phase_d_power_early_rate.py`,
`phase_d_power_latency.py`; outputs
`outputs/phase_d_power_early_rate.{csv,json}`,
`outputs/phase_d_power_latency.{csv,json}`,
figure `outputs/fig_phase_d_power.png`.
