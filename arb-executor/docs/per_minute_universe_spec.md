# Per-Minute Universe specification — the foundational observation grain

**Status:** SPEC (T37a). Implementation gated on spec closure (T37b producer build + T37c verification gate).

**Author:** Druid (operator) + chat-side Claude (Opus 4.7) + Code (Claude Code desktop, executor) — Session 11 drafting.

**Foundation pointers:**

- **T28 G9 parquets** (commit `ea84e74`, sha256-pinned per `MANIFEST.md`). `g9_candles.parquet` is the per-minute BBO + OHLC + OI + volume source; `g9_trades.parquet` is the microsecond-resolution trade tape; `g9_metadata.parquet` is the per-ticker lifecycle metadata.
- **ANALYSIS_LIBRARY Cat 11** (commit `4e36f30`) — Layer B v1 / v2 corpus measurement anchored on cell-keyed aggregation. Per-minute universe supersedes the cell-keyed binning as the canonical observation grain for downstream analytical questions; cell aggregation becomes one optional grouping dimension, not the unit of measurement.
- **LESSONS A22** (measurement universe is not bid/ask/spread), **A24** (variable inventory is the foundation), **A26** (taker_side is in trade CSVs), **A35** (volume per minute as match-start anchor), **B14, B15** (match-level aggregates conflate time-window opportunities; unit of analysis must match unit of decision), **B16** (Layer A / B / C separation principle), **G18** (G9 candles are honest BBO snapshots at minute close), **G19** (candle minute populate-status differs by field family — yes_bid/ask 100% populated, price/volume/OI ~65% null when no trades).

**Per LESSONS B15:** "Every variable in this domain is a flowing time series. There is no static snapshot of a market except settlement. The unit of analysis must match the unit of decision. Stratify on values-at-decision-time, not whole-match-aggregates."

**Per LESSONS A22:** "When designing measurement, ask: what dimension of this data have we NOT touched yet?"

The per-minute universe is the answer to both. One row per (ticker, minute). Every observable feature at that minute. Forward-looking labels for realized outcomes from that minute. Foundation table for every downstream analytical question — ranking, cohort selection, temporal routing, exit policy optimization — which then collapse to queries against this single table rather than requiring separate producers.

---

## 1. Scope (T37)

**Per-(ticker, minute) feature table covering the full G9 corpus.**

In scope:

- **Every ticker in g9_metadata** (20,110 tickers). No sampling cap. The producer reads every ticker, evaluates every minute of its tradeable life.
- **Every minute the ticker existed in g9_candles** (~210-720 minutes per ticker depending on premarket length and match duration). The minute set is exactly the set of `end_period_ts` values in g9_candles for that ticker; no synthetic minute fill, no padding outside observed lifespan.
- **Premarket + in_match + settlement_zone** all included. Regime classification per minute is a derived feature column, not a filter. Downstream consumers select regime via query.
- **All 5 categories** (ATP_MAIN, ATP_CHALL, WTA_MAIN, WTA_CHALL, OTHER). No category exclusion.
- **All policy-evaluation grain.** This producer does NOT evaluate exit policies. Exit policy evaluation is a separate downstream concern (Layer B-equivalent query against this table). The per-minute universe outputs the raw observation + forward-looking labels; policy logic lives in queries.

Out of scope for T37:

- **Exit policy evaluation.** Deferred to downstream queries against this table. Layer B v2's policy grid logic (limit / time_stop / trailing / limit_time_stop / limit_trailing) becomes a vectorized pandas operation over the forward-looking label columns of this table.
- **Cell-key aggregation.** Cell-key fields (category, entry_band, spread_band, volume_intensity, regime) are emitted as columns so downstream consumers can group by them, but the producer does NOT pre-aggregate to cell summaries. Cell summaries become groupby operations against this table.
- **Fees.** Same as Layer B v2 — fees are a Layer C concern, layered on at consumption time.
- **In-match channel cell-key tracking.** Premarket cells are derived directly from the bid/ask/volume columns. In-match minutes are flagged via the regime column; downstream consumers compute in-match cells if needed.
- **Capital, queue position, sizing, paired-leg modeling.** All deferred to downstream layers.

---

## 2. The per-minute schema

One row per (ticker, minute). Schema is a flat parquet with columns grouped logically below.

### 2.1 Identity columns

| Column | Type | Source | Notes |
|---|---|---|---|
| `ticker` | string | g9_candles | Primary key component |
| `event_ticker` | string | g9_metadata | Pairs the two players in a match (player1/player2 tickers share event_ticker) |
| `minute_ts` | int64 (unix seconds) | g9_candles.end_period_ts | Minute close timestamp (UTC). Primary key component. |
| `category` | string | derived from ticker prefix | ATP_MAIN / ATP_CHALL / WTA_MAIN / WTA_CHALL / OTHER. Per `cell_key_helpers.py:categorize`. |
| `player_competitor_uuid` | string | g9_metadata.custom_strike | Sportradar UUID; enables cross-ticker player joins |

### 2.2 BBO range within the minute (G9 candle native, 100% populated per G19)

| Column | Type | Notes |
|---|---|---|
| `yes_bid_open` | float64 | Yes-side bid at minute start |
| `yes_bid_high` | float64 | Yes-side bid high within the minute |
| `yes_bid_low` | float64 | Yes-side bid low within the minute |
| `yes_bid_close` | float64 | Yes-side bid at minute close (canonical snapshot per G18) |
| `yes_ask_open` | float64 | Yes-side ask at minute start |
| `yes_ask_high` | float64 | Yes-side ask high within the minute |
| `yes_ask_low` | float64 | Yes-side ask low within the minute |
| `yes_ask_close` | float64 | Yes-side ask at minute close |
| `spread_close` | float64 | yes_ask_close − yes_bid_close (derived) |
| `mid_close` | float64 | (yes_ask_close + yes_bid_close) / 2 (derived) |
| `bid_range_intra_minute` | float64 | yes_bid_high − yes_bid_low (derived; non-zero = bid moved within minute) |
| `ask_range_intra_minute` | float64 | yes_ask_high − yes_ask_low (derived) |

Per LESSONS G18: yes_bid_close and yes_ask_close are honest BBO snapshots at minute close — 71% / 63% exact match against B-tier per-tick BBO sampled at minute end. Use _close as the canonical instantaneous-quote feature. Use the open/high/low/close range when intra-minute movement matters (a non-zero `bid_range_intra_minute` flags book movement that the close alone misses).

### 2.3 Trade activity within the minute (G9 candle + trades, ~65% null per G19)

| Column | Type | Notes |
|---|---|---|
| `price_close` | float64 | Last trade price in the minute (null if no trades) |
| `price_open` | float64 | First trade price in the minute |
| `price_high` | float64 | Highest trade price in the minute |
| `price_low` | float64 | Lowest trade price in the minute |
| `price_mean` | float64 | Mean trade price in the minute |
| `price_previous` | float64 | Last trade price as-of previous minute (forward-fill from last trade event) |
| `volume_in_minute` | float64 | Total contracts traded in the minute (g9_candles.volume_fp) |
| `trade_count_in_minute` | int32 | Number of trade events in the minute (count of g9_trades rows in [minute_ts−60, minute_ts)) |
| `minute_has_trade` | bool | trade_count_in_minute > 0 |
| `taker_yes_count_in_minute` | float64 | Sum of count_fp for trades where taker_side="yes" |
| `taker_no_count_in_minute` | float64 | Sum of count_fp for trades where taker_side="no" |
| `taker_flow_in_minute` | float64 | taker_yes_count − taker_no_count (signed; positive = net yes-buying) |
| `vwap_in_minute` | float64 | Volume-weighted avg trade price; null if no trades |

Per LESSONS A26 + G19: taker_side is in g9_trades. Trade columns are null when no trade occurred in the minute (~65% of corpus minutes per G19). Null is meaningful, not error.

### 2.4 Open interest

| Column | Type | Notes |
|---|---|---|
| `open_interest_at_minute_end` | float64 | g9_candles.open_interest_fp; null per G19 when no trade activity to update OI |
| `open_interest_ffill` | float64 | Forward-filled OI from last non-null observation (carries OI level forward through quiet minutes) |
| `open_interest_delta_from_prior_minute` | float64 | open_interest_ffill - open_interest_ffill(prior minute); positive = position growth, negative = position unwind |

OI is the only persistent state-of-the-market variable beyond price. Tracking deltas surfaces position-building and position-unwinding regimes that don't show up in price alone.

Per LESSONS G19: historical-tier markets (the pre-Apr-18-2026 subset) have OI null throughout in g9_candles because the historical pull backfill omits OI; live-tier markets (Apr 18 2026+) have OI populated. Producer emits null where source is null. Downstream consumers handle tier-aware OI availability via the `_tier` field in g9_metadata or directly via null-rate. Same disposition applies to `volume_in_minute` (g9_candles.volume_fp): null throughout for historical-tier; producer recomputes trade-derived activity from g9_trades into `trade_count_in_minute`, `taker_yes_count_in_minute`, `taker_no_count_in_minute`, `taker_flow_in_minute`, `vwap_in_minute` per Section 2.3 so trade activity is observable on historical-tier rows even where candle volume_fp is null.

### 2.5 Match-lifecycle timing

| Column | Type | Notes |
|---|---|---|
| `open_time_ts` | int64 | g9_metadata.open_time (market open, unix seconds) |
| `expected_expiration_ts` | int64 | g9_metadata.expected_expiration_time |
| `close_time_ts` | int64 | g9_metadata.close_time |
| `settlement_ts` | int64 | g9_metadata.settlement_ts |
| `match_start_ts` | int64 | Inferred from match-start signal hierarchy per LESSONS A35 amended v4. Four-level fallback chain: (1) `both_sides_price_discovery` — first K≥3 consecutive minutes where BOTH own.trade_count_in_minute ≥ M_TRADES AND partner.trade_count_in_minute ≥ M_TRADES AND own intra-minute range (bid OR ask) > R cents AND partner intra-minute range (bid OR ask) > R cents (defaults: K=3, M_TRADES=3, R=0.02); (2) `both_sides_trade_density` — same K=3, both-sides ≥3 trades, but no price-range gate; (3) `expected_expiration_fallback`; (4) `unknown` |
| `match_start_method` | string | "both_sides_price_discovery" / "both_sides_trade_density" / "expected_expiration_fallback" / "unknown" |
| `time_to_match_start_min` | float64 | (match_start_ts − minute_ts) / 60; negative once in-match |
| `time_to_close_min` | float64 | (close_time_ts − minute_ts) / 60 |
| `time_to_settlement_min` | float64 | (settlement_ts − minute_ts) / 60 |
| `minutes_since_open` | float64 | (minute_ts − open_time_ts) / 60 |

Per LESSONS C19: Kalshi market-lifecycle timestamps don't track actual match start (pooled stdev 13.5 hours across categories). Per LESSONS A35 amended v4 (2026-05-12 post-T37b Phase 1 v3 trade-count probe): the match-start signal is a **four-level fallback hierarchy** that distinguishes "active trading" from "active price discovery."

**Signal hierarchy:**
1. **`both_sides_price_discovery`** (primary): first minute in a run of K≥3 consecutive minutes where ALL of: own.trade_count_in_minute ≥ M_TRADES AND partner.trade_count_in_minute ≥ M_TRADES AND own intra-minute range (max(bid_range_intra_minute, ask_range_intra_minute)) > R AND partner intra-minute range (max(bid_range_intra_minute, ask_range_intra_minute)) > R. Defaults K=3, M_TRADES=3, R=0.02. The price-range gate filters premarket positioning (trades at stable prices) from match-driven price discovery (trades with material BBO movement).
2. **`both_sides_trade_density`** (fallback): same K=3 and both-sides ≥M_TRADES (default 3) condition, but no price-range gate. Captures the "first sustained both-sides trading" moment even when prices haven't yet diverged.
3. **`expected_expiration_fallback`**: g9_metadata.expected_expiration_time when no trade-based signal fires (e.g., extremely thin markets, partial data tier).
4. **`unknown`**: emitted when even the expected-expiration fallback yields a nonsensical value (e.g., expected_expiration > settlement_ts).

**Signal evolution rationale:** v1 used candle `volume_fp` (LESSONS G19: null throughout for historical-tier markets, returns "unknown" on ~58% of corpus). v2 used per-ticker `trade_count_in_minute > 0` (any non-zero) which fired on sporadic early-premarket trades far ahead of the visible regime change. v3 added the both-sides-simultaneous condition with M=5 to filter one-sided noise, but M=5 was too strict for many tickers (RUN had no K=3 run at M=5). v4 lowers M to 3 (matched against probe data showing 14:41 ET landing on RUN at M=3) and adds a price-range gate on top, with fallback to v3-style trade-density-only when the price-range signal is too strict. Tier-1 captures "match-driven price discovery"; tier-2 captures "active both-sides trading"; tier-3 captures "metadata-derived expectation"; tier-4 captures "no signal."

**Default values** (exposed as `MATCH_START_K_DEFAULT`, `MATCH_START_M_TRADES_DEFAULT`, `MATCH_START_R_DEFAULT` in producer code): K=3, M_TRADES=3, R=0.02. T37c validation gate inspects defaults on a stratified sample of 50 markets to either confirm or amend.

### 2.6 Regime classification

| Column | Type | Notes |
|---|---|---|
| `regime` | string | "premarket" / "in_match" / "settlement_zone" |
| `premarket_phase` | string | "formation" / "stable" / null (null if not premarket) |

Regime rules (sibling to Layer A v1 producer):
- `premarket`: minute_ts < match_start_ts AND minute_ts >= open_time_ts
- `in_match`: minute_ts >= match_start_ts AND minute_ts < settlement_ts − 300 (excludes final 5 minutes pre-settle)
- `settlement_zone`: minute_ts >= settlement_ts − 300 AND minute_ts <= settlement_ts

Premarket phase rules (NEW with T37, addressing operator's formation-vs-stable framing):
- `formation`: minutes_since_open < formation_window_min (default 120; tunable parameter)
- `stable`: minutes_since_open >= formation_window_min AND regime == "premarket"

The formation_window_min default is 120 (first 2 hours after market open). T37c validation gate inspects formation-vs-stable BBO behavior on a stratified sample of 50 markets to either confirm the 120-min default or amend.

### 2.7 Cell-key feature columns (denormalized for downstream groupby convenience)

| Column | Type | Notes |
|---|---|---|
| `entry_band_lo` | int | Lower bound of yes_ask_close entry band (0, 10, 20, ..., 90 cents) |
| `entry_band_hi` | int | Upper bound (10, 20, ..., 100 cents) |
| `spread_band` | string | "tight" / "medium" / "wide" per Layer A spread thresholds |
| `volume_intensity` | string | "low" / "mid" / "high" per Layer A volume thresholds |

These columns mirror the cell-key derivation in `cell_key_helpers.py`. They are emitted per-minute (not per-cell-aggregate) so downstream consumers can group however they want. The cell-key scheme becomes one possible grouping dimension; it is no longer the unit of measurement.

### 2.8 Forward-looking labels (the realized-outcome columns)

For each minute, compute the forward-looking max/min bid and ask within configurable horizons. These are the "what bounce was achievable from here" labels.

| Column | Type | Notes |
|---|---|---|
| `max_yes_bid_forward_5min` | float64 | Max yes_bid_high observed in (minute_ts, minute_ts + 300] |
| `max_yes_bid_forward_15min` | float64 | Max in 15 min |
| `max_yes_bid_forward_30min` | float64 | Max in 30 min |
| `max_yes_bid_forward_60min` | float64 | Max in 60 min |
| `max_yes_bid_forward_to_match_start` | float64 | Max from minute_ts to match_start_ts |
| `max_yes_bid_forward_to_settlement` | float64 | Max from minute_ts to settlement_ts |
| `min_yes_ask_forward_5min` | float64 | Min yes_ask_low observed in (minute_ts, minute_ts + 300] |
| `min_yes_ask_forward_15min` | float64 | Min in 15 min |
| `min_yes_ask_forward_30min` | float64 | Min in 30 min |
| `min_yes_ask_forward_60min` | float64 | Min in 60 min |
| `min_yes_ask_forward_to_match_start` | float64 | Min from minute_ts to match_start_ts |
| `min_yes_ask_forward_to_settlement` | float64 | Min from minute_ts to settlement_ts |
| `bounce_5min` | float64 | max_yes_bid_forward_5min − yes_ask_close (the bounce achievable if you posted a maker bid at this minute's bid level and the bid spiked within 5 min) |
| `bounce_15min` | float64 | Same construction over 15 min |
| `bounce_30min` | float64 | Same over 30 min |
| `bounce_60min` | float64 | Same over 60 min |
| `bounce_to_match_start` | float64 | Same to match-start |
| `bounce_to_settlement` | float64 | Same to settlement |
| `settlement_value` | float64 | g9_metadata.settlement_value_dollars; same across all minutes of a ticker |
| `result` | string | g9_metadata.result; same across all minutes of a ticker |

Per LESSONS B16: Layer A is the property of the market (forward bounce distribution). These forward-looking label columns ARE the Layer A measurement, computed per-minute instead of per-cell. Layer A v1 aggregated to per-cell distributions; this table preserves per-minute granularity. Per-cell distributions become groupby + percentile operations against these columns.

### 2.9 Paired-leg observables (added 2026-05-12 post-T37b Phase 1 visual review)

Every match has two tickers sharing the same `event_ticker` — the two players' YES-side contracts (e.g., `KXATPMATCH-25JUN18RUNMCD-RUN` and `KXATPMATCH-25JUN18RUNMCD-MCD`). They are inverse positions on the same underlying outcome: yes-side bid on RUN at $0.40 implies the market is pricing MCD's yes-side bid near $0.60, and so on. Analysis that looks at only one ticker's BBO sees half the picture; the partner's BBO carries inverse-side context that exposes arbitrage gaps, sided pressure, and paired-leg execution opportunities.

For each row, also emit the partner ticker's observables at the same minute:

| Column | Type | Notes |
|---|---|---|
| `partner_ticker` | string | The other ticker sharing this row's `event_ticker` (e.g., for RUN this is MCD) |
| `partner_yes_bid_close` | float64 | Partner's yes_bid_close at this minute |
| `partner_yes_ask_close` | float64 | Partner's yes_ask_close at this minute |
| `partner_spread_close` | float64 | Partner's spread_close (yes_ask − yes_bid) |
| `partner_volume_in_minute` | float64 | Partner's g9_candles.volume_fp (null pattern follows tier) |
| `partner_trade_count_in_minute` | int32 | Partner's trade events in [minute_ts−60, minute_ts) |
| `partner_taker_flow_in_minute` | float64 | Partner's taker_yes − taker_no in the minute (signed) |
| `partner_open_interest_ffill` | float64 | Partner's forward-filled OI |
| `paired_yes_bid_sum` | float64 | own.yes_bid_close + partner.yes_bid_close |
| `paired_yes_ask_sum` | float64 | own.yes_ask_close + partner.yes_ask_close |
| `paired_mid_sum` | float64 | own.mid_close + partner.mid_close (should hover near $1 in well-formed markets) |
| `paired_arb_gap_maker` | float64 | 1.00 − paired_yes_bid_sum (positive = both sides could rest bids for free spread capture if filled) |
| `paired_arb_gap_taker` | float64 | paired_yes_ask_sum − 1.00 (positive = paying both asks costs > $1, no taker-arbitrage; negative = sub-$1 paired-ask, true taker arbitrage) |
| `partner_volume_ratio` | float64 | own.volume_in_minute / (own.volume_in_minute + partner.volume_in_minute); null when both sides have null/zero volume; shows which side carries activity |

Paired-leg columns are computed by joining the per-minute output of the partner ticker (loaded as a separate per-ticker block during processing) on `(event_ticker, minute_ts)`. When partner data is missing for a minute (one side has a candle, the other doesn't), partner columns are null for that row.

Per LESSONS B23 (bilateral mechanism — distortions are negative-cost-basis extreme) + LESSONS E18 (bilateral funnel layers): `paired_arb_gap_maker` directly surfaces the maker-side double-cash opportunity Druid's framework anchors on. `paired_mid_sum` deviation from $1 is the market-efficiency signal — wider deviations correlate with thinner books and asymmetric information across the two sides. Downstream consumers can filter cells where `paired_arb_gap_maker > threshold` for bilateral strategies.

### 2.10 Depth limitation (added 2026-05-12 post-T37b Phase 1 v2 visual review)

Per-minute universe captures **top-of-book BBO at minute resolution** (yes_bid_close, yes_ask_close, plus open/high/low intra-minute ranges per Section 2.2). Full 5-deep orderbook with resting sizes at each level is in **A-tier** (`analysis/premarket_ticks/*.csv`, Apr 18 2026+) per LESSONS A22 / A23 / A24 and can be joined as a v2-of-this-spec for the overlap window. **Trade-tape behavioral depth signals** — iceberg detection (large orders refreshing at the same price level), fade-vs-absorb (price moving through vs holding at a level despite trade pressure), depth-trajectory proxies (rate of bid/ask drift relative to traded volume) — are derivable from g9_trades aggressor-side sequences and are v2 candidates. **G9 corpus (pre-Apr-18-2026) does not have explicit depth beyond top-of-book.** Downstream consumers requiring depth must either: (a) filter to the Apr 18+ overlap and join A-tier 5-deep data, or (b) accept top-of-book + trade-tape proxies as the observable depth surface.

---

## 3. Producer architecture

`data/scripts/build_per_minute_universe.py` — single-file producer. Uses `cell_key_helpers.py` for category / entry_band / spread_band / volume_intensity derivation. Streaming row-group reads on g9_candles + filter-pushdown trade-tape reads on g9_trades, per LESSONS C28 streaming discipline.

### 3.1 Per-ticker processing

For each ticker in g9_metadata:

1. Load g9_metadata row for this ticker (open_time, expected_expiration, close_time, settlement_ts, settlement_value, result, custom_strike for player UUID).
2. Load g9_candles rows for this ticker (filter-pushdown by ticker). Sort by end_period_ts.
3. Load g9_trades rows for this ticker (filter-pushdown by ticker). Sort by created_time.
4. Compute match_start_ts from candle-volume signal per LESSONS A35:
   - Find first minute in a run of K≥3 consecutive minutes with volume_fp > 0.
   - If no such run exists, fall back to expected_expiration_time and mark match_start_method = "expected_expiration_fallback".
   - If even the fallback yields a nonsensical value (e.g., match_start > settlement), mark "unknown" and leave match_start_ts null.
5. Forward-fill open_interest across null minutes (open_interest_ffill column).
6. Aggregate trade events into per-minute buckets:
   - For each minute_ts in the candles set, count trades where created_time ∈ [minute_ts − 60, minute_ts).
   - Sum count_fp by taker_side to compute taker_yes_count_in_minute and taker_no_count_in_minute.
   - Compute vwap_in_minute as sum(price × count) / sum(count) within the minute.
7. Compute derived columns: spread_close, mid_close, bid_range_intra_minute, ask_range_intra_minute, taker_flow_in_minute, regime, premarket_phase, cell-key features (entry_band, spread_band, volume_intensity), all timing columns (time_to_match_start_min, etc.).
8. Compute forward-looking labels via vectorized window scan on the per-ticker minute series:
   - For each minute, scan forward to (minute + horizon) and compute max(yes_bid_high) and min(yes_ask_low) within that window.
   - Implementation: precompute cumulative-max and cumulative-min arrays per ticker, then slice for each horizon.
9. Emit one row per minute for this ticker.

### 3.2 Compute envelope

Working set per ticker is small:
- One g9_metadata row: ~3 KB.
- g9_candles for one ticker: ~210-720 rows × 17 columns × 8 bytes = ~30-100 KB.
- g9_trades for one ticker: ~50-1000 rows × 7 columns × 50 bytes = ~17-350 KB.
- Per-minute output for one ticker: ~210-720 rows × ~50 columns × 12 bytes = ~125-430 KB.

Per-ticker working set bounded at ~1 MB. With 20,110 tickers, total output ~6-9 GB compressed parquet (estimate; T37b Phase 1 sizing probe will confirm).

VPS RAM budget (~1.3 GiB effective per Layer B v2 Section 5.1): comfortable headroom. Single-process streaming, no parallelization required at T37 scope. If T37b runtime exceeds budget materially, parallelization across tickers is the natural extension.

### 3.3 Phased rollout

- **Phase 1 (sizing + correctness probe):** single ticker × full lifecycle. Phase 1 ticker: **KXATPMATCH-25JUN18RUNMCD-RUN** (the chart Druid uploaded to anchor the rebuild conversation). Validates schema correctness, forward-label computation correctness, regime classification, formation-phase derivation. Output written to `data/durable/per_minute_universe/probe/per_minute_universe_phase1.parquet`. Phase 1 PASS criterion: visual inspection against the chart (Druid + chat-side joint review). Runtime budget: <2 min.
- **Phase 2 (corpus subset):** 100 tickers stratified across categories + premarket-length deciles. Validates corpus-scale runtime and memory behavior. Computes per-ticker compute cost distribution to project Phase 3 runtime accurately. Runtime budget: <20 min.
- **Phase 3 (full corpus):** all 20,110 tickers. Output to `data/durable/per_minute_universe/per_minute_features.parquet`. Per-ticker incremental writes (mirror Layer B v2's kill-resilience pattern from commit 73826c29). Runtime budget: <8 hours (estimate based on Phase 2 measurement).

Each phase gates the next per LESSONS C28 + D11.

### 3.4 Determinism

Producer is deterministic given fixed inputs. sha256 of inputs (g9_candles, g9_trades, g9_metadata) recorded in run_summary.json. Re-running on the same inputs produces byte-identical output. Cross-reference Layer B v2 spec Section 5.4 — same discipline.

---

## 4. Outputs

Output directory: `data/durable/per_minute_universe/`

### Output 1: Per-minute feature table (primary deliverable)

`data/durable/per_minute_universe/per_minute_features.parquet`

One row per (ticker, minute). ~9.5M rows estimated (1:1 with g9_candles row count). ~50 columns per Section 2.

Schema is partitioned by ticker for filter-pushdown efficiency on downstream queries.

### Output 2: Run summary

`data/durable/per_minute_universe/run_summary.json`

Producer metadata: runtime per phase, ticker count, total minutes, sha256 of inputs, git commit of producer, peak working-set memory, validation-gate check results.

### Output 3: Build log

`data/durable/per_minute_universe/build_log.txt`

Per-ticker runtime, per-ticker minute count, per-ticker null-rate on forward-looking labels (tickers near settlement have null forward-60min etc.), memory snapshots, warnings on match-start-method=unknown tickers.

### Output 4: Validation report

`data/durable/per_minute_universe/validation_report.md`

T37c validation gate output (Section 5). Records each check's PASS/FAIL status, anomaly counts, regression check against Layer B v2's cell_summary_phase3.parquet.

---

## 5. Validation gate (T37c)

Six checks. PASS verdict requires Checks 1-4 PASS (hard gates); Checks 5-6 are informative measurements.

### Hard gates

**Check 1 (gating): row count parity with G9 candles.**

PASS criterion: row count in per_minute_features.parquet equals row count in g9_candles.parquet exactly (1:1 ingest, no aggregation, no padding). g9_candles has 9,500,168 rows per ANALYSIS_LIBRARY T28; per_minute_features must match. If row count differs, the producer is either dropping minutes or fabricating them.

**Check 2 (gating): 100% population on always-populated columns.**

PASS criterion: yes_bid_close, yes_ask_close, spread_close, mid_close, ticker, minute_ts, regime have 0 nulls. Per LESSONS G19, these columns are 100% populated in g9_candles; any null in the per-minute output indicates producer bug.

**Check 3 (gating): regression against Layer B v2 cell_summary_phase3.**

PASS criterion: for each of the 235 cells in Layer B v2's cell_summary_phase3.parquet, group per_minute_features by the same cell-key derivation and verify per-cell n_moments approximately matches cell_summary_phase3's n_moments (within ±5% per cell; Layer B v2 sampled tickers via Layer A's sample_manifest, so per_minute_universe will have MORE moments per cell since it doesn't sample). The check is: per_minute_universe per-cell moments >= cell_summary_phase3 per-cell moments × 0.95 for all 235 cells (it should be substantially MORE, since no sampling). Failure indicates cell-key derivation drift.

**Check 4 (gating): forward-label monotonicity.**

PASS criterion: for every row, max_yes_bid_forward_60min >= max_yes_bid_forward_30min >= max_yes_bid_forward_15min >= max_yes_bid_forward_5min (nested windows must produce monotonic maxes). And symmetrically for min_yes_ask_forward_*. Any violation indicates window-scan bug.

### Informative measurements

**Check 5 (informative): match-start signal coverage.**

Reports the fraction of tickers where match_start_method = "candle_volume" (clean signal) vs "expected_expiration_fallback" vs "unknown". Expected baseline per LESSONS A35: candle-volume signal works on the substantial majority. If <80% are "candle_volume", surface for chat-side review — may need to tune K (the consecutive-non-zero-volume threshold) or add additional fallback logic.

**Check 6 (informative): formation-window default validation.**

For a stratified sample of 50 tickers, plot premarket-phase distinction at formation_window_min = 60, 90, 120, 180. Visual inspection by chat-side + operator to confirm whether 120-min default is correct or needs amendment. Records the chosen formation_window_min in run_summary.json for downstream consumer reference.

---

## 6. Downstream consumers (what becomes a query against this table)

**Layer A v2 (forward-bounce distribution per cell):**

```python
per_minute.groupby(['category', 'entry_band_lo', 'entry_band_hi', 'spread_band', 'volume_intensity', 'regime']).agg(
    bounce_5min_p50=('bounce_5min', lambda x: x.quantile(0.5)),
    bounce_15min_p50=('bounce_15min', lambda x: x.quantile(0.5)),
    # ... etc
)
```



**Layer B v3 (exit policy evaluation per cell):**
Vectorized pandas operation over forward-label columns. For limit_c=30 on cell X:
- Filter to cell X moments.
- For each moment, compute the time of first forward bid ≥ entry_price + 0.30 (using the trade tape for sub-minute resolution where needed).
- Aggregate fill rate, capture distribution.

**Temporal routing analysis:**

```python
per_minute.groupby(['category', 'entry_band_lo', 'entry_band_hi', 'spread_band', 'volume_intensity', 'premarket_phase']).agg(
    bounce_60min_mean=('bounce_60min', 'mean'),
    n_moments=('ticker', 'count'),
)
```

This answers "for the rank-1 deployable cell, is the realized bounce different in formation period vs stable period?" — the core question the temporal probe was trying to answer at the cell-aggregate level. Per-minute universe answers it natively.

**Cohort selection / Kelly sizing:**
Per-cell fill rate × capture distribution × OI / volume context → sizing decision. Same query pattern.

**Paired-cell cross-check:**
Join per_minute on event_ticker to pair the two sides of every match. Then verify yes-side + no-side ≈ $1 at each minute, and analyze paired bounce structure.

---

## 7. Cross-references

- **ROADMAP T37** — to be authored at commit pointer pending. T37 chain: T37a (this spec), T37b (producer build), T37c (validation gate).
- **ROADMAP T36c** — Layer B v2 deployment-readiness assessment. Subsumed by T37 corpus delivery: deployment ranking comes from queries against per_minute_features, not from cell_summary_phase3 alone. T36 outputs remain valid as a cross-check anchor (per_minute_universe regenerates the same cell-keyed measurements under richer grain).
- **LESSONS A22, A24, A26, A35, B14, B15, B16, G18, G19** — anchored throughout the spec.
- **layer_b_v2_spec.md Section 7 (calibration)** — per_minute_universe's Check 3 inherits the same calibration discipline: regression against the immediately-prior canonical layer.
- **layer_b_spec.md (Layer B v1)** — superseded for non-settle premarket cells once T37c PASSes and downstream query patterns established.
- **forensic_replay_v1_spec.md Section 1** — premarket / in_match / settle channel framing. Inherited as the regime classification rule in Section 2.6.
- **ANALYSIS_LIBRARY Cat 11** — empirical anchor for cell-keyed measurements. Cat 12 (post-T37c) will anchor per-minute-grain corpus measurements; Cat 11 remains valid as the cell-keyed projection of the per-minute universe.
- **SIMONS_MODE.md** — the explicit framing this spec answers. The unit of decision is per-minute (a maker bid is posted at a specific minute with the BBO + volume + OI state observed at that minute). The unit of analysis must match. Per_minute_universe is the foundational table that makes Simons-style queries against the corpus possible.

---

## 8. Open items for v2 of this spec

- **Within-minute resolution for high-activity periods.** g9_trades has microsecond timestamps. For minutes with N > 10 trades, the trade tape carries sub-minute price signal that the minute-aggregate columns smooth over. T37 v2 could emit a parallel `per_trade_features` table joinable to per_minute_features by (ticker, trade_id) for high-resolution downstream analysis. Deferred — wait for the per_minute_features queries to surface concrete need.
- **In-match game-state features.** ESPN scrape (per session-history G9 work) covers Mar 4-8 2026 with point-by-point game state for 504 games. Joining game-state to per_minute_features for in_match regime minutes would expose mispricing-vs-true-probability dynamics. Out of T37 scope; v2 candidate.
- **B-tier + A-tier microstructure for Apr 18+ overlap.** The `analysis/premarket_ticks/*.csv` 27-column 5-deep orderbook source covers Apr 18+. Joinable to per_minute_features for the overlap window to add depth-imbalance, queue-trajectory features. Out of T37 scope; v2 candidate.
- **Cross-cell paired-leg join.** event_ticker pairs the two sides of every match. v2 could pre-emit paired-leg columns (yes_side_yes_bid_close, no_side_yes_bid_close, paired_sum_close, paired_arbitrage_gap) for direct paired analysis without join cost. Deferred.

---

## 9. CHANGELOG

- **2026-05-12 ET (initial spec, T37a):** Sections 1-8 + footer. Drafted Session 11, post-temporal-probe-completion. Anchored on operator's challenge to surface every variable per N (player-in-game) at every minute of the premarket window — the unit-of-analysis must match the unit-of-decision (LESSONS B15). Supersedes the cell-keyed binning architecture as the canonical observation grain; cell aggregation becomes a downstream query, not the producer output.
- **2026-05-12 ET (T37a amendment, post-Phase-1 visual review):** Three coordinated edits driven by Phase 1 RUN-ticker visual inspection. (1) Section 2.5 match-start signal source switched from candle-volume (LESSONS G19: null throughout for historical-tier) to **trade-density** (consecutive minutes with `trade_count_in_minute > 0` from g9_trades aggregation). Method values changed to `trade_density / expected_expiration_fallback / unknown`. Expected outcome on RUN: match_start_ts lands at the visual regime change in_match boundary rather than the 19:00 UTC expected_expiration approximation. (2) Section 2.4 OI/volume tier-note added: historical-tier markets have OI null throughout (per G19); producer emits null where source is null; trade-derived volume columns recompute activity from g9_trades so historical-tier rows are still observable. (3) New Section 2.9 paired-leg observables: every match has two tickers sharing event_ticker, and the partner's BBO/volume/OI/taker-flow observables are emitted alongside own-side data for each row. Adds `partner_ticker`, `partner_yes_bid_close`, `partner_yes_ask_close`, `partner_spread_close`, `partner_volume_in_minute`, `partner_trade_count_in_minute`, `partner_taker_flow_in_minute`, `partner_open_interest_ffill`, `paired_yes_bid_sum`, `paired_yes_ask_sum`, `paired_mid_sum`, `paired_arb_gap_maker`, `paired_arb_gap_taker`, `partner_volume_ratio` — 14 new columns. Anchored on LESSONS B23 + E18 bilateral mechanism framings. Producer working memory roughly doubles to ~2 MB per pair; well within VPS budget.
- **2026-05-12 ET (T37a amendment v3, post-Phase-1-v2 visual review):** Two coordinated edits driven by Phase 1 v2 chart inspection. (1) Section 2.5 match-start signal upgraded from v2 single-ticker trade-density (`trade_count_in_minute > 0`, fired at 13:06 ET on RUN — too early, sporadic premarket trades not the regime change) to **v3 both-sides-simultaneous trade-density** (first K≥3 consecutive minutes where BOTH own.trade_count_in_minute ≥ M AND partner.trade_count_in_minute ≥ M, default M=5). Method values changed to `both_sides_trade_density / expected_expiration_fallback / unknown`. Leverages paired-leg structure now available via Section 2.9. Rationale: real match-start events trigger simultaneous trader reaction on both sides; sporadic premarket activity is one-sided. (2) New Section 2.10 depth-limitation paragraph documenting that G9 captures top-of-book at minute resolution; A-tier 5-deep orderbook covers Apr 18+ as a v2-spec join target; trade-tape behavioral-depth signals (iceberg, fade-vs-absorb, depth-trajectory) are v2 candidates.
- **2026-05-12 ET (T37a amendment v4, post-Phase-1-v3 trade-count probe):** Section 2.5 match-start signal upgraded from v3 single-tier `both_sides_trade_density` (M=5 too strict; returned None on RUN; fell back to expected_expiration) to **v4 four-level signal hierarchy**. Tier 1 `both_sides_price_discovery` adds an intra-minute price-range gate (own AND partner both show bid OR ask range > R=0.02 within the minute) on top of K=3 / M_TRADES=3 trade-density; this distinguishes match-driven price discovery from premarket positioning at stable prices. Tier 2 fallback `both_sides_trade_density` is K=3 / M_TRADES=3 without the price-range gate (Option A from the probe; lands at 14:41 ET on RUN). Tier 3 `expected_expiration_fallback`; Tier 4 `unknown`. Probe data anchoring the tuning: at the 14:39-14:41 ET trade-density window on RUN, intra-minute bid/ask ranges were small (premarket-style positioning at stable prices); at the 15:33-15:55 ET window, ranges expanded materially as bid/ask started moving on event-driven information. Producer constants: `MATCH_START_K_DEFAULT=3`, `MATCH_START_M_TRADES_DEFAULT=3`, `MATCH_START_R_DEFAULT=0.02`.

---

*Spec authored 2026-05-12 ET. T37a → spec lands at commit (TBD) → Coordination Point 1 STOP. T37b Phase 1 (RUN ticker validation) → Coordination Point 2 STOP. T37b Phase 2 (100-ticker sizing) → Coordination Point 3 STOP. T37b Phase 3 (full corpus) → T37c validation gate.*
