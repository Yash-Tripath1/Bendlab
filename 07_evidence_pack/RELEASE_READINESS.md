# Release readiness assessment

## Observed main and existing release

The observed `origin/main` tip is `f1b494270d4882b2607a3f017f460859cf358063`, with Git committer timestamp `2026-11-27T23:56:19+05:30`. This timestamp is later than the assessment date, `2026-11-11`; verify the repository clock/history before tagging. The only tag reported by local and remote tag listings is `v1.0.0`. It points to `b09ea5aa6003082b41d726b2b8499ded313dcb21`, dated `2026-10-16T23:27:14+05:30`, subject `corrected H6/H8, model-selection design study`. GitHub reports the `v1.0.0` release published at `2026-10-18T19:10:05Z`.

`v1.0.0` predates the paper analyses: its tree contains no Phase E report, preregistration, or Phase E output files. Those later analyses are documented in `02_workstream_A_external_benchmark/PHASE_B0_REPORT.md`, `growth_phase/PHASE_E_PREREGISTRATION.md`, and `02_workstream_A_external_benchmark/PHASE_E_RESULTS.md`. The Phase E report describes the fixed-threshold negative result and paired parity with B1; it does not claim superiority or a validated mechanism. Do not move or replace `v1.0.0`.

## Recommended paper tag: `v2.0.0`

Tag the `main` commit that includes the reviewed paper evidence, after that evidence is merged. Do not tag the currently observed `f1b494...` commit if the paper cites `fig06` or these new documents, because that commit does not contain them. The commands below are for a human to run in Windows PowerShell after merge. They create an annotated tag only if the current `origin/main` contains the new paper files and `v2.0.0` does not already exist. They then verify that the local and remote tag dereference to the same commit as `origin/main`.

```powershell
git fetch origin
$target = (git rev-parse origin/main).Trim()
git cat-file -e "${target}:07_evidence_pack/PROJECT_CLOSE.md"
if ($LASTEXITCODE -ne 0) { throw "Paper close is not present on origin/main; do not tag." }
git cat-file -e "${target}:07_evidence_pack/figures/fig06_phase_e_equivalence.png"
if ($LASTEXITCODE -ne 0) { throw "fig06 is not present on origin/main; do not tag." }
if (git tag --list v2.0.0) { throw "Local v2.0.0 already exists; inspect it before proceeding." }
if (git ls-remote origin 'refs/tags/v2.0.0') { throw "Remote v2.0.0 already exists; inspect it before proceeding." }
git tag -a v2.0.0 -m "BendLab paper version" $target
git push origin refs/tags/v2.0.0

$localCommit = (git rev-parse 'v2.0.0^{commit}').Trim()
if ($localCommit -ne $target) { throw "Local v2.0.0 does not point to origin/main." }
$remoteRef = git ls-remote origin 'refs/tags/v2.0.0^{}'
$remoteCommit = (($remoteRef -split '\s+')[0]).Trim()
if ($remoteCommit -ne $target) { throw "Remote v2.0.0 does not point to origin/main." }
"Verified v2.0.0 -> $remoteCommit"
```

## Remote branches and deletion assessment

This is a pre-PR snapshot. Remote heads were read from `git ls-remote --heads origin`; tip metadata and GitHub compare results were read from the GitHub branches and compare APIs. `origin/HEAD` is a symbolic pointer to `origin/main`, not a separate branch.

| Remote branch | Tip commit and committer date (UTC) | Merge status relative to main | Tree differs from main? | Deletion safety, no deletion performed |
|---|---|---|---|---|
| `origin/main` | `f1b494270d4882b2607a3f017f460859cf358063`, `2026-11-27T18:26:19Z` | Default branch | No | Do not delete. |
| `origin/arena/5d10ddb3-bendlab` | `02b81d4ef39c888bd131879854a52018d922c375`, `2026-11-27T18:09:03Z` | PR #10 merged; tip is an ancestor of main, zero commits ahead and two behind | No, identical tree | Do not delete while it is the active session branch. Its remote tip has no unique tree content in this snapshot. |
| `origin/arena/f1102a30-bendlab` | `a452dc4f1edb98c58a64ca0008f68d10c07b4218`, `2026-11-11T17:07:23Z` | PR #4 merged; tip is an ancestor of main, zero ahead and 27 behind | Yes, later main changes | Content-wise safe after checking for local or external reliance; no unique commit is missing from main. |
| `origin/growth-phase-audit-v2` | `92285f2a1c25daf6c9ebd334a819596f2b5a1c89`, `2026-10-25T18:26:19Z` | PR #3 merged, but the current tip diverges: one commit ahead and 30 behind main | Yes | Not safe to delete without preserving or reviewing the branch-only commit `growth based degeneracy`. |
| `origin/growth-phase-d-restore` | `c94e08e8d7baba86cf8b21fb579348dfc4f1f1ba`, `2026-11-24T19:11:28Z` | PR #5 merged; tip is an ancestor of main, zero ahead and 25 behind | Yes, later main changes | Content-wise safe after checking for local or external reliance; no unique commit is missing from main. |

The main, active-session branch, and `growth-phase-d-restore` timestamps are later than the assessment date. Verify this apparent future metadata before release. GitHub also reports PR #2 as open with `main` as both head and base: `https://github.com/Yash-Tripath1/Bendlab/pull/2`. The active-session row records the remote tip before this PR. This PR advances that branch but does not delete any branch or alter tags or releases. At the time of the inventory, the local worktree was based on the observed main commit and the paper changes had not yet been pushed.

**Administrative provenance note:** the hashes, dates, tag/release versions, PR numbers, and ahead/behind counts above come from Git/GitHub metadata, not a committed-file producer. Under the committed-file-only citation rule these administrative values are `UNSOURCED`; their observed sources are `git ls-remote`, Git commit/tag metadata, and the GitHub branches, compare, release, and pull-request endpoints. Analysis-result numbers in the paper documents cite their committed output paths.

## Zenodo archive recommendation

Create the Zenodo deposit from the exact paper-release commit after the paper evidence is merged, and cite the resulting DOI and Git commit together. Check that the Git-tracked snapshot includes the scripts, tests, documentation, committed outputs, and input data required to reproduce the paper. A Zenodo archive will not include ignored or untracked local files, so do not mint the paper archive from this unmerged working tree.

## Read-only `requirements.txt` import audit

A static AST scan covered tracked Python files plus the new fig06 script. Direct third-party imports found were `fpdf`, `lifelines`, `matplotlib`, `numpy`, `pandas`, `pytest`, `scipy`, and `sklearn`; they map to the listed `fpdf2`, `lifelines`, `matplotlib`, `numpy`, `pandas`, `pytest`, `scipy`, and `scikit-learn` distributions. The `fpdf2` wheel metadata was checked read-only and supplies the `fpdf` top-level module. `openpyxl` is also listed for Excel-file support. No missing direct import dependency was found. This is a static import audit, not a test of optional runtime paths. `requirements.txt` was not changed.
