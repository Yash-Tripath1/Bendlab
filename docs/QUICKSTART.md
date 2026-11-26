# Fresh-clone quickstart

This short workflow covers the canonical project entry points, the test
suite, and one saved figure/results regeneration. Use Python 3.10 or later.
Run commands from the repository root unless a command explicitly changes
directories.

## Clone and install

```bash
git clone https://github.com/Yash-Tripath1/Bendlab.git
cd Bendlab
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## Read and test

Start with [`README.md`](../README.md), then read
[`CURRENT_STATUS.md`](CURRENT_STATUS.md). The regression suite is:

```bash
python -m pytest -q
```

## Regenerate one figure and one results file

From a disposable fresh clone only, run:

```bash
python real_seedling_sim.py
```

This script reads the committed `results/fit_fig1c.csv` and measured data;
it does not refit the 48 trajectories. It writes the predicted protocol
summary to `results/real_seedling_protocols.csv` and the dashboard to
`results/figures/real_seedlings_dashboard.png`. The command can replace
those two files in the clone. The consolidation verification was run only
in a temporary fresh clone; no regenerated output was committed to this
working branch.

## Verification record

The exact command, elapsed time, and output comparison for the one
regeneration check are recorded in
[`CONSOLIDATION_2026-11-26.md`](CONSOLIDATION_2026-11-26.md). Use the saved
reports for scientific values; the quickstart is not a new analysis.
