"""Phase C latency reanalysis (post-audit): censoring-aware
time-to-threshold analysis.

Implements PHASE_C_LATENCY_ADDENDUM.md, whose definitions were fixed
before this script was run. The original Phase C latency regression
coded the 5 never-crossing plants as exact 22 h events and the
plants already at or above 10 deg at baseline as zero-time events;
that estimate is superseded as an interpretation (retained in
phase_c_results.json for provenance).

Primary analysis: plants with theta(0) < 10 deg (at risk of a first
crossing), event = first observed theta >= 10 deg, right-censoring
at the last observed time, Cox proportional hazards on
log L0 + log intensity + theta(0), Efron ties (lifelines).
Pre-declared sensitivities: the at-risk model without theta(0) and
with log L0 alone; and a revised endpoint on all 213 plants (time to
theta(0) + 10 deg). Decision rule for the M1c inclusion question is
in the addendum.

Requires: lifelines (in addition to numpy, pandas).
Outputs: outputs/phase_c_latency_cox.json,
         outputs/phase_c_latency_times.csv
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.statistics import proportional_hazard_test

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"


def load():
    paired = pd.read_csv(OUT / "paired_plants.csv")
    U = pd.read_csv(HERE / "data" / "00_Data" / "uni_trajectories.csv")
    plants = {}
    for pid, g in U.sort_values("dt").groupby("real_id"):
        plants[pid] = (g["dt"].to_numpy(float), g["theta"].to_numpy(float))
    return paired, plants


def build_times(paired, plants):
    rows = []
    for _, r in paired[paired.has_length].iterrows():
        t, th = plants[r.real_id]
        theta0 = float(th[0])
        hit = np.where(th >= 10.0)[0]
        hit_delta = np.where(th >= theta0 + 10.0)[0]
        rows.append({
            "real_id": r.real_id, "I": float(r.light_i),
            "L0": float(r.L0_mm), "theta0": theta0,
            "at_risk_10deg": bool(theta0 < 10.0),
            "T_10deg": float(t[hit[0]]) if len(hit) else float(t[-1]),
            "event_10deg": bool(len(hit)),
            "T_plus10": float(t[hit_delta[0]]) if len(hit_delta)
            else float(t[-1]),
            "event_plus10": bool(len(hit_delta)),
            "t_last": float(t[-1])})
    return pd.DataFrame(rows)


def fit_cox(df, duration, event, covs, label):
    d = df.rename(columns={duration: "T", event: "E"})[["T", "E"] + covs]
    cph = CoxPHFitter()
    cph.fit(d, duration_col="T", event_col="E")  # lifelines Efron tie handling
    s = cph.summary.loc["logL0"]
    out = {"label": label, "n": int(len(d)),
           "events": int(d.E.sum()), "censored": int(len(d) - d.E.sum()),
           "HR_per_logL0": float(np.exp(s["coef"])),
           "coef_logL0": float(s["coef"]),
           "se_coef": float(s["se(coef)"]),
           "ci95_HR": [float(np.exp(s["coef"] - 1.96 * s["se(coef)"])),
                       float(np.exp(s["coef"] + 1.96 * s["se(coef)"]))],
           "p_logL0": float(s["p"])}
    if label == "primary_at_risk_adjusted":
        ph = proportional_hazard_test(cph, d, time_transform="log")
        out["ph_test_log_time"] = {
            "global_p_min_covariate_p": {
                k: float(v) for k, v in
                ph.summary["p"].items()},
            "note": ("per-covariate Schoenfeld tests (log time); "
                     "lifelines reports no single global statistic, "
                     "so all three p values are given")}
        out["_cph"] = cph  # stripped before serialising
    return out


def main():
    paired, plants = load()
    df = build_times(paired, plants)
    df.to_csv(OUT / "phase_c_latency_times.csv", index=False)
    df["logL0"] = np.log(df.L0)
    df["logI"] = np.log(df.I)
    at = df[df.at_risk_10deg]

    counts = {
        "paired_plants": int(len(df)),
        "baseline_at_or_above_10deg_excluded_from_primary":
            int((~df.at_risk_10deg).sum()),
        "at_risk_n": int(len(at)),
        "at_risk_events": int(at.event_10deg.sum()),
        "at_risk_censored_never_reached_10deg":
            int((~at.event_10deg).sum()),
        "original_coding_flaws_for_reference": {
            "plants_assigned_exact_22h_in_original":
                int((~df.event_10deg).sum()),
            "plants_coded_zero_latency_in_original":
                int((~df.at_risk_10deg).sum())}}

    models = [
        fit_cox(at, "T_10deg", "event_10deg",
                ["logL0", "logI", "theta0"], "primary_at_risk_adjusted"),
        fit_cox(at, "T_10deg", "event_10deg",
                ["logL0", "logI"], "sensitivity_at_risk_no_theta0"),
        fit_cox(at, "T_10deg", "event_10deg",
                ["logL0"], "sensitivity_at_risk_logL0_only"),
        fit_cox(df, "T_plus10", "event_plus10",
                ["logL0", "logI", "theta0"],
                "sensitivity_revised_endpoint_plus10deg_all_plants"),
    ]
    primary = models[0]
    ph_ps = list(primary["ph_test_log_time"]
                 ["global_p_min_covariate_p"].values())
    ci_excludes_1 = primary["ci95_HR"][0] > 1.0 or \
        primary["ci95_HR"][1] < 1.0
    ph_ok = bool(min(ph_ps) >= 0.05)
    result = {
        "status": ("POST-AUDIT reanalysis under "
                   "PHASE_C_LATENCY_ADDENDUM.md (definitions fixed "
                   "before this run; not original pre-registration)"),
        "counts": counts,
        "models": [{k: v for k, v in m.items() if k != "_cph"}
                   for m in models],
        "decision_rule_from_addendum": {
            "latency_signal_detected": bool(ci_excludes_1 and ph_ok),
            "ci_excludes_1": bool(ci_excludes_1),
            "ph_schoenfeld_all_p_ge_0.05": ph_ok,
            "consequence": (
                "if detected: M1c is presented alongside M1a/M1d in "
                "the v3 report (post-audit provenance kept); "
                "if not: the original exclusion of M1c from the "
                "primary comparison stands under the corrected "
                "analysis and M1c remains a labelled sensitivity")},
        "superseded_original_estimate": {
            "source": "phase_c_results.json associations.latency10_h",
            "coef_per_logL0_h": -0.7483841517581271,
            "ci95": [-2.016325257242018, 0.38167355886227167],
            "why_superseded": ("right-censoring coded as exact 22 h "
                               "events and baseline-at-threshold "
                               "plants coded as zero-time events")}}
    (OUT / "phase_c_latency_cox.json").write_text(
        json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
