# External-audit follow-up results, 2026-10-16

All analyses below were run in response to the external audit of
2026-10-16. Code: `audit_followup.py`, `exp_design_model_selection.py`,
corrected `round1.py` and `phase_a.py`. Raw outputs:
`results/audit_followup_summary.json`, `results/audit_followup_*.csv`,
`results/exp_design_model_selection.csv`, `results/phaseA_summary.json`.

## H1 as written (within-cluster ranges)

Median within-cluster parameter range, as a fraction of the full
population range (uniform population, static light): k 0.77, tau 0.98,
max_rate 1.00, phi0 0.84. All four parameters exceed the stated 20%
retention threshold. **H1 is supported as written.** (The earlier
IQR-based analysis answered a different, stricter question.)

## H2 as written (spread reduction in percentage points)

Change in median within-cluster range retention, static to flip
(percentage points): k **-21.6** (reduction), tau **+2.2**, max_rate
**0.0**, phi0 **+7.9** (increases). Only k meets the 10-point reduction;
the direction is inconsistent across parameters. **H2 is not supported
as written.**

## H3 as written (behavioural-distance cliffs)

On the same 64 x 64 (k, tau) grid, using Euclidean distance in the
six-feature standardised behaviour space: median adjacent distance
0.123; **20 of 8,064 adjacent edges (0.25%) exceed 5x the median**, with
a maximum ratio of 6.7x. **H3 is supported as written** under this
behavioural-distance definition. This supersedes the earlier conclusion
based on the 2 h half-rise-jump criterion, which was not the written
criterion.

## H7 at matched observation budget

Mean relative parameter recovery error (three population seeds, mean
across seeds), full protocol duration versus every protocol truncated
to a common 6 h budget:

| Protocol | Full | Matched 6 h |
|---|---:|---:|
| static6 | 0.242 | 0.242 |
| flip4_8 | 0.219 | 0.238 |
| sweep12 | 0.179 | 0.221 |
| flip12_14 | 0.174 | 0.237 |
| dflip16 | 0.150 | 0.240 |

At matched budget the best-to-worst gap shrinks from 0.092 to 0.021:
most of the apparent protocol advantage is observation time, not light
schedule. H7's original declared criterion also was not met. **H7 is
not supported as a protocol-ranking claim.**

## Weighted population: max_rate sensitivity

Behavioural twins (nearest neighbour curve RMSE below 0.5 degrees)
occur under every treatment of fitted max_rate: point estimates 36.6%,
profile lower bounds 30.0%, independent prior 35.7%, no cap 37.1%. The
existence of behavioural twins is therefore robust to the max_rate
treatment. However, the fraction of twins whose parameters differ by
more than 50% depends strongly on that treatment (14.5% for point
estimates versus 2.6% for lower-bound or no-cap), because point-estimate
max_rate values carry variation the data did not determine. The weighted
population must be described as a bootstrap-plus-jitter scenario, and
max_rate-specific degeneracy claims must use the lower-bound treatment.

## H6 with phi0 held fixed (corrected code)

Same-cluster parent pairs: 60.7% of recombinants assigned to the source
cluster. Cross-cluster controls: 47.0% assigned to the first parent's
cluster and 62.4% to either parent's cluster. Same-cluster retention is
therefore barely above the cross-cluster control rate. **The earlier
claim of a connected degenerate region is withdrawn.** The defensible
statement is local: recombinants of similar parents often remain
behaviourally similar, at a rate close to that of cross-cluster
controls under this procedure.

## H8 fixed policy as specified (corrected code)

With the fixed policy repeating the preferred protocol (dflip16) while
it fits the 24 h budget and then stopping (no silent fallback), success
rates per 100 plants: random 89.4, fixed 83.4, greedy 88.6, Thompson
63.2. The fixed policy no longer saturates the budget by construction,
and adaptive policies do not beat random in this design. H8 v2 (harder
design in `docs/ADAPTIVE_IDENTIFICATION.md`) remains unrun.

## Phase A on a matched horizon

Population simulations now run to 32.5 h, the longest measured Fig1C
duration, and predicted final angles are evaluated at each plant's own
final time. Recomputed headline values are essentially unchanged:
leave-one-block-out held-out median curve RMSE **11.75 degrees**, mean
band coverage **0.881**; max_rate remains unidentified in **47 of 48**
fits. The earlier full-window numbers were computed with predictions
held constant after 24 h and should be replaced by these.

## Vector stimulus: model-selection design study

Procedure: simulate full datasets under each candidate mechanism at the
160-degree, 2:1 condition (parameters from the weighted population,
2-degree noise, 2 h readouts), fit every candidate to every seedling by
grid search over (k, tau, max_rate) at the candidate's effective angle,
and select the mechanism with the lowest total error. 25 replicate
datasets per cell. Correct-selection probability:

| n per dataset | Physical | Transduced | Circumference | Overall |
|---|---:|---:|---:|---:|
| 10 | 1.00 | 0.52 | 1.00 | 0.84 |
| 20 | 1.00 | 0.88 | 1.00 | 0.96 |
| 40 | 1.00 | 0.88 | 1.00 | 0.96 |

At the 60-degree, 1:1 control, where the mechanisms make nearly
identical predictions, correct selection is at chance (0.28 to 0.36),
which validates the procedure. Under this stated selection procedure,
**n = 20 seedlings per dataset gives about 96% correct model selection**
at the best condition (transduced-source is the hardest truth). This
replaces the withdrawn Welch sample-size claims. It remains a
simulation-based design estimate under the BendLab dynamics and the
weighted-population variability, not a guarantee for laboratory data.

## What remains genuinely open

- Wet-lab validation of any stimulus-model or protocol claim.
- The Model v2 comparison (circadian clock versus biphasic memory
  kernel) on held-out data, and the H8 v2 harder design: specified, not
  run.
- Application of the inverse models to real measured curves: fitted
  sunflower parameters often lie outside the synthetic training ranges,
  so this awaits either wider-range training with uncertainty
  quantification or a domain-adaptation study.
