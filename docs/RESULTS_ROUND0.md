# Results, round 0 — 11 October 2026

Everything below is from `fit_real.py` and `sweep.py`, both seeded, both
rerunnable. Real data is PLOS Biology 2023 S13, sheet Fig1C, 48 plants across
six light treatments.

## 1. H5, the reality anchor

Fits the two-state model `(k, tau, max_rate, phi0)` to each real curve by
bounded least-squares under static light.

| Block | n | median RMSE (deg) | across-plant spread (deg) | RMSE / spread | pass |
|---|---|---|---|---|---|
| ZT0  | 7 | 1.97 | 5.17  | 0.38 | yes |
| ZT3  | 9 | 4.06 | 5.58  | 0.73 | yes |
| ZT6  | 8 | 6.24 | 8.58  | 0.73 | yes |
| ZT9  | 6 | 4.00 | 5.27  | 0.76 | yes |
| ZT12 | 9 | 5.17 | 11.47 | 0.45 | yes |
| ZT16 | 9 | 7.55 | 9.38  | 0.80 | yes |

Overall median RMSE 5.07 deg against median spread 8.58 deg, ratio 0.59.
Per-plant RMSE runs 1.76 to 10.22 deg.

**Reading.** The model is wrong by less than real plants differ from each
other. That is the bar we set, and it clears it in all six blocks. It earns
the right to be studied, which is all H5 was ever for.

**The caveat that matters.** 22 of 48 plants end with a parameter pinned at a
bound: 20 with `tau` at its upper bound of 12 h, 11 with `phi0` at 130 deg.
Those fits are not converged, they are stopped at the wall, which means the
model wants something the parameter box does not contain. Two candidate
explanations and we cannot yet separate them:

- the static-light assumption is wrong for the ZT12 and ZT16 treatments, which
  is plausible since those blocks are the ones with the worst RMSE
- the two-state model is missing a mechanism, for instance a saturation that
  acts on the stimulus rather than on the rate

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

| Parameter | median within-cluster IQR | full range | retained |
|---|---|---|---|
| k        | 0.856 | 2.950 | 29% |
| tau      | 2.476 | 5.749 | 43% |
| max_rate | 9.392 | 37.993 | 25% |
| phi0     | 26.176 | 79.991 | 33% |

A behaviour cluster keeps roughly a quarter to a half of the full parameter
range. The largest cluster, 2,197 plants, spans k over 2.947 of a possible
2.950 and phi0 over 79.96 of 79.99, essentially the entire box, while its
members are behaviourally near-identical.

**Reading.** H1 holds in the strong form. Knowing what a plant does does not
tell you what it is. This is the result the project is about, and it appeared
in the first sweep.

**What the clusters actually are.** They are speed classes, not parameter
classes. Median half-rise time runs 11.0 to 13.5 h across clusters and median
max rate 11.0 to 31.4 deg/h, so the split is fast-benders against
slow-benders. Correlation with the light angle is weak: `corr(final_angle,
phi0) = 0.64`, `corr(auroc, phi0) = 0.604`. The behavioural fingerprint is
mostly telling us how fast the plant moves, and only partly where it ends up.

## 4. H2, does the flip add information? First probe only

Same 10,000 plants, light steps 45 deg at t = 8 h, integrated as one
continuous run so the rate state carries across the flip. Mean angle drop in
the two hours after the flip is 19.92 deg, so the regime bites.

Within-cluster parameter spread under the flip is not visibly tighter than
under static light: k retains about the same, tau slightly worse. On this
metric, **H2 is not supported yet.**

That is a weak test and it may be the wrong one. Clustering into six groups
throws away most of the information a flip creates. A better probe compares
continuous quantities, for instance whether the flip response separates
plants that static features map to the same point. Logged as the next step,
not as a conclusion.

## 5. Status against the hypotheses

| # | Status |
|---|---|
| H1 | supported, strongly, on the first sweep |
| H2 | not supported on the current metric; metric likely inadequate |
| H3 | not tested, needs a dense parameter sweep |
| H4 | not tested, needs the sweep regime and a cluster-agreement measure |
| H5 | passed 6/6 blocks, with 22 of 48 fits bound-pinned, so provisional |

## 6. Declared next steps

1. Widen the tau bound and refit, to separate "model needs more lag" from
   "static light is wrong for ZT12 and ZT16".
2. Fit a non-static light regime to those two blocks and compare RMSE. This is
   the cheapest way to tell the two explanations apart.
3. Replace the cluster-retention metric for H2 with a continuous one.
4. H3: dense 2-D sweep over (k, tau) at fixed cap, look for discontinuity.
5. Weighted population sampling, once the fit says where the plausible region
   is. Uniform first was deliberate: weighted sampling before the anchor
   exists would mean inventing the plausible region.

## Files

| File | Content |
|---|---|
| `results/fit_fig1c.csv` | 48 per-plant fits, params, RMSE, bound flags |
| `results/sweep_features.csv.gz` | 20,000 rows, static and flip features plus parameters |
| `results/sweep_clusters_static.csv` | static-regime cluster summary |
| `results/sweep_clusters_flip.csv` | flip-regime cluster summary |
