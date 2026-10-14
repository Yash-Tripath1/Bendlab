# Data sources

This document records the provenance of the measured data used by
BendLab and identifies candidate datasets for subsequent validation. It
also distinguishes measured data from reference simulations. Only the
PLOS Biology S13 dataset is currently used in the fitting pipeline.

## Tier 1 — datasets suitable for immediate analysis

| Source | Data provided | Access |
|---|---|---|
| Brooks, Atamian & Harmer (2023), *PLOS Biology*, doi:10.1371/journal.pbio.3002344, S13 Data | Stem-angle time series for phototropism and heliotropism experiments; sheet Fig1C contains 48 plants in six stimulus-start-time groups | Public download; included in `data/real/` |
| Atamian et al. (2016), *Science* 353:587–590, doi:10.1126/science.aaf9793 | Quantitative results on circadian regulation of sunflower heliotropism, including day/night growth asymmetry and orientation of mature plants | Subscription access may be required |
| Orbovic & Poff (1993), *Plant Physiology* 103:157–163 | Growth distribution during first positive phototropic curvature of Arabidopsis hypocotyls | Public, PMC158958 |
| Blaauw sine law | Classical quantitative relationship between stimulus direction and first positive phototropic curvature | Primary literature |

The S13 workbook is the only source presently available as a structured,
analysis-ready table. The remaining sources require institutional access
or extraction of numerical values from published figures.

### Orbovic & Poff (1993)

The widely reproduced Orbovic & Poff curves are population-mean curvature
time courses for first positive phototropism, with blue-light stimulation
beginning at time zero and measurements on a minutes timescale; a
temperature series (15, 25 and 28 °C) is also reported. Because the data
are population means rather than individual-plant trajectories, they are
suitable for external validation of trajectory shape, including whether
a two-phase rise occurs outside the sunflower dataset, but not for the
per-plant fitting pipeline. Digitisation has not yet been performed.

## Tier 2 — numerical extraction from published figures

Where numerical data are available only as figures, the following
procedure will be used:

1. extract the data with WebPlotDigitizer or an equivalent tool;
2. calibrate each axis using at least two labelled points;
3. record the publication, DOI, figure number, extraction date, operator
   and calibration points for every extracted curve;
4. represent digitisation uncertainty in subsequent analyses, or restrict
   conclusions from digitised data to trajectory shape.

## Tier 3 — larger phenotyping and modelling resources

| Resource | Content | Access |
|---|---|---|
| TERRA-REF | Field phenotypes and imaging for sorghum and wheat | Public; USDA Ag Data Commons mirrors include doi:10.15482/USDA.ADC/1529177 (CC0) |
| OpenAlea | Functional-structural plant modelling in Python | Open source |
| CPlantBox | Root and shoot architecture simulation with Python bindings | Open source |
| PCSE / WOFOST | Process-based crop-growth models | Open source |
| GrowliFlower, PlantCLEF | Image datasets; not stem-angle time series | Public |

These resources are not appropriate starting points for the present
analysis because they address growth, architecture or classification
questions rather than the time course of a single stem angle.

## External simulations used as references

Interactive plant-growth and tropism simulations available at
mysimulator.uk may be useful as references for interface design and for
qualitative presentation of light-dependent bending. They are teaching
visualisations accompanied by accuracy caveats and are not used as data,
parameter sources or validation benchmarks in this project.
