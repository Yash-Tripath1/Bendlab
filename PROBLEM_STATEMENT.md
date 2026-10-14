# BendLab — problem statement

## Parameter identifiability in a minimal model of phototropic stem bending

**Version:** 0.1.0  
**Date:** 11 October 2026  
**Authors:** Anadi Tripathi and Umaid  
**Status:** Experiment series 1 complete; model extension and adaptive
identification v2 specified

---

## Abstract

A plant stem bends toward incident light, but similar bending trajectories
can arise from different combinations of physiological and environmental
parameters. BendLab investigates this parameter-identifiability problem
using a four-parameter model of phototropic bending. The project combines
controlled simulations with fits to published sunflower stem-angle data.

The central question is whether the parameter values of an individual
plant can be recovered from its bending trajectory under static light and,
if not, whether alternative light protocols or adaptive protocol selection
can recover additional information. The completed analyses show that
behaviourally similar simulated plants can retain much of the full
parameter range, that one model parameter can be exactly unidentifiable
for non-saturating trajectories, and that behavioural classifications
depend on the light protocol under which they are measured. The model
nevertheless reproduces measured sunflower trajectories with an error
smaller than the observed variation among plants.

---

## 1. Background and rationale

Phototropic bending is commonly represented as a response to the angular
difference between the stem axis and the incident light direction. A
phenomenological model of this response is useful only if its parameters
can be related to observable behaviour. In practice, several parameter
combinations may generate nearly indistinguishable trajectories. This
many-to-one mapping is termed **parameter degeneracy**.

Degeneracy has two distinct consequences. First, it limits the biological
interpretation that can be placed on parameters obtained by fitting a
single trajectory. Second, it raises an experimental-design question:
different light regimes may expose different aspects of the underlying
dynamics, so some protocols may identify the plant more effectively than
others.

BendLab addresses both consequences. Simulation is used because the true
parameter values are known, making it possible to measure directly how
much parameter information is retained or lost when plants are grouped by
behaviour. Published measurements are used to restrict the simulations to
a parameter region supported by experimental data.

## 2. Model

Let $\theta(t)$ denote stem angle and $r(t)$ the instantaneous rate of
change of stem angle. The model is

$$
\dot{\theta} = r,
\qquad
\tau \dot{r}
=
\operatorname{clip}\!\left(
  k \sin(\phi(t)-\theta),\,
  -r_{\max},\,
  r_{\max}
\right) - r,
$$

where:

| Parameter | Unit | Interpretation |
|---|---:|---|
| $k$ | degrees h$^{-2}$ | Response gain to the angular difference between light direction and stem axis |
| $\tau$ | h | Time constant of the sensing and response lag |
| $r_{\max}$ (`max_rate`) | degrees h$^{-1}$ | Maximum permitted bend rate |
| $\phi_0$ | degrees | Light direction under a static-light regime |

The term $\sin(\phi-\theta)$ follows the qualitative form of the
Blaauw sine law for first positive phototropism. The first-order lag
represents the delay between a change in the perceived stimulus and the
resulting change in bend rate. The rate limit represents saturation of
the bending response.

This is a minimal phenomenological model, not a mechanistic model of
photoreception, auxin transport or differential growth.

### State variables and integration

- $\theta$: stem angle relative to vertical, in degrees.
- $r$: bend rate, in degrees per hour.
- Integration: explicit Euler method.
- Nominal step: 1 min (1/60 h).
- Initial stem angle: $0^\circ$ unless a protocol specifies otherwise.
- Initial bend rate: $0^\circ\,\mathrm{h}^{-1}$.

Parameter ranges are specified in `generate_plants.py`. The biologically
weighted population is derived from the clean fits reported in
`docs/RESULTS_ROUND0.md`.

## 3. Research questions

1. **Degeneracy.** To what extent do different parameter combinations
   produce indistinguishable bending trajectories?
2. **Model adequacy.** Can the four-parameter model reproduce measured
   sunflower stem-angle trajectories within the variation observed among
   plants?
3. **Protocol dependence.** Are behavioural classifications stable when
   the light regime changes?
4. **Connectivity.** Is the set of parameter combinations producing
   similar behaviour connected, or does it consist of isolated regions?
5. **Experimental design.** Which light protocols provide the greatest
   information about an individual plant, and can adaptive protocol
   selection outperform fixed or random selection?

## 4. Hypotheses and falsification criteria

### H1 — Behavioural degeneracy

After clustering simulated trajectories obtained under static light,
within-cluster parameter ranges will retain at least 20 per cent of the
full population range for at least three of the four parameters.

**Falsification:** retention below 20 per cent for at least three
parameters.

### H2 — Information from a change in light direction

A 45-degree change in light direction during the observation period will
reduce within-cluster parameter spread by at least 10 percentage points
relative to static light.

**Falsification:** no parameter shows a reduction of at least 10
percentage points, or reductions are inconsistent in direction.

### H3 — Discontinuities in the parameter-to-behaviour mapping

The mapping from parameters to behavioural features contains regions in
which a small parameter change produces a qualitatively different
trajectory.

**Falsification:** dense sampling identifies no adjacent parameter pairs
whose behavioural distance exceeds five times the median adjacent-pair
distance.

### H4 — Protocol dependence of behavioural classes

Behavioural clusters obtained under a moving-light regime will differ
materially from those obtained under static light.

**Criterion:** an adjusted Rand index (ARI) below 0.50 between static-
and moving-light cluster assignments is interpreted as failure of cluster
persistence.

### H5 — Adequacy for measured sunflower trajectories

When fitted independently to each measured sunflower trajectory, the
model will produce a median RMSE below the across-plant standard
deviation in at least five of the six stimulus-start-time groups.

**Falsification:** the criterion is met in four or fewer groups, or more
than half of the individual fits require a parameter at an optimisation
bound.

### H6 — Connectivity of the degenerate parameter set

Parameter vectors obtained by recombining pairs of behaviourally
equivalent simulated plants will remain in the source behavioural class
more frequently than recombinants of behaviourally distinct pairs.

**Falsification:** the class-retention rate for equivalent source pairs
does not exceed that for the control pairs.

### H7 — Differences among light protocols

Light protocols differ in the parameter information they provide, as
measured by nearest-neighbour parameter-recovery error under noisy
observations.

**Criterion:** H7 is supported if the difference between the best and
worst protocols is at least 0.10 in mean relative recovery error.

### H8 — Adaptive protocol selection

A policy that selects the next light protocol adaptively will identify
more plants than random or fixed protocol selection when identification
is defined by accurate prediction of a held-out protocol trajectory.

Version 1 of this experiment was saturated. The pre-specified criterion
for v2 is given in `docs/ADAPTIVE_IDENTIFICATION.md`: the best adaptive
policy must exceed both non-adaptive baselines by at least five
successful predictions per 100 plants.

## 5. Measured data

The measured dataset is S13 Data from:

> Brooks, C. J., Atamian, S. H. & Harmer, S. L. (2023). *Multiple
> light signaling pathways control solar tracking in sunflowers*. PLOS
> Biology. doi:10.1371/journal.pbio.3002344.

Sheet Fig1C contains sunflower stem-angle trajectories following
unilateral blue-light stimulation beginning at six zeitgeber times
(ZT0, ZT3, ZT6, ZT9, ZT12 and ZT16). The handling rules, including the
requirement to analyse elapsed time from stimulus onset rather than
absolute zeitgeber time, are specified in `docs/DATA_CONTRACT.md`.

## 6. Analysis sequence

1. Fit the model to each measured trajectory (H5).
2. Derive the empirically weighted parameter population from clean fits.
3. Generate uniform and weighted simulated populations and extract
   behavioural features.
4. Cluster trajectories and quantify within-cluster parameter retention
   (H1, H2).
5. Evaluate discontinuities, protocol dependence and connectivity
   (H3, H4, H6).
6. Compare light protocols and protocol-selection policies (H7, H8).
7. Re-derive the principal results through independent code paths and
   analytical limiting cases.

## 7. Scope and limitations

BendLab is a study of a minimal mathematical model. Simulation results
characterise that model and should not be interpreted as direct evidence
about living plants. The measured-data analysis supports the limited
conclusion that the model can reproduce the recorded stem-angle
trajectories under the specified stimulus conditions; it does not
establish the underlying physiological mechanism.

The model does not currently represent:

- circadian modulation of phototropic sensitivity;
- autostraightening (autotropism) in the absence of a directional error
  signal;
- photoreceptor-specific responses to spectral composition;
- gravitropic interaction;
- spatial growth along the stem;
- a moving solar stimulus and night-time reorientation.

These omissions define candidate model extensions. An extension will be
evaluated by held-out prediction against the present model, rather than
by improvement in within-sample fit alone.

## 8. Reproducibility

All stochastic analyses use declared seeds. Parameter bounds, decision
thresholds and falsification criteria are recorded before the
corresponding analyses are run. Corrections and retracted results remain
in the results documents with the numerical values they affected, so that
the provenance of each conclusion can be inspected.

## References

1. Brooks, C. J., Atamian, S. H. & Harmer, S. L. (2023). Multiple light
   signaling pathways control solar tracking in sunflowers. *PLOS
   Biology*. https://doi.org/10.1371/journal.pbio.3002344
2. Atamian, S. H., Creux, E. A., Brown, E. A., Garner, A. G., Blackman,
   B. K. & Harmer, S. L. (2016). Circadian regulation of sunflower
   heliotropism, floral orientation, and pollinator visits. *Science*,
   353, 587–590. https://doi.org/10.1126/science.aaf9793
3. Orbovic, V. & Poff, K. L. (1993). Growth distribution during first
   positive phototropic curvature of Arabidopsis hypocotyls. *Plant
   Physiology*, 103, 157–163.
