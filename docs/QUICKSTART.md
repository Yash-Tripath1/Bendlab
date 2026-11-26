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
those two files in the clone. The successful byte-comparison run below was
performed in a temporary fresh clone, and its outputs were not committed.

## Fresh-clone verification record

The install, test, and regeneration commands in this section were run from
a fresh temporary clone of the active branch at commit `7e54a0a`, using
Python 3.11.2. Installation with `python -m pip install -r requirements.txt`
completed successfully. The README entry point and
[`CURRENT_STATUS.md`](CURRENT_STATUS.md) were read before testing.

`python -m pytest -q` completed with **17 passed in 1.87s**.

The exact artifact-generation command was:

```bash
python real_seedling_sim.py
```

It exited without error in **2.535 seconds**, wrote
`results/real_seedling_protocols.csv` (264 rows), and saved
`results/figures/real_seedlings_dashboard.png`. Both generated files were
byte-for-byte identical to their committed versions. Their SHA-256 values
were `9472329b54ed4e9e4549c0c15a59f4b7e09d39ca119e8664924ccb61a12901a9`
for the CSV and
`5e619a7d829f8359e1623bcc7ec9570446f0f9a5d4bad2f53c5ee9f1fe4dea0c` for
the PNG. The temporary clone was restored to its committed artifacts after
comparison; no generated output was committed to this working branch.

Use the saved reports for scientific values; this quickstart run is a
reproduction check, not a new analysis.
