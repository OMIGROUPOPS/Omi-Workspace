# ATP_MAIN staircase — abort-trigger validation evidence

Evidence for the four abort bars (C-ABORT-EVIDENCE). All numbers REPRODUCIBLE from the committed corpus via `analysis/exit_charts/abort_validation.py` (re-run 2026-06-15, numbers regenerate). This is **evidence only** — the seal-spec amendment (locked bars) is a separate commit pending Plex re-ruling on triggers 1 & 3 against this.

## 1. Corpus identity (N reconciled)
| quantity | N | meaning |
|---|---|---|
| engagement attempts (placed legs) | **4,975** | fill-rate denominator |
| **fills (fills table)** | **3,595** | the "3,595" — filled legs |
| **rolling-10 windows** | **3,586** | the "3,586" = N_fills − 9 (every trigger-1 & trigger-3 FP denominator) |

The two numbers are both correct for different objects: **3,595 = fills**, **3,586 = rolling-10 windows over those fills**. All windowed-trigger FP rates use 3,586.

- **Fills table:** `docs/policy/range_final_ATP_MAIN_abort_fills.csv` — content-sha256 `4e4c15534c6cb6a2f38802760b584c101bbf1f1b245e2631d7db075cc678a92e` (cols: ticker_idx, cell, regime, anchor, offset, match_start_ts, exit_er, mk_ret, mk_cap).
- **Source corpus:** `data/durable/per_minute_universe/per_minute_features_batch_*.parquet` (ATP_MAIN) + schedule `range_final_walk_schedule.json` (@3a701ba) + `range_final_ATP_MAIN.csv` (@3c2161c) + `deploy_gated_optima_full.csv` (exit). PMF is the durable corpus (on VPS, not in git); the committed fills CSV is the sha-pinned materialized intermediate.

## 2. Analysis script (committed, reproduces all four)
`analysis/exit_charts/abort_validation.py` — re-run regenerates: trigger-1 FP 0/3586, trigger-3 FP 0/3586, fill-rate 3595/4975=72.3%, per-regime expected table. ✅ reproduced.

## 3. Per-regime expected-offset + DERIVATION RULE
**RULE:** `expected[regime] = median( realized fill_offset over all validation fills whose placement-cell falls in the regime's 10c bin )` — i.e. **walk-derived from the abort-validation fills table**, NOT a column of the sealed CSV.

| regime | expected (median fill_offset) | cross-check: median(cur_offset) |
|---|---|---|
| r05_14 | 1 | 1 |
| r15_24 | 1 | 2 |
| r25_34 | 2 | 1 |
| r35_44 | 2 | 1 |
| r45_54 | 2 | 2 |
| r55_64 | 2 | 2 |
| r65_74 | 2 | 1 |
| r75_84 | 2 | **7** |
| r85_94 | 1 | 1 |

**`median(cur_offset)` does NOT reproduce the expected table** (diverges materially, esp. r75_84: cur 7 vs realized 2; r25_34/r35_44/r65_74). So the expected-offset is **not** derivable from the entry table by the "median cur_offset" rule — it is a genuine product of the staircase walk (reproducible by the committed script from the PMF). Stated honestly so Plex doesn't treat it as a CSV-column rule.

## 4. Rolling-10 ROC methodology (so min +7.78 / 0-negative is reproducible)
- **per-FILL** (filled legs only; misses excluded — this is why mean 11.70 > the all-legs ROC base 10.38).
- ordered **chronologically by `match_start_ts`**.
- **stride 1 (overlapping)** windows; N = 3,586.
- **SIMPLE capital-weighted** ROC per window = `Σ mk_ret / Σ mk_cap × 100` (NOT compounded).
- Result: mean 11.70, sd 1.17, **min 7.78**, max 17.91. **Trigger 3 (rolling-10-fill ROC < 0): FP 0/3586 = 0.0%.**

## 5. Fill-rate bar (point-estimate; denominator = engagement attempts)
- rate = **fills / attempts** = 3595 / 4975 = **72.3%**. (attempts = placed legs; live: first nonzero placement = t=0, count over the first 10 attempts.)
- **BAR = 72.3% − 10pp = 62.3%** (point-estimate). **Bootstrap CI DROPPED** — it implied 61.0, a different number; the bar is the point-estimate minus 10pp.
- live: over the first 10 engagement attempts, `fills/10 < 6.23` (i.e. ≤6 fills) → abort.

## 6. Anchor-1 floor — code-pointer + HONEST conditionality
- The offset≥1 (bid ≤ anchor−1) floor is enforced **only in the validation sim** (`abort_validation.py`: `D = max(1, ...)`).
- **LIVE: there is NO offset≥anchor−1 invariant.** `_reprice_target` (**live_v4.py:3166**) and `_fallback_order` (**live_v4.py:3175**) clamp to `max(1, best_ask − 1)` — a floor on **absolute price (ask−1)**, not on offset-relative-to-anchor. `live_v4.py` blob @HEAD (1d7b776): **`1912d8bc`**.
- **Does a code path allow sub-anchor-1 placement? YES** — when `best_ask > anchor`, the clamp posts at `ask−1`, which is shallower (higher) than `anchor−1`, i.e. offset < 1 relative to the placement anchor.
- **Therefore trigger-1's 0% FP and the r05_14/r65_74 degenerate-band immunity are CONDITIONAL** on the eventual staircase deploy adding an explicit `offset ≥ 1` (bid ≤ anchor−1) clamp that overrides/subordinates the ask−1 fallback. Until that clamp exists in live code, the immunity is a sim property, not a live guarantee.

## Trigger summary (evidence for Plex re-ruling — bars NOT yet sealed)
| # | trigger | bar | validation FP |
|---|---|---|---|
| 1 OFFSET | ≥3 of first 10 fills shallower than regime-expected by >1c (residual < −1c) | X=1c, ≥3-of-10 | **0/3586 = 0.0%** (conditional on §6 invariant) |
| 2 FILL-RATE | fills/attempts over first 10 < 62.3% | 62.3% (72.3 − 10pp) | point-estimate |
| 3 ROLLING-ROC | rolling-10-fill ROC < 0 | 0 (val min +7.78) | **0/3586 = 0.0%** |
| 4 WALK-STEP | out-of-order / depth-increase vs 9-knot sequence | zero tolerance | structural |
