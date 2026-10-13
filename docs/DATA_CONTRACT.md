# Data contract

## Real data: `data/real/stem_angles_plosbiol2023_s13.xlsx`

Source: "Multiple light signaling pathways control solar tracking in sunflowers",
PLOS Biology 2023, doi [10.1371/journal.pbio.3002344](https://doi.org/10.1371/journal.pbio.3002344),
supporting file S13 Data. Downloaded 11 October 2026. 67,115 bytes.
SHA-256 `1257f4069f4fb600d0bddb616110772af28552dc43ad330c18aa3dea58a590b7`.

Sheets, as read with pandas `ExcelFile`:

| Sheet | Time column | Time range | Rows | Plant columns | What it is |
|---|---|---|---|---|---|
| `Fig1B` | `ZT` | 4.0 – 20.0 | 33 | 3 | stem angle, half-hour steps |
| `Fig1C` | `ZT` | 0.0 – 41.5 | 112 | 48 | stem angle across six light treatments, half-hour steps |
| `Fig2B` | `time` | 14 – 77 | 64 | 6 | stem angle, hourly |
| `Fig4A` | `ZT` | 0 – 77 | 78 | 17 | stem angle, hourly |
| `Fig4J` | `ZT` | 0 – 97 | 98 | 15 | stem angle, hourly |

`read.me` states: stem angle measurements for plants undergoing phototropism or
heliotropism; data were used to plot figures 1B, 1C, 2B, 4A, 4J.

Verified parse of `Fig1C` to long form: 2,606 non-null rows, angle range
-2.759 to 78.143 degrees. Per-block row counts and ranges:

| Block | Rows | Angle min | Angle max |
|---|---|---|---|
| `ZT0`  | 336 | -1.487 | 69.555 |
| `ZT3`  | 474 | -1.955 | 61.540 |
| `ZT6`  | 392 | -1.076 | 60.600 |
| `ZT9`  | 396 | -1.586 | 60.776 |
| `ZT12` | 540 | -2.759 | 78.143 |
| `ZT16` | 468 | -1.571 | 70.937 |

Row counts differ by block because plants drop out at different times, not
because of a parsing difference.

### `Fig1C` treatment blocks

Column prefixes encode the treatment. Counts as counted from the header:

| Block | Plants |
|---|---|
| `ZT0`  | 7 |
| `ZT3`  | 9 |
| `ZT6`  | 8 |
| `ZT9`  | 6 |
| `ZT12` | 9 |
| `ZT16` | 9 |

Total 48 columns. The paper defines what each block is; read it before
assigning meaning.

### Units and handling rules

- Angle is in degrees. Sign convention is whatever the paper uses — confirm
  against the figures before comparing signs across sheets.
- Sheets are ragged: `Fig1C` cells are empty outside each plant's own window.
  Parse as long form and drop nulls rather than filling them.
- Time base differs by sheet. `ZT` is zeitgeber time (hours since lights on).
  `Fig2B` uses plain `time` in hours. Do not concatenate sheets without
  converting to a common base and recording which sheet each row came from.
- **`Fig1C` stimulus onset (the rule whose absence cost us a retraction).**
  ZT is the plant's absolute clock, not time since stimulus. In Fig 1C each
  block was first exposed to unilateral blue light at its own ZT (Fig 1
  legend, Brooks et al. 2023), so a plant's first non-null cell is its
  stimulus onset and its angle there is 0 by construction. Any fit,
  simulation or feature that consumes these curves must use elapsed time
  `t - t_first` per plant. Feeding raw ZT to a model that assumes the
  stimulus started at t = 0 makes late blocks look pathologically slow
  (in our case: `tau` pinned at its bound for all 18 ZT12/ZT16 plants).
  Added 13 Oct 2026 after exactly that bug shipped; see the bug log in
  `docs/RESULTS_ROUND0.md`. `fit_real.py` enforces this by shifting
  inside `fit_plant`, and `audit_round1.py` check 3d guards it.
- Sampling differs by sheet: `Fig1B` and `Fig1C` are half-hourly, the rest
  hourly. Interpolate explicitly when comparing, and say so.

### Licence

PLOS Biology publishes under CC BY (confirmed on the journal's information
page, October 2026): articles and their supporting files may be copied and
redistributed with attribution. This file is therefore included in
`data/real/` with attribution in `README.md`. Keep the citation, the download
date and the checksum attached to the file wherever it moves.

## Synthetic data

Not yet written. When it is, this section gets the same treatment: generator
name, seed rule, parameter ranges and their units, output schema, and the
train/validation/test split with disjoint seeds.

## Provenance

Record for every file: source URL or DOI, download date, byte size, and a
checksum. If a file is regenerated, the old one is renamed, not overwritten.
