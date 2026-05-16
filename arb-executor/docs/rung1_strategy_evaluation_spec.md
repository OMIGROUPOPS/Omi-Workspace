# Rung 1 Spec — Per-Band Optimized-Exit-Target Strategy Evaluation

**Status:** v0.1 — initial draft 2026-05-15 ET. Operator-locked threshold grid, metric subset, and Greek-label deferral. Producer build unblocked at v0.1.

**Anchored to:**
- `rung0_cell_economics_spec.md` v1.1 (commit 87103d0d) — Rung 0 schema is the input
- `data/durable/rung0_cell_economics/cell_economics.parquet` (sha256 `6fdd019d08722d0afb5688181fb60394d73dc2b05765af74d6c5675edd17c992`, commit 5ca2d89c) — actual landed input
- `docs/external_synthesis/plex_rung1_metric_design_2026-05-15.md` (commit 3f7dc02c) — comprehensive metric inventory; v0.1 picks a 16-metric subset
- LESSONS E32 (locked cell/exit model — no stop, ride to settlement), A21 (Wall Street grade metrics), A38 (dual-peak doctrine), A39 (cents vs ROI as separate ranking metrics), G21 (ET on operator surfaces), C36 (canonical sourcing discipline), C37 (pre-replace validation gate)
- `recomputation_ladder.json` Rung 1
- `SIMONS_MODE.md` Section 4 (Rung 1 is pure Problem 1 — cell selection; strategy-evaluation-only, no execution claims)
- TAXONOMY Section 2.5 (GRAIN / VECTOR / OBJECTIVE classification — Rung 1's GRAIN is per-(cell, threshold), VECTOR is bounce-distribution-over-thresholds, OBJECTIVE is exit-optimized)

**Output:** `data/durable/rung1_strategy_evaluation/strategy_evaluation.parquet`

**ROADMAP:** T39 Rung 1.

---

## 1. Scope

Rung 1 produces the canonical per-band optimized-exit-target evaluation surface on the Rung 0 corpus. For each cell (72 cells = 4 categories × 18 price bands) × each candidate exit threshold (8 thresholds), Rung 1 emits a decision-grade metric surface answering: **"what realized return would the strategy of 'enter at T-20m, post a resting maker sell at +threshold¢, exit on first kiss or ride to settlement under E32's no-stop model' have produced?"**

The output replaces all legacy settlement-scored exit-sweep analyses (`exit_sweep_grid`, `exit_sweep_curves`, `optimal_exits`, `exit_sweep_leader_70_74` per `unit_of_analysis_audit.json`) with a single canonical exit-optimized table built on the FOUNDATION-TIER corpus.

### 1.1 The operational definition

For every row in `cell_economics.parquet` AND every threshold in the grid:
- **Hit:** `peak_bid_bounce_pre_resolution >= threshold / 100` (Rung 0 stores bounces in dollars; threshold is in cents).
- **Realized cents per row:** if hit, `realized_cents = threshold`; if miss, `realized_cents = realized_at_settlement * 100` (Rung 0 col 28, dollars → cents).
- **Realized ROI per row:** `realized_roi = realized_cents / (t20m_trade_price * 100)` (cents over entry cost in cents = ROI on cost basis per A39).

For each (cell, threshold) group, aggregate the per-row realized distributions into 16 core metrics with confidence intervals per A21.

### 1.2 In scope

- Per-(cell, threshold) grain. 72 cells × 8 thresholds = 576 output rows (less any cell-threshold combinations with zero observations, which should be none under the v0.1 design).
- Threshold grid: +5¢, +10¢, +15¢, +20¢, +25¢, +30¢, +40¢, +50¢ (8 thresholds, denser in the strategically interesting region).
- The 16 core metrics defined in Section 4, each with CI bounds where applicable.
- Wilson CIs for proportions (hit rate, settlement loss frequency). BCa bootstrap CIs for distributional metrics (mean cents, mean ROI, std, downside std, Sharpe-like, Sortino-like).
- Within-cell bootstrap is row-level n=1000 (Plex's open-question Resolution 1).
- Sample-quality flags: `low_n_flag` (observations_n < 30) and `weak_ci_flag` (ROI CI crosses zero OR hit_rate CI width > 0.20).
- Deployment-throughput context: mean entry price, daily opportunity rate, expected cents per dollar capital per day.
- Headline rankings emitted in `validation_report.md`: top-10 by mean realized cents AND top-10 by mean realized ROI per A39.

### 1.3 Out of scope

- **Cross-cell aggregations** (e.g., `variance_across_cells_at_threshold`) — Rung 1.5 follow-up. The chat-side resolution for cross-cell match-clustered bootstrap (Plex Resolution 1) is documented but the metric itself is deferred to keep v1 lean.
- **Greek-labeled curve-shape metrics** (`execution_delta_proxy`, `gamma_convexity_proxy`, `theta_decay_to_first_extreme`, `vega_bounce_vol_sensitivity`, `liquidity_greek_proxy`, `binary_prob_delta`) — deferred to Rung 1.5. Operator decision on Greek labels vs honest descriptors (e.g., `hit_rate_threshold_slope`) deferred with them.
- **Path-dependent drawdown metrics** (`cumulative_pnl_path_drawdown_*`) — Plex flagged v2; v1 spec keeps them out. Chronology preserved in Rung 0 cols 5/6 makes these computable later without re-running the producer.
- **Max loss per contract** (`max_loss_per_contract_cents`) — deterministic bound under E32 = `−t20m_trade_price * 100` cents (if N loses, ride to settlement at 0). Per-row already computable; emitting it as an aggregated metric adds no information beyond the realized-cents distribution itself.
- **Fees** — Cat 2 fee table layered at consumption time, not in Rung 1. v1 reports gross realized cents and gross ROI. Fee-adjusted variants are a downstream consumer choice.
- **Maker fill probability** — Rung 3 work (Problem 2 territory). Rung 1's `threshold_hit_rate` measures whether the price reached the threshold, NOT whether a resting maker sell at that price actually got filled. The Rung 1 metrics assume idealized maker fill at price-touch (the same assumption Rung 0 inherits); the gap between idealized-touch and actual-fill is Rung 3 + T38 work.
- **In-match vs premarket exit decomposition** — Rung 0 col 21 `peak_bid_in_premarket` carries the per-row split. Rung 1 v0.1 aggregates across both windows; Rung 1.5 can stratify if operator wants the split.
- **Bilateral capture** — Rung 2 work.

---

## 2. The cell-threshold key

### 2.1 Definition

A Rung 1 row is keyed `(cell_key, threshold_cents)` where:
- `cell_key` = Rung 0's `cell_key` column (string, format `"{category}__{price_band}"`, e.g., `"WTA_CHALL__0.30-0.35"`)
- `threshold_cents` = one of {5, 10, 15, 20, 25, 30, 40, 50}

72 cells × 8 thresholds = **576 output rows** under the v0.1 design.

### 2.2 The threshold grid (locked)

Eight candidate exit targets:

| threshold_cents | rationale |
|---|---|
| 5 | Lowest tradeable target; high-hit-rate baseline |
| 10 | Strategically central; B23 bilateral capture anchor was at +10¢ |
| 15 | Strategically central; modest stretch |
| 20 | Strategically central |
| 25 | Aggressive within the headline range (mean Rung 0 bounces are in the 30-34¢ range for top-10 cents cells) |
| 30 | Near the mean for top-10 cents cells |
| 40 | Stretch target; expected hit-rate decline |
| 50 | Ceiling target for v1; above this hit rates collapse for most cells |

The grid is dense in the +5 to +30¢ region (the strategically interesting deployment zone) and sparser above. Above +50¢ is not measured in v1 because:
- A 75¢ contract has only +24¢ to ceiling — a +50¢ target is structurally impossible
- For mid-band cells (25-50¢ entries), +50¢ targets put the exit at 75-100¢ where most peaks don't reach
- Adding +60/+70/+80¢ thresholds would inflate the output schema without adding decision-relevant information

If a Rung 1.5 amendment establishes that specific cells have peak distributions warranting higher thresholds, the grid can be extended; v0.1 ships at 8 thresholds.

### 2.3 Per-row realized cents computation (load-bearing)

For each Rung 0 row r and each threshold t in the grid:
```
peak_bounce_cents          = r.peak_bid_bounce_pre_resolution * 100   # dollars → cents
entry_price_cents          = r.t20m_trade_price * 100
realized_at_settlement_cents = r.realized_at_settlement * 100         # already signed; negative for losing rides
hit = peak_bounce_cents >= t
if hit:
    realized_cents = t
else:
    realized_cents = realized_at_settlement_cents                     # under E32 no-stop: ride to settlement
realized_roi = realized_cents / entry_price_cents                     # ROI on cost basis per A39
```

**Why this is right under E32 (operator-readable derivation):**
- E32 specifies no stop. If the bot enters at T-20m and the price never reaches the +threshold exit target, the position rides to settlement.
- Under E32, settlement = first 99¢/1¢ touch. The position pays either +(99¢ − entry_price) if the bot's side wins, or −(entry_price − 1¢) if it loses.
- Rung 0 col 28 `realized_at_settlement` = `settlement_value_dollars − t20m_trade_price`, where `settlement_value_dollars` is 0.0 or 1.0. So a winning ride: 1.0 − 0.30 = +0.70 (= +70¢). A losing ride: 0.0 − 0.30 = −0.30 (= −30¢). Already in dollars; conversion to cents is *100.
- Approximation: under E32 the "first 99¢/1¢ touch" is the settlement event, NOT the actual final settlement. There's a small discrepancy where `settlement_value_dollars` (the final 0/1) is the true terminal value but the bot's position closes at the 99¢/1¢ touch moment. v1 uses `realized_at_settlement` (the 0/1 endpoint) as the conservative loss baseline — it slightly understates capture on winners (you could exit at 99¢ ≈ +69¢ rather than ride to 1.00 = +70¢, 1¢ difference) and exactly matches loss on losers (1¢ touch = the loss baseline). Net bias: trivially conservative on winners, exact on losers. Acceptable for v1; can be refined in Rung 1.5 with `first_extreme_touch_ts` (col 27) if it matters.

### 2.4 Why no separate "in-match exit" treatment in v0.1

E32's two-exit-window model (premarket + in-match) is unified at Rung 0's `peak_bid_pre_resolution` metric: it captures the peak across both windows up to first-extreme-touch. Rung 1 v0.1 aggregates over both. Rung 0 col 21 `peak_bid_in_premarket` is preserved for Rung 1.5 stratification but doesn't change the v0.1 metric definitions.

---

## 3. The 16 core metrics (locked v0.1 ship list)

Plex's synthesis (commit 3f7dc02c) inventoried 50+ candidate metrics. v0.1 ships 16 critically-selected metrics that produce the decision surface; the other 35+ are reference inventory for Rung 1.5+ work.

Selection criteria for v0.1:
1. **Both cents AND ROI must be represented** in every category (per A39).
2. **CIs on every estimate** (per A21).
3. **No mechanical redundancy** — `mean_realized_bounce_cents` and `expected_value_cents` are the same number with different labels; v1 emits only the operationally-named one.
4. **No diagnostic-only metrics** in v1 (e.g., `threshold_hit_rate_full_window` exists only as a sanity comparator against A38 saturation; v1 doesn't ship it as a row column).
5. **Greek labels excluded** (deferred entirely to Rung 1.5; v0.1 ships clean of them).

### 3.1 The 16 metrics (definitions)

**RETURN (5 metrics + CIs):**

1. `threshold_hit_rate` — fraction of cell rows where `peak_bid_bounce_pre_resolution >= threshold/100`. Wilson CI bounds.
2. `mean_realized_cents` — mean of per-row `realized_cents` (per Section 2.3 derivation). BCa bootstrap CI bounds.
3. `mean_realized_roi_pct` — mean of per-row `realized_roi * 100` (ROI in percent). BCa bootstrap CI bounds.
4. `median_realized_cents` — median of per-row `realized_cents`. BCa bootstrap CI bounds for the median.
5. `median_realized_roi_pct` — median of per-row `realized_roi * 100`. BCa bootstrap CI bounds for the median.

**RISK (3 metrics + CIs):**

6. `std_realized_cents` — std of per-row `realized_cents` distribution. BCa bootstrap CI bounds.
7. `std_realized_roi_pct` — std of per-row `realized_roi * 100`. BCa bootstrap CI bounds.
8. `downside_std_realized_cents` — std of per-row `realized_cents` filtered to negative values only (downside convention per Plex Resolution 2: downside is the actual loss distribution under E32's no-stop logic, NOT zero-return). BCa bootstrap CI bounds. If all rows in the (cell, threshold) group are positive (no losing rides at this threshold), set to 0.0 and flag in `weak_ci_flag`.

**RISK-ADJUSTED (2 metrics + CIs):**

9. `sharpe_like_roi` — `mean_realized_roi_pct / std_realized_roi_pct`. BCa bootstrap CI bounds via resampled ratio distribution. If denominator is 0 (no variance in realized ROI within the group, extremely unlikely), return null and flag.
10. `sortino_like_roi` — `mean_realized_roi_pct / downside_std_realized_roi_pct`. BCa bootstrap CI bounds. Same null/flag handling.

`downside_std_realized_roi_pct` is computed inline (negative-ROI-only std) but not emitted as a separate column — its only purpose is the Sortino denominator. Same for `sharpe_like_cents` and `sortino_like_cents`; the ROI variants are operator-preferred per A39 + Plex inventory.

**SAMPLE-QUALITY (4 metrics, no CIs needed):**

11. `observations_n` — count of Rung 0 rows in the (cell, threshold) group. Equal to `band_n_count` from Rung 0 col 13 by construction (every row in the cell contributes to every threshold; Rung 1 doesn't drop rows per-threshold).
12. `unique_match_count` — distinct `event_ticker` count in the group. Will be ≤ `observations_n` (matches with both sides in the same cell would double-count, though under E32's price-symmetric pairing this is rare — both sides of a 0.50 match could land in the 0.45-0.50 and 0.50-0.55 bands, falling in different cells most of the time).
13. `low_n_flag` — boolean: `observations_n < 30`. Surfaces the small-sample warning per A21.
14. `weak_ci_flag` — boolean: TRUE if any of: (a) `mean_realized_roi_pct` BCa CI crosses zero, OR (b) `threshold_hit_rate` Wilson CI width > 0.20, OR (c) `low_n_flag` is TRUE. Composite filter for "this estimate isn't statistically stable."

**CAPITAL & THROUGHPUT (2 metrics + 1 context column):**

15. `mean_entry_price_cents` — mean of `t20m_trade_price * 100` across the cell. Same for every threshold within a cell (cell-level, not threshold-level). Required context for ROI interpretation.
16. `expected_cents_per_dollar_capital_day` — `(mean_realized_cents * daily_opportunity_rate) / mean_entry_price_cents`. The bot's actual deployment-EV metric: "how many cents do I earn per dollar of capital deployed per day if I run this (cell, threshold) strategy?"

Plus one helper column (not in the count of 16; computed from row timestamps):

- `daily_opportunity_rate` — `observations_n / corpus_active_days_in_sample`, where `corpus_active_days_in_sample` is the count of distinct dates in the corpus where Rung 0 emitted rows (computed once on the FULL unfiltered Rung 0 corpus and reused per row). Measures **N's-per-day** for this cell (per LESSONS G22: N is the player-binary market, the unit-of-observation; ct is the position-size unit. Each row is one N, not one ct). Same value for every threshold within a cell. Note: this is the corpus-wide rate (averaging across active and dead days). Per-category and per-cell active-day-normalized rate variants are deferred to Rung 1.5 — the corpus-wide rate is the operationally-correct denominator for the v0.1 deployment-EV math.

### 3.2 The full output schema

| # | Column | Type | Source / formula |
|---|---|---|---|
| 1 | `cell_key` | string | Rung 0 cell_key |
| 2 | `category` | string | Rung 0 category (denormalized for readability) |
| 3 | `price_band` | string | Rung 0 price_band (denormalized) |
| 4 | `threshold_cents` | int8 | one of {5,10,15,20,25,30,40,50} |
| 5 | `threshold_hit_rate` | float | Section 3.1 metric 1 |
| 6 | `threshold_hit_rate_ci_lower` | float | Wilson lower bound |
| 7 | `threshold_hit_rate_ci_upper` | float | Wilson upper bound |
| 8 | `mean_realized_cents` | float | metric 2 |
| 9 | `mean_realized_cents_ci_lower` | float | BCa lower |
| 10 | `mean_realized_cents_ci_upper` | float | BCa upper |
| 11 | `mean_realized_roi_pct` | float | metric 3 |
| 12 | `mean_realized_roi_pct_ci_lower` | float | BCa lower |
| 13 | `mean_realized_roi_pct_ci_upper` | float | BCa upper |
| 14 | `median_realized_cents` | float | metric 4 |
| 15 | `median_realized_cents_ci_lower` | float | BCa lower |
| 16 | `median_realized_cents_ci_upper` | float | BCa upper |
| 17 | `median_realized_roi_pct` | float | metric 5 |
| 18 | `median_realized_roi_pct_ci_lower` | float | BCa lower |
| 19 | `median_realized_roi_pct_ci_upper` | float | BCa upper |
| 20 | `std_realized_cents` | float | metric 6 |
| 21 | `std_realized_cents_ci_lower` | float | BCa lower |
| 22 | `std_realized_cents_ci_upper` | float | BCa upper |
| 23 | `std_realized_roi_pct` | float | metric 7 |
| 24 | `std_realized_roi_pct_ci_lower` | float | BCa lower |
| 25 | `std_realized_roi_pct_ci_upper` | float | BCa upper |
| 26 | `downside_std_realized_cents` | float | metric 8 |
| 27 | `downside_std_realized_cents_ci_lower` | float | BCa lower |
| 28 | `downside_std_realized_cents_ci_upper` | float | BCa upper |
| 29 | `sharpe_like_roi` | float or null | metric 9 |
| 30 | `sharpe_like_roi_ci_lower` | float or null | BCa lower |
| 31 | `sharpe_like_roi_ci_upper` | float or null | BCa upper |
| 32 | `sortino_like_roi` | float or null | metric 10 |
| 33 | `sortino_like_roi_ci_lower` | float or null | BCa lower |
| 34 | `sortino_like_roi_ci_upper` | float or null | BCa upper |
| 35 | `observations_n` | int32 | metric 11 |
| 36 | `unique_match_count` | int32 | metric 12 |
| 37 | `low_n_flag` | bool | metric 13 |
| 38 | `weak_ci_flag` | bool | metric 14 |
| 39 | `mean_entry_price_cents` | float | metric 15 |
| 40 | `daily_opportunity_rate` | float | helper (N's/day for this cell — qualifying-entry arrival rate; per G22) |
| 41 | `expected_cents_per_dollar_capital_day` | float | metric 16 |

**41 columns total.** 16 core metrics + their CI bounds (24 CI cols) + 1 helper (`daily_opportunity_rate`).

---

## 4. Bootstrap design (locked per Plex Resolution 1)

### 4.1 Within-cell bootstrap (the v0.1 default for all metrics)

Row-level bootstrap with n=1000 resamples. BCa where computable; percentile fallback if BCa fails to converge (rare; flagged in validation report).

Justification (operator-readable): Rung 0 emits one row per N per side. The two sides of a paired match fall in different price bands (their T-20m prices sum to ~$1, so one side at 0.30 puts the other at 0.70 — different cells). Within a single cell, rows are functionally independent observations from different matches. Row-level resampling is statistically correct at the within-cell level.

BCa specifics:
- 1000 bootstrap resamples per (cell, threshold) metric.
- Bias-corrected and accelerated; falls back to percentile bootstrap if BCa acceleration parameter computation fails.
- 95% CIs (2.5th and 97.5th percentile of the bootstrap distribution under percentile; BCa-adjusted equivalents).
- For ratio metrics (Sharpe-like, Sortino-like), bootstrap the ratio directly (resample the rows, recompute the ratio per resample) rather than bootstrapping numerator and denominator separately.

### 4.2 Cross-cell bootstrap (Rung 1.5 follow-up, not v0.1)

When metrics aggregate across cells where the same match contributes to multiple cells, match-clustered resampling at `event_ticker` level is required. Plex's `variance_across_cells_at_threshold` would need this. v0.1 doesn't emit cross-cell aggregates; the clustering protocol is documented for Rung 1.5.

---

## 5. Headline rankings emitted in validation_report.md

The producer emits the parquet AND a markdown report with operator-readable summaries:

### 5.1 Top-10 by mean realized cents (per A39, cents view)

For each threshold in the grid, list the top-10 cells by `mean_realized_cents`. Include cell_key, observations_n, mean cents (with CI), mean ROI (with CI), low_n_flag, weak_ci_flag.

### 5.2 Top-10 by mean realized ROI (per A39, ROI view)

Same structure, sorted by `mean_realized_roi_pct` per threshold.

### 5.3 Per-cell recommended threshold

For each of the 72 cells, list the threshold maximizing each of:
- `mean_realized_cents` (capital-throughput regime)
- `mean_realized_roi_pct` (capital-efficiency regime)
- `sharpe_like_roi` (risk-adjusted regime)

Three recommendations per cell. Operator-facing chosen-threshold decision is downstream.

### 5.4 Threshold-curve summaries

For each cell, show how `mean_realized_cents`, `mean_realized_roi_pct`, and `threshold_hit_rate` change across the 8 thresholds. ASCII sparkline-style table or per-cell mini-plots. Reveals which cells have steep vs flat threshold curves — informs the Rung 1.5 curve-shape diagnostics.

### 5.5 Sample-quality summary

Counts of cells flagged by `low_n_flag` and `weak_ci_flag` at each threshold. Coverage map: which thresholds have N≥30 in all 72 cells vs which collapse to low-N tails at aggressive thresholds.

---

## 6. Validation gates

### 6.1 Hard gates (must PASS before os.replace, per C37)

1. **Row count.** Output must have exactly 72 × 8 = **576 rows**. Zero violations.
2. **Cell coverage.** Every (cell_key, threshold) combination in the cross-product of 72 cells × 8 thresholds appears exactly once. Zero missing combinations; zero duplicates.
3. **Hit rate monotonicity within cell.** For each cell, `threshold_hit_rate` must be monotonically non-increasing as threshold increases (higher target = lower hit rate, by construction). Zero violations.
4. **Realized cents bounds.** For each row, `mean_realized_cents` must be ≤ `threshold_cents` (since hit rows contribute exactly threshold; miss rows contribute ≤ 0 under E32 ride-to-settlement which can't exceed threshold). For each row, `mean_realized_cents` must be ≥ `min(realized_at_settlement * 100)` for any contributing Rung 0 row (i.e., not below the worst possible loss). Zero violations on either bound.
5. **CI ordering.** For every metric with CI bounds, `ci_lower ≤ point_estimate ≤ ci_upper`. Zero violations across all 8 CI-bounded metrics.
6. **Sample-quality consistency.** Where `low_n_flag` is TRUE, `weak_ci_flag` must also be TRUE (per definition: weak_ci_flag is OR-composite including low_n_flag). Zero violations.
7. **Mean-vs-median sanity.** For positive-skewed distributions (which most cell-threshold groups will be — most rows hit moderate, a few hit huge), `mean_realized_cents ≥ median_realized_cents`. v0.1 makes this a **soft gate** (logged as anomaly, not blocking) because some (cell, threshold) groups with high losing-ride fractions could legitimately invert this. Surface count in validation_report.

### 6.2 Informative measurements (logged, not gating)

- Per-cell n_observations distribution (anchor for Rung 1.5 weight-by-N considerations).
- BCa convergence rate across the 24 CI-bounded metrics. If >5% of CI computations fall back to percentile, surface in validation_report as a numerical-stability flag.
- Cross-threshold cell-rank correlation. For each cell, how does its rank-by-cents change across the 8 thresholds? Cells with stable rankings are more robust deployment candidates; cells with flipping ranks are threshold-sensitive.
- Threshold at which each cell becomes weak_ci_flagged. Concrete read on "this cell supports up to threshold T before the data runs thin."
- Top-10-by-cents and top-10-by-ROI overlap fraction. A39 predicts low overlap (the rankings answer different questions); the actual fraction is a validation of A39's strength on this corpus.

---

## 7. Producer architecture

### 7.1 Input

- `data/durable/rung0_cell_economics/cell_economics.parquet` (read-only, sha256 `6fdd019d…`)

That's the only input. Rung 1 is a derived table from Rung 0; no foundation-corpus access needed.

### 7.2 Processing

Vectorized pandas pass (or polars if memory is a concern, though 14,033 rows × 36 cols is comfortably within RAM):

1. Load Rung 0 parquet.
2. Compute `corpus_active_days_in_sample` once: `len(set(rung0.match_start_ts.dt.date))`. Reused per row.
3. For each threshold in {5, 10, 15, 20, 25, 30, 40, 50}:
   a. Compute per-row `hit`, `realized_cents`, `realized_roi` (Section 2.3 derivation).
   b. Group by `cell_key`.
   c. For each (cell, threshold), compute the 16 metrics + helpers (Section 3).
   d. Compute CIs via 1000-resample BCa bootstrap per metric per (cell, threshold). For Wilson CIs (proportions), use closed-form.
4. Assemble the 41-column output DataFrame.
5. Compute validation gates (Section 6).
6. C37 discipline: write to `strategy_evaluation.parquet.new`; if all hard gates PASS, `os.replace`. If any hard gate fails, halt, preserve `.new` for inspection, write halt log.
7. Generate `validation_report.md` (Section 5).

### 7.3 Runtime budget

- 576 metric groups × ~10 metrics needing bootstrap × 1000 resamples = ~5.76M bootstrap computations.
- Each bootstrap computation is a small array operation (mean, std, or percentile on ~50-330 floats).
- Expected runtime: **5-20 minutes single-threaded**. Faster if vectorized with numpy. No multi-process / multi-thread requirement for v0.1.
- Memory: ~10 MB peak (14,033 rows × 36 cols ~1.7 MB; transient bootstrap arrays add <10 MB at peak). Well within VPS limits.

### 7.4 Output

- `data/durable/rung1_strategy_evaluation/strategy_evaluation.parquet` (576 rows × 41 cols)
- `data/durable/rung1_strategy_evaluation/validation_report.md`
- `data/durable/rung1_strategy_evaluation/strategy_evaluation.meta.json` (sidecar: sha256, input sha256, producer commit, run timestamp)

### 7.5 C37 discipline applied

- Write to `.new` extension only.
- Run all 6 hard gates against on-disk `.new` bytes (re-load the .new parquet, validate against its actual contents — not against in-memory data).
- `os.replace` only on all-pass.
- Failure: preserve `.new`, write halt log to `logs/`, exit non-zero. Operator investigates with disk-evidence (C37 doctrine).

---

## 8. Cross-references

- Foundation: `rung0_cell_economics_spec.md` v1.1 (commit 87103d0d); landed `cell_economics.parquet` sha256 `6fdd019d…` (commit 5ca2d89c).
- Metric inventory source: `docs/external_synthesis/plex_rung1_metric_design_2026-05-15.md` (commit 3f7dc02c) — v0.1 picks 16 of Plex's 50+ metrics with rationale documented.
- Doctrinal anchors: LESSONS E32 (no-stop ride-to-settlement, the load-bearing model); A21 (Wall Street grade metrics); A38 (dual-peak doctrine; Rung 1 uses `_pre_resolution` exclusively); A39 (cents vs ROI as separate ranking metrics — load-bearing for v0.1's dual-headline structure).
- TZ discipline: G21 (all operator-facing timestamps ET, no UTC leakage).
- Sourcing discipline: C36 (single canonical source — Rung 1 sources from Rung 0 only).
- Pre-replace gate discipline: C37.
- Classification axes: TAXONOMY Section 2.5 (Rung 1 GRAIN = per-(cell, threshold); VECTOR = bounce-distribution-over-thresholds; OBJECTIVE = exit-optimized).
- Ladder context: `recomputation_ladder.json` Rung 1; ROADMAP T39.
- SIMONS_MODE: Rung 1 is pure Problem 1 (cell selection / strategy). Rung 3 will integrate P2 (execution) when fill-probability work begins post-Rung-2.
- Out-of-scope acknowledgments: F33 (depth-chain gap; Rung 1 assumes idealized maker fill at price-touch, consistent with Rung 0; F33 bites at Rung 3 sizing not Rung 1 strategy evaluation); F8 (bot-side settlement detection gap; Rung 1 reads `realized_at_settlement` from Rung 0 col 28 which is sourced from g9_metadata ground truth, not bot logs).

---

## 9. Resolution log (v0.1 lock — 2026-05-15)

Operator-locked decisions at spec authoring time:

| # | Question | v0.1 Resolution | Source |
|---|---|---|---|
| 1 | Threshold grid | 8 thresholds: +5, +10, +15, +20, +25, +30, +40, +50¢ | Operator decision 2026-05-15 |
| 2 | Metric subset for v1 ship | 16 core metrics (5 RETURN + 3 RISK + 2 RISK-ADJUSTED + 4 SAMPLE-QUALITY + 2 CAPITAL-THROUGHPUT) with CIs | Operator decision 2026-05-15; selection criteria documented in Section 3 |
| 3 | Greek-labeled metrics | DEFERRED to Rung 1.5 entirely. Naming question (Greek vs honest descriptors) deferred with them | Operator decision 2026-05-15 |
| 4 | Bootstrap design | Row-level n=1000 BCa within-cell. Cross-cell match-clustered on event_ticker deferred to Rung 1.5 | Plex Resolution 1 (commit 3f7dc02c); v1 doesn't need cross-cell aggregates |
| 5 | Sortino downside convention | Negative-values-only std on `realized_cents` distribution (uses Rung 0 col 28 `realized_at_settlement` for non-hit terminal value per E32 no-stop) | Plex Resolution 2; verified against Rung 0 schema |
| 6 | Chronology / day-denominator | Computed from Rung 0 col 5 `match_start_ts` distinct dates | Plex Resolution 3; chronology preserved by construction |
| 7 | Realized cents derivation | Hit → threshold; miss → realized_at_settlement * 100 (signed; negative for losing rides under E32 no-stop) | Section 2.3; load-bearing for Sortino and all downside metrics |
| 8 | In-match vs premarket exit decomposition | DEFERRED to Rung 1.5. v0.1 aggregates both windows | Operator decision (keep v0.1 lean); Rung 0 col 21 `peak_bid_in_premarket` preserves the per-row split |
| 9 | Fees | NOT in v0.1. Gross realized cents and gross ROI only. Fee-adjusted variants are downstream consumer choice | Cat 2 doctrine; layered at consumption time |
| 10 | `weak_ci_flag` definition | Composite: ROI CI crosses zero OR hit_rate CI width > 0.20 OR low_n_flag TRUE | Operator-default; threshold values can be amended in Rung 1.5 if operator wants tighter/looser filter |

End of Rung 1 spec v0.1.
