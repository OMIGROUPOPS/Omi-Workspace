# OMI Taxonomy — Data Tiers, Analysis Depth, Variable Inventory

**Purpose:** Formal definitions and shared language for any analysis in the OMI tennis trading operation. Two parallel classification axes (data tier and analysis depth) plus the per-tier variable inventory. Any prior analysis or proposed analysis must reference both axes.

**Cross-references:**
- Lessons that establish this framing: A20, A22, A23, A24, A28, E23, E26, F16, F20.
- Library entries that classify against this taxonomy: ANALYSIS_LIBRARY.md.

**Last populated:** 2026-04-30 ~14:55 ET, mid-Session 4. Section 1 match-counts placeholder pending tier-counter completion. Section 4 fully populated with verified TZ labels.

---

## SECTION 1: DATA TIER DEFINITIONS

Tiers are ordered by fidelity: A is highest, C is lowest. Higher tier means more variables, finer time resolution, or both. Some matches exist in multiple tiers; analysis on a multi-tier match should use the highest available tier.

### A-tier — Full depth tick CSVs

- Source: /root/Omi-Workspace/arb-executor/analysis/premarket_ticks/*.csv
- Date range: Apr 18 2026 to ongoing
- File count: 1,732 (Apr 30 snapshot)
- Match count both-sides: 854 events (per partial tier-counter, Apr 30). Per-category: ATP_CHALL=455, ATP_MAIN=132, WTA_CHALL=133, WTA_MAIN=134. Caveat: 24 filenames unparsed by tier-counter regex (5-letter pair codes like KXATPCHALLENGERMATCH-26APR20LAOST-OST.csv vs assumed 6-letter pairs); true match count is at least 854, undercount likely by ~12-24 events. See F24.
- Sampling rate: Approximately every second when book changes
- Schema: 27 columns. ts_et (ET), ticker, bid_1 through bid_5 with sizes, ask_1 through ask_5 with sizes, mid, bid_depth_5, ask_depth_5, depth_ratio, last_trade.
- All timestamps: VERIFIED ET.
- What it uniquely supports: Order book depth questions, capacity-for-size analysis, microstructure (iceberg detection, fade vs absorb, depth ratio dynamics), book imbalance trajectory, market impact estimation.

### A-tier supplemental — analysis/trades/*.csv

- Source: /root/Omi-Workspace/arb-executor/analysis/trades/
- Date range: Apr 19 2026 to ongoing
- File count: 1,693
- Total trade records: ~2.75M
- Schema: 5 columns. ts_et (ET), ticker, price, count, taker_side.
- All timestamps: VERIFIED ET.
- What it uniquely supports: Aggressor side, VWAP, volume profile, market impact (Kyle's lambda), buying-pressure-vs-selling-pressure analysis. Per A26, this is depth-3 and depth-4 capacity collected but unused.

### B-tier — Top-of-book BBO archive

- Source: arb-executor/data/durable/bbo_log_v4.csv.gz (durable per Phase 1B Session 6, sha256-verified, 879 MB; producer wrote to /tmp/bbo_log_v4.csv.gz which is the live /tmp copy still used by tennis_v5.py)
- Date range: 2026-03-20 04:49:51 ET to 2026-04-17 15:15:49 ET
- Row count: 515,454,156 (~515M)
- Match count by category: TO BE POPULATED. B-tier counter failed mid-stream Apr 30 (OOM on 515M-row set accumulation in 1.9 GB VPS). Retry pending with disk-incremental approach (jsonl append per ticker, aggregate post-stream).
- Schema: 5 columns. timestamp (ET), ticker, bid, ask, spread.
- All timestamps: VERIFIED ET (tennis_v5.py line 285 time.strftime + system tz America/New_York).
- Producer: tennis_v5.py (legacy bot)
- What it uniquely supports: Larger N for cell aggregation than A-tier alone; full-period top-of-book trajectory analysis; binary "did price reach +X" questions; Channel 1 vs Channel 2 timing decomposition (with match-start derivable).
- What it does NOT support: Order book depth, capacity, microstructure beyond top-of-book.

### C-tier — Match summary table

- Source: tennis.db.historical_events
- Date range: Jan 2 2026 to Apr 10 2026
- Row count: 5,889 (with total_trades >= 10)
- Match count by category: TO BE POPULATED. C-tier counts not yet computed; tier-counter completed A-tier successfully but failed B-tier with OOM, and Step 4 cross-tier overlap did not run. C-tier counts deferred to OOM-resilient retry of tier-counter.
- Schema: 14 columns. event_ticker, category, winner, loser, first/min/max/last for both winner and loser sides, total_trades, first_ts, last_ts.
- All timestamps: VERIFIED UTC (ISO 8601 with Z suffix).
- What it uniquely supports: Pre-Mar-20 historical reach; existence proofs across the entire Jan 2 - Apr 10 window; volume proxy via total_trades.
- What it does NOT support: Any timing decomposition (only first and last timestamps for the entire match), order book depth, microstructure.

### G-tier — Full Kalshi historical archive (per-minute candles + microsecond trades)

- Source: /root/Omi-Workspace/arb-executor/data/historical_pull/
- Subdirectories: candlesticks/ (per-market CSV), trades/ (per-market CSV), market_metadata/ (per-market JSON), enumeration/manifest.json
- Date range: 2025-06-18 to 2026-05-02 (full Kalshi tennis archive at delivery)
- Manifest count: 20,110 markets total
- File counts on disk: 19,687 candlestick CSVs (423 sub-1-minute markets correctly skipped), 20,018 trade CSVs (92 zero-volume markets correctly skipped), 20,110 metadata JSONs (one per manifest market)
- Total size: 5.0 GB
- Sampling rate: Per-minute candlesticks (median 250 candles per market, p95 485, range 3-647); trade tape at microsecond resolution (median 100 trades per market, p95 525, range 2-792)
- Schema (candlesticks CSV, 17 columns): end_period_ts (epoch seconds UTC), open_interest_fp, price_close, price_high, price_low, price_mean, price_open, price_previous, volume_fp, yes_ask_close, yes_ask_high, yes_ask_low, yes_ask_open, yes_bid_close, yes_bid_high, yes_bid_low, yes_bid_open. Price fields are decimal dollars; _fp suffix denotes fixed-point integer. Field names confirmed against /candlesticks/*.csv header line. **Schema variant by era (per LESSONS F29):** 2025-era markets use bare names as listed above; 2026-era markets append `_dollars` suffix to all price fields (price_close_dollars, yes_bid_close_dollars, yes_ask_close_dollars, etc.). Value semantics are identical; only column names differ. T17 parquet conversion normalizes to bare names as canonical.
- Schema (trades CSV, 7 columns): count_fp, created_time (ISO 8601 microsecond UTC, e.g., 2025-06-18T13:41:08.553962Z), no_price_dollars, taker_side (yes|no), ticker, trade_id, yes_price_dollars.
- Schema (market_metadata JSON, ~45 keys per market): ticker, event_ticker, custom_strike (contains tennis_competitor UUIDs for player identity), open_time, close_time, created_time, settlement_ts, settlement_value_dollars, result, status, volume_fp, volume_24h_fp, open_interest_fp, last_price_dollars, expected_expiration_time, expiration_time, can_close_early, early_close_condition, rules_primary, rules_secondary, market_type, notional_value_dollars, liquidity_dollars, no_ask_dollars, no_bid_dollars, yes_ask_dollars, yes_bid_dollars, no_sub_title, yes_sub_title, _tier (marks historical vs live), and others. All timestamps ISO 8601 UTC.
- All timestamps: VERIFIED UTC. Trade created_time is microsecond ISO Z; candle end_period_ts is epoch seconds UTC; metadata timestamps are ISO 8601 UTC.
- Producer: arb-executor/data/scripts/build_g9_archive.py — pulls from Kalshi /historical/markets/{ticker}/candlesticks + /historical/trades + /historical/markets/{ticker} endpoints. Re-runnable to extend forward.
- What it uniquely supports: Per-moment bounce analysis (Layer A) on a 10x larger universe than B-tier; full-archive coverage retroactive to mid-2025; aggressor-flow analysis (taker_side per trade) at microsecond resolution; cross-tier validation against B-tier for the Mar 20 - Apr 17 overlap window; player-identity work via custom_strike.tennis_competitor UUIDs (per ROADMAP T25 fair-value scoping).
- What it does NOT support: Order book depth beyond top-of-book candle bid/ask (no bid_2-5 / ask_2-5 — that requires A-tier); pre-Jun-2025 data (Kalshi /historical/* endpoints have a horizon).
- Status: G9 dataset DELIVERED 2026-05-02 per ROADMAP G9. Parquet conversion pending T17 (~30-60 min runtime to consolidated g9_trades.parquet + g9_candles.parquet + g9_metadata.parquet). Layer A v1 implementation gated on T17 + T18 (candles semantics probe).

### Other operational data sources (full schemas in Section 4)

- tennis.db.book_prices (3,064,108 rows, Apr 19+) — CANONICAL SHARP CONSENSUS SOURCE per F15
- tennis.db.kalshi_price_snapshots (290,217 rows, Apr 21+) — has volume_24h not present elsewhere
- tennis.db.live_scores (4,865 rows) — final-outcome only per A25
- tennis.db.bookmaker_odds (32,471 rows) — DEPRIORITIZED per F15
- tennis.db.betexplorer_staging (42,941 rows) — external odds with FV cents derived
- tennis.db.dca_truth (655 rows) — pre-computed DCA outcomes
- tennis.db.edge_scores (203 rows) — Pinnacle vs Kalshi A-F grade
- tennis.db.players (612 rows) — sparsely populated, players.last_updated UTC per F20
- tennis.db.matches (3,627 rows, Feb 5 - Apr 17) — operational fill log; entry_time NULL on live (F17), settlement_time has two formats (F18)
- analysis/trades/*.csv (1,693 files, Apr 19+) — trade-level with taker_side per A26
- live_v3_*.jsonl logs — bot structured event log, ts ET-verified, ts_epoch tz-agnostic
- arb-executor/data/durable/kalshi_fills_history.json (7,489 server-side fills, Mar 1 - Apr 29; durable per Phase 1B Session 6, sha256-verified, 4.5 MB; producer at tmp/fills_history_pull.py per Phase 1C-i) — TIER-A FACT SOURCE per A30. Canonical for entry timing, fill quantity, taker vs maker, settlement reconciliation. Supersedes matches.matches and local logs for per-fill ground truth. created_time is UTC ISO Z; ts is Unix epoch. Original /tmp copy remains the live working file for re-pull operations.

### External sources (status varies — see per-bullet annotation)

- Kalshi `/historical/markets/{ticker}/candlesticks` API — PULLED 2026-05-02 per G9 delivery, now in G-tier at arb-executor/data/historical_pull/candlesticks/. Re-pullable via arb-executor/data/scripts/build_g9_archive.py.
- Kalshi `/historical/trades` API — PULLED 2026-05-02 per G9 delivery, now in G-tier at arb-executor/data/historical_pull/trades/. Microsecond timestamps + taker_side per A26.
- Kalshi orderbook history — NOT YET PULLED. Endpoint surface unverified; periodic depth snapshots may or may not be available retroactively. Probe pending if/when depth-history analysis becomes a priority.
- Sportsbook line history (DraftKings, Pinnacle, etc.) — NOT PULLED. The tennis.db.book_prices table holds poll-based snapshots from this session's bot operation, not full historical DK/Pinnacle line history. Genuinely external; would require separate scraping infrastructure if needed.

---

## SECTION 2: ANALYSIS DEPTH LEVELS

Depth describes what class of question is being asked, not how complex the math is. Higher depth requires more variables and unlocks fundamentally new question classes.

### Depth 0 — Existence

- Question class: Did X occur at all.
- Minimum data: One summary statistic per match per side.
- Tier sufficient: C.
- Example: "In 70.7% of 458 paired matches, did both sides briefly reach +10c above first-observed price." (April 14 paired analysis.)
- Strict limits: Says nothing about magnitude beyond the threshold tested, nothing about capturability, nothing about timing, nothing about per-cell distribution.

### Depth 1 — Distribution

- Question class: What is the distribution of X across matches.
- Minimum data: Aggregated summary statistics across many matches.
- Tier sufficient: C.
- Example: "What fraction of matches in cell X had max-bounce greater than +Yc, plotted across Y from 1 to 50."
- Strict limits: Says magnitude and frequency. Says nothing about timing or capturability.

### Depth 2 — Trajectory

- Question class: When during the match did X happen.
- Minimum data: Time series of bid/ask.
- Tier sufficient: B (top-of-book OK).
- Example: "Of matches that reached +10c, what fraction reached it before match start (Channel 1) vs after (Channel 2)."
- Strict limits: Says timing. Says nothing about whether the move was capturable in size.

### Depth 3 — Capacity

- Question class: Could a real order have filled at the price.
- Minimum data: Time series with order book depth and sizes.
- Tier sufficient: A (depth required).
- Example: "When the price spiked to +15c, was there at least 10 contracts of resting size at the target."
- Strict limits: Says capturability for our actual sizing. Says nothing about why the move happened.

### Depth 4 — Microstructure

- Question class: What is the structural property of the price/order behavior.
- Minimum data: A-tier plus modeling.
- Tier sufficient: A.
- Example questions: Realized volatility per cell. Autocorrelation of returns. Depth ratio dynamics. Iceberg detection. Effective vs realized spread. Greeks (delta, gamma, theta, vega) properly computed. Implied volatility surface. Kyle's lambda / market impact.
- Strict limits: Says regime properties. Says nothing about strategy P&L.

### Depth 5 — Strategy simulation

- Question class: What would realized P&L be if strategy X were deployed over period Y.
- Minimum data: Depth-3 plus bot's actual entry/exit logic, fees, slippage, capital constraints, order race conditions.
- Tier sufficient: A plus bot config.
- Example: "Replay of bot's actual entry/exit logic on Apr 18-29 tick data, with config Z, with fee model, computing realized P&L per cell."
- Strict limits: Says strategy validity for a specific config. Says nothing about external alpha sources or context dependencies.

### Depth 6 — Cross-sectional and temporal context

- Question class: How does edge depend on external variables.
- Minimum data: Depth-5 plus external data (sportsbook lines, surface, round, ranking, calendar).
- Tier sufficient: A plus external sources.
- Example questions: Does Kalshi lag DraftKings by N seconds and is that exploitable. Does our edge vary by tournament tier or surface. Cross-match correlation during tournament-level news events.

---

## SECTION 3: DEPTH × TIER MATRIX

| Depth | C-tier | B-tier | A-tier |
|---|---|---|---|
| 0 — Existence | Yes | Yes | Yes |
| 1 — Distribution | Yes | Yes | Yes |
| 2 — Trajectory | Limited (only first_ts and last_ts) | Yes | Yes |
| 3 — Capacity | No | No | Yes |
| 4 — Microstructure | No | Partial (top-of-book vol only) | Yes |
| 5 — Strategy simulation | No | Limited (no fill simulation realism) | Yes |
| 6 — Cross-sectional context | No | No | Yes (with external data) |

---

## SECTION 4: VARIABLE INVENTORY PER SOURCE

Full column listing for every data source. Each variable described with type, TZ status, and depth questions enabled.

### A-tier — premarket_ticks/*.csv (27 columns, Apr 18+)

| Column | Type | TZ | Description | Depth enabled |
|---|---|---|---|---|
| ts_et | timestamp string | VERIFIED ET | Eastern Time tick timestamp, format YYYY-MM-DD HH:MM:SS AM/PM | 2-6 |
| ticker | string | n/a | Full Kalshi market ticker | identity |
| bid_1 | int (cents) | n/a | Best bid price | 0-2 |
| bid_1_sz | int | n/a | Size resting at best bid | 3-4 |
| bid_2 | int | n/a | 2nd-best bid price | 3-4 |
| bid_2_sz | int | n/a | Size at 2nd-best bid | 3-4 |
| bid_3 | int | n/a | 3rd-best bid price | 3-4 |
| bid_3_sz | int | n/a | Size at 3rd-best bid | 3-4 |
| bid_4 | int | n/a | 4th-best bid price | 3-4 |
| bid_4_sz | int | n/a | Size at 4th-best bid | 3-4 |
| bid_5 | int | n/a | 5th-best bid price | 3-4 |
| bid_5_sz | int | n/a | Size at 5th-best bid | 3-4 |
| ask_1 | int (cents) | n/a | Best ask price | 0-2 |
| ask_1_sz | int | n/a | Size resting at best ask | 3-4 |
| ask_2 | int | n/a | 2nd-best ask price | 3-4 |
| ask_2_sz | int | n/a | Size at 2nd-best ask | 3-4 |
| ask_3 | int | n/a | 3rd-best ask price | 3-4 |
| ask_3_sz | int | n/a | Size at 3rd-best ask | 3-4 |
| ask_4 | int | n/a | 4th-best ask price | 3-4 |
| ask_4_sz | int | n/a | Size at 4th-best ask | 3-4 |
| ask_5 | int | n/a | 5th-best ask price | 3-4 |
| ask_5_sz | int | n/a | Size at 5th-best ask | 3-4 |
| mid | float (cents) | n/a | (best_bid + best_ask) / 2 | 0-2 |
| bid_depth_5 | int | n/a | Sum of bid sizes top 5 levels | 3-4 |
| ask_depth_5 | int | n/a | Sum of ask sizes top 5 levels | 3-4 |
| depth_ratio | float | n/a | bid_depth_5 / (bid_depth_5 + ask_depth_5) | 4 |
| last_trade | int (cents) | n/a | Most recent trade price (0 if none) | 0-2 |

Used in prior analyses: 6 of 27 columns. 21 unused depth/size signals per A22.

### A-tier supplemental — analysis/trades/*.csv (5 columns)

| Column | Type | TZ | Description | Depth enabled |
|---|---|---|---|---|
| ts_et | timestamp string | VERIFIED ET | Eastern Time trade timestamp | 2-6 |
| ticker | string | n/a | Full Kalshi market ticker | join key |
| price | int (cents) | n/a | Execution price | 0-3 |
| count | int | n/a | Trade size in contracts | 3-4 |
| taker_side | string yes/no | n/a | Aggressor side | 4 |

Per A26: capacity and microstructure data already collected, barely used.

### B-tier — bbo_log_v4.csv.gz (5 columns, Mar 20 - Apr 17)

| Column | Type | TZ | Description | Depth enabled |
|---|---|---|---|---|
| timestamp | string | VERIFIED ET | Naive ET timestamp from system clock at write | 2 |
| ticker | string | n/a | Full Kalshi market ticker | join key |
| bid | int (cents) | n/a | Best bid only | 0-2 |
| ask | int (cents) | n/a | Best ask only | 0-2 |
| spread | int (cents) | n/a | ask - bid | 0-2 |

515M rows. Top-of-book only. No depth, no sizes, no aggressor side.

### C-tier — tennis.db.historical_events (14 columns, Jan 2 - Apr 10)

| Column | Type | TZ | Description | Depth enabled |
|---|---|---|---|---|
| event_ticker | TEXT PK | n/a | Kalshi event ticker | identity |
| category | TEXT | n/a | ATP_MAIN / ATP_CHALL / WTA_MAIN / WTA_CHALL | partition |
| winner | TEXT | n/a | Winning player code | side identity |
| loser | TEXT | n/a | Losing player code | side identity |
| first_price_winner | REAL | n/a | First observed trade price, winner side | 0-1 (with A19 caveats) |
| min_price_winner | REAL | n/a | Min price during full match | 0-1 |
| max_price_winner | REAL | n/a | Max price during full match | 0-1 |
| last_price_winner | REAL | n/a | Last traded price before settlement | 0-1 |
| first_price_loser | REAL | n/a | First observed trade price, loser | 0-1 |
| min_price_loser | REAL | n/a | Min price during full match, loser | 0-1 |
| max_price_loser | REAL | n/a | Max price during full match, loser | 0-1 |
| total_trades | INTEGER | n/a | Trade count | 1 |
| first_ts | TEXT | VERIFIED UTC | ISO 8601 with Z, first timestamp | 2 (limited) |
| last_ts | TEXT | VERIFIED UTC | ISO 8601 with Z, last timestamp | 2 (limited) |

### tennis.db.book_prices (3,064,108 rows, Apr 19+) — CANONICAL SHARP CONSENSUS per F15

| Column | Type | TZ | Description |
|---|---|---|---|
| event_ticker | TEXT PK | n/a | Kalshi event |
| book_key | TEXT PK | n/a | Bookmaker (pinnacle, gtbets, etc.) |
| player1_name | TEXT | n/a | Player 1 |
| player2_name | TEXT | n/a | Player 2 |
| book_p1_fv_cents | REAL | n/a | Bookmaker FV cents player 1 |
| book_p2_fv_cents | REAL | n/a | Bookmaker FV cents player 2 |
| raw_odds_p1 | REAL | n/a | Decimal odds player 1 |
| raw_odds_p2 | REAL | n/a | Decimal odds player 2 |
| vig_pct | REAL | n/a | Bookmaker vig (already stripped from FV) |
| sport_key | TEXT | n/a | Sport identifier |
| commence_time | TEXT | VERIFIED UTC | ISO Z scheduled match start |
| polled_at | TEXT PK | VERIFIED ET | When this snapshot was taken (system tz, naive) |

Multiple bookmakers per event per poll. Pinnacle present. Enables: depth-6 cross-platform edge analysis, FV anchor reconciliation, lag analysis.

### tennis.db.kalshi_price_snapshots (290,217 rows, Apr 21+)

| Column | Type | TZ | Description |
|---|---|---|---|
| polled_at | TEXT PK | VERIFIED ET | Author named variable now_et explicitly |
| ticker | TEXT PK | n/a | Market ticker |
| event_ticker | TEXT | n/a | Event ticker |
| series_ticker | TEXT | n/a | Series ticker |
| bid_cents | INTEGER | n/a | Bid at poll |
| ask_cents | INTEGER | n/a | Ask at poll |
| last_cents | INTEGER | n/a | Last trade at poll |
| volume_24h | REAL | n/a | Trailing 24h volume — signal not in B-tier or A-tier |
| commence_time | TEXT | VERIFIED UTC | Match start UTC |

5-minute resolution. Used by greeks_decomposition.py.

### tennis.db.live_scores (4,865 rows) — LIMITED per A25

| Column | Type | TZ | Description |
|---|---|---|---|
| id | INTEGER PK | n/a | Row ID |
| te_match_id | TEXT | n/a | TennisExplorer match ID |
| player1 | TEXT | n/a | Player 1 name |
| player2 | TEXT | n/a | Player 2 name |
| p1_sets | INTEGER | n/a | Final set count player 1 |
| p2_sets | INTEGER | n/a | Final set count player 2 |
| p1_games | TEXT | n/a | Per-set game scores (EMPTY in samples) |
| p2_games | TEXT | n/a | Per-set game scores (EMPTY in samples) |
| status | TEXT | n/a | Match status ('finished' in samples) |
| kalshi_ticker | TEXT | n/a | 3-letter side code (NOT full ticker) |
| last_updated | TEXT | VERIFIED ET | te_live.py has no UTC imports |

Schema suggests in-match state but population is final-outcome only.

### tennis.db.bookmaker_odds (32,471 rows) — DEPRIORITIZED per F15

| Column | Type | TZ | Description |
|---|---|---|---|
| id | INTEGER PK | n/a | Row ID |
| te_match_id | TEXT | n/a | TennisExplorer match ID |
| player1 | TEXT | n/a | Player 1 ('?' literal in samples) |
| player2 | TEXT | n/a | Player 2 ('?' literal in samples) |
| p1_decimal_odds | REAL | n/a | Decimal odds |
| p2_decimal_odds | REAL | n/a | Decimal odds |
| p1_implied_prob | REAL | n/a | Implied probability |
| p2_implied_prob | REAL | n/a | Implied probability |
| kalshi_ticker | TEXT | n/a | NULL in samples |
| kalshi_price | INTEGER | n/a | NULL in samples |
| edge_pct | REAL | n/a | NULL in samples |
| scraped_at | TEXT | UNVERIFIED | Naive format, likely ET |

Junk-drawer. Use book_prices instead.

### tennis.db.betexplorer_staging (42,941 rows)

| Column | Type | TZ | Description |
|---|---|---|---|
| p1_name | TEXT PK | n/a | Player 1 |
| p2_name | TEXT PK | n/a | Player 2 |
| p1_fv_cents | REAL | n/a | FV cents player 1 (vig stripped) |
| p2_fv_cents | REAL | n/a | FV cents player 2 |
| raw_odds_p1 | REAL | n/a | Raw decimal odds |
| raw_odds_p2 | REAL | n/a | Raw decimal odds |
| vig_pct | REAL | n/a | Vig stripped |
| tournament | TEXT | n/a | Tournament identifier |
| source_url | TEXT | n/a | Scrape URL |
| scraped_at | TEXT PK | UNVERIFIED | Naive format, likely ET |

External odds with tournament context. Useful for depth-6 surface/tournament-tier conditional analysis.

### tennis.db.dca_truth (655 rows)

| Column | Type | TZ | Description |
|---|---|---|---|
| ticker | TEXT PK | n/a | Position ticker |
| match_date | TEXT | UNVERIFIED | Match date |
| side_code | TEXT | n/a | 3-letter side code |
| entry_price | REAL | n/a | Entry price |
| entry_size | INTEGER | n/a | Entry size |
| dca_price | REAL | n/a | DCA fill price |
| dca_size | INTEGER | n/a | DCA fill size |
| blended_avg | REAL | n/a | Blended avg cost |
| total_size | INTEGER | n/a | Total contracts |
| exit_type | TEXT | n/a | Exit reason |
| exit_price | REAL | n/a | Exit price |
| result | TEXT | n/a | Outcome label |
| pnl_with_dca | REAL | n/a | P&L including DCA |
| pnl_without_dca | REAL | n/a | Hypothetical P&L without DCA |
| pnl_diff | REAL | n/a | DCA effect |
| category | TEXT | n/a | ATP_MAIN / ATP_CHALL / WTA_MAIN / WTA_CHALL |
| settlement_pnl | REAL | n/a | Settlement P&L |

Pre-computed DCA outcome dataset. 655 positions.

### tennis.db.edge_scores (203 rows)

| Column | Type | TZ | Description |
|---|---|---|---|
| event_ticker | TEXT PK | n/a | Event |
| player1_name | TEXT | n/a | Player 1 |
| player2_name | TEXT | n/a | Player 2 |
| pinnacle_p1 | REAL | n/a | Pinnacle FV cents player 1 |
| pinnacle_p2 | REAL | n/a | Pinnacle FV cents player 2 |
| kalshi_p1 | INTEGER | n/a | Kalshi price player 1 |
| kalshi_p2 | INTEGER | n/a | Kalshi price player 2 |
| edge_p1 | REAL | n/a | Edge player 1 |
| edge_p2 | REAL | n/a | Edge player 2 |
| grade | TEXT | n/a | A-F grade |
| sport_key | TEXT | n/a | Sport |
| commence_time | TEXT | VERIFIED UTC | Match start |
| updated_at | TEXT | UNVERIFIED | Naive, likely ET |
| fv_tier | INTEGER | n/a | FV tier |
| fv_source | TEXT | n/a | Source name |
| num_books | INTEGER | n/a | Number of books |

Per-event Pinnacle vs Kalshi edge with grading. Small dataset.

### tennis.db.players (612 rows)

| Column | Type | TZ | Description |
|---|---|---|---|
| id | INTEGER | n/a | Row ID |
| name | TEXT | n/a | Player name |
| kalshi_code | TEXT | n/a | 3-letter Kalshi code |
| country | TEXT | n/a | Country |
| ranking | INTEGER | n/a | Rank |
| ranking_date | TEXT | UNVERIFIED | Ranking date |
| surface_hard_wr | REAL | n/a | Hard surface win rate |
| surface_clay_wr | REAL | n/a | Clay surface win rate |
| surface_grass_wr | REAL | n/a | Grass surface win rate |
| last_updated | TEXT | VERIFIED UTC | SQLite date('now') returns UTC per F20 |

Sparsely populated. Surface and ranking columns enable depth-6 conditional analysis if backfilled.

### tennis.db.matches (3,627 rows, Feb 5 - Apr 17)

23 columns total. Per-fill operational history. Contains 977 real fills (live + live_log) and 2,650 backfill reconstructions.

Critical caveats:
- entry_time NULL on every live and live_log row sampled per F17. Must derive from JSONL logs.
- settlement_time has TWO writer formats: live rows naive (no Z), backfill rows ISO no-Z, different writers per F18.
- Backfill rows have settlement_time before entry_time (negative time_to_settle_min) per F14.

Selected columns of interest: id, date, event_ticker, market_ticker, tournament, category, our_side, other_side, entry_price, other_price, final_price, result, pregame_flat, dca_price, total_size, avg_price, pnl_cents, entry_time, settlement_time, time_to_settle_min, max_dip, scenario, source.

### live_v3_*.jsonl logs

| Field | Type | TZ | Description |
|---|---|---|---|
| ts | string | VERIFIED ET | Format YYYY-MM-DD HH:MM:SS AM/PM ET (literal ET suffix) |
| ts_epoch | float | VERIFIED tz-agnostic | Unix seconds |
| event | string | n/a | Event type (entry_filled, exit_filled, cell_match, scalp_filled, paper_fill, paper_exit_fill) |
| ticker | string | n/a | Market ticker |
| market_ticker | string | n/a | Market ticker (alternate field) |

Per F17 [REFINED]: live_v3 JSONL covers Apr 24+ only (166 entry_filled events). For Mar 26 - Apr 23 fills, see kalshi_fills_history.json (per A30) as the canonical source.

### kalshi_fills_history.json (durable: arb-executor/data/durable/) — TIER-A FACT SOURCE per A30

- Source: `arb-executor/data/durable/kalshi_fills_history.json` (4.5 MB, durable per Phase 1B Session 6, sha256-verified). Refresh: rerun `tmp/fills_history_pull.py` (per Phase 1C-i); the producer writes to `/tmp/kalshi_fills_history.json`, then copy to `arb-executor/data/durable/` to update the canonical.
- Date range: 2026-03-01 00:06:24 UTC to 2026-04-29 13:02:05 UTC (re-runnable to extend)
- Total fills: 7,489 (Mar: 3,497; Apr: 3,992)
- Schema: dict with keys fills (list), min_ts (epoch), max_ts (epoch), fetched_at (epoch float)
- /tmp ephemerality MITIGATED per Phase 1B Session 6 — durable copy at `arb-executor/data/durable/kalshi_fills_history.json` is canonical. Original /tmp file remains as live producer working file; F27 risk mitigated for this specific source. F1 PARTIAL CLOSURE in ROADMAP tracks the broader durability migration.

Per-fill schema (15 fields):

| Field | Type | TZ | Description |
|---|---|---|---|
| action | string | n/a | "buy" or "sell" — bot side of the trade |
| count_fp | string | n/a | Actual executed quantity (decimal string, e.g. "10.00"). AUTHORITATIVE per F9 |
| created_time | string | VERIFIED UTC | ISO 8601 with Z suffix |
| fee_cost | float | n/a | Per-fill fee in dollars |
| fill_id | string | n/a | UUID of the fill |
| is_taker | boolean | n/a | TRUE if bot was taker (lifted ask / hit bid), FALSE if maker. Depth-4 microstructure per A26 |
| market_ticker | string | n/a | Full Kalshi market ticker |
| no_price_dollars | float | n/a | NO-side price per share, decimal dollars |
| yes_price_dollars | float | n/a | YES-side price per share, decimal dollars |
| order_id | string | n/a | UUID of the parent order; groups partial fills |
| side | string | n/a | "yes" or "no" — which side of the binary contract |
| subaccount_number | int | n/a | 0 (single-account operation) |
| ticker | string | n/a | Full Kalshi ticker (== market_ticker in samples) |
| trade_id | string | n/a | UUID of the trade |
| ts | int | tz-agnostic | Unix epoch seconds (duplicates created_time) |

Closes/refines:
- F17 (matches.entry_time NULL): created_time is the canonical entry timestamp
- F9 (qty under-reporting): count_fp is the actual executed quantity
- F8 partial (settlement events sometimes unlogged locally): server-side has every fill
- A26 (taker_side underused): is_taker available at execution level
- F10 (Apr 17-23 fill detection broken locally): server-side has fills regardless of bot-side log gap

Joining: created_time is UTC; conversion required when joining to ET sources (premarket_ticks ts_et, JSONL ts, bbo_log_v4 timestamp). Per F16 / F20.

### Final TZ verification table

| Source | Column | Status |
|---|---|---|
| premarket_ticks | ts_et | VERIFIED ET |
| trades | ts_et | VERIFIED ET |
| bbo_log_v4 | timestamp | VERIFIED ET |
| historical_events | first_ts, last_ts | VERIFIED UTC |
| book_prices | polled_at | VERIFIED ET |
| book_prices | commence_time | VERIFIED UTC |
| kalshi_price_snapshots | polled_at | VERIFIED ET |
| kalshi_price_snapshots | commence_time | VERIFIED UTC |
| live_scores | last_updated | VERIFIED ET |
| players | last_updated | VERIFIED UTC (per F20) |
| matches | entry_time | NULL on live; UNVERIFIED on backfill (F17) |
| matches | settlement_time | UNVERIFIED, two writer formats (F18) |
| live_v3_*.jsonl | ts | VERIFIED ET |
| kalshi_fills_history.json | created_time | VERIFIED UTC |
| kalshi_fills_history.json | ts | VERIFIED tz-agnostic (Unix epoch) |
| live_v3_*.jsonl | ts_epoch | VERIFIED tz-agnostic |

ET sources joining UTC sources require explicit conversion. matches table timestamps require per-row format detection.

---

## SECTION 5: CHANGELOG

- 2026-04-30 ~13:21 ET: Initial scaffolding (commit c794b26).
- 2026-04-30 ~14:55 ET (this commit): Section 4 fully populated with verified TZ labels per the variable-inventory probe + TZ probe + TZ follow-up probe. Section 1 source descriptions populated; match counts placeholder pending tier-counter completion.
- 2026-04-30 ~16:00 ET: Section 1 partial-populate. A-tier match counts landed (854 both-sides events across 4 categories, 1,732 total CSV files). B-tier and C-tier counts deferred to OOM-resilient tier-counter retry. F24 (regex undercount) referenced.
- 2026-04-30 ~17:30 ET (item 10 closure): kalshi_fills_history.json added as Tier-A fact source. Section 1 reference, Section 4 full schema, TZ table updated. F17 reference adjusted to point at A30. Closes F17/F9/F8/A26/F10 partially-or-fully per E29.
- 2026-05-02 (Session 5): G9 dataset DELIVERED. Full Kalshi tennis archive pulled via /historical/markets/{ticker}/candlesticks + /historical/trades + /historical/markets/{ticker} endpoints. 20,110 markets, 5.0 GB at arb-executor/data/historical_pull/ (subdirs: candlesticks/, trades/, market_metadata/). Producer: arb-executor/data/scripts/build_g9_archive.py. TAXONOMY itself not edited Session 5 — G-tier addition deferred to Session 6 Phase 5. Reference: ROADMAP G9 closure.
- 2026-05-04 (Session 6 Phase 5-i): G-tier section added to Section 1 (commit 680ea208). Subdirectory layout, file counts, and producer documented.
- 2026-05-04 (Session 6 Phase 5-i-fix): G-tier schema corrected to disk-verified field names (commit f89c9bb). Pre-fix entry contained errors: claimed trades-as-JSON (actually CSV), wrong candle column names (used yes_close/no_close instead of disk-verified price_close/volume_fp/etc.), and over-stated file count (claimed 20,110 per file type when reality is 19,687 candles + 20,018 trades + 20,110 metadata). Same root cause as LESSONS D15 — schema drift between session memory and disk; should have probed before drafting.
- 2026-05-04 (Session 6 Phase 5-ii): /tmp paths updated to durable paths (commit f492d25). Five references updated: B-tier source (line 40), kalshi_fills_history.json bullet in Section 1 'Other operational data sources' (line 92), Section 4 heading (line 435), Section 4 source line (line 437), Section 4 ephemerality risk note (line 441 — risk → MITIGATED). Reflects Phase 1B/1C durability migration done earlier in Session 6.
- 2026-05-04 (Session 6 Phase 5-iii): External Sources section updated for G9 delivery reflection (commit c5a2477). Header changed from '(not currently pulled but accessible)' to '(status varies — see per-bullet annotation)'. Bullets 1-2 (Kalshi candlesticks + historical trades APIs) annotated PULLED (now in G-tier); bullets 3-4 (Kalshi orderbook history, sportsbook line history) annotated NOT PULLED with rationale.
- 2026-05-04 (Session 6 Phase 5-iv): This commit. CHANGELOG entries for Session 5 G9 delivery and Session 6 Phase 5 work appended.
