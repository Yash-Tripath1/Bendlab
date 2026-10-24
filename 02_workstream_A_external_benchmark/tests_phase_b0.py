"""Phase B0 reproducibility tests (portable; run from a clean checkout):

    python tests_phase_b0.py

All paths are resolved relative to this file. Covers leakage-safe split
integrity (Workstream A), the per-plant single-intensity condition, and
the corrected s_shape_sign_changes semantics (Workstream B). These tests
check Phase B0 analysis code only; they do not modify either repository.
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PKG_ROOT = HERE.parent                                # repository root
WS_A = HERE / "workstream_a"
WS_B = PKG_ROOT / "03_workstream_B_shape_extension_audit" / "workstream_b"
SHAPE_BRANCH = PKG_ROOT / "04_shape_extension_branch"
DATA = PKG_ROOT / "05_data_external" / "uni_trajectories.csv"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_each_plant_has_one_intensity():
    """Every real_id maps to exactly one light_i value (audit item A4)."""
    df = pd.read_csv(DATA)
    nun = df.groupby("real_id")["light_i"].nunique()
    assert (nun == 1).all(), \
        f"{int((nun != 1).sum())} plants have multiple intensity values"
    assert df["real_id"].nunique() == 268
    print("ok: every one of the 268 plants has exactly one intensity group")


def test_splits_are_plant_disjoint_and_stratified():
    bench = _load("bench", WS_A / "phase_b0_kempinski_benchmark.py")
    _, plants = bench.load_plants(DATA)
    folds = bench.stratified_folds(plants, n_folds=5, seed=42)
    seen = [i for f in folds for i in f]
    assert sorted(seen) == list(range(len(plants))), "plant in two folds"
    intensities = {p["I"] for p in plants}
    for f in folds:
        assert {plants[i]["I"] for i in f} == intensities, \
            "fold missing an intensity group (stratification broken)"
    print("ok: plant-held-out folds are disjoint and cover all intensities")


def test_corrected_s_shape_semantics():
    sys.path.insert(0, str(WS_B))
    sys.path.insert(0, str(SHAPE_BRANCH))
    audit = _load("shape_audit", WS_B / "shape_audit_corrected_v2.py")
    # S-bend along the stem, constant in time: kappa = (+10, -5, +10, +15)
    th = np.zeros((10, 1, 5))
    th[:, :, 1], th[:, :, 2], th[:, :, 3], th[:, :, 4] = 10, 5, 15, 30
    assert audit.corrected_s_shape(th)[0] == 2.0
    assert audit.buggy_s_shape(th)[0] == 0.0, "submitted feature sees no S-bend"
    # Pure temporal sign flip of one joint, no spatial S at any time
    th2 = np.zeros((10, 1, 5))
    th2[:5, :, 4], th2[5:, :, 4] = 20, -20
    assert audit.corrected_s_shape(th2)[0] == 0.0
    assert audit.buggy_s_shape(th2)[0] > 0, "submitted feature counts time flips"
    print("ok: corrected feature counts joint-axis sign changes; "
          "submitted feature counts time-axis sign flips")


if __name__ == "__main__":
    test_each_plant_has_one_intensity()
    test_splits_are_plant_disjoint_and_stratified()
    test_corrected_s_shape_semantics()
    print("ALL PHASE B0 TESTS PASSED")
