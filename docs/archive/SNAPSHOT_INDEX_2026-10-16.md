# Retired canonical snapshot index

This record documents the retired root snapshot `01_canonical_bendlab/` as it
stood in the repository snapshot created at commit `b09ea5a`
(`b09ea5aa6003082b41d726b2b8499ded313dcb21`).

- The snapshot contained 141 files.
- Its `results/` directory had 77 matching paths against the current root
  results. Seventy-four of the 77 files were byte-identical; the remaining
  three differed. No root result was replaced or merged as part of retirement.
- The only snapshot document without a same-path counterpart was moved to
  [`CHANGES_2026-10-15_VALIDATION_RUN.md`](CHANGES_2026-10-15_VALIDATION_RUN.md)
  before the snapshot was removed.
- The retired tree remains recoverable from Git history at commit `b09ea5a`.
  The directory was removed from the current checkout, not erased from history.

This index is a provenance note, not an endorsement of the snapshot's outputs
or a claim that its differing results have been reconciled.
