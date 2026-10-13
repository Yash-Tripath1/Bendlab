# Results, round 0 — 11 October 2026

Everything below is from `fit_real.py` and `sweep.py`, both seeded, both
rerunnable. Real data is PLOS Biology 2023 S13, sheet Fig1C, 48 plants across
six light treatments.

> **Correction, 13 October 2026.** Sections 1 and 5 were rewritten after
> Anadi Tripathi found a time-base bug in the fitter (bug log, section 8).
> The first version claimed the static-light assumption "fails by time of
> day" and excluded all midday/afternoon plants from everything downstream.
> **That claim is retracted.** The afternoon plants were never unfittable;
> we were fitting them on the wrong clock. Every number that depended on
> the fits has been rerun; the retracted values are quoted in the bug log
> so the size of the error stays on record.

## 1. H5, the reality anchor

Fits the two-state model `(k, tau, max_rate, phi0)` to each real curve by
bounded least-squares under static light.

Numbers are from the clock-corrected refit of 13 October: each plant is
fitted on elapsed time since its own stimulus onset (the unilateral blue
light started at each block's ZT; see `docs/DATA_CONTRACT.md`). The
widened-bound refit of 12 October used the same bounds but the wrong
clock and is superseded.

| Block | n | median RMSE (deg) | across-plant spread (deg) | RMSE / spread | pass |
|---|---|---|---|---|---|
| ZT0  | 7 | 1.97 | 5.17  | 0.38 | yes |
| ZT3  | 9 | 1.78 | 5.58  | 0.32 | yes |
| ZT6  | 8 | 2.01 | 8.58  | 0.23 | yes |
| ZT9  | 6 | 2.42 | 5.27  | 0.46 | yes |
| ZT12 | 9 | 1.41 | 11.47 | 0.12 | yes |
| ZT16 | 9 | 1.45 | 9.38  | 0.15 | yes |

Overall median RMSE 1.80 deg against median spread 8.58 deg, ratio 0.21.

**Reading.** The model is wrong by less than real plants differ from each
other, in all six blocks, by a factor of two to eight. That is the bar we
set, and it clears it everywhere. It earns the right to be studied, which
is all H5 was ever for.

**The caveat that matters.** Only 4 of 48 plants end with a parameter
pinned at a bound, and they sit at the opposite wall from the retracted
version: four of the six ZT9 plants pin `tau` at its *lower* bound
(0.05 h, three minutes). Their curves move within the first hour -- up to
10 deg in 60 minutes, the fastest onset of any block -- and the model
wants a shorter lag than it is allowed to express. ZT9-1 is also the
worst fit in the dataset (RMSE 6.76 deg); the ZT9 curves rise fast, stall,
and rise again, a shape a single lag can only approximate.

| Block | clean fits | median tau (h) |
|---|---|---|
| ZT0  | 7/7 | 4.11 |
| ZT3  | 9/9 | 3.63 |
| ZT6  | 8/8 | 2.87 |
| ZT9  | 2/6 | 0.05 (bound) |
| ZT12 | 9/9 | 4.60 |
| ZT16 | 9/9 | 5.52 |

Time of day has not vanished from the results; it has moved to where the
paper itself puts it. The dials differ by block -- median `k` is 17 to 25
for ZT0-ZT6 and about 5 for ZT9 and ZT12 -- which is the model's way of
registering the gated, time-of-day-dependent phototropism Brooks et al.
report. Gating in the parameters is biology the model can express. What
it could not express, it turns out, was our own timestamp error.

Consequence for everything downstream: the 44 clean fits define the
plausible region, spanning all six stimulus start times. The four ZT9
lower-bound fits are excluded, not because their data is bad but because
a lag pinned at the wall is an optimizer artifact, not a measurement.

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

## 5. Weighted population, rerun 13 October

The same sweep as section 3, but plants are drawn where real sunflowers were
actually measured rather than uniformly over the box. Source: the 44 clean
fits from section 1, bootstrap-resampled with declared 15 per cent lognormal
jitter, seed 2, 10,000 plants, `sweep_weighted.py`. (The 12 October version
drew from 28 morning-only fits; that restriction was a consequence of the
clock bug and is gone.)

Source region, from the clean fits alone: k 3.78 to 46.83, tau 0.45 to
42.01, max_rate 6.21 to 179.75, phi0 23.93 to 81.56. No global clip is
applied, so the plausible region is defined by the measurements and
nothing else.

| Parameter | within-cluster IQR | weighted range | retains | uniform run |
|---|---|---|---|---|
| k        | 6.999  | 75.218  | 9%  | 25% |
| tau      | 2.528  | 69.031  | 4%  | 36% |
| max_rate | 37.456 | 275.804 | 14% | 50% |
| phi0     | 12.260 | 103.057 | 12% | 25% |

**Reading.** Degeneracy survives in the plausible region but is weaker.
Every parameter is better determined by behaviour when plants are drawn
from where real plants live: retention falls on all four against the
uniform run, tau from 36 to 4 per cent and max_rate from 50 to 14. The
honest statement is no longer "behaviour tells you almost nothing", it is
"behaviour tells you a good deal less than you would like, and how much
depends on where in parameter space you are".

**The cap comes alive.** Under the uniform box the speed limit bound the
trajectory for 1 plant in 2,000. In the weighted population it binds for
8.28 per cent of plants. The cap is not intrinsically inert; it was inert
because the uniform box spends most of its volume on caps far above any
rate those plants would ever reach. This is the strongest argument yet
for weighted sampling: it changes which parameters matter, not just how
often they appear.

**Scope limit, stated because it limits every number above.** The
population now spans all six stimulus start times. Its only exclusion is
the four ZT9 plants pinned at the tau lower bound, so ZT9 is
under-represented (2 of its 6 plants). It is "the sunflowers our model
can represent", which after the clock correction is nearly all of them.

**Median final angle is 46.0 deg** against a measured plateau of roughly
50 to 60 deg, so the population is centred slightly low. `corr(
final_angle, phi0)` is 0.881, up from 0.64 under uniform sampling: where
real plants live, the final angle tracks the light angle closely, and
the degeneracy hides in the dynamics (k, tau, cap) rather than in where
the plant ends up.

## 6. Status against the hypotheses

| # | Status |
|---|---|
| H1 | supported under uniform sampling, weaker but present under weighted |
| H2 | not supported on the current metric; metric likely inadequate |
| H3 | not tested, needs a dense parameter sweep |
| H4 | not tested, needs the sweep regime and a cluster-agreement measure |
| H5 | passed 6/6 blocks; 4/48 fits bound-pinned, all ZT9 at the tau lower bound |

## 7. Declared next steps

1. ~~Widen the tau bound and refit~~ — **done 12 October**, section 1. The
   wall moved and we misread that as evidence; the wall was a clock
   offset. Retracted, see bug log.
2. ~~Fit a non-static light regime to ZT12 and ZT16~~ — **moot as of
   13 October.** Those plants never needed a moving light; they needed
   their own start time. The recovered population is already in every
   downstream number. What replaces this step: explain the ZT9 onset --
   four plants whose lag wants to be under three minutes, and whose
   rise-stall-rise shape is the worst fit in the dataset.
   **Done 13 October**: `docs/RESULTS_ROUND2_ZT9.md`. Freeing the tau
   floor buys 0.8% RMSE, so the bound is a symptom; the two-phase rate
   profile is a genuine model limitation.
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

**13 October: the fitter used the plant's absolute clock as elapsed time.
Found by Anadi Tripathi, who photographed the argument and brought it to the
project.**

The Fig1C time column is headed `ZT`: zeitgeber time, hours since the
growth-chamber lights came on. Brooks et al. started the unilateral blue
light at six different times of day, so each block's curves begin -- at
angle zero, by construction -- at its own ZT. `fit_real.py` integrated
the model with the lamp on from ZT 0 and scored only from each plant's
first timestamp. For a ZT16 plant that asks the model to stay straight
through 16 unobserved hours of illumination and then bend; the only
escape the optimizer has is to drive the lag `tau` to its upper bound
and keep it there. Consequences, stated plainly:

- all 48 fits except the ZT0 block (whose clock genuinely starts at 0)
  were distorted, `tau` inflated roughly in proportion to the block's ZT
- the reported H5 caveat -- "the static-light assumption fails by time
  of day", 20/48 fits pinned, all of them ZT12/ZT16, midday and
  afternoon plants excluded from the plausible region -- measured our
  timestamp error, not the plants. **Retracted in full.**
- our 12 October "falsification" of the missing-mechanism explanation
  was unsound: we argued a missing mechanism "would not care which
  block it was in", but a clock offset cares exactly that way, growing
  with ZT. The widened bound "moved the wall without emptying it"
  because the wall was the offset itself.
- every fit-dependent number was rerun: median RMSE 4.74 -> 1.80 deg,
  clean fits 28 -> 44 of 48 (ZT12 and ZT16 are 9/9 clean), the weighted
  sweep (section 5), the whole round-1 suite (`docs/RESULTS_ROUND1.md`)
  and the real-seedling predictions. One round-1 verdict flipped: H4
  (ARI 0.606 -> 0.442, clusters do not persist across light regimes).

What survived: the ZT0 fits are bit-identical (ZT0-1's degeneracy probes
in section 2 still read 1.894 against 1.894), everything that never
touches real data (the uniform sweep, H1, the simulator's physics
checks), and H5's headline direction -- the model still passes, now by
a factor of two to eight instead of scraping the bar in the afternoon.

Why the audit missed it: `audit_round1.py` check 3 recomputed the RMSEs
through `run_model` on the raw ZT timestamps, the same convention as the
fitter, so it verified the arithmetic of the wrong quantity. It now
evaluates on elapsed time and carries a regression guard (check 3d:
every plant's fitted start must equal its block's ZT, and the pinned
count is asserted). The data contract gained the handling rule that
would have prevented this (`docs/DATA_CONTRACT.md`, "stimulus onset").

The bug also left a genuine finding behind, the way the last one did:
fitted `tau` medians ran 4.11, 3.63, 2.87, bound, 4.60, 5.52 across
ZT0..ZT16 -- no monotone clock trend once the clock is right -- while
median `k` falls from 17-25 in the morning blocks to about 5 at
ZT9/ZT12. Time of day gates the gain, not the lag. That is a statement
about sunflowers, and it was invisible while the lag was busy absorbing
our error.

## Files

| File | Content |
|---|---|
| `results/fit_fig1c.csv` | 48 per-plant fits, params, RMSE, bound flags |
| `results/sweep_features.csv.gz` | 20,000 rows, static and flip features plus parameters |
| `results/sweep_clusters_static.csv` | static-regime cluster summary |
| `results/sweep_clusters_flip.csv` | flip-regime cluster summary |
| `results/sweep_weighted_features.csv.gz` | weighted-population features, static and flip |
| `results/sweep_weighted_clusters_static.csv` | weighted-population cluster summary |
