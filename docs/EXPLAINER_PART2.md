# BendLab, explained — part 2

Continuation of `EXPLAINER.md`. Part 1 ended with: fake plants exist, they
bend believably, and watching one bend tells you less than you'd think about
its dials. Part 2 is what happened after: we made the fake plants *realistic*,
ran every remaining experiment, got audited, and found bugs — including one,
spotted by Anadi Tripathi, that reversed two of our headlines. That one gets its
own telling below, because it is the most instructive thing in the project
so far.

Companion figure: `results/figures/explainer2_dashboard.png`. Six panels,
every one drawn directly from the raw files. The section numbers below match
the panel numbers.

## 1. Two completely different plants, one curve

This is the whole thesis in one picture. Plant A's dials read
k=7.9, tau=4.8, cap=251, light=43 degrees. Plant B's read k=9.4,
tau=6.4, cap=24, light=40 degrees. Their curves agree within 1.3
degrees for a full day -- while one plant's speed limit is *ten times*
the other's.

Why can this happen? Neither plant ever bends anywhere near its speed
limit, so the limit leaves no trace on the curve. A dial that never
comes into play might as well not exist, and the curve records *what
happened*, not *why*. That is degeneracy in its purest form, and the
broader version -- whole clusters of look-alike plants spanning most of
every dial's range -- is measured properly in the results documents.
The picture is the entire argument in miniature.

## 2. The reality check

Before any of this matters, the fake plant has to bend like a real one. The
green dots are one real sunflower seedling from a published paper. The black
line is our fake plant fitted to it. They agree to within about 2 degrees,
and that real plant even overshoots and then relaxes — a wiggle our model
reproduces, because our model is secretly a damped pendulum (see panel 6).

One caveat we used to keep repeating: that this only holds for
morning-light treatments, because the midday and afternoon experiments
could not be fit. **That caveat was wrong, and it was ours, not the
plants'.** The paper's clock is zeitgeber time -- hours since the
chamber lights came on -- and each group of plants got its side light
switched on at a different time of day. We fed the raw clock to a
fitter that assumed the light had been on since hour zero, so an
afternoon plant looked impossibly slow and the fitter duly reported
impossibly slow plants. On the corrected clock (time since *its* light
came on) every group fits, afternoon included, to about 2 degrees.
The one genuine oddity left is the ZT9 group, which starts bending
faster than our model's shortest allowed lag. A model that tells you
where it stops working is a working model; a team that checks whether
the failure is in the model or in its own timestamps is a working
team. Full retraction: `RESULTS_ROUND0.md`, bug log.

## 3. The identification ladder

Question: can we tell which plant is which, from its curves? Three rungs:

- guess from nothing at all (predict with the average plant): 30 per cent
- one single 6-hour curve, plus the crudest possible matching: 44 per cent
- a full day of light experiments: 89 per cent

Two things fall out. Measuring helps a lot: 30 to 44 to 89. And within the
full-day rung, it makes almost no difference *how cleverly you choose* the
experiments: random choice scores 89, our smartest policy 88.6. The matching
hackathon found the same shape of truth in a completely different problem:
"doing it at all" is the step function, "doing it smart" is not a lever.
Two projects, one lesson, and we predicted it before running.

## 4. Umaid's breeding test

Umaid asked: take two plants that bend the same way, breed them (mix their
dials), does the child bend the same way too? If yes, the zone of identical
twins is connected — you can walk from one twin to another through small
changes without ever leaving the zone. If no, it's scattered islands.

The dots are 40 breeding experiments. Near the left (similar parents)
most children stay under the dashed "same plant" line; further right
the drift grows, though the far-right sample is thin. So: a connected
valley with soft walls, not scattered islands and not a flat plain
either. (An earlier run claimed the valley dramatically "pinches off"
at the edges; on the corrected population that does not reproduce, and
we have said so in the results document rather than quietly keeping
the prettier sentence.) It also means the crossover idea is a
meaningful tool here — for typical pairs.

## 5. The scoreboard

Eight hypotheses: four alive, two dead, one unproven, one sent back
for redesign. That is a healthy round. A round where everything survives is
a round where you tested nothing. Dead hypotheses here were cheap: seconds
of compute, no lab animals, no broken equipment. The scoreboard is the
project's honest state, and the survivors are the ones round two
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
   (44 per cent); the ladder is the truth.

None of the project's numbers changed because of these three. All of the
audit's own claims changed. But the audit also has a fourth chapter, and
this one is not funny. When Anadi Tripathi found the clock bug described in
section 2, it emerged that the audit's own reality check had evaluated
the fits on the same wrong clock as the fitter -- so it had verified,
beautifully and to fourteen decimal places, the arithmetic of a wrong
quantity. An independent code path that shares the assumption under
test is only half an audit. The audit now fits on elapsed time, asserts
every plant's start time against its treatment label, and prints ALL
CHECKS PASSED -- a claim that now includes a guard against the exact
bug it once missed. The lesson is not "the audit was bad", it is that
the second pair of eyes matters, that an audit must be audited too,
and that sometimes the second pair of eyes belongs to the person who
was told to just photograph the argument and send it over.

## Why seconds is not suspicious

The whole suite does about 44 million tiny arithmetic updates. A modern
laptop does a few billion of those per second. The matching hackathon felt
slow because its work was different: each day of each episode ran a
graph-matching algorithm over 200 people, and there were over a thousand
episodes under a 10-second-per-decision budget. Same computer class, a
thousand times more work. Speed is arithmetic, not cheating.

## Where the story goes next

The fake-plant side is nearly done. What remains is the bridge to real
plants: explain the ZT9 group's impossibly fast first hour (probably a
shorter lag than our model allows, possibly something the paper's
time-of-day gating does at that hour), add a second real dataset
(Arabidopsis curves, digitised from a 1993 paper), and make the
identification game harder so cleverness has something to bite on.
Then, and only then, does this start to look like a paper — see the
README for the paper question answered honestly.

Reading order for new readers: `EXPLAINER.md`, this file, then
`RESULTS_ROUND0.md` and `RESULTS_ROUND1.md` for the grown-up versions of
the same numbers.
