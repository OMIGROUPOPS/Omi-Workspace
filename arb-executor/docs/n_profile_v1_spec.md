# N Profile v1 Spec — Per-N Measurement Universe Rollup

**Status:** v0.1 — initial draft 2026-05-16 ET. Operator-flagged as foundational gap: Rung 0's T-20m strategy-anchored summary is NOT the per-N measurement universe; per_minute_features.parquet (per-N-minute) is the granular foundation but no canonical per-N rollup exists. This spec defines that rollup.

**Anchored to:**
- LESSONS A22 (measurement universe: volume, trade flow, order book dynamics, paired-cell lead-lag, calendar context, microstructure — not bid/ask/mid)
- LESSONS A24 (enumerate variable inventory per tier as analysis foundation)
- LESSONS B15 (every variable is a flowing time series; unit of analysis matches unit of decision)
- LESSONS B16 (Layer A/B/C separation; this is the per-N rollup layer)
- LESSONS G22 (N is the player-binary market / unit-of-observation; one row per N)
- LESSONS C36 (trade tape is canonical for trade activity)
- LESSONS C37 (pre-replace validation gate against on-disk bytes)
- LESSONS G18, G19, F29 (candle semantics, sparse populations, era-based schema drift)
- LESSONS B23 / B24 (paired-event structure; partner-N stats are load-bearing for bilateral)
- LESSONS F31 (OI partially tracked, candle column + trade-tape per-side reconstruction)
- LESSONS A26 (taker_side underused; A35 confirms 100% populated)
- LESSONS A35 (volume-per-minute match-start anchor)
- TAXONOMY G-tier (g9 corpus schema)
- per_minute_universe_spec.md (the granular foundation this rollup reads from)

**Output:** `data/durable/n_profile_v1/n_profile.parquet`

---

## 1. Scope

n_profile_v1 produces a per-N corpus-wide rollup: one row per N in the binary-outcome subset, covering its full lifetime measurement universe at per-N grain (not per-N-minute, not at strategy-anchor timestamps).

The artifact answers: **"for any N in the corpus, what's its activity / volume / liquidity / paired-partner profile, all in one row?"**

This is the foundation that downstream work — Rung 0 (T-20m strategy primitive), Rung 1 (per-cell threshold sweep), Rung 2 (bilateral capture), deployment N-selection — should read from for any per-N context or stratification. The rungs were built before this layer existed; they are valid but operate on an incomplete foundation. Post-landing, downstream specs reference n_profile_v1 for per-N context columns (volume tier, paired-partner deployability, etc.) and Rung 1 / Rung 2 should add stratification on n_profile_v1's metrics.

### 1.1 In scope

- One row per N in the binary-outcome subset (~19,614 candidate N's; final count post-dropouts logged in validation_report).
- Identity / pairing columns (ticker, event_ticker, paired_event_partner_ticker, category, settlement value).
- Lifetime activity (first/last trade timestamps, premarket vs in-match split by minute count and volume).
- Volume profile (total volume, premarket volume, in-match volume, peak-volume minute and value).
- Trade-count profile (total trades, by phase, mean trades per active minute).
- Taker-side flow (yes-taker-volume, no-taker-volume, imbalance — per A26 / G19).
- OI trajectory (OI at match_start, at T-20m, max OI and minute, premarket OI growth rate).
- Price activity (first/last trade prices, min/max price pre-settlement, realized vol premarket / in-match).
- Partner-N stats joined alongside (the bilateral hook): partner's total volume, premarket volume, in-match volume, trade count, both-sides-active minute count.
- Sample-quality flags (has complete trade tape, has complete candle tape, tier, match-start signal method).

### 1.2 Out of scope

- Per-N-minute time series (that's per_minute_features.parquet — n_profile_v1 is the per-N rollup, not the granular).
- Greeks (delta/gamma/theta/vega proxies per A22 — computable but bigger producer scope; v2 candidate).
- Market impact and effective-spread microstructure (per A22 — A-tier-overlap dependent, post-Apr-18 only; v2).
- Order book depth at non-BBO (F33 blocked-track; not in g9; G13 collection gap).
- Paired-event joint moment series (G12 separate track; n_profile_v1 emits per-N rollups with partner_* columns alongside, not paired joint-moment rows).
- ESPN game-state join (deferred to v2 + ESPN integration work).

### 1.3 Relationship to existing artifacts

- **per_minute_features.parquet (T37, 9.33M rows, 88 cols):** granular per-(N, minute) foundation. n_profile_v1 reads from it for premarket / in-match phase splits and per-minute aggregations.
- **g9_trades.parquet (33.7M rows):** canonical trade tape per C36. n_profile_v1 reads from it for trade counts, volume, taker-side flow.
- **g9_candles.parquet (9.5M rows):** per-minute BBO + volume + OI. n_profile_v1 reads from it for OI trajectory (candle column is direct read per F31).
- **g9_metadata.parquet (20,110 rows):** per-N static metadata. n_profile_v1 reads from it for settlement value, market_open_ts, category derivation.
- **cell_economics.parquet (Rung 0, 14,033 rows):** T-20m strategy-anchored summary. NOT a foundation — n_profile_v1 is upstream of Rung 0 conceptually. Rung 0 can be joined to n_profile_v1 by ticker for cell-context-with-volume reads.

---

## 2. Schema

One row per N. Estimated row count: ~19,614 (binary-outcome subset of g9_metadata; actual emitted count depends on data-completeness dropouts measured in Phase 1 probe).

### 2.1 Column families and definitions

**Identity / pairing (7 columns):**
| # | Column | Type | Description |
|---|---|---|---|
| 1 | `ticker` | string | The N's Kalshi ticker |
| 2 | `event_ticker` | string | Paired event (= ticker.rsplit('-', 1)[0]) |
| 3 | `paired_event_partner_ticker` | string | Partner N's ticker (the other player's binary on the same match) |
| 4 | `category` | string | WTA_MAIN / WTA_CHALL / ATP_MAIN / ATP_CHALL |
| 5 | `match_start_ts` | ts ET | Inferred per per_minute_universe_spec match-start signal hierarchy |
| 6 | `settlement_ts` | ts ET | Settlement |
| 7 | `settlement_value_dollars` | float | 0.0 or 1.0 (scalars excluded — same filter as Rung 0) |

**Lifetime timing (4 columns):**
| 8 | `market_open_ts` | ts ET | When the N's market opened |
| 9 | `first_trade_ts` | ts ET or null | Microsecond timestamp of N's first trade (any size) |
| 10 | `last_trade_ts_pre_resolution` | ts ET or null | Last trade before first_extreme_touch_ts (per Rung 0 col 27 semantics) |
| 11 | `lifetime_minutes` | int | Total minutes from market_open_ts to settlement_ts |

**Premarket vs in-match phase counts (4 columns):**
| 12 | `n_minutes_premarket` | int | Minutes from market_open_ts to match_start_ts |
| 13 | `n_minutes_in_match` | int | Minutes from match_start_ts to settlement_ts |
| 14 | `n_active_minutes_premarket` | int | Minutes in premarket with at least one trade (count_fp > 0) |
| 15 | `n_active_minutes_in_match` | int | Minutes in_match with at least one trade |

**Volume profile (6 columns; source = g9_trades per C36):**
| 16 | `total_volume_lifetime` | int64 | Sum of count_fp across all trades on this N (premarket + in_match) |
| 17 | `total_volume_premarket` | int64 | Sum of count_fp for trades where created_time < match_start_ts |
| 18 | `total_volume_in_match` | int64 | Sum of count_fp for trades where created_time >= match_start_ts |
| 19 | `peak_volume_minute_ts` | ts ET or null | Minute with the highest single-minute volume (premarket + in_match combined) |
| 20 | `peak_volume_in_that_minute` | int64 | The peak-minute's volume |
| 21 | `mean_volume_per_active_minute` | float | total_volume_lifetime / (n_active_minutes_premarket + n_active_minutes_in_match) |

**Trade-count profile (4 columns; source = g9_trades count, filter count_fp > 0 per C36):**
| 22 | `total_trade_count_lifetime` | int | Count of trades with count_fp > 0 across N's life |
| 23 | `total_trade_count_premarket` | int | Same, premarket only |
| 24 | `total_trade_count_in_match` | int | Same, in_match only |
| 25 | `mean_trades_per_active_minute` | float | total_trade_count_lifetime / (active_minutes_premarket + active_minutes_in_match) |

**Taker-side flow (3 columns; per A26 / F31):**
| 26 | `yes_taker_volume_cum` | int64 | Sum of count_fp where taker_side = 'yes' (lifetime) |
| 27 | `no_taker_volume_cum` | int64 | Sum of count_fp where taker_side = 'no' (lifetime) |
| 28 | `yes_taker_imbalance` | float | (yes_taker_volume_cum - no_taker_volume_cum) / total_volume_lifetime; null if total_volume = 0 |

**OI trajectory (4 columns; per F31; source = g9_candles.open_interest_fp):**
| 29 | `oi_at_match_start` | int or null | OI from the candle minute containing match_start_ts |
| 30 | `oi_at_t20m` | int or null | OI from the candle minute at T-20m (consistency join with Rung 0 col 31) |
| 31 | `oi_max_lifetime` | int or null | Max OI observed across N's life |
| 32 | `oi_max_minute_ts` | ts ET or null | Timestamp of oi_max_lifetime |

**Price activity (4 columns; source = g9_trades for first/last/min/max):**
| 33 | `price_first_trade` | float or null | First observed trade price (yes_price_dollars) |
| 34 | `price_last_trade_pre_resolution` | float or null | Last trade price before first_extreme_touch_ts |
| 35 | `price_min_pre_resolution` | float or null | Min trade price before first_extreme_touch_ts |
| 36 | `price_max_pre_resolution` | float or null | Max trade price before first_extreme_touch_ts |

**Partner-N stats joined (4 columns; the bilateral hook — joined by paired_event_partner_ticker):**
| 37 | `partner_total_volume_lifetime` | int64 | Partner N's total_volume_lifetime |
| 38 | `partner_total_trade_count_lifetime` | int | Partner N's total trade count |
| 39 | `partner_total_volume_premarket` | int64 | Partner N's premarket volume |
| 40 | `both_sides_active_minutes` | int | Count of minutes where BOTH this N AND partner N had at least one trade |

**Sample-quality flags (3 columns):**
| 41 | `has_complete_trade_tape` | bool | True if g9_trades has rows for this ticker (some historical-tier may not) |
| 42 | `has_complete_candle_tape` | bool | True if g9_candles has rows for this ticker |
| 43 | `tier` | string | "historical" / "live" per the Mar 2 2026 cutoff |

**44 columns total.** Single row per N. Estimated emitted row count post-dropouts: ~17,000-19,000 (final number determined by Phase 1 probe; dropouts include missing trade tape, missing match_start_ts inference, partner-ticker resolution failures).

---

## 3. Producer architecture

### 3.1 Input artifacts (read-only)

- `data/durable/g9_trades.parquet` — canonical trade tape (per C36)
- `data/durable/g9_candles.parquet` — per-minute BBO + volume + OI
- `data/durable/g9_metadata.parquet` — per-N static metadata
- `data/durable/per_minute_universe/per_minute_features.parquet` — for premarket/in-match phase boundaries via match_start_ts column

All read-only.

### 3.2 Pipeline

1. Load g9_metadata. Filter to binary-outcome subset (settlement_value ∈ {0.0, 1.0}; scalars excluded per Rung 0).
2. Load per_minute_features (subset of columns: ticker, minute_ts, match_start_ts derived per row, trade_count_in_minute, volume_in_minute). Read by row groups for memory discipline per C28.
3. For each ticker in the binary-outcome subset:
   - Look up match_start_ts (per_minute_universe_spec hierarchy)
   - Load g9_trades for this ticker (single ticker, streaming acceptable)
   - Compute trade-tape aggregates (volume / count / taker-side / price min/max/first/last) split by premarket vs in_match phase
   - Load g9_candles for this ticker, compute OI trajectory aggregates
   - Compute per-minute aggregates from per_minute_features for active-minute counts
   - Emit one row with all 43 columns (partner stats column-44 / both_sides_active filled in pass 2)
4. Pass 2: for each row, look up partner_event_partner_ticker, join partner's stats columns from pass-1 output.
5. Pass 3: compute both_sides_active_minutes by per-minute join on (ticker, minute_ts) for paired rows where both N's have count_fp > 0 in the same minute.

Single-pass-per-ticker discipline per C28 streaming pattern. Memory budget: per-ticker work is small (single ticker has at most ~720 minutes of candles + ~thousands of trades).

### 3.3 Phased rollout

- **Phase 1:** 50 stratified tickers (10 per category × 5 categories minus 1, plus 5 from the long-volume-tail and 5 from the short-volume-tail). <5 min runtime budget. Visual inspection. Validates schema correctness on heterogeneous data.
- **Phase 2:** 1000 tickers stratified by category × tier (historical vs live). <30 min budget. Validates partner-join correctness and runtime scales linearly.
- **Phase 3:** Full binary-outcome subset (~19,614 tickers). Estimated runtime: per-ticker walk is ~10-50ms, total ~5-15 min single-threaded. Kill-resilient incremental writes per T37 pattern.

### 3.4 Output

- `data/durable/n_profile_v1/n_profile.parquet`
- `data/durable/n_profile_v1/validation_report.md`
- `data/durable/n_profile_v1/n_profile.meta.json` (sha256 sidecar)

C37 discipline: write to `.new`, reload-from-disk, gate-validate, `os.replace` only on all-pass.

---

## 4. Validation gates

### 4.1 Hard gates

1. **Row count parity.** Emitted row count = unique tickers in binary-outcome subset of g9_metadata minus measured dropouts. Dropouts must be enumerated by reason and totaled exactly.
2. **Partner-ticker resolution.** For every emitted row where partner_total_volume_lifetime is non-null, the partner ticker must also be an emitted row. Bilateral joins must close (or be explicitly logged as orphan).
3. **Phase consistency.** For every row, n_minutes_premarket + n_minutes_in_match = lifetime_minutes (within 1-minute rounding tolerance). Zero violations.
4. **Volume conservation.** total_volume_lifetime = total_volume_premarket + total_volume_in_match exactly per row.
5. **Taker-side conservation.** yes_taker_volume_cum + no_taker_volume_cum = total_volume_lifetime exactly per row (per G19 100%-populated taker_side).
6. **OI monotonicity sanity.** oi_max_lifetime >= oi_at_match_start (if both non-null) and >= oi_at_t20m (if both non-null).
7. **TZ correctness.** Every timestamp column is timezone-aware ET. Zero naive timestamps per G21.

### 4.2 Informative measurements (logged, not blocking)

- Distribution of total_volume_lifetime (median, p25/p75/p90/p99/max). Reveals the volume-tail structure.
- Both-sides-active minute count distribution. Reveals bilateral feasibility floor.
- Per-tier counts and dropout breakdown.
- yes_taker_imbalance distribution (centered? skewed?).
- Partner-volume-pairing ratio distribution: this_N_volume / partner_N_volume, log-scale. Reveals symmetric vs asymmetric paired liquidity.

---

## 5. Headline rankings emitted in validation_report.md

The producer emits the parquet AND a markdown report with operator-readable summaries:

### 5.1 Top-100 N's by total_volume_lifetime
Surface ticker, category, premarket vs in-match volume split, partner volume, peak-minute timing.

### 5.2 Top-100 paired matches by combined-side total_volume
event_ticker, both sides' tickers, combined volume, volume balance ratio.

### 5.3 Distribution summaries
Per category: volume distribution, trade-count distribution, both-sides-active minutes distribution.

### 5.4 Volume tier candidate cut points
Quartile boundaries for total_volume_lifetime per category. Forward input for Rung 1.5 / Rung 2 volume-stratified analyses.

### 5.5 Paired bilateral feasibility floor
Fraction of paired matches where both N's have total_volume_premarket > {50, 100, 500, 1000} cts. The bilateral mechanism (B23) needs both sides tradeable; this gates which matches are bilateral-deployable.

---

## 6. Cross-references

- Foundation: per_minute_universe_spec.md (T37); per_minute_features.parquet sha256 9fde4b5d…; g9_trades.parquet, g9_candles.parquet, g9_metadata.parquet (T28 sha256-pinned at ea84e74).
- Measurement-universe doctrine: A22, A24, B15, B16.
- Per-N unit semantics: G22.
- Pairing semantics: B19, B23, B24, F13, G12 (paired joint-moment dataset — separate track).
- Trade-tape canonicality: C36, A26, G19 (100% taker_side populated).
- OI from candle column: F31 (corrected; OI is direct-read, not reconstructed).
- TZ discipline: G21.
- C37 pre-replace gate.
- ROADMAP: this artifact gets a new T-item (T40 candidate). The recomputation_ladder positioning is OPEN — n_profile_v1 is upstream of Rung 0 conceptually but Rung 0 was built first; ladder amendment is a follow-up commit not in scope here.

---

## 7. Resolution log (v0.1 — 2026-05-16)

| # | Question | v0.1 Resolution | Source |
|---|---|---|---|
| 1 | Per-N grain or per-N-minute? | Per-N rollup (one row per N). Per-N-minute is per_minute_features.parquet. | Spec scope; B16 layer separation |
| 2 | Include Greeks / market impact in v1? | Deferred to v2. v1 ships clean of derivative metrics that need A-tier overlap or path-volatility. | A22 framing; v1 = lean rollup |
| 3 | Partner stats: joined or separate dataset? | Joined columns alongside (4 partner_* columns). Paired joint-moment series is G12 separate track. | Operator usability; G12 is per-moment not per-N |
| 4 | Volume source for activity counts | Trade tape (g9_trades count_fp > 0) per C36 canonical, NOT candle volume_fp (65% null per G19 / F29). | C36 |
| 5 | OI source | g9_candles.open_interest_fp direct read; trade-tape per-side flow as supplementary columns 26-28. | F31 amendment |
| 6 | Match-start signal | Reuse per_minute_universe_spec 4-tier hierarchy from per_minute_features.parquet. | A35; T37 |
| 7 | Tier discrimination | Add `tier` column ("historical" / "live") for downstream filtering per F29 era-based behavior. | F29 |
| 8 | Phase boundary handling | match_start_ts column on per_minute_features is authoritative; phase splits computed via timestamp comparison. | per_minute_universe_spec |

End of n_profile_v1 spec v0.1.
