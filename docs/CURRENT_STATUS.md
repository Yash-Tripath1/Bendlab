# BendLab: current status (canonical)

This is the single canonical summary of what BendLab has established,
what it has withdrawn, and what remains open, as of 16 October 2026.
Where older documents differ, this file and the dated amendments in
them take precedence.

## The question

Can different internal parameters of a sunflower seedling produce
nearly identical bending behaviour, and which parameters can a bending
curve actually reveal? BendLab is a model-identifiability study built
on a four-parameter phenomenological model (sensitivity k, lag tau,
bend-rate cap max_rate, effective light angle phi0). It is not, at
present, evidence for a particular biological mechanism.

## Established (with evidence graded)

- **Behavioural degeneracy is real in the model.** Different parameter
  combinations produce nearly indistinguishable trajectories (H1,
  supported as written; nearest-neighbour, clustering, and twin
  analyses agree, and twin existence is robust to how the unidentifiable
  max_rate is treated in population resampling).
- **max_rate is the blind dial.** When the bend-rate cap never binds, a
  curve carries almost no information about it: per-fit uncertainties
  flag it in 47 of 48 measured plants, a 400,000-plant sweep and a
  trained neural network (median error about 44% while other parameters
  sit at 1 to 4%) independently agree.
- **The model fits most published curves in-sample** (48 sunflower
  trajectories, median RMSE 1.80 degrees, 44 of 48 fits not
  bound-pinned), but predicting a held-out block is much weaker
  (leave-one-block-out median 11.75 degrees). In-sample fit is not
  generalisation.
- **ZT9 curves are a systematic failure** of the base model. A shared
  circadian-clock term fitted without ZT9 improves all six held-out ZT9
  plants (median 2.42 to 1.44 degrees). This is a candidate extension
  supported by a held-out-block test, not a confirmed mechanism.
- **Hypotheses as written** (retested 2026-10-16): H1 supported; H2 not
  supported (only k improves with a light-direction change); H3
  supported under the written behavioural-distance criterion (rare
  cliff edges exist); H4 supported (behavioural clusters do not persist
  across light regimes, ARI 0.442); H5 supported in-sample; H6 only weak
  local retention (connectivity claim withdrawn); H7 not supported at
  matched observation budget; H8 adaptive policies do not beat random in
  the corrected v1 design.
- **A concrete experiment is designable.** Under a stated
  model-selection procedure, 20 seedlings per dataset at a 160-degree,
  2:1 two-source geometry select the correct stimulus mechanism in
  about 96% of simulated datasets (control geometry: chance). This is a
  simulation-based estimate, not a laboratory guarantee.

## Withdrawn or corrected, on the record

- All pre-13-October fit values (clock-offset error in the fitter).
- The original H4 interpretation, the H3 "falsified" verdict, the H6
  connectivity claim, and the Welch-based vector sample sizes.

## Open

- Wet-lab validation of any stimulus or protocol claim.
- Model v2 head-to-head: circadian clock versus biphasic memory kernel
  on held-out data (specified, not run).
- H8 v2 harder adaptive design (specified, not run).
- Inverse models on real curves: fitted sunflower parameters often lie
  outside the synthetic training ranges, so this needs wider-range
  training with uncertainty quantification.

Key sources: `docs/RESULTS_ROUND0.md`, `docs/RESULTS_ROUND1.md`,
`docs/AUDIT_FOLLOWUP_RESULTS.md`, `docs/MODEL_V2_CANDIDATES.md`,
`results/phaseA_summary.json`.
