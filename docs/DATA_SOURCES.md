# Where plant data actually comes from

The short answer to "where do we get data like the hackathon gave us": the
hackathon did not hand us measured data. It handed us a **generator**
(`kit.py`, `build_public_data.py`) plus the outputs of that generator in
`data/public_01` … `data/public_10`, and a `data_manifest.json` recording seeds
and splits. Everything synthetic came from code they wrote.

For a plant model we supply our own generator. Real data has one job here:
H5, the anchor that keeps the model honest.

## Tier 1 — ready now, curve-shaped, matches our state variable

| Source | What it gives | Access |
|---|---|---|
| PLOS Biol 2023, doi 10.1371/journal.pbio.3002344, S13 Data | stem angle time series, phototropism and heliotropism, 48 plants across six light treatments in `Fig1C` alone | direct download, already in `data/real/` |
| Atamian et al. 2016, *Science* 353:587–590, doi 10.1126/science.aaf9793 | the heliotropism result our clock term exists to reproduce: east side grows faster by day, west side at night, mature plants fix east | paywalled, check IITM library access |
| Orbovic, Poff & DeGroot 1993, *Plant Physiology* 103:157–163 | elongation rates of both flanks of Arabidopsis hypocotyls during first and second positive phototropism | free, PMC158958 |
| Blaauw sine law (first positive phototropism) | the classical quantitative relation our `sin(phi - theta)` term is a descendant of | primary literature |

The PLOS S13 file is the only one that is already a clean table. Everything
else needs either library access or figure digitising.

Scoped 13 October 2026: the Orbovic & Poff (1993) curves most often
reproduced are **mean curvature time courses** for first positive
phototropism (blue light at t = 0, minutes scale), including the
temperature series (15/25/28 degC) re-plotted in later work. They are
population means, not per-plant curves, so they can validate curve
*shape* (including whether a two-phase rise appears outside our
sunflower data) but cannot enter the per-plant fitting pipeline.
Digitisation has not started.

## Tier 2 — figure digitising, when a paper only shows a plot

- WebPlotDigitizer (automeris.io/wpd), free, browser-based
- Workflow: save the figure PNG, set axes from two labelled points, click the
  curve, export CSV
- Every digitised curve gets a provenance row: paper, DOI, figure number,
  date, who digitised it, and the two calibration points used
- Digitised points carry error. Propagate it, or restrict claims to shape
  rather than exact values

## Tier 3 — large phenotyping datasets, useful later, not for v0

| Source | Content | Access |
|---|---|---|
| TERRA-REF | field phenotypes and imaging for sorghum and wheat | open, USDA Ag Data Commons mirrors, e.g. doi 10.15482/USDA.ADC/1529177, CC0 |
| OpenAlea | functional-structural plant modelling in Python, with runnable examples such as the Adel wheat model | open source |
| CPlantBox | root and shoot architecture simulation, Python bindings | open source |
| PCSE / WOFOST | process-based crop growth models, the real version of a GDD toy | open source |
| GrowliFlower, PlantCLEF | image datasets, not angle time series | open |

TERRA-REF and the modelling platforms are worth knowing about. None of them is
the right starting point for a bending-angle study: they answer growth and
architecture questions, and our state variable is one angle.

## The mysimulator.uk pages

Both links are teaching visualisations with a stated accuracy caveat — the
agronomy page says outright that its moisture, photoperiod and yield terms are
"simplified teaching approximations". Treat them as UI references for our own
demo, not as data and not as a model to validate against.

The phototropism page's auxin lit/shaded split is a good visual language for
showing why a stem bends. The GDD page is the agronomy framing, which is a
different research question from ours.
