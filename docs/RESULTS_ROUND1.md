# Results, round 1 — the complete fake-plant suite — 13 October 2026

All experiments in this file run entirely on simulated plants drawn from the
weighted population (clean fits, round 0 section 5). No new real data. Source:
`round1.py`, seeded, total wall time 14 seconds on one core. Every threshold
was declared in the script before the first run.

Dashboard: `results/figures/round1_dashboard.png`.

> **Amendment, 13 October 2026.** This suite was rerun on the
> clock-corrected weighted population (44 clean fits spanning all six
> stimulus start times; the original run drew from 28 morning-only fits
> produced by a time-base bug in `fit_real.py` -- see the retraction in
> `docs/RESULTS_ROUND0.md`, bug log). All numbers below are from the
> corrected run. Three verdicts are unchanged (H3 falsified, H6
> supported with leakage, H7 not supported as declared; H8 still
> saturated). **One verdict flipped: H4.** On the corrected population
> the behaviour clusters do *not* persist across light regimes
> (ARI 0.442, against 0.606 originally reported), so H4 is supported,
> not falsified. The original H4 reading is retracted wherever it
> appears in this file.

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

## H4: do clusters survive a moving sun? — SUPPORTED

Same 6,000 weighted plants clustered under static light and under a 12 h
sawtooth sweep (+/-45 deg around each plant's own phi0), same six features,
six clusters each. Declared persistence threshold: ARI >= 0.50.

Result: **ARI = 0.442.** Clusters do not persist across regimes.

The behavioural classes are partly properties of the light show, not just
of the plant: a moving sun repartitions the population. (The original run
reported ARI 0.606 and the opposite conclusion; that population excluded
every afternoon plant because of the clock bug, and morning-only plants
apparently sort more stably. Retracted.) Consequence: a cluster label is
a statement about a plant *under a protocol*, not a plant type -- which
is good news for H2's underlying hope that richer regimes reveal more,
even though H2's own cluster metric still does not show it, and a
warning against reifying the six classes anywhere downstream.

## H6: is the degenerate set connected? — SUPPORTED, WITH LEAKAGE

Umaid's crossover test. 300 pairs of behaviourally identical parents
(same static cluster), uniform gene crossover, mutation on each gene with
probability 0.5 and sd = 10 per cent of the weighted range, offspring
assigned to the nearest cluster centroid.

| Parents | Offspring stay in class |
|---|---|
| Same cluster (n=300) | **57.3%** |
| Cross-cluster control, mother's class (n=234) | 29.5% |
| Cross-cluster control, either parent's class | 53.8% |

Reading: offspring of equivalent parents stay equivalent at about twice
the control rate, so the degenerate set is **connected, not a scatter of
isolated islands** — small genetic steps mostly stay inside. But 43 per cent
leak out, so it is a valley with soft walls, not a flat neutral plane.
Evolutionary or sampling methods walking the set are meaningful, but need to
check membership at every step. Note the generous control: "either parent's
class" for cross-cluster pairs (53.8%) is a union of two classes; the
informative comparison is 57.3 against 29.5.

## H7: do protocols differ in what they reveal? — NOT SUPPORTED (as declared)

1,000 weighted plants per protocol. Recovery test: add 2 deg Gaussian noise
(low end of round-0 fit residuals), find the nearest other plant's noisy
curve, take that plant's parameters as the guess. Metric: mean relative
error, |true - recovered| divided by the population's 5-95 span. Declared
support threshold: best-worst gap >= 0.10.

| Protocol | cost (h) | mean rel. err | k | tau | cap | phi0 |
|---|---|---|---|---|---|---|
| dflip16   | 16 | **0.153** | 0.111 | 0.085 | 0.246 | 0.168 |
| flip12_14 | 14 | 0.178 | 0.154 | 0.149 | 0.239 | 0.171 |
| sweep12   | 12 | 0.183 | 0.143 | 0.172 | 0.272 | 0.143 |
| flip4_8   | 8  | 0.236 | 0.186 | 0.188 | 0.290 | 0.282 |
| static6   | 6  | 0.244 | 0.226 | 0.190 | 0.278 | 0.280 |

Result: gap = 0.091 < 0.10. **H7 not supported as declared.**

Two honest observations anyway, logged as description, not as rescued
claims. The ordering is consistent and sensible: every dynamic protocol
beats static light, and the double flip wins. And the cap is the worst-
recovered parameter under every protocol bar one statistical tie with
phi0 under static6 (0.24 to 0.29), exactly as the round-0
exact-degeneracy result predicts; tau, by contrast, is now the
best-recovered dial under the double flip (0.085). The threshold was
ours and arguably strict; what the declared test says is that no
protocol is a game-changer over another.

## H8: the identification game — pre-mortem CONFIRMED

500 weighted plants, 24 h budget, menu with costs (static6, flip4_8,
flip12_14, sweep12, dflip16), 2 deg noise, success = predict the held-out
ramp protocol (phi0 -30 to +30 over 24 h, never in the menu) within 5 deg
RMSE. Hypothesis set: 3,000 weighted draws. Policies: random, fixed (H7's
best, dflip16), greedy one-step expected-information-gain, plug-in Thompson.

| Policy | success per 100 |
|---|---|
| random   | **89.4** |
| greedy   | 88.6 |
| fixed    | 83.2 |
| thompson | 63.2 |

Greedy vs fixed, paired W/T/L: 37/406/10.

**The headline is the pre-mortem, confirmed almost word for word.** With a
24 h budget, *measuring at all* is a step function: even random protocol
choice identifies 89 plants in 100. Adaptive intelligence buys nothing over
rolling dice, and the single "best" protocol is actually worse than
mixing. This is structurally the same negative result as the matching
hackathon's "asking is a step function, not a lever", in a different domain,
found by a different team member (Umaid's crossover aside, the pre-mortem
was written before any of this ran).

The plug-in Thompson policy's 63.2 is far below the rest (binomial SE
about 2 per 100) and is read as a design artifact of the plug-in
approximation chasing posterior entropy on single samples, not as
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
| H2 | not supported on cluster metrics |
| H3 | falsified — smooth map, no cliffs at this resolution |
| H4 | supported — clusters do not persist across regimes (ARI 0.442) |
| H5 | passed 6/6 blocks on the corrected clock; 4/48 fits bound-pinned (ZT9) |
| H6 | supported with leakage — connected valley, 43% crossover escape |
| H7 | not supported as declared; dynamic protocols order above static |
| H8 | unanswerable as specified — game saturated by random play |

## What round 1 says overall

Two of eight hypotheses are dead as declared (H3, H7), one is
unanswerable until redesigned (H8), one is alive on a metric we do not
trust (H2), and the survivors are H1 (degeneracy), H4 (classes are
regime-dependent), H5 (the anchor) and H6 (connectivity, Umaid's). A
first round that kills half of what it touches is a first round that was
worth running: every death here was cheap (seconds of compute) and each
one narrows round 2. The consistent story across everything, corrected:
**a plant's behaviour is readable but is a property of the plant
*under a protocol*, not of the plant alone; the plant's parameters are
harder still; and no light show we tried changes that trade-off by
much.** (The first version of this paragraph called the behavioural
type "robust" on the strength of the retracted H4 result.)

## Limitations, stated

- Everything here is the simulator studying itself; H5 is the only bridge to
  real plants. Since the 13 October clock correction the bridge spans all
  six stimulus start times; its weak point is now the four ZT9 plants
  whose sub-three-minute onset the model's lag cannot express, so ZT9 is
  under-represented in the weighted population (2 of 6 plants).
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
  xlsx and the saved parameters, on elapsed time since stimulus onset:
  median 1.801 (reported 1.80), spread 8.582 (reported 8.58), per-plant
  deviation below 1e-14. A regression guard (check 3d) asserts every
  plant's fitted start equals its block's ZT and pins down the
  bound-pinned count, so the clock bug cannot return silently.
- **Exact degeneracy.** Cap-in vs cap-out RMSE on ZT0-1: 1.8939 vs 1.8939.
- **Retention numbers.** Independently recomputed: 9.3 / 3.7 / 13.6 / 11.9
  per cent against the reported 9 / 4 / 14 / 12.
- **H4 stability.** ARI across three clustering seeds: 0.442, 0.442, 0.444 --
  stably *below* the 0.50 persistence threshold. The corrected verdict
  (clusters do not persist) is not a seed artifact.
- **H8 ladder.** No data 30 per cent, one noisy 6 h static curve 44, full
  budget 89. The saturation is real but it is earned rung by rung; the
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
   (44 per cent), and the corrected ladder is the stronger result.

A fourth bug, larger than these three combined, arrived after the audit:
the ZT time-base error in `fit_real.py` (13 October, found by Yash;
full account in `docs/RESULTS_ROUND0.md`). The audit did not catch it
because its H5 check evaluated curves on the same raw-ZT convention as
the fitter -- it shared the assumption it was meant to test. The audit
now evaluates on elapsed time and carries a regression guard
(check 3d). Recorded here because it is the audit's real failure mode:
an independent code path with a non-independent assumption is only
half an audit.

One genuine refinement to H6 came out of the audit: connectivity of the
degenerate set holds for typical pairs but is not uniform. For
curve-equivalent pairs, 24/40 crossover children (light held fixed, phi0
not averaged) stay within 3 deg, median drift 1.88 deg, and drift tends
to grow with parental k-separation (median 1.53 deg below 0.1 of the
range, 3.4-4.4 deg above it, though only 6 of 40 pairs sit up there).
The single most-separated equivalent pair the search could find turns
out to be separated almost entirely in the cap (22 against 260 deg/h,
the exactly-degenerate dial) and its midpoint drifts only 1.07 deg --
so the dramatic 33 deg "pinch-off" reported by the first audit run was
an artifact of the morning-only population and does not reproduce. The
valley is connected; whether it pinches at its true extremes is still
open. Also noted: phi0 is an experimental condition, not a plant trait,
so any crossover test must hold it fixed.

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
