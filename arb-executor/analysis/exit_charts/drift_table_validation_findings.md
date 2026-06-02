# Drift-informed entry table — validation finding (NEGATIVE, current table stays)

**Date:** 2026-06-02 · **Verdict:** do NOT deploy the drift-informed candidate; the current T47-derived per-cell table (`entry_table_percell.csv`) stays.

## Question

The committed lifecycle/drift surfaces (`premarket_lifecycle_surface_midanchor_*.csv`) showed a clean descriptive shape: the catchable discount/drift is an early-window phenomenon (fill_reach + deepen_frac decay T-240→T-2, firm in the last ~30 min), favorites drift up / underdogs down / mids oscillate, all caught early. Does encoding that into the per-cell entry table — **place early, shallow everywhere** — produce HIGHER realized blended ROC than the current T47 net-optimal table?

## Method

- **Candidate** (`build_entry_table_drift.py` → `entry_table_drift_candidate.csv`): per cell, placement_minute = earliest tbin with occ-wt fill_reach ≥ 0.90 (→ 334/360 at T-240); offset = deepest shallow d∈{1,2,3} with early fill_reach ≥ 0.80 (shallow everywhere, capped 3, NOT f×D-argmax — deliberately drops T47's deep 7-18¢ throughput cells).
- **Validation** (`drift_table_validate.py`): a timing-aware, running-mid-anchored per-match walk modelling what the live bot (T58) does — anchor on the running-mid at placement, place when tts ≤ the cell's placement_minute, fill iff a traded low reaches anchor−offset between placement and the volume live-onset; mirror-correct, capital-weighted realized ROC = Σ(ret)/Σ(cap), with EXIT = the locked gated_optima exp_ret_match. Same leg population + identical accounting for both tables; ONLY the (placement_minute, offset) per cell differs. Engine sanity: CURRENT-table real_roc reproduces the committed `entry_lift_permatch` blended_capW (ATP_MAIN 18.48≈18.53, ATP_CHALL 11.24≈11.18).

## Result

| category | CURRENT real_roc | DRIFT real_roc | Δ | fill% (cur→drift) |
|---|---|---|---|---|
| ATP_MAIN | 18.48 | **19.27** | **drift +0.79** | 76.2 → 58.8 |
| WTA_MAIN | **11.42** | 11.13 | current +0.29 | 66.2 → 64.3 |
| ATP_CHALL | **11.24** | 11.17 | current +0.07 | 58.0 → 66.7 |
| WTA_CHALL | **10.34** | 9.10 | current +1.24 | 60.5 → 78.0 |

Drift wins 1 of 4 (ATP_MAIN, modest) and loses 3 of 4, including the largest single margin (WTA_CHALL −1.24). Net: **does not beat current.**

## Reading

1. **Descriptive shapes ≠ realized edge.** The drift microstructure is real, but encoding it (early + shallow-everywhere) does not convert to net realized ROC under the fixed-profit exit + paired mirror. Confirms the T47 lesson that the productive lever is the static per-cell offset on the net-PnL objective, not the descriptive dip/drift shape.
2. **More fills ≠ better.** WTA_CHALL: drift fills MORE (60→78%) but earns LESS (10.34→9.10). ATP_MAIN: drift fills LESS (76→59%) but earns MORE. Fill rate is not the objective; realized ROC is.
3. **T47's deep-throughput cells earn their keep.** Flattening every cell to ≤3¢ (dropping the 7-18¢ deep-underdog cells) is what costs WTA_CHALL −1.24 — those deep choices realize ROC the shallow candidate forgoes. The per-match walk that gave +3pp already validated the current offsets; this re-confirms them.

## Disposition

Current `entry_table_percell.csv` stays deployed. The ATP_MAIN +0.79 is not pursued (single-category, single-walk; cherry-picking one category risks over-fit, and the WTA_CHALL −1.24 is the stronger signal that shallow-everywhere is worse). Drift shapes remain a descriptive (Layer-A) finding, not a deployable edge. Reproducible via the two producers above.
