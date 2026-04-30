# OMI Taxonomy — Data Tiers, Analysis Depth, Variable Inventory

**Purpose:** Formal definitions and shared language for any analysis in the OMI tennis trading operation. Two parallel classification axes (data tier and analysis depth) plus the per-tier variable inventory. Any prior analysis or proposed analysis must reference both axes.

**Cross-references:**
- Lessons that establish this framing: A20, A22, A23, A24, E23, E26 in LESSONS.md.
- Library entries that classify against this taxonomy: ANALYSIS_LIBRARY.md.

---

## SECTION 1: DATA TIER DEFINITIONS

Tiers are ordered by fidelity: A is highest, C is lowest. Higher tier means more variables, finer time resolution, or both. Some matches exist in multiple tiers; analysis on a multi-tier match should use the highest available tier.

### A-tier — Full depth tick CSVs

- **Source:** `/root/Omi-Workspace/arb-executor/analysis/premarket_ticks/*.csv`
- **Date range:** Apr 18 2026 to ongoing
- **File count:** [TO BE POPULATED from variable-inventory CC probe]
- **Match count (events with both sides):** [TO BE POPULATED from tier-count CC probe]
- **Sampling rate:** Approximately every second when book changes
- **Schema:** 27 columns. ts_et, ticker, bid_1 through bid_5 with sizes, ask_1 through ask_5 with sizes, mid, bid_depth_5, ask_depth_5, depth_ratio, last_trade.
- **What it uniquely supports:** Order book depth questions, capacity-for-size analysis, microstructure (iceberg detection, fade vs absorb, depth ratio dynamics), book imbalance trajectory, market impact estimation.

### B-tier — Top-of-book BBO archive

- **Source:** `/tmp/bbo_log_v4.csv.gz`
- **Date range:** Mar 20 2026 to Apr 17 2026
- **Row count:** [TO BE POPULATED from tier-count CC probe; expected ~515M]
- **Match count (events with both sides):** [TO BE POPULATED]
- **Sampling rate:** Per-tick when book changes
- **Schema:** 5 columns. timestamp, ticker, bid, ask, spread.
- **Producer:** tennis_v5.py (legacy bot)
- **What it uniquely supports:** Larger N for cell aggregation than A-tier alone; full-period top-of-book trajectory analysis; binary "did price reach +X" questions; Channel 1 vs Channel 2 timing decomposition (with match-start derivable).
- **What it does NOT support:** Order book depth, capacity, microstructure beyond top-of-book.

### C-tier — Match summary table

- **Source:** `tennis.db.historical_events`
- **Date range:** Jan 2 2026 to Apr 10 2026
- **Row count:** 5,889 (with total_trades >= 10)
- **Match count by category:** [TO BE POPULATED from tier-count CC probe]
- **Schema:** 14 columns. event_ticker, category, winner, loser, first/min/max/last for both winner and loser sides, total_trades, first_ts, last_ts.
- **What it uniquely supports:** Pre-Mar-20 historical reach; existence proofs across the entire Jan 2 - Apr 10 window; volume proxy via total_trades.
- **What it does NOT support:** Any timing decomposition (only first and last timestamps for the entire match), order book depth, microstructure.

### Other operational data sources (schemas to inventory)

- `tennis.db.book_prices` (2.99M rows, Apr 19-29) — schema TO BE INVENTORIED
- `tennis.db.kalshi_price_snapshots` (274K rows, Apr 21-29) — schema TO BE INVENTORIED
- `tennis.db.live_scores` (4,729 rows) — schema TO BE INVENTORIED. Potentially game-state data.
- `tennis.db.bookmaker_odds` (32,471 rows) — schema TO BE INVENTORIED. Potentially sportsbook lines.
- `tennis.db.betexplorer_staging` (42,345 rows) — schema TO BE INVENTORIED.
- `tennis.db.dca_truth` (655 rows) — schema TO BE INVENTORIED.
- `tennis.db.edge_scores` (202 rows) — schema TO BE INVENTORIED.
- `analysis/trades/*.csv` (1,693 files, 180 MB, Apr 19+) — schema TO BE INVENTORIED. Per-ticker trade records.
- `analysis/handoff_*/` directories — prior analysis snapshots, individual files inventoried in ANALYSIS_LIBRARY.md.

### External sources (not currently pulled but accessible)

- Kalshi candlesticks API — historical OHLC per market per interval. Pulls pre-Mar-20 data not in local archives.
- Kalshi historical trades API — full trade history with aggressor side.
- Kalshi orderbook history — periodic depth snapshots.
- Sportsbook line history (DraftKings, Pinnacle, etc.) — sharp consensus over time.

---

## SECTION 2: ANALYSIS DEPTH LEVELS

Depth describes what class of question is being asked, not how complex the math is. Higher depth requires more variables and unlocks fundamentally new question classes. Analysis below the minimum-required depth for a question produces incomplete or misleading answers (see E25: the 70.7% rate is a depth-0 existence proof; treating it as edge validation overstates).

### Depth 0 — Existence

- **Question class:** Did X occur at all.
- **Minimum data:** One summary statistic per match per side.
- **Tier sufficient:** C.
- **Example:** "In 70.7% of 458 paired matches, did both sides briefly reach +10c above first-observed price." (April 14 paired analysis.)
- **Strict limits:** Says nothing about magnitude beyond the threshold tested, nothing about capturability, nothing about timing, nothing about per-cell distribution.

### Depth 1 — Distribution

- **Question class:** What is the distribution of X across matches.
- **Minimum data:** Aggregated summary statistics across many matches.
- **Tier sufficient:** C.
- **Example:** "What fraction of matches in cell X had max-bounce greater than +Yc, plotted across Y from 1 to 50."
- **Strict limits:** Says magnitude and frequency. Says nothing about timing or capturability.

### Depth 2 — Trajectory

- **Question class:** When during the match did X happen.
- **Minimum data:** Time series of bid/ask.
- **Tier sufficient:** B (top-of-book OK).
- **Example:** "Of matches that reached +10c, what fraction reached it before match start (Channel 1) vs after (Channel 2)."
- **Strict limits:** Says timing. Says nothing about whether the move was capturable in size.

### Depth 3 — Capacity

- **Question class:** Could a real order have filled at the price.
- **Minimum data:** Time series with order book depth and sizes.
- **Tier sufficient:** A (depth required).
- **Example:** "When the price spiked to +15c, was there at least 10 contracts of resting size at the target."
- **Strict limits:** Says capturability for our actual sizing. Says nothing about why the move happened.

### Depth 4 — Microstructure

- **Question class:** What is the structural property of the price/order behavior.
- **Minimum data:** A-tier plus modeling.
- **Tier sufficient:** A.
- **Example questions:** Realized volatility per cell. Autocorrelation of returns. Depth ratio dynamics. Iceberg detection. Effective vs realized spread. Greeks (delta, gamma, theta, vega) properly computed. Implied volatility surface. Kyle's lambda / market impact.
- **Strict limits:** Says regime properties. Says nothing about strategy P&L.

### Depth 5 — Strategy simulation

- **Question class:** What would realized P&L be if strategy X were deployed over period Y.
- **Minimum data:** Depth-3 plus bot's actual entry/exit logic, fees, slippage, capital constraints, order race conditions.
- **Tier sufficient:** A plus bot config.
- **Example:** "Replay of bot's actual entry/exit logic on Apr 18-29 tick data, with config Z, with fee model, computing realized P&L per cell."
- **Strict limits:** Says strategy validity for a specific config. Says nothing about external alpha sources or context dependencies.

### Depth 6 — Cross-sectional and temporal context

- **Question class:** How does edge depend on external variables.
- **Minimum data:** Depth-5 plus external data (sportsbook lines, surface, round, ranking, calendar).
- **Tier sufficient:** A plus external sources.
- **Example questions:** Does Kalshi lag DraftKings by N seconds and is that exploitable. Does our edge vary by tournament tier or surface. Cross-match correlation during tournament-level news events.
- **Strict limits:** Highest currently conceived. Future levels may emerge.

---

## SECTION 3: DEPTH × TIER MATRIX

Which depth questions are answerable from which tier. Not all combinations work — some depths require variables only present in higher tiers.

| Depth | C-tier | B-tier | A-tier |
|---|---|---|---|
| 0 — Existence | Yes | Yes | Yes |
| 1 — Distribution | Yes | Yes | Yes |
| 2 — Trajectory | Limited (only first_ts and last_ts) | Yes | Yes |
| 3 — Capacity | No | No | Yes |
| 4 — Microstructure | No | Partial (top-of-book vol only) | Yes |
| 5 — Strategy simulation | No | Limited (no fill simulation realism) | Yes |
| 6 — Cross-sectional context | No | No | Yes (with external data) |

[TO BE POPULATED with refinements after variable-inventory CC probe lands]

---

## SECTION 4: VARIABLE INVENTORY PER TIER (full column lists)

[TO BE POPULATED from variable-inventory CC probe. Will list every column in every source, with a one-line description of what each column represents and what depth questions it enables.]

---

## SECTION 5: CHANGELOG

- 2026-04-30: Initial scaffolding. Sections 1-3 partially populated from chat-derived knowledge; Sections 1 placeholders, Section 4 entirely TO BE POPULATED, await CC variable-inventory and tier-count probes.
