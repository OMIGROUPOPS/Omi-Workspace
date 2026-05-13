# T38a — Real-Time Book Capture Daemon Spec

**File:** `arb-executor/docs/t38_books_daemon_spec.md`
**Status:** Draft v0.3 (formula-locked + Marriott 2026 empirical validation; awaiting producer build authorization after T37 Phase 3 lands)

## 1. Status and foundation

**Status:**
- T38: OPEN, pre-implementation.
- This spec defines T38a v1: the initial real-time book capture daemon producing forward-only orderbook corpora.
- Implementation is authorized after:
  - T37 Phase 3 corpus lands clean and validated.
  - This spec is reviewed by operator and aligned with ROADMAP.

**Foundation pointers:**
- Operating philosophy: `SIMONS_MODE.md` — Kalshi as peer-to-peer venue, Problem 1 vs Problem 2 separation, "unit of analysis = unit of decision," Renaissance-style single canonical schema across historical and live corpora.
- Measurement discipline and data-integrity: `LESSONS.md`
  - A20–A24 (data tiers & variable inventory).
  - A22/A24/A31 (volume and depth as primary axes).
  - F1, F8, F17, F22, F30 (durability, corruption modes, canonical sources, bias reconciliation).
- Analysis inventory and canonical artifacts: `ANALYSIS_LIBRARY.md` — Cat 11 forensic replay (Layer B v1 undercount) and depth/tier catalog.
- Current universe & simulator:
  - `per_minute_universe_spec.md` (T37a) — per-minute features corpus ("G9-style" canonical observation grain).
  - `layer_b_v2_spec.md` (T36a) — tick-level simulator correcting Layer B v1 structural undercount via forensic replay v1.
  - `forensic_replay_v1_spec.md` — tick-grain fill semantics and replay architecture.
  - T38-MIN columns must match the T37 `per_minute_features.parquet` schema on `(ticker, minute_ts)` keys — schema relationship is additive (`T38-MIN = T37 columns + 40 raw depth-level columns + ~10 derived depth-aggregate metrics + 3 quality/provenance flags`), not divergent. Any future T37 schema change must be reflected in T38-MIN to maintain join compatibility.

T38a is explicitly **downstream** of T37: it does not redefine the per-minute universe, it extends it forward in time and enriches it with live orderbook depth, using the same keys and minute boundaries.

## 2. Scope

**In scope (T38a v1):**
- A daemonized process (or small family of processes) that:
  - Maintains live local orderbooks for a configured universe of Kalshi tennis tickers via WebSocket orderbook updates.
  - Periodically seeds and resyncs local books via REST orderbook snapshots.
  - Writes two new durable corpora under `arb-executor/data/durable/`:
    - `t38_books_minute/` (T38-MIN): per-minute book snapshots aligned 1:1 with T37 per-minute features.
    - `t38_books_tick/` (T38-TICK): raw snapshot + delta event stream for full-depth reconstruction.
- Implements a reusable reconstruction primitive `get_book_at(ticker, ts)` built on T38-TICK.
- Provides enough schema alignment that future T-items can:
  - Join T38-MIN onto T37 by `(ticker, minute_ts)`.
  - Join T38-TICK onto G9 trades and Layer B v2 replay fills by `(ticker, event_ts)` windows.

**Out of scope (T38a v1):**
- Any trading or execution logic. T38a is *observation-only*; it does not place, cancel, or modify orders.
- Any bilateral analytics or Layer C/later-line modeling. Bilateral analysis is explicitly behind G12 and v3; T38a only supplies data.
- Any attempt to backfill deep historical depth via Kalshi: T38a starts at deployment time; historical depth remains limited to what G9/T37 can reconstruct or infer.

## 3. Schema

T38 produces two main tables. Both are columnar (Parquet) and partitioned for durability and throughput.

### 3.1 T38-MIN — per-minute snapshots

**Path:** `arb-executor/data/durable/t38_books_minute/`
**Grain:** one row per `(ticker, minute_ts)` matching T37 per-minute universe grain.
**Partitioning:** `date=YYYY-MM-DD/ticker=KX.../`

**Keys**
- `ticker` — Kalshi market ticker, string.
- `minute_ts` — Unix epoch (seconds) rounded to minute-close boundary, UTC. This must match the T37 minute anchor.

**Best-of-book (aligned with T37)**
- `yes_bid_1`, `yes_ask_1` — best YES bid and ask prices (float, 0–1).
- `no_bid_1`, `no_ask_1` — best NO bid and ask (float, 0–1), if present or derived via binary symmetry.
- `mid` — canonical midprice, consistent with T37 definition.
- `spread` — canonical spread, consistent with T37.

**Per-minute trade stats (mirror + extend T37)**
- `minute_trades_count` — number of trades in this minute (if trade stream available).
- `minute_volume_fp` — total executed ct's in this minute (fp units consistent with Kalshi fills).
- `minute_taker_yes_volume_fp` — volume where `taker_side = yes`.
- `minute_taker_no_volume_fp` — volume where `taker_side = no`.
- `minute_trade_imbalance` — `(yes - no) / (yes + no)` for the minute (float, -1..1).

**Depth columns (top-10 levels per side)**

Per side: YES and NO. For each level `i ∈ {1..10}`:
- `yes_price_i` — YES price at level i.
- `yes_qty_fp_i` — YES quantity at level i (fp ct units).
- `no_price_i` — NO price at level i.
- `no_qty_fp_i` — NO quantity at level i (fp ct units).

If fewer than 10 levels are available, unused levels are `NULL` and excluded from aggregates.

**Derived aggregate depth metrics**

All derived metrics below are computed from the raw top-10 ladder columns in the same T38-MIN row: `yes_price_i`, `yes_qty_fp_i`, `no_price_i`, `no_qty_fp_i` for `i ∈ {1..10}`.

**Null-handling convention.** For all depth aggregates: a level is present iff both price_i and qty_fp_i are non-null and qty_fp_i > 0. Missing levels are excluded, not zero-filled. If an aggregate requires at least one present level on a side and that side has none, the aggregate is NULL. If an aggregate requires both sides and one side is absent, the aggregate is NULL. If a denominator is zero after exclusions, the aggregate is NULL. This rule prevents fake balance from zero-filling non-existent levels and preserves the difference between "thin book" and "balanced book."

1. **total_yes_depth_top10** — sum of `yes_qty_fp_i` across present YES levels in ranks 1-10. Units: ct. Range: [0, +∞), NULL if no YES levels present. Single-pass row aggregate. Captures total visible YES-side resting liquidity.

2. **total_no_depth_top10** — sum of `no_qty_fp_i` across present NO levels in ranks 1-10. Units: ct. Range: [0, +∞), NULL if no NO levels present. Single-pass row aggregate. Captures total visible NO-side resting liquidity.

3. **depth_imbalance_top5** — let YES5 = sum of yes_qty_fp_i for i in {1..5} present; NO5 = sum of no_qty_fp_i for i in {1..5} present. Then `depth_imbalance_top5 = YES5 / (YES5 + NO5)`. Unitless, range [0, 1] where 0.5 = balanced visible depth, >0.5 = YES-heavy, <0.5 = NO-heavy. NULL if YES5+NO5 = 0. Single-pass row aggregate. Standard microstructure top-of-book pressure measure tied to near-term quote pressure and microprice tilt.

4. **depth_imbalance_top10** — same construction as top5 but over all present levels in ranks 1-10. `depth_imbalance_top10 = YES10 / (YES10 + NO10)`. Comparing top5 vs top10 reveals whether one-sided pressure is purely at the touch or persists deeper into visible liquidity.

5. **depth_weighted_mid** — top-of-book microprice in YES-price space. Requires top-of-book presence both sides (yes_bid_1, yes_ask_1, yes_qty_fp_1, no_qty_fp_1). Let Q_yes = yes_qty_fp_1, Q_no = no_qty_fp_1. Then `depth_weighted_mid = (Q_yes * yes_ask_1 + Q_no * yes_bid_1) / (Q_yes + Q_no)`. Units: YES-price in dollars. Range [yes_bid_1, yes_ask_1]. NULL if either side's top level is missing or Q_yes+Q_no = 0. Single-pass. Captures where the top-of-book is likely to clear next given visible queue imbalance: more YES-side bid depth pulls toward the ask, more NO-side depth pulls toward the bid. Top-of-book microprice chosen over multi-level weighted midpoint because it cleanly separates directional pressure (this metric) from book shape (depth_slope_*) and distance from touch (book_compactness_index).

6. **depth_slope_yes** — log-depth-by-level OLS regression slope. For present YES levels indexed by rank i, with quantities q_i = yes_qty_fp_i, set x_i = i and y_i = ln(q_i). Then `depth_slope_yes = β_yes` from OLS regression y_i = α_yes + β_yes * x_i. Requires at least 3 present YES levels; NULL otherwise. Units: log-ct per level rank. Typical range: usually negative in front-loaded books (depth concentrated near the touch), near zero in flat books, positive in unusual back-loaded books. Log formulation chosen over raw linear because raw slope is dominated by single large resting orders and scales badly across liquidity regimes; log-depth measures shape rather than absolute size, comparable across markets.

7. **depth_slope_no** — analogous to depth_slope_yes but over present NO levels with q_i = no_qty_fp_i. Same requirements, units, interpretation, and NULL rules.

8. **top_of_book_widening** — let spread_t = yes_ask_1(t) - yes_bid_1(t); spread_{t-1} = yes_ask_1(t-1) - yes_bid_1(t-1) where t-1 is the immediately previous observed minute row for the same ticker in T38-MIN. Then `top_of_book_widening = spread_t - spread_{t-1}`. Units: dollars/price points. Range unbounded but practically centered near zero. Positive = spread widened vs previous observed minute; negative = tightened. NULL if no previous minute row, or if either minute lacks valid top-of-book bid/ask. No implicit zero-fill over missing minutes; gap-sensitive consumers should consult separate quality flags. Requires prior-minute state for the same ticker; single lag, no longer history.

9. **book_compactness_index** — rank-weighted visible-depth concentration. Define rank-weights w_i = 1/i for i in {1..10}. Let TOT = YES10 + NO10. Let WD = Σ_{i present in YES} (w_i * yes_qty_fp_i) + Σ_{i present in NO} (w_i * no_qty_fp_i). Then `book_compactness_index = WD / TOT`. Unitless, range (0, 1]. Value of 1.0 means all visible depth sits at level 1; lower values mean depth pushed farther down the ladder. NULL if TOT = 0. Single-pass. Distinct from slope (which measures one-sided profile shape) — compactness measures overall closeness of visible two-sided liquidity to the touch. A book can be balanced but dispersed, or imbalanced but compact.

**Data-quality / provenance flags**
- `book_snapshot_source ∈ {rest, websocket}` — where the canonical snapshot originated for this minute.
- `snapshot_complete_bool` — true if a full snapshot was seen within the minute; false if the minute was filled strictly via interpolated deltas since the last snapshot.
- `sequence_gap_flag` — true if any delta sequence gap was detected in the preceding interval (even if later reconciled).

### 3.2 T38-TICK — raw depth event stream

**Path:** `arb-executor/data/durable/t38_books_tick/`
**Grain:** one row per orderbook-related event (snapshot, delta) and optional trade events.
**Partitioning:** `date=YYYY-MM-DD/ticker=KX.../`

**Keys**
- `ticker` — Kalshi market ticker.
- `event_ts` — Unix epoch milliseconds (or better) when the event was received / timestamped.
- `event_schema_version` — integer, starting at 1; increments on any breaking encoding change.

**Event type**
- `event_type ∈ {snapshot, delta, trade, status}`

**Snapshot events** (`event_type = snapshot`)
- `snapshot_depth_levels` — number of levels included per side.
- `yes_prices[]`, `yes_qty_fp[]` — arrays of length `snapshot_depth_levels`.
- `no_prices[]`, `no_qty_fp[]` — arrays of length `snapshot_depth_levels`.

These are direct encodings of API snapshot responses; no inference.

**Delta events** (`event_type = delta`)
- `delta_side ∈ {YES, NO}`
- `delta_price` — price level affected.
- `delta_qty_change_fp` — signed size delta (positive for add, negative for reduce/remove).
- `delta_level_index` — optional; if API gives explicit level index.
- `seq_id` — sequence or message identifier if provided by Kalshi; used for gap detection and resync triggers.

When multiple `orderbook_delta` messages share the same `event_ts` for a given ticker, the producer MUST apply all such deltas to the in-memory book state before emitting any derived snapshot, T38-MIN row, or T38-TICK aggregate view for that timestamp. All deltas with identical `event_ts` are treated as a single logical update; the resulting book state is emitted once per timestamp. This matches Kalshi exchange semantics when multiple order updates arrive within the same millisecond and prevents per-delta intermediate states from being mistaken for the canonical book state at that moment. Reference: Marriott (2026), Section 4.1 grouped-emit reconstruction algorithm.

**Trade events** (`event_type = trade`, optional in v1 if trade channel already covered by G9)
- `trade_price`
- `trade_qty_fp`
- `trade_taker_side ∈ {yes, no}`

**Status events** (`event_type = status`)
- `status_code` — e.g., market open, suspended, closed.
- `status_payload` — JSON blob if needed.

T38-TICK is **the** source for `get_book_at`. Snapshot and delta semantics follow Kalshi orderbook update docs exactly; no rewriting or "smart" aggregation at this layer.

## 4. Producer architecture

### 4.1 Overview

T38 consists of:
- A **subscription manager** that controls WebSocket connections and ticker assignments.
- A **WebSocket worker** per connection that:
  - Subscribes to `orderbook_updates` for its assigned tickers.
  - Processes `orderbook_snapshot` and `orderbook_delta` messages.
  - Maintains in-memory local books (`LocalBook[ticker]`).
  - Emits T38-TICK events and, at minute boundaries, T38-MIN snapshots.
- A **REST snapshot worker** that:
  - Periodically calls Kalshi REST orderbook endpoints for selected tickers.
  - Seeds new ticker books.
  - Cross-checks local reconstruction against ground truth snapshots and triggers resync on discrepancy.
- A **compaction / rollup job** that:
  - Moves raw NDJSON / chunk files from `/tmp/t38_stream_raw/` into partitioned Parquet under `data/durable/t38_books_minute/` and `t38_books_tick/`.
  - Updates MANIFEST catalog.

### 4.2 WebSocket subscription strategy

Kalshi WebSocket `orderbook_updates` channel semantics:
- On subscription to a market, server sends an initial `orderbook_snapshot` object, then streams `orderbook_delta` messages for any changes.
- Client can call `update_subscription` to add or remove markets without dropping the connection.
- Snapshot messages can also be requested explicitly with `get_snapshot` without changing subscription.

T38 uses multiple WebSocket connections:
- Each connection manages *up to* `K` tickers (initial heuristic: 50–100), stratified by activity/volume so that high-volume tickers are not co-located with too many other high-volume markets.
- Subscription manager maintains a registry of `(ticker → connection_id)`, monitors per-connection event rate and processing lag, and migrates low-priority tickers off hot connections via `update_subscription` when lag exceeds threshold.
- On connection start: call `subscribe` with initial ticker set; wait for `orderbook_snapshot` per ticker; initialize `LocalBook[ticker]`.
- During runtime: for each `orderbook_delta`, update `LocalBook[ticker]` and write delta event to T38-TICK raw buffer. For each new `orderbook_snapshot`, replace `LocalBook[ticker]` wholesale and write snapshot event.

### 4.3 REST snapshot worker

REST endpoints (Kalshi orderbook API) return full book snapshots per ticker.

T38 uses REST for:
- **Cold start**: when a ticker enters the universe, call REST, seed `LocalBook[ticker]`, then attach WebSocket subscription.
- **Periodic resync**:
  - Every N minutes (default `N = 15`), the worker cycles through all active tickers and requests a full REST orderbook snapshot for each.
  - Empirical evidence from Marriott (2026) shows that a 15-minute full-cycle cadence applied across approximately 30,000 active Kalshi markets per day was sufficient to bound reconstruction error to a single snapshot window, with zero observed sequence gaps under normal operating conditions.
  - For each ticker, compare the REST snapshot to `LocalBook[ticker]` rebuilt via snapshot+delta.
  - If difference exceeds tolerance (e.g., any price level difference, or aggregate depth difference over threshold), flag `sequence_gap_flag` and hard-resync: reset book to REST snapshot and resume delta processing.
  - The daemon supports per-ticker cadence override; `N` may be reduced for specific high-priority tickers if downstream validation or operational monitoring shows the need.

REST snapshots are commonly persisted with one row per active price level. Before constructing reconstruction windows for `get_book_at` or running T38c Check 1 (reconstructed `LocalBook` vs REST snapshot comparison), the producer MUST deduplicate snapshot timestamps per `(ticker, snapshot_ts)` and operate on the distinct set of snapshot anchors. Failing to deduplicate would incorrectly treat each populated level as a separate window boundary and multiply iteration work by the number of populated levels. Reference: Marriott (2026), Section 5.2 duplicate-snapshot-timestamp implementation pitfall.

- **Gap handling**: if WebSocket worker detects missing `seq_id` ranges or protocol-level errors, triggers immediate REST resync and snapshot event.

Rate limiting: global cap on REST calls per minute, tuned to stay comfortably below Kalshi's documented / observed quotas. Backoff on any 429/5xx responses with jitter.

### 4.4 LocalBook representation

`LocalBook[ticker]` holds the current full-depth orderbook state for a ticker: two ordered maps per side (YES and NO), keyed by price, with quantities in fp units. Additional summary fields (best bid/ask, depth aggregates) are derived on demand, not stored separately. All transformation for T38-MIN and `get_book_at` uses `LocalBook` keyed by `(ticker, ts)` snapshots.

`LocalBook` update semantics are timestamp-grouped, not per-delta-emitted. If multiple deltas for the same ticker share the same `event_ts`, all such deltas are applied first, and only then is the resulting book state treated as the canonical state for that timestamp. This rule is load-bearing for `get_book_at(ticker, ts)` correctness and for any intra-minute book view derived from T38-TICK.

## 5. Outputs

1. **T38-MIN corpus** — `arb-executor/data/durable/t38_books_minute/` — per-minute, per-ticker depth snapshots aligned 1:1 with T37 per-minute rows. Top-10 levels per side and ~10 derived aggregate metrics. Directly joinable to `per_minute_universe.parquet` by `(ticker, minute_ts)`.

2. **T38-TICK corpus** — `arb-executor/data/durable/t38_books_tick/` — raw event stream: snapshots and deltas (+ optional trades and status). Primary inputs for `get_book_at(ticker, ts)` reconstruction, Layer B v2+ enhancements (queue modeling, slippage distributions, realized spread), and depth-driven quantitative research.

3. **MANIFEST / catalog entries** — updated MANIFEST-like file under `arb-executor/data/durable/` documenting available dates and tickers, schema versions for T38-MIN and T38-TICK, and checksums for partition files.

## 6. Validation gate (T38c)

T38a is not "trusted" by default. Validation happens via a T38c gate, analogous to T37 phase gates and Cat 11 forensic replay.

**T38c checks:**

1. **Internal consistency (books vs REST)** — for a random sample of `(ticker, ts)` pairs, compare `LocalBook` reconstruction to REST orderbook snapshot. Accept only if mismatches are within a defined tolerance (ideally zero difference across all listed levels).

2. **Minute-grain alignment with T37** — for the overlap window where both T37 and T38-MIN exist: recompute T37 per-minute features that depend on best bid/ask and shallow depth from T38-MIN (or directly from `get_book_at`); compare distributions and per-minute values; any systematic bias must be investigated and resolved. This check explicitly includes calibration of T37 depth-proxy columns against T38 actual depth, especially `price_levels_consumed`, consumption-velocity style measures, and trade-clustering proxies where overlap permits. Goal: confirm that T37's original best-bid/ask and per-minute aggregates are accurate or quantify any residual bias.

3. **Event-level sanity checks** — no negative depth after applying deltas; no levels with zero qty remain in the book; spreads remain within plausible bounds; pathologies (e.g., infinite spread) are tagged and rare.

4. **Sequence and gap diagnostics** — track frequency of `sequence_gap_flag` and REST resync events. If gaps are frequent enough to threaten measurement reliability, T38 must not be treated as A-tier for those tickers without mitigation.

T38c passes must be recorded in `LESSONS.md` (F-category) and/or `ANALYSIS_LIBRARY.md` as a canonical validation artifact.

## 7. Open items for v2 (T38b+)

- **Expanded depth exports:** optionally store full depth in T38-MIN for specific high-liquidity tickers where deeper book structure matters.
- **Latency and timestamp calibration:** measure and model latency between Kalshi server time and local timestamps, especially if later needed for sub-second execution modeling.
- **Multi-venue integration:** if additional venues are ever added, T38b could generalize to multi-source books with venue tags; v1 is Kalshi-only.
- **Compression / encoding optimization:** columnar encoding optimizations (e.g., run-length encoding of prices, dictionary-encoding of deltas) once volume is clear.

## 8. Cross-references

- **SIMONS_MODE.md** — Problem 1 vs Problem 2, minute-scale microstructure, single canonical observation grain for historical and live.
- **LESSONS.md** — A20–A24 (data tiers, variable inventory), A22/A24/A31 (volume and depth as first-class variables), F1/F8/F17/F22/F30 (durability, corruption modes, canonical sources, reconciliation).
- **ANALYSIS_LIBRARY.md** — Cat 11 (forensic replay realized capture) — tick-level semantics and need for accurate depth at fill time.
- **per_minute_universe_spec.md (T37a)** — defines per-minute grain and feature set T38-MIN must align to.
- **layer_b_v2_spec.md (T36a)** — uses tick-level semantics; will consume T38-TICK and/or T38-MIN for future refinements.
- **forensic_replay_v1_spec.md** — reference for tick-level simulation and fill semantics that `get_book_at` must support.

## 9. Changelog

- **2026-05-12 — Draft v0.1 (chat-side synthesis)**
  - Initial T38a spec authored from SIMONS_MODE/LESSONS/ANALYSIS_LIBRARY/T37/T36 context and Kalshi orderbook API + reconstruction literature.
  - Depth horizon set at top-10 levels per side in T38-MIN; full depth preserved in T38-TICK.
  - Two-layer architecture (T38-MIN + T38-TICK) formalized with `get_book_at` as the core reconstruction primitive.
  - File paths named with `t38_` prefix to distinguish live daemon lineage from G9 historical pull.
  - ct terminology in prose, taker-side semantics normalized to yes/no, additive schema-alignment constraint explicit, T38c calibration wording extended to cover T37 depth-proxy validation.

- **2026-05-12 — Draft v0.2 (derived-metric formulas locked)**
  - Replaced the deferred "Derived aggregate depth metrics" placeholder in Section 3.1 with closed-form definitions for all T38-MIN depth aggregates.
  - Locked imbalance metrics to cumulative top-5 and top-10 depth ratios.
  - Locked `depth_weighted_mid` to top-of-book microprice form in YES-price space.
  - Locked `depth_slope_yes` / `depth_slope_no` to log-depth-by-level OLS slopes.
  - Kept `book_compactness_index` and defined it as a rank-weighted visible-depth concentration metric.
  - Added explicit null-handling, units, range expectations, and computational-shape rules for each metric.

- **2026-05-12 — Draft v0.3 (Marriott 2026 empirical validation amendments)**
  - REST snapshot cadence: locked default to `N = 15` minutes, with empirical grounding from Marriott (2026) Section 3 (15-minute full-cycle cadence across ~30k active markets with zero observed sequence gaps).
  - T38-TICK / LocalBook: added explicit grouped-delta-by-timestamp emit semantics — all deltas sharing `event_ts` apply atomically, one emit per timestamp. Closes a missing-edge-case gap surfaced by Marriott (2026) Section 4.1.
  - REST snapshot worker: added explicit deduplication requirement for snapshot timestamps before window construction. Closes implementation pitfall surfaced by Marriott (2026) Section 5.2.
  - All v0.3 amendments are additive; v0.2 formulas, schema, and architecture stand unchanged.
