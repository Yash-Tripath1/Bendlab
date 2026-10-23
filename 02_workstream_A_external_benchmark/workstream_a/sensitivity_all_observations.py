"""Sensitivity check: refit the all-data W1/W2 wrappers using EVERY
observation (module default fits on every 4th point, about 16-minute
spacing, while the archive samples about every 4 minutes).

Compares fitted parameters and in-sample median per-plant RMSE against
the packaged subsampled fit. Run from a packaged checkout:

    python sensitivity_all_observations.py [--data PATH]

Writes sensitivity_all_observations.json next to this script.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import phase_b0_kempinski_benchmark as B


def insample_median_rmse(model, plants, phi_mode):
    pred = B.predict_wrapper(model, list(range(len(plants))), plants)
    rms = [float(np.sqrt(np.mean((pred[p["id"]] - p["theta"]) ** 2)))
           for p in plants]
    return float(np.median(rms))


def main():
    df, plants = B.load_plants(B.DATA)
    out = {}
    for mode in ("fixed90", "phi_of_I"):
        row = {}
        for sub in (4, 1):
            B.SUB = sub                      # module-level fit subsampling
            m = B.fit_wrapper(list(range(len(plants))), plants, mode)
            row[f"sub{sub}"] = {
                "a": m["a"], "b": m["b"], "tau": m["tau"],
                "max_rate": m["max_rate"],
                "phi_params": (list(m["phi_params"])
                               if m["phi_params"] is not None else None),
                "insample_median_rmse_deg": insample_median_rmse(
                    m, plants, mode)}
        out[mode] = row
    dest = Path(__file__).resolve().parent / "sensitivity_all_observations.json"
    dest.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    print("saved", dest)


if __name__ == "__main__":
    main()
