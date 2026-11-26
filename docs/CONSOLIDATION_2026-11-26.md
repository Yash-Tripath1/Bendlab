# Repository consolidation record

**Record identifier:** 2026-11-26, following the requested filename.
Verification outcomes are recorded below from the actual runs; no
scientific result is inferred by this document.

## Repository reality and branch reconciliation

- Fresh-clone baseline: `main` at `92df6e0`, 417 tracked files, and 58
  tracked Markdown documents, matching the supplied inventory. The stale
  local checkout initially reported 402 tracked files at `4f33ede`.
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
| Working Markdown documents | Replaced em dashes in working documents; frozen snapshots were left untouched. |
| `03_workstream_B_shape_extension_audit/workstream_b/shape_audit_corrected_v1.py` | Changed only its import and output paths to repository-relative `Path` values. Analysis calculations were not changed or rerun. |
| `clock_validation.py`, package/test notes | Updated references to renamed or archived documentation paths. |
| `growth_phase/README.md` | A draft update was restored byte-for-byte to the manifest-listed version after the fresh-clone test showed that the protected checksum manifest includes this README. It has no final content change. |

## Verification

- The initial fresh clone of `main` was clean at `92df6e0`: 417 tracked
  files and 58 tracked Markdown documents. The document inventory now has
  62 Markdown documents and indexes all tracked Markdown and HTML pages.
- The active branch was fast-forwarded from `4f33ede` to the merged Phase E
  branch head `7e64f1a` before edits. The 17 pre-existing dirty Phase E
  paths were byte-identical to that remote head. They were saved in a
  safety stash during reconciliation and are present in the resulting
  branch tree. No reset, clean, force-push, or history rewrite was used.
- An early test attempt on draft commit `a86b7dc` returned 16 passed and 1
  failed: `test_growth_phase_sha256_manifest` detected that a draft edit to
  `growth_phase/README.md` no longer matched the protected manifest. The
  README was restored byte-for-byte to the manifest-listed version
  (`94800747e19f6d33cc2cafb511a4a8b10181c6371f82888ca0852f45c79a3391`);
  the manifest and test code were not changed. In a fresh clone at
  `7e54a0a`, `python -m pytest -q` passed: **17 passed in 1.87s**.
- In that final fresh clone, `python -m pip install -r requirements.txt`
  completed successfully under Python 3.11.2. Pip printed a non-failing
  legacy `setup.py install` deprecation warning for `autograd-gamma`.
- The requested regeneration check ran only in that disposable clone. The
  exact command was `python real_seedling_sim.py`; it exited successfully
  in **2.535 seconds**, wrote the result CSV with 264 rows, and saved the
  dashboard PNG. Both files were byte-for-byte identical to their
  committed versions: the CSV was 20,583 bytes and the PNG was 909,756
  bytes; each had a 0-byte size delta and 0 differing byte positions.
  CSV SHA-256:
  `9472329b54ed4e9e4549c0c15a59f4b7e09d39ca119e8664924ccb61a12901a9`.
  PNG SHA-256:
  `5e619a7d829f8359e1623bcc7ec9570446f0f9a5d4bad2f53c5ee9f1fe4dea0c`.
  The clone's committed artifacts were restored after comparison.
- Active references to the renamed external-validation note and archived
  packaging notes were updated. The full tracked-Markdown relative-link
  scan found **0 broken links**. In the fresh-clone inventory, 31 Markdown
  documents contained 193 em dashes: 15 working documents contained 85,
  and 16 frozen documents contained 108. The working-document count is now
  zero; the 108 frozen occurrences were left untouched. The renamed
  external-validation note has no `/home`, `/tmp`, or other machine-specific
  absolute paths.
- The specified v1 shape-audit script passed `py_compile`; its only changes
  are path resolution and the output path. Its analysis was not rerun.
- From the final working tree, after activating the temporary clone's
  virtual environment, the exact command `python -m pytest -q` passed:
  **17 passed**. The required command
  `(cd growth_phase && sha256sum -c SHA256SUMS.txt)` completed with **58/58
  OK**. `git diff --check` and the staged whitespace check were clean.

## Scientific integrity

No scientific values, thresholds, verdicts, or conclusions in the source
reports or saved scientific outputs were changed. The README and status
summaries repeat quantitative claims from the linked sources and retain
their original qualifications. No analysis was refit or rerun in the
working tree. The sole requested artifact regeneration was confined to a
disposable fresh clone, produced byte-identical outputs, and was not
committed.

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
