# Paper outline

| Paper section | Job | Paper data | Cite | Do not claim |
|---|---|---|---|---|
| Data | Define analytic samples, quality checks, and observed intensity coverage. | `PAPER_DATA.md` §1 | `fig02_external_benchmark_rmse.png`; `fig03_intensity_transfer.png` | No archive coverage above its tracked maximum; no known physical geometry for length fields. |
| Model | State equations, parameter units, and angular convention. | `PAPER_DATA.md` §2 | None | The phenomenological equations identify a mechanism or `max_rate` is physiological. |
| Identifiability | Separate Jacobian estimability, raw cap-to-peak comparison, and range retention. | `PAPER_DATA.md` §3 | `fig01_identifiability_rate_cap.png` | The two cap counts answer the same question or raw peaks prove cap activation. |
| In-sample fit and transfer | Contrast Fig1C fit quality, block-held-out prediction, and held-out ZT9 results. | `PAPER_DATA.md` §4 | `fig05_zt9_transfer.png` | In-sample fit establishes generalization or a circadian mechanism. |
| External benchmark | Report plant-held-out comparisons and distinguish B0 from Phase E. | `PAPER_DATA.md` §5 | `fig02_external_benchmark_rmse.png`; `fig03_intensity_transfer.png` | Average the two saved W2 results or infer physiological parameter recovery from prediction. |
| Phase E | Give the preregistered verdict, paired contrasts, fitted parameters, and leave-one-intensity-out results. | `PAPER_DATA.md` §6 | `fig02_external_benchmark_rmse.png`; `fig03_intensity_transfer.png` shows primary stratification only, not the leave-one-intensity-out test; `fig06_phase_e_equivalence.png` shows paired W3/B1 errors and the difference interval | W3 met its threshold, beat B1, demonstrated a mechanism, or was formally equivalent to B1. |
| Rate-limit anomaly | Reconcile fitted W3 `max_rate` with the smoothed observed-rate check. | `PAPER_DATA.md` §7 | None | `max_rate` is a physiological maximum or should be retuned to the smoothed peak. |
| Growth coupling | Present the observational overlap result, conditional nulls, strata, and ambiguous verdict. | `PAPER_DATA.md` §8 | `fig04_growth_coupling_nulls.png` | Growth causes bending, length geometry is known, or nulls are pure geometry tests. |
| Supporting analyses | Place Phase C associations and Phase D design simulation in secondary context. | `PAPER_DATA.md` §9 | `fig05_zt9_transfer.png` only if clock-transfer context is relevant | Treat design simulations as guaranteed enrollment needs or label the Cox result conditional-logit. |

**Recommended writing order:** Data, Model, Identifiability, In-sample fit and transfer, External benchmark, Phase E, Rate-limit anomaly, Growth coupling, Supporting analyses. Resolve the scope and terminology limits in `PAPER_DATA.md` before drafting the interpretation.