# BendLab, explained — part 2

Continuation of `EXPLAINER.md`. Part 1 ended with: fake plants exist, they
bend believably, and watching one bend tells you less than you'd think about
its dials. Part 2 is what happened after: we made the fake plants *realistic*,
ran every remaining experiment, got audited, and found three bugs — all of
them mine, not the project's.

Companion figure: `results/figures/explainer2_dashboard.png`. Six panels,
every one drawn directly from the raw files. The section numbers below match
the panel numbers.

## 1. Two completely different plants, one curve

This is the whole thesis in one picture. Plant A's dials read
k=1.5, tau=3.0, cap=36, light=124 degrees. Plant B's read k=9.5, tau=20.2,
cap=34, light=26 degrees. Almost nothing in common. Their curves agree
within 1.2 degrees for a full day.

Why can this happen? Plant A points at a far target but is weak, so it
creeps. Plant B points at a near target but is slow to react, so it also
creeps. Creeping looks like creeping, whatever the reason. The curve records
*what happened*, not *why*. That is degeneracy, and the picture is the
entire argument.

## 2. The reality check

Before any of this matters, the fake plant has to bend like a real one. The
green dots are one real sunflower seedling from a published paper. The black
line is our fake plant fitted to it. They agree to within about 2 degrees,
and that real plant even overshoots and then relaxes — a wiggle our model
reproduces, because our model is secretly a damped pendulum (see panel 6).

One caveat we keep repeating: this holds for morning-light treatments. The
midday and afternoon experiments in that paper cannot be fit by our model,
and we know exactly why that is (the model assumes the light sits still; at
midday it evidently does not). A model that tells you where it stops
working is a working model.

## 3. The identification ladder

Question: can we tell which plant is which, from its curves? Three rungs:

- guess from nothing at all (predict with the average plant): 31 per cent
- one single 6-hour curve, plus the crudest possible matching: 56 per cent
- a full day of light experiments: 92 per cent

Two things fall out. Measuring helps a lot: 31 to 56 to 92. And within the
full-day rung, it makes almost no difference *how cleverly you choose* the
experiments: random choice scores 92, our smartest policy 91.6. The matching
hackathon found the same shape of truth in a completely different problem:
"doing it at all" is the step function, "doing it smart" is not a lever.
Two projects, one lesson, and we predicted it before running.

## 4. Umaid's breeding test

Umaid asked: take two plants that bend the same way, breed them (mix their
dials), does the child bend the same way too? If yes, the zone of identical
twins is connected — you can walk from one twin to another through small
changes without ever leaving the zone. If no, it's scattered islands.

The dots are 40 breeding experiments. Near the left (similar parents) the
children stay on the dashed "same plant" line. Far right (very different
parents who happen to match) the children drift off. So: connected valley
near the floor, pinching off at the edges. That is a *shape*, and knowing
the shape of a thing is what research is for. It also means the crossover
idea is a meaningful tool here — for typical pairs.

## 5. The scoreboard

Eight hypotheses, three dead, one unproven, one sent back for redesign,
three alive. That is a healthy round. A round where everything survives is
a round where you tested nothing. Dead hypotheses here were cheap: seconds
of compute, no lab animals, no broken equipment. The scoreboard is the
project's honest state, and the three survivors are the ones round two
builds on.

## 6. The audit, or: trust nothing, including this document

Someone (fairly) said they did not trust the results, and that the whole
thing running in seconds smelled fishy. So a separate script re-derived
every number from the raw files, and the simulator was checked against
physics with a closed-form answer — the damped pendulum formula you can
derive with pen and paper. Panel 6 is that check: the blue line is the
formula, the red dots are the simulator, and they sit on top of each other
through four oscillations. The simulator is right.

The audit found three bugs along the way, and all three were in the audit
itself:

1. It forgot that our angles are degrees while the sine formula wants
   radians. Classic. It briefly "proved" the simulator was wrong when the
   simulator was the correct one.
2. It tested a claim we never made — that same-cluster plants have
   identical curves. Clusters are "similar summaries", not "same curves".
3. It guessed one cheap curve would be enough to identify plants. It is not
   (56 per cent); the ladder is the truth.

None of the project's numbers changed because of these. All of the audit's
own claims changed. The lesson is not "the audit was bad", it is that the
second pair of eyes matters, and that an audit must be audited too. The
audit now lives in the repo (`audit_round1.py`) and prints ALL CHECKS PASSED.

## Why seconds is not suspicious

The whole suite does about 44 million tiny arithmetic updates. A modern
laptop does a few billion of those per second. The matching hackathon felt
slow because its work was different: each day of each episode ran a
graph-matching algorithm over 200 people, and there were over a thousand
episodes under a 10-second-per-decision budget. Same computer class, a
thousand times more work. Speed is arithmetic, not cheating.

## Where the story goes next

The fake-plant side is nearly done. What remains is the bridge to real
plants: fix the midday/afternoon mystery (let the light move in the model),
add a second real dataset (Arabidopsis curves, digitised from a 1993 paper),
and make the identification game harder so cleverness has something to bite
on. Then, and only then, does this start to look like a paper — see the
README for the paper question answered honestly.

Reading order for new readers: `EXPLAINER.md`, this file, then
`RESULTS_ROUND0.md` and `RESULTS_ROUND1.md` for the grown-up versions of
the same numbers.
