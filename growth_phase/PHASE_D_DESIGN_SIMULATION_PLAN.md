# Prospective fixed-light study: design simulation plan

Date: 2026-10-24. Status: DESIGN SIMULATION ONLY. No new plants, no
new biological data, and no new claim about the archive. This plan
fixes, before the design simulations are run, how the tentative
early-rate equation from the Phase C pilot will be turned into
sample-size and design guidance for a future fixed unilateral
blue-light experiment. Writing it before running the simulations
prevents the simulation grid itself from being tuned to a preferred
answer.

## The hypothesis to be tested prospectively (not a discovered law)

Primary endpoint model for a future experiment:

    r_0-2,i = beta_0
              + beta_L * ln(L0,i / 14 mm)
              + beta_I * ln(I_i / 2.25 W/m^2)
              + beta_theta * theta_0,i
              + epsilon_i

where r_0-2 is the bending rate over 0-2 h (deg/h) measured exactly
as in the archive analysis (linear slope of tip angle on time over
0-2 h), L0 is starting centreline stem length, I is fixed
unilateral blue-light intensity, and theta_0 is starting angle.
The primary test is beta_L (two-sided, alpha = 0.05). Pilot values
from the 213 paired archive plants, used only as planning inputs:
beta_L = 2.12 deg/h per log unit, beta_I = 0.20, beta_theta =
-0.139 deg/h per degree, residual SD = 3.85 deg/h, R^2 = 0.09.
A doubling of L0 corresponds to 2.12 * ln 2 = about 1.47 deg/h.

Secondary endpoint: time to first reaching 10 deg, analysed by the
censoring-aware Cox model of `PHASE_C_LATENCY_ADDENDUM.md` on the
at-risk population (theta_0 < 10 deg). Pilot: HR 1.42 per log unit
of L0, 95% CI [0.97, 2.06].

Explicitly out of scope for these simulations: ZT effects (the
future design would need deliberate multi-ZT sampling; nothing here
sizes that), autostraightening/recovery (needs a light-removal
phase), growth-restricting agents (a later perturbation; no pilot
effect size exists, so no honest power number can be computed yet),
and any mechanism selection among M1a/M1c/M1d (Gate 2 already covers
what tip trajectories can and cannot distinguish).

## Simulation 1: power for the primary early-rate test

Data-generating model: the equation above with pilot beta_I,
beta_theta, and residual SD held fixed, and beta_L varied because
pilot point estimates are optimistic planning inputs:

- beta_L = 2.12 (pilot value),
- beta_L = 1.59 (75% of pilot),
- beta_L = 1.06 (50% of pilot, the prudent planning case),
- beta_L = 0 (type I error calibration).

Covariate designs, all drawn from the 213 paired archive plants:

- Design A, archive-like: (L0, I, theta_0) resampled jointly.
- Design B, balanced intensity: (L0, theta_0) resampled jointly and
  intensity assigned in balanced rotation across the 10 archive
  intensity levels, breaking the archive L0-intensity correlation
  (intensity groups account for 8.4% of L0 variance).
- Design C, wider natural length range: (I, theta_0) resampled
  jointly; ln L0 drawn from a normal distribution with the archive
  mean and 1.5x the archive SD, truncated to 4-45 mm. This asks
  what recruiting across a wider natural size range (not forcing
  plants to a length) would buy.

Sample sizes per design and effect: 50, 75, 100, 150, 200, 300,
450, 650, 900 plants. At least 2,000 simulated experiments per cell,
each analysed by the exact planned OLS fit. Reported per cell:
power (fraction with p < 0.05 for beta_L), coverage of the 95% CI,
mean CI width, and the sign-error fraction among significant
results. Required N for 80% and 90% power is interpolated from the
grid and always quoted for the prudent (50%) effect as the headline,
with the pilot-effect number shown as the optimistic bound.

## Simulation 2: power for the secondary latency (Cox) test

Event times are simulated from the fitted archive Cox model
(baseline cumulative hazard with the pilot log-intensity and
theta_0 coefficients), with the log-L0 hazard ratio varied:
1.42 (pilot), 1.21 (half the pilot log-hazard, prudent case), and
1.00 (null calibration at the archive size only). Covariates are
resampled jointly from the paired archive rows; plants with
theta_0 >= 10 deg are generated but excluded from the at-risk
analysis (as the future analysis prespecifies), and censoring is at
each plant's resampled last observation time. At least 500
simulated experiments per cell at enrolled N = 150, 213, 300, 450,
650, 900, each analysed by the prespecified Cox model. Reported:
power for the log-L0 term, mean analysed (at-risk) n, event and
censoring fractions. This simulation assumes proportional hazards
for generating event times although the archive theta_0 term
showed non-proportionality; it is a planning approximation and will
be labelled as such.

## Decision rules for the design recommendation

1. The recommended enrolment target is the smallest simulated N
   reaching at least 80% power for beta_L = 1.06 (prudent case)
   under Design A or B, whichever the future experiment can
   actually implement; the pilot-effect N is reported but never
   used as the recommendation on its own.
2. Balanced intensity (Design B) is recommended over archive-like
   allocation only if it reduces the required N by at least 10% at
   the prudent effect; otherwise allocation is left to practical
   constraints.
3. A wider natural L0 range (Design C) is reported as an option
   with its required N, never as an instruction to select plants
   by length in a way that would change the population studied.
4. The latency endpoint remains secondary unless Simulation 2 shows
   at least 80% power at the recommended N under the prudent hazard
   ratio; otherwise it is declared exploratory in the future
   pre-registration.
5. Simulations size the early-rate and latency tests only. They do
   not convert the pilot association into a mechanism, and the
   future experiment's pre-registration must be committed
   separately before any outcome data are collected.
