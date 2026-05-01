# U4 Phase 3 Design — Per-Moment State Vector Dataset

**Status:** DRAFT — pre-execution review. Operator must approve before any heavy compute.
**Date:** 2026-04-30 (Session 5).
**References:** ROADMAP U4 (PARTIALLY ANALYZED), G17, B14, F28, T13, U2, U3, U8.

---

## REFRAMING

Phase 1 and Phase 2 used per-match aggregates from `historical_events` — first/min/max/last across the entire match window. Two problems with this unit of analysis:

1. **Aggregates conflate windows.** Premarket and in-match are structurally different opportunities. A whole-match max collapses both. (B14 / G17.)
2. **Aggregates conflate moments.** Every variable in this domain is a flowing time series — price, spread, depth, volume, skew, implied probability. A bot decides at one moment, with the state observed at that moment, and either captures the next N minutes of forward movement or doesn't. The unit of analysis must match the unit of decision.

Phase 2's "1000+ trades = 76.4% bilateral capture" is a population mean across all matches that *eventually* hit 1000+ trades. At the moment the bot would have entered most of those matches, cumulative volume was much lower. The strata variable was the wrong column at the wrong time.

Phase 3 is therefore not a refinement of Phase 2's bucket boundaries. It is a redesign of the unit of analysis from per-match to per-moment.

---

## CORE QUESTION

For each observation moment in the dataset, given the state vector at that moment (price, volume-so-far, spread, depth, time-to-commence, etc.), what is the conditional probability of forward bilateral capture, forward unilateral bounce, and terminal settlement outcome?

Once the per-moment dataset exists, every strategic question becomes a stratification over it:
- Bilateral capture conditional on volume-at-decision-time, within premarket vs in-match (G17, the original B14 question).
- Right cell definition (U2).
- Channel 1 vs Channel 2 bounce decomposition (U3).
- Inverse-cell cross-check (U8).
- Future stress tests and simulations.

---

## DATASET SCHEMA

Each row = one (ticker, timestamp) observation. Two tickers per match (winner, loser sides). The "winner" / "loser" labels are assigned retrospectively from settlement; for the bot's perspective these are just two correlated tickers per match.

### State columns (observed at moment t)

- match_id (from historical_events, join key)
- ticker (from bbo_log, per-side identifier)
- timestamp (from bbo_log, normalize to ET per TAXONOMY)
- commence_time (from historical_events, match start)
- time_to_commence_sec (derived; negative = premarket, positive = in-match)
- window (derived; "premarket" / "in_match" categorical convenience)
- category (from historical_events; ATP_MAIN / ATP_CHALL / WTA_MAIN / WTA_CHALL)
- mid (from bbo_log; (bid + ask) / 2)
- bid, ask, spread (from bbo_log)
- bid_size, ask_size (top-of-book from bbo_log)
- depth_5_bid, depth_5_ask (A-tier only; null on B-tier rows)
- cum_trades_so_far (volume-at-decision-time; trade source TBD in Stage 0)
- mid_5min_ago, mid_30min_ago (rolling lookback from bbo_log)
- mid_change_5min, mid_change_30min (derived deltas)
- max_mid_so_far, min_mid_so_far (rolling within ticker)
- ticks_so_far (rolling bbo update count)
- paired_side_mid, paired_side_spread (joined from companion ticker at same moment with tolerance)

### Forward outcome columns (labels, observed forward from t)

- max_mid_next_5min, max_mid_next_30min, max_mid_next_2hr, max_mid_until_settlement
- min_mid_next_5min, min_mid_next_30min (for downside / stop-loss analysis)
- paired_max_mid_next_5min, paired_max_mid_next_30min (companion forward max)
- bilateral_5c_5min (bool: this side AND paired side rose +5c, both within 5min)
- bilateral_5c_30min, bilateral_10c_5min, bilateral_10c_30min, bilateral_10c_until_settlement
- terminal_winner (bool from settlement: did this side win)

### Computed once dataset exists, not stored

- Bilateral capture probability conditional on any subset of state columns.
- Channel 1 (premarket) vs Channel 2 (in-match) attribution by filtering on `window`.
- Per-cell metrics by binning mid into 5c bands and stratifying on category x side x volume-at-moment.

---

## SAMPLING CADENCE

The full bbo_log_v4 is 515M ticks over ~22 effective days. Sampling every tick is unnecessary and creates redundancy (consecutive ticks are highly correlated). Two sampling options:

(a) Time-based: one observation per ticker per 30-second wall-clock bucket, taking the latest tick in that bucket.
(b) Tick-based: one observation per ticker every Nth tick (e.g., every 50 ticks).

Recommendation: (a) time-based at 30s cadence. Reasons:
- Bot decisions are time-driven, not tick-driven. A 30s cadence approximates realistic decision frequency.
- Time-based cadence makes premarket vs in-match comparable: a quiet premarket and a busy in-match yield equivalent row counts per minute, so neither dominates by tick count.
- Forward-window labels (max_mid_next_5min etc.) have well-defined boundaries.

Cadence is configurable. Stage 0 probe will report row counts at 30s, 60s, 5min cadences so we can pick the resolution-vs-size trade-off.


---

## DATA SOURCES & COVERAGE LIMITS

- B-tier bbo_log_v4.csv.gz is the primary source. Covers Mar 20 - Apr 17 ET (~28 days). Top-of-book BBO only — no 5-deep depth. cum_trades_so_far requires a separate trade source.
- A-tier premarket_ticks for Apr 18+ has 5-deep depth columns; depth_5_bid / depth_5_ask are populated only here.
- historical_events Jan 2 - Apr 10 provides commence_time and category. Effective intersection with B-tier: Mar 20 - Apr 10 (~22 days).
- kalshi_fills_history.json (per A30) is Tier-A fact source for fill events but does not provide per-moment state — it is for joining bot fill outcomes, not for sampling.
- cum_trades_so_far source: TBD. Stage 0 must identify whether this comes from a trades table, JSONL trade events, or volume_24h time-series in kalshi_price_snapshots (Apr 21+ only per F26). If no source provides cumulative trade count over time per ticker for the Mar 20 - Apr 10 window, we either compute it from BBO ticks (one tick proxy) or drop volume-at-moment from Phase 3 v1 and add in v2.
- paired_side_mid requires joining each ticker observation against the companion ticker's most-recent observation at the same timestamp (within tolerance, e.g., 60s). This is the most expensive join in the pipeline.

---

## STREAMING PATTERN

T2 OOM'd at full 515M-row in-memory accumulation. Phase 3 must stream.

1. Load historical_events (~10K rows) into a {ticker -> match_metadata} dict. Bounded memory.
2. Open bbo_log_v4.csv.gz for streaming read (line-by-line or chunksize=1M).
3. For each ticker, maintain a rolling state object: last 30min of (timestamp, mid) for lookback features; max_mid_so_far, min_mid_so_far, ticks_so_far; last sample emission time (for 30s cadence gate).
4. On each tick: skip if ticker not in match dict; else update rolling state; if wall-clock advanced >= 30s since last emission for this ticker, emit a state-vector row to /tmp/u4_phase3_state.parquet (append, partitioned by date).
5. After full first pass, run a second pass to compute forward-window labels (max_mid_next_5min etc.) for each emitted row. This is a forward-lookup against the same per-ticker rolling state.
6. After second pass, run a third pass to join paired_side state. This is the most expensive step; needs careful design.

Memory ceiling for rolling state: O(num_tickers x ~30min of ticks per ticker x ~12 floats) ~ 10K x 200 x 12 bytes x 8 ~ 200MB. Safe.

Output ceiling: realistic ~10K matches x ~6 active hours x 120 samples/hour x 2 sides ~ 14M rows x ~30 columns. Parquet, ~500MB-1GB.

---

## EXECUTION PLAN

### Stage 0 — Pre-flight probes (read-only, ~5 min)
1. Confirm bbo_log_v4 schema (columns, depth presence, timestamp tz).
2. Identify cum_trades_so_far source. Candidates: trades table; JSONL trade events; kalshi_price_snapshots.volume_24h time-series (Apr 21+ caveat); BBO ticks as last-resort proxy.
3. Sample 5 random matches from Mar 20 - Apr 10 intersection. Verify both sides' tickers in bbo_log_v4. Verify commence_time vs first BBO tick relationship.
4. Report row counts at 30s / 60s / 5min cadences for one sample day to size the output.

### Stage 1 — First-pass streaming (heavy, est. 30-90 min)
Stream bbo_log_v4, emit state-vector rows at 30s cadence per ticker. Output: /tmp/u4_phase3_state_pass1.parquet.

### Stage 2 — Forward-label pass (heavy, est. 30-60 min)
Reverse-time pass to populate forward-window outcome columns. Output: /tmp/u4_phase3_state_pass2.parquet.

### Stage 3 — Paired-side join (heavy, est. 60+ min)
For each row, look up companion ticker state at same timestamp (with tolerance). Output: /tmp/u4_phase3_state.parquet (final).

### Stage 4 — Validation
Sanity-check against Phase 2. Filter the per-moment dataset to "first observation per ticker" and confirm bilateral_10c rate matches Phase 2's first_price-based number within tolerance. Differences here surface methodological issues before any new analysis runs.

### Stage 5 — Strategic queries (light)
Once dataset validated, every U4-related question becomes a stratification: G17 / B14 decomposition, U2 cell definition, U3 channel decomp, U8 inverse-cell. Each query is a single groupby on parquet.

---

## RISK ASSESSMENT

1. OOM (T2 precedent). Mitigation: streaming, bounded ticker dict, parquet append. No full-file dataframe.
2. cum_trades_so_far source missing. If Stage 0 confirms no per-ticker cumulative trade source for Mar 20 - Apr 10, v1 ships without it; v2 adds it once a source is identified.
3. Paired-side join performance. O(N) lookups against indexed companion-ticker dict. Measure on single-day subset before full pipeline.
4. Forward-window labels at match edges. Last 30 minutes of each match have truncated forward windows. Flag with `forward_window_truncated` rather than drop.
5. Tier mixing (B-tier vs A-tier). depth_5 columns null on B-tier. Strategy queries depending on depth_5 must filter to A-tier rows (Apr 18+).
6. Sampling cadence is a parameter. Retune after Stage 0 row count results.
7. F28 ephemerality. Outputs land on /tmp. Final parquet copy to /root/Omi-Workspace/arb-executor/data/ after validation.
8. Analysis-on-aggregate fallacy can recur. Any future user who groups by match and takes whole-match aggregates re-introduces the bug Phase 3 fixes. Document in deliverables.

---

## DELIVERABLES

1. /tmp/u4_phase3_state.parquet — per-moment dataset, ~14M rows x ~30 cols.
2. /tmp/u4_phase3_streaming_pass1.py — first-pass state extractor.
3. /tmp/u4_phase3_forward_labels_pass2.py — forward-window labeler.
4. /tmp/u4_phase3_paired_join_pass3.py — paired-side state joiner.
5. /tmp/u4_phase3_validation.py — Phase 2 reproducibility check.
6. /tmp/u4_phase3_strategic_queries.py — initial bilateral / cell / channel queries.
7. /tmp/u4_phase3_summary.txt — text summary with strategic conclusion.
8. ANALYSIS_LIBRARY entries (separate commit, post-execution).
9. ROADMAP U4 update: status -> "FULLY ANALYZED" with per-moment finding.
10. New ROADMAP G-item: "Future analyses must use per-moment dataset for any moving-variable strata; per-match aggregates only for terminal-state questions."

---

## OPEN QUESTIONS FOR OPERATOR

1. Cadence: 30s default. Operator wants finer (10s) or coarser (60s, 5min)?
2. Forward windows: 5min, 30min, 2hr, until_settlement. Add or remove any?
3. Bilateral threshold: +5c and +10c included. Add +15c, +20c?
4. Paired-side tolerance: companion ticker observation within 60s. Tighten (30s) or loosen (120s)?
5. Dataset destination after validation: /root/Omi-Workspace/arb-executor/data/ or elsewhere?
6. Pre-Mar-20 coverage: Phase 3 v1 covers Mar 20 - Apr 10 only (B-tier intersect historical_events). Pre-Mar-20 stays per-match. Acceptable for v1?

---

## NEXT STEPS

1. Operator reviews this design.
2. Push back on anything off.
3. If approved: send Stage 0 probes to CC.
4. After Stage 0 confirms: Stage 1 streaming pipeline.
5. Iterate Stages 2-5 as outputs land.
