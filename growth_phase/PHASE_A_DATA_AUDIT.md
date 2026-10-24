# Growth-aware phototropism, Phase A: paired length/trajectory audit

Data auditing only; no response outcome was fitted in this phase.
Source: Kempinski et al. (2026) archive, Zenodo record 21206480
(md5 `06d911cc56c6cf92d66af15304bb93f9`). Script: `phase_a_join.py`;
outputs: `outputs/paired_plants.csv`, `outputs/phase_a_audit.json`.

## What the archive actually contains (verified, not assumed)

- `00_Data/uni_trajectories.csv`: 268 unilateral plants, tip angle
  (deg), 0 to 22 h, about 4-minute sampling.
- `07_Supplementary/length_est_data.csv`: 246 rows, 245 unique
  `real_id`s, with `length_start`, `length_finish` (mm, per the
  archive's `length_est.py`, which computes growth speed as
  (finish − start)/dt in mm/h), an interval `dt`, and `light_intens`.
- **213 of the 268 unilateral plants have a length record.**
  `light_intens / 100` equals the trajectory `light_i` for all 213:
  the join is exact, not approximate.
- 32 length IDs are not in the unilateral set (they belong to the
  bilateral experiments; their `light_intens` values include 720 and
  1200, outside the unilateral range). Excluded from this phase.
- 55 unilateral plants (20.5%) have no length record. Length-record
  COVERAGE by intensity ranges 0.68 to 1.00, so MISSINGNESS by
  intensity is 0.00 to 0.32 (highest, 0.32, at 4.4 W/m² and 0.318 at
  3.2 W/m²; full table in `outputs/phase_a_audit.json`). Coverage by
  side is L 0.815 vs R 0.775 (missingness 0.185 vs 0.225). No extreme
  pattern, but the analysis set is a subset and is treated as such.

## Issues found and how they were resolved

1. **Duplicate record:** `11_11_L_5` appears twice with identical
   values (only the row index differs). It is an exact copy, so
   deduplication loses no information. Resolved by deduplication,
   documented here rather than silently.
2. **Window mismatch:** the length interval `dt` is typically about
   0.87 h LONGER than the angle trajectory (median; range 0 to 3.93 h;
   183 of 213 plants). Net growth is therefore an interval-average over
   its own, slightly longer window. Consequence, pre-registered:
   `length_start` is the primary length variable (L0, median 14.1 mm,
   range 4.9 to 40.9 mm); net growth is used only as an interval-average
   covariate, never as a time-resolved growth trajectory. Whether
   `length_start` was measured exactly at trajectory t = 0 cannot be
   verified from the archive files alone and is flagged as an
   assumption, consistent with the supplementary script's design.
3. **Units verified from source code,** not from column names:
   mm and mm/h per `length_est.py`.

## What this paired set can and cannot support

Can: association of L0 with tip-angle dynamics (latency, rate,
late-window plateau) controlling for intensity and initial angle;
association of interval-average elongation with overall angular change;
plant-held-out comparison of the pre-registered M0 vs M1 variants.

Cannot: local/time-resolved growth mechanisms, growth-zone location,
curvature kappa(s,t), ZT effects, or post-stimulus autostraightening.
None of those variables exist in this archive. Brooks data have no
per-plant length and are excluded from length analyses.

**Gate 1 (data): passed with the caveats above.** The merge is frozen
in `outputs/paired_plants.csv` (one row per unilateral plant, 213 with
lengths, `has_length` flag retained so the 55 unmatched plants stay
visible in sensitivity analyses).
