"""Phase A: audit and join the Kempinski length supplement to the
unilateral trajectories. Data auditing only; no outcome fitting.

Inputs (Zenodo record 21206480, md5 06d911cc56c6cf92d66af15304bb93f9):
  data/00_Data/uni_trajectories.csv
  data/07_Supplementary/length_est_data.csv  (+ length_est.py for units)
Outputs: outputs/paired_plants.csv, outputs/phase_a_audit.json
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)


def main():
    U = pd.read_csv(DATA / "00_Data" / "uni_trajectories.csv")
    Lraw = pd.read_csv(DATA / "07_Supplementary" / "length_est_data.csv")
    audit = {}

    # duplicate resolution: the 11_11_L_5 pair is an EXACT duplicate row
    # (identical values), so deduplication loses no information.
    dup_ids = Lraw[Lraw.real_id.duplicated(keep=False)].real_id.unique()
    exact = all(Lraw[Lraw.real_id == i].drop(columns=["Unnamed: 0"])
                .drop_duplicates().shape[0] == 1 for i in dup_ids)
    audit["duplicate_ids"] = list(dup_ids)
    audit["duplicates_are_exact_copies"] = bool(exact)
    L = Lraw.drop_duplicates(subset=[c for c in Lraw.columns
                                     if c != "Unnamed: 0"])

    first = U.sort_values("dt").groupby("real_id").first()
    last_t = U.groupby("real_id")["dt"].max()
    base = pd.DataFrame({
        "light_i": first["light_i"],
        "theta0_deg": first["theta"],
        "traj_duration_h": last_t,
        "n_points": U.groupby("real_id").size()})
    base["side"] = [i.split("_")[2] for i in base.index]

    m = base.join(L.set_index("real_id")[
        ["dt", "length_start", "length_finish", "light_intens"]],
        how="left")
    m = m.rename(columns={"dt": "length_dt_h",
                          "length_start": "L0_mm",
                          "length_finish": "Lfinish_mm"})
    m["has_length"] = m["L0_mm"].notna()
    m["light_conversion_ok"] = np.isclose(
        m["light_intens"] / 100.0, m["light_i"])
    m["net_growth_mm"] = m["Lfinish_mm"] - m["L0_mm"]
    m["growth_speed_mm_h"] = m["net_growth_mm"] / m["length_dt_h"]
    m["length_window_minus_traj_h"] = m["length_dt_h"] - m["traj_duration_h"]
    m = m.reset_index().rename(columns={"index": "real_id"})
    m.to_csv(OUT / "paired_plants.csv", index=False)

    audit.update({
        "trajectory_plants": int(base.shape[0]),
        "length_rows_raw": int(len(Lraw)),
        "length_unique_ids": int(Lraw.real_id.nunique()),
        "matched_plants": int(m.has_length.sum()),
        "unmatched_plants": int((~m.has_length).sum()),
        "length_only_ids_not_in_unilateral": int(
            len(set(L.real_id) - set(base.index))),
        "intensity_conversion_/100_matches_all_matched": bool(
            m.loc[m.has_length, "light_conversion_ok"].all()),
        "L0_mm_median_range": [float(m.L0_mm.median()),
                               float(m.L0_mm.min()), float(m.L0_mm.max())],
        "length_window_minus_traj_h_median_range": [
            float(m.length_window_minus_traj_h.median()),
            float(m.length_window_minus_traj_h.min()),
            float(m.length_window_minus_traj_h.max())],
        # has_length.mean() is COVERAGE (fraction with a length
        # record); missingness is 1 - coverage. The v1 output labelled
        # the coverage values "missingness"; corrected 2026-10-24
        # (audit point 5), v1 preserved as phase_a_audit_v1.json.
        "coverage_by_intensity": (
            m.groupby("light_i")["has_length"].mean().round(3)
            .to_dict()),
        "missingness_by_intensity": (
            (1 - m.groupby("light_i")["has_length"].mean()).round(3)
            .to_dict()),
        "coverage_by_side": (
            m.groupby("side")["has_length"].mean().round(3).to_dict()),
        "missingness_by_side": (
            (1 - m.groupby("side")["has_length"].mean()).round(3)
            .to_dict()),
        "units": "lengths in mm per archive length_est.py; growth speed mm/h",
        "timing_caveat": ("length interval is typically ~0.9 h longer than "
                          "the angle trajectory (median); net growth is an "
                          "interval-average over its own window"),
    })
    (OUT / "phase_a_audit.json").write_text(json.dumps(audit, indent=2))
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
