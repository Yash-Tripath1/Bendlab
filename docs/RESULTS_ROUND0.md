# Results, round 0 — 11 October 2026

Everything below is from `fit_real.py` and `sweep.py`, both seeded, both
rerunnable. Real data is PLOS Biology 2023 S13, sheet Fig1C, 48 plants across
six light treatments.

## 1. H5, the reality anchor

Fits the two-state model `(k, tau, max_rate, phi0)` to each real curve by
bounded least-squares under static light.

Numbers are from the widened-bound refit of 12 October (`tau` upper bound
12 to 48 h). The first version of this table used the narrower bound and is
superseded.

| Block | n | median RMSE (deg) | across-plant spread (deg) | RMSE / spread | pass |
|---|---|---|---|---|---|
| ZT0  | 7 | 1.97 | 5.17  | 0.38 | yes |
| ZT3  | 9 | 4.06 | 5.58  | 0.73 | yes |
| ZT6  | 8 | 6.24 | 8.58  | 0.73 | yes |
| ZT9  | 6 | 3.85 | 5.27  | 0.73 | yes |
| ZT12 | 9 | 4.70 | 11.47 | 0.41 | yes |
| ZT16 | 9 | 6.98 | 9.38  | 0.74 | yes |

Overall median RMSE 4.74 deg against median spread 8.58 deg, ratio 0.55.

**Reading.** The model is wrong by less than real plants differ from each
other. That is the bar we set, and it clears it in all six blocks. It earns
the right to be studied, which is all H5 was ever for.

**The caveat that matters.** 20 of 48 plants still end with `tau` pinned at
the new 48 h bound. Widening the bound moved the wall without emptying it,
which is itself informative: the model does not want a slightly longer lag,
it wants an indefinitely long one, which is what a plant does when the
static-light assumption fails and no lag value can compensate. The pinned
fits concentrate exactly where expected:

| Block | clean fits | median tau |
|---|---|---|
| ZT0  | 7/7 | 4.11  |
| ZT3  | 9/9 | 5.59  |
| ZT6  | 8/8 | 6.87  |
| ZT9  | 4/6 | 9.74  |
| ZT12 | 0/9 | 48.00 (bound) |
| ZT16 | 0/9 | 48.00 (bound) |

This resolves the ambiguity stated in the first version of this section. The
two candidate explanations were "static light is wrong for ZT12 and ZT16" and
"the model is missing a mechanism". Widening the bound falsifies the second:
a missing mechanism would not care which treatment block it was in. The
early-day blocks fit cleanly at tau between 4 and 10 h; the midday and
afternoon blocks want tau without limit. **The static-light assumption is the
failure, and it fails by time of day.**

Consequence for everything downstream: only the 28 clean fits define the
plausible region. ZT12 and ZT16 are excluded from it, not because their data
is bad but because our model cannot represent them.

Also note the spread column is generous to us. It counts genuine plant-to-plant
differences as if they were measurement noise, so passing is the easy bar.

## 2. Degeneracy, two probes on real data

Plant ZT0-1, refit with `tau` held on a grid:

| tau fixed | k | max_rate | phi0 | RMSE |
|---|---|---|---|---|
| 0.25 | 9.76  | 22.94  | 52.24 | 7.085 |
| 0.50 | 10.09 | 121.99 | 51.73 | 6.779 |
| 1.00 | 10.82 | 155.36 | 50.65 | 6.142 |
| 2.00 | 12.53 | 22.57  | 48.55 | 4.897 |
| 4.00 | 16.72 | 30.00  | 44.89 | 2.857 |

RMSE falls 7.09 to 2.86 as tau goes 0.25 to 4.0, and `k` and `phi0` drift with
it. So `tau` is not sloppy on this curve, it carries real information, but
`k` and `phi0` cannot be pinned down without first knowing `tau`. That is the
degeneracy showing up as a ridge, not as a flat floor.

The second probe is exact rather than approximate. Refit with the cap removed
gives RMSE 1.894 against 1.894 with the fitted cap. Identical, because the
realised rate never reaches the cap, so any cap above the peak rate produces
the same trajectory. `max_rate` is unidentifiable from a curve that does not
saturate. Not approximately, exactly.

## 3. H1, does behaviour determine parameters?

10,000 uniform plants, 24 h static light, six clusters on six behaviour
features, seed 1.

Numbers below are from the corrected run of 12 October; the first version of
this table was computed on a corrupted feature column and is superseded (see
the bug log, section 7).

| Parameter | median within-cluster IQR | full range | retained |
|---|---|---|---|
| k        | 0.747 | 2.950  | 25% |
| tau      | 2.048 | 5.749  | 36% |
| max_rate | 19.058 | 37.993 | 50% |
| phi0     | 20.264 | 79.991 | 25% |

A behaviour cluster keeps a quarter to a half of the full parameter range.
The largest cluster, 2,859 plants, spans essentially the entire box for both
k (2.947 of 2.950) and phi0 (79.96 of 79.99), and the entire max_rate range,
while its members are behaviourally near-identical.

**Reading.** H1 holds in the strong form, and the corrected run strengthens
it: retention went from 29-43 per cent to 25-50 per cent. Knowing what a
plant does does not tell you what it is. This is the result the project is
about.

**What the clusters actually are.** Response-magnitude classes, not parameter
classes. Median observed peak rate runs 0.22 to 2.13 deg/h across clusters
and median final angle 4.5 to 41.3 deg, so the split separates strong
responders from weak ones. Correlation with the light angle is moderate at
best: `corr(final_angle, phi0) = 0.64`, `corr(auroc, phi0) = 0.604`.

**The cap is inert under static light.** The observed peak rate carries
almost no information about the cap parameter: `corr(peak_rate, max_rate) =
0.01`, and in a 2,000-plant probe the cap bound the trajectory for 1 plant.
Median observed peak rate is 0.76 deg/h against a median cap of 21.2 deg/h.
This is the same phenomenon as the exact degeneracy on real plant ZT0-1 in
section 2: a cap that never binds leaves no trace on the curve.

## 4. H2, does the flip add information? First probe only

Same 10,000 plants, light steps 45 deg at t = 8 h, integrated as one
continuous run so the rate state carries across the flip. Mean angle drop in
the two hours after the flip is 19.92 deg, so the regime bites.

Within-cluster parameter spread under the flip is mixed against static: k
tightens (median IQR 0.523 against 0.747) while tau (2.334 against 2.048) and
phi0 (25.355 against 20.264) loosen, and max_rate is unchanged because the
cap is inert in both regimes. On this metric, **H2 is not supported yet.**

That is a weak test and it may be the wrong one. Clustering into six groups
throws away most of the information a flip creates, and the k-tightening
hints that a finer metric would find more. A better probe compares
continuous quantities, for instance whether the flip response separates
plants that static features map to the same point. Logged as the next step,
not as a conclusion.

## 5. Weighted population, 12 October

The same sweep as section 3, but plants are drawn where real sunflowers were
actually measured rather than uniformly over the box. Source: the 28 clean
fits from section 1, bootstrap-resampled with declared 15 per cent lognormal
jitter, seed 2, 10,000 plants, `sweep_weighted.py`.

Source region, from the clean fits alone: k 1.63 to 23.03, tau 2.63 to 19.54,
max_rate 3.04 to 45.38, phi0 26.35 to 89.25. No global clip is applied, so the
plausible region is defined by the measurements and nothing else.

| Parameter | within-cluster IQR | weighted range | retains | uniform run |
|---|---|---|---|---|
| k        | 4.606  | 35.115 | 13% | 25% |
| tau      | 3.376  | 34.073 | 10% | 36% |
| max_rate | 21.012 | 75.820 | 28% | 50% |
| phi0     | 8.453  | 109.510 | 8% | 25% |

**Reading.** Degeneracy survives in the plausible region but is weaker. Every
parameter is better determined by behaviour when plants are drawn from where
real plants live: retention falls on all four, tau from 36 to 10 per cent and
phi0 from 25 to 8. The honest statement is no longer "behaviour tells you
almost nothing", it is "behaviour tells you a good deal less than you would
like, and how much depends on where in parameter space you are".

**The cap comes alive.** Under the uniform box the speed limit bound the
trajectory for 1 plant in 2,000. In the weighted population it binds for
7.19 per cent of plants. The cap is not intrinsically inert; it was inert
because the uniform box spends most of its volume on caps far above any rate
those plants would ever reach. This is the strongest argument yet for weighted
sampling: it changes which parameters matter, not just how often they appear.

**Scope limit, stated because it limits every number above.** ZT12 and ZT16
contribute no clean fits, so this population represents early-day light
treatments only. It is not "real sunflowers", it is "the sunflowers our model
can represent".

**Median final angle is 42.4 deg** against a measured plateau of roughly 50 to
60 deg in the same blocks, so the population is centred slightly low. `corr(
final_angle, phi0)` is 0.553, down from 0.64 under uniform sampling.

## 6. Status against the hypotheses

| # | Status |
|---|---|
| H1 | supported under uniform sampling, weaker but present under weighted |
| H2 | not supported on the current metric; metric likely inadequate |
| H3 | not tested, needs a dense parameter sweep |
| H4 | not tested, needs the sweep regime and a cluster-agreement measure |
| H5 | passed 6/6 blocks; 20/48 fits bound-pinned, localised to ZT12 and ZT16 |

## 7. Declared next steps

1. ~~Widen the tau bound and refit~~ — **done 12 October**, section 1. Falsified
   the missing-mechanism explanation; the static-light assumption fails by
   time of day.
2. Fit a non-static light regime to ZT12 and ZT16 and compare RMSE. This is
   now the highest-value step, because recovering those 20 plants widens the
   plausible region and every weighted number depends on it.
3. Replace the cluster-retention metric for H2 with a continuous one.
4. H3: dense 2-D sweep over (k, tau) at fixed cap, look for discontinuity.
5. ~~Weighted population sampling~~ — **done 12 October**, section 5.
6. H6: crossover two plants from the same behavioural cluster, mutate the
   offspring, and measure how often the offspring stay in the class. This
   tests whether the degenerate set is connected or a scatter of isolated
   islands, which decides whether evolutionary search over it is meaningful.
7. H7: rank light protocols by how much they shrink within-class parameter
   spread. This needs a continuous identifiability metric, not cluster
   counts, so it depends on fixing the H2 metric first.
8. The identification game in `docs/IDENT_GAME.md` should draw hidden plants
   from the weighted population, not the uniform box, so that difficulty
   reflects plants that exist.

## 8. Bug log

**12 October: feature/parameter column collision in `sweep.py`. Found by
Umaid, reading the code, before any of us noticed it in the numbers.**

The behaviour feature for observed peak bend rate was named `max_rate`, the
same as the parameter that caps the rate. The feature table wrote the
observed rate under that name, then the parameter loop overwrote the column
with the true cap. Consequences, stated plainly:

- the round-0 clustering ran on five behaviour features plus one true
  parameter, i.e. it partly clustered on the answer key
- the first reported retention figure for max_rate (25 per cent) measured
  the corrupted column and meant nothing
- all section 3 and 4 numbers from the first version are superseded by the
  corrected run of 12 October

What survived: H5 entirely (`fit_real.py` never touches the feature table),
and the direction of H1, which the corrected numbers *strengthen* (retention
25-50 per cent against the corrupted 25-43). The fix: the observed-rate
feature is renamed `peak_rate`, parameter columns in feature tables are
written with a `param_` prefix, and `sweep.py` now fails at import if a
feature name and a parameter name ever collide.

The bug also surfaced a real finding on the way out: the cap is inert under
static light for this parameter box (section 3), which is why the corrupted
and corrected runs agree on the qualitative conclusion.

## Files

| File | Content |
|---|---|
| `results/fit_fig1c.csv` | 48 per-plant fits, params, RMSE, bound flags |
| `results/sweep_features.csv.gz` | 20,000 rows, static and flip features plus parameters |
| `results/sweep_clusters_static.csv` | static-regime cluster summary |
| `results/sweep_clusters_flip.csv` | flip-regime cluster summary |
| `results/sweep_weighted_features.csv.gz` | weighted-population features, static and flip |
| `results/sweep_weighted_clusters_static.csv` | weighted-population cluster summary |
