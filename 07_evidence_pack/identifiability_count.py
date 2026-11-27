#!/usr/bin/env python3
"""Reconcile the two committed max_rate identifiability operationalizations.

This script reads the saved Fig1C fits, the saved Phase A uncertainty table,
and the committed S13 workbook. It does not call an optimizer or rerun a fit.
The direct observed-peak criterion is the existing canonical feature definition:
maximum absolute adjacent-sample angle difference divided by the uniform
sampling interval, in degrees per hour.

Run from any directory with:
    python 07_evidence_pack/identifiability_count.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "01_canonical_bendlab"
sys.path.insert(0, str(CANONICAL))

from data_real import curves, load_long  # noqa: E402
from features import peak_rate  # noqa: E402

FIT_FILE = CANONICAL / "results/fit_fig1c.csv"
UNCERTAINTY_FILE = CANONICAL / "results/phaseA_fit_uncertainty.csv"
SUMMARY_FILE = CANONICAL / "results/phaseA_summary.json"
DATA_FILE = CANONICAL / "data/real/stem_angles_plosbiol2023_s13.xlsx"
OUTPUT_FILE = ROOT / "07_evidence_pack/outputs/identifiability_count.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    fits = pd.read_csv(FIT_FILE)
    uncertainty = pd.read_csv(UNCERTAINTY_FILE)
    summary = json.loads(SUMMARY_FILE.read_text(encoding="utf-8"))
    curves_by_plant = curves(load_long(str(DATA_FILE), sheet="Fig1C"))

    require(len(fits) == 48, f"Expected 48 saved fits, found {len(fits)}")
    require(fits["plant"].is_unique, "Saved fit plant IDs are not unique")
    require(len(uncertainty) == 48, "Expected 48 saved Phase A uncertainty rows")
    require(uncertainty["plant"].is_unique, "Uncertainty plant IDs are not unique")
    require(set(fits["plant"]) == set(uncertainty["plant"]),
            "Fit and uncertainty plant IDs differ")

    fit_by_plant = fits.set_index("plant")
    uncertainty_by_plant = uncertainty.set_index("plant")
    rows: list[dict[str, object]] = []
    for curve_key, (times, angles) in sorted(curves_by_plant.items()):
        plant = curve_key.split("/", 1)[1]
        require(plant in fit_by_plant.index,
                f"No saved fit for observed plant {plant}")
        intervals = np.diff(times)
        require(len(intervals) > 0 and np.all(intervals > 0),
                f"Invalid time grid for {plant}")
        require(np.allclose(intervals, intervals[0], rtol=0.0, atol=1e-9),
                f"Nonuniform sampling for {plant}; canonical peak_rate assumes uniform sampling")
        observed_peak = peak_rate(times, angles)
        fitted_cap = float(fit_by_plant.loc[plant, "max_rate"])
        jacobian_flag = not np.isfinite(
            float(uncertainty_by_plant.loc[plant, "max_rate_rel_se"])
        )
        rows.append({
            "plant": plant,
            "fitted_max_rate_deg_h": fitted_cap,
            "observed_peak_adjacent_rate_deg_h": float(observed_peak),
            "cap_minus_observed_peak_deg_h": float(fitted_cap - observed_peak),
            "fitted_cap_exceeds_observed_peak": bool(fitted_cap > observed_peak),
            "cap_at_or_below_observed_peak": bool(fitted_cap <= observed_peak),
            "phase_a_jacobian_zero_sensitivity_flag": bool(jacobian_flag),
        })

    rows.sort(key=lambda row: str(row["plant"]))
    above = [row for row in rows if row["fitted_cap_exceeds_observed_peak"]]
    at_or_below = [row for row in rows if row["cap_at_or_below_observed_peak"]]
    jacobian_flags = [row for row in rows
                      if row["phase_a_jacobian_zero_sensitivity_flag"]]
    phase_a_summary_count = int(
        summary["fit_uncertainty_unidentified_counts"]["max_rate"]
    )
    require(len(above) == 40, f"Expected direct criterion 40/48, found {len(above)}")
    require(len(at_or_below) == 8, f"Expected 8 at-or-below cases, found {len(at_or_below)}")
    require(len(jacobian_flags) == 47,
            f"Expected Phase A Jacobian flag 47/48, found {len(jacobian_flags)}")
    require(phase_a_summary_count == len(jacobian_flags),
            "Saved Phase A summary and uncertainty rows disagree")
    require({str(row["plant"]) for row in at_or_below} == {
        "ZT0-2", "ZT0-3", "ZT0-6", "ZT0-7", "ZT3-4", "ZT3-8", "ZT6-7", "ZT6-8"
    }, "Direct cap-at-or-below plant IDs differ from the audit specification")

    result = {
        "analysis": "Saved-fit rate-cap identifiability reconciliation",
        "model_fits_rerun": False,
        "n_plants": len(rows),
        "direct_observed_peak_rate_criterion": {
            "definition": (
                "fitted max_rate exceeds the plant's maximum absolute adjacent-sample "
                "observed angle change divided by the uniform sampling interval"
            ),
            "feature_implementation": "01_canonical_bendlab/features.py::peak_rate",
            "smoothing": "none; raw adjacent observations",
            "units": "degrees per hour",
            "fitted_cap_above_observed_peak_count": len(above),
            "fitted_cap_above_observed_peak_fraction": len(above) / len(rows),
            "cap_at_or_below_observed_peak_count": len(at_or_below),
            "cap_at_or_below_observed_peak_plants": [row["plant"] for row in at_or_below],
        },
        "historical_phase_a_jacobian_criterion": {
            "definition": (
                "part2_uncertainty in phase_a.py sets max_rate SE to infinity when "
                "the fitted residual Jacobian column norm is below 1e-9; the summary "
                "counts non-finite max_rate relative SE values"
            ),
            "saved_uncertainty_table_count": len(jacobian_flags),
            "saved_phase_a_summary_count": phase_a_summary_count,
            "jacobian_flagged_plants": [row["plant"] for row in jacobian_flags],
        },
        "interpretation": (
            "The 47/48 Jacobian-based count is reproducible from committed code and "
            "output. It is not the same estimand as the direct comparison with each "
            "plant's observed maximum adjacent-sample rate, which yields 40/48."
        ),
        "inputs": {
            "fit_csv": str(FIT_FILE.relative_to(ROOT)),
            "uncertainty_csv": str(UNCERTAINTY_FILE.relative_to(ROOT)),
            "phase_a_summary_json": str(SUMMARY_FILE.relative_to(ROOT)),
            "observed_workbook": str(DATA_FILE.relative_to(ROOT)),
        },
        "per_plant": rows,
    }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        "Direct observed-peak criterion: 40/48 fitted caps above observed peak; "
        "8/48 at or below. Phase A Jacobian criterion: 47/48 flagged."
    )
    print(f"Wrote {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
