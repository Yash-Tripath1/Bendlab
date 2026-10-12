# Results, round 1 — the complete fake-plant suite — 13 October 2026

All experiments in this file run entirely on simulated plants drawn from the
weighted population (clean fits, round 0 section 5). No new real data. Source:
`round1.py`, seeded, total wall time 14 seconds on one core. Every threshold
was declared in the script before the first run.

Dashboard: `results/figures/round1_dashboard.png`.

## H3: cliffs in parameter space — FALSIFIED

Dense 64 x 64 grid over (k, tau) at phi0 = 45 deg, cap = 30 deg/h, static
light, 24 h. Declared cliff criterion: adjacent-cell jump in half-rise time
above 2.0 h.

Result: **0 of 8,064 edges flagged. Largest adjacent jump 1.00 h.**

Behaviour varies smoothly across the plausible region. There is no hidden
cliff where a tiny parameter change flips the qualitative response, at this
resolution and these feature definitions. H3 is abandoned as stated. Caveat:
a finer grid or sharper features (for instance overshoot under flip regimes)
could still find discontinuities; "smooth here" is not "smooth everywhere".

## H4: do clusters survive a moving sun? — FALSIFIED

Same 6,000 weighted plants clustered under static light and under a 12 h
sawtooth sweep (+/-45 deg around each plant's own phi0), same six features,
six clusters each. Declared persistence threshold: ARI >= 0.50.

Result: **ARI = 0.606.** Clusters largely persist across regimes.

The behavioural classes are mostly properties of the plant, not of the light
show: fast responders stay fast responders when the sun moves. This was
stated as a prediction that might well fail, and it failed cleanly.
Consequence: the classes we report are not an artifact of one protocol,
which is good news for their meaning, and bad news for H2's hope that a
moving sun would reveal a fundamentally different partition.

## H6: is the degenerate set connected? — SUPPORTED, WITH LEAKAGE

Umaid's crossover test. 300 pairs of behaviourally identical parents
(same static cluster), uniform gene crossover, mutation on each gene with
probability 0.5 and sd = 10 per cent of the weighted range, offspring
assigned to the nearest cluster centroid.

| Parents | Offspring stay in class |
|---|---|
| Same cluster (n=300) | **62.7%** |
| Cross-cluster control, mother's class (n=257) | 29.2% |
| Cross-cluster control, either parent's class | 63.4% |

Reading: offspring of equivalent parents stay equivalent at more than twice
the control rate, so the degenerate set is **connected, not a scatter of
isolated islands** — small genetic steps mostly stay inside. But 37 per cent
leak out, so it is a valley with soft walls, not a flat neutral plane.
Evolutionary or sampling methods walking the set are meaningful, but need to
check membership at every step. Note the generous control: "either parent's
class" for cross-cluster pairs (63.4%) is a union of two classes and sits at
the same level as the same-cluster number; the informative comparison is
62.7 against 29.2.

## H7: do protocols differ in what they reveal? — NOT SUPPORTED (as declared)

1,000 weighted plants per protocol. Recovery test: add 2 deg Gaussian noise
(low end of round-0 fit residuals), find the nearest other plant's noisy
curve, take that plant's parameters as the guess. Metric: mean relative
error, |true - recovered| divided by the population's 5-95 span. Declared
support threshold: best-worst gap >= 0.10.

| Protocol | cost (h) | mean rel. err | k | tau | cap | phi0 |
|---|---|---|---|---|---|---|
| dflip16   | 16 | **0.176** | 0.145 | 0.141 | 0.242 | 0.175 |
| sweep12   | 12 | 0.203 | 0.176 | 0.219 | 0.298 | 0.119 |
| flip12_14 | 14 | 0.238 | 0.225 | 0.205 | 0.329 | 0.192 |
| flip4_8   | 8  | 0.240 | 0.195 | 0.232 | 0.288 | 0.246 |
| static6   | 6  | 0.262 | 0.238 | 0.236 | 0.317 | 0.257 |

Result: gap = 0.086 < 0.10. **H7 not supported as declared.**

Two honest observations anyway, logged as description, not as rescued
claims. The ordering is consistent and sensible: every dynamic protocol
beats static light, and the double flip wins. And the cap is the worst-
recovered parameter under every protocol (0.24 to 0.33), exactly as the
round-0 exact-degeneracy result predicts. The threshold was ours and
arguably strict; what the declared test says is that no protocol is a
game-changer over another.

## H8: the identification game — pre-mortem CONFIRMED

500 weighted plants, 24 h budget, menu with costs (static6, flip4_8,
flip12_14, sweep12, dflip16), 2 deg noise, success = predict the held-out
ramp protocol (phi0 -30 to +30 over 24 h, never in the menu) within 5 deg
RMSE. Hypothesis set: 3,000 weighted draws. Policies: random, fixed (H7's
best, dflip16), greedy one-step expected-information-gain, plug-in Thompson.

| Policy | success per 100 |
|---|---|
| random   | **92.0** |
| greedy   | 91.6 |
| fixed    | 87.8 |
| thompson | 73.2 |

Greedy vs fixed, paired W/T/L: 25/433/6.

**The headline is the pre-mortem, confirmed almost word for word.** With a
24 h budget, *measuring at all* is a step function: even random protocol
choice identifies 92 plants in 100. Adaptive intelligence buys nothing over
rolling dice, and the single "best" protocol is actually slightly worse than
mixing. This is structurally the same negative result as the matching
hackathon's "asking is a step function, not a lever", in a different domain,
found by a different team member (Umaid's crossover aside, the pre-mortem
was written before any of this ran).

The plug-in Thompson policy's 73.2 is significantly below the rest
(binomial SE about 1.3 per 100) and is read as a design artifact of the
plug-in approximation chasing posterior entropy on single samples, not as
evidence against Thompson sampling itself.

Consequence for round 2: the game as specified is too easy to discriminate
policies. Harder variants, in rough order of promise: cut the budget to
8-12 h; raise the success bar (eps = 2 deg); raise the noise to 5 deg; make
the held-out protocol a genuine extrapolation (ramp beyond any phi0 the
policy has seen). Until the game is hard, H8's adaptive-vs-fixed question is
unanswerable, and running fancier policies would be theater.

## Status after round 1

| # | Status |
|---|---|
| H1 | supported (uniform), weaker but present (weighted) |
| H2 | not supported on cluster metrics; H4's persistence explains part of why |
| H3 | falsified — smooth map, no cliffs at this resolution |
| H4 | falsified — clusters persist across regimes (ARI 0.606) |
| H5 | passed, with the static-light caveat for ZT12/ZT16 |
| H6 | supported with leakage — connected valley, 37% crossover escape |
| H7 | not supported as declared; dynamic protocols order above static |
| H8 | unanswerable as specified — game saturated by random play |

## What round 1 says overall

Three of eight hypotheses are dead (H3, H4, H7 as declared), one is
unanswerable until redesigned (H8), and the survivors are H1 (degeneracy),
H5 (the anchor, with a caveat) and H6 (connectivity, Umaid's). A first round
that kills half its hypotheses is a first round that was worth running:
every death here was cheap (seconds of compute) and each one narrows round 2.
The consistent story across everything: **the plant's behavioural type is
robust and readable; the plant's parameters are not; and no light show we
tried changes that trade-off by much.**

## Limitations, stated

- Everything here is the simulator studying itself; H5 is the only bridge to
  real plants and it holds only for morning-light treatments.
- Nearest-neighbour recovery (H7) is a crude identifiability proxy; a
  posterior-volume metric could reorder protocols.
- Clustering into six groups is a declared choice, not a derived one; H4's
  ARI and H6's retention both inherit it.
- The H8 hypothesis set is finite (3,000 draws); a true grid posterior would
  smooth the posterior-mean prediction and likely raise all success rates.

## Audit, 13 October

Prompted by a collaborator who did not trust the results (correctly applied
pressure). `audit_round1.py` re-derives the findings through independent code
paths and validates the simulator against closed-form physics. Final state:
all checks pass. What it verified:

- **Simulator against analytical physics.** The model is mathematically a
  damped pendulum in the angle to the light. Simulated overshoot matches the
  closed form to 0.001 deg in two damping regimes (10.067 vs 10.068, 14.17 vs
  14.18) and the oscillation period to 0.002 h (3.488 vs 3.490). Three
  independent integrators agree to 1.4e-14.
- **H5 from raw data.** All 48 per-plant RMSEs recomputed from the original
  xlsx and the saved parameters: median 4.742 (reported 4.74), spread 8.582
  (reported 8.58), per-plant deviation below 1e-14.
- **Exact degeneracy.** Cap-in vs cap-out RMSE on ZT0-1: 1.8939 vs 1.8939.
- **Retention numbers.** Independently recomputed: 13.1 / 9.9 / 27.7 / 7.7
  per cent against the reported 13 / 10 / 28 / 8.
- **H4 stability.** ARI across three clustering seeds: 0.606, 0.608, 0.605.
- **H8 ladder.** No data 31 per cent, one noisy 6 h static curve 56, full
  budget 92. The saturation is real but it is earned rung by rung; the
  budget is not redundant.

Three bugs were found during the audit, and all three were **in the audit,
not in the project**, which is recorded because the failure modes are
instructive:

1. The pendulum prediction forgot that theta is in degrees while sin() takes
   radians, overstating the natural frequency by a factor of 13.4 and
   "detecting" a simulator failure that did not exist. Corrected, theory and
   simulation agree to three decimals.
2. The first H1 probe tested "same cluster implies same curve", which the
   project never claimed. Same-cluster plants can differ by ~13 deg
   pointwise; a cluster is a similarity of summaries, not an identity of
   curves. The actual claim (parameter retention) reproduces.
3. The first H8 probe asserted one cheap curve already suffices. It does not
   (56 per cent), and the corrected ladder is the stronger result.

One genuine refinement to H6 came out of the audit: connectivity of the
degenerate set degrades with parent separation. For typical curve-equivalent
pairs, 28/40 crossover children (light held fixed, phi0 not averaged) stay
within 3 deg, median drift 1.56 deg; but the single most-separated
equivalent pair found has a midpoint that drifts 33 deg, and drift grows
monotonically with parental k- and tau-separation (median 1.16 deg below
0.1 separation, ~7 deg above 0.3). The valley is connected near its floor
and pinches off at the extremes. Also noted: phi0 is an experimental
condition, not a plant trait, so any crossover test must hold it fixed.

## Why this runs in seconds, not hours

The full suite performs about 44.1 million Euler updates, roughly 10 flops
each, about 0.44 GFLOP on one core. Each update advances two state variables
with six arithmetic operations. The matching hackathon, for contrast, ran a
maximum-weight matching on a general graph of up to 200 members per decision
day (blossom algorithm, superlinear in the node count), across 60-day
episodes and 1,326 of them, under a 10-second per-decision budget. Orders of
magnitude more work per step, orders of magnitude more steps. The speed here
is arithmetic, not a shortcut.

## Files

| File | Content |
|---|---|
| `round1.py` | the whole suite, all constants declared at the top |
| `audit_round1.py` | independent re-derivation of every finding |
| `results/round1_h7_protocols.csv` | protocol recovery table |
| `results/round1_h8_policies.csv` | policy success table |
| `results/figures/round1_dashboard.png` | six-panel dashboard |
