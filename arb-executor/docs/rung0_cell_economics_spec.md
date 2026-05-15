# Rung 0 Spec — Canonical Exit-Optimized Cell Economics

**Status:** v1.1 — operator amendment 2026-05-14 (pre-T-20m metadata preserved, dual peak vs first-extreme-touch). Producer build unblocked at v1.1.

**Anchored to:**
- per_minute_universe_spec.md (T37 foundation, checkpoint 3 sha256 9fde4b5d…)
- g9_trades.parquet (microsecond trade tape, 33.7M rows)
- LESSONS E32 (locked cell/exit model), G21 (ET on operator surfaces), C36 (trade-tape canonical), B25 (tick-level fill semantics)
- recomputation_ladder.json Rung 0
- TAXONOMY Section 2.5 (GRAIN / VECTOR / OBJECTIVE)

**Output:** `data/durable/rung0_cell_economics/cell_economics.parquet`
**ROADMAP:** T39 chain.

---

## 1. Scope

Rung 0 produces the canonical exit-optimized per-N peak-bounce table on the FOUNDATION-TIER corpus. It absorbs six legacy entries (`baseline_econ`, `rebuilt_scorecard`, `pnl_by_cell_config`, `per_cell_real_economics`, `comparison_real_vs_analysis`, `post_retune_economics` base metrics) and closes LESSONS E27. All downstream rungs depend on this table; nothing else gets built first.

### 1.1 The operational definition
For every N in the binary-outcome subset of the corpus:
- Entry = real trade on the trade tape at or near T-20m (operator sharpening: not theoretical mid).
- Peak = highest bid that was live from entry through settlement (operator sharpening: bid, not just trade — "what could I have exited at as a maker").
- One number per N: `peak_bounce` (peak minus entry, in dollars).
- Group N's by cell band. Rank cells by **average peak per band**. Done.

That's the whole metric. No exit grid sweep, no per-threshold matrix — just the peak per N, the average per band.

### 1.2 In scope
- Cell key = (category, T-20m price band). Per-(cell, N) grain (one row per N).
- Real trade-tape entry at T-20m with ±2min tolerance.
- 5¢ bands, 5-95¢ only (extremes excluded by design per E32).
- Peak-bid headline metric + peak-trade as a free secondary column.
- Volume / OI / top-of-book context columns (operator sharpening: required, not optional).
- Phase attribution at entry (PHASE_2/PHASE_3 expected, recorded per N).
- Paired-event link preserved via `paired_event_partner_ticker` for Rung 2.
- Four categories (WTA Main / WTA Challenger / ATP Main / ATP Challenger). Every output stratified across all four.

### 1.3 Out of scope
- Exit threshold / target selection per band — Rung 1.
- Cell-band categorization (grouping bands into 3-4 behavior families) — Rung 1.
- Fees — Cat 2 fee table layered at consumption time.
- Maker fill probability / queue / execution mechanics — Rung 3.
- Paired-leg analysis (bilateral capture rate, etc.) — Rung 2.
- Anchor recomputation (70.7%, 977-fill P&L) — Rung 2.
- Deep orderbook depth (walls at +1¢/+2¢/+5¢) — F33 gap; T38 forward-only.

---

## 2. The cell key

### 2.1 Definition
A cell is `(category, price_band_at_T-20m)`. Per E32: the cell is the N's Kalshi price at a fixed T-20m mark, one axis (price), partitioned by the four categories. Direction is NOT an axis — N and its inverse are two faces of one event, joined via `event_ticker`.

**Note on T-20m as a tractability choice (v1.0+):** T-20m is the v1.1 cell anchor because the stable-window diagnostic established it as the late-premarket convergence point (per_minute_universe_spec.md Section 7; data/analysis/stable_window_diagnostic_v2.json). The choice is for analytical tractability and to keep the strategic interpretation crisp — anchor at one moment, measure forward. A lot of market behavior in the preceding hours (formation, FV-anchor convergence, volume buildup, BBO dynamics) is not analyzed here and is queued as future research. Earlier anchors (T-1h, T-2h, formation-gate-relative) and entry-condition-driven anchors (FV-divergence threshold crossings, volume-threshold crossings) are deferred to Rung 1+ as variants once the T-20m baseline is established. The v1.1 columns `n_minutes_premarket`, `first_trade_ts`, and `n_trades_pre_t20m` preserve pre-T-20m metadata on every row so future variants can stratify without re-running the producer.

### 2.2 Categories
Four, partitioning every output: `WTA_MAIN`, `WTA_CHALL`, `ATP_MAIN`, `ATP_CHALL`. The fifth `OTHER` bucket from `cell_key_helpers.CATEGORIES` is empirically empty in the tennis corpus — exclude. Fail loud if any ticker categorizes as `OTHER`.

### 2.3 Price bands — 5¢, range 5-95¢ only
- **18 bands per category** (0.05-0.10, 0.10-0.15, …, 0.90-0.95). 4 × 18 = **72 cells total**.
- **0.00-0.05 and 0.95-1.00 are EXCLUDED BY DESIGN.** Per E32: ~5¢ band fails on traction (insufficient movement to bounce a tradeable amount); ~95¢ band fails on geometry (insufficient upside — risking 95¢ to gain at most 4¢). The operation doesn't put weight on these bands. Don't carry them.
- If a ticker's T-20m anchor falls in 0.00-0.05 or 0.95-1.00, the ticker is dropped from the Rung 0 output (recorded in the dropout log, not the cell-economics output).
- Each cell row carries `band_n_count` (load-bearing) so downstream consumers respect per-band sample-size without silent re-aggregation.

### 2.4 The T-20m anchor — real trade on the trade tape
Per operator sharpening: the entry is a *real trade that actually executed*, not a theoretical BBO mid.

Resolution procedure per ticker:
1. Compute `target_ts = match_start_ts - timedelta(minutes=20)` (ET; converted from g9 UTC at read per G21).
2. Walk `g9_trades` for that ticker. Find the trade whose `created_time` is nearest to `target_ts`.
3. If a trade exists within ±2 minutes of `target_ts`:
   - `t20m_trade_ts` = that trade's timestamp (ET)
   - `t20m_trade_price` = that trade's `yes_price_dollars`
   - `t20m_anchor_method` = `"exact"` if within ±5 seconds, else `"nearest_within_2min"`
4. If no trade within ±2 minutes: ticker dropped from Rung 0 output (recorded in dropout log).
5. **Note:** the v0.1 spec used `mid_close` from the per-minute foundation as a fallback when no exact trade existed. v1.0 rejects that — the entry MUST be a real trade-tape event, not a synthesized BBO mid. Tickers with no nearby trade get dropped.

Expected coverage: the Decision-3 probe (commit 2547f6a6 audit + /tmp/decision3_t20m_anchor_probe.json) measured 89.48% under the per-minute-foundation fallback rule. The trade-tape rule is stricter — coverage will be lower, possibly materially. Phase 1 of the producer measures actual trade-tape coverage and surfaces it in the run summary.

---

## 3. The peak — operational definition

### 3.1 Headline: peak-bid
Per operator sharpening + B25 mechanism: walk the trade tape from `t20m_trade_ts` forward. The walk has a natural terminator: the first trade where the yes-side price hits an extreme (`yes_price_dollars ≥ 0.99` OR `≤ 0.01`) marks the moment the outcome is structurally decided — the position is over. Two peaks are recorded:

- `peak_bid_price_full` = max(`yes_price_dollars` where `taker_side='no'`) from `t20m_trade_ts` through `settlement_ts`. The full-window peak; for winning N's this saturates near 0.99.
- `peak_bid_price_pre_resolution` = max(`yes_price_dollars` where `taker_side='no'`) from `t20m_trade_ts` through (`first_extreme_touch_ts - epsilon`), i.e., before the outcome is structurally revealed. For winning N's this is the peak that could have been exited at as a maker BEFORE the answer was known — the volatility-en-route, not the saturation. For N's that never touch an extreme before settlement (rare; markets that resolve at exactly 0.5 or via some other mechanism), `peak_bid_price_pre_resolution` equals `peak_bid_price_full`.

For Rung 1 ranking purposes the headline metric is `peak_bid_bounce_pre_resolution` — that's the answer to "highest exit you could have hit before the answer was known." `peak_bid_bounce_full` is preserved for comparison and diagnostics.

Derived columns emitted (per N):
- `peak_bid_price_full`, `peak_bid_bounce_full` = `peak_bid_price_full - t20m_trade_price`.
- `peak_bid_price_pre_resolution`, `peak_bid_bounce_pre_resolution` = `peak_bid_price_pre_resolution - t20m_trade_price`. **Headline metric.**
- `first_extreme_touch_ts` — timestamp of the first trade with `yes_price_dollars ≥ 0.99` OR `≤ 0.01`, or null if no extreme touch occurred before `settlement_ts`.

### 3.2 Secondary: peak-trade
Parallel dual treatment to peak-bid — emit both full-window and pre-resolution variants:

- `peak_trade_price_full` = max `yes_price_dollars` across ALL trades from `t20m_trade_ts` through `settlement_ts` (any `taker_side`).
- `peak_trade_bounce_full` = `peak_trade_price_full - t20m_trade_price`.
- `peak_trade_price_pre_resolution` = max `yes_price_dollars` across ALL trades from `t20m_trade_ts` through (`first_extreme_touch_ts - epsilon`).
- `peak_trade_bounce_pre_resolution` = `peak_trade_price_pre_resolution - t20m_trade_price`.

Free to compute; carried alongside. Useful for diagnostic comparison: where peak-trade ≫ peak-bid, a yes-taker reached high but no maker bid stayed there long enough to be hit.

### 3.3 Peak context (when did it happen)
The headline timestamp is `peak_bid_ts_pre_resolution` — when peak-bid was live BEFORE the outcome was structurally revealed (matching the headline metric `peak_bid_bounce_pre_resolution`). `peak_bid_ts_full` carries the full-window peak's timestamp for diagnostic comparison.

- `peak_bid_ts_pre_resolution` — timestamp of the bid-revealing trade that produced `peak_bid_price_pre_resolution` (ET). **Headline.**
- `peak_bid_ts_full` — timestamp of the bid-revealing trade that produced `peak_bid_price_full` (ET). Diagnostic.
- `peak_bid_in_premarket` — bool. True if `peak_bid_ts_pre_resolution < match_start_ts`; false if peak was in-match.
- `peak_bid_minutes_after_entry` — `(peak_bid_ts_pre_resolution - t20m_trade_ts).total_seconds() / 60`.

### 3.4 Why this is enough
Under the locked model (no stop, ride to target or settlement), every threshold below `peak_bid_price` is "would have hit." Every threshold above is "would not have hit." The peak IS the answer to the threshold-sweep question — no need to enumerate the grid. Rung 1 derives per-band optimized targets directly from the distribution of peaks within each band.

### 3.5 Settlement context
- `settlement_outcome` — `"yes_win"` / `"no_win"` (scalar markets excluded at producer entry).
- `realized_at_settlement` — `settlement_value_dollars - t20m_trade_price`. The no-action baseline (what you'd have gotten holding through resolution).
- `bounce_to_settlement` — same as `peak_trade_bounce` if peak happened in-match and we're holding through; recorded separately because settlement is the answer key per E32.

LESSONS F8 (bot-side missing settlement events) doesn't bite at Rung 0 — we read settlement from `g9_metadata`, ground truth from Kalshi's resolution, not from bot logs.

---

## 4. Context columns (operator sharpening: required)

For each N, attach activity-level context at the cell band level for downstream stratification:

### 4.1 Volume
- `total_premarket_volume` — sum of `count_fp` in g9_trades for this ticker from `open_time` to `match_start_ts`.
- `total_premarket_trade_count` — count of trade rows (filtered for `count_fp > 0` per C36 zero-size discipline) over the same window.

### 4.2 Open Interest
- `oi_at_t20m` — `open_interest_fp` from g9_candles at or near `target_ts` (per-minute resolution from the foundation corpus; null if g9_candles row is null at that minute — historical-tier markets per F31 will be 0/null throughout).

### 4.3 Top-of-book context
- `bbo_bid_size_at_t20m`, `bbo_ask_size_at_t20m` — top-of-book sizes from g9_candles at the T-20m minute. Best-effort top-of-book; deeper orderbook is not available (F33).

(Deep orderbook depth is NOT in this schema — F33 gap, T38 forward-only. Surface this absence honestly; do not synthesize.)

### 4.4 Premarket-context columns (preserved for future research, not analyzed in Rung 0)
Emitted on every row to preserve pre-T-20m metadata so future variants (earlier anchors, formation-relative stratification, FV-convergence research per Section 2.1) can stratify without re-running the producer. Not analyzed in Rung 0's headline outputs.

- `n_minutes_premarket` — int. Total premarket lifetime in minutes = `(match_start_ts - open_time) / 60`. Stratifier for future "long premarket vs short premarket" analysis.
- `first_trade_ts` — ts ET (nullable). Timestamp of the N's first trade ever (the formation gate per Cat 8 / LESSONS F34). Null if no trades pre-T-20m.
- `n_trades_pre_t20m` — int. Count of trades (`count_fp > 0` per C36) from `open_time` to `t20m_trade_ts`.

---

## 5. Output schema (final)

One row per N that resolved a valid trade-tape T-20m anchor AND fell in a band within 0.05-0.95.

| # | Column | Type | Description |
|---|---|---|---|
| 1 | `ticker` | string | The N's Kalshi ticker |
| 2 | `event_ticker` | string | The paired event (join key for Rung 2) |
| 3 | `paired_event_partner_ticker` | string | The opponent N's ticker |
| 4 | `category` | string | WTA_MAIN / WTA_CHALL / ATP_MAIN / ATP_CHALL |
| 5 | `match_start_ts` | ts ET | Match start (converted from g9 UTC at read) |
| 6 | `settlement_ts` | ts ET | Settlement |
| 7 | `settlement_value_dollars` | float | 0.0 or 1.0 (scalars excluded) |
| 8 | `t20m_trade_ts` | ts ET | Timestamp of the actual T-20m anchor trade |
| 9 | `t20m_trade_price` | float | The N's price at the T-20m anchor trade |
| 10 | `t20m_anchor_method` | string | `"exact"` / `"nearest_within_2min"` |
| 11 | `price_band` | string | e.g. `"0.30-0.35"` |
| 12 | `cell_key` | string | `"{category}__{price_band}"` |
| 13 | `band_n_count` | int | Total N's in this row's cell (load-bearing, populated after first-pass aggregation) |
| 14 | `phase_state_at_t20m` | string | From v0.2 classifier (PHASE_2 / PHASE_3 expected) |
| 15 | `peak_bid_price_full` | float | **v1.1** — Full-window peak bid (t20m → settlement). Diagnostic. |
| 16 | `peak_bid_price_pre_resolution` | float | **v1.1, HEADLINE** — Peak bid before first 99¢/1¢ extreme touch |
| 17 | `peak_bid_bounce_full` | float | **v1.1** — peak_bid_price_full − t20m_trade_price |
| 18 | `peak_bid_bounce_pre_resolution` | float | **v1.1, HEADLINE** — peak_bid_price_pre_resolution − t20m_trade_price |
| 19 | `peak_bid_ts_pre_resolution` | ts ET | **v1.1, HEADLINE** — Timestamp of pre-resolution peak bid |
| 20 | `peak_bid_ts_full` | ts ET | **v1.1** — Timestamp of full-window peak bid |
| 21 | `peak_bid_in_premarket` | bool | True if `peak_bid_ts_pre_resolution < match_start_ts` |
| 22 | `peak_bid_minutes_after_entry` | float | Minutes from entry to peak_bid_ts_pre_resolution |
| 23 | `peak_trade_price_full` | float | **v1.1** — Secondary: full-window max trade price |
| 24 | `peak_trade_price_pre_resolution` | float | **v1.1** — Secondary: pre-resolution max trade price |
| 25 | `peak_trade_bounce_full` | float | **v1.1** — peak_trade_price_full − t20m_trade_price |
| 26 | `peak_trade_bounce_pre_resolution` | float | **v1.1** — peak_trade_price_pre_resolution − t20m_trade_price |
| 27 | `first_extreme_touch_ts` | ts ET or null | **v1.1** — Timestamp of first trade with `yes_price_dollars ≥ 0.99` OR `≤ 0.01`; null if none |
| 28 | `realized_at_settlement` | float | settlement_value − t20m_trade_price (no-action baseline) |
| 29 | `total_premarket_volume` | int | Volume from open_time to match_start |
| 30 | `total_premarket_trade_count` | int | Trade count (count_fp > 0 only) from open_time to match_start |
| 31 | `oi_at_t20m` | int or null | Open interest at T-20m minute (null for historical-tier-zero per F31) |
| 32 | `bbo_bid_size_at_t20m` | int or null | Top-of-book bid size at T-20m minute |
| 33 | `bbo_ask_size_at_t20m` | int or null | Top-of-book ask size at T-20m minute |
| 34 | `n_minutes_premarket` | int | **v1.1** — Total premarket lifetime: `(match_start_ts − open_time) / 60` |
| 35 | `first_trade_ts` | ts ET or null | **v1.1** — Timestamp of N's first trade ever (formation gate; null if no pre-T-20m trades) |
| 36 | `n_trades_pre_t20m` | int | **v1.1** — Count of trades (count_fp > 0) from open_time to t20m_trade_ts |

**36 columns total** (v1.1). One row per qualifying N. Estimated row count: lower than the 89.48% per-minute-foundation coverage from the Decision 3 probe, because the trade-tape entry rule is stricter. Phase 1 measures actual.

---

## 6. Validation gates

### Hard gates
1. **Anchor consistency.** Every row's `t20m_trade_ts` is within ±2 minutes of (`match_start_ts - 20min`). Zero violations.
2. **Band exclusion.** Zero rows with `price_band` in 0.00-0.05 or 0.95-1.00.
3. **Peak monotonicity.** Both `peak_bid_price_full ≥ t20m_trade_price` and `peak_bid_price_pre_resolution ≥ t20m_trade_price` for every row. Same for peak_trade equivalents. Additionally `peak_bid_price_full ≥ peak_bid_price_pre_resolution` by construction (full window is a superset). Same for peak_trade.
4. **Settlement consistency.** `realized_at_settlement = settlement_value_dollars - t20m_trade_price` exactly per row. Zero drift.
5. **TZ correctness.** Every emitted timestamp is timezone-aware ET. Zero naive timestamps, zero UTC leakage to operator-facing columns (per G21).

### Informative measurements
- Coverage: how many of the 19,207 binary-outcome tickers produced a row vs were dropped (no nearby trade, in extreme band, no match_start_ts).
- Per-cell N count distribution (drives Rung 1's per-band CI work).
- Distribution of `phase_state_at_t20m` per category (sanity check: T-20m should be predominantly PHASE_2/PHASE_3 converged-zone, not PHASE_1 formation-chaos).
- Mean and median `peak_bid_bounce` per cell — first preview of Rung 1's headline ranking.

---

## 7. Producer architecture

Per-ticker streaming, kill-resilient incremental writes (mirrors T37 producer pattern at commit 73826c29).

- **Input:** `per_minute_features.parquet` (for OI + BBO context), `g9_trades.parquet` (for trade-tape entry + peak walk), `g9_metadata.parquet` (for settlement). All read-only.
- **Phase 1:** single ticker — KXATPMATCH-25JUN18RUNMCD-RUN — visual inspection against the Rune chart that anchored E32. <2 min budget.
- **Phase 2:** ~160 paired tickers stratified by category × premarket-length quartile. <30 min budget.
- **Phase 3:** full binary-outcome subset (~19,207 tickers minus dropouts). Estimated runtime: per-ticker work is trade-tape walk from T-20m through settlement = ~10-50ms per ticker depending on trade count. Total: ~5-15 min wall-clock single-threaded. Fast because the per-minute foundation already did the expensive minute-grain work; Rung 0 just walks the trade tape (cheap) and reads context columns from the foundation (one row per ticker, near-instant).
- **Output:** `data/durable/rung0_cell_economics/cell_economics.parquet`.
- **Validation report:** `data/durable/rung0_cell_economics/validation_report.md`.

C36 disciplines apply:
- `count_fp > 0` filter on g9_trades for trade-count aggregates.
- Trade tape is canonical for trade activity; candle aggregates not used for that.
- Pre-replace validation gate (C37): compute `.new`, run all hard gates, `os.replace` only on all-pass.

---

## 8. Cross-references
- Foundation: per_minute_universe_spec.md (T37); per_minute_features.parquet checkpoint 3 sha256 `9fde4b5d…`.
- Trade tape: g9_trades.parquet schema in TAXONOMY Section 1 G-tier.
- Cell model: LESSONS E32.
- TZ discipline: LESSONS G21; F16; C23.
- Trade-tape canonicality: LESSONS C36.
- Tick-level fill mechanism: LESSONS B25; Cat 11 forensic replay.
- F33 depth-chain gap: documented; T38 forward-only.
- F8 settlement detection: bot-side gap, does not bite at Rung 0 (we read settlement from g9_metadata ground truth).
- Classification axes: TAXONOMY Section 2.5.
- Ladder context: recomputation_ladder.json Rung 0; ROADMAP T39.

---

## 9. Resolution log (v1.0 lock — 2026-05-14)

The v0.1 spec carried 5 DECISION POINTs. Operator sharpenings on 2026-05-14 collapsed and resolved them as follows:

| v0.1 # | v0.1 Question | v1.0 Resolution | Source |
|---|---|---|---|
| 1 | Aggregation grain | per-(cell, N) | T37 validity gate doctrine |
| 2 | Band width | 5¢, EXCLUDING 5/95¢ extremes (18 bands × 4 cat = 72 cells) | Operator sharpening + E32 |
| 3 | T-20m fallback | Nearest real trade ±2min ONLY (no BBO-mid fallback) | Operator sharpening (real trade, not theoretical mid) |
| 4 | Entry mode | Real trade on trade tape (Option D, not v0.1's mid-close) | Operator sharpening |
| 5 | Exit grid | RETIRED — replaced by single peak-bid metric | Operator sharpening (no threshold sweep; the peak IS the answer) |

Additional v1.0 additions not in v0.1:
- Volume / OI / top-of-book context columns as required (operator sharpening).
- Peak-bid as headline + peak-trade as secondary (clarification on "highest spike" — bid-side is what a maker could have exited at).
- TZ discipline: all emitted timestamps ET per G21; UTC stays at raw-bytes layer only.
- Tick-level inline confirmation: g9_trades preserves every trade microsecond-precise; taker_side reveals one side of the book per tick; both sides reconstructible at tick resolution by walking the tape (B25 mechanism).
- F33 depth-chain gap acknowledged honestly: not in Rung 0, T38 forward-only.

### v1.1 amendment (2026-05-14)
- Section 2.1: T-20m-as-tractability paragraph added; pre-T-20m research direction queued.
- Section 3: peak-walk termination clarified to first-extreme-touch; dual peak (full vs pre-resolution) emitted on every row.
- Section 4.4: three premarket-context columns added (n_minutes_premarket, first_trade_ts, n_trades_pre_t20m).
- Section 5: schema grew from 27 to 36 columns (5 old peak columns → 10 new dual-peak columns + first_extreme_touch_ts + 3 premarket-context columns).
- Section 6: peak monotonicity gate updated for dual peak (full and pre-resolution both must clear t20m_trade_price; full ≥ pre-resolution by construction).

The producer build is gated on v1.1, not v1.0 — operator amendment caught before producer arc launched.
