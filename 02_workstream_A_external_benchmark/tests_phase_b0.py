"""Phase B0 reproducibility tests (run: python tests_phase_b0.py).

Covers: leakage-safe split integrity (Workstream A), the angle/intensity
conventions used by the benchmark wrapper, and the corrected
s_shape_sign_changes semantics (Workstream B). These tests check the
Phase B0 analysis code only; they do not modify either repository.
"""

import sys

import numpy as np

sys.path.insert(0, "/home/user/phase_b0/workstream_a")
sys.path.insert(0, "/home/user/phase_b0/workstream_b")
sys.path.insert(0, "/home/user/phase_b0/shape_repo")

from phase_b0_kempinski_benchmark import load_plants, stratified_folds  # noqa: E402
from shape_audit_corrected_v1 import buggy_s_shape, corrected_s_shape  # noqa: E402

DATA = "/home/user/phase_b0/zenodo/extracted/00_Data/uni_trajectories.csv"


def test_splits_are_plant_disjoint_and_stratified():
    _, plants = load_plants(DATA)
    folds = stratified_folds(plants, n_folds=5, seed=42)
    seen = [i for f in folds for i in f]
    assert sorted(seen) == list(range(len(plants))), "plant in two folds"
    intensities = {p["I"] for p in plants}
    for f in folds:
        assert {plants[i]["I"] for i in f} == intensities, \
            "fold missing an intensity group (stratification broken)"
    print("ok: plant-held-out folds are disjoint and cover all intensities")


def test_each_plant_has_one_intensity():
    _, plants = load_plants(DATA)
    assert len(plants) == 268
    assert all(np.isfinite(p["theta"]).all() for p in plants)
    print("ok: 268 plants, one intensity each, no NaN trajectories")


def test_corrected_s_shape_semantics():
    # S-bend along the stem, constant in time: kappa = (+10, -5, +10, +15)
    th = np.zeros((10, 1, 5))
    th[:, :, 1], th[:, :, 2], th[:, :, 3], th[:, :, 4] = 10, 5, 15, 30
    assert corrected_s_shape(th)[0] == 2.0
    assert buggy_s_shape(th)[0] == 0.0, "submitted feature sees no S-bend"
    # Pure temporal sign flip of one joint, no spatial S at any time
    th2 = np.zeros((10, 1, 5))
    th2[:5, :, 4], th2[5:, :, 4] = 20, -20
    assert corrected_s_shape(th2)[0] == 0.0
    assert buggy_s_shape(th2)[0] > 0, "submitted feature counts time flips"
    print("ok: corrected feature counts joint-axis sign changes; "
          "submitted feature counts time-axis sign flips")


if __name__ == "__main__":
    test_splits_are_plant_disjoint_and_stratified()
    test_each_plant_has_one_intensity()
    test_corrected_s_shape_semantics()
    print("ALL PHASE B0 TESTS PASSED")
