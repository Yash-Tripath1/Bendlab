"""Vector-sum light stimulus comparison for BendLab.

This experiment keeps the BendLab tip-angle dynamics fixed and changes only
how multiple light sources are converted into an effective stimulus.

Models compared
---------------
0. current / physical:  effective direction from the physical vector sum of
   source intensities.
1. transduced-source:   each source intensity is compressed by a power law
   before vector summation, following the sunflower distributed-sensing
   framework reported by Kempinski et al. (2026).
2. circumference:       light is integrated around a discretised stem
   circumference with transmission to the shaded side, transduced locally,
   and then summed vectorially. This is a two-dimensional reduction of the
   distributed-sensing model, used here for stimulus comparison rather than
   as a fitted biological model.

The dynamic update is otherwise the BendLab update: stimulus, first-order
bend-rate relaxation, rate clipping, then angle advance at dt = 1 minute.
"""

from __future__ import annotations

import json
import os
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from generate_plants import PARAM_NAMES, weighted_population
from sim import simulate as py_simulate
from sim import static_light

SEED = 20261014
DT = 1.0 / 60.0
ALPHA = 0.30          # compressive transduction exponent (Kempinski et al.)
TRANSMISSION = 0.10   # light transmission across the stem (Kempinski et al.)
PSI_N = 721

OUT_GRID = "results/vector_stimulus_grid.csv"
OUT_SCEN = "results/vector_stimulus_scenarios.csv"
OUT_POP = "results/vector_stimulus_population.csv"
OUT_SUMMARY = "results/vector_stimulus_summary.json"
OUT_FIG = "results/figures/vector_stimulus_dashboard.png"

MODELS = ("physical", "transduced_source", "circumference")


# --------------------------------------------------------------------------
# Vector helpers. Angles are measured from vertical, in degrees.
# A direction vector is (sin(phi), cos(phi)); the resultant angle is
# atan2(x, y), consistent with that convention.
# --------------------------------------------------------------------------

def unit(phi_deg):
    r = np.deg2rad(np.asarray(phi_deg, dtype=float))
    return np.stack([np.sin(r), np.cos(r)], axis=-1)


def resultant(sources):
    """sources: iterable of (phi_deg, intensity). Returns angle, vector."""
    vec = np.zeros(2)
    for phi, inten in sources:
        vec += float(inten) * unit(phi)
    angle = float(np.rad2deg(np.arctan2(vec[0], vec[1]))) if np.any(vec) else 0.0
    return angle, vec


def physical_stimulus(sources):
    angle, vec = resultant(sources)
    total = sum(float(i) for _, i in sources)
    coherence = float(np.linalg.norm(vec) / total) if total > 0 else 0.0
    return angle, coherence


def transduced_source_stimulus(sources, alpha=ALPHA):
    weighted = [(phi, float(i) ** alpha) for phi, i in sources if i > 0]
    angle, vec = resultant(weighted)
    # Coherence normalisation: one source, or several aligned sources, give
    # g = 1; opposed sources reduce g towards zero.
    denom = sum(w for _, w in weighted)
    coherence = float(np.linalg.norm(vec) / denom) if denom > 0 else 0.0
    return angle, coherence


_PSI = np.linspace(-np.pi, np.pi, PSI_N, endpoint=False)
_PSI_UNIT = np.stack([np.sin(_PSI), np.cos(_PSI)], axis=1)


def _circ_vector(sources, alpha=ALPHA, transmission=TRANSMISSION, psi=_PSI,
                 psi_unit=_PSI_UNIT):
    local = np.zeros(len(psi))
    for phi, inten in sources:
        if inten <= 0:
            continue
        delta = psi - np.deg2rad(float(phi))
        local += float(inten) * (
            np.maximum(np.cos(delta), 0.0)
            + transmission * np.maximum(-np.cos(delta), 0.0)
        )
    transduced = np.power(local, alpha)
    dpsi = float(psi[1] - psi[0])
    return np.sum(transduced[:, None] * psi_unit, axis=0) * dpsi


def _circ_ref(total_intensity, alpha=ALPHA, transmission=TRANSMISSION):
    if total_intensity <= 0:
        return 1.0
    vec = _circ_vector([(0.0, float(total_intensity))], alpha, transmission)
    mag = float(np.linalg.norm(vec))
    return mag if mag > 0 else 1.0


def circumference_stimulus(sources, alpha=ALPHA, transmission=TRANSMISSION):
    total = sum(float(i) for _, i in sources)
    if total <= 0:
        return 0.0, 0.0
    vec = _circ_vector(sources, alpha, transmission)
    angle = float(np.rad2deg(np.arctan2(vec[0], vec[1])))
    coherence = float(np.linalg.norm(vec) / _circ_ref(total, alpha, transmission))
    return angle, coherence


def stimulus(sources, model):
    if model == "physical":
        return physical_stimulus(sources)
    if model == "transduced_source":
        return transduced_source_stimulus(sources)
    if model == "circumference":
        return circumference_stimulus(sources)
    raise ValueError(model)


# --------------------------------------------------------------------------
# Dynamics. phi_series and gain_series are sampled every DT.
# --------------------------------------------------------------------------

def simulate_with_stimulus(params, phi_series, gain_series):
    k, tau, max_rate = (float(params["k"]), float(params["tau"]),
                        float(params["max_rate"]))
    n = len(phi_series) - 1
    theta = np.empty(n + 1)
    rate = np.empty(n + 1)
    th, r = 0.0, 0.0
    theta[0], rate[0] = th, r
    for i in range(n):
        stim = k * gain_series[i] * np.sin(np.deg2rad(phi_series[i] - th))
        r += (stim - r) * (DT / tau)
        r = float(np.clip(r, -max_rate, max_rate))
        th += r * DT
        theta[i + 1], rate[i + 1] = th, r
    times = np.arange(n + 1) * DT
    return times, theta, rate


def simulate_population(pop, phi_series, gain_series, record_dt=0.5):
    k = pop[:, 0].copy()
    tau = pop[:, 1].copy()
    max_rate = pop[:, 2].copy()
    n = len(phi_series) - 1
    rec = max(1, int(round(record_dt / DT)))
    theta = np.zeros(len(pop))
    r = np.zeros(len(pop))
    out = [theta.copy()]
    for i in range(n):
        stim = k * gain_series[i] * np.sin(np.deg2rad(phi_series[i] - theta))
        r += (stim - r) * (DT / tau)
        np.clip(r, -max_rate, max_rate, out=r)
        theta = theta + r * DT
        if (i + 1) % rec == 0:
            out.append(theta.copy())
    times = np.arange(len(out)) * record_dt
    return times, np.array(out)


def constant_series(sources_by_model, duration=24.0):
    n = int(round(duration / DT))
    series = {}
    for model in MODELS:
        phi, g = stimulus(sources_by_model, model)
        series[model] = (np.full(n + 1, phi), np.full(n + 1, g))
    return series


# --------------------------------------------------------------------------
# Scenarios
# --------------------------------------------------------------------------

def two_source_grid():
    rows = []
    separations = [15, 30, 45, 60, 90, 120, 150]
    ratios = [1, 1.5, 2, 3, 5, 10, 20]
    for sep in separations:
        for ratio in ratios:
            sources = [(-sep / 2, 1.0), (sep / 2, float(ratio))]
            phys = physical_stimulus(sources)[0]
            row = {"separation_deg": sep, "intensity_ratio": ratio,
                   "physical_direction": phys}
            for model in ("transduced_source", "circumference"):
                ang = stimulus(sources, model)[0]
                row[f"{model}_direction"] = ang
                row[f"{model}_distortion_deg"] = ang - phys
            rows.append(row)
    return pd.DataFrame(rows)


def moving_sun_series(duration=24.0):
    """Direct sun crossing the sky plus symmetric diffuse sources (day only)."""
    n = int(round(duration / DT))
    times = np.arange(n + 1) * DT
    diffuse_angles = [-60, -30, 0, 30, 60]
    series = {}
    raw = {m: ([], []) for m in MODELS}
    # A coarser circumference grid is sufficient for the time series.
    psi = np.linspace(-np.pi, np.pi, 361, endpoint=False)
    psi_unit = np.stack([np.sin(psi), np.cos(psi)], axis=1)

    def circ(sources):
        total = sum(i for _, i in sources)
        if total <= 0:
            return 0.0, 0.0
        vec = _circ_vector(sources, psi=psi, psi_unit=psi_unit)
        ref_vec = _circ_vector([(0.0, total)], psi=psi, psi_unit=psi_unit)
        ref = float(np.linalg.norm(ref_vec)) or 1.0
        return (float(np.rad2deg(np.arctan2(vec[0], vec[1]))),
                float(np.linalg.norm(vec) / ref))

    for t in times:
        if 0 <= t < 12:
            sun_phi = -60 + 120 * (t / 12)
            sun_i = float(np.sin(np.pi * t / 12)) ** 0.7
            sources = [(sun_phi, sun_i)] + [(a, 0.12) for a in diffuse_angles]
        else:
            sources = []
        for model in MODELS:
            if model == "circumference":
                phi, g = circ(sources)
            else:
                phi, g = stimulus(sources, model)
            raw[model][0].append(phi)
            raw[model][1].append(g)
    for model in MODELS:
        series[model] = (np.array(raw[model][0]), np.array(raw[model][1]))
    # Null comparator: direct sun only, unit gain in daylight, zero at night.
    null_phi = np.where(times < 12, -60 + 120 * np.clip(times, 0, 12) / 12, 0.0)
    null_g = np.where((times >= 0) & (times < 12), 1.0, 0.0)
    series["current_sun_only"] = (null_phi, null_g)
    return times, series


def scenario_dynamics():
    rep = {"k": 16.579, "tau": 3.616, "max_rate": 31.145, "phi0": 45.006}
    rows = []
    curves = {}

    scenarios = {
        "two_source_90_ratio5": [(-45, 1.0), (45, 5.0)],
        "opposing_plus_weak": [(-80, 10.0), (80, 10.0), (25, 1.0)],
    }
    for name, sources in scenarios.items():
        series = constant_series(sources)
        curves[name] = {}
        for model in MODELS:
            phi_s, g = series[model]
            t, th, _ = simulate_with_stimulus(rep, phi_s, g)
            curves[name][model] = (t, th)
            rows.append({
                "scenario": name, "model": model,
                "effective_direction": float(phi_s[0]),
                "effective_gain": float(g[0]),
                "final_angle": float(th[-1]),
                "half_rise_time": float(t[np.argmax(th >= 0.5 * th.max())])
                if th.max() > 0 else np.nan,
            })
        # physical direction as the reference for this scenario
        for r in rows:
            pass

    times, sun = moving_sun_series()
    curves["moving_sun_diffuse"] = {}
    for model in list(MODELS) + ["current_sun_only"]:
        phi_s, g = sun[model]
        t, th, _ = simulate_with_stimulus(rep, phi_s, g)
        curves["moving_sun_diffuse"][model] = (t, th)
        rows.append({
            "scenario": "moving_sun_diffuse", "model": model,
            "effective_direction": np.nan, "effective_gain": np.nan,
            "final_angle": float(th[-1]),
            "half_rise_time": float(t[np.argmax(th >= 0.5 * th.max())])
            if th.max() > 0 else np.nan,
        })
    return pd.DataFrame(rows), curves, (times, sun)


def population_comparison(sun_series, n=20_000):
    fits = pd.read_csv("results/fit_fig1c.csv")
    clean = fits[fits["at_bound"] == "[]"].copy()
    pop = weighted_population(n, seed=SEED, fit_frame=clean)
    results = {}
    for model in list(MODELS) + ["current_sun_only"]:
        phi_s, g = sun_series[model]
        t, th = simulate_population(pop, phi_s, g)
        results[model] = th
    ref = results["current_sun_only"]
    rows = []
    for i in range(n):
        row = {"plant_id": i}
        for p, val in zip(PARAM_NAMES, pop[i]):
            row[f"param_{p}"] = float(val)
        for model, th in results.items():
            row[f"final_{model}"] = float(th[-1, i])
            row[f"rmse_vs_sun_only_{model}"] = float(
                np.sqrt(np.mean((th[:, i] - ref[:, i]) ** 2)))
        rows.append(row)
    return pd.DataFrame(rows), results


def make_dashboard(grid, scen, curves, popdf):
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle("BendLab vector-sum stimulus comparison", fontsize=15)

    # Distortion heatmap (circumference model).
    a = axes[0, 0]
    piv = grid.pivot(index="intensity_ratio", columns="separation_deg",
                     values="circumference_distortion_deg")
    vmax = float(np.nanmax(np.abs(piv.values))) if piv.size else 1.0
    im = a.imshow(piv.values, origin="lower", aspect="auto", cmap="coolwarm",
                  vmin=-vmax, vmax=vmax)
    a.set_xticks(range(len(piv.columns)), [str(c) for c in piv.columns])
    a.set_yticks(range(len(piv.index)), [str(i) for i in piv.index])
    a.set_xlabel("source separation (deg)")
    a.set_ylabel("intensity ratio")
    a.set_title("Perceived-direction distortion\ncircumference model vs physical sum")
    fig.colorbar(im, ax=a, label="distortion (deg)")

    # Direction vs ratio at 90-degree separation.
    a = axes[0, 1]
    sub = grid[grid.separation_deg == 90]
    a.plot(sub.intensity_ratio, sub.physical_direction, "o-", label="physical")
    a.plot(sub.intensity_ratio, sub.transduced_source_direction, "o-",
           label="transduced sources")
    a.plot(sub.intensity_ratio, sub.circumference_direction, "o-",
           label="circumference")
    a.set_xscale("log")
    a.set_xlabel("intensity ratio (source 2 / source 1)")
    a.set_ylabel("effective direction (deg)")
    a.set_title("Two sources at ±45°: where does the plant aim?")
    a.legend(fontsize=8)

    # Opposing lights + weak third cue: final angles.
    a = axes[0, 2]
    sub = scen[scen.scenario == "opposing_plus_weak"]
    a.bar(sub.model, sub.final_angle, color=["#7f8c8d", "#4c9f70", "#3f6fb5"])
    a.set_ylabel("final stem angle (deg)")
    a.set_title("Strong near-opposing lights + weak cue at +25°")

    # Moving-sun trajectories.
    a = axes[1, 0]
    for model, (t, th) in curves["moving_sun_diffuse"].items():
        a.plot(t, th, lw=1.8, label=model)
    a.set_xlabel("time (h)")
    a.set_ylabel("stem angle (deg)")
    a.set_title("Moving sun + diffuse sky (representative fitted plant)")
    a.legend(fontsize=8)

    # Population final-angle differences vs sun-only null.
    a = axes[1, 1]
    for model in MODELS:
        a.hist(popdf[f"final_{model}"] - popdf["final_current_sun_only"],
               bins=45, alpha=0.55, label=model)
    a.axvline(0, color="black", lw=1)
    a.set_xlabel("final angle difference vs sun-only model (deg)")
    a.set_ylabel("plants")
    a.set_title("Population effect under moving sun (n=%s)" % f"{len(popdf):,}")
    a.legend(fontsize=8)

    # Scenario table as text panel.
    a = axes[1, 2]
    a.axis("off")
    short_model = {"physical": "physical", "transduced_source": "transduced",
                   "circumference": "circumf.", "current_sun_only": "sun-only"}
    short_scen = {"two_source_90_ratio5": "two-source 90° ×5",
                  "opposing_plus_weak": "near-opposing + weak",
                  "moving_sun_diffuse": "moving sun + diffuse"}
    lines = ["Effective stimulus by scenario", ""]
    for _, r in scen.iterrows():
        sname = short_scen.get(r.scenario, r.scenario)
        mname = short_model.get(r.model, r.model)
        if np.isnan(r.effective_direction):
            lines.append("%s | %s: final %.1f°" % (sname, mname, r.final_angle))
        else:
            lines.append("%s | %s: aim %.1f°, gain %.2f, final %.1f°"
                         % (sname, mname, r.effective_direction,
                            r.effective_gain, r.final_angle))
    a.text(0.0, 1.0, "\n".join(lines), va="top", ha="left", fontsize=7.6,
           family="monospace", transform=a.transAxes)
    a.set_title("Scenario summary")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT_FIG, dpi=170)
    plt.close(fig)


def main():
    os.makedirs("results/figures", exist_ok=True)
    t0 = time.time()

    # Validation: one source must reproduce the existing BendLab simulator.
    p = {"k": 16.579, "tau": 3.616, "max_rate": 31.145, "phi0": 45.006}
    n = int(round(24 / DT))
    for model in MODELS:
        phi, g = stimulus([(45.006, 1.0)], model)
        # The circumference model is numerical; allow its quadrature error.
        tol = 0.05 if model == "circumference" else 1e-9
        assert abs(phi - 45.006) < tol and abs(g - 1.0) < 2e-3, (model, phi, g)
    phi_s = np.full(n + 1, 45.006)
    g_s = np.ones(n + 1)
    _, th_new, _ = simulate_with_stimulus(p, phi_s, g_s)
    _, th_ref = py_simulate(p["k"], p["tau"], p["max_rate"],
                            static_light(45.006), 24.0)
    validation_err = float(np.max(np.abs(th_new - th_ref)))
    print("single-source validation vs sim.py: max abs diff = %.3e deg"
          % validation_err, flush=True)

    grid = two_source_grid()
    grid.to_csv(OUT_GRID, index=False)
    print("two-source grid done (%.1fs)" % (time.time() - t0), flush=True)

    scen, curves, (_, sun_series) = scenario_dynamics()
    scen.to_csv(OUT_SCEN, index=False)
    print("scenario dynamics done (%.1fs)" % (time.time() - t0), flush=True)

    popdf, _ = population_comparison(sun_series)
    popdf.to_csv(OUT_POP, index=False)
    print("population comparison done (%.1fs)" % (time.time() - t0), flush=True)

    make_dashboard(grid, scen, curves, popdf)

    summary = {
        "alpha": ALPHA,
        "transmission": TRANSMISSION,
        "validation_max_abs_diff_deg_vs_sim_py": validation_err,
        "max_abs_circumference_distortion_deg": float(
            grid.circumference_distortion_deg.abs().max()),
        "max_abs_transduced_distortion_deg": float(
            grid.transduced_source_distortion_deg.abs().max()),
        "population_n": int(len(popdf)),
        "runtime_seconds": round(time.time() - t0, 1),
    }
    for model in MODELS:
        d = popdf[f"final_{model}"] - popdf["final_current_sun_only"]
        summary[f"final_diff_vs_sun_only_{model}"] = {
            "median_deg": float(d.median()),
            "p95_abs_deg": float(d.abs().quantile(0.95)),
            "max_abs_deg": float(d.abs().max()),
            "median_trajectory_rmse_deg": float(
                popdf[f"rmse_vs_sun_only_{model}"].median()),
        }
    scen_records = scen.to_dict(orient="records")
    summary["scenarios"] = scen_records
    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print("\n=== VECTOR STIMULUS SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print("\nsaved %s" % OUT_FIG)


if __name__ == "__main__":
    main()
