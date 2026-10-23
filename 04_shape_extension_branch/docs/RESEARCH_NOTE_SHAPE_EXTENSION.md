# Research note: Can stem-shape measurement break parameter degeneracy in phototropic bending?

**Project:** BendLab — parameter identifiability in a minimal model of phototropic stem bending
**Repository branch:** `shape-extension` (github.com/umaidsiddiqui10/Bendlab)
**Date:** 18 October 2026
**Status:** Complete — one pre-registered confirmation after two documented falsifications
**Reproducibility:** every number below comes from seeded scripts in the branch; no unseeded randomness, no post-hoc metric changes inside a study

---

## 1. Background

BendLab studies a four-parameter model of phototropic stem bending:

    tau * dr/dt = k * sin(phi(t) - theta) - r
    r = clip(r, -max_rate, +max_rate)
    dtheta/dt = r

where `theta` is the stem angle from the vertical (the measured output),
`k` the response gain, `tau` the sensing lag, `max_rate` the bend-rate
cap, and `phi` the light direction. The project's central result
(experiment series 1) is **parameter degeneracy**: behaviourally similar
trajectories arise from widely different parameters. After clustering
10,000 simulated plants into six behavioural groups, within-cluster
parameter ranges retained 25–50 per cent of the full sampled range, and
`max_rate` is *exactly* unidentifiable for any trajectory whose bend
rate never reaches the cap (verified on a measured sunflower trajectory).

A single bending curve is therefore not a fingerprint of mechanism: two
plants can bend to the same tip-angle trajectory while differing in how
strongly, how fast and toward what target they bend.

## 2. The idea tested in this note

Instead of one angle, measure the **shape** of the stem: the angle
between the vertical and several points along the stem, over time —
i.e. the curvature profile theta(s, t). Two plants with the same tip
curve may bend at the tip vs the base, in a C vs an S, with different
bend-propagation timing. If the curvature profile carries parameter
information the tip angle discards, shape measurement should reduce
degeneracy.

## 3. Plan

1. **Model extension** (`sim_multiseg.py`): an n-segment elastic chain
   (5 segments in all studies). Each segment senses light locally with
   gain `k_i` and is coupled to its neighbours by an elastic torque
   `c * laplacian(theta)`. One structural parameter `zeta` sets a
   sensitivity gradient `k_i = k (1 - zeta + 2 zeta s_i)` (base vs tip;
   `zeta = 0` is a uniform chain). The extension is contract-checked to
   reduce **exactly** to the original model at `zeta = 0` (machine
   precision), so tip-angle results remain comparable with series 1.
2. **Observables** (`features.py`, `features_shape.py`): a tip-only arm
   (the six series-1 features, unchanged) and a shape arm (eight
   curvature-profile features: overall curvature, curvature centroid
   height, tip/base bias, S-shape incidence, bend-propagation gap, etc.).
   All feature definitions were fixed in writing **before** any run.
3. **Study design**: three studies, each with a hypothesis and
   falsification criterion registered **before** the run. Where a study
   failed for structural reasons, the corrected study was specified in
   advance of its own run. Any exploratory analysis is labelled
   non-confirmatory, and confirmatory runs use **fresh populations**
   (new seeds) so protocol choices cannot over-fit to exploration.

## 4. Outcomes — the three studies

### Study 1 (v1): clustering on tip vs tip+shape features — FALSIFIED, uninformatively

Same population as the published H1 sweep (10,000 plants), same metric
(median within-cluster IQR / full range).

| Parameter | tip-only | tip+shape | delta |
|---|---:|---:|---:|
| k | 25.3% | 25.4% | −0.1 pp |
| tau | 35.6% | 35.5% | +0.1 pp |
| max_rate | 50.2% | 50.1% | 0.0 pp |
| phi0 | 25.3% | 25.5% | −0.2 pp |

Verdict as pre-registered: not supported. **Diagnosis (structural):** the
uniform chain rotates rigidly and *attracts* curvature to zero (an
injected 6° S-curve decays to exactly 0.000° within 24 h), so every
shape feature was a constant across the population (std exactly 0). The
comparison tested a channel that did not exist; it is evidence about the
model class, not about shape measurement. (Sanity anchors: the tip arm
reproduced H1's published retention numbers and largest-cluster size,
n = 2,859, exactly.)

### Study 2 (v2): same comparison with the sensitivity gradient — FALSIFIED, honestly

`zeta > 0` opens the shape channel (joint curvatures up to 19.7°).

| Parameter | tip-only | tip+shape | delta |
|---|---:|---:|---:|
| k | 24.3% | 29.1% | **−4.8 pp** |
| tau | 40.5% | 48.3% | **−7.8 pp** |
| max_rate | 50.1% | 50.1% | −0.1 pp |
| phi0 | 22.6% | 32.5% | **−10.0 pp** |
| c (coupling) | 51.7% | 37.3% | +14.3 pp |
| zeta (gradient) | 44.2% | 41.5% | +2.7 pp |

Verdict as pre-registered: not supported. Shape features identify the
**shape-making** parameters (`c` clearly, `zeta` weakly), but mixing 8
shape features into a flat clustering distance against 6 tip features
*displaced* the drive-parameter information: shape-dominated clusters
group plants by `c/zeta` and release `k/tau/phi0`. Interpretation: a
decoder failure, not an information failure — to be tested, not assumed.

### Exploration (labelled non-confirmatory)

On the saved v2 population, three probes separated "no information" from
"wrong decoder": nearest-neighbour recovery, **twin refinement** (among
a plant's 20 nearest neighbours in tip-feature space — its curve twins —
pick the one nearest in shape space), and a flexible decoder
(ExtraTrees, cross-validated R²). All three showed strong signal; the
twin-refinement protocol became the pre-registered v3.

### Study 3 (v3): twin refinement on a fresh population — SUPPORTED

Pre-registered criterion: shape refinement reduces median normalised
parameter error by ≥ 25% versus the plain tip twin, for ≥ 2 of the four
original parameters. Fresh seeds (population 101 / c 102 / zeta 103),
n = 10,000.

| Parameter | tip twin | refined by shape | oracle (best of 20) | error reduction |
|---|---:|---:|---:|---:|
| **k** | 11.86% | **6.03%** | 0.81% | **−49.2%** ✅ |
| **phi0** | 10.54% | **5.70%** | 0.71% | **−45.9%** ✅ |
| zeta | 18.54% | 8.83% | 1.32% | −52.4% |
| c | 23.41% | 13.75% | 1.54% | −41.3% |
| tau | 10.36% | 11.02% | 1.11% | −6.4% ✗ |
| max_rate | 28.98% | 28.66% | 1.68% | +1.1% ✗ |

**Verdict: SUPPORTED** — `k` and `phi0` both exceed the 25% threshold,
exactly the two parameters the pre-registration expected to qualify.
Effect sizes replicate the exploration almost exactly on independent
seeds (e.g. R² combined arm: k 0.924 vs 0.926 explored; phi0 0.962 vs
0.957 explored).

Secondary outputs (reported, no verdict) confirm the picture with two
more decoders:

- Nearest-neighbour recovery, combined features: k error 4.9%, phi0 4.5%
  (curve-only: 11.9%, 10.5%).
- ExtraTrees 5-fold CV R², combined vs curve-only: k **0.924** vs 0.677;
  tau **0.761** vs 0.522; phi0 **0.962** vs 0.625; zeta **0.913** vs
  0.286; c **0.786** vs 0.056; max_rate −0.009 vs −0.024.

## 5. Final results — what the data support

1. **The method works.** Among plants with indistinguishable bending
   curves, the curvature profile identifies the right plant at roughly
   **half the identification error** for response gain (k) and effective
   light target (phi0), and a joint flexible decoder recovers k, tau and
   phi0 at R² 0.76–0.96 versus 0.52–0.68 from the curve alone.
2. **Shape answers shape questions.** The parameters that create shape
   (elastic coupling c, sensitivity gradient zeta) are identified
   strongly by shape and hardly at all by the tip curve (c: R² 0.79 vs
   0.06).
3. **Limits are sharp and informative.**
   - `max_rate` is at chance in **every** method whenever the rate cap
     does not bind — an exact degeneracy (H1), not a method failure. No
     amount of spatial or temporal resolution helps under static light.
   - `tau` is recovered well by the joint decoder (R² 0.76) but **not**
     by shape tie-breaking among curve twins; the oracle row (1.1%) shows
     the information exists in the candidate set and shape distance does
     not rank it. This is the clearest open target.

## 6. Improvements made along the way

- **Model engineering:** multi-segment simulator with machine-precision
  reduction to the published model (`check_multiseg.py`, all checks
  pass: exact reduction, batch/single agreement at 7e-15, rate-cap
  contract, determinism).
- **Structural auditing:** a pre-registered null can be vacuous; feature
  variance and curvature traces were audited before any interpretation.
- **Decoder design:** heterogeneous observables should not be
  flat-concatenated into one distance. Two designs work: tie-breaking
  among behavioural twins (refinement), or flexible joint decoding
  (regression), each of which weights what each observable carries.
- **Metric sensitivity:** cluster retention is a blunt identifiability
  instrument (consistent with the project's H2 experience).
  Nearest-neighbour recovery and cross-validated prediction are more
  responsive and more directly interpretable.
- **Scientific process:** every study pre-registered with falsification
  criteria; exploratory probes labelled as such; confirmations on fresh
  seeds; negatives, corrections and diagnoses recorded with the numbers.

## 7. Limitations

Results describe the simulator class, not living plants. All v3
observations are noiseless; one protocol (static light); one chain
length (5 segments); the sensitivity gradient `zeta` is a modelling
choice, not a measured profile; the model sees one planar angle per
segment. Real-plant claims require image-derived stem tracing
(theta(s, t) from photographs) and a noise-robustness study at the
measured-data cadence (half-hourly, as in the PLOS sunflower dataset
used by BendLab).

## 8. Recommended next steps

1. **Moving-light arm** (pre-register next): the declared candidate for
   unlocking `tau`, since lag differences are exposed by protocol
   changes (cf. H4: behavioural classes are protocol-dependent).
2. **Noise robustness:** repeat v3 with observation noise at the
   measured cadence and amplitude; five noisy measurements are not
   automatically better than one clean one.
3. **Richer shape-time features** targeting lag (e.g. curvature-wave
   timing), to close the oracle gap for `tau`.
4. **Real shape data:** stem-outline tracking on sunflower time-lapse
   images; then fit the multi-segment model to (theta(s, t)) directly.

## 9. Reproduction

From the repository root (Python 3.10+, `pip install -r requirements.txt`):

    python check_multiseg.py            # model contract checks
    python shape_degeneracy.py          # Study 1 (v1) — falsified, empty channel
    python shape_degeneracy_v2.py       # Study 2 (v2) — falsified, decoder failure
    python shape_probe_exploratory.py   # labelled exploration
    python shape_identification_v3.py   # Study 3 (v3) — SUPPORTED

Seeds: v1 population 1 / coupling 2; v2 + zeta 3; v3 population 101,
coupling 102, zeta 103; clustering and CV seed 1 / 101 respectively.
Full documents: `docs/SHAPE_EXTENSION.md` (design and pre-registrations),
`docs/SHAPE_EXTENSION_RESULTS.md` (all results and diagnoses).
Numerical outputs: `results/shape_*` and `results/figures/`.

---

*Prepared for external circulation. The study is part of the BendLab
project (Anadi Tripathi, project lead; Umaid, collaborator); this
extension was developed with Arena.ai Agent Mode assistance and follows
the project's reporting standards (pre-specified hypotheses, falsified
claims reported as falsified, corrections and error logs retained).*
