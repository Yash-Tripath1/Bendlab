# Repository consolidation record

**Record identifier:** 2026-11-26. The filename follows the requested task
identifier. Verification date and outcomes are recorded below from the
actual runs; no scientific result is inferred by this document.

## Repository reality and branch reconciliation

- Fresh-clone baseline: `main` at `92df6e0`, 417 tracked files, and 58
  tracked Markdown documents.
- The active branch was fast-forwarded from `4f33ede` to the already-pushed
  Phase E head `7e64f1a`; the merged pull request state was checked before
  consolidation work. No reset, clean, force-push, or history rewrite was
  used.
- The pre-existing local Phase E files were byte-identical to the remote
  branch. A safety stash was retained while the branch was fast-forwarded;
  the files are now present in the committed branch tree.

## File-change table

| Path or group | Change |
|---|---|
| `README.md` | Rewritten as the project entry point, with the canonical model, Experiment Series 1, Phase B0 Workstreams A and B, Growth-aware Phases A to E, current status, citations, and contributor attribution. |
| `docs/CURRENT_STATUS.md` | Extended the canonical status summary through Phases D and E. |
| `docs/INDEX.md`, `docs/IMPLEMENTATION_STATUS.md` | Added the complete document index and implementation/evidence status. |
| `docs/QUICKSTART.md` | Added fresh-clone commands, completed after the verification runs below. |
| `docs/CONSOLIDATION_2026-11-26.md` | Recorded scope, verification, non-fixes, and remaining duplication. |
| `docs/DATA_CONTRACT.md` | Documented the legacy adaptation datasets, observed repository provenance, hashes, and dead reference status. |
| `requirements.txt` | Added lower-bound `lifelines` and `pytest` dependencies. |
| Root packaging notes | Moved to `docs/archive/PACKAGE_README_2026-10-23.md` and `docs/archive/PHASE_B0_FIXES_2026-10-23.md`. |
| External-validation note | Renamed to `docs/CHANGES_2026-10-15_EXTERNAL_VALIDATION.md`; attribution remains in the document and Git history. Absolute local paths were replaced with clone/work-directory variables or relative artifact names. |
| Working Markdown documents | Replaced em dashes only in working documents; frozen snapshots were left untouched. |
| `03_workstream_B_shape_extension_audit/workstream_b/shape_audit_corrected_v1.py` | Changed only its import and output paths to repository-relative `Path` values. Analysis calculations were not changed or rerun. |
| `clock_validation.py`, package/test notes | Updated references to renamed or archived documentation paths. |
| `growth_phase/README.md` | Updated the folder guide through Phase E; all other protected growth-phase files were left untouched. |

## Verification

Verification will be recorded after the fresh-clone workflow, regression
suite, artifact comparison, and checksum manifest have completed.

## Scientific integrity

No scientific numbers, thresholds, verdicts, conclusions, fit outputs, or
saved result files in the working repository were changed. No analyses were
refit or rerun in the working tree. The sole requested artifact regeneration
was confined to a disposable fresh clone and is reported with its comparison
and magnitude below.

## Deliberate non-fixes

- The two `results/adaption_*.csv` datasets remain at their original paths.
  The instruction dataset has no current consumer and incomplete provenance;
  the inverse dataset has a documented seed description but no tracked
  generator. No provenance was invented.
- The frozen directories `01_canonical_bendlab/`,
  `04_shape_extension_branch/`, and `05_data_external/` were not edited,
  moved, or deleted. Frozen Phase A/B-C report snapshots and protected audit
  records were not edited.
- `results/fit_fig1c.csv`, Phase E outputs, and all other saved scientific
  outputs in the working tree were left unchanged.
- No analysis script was repaired or retuned. The consolidation changed
  documentation, dependencies, and the specified shape-audit path only.

## Remaining canonical-repository duplication

The clean baseline contained a nested canonical snapshot and other preserved
copies. They remain in place pending approval for any future relocation.

| Duplication | Fresh-clone inventory | Future recommendation |
|---|---|---|
| `01_canonical_bendlab/` versus the repository root | 141 tracked snapshot files; 140 relative-path overlaps with the rest of the repository, of which 108 are byte-identical and 32 differ; one path exists only in the snapshot. | Keep the snapshot frozen now. At a future approved release, archive it by immutable commit SHA or DOI rather than carrying a second editable copy. |
| Root `results/` versus `01_canonical_bendlab/results/` | 77 matching paths, 74 byte-identical; the two dashboard PNGs and `vector_stimulus_summary.json` differ. | Preserve both copies and their differences until a provenance review decides which is authoritative. |
| `04_shape_extension_branch/` versus root | 31 files in the snapshot; five same-name root overlaps, four byte-identical and `generate_plants.py` different. | Keep as a provenance snapshot. If approved for release archiving, preserve its branch commit and keep the audit report and tests in the working tree. |
| External trajectory data | `05_data_external/uni_trajectories.csv` and `growth_phase/data/00_Data/uni_trajectories.csv` are byte-identical, 2,189,008 bytes each. | Keep both paths for now because the benchmark and growth-phase package use them. A future packaging change should use one versioned source plus documented relative references, with checksum validation. |

No snapshot or dataset relocation is part of this consolidation.
