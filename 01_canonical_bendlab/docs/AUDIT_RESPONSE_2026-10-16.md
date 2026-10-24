# External audit response, 2026-10-16

An external AI audit of the repository was received on 2026-10-16. Each
claim was checked against the code and documents before any response was
written. This file records what was verified, what was fixed immediately,
and what remains open. BendLab is best described at present as a
promising model-identifiability study, not as evidence for a particular
biological mechanism or a validated experimental protocol.

## Fixed on 2026-10-16

1. **Model contract.** `PROBLEM_STATEMENT.md` gave k units of degrees
   per hour squared and wrote the rate cap around the stimulus term.
   The code (and therefore every reported result) uses k in degrees per
   hour and clips the bend rate after each lag update. The problem
   statement now writes the implemented discrete update exactly, states
   that sine arguments are converted to radians, and defines phi0 as an
   effective per-plant target angle rather than a measured lamp azimuth.
   `check_model_contract.py` adds regression checks for a cap-binding
   trajectory followed by a light reversal. All checks pass.
2. **Dependencies.** `requirements.txt` now requires NumPy >= 2.0 (the
   code uses `np.trapezoid`) and includes matplotlib and fpdf2.
3. **Public briefing.** `docs/PROJECT_BRIEFING.md` no longer names
   external researchers or reports outreach status, and the vector
   sample-size claims have been withdrawn there (see open item 4).
   `exp_design.py` carries the same caution in its docstring.
4. **Website wording.** The trained-model page now states explicitly
   that it must not be applied to real measured curves and that ensemble
   spread is not a calibrated confidence interval. The curve fitter page
   now describes its optimiser accurately (deterministic multi-start
   Nelder-Mead minimisation of squared error within bounds).

## Addressed in the follow-up (same day)

Full numbers: `docs/AUDIT_FOLLOWUP_RESULTS.md`; code:
`audit_followup.py`, `exp_design_model_selection.py`, corrected
`round1.py` and `phase_a.py`.

1. **H1 to H3 retested as written.** H1 supported (range criterion);
   H2 not supported (only k improves; direction inconsistent); H3
   supported under the written behavioural-distance criterion (20 of
   8,064 adjacent edges above 5x the median), superseding the earlier
   verdict. `docs/RESULTS_ROUND1.md` is amended.
2. **Weighted population max_rate sensitivity.** Twin existence is
   robust across point-estimate, lower-bound, independent-prior and
   no-cap treatments (30 to 37%); max_rate-specific degeneracy claims
   must use the lower-bound treatment.
3. **H6 and H8 implementations corrected and rerun.** H6 now holds
   phi0 fixed: same-cluster retention 60.7% versus 62.4% cross-cluster
   controls landing in either source class, so the connectivity claim
   is withdrawn. The H8 fixed policy now stops when the preferred
   protocol no longer fits the budget: fixed 83.4 versus random 89.4
   successes per 100.
4. **Vector model selection done properly.** Full datasets simulated
   under each mechanism, every candidate fitted per seedling, selection
   by total error: at 160 degrees / 2:1, correct selection is 84% at
   n = 10 and 96% at n = 20 (control geometry: chance). These numbers,
   with their stated procedure, replace the withdrawn Welch claims.
5. **Phase A recomputed on a matched 32.5 h horizon.** Headline values
   essentially unchanged (held-out median 11.75 degrees, coverage
   0.881; max_rate unidentified in 47 of 48).
6. **H7 at matched budget.** The best-to-worst gap shrinks from 0.092
   (full durations) to 0.021 at a common 6 h budget: the apparent
   protocol advantage is mostly observation time.
7. **Site and canonical status.** An About / Results / Data /
   Limitations page was added to the Pages site (About tab), and
   `docs/CURRENT_STATUS.md` is now the single canonical summary;
   `docs/PROJECT_BRIEFING.md` points to it.

## Remaining open (not possible at this stage)

- Wet-lab validation of any stimulus-model or protocol claim.
- Model v2 head-to-head (circadian clock versus biphasic memory kernel)
  and the H8 v2 harder design: specified in advance, not run in this
  pass.
- Applying the inverse models to real measured curves: fitted
  parameters often lie outside the synthetic training ranges, so this
  needs wider-range training with uncertainty quantification.

## Defensible current summary

Under the specified phenomenological model, different parameter
combinations can produce similar trajectories, and a bend-rate cap
cannot be inferred when it never binds. The model fits most of the 48
published sunflower curves in-sample (median RMSE 1.80 degrees), with a
systematic limitation in some ZT9 curves. The shared circadian-clock
term is a candidate extension supported by a held-out-block test, not a
blind forecast. The multi-source stimulus and neural-inverse results are
simulator-based until tested against measured data.
