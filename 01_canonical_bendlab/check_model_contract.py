#!/usr/bin/env python3
"""Regression checks for the model contract in PROBLEM_STATEMENT.md.

The contract is the discrete update implemented by sim.py: the bend
rate relaxes toward the stimulus, and the rate cap is applied to the
bend rate AFTER each lag update (not to the stimulus before the lag).
These checks exercise a cap-binding trajectory followed by a light
reversal, the regime where the two possible clip orderings differ.
"""
from __future__ import annotations

import numpy as np

from sim import DEFAULT_DT, flip_light, simulate, static_light


def rates(thetas: np.ndarray) -> np.ndarray:
    return np.diff(thetas) / DEFAULT_DT


def main() -> None:
    # 1. The bend rate never exceeds the cap, even under a strong stimulus.
    _, th = simulate(k=10.0, tau=0.5, max_rate=2.0,
                     phi_fn=static_light(80.0), t_end=24.0)
    r = rates(th)
    assert np.max(np.abs(r)) <= 2.0 + 1e-9, np.max(np.abs(r))
    assert np.max(np.abs(r)) > 1.99, "test case must actually bind the cap"
    print("1. cap binds and is never exceeded: OK")

    # 2. After a light reversal, the plant keeps bending briefly in the
    #    old direction (rate inertia from the lag), then bends back.
    _, th = simulate(k=10.0, tau=0.5, max_rate=2.0,
                     phi_fn=flip_light(80.0, -80.0, 6.0), t_end=24.0)
    r = rates(th)
    i_flip = int(round(6.0 / DEFAULT_DT))
    assert th[i_flip] > 5.0, "plant should have bent toward the first light"
    assert r[i_flip] > 0.0, "rate should not reverse instantaneously"
    assert r[-1] < 0.0, "rate should eventually reverse"
    assert th[-1] < th[i_flip], "stem should bend back after reversal"
    print("2. cap-binding reversal shows lag inertia, then bends back: OK")

    # 3. With the cap effectively absent, the same code follows the
    #    unclipped first-order lag (sanity check on the update itself).
    _, th = simulate(k=2.0, tau=2.0, max_rate=1e9,
                     phi_fn=static_light(45.0), t_end=24.0)
    assert np.all(np.diff(th) >= -1e-12), "static positive light: monotone bend"
    assert 20.0 < th[-1] < 45.0
    print("3. unclipped lag response is monotone toward the light: OK")

    print("ALL MODEL CONTRACT CHECKS PASSED")


if __name__ == "__main__":
    main()
