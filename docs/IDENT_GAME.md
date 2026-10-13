# The identification game (round 2 design sketch)

**Status, 13 October: v1 implemented and run in `round1.py`. The game as
specified is saturated — random protocol choice scores 89 per 100, so no
policy comparison is meaningful yet. The harder v2 below was declared on
13 October 2026 and has NOT been run; its thresholds are fixed in advance
and must not be edited after seeing v2 output.**

Round 0 measured whether behaviour identifies parameters. Round 2 turns the
question into a scoreable game, so that protocol-choice policies can be
compared the way the matching hackathon compared asking policies.

Draft, 11 October 2026. Every number here is a proposal.

## Why a game at all

Mapping the degenerate set (H1, H3, H4, H6) is measurement and needs no
objective. Asking *which experiment to run next* (H7) is a decision, and a
decision needs a score. This document defines that score. It is deliberately
built to reuse the sequential-matching harness shape: episodes, actions,
budgets, policies, seed-block statistics.

## Mapping from the matching problem

| Sequential matching | Identification game |
|---|---|
| Hidden preferences of a member | Hidden parameter vector of a plant |
| Ask a clarification question | Run a light protocol on the plant |
| Answer, delayed up to 40 days | Angle curve, observed every 30 min |
| 12 asks per day | Budget: total hours of light exposure |
| MSMI (rare, binary, delayed) | Predictive identification (see below) |
| Policy: who to ask about | Policy: which protocol to run next |

## The objective: predictive identification, not parameter guessing

The tempting score is "guess the parameters within tolerance". It is wrong,
and round 0 already proved why: along sloppy directions the parameters are
not recoverable at any budget, so a parameter-guessing score mostly measures
which plants were lucky draws from stiff directions.

The honest objective is prediction. Success is defined on a **held-out
protocol**: after spending the budget, the policy's posterior must predict
the plant's angle curve under one protocol it never ran, within tolerance
eps, for the protocol's full duration.

    identification = predict-the-unseen-curve, on budget, within eps

This measures what identifiability is actually for. A posterior that is wide
along sloppy directions but predicts new curves accurately *passes*, which is
the correct verdict: the sloppy directions do not matter for behaviour.

- eps: proposed 5 degrees, the median per-plant fit RMSE from round 0, so
  "as good as our best model fits real data" is the bar.
- Held-out protocol: chosen by the evaluation harness, never shown to the
  policy. Split by world, mirroring the disjoint-seed rule from the matching
  kit.

## Episode

1. Draw a hidden plant from `generate_plants.py` (uniform now, weighted once
   the fit defines a plausible region).
2. Protocol menu, fixed and public, each with a cost in hours:
   - `static` 6 h
   - `flip@4` 8 h (45 degree step at hour 4)
   - `flip@12` 14 h
   - `sweep` 12 h (moving light)
   - `double-flip` 16 h
3. The policy picks protocols until the budget (proposed 24 h) is spent.
4. Observations: angle every 30 min plus Gaussian noise. Noise scale from
   real data: per-plant fit residuals, median about 2-5 degrees. No clean
   curves; a policy that only works without noise is not a result.
5. Belief: posterior over the 4-D parameter box on a grid. Four dimensions is
   small enough for exact grid Bayes; no MCMC, no particle filter.
6. Score: identifications per 100 plants, plus W/T/L against each baseline.

Note the structural difference from MSMI: observations are dense. MSMI gave
about one binary event per episode, which is why the matching work needed
directional-response proxies for online learning. Here every 30 minutes
produces a continuous measurement, so the sparse-reward pathology does not
exist and no proxy is needed.

## Policies to compare

| Policy | Rule |
|---|---|
| `random` | uniform choice from affordable protocols |
| `fixed-best` | the single protocol with the best round-0 identifiability gain, repeated or stopped |
| `greedy` | each step, the protocol maximising expected identification gain under the current posterior |
| `thompson` | sample a parameter vector from the posterior, choose the protocol that best distinguishes that sample from the rest of the posterior |

Statistics reuse the matching kit: seed blocks, percentile bootstrap over
blocks, exact sign-flip permutations, W/T/L beside every interval, power
analysis before believing any ordering.

## Pre-mortem, written before running anything

The matching round found that asking at all was a step function and the
choice of asking rule moved coverage by about 0.003. The same failure is
plausible here: if one cheap protocol captures nearly all available
identifiability, adaptive policies will tie it and the honest headline will
again be a negative result. H8 is written so that outcome is a finding, not a
disappointment. The interesting sub-question either way: does the answer
depend on the plant, i.e. do different regions of parameter space need
different protocols?

## Harder variant v2 — declared 13 October 2026, not yet run

One change at a time was considered and rejected: each single change
leaves escape routes. v2 tightens all four screws together, because the
v1 failure mode was total saturation.

| Setting | v1 (run) | v2 (declared) |
|---|---|---|
| Budget | 24 h | **12 h** |
| Observation noise | 2 deg | **5 deg** |
| Success tolerance eps | 5 deg RMSE | **2 deg RMSE** |
| Held-out protocol | ramp24 (within seen phi0 range) | **ramp24, as before** |
| Population | weighted, 28 morning fits (bug) then 44 | **weighted, 44 clean fits** |
| Hidden plants / hypothesis set | 500 / 3,000 | **500 / 3,000** |
| Policies | random, fixed, greedy, thompson | **same four, same rules** |

Rules that bind the interpretation, declared now:

1. **Hardness gate.** If random still scores above 80 per 100, v2 is
   also saturated and no policy comparison may be reported; redesign
   again (extrapolating held-out ramp is the next lever). If random
   scores below 20, the game is too hard to discriminate and eps is
   revisited — with the change logged, not silently applied.
2. **Support criterion for H8.** Adaptive choice is supported only if
   the best adaptive policy beats BOTH non-adaptive baselines (random
   and fixed) by at least 5 successes per 100, paired W/T/L reported.
   A win against fixed alone does not count: v1 showed fixed can be
   worse than mixing.
3. **Noise honesty.** 5 deg is the top of the observed residual range
   (worst real fit, ZT9-1, is 6.76 deg); v2 results must be reported as
   "at the noisy end of real", never as typical conditions.
4. Seeds derive from the round-1 seed base by the same offsets; the
   implementation must print them before the first episode runs.
