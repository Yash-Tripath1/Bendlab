# BendLab

**v0.0.1 | Anadi Tripathi + Umaid | 11 October 2026**

In-silico phenotyping of phototropic behaviour: generate a large population of
simulated bending plants, measure how each responds to changing light, and find
which parameter combinations are behaviourally distinguishable.

> Scope. This is a model study. Every result describes the behaviour of the
> simulator, not of real plants, unless a section explicitly compares against
> measured data and says so.

## The question

A bending-stem model has parameters: bend rate `k`, sensing delay, saturation
limit, and (later) a clock term. Two very different parameter vectors can
produce the same bending curve. If that is true, then:

- fitting a curve cannot recover the parameters, only some combination of them
- the interesting objects are the *equivalence classes*, not the parameters
- a second light regime may separate classes that one regime could not

## Formalisation

State: bend angle `theta(t)`, in degrees, measured from vertical.

Toy model: `dtheta/dt = k * sin(phi(t) - theta)` with first-order sensing lag
and a saturation cap on `|dtheta/dt|`.

Light regimes (`phi(t)`):
- `static` — constant angle, held
- `flip` — static, then a step change mid-run
- `sweep` — linear sweep across ~180 degrees over 12 h, reset overnight

Each simulated plant is one parameter vector. A run is `(parameter vector,
regime)`. Features extracted per run: time to orient, overshoot, final angle
error, tracking lag, turnaround behaviour.

## Hypotheses and falsification criteria

Written before any experiment is run. A hypothesis is abandoned, not softened,
when falsified.

| # | Hypothesis | Falsified if |
|---|---|---|
| H1 | Distinct parameter vectors produce indistinguishable curves under `static` light | Feature-space clusters separate parameter vectors cleanly at a fixed noise level |
| H2 | Adding `flip` separates some classes that `static` could not | Cluster purity on `flip` features is no better than on `static` features |
| H3 | Behaviour is discontinuous somewhere in parameter space — a small change flips the qualitative response | A dense sweep shows response features varying smoothly and boundedly everywhere |
| H4 | Clusters formed under `static` light do not persist under `sweep` | Cluster agreement between regimes is high (adjusted Rand index above a pre-set threshold) |
| H5 | The simulator's fitted parameters reproduce published stem-angle curves within their measurement noise | Fitted trajectories fall outside the per-plant spread of the measured data |

H1, H3 and H4 are stated as predictions that may well fail. H5 is the reality
anchor: if it fails, nothing above it means anything.

Two hypotheses were added on 11 October, after round 0 and before the
experiments that test them.

| # | Hypothesis | Falsified if |
|---|---|---|
| H6 | The set of parameter vectors sharing one behavioural fingerprint is connected: crossing over two behaviourally identical plants produces offspring that are also behaviourally identical | Offspring routinely fall outside the parents' equivalence class at small crossover and mutation step sizes |
| H7 | Light protocols differ measurably in how much they shrink the degenerate set, and can be ranked by identifiability gain | All tested protocols leave the same within-class parameter spread |
| H8 | Under a fixed budget of light exposure, an adaptive protocol-choice policy identifies plants (predicts an unseen protocol's curve within tolerance) more often than the best fixed protocol | The best fixed protocol matches or beats the adaptive policy within the seed-block CI |

H6 is a geometry claim about the degenerate set, and it decides whether an
evolutionary search over that set is even meaningful. H7 is the applied
payoff: if some protocols resolve more of the plant than others, that ranking
is a recommendation an experimenter could act on.

## Method, kept separate so each part can be ablated

1. **Generate.** Parameter vectors drawn by a seeded generator. Every run
   reproducible from the seed alone.
2. **Simulate.** Fixed-step integration, no unseeded randomness in the loop.
3. **Extract.** Feature functions defined before results are seen.
4. **Cluster.** Standard methods; cluster count chosen by a stated criterion,
   not by which one looks best.
5. **Diagnose.** Which parameter combinations are invariant within a class.
6. **Anchor.** Fit against measured stem-angle data.

## Data

| Kind | Source | Status |
|---|---|---|
| Synthetic populations | our own seeded generator | to write |
| Real stem angles, phototropism + heliotropism | PLOS Biology 2023, doi 10.1371/journal.pbio.3002344, S13 Data | in `data/real/` |

The real file is `stem_angles_plosbiol2023_s13.xlsx`: sheets `Fig1B`, `Fig1C`,
`Fig2B`, `Fig4A`, `Fig4J`, each a stem-angle time series per plant in degrees,
from sunflower plants undergoing phototropism or heliotropism. `Fig1C` holds
six light treatments (columns `ZT0-*` through `ZT16-*`, 7-9 plants each). `Fig2B`
is a time series in hours. Read `docs/DATA_CONTRACT.md` before touching it.

## What this is not

Not a claim about real plants. Not a functional-structural plant model. Not a
crop-yield tool. The simulator is a controlled object whose behaviour we study;
its relationship to botany is one published curve at a time.

## Disclosure

AI tools used: Arena.ai Agent Mode (ideation, code, drafting). All external
data sources and their licences are listed in the Data table above.
