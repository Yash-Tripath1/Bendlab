# Adaptive identification experiment: design specification

**Status, 13 October 2026.** Version 1 has been implemented and run in
`round1.py`. The design was saturated: random protocol selection produced
89 successful predictions per 100 plants, so no policy comparison was
meaningful. Version 2, specified at the end of this document, was declared
on 13 October 2026 and **has not been run**. Its thresholds are fixed in
advance and must not be revised after v2 output has been examined.

## Purpose

The preceding experiments quantify whether observed behaviour identifies
the underlying parameters. The adaptive identification experiment addresses
a different question: given a limited observation budget, can adaptive
selection of the next light protocol improve prediction of behaviour
under a protocol that has not yet been run?

The experiment therefore compares protocol-selection policies under a
common simulation model, noise model, observation budget and evaluation
rule.

## Outcome measure: predictive identification

Parameter recovery is not used as the primary outcome. Some parameter
directions are weakly identifiable or unidentifiable, so exact parameter
recovery would conflate policy performance with the intrinsic geometry
of the parameter-to-trajectory mapping.

A policy is instead evaluated by prediction on a **held-out protocol**.
After the observation budget has been spent, the policy's posterior
distribution is used to predict the hidden plant's stem-angle trajectory
under a protocol that has not been run. Prediction is successful if the
trajectory RMSE is below a pre-specified tolerance, $\varepsilon$.

This outcome directly measures whether the information obtained is
sufficient for behavioural prediction. A posterior may remain broad
along parameter directions that have little effect on predicted
trajectories and still perform well under this criterion.

## Experimental unit and protocol menu

1. A hidden parameter vector is drawn from the weighted population
   defined by the clean fits to measured sunflower trajectories.
2. The policy selects protocols from a fixed menu until the observation
   budget is exhausted:
   - `static6`: static light for 6 h;
   - `flip4_8`: static light with a 45-degree step at hour 4, total duration 8 h;
   - `flip12_14`: step at hour 12, total duration 14 h;
   - `sweep12`: 12 h moving-light protocol;
   - `dflip16`: two-step protocol over 16 h.
3. Observations are stem angles sampled every 30 min with additive
   Gaussian noise.
4. The policy maintains a posterior distribution over the four model
   parameters.
5. Performance is reported as successful predictions per 100 hidden
   plants, with paired win/tie/loss counts for policy comparisons.

## Policies

| Policy | Selection rule |
|---|---|
| `random` | Uniform random choice among affordable protocols |
| `fixed` | Repeated use of the protocol with the highest identifiability score in the preceding protocol comparison, or termination when the budget cannot accommodate it |
| `greedy` | At each step, selection of the protocol with the largest expected information gain under the current posterior |
| `thompson` | Sampling of a parameter vector from the posterior, followed by selection of the protocol that best distinguishes that sample from the remainder of the posterior |

## Anticipated failure mode

A single informative protocol may capture nearly all of the available
identifiability. In that case, adaptive selection would provide no
advantage over random or fixed selection. Hypothesis H8 is written so
that this outcome is interpretable as a negative result for adaptive
selection rather than as a failure of the experiment. A secondary
question is whether the optimal protocol depends on the region of
parameter space occupied by the hidden plant.

Version 1 realised this anticipated failure mode.

## Version 2 — declared 13 October 2026, not yet run

Individual changes to the budget, noise and success tolerance were
considered insufficient because each leaves an alternative route by which
the design could remain saturated. Version 2 therefore changes the main
difficulty parameters jointly.

| Setting | v1 (run) | v2 (declared) |
|---|---|---|
| Budget | 24 h | **12 h** |
| Observation noise | 2 degrees | **5 degrees** |
| Success tolerance, $\varepsilon$ | 5 degrees RMSE | **2 degrees RMSE** |
| Held-out protocol | `ramp24` | **`ramp24`, unchanged** |
| Population | Weighted population from 44 clean fits | **Weighted population from 44 clean fits** |
| Hidden plants / hypothesis set | 500 / 3,000 | **500 / 3,000** |
| Policies | Random, fixed, greedy, Thompson | **Same four policies and rules** |

### Interpretation rules declared in advance

1. **Saturation rule.** If random protocol selection still produces more
   than 80 successful predictions per 100 plants, v2 is also saturated
   and no policy comparison may be reported. The design must then be
   revised again; an extrapolating held-out ramp is the next candidate
   change. If random produces fewer than 20 successes per 100, the
   experiment is too difficult to discriminate among policies and
   $\varepsilon$ may be revisited, with the change recorded.

2. **Criterion for H8.** Adaptive selection is supported only if the best
   adaptive policy exceeds **both** non-adaptive baselines (random and
   fixed) by at least five successful predictions per 100 plants, with
   paired win/tie/loss counts reported. Superiority over the fixed policy
   alone is insufficient because v1 showed that a fixed protocol can
   perform worse than mixed random selection.

3. **Noise interpretation.** Five degrees is at the upper end of the
   observed residual range; the worst measured-data fit, ZT9-1, has an
   RMSE of 6.76 degrees. Version 2 results must therefore be described as
   obtained under high-noise conditions representative of the noisy end
   of the measured residuals, not as typical conditions.

4. **Seeds.** Random seeds are derived from the experiment-series seed
   base by the same offsets used for v1, and the implementation must
   print them before the first evaluation begins.
