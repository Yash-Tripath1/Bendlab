"""Unified repository-wide regression suite for BendLab.

Covers:
  1. Core model contract (sim.py: clip after lag update, scalar vs batch)
  2. Model v2 exact reductions (sim_gamma.py, sim_clock_gamma.py incl. k0 < 0.01)
  3. Multi-segment stem extension exact reduction (sim_multiseg.py at zeta = 0)
  4. Data contract, SHA-256 checksums, and multi-sheet trajectory non-collision
  5. Strict RFC 8259 JSON validity across canonical outputs
  6. GitHub Pages build parity (build_site.py) & JS <-> Python bit-exact parity
  7. Markdown relative-link and control-character hygiene
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import build_site  # noqa: E402
import fit_real  # noqa: E402
import sim  # noqa: E402
import sim_clock_gamma  # noqa: E402
import sim_gamma  # noqa: E402
from data_real import DATA_FILE, curves, load_long  # noqa: E402


# ---------------------------------------------------------------------------
# 1. Core model contract (sim.py)
# ---------------------------------------------------------------------------
def test_model_contract_cap_and_inertia():
    _, th = sim.simulate(
        k=10.0, tau=0.5, max_rate=2.0,
        phi_fn=sim.static_light(80.0), t_end=24.0,
    )
    rates = np.diff(th) / sim.DEFAULT_DT
    assert np.max(np.abs(rates)) <= 2.0 + 1e-9
    assert np.max(np.abs(rates)) > 1.99

    _, th_rev = sim.simulate(
        k=10.0, tau=0.5, max_rate=2.0,
        phi_fn=sim.flip_light(80.0, -80.0, 6.0), t_end=24.0,
    )
    rates_rev = np.diff(th_rev) / sim.DEFAULT_DT
    i_flip = int(round(6.0 / sim.DEFAULT_DT))
    assert th_rev[i_flip] > 5.0
    assert rates_rev[i_flip] > 0.0, "bend rate must show lag inertia at flip"
    assert rates_rev[-1] < 0.0
    assert th_rev[-1] < th_rev[i_flip]


def test_scalar_batch_and_fitter_integrator_parity():
    params = [(10.0, 2.0, 30.0, 50.0), (25.0, 0.5, 8.0, 35.0), (0.001, 1.0, 30.0, 45.0)]
    ks, taus, mrs, phis = map(np.array, zip(*params))
    t_b, th_b = sim.batch_simulate(ks, taus, mrs, phis, None, 24.0, record_dt=0.5)
    for j, (k, tau, mr, phi) in enumerate(params):
        t_s, th_s = sim.simulate(k, tau, mr, sim.static_light(phi), 24.0)
        assert np.max(np.abs(th_s[::30] - th_b[:, j])) < 1e-12
        th_f = fit_real.run_model(k, tau, mr, phi, t_b)
        assert np.max(np.abs(th_f - th_b[:, j])) < 1e-12


# ---------------------------------------------------------------------------
# 2. Model v2 candidates (sim_gamma.py, sim_clock_gamma.py)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "k,tau,mr,phi",
    [
        (10.0, 2.0, 30.0, 50.0),
        (40.77, 4.37, 7.39, 45.3),
        (1e-3, 1.0, 30.0, 45.0),   # below K_EFF_FLOOR = 0.01
        (0.0, 1.0, 30.0, 45.0),    # zero gain edge case
    ],
)
def test_model_v2_exact_reduction_to_sim(k, tau, mr, phi):
    _, ref = sim.simulate(k, tau, mr, sim.static_light(phi), 24.0)
    _, g0 = sim_gamma.simulate(k, tau, mr, sim.static_light(phi), 24.0, gamma=0.0)
    _, c0 = sim_clock_gamma.simulate(
        k, tau, mr, sim.static_light(phi), 24.0, gamma=0.0, a=0.0
    )
    assert np.array_equal(ref, g0)
    assert np.array_equal(ref, c0)

    _, cb = sim_clock_gamma.batch_simulate_static(
        np.array([k]), np.array([tau]), np.array([mr]), np.array([phi]),
        24.0, record_dt=0.5, gamma=0.0, a=0.0,
    )
    assert np.max(np.abs(ref[::30] - cb[:, 0])) < 1e-12


def test_clock_gamma_zt9_1_anchor():
    df = load_long(sheet="Fig1C")
    t, y = curves(df)["Fig1C/ZT9-1"]
    te = t - t[0]

    ts_c, th_c = sim_clock_gamma.simulate(
        4.74, 0.10, 75.3, sim.static_light(56.4), float(te[-1]),
        gamma=0.0, a=0.90, phase=7.6, ZT_start=9.0,
    )
    rmse_clock = float(np.sqrt(np.mean((np.interp(te, ts_c, th_c) - y) ** 2)))
    assert abs(rmse_clock - 3.204) < 0.01


# ---------------------------------------------------------------------------
# 3. Multi-segment shape extension exact reduction
# ---------------------------------------------------------------------------
def test_multiseg_exact_reduction():
    ms_dir = ROOT / "04_shape_extension_branch"
    sys.path.insert(0, str(ms_dir))
    try:
        import sim_multiseg  # type: ignore
    finally:
        sys.path.remove(str(ms_dir))

    _, ref = sim.simulate(12.0, 1.5, 15.0, sim.static_light(50.0), 24.0)
    _, segs_c0 = sim_multiseg.simulate(12.0, 1.5, 15.0, 0.0, sim.static_light(50.0), 24.0)
    _, segs_unif = sim_multiseg.simulate(
        12.0, 1.5, 15.0, 1.0, sim.static_light(50.0), 24.0, zeta=0.0
    )
    assert np.max(np.abs(segs_c0 - ref[:, None])) == 0.0
    assert np.max(np.abs(segs_unif - ref[:, None])) == 0.0


# ---------------------------------------------------------------------------
# 4. Data contract, checksums, and multi-sheet trajectory non-collision
# ---------------------------------------------------------------------------
def test_s13_checksum_and_sheet_separation():
    digest = hashlib.sha256((ROOT / DATA_FILE).read_bytes()).hexdigest()
    assert digest == "1257f4069f4fb600d0bddb616110772af28552dc43ad330c18aa3dea58a590b7"

    raw = load_long()
    all_curves = curves(raw)
    # 5 sheets: Fig1B (3) + Fig1C (48) + Fig2B (6) + Fig4A (17) + Fig4J (15) = 89
    assert len(all_curves) == 89
    assert "Fig1B/plant 1" in all_curves and "Fig2B/plant 1" in all_curves
    assert len(all_curves["Fig1B/plant 1"][0]) != len(all_curves["Fig2B/plant 1"][0])

    fits = pd.read_csv(ROOT / "results" / "fit_fig1c.csv")
    assert len(fits) == 48
    assert int((fits["at_bound"] != "[]").sum()) == 4
    assert abs(float(fits["rmse"].median()) - 1.801) < 0.005


def test_growth_phase_sha256_manifest():
    manifest = ROOT / "growth_phase" / "SHA256SUMS.txt"
    lines = [ln.strip() for ln in manifest.read_text().splitlines() if ln.strip()]
    assert len(lines) >= 35
    for ln in lines:
        expected, rel = ln.split(None, 1)
        target = ROOT / "growth_phase" / rel.strip()
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        assert actual == expected, f"SHA-256 mismatch for {target}"


# ---------------------------------------------------------------------------
# 5. Strict RFC 8259 JSON validity (no literal NaN / Infinity)
# ---------------------------------------------------------------------------
def test_canonical_json_outputs_are_strict_rfc8259():
    json_paths = (
        list((ROOT / "results").rglob("*.json"))
        + list((ROOT / "02_workstream_A_external_benchmark").rglob("*.json"))
        + [ROOT / "03_workstream_B_shape_extension_audit" / "workstream_b" / "corrected_audit_results_v2.json"]
        + list((ROOT / "growth_phase" / "outputs").rglob("*.json"))
    )
    assert len(json_paths) >= 15

    def _forbid_nonstandard(token: str):
        raise ValueError(f"Non-RFC8259 JSON constant: {token}")

    for p in json_paths:
        json.loads(p.read_text(encoding="utf-8"), parse_constant=_forbid_nonstandard)


# ---------------------------------------------------------------------------
# 6. Website build sync, UI regression guards & JS <-> Python parity
# ---------------------------------------------------------------------------
def test_site_build_sync_and_ui_guards():
    for src, dst, key, width in build_site.PAGES:
        src_html = (ROOT / src).read_text(encoding="utf-8")
        expected = src_html.replace("</style>", build_site.NAV_CSS + "</style>", 1)
        expected = expected.replace("<body>", "<body>\n" + build_site.nav(key, width), 1)
        actual = (ROOT / dst).read_text(encoding="utf-8")
        assert actual == expected, f"{dst} is out of sync with {src}; run python build_site.py"
        assert 'banner.style.display = "none"' not in src_html, (
            f"{src} sets inline display:none on banner, permanently hiding subsequent warnings"
        )

    sim_html = (ROOT / "bendlab_visual_simulator.html").read_text(encoding="utf-8")
    assert "response gain · °/h" in sim_html


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_js_simulators_bit_exact_with_python():
    _, py_th = sim.simulate(10.0, 0.5, 2.0, sim.static_light(80.0), 24.0)
    js_driver = r"""
    const fs = require("fs");
    const vm = require("vm");
    const py = JSON.parse(process.argv[1]);
    for (const fn of ["bendlab_curve_fitter.html", "bendlab_model_demo.html"]) {
      const html = fs.readFileSync(fn, "utf8");
      const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
      const ctx = vm.createContext({ Math, Number, Array, Object, Float64Array, JSON, console });
      for (const s of scripts) vm.runInContext(s, ctx);
      vm.runInContext("globalThis._dense = simulateDense([10.0, 0.5, 2.0, 80.0]);", ctx);
      const d = Array.from(ctx._dense);
      let maxDiff = 0;
      for (let i = 0; i < py.length; i++) maxDiff = Math.max(maxDiff, Math.abs(d[i] - py[i]));
      if (maxDiff > 1e-12) {
        console.error(fn, "drift:", maxDiff);
        process.exit(1);
      }
    }
    """
    subprocess.run(
        ["node", "-e", js_driver, json.dumps(py_th.tolist())],
        cwd=ROOT,
        check=True,
    )


# ---------------------------------------------------------------------------
# 7. Documentation hygiene (no stray control chars, broken links, or URL typos)
# ---------------------------------------------------------------------------
def test_markdown_hygiene_and_relative_links():
    md_files = (
        list(ROOT.glob("*.md"))
        + list((ROOT / "docs").glob("*.md"))
        + list((ROOT / "02_workstream_A_external_benchmark").glob("*.md"))
        + list((ROOT / "03_workstream_B_shape_extension_audit").glob("*.md"))
        + list((ROOT / "growth_phase").glob("*.md"))
    )
    link_re = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for md in md_files:
        txt = md.read_text(encoding="utf-8")
        assert "Yash-Tripathi/" not in txt, f"Broken GitHub username typo in {md}"
        bad_ctrl = [ch for ch in txt if ord(ch) < 32 and ch not in ("\n", "\r")]
        assert not bad_ctrl, f"Unexpected control char {bad_ctrl!r} in {md}"
        for raw_target in link_re.findall(txt):
            target = raw_target.strip().split()[0].split("#")[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (md.parent / target).resolve()
            assert resolved.exists(), f"Broken link {raw_target!r} in {md}"
