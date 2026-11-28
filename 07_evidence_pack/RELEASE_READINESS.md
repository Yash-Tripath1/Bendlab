# Release readiness and Zenodo versioning

## Decision

Do not create a tag or release from the current active-session checkout. The
paper-facing evidence is documented and the technical smoke checks pass, but
the active branch points at an older commit, the supplied current date conflicts
with the remote commit timestamps, and the release metadata and legacy dataset
provenance still need explicit review. No tag or release was created during
this audit.

This document is an operational release note, not a scientific-results report.
The scientific reports, fitted results, figures, and preregistrations were not
rerun or edited as part of this readiness pass.

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

The observed `origin/main` is
`5768b9e7d6ba59f70a10c1580f2a66fe7f33c26a` (`5768b9e`), the merge commit for
PR #12. GitHub reports that merge at `2026-11-28T05:15:36Z`, and reports three
successful checks on the merge commit (`build`, `deploy`, and
`report-build-status`). The supplied session date is 2026-11-11, so this is a
future-timestamp conflict that must be checked before release.

The session initially opened on `4f33ede`; its worktree matched the 318-file
`origin/main` tree before the release-readiness edits. To prepare this follow-up
without rewriting the earlier commits, the active branch was fast-forwarded to
its existing remote topic head `9984f89`. That tree is identical to the PR #12
merge tree. This follow-up changes nine documentation or manifest files only;
it does not change code, data, saved scientific outputs, `growth_phase/`, or
`tests/`. A tag made from the active topic branch would still target a topic
commit. After this follow-up is merged, tag a clean `origin/main` commit, and
only after the chronology conflict is resolved.

The only remote version tag observed in this audit is `v1.0.0`, and GitHub
lists it as the latest release. No `CITATION.cff` or `.zenodo.json` is tracked.
That does not prevent a GitHub-to-Zenodo release, but the v2.0.0 record's
creators, version, resource type, concept relationship, and licence must be
checked in Zenodo before it is cited. The earlier tag-plan snapshot in this
file has been replaced with the owner-supplied v1.0.0 and concept-DOI
information above.

## Readiness checks completed

- `.venv/bin/python -m pytest -q`: 17 passed.
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
3. Confirm the new version's metadata says `v2.0.0`, resource type Software,
   and creators Anadi Tripathi and Umaid Siddiqui. Review the record licence
   against the scope note above; do not silently change the repository
   `LICENSE` or the v1.0.0 Zenodo record.
4. Copy the new version-specific DOI from the v2.0.0 landing page. Verify that
   it resolves to the new record and that the concept DOI still resolves to
   the version group. Use the version-specific DOI in the paper's software
   citation; retain the concept DOI when citing the series of versions.
5. Record the new DOI, GitHub tag, exact commit SHA, Zenodo version, licence
   metadata, and archive checksum in the paper and release notes.

Do not report v2.0.0 as archived until these checks are complete. The record
23457746 details in this file are owner-supplied; verify the displayed Zenodo
metadata during the human release procedure.
