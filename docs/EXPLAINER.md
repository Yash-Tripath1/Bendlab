# BendLab, explained without jargon

Written for anyone opening the repo cold, including future us.

## The one-paragraph version

Plants bend toward light. We built a fake plant on a computer with four
dials, made 10,000 of them with random dial settings, watched them all bend,
and sorted them into piles by *how* they bent. Then we asked: if I hand you a
bending curve, can you work out the dials? The answer, so far, is no. Many
different plants produce the same curve.

## The four dials

| Dial | Code name | What it means |
|---|---|---|
| How strongly it responds to light | `k` | a plant with high `k` feels the light more urgently |
| How long it takes to react | `tau` | the delay between light changing and the plant starting to move |
| Fastest it can bend | `max_rate` | a speed limit, in degrees per hour |
| Where the light is | `phi0` | the angle the plant is trying to reach |

That is the whole plant. Four numbers and one equation.

## Why use a fake plant at all

Real experiments are slow. One Arabidopsis seedling, one light condition, one
afternoon, and you have a single curve. A simulation gives you 10,000 curves
in five seconds, and, more importantly, it gives you the dial settings, which
a real plant never tells you.

The price is that a fake plant can only ever tell you about itself. That is
why `fit_real.py` exists: it checks the fake plant against real measurements
before anyone is allowed to take the rest seriously.

## What "degeneracy" means here

Two different sets of dial settings can produce curves you cannot tell apart.

The cleanest example we found is exact, not approximate. Plant ZT0-1 in the
real data has a speed limit, `max_rate`. When we refit that plant with the
speed limit removed entirely, the fit quality is 1.894 degrees of error. With
the limit fitted, it is 1.894 degrees. Identical, to the last decimal, because
the plant never actually reaches its speed limit during the experiment. The
limit leaves no trace on the curve, so no amount of careful measurement could
recover it.

That is degeneracy: information the experiment simply does not contain.

## What we found

**The model is close enough to real plants to be worth studying.** Fitted
against 48 real sunflower curves, our error was 5.07 degrees. Real plants in
that same dataset differ from each other by 8.58 degrees. Our model is wrong
by less than plants naturally vary.

**Knowing what a plant does does not tell you what it is.** We sorted 10,000
simulated plants into six piles by behaviour. The largest pile, 2,197 plants,
contained essentially every possible value of the light angle while its
members bent almost identically. On average a behavioural pile still holds a
quarter to a half of the full range of every dial.

**The piles are about speed, not direction.** The clusters separate
fast-benders from slow-benders. How fast a plant moves comes through clearly.
Where it ends up, much less so.

**Changing the light mid-experiment did not help, on our first test.** We
moved the light 45 degrees at hour 8 and re-clustered. The piles did not get
any better at predicting dials. We think our measuring stick is too blunt
here, not that the idea is wrong, but that is a suspicion and not a result.

## Why anyone should care

If behaviour cannot identify the underlying parameters, then a whole class of
modelling paper is on shakier ground than it looks: the ones that fit a model
to a curve and report the fitted parameters as if they were measurements. Our
result says the curve often does not contain that information.

It also points somewhere useful. If one light condition cannot separate two
plants, maybe a different one can. Finding which experiments *do* carry
information is the next question, and it is a more interesting one than the
one we started with.

## Reading order for the repo

1. `PROBLEM_STATEMENT.md` — the question and the five hypotheses
2. `docs/RESULTS_ROUND0.md` — what came out, including what failed
3. `sim.py` — the model, about 60 lines of actual logic
4. `docs/DATA_SOURCES.md` — where the real data came from and where more lives
