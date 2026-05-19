# Rung 1 Spec — Per-Band Optimized-Exit-Target Strategy Evaluation

**Status:** v0.3.1 — 2026-05-19 ET. Whole-spec coherence completion of the v0.2/v0.3 continuous-exit-axis design (every surviving v0.1-grid contradiction across §1/§1.1/§1.2/§2.3/§3/§6.2/§8 closed) + restored §3.1 metric 16 (expected_cents_per_dollar_capital_day) into both artifacts. Spec internally consistent. Two artifacts: dense per-cell exit curve (Artifact A) + 72-row per-cell data-derived optimum (Artifact B), cents/ROI/Sharpe per A39. 72 cells (4 cat × 18 band) fixed; exit axis continuous 1..98c. Producer build unblocked at v0.3.1.

**Anchored to:**
- `rung0_cell_economics_spec.md` v1.1 (commit 87103d0d) — Rung 0 schema is the input
- `data/durable/rung0_cell_economics/cell_economics.parquet` (sha256 `6fdd019d08722d0afb5688181fb60394d73dc2b05765af74d6c5675edd17c992`, commit 5ca2d89c) — actual landed input
- `docs/external_synthesis/plex_rung1_metric_design_2026-05-15.md` (commit 3f7dc02c) — comprehensive metric inventory; v0.1 picks a 16-metric subset
- LESSONS E32 (locked cell/exit model — no stop, ride to settlement), A21 (Wall Street grade metrics), A38 (dual-peak doctrine), A39 (cents vs ROI as separate ranking metrics), G21 (ET on operator surfaces), C36 (canonical sourcing discipline), C37 (pre-replace validation gate)
- `recomputation_ladder.json` Rung 1
- `SIMONS_MODE.md` Section 4 (Rung 1 is pure Problem 1 — cell selection; strategy-evaluation-only, no execution claims)
- TAXONOMY Section 2.5 (GRAIN / VECTOR / OBJECTIVE classification — Rung 1's GRAIN is per-(cell, exit-line) for the curve artifact and per-cell for the optimum artifact, VECTOR is realized-return-over-the-continuous-exit-axis, OBJECTIVE is exit-optimized)

**Output:** `data/durable/rung1_strategy_evaluation/strategy_evaluation.parquet`

**ROADMAP:** T39 Rung 1.

---

## 1. Scope

Rung 1 produces the canonical per-band optimized-exit-target evaluation surface on the Rung 0 corpus. For each of the 72 fixed cells (4 categories × 18 price bands 5-95c; the cell is the T-20m recorded entry) Rung 1 emits, over a continuous exit-line axis (1..98c, §2.2), a decision-grade surface answering: **"what realized return would the strategy of 'enter at T-20m, post a resting maker sell at +L cents for the cell's data-derived optimal L, exit on first kiss or ride to settlement under E32 no-stop' have produced?"** — emitted as two artifacts (§3.2): the dense per-cell exit curve, and the 72-row per-cell data-derived optimum.

The output replaces all legacy settlement-scored exit-sweep analyses (`exit_sweep_grid`, `exit_sweep_curves`, `optimal_exits`, `exit_sweep_leader_70_74` per `unit_of_analysis_audit.json`) with a single canonical exit-optimized analysis (the two v0.3 artifacts, §3.2) built on the FOUNDATION-TIER corpus.

### 1.1 The operational definition

For every row in `cell_economics.parquet` and any candidate exit line L (continuous, 1..98c per §2.2):
- **Hit:** `peak_bid_bounce_pre_resolution >= L / 100` (Rung 0 stores bounces in dollars; L is in cents).
- **Realized cents per row:** if hit, `realized_cents = L`; if miss, `realized_cents = realized_at_settlement * 100` (Rung 0 col 28, dollars → cents).
- **Realized ROI per row:** `realized_roi = realized_cents / (t20m_trade_price * 100)` (cents over entry cost in cents = ROI on cost basis per A39).

For each (cell, exit-line) group, aggregate the per-row realized distributions into the core metrics with confidence intervals per A21; the per-cell data-derived optimum (§3.2 Artifact B) is the argmax over L.

### 1.2 In scope

- Two artifacts (§3.2): Artifact A the dense per-cell exit curve, keyed (cell_key, exit_line_cents) over 1..98c = 72 × 98 = 7,056 rows; Artifact B the per-cell data-derived optimum, keyed cell_key = 72 rows.
- Continuous exit-line axis: 1..98c at 1c step (no pre-imposed grid; §2.2 — the v0.1 8-point grid is superseded per A39/E32(e)).
- The core metrics defined in Section 3, each with CI bounds where applicable.
- Wilson CIs for proportions (hit rate, settlement loss frequency). BCa bootstrap CIs for distributional metrics (mean cents, mean ROI, std, downside std, Sharpe-like, Sortino-like).
- Within-cell bootstrap is row-level n=1000 (Plex's open-question Resolution 1).
- Sample-quality flags: `low_n_flag` (observations_n < 30) and `weak_ci_flag` (ROI CI crosses zero OR hit_rate CI width > 0.20).
- Deployment-throughput context: mean entry price, daily opportunity rate, expected cents per dollar capital per day.
- Headline rankings emitted in `validation_report.md`: top-20 cells by cents-optimal realized cents AND top-20 by ROI-optimal realized ROI per A39 (§5).

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

## 2. The cell / exit-line key

### 2.1 Definition

The 72 cells are FIXED: `cell_key` = Rung 0's `cell_key` (string, `"{category}__{price_band}"`, e.g. `"WTA_CHALL__0.30-0.35"`) — 4 categories (ATP_MAIN, ATP_CHALL, WTA_MAIN, WTA_CHALL) × 18 price bands (5-95c, 5c step). The cell is the T-20m recorded entry; it does not change. The exit axis is what is continuous (v0.2, §2.2).

Row keys (v0.3 two-artifact shape, §3.2):
- **Artifact A** (the dense exit-curve table) is keyed `(cell_key, exit_line_cents)` where `exit_line_cents` ∈ {1, 2, ..., 98} (every 1c). 72 cells × 98 exit lines = 7,056 rows.
- **Artifact B** (the per-cell optimum summary) is keyed `cell_key` alone. Exactly 72 rows — one data-derived optimum per fixed cell (separately for the cents / ROI / Sharpe regimes per A39, §3.2).

The v0.1 `(cell_key, threshold_cents)` 8-point / 576-row key is SUPERSEDED (v0.2 continuous axis + v0.3 two-artifact shape; provenance §9 v0.2/v0.3/v0.3.1 amendments).

### 2.2 The exit axis (v0.2 — continuous, per-cell data-derived)

v0.1 locked an 8-point absolute-cent grid (5/10/15/20/25/30/40/50). v0.2 replaces it. Rationale (operator scrutiny, recorded §9): a fixed ABSOLUTE grid is the wrong axis by the operation's own doctrine — LESSONS A39 (a +5c line is +20% ROI on a 25c cell vs +6.7% on a 75c cell; absolute-cent lines are not comparable across cells of different entry price) and LESSONS E32(e) verbatim ("Every band gets its own exit target derived from the band" — a universal fixed grid contradicts the per-band-derived-target model). This is the same defect class A39 already caught one level up in this spec's metric design; the grid is the same error relocated to the exit axis.

v0.2 design: the producer does NOT pre-impose an exit grid. For each cell it emits the **full per-row realized-outcome distribution** — the raw material from which any exit line's realized outcome is a pure downstream function of three Rung 0 columns already stored per N (`peak_bid_bounce_pre_resolution`, `realized_at_settlement`, `t20m_trade_price`). Per §2.3, for ANY candidate exit line L: `hit = peak_bounce_cents >= L`; `realized_cents = L if hit else realized_at_settlement_cents`. This is continuous in L by construction — the v0.1 grid was an unnecessary discretization of a function that is defined for all L.

The producer emits, per cell:
- The per-row arrays needed to evaluate any L: `peak_bid_bounce_pre_resolution`, `realized_at_settlement`, `t20m_trade_price` (and identity/context columns) for every N in the cell. This is the primitive; it is exit-axis-agnostic.
- A **dense realized curve** over a 1c absolute sweep (L = 1c..98c, every 1c) AND over a ROI-relative sweep (L = entry_price * m for m in a dense multiple set) AND a ceiling-relative reference (L as fraction of available room = 99c - entry_price), so all three A39-relevant views are precomputed for the report; NONE is privileged as "the" grid — they are views of the same per-row primitive.
- The **per-cell optimal exit line** = argmax over the dense absolute sweep of mean_realized (cents) AND, separately, argmax of mean_realized_roi (per A39 — both emitted, neither a proxy for the other; downstream picks the decision-appropriate one). The full realized curve is surfaced (§5) so the shape is visible — a clean peak vs a flat ridge vs a B13 ceiling-truncated cliff is decision-relevant and must not be summarized away.
- A **B13 ceiling-bind flag** per (cell, L): set when L is geometrically near-unreachable for that cell's entry price (L >= 99c - entry_price_cents - epsilon), so a cell is never falsely judged "no edge at L" when L was mathematically impossible there (LESSONS B13: bounded-variable ceiling artifacts must be flagged before interpreting threshold cliffs as edge findings).

Sample-quality and CIs (§3/§4) are computed AT the per-cell data-derived optimum (and at any downstream-requested L), not at 8 pre-chosen points — the Wilson/BCa machinery is unchanged, only its evaluation point becomes data-derived rather than locked.

### 2.3 Per-row realized cents computation (load-bearing)

For each Rung 0 row r and any candidate exit line L (continuous, 1..98c per §2.2; the v0.1 "threshold t in the grid" framing is superseded — the computation below is defined for any L, never a fixed grid):
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
- E32 specifies no stop. If the bot enters at T-20m and the price never reaches the +L exit line, the position rides to settlement.
- Under E32, settlement = first 99¢/1¢ touch. The position pays either +(99¢ − entry_price) if the bot's side wins, or −(entry_price − 1¢) if it loses.
- Rung 0 col 28 `realized_at_settlement` = `settlement_value_dollars − t20m_trade_price`, where `settlement_value_dollars` is 0.0 or 1.0. So a winning ride: 1.0 − 0.30 = +0.70 (= +70¢). A losing ride: 0.0 − 0.30 = −0.30 (= −30¢). Already in dollars; conversion to cents is *100.
- Approximation: under E32 the "first 99¢/1¢ touch" is the settlement event, NOT the actual final settlement. There's a small discrepancy where `settlement_value_dollars` (the final 0/1) is the true terminal value but the bot's position closes at the 99¢/1¢ touch moment. v1 uses `realized_at_settlement` (the 0/1 endpoint) as the conservative loss baseline — it slightly understates capture on winners (you could exit at 99¢ ≈ +69¢ rather than ride to 1.00 = +70¢, 1¢ difference) and exactly matches loss on losers (1¢ touch = the loss baseline). Net bias: trivially conservative on winners, exact on losers. Acceptable for v1; can be refined in Rung 1.5 with `first_extreme_touch_ts` (col 27) if it matters.

### 2.4 Why no separate "in-match exit" treatment in v0.1

E32's two-exit-window model (premarket + in-match) is unified at Rung 0's `peak_bid_pre_resolution` metric: it captures the peak across both windows up to first-extreme-touch. Rung 1 v0.1 aggregates over both. Rung 0 col 21 `peak_bid_in_premarket` is preserved for Rung 1.5 stratification but doesn't change the v0.1 metric definitions.

---

## 3. The core metrics (v0.3 — evaluated on the continuous exit axis)

Plex's synthesis (commit 3f7dc02c) inventoried 50+ candidate metrics. v0.1 ships 16 critically-selected metrics that produce the decision surface; the other 35+ are reference inventory for Rung 1.5+ work.

Selection criteria for v0.1:
1. **Both cents AND ROI must be represented** in every category (per A39).
2. **CIs on every estimate** (per A21).
3. **No mechanical redundancy** — `mean_realized_bounce_cents` and `expected_value_cents` are the same number with different labels; v1 emits only the operationally-named one.
4. **No diagnostic-only metrics** in v1 (e.g., `threshold_hit_rate_full_window` exists only as a sanity comparator against A38 saturation; v1 doesn't ship it as a row column).
5. **Greek labels excluded** (deferred entirely to Rung 1.5; v0.1 ships clean of them).
6. **(v0.2) Evaluation point is data-derived, not grid-locked.** Every metric below is computed at the per-cell optimal exit line (argmax of the dense realized curve, emitted separately for cents and ROI per A39) and is also computable at any downstream-requested L from the emitted per-row primitive. "Per (cell, threshold)" throughout §3/§4 now means "per (cell, evaluated-exit-line)" where the headline evaluated line is the per-cell data-derived optimum; the locked-grid framing is superseded per §2.2 v0.2.

### 3.1 The 16 metrics (definitions)

**RETURN (5 metrics + CIs):**

1. `threshold_hit_rate` — fraction of cell rows where `peak_bid_bounce_pre_resolution >= L/100` (L the candidate exit line). Wilson CI bounds.
2. `mean_realized_cents` — mean of per-row `realized_cents` (per Section 2.3 derivation). BCa bootstrap CI bounds.
3. `mean_realized_roi_pct` — mean of per-row `realized_roi * 100` (ROI in percent). BCa bootstrap CI bounds.
4. `median_realized_cents` — median of per-row `realized_cents`. BCa bootstrap CI bounds for the median.
5. `median_realized_roi_pct` — median of per-row `realized_roi * 100`. BCa bootstrap CI bounds for the median.

**RISK (3 metrics + CIs):**

6. `std_realized_cents` — std of per-row `realized_cents` distribution. BCa bootstrap CI bounds.
7. `std_realized_roi_pct` — std of per-row `realized_roi * 100`. BCa bootstrap CI bounds.
8. `downside_std_realized_cents` — std of per-row `realized_cents` filtered to negative values only (downside convention per Plex Resolution 2: downside is the actual loss distribution under E32's no-stop logic, NOT zero-return). BCa bootstrap CI bounds. If all rows in the (cell, exit-line) group are positive (no losing rides at this exit line), set to 0.0 and flag in `weak_ci_flag`.

**RISK-ADJUSTED (2 metrics + CIs):**

9. `sharpe_like_roi` — `mean_realized_roi_pct / std_realized_roi_pct`. BCa bootstrap CI bounds via resampled ratio distribution. If denominator is 0 (no variance in realized ROI within the group, extremely unlikely), return null and flag.
10. `sortino_like_roi` — `mean_realized_roi_pct / downside_std_realized_roi_pct`. BCa bootstrap CI bounds. Same null/flag handling.

`downside_std_realized_roi_pct` is computed inline (negative-ROI-only std) but not emitted as a separate column — its only purpose is the Sortino denominator. Same for `sharpe_like_cents` and `sortino_like_cents`; the ROI variants are operator-preferred per A39 + Plex inventory.

**SAMPLE-QUALITY (4 metrics, no CIs needed):**

11. `observations_n` — count of Rung 0 rows in the (cell, exit-line) group. Equal to `band_n_count` from Rung 0 col 13 by construction (every row in the cell contributes to every exit line; Rung 1 doesn't drop rows per-exit-line).
12. `unique_match_count` — distinct `event_ticker` count in the group. Will be ≤ `observations_n` (matches with both sides in the same cell would double-count, though under E32's price-symmetric pairing this is rare — both sides of a 0.50 match could land in the 0.45-0.50 and 0.50-0.55 bands, falling in different cells most of the time).
13. `low_n_flag` — boolean: `observations_n < 30`. Surfaces the small-sample warning per A21.
14. `weak_ci_flag` — boolean: TRUE if any of: (a) `mean_realized_roi_pct` BCa CI crosses zero, OR (b) `threshold_hit_rate` Wilson CI width > 0.20, OR (c) `low_n_flag` is TRUE. Composite filter for "this estimate isn't statistically stable."

**CAPITAL & THROUGHPUT (2 metrics + 1 context column):**

15. `mean_entry_price_cents` — mean of `t20m_trade_price * 100` across the cell. Same for every exit line within a cell (cell-level). Required context for ROI interpretation.
16. `expected_cents_per_dollar_capital_day` — `(mean_realized_cents * daily_opportunity_rate) / mean_entry_price_cents`. The bot's actual deployment-EV metric: "how many cents do I earn per dollar of capital deployed per day if I run this (cell, exit-line) strategy?" Emitted in Artifact A (cell-level inputs, evaluated at each exit line's `mean_realized_cents`) and in Artifact B at the cents- and ROI-optimal exits (§3.2).

Plus one helper column (not in the count of 16; computed from row timestamps):

- `daily_opportunity_rate` — `observations_n / corpus_active_days_in_sample`, where `corpus_active_days_in_sample` is the count of distinct dates in the corpus where Rung 0 emitted rows (computed once on the FULL unfiltered Rung 0 corpus and reused per row). Measures **N's-per-day** for this cell (per LESSONS G22: N is the player-binary market, the unit-of-observation; ct is the position-size unit. Each row is one N, not one ct). Same for every exit line within a cell (cell-level). Note: this is the corpus-wide rate (averaging across active and dead days). Per-category and per-cell active-day-normalized rate variants are deferred to Rung 1.5 — the corpus-wide rate is the operationally-correct denominator for the v0.1 deployment-EV math.

### 3.2 The two output artifacts (v0.3)

v0.3 emits TWO artifacts (the v0.1 single 576-row grid table is superseded — see §9 v0.3 amendment):

**Artifact A — the dense exit-curve table** (`strategy_evaluation_curve.parquet`). One row per (cell_key, exit_line_cents) where exit_line_cents sweeps 1..98 at 1c step. 72 cells x 98 lines = 7,056 rows (less any (cell,line) with zero contributing rows — none expected; every cell row contributes to every line per the §2.3 hit test). This IS the per-cell curve — the evidence. Schema (per (cell, exit_line)):

| # | Column | Type | Source / formula |
|---|---|---|---|
| 1 | `cell_key` | string | Rung 0 cell_key |
| 2 | `category` | string | Rung 0 category (denormalized) |
| 3 | `price_band` | string | Rung 0 price_band (denormalized) |
| 4 | `exit_line_cents` | int16 | the candidate exit line, 1..98 (replaces the v0.1 locked threshold_cents) |
| 5 | `threshold_hit_rate` | float | §3.1 metric 1 at this exit_line |
| 6 | `threshold_hit_rate_ci_lower` | float | Wilson lower |
| 7 | `threshold_hit_rate_ci_upper` | float | Wilson upper |
| 8 | `mean_realized_cents` | float | §3.1 metric 2 |
| 9 | `mean_realized_cents_ci_lower` | float | BCa lower |
| 10 | `mean_realized_cents_ci_upper` | float | BCa upper |
| 11 | `mean_realized_roi_pct` | float | §3.1 metric 3 |
| 12 | `mean_realized_roi_pct_ci_lower` | float | BCa lower |
| 13 | `mean_realized_roi_pct_ci_upper` | float | BCa upper |
| 14 | `median_realized_cents` | float | §3.1 metric 4 |
| 15 | `median_realized_roi_pct` | float | §3.1 metric 5 |
| 16 | `std_realized_cents` | float | §3.1 metric 6 |
| 17 | `std_realized_roi_pct` | float | §3.1 metric 7 |
| 18 | `downside_std_realized_cents` | float | §3.1 metric 8 |
| 19 | `sharpe_like_roi` | float or null | §3.1 metric 9 |
| 20 | `sortino_like_roi` | float or null | §3.1 metric 10 |
| 21 | `observations_n` | int32 | §3.1 metric 11 (cell-level; same across all exit_lines in a cell) |
| 22 | `unique_match_count` | int32 | §3.1 metric 12 (cell-level) |
| 23 | `low_n_flag` | bool | §3.1 metric 13 (cell-level) |
| 24 | `weak_ci_flag` | bool | §3.1 metric 14 (evaluated at this exit_line) |
| 25 | `b13_ceiling_bind_flag` | bool | TRUE when exit_line_cents >= (99 - entry_price_cents - 1) for this cell — the line is geometrically near-unreachable (LESSONS B13); set so a cell is never falsely judged "no edge at this line" when the line was mathematically impossible there |
| 26 | `mean_entry_price_cents` | float | §3.1 metric 15 (cell-level) |
| 27 | `daily_opportunity_rate` | float | helper (N's/day for this cell per G22; cell-level) |
| 28 | `expected_cents_per_dollar_capital_day` | float | §3.1 metric 16 — (mean_realized_cents_at_this_exit_line × daily_opportunity_rate) / mean_entry_price_cents; the deployment-EV per dollar capital per day (cell-level inputs, evaluated at this exit_line's mean_realized_cents) |

CI bounds emitted only on the four decision-load-bearing metrics (hit_rate Wilson; mean_cents / mean_roi / the ratio metrics BCa) to keep the dense table tractable at 7,056 rows x 1000-resample bootstrap; the full 24-CI inventory from v0.1 is preserved in Artifact B at the per-cell optimum (where decisions are actually read) per §3.1/§4. std/median emitted as point estimates on the dense curve (shape diagnostics, not the decision read).

**Artifact B — the per-cell optimum summary** (`strategy_evaluation_optimum.parquet`). Exactly 72 rows (one per cell). For each cell, the DATA-DERIVED optimal exit line, separately for the cents view and the ROI view (A39 — they answer different questions and their optima differ), each with that line's full metric+CI set:

| # | Column | Type | Source / formula |
|---|---|---|---|
| 1 | `cell_key` | string | the cell |
| 2 | `category` | string | denormalized |
| 3 | `price_band` | string | denormalized |
| 4 | `observations_n` | int32 | cell row count |
| 5 | `unique_match_count` | int32 | distinct event_ticker in cell |
| 6 | `low_n_flag` | bool | observations_n < 30 |
| 7 | `mean_entry_price_cents` | float | cell mean entry |
| 8 | `daily_opportunity_rate` | float | N's/day (G22) |
| 9 | `opt_cents_exit_line` | int16 | argmax over the dense curve of mean_realized_cents for this cell (B13-bound lines excluded from the argmax search) |
| 10 | `opt_cents_mean_realized_cents` | float | mean_realized_cents at opt_cents_exit_line |
| 11 | `opt_cents_mean_realized_cents_ci_lower` | float | BCa lower at that line |
| 12 | `opt_cents_mean_realized_cents_ci_upper` | float | BCa upper |
| 13 | `opt_cents_hit_rate` | float | hit_rate at that line |
| 14 | `opt_cents_hit_rate_ci_lower` | float | Wilson lower |
| 15 | `opt_cents_hit_rate_ci_upper` | float | Wilson upper |
| 16 | `opt_cents_mean_realized_roi_pct` | float | mean ROI at the cents-optimal line (cross-view reference) |
| 17 | `opt_cents_weak_ci_flag` | bool | §3.1 metric 14 at that line |
| 18 | `opt_roi_exit_line` | int16 | argmax over the dense curve of mean_realized_roi_pct for this cell (B13-bound lines excluded) |
| 19 | `opt_roi_mean_realized_roi_pct` | float | mean ROI at opt_roi_exit_line |
| 20 | `opt_roi_mean_realized_roi_pct_ci_lower` | float | BCa lower |
| 21 | `opt_roi_mean_realized_roi_pct_ci_upper` | float | BCa upper |
| 22 | `opt_roi_hit_rate` | float | hit_rate at that line |
| 23 | `opt_roi_hit_rate_ci_lower` | float | Wilson lower |
| 24 | `opt_roi_hit_rate_ci_upper` | float | Wilson upper |
| 25 | `opt_roi_mean_realized_cents` | float | mean cents at the ROI-optimal line (cross-view reference) |
| 26 | `opt_roi_weak_ci_flag` | bool | §3.1 metric 14 at that line |
| 27 | `opt_sharpe_exit_line` | int16 | argmax over the dense curve of sharpe_like_roi (risk-adjusted regime; B13-bound excluded) |
| 28 | `opt_sharpe_value` | float or null | sharpe_like_roi at that line |
| 29 | `opt_sharpe_mean_realized_roi_pct` | float | mean ROI at the Sharpe-optimal line |
| 30 | `curve_shape_note` | string | one of {"clean_peak","flat_ridge","ceiling_truncated","monotone","weak_low_n"} — deterministic classifier over the cell's dense curve (peak prominence + B13-bind fraction + low_n), so the summary states whether the optimum is a robust peak or fragile; definition in §5.3 |
| 31 | `opt_cents_expected_cents_per_dollar_capital_day` | float | §3.1 metric 16 evaluated at opt_cents_exit_line (deployment-EV per dollar capital per day at the cents-optimal exit) |
| 32 | `opt_roi_expected_cents_per_dollar_capital_day` | float | §3.1 metric 16 evaluated at opt_roi_exit_line (deployment-EV per dollar capital per day at the ROI-optimal exit) |

Artifact B is a PURE DETERMINISTIC read off Artifact A (argmax + the already-computed metrics/CIs at the argmax line) — no additional modeling, no additional bootstrap beyond what Artifact A already computed at that line. The two artifacts are consistency-gated (§6 gate 7).

---

## 4. Bootstrap design (locked per Plex Resolution 1)

### 4.1 Within-cell bootstrap (the v0.1 default for all metrics)

Row-level bootstrap with n=1000 resamples. BCa where computable; percentile fallback if BCa fails to converge (rare; flagged in validation report).

Justification (operator-readable): Rung 0 emits one row per N per side. The two sides of a paired match fall in different price bands (their T-20m prices sum to ~$1, so one side at 0.30 puts the other at 0.70 — different cells). Within a single cell, rows are functionally independent observations from different matches. Row-level resampling is statistically correct at the within-cell level. (v0.2) The bootstrap is evaluated at the per-cell data-derived optimal exit line (and any downstream-requested L), not at 8 locked grid points; the resampling protocol (row-level, n=1000, BCa with percentile fallback) is unchanged — only the evaluation point becomes data-derived. CIs are therefore reported on the ACTUAL per-cell optimum, not on whichever of 8 arbitrary points was nearest it (a strict improvement in decision-relevance).

BCa specifics:
- 1000 bootstrap resamples per (cell, exit-line) metric.
- Bias-corrected and accelerated; falls back to percentile bootstrap if BCa acceleration parameter computation fails.
- 95% CIs (2.5th and 97.5th percentile of the bootstrap distribution under percentile; BCa-adjusted equivalents).
- For ratio metrics (Sharpe-like, Sortino-like), bootstrap the ratio directly (resample the rows, recompute the ratio per resample) rather than bootstrapping numerator and denominator separately.

### 4.2 Cross-cell bootstrap (Rung 1.5 follow-up, not v0.1)

When metrics aggregate across cells where the same match contributes to multiple cells, match-clustered resampling at `event_ticker` level is required. Plex's `variance_across_cells_at_threshold` would need this. v0.1 doesn't emit cross-cell aggregates; the clustering protocol is documented for Rung 1.5.

---

## 5. Headline rankings emitted in validation_report.md

The producer emits both parquets AND a markdown report:

### 5.1 Top-20 cells by cents-optimal realized cents (A39 cents view)
From Artifact B sorted by `opt_cents_mean_realized_cents` desc: cell_key, observations_n, opt_cents_exit_line, the cents value with CI, the cross-view ROI, low_n_flag, opt_cents_weak_ci_flag, curve_shape_note.

### 5.2 Top-20 cells by ROI-optimal realized ROI (A39 ROI view)
From Artifact B sorted by `opt_roi_mean_realized_roi_pct` desc: same structure, ROI-view columns. Per A39 the two top-20 lists are expected to differ materially; their overlap fraction is surfaced (§6.2).

### 5.3 Curve-shape classifier (definition + per-cell table)
`curve_shape_note` deterministic rules over a cell's dense Artifact-A curve (mean_realized_cents vs exit_line, B13-bound lines excluded from peak search): "weak_low_n" if low_n_flag; else "ceiling_truncated" if >50% of 1..98 lines are b13_ceiling_bind_flag; else "monotone" if |Spearman(exit_line, mean_realized_cents)| >= 0.9; else "clean_peak" if the max is >= 1.0c above both the value at the lowest non-B13 line and the value 10c either side of the argmax; else "flat_ridge". Emit the 72-cell table of cell_key -> curve_shape_note + opt_cents_exit_line + peak prominence (max minus the mean of the curve).

### 5.4 Per-cell recommended exit (the deliverable headline)
The 72-cell table: cell_key, opt_cents_exit_line (+ cents & CI), opt_roi_exit_line (+ ROI & CI), opt_sharpe_exit_line, curve_shape_note, low_n_flag, weak_ci_flags. This is the operator-facing answer — per cell, the data-derived exit line under each regime, with the curve-shape honesty flag.

### 5.5 Sample-quality summary
Counts of cells by low_n_flag and by curve_shape_note. How many of 72 cells have a clean_peak vs flat_ridge vs ceiling_truncated vs weak_low_n cents-optimum. Coverage read: which categories (ATP_MAIN/ATP_CHALL/WTA_MAIN/WTA_CHALL) carry the clean-peak cells.

---

## 6. Validation gates

### 6.1 Hard gates (must PASS before os.replace, per C37)

Gates run against the reloaded-from-disk .new bytes of BOTH artifacts.

1. **Curve table row count.** Artifact A has exactly 72 cells x 98 exit_lines = 7,056 rows. Zero missing (cell_key, exit_line_cents) combinations in the 72 x (1..98) cross-product; zero duplicates. Zero violations.
2. **Summary row count.** Artifact B has exactly 72 rows, one per cell_key, every one of the 72 fixed cells present exactly once. Zero violations.
3. **Hit-rate monotonicity within cell.** In Artifact A, for each cell, `threshold_hit_rate` is monotonically non-increasing as `exit_line_cents` increases (higher line = lower hit rate, by construction). Zero violations (tolerance 1e-9 for float noise).
4. **Realized-cents bounds.** In Artifact A, for each row, `mean_realized_cents` <= `exit_line_cents` (hit rows contribute exactly the line; miss rows ride to settlement, <= the line) AND `mean_realized_cents` >= the cell's worst single-row `realized_at_settlement * 100`. Zero violations either bound.
5. **CI ordering.** Every emitted CI triple (point, lower, upper) in BOTH artifacts satisfies lower <= point <= upper. Zero violations.
6. **Sample-quality consistency.** Wherever `low_n_flag` is TRUE, `weak_ci_flag` is TRUE (weak_ci_flag is the OR-composite including low_n_flag), in both artifacts. Zero violations.
7. **Summary-derivation consistency (the v0.3 load-bearing gate).** Artifact B is a pure read off Artifact A: for every cell, `opt_cents_exit_line` equals the argmax of Artifact A's `mean_realized_cents` over that cell's non-B13-bound lines, and `opt_cents_mean_realized_cents` (and its CIs, hit_rate, etc.) equals Artifact A's value at exactly that (cell, opt_cents_exit_line) row — byte-equal on the metric, CI-consistent. Same for the ROI-optimal and Sharpe-optimal lines. Zero violations: the summary must be derivable from the curve, never independently computed.
8. **Mean-vs-median soft gate (logged, not blocking).** In Artifact A, count rows where `mean_realized_cents < median_realized_cents` (legit for high-losing-ride groups); surface the count in validation_report, do not block.

### 6.2 Informative measurements (logged, not gating)

- Per-cell n_observations distribution (anchor for Rung 1.5 weight-by-N considerations).
- BCa convergence rate across the CI-bounded metrics emitted (Artifact A emits Wilson on hit_rate + BCa on mean_cents/mean_roi/ratio metrics; Artifact B carries the full CI set at the per-cell optimum). If >5% of CI computations fall back to percentile, surface in validation_report as a numerical-stability flag.
- Cross-exit-line cell-rank stability. For each cell, how does its rank-by-cents change across the continuous exit axis? Cells with stable rankings are more robust deployment candidates; cells with rank flipping across nearby exit lines are exit-line-sensitive (relates to curve_shape_note §5.3).
- Exit line at which each cell becomes weak_ci_flagged. Concrete read on "this cell supports up to exit line L before the data runs thin."
- Top-20-by-cents and top-20-by-ROI overlap fraction (§5.1/§5.2). A39 predicts low overlap (the rankings answer different questions); the actual fraction is a validation of A39's strength on this corpus.
- `expected_cents_per_dollar_capital_day` (§3.1 metric 16) sanity: informative only — a negative or extreme value at a cell's optimum is flagged in validation_report (not a hard gate; it is a restored existing metric, not new scope).

---

## 7. Producer architecture

### 7.1 Input

- `data/durable/rung0_cell_economics/cell_economics.parquet` (read-only, sha256 `6fdd019d…`)

That's the only input. Rung 1 is a derived table from Rung 0; no foundation-corpus access needed.

### 7.2 Processing

Vectorized pandas (14,033 rows x 36 cols, comfortably in RAM):
1. Load Rung 0 parquet (the only input).
2. Compute `corpus_active_days_in_sample` once = distinct dates in the FULL unfiltered Rung 0 corpus; reused per cell.
3. Group by `cell_key` (the 72 fixed cells; cell = T-20m recorded entry, 4 categories x 18 bands).
4. For each cell, for each exit_line in 1..98 (1c step): compute per-row hit/realized_cents/realized_roi via §2.3 (continuous in the line by construction), aggregate the §3.1 metrics, compute CIs (Wilson closed-form for hit_rate; row-level n=1000 BCa per §4 for mean_cents/mean_roi/ratio metrics — fallback to percentile, flagged), set b13_ceiling_bind_flag. -> Artifact A (the dense curve).
5. For each cell, derive Artifact B by argmax over Artifact A's non-B13-bound lines (separately for mean_realized_cents, mean_realized_roi_pct, sharpe_like_roi) and copy that line's already-computed metrics/CIs; compute curve_shape_note per §5.3. Artifact B is a pure read of Artifact A — no new bootstrap.
6. Validation gates §6 against reloaded .new bytes of BOTH artifacts.
7. C37: write both `.new`; if all hard gates PASS, os.replace both; else halt, preserve both .new, write halt log to logs/, exit non-zero.
8. Generate validation_report.md (§5).

### 7.3 Runtime budget

- 7,056 (cell x exit_line) groups x 3 bootstrap metrics x 1000 resamples ~= 21M bootstrap computations (each a small array op on ~30-330 floats); Artifact B adds zero bootstrap (pure argmax read of Artifact A).
- Each bootstrap computation is a small array operation (mean, std, or percentile on ~50-330 floats).
- Expected runtime: 15-45 minutes single-threaded (denser exit axis than v0.1); numpy-vectorized bootstrap recommended. Phased rollout 1/2/3 (subsample cells -> all cells -> all cells + report).
- Memory: ~10 MB peak (14,033 rows × 36 cols ~1.7 MB; transient bootstrap arrays add <10 MB at peak). Well within VPS limits.

### 7.4 Output

- `data/durable/rung1_strategy_evaluation/strategy_evaluation_curve.parquet` (Artifact A — 7,056 rows x 28 cols, the dense per-cell exit curve)
- `data/durable/rung1_strategy_evaluation/strategy_evaluation_optimum.parquet` (Artifact B — 72 rows x 32 cols, the per-cell data-derived optimum, cents & ROI & Sharpe regimes)
- `data/durable/rung1_strategy_evaluation/validation_report.md` (§5)
- `data/durable/rung1_strategy_evaluation/strategy_evaluation.meta.json` (sidecar: both sha256s, input sha256 6fdd019d, producer commit, run timestamp)

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
- Classification axes: TAXONOMY Section 2.5 (Rung 1 GRAIN is per-(cell, exit-line) for the curve artifact and per-cell for the optimum artifact, VECTOR is realized-return-over-the-continuous-exit-axis; OBJECTIVE = exit-optimized).
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

### v0.2 amendment — 2026-05-19 ET (operator scrutiny: continuous exit axis)

The v0.1 operator-locked 8-point absolute grid (§2.2) is SUPERSEDED. Operator scrutiny established it as the same defect class LESSONS A39 already caught one level up in this spec: a fixed ABSOLUTE-cent grid is the wrong exit axis because absolute-cent lines are not comparable across cells of different entry price (A39: +5c = +20% ROI at 25c vs +6.7% at 75c), and LESSONS E32(e) states verbatim "Every band gets its own exit target derived from the band" — a universal fixed grid contradicts E32's own per-band-derived-target model. v0.2 replaces the grid with a continuous design: emit the per-cell per-row realized-outcome distribution as the exit-axis-agnostic primitive (a pure function of three already-stored Rung 0 columns per §2.3, which was already continuous-ready and is preserved unchanged); derive dense-absolute + ROI-relative + ceiling-relative views and the per-cell argmax-optimal exit (separately for cents and ROI per A39) downstream; flag B13 ceiling-bind per (cell, L). §3/§4 metrics+bootstrap retargeted from "8 locked points" to "the per-cell data-derived optimum + any downstream L" (machinery unchanged, evaluation point now data-derived). Honest provenance: the v0.1 grid was an operator-locked constraint at spec-authoring time, superseded by later operator scrutiny — recorded, not silently rewritten, same discipline this spec already applied to the A39 cents-vs-ROI catch (G23/4f55339 honest-provenance lineage). No producer exists yet at v0.2; producer build follows in a separate single-concern commit against this amended spec.

### v0.3 amendment — 2026-05-19 ET (spec-coherence: §3.2/§5/§6/§7 made consistent with the continuous design)

v0.2 amended §2.2 to the continuous per-cell design but left §3.2/§5/§6/§7 v0.1-grid-shaped (still "{5..50}", "576 rows", "72 x 8") — the spec contradicted itself and "build to spec" was undefined. v0.3 makes the whole spec coherent. Output shape (operator decision): BOTH a dense (cell x 1c exit line, 1..98) curve table = the evidence, AND a 72-row per-cell-optimum summary (data-derived optimal exit separately for cents and ROI and Sharpe per A39, each with that line's metrics/CIs, plus a deterministic curve_shape_note) = the answer. The 72 cells (4 categories x 18 bands, cell = T-20m recorded entry) are FIXED and unchanged; only the exit axis became continuous. Artifact B is a pure deterministic read of Artifact A, consistency-gated (§6 gate 7). §2.2/§2.3 preserved. Honest provenance: v0.2 left the spec internally incoherent; v0.3 resolves it — recorded, not silently reshaped (G23/4f55339 lineage). No producer exists at v0.3; producer build follows in a separate single-concern commit against this amended spec.

### v0.3.1 amendment — 2026-05-19 ET (whole-spec coherence completion + metric-16 restoration)

v0.3 made §3.2/§5/§6/§7 continuous-coherent but a full-file sweep found the dead v0.1 grid ALSO surviving in §1/§1.1/§1.2 (scope/operational-def/in-scope), the §1.2 "Anchored to" + §8 GRAIN/VECTOR cross-refs, the §3 title, §3.1 metric-def wording, §2.3 L101 derivation prose, and §6.2 informative bullets — and that v0.3 had DROPPED §3.1 metric 16 (expected_cents_per_dollar_capital_day, the deployment-EV-per-dollar-capital number) from BOTH artifact schemas. The spec was still internally incoherent after v0.3 and was missing its most operator-relevant throughput metric. v0.3.1 closes EVERY surviving REAL dead-grid contradiction in one pass (§1/§1.1/§1.2/§2.3-prose/§3-title/§3.1-wording/§6.2/§8/§12-anchor) consistent with the two-artifact continuous design, and RESTORES metric 16 into Artifact A (cell-level col) and Artifact B (at each regime optimum). §9 historical logs + v0.2/v0.3 amendment blocks + v0.2/v0.3 supersession notes + deferred-metric proper nouns + v0.3 schema column names preserved untouched (benign provenance). Honest provenance: v0.2 and v0.3 were each INCOMPLETE coherence passes (scoped to edited sections, not whole-spec verified) and v0.3 additionally introduced a metric-drop regression — the recurring scoping-incompleteness pattern; the durable fix is whole-file defect-class sweep BEFORE asserting coherence, applied here. Spec is internally consistent ONLY at v0.3.1 — producer build unblocked at v0.3.1, not before.
