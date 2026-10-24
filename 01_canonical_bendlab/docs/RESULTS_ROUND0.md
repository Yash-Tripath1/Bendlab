# Results I: model fitting and parameter degeneracy

**Date:** 11 October 2026; corrected 13 October 2026  
**Sources:** `fit_real.py` and `sweep.py`  
**Measured data:** PLOS Biology (2023), S13 Data, sheet Fig1C; 48
sunflower plants in six stimulus-start-time groups

> **Correction, 13 October 2026.** Sections 1 and 5 were revised after
> identification of a time-base error in the fitting pipeline (Section 8).
> The initial version concluded that the static-light model was inadequate
> for midday and afternoon stimulus times and excluded those plants from
> subsequent analyses. **That conclusion is retracted.** Those plants were
> fitted using absolute zeitgeber time as elapsed stimulus time. Every
> result dependent on the affected fits has been recalculated; the
> retracted values are retained in Section 8 so that the magnitude of the
> error remains documented.

## 1. H5: adequacy of the model for measured sunflower trajectories

The two-state model, parameterised by (`k`, `tau`, `max_rate`, `phi0`),
was fitted independently to each measured trajectory by bounded
least squares under static light.

The values below are from the corrected analysis of 13 October 2026.
Each plant is fitted on elapsed time since its own stimulus onset; the
unilateral blue light began at the stimulus-start time (ZT) of its
treatment group (see `docs/DATA_CONTRACT.md`). The widened-bound refit of
12 October used the same parameter bounds but the incorrect time base and
is superseded.

| Group | n | Median RMSE (degrees) | Across-plant SD (degrees) | RMSE / SD | Criterion met |
|---|---:|---:|---:|---:|---|
| ZT0 | 7 | 1.97 | 5.17 | 0.38 | Yes |
| ZT3 | 9 | 1.78 | 5.58 | 0.32 | Yes |
| ZT6 | 8 | 2.01 | 8.58 | 0.23 | Yes |
| ZT9 | 6 | 2.42 | 5.27 | 0.46 | Yes |
| ZT12 | 9 | 1.41 | 11.47 | 0.12 | Yes |
| ZT16 | 9 | 1.45 | 9.38 | 0.15 | Yes |

The overall median RMSE is 1.80 degrees against a median across-plant
standard deviation of 8.58 degrees (ratio 0.21).

**Interpretation.** Model error is smaller than variation among measured
plants in all six groups, by a factor of approximately two to eight. The
model therefore satisfies the pre-specified adequacy criterion required
for its use in the subsequent identifiability analyses. This result does
not identify a physiological mechanism; it establishes only that the
model can reproduce the measured trajectories to within plant-to-plant
variation under the stated conditions.

**Boundary solutions.** Four of the 48 fits have a parameter at an
optimisation bound. All four are ZT9 plants for which `tau` reaches its
lower bound of 0.05 h (3 min). These plants respond within the first hour
— by as much as 10 degrees in 60 min, the fastest onset in the dataset —
and their fitted lag is shorter than the model is permitted to express.
ZT9-1 is also the largest individual fit error (RMSE 6.76 degrees). The
ZT9 trajectories rise rapidly, slow, and rise again; that two-phase rate
profile cannot be represented exactly by a single first-order lag.

| Group | Clean fits | Median fitted `tau` (h) |
|---|---:|---:|
| ZT0 | 7/7 | 4.11 |
| ZT3 | 9/9 | 3.63 |
| ZT6 | 8/8 | 2.87 |
| ZT9 | 2/6 | 0.05 (lower bound) |
| ZT12 | 9/9 | 4.60 |
| ZT16 | 9/9 | 5.52 |

Time dependence has not disappeared from the results; it is expressed
through the fitted parameters rather than through a failure to fit. Median
`k` is approximately 17–25 in ZT0–ZT6 and approximately 5 in ZT9 and
ZT12, consistent with the time-of-day dependence of phototropic
responsiveness reported by Brooks et al. The present model can represent
that dependence only indirectly, through group-specific fitted parameter
values.

The 44 fits without boundary solutions define the empirically supported
parameter region used in subsequent weighted-population analyses. The
four ZT9 boundary fits are excluded because a parameter held at its bound
is an optimiser boundary solution rather than an estimated value. Their
exclusion is not based on the quality of the measured data.

The adequacy criterion is conservative in favour of the model because
genuine plant-to-plant variation contributes to the across-plant standard
deviation used as the comparator. Satisfying the criterion should
therefore be regarded as a minimum requirement, not as strong evidence of
mechanistic correctness.

## 2. Parameter degeneracy in measured trajectories

### 2.1 Approximate degeneracy along the lag direction

Plant ZT0-1 was refitted with `tau` fixed on a grid:

| Fixed `tau` (h) | `k` | `max_rate` | `phi0` | RMSE (degrees) |
|---:|---:|---:|---:|---:|
| 0.25 | 9.76 | 22.94 | 52.24 | 7.085 |
| 0.50 | 10.09 | 121.99 | 51.73 | 6.779 |
| 1.00 | 10.82 | 155.36 | 50.65 | 6.142 |
| 2.00 | 12.53 | 22.57 | 48.55 | 4.897 |
| 4.00 | 16.72 | 30.00 | 44.89 | 2.857 |

RMSE decreases from 7.09 to 2.86 degrees as `tau` increases from 0.25 to
4.0 h, while the fitted values of `k` and `phi0` change systematically.
The lag therefore carries information in this trajectory, but neither `k`
nor `phi0` can be estimated independently of it. The degeneracy takes the
form of a correlated ridge in parameter space rather than a completely
flat likelihood surface.

### 2.2 Exact degeneracy of the maximum bend rate

Refitting ZT0-1 after removing the maximum-rate limit gives RMSE 1.894
degrees, identical to the fit obtained with the limit included. The
realised bend rate never reaches the fitted limit. Consequently, any
limit above the maximum realised rate produces the same trajectory, and
`max_rate` is exactly unidentifiable from this curve.

## 3. H1: whether behaviour determines parameters

A population of 10,000 simulated plants was sampled uniformly, simulated
for 24 h under static light, and clustered into six groups using six
behavioural features (seed 1).

The values below are from the corrected run of 12 October 2026; the first
version of this table used a corrupted feature column and is superseded
(see the error log in Section 8).

| Parameter | Median within-cluster IQR | Full sampled range | Range retained |
|---|---:|---:|---:|
| `k` | 0.747 | 2.950 | 25% |
| `tau` | 2.048 | 5.749 | 36% |
| `max_rate` | 19.058 | 37.993 | 50% |
| `phi0` | 20.264 | 79.991 | 25% |

A behavioural cluster retains one-quarter to one-half of the full
parameter range. The largest cluster, containing 2,859 simulated plants,
spans essentially the full sampled ranges of `k` (2.947 of 2.950),
`phi0` (79.96 of 79.99 degrees) and `max_rate`, despite the behavioural
similarity of its members.

**Interpretation.** H1 is supported. Knowledge of a plant's behavioural
cluster does not determine its parameter values. The corrected analysis
strengthens the initial conclusion: retained ranges are 25–50 per cent,
compared with 29–43 per cent in the superseded calculation.

**Composition of the clusters.** The clusters primarily separate response
magnitude rather than parameter combinations. Median observed peak bend
rate increases from 0.22 to 2.13 degrees h⁻¹ across clusters and median
final angle from 4.5 to 41.3 degrees. Correlations with light angle are
moderate: $r = 0.64$ for final angle against `phi0` and $r = 0.604$
for area under the response curve against `phi0`.

**Inactivity of the maximum-rate limit under static light.** The observed
peak bend rate contains almost no information about `max_rate`
($r = 0.01$). In a separate sample of 2,000 plants, the rate limit
constrained the trajectory of only one plant. The median observed peak
rate is 0.76 degrees h⁻¹, compared with a median rate limit of 21.2
degrees h⁻¹. This is the population-level counterpart of the exact
degeneracy in ZT0-1: a limit that is never reached produces no observable
signature in the trajectory.

## 4. H2: information provided by a change in light direction

The same 10,000 simulated plants were simulated with a 45-degree step in
light direction at $t = 8$ h. The trajectory was integrated continuously
so that the bend-rate state was carried across the step. The mean angle
change during the two hours after the step was 19.92 degrees, confirming
that the regime change had a substantial behavioural effect.

Within-cluster parameter spread after the step was mixed relative to
static light: `k` narrowed (median IQR 0.523 versus 0.747), whereas `tau`
(2.334 versus 2.048) and `phi0` (25.355 versus 20.264) widened. `max_rate`
was unchanged because the limit remained largely inactive in both regimes.

**Conclusion:** H2 is not supported under the cluster-retention metric.

This is a limited test. Classification into six clusters discards much of
the information generated by the step change, and the narrowing observed
for `k` suggests that a continuous identifiability measure may be more
sensitive. Development of such a measure is a prerequisite for a stronger
test of H2 and is recorded as a subsequent step rather than treated as a
conclusion here.

## 5. Empirically weighted population

The H1 simulation was repeated using parameter vectors sampled from the
region supported by the measured sunflower fits rather than uniformly
over the parameter box. The source population comprised the 44 clean fits
of Section 1, bootstrap-resampled with a pre-specified 15 per cent
lognormal multiplicative jitter (seed 2; `sweep_weighted.py`; 10,000
plants). The 12 October version used 28 morning-only fits; that
restriction resulted from the time-base error and no longer applies.

Parameter ranges in the clean fits were `k` 3.78–46.83, `tau`
0.45–42.01 h, `max_rate` 6.21–179.75 degrees h⁻¹ and `phi0`
23.93–81.56 degrees. No additional global clipping was applied, so the
weighted population is determined by the fitted measurements.

| Parameter | Within-cluster IQR | Weighted sampled range | Retained | Uniform population |
|---|---:|---:|---:|---:|
| `k` | 6.999 | 75.218 | 9% | 25% |
| `tau` | 2.528 | 69.031 | 4% | 36% |
| `max_rate` | 37.456 | 275.804 | 14% | 50% |
| `phi0` | 12.260 | 103.057 | 12% | 25% |

**Interpretation.** Degeneracy remains present in the empirically
supported region but is substantially weaker than under uniform sampling.
Behaviour retains less of every parameter range, most markedly for `tau`
(36 to 4 per cent) and `max_rate` (50 to 14 per cent). The appropriate
conclusion is therefore not that behaviour is uninformative, but that the
degree of identifiability depends strongly on the region of parameter
space under consideration.

**Activity of the maximum-rate limit.** The rate limit constrained one
plant in 2,000 under uniform sampling, but 8.28 per cent of plants in
the weighted population. The limit is therefore not intrinsically inactive;
its apparent inactivity under uniform sampling reflects the large volume
of the parameter box in which the specified limit lies far above any rate
the model realises. Weighted sampling changes which parameters are
practically identifiable, not merely the frequency with which parameter
values occur.

**Population scope.** The weighted population spans all six
stimulus-start times. Its only exclusions are the four ZT9 fits at the
`tau` lower bound, so ZT9 is represented by two of its six plants. The
population should accordingly be described as the measured sunflowers
representable by the present model, rather than as the full measured
sample.

The median final angle in the weighted population is 46.0 degrees,
compared with measured plateau values of approximately 50–60 degrees.
The correlation between final angle and `phi0` is 0.881, compared with
0.64 under uniform sampling. In the empirically supported region, final
angle therefore follows light angle closely, and residual parameter
degeneracy is concentrated in the approach dynamics (`k`, `tau` and
`max_rate`) rather than in the final orientation.

## 6. Status of hypotheses after this stage

| Hypothesis | Status |
|---|---|
| H1 | Supported under uniform sampling; weaker but present under weighted sampling |
| H2 | Not supported under the current metric; the metric is likely insufficiently sensitive |
| H3 | Not yet tested; requires a dense parameter sweep |
| H4 | Not yet tested; requires a moving-light regime and a cluster-agreement measure |
| H5 | Supported in all six stimulus-start-time groups; 4/48 fits bound-pinned, all ZT9 at the `tau` lower bound |

## 7. Subsequent steps identified at this stage

1. ~~Increase the `tau` upper bound and refit~~ — completed 12 October
   (Section 1). The apparent persistence of boundary solutions was later
   shown to result from the time-base error. This interpretation is
   retracted; see Section 8.
2. ~~Fit a non-static light regime to ZT12 and ZT16~~ — superseded on
   13 October. Those groups did not require a moving-light model; they
   required elapsed time from their respective stimulus onsets. The
   remaining question is the ZT9 onset pattern: four plants with fitted
   lags at the three-minute lower bound and a rise–stall–rise trajectory
   shape. **Addressed 13 October** in `docs/RESULTS_ROUND2_ZT9.md`:
   reducing the `tau` lower bound improves RMSE by only 0.8 per cent,
   indicating that the boundary solution is a symptom of the model's
   inability to reproduce the two-phase rate profile.
3. Replace the cluster-retention metric for H2 with a continuous
   identifiability metric.
4. Evaluate H3 using a dense two-dimensional sweep over (`k`, `tau`).
5. ~~Construct the empirically weighted population~~ — completed
   12 October; corrected 13 October (Section 5).
6. Evaluate H6 by recombining parameter vectors from behaviourally
   equivalent plants, applying mutation, and measuring retention of the
   source behavioural class.
7. Evaluate H7 by ranking light protocols according to a continuous
   identifiability criterion; this depends on completion of step 3.
8. Draw hidden plants for the adaptive identification experiment from the
   weighted population rather than the uniform parameter box, so that its
   difficulty reflects the empirically supported region.

## 8. Error log

### 8.1 Feature/parameter column collision (12 October 2026)

**Identification:** identified by Umaid during code review.

The behavioural feature representing observed peak bend rate was named
`max_rate`, the same name as the parameter specifying the maximum
permitted bend rate. In the feature table, the observed-rate column was
therefore overwritten by the true parameter value. Consequences were:

- clustering used five behavioural features and one true parameter; the
  analysis therefore partly clustered plants using a quantity it was
  intended to predict;
- the initially reported range retention for `max_rate` (25 per cent) was
  calculated from the corrupted column and is not interpretable;
- all values in Sections 3 and 4 of the first version are superseded by
  the corrected run of 12 October.

H5 was unaffected because `fit_real.py` does not use the feature table.
The direction of the H1 conclusion was also unaffected and is strengthened
by the corrected values (retention 25–50 per cent, compared with the
corrupted 25–43 per cent). The correction renamed the observed feature to
`peak_rate`, prefixed parameter columns with `param_`, and added an import-
time check in `sweep.py` that fails if a feature name and a parameter name
coincide.

The error also identified a genuine property of the model: under static
light and over the uniform parameter box, the maximum-rate limit is almost
never active (Section 3). This explains why the corrupted and corrected
analyses reached the same qualitative conclusion for H1.

### 8.2 Use of absolute zeitgeber time as elapsed stimulus time (13 October 2026)

**Identification:** identified by Anadi during review of the time-base
assumptions.

The Fig1C time column is headed ZT (zeitgeber time: hours since the
growth-chamber photoperiod began). Brooks et al. began unilateral blue-light
stimulation at six different times of day, and each group's trajectories
begin, at zero angle by construction, at its own ZT. `fit_real.py`
originally integrated the model with the light on from ZT 0 and evaluated
the fit only from each plant's first timestamp. For a ZT16 plant, this
required the model to remain unbent through 16 unobserved hours of
illumination before reproducing the observed response. The only available
compensation was to increase `tau` to its upper bound. Consequences were:

- all fits except those in ZT0 (for which elapsed and absolute time
  coincide) were distorted, with `tau` inflated approximately in
  proportion to group ZT;
- the original H5 qualification — that the static-light assumption failed
  by time of day, with 20/48 fits bound-pinned in ZT12/ZT16 and midday and
  afternoon plants excluded from the supported region — measured the
  timestamp error rather than a property of the plants and is **retracted
  in full**;
- the 12 October argument against a missing-mechanism explanation was
  unsound. That argument held that a missing mechanism would not depend
  systematically on treatment group, whereas the time-base error does
  increase with ZT. The observation that widening the bound moved but did
  not remove the boundary solutions was a consequence of the offset;
- all fit-dependent results were recalculated. Median RMSE changed from
  4.74 to 1.80 degrees; clean fits increased from 28 to 44 of 48 (ZT12
  and ZT16 are each 9/9 clean); the weighted sweep (Section 5), the full
  experiment series in `docs/RESULTS_ROUND1.md`, and the predictions from
  measured-data parameter sets were rerun. One conclusion changed: H4
  (ARI 0.606 to 0.442; behavioural clusters do not persist across light
  regimes).

The ZT0 fits are unchanged, because absolute and elapsed time coincide for
that group; the ZT0-1 degeneracy analyses in Section 2 (1.894 versus
1.894 degrees) remain valid. Analyses that do not use measured data (the
uniform sweep, H1 and the simulator validation checks) were also
unaffected. H5 remains supported, now with a margin of two- to eightfold
rather than a marginal pass at later stimulus times.

**Reason the audit did not detect the error.** Check 3 of
`audit_round1.py` recomputed RMSEs using the same raw-ZT convention as
the fitting code. It therefore verified the arithmetic of an incorrectly
defined quantity. The audit now evaluates elapsed time and includes a
regression check (check 3d) requiring each plant's fitted start time to
equal the ZT of its treatment group, together with the expected number of
bound-pinned fits. The corresponding handling rule has been added to
`docs/DATA_CONTRACT.md`.

The correction also revealed a pattern not visible in the erroneous
analysis. Corrected median `tau` values are 4.11, 3.63, 2.87,
bound-pinned, 4.60 and 5.52 h across ZT0–ZT16, with no monotonic
relationship to stimulus-start time. By contrast, median `k` decreases
from approximately 17–25 in the morning groups to approximately 5 at ZT9
and ZT12. In this dataset, time of day is therefore associated primarily
with response gain rather than with response lag.

## Files

| File | Content |
|---|---|
| `results/fit_fig1c.csv` | Parameter fits, RMSE and boundary-solution indicators for 48 plants |
| `results/sweep_features.csv.gz` | Behavioural features and parameters for 20,000 simulations under static and step-change regimes |
| `results/sweep_clusters_static.csv` | Cluster summary under the static regime |
| `results/sweep_clusters_flip.csv` | Cluster summary under the step-change regime |
| `results/sweep_weighted_features.csv.gz` | Behavioural features for the weighted population under static and step-change regimes |
| `results/sweep_weighted_clusters_static.csv` | Cluster summary for the weighted population |
