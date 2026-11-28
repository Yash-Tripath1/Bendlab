# Release readiness and Zenodo versioning

## Decision

The v2.0.0 release procedure is documented for the human release operator; no
v2.0.0 tag, GitHub release, or Zenodo version was created as part of this work.
PR #13 merged into `origin/main` at `dcfa6d19c5e84ea44646cdafc19be19211fac15c`
on 2026-11-28, consistent with the session date. The earlier warning about a
future-dated remote commit used an incorrect session date and is withdrawn.
The active-session worktree is not the release target: it is based on `4f33ede`
and contains unmerged local changes. After this audit update is reviewed and
merged, use a clean clone of the latest `origin/main` and follow the Windows
PowerShell procedure below. Complete the metadata and provenance checks before
creating the GitHub release and linking Zenodo.

This document is an operational release note, not a scientific-results report.
The Phase E report received a descriptive correction to distinguish the saved
harness tolerance from the preregistered threshold; historical Markdown received
punctuation-only normalization. No scientific result values changed, no fits,
figures, or data were regenerated, and no preregistrations were edited.

## Existing BendLab Zenodo release

The following v1.0.0 metadata was supplied by the repository owner for this
release audit; the Zenodo host was not accessed independently.

| Field | Existing release |
|---|---|
| Version | `v1.0.0` |
| Version record | [Zenodo record 23457746](https://zenodo.org/records/23457746) |
| Version DOI | `10.5281/zenodo.23457746` |
| Concept DOI | `10.5281/zenodo.23457744` |
| Resource type | Software |
| Published | 2026-10-18 |
| Creators | Anadi Tripathi; Umaid Siddiqui |
| Archived Git commit | `b09ea5aa6003082b41d726b2b8499ded313dcb21` (`b09ea5a`) |
| Zenodo licence | CC-BY-4.0 |

The v1.0.0 archive predates Phases B0 through E and therefore does not contain
the analyses intended for the paper. Preserve that version. The paper-facing
release should be v2.0.0 as a new version under concept DOI
`10.5281/zenodo.23457744`, not as a separate Zenodo concept record. Zenodo
will assign a new version-specific DOI for v2.0.0; record that DOI after the
archive is created. Keep the external trajectory dataset's source attribution
to Zenodo record 21206480 separate and unchanged.

## Licence scope finding

The existing Zenodo v1.0.0 record lists CC-BY-4.0. The repository's top-level
[`LICENSE`](../LICENSE) says the code is MIT-licensed and explicitly excludes
the PLOS workbook in `data/real/`, which retains its source CC BY terms. The
external archive is identified as CC-BY-4.0 in the project documentation. The
Zenodo record's CC-BY-4.0 declaration and the repository's MIT code licence
therefore have different stated scopes. This is a scope mismatch to carry into
the v2.0.0 release review, not a determination that either licence is invalid.
As instructed, neither the Zenodo record nor the repository `LICENSE` was
changed.

The legacy `results/adaptation_instruction_dataset.csv` is documented as an
orphan with no tracked generator, source record, or current code consumer. The
inverse dataset's described generation seed cannot be independently checked
because its generator is not in the checkout. Both files remain in the tree.
Before archiving them as distributable materials, verify their provenance and
redistribution rights or make an explicit, reviewed decision about their scope.
No file was deleted in this audit.

## Repository state and chronology

As of 2026-11-28, `origin/main` is
`dcfa6d19c5e84ea44646cdafc19be19211fac15c` (`dcfa6d1`), the merge commit for
PR #13. GitHub reports that merge at `2026-11-28T09:46:02Z`, consistent with
the session date. The earlier warning based on a 2026-11-11 session date was
incorrect and is withdrawn.

The active-session branch remains based on `4f33ede` and its worktree contains
unmerged changes; neither is the v2.0.0 release target. After this audit update
is reviewed and merged, resolve the latest `origin/main` from a fresh, clean
clone and run the documented checks. No v2.0.0 tag, GitHub release, or Zenodo
publication was made in this work. The human operator should verify the live
release target at the time of release rather than rely on a SHA recorded here.

The v1.0.0 GitHub release is the only release observed, and no v2.0.0 tag or
release was found. The root `CITATION.cff` records the archived v1.0.0 citation
only; it does not assign a DOI to the current post-Phase B0-through-E tree. No
`.zenodo.json` is present. The audit reports that the existing v1.0.0 Zenodo
title is `Yash-Tripath1/Bendlab: v1.0.0`; this was not independently checked
or changed. Verify that the future v2.0.0 Zenodo record has the intended title
before publishing, as described below.

## Readiness checks completed

- `.venv/bin/python -m pytest -q`: 17 passed in 1.76s on Python 3.11.2
  during this audit.
- `.venv/bin/cffconvert --validate --infile CITATION.cff`: valid CFF 1.2.0
  metadata.
- A GitHub Actions workflow is added to run the regression suite on pushes,
  pull requests, and manual dispatch with Python 3.11 and `requirements.txt`.
  Verify its first GitHub check is green after this audit update is merged; no
  CI result is claimed here.
- `python build_site.py`: all four pages generated successfully.
- `growth_phase/SHA256SUMS.txt`: 58 of 58 entries pass.
- `07_evidence_pack/SHA256SUMS.txt`: 8 of 8 entries pass, including Figure 6.
- Static syntax check: 79 Python files parsed, no syntax errors.
- `pip check`: no broken requirements reported.
- The Phase C M0 versus B0 W1 RMSE contexts are reconciled in
  [`PAPER_DATA.md`](PAPER_DATA.md); neither source report was edited.
- The evidence-pack README, reproducibility table, paper outline, and checksum
  manifest now consistently account for six figures. Figure 6 is a paired
  comparison described as parity, not superiority or a formal equivalence
  test. The PNG was not regenerated in this audit.

The `growth_phase/README.md` still contains historical branch-handoff language.
It is part of the protected growth-phase package and was not changed. Read it
as the package's original handoff note, not as the current repository release
status.

## Human procedure for GitHub release v2.0.0 and Zenodo versioning

Run these steps yourself in Windows PowerShell only after the chronology,
provenance, and release-metadata reviews above are resolved. This procedure is
for a clean clone; do not run it from the current active-session checkout.

### 1. Prepare and verify the release commit

```powershell
git clone https://github.com/Yash-Tripath1/Bendlab.git
Set-Location Bendlab
git fetch origin --tags
$target = (git rev-parse origin/main).Trim()
if ($LASTEXITCODE -ne 0) { throw "Could not resolve origin/main." }
$status = git status --porcelain
if ($status) { $status; throw "Release checkout is not clean." }
if ($target -ne (git rev-parse HEAD).Trim()) { throw "Checkout is not at origin/main." }
git cat-file -e "${target}:07_evidence_pack/PAPER_DATA.md"
if ($LASTEXITCODE -ne 0) { throw "Paper data sheet is missing from release target." }
git cat-file -e "${target}:07_evidence_pack/figures/fig06_phase_e_equivalence.png"
if ($LASTEXITCODE -ne 0) { throw "Figure 6 is missing from release target." }
$v1Tag = git ls-remote origin "refs/tags/v1.0.0"
if (-not $v1Tag) { throw "The existing v1.0.0 tag was not found; stop and inspect tags." }
$v1Commit = (git rev-parse "v1.0.0^{commit}").Trim()
if ($v1Commit -ne "b09ea5aa6003082b41d726b2b8499ded313dcb21") {
    throw "The v1.0.0 tag does not resolve to the archived commit recorded for Zenodo."
}
gh release view v1.0.0
if ($LASTEXITCODE -ne 0) { throw "The existing v1.0.0 GitHub release is not visible." }
$existingTag = git ls-remote origin "refs/tags/v2.0.0"
if ($existingTag) { throw "Remote v2.0.0 already exists; inspect it before proceeding." }
gh release list --limit 20
```

Run the project checks from that clean clone before releasing:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe build_site.py
```

Verify both SHA-256 manifests in PowerShell:

```powershell
function Test-Sha256Manifest([string]$Manifest) {
    $directory = Split-Path -Parent $Manifest
    $lines = Get-Content -LiteralPath $Manifest
    foreach ($line in $lines) {
        $parts = $line -split '\s{2,}', 2
        if ($parts.Count -ne 2) { throw "Malformed entry in ${Manifest}: $line" }
        $expected = $parts[0].ToLowerInvariant()
        $path = Join-Path $directory $parts[1]
        $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $expected) { throw "Checksum mismatch: $path" }
    }
    "PASS: $($lines.Count) entries in $Manifest"
}
Test-Sha256Manifest "growth_phase\SHA256SUMS.txt"
Test-Sha256Manifest "07_evidence_pack\SHA256SUMS.txt"
```

Confirm the existing v1.0.0 release is intact and the version-specific tag name
is unused. Do not move or replace v1.0.0.

### 2. Connect the existing Zenodo concept before publishing

In the Zenodo GitHub integration settings, enable
`Yash-Tripath1/Bendlab` before creating the GitHub release. Confirm that the
integration is associated with the existing BendLab concept DOI
`10.5281/zenodo.23457744` and that it will create a new version of that concept
record. Do not manually create a separate Zenodo concept record for v2.0.0.

### 3. Create the GitHub release

After the clean target and checks are verified, create the GitHub release from
PowerShell. `--target` pins the release tag to the previously verified commit.
This command creates the tag and release; it is intentionally included for the
human operator and was not run during this audit.

```powershell
gh release create v2.0.0 `
  --target $target `
  --title "BendLab v2.0.0" `
  --notes "Paper-facing evidence release. Includes the reviewed Phase B0 through Phase E analyses and the six-figure evidence pack. See 07_evidence_pack/RELEASE_READINESS.md for scope and limitations."
if ($LASTEXITCODE -ne 0) { throw "GitHub release creation failed." }
```

Verify the GitHub release and that its tag resolves to the intended commit:

```powershell
gh release view v2.0.0
if ($LASTEXITCODE -ne 0) { throw "GitHub release v2.0.0 is not visible." }
git fetch origin --tags
$tagCommit = (git rev-parse "v2.0.0^{commit}").Trim()
if ($tagCommit -ne $target) { throw "v2.0.0 does not point to the verified release commit." }
```

### 4. Verify the Zenodo version and DOI

After Zenodo processes the GitHub release, inspect the Zenodo record pages
manually:

1. Confirm the existing v1.0.0 record remains record 23457746 and its files are
   unchanged.
2. Confirm a v2.0.0 record appears under concept DOI
   `10.5281/zenodo.23457744`, rather than as a separate concept record.
3. Confirm the v2.0.0 record title is exactly `BendLab v2.0.0`, not an
   owner/repository slug. The audit reports that the existing v1.0.0 title is
   `Yash-Tripath1/Bendlab: v1.0.0`; that metadata was not changed. If the v2.0.0
   draft still uses a repository slug, resolve its title before publication;
   do not change the v1 record. Confirm the new version says `v2.0.0`, resource
   type Software, and creators Anadi Tripathi and Umaid Siddiqui. Review the
   record licence against the scope note above; do not silently change the
   repository `LICENSE` or the v1.0.0 Zenodo record.
4. Copy the new version-specific DOI from the v2.0.0 landing page. Verify that
   it resolves to the new record and that the concept DOI still resolves to
   the version group. Use the version-specific DOI in the paper's software
   citation; retain the concept DOI when citing the series of versions.
5. Record the new DOI, GitHub tag, exact commit SHA, Zenodo version, licence
   metadata, and archive checksum in the paper and release notes.

Do not report v2.0.0 as archived until these checks are complete. The record
23457746 details in this file are owner-supplied; verify the displayed Zenodo
metadata during the human release procedure.
