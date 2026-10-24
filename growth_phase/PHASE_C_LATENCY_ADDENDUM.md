# Phase C latency endpoint: post-audit analysis addendum

Date: 2026-10-24. Status: POST-AUDIT. This addendum fixes the analysis
definition for the latency endpoint BEFORE the reanalysis script
(`phase_c_latency_cox.py`) is run. It does not amend the original
pre-registration (`PHASE_B_PREREGISTRATION.md`, unchanged), and it
cannot retroactively make the reanalysis pre-registered: the external
auditor's exploratory Cox results are already known to us. What this
addendum does is prevent further analytic discretion in the reanalysis
itself: population, endpoint, model, and decision rule are all fixed
below, in advance of running it.

## Why the original latency number cannot stand

The original Phase C latency outcome (coefficient per log L0
-0.75 h, 95% CI [-2.02, 0.38], ordinary regression) was constructed
in `phase_c_historical.py` as follows:

- plants that never reach 10 deg (5 plants) were assigned a latency
  of exactly 22 h, i.e. right-censoring was treated as an exact
  event time at the end of follow-up;
- plants already at or above 10 deg at baseline were coded as
  latency 0, i.e. as instantaneous events, although they were never
  at risk of a first crossing during follow-up.

Both codings bias an ordinary regression in directions that are not
knowable without a censoring-aware analysis, so the original
statement "no latency signal" is method-dependent. The original
estimate is retained in the Phase C record for provenance but is
superseded, as an interpretation, by the reanalysis defined here.

## Fixed definitions for the reanalysis

At-risk population (primary): paired plants whose initial angle is
below the threshold, theta(0) < 10 deg. Plants at or above 10 deg at
baseline cannot experience a first crossing of 10 deg and are
excluded from the primary analysis.

Endpoint (primary): time from start of recording to the first
observed angle at or above 10 deg. Plants that never reach 10 deg
are right-censored at their last observed time. Crossing times are
known only to the sampling grid (about 4 min); the first sampled
crossing time is used as the event time and this discretisation is
stated as a limitation (a fully interval-censored model is a possible
refinement, not part of this reanalysis).

Primary model: Cox proportional hazards,
event time regressed on log L0 (the term of interest), log light
intensity, and initial angle theta(0), with Efron handling of ties.
Reported: hazard ratio for log L0 per log unit with 95% Wald CI,
the corresponding p value, the numbers at risk / events / censored,
and a proportional-hazards check (Schoenfeld residuals).

Pre-declared sensitivities (not decision-bearing):

1. the same at-risk Cox model without the theta(0) covariate, and
   with log L0 alone, to show covariate sensitivity;
2. a revised endpoint on all 213 plants: time to an increase of at
   least 10 deg above each plant's own starting angle
   (theta >= theta(0) + 10), censored at last observation. This
   endpoint puts every plant at risk but answers a different
   question; it is reported as exploratory only.

## Decision rule for revisiting the M1c inclusion decision

The pre-registration included M1c in the primary Phase C prediction
comparison "only if latency signal appears".

- If the primary Cox analysis detects an L0 latency association
  (95% CI for the log L0 hazard ratio excludes 1, without a gross
  proportional-hazards violation), then the corrected analysis would
  have met the inclusion condition, and the v3 report must present
  the M1c result alongside M1a/M1d, while keeping its post-audit
  provenance label. The primary Phase C record is still not rewritten.
- If the primary Cox analysis does not detect an L0 latency
  association (CI includes 1), the original exclusion of M1c from
  the primary comparison stands under the corrected analysis as
  well, and M1c remains a labelled sensitivity.

Either way, no mechanism claim follows from a latency association
alone, and the M1c predictive result (already computed as a
sensitivity) is reported regardless of the decision.
