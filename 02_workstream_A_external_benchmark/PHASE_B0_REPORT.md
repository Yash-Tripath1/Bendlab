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
**The model has no light-intensity input and no equilibrium mechanism:**
with a fixed light angle phi its only steady state is theta = phi.
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
≈ 7.5 min. The raw Zenodo archive (11.7 MB, md5
`06d911cc56c6cf92d66af15304bb93f9`, matching the record) is kept
locally under `phase_b0/zenodo/` and is **not** added to any repository.

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
| Angles | theta in degrees in trajectories (−18.7 to +76.1); steady-state summaries (`uni_stst_angles.csv`, mean over 16–21 h) are in **radians** (archive code converts with `deg2rad`); theta quantised to 0.1° |
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
archive's steady-state table, so the cleaned file is internally
consistent with the published summaries.

## 2. How intensity enters (it doesn't — wrapper declared)

The published model contains no intensity variable: `k` is a per-plant
gain. Rather than silently inventing a mapping inside the model, the
benchmark uses a separate wrapper, fitted on training plants only:

- **W1 (the benchmark proper):** canonical model, phi = 90° shared and
  fixed, `k(I) = a·I^b` (power-law gain, the same functional family as
  the paper's transduction ν(I) ∝ I^α), tau and max_rate shared,
  theta(0) = each plant's observed initial angle. All-data fit:
  a = 1.44, b = 0.38, tau pinned at its 0.05 h lower bound,
  max_rate = 20°/h (boundary behaviour that itself signals strain).
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
| B2 saturating exponential | 10.92 | +1.5 |
| B0 persistence | 25.96 | −27.4 |

Plant-level bootstrap (2,000 resamples): W1 is worse than the trivial
group-mean baseline by +4.22° median RMSE (95% CI 3.52–4.74); W2 is
statistically indistinguishable from B1 (−0.18°, CI −0.47–0.13). W1's
error grows with intensity (median RMSE 10.3° at 0.7 W/m² → 16.4° at
5.8) and with time (2.9° in 0–2 h, comparable to persistence; 14.9° in
6–12 h), with a systematic positive late bias: the model keeps driving
theta toward 90° while measured plants plateau at 18–37°. The measured
group means are also visibly non-monotone (rise, overshoot around
8–10 h, settle), a shape no fixed-phi first-order model can produce.
See `fig1_mean_trajectories.png`, `fig2_heldout_by_intensity.png`.

Leave-one-intensity-group-out (held group untouched in fitting and
model selection): W1 median RMSE ranges 10.4–16.5° and is the worst
arm in every interior group. Endpoints, reported separately as
extrapolation: at 0.7 W/m² W1 = 10.4° vs B2 = 9.6°; at 5.8 W/m²
W1 = 16.5° vs B1 = 10.5° (endpoint-clamped) and B2 = 12.2°. The
intensity law fitted without the endpoint does not rescue the top
group, because in this model intensity changes speed, not the
steady-state angle, and the data's steady state is what varies with
intensity. `fig3_loio_by_intensity.png`.

Per-plant calibration is a different question and is far worse: fitting
(k, tau) per plant on 0–4 h only (phi=90, non-binding cap) and
forecasting 4–22 h gives median forecast RMSE **51.1°** and median
final error **+55.7°** (early-window fits choose large k with
tau ≈ 10 h, then run away toward 90°). Population prediction on the
same late window (12–22 h RMSE 11.7°) is poor but not catastrophic.
Conflating these two modes would badly misstate the model either way.
`fig4_calibration_and_phi.png` (left).

Diagnostic locating the failure: per-plant full-curve fits with phi
free reach median RMSE 4.09° versus 11.58° with phi fixed at 90°. The
fitted phi_free is median 28.8° (IQR 20.8–37.7°) and **rises with
intensity** (22.5° at 0.7 W/m² → 40.7° at 5.8), tracking the paper's own
steady-state angles (0.32–0.60 rad ≈ 18–35°). In other words, whenever
this scalar model fits these data, "phi0" is functioning as an
empirical equilibrium angle that absorbs the balance between the light
drive and the counteracting gravitropic/proprioceptive terms that the
Kempinski ORGAN model carries explicitly (its β and γ terms) and
BendLab omits — not as the known 90° lamp direction.

## 4. Recommendation on scalar-model transfer

1. **Do not transfer the current scalar model, as published, to
   intensity-varying phototropism prediction.** With the true light
   geometry imposed (phi = 90°) it is beaten by a group-mean baseline
   on external data, at every intensity and in extrapolation, with a
   systematic late overshoot. This is a structural limitation (no
   equilibrium mechanism), not a calibration problem: no intensity law
   on k can fix an asymptote.
2. **The model remains usable in its original narrow role** — within a
   single fixed protocol (the Brooks assay), with phi0 fitted per
   plant/block and interpreted strictly as a nuisance/effective angle.
   Note this benchmark neither confirms nor refutes that use: different
   assay, different angle definition (millimetre-scale tip tangent vs
   base-to-apex chord).
3. **Any future intensity-capable revision needs an explicit
   counteracting term** (gravitropic/proprioceptive, e.g. a −γ·theta
   equilibrium term of the kind the project has already probed as a
   proxy) so that steady-state angle, not just speed, can depend on
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
