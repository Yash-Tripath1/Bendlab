# BendLab: current status (canonical)

This is the single canonical summary of what BendLab has established,
what it has withdrawn, and what remains open across Experiment Series 1,
Phase B0, and the Growth-Aware Phototropism study (Phases A–C). Where
older documents differ, this file and the dated amendments in them take
precedence.

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
- **External benchmark on 268 unilateral trajectories (Phase B0
  Workstream A, Kempinski et al. 2026, 0.7–5.8 W/m²):** fixing
  `phi = 90` degrees to physical horizontal lamp geometry with an
  intensity-gain wrapper (`W1`, `k(I) = a * I^b`) fails to beat simple
  empirical baselines (plant-held-out median RMSE 14.41 degrees vs 9.73
  degrees intensity-group mean curve `B1` and 10.92 degrees saturating
  exponential `B2`; LOIO median RMSE 10.4–16.5 degrees across
  intensities). Because measured stems settle into late-window plateaus
  around 18–37 degrees (per-plant `phi_free` median 28.8 degrees) rather
  than 90 degrees, `phi0` in the canonical scalar model functions as an
  empirical equilibrium angle: allowing an intensity-dependent effective
  angle (`W2` diagnostic, `phi_eff(I)`) lowers plant-held-out median
  RMSE to 9.97 degrees.
- **Multi-segment stem shape narrows `k` degeneracy but leaves
  `max_rate` blind (Phase B0 Workstream B):** the 5-segment coupled
  chain (`04_shape_extension_branch/sim_multiseg.py`) reduces to
  `sim.py` exactly at `zeta = 0`. Refining tip-matched twins using stem
  curvature cuts `k` error by 46.8% under a leakage-safe reference/query
  split (`phi0` varying; 49.2% in-population) and by 33.4–36.7% when
  `phi0` is fixed at 60 or 90 degrees, while `max_rate` error changes by
  at most ~1.1%.
- **Growth-aware phototropism audit (`growth_phase/`, n = 213 paired
  seedlings with starting length `L0`):** `L0` is positively associated
  with early 0–2 h bending rate (+2.12 deg/h per log-length unit, 95% CI
  [0.66, 3.62], controlling log intensity and initial angle), whereas
  censoring-aware Cox latency analysis on the 190 at-risk plants shows
  no statistically significant onset-hazard effect (HR = 1.42 per log
  unit, 95% CI [0.97, 2.06], p = 0.068). Length-coupled ODE variants
  (M1a gain `k(L0)`, M1c transport lag `tau(L0)`, M1d opposing
  `gamma(L0)`) do not improve held-out trajectory RMSE over length-blind
  M0 (10.25 degrees; all within 1.5 per cent: M1a 10.41, M1d 10.35, M1c
  10.29 degrees).

## Withdrawn or corrected, on the record

- All pre-13-October fit values (clock-offset error in the fitter).
- The original H4 interpretation, the H3 "falsified" verdict, the H6
  connectivity claim, and the Welch-based vector sample sizes.
- The `s_shape_sign_changes` axis-indexing bug in Workstream B (which
  sliced time rather than joints, though both definitions are
  identically zero under static light; audited in
  `03_workstream_B_shape_extension_audit/SHAPE_EXTENSION_AUDIT.md`) and
  the original uncensored Phase C latency regression in `growth_phase`
  (superseded by censoring-aware Cox analysis).

## Open

- Wet-lab validation of any stimulus or protocol claim.
- Mechanistic straightening/equilibrium formulation (`sim_gamma.py` /
  `sim_clock_gamma.py`) benchmarked directly on the multi-intensity
  external dataset so `phi_light = 90` degrees remains physical lamp
  geometry while `gamma` sets the equilibrium angle.
- Model v2 head-to-head: circadian clock versus biphasic memory kernel
  on held-out data (specified, not run).
- H8 v2 harder adaptive design (specified, not run).
- Inverse models on real curves: fitted sunflower parameters often lie
  outside the synthetic training ranges, so this needs wider-range
  training with uncertainty quantification.

Key sources: `docs/RESULTS_ROUND0.md`, `docs/RESULTS_ROUND1.md`,
`docs/AUDIT_FOLLOWUP_RESULTS.md`, `docs/MODEL_V2_CANDIDATES.md`,
`02_workstream_A_external_benchmark/PHASE_B0_REPORT.md`,
`03_workstream_B_shape_extension_audit/SHAPE_EXTENSION_AUDIT.md`,
`growth_phase/PHASE_BC_RESULTS.md`, `results/phaseA_summary.json`.
