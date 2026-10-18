# BendLab — Complete Project Briefing

> **Status note, 16 October 2026.** This briefing is superseded by `docs/CURRENT_STATUS.md`, the canonical summary. Several claims here (hypothesis verdicts, H6 connectivity, vector sample sizes) were corrected or withdrawn after external review; see `docs/AUDIT_FOLLOWUP_RESULTS.md`.


**For:** Anadi Tripathi and Umaid
**Date:** 15 October 2026
**Status:** Active independent computational research project. Repository: https://github.com/Yash-Tripathi/Bendlab

This document explains, in plain language, everything BendLab is, everything we have done, what we found, what we got wrong and corrected, and what should happen next. It assumes no prior context.

---

## 1. The project in 30 seconds

Plants bend toward light. BendLab is a small computer model of *how* a seedling stem bends toward a light source over time. We take real bending measurements from published sunflower experiments, fit our model to each individual seedling, and then use the fitted model to ask questions that are hard to ask in a wet lab: Which properties of the bending behaviour actually identify a plant? When two plants bend identically, are they really the same underneath? And when several lights shine at once, what direction does the plant *think* the light is coming from?

BendLab is simulation and data analysis only. We have grown no plants. Everything below is either (a) fitting the model to published experimental data, or (b) simulations whose assumptions are stated explicitly.

---

## 2. The model

A seedling's stem tip angle θ (degrees from vertical) evolves in one-minute steps:

- **Stimulus:** s = k · g · sin(φ − θ), where φ is the effective light direction, g is the effective light strength, and k is the plant's light sensitivity.
- **Bend rate:** the bending speed r relaxes toward s with time constant tau (hours). Slow tau = sluggish plant.
- **Speed limit:** r is clipped to ±max_rate (degrees per hour).
- **Advance:** θ increases by r each step.

So each simulated plant is just four numbers:

| Parameter | Meaning |
|---|---|
| k | How strongly light pulls the plant |
| tau | How quickly the bending speed responds (memory/sluggishness) |
| max_rate | The fastest the stem can physically bend |
| φ0 (phi0) | The light direction the plant is responding to (fitted, for static-light experiments) |

This simplicity is deliberate: with only four parameters, we can fit real plants, search huge populations, and understand exactly why the model succeeds or fails. It is also the model's main limitation (Section 9).

---

## 3. The data

All real data come from one published source: **Brooks, Atamian & Harmer (2023), PLOS Biology** (doi: 10.1371/journal.pbio.3002344), supplementary dataset S13.

- **Figure 1C (our main dataset):** 48 sunflower seedlings, each bent toward blue light switched on at one of six times of day (ZT0, 3, 6, 9, 12, 16). Each seedling gives a bending-angle time course.
- We also scoped other panels: Figure 2B (field heliotropism — plants tracking the sun, n=6) and Figure 4A (transplant-after-sunset, n=17) are candidates for future moving-sun fits. Figure 4J is **parked**: its values appear to be Z-score normalised in a way we could not resolve, and modelling it before resolving that would be building on sand.
- Mutant and light-quality sheets exist, but our model has no receptor "dials," so we do not fit them.

---

## 4. What we did, in order

### 4.1 Fitted the model to real seedlings
Each of the 48 seedlings was fitted individually. After an important bug fix (Section 5), the honest result is:

- **Median fit error: 1.80°** across all 48 curves — small compared to the ~50–80° the plants actually bend.
- **44 of 48 fits are "clean"** (no fitted parameter pushed against an allowed boundary, which usually means the model is straining).
- Those 44 clean fits define our **empirically weighted population**: simulated plants sampled to look like real measured seedlings, rather than arbitrary parameter values.

### 4.2 Asked whether bending behaviour identifies a plant
We simulated large populations and clustered plants by *behaviour* (the shape of their bending curve), then asked whether the clusters correspond to similar underlying parameters.

Findings (confirmed at 100,000 plants and again at 400,000):
- Plants in the same behaviour cluster still span wide parameter ranges (within-cluster spread is ~25–50% of the full parameter range depending on the parameter). Behaviour alone does not pin down the machinery.
- **Behaviour clusters do not survive a change of light regime.** Clustering plants under static light and re-clustering the same plants under flipping/sweeping light gives agreement (adjusted Rand index, ARI) of only **0.32–0.49**, below the 0.50 "same grouping" threshold. A plant's behavioural "type" is partly a property of the light it happens to be under.
- **Parameter recovery:** from a plant's nearest behavioural neighbour, k, tau and φ0 are recovered to ~1–2% error, but **max_rate only to ~33%**. Reason: if the speed limit never actually binds during an experiment, the data contain almost no information about it.
- **Behavioural twins exist:** genuinely different parameter sets can produce near-identical bending curves (twin searches found pairs matching to ~0.01° over 24 h with very different parameters). This is a real identifiability limit, not a numerical accident.

### 4.3 Adaptive identification (H8) — designed, frozen, not run
We designed an experiment-in-silico: can an adaptive policy that *chooses* the next light stimulus identify a hidden plant faster than fixed protocols? Version 1 was run; the improved version 2 (12 h budget, 5° observation noise, held-out ramp24 test, preregistered success criteria) is **written down and frozen in `docs/ADAPTIVE_IDENTIFICATION.md` and has deliberately not been run**. It remains available but is no longer the highest-value next step.

### 4.4 The visual simulator
`bendlab_visual_simulator.html` is a standalone, browser-based version of the exact same model (validated to agree with the Python integrator to floating-point precision). It lets anyone — including non-programmers — change parameters, pick light regimes, compare twin plants, and export data. It is prepared for GitHub Pages (`docs/index.html`); publishing it only requires pushing the repo and enabling Pages.

---

## 5. The bug we caught, and the claim we retracted

This deserves its own section because it is the part of the project we are proudest of.

An early version of the fitter integrated each seedling's curve from the wrong clock origin (absolute time instead of time since *its* light switched on). This distorted fits systematically, and produced a confident-sounding conclusion: *"the static-light model fails depending on time of day."*

That conclusion was **wrong, and we withdrew it.** After the fix:
- Median fit error improved from 4.74° to **1.80°**.
- Clean fits rose from 28/48 to **44/48**.
- One earlier hypothesis (H4, cluster persistence) **flipped** to ARI ≈ 0.44, and we report the flipped result.
- An independent audit script (`audit_round1.py`) re-derives the numbers by a separate code path; it passes all checks.

Lesson we now operate by: any number in this project should be reproducible by an independent route before it is believed, and corrections are documented, not hidden.

---

## 6. The one real failure: ZT9

Seedlings whose light switched on at ZT9 (mid-morning in the source experiment) fit systematically worse (median 2.42°, worst plant 6.76°). Diagnostics show a consistent **two-phase shape**: the real plants bend *faster* than the model early (4–8 h) and *slower* later (8–16 h), then agree again late. Refitting with the tau floor removed barely helps (2.420° → 2.400°), so this is a genuine **model-shape failure**, not an optimiser artefact.

Two candidate biological mechanisms, both from papers sent to us by a collaborator contact (Section 8):
- **Biphasic memory** (Rivière & Meroz 2023): plants integrate past stimuli with a kernel that goes positive then negative — literally "respond, then partially undo."
- **Proprioception / autostraightening** (Bastien et al. 2012): the stem senses its own curvature and straightens itself; a model without this term cannot reproduce late-time behaviour.

Testing these two against each other on held-out data ("Model v2") is the largest open scientific item in the project. It is deliberately *specified before it is coded*.

---

## 7. The vector-sum sunlight work (October 2026)

Kempinski et al. (2026) reported that sunflower seedlings do not respond to the *physical* sum of multiple lights; they respond to a sum of **nonlinearly transduced** local light signals around the stem (compressive exponent α ≈ 0.30, cross-stem transmission T ≈ 0.10). We built a stimulus-layer comparison inside BendLab, keeping the dynamics fixed and varying only how multiple sources become one effective direction and strength:

1. **Physical** — vector sum of raw intensities (current BendLab behaviour for multiple sources).
2. **Transduced-source** — each source compressed by I^α before vector summation.
3. **Circumference** — light integrated around a discretised stem circumference with transmission and local transduction (a 2-D reduction of the distributed-sensing idea).

Validation first: for a single source, all models reduce exactly to current BendLab (0.000° difference against `sim.py`).

**Findings:**
- Perceived direction can be distorted by up to **30.5°** (transduced-source) and **17.2°** (circumference) relative to physical summation, concentrated at 120–150° source separations and moderate intensity ratios.
- Under a moving sun plus diffuse sky, final angles differ from sun-only simulations by median ~9–16° depending on model, with 95th-percentile differences above 40°.
- A 45-condition sensitivity atlas (100,000 weighted plants) showed the effect is **driven by diffuse light**: ~0° with no diffuse sky, ~12–13° at strong diffuse. Varying α (0.15–0.50) changes it modestly; transmission T up to 0.25 softens but does not remove it.
- Behaviour clusters under the moving sun are moderately robust to the stimulus model at this scale (ARI 0.68–0.71 vs sun-only).
- The models are **most separable at near-opposing geometries**: 140–170° separation, intensity ratios 1.5–3. At 160°/2:1 the predicted final angles are ~61° (physical), ~44° (circumference), ~23° (transduced) — differences far larger than measurement noise. This motivated the experimental-design analysis in Section 8.

---

## 8. NEW: Could a real laboratory tell these models apart? (experimental design)

The models disagree *in silico*; the practical question is whether the disagreement survives real plant-to-plant variability and measurement noise in a feasible experiment. We simulated that experiment before anyone runs it:

- **Population:** 4,000 plants drawn from the empirically weighted population (real-fit-based variability).
- **Conditions:** the six strongest discriminating two-source geometries, plus a 90° condition and a 60°/1:1 "control" where the models nearly agree.
- **Readouts tested:** stem angle at 2 h, final angle at 24 h, and mean angle over 12/18/24 h.
- **Analysis:** 2,000 Monte-Carlo repetitions per cell; n seedlings per group, Gaussian measurement noise σ = 0.5–5°, Welch t-tests between each model pair; power = fraction significant at p < 0.05.

**Validation:** at the control condition, power came out at **0.044–0.051** — statistically indistinguishable from the 5% false-positive rate, exactly as it must if the machinery is honest.

**Findings:**
- At the best condition (**160 degrees separation, 2:1 intensity ratio**, final-angle readout, sigma = 2 degrees noise), the simulated final-angle distributions differ most strongly. An earlier version of this briefing quoted Welch-test sample sizes (n = 5 to 20 per group) as model-discrimination power. That interpretation is **withdrawn**: a Welch test between samples simulated under two candidate mechanisms measures distribution separation, not the probability that an experiment plus a model-selection procedure would identify the correct mechanism. Those sample sizes should not be quoted.
- **Measurement precision is nearly irrelevant; plant variability is the bottleneck.** Raising noise from σ = 0.5° to σ = 5° barely changes the required n (15 → 20 for the hardest pair). A phone camera and a protractor app would, statistically speaking, be enough; more seedlings beat better cameras.
- **Final angle at 24 h is the best readout.** The 2 h early angle is nearly useless for discrimination (power < 0.10 at n = 20) — early on, all models predict similar small bends. Trajectory averaging (12/18/24 h) is slightly worse than the final angle alone.
- Several geometries work, not just the champion: 120°/2:1 and 140°/3:1 need only n = 10–15 for every pair.

**Bottom line (revised):** the two-source geometry is a promising, inexpensive candidate design, and the three stimulus models make clearly different predictions under it. A defensible sample size requires a further simulation study: generate full datasets under each candidate mechanism, apply the actual planned model-selection procedure (including parameter-fitting uncertainty and biological variation), and report how often it selects the correct model. Until that is done, the vector results are model predictions that motivate a test, not a costed, statistically validated protocol.

Files: `exp_design.py`; `results/exp_design_power.csv`; `results/exp_design_recommendations.csv`; `results/figures/exp_design_dashboard.png`.

---

## 9. Limitations — read before quoting any number

1. The model has four parameters and no biology below the stem-tip angle: no photoreceptors, no hormones, no gravity response, no growth. It is a phenomenological bending model.
2. ZT9 (Section 6) is a genuine failure of the current model. Nothing in the vector-stimulus work fixes it; the stimulus work addresses *multi-source direction/gain*, not temporal response shape.
3. All population simulations inherit the limits of 44 fitted seedlings from one published dataset, one species, one light quality.
4. The circumference stimulus model is a 2-D reduction built for comparison; its parameters (α, T) are taken from Kempinski et al., not fitted by us.
5. H8 v2 is unrun; Figure 4J is unmodelled; mutant data are out of scope for this model.
6. The experimental-design numbers assume our model's dynamics and the fitted-population variability transfer to a new laboratory's seedlings. They are a strong prior for design, not a guarantee.

---

## 10. External input

Papers and criticism received from external researchers during the
project have been incorporated into the analyses above. Correspondence
and outreach records are maintained privately by the authors and are
not part of this public document.

---

## 11. Recommended next steps (in order)

1. **Seek external criticism** of the vector-stimulus predictions and of the model-selection experimental design (Section 8), before any sample-size claim is quoted.
2. **Model v2 specification** (on paper, before code): biphasic-memory vs proprioception arms, judged on held-out ZT9/non-ZT9 data under preregistered criteria.
3. **Fit the moving-sun panels** (Fig2B, Fig4A) now that moving-sun stimulus machinery exists — the next real-data validation.
4. Publish the visual simulator via GitHub Pages (push + enable; five minutes).
5. H8 v2 run, only if the above stall.

---

## 12. Plain-language glossary

- **Identifiability:** whether the data you can collect actually determine the thing you want to know. BendLab repeatedly finds limits here (max_rate, twins).
- **Behavioural twins:** two simulated plants with different internal parameters whose bending curves are nearly identical.
- **ARI (adjusted Rand index):** 1.0 = two groupings of plants are identical; ~0 = unrelated. We treat 0.50 as the "same grouping, roughly" line.
- **Weighted population:** simulated plants sampled so their parameters resemble the 44 real fitted seedlings, instead of covering an arbitrary box evenly.
- **Power (statistical):** the probability an experiment detects a real difference. 80% is the conventional design target.
- **Held-out test:** judging a model on data that played no part in building or fitting it. The only honest kind of test.

---

## 13. Where things live

| What | Where |
|---|---|
| Core model | `sim.py` |
| Real-data fits | `fit_real.py`, `results/fit_fig1c.csv` |
| Independent audit | `audit_round1.py` (all checks pass) |
| Population sweeps | `big_sweep.py` (100k), `mega_sweep.py` (400k) |
| Vector-stimulus comparison | `vector_stimulus.py`, `vector_batch.py`, `vector_grand_atlas.py` |
| Experimental design | `exp_design.py` |
| Visual simulator | `bendlab_visual_simulator.html`, `docs/index.html` |
| Frozen H8 v2 design | `docs/ADAPTIVE_IDENTIFICATION.md` |
| Results & figures | `results/`, `results/figures/` |
| This briefing | `docs/PROJECT_BRIEFING.md` |

*Prepared with AI assistance (Arena.ai Agent Mode). All results independently audited where stated; corrections and retractions are recorded in Sections 5–6 rather than removed.*
