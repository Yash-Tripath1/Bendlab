# Repository restructuring verification

This record accompanies the seven-commit restructuring. Verification is limited to the requested integrity checks; no model fitting or scientific analysis was run beyond the specified saved-output audit.

## Commands and outcomes

### Regression suite

Command: `.venv/bin/python -m pytest -q`

Output: `17 passed`.

### Protected growth-phase manifest

Command: `(cd growth_phase && sha256sum -c SHA256SUMS.txt)`

Output: `58/58 OK`. The manifest and its files were not edited.

### Identifiability audit comparison

Command: `.venv/bin/python 07_evidence_pack/identifiability_count.py`

Output:

```text
Direct observed-peak criterion: 40/48 fitted caps above observed peak; 8/48 at or below. Phase A Jacobian criterion: 47/48 flagged.
Wrote 07_evidence_pack/outputs/identifiability_count.json
```

The generated JSON was compared recursively with the committed JSON. All keys, strings, paths, counts, flags, and lists matched. Of 145 float fields, four differed only in the final reported digit. The committed artifact was restored byte-for-byte after comparison. Its SHA-256 before and after was `45a0218c39f64aec59d28f32d176e4efaf094eb0aa662614d3e28d66ceb39c27`; the temporary generated comparison copy had SHA-256 `61f89144629fc3df84bb181cadea9707dd9860fa9639d604ac5bfec928f6960a`.

### Figure 5 regeneration

Command: `.venv/bin/python 07_evidence_pack/figures/fig05_zt9_transfer.py`

Output: `Wrote 07_evidence_pack/figures/fig05_zt9_transfer.png at 300 dpi and 85 mm width`.

The generated figure was byte-identical to the committed figure. Original, generated, and restored SHA-256: `5660032af8b82600edd9509a5735d7f161dbe78f05e3f64734b55f271b62fbfa`.

### Site build

Command: `python build_site.py`

Output:

```text
bendlab_about.html -> docs/about.html
bendlab_visual_simulator.html -> docs/index.html
bendlab_model_demo.html -> docs/model.html
bendlab_curve_fitter.html -> docs/fitter.html
```

Of the four generated pages, only `docs/about.html` has a diff. The simulator, model demo, and curve-fitter sources and generated pages have no content diff.

### Dataset rename integrity

All four documented `results/adaptation_*.csv` SHA-256 hashes match their current files. Each renamed file is byte-for-byte identical to its pre-rename path in the parent commit. No data bytes changed.

### Reference scan

A whole tracked-text-tree scan was run for the retired snapshot marker and the former dataset-name prefix, excluding Git internals and binary contents. It intentionally reports residual historical and preserved-output references. The combined search returned 33 snapshot-marker lines and 9 former-name-prefix lines, 42 unique matched lines across 18 files; the filename scan found no matching paths. No committed output was altered to suppress matches. The exact command and complete hit list are included in the delivery summary.

## Before and after tree measurement

Method: count paths in `git ls-files` and sum the current byte sizes of those tracked regular files. This excludes `.git` and ignored local environments. The before value was measured on the clean baseline before edits.

| Tree | Tracked files | Total file-content bytes |
|---|---:|---:|
| Before restructuring | 455 | 68340726 |
| After restructuring | 318 | 39696029 |
