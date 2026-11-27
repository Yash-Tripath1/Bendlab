# Evidence-pack reproducibility

## Scope and status

The pack was prepared with the repository's existing saved inputs and outputs.
The only new numerical analyses are (a) a direct comparison of saved Fig1C fit
caps to raw observed adjacent-sample rates, and (b) the narrowly scoped H4
static-versus-sweep simulation/clustering reproduction. Neither performs
parameter fitting. A deterministic `sim.py::batch_simulate` convention check
uses explicitly chosen parameters and is not a historical benchmark.

Do **not** rerun `phase_a.py` as part of this pack. Its
committed `results/phaseA_run.log` contains a recorded traceback. No Phase A,
Phase E, growth-coupling, inverse-model, or other parameter fits were rerun for
this pack. The committed Phase E baseline checks were read and validated from
the existing summary JSON; the Phase E fitting/evaluation harness was not rerun.

All scripts in this directory write only beneath `07_evidence_pack/`. The
source reports and all inputs listed below remain untouched.

## Environment

The run used Python **3.11.2** and the package versions pinned in
[`requirements-evidence.txt`](requirements-evidence.txt): NumPy 2.4.6, pandas
3.1.1, SciPy 1.17.1, scikit-learn 1.9.1, Matplotlib 3.11.2, and openpyxl
3.1.5. The repository's root `requirements.txt` supplies compatible minimum
versions; the pinned file records the environment actually used here.

From a fresh checkout, create an environment and install the evidence-pack
pins, for example:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r 07_evidence_pack/requirements-evidence.txt
```

The analysis also imports the repository's local modules and reads the tracked
workbooks/CSVs/JSONs listed below, so run commands from the repository root.

## Rebuild commands

From the repository root, run the two audit scripts first, then regenerate the
five figures:

```bash
.venv/bin/python 07_evidence_pack/identifiability_count.py
.venv/bin/python 07_evidence_pack/committed_number_audit.py
for script in 07_evidence_pack/figures/fig0*.py; do
  .venv/bin/python "$script"
done
```

Expected audit summaries include:

- 48 saved Fig1C fits; direct observed-peak comparison **40 above / 8 at or
  below**; saved Phase A Jacobian flag **47/48**.
- Saved-fit medians **1.8011 degrees** in-sample RMSE and **8.5824 degrees**
  across-plant spread; **44/48** fits not at any optimization bound.
- Model-selection result **72/75 = 96%** at the specified 160-degree, 2:1,
  20-seedling condition.
- H4 ARI **0.441682** (reported to three decimals as **0.442**), using the
  committed population generator, simulator, features, and clustering settings.
- All five recorded Phase E baseline reproduction checks remain within the
  saved 0.05-degree harness tolerance. This pack validates those saved checks;
  it does not rerun the Phase E fits.
- The explicit root-simulator check terminates at **90.6870** and **90.3761**
  degrees from starting angles 5 and 40 degrees, respectively. Its explicitly
  chosen parameter values are recorded in the JSON; these values are not
  historical fitted parameters.

The scripts assert expected row counts and key results and fail loudly if
saved inputs change. `identifiability_count.py` reads the saved fit CSV,
uncertainty CSV, Phase A summary, and S13 workbook. It calls the project's
existing `features.peak_rate` function (raw absolute adjacent differences over
the uniform sampling interval) and does not smooth observations or fit a
model.

`committed_number_audit.py` reads the saved fit and model-selection CSVs and
Phase B0/Phase E summary JSONs. Its H4 section reconstructs the 6,000-vector
weighted population and runs the two committed stimulus simulations plus
standardization, KMeans, and ARI; it uses six clusters, `n_init=10`, population
seed 21, KMeans seed 13, 24 hours, and 30-minute recorded features. It does not
call a fitting optimizer and does not run H6. The simulator frame check calls
the repository-root simulator with `k=10`, `tau=2.2`, `max_rate=200`,
`phi0=90`, 24 hours, and a one-minute step for `theta0=5` and `40` degrees.
Those test inputs were chosen for this check and are not historical results.

## Figure regeneration and provenance

Each `figures/fig0*.py` script reads its named committed or evidence-pack
CSV/JSON input and writes the adjacent PNG. The figure scripts do not call a fitter or run a
new model search. Figures are saved at 300 dpi and an 85 mm nominal width. Figures 1-3 use a
70 mm height, figure 4 uses 72 mm, and figure 5 uses 66 mm. The image and JSON
output hashes are recorded in `SHA256SUMS.txt`; check them from this directory
with `sha256sum -c SHA256SUMS.txt`.

| Script | Input(s) | Output |
|---|---|---|
| `fig01_identifiability_rate_cap.py` | `outputs/identifiability_count.json` | `figures/fig01_identifiability_rate_cap.png` |
| `fig02_external_benchmark_rmse.py` | `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_heldout_per_plant.csv` | `figures/fig02_external_benchmark_rmse.png` |
| `fig03_intensity_transfer.py` | `02_workstream_A_external_benchmark/workstream_a/outputs/phase_e_w3_primary_by_intensity.csv` | `figures/fig03_intensity_transfer.png` |
| `fig04_growth_coupling_nulls.py` | `06_growth_coupling/outputs/analysis_results_amended.json`, `amended_task4_null_rhos.csv` | `figures/fig04_growth_coupling_nulls.png` |
| `fig05_zt9_transfer.py` | `results/clock_validation_shared_heldout.csv` | `figures/fig05_zt9_transfer.png` |

Figure 4 summarizes the 1,000 stored eligible-sample draws for each of the
four amended null series; its intervals are recomputed as linear 2.5th, 50th,
and 97.5th percentiles. Figure 5 uses the six saved held-out ZT9 per-plant
rows. Figure 2 uses Phase E held-out predictions, not the older Phase B0
benchmark summary. Do not mix their slightly different W2 values or describe
them as a single run.

## Files produced

- `outputs/identifiability_count.json`
- `outputs/committed_number_audit.json`
- Five `figures/*.png` files listed above.

The JSON files retain input paths, criteria, settings, results, and relevant
per-plant data. The Python files beside them are the executable audit and
figure sources.
