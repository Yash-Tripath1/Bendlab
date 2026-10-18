# Shape extension — results

**Date:** 18 October 2026
**Branch:** `shape-extension`
**Pre-registration:** `docs/SHAPE_EXTENSION.md` (written before any run)
**Runs:** `check_multiseg.py`, `shape_degeneracy.py`, then
`shape_degeneracy_v2.py`

---

## 1. Regression checks (`check_multiseg.py`)

All checks passed before any study was run.

| Check | Result |
|---|---|
| c = 0 reduces to `sim.simulate`, every segment, 4 parameter cases | max diff exactly 0.0 |
| uniform start invariant for c = 0.35 and c = 1.0 | max diff exactly 0.0 |
| batch vs single, coupling active | max diff 7.1e-15 |
| determinism (two runs) | bit-identical |
| cap contract (cap-binding case, max_rate = 3) | max step 0.0500 deg = max_rate * dt |

## 2. H-SHAPE v1: as specified

Population: 10,000 plants, the four-parameter margins of the H1 sweep
(`generate_plants.uniform_population`, seed 1) plus c ~ Uniform[0, 1]
(seed 2). Static light, 24 h, 0.5 h records, n_seg = 5. Clustering and
retention metric exactly as in `sweep.py`.

Retention (median within-cluster IQR / full range):

| Parameter | tip-only | tip+shape | delta (pp) |
|---|---:|---:|---:|
| k | 25.3% | 25.4% | -0.1 |
| tau | 35.6% | 35.5% | +0.1 |
| max_rate | 50.2% | 50.1% | 0.0 |
| phi0 | 25.3% | 25.5% | -0.2 |
| c | 51.0% | 51.3% | -0.3 |

**Verdict against the pre-registered criterion (>= 10 pp reduction for
>= 2 parameters): NOT SUPPORTED — falsified as specified. No parameter
shows a reduction of even 1 pp.**

Two independent confirmations that the tip arm is faithfully the H1
experiment: the retention numbers reproduce the published H1 values
(25, 36, 50, 25 per cent) and the largest tip-only cluster contains
2,859 plants, the published H1 largest-cluster size.

Files: `results/shape_degeneracy_features.csv.gz`,
`results/shape_clusters_tip.csv`, `results/shape_clusters_full.csv`,
`results/shape_retention_summary.csv`,
`results/shape_degeneracy_summary.json`,
`results/figures/shape_retention.png`.

## 3. Diagnosis: the shape channel is structurally empty in v1

The null result is not evidence that shape measurement is useless. It is
a property of the model class as specified, discovered by audit of the
saved feature table:

- Every shape feature column has standard deviation **exactly 0.0**
  across the 10,000 plants (`curv_final_abs` is 0.0 for every plant).
- Joint curvature is identically zero on every simulated run: e.g. one
  plant at k = 2, c = 1 bends its tip to 31.554 deg with all five
  segments equal at every recorded time.
- Injected curvature decays: starting from a curved stem (max joint
  curvature 6.0 deg), the curvature falls to 3.300 deg at 1 h, 0.693 at
  4 h and exactly 0.0 at 24 h.

**Structural reason.** With identical parameters on every segment and a
uniform initial state, the chain's uniform subspace is invariant (the
discrete Laplacian is exactly zero) and it is also attracting: both the
tropic drive and the elastic coupling act as restoring terms against
curvature. A uniform chain therefore rotates as a rigid rod — the model
is dynamically the rigid sim.py model with extra labels. Rigid rotation
cannot report shape, so the shape arm carried literally zero
information and the v1 comparison was uninformative about the value of
shape measurement: a test of a channel that does not exist.

**Consequence for reporting.** H-SHAPE v1 stands falsified as specified.
Because the falsification is structural rather than empirical, it
carries no evidence against the shape hypothesis itself. The corrected
experiment is specified in advance below, before it is run.

## 4. H-SHAPE v2 (pre-registered)

**Model change (sim_multiseg, `zeta` parameter).** Real bending requires
structural heterogeneity along the stem; the minimal physiological form
is a sensitivity gradient (the elongation zone near the tip responds
more strongly than the mature base). One new dimensionless parameter
zeta ("sensitivity concentration") modulates the per-segment gain:

    k_i = k * (1 - zeta + 2 * zeta * s_i),   s_i = i / (n_seg - 1)

so the base gain is k(1 - zeta) and the tip gain is k(1 + zeta).
zeta = 0 reproduces v1 exactly (uniform chain); zeta = 1 puts all
sensitivity contrast between base and tip. c (elastic coupling) is
unchanged. With zeta > 0 the uniform state is no longer a solution, the
stem takes a measurable shape, and the shape features vary across
plants.

**Population.** Same four-parameter margins (H1 population, seed 1);
c ~ Uniform[0, 1] (seed 2, as v1); zeta ~ Uniform[0, 1] (seed 3,
declared). n_seg = 5, static light, 24 h, 0.5 h records: unchanged.

**Hypothesis H-SHAPE-v2.** Clustering with tip+shape features reduces
median within-cluster IQR retention by at least 10 percentage points
relative to tip-only features, for at least two of the four original
parameters (k, tau, max_rate, phi0).

**Falsification.** Fewer than two of the four show a reduction of at
least 10 percentage points.

The criterion counts only the four original parameters: the motivating
question is whether shape measurement helps identify the parameters that
H1 showed to be degenerate. Retention for the new parameters (c, zeta)
is reported as secondary output and does not enter the verdict.

**Declared limitations carried into v2.** No measurement noise yet
(a noise-robust comparison remains a follow-up); n_seg fixed at 5; one
protocol (static light); the sensitivity gradient is a modelling choice,
not a measured profile; results describe the model class, not living
plants.

## 5. H-SHAPE v2: results

Run: `python shape_degeneracy_v2.py`, 18 October 2026, after section 4
was specified. Shape channel confirmed open: maximum joint curvature
across the run 19.733 deg. All regression checks passed, including exact
reduction at zeta = 0 and batch/single agreement at 7.1e-15 with
zeta = 0.8.

Retention (median within-cluster IQR / full range):

| Parameter | tip-only | tip+shape | delta (pp) |
|---|---:|---:|---:|
| k | 24.3% | 29.1% | **-4.8** |
| tau | 40.5% | 48.3% | **-7.8** |
| max_rate | 50.1% | 50.1% | **-0.1** |
| phi0 | 22.6% | 32.5% | **-10.0** |
| c | 51.7% | 37.3% | +14.3 |
| zeta | 44.2% | 41.5% | +2.7 |

**Verdict against the pre-registered criterion (>= 10 pp reduction for
>= 2 of the four original parameters): NOT SUPPORTED — falsified as
specified. No original parameter reaches the threshold; for three of the
four, retention is WORSE under the shape arm.**

The pre-registered secondary outputs show where the shape information
went: c improves by 14.3 pp (the coupling is the parameter that most
directly shapes the curvature profile) and zeta by 2.7 pp, but the
original parameters do not benefit at all.

Cluster structure is consistent with that reading: the largest tip-only
cluster holds 2,751 plants, the largest shape-arm cluster 4,089. Once
the clustering metric is dominated by the eight shape features (8 of 14
dimensions after scaling), plants group by shape-making similarity —
largely c and zeta — and within those shape-homogeneous groups the drive
parameters k, tau, max_rate and phi0 are freer to vary, not less.
Adding shape features to the clustering set actively displaced the
drive-parameter information the tip features carried.

**Interpretation, stated as what the data support.** Opening the shape
channel (v2 fixes v1's structural defect) is not sufficient for shape
measurement to improve identification of the original parameters under
the cluster-retention metric. The result joins the project's standing
warning about that metric (H2, `docs/RESULTS_ROUND1.md`): cluster
retention is a blunt instrument, and a negative under it is evidence
about the metric as much as about the hypothesis. What v2 does show is
that the curvature profile identifies the shape-making parameters of the
model class (c materially; zeta weakly) — measurement of shape answers
questions about shape.

**Declared follow-ups (not run, not used to reinterpret the verdict).**
Each requires its own pre-registration: (1) shape-only arm vs tip-only,
without mixing the two in one metric; (2) a more sensitive
identifiability metric — nearest-neighbour parameter recovery as in H7 —
applied to both arms; (3) a moving-light protocol arm; (4) observation
noise, at the measured-data cadence and amplitude. Image-derived stem
tracing remains the data requirement for any claim about living plants.

Files: `results/shape_degeneracy_v2_features.csv.gz`,
`results/shape_clusters_v2_tip.csv`, `results/shape_clusters_v2_full.csv`,
`results/shape_retention_v2_summary.csv`,
`results/shape_degeneracy_v2_summary.json`,
`results/figures/shape_retention_v2.png`.

## 7. Exploratory probe (NOT confirmatory)

`shape_probe_exploratory.py` was run on the saved v2 population to
decide whether a confirmatory study is warranted and what protocol it
should use. Everything in this section is exploratory: no hypothesis
tested here may be reported as confirmed. Outputs:
`results/shape_probe_exploratory.csv`.

Probe A (nearest-neighbour recovery, median |param difference| / full
range): with COMBINED features the behavioural twin's parameter error
falls to 5.0% (k), 4.3% (phi0), 7.1% (zeta) against 11.8%, 10.2%, 19.1%
with tip-only features.

Probe B (twin refinement — the original shape method, stated properly:
among a plant's 20 nearest tip-space neighbours, pick the one closest in
shape space): error falls from 11.8% to 6.0% (k), 10.2% to 5.5% (phi0),
24.7% to 13.9% (c), 19.1% to 8.6% (zeta). tau and max_rate do not
improve. The oracle (best of the 20 per parameter) sits at 0.7–1.6%:
there is headroom that shape does not capture for tau and max_rate.

Probe C (ExtraTrees, 5-fold CV R2): COMBINED features give 0.926 (k),
0.759 (tau), 0.957 (phi0), 0.916 (zeta) against tip-only 0.677, 0.513,
0.621, 0.300. max_rate is at chance in every arm (-0.03 to -0.01),
consistent with H1's exact-degeneracy result for non-binding caps.

Reading: the H-SHAPE-v2 negative was a decoder failure (shape dimensions
displacing tip dimensions in a KMeans distance, scored by the blunt
cluster-retention metric), not an information failure. Shape features
identify parameters, and among tip-space curve twins they identify which
twin is which — the original idea of this extension.

## 8. Twin-refinement v3 (pre-registered)

Written before the v3 run. Protocol and threshold were informed by the
section-7 exploration; the guard against over-fitting to that
exploration is that v3 runs on a FRESH population with new seeds.

**Population.** n = 10,000, the four-parameter uniform box of
`generate_plants.py` at seed 101; c ~ Uniform[0, 1] (seed 102);
zeta ~ Uniform[0, 1] (seed 103). Protocol unchanged: static light,
24 h, 0.5 h records, n_seg = 5, zeta-gradient model of section 4.

**Primary protocol (the original shape method).** Standardise tip
features (6) and shape features (8) separately. For each plant, take its
20 nearest neighbours in tip-feature space (behavioural twins under the
current observable). Among those 20, pick the one nearest in
shape-feature space. Identification error per parameter = median
|parameter difference| / full population range, reported for the plain
tip nearest neighbour and the refined pick.

**Hypothesis (v3).** Twin refinement reduces the median normalised
parameter error by at least 25 per cent relative to the plain tip
nearest neighbour, for at least two of the four original parameters
(k, tau, max_rate, phi0).

**Falsification.** Fewer than two of the four show a reduction of at
least 25 per cent.

**Secondary outputs (reported, no verdict).** Oracle (best of the 20
per parameter); nearest-neighbour recovery for tip-only, shape-only and
combined arms; ExtraTrees 5-fold CV R2 for the three arms; results for
the extension parameters c and zeta.

**Declared expectations.** The exploration suggests k and phi0 will
qualify and tau and max_rate will not (max_rate because the cap rarely
binds — an exact-degeneracy property from H1, not a method failure).
The criterion is unchanged by this expectation.

## 9. Twin-refinement v3: results

Run: `python shape_identification_v3.py`, 18 October 2026, on the fresh
population of section 8 (seeds 101/102/103), after section 8 was
specified.

Primary protocol (20 tip-space twins refined by shape):

| Parameter | tip twin | refined | oracle | reduction |
|---|---:|---:|---:|---:|
| k | 11.86% | 6.03% | 0.81% | **+49.2%** |
| tau | 10.36% | 11.02% | 1.11% | -6.4% |
| max_rate | 28.98% | 28.66% | 1.68% | +1.1% |
| phi0 | 10.54% | 5.70% | 0.71% | **+45.9%** |
| c | 23.41% | 13.75% | 1.54% | +41.3% |
| zeta | 18.54% | 8.83% | 1.32% | +52.4% |

**Verdict against the pre-registered criterion (>= 25 per cent error
reduction for >= 2 of the four original parameters): SUPPORTED.**
Exactly the two parameters declared as likely qualifiers do qualify:
k (+49.2 per cent) and phi0 (+45.9 per cent). tau and max_rate behave
as declared: no improvement. The fresh population reproduces the
exploratory effect sizes closely (exploration: k 48.8 per cent, phi0
45.9 per cent), so the section-7 protocol choice did not over-fit.

Secondary outputs (reported, no verdict):

NN recovery, median |difference| / full range:

| Parameter | tip | shape | combined |
|---|---:|---:|---:|
| k | 11.86% | 12.44% | 4.92% |
| tau | 10.36% | 19.73% | 10.05% |
| max_rate | 28.98% | 28.83% | 28.55% |
| phi0 | 10.54% | 5.22% | 4.47% |
| c | 23.41% | 7.67% | 10.63% |
| zeta | 18.54% | 15.70% | 6.99% |

ExtraTrees 5-fold CV R2:

| Parameter | tip | shape | combined |
|---|---:|---:|---:|
| k | 0.677 | 0.604 | 0.924 |
| tau | 0.522 | 0.187 | 0.761 |
| max_rate | -0.024 | -0.006 | -0.009 |
| phi0 | 0.625 | 0.915 | 0.962 |
| c | 0.056 | 0.792 | 0.786 |
| zeta | 0.286 | 0.509 | 0.913 |

**Reading.** The method works. Among plants with indistinguishable
tip-angle behaviour, the curvature profile selects the right plant
about half the identification error away from guessing: k error is
halved and phi0 error is halved, and the flexible decoder raises R2 to
0.92-0.96 for k and phi0 and 0.76 for tau with combined observables.
What shape cannot do is equally clear and equally informative:

- **max_rate** stays at chance in every arm. The oracle row (1.68 per
  cent) shows the 20 twins do contain near-correct max_rate values, but
  shape cannot tell which — and when the rate cap does not bind, no
  observable can (the H1 exact-degeneracy result). This is a property
  of the parameter under static light, not of the method.
- **tau** does not improve under twin refinement (though the combined
  decoder recovers it at R2 0.76): among tip twins, shape distance does
  not rank lag similarity. The oracle gap (1.11 per cent vs 11.02 per
  cent) says the information is present in the candidate set; a richer
  shape-time feature set or the moving-light arm is the declared route.

**Conclusion for the shape-measurement question.** Measuring angles
between the vertical and multiple points of the stem does make plants
tell apart what a single bending curve conflates — for the response
gain and the target angle, and for the shape-making parameters of the
model class. It is not a universal key (tau, max_rate under non-binding
caps), and it requires a decoder that respects what each observable
carries (refinement among twins, or a flexible joint decoder), not a
flat clustering metric. The pre-registered criterion is met.

Files: `results/shape_identification_v3.csv`,
`results/shape_identification_v3_summary.json`,
`results/figures/twin_refinement_v3.png`.

1. The v1 model class has an empty shape channel (uniform chains rotate
   rigidly and attract curvature to zero); its pre-registered test was
   run, falsified as specified, and diagnosed as uninformative.
2. The corrected model (sensitivity gradient zeta) opens the channel
   (joint curvatures up to 19.7 deg). Its pre-registered test (v2) is
   **also NOT SUPPORTED**: shape features improve identification only of
   the shape-making parameter c (+14.3 pp) and marginally zeta (+2.7 pp);
   for k, tau, max_rate and phi0 they change nothing or make retention
   worse, because shape-dominated clustering groups plants by c/zeta and
   releases the drive parameters.
3. Methodological result, the firmest of the three: the cluster-retention
   metric has now produced one structurally uninformative result (v1) and
   one metric-limited negative (v2). For the original parameters the
   hypothesis needed a different decoder to be tested fairly; that test
   (twin refinement and flexible decoding, sections 7-9) is SUPPORTED for
   k and phi0.
