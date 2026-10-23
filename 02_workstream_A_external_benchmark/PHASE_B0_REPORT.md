# Phase B0 report — Workstream A: Kempinski external benchmark of the scalar model

**Companion deliverable:** `SHAPE_EXTENSION_AUDIT.md` (Workstream B).
The two workstreams are independent: this report uses only real
tip-angle data and the canonical scalar model; the shape audit uses only
the shape-extension branch's simulated populations. Neither is evidence for the other.

**Canonical BendLab state (verified 2026-10-18).** Upstream `main` is
unchanged at `b09ea5aa6003082b41d726b2b8499ded313dcb21`. Model
interface: `sim.py`, `simulate(k, tau, max_rate, phi_fn, t_end, dt)` /
`batch_simulate(...)`, implementing
`tau dr/dt = k sin(phi - theta) - r`, cap applied after the lag update,
theta in degrees from vertical, 1-minute reference step
(`PROBLEM_STATEMENT.md` §2, guarded by `check_model_contract.py`).
**The model has no light-intensity input and no counteracting term:**
under a fixed light angle phi its long-run equilibrium is theta = phi,
so it has no intensity-dependent equilibrium.
Changing the gain k cannot change that asymptote (it can change
finite-time trajectories). What is benchmarked below as W1 is therefore
not the published model unchanged: it is the published model plus a
separate wrapper intensity law (Section 2).
Measured-data interface: Brooks et al. (2023) S13 tip angles only.
This benchmark therefore evaluates *trajectory prediction* on external
tip-angle data. It does not evaluate recovery of physiological
parameters (the archive has no ground-truth parameters), and it cannot
test local curvature kappa(s,t), whole-stem shape, autostraightening,
or zeitgeber-time gating, because the archive contains tip angles only.

**Reproducibility.** `workstream_a/phase_b0_kempinski_benchmark.py`
(standalone; imports the canonical model read-only; nothing in the
published simulator, app or site was changed), outputs in
`workstream_a/outputs/`, plots by `workstream_a/make_plots.py`, tests
in `tests_phase_b0.py` (all passing: split disjointness/stratification,
one-intensity-per-plant, corrected shape-feature semantics). Runtime
≈ 7.5 min. Data tracking, stated precisely: the full Zenodo archive
(11.7 MB, md5 `06d911cc56c6cf92d66af15304bb93f9`, matching the record)
is NOT tracked in the repository. The single extracted file used by the
benchmark, `uni_trajectories.csv` (2.1 MB), IS tracked under
`05_data_external/`, deliberately, so the benchmark reproduces from a
clean checkout. Scripts resolve all paths relative to the checkout and
accept `--data` for any other copy of the file.

## 1. Data audit: `uni_trajectories.csv`

Verified against the archive README, the PNAS paper (local PDF) and the
archive's own analysis code (`01_Preprocessing/02_Uni_cleanup.py`,
`02_Analysis/02_Unilateral_light.ipynb`):

| Item | Finding |
|---|---|
| Rows / plants | 88,504 rows; 268 distinct `real_id`; 323–331 rows per plant |
| Schema | `dt` [h], `theta` [deg], `light_i` [W/m²], `real_id` — nothing else |
| Missing / duplicates | none; no duplicated (plant, time) pairs |
| Intensity groups | 10: 0.7, 1.1, 1.4, 1.9, 2.25, 3.0, 3.2, 3.85, 4.4, 5.8 W/m²; 15–33 plants each; **every plant belongs to exactly one group** |
| Sampling | 0–22 h (a few plants end at 21.47 h); intervals alternate 0.06/0.07 h (≈4 min, i.e. 1/15 h rounded to 2 dp) |
| Angles | theta in degrees in trajectories (−18.7 to +76.1); late-window summaries (`uni_stst_angles.csv`, mean over 16–21 h; called steady-state by the source, an operational late-window plateau here since no equilibrium is demonstrated) are in **radians** (archive code converts with `deg2rad`); theta quantised to 0.1° |
| Initial angles | **not zero**: mean ≈ 0°, range −15° to +15° (per-plant initial posture / circumnutation phase) |
| Plant IDs | encode side (`L`/`R`: 130/138 plants) and two numeric fields whose meaning (experiment day/batch) is not documented in the archive README; no other metadata |

**Angle definition and mapping (documented, decisive for fairness).**
Per the paper's Methods, theta is the angle between the stem tangent
near the tip — from two fluorescent markers painted at the tip and a
few millimetres below, tracked with a CSRT tracker — and the vertical.
It is a *local tip-segment angle over millimetres*, not a whole-stem
centerline and not the base-to-apex chord angle of the Brooks dataset.
In the archive, theta is positive toward the light for both `L` and `R`
plants (both sides bend to positive theta), so the archived sign
convention is "toward the source". BendLab's theta has exactly this
meaning (deviation from vertical toward phi), so the mapping is
theta_BendLab = theta_archive, in degrees, with no re-signing. The lamp
is a horizontal side panel, so the known shared light angle is
**phi = 90°** for every plant.

**Discrepancy flagged (as requested).** The paper states unilateral
intensities spanning 0.7–7 W/m², and the archive's plotting code uses a
colour scale extending to 7.5 W/m² with a preprocessing cutoff that
"removes high-intensity (light-saturation) points" above 7 W/m² — yet
the archived `light_i` values top out at **5.8 W/m²** and no group above
that exists in `uni_trajectories.csv` or `uni_stst_angles.csv`. Whether
a ≈7 W/m² group was measured and excluded, or never run, cannot be
determined from the archive. Consequence for this benchmark: claims
cover 0.7–5.8 W/m² only; the top archived group (5.8) must be treated
as the high endpoint. This should be put to the Kempinski authors
before any reuse beyond benchmarking.

**Provenance limits.** The archive contains cleaned trajectories only:
no raw marker coordinates, no images, no fluence time series beyond
calibration supplements. Batch structure hidden in `real_id` could not
be modelled; recomputing group means from the raw CSV reproduces the
archive's late-window summary table, so the cleaned file is internally
consistent with the published summaries.

## 2. How intensity enters (it doesn't — wrapper declared)

The published model contains no intensity variable: `k` is a per-plant
gain. Rather than silently inventing a mapping inside the model, the
benchmark uses a separate wrapper, fitted on training plants only:

- **W1 (the benchmark proper):** the canonical model augmented by the
  wrapper `k(I) = a·I^b` (power-law gain, the same functional family as
  the paper's transduction ν(I) ∝ I^α), phi = 90° shared and fixed,
  tau and max_rate shared, theta(0) = each plant's observed initial
  angle. This wrapper is an addition for this benchmark, not part of
  the published model. All-data fit (on every 4th observation, about
  16-minute spacing, from data sampled about every 4 minutes):
  a = 1.44, b = 0.38. tau sits at its 0.05 h lower bound: treat this
  as unresolved model-fit behaviour at the bound, not a biological lag
  estimate (all-observation sensitivity: see the end of Section 3).
  max_rate comes out at exactly 20°/h, its initial value, inside its
  [0.5, 60] bounds: the fitted k(I) peaks at ≈2.8°/h, so the cap never
  binds and max_rate is inactive/unidentified in this fit. It is NOT
  a boundary solution and no meaning should be read into the value.
- **W2 (structural diagnostic, NOT a candidate model):** as W1 plus an
  effective angle phi_eff(I) = clip(c0 + c1·ln I), also fitted on
  training data only. W2 exists to localise the structural problem.
- **Baselines:** B0 persistence (theta frozen at theta(0)); B1
  nonparametric group-mean curve of the training plants at the same
  intensity (for LOIO, interpolated in log I, clamped at endpoints);
  B2 a simple saturating exponential theta_inf(I) = a·I^b with one
  shared time constant.

## 3. Held-out results

Plant-held-out evaluation: 5 folds, plants assigned within intensity
strata, every time point of a plant in one split (tests verify this).
Median per-plant trajectory RMSE (degrees; 268 plants):

| Model | median RMSE | final-angle error (median) |
|---|---:|---:|
| **W1 BendLab wrapper, phi=90** | **14.41** | **+13.4 (overshoot)** |
| W2 diagnostic, phi_eff(I) | 9.97 | −0.6 |
| B1 group-mean curve | 9.73 | −0.1 |
| B1r group-mean, recentered to each plant's theta(0) | 10.03 | −0.3 |
| B2 saturating exponential | 10.92 | +1.5 |
| B0 persistence | 25.96 | −27.4 |

Uncertainty: an unstratified plant-level bootstrap (2,000 resamples;
batch structure in the archive is undocumented, so no batch-aware
resampling is possible) puts W1 worse than the group-mean baseline by
+4.22° median RMSE (95% CI 3.52–4.74). A stratified-by-intensity plant
bootstrap gives essentially the same interval (3.64–4.72), so the
conclusion does not depend on ignoring the strata. W2 is statistically
indistinguishable from B1 (−0.18°, CI −0.47–0.13). Recentering the
group-mean baseline to each test plant's own initial angle (B1r, 10.03°)
does not improve it; B1's advantage is trajectory shape, not offsets. W1's
error grows with intensity (median RMSE 10.3° at 0.7 W/m² → 16.4° at
5.8) and with time (2.9° in 0–2 h, comparable to persistence; 14.9° in
6–12 h), with a systematic positive late bias: the model keeps driving
theta toward 90° while measured plants settle into an operational
late-window plateau at 18–37°. The measured
group means are also visibly non-monotone (rise, overshoot around
8–10 h, settle), a shape this model cannot produce under the known phi = 90° geometry (narrowed precisely below).
See `fig1_mean_trajectories.png`, `fig2_heldout_by_intensity.png`.

Leave-one-intensity-group-out (held group untouched in fitting and
model selection): W1 median RMSE ranges 10.4–16.5° and is the worst
arm in every interior group. Endpoints, reported separately as
extrapolation: at 0.7 W/m² W1 = 10.4° vs B2 = 9.6°; at 5.8 W/m²
W1 = 16.5° vs B1 = 10.5° (endpoint-clamped) and B2 = 12.2°. The
intensity law fitted without the endpoint does not rescue the top
group, because in this model intensity changes speed, not the
equilibrium angle, and the data's late-window plateau is what varies
with intensity. A fixed-phi lag model is not incapable of overshoot in
general (it can overshoot past a target); the limitation here is
specific: with phi = 90° it cannot rise, peak at 25–45°, and turn back
down while still far below 90°, which is the measured shape.
`fig3_loio_by_intensity.png`.

Per-plant calibration is a different question and is far worse: fitting
(k, tau) per plant on 0–4 h only (phi=90, non-binding cap) and
forecasting 4–22 h gives median forecast RMSE **51.1°** and median
final error **+55.7°** (early-window fits choose large k with
tau ≈ 10 h, then run away toward 90°). On the SAME 4–22 h window
(common-window comparison added in this revision), population-level
held-out prediction by W1 has median RMSE 15.1°: poor, but not the
calibration catastrophe. The two modes answer different questions and
must not be averaged or interchanged.
Conflating these two modes would badly misstate the model either way.
`fig4_calibration_and_phi.png` (left).

Diagnostic locating the failure: per-plant fits to each full-duration
trajectory (fits use every 4th observation, about 16-minute spacing,
at a 4-minute integration step; this is a downsampled full-trajectory
fit, not a fit to every observation) with phi free reach median RMSE
4.09° versus 11.58° with phi fixed at 90°. The
fitted phi_free is median 28.8° (IQR 20.8–37.7°) and **rises with
intensity** (22.5° at 0.7 W/m² → 40.7° at 5.8), tracking the paper's own
late-window plateau angles (0.32–0.60 rad ≈ 18–35°). In other words, whenever
this scalar model fits these data, "phi0" is functioning as an
empirical equilibrium angle that absorbs the balance between the light
drive and the counteracting gravitropic/proprioceptive terms that the
Kempinski ORGAN model carries explicitly (its β and γ terms) and
BendLab omits — not as the known 90° lamp direction.

Sensitivity to fit subsampling (added in this revision,
`workstream_a/sensitivity_all_observations.py`): refitting the all-data
wrappers on EVERY observation instead of every 4th changes nothing
materially. W1: a 1.435→1.434, b 0.379→0.379, tau still at its 0.05 h
lower bound, in-sample median RMSE 14.42° both ways. W2 parameters move
by <2%. The bound-pinned tau is therefore a property of the model/data
mismatch, not of the subsampling, and the subsampled headline fits
stand.

## 4. Recommendation on scalar-model transfer

1. **Do not transfer the current scalar model, as published, to
   intensity-varying phototropism prediction.** With the true light
   geometry imposed (phi = 90°) it is beaten by a group-mean baseline
   on external data, at every intensity and in extrapolation, with a
   systematic late overshoot. Precisely: the tested intensity-augmented
   wrapper (W1) underperforms on this external assay with known
   phi = 90°. That is a structural limitation (the model's long-run
   equilibrium is phi whatever k does), not a calibration problem.
   This result does not invalidate the model's earlier in-assay fits to
   the Brooks data, which used a different protocol and a different
   angle definition; it says the model does not transfer, unchanged in
   structure, across assays and intensity ranges.
2. **The model remains usable in its original narrow role** — within a
   single fixed protocol (the Brooks assay), with phi0 fitted per
   plant/block and interpreted strictly as a nuisance/effective angle.
   Note this benchmark neither confirms nor refutes that use: different
   assay, different angle definition (millimetre-scale tip tangent vs
   base-to-apex chord).
3. **Any future intensity-capable revision needs an explicit
   counteracting term** (gravitropic/proprioceptive, e.g. a −γ·theta
   equilibrium term of the kind the project has already probed as a
   proxy) so that the equilibrium angle, not just speed, can depend on
   intensity. Designing that revision is outside Phase B0; it must be
   validated by held-out prediction, and it would still say nothing
   about curvature, ZT gating or autostraightening on tip-angle data.
4. **Before any further external use of this archive:** ask the
   Kempinski authors about the missing >5.8 W/m² group(s) and the
   `real_id` batch encoding.

## 5. Limitations of this benchmark

Tip angles only (millimetre-scale tip tangent); no curvature, shape,
ZT or autostraightening inference is possible, and none is made.
Cleaned data only — tracker errors and batch effects could not be
audited. Observed trajectories carry large high-frequency circumnutation
(paper-reported growth-direction SE ≈ 12°), which no smooth model here
attempts to represent and which inflates all arms' RMSE roughly
equally. Per-plant fits used a 4-minute integration step (checked
against the 1-minute contract step: ≤0.33° trajectory difference,
negligible beside 4–16° RMSEs). Group-mean baseline B1 uses each test
plant's own intensity label, as do all arms.
