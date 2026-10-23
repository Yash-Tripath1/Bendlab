"""Read the PLOS S13 stem-angle file into tidy long form.

Keeps the sheet of origin, because sheets differ in sampling rate and time
base and must not be silently concatenated.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DATA_FILE = "data/real/stem_angles_plosbiol2023_s13.xlsx"


def load_long(path: str = DATA_FILE, sheet: str | None = None) -> pd.DataFrame:
    """Return columns: sheet, plant, block, t, angle."""
    xl = pd.ExcelFile(path)
    sheets = xl.sheet_names if sheet is None else [sheet]
    frames = []
    for s in sheets:
        if s == "read.me":
            continue
        df = xl.parse(s)
        tcol = df.columns[0]
        long = df.melt(id_vars=tcol, var_name="plant", value_name="angle")
        long = long.rename(columns={tcol: "t"}).dropna(subset=["angle", "t"])
        long["sheet"] = s
        long["block"] = long["plant"].astype(str).str.split("-").str[0]
        long["plant_n"] = long["plant"].astype(str).str.split("-").str[1]
        frames.append(long[["sheet", "plant", "block", "plant_n", "t", "angle"]])
    out = pd.concat(frames, ignore_index=True)
    return out.sort_values(["sheet", "block", "plant_n", "t"]).reset_index(drop=True)


def curves(df: pd.DataFrame) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Split long form into {plant_label: (t, angle)}."""
    out = {}
    for (sh, plant), g in df.groupby(["sheet", "plant"]):
        g = g.sort_values("t")
        out[f"{sh}/{plant}"] = (g["t"].to_numpy(float), g["angle"].to_numpy(float))
    return out
