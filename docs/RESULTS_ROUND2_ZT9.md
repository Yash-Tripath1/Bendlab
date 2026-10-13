# ZT9 autopsy — 13 October 2026

After the clock correction (`RESULTS_ROUND0.md`, bug log), one anomaly
survived: four of the six ZT9 plants fit with `tau` pinned at its lower
bound (0.05 h), and ZT9-1 is the worst fit in the dataset (RMSE
6.76 deg). This autopsy (`zt9_autopsy.py`, dashboard
`results/figures/zt9_autopsy_dashboard.png`) asked three questions,
with verdict rules declared in the script before it ran.

## A. Where does the fit miss? — a systematic shape, not noise

Mean residuals (measured − fitted) by elapsed segment:

| Plant | 0–1 h | 1–4 h | 4–8 h | 8–16 h | 16 h–end |
|---|---|---|---|---|---|
| ZT9-1 | +0.45 | +10.93 | +11.49 | −4.34 | −0.08 |
| ZT9-2 | −1.33 | +1.57 | +9.78 | −2.04 | −0.34 |
| ZT9-3 | −1.48 | +0.20 | +4.25 | −1.25 | −0.04 |
| ZT9-4 | −0.46 | +1.76 | +2.60 | −0.26 | −0.25 |
| ZT9-5 | −0.53 | −1.03 | +0.74 | +0.61 | −0.30 |
| ZT9-6 | −0.87 | −0.82 | −1.88 | +1.29 | −0.22 |

Five of six plants sit *above* their fitted curve through the 4–8 h
window and the misfit is largest exactly in the bound-pinned plants.
The measured curves rise faster in mid-course than the model allows,
then stall (ZT9-1's smoothed bend rate goes negative, −2.9 deg/h)
while the model catches up. That is a two-phase rate profile: fast
rise, pause, second rise. A single first-order lag produces one
smooth rise and cannot make that shape at any parameter values.

## B. Is the tau floor the problem? — No (declared test)

Refitting all six ZT9 plants with the `tau` lower bound at 0.05,
0.01 and 0.001 h, everything else identical:

| tau floor | median RMSE | worst RMSE |
|---|---|---|
| 0.05 h (current) | 2.420 | 6.759 |
| 0.01 h | 2.401 | 6.729 |
| 0.001 h | 2.400 | 6.728 |

Median improvement 0.8%, far under the declared 10% "not the driver"
line. The freed fits choose tau ≈ 0.008 h (about 30 seconds —
effectively instant sensing) and the shape error survives intact.
**Verdict: the lower bound is a symptom, not the cause.** The
optimizer was pushing tau down to approximate the fast mid-rise; the
wall stopped the dial, not the misfit. The pin stays a valid reason
to exclude these four plants from the weighted population, and the
reason is now understood rather than merely flagged.

## C. Do stalls line up with the circadian clock? — Inconclusive

A genuine stall was defined as a 2.5 h-smoothed rate minimum in
elapsed 3–20 h followed by re-acceleration ≥ 1 deg/h within 8 h (a
first pass without this rule and a common window was discarded — it
mostly detected end-of-observation slowdown). 42 of 48 curves stall
by this definition, so stalling is generic, not a ZT9 peculiarity.
Block-median stall times are tighter in elapsed time (IQR 3.31 h)
than in circadian phase (IQR 7.31 h), and the six ZT9 stalls split
between evening phases (17.75–19.75) and post-midnight phases
(0.75–3.25). **No single dusk trigger; reported as inconclusive,
not as evidence either way.**

## Bottom line

ZT9 is a genuine model limitation, localised and understood: the
two-state model cannot produce a fast-rise–stall–rise rate profile.
Candidate mechanisms (a circadian gate on gain, autostraightening
superimposed on phototropism) are named here as speculation, not
results; testing them needs a model extension declared in advance,
or the Arabidopsis mean-curvature curves in `DATA_SOURCES.md` as an
independent shape check. ZT9 remains excluded from the weighted
population (2 of 6 plants), now with the reason on record.
