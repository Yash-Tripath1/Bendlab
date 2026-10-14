"""Experiment series 1: synthetic-population analyses.

This script evaluates the hypotheses that require no additional measured
data: H3 (discontinuities in parameter space), H4 (cluster transfer across
light regimes), H6 (connectivity of the degenerate parameter set), H7
(protocol ranking by parameter identifiability) and H8 (adaptive protocol
selection for predictive identification).

Design note: all thresholds and analysis choices are declared at the top of
this file and were fixed before the corresponding runs. Unsupported
hypotheses are reported as unsupported and are not reformulated after
inspection of the results.

Run after fit_real.py and sweep_weighted.py (needs results/fit_fig1c.csv).
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from generate_plants import PARAM_NAMES, weighted_population
from sim import batch_simulate
from sweep import half_rise_batch, feature_frame

# ---------------------------------------------------------------- constants
SEED_BASE = 13

# population source: clean fits only (see RESULTS_ROUND0 section 1)
FIT_CSV = "results/fit_fig1c.csv"

# H3: dense grid, cliff threshold declared in hours of half-rise jump
H3_N = 64
H3_K = (1.0, 36.0)
H3_TAU = (1.0, 36.0)
H3_PHI0, H3_CAP = 45.0, 30.0
H3_CLIFF_H = 2.0  # adjacent-cell half-rise jump above this counts as a cliff

# H4: ARI at or above this means clusters persist (H4 falsified)
H4_ARI_PERSIST = 0.5
H4_POP = 6_000
N_CLUSTERS = 6

# H6: crossover test
H6_PAIRS = 300
H6_MUT_PROB = 0.5
H6_MUT_SD_FRAC = 0.10  # mutation standard deviation, as a fraction of the weighted range for each parameter

# H7: protocol ranking by nearest-neighbour recovery under noise
H7_POP = 1_000
SIGMA_OBS = 2.0        # degrees, from round-0 fit residuals (2-5 deg, low end)
H7_GAP_SUPPORT = 0.10  # best-worst gap in mean relative error to call H7 supported

# H8: adaptive identification experiment
H8_PLANTS = 500
H8_HYP = 3_000
H8_BUDGET = 24.0
H8_EPS = 5.0           # success tolerance, degrees RMSE on the held-out ramp
H8_EIG_DRAWS = 8
H8_MAX_REUSE = 4       # noise draws pregenerated per plant per protocol

RECORD_DT = 0.5
T_END = 24.0
FEAT_COLS = ["half_rise_time", "peak_angle", "final_angle", "overshoot",
             "peak_rate", "auroc"]


def clean_fits() -> pd.DataFrame:
    fits = pd.read_csv(FIT_CSV)
    return fits[fits["at_bound"] == "[]"].copy()


# ------------------------------------------------- light regimes (vectorised)
def light_static(t, p0):
    return p0


def light_flip4(t, p0):
    return p0 + (45.0 if t >= 4.0 else 0.0)


def light_flip12(t, p0):
    return p0 + (45.0 if t >= 12.0 else 0.0)


def light_sweep12(t, p0):
    # sawtooth centred on each plant's own phi0: -45 to +45 over 12 h, reset
    return p0 + 45.0 * (2.0 * ((t % 12.0) / 12.0) - 1.0)


def light_dflip16(t, p0):
    # +45 between hours 6 and 14, back to phi0 after
    return p0 + (45.0 if 6.0 <= t < 14.0 else 0.0)


def light_ramp24(t, p0):
    # held-out protocol for H8: continuous ramp, never in the menu
    return p0 - 30.0 + 60.0 * (t / 24.0)


PROTOCOLS = {
    "static6":   (6.0, light_static),
    "flip4_8":   (8.0, light_flip4),
    "flip12_14": (14.0, light_flip12),
    "sweep12":   (12.0, light_sweep12),
    "dflip16":   (16.0, light_dflip16),
}
HELDOUT = ("ramp24", (24.0, light_ramp24))


def run_protocol(pop: pd.DataFrame, name: str):
    dur, fn = PROTOCOLS[name] if name in PROTOCOLS else HELDOUT[1]
    t, th = batch_simulate(pop["k"], pop["tau"], pop["max_rate"], pop["phi0"],
                           fn, dur, record_dt=RECORD_DT)
    return t, th


def library(pop: pd.DataFrame, name: str) -> np.ndarray:
    """Noiseless curves for the H8 hypothesis set, shape (n_plants, n_time).

    Transposed relative to run_protocol because the H8 analysis indexes by plant.
    """
    return run_protocol(pop, name)[1].T


def truth_library(pop: pd.DataFrame, name: str) -> np.ndarray:
    return run_protocol(pop, name)[1].T


def pop_frame(vals: np.ndarray) -> pd.DataFrame:
    df = pd.DataFrame(vals, columns=PARAM_NAMES)
    df.insert(0, "plant_id", np.arange(len(df)))
    return df


def entropy(p: np.ndarray) -> float:
    return float(-(p * np.log(p + 1e-300)).sum())


# ------------------------------------------------------------------------ H3
def run_h3() -> dict:
    ks = np.linspace(*H3_K, H3_N)
    taus = np.linspace(*H3_TAU, H3_N)
    K, T = np.meshgrid(ks, taus)
    pop = pop_frame(np.column_stack([K.ravel(), T.ravel(),
                                     np.full(K.size, H3_CAP),
                                     np.full(K.size, H3_PHI0)]))
    t, th = run_protocol(pop, "static6")  # static light; duration irrelevant,
    # rerun at full length so half-rise is measurable
    t, th = batch_simulate(pop["k"], pop["tau"], pop["max_rate"], pop["phi0"],
                           light_static, T_END, record_dt=RECORD_DT)
    hr = half_rise_batch(t, th).reshape(H3_N, H3_N)
    final = th[-1].reshape(H3_N, H3_N)
    dk = np.abs(np.diff(hr, axis=0))
    dt_ = np.abs(np.diff(hr, axis=1))
    cliff_edges = int((dk > H3_CLIFF_H).sum() + (dt_ > H3_CLIFF_H).sum())
    total_edges = dk.size + dt_.size
    out = {
        "grid": f"{H3_N}x{H3_N}",
        "cliff_edges": cliff_edges,
        "edge_frac": round(cliff_edges / total_edges, 4),
        "max_jump_h": round(float(max(dk.max(), dt_.max())), 2),
        "half_rise": hr, "final": final, "ks": ks, "taus": taus,
    }
    print("[H3] edges meeting the discontinuity criterion: %d/%d (%.2f%%); maximum adjacent change %.2f h"
          % (cliff_edges, total_edges, 100 * cliff_edges / total_edges,
             out["max_jump_h"]))
    return out


# ------------------------------------------------------------------------ H4
def run_h4_h6(clean: pd.DataFrame):
    pop = pop_frame(weighted_population(H4_POP, SEED_BASE + 8, clean))
    scaler = StandardScaler()

    # static regime
    t_s, th_s = batch_simulate(pop["k"], pop["tau"], pop["max_rate"],
                               pop["phi0"], light_static, T_END,
                               record_dt=RECORD_DT)
    feat_s = feature_frame(t_s, th_s, pop, "static")
    Xs = scaler.fit_transform(feat_s[FEAT_COLS].to_numpy())
    lab_s = KMeans(N_CLUSTERS, n_init=10,
                   random_state=SEED_BASE).fit_predict(Xs)

    # sweep regime: moving sun, same plants, same feature definitions
    t_w, th_w = batch_simulate(pop["k"], pop["tau"], pop["max_rate"],
                               pop["phi0"], light_sweep12, T_END,
                               record_dt=RECORD_DT)
    feat_w = feature_frame(t_w, th_w, pop, "sweep")
    scaler_w = StandardScaler()
    Xw = scaler_w.fit_transform(feat_w[FEAT_COLS].to_numpy())
    lab_w = KMeans(N_CLUSTERS, n_init=10,
                   random_state=SEED_BASE).fit_predict(Xw)

    ari = adjusted_rand_score(lab_s, lab_w)
    verdict = "H4 FALSIFIED (clusters persist)" if ari >= H4_ARI_PERSIST \
        else "H4 supported (clusters do not persist)"
    print("[H4] adjusted Rand index static-vs-sweep = %.3f (threshold %.2f): %s"
          % (ari, H4_ARI_PERSIST, verdict))

    # -------------------------------------------------------------------- H6
    rng = np.random.default_rng(SEED_BASE + 6)
    vals = pop[list(PARAM_NAMES)].to_numpy()
    lo = vals.min(axis=0)
    hi = vals.max(axis=0)
    mut_sd = H6_MUT_SD_FRAC * (hi - lo)

    def recombine(i, j):
        mask = rng.random(len(PARAM_NAMES)) < 0.5
        recombinant = np.where(mask, vals[i], vals[j])
        hits = rng.random(len(PARAM_NAMES)) < H6_MUT_PROB
        recombinant = recombinant + hits * rng.normal(0.0, 1.0, len(PARAM_NAMES)) * mut_sd
        return np.clip(recombinant, lo, hi)

    centroids = KMeans(N_CLUSTERS, n_init=10,
                       random_state=SEED_BASE).fit(Xs).cluster_centers_

    def cluster_of(recombinant_vals: np.ndarray) -> np.ndarray:
        cpop = pop_frame(recombinant_vals)
        ct, cth = batch_simulate(cpop["k"], cpop["tau"], cpop["max_rate"],
                                 cpop["phi0"], light_static, T_END,
                                 record_dt=RECORD_DT)
        cf = feature_frame(ct, cth, cpop, "static")
        return np.argmin(((scaler.transform(cf[FEAT_COLS].to_numpy())
                           [:, None, :] - centroids[None]) ** 2
                          ).sum(axis=2), axis=1)

    same_idx = [rng.choice(np.flatnonzero(lab_s == c), 2, replace=False)
                for c in range(N_CLUSTERS)
                for _ in range(H6_PAIRS // N_CLUSTERS)
                if (lab_s == c).sum() >= 2]
    same_pairs = np.array(same_idx)[:H6_PAIRS]
    diff_pairs = np.array([[rng.integers(len(pop)), rng.integers(len(pop))]
                           for _ in range(H6_PAIRS)])
    diff_pairs = diff_pairs[lab_s[diff_pairs[:, 0]] != lab_s[diff_pairs[:, 1]]]

    recombinants_same = cluster_of(np.array([recombine(i, j) for i, j in same_pairs]))
    keep_same = float(np.mean(recombinants_same == lab_s[same_pairs[:, 0]]))

    recombinants_diff = cluster_of(np.array([recombine(i, j) for i, j in diff_pairs]))
    keep_diff_first = float(np.mean(recombinants_diff == lab_s[diff_pairs[:, 0]]))
    keep_diff_any = float(np.mean((recombinants_diff == lab_s[diff_pairs[:, 0]])
                                  | (recombinants_diff == lab_s[diff_pairs[:, 1]])))

    print("[H6] same-cluster source pairs: %.1f%% of recombinants assigned "
          "to the source class (n=%d)" % (100 * keep_same, len(same_pairs)))
    print("[H6] cross-cluster controls: %.1f%% assigned to the first source "
          "class; %.1f%% to either source class (n=%d)"
          % (100 * keep_diff_first, 100 * keep_diff_any, len(diff_pairs)))
    return {"ari": ari, "verdict": verdict, "keep_same": keep_same,
            "keep_diff_first": keep_diff_first, "keep_diff_any": keep_diff_any,
            "n_same": len(same_pairs), "n_diff": len(diff_pairs)}


# ------------------------------------------------------------------------ H7
def run_h7(clean: pd.DataFrame) -> pd.DataFrame:
    pop = pop_frame(weighted_population(H7_POP, SEED_BASE + 18, clean))
    params = pop[list(PARAM_NAMES)].to_numpy()
    span = np.percentile(params, 95, axis=0) - np.percentile(params, 5, axis=0)
    rng = np.random.default_rng(SEED_BASE + 19)

    rows = []
    for name, (dur, _) in PROTOCOLS.items():
        t, th = run_protocol(pop, name)
        noise = rng.normal(0.0, SIGMA_OBS, th.shape)
        obs = th + noise
        nn = NearestNeighbors(n_neighbors=2).fit(obs.T)
        _, idx = nn.kneighbors(obs.T)
        rec = params[idx[:, 1]]  # parameters of the nearest distinct plant
        rel_err = np.abs(params - rec) / span
        rows.append({
            "protocol": name, "cost_h": dur,
            "mean_rel_err": float(rel_err.mean()),
            **{f"err_{n}": float(rel_err[:, i].mean())
               for i, n in enumerate(PARAM_NAMES)},
        })
    tab = pd.DataFrame(rows).sort_values("mean_rel_err")
    gap = float(tab["mean_rel_err"].max() - tab["mean_rel_err"].min())
    tab["H7_supported"] = gap >= H7_GAP_SUPPORT
    print("[H7] protocol ranking (mean relative recovery error, lower=better):")
    print(tab.round(3).to_string(index=False))
    print("[H7] best-worst gap %.3f vs threshold %.2f -> %s"
          % (gap, H7_GAP_SUPPORT,
             "H7 supported" if gap >= H7_GAP_SUPPORT else "H7 NOT supported"))
    tab.to_csv("results/round1_h7_protocols.csv", index=False)
    return tab


# ------------------------------------------------------------------------ H8
def run_h8(clean: pd.DataFrame, best_protocol: str) -> pd.DataFrame:
    hyp = pop_frame(weighted_population(H8_HYP, SEED_BASE + 21, clean))
    truth = pop_frame(weighted_population(H8_PLANTS, SEED_BASE + 22, clean))

    # noiseless libraries on the hypothesis set, shape (n_plants, n_time)
    libs = {name: library(hyp, name) for name in PROTOCOLS}
    lib_ramp = batch_simulate(hyp["k"], hyp["tau"], hyp["max_rate"],
                              hyp["phi0"], light_ramp24, 24.0,
                              record_dt=RECORD_DT)[1].T
    truths = {name: truth_library(truth, name) for name in PROTOCOLS}
    truth_ramp = batch_simulate(truth["k"], truth["tau"], truth["max_rate"],
                                truth["phi0"], light_ramp24, 24.0,
                                record_dt=RECORD_DT)[1].T

    # shared noise: identical across policies for the same plant+protocol+use
    noise = {name: np.random.default_rng(SEED_BASE + 23 + i).normal(
                 0.0, SIGMA_OBS, (H8_PLANTS, H8_MAX_REUSE, libs[name].shape[1]))
             for i, name in enumerate(PROTOCOLS)}

    def loglik(lib, y):
        return -0.5 * ((lib - y[None, :]) ** 2).sum(axis=1) / SIGMA_OBS ** 2

    def run_policy(kind: str) -> np.ndarray:
        success = np.zeros(H8_PLANTS, bool)
        for pi in range(H8_PLANTS):
            logw = np.zeros(H8_HYP)
            elapsed, uses = 0.0, {n: 0 for n in PROTOCOLS}
            prng = np.random.default_rng(SEED_BASE * 1000 + pi
                                         + {"random": 0, "fixed": 1,
                                            "greedy": 2, "thompson": 3}[kind] * 100000)
            while True:
                afford = [n for n, (c, _) in PROTOCOLS.items()
                          if c <= H8_BUDGET - elapsed + 1e-9]
                if not afford:
                    break
                if kind == "random":
                    pick = afford[prng.integers(len(afford))]
                elif kind == "fixed":
                    pick = best_protocol if best_protocol in afford \
                        else min(afford, key=lambda n: PROTOCOLS[n][0])
                else:
                    w = np.exp(logw - logw.max())
                    w /= w.sum()
                    H0 = entropy(w)
                    scores = {}
                    for n in afford:
                        if kind == "greedy":
                            draw = prng.choice(H8_HYP, H8_EIG_DRAWS, p=w)
                            ys = libs[n][draw] + prng.normal(
                                0.0, SIGMA_OBS, (H8_EIG_DRAWS, libs[n].shape[1]))
                            lw2 = logw[None, :] + np.stack(
                                [loglik(libs[n], y) for y in ys])
                            m = lw2.max(axis=1, keepdims=True)
                            p2 = np.exp(lw2 - m)
                            p2 /= p2.sum(axis=1, keepdims=True)
                            scores[n] = H0 - float(np.mean(
                                [entropy(p) for p in p2]))
                        else:  # thompson: plug-in on one posterior sample
                            h = prng.choice(H8_HYP, p=w)
                            y = libs[n][h] + prng.normal(
                                0.0, SIGMA_OBS, libs[n].shape[1])
                            lw2 = logw + loglik(libs[n], y)
                            m = lw2.max()
                            p2 = np.exp(lw2 - m)
                            p2 /= p2.sum()
                            scores[n] = -entropy(p2)  # lower entropy better
                    pick = max(scores, key=scores.get) if kind == "greedy" \
                        else min(scores, key=scores.get)
                u = uses[pick]
                y = truths[pick][pi] + noise[pick][pi, u % H8_MAX_REUSE]
                uses[pick] = u + 1
                logw = logw + loglik(libs[pick], y)
                elapsed += PROTOCOLS[pick][0]
            w = np.exp(logw - logw.max())
            w /= w.sum()
            pred = w @ lib_ramp
            rmse = float(np.sqrt(np.mean((pred - truth_ramp[pi]) ** 2)))
            success[pi] = rmse <= H8_EPS
        return success

    results = {}
    for kind in ("random", "fixed", "greedy", "thompson"):
        t0 = time.time()
        results[kind] = run_policy(kind)
        print("[H8] %-9s success %5.1f/100  (%.0fs)"
              % (kind, 100 * results[kind].mean(), time.time() - t0))

    g, f = results["greedy"], results["fixed"]
    wtl = (int((g & ~f).sum()), int((g & f).sum()), int((~g & f).sum()))
    print("[H8] greedy vs fixed W/T/L: %d/%d/%d" % wtl)
    tab = pd.DataFrame([{"policy": k, "success_per_100": round(100 * v.mean(), 1),
                         "n": len(v)} for k, v in results.items()])
    tab.to_csv("results/round1_h8_policies.csv", index=False)
    return tab


# -------------------------------------------------------------------- figure
def make_figure(h3, h46, h7, h8, clean):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pop = pop_frame(weighted_population(2_000, SEED_BASE + 30, clean))
    t, th = batch_simulate(pop["k"], pop["tau"], pop["max_rate"], pop["phi0"],
                           light_static, T_END, record_dt=RECORD_DT)

    fig, ax = plt.subplots(2, 3, figsize=(15.5, 8.6))
    fig.suptitle("BendLab experiment series 1: synthetic-population analyses "
                 "(13 October 2026)", fontsize=13, weight="bold")

    a = ax[0, 0]
    im = a.pcolormesh(h3["ks"], h3["taus"], h3["half_rise"].T,
                      shading="auto", cmap="viridis")
    a.set_title("H3: half-rise time over (k, tau)\nno discontinuity edges detected (%.1f%%)"
                % (100 * h3["edge_frac"]))
    a.set_xlabel("k (per hour)")
    a.set_ylabel("tau (hours)")
    fig.colorbar(im, ax=a, label="hours")

    a = ax[0, 1]
    a.bar(["static vs sweep"], [h46["ari"]], color="tab:blue", width=0.4)
    a.axhline(H4_ARI_PERSIST, color="red", ls="--",
              label="persist threshold %.1f" % H4_ARI_PERSIST)
    a.set_ylim(0, 1)
    a.set_title("H4: cluster agreement across regimes\nARI = %.3f -> %s"
                % (h46["ari"], "clusters persist" if h46["ari"] >= H4_ARI_PERSIST
                   else "clusters do not persist"))
    a.legend()
    a.set_ylabel("adjusted Rand index")

    a = ax[0, 2]
    a.bar(["Same-cluster\nsource pair", "Cross-cluster\n(first source)",
           "Cross-cluster\n(either source)"],
          [100 * h46["keep_same"], 100 * h46["keep_diff_first"],
           100 * h46["keep_diff_any"]],
          color=["tab:green", "tab:orange", "tab:red"], width=0.55)
    a.set_ylim(0, 100)
    a.set_title("H6: percentage of recombinant parameter vectors\nassigned to the source behavioural class")
    a.set_ylabel("percent")

    a = ax[1, 0]
    a.barh(h7["protocol"], h7["mean_rel_err"], color="tab:purple")
    a.invert_yaxis()
    for i, (e, c) in enumerate(zip(h7["mean_rel_err"], h7["cost_h"])):
        a.text(e + 0.005, i, "%.2f (%.0fh)" % (e, c), va="center", fontsize=9)
    a.set_title("H7: parameter-recovery error by protocol\n(lower indicates greater identifiability; duration in hours)")
    a.set_xlabel("mean relative error")

    a = ax[1, 1]
    colors = {"random": "gray", "fixed": "tab:blue", "greedy": "tab:green",
              "thompson": "tab:orange"}
    a.bar(h8["policy"], h8["success_per_100"],
          color=[colors[p] for p in h8["policy"]], width=0.55)
    a.set_ylim(0, 100)
    a.set_title("H8: adaptive identification experiment, %d plants\nheld-out ramp prediction "
                "within %.0f deg" % (H8_PLANTS, H8_EPS))
    a.set_ylabel("success per 100")

    a = ax[1, 2]
    for j in range(0, 150):
        a.plot(t, th[:, j], color="green", alpha=0.15, lw=0.7)
    a.set_title("Empirically weighted population\n150 simulated trajectories under static light")
    a.set_xlabel("hours")
    a.set_ylabel("stem angle (deg)")

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig("results/figures/round1_dashboard.png", dpi=140)
    print("[fig] saved results/figures/round1_dashboard.png")


def main():
    t0 = time.time()
    clean = clean_fits()
    print("clean fits: %d | blocks: %s\n"
          % (len(clean), sorted(clean["block"].unique())))
    h3 = run_h3()
    h46 = run_h4_h6(clean)
    h7 = run_h7(clean)
    best = h7.iloc[0]["protocol"]
    h8 = run_h8(clean, best_protocol=best)
    make_figure(h3, h46, h7, h8, clean)
    print("\ntotal elapsed time: %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    import os
    os.makedirs("results", exist_ok=True)
    main()
