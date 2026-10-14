# Results III: diagnostic analysis of the ZT9 model limitation

**Date:** 13 October 2026  
**Source:** `zt9_diagnostics.py`  
**Summary figure:** `results/figures/zt9_diagnostic_dashboard.png`

Following correction of the time-base error (`docs/RESULTS_ROUND0.md`,
Section 8), one systematic model limitation remained. Four of the six
ZT9 plants were fitted with the sensing lag `tau` at its lower bound
(0.05 h), and ZT9-1 had the largest fit error in the dataset (RMSE
6.76 degrees). Three analyses were specified in `zt9_diagnostics.py`
before the results were examined: (A) the temporal distribution of
residuals, (B) sensitivity of the fits to the lower bound on `tau`, and
(C) the timing of reductions in bend rate relative to elapsed and
circadian time.

## A. Residual structure

Mean residuals (measured − fitted angle, degrees) by elapsed-time
segment were:

| Plant | 0–1 h | 1–4 h | 4–8 h | 8–16 h | 16 h–end |
|---|---:|---:|---:|---:|---:|
| ZT9-1 | +0.45 | +10.93 | +11.49 | −4.34 | −0.08 |
| ZT9-2 | −1.33 | +1.57 | +9.78 | −2.04 | −0.34 |
| ZT9-3 | −1.48 | +0.20 | +4.25 | −1.25 | −0.04 |
| ZT9-4 | −0.46 | +1.76 | +2.60 | −0.26 | −0.25 |
| ZT9-5 | −0.53 | −1.03 | +0.74 | +0.61 | −0.30 |
| ZT9-6 | −0.87 | −0.82 | −1.88 | +1.29 | −0.22 |

In five of the six plants, the measured angle exceeded the fitted angle
during the 4–8 h interval; the discrepancy was largest in the plants whose
fitted `tau` reached its lower bound. The measured trajectories therefore
rise more rapidly in mid-course than the model permits, then slow while
the fitted trajectory continues to increase (for ZT9-1, the 2.5 h
smoothed bend rate reached −2.9 degrees h⁻¹). The measured response is
thus characterised by a two-phase rate profile—rapid rise, marked
reduction in bend rate, and a second rise—which a model containing a
single first-order lag cannot reproduce at any parameter values.

**Conclusion A.** The ZT9 misfit is systematic in time and is attributable
to the trajectory shape representable by the model, rather than to
unstructured measurement noise.

## B. Sensitivity to the lower bound on tau

All six ZT9 plants were refitted with the `tau` lower bound set to 0.05,
0.01 and 0.001 h, with all other fitting settings unchanged.

| `tau` lower bound | Median RMSE | Maximum RMSE |
|---|---:|---:|
| 0.05 h (standard) | 2.420 | 6.759 |
| 0.01 h | 2.401 | 6.729 |
| 0.001 h | 2.400 | 6.728 |

Reducing the lower bound by a factor of 50 decreased median RMSE by
0.8 per cent, below the pre-specified 10 per cent criterion for concluding
that the bound was not the principal source of error. With the lowest
bound, the fitted values of `tau` were approximately 0.008 h
(approximately 30 s), but the segment-residual pattern persisted.

**Conclusion B.** The lower bound on `tau` is a consequence of the shape
misfit rather than its cause. During fitting, `tau` is driven downward in
an attempt to reproduce the rapid mid-course rise; the bound limits that
parameter movement without removing the structural error. The four
boundary solutions remain excluded from the weighted population, now with
the basis for exclusion established.

## C. Timing of reductions in bend rate

A trajectory was classified as stalled if its 2.5 h smoothed bend rate
reached a minimum within elapsed 3–20 h and subsequently increased by at
least 1 degree h⁻¹ within 8 h. An earlier definition without the
re-acceleration requirement and the common observation window was
discarded because it principally detected the reduction in bend rate near
the end of the recording.

Forty-two of the 48 measured trajectories satisfied the stall criterion;
the pattern is therefore not specific to ZT9. Block-median stall times
were less dispersed in elapsed time (IQR 3.31 h) than in circadian phase,
expressed as absolute ZT modulo 24 (IQR 7.31 h). The six ZT9 stall phases
were divided between the evening (17.75–19.75) and the period after
midnight (0.75–3.25).

**Conclusion C.** The analysis does not identify a single circadian phase
at which reductions in bend rate occur and is reported as inconclusive.

## Overall conclusion

The ZT9 result is a localised structural limitation of the two-state
model: the model cannot generate the observed rapid-rise, reduced-rate,
second-rise profile. Candidate extensions—circadian modulation of
response gain and an autostraightening term superimposed on the
phototropic response—are hypotheses for subsequent work, not conclusions
of this analysis. They require a model extension and falsification
criteria specified in advance. The population-mean Arabidopsis curvature
curves identified in `docs/DATA_SOURCES.md` provide a possible external
check on whether the same trajectory shape occurs outside this dataset.

ZT9 remains under-represented in the weighted population (two of six
plants), with the reason for exclusion documented here.
