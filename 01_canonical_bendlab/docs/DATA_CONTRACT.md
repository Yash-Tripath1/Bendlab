# Data specification and handling rules

## Measured data: `data/real/stem_angles_plosbiol2023_s13.xlsx`

Source: "Multiple light signaling pathways control solar tracking in sunflowers",
PLOS Biology 2023, doi [10.1371/journal.pbio.3002344](https://doi.org/10.1371/journal.pbio.3002344),
supporting file S13 Data. Downloaded 11 October 2026. 67,115 bytes.
SHA-256 `1257f4069f4fb600d0bddb616110772af28552dc43ad330c18aa3dea58a590b7`.

Sheets, as read with pandas `ExcelFile`:

| Sheet | Time column | Time range | Rows | Plant columns | Content |
|---|---|---|---|---|---|
| `Fig1B` | `ZT` | 4.0 – 20.0 | 33 | 3 | stem angle, half-hour steps |
| `Fig1C` | `ZT` | 0.0 – 41.5 | 112 | 48 | stem angle across six light treatments, half-hour steps |
| `Fig2B` | `time` | 14 – 77 | 64 | 6 | stem angle, hourly |
| `Fig4A` | `ZT` | 0 – 77 | 78 | 17 | stem angle, hourly |
| `Fig4J` | `ZT` | 0 – 97 | 98 | 15 | stem angle, hourly |

The workbook `read.me` sheet states that the data comprise stem-angle
measurements for plants undergoing phototropism or heliotropism and were
used to plot Figures 1B, 1C, 2B, 4A and 4J.

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

Row counts differ among blocks because the observation windows differ;
this is a property of the source table rather than a parsing difference.

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

The total is 48 plant columns. Treatment interpretation follows the
definitions in Brooks et al. (2023).

### Units and handling rules

- Angle is in degrees. The sign convention is that of the source
  publication; it must be confirmed against the published figures before
  signs are compared across sheets.
- The sheets are ragged: `Fig1C` cells are empty outside each plant's
  observation window. Data must be parsed in long form, with missing cells
  omitted rather than imputed.
- The time base differs by sheet. `ZT` denotes zeitgeber time (hours since
  the start of the photoperiod). `Fig2B` uses experimental time in hours.
  Sheets must not be concatenated without conversion to a common time base
  and retention of the source-sheet identifier.
- **`Fig1C` stimulus onset.** Zeitgeber time is an absolute circadian
  time, not elapsed time since stimulation. In Fig1C, each treatment
  group was first exposed to unilateral blue light at its own ZT (Fig. 1
  legend, Brooks et al. 2023). A plant's first non-missing observation
  therefore defines its stimulus onset, and its angle at that time is zero
  by construction. Every fit, simulation or feature calculation using
  these trajectories must use elapsed time, `t - t_first`, calculated
  separately for each plant. Supplying absolute ZT to a model that assumes
  stimulation at $t=0$ causes later stimulus-start groups to appear
  artificially slow; in the initial analysis this placed `tau` at its upper
  bound for all 18 ZT12/ZT16 plants. This rule was added on 13 October
  2026 after that error had entered the results (see
  `docs/RESULTS_ROUND0.md`, Section 8). `fit_real.py` applies the shift in
  `fit_plant`, and check 3d of `audit_round1.py` provides a regression test.
- Sampling intervals differ by sheet: `Fig1B` and `Fig1C` are half-hourly,
  whereas the remaining sheets are hourly. Any interpolation used for
  comparison must be specified in the analysis.

### Additional sheets assessed on 13 October 2026

| Sheet | Experiment (according to the published legend) | Angle convention | Current status |
|---|---|---|---|
| `Fig1B` | Phototropism time course following blue-light stimulation at ZT3, n=3 | Change from zero at stimulus onset | Candidate validation set; very small sample size |
| `Fig2B` | Stem angles of field-grown heliotropic plants, n=6 | **Absolute** stem angle (approximately 71–122 degrees), varying between day and night | Requires a moving-sun model; not to be fitted with the static-light model |
| `Fig4A` | Chamber-grown plants transplanted to the field after sunset; initiation of heliotropism, n=17 | **Absolute** stem angle (approximately 64–119 degrees) | Requires a moving-sun model with night-time reorientation |
| `Fig4J` | Plants in filter enclosures: clear, blue-depleted and red-depleted light, n=5 per treatment | Published figure is **Z-score normalised**; workbook values resemble degrees (approximately 64–112) | **Not to be modelled until the normalisation is resolved against S15 Data** |

Three handling rules follow from the Fig1C time-base error: (1) for
absolute-angle sheets, the angle convention must be established before
fitting, because the model variable $	heta$ represents deviation from
an initially vertical orientation and is not necessarily commensurate
with the published absolute angle; (2) the stimulus onset and time-zero
definition for every new sheet must be recorded here before analysis;
(3) the three Fig4J filter groups are treatments applied to the incident
light, not plant genotypes.

### Licence

PLOS Biology publishes under CC BY (confirmed from the journal's
information page in October 2026); articles and supporting files may be
copied and redistributed with attribution. The workbook is therefore
included in `data/real/`, with attribution in `README.md`. The citation,
download date, byte size and checksum must accompany the file in any
redistribution.

## Simulated data

Simulated populations are generated by `generate_plants.py`. A simulated
plant is a four-parameter vector (`k`, `tau`, `max_rate`, `phi0`). The
uniform population samples the declared parameter box; the empirically
weighted population bootstrap-resamples the clean measured-data fits and
applies 15 per cent lognormal multiplicative jitter. Every population is
generated from a declared integer seed recorded in the generating script.
Simulated trajectories and behavioural features are written to the CSV
files listed in the relevant results documents.

## Provenance requirements

Every externally obtained data file must be accompanied by its source URL
or DOI, download date, byte size and checksum. Superseded generated files
retained for provenance must be versioned or renamed rather than silently
overwritten.
