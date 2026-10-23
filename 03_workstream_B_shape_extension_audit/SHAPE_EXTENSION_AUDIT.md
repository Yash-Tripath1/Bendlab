# Phase B0 — Workstream B: audit of the shape-extension submission

**Scope of this audit.** Independent check of the `shape-extension`
branch of umaidsiddiqui10/Bendlab at commit
`494687940c3490d1af6e4ac36abf4a4a59adc7e5` (branch tip verified
2026-10-18; it has not moved from the submitted snapshot). This
workstream is independent of the Kempinski benchmark (Workstream A):
nothing here uses real-plant data, and nothing in Workstream A is
evidence for or against this extension. The branch was cloned to an
isolated directory; the submitted code and results were not modified.
Corrected reruns are versioned separately in
`workstream_b/shape_audit_corrected_v1.py`.

**Canonical BendLab state.** Upstream main is still at
`b09ea5aa6003082b41d726b2b8499ded313dcb21` (2026-10-16), unchanged from
the previous audit. Its model interface is `sim.py`: `simulate(k, tau,
max_rate, phi_fn, t_end, dt)` and `batch_simulate(...)` implementing
`tau dr/dt = k sin(phi - theta) - r`, cap applied after the lag update,
`theta` from vertical in degrees. There is no light-intensity input
anywhere in the model; `phi0` is a per-plant effective light angle in
the population generators. Measured-data interface remains the Brooks
S13 tip angles via `fit_real.py` / `data_real.py`.

## Claim-by-claim audit

### 1. "v3 twin refinement is SUPPORTED: k +49.2%, phi0 +45.9% error reduction"

- **Evidence checked.** Ran `python check_multiseg.py`: ALL CHECKS
  PASSED (exact reduction to `sim.py` at zeta=0, batch/single agreement
  ~7e-15, determinism, cap contract). Ran
  `python shape_identification_v3.py` independently (31 s): every
  headline value reproduces the submitted
  `results/shape_identification_v3_summary.json` exactly (residual
  differences ~1e-13, floating-point noise). Submitted and rerun
  summaries are both preserved under `workstream_b/`.
- **Verdict.** Reproducible as a simulation result, with the narrowing
  in items 3–5 below.

### 2. `features_shape.py`: `s_shape_sign_changes` does not do what its documentation says

- **Evidence checked.** The docstring defines the feature as the
  "number of sign changes in kappa_j along the stem" (across
  neighbouring joints, per time). The code builds `signs` with shape
  (T, N, J) and computes `signs[1:] * signs[:-1]`, which slices axis 0:
  it compares the SAME joint at consecutive TIME points. Unit checks
  (in `tests_phase_b0.py`): a synthetic constant S-bend (curvature
  +10, −5, +10, +15 deg) scores 2.0 under the corrected definition and
  0.0 under the submitted one; a pure temporal sign flip of one joint
  scores 0.0 corrected and >0 submitted. The submitted feature measures
  temporal curvature sign flips, not S-shapedness.
- **Effect on the reported results: none, verifiably.** In the v1, v2
  and v3 populations the feature is identically zero under BOTH
  definitions (checked in the submitted v1/v2 feature files and in our
  rerun): under static light this chain only ever produces single-signed
  curvature, so there are no S-bends to count and no temporal flips
  either. A versioned corrected rerun
  (`workstream_b/shape_audit_corrected_v1.py`, corrected feature =
  sign changes across joints) reproduces the v3 primary result to the
  digit: k +49.2%, phi0 +45.9%, tau −6.4%, max_rate +1.1%.
- **Recommended action.** Fix the implementation (or the docstring) in
  the branch before any regime in which curvature can change sign over
  time or along the stem is studied; there the two definitions diverge
  and the current code would silently report the wrong observable. Do
  not overwrite the submitted v3 outputs: they are unaffected, and the
  corrected rerun is already versioned separately.

### 3. "Curve twins": neighbours are chosen by six tip summary features, not the full trajectory

- **Evidence checked.** v3 selects each plant's 20 neighbours in the
  6-feature tip space of `features.py` (half-rise time, peak/final
  angle, overshoot, peak rate, AUROC), standardised on the same
  population that is then evaluated (self-matching; each plant is its
  own pool-mate, excluded only as its own nearest neighbour). We
  quantified what those "twins" look like as full trajectories (49
  records, 0.5 h spacing): the plain tip nearest neighbour has median
  full-trajectory RMSE **0.13 deg** from the query plant (75th pct
  0.28 deg); the shape-refined pick **0.23 deg** (median max deviation
  0.40 deg). So in this noiseless simulated population the summary
  features really do pick near-identical full curves; the claim is not
  an artefact of the summary space.
- **Narrowing required.** The claim should read "among plants whose tip
  trajectories are near-identical (median 0.13 deg RMSE in-silico)…",
  and it is established only for noiseless simulations. With realistic
  measurement noise, six summary features will select noisier twins.
- **Reference/query split (recommended test, run here).** Repeating the
  protocol with scalers and the neighbour pool fitted on a random half
  of the population and queries drawn from the other half (seed 7):
  k +46.8%, phi0 +44.1%, tau +0.7%, max_rate +1.1% (submitted feature);
  identical with the corrected feature. The primary result is not a
  self-matching artefact.

### 4. phi0 is doing double duty; report k / tau / max_rate separately

- **Evidence checked.** In all shape studies, `phi0` is sampled
  independently per simulated plant, Uniform[5, 85] deg
  (`generate_plants.py`), i.e. each simulated plant is given its own
  randomised light direction. BendLab's own problem statement describes
  fitted phi0 as an *effective* angle that "may absorb lamp geometry and
  initial-orientation offsets" and should not be read as a measured lamp
  azimuth.
- **Issue.** Under a standardised fixed-light assay the lamp direction
  is a known, shared experimental input (e.g. 90 deg for horizontal side
  light), not a plant property. Recovering a randomised experimental
  condition from shape data (phi0 +45.9%) is a statement about the
  decoder, not about identifying a physiological parameter of a plant.
  The pre-registered criterion (≥25% reduction for ≥2 of the four
  original parameters) is met only because phi0 counts as one of the
  two qualifiers.
- **Primary results restated without phi0** (from the submitted v3
  numbers): **k +49.2%** (qualifies), **tau −6.4%** (does not),
  **max_rate +1.1%** (does not; consistent with the exact non-binding-cap
  degeneracy). Only 1 of 3 physiological parameters qualifies.
- **Direct test (run here).** Repeating the primary protocol with phi0
  fixed at 60 deg for every plant (known shared input; same seeds and
  other parameters): k +33.4%, tau +13.1%, max_rate −0.8%. Shape
  refinement still helps k materially, but the margin is smaller,
  because much of the tip-space degeneracy in the submitted design was
  manufactured by randomising phi0. (With phi0 fixed, the plain tip
  twin is already far better: k tip-NN error 1.85% of range vs 11.86%.)
- **Recommended action.** In future reports: (i) headline k, tau,
  max_rate; (ii) report phi0 recovery separately and labelled as
  recovery of an imposed light-direction offset; (iii) pre-register any
  criterion on the physiological parameters only.

### 5. Model assumptions and limits

- Five rigid segments (four joints), planar angles only; coupling
  `c ~ U[0,1]` /h and sensitivity gradient `zeta ~ U[0,1]` are imposed
  ranges with no measured counterpart; initial state is a perfectly
  vertical, motionless stem for every plant; observations are noiseless
  and densely sampled (0.5 h records of exact segment angles, which no
  current dataset provides). The shape "observable" is the model's own
  segment angles, not image-derived centerlines: no stem tracing, no
  occlusion, no circumnutation, no growth.
- The extension also omits gravity and any autostraightening term, the
  same limitations as the scalar model; zeta (tip-weighted sensitivity)
  is a modelling choice, not a measured sunflower profile.
- **Primary vs secondary.** The pre-registered primary result is the
  twin-refinement table. The ExtraTrees/NN decoder numbers (e.g.
  combined-arm R² tau 0.76) are secondary outputs "reported, no
  verdict" by the protocol itself; they show information is present in
  the candidate features, but a flexible decoder trained and evaluated
  inside the same simulated population is weaker evidence than the
  primary protocol and should not be headlined as identification
  accuracy for real plants.
- **Correct characterisation.** This is a model-conditioned simulation
  result: *within this five-segment model class*, noiseless shape
  observables carry parameter information that the tip trajectory
  discards, most cleanly for k. It is not evidence that real sunflower
  stems bend with this curvature profile, and it does not solve
  real-plant degeneracy (real shape data do not yet exist in the
  project; cf. the Phase B research plan).

### 6. Pre-registration timing: what public history can and cannot verify

- Git history (all 2026-10-18): `9cf7fb0` 10:04 UTC adds the simulator,
  v1/v2 code, the design document and the results document (including
  the section-4 "pre-registration" of v2 and the v2 results) in ONE
  commit. `6d56df0` 10:16 UTC adds the exploratory probe, the v3 script,
  and results-document sections 7 (exploration), 8 (v3
  "pre-registration") and 9 (v3 results) in ONE commit. `4946879`
  10:26 UTC adds the research note.
- **Conclusion.** The public history verifies that documents, code and
  results are mutually consistent and that the stated protocol in
  section 8 matches the script that reproduces section 9 exactly. It
  does **not** independently verify that any protocol was fixed before
  its run: each "pre-registration" first becomes public in the same
  commit as the code and results it governs, minutes apart. This is a
  provenance limitation, not an accusation: the internal ordering may
  well have been as described, but a sceptical reader cannot check it.
- **Recommended action.** For the next study, push the pre-registration
  document as its own commit (ideally timestamped by the hosting
  platform) before the run commit exists. One commit of discipline
  converts this from assertion to evidence.

### 7. Moving-light follow-up

Not pursued, per Phase B0 scope. (Noted only because the note
recommends it; nothing here evaluates it.)

## Bottom line (Workstream B)

Reproducible, honestly reported simulation study with one inert code
bug (item 2), one claim that needs narrowing (item 3), and one
accounting issue that changes how the headline should be read: with
phi0 treated as the known assay input it is, shape refinement improves
identification of **k** (and of the shape-making parameters c and zeta),
does not help tau under the primary protocol, and cannot help max_rate
under static light. The v3 "SUPPORTED" verdict stands only for the
four-parameter accounting that counts phi0. Pre-registration timing is
not independently verifiable from public history. None of this is
evidence about real sunflower stems; that requires image-derived
centerlines the project does not yet have.
