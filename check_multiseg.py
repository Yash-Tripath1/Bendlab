"""Regression checks for the multi-segment shape-extension simulator.

Verifies, for a small grid of parameter sets, that:
  1. sim_multiseg.simulate with c = 0 reproduces sim.simulate exactly
     (every segment; exact equality, not a tolerance);
  2. sim_multiseg.simulate from a uniform initial state reproduces
     sim.simulate exactly for any c (the coupling torque is zero while
     the stem is straight and uniform);
  3. sim_multiseg.batch_simulate agrees with simulate under static light
     to floating-point round-off;
  4. simulate is deterministic (two runs bit-identical);
  5. the rate cap binds as specified: |theta increment| never exceeds
     max_rate * dt, on a deliberately cap-binding case.

Run: python check_multiseg.py   (exit code 0 = all checks pass)
"""

from __future__ import annotations

import sys

import numpy as np

import sim
import sim_multiseg as SM
from sim import static_light

# Same case grid as check_model_v2.py, plus c values spanning the declared
# coupling range of the shape extension (see docs/SHAPE_EXTENSION.md).
CASES = [(10.0, 2.0, 30.0, 50.0), (25.0, 0.5, 8.0, 35.0), (5.0, 6.0, 100.0, 70.0),
         (40.77, 4.37, 7.39, 45.3)]  # last: ZT3-8, the cap-binding fit
C_VALUES = [0.0, 0.35, 1.0]


def main():
    ok = True

    # Check 1: c = 0 must reduce to sim.simulate EXACTLY, every segment.
    for k, tau, mr, phi in CASES:
        _, ref = sim.simulate(k, tau, mr, static_light(phi), 24.0)
        _, th = SM.simulate(k, tau, mr, 0.0, static_light(phi), 24.0)
        d = float(np.abs(th - ref[:, None]).max())
        print("c=0 reduction    k=%-6g tau=%-4g max diff %.2e" % (k, tau, d))
        ok &= (d == 0.0)

    # Check 2: uniform start is invariant to c (laplacian stays zero).
    for k, tau, mr, phi in CASES:
        _, ref = sim.simulate(k, tau, mr, static_light(phi), 24.0)
        for c in C_VALUES[1:]:
            _, th = SM.simulate(k, tau, mr, c, static_light(phi), 24.0)
            d = float(np.abs(th - ref[:, None]).max())
            print("uniform invariant c=%.2f k=%-6g max diff %.2e" % (c, k, d))
            ok &= (d == 0.0)

    # Check 3: batch vs single, coupling active and stem free to curve.
    ks = np.array([c[0] for c in CASES])
    taus = np.array([c[1] for c in CASES])
    mrs = np.array([c[2] for c in CASES])
    phis = np.array([c[3] for c in CASES])
    cs = np.array([0.2, 0.6, 1.0, 0.4])
    times, batch = SM.batch_simulate_static(ks, taus, mrs, phis, cs, 24.0,
                                            record_dt=0.5, n_seg=5)
    for i in range(len(CASES)):
        _, single = SM.simulate(ks[i], taus[i], mrs[i], cs[i],
                                static_light(phis[i]), 24.0, n_seg=5)
        single_rec = single[::30]  # dt=1/60 -> every 0.5 h
        d = float(np.abs(batch[:, i, :] - single_rec).max())
        print("batch vs single  plant %d max diff %.2e" % (i, d))
        ok &= d < 1e-9

    # Check 4: determinism.
    _, run1 = SM.simulate(*CASES[0][:2], CASES[0][2], 0.8,
                          static_light(CASES[0][3]), 24.0)
    _, run2 = SM.simulate(*CASES[0][:2], CASES[0][2], 0.8,
                          static_light(CASES[0][3]), 24.0)
    det = bool(np.array_equal(run1, run2))
    print("determinism      bit-identical: %s" % det)
    ok &= det

    # Check 5: rate cap binding (low cap, strong drive): per-step angle
    # increment must never exceed max_rate * dt.
    mr = 3.0
    dt = SM.DEFAULT_DT
    _, th = SM.simulate(40.0, 0.5, mr, 1.0, static_light(80.0), 24.0)
    step = np.abs(np.diff(th, axis=0)).max()
    print("cap binding      max step %.4f deg vs cap*dt %.4f deg"
          % (step, mr * dt))
    ok &= step <= mr * dt + 1e-12

    # Check 6: zeta = 0 explicitly keeps the uniform invariant (exact),
    # and zeta = 0 with c = 0 keeps the exact sim.py reduction.
    for k, tau, mr, phi in CASES:
        _, ref = sim.simulate(k, tau, mr, static_light(phi), 24.0)
        _, th_u = SM.simulate(k, tau, mr, 0.7, static_light(phi), 24.0,
                              zeta=0.0)
        _, th_r = SM.simulate(k, tau, mr, 0.0, static_light(phi), 24.0,
                              zeta=0.0)
        d = max(float(np.abs(th_u - ref[:, None]).max()),
                float(np.abs(th_r - ref[:, None]).max()))
        print("zeta=0 exact     k=%-6g max diff %.2e" % (k, d))
        ok &= (d == 0.0)

    # Check 7: zeta > 0 must develop curvature (the shape channel opens):
    # joints separate and tip diverges from base on a bending stem.
    _, th = SM.simulate(2.0, 1.0, 20.0, 0.5, static_light(60.0), 24.0,
                        zeta=0.8)
    curv = float(np.abs(SM.joint_curvatures(th)).max())
    sep = float(abs(th[-1, -1] - th[-1, 0]))
    print("zeta=0.8 shape   max |kappa| %.3f deg | tip-base %.3f deg"
          % (curv, sep))
    ok &= (curv > 0.5 and sep > 0.5)

    # Check 8: batch vs single with zeta active.
    _, single = SM.simulate(2.0, 1.0, 20.0, 0.5, static_light(60.0), 24.0,
                            zeta=0.8)
    times, batch = SM.batch_simulate_static(
        np.array([2.0]), np.array([1.0]), np.array([20.0]),
        np.array([60.0]), np.array([0.5]), 24.0, record_dt=0.5,
        n_seg=5, zeta=0.8)
    d = float(np.abs(batch[:, 0, :] - single[::30]).max())
    print("batch vs single  zeta=0.8 max diff %.2e" % d)
    ok &= d < 1e-9

    print("ALL CHECKS PASSED" if ok else "CHECKS FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
