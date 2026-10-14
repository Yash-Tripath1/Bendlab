# Results II: synthetic-population experiment series

**Date:** 13 October 2026  
**Source:** `round1.py`  
**Population:** simulated plants sampled from the empirically weighted
parameter region

All experiments in this document use simulated plants drawn from the
weighted population derived from the clean measured-data fits. No
additional measured data were introduced. All decision thresholds were
specified in the analysis script before the results were examined.
Total elapsed time was approximately 14 seconds on one processor core.

Summary figure: `results/figures/round1_dashboard.png`.

> **Amendment, 13 October 2026.** This experiment series was rerun using
> the clock-corrected weighted population (44 clean fits spanning all six
> stimulus-start times). The original run used 28 morning-only fits
> produced by the time-base error in `fit_real.py` (see the correction in
> `docs/RESULTS_ROUND0.md`). All numerical values below are from the
> corrected run. Three conclusions are unchanged: H3 falsified as
> specified, H6 supported with incomplete retention, and H7 not supported
> under its declared criterion; H8 remains saturated. **The H4 conclusion
> changed.** On the corrected population, behavioural clusters do not
> persist across light regimes (ARI 0.442, compared with 0.606 in the
> original run); H4 is therefore supported rather than falsified. The
> original H4 interpretation is retracted.

## H3: Discontinuities in parameter space — falsified as specified

A dense 64 × 64 grid was evaluated over response gain (`k`) and sensing
lag (`tau`) at `phi0 = 45` degrees and `max_rate = 30` degrees h⁻¹ under
static light for 24 h. The pre-specified discontinuity criterion was an
adjacent-cell change in half-rise time greater than 2.0 h.

**Result:** 0 of 8,064 adjacent edges satisfied the criterion. The
largest adjacent change was 1.00 h.

Behaviour therefore varies smoothly over the sampled parameter region at
this grid resolution and under the selected feature definitions. H3 is
not retained. This conclusion does not exclude discontinuities at finer
resolution or under alternative behavioural features, such as overshoot
under step-change regimes.

## H4: Persistence of behavioural clusters across light regimes — supported

The same 6,000 weighted simulated plants were clustered under static light
and under a 12 h sawtooth light sweep (±45 degrees about each plant's own
`phi0`), using the same six behavioural features and six clusters in each
regime. Cluster persistence was defined in advance as an adjusted Rand
index (ARI) of at least 0.50.

**Result:** ARI = 0.442.

The behavioural clusters do not persist across the two light regimes. The
classes are therefore properties of the plant–protocol combination rather
than intrinsic plant categories. The original analysis reported ARI
0.606 and the opposite conclusion; that population excluded all afternoon
stimulus-start groups because of the time-base error and is retracted.

An implication is that a cluster label should not be interpreted as a
plant type independent of the measurement protocol. This finding is
consistent with the motivation for H2—that richer light regimes may reveal
additional structure—although H2's cluster-retention metric did not itself
demonstrate improved parameter recovery.

## H6: Connectivity of the degenerate parameter set — supported with incomplete retention

Two behaviourally equivalent source parameter vectors were recombined
parameter by parameter. Each parameter of the recombinant was selected
from one of the two sources with equal probability; mutation was then
applied independently to each parameter with probability 0.5 and standard
deviation equal to 10 per cent of the weighted parameter range. Each
recombinant was assigned to the nearest behavioural-cluster centroid.

| Source pair | Recombinants assigned to the reference source class |
|---|---:|
| Same behavioural cluster (n = 300) | **57.3%** |
| Different clusters; first source class (n = 234) | 29.5% |
| Different clusters; either source class (n = 234) | 53.8% |

Recombinants of behaviourally equivalent sources remained in the source
class at approximately twice the rate obtained when scored against the
first source class of cross-cluster controls. The degenerate set is
therefore connected over the sampled neighbourhood rather than consisting
entirely of isolated parameter combinations. Retention is nevertheless
incomplete: 42.7 per cent of same-cluster recombinants were assigned
outside the source class. The region is thus connected but not flat, and
search or sampling procedures traversing it require repeated membership
assessment.

The comparison against the first source class (57.3 versus 29.5 per cent)
is the more informative control. Assignment to either source class in
cross-cluster pairs is a union event over two classes and therefore has a
higher chance rate.

## H7: Differences in identifiability among light protocols — not supported as specified

For each protocol, 1,000 weighted simulated plants were simulated.
Gaussian observation noise with standard deviation 2 degrees was added,
and each plant's parameters were estimated by those of its nearest
neighbour in trajectory space. Recovery error was defined as the absolute
parameter difference divided by the population 5–95 percentile span.
H7 required a best-to-worst protocol difference of at least 0.10 in mean
relative error.

| Protocol | Duration (h) | Mean relative error | `k` | `tau` | `max_rate` | `phi0` |
|---|---:|---:|---:|---:|---:|---:|
| `dflip16` | 16 | **0.153** | 0.111 | 0.085 | 0.246 | 0.168 |
| `flip12_14` | 14 | 0.178 | 0.154 | 0.149 | 0.239 | 0.171 |
| `sweep12` | 12 | 0.183 | 0.143 | 0.172 | 0.272 | 0.143 |
| `flip4_8` | 8 | 0.236 | 0.186 | 0.188 | 0.290 | 0.282 |
| `static6` | 6 | 0.244 | 0.226 | 0.190 | 0.278 | 0.280 |

**Result:** best-to-worst difference = 0.091, below the specified 0.10
threshold. H7 is therefore not supported as declared.

Two descriptive observations are reported without altering that
conclusion. First, the ordering is consistent: every dynamic protocol
ranked above static light, and the two-step protocol ranked first.
Second, `max_rate` had the largest recovery error under nearly every
protocol, consistent with the exact unidentifiability demonstrated for
non-saturating trajectories. Under the two-step protocol, `tau` was the
most accurately recovered parameter (0.085). These observations do not
meet the pre-specified criterion for H7.

## H8: Adaptive protocol selection — original design saturated

The experiment used 500 hidden weighted plants, a 24 h observation
budget, additive noise of 2 degrees, and a hypothesis set of 3,000
weighted parameter vectors. After the budget was spent, each policy was
scored by prediction of the held-out `ramp24` trajectory. Success was
defined as prediction RMSE no greater than 5 degrees.

| Policy | Successful predictions per 100 plants |
|---|---:|
| Random | **89.4** |
| Greedy expected-information-gain | 88.6 |
| Fixed (`dflip16`) | 83.2 |
| Plug-in Thompson sampling | 63.2 |

For greedy versus fixed selection, the paired win/tie/loss counts were
37/406/10.

The principal result is the saturation of the design. Under a 24 h
budget, observation itself provides most of the attainable predictive
information: random protocol selection produced 89.4 successful
predictions per 100 plants. Adaptive selection did not improve on random
selection, and repeated use of the single highest-ranked protocol
performed worse than mixed selection.

The substantially lower value for plug-in Thompson sampling (63.2 per
100; binomial standard error approximately 2 per 100) is interpreted as a
consequence of the plug-in approximation used in this implementation,
which bases decisions on individual posterior samples and can select
protocols that reduce entropy without improving held-out prediction. It
is not interpreted as evidence against Thompson sampling in general.

A more demanding version of the experiment has been specified in advance
in `docs/ADAPTIVE_IDENTIFICATION.md`. Until the design discriminates among
policies, H8 cannot be assessed.

## Summary of hypothesis status after experiment series 1

| Hypothesis | Status |
|---|---|
| H1 | Supported under uniform sampling; weaker but present under weighted sampling |
| H2 | Not supported under the cluster-retention metric |
| H3 | Falsified as specified: no discontinuities at the sampled resolution |
| H4 | Supported: behavioural clusters do not persist across light regimes (ARI 0.442) |
| H5 | Supported in all six stimulus-start-time groups; 4/48 fits bound-pinned (ZT9) |
| H6 | Supported with incomplete retention: connected degenerate region, 42.7% of recombinants assigned outside the source class |
| H7 | Not supported under the declared threshold (observed difference 0.091 < 0.10) |
| H8 | Not assessable in the original saturated design |

## Interpretation

Of the eight hypotheses, H3 and H7 were not retained under their
pre-specified criteria, H8 could not be assessed under the original
design, H2 remains dependent on an inadequate metric, and H1, H4, H5 and
H6 were supported with the qualifications stated above.

Taken together, the corrected results support three conclusions:

1. observed bending behaviour is informative, but it is a property of the
   plant under a particular light protocol rather than a protocol-independent
   plant type;
2. the underlying parameters are less identifiable than the behaviour;
3. none of the light protocols evaluated changed that relationship by an
   amount meeting the pre-specified criterion.

The earlier description of behavioural type as robust across regimes was
based on the retracted H4 result and is withdrawn.

## Limitations

- With the exception of the H5 fits, the experiments characterise the
  simulator rather than living plants. After the 13 October clock
  correction, the fitted population spans all six stimulus-start times.
  Its principal limitation is the exclusion of four ZT9 plants whose
  rapid onset is outside the dynamics of the present model; ZT9 is
  therefore represented by two of its six plants in the weighted
  population.
- Nearest-neighbour recovery (H7) is a coarse identifiability proxy. A
  posterior-volume or Fisher-information analysis could produce a different
  protocol ranking.
- The use of six clusters is a declared modelling choice rather than a
  derived optimum. The H4 ARI and the H6 retention rate are conditional on
  that choice.
- The H8 hypothesis set is finite (3,000 parameter vectors). A continuous
  posterior representation would smooth the posterior-mean prediction and
  might increase all success rates.

## Independent audit

Following critical review of the initial results, the principal findings
were re-derived through independent code paths in `audit_round1.py`, and
the simulator was compared with closed-form solutions in limiting regimes.
All checks passed. The audit verified the following.

- **Simulator against analytical mechanics.** In the relevant limit, the
  model is equivalent to a damped pendulum in the angle between stem and
  light. Simulated overshoot agreed with the closed-form prediction to
  0.001 degrees in two damping regimes (10.067 versus 10.068 degrees and
  14.17 versus 14.18 degrees), and the oscillation period agreed to
  0.002 h (3.488 versus 3.490 h). Three independent integration paths
  agreed to within $1.4\times10^{-14}$.
- **H5 from the source data.** All 48 per-plant RMSEs were recomputed
  from the original workbook and saved parameters using elapsed time since
  stimulus onset: median 1.801 degrees (reported 1.80), median spread
  8.582 degrees (reported 8.58), with per-plant deviation below
  $10^{-14}$. A regression check requires each fitted start time to
  equal the stimulus-onset ZT of its treatment group and confirms the
  number of bound-pinned fits, preventing silent recurrence of the
  time-base error.
- **Exact degeneracy.** RMSE for ZT0-1 with and without the maximum-rate
  limit was 1.8939 degrees in both cases.
- **Parameter retention.** Independent recomputation gave 9.3, 3.7, 13.6
  and 11.9 per cent for `k`, `tau`, `max_rate` and `phi0`, respectively,
  compared with the reported 9, 4, 14 and 12 per cent.
- **H4 stability.** ARI values across three clustering seeds were 0.442,
  0.442 and 0.444, all below the 0.50 persistence threshold. The corrected
  H4 conclusion is therefore not attributable to a particular clustering
  seed.
- **Information levels for H8.** Successful prediction increased from
  30 per cent with no plant-specific data to 44 per cent after one noisy
  six-hour static trajectory and 89 per cent under the full budget. The
  high full-budget performance is thus attained progressively and is not
  explained by a single short trajectory alone.

Three errors were identified in the initial version of the audit. All
three occurred in the audit code rather than in the analysis pipeline,
and their failure modes are relevant to the use of independent checks.

1. The analytical pendulum calculation treated angle in degrees as though
   it were in radians, overstating the natural frequency by a factor of
   13.4 and producing an apparent simulator failure. After correction,
   theory and simulation agree to three decimal places.
2. The first H1 check tested the stronger proposition that plants in the
   same cluster have nearly identical trajectories. That proposition was
   not part of H1. Same-cluster trajectories can differ by approximately
   13 degrees at a given time because clustering summarises trajectories by
   features rather than requiring pointwise identity. The stated H1 claim,
   parameter-range retention, reproduces.
3. The first H8 check asserted that one short trajectory was already
   sufficient for successful prediction. The corrected information-level
   analysis gives 44 per cent for that condition.

A fourth error, larger in consequence than these three, was identified
after the audit: the ZT time-base error in `fit_real.py` (see
`docs/RESULTS_ROUND0.md`). The initial audit did not detect it because its
H5 check used the same absolute-ZT convention as the fitting code. The
check therefore verified the arithmetic of an incorrectly defined
quantity. Both scripts have been corrected, and the audit now evaluates
elapsed time and includes the regression check described above. This is
recorded because an independent code path does not constitute an
independent audit if it shares the assumption under examination.

The audit also refined the interpretation of H6. Connectivity holds for
typical curve-equivalent pairs but is not uniform over the full parameter
range. In a sample of 40 curve-equivalent pairs, 24 recombinant parameter
vectors remained within 3 degrees of the source trajectories, with median
maximum deviation 1.88 degrees. Deviation tended to increase with
separation in `k`: median 1.53 degrees below 0.1 of the parameter range
and 3.4–4.4 degrees above that value, although only six of the 40 pairs
were in the more separated group. For the most widely separated equivalent
pair identified, separation was concentrated in `max_rate` (22 versus
260 degrees h⁻¹, the exactly unidentifiable parameter), and the midpoint
trajectory deviated by only 1.07 degrees. An earlier apparent 33-degree
separation effect did not reproduce on the corrected population and is
attributed to the morning-only sample. Whether the connected region
narrows at its most extreme points remains unresolved. The audit also
confirmed that `phi0`, as the experimental light condition, must be held
fixed in crossover analyses rather than averaged between sources.

## Computational cost

The full experiment suite performs approximately 44.1 million Euler
integration steps. Each step updates two state variables using six
arithmetic operations, corresponding to approximately 0.44 GFLOP on one
processor core. The short runtime follows from the low dimensionality of
the model and does not affect the interpretation of the results.

## Files

| File | Content |
|---|---|
| `round1.py` | Complete analysis script; all constants and criteria are declared at the top |
| `audit_round1.py` | Independent re-derivation and analytical validation |
| `results/round1_h7_protocols.csv` | Protocol-recovery table |
| `results/round1_h8_policies.csv` | Policy-performance table |
| `results/figures/round1_dashboard.png` | Six-panel summary figure |
