# Layer B v1 specification — exit-policy parameter sweep

**Status:** SPEC (T31a). Implementation gated on this spec's closure (T31b).
**Foundation pointer:** T28 G9 parquets (commit ea84e74), sha256-pinned.
**Layer A v1 input:** cell_stats.parquet (T29 producer commit 1398c39, MANIFEST commit 37a5216, ANALYSIS_LIBRARY entry commit cf31903, T21 PASS verdict commit faf51d9).
**Per LESSONS B16:** Layer B is property of strategy given Layer A. No fees, no slippage, no fill-probability — those live in Layer C (G11). Layer B answers the strategy-side question: given the cell's forward-bounce distribution, which exit policy captures the most of it?

## Scope (v1)

In-match scalp exit policies on substantial cells (n_markets >= 20, 371 cells per Phase 1 finding). Two channels processed as separate sweeps per LESSONS E31:

- **Premarket channel.** Cell key: (category, regime=premarket, entry_band, spread_band, volume_intensity). 5-dimensional. ~258 substantial cells.
- **In-match channel.** Cell key from sample_manifest.json: (category, regime=in_match, entry_band, spread_band, volume_intensity). 5-dimensional. The sample_manifest was built by Layer A v1 (T29) before the F30 finding and uses 5-dim keys uniformly across all regimes. Layer B v1 retains the 5-dim key for invariant preservation: rebuilding sample_manifest with 4-dim in_match keys would require re-running the T29 producer (60 min) and producer-time fan-out aggregation introduces re-derivation drift. Per F30, volume_intensity is uninformative within in_match (117 substantial high cells, 3 substantial mid, 0 substantial low — collapses to single bucket). Layer B output records volume_intensity faithfully; downstream consumers (Layer C, strategy selection) collapse the dimension via filter at consumption time. ~117+3 = ~120 substantial in_match cells across volume_intensity buckets.

Out of scope for v1:

- **Settlement-zone exit policies.** Per T21 Check 3, settlement-zone exhibits structural directional asymmetry (high-entry pin, low-entry crash) that requires structurally different exit logic ("fold and let it settle" is a valid policy only at settlement_zone). Mixing settlement-zone with in-match scalping risks the same entanglement that broke prior cell-economics work. Settlement-zone Layer B is deferred to a v2 settlement variant. WTA settlement_zone also has zero substantial cells, compounding the scoping rationale.
- **Per-event paired exit policies** (e.g., "exit if inverse cell crosses threshold"). Requires per-event paired moments dataset (G12), which is parallel-deferred. Layer B v1 is single-leg.
- **Capital constraints.** Per B16, Layer B is strategy-side only; capital utilization tracked but does not constrain policy selection. Capital-constrained selection is a Layer C concern.
- **Resting-order queue position.** Layer B assumes instant fills at limit price. Queue-position fill probability is Layer C.
- **Scalar-outcome markets.** g9_metadata contains 496 markets (~2.5% of universe) where `result == "scalar"`. These are non-binary markets (set counts, total games, etc.) where settlement is a numeric value rather than YES/NO. Excluded from Layer B v1 scope; the bot's strategy is binary tennis match scalping. Layer B v2 may add a scalar variant if strategy expands.

## Operational decisions

### 1. Simulation methodology

**Decision: per-trajectory walk against g9_candles re-read by sampled ticker (Methodology A).**

Three methodologies considered:

- **Methodology A** (chosen): re-pull g9_candles per sampled ticker via sample_manifest.json. Reconstruct forward window minute-by-minute. Walk forward, fire policy on first trigger, record realized capture. Honest per-(cell, policy) capture distributions. Estimated cost: 30-60 min runtime. Comparable to T29 producer.
- **Methodology B** (rejected): synthetic trajectories sampled from cell_stats marginal distributions. Fast but loses correlation structure between bounce_X and drawdown_X within a moment (high-bounce moments correlate with low-drawdown; marginal sampling destroys this). Capture distributions would be close-but-not-honest. Layer B is the strategy gate; honesty matters more than speed.
- **Methodology C** (rejected): closed-form policy evaluation. Works for limit-only and time-stop-only. Trailing stops are path-dependent and combined policies have interaction effects; closed-form falls apart on the actually-interesting policies. Could compute simple cases for free but the producer would need A or B anyway, so consolidate to A.

Cell_stats.parquet remains the *summary* artifact (T21 validated its methodology). The trajectory access via sample_manifest.json + g9_candles is the per-event probe path the producer was always designed to enable.

### 2. Cell-minimum-sample-size threshold

**Decision: inherit n_markets >= 20 from T21 substantial-cell scope.**

Same threshold as T21 Phase 2 statistical analysis. 371 cells out of 671 total. Below this threshold, percentile estimates are unreliable per A31 / B17 work. Layer B inherits the threshold rather than introducing a new one; consistent with B16's "Layer B is property of strategy given Layer A" — Layer A's substantial-cell definition propagates forward.

A second threshold applies at the per-cell-trajectory level: each cell must have at least 50 simulated trajectories from sampled tickers with valid forward windows. If sample_manifest.json's cell entry yields fewer than 50 trajectory-windows after filtering for valid candle data, the cell is excluded from the v1 sweep and flagged in the producer log. This handles the case where a "substantial" cell has 25 markets but only 8 of them have minute-by-minute candle data dense enough to walk forward through the relevant horizons.

### 3. Source columns from g9_candles

**Decision: yes_ask_close (entry-side fill assumption) and yes_bid_close (exit-side fill assumption) only.**

For a long-YES position entered at moment t:
- Entry assumed at yes_ask_close[t] (cross the spread to enter).
- Exit at yes_bid_close[t+k] when policy fires at horizon k (cross the spread to exit).

This is the conservative-fill assumption (always cross the spread). Layer C will refine to maker-fill probability and queue position.

For limit-exit policies, the policy fires at the first minute k where yes_bid_close[t+k] >= entry_price + limit_threshold. Captured = yes_bid_close[t+k_fire] - yes_ask_close[t].

For trailing-stop policies, the policy maintains a running max of yes_bid_close from t forward and fires at the first minute where yes_bid_close drops below (running_max - trail_offset).

For time-stop policies, the policy fires at horizon T regardless of price; capture = yes_bid_close[t+T] - yes_ask_close[t].

For combined policies (limit + time-stop), whichever triggers first.

Trade-tape (g9_trades) not used in v1. Candle-level resolution is the simulation grain; sub-minute fills are a Layer C concern.

### 4. Policy parameter space

**Decision: hierarchical sweep with explicit cap on combinatorial explosion.**

Single-policy types:
- **Limit-exit:** thresholds {1, 2, 3, 5, 7, 10, 15, 20, 30} cents above entry. 9 policies.
- **Time-stop:** horizons {30s, 1min, 5min, 15min, 30min, 60min, 120min, 240min, settle}. 9 policies.
- **Trailing-stop:** offsets {1, 2, 3, 5, 7, 10, 15, 20} cents below running max. 8 policies.

Combined policy types:
- **Limit + time-stop:** Cartesian product, but pruned to dominant cells (e.g., +1c limit with 240min stop is not strategy-meaningful since hitting +1c is trivial). Subset: thresholds {3, 5, 10, 15, 20} × horizons {15min, 30min, 60min, 120min}. 20 combined policies.
- **Limit + trailing:** {5, 10, 15} × {3, 5, 10}. 9 combined policies.

Total policies per cell: 9 + 9 + 8 + 20 + 9 = 55. Across 375 substantial cells (premarket + in-match): ~20,625 (cell, policy) tuples per channel sweep. Output schema is one row per tuple.

If actual parameter coverage is undershoot (operator wants finer 1c-step granularity on limit-exit), v2 expands the parameter space. v1 captures the strategy-relevant grid.

### 5. Policy non-fire handling

**Decision: explicit "settled_unfired" and "horizon_expired" buckets in capture distribution.**

For each (cell, policy) tuple, simulated trajectories fall into three outcomes:
- **Fired-and-captured:** policy triggered at minute k_fire; realized capture = yes_bid_close[t+k_fire] - yes_ask_close[t]. Capture can be negative (limit hit on a downward swing for trailing-stop policies).
- **Horizon-expired:** policy was a time-stop at horizon T but trajectory has only k < T minutes of forward window. Outcome = "horizon_expired"; capture computed at the actual final minute available. For trailing-stop and limit-exit, "horizon-expired" applies if the trajectory ran out of forward window before the policy fired.
- **Settled-unfired:** market settled before the forward window completed; policy never fired. Outcome = "settled_unfired"; realized capture = settlement_value - yes_ask_close[t] where settlement_value resolves from g9_metadata.parquet's `result` column: "yes" → 1.00, "no" → 0.00. Markets where `result == "scalar"` (496 of 20,110 total per disk probe; 2.5% of universe) are **excluded from Layer B v1 scope** because scalar settlement is not binary YES/NO and requires different exit-policy dynamics. The producer must verify result is in {"yes", "no"} per ticker before processing trajectories from that ticker; skipped scalar tickers are counted and reported in the producer log. Layer B v2 may add a scalar-markets variant if strategy expands to non-binary markets.

The capture distribution for each (cell, policy) is computed across all three outcome types — settled-unfired observations contribute their settlement-resolved capture, not a null.

Output schema records, per (cell, policy):
- n_simulated, n_fired, n_horizon_expired, n_settled_unfired (counts)
- capture_mean, capture_p10, capture_p25, capture_p50, capture_p75, capture_p90 (across all outcomes)
- fire_rate (n_fired / n_simulated)
- median_time_to_fire (for fired observations only)

## Output schema

**File:** `arb-executor/data/durable/layer_b_v1/exit_policy_per_cell.parquet`

**Columns:**

| Column | Type | Description |
|---|---|---|
| channel | string | "premarket" or "in_match" |
| category | string | ATP_MAIN / ATP_CHALL / WTA_MAIN / WTA_CHALL / OTHER |
| entry_band_lo | int | Cell entry-band lower bound (cents) |
| entry_band_hi | int | Cell entry-band upper bound (cents) |
| spread_band | string | tight / medium / wide |
| volume_intensity | string | low / mid / high (premarket only; null for in_match) |
| policy_type | string | limit / time_stop / trailing / limit_time_stop / limit_trailing |
| policy_params | string | JSON-serialized parameter dict, e.g., `{"limit": 5}` or `{"limit": 10, "time_stop": 60}` |
| n_simulated | int | Number of trajectories simulated for this (cell, policy) |
| n_fired | int | Number of trajectories where policy triggered |
| n_horizon_expired | int | Number where forward window ran out before policy fired |
| n_settled_unfired | int | Number where market settled before policy fired |
| fire_rate | float | n_fired / n_simulated |
| capture_mean | float | Mean realized capture across all outcomes (cents) |
| capture_p10 | float | 10th percentile capture |
| capture_p25 | float | 25th percentile capture |
| capture_p50 | float | Median capture |
| capture_p75 | float | 75th percentile capture |
| capture_p90 | float | 90th percentile capture |
| median_time_to_fire | float | Median minutes from entry to fire (fired observations only); null if n_fired = 0 |
| capital_utilization | float | Mean fraction of horizon during which position was held |

Plus paired summary visuals at `arb-executor/data/durable/layer_b_v1/visual_*.png` analogous to T29's per-(channel, category) plots: heatmap of best (per cell) policy by capture_mean, policy-type-comparison plots, time-to-fire distributions.

## Producer architecture

`arb-executor/data/scripts/build_layer_b_v1.py`. Flow:

1. Load cell_stats.parquet and sample_manifest.json. Filter to substantial cells (n_markets >= 20). Split by channel.
   - **Cell-key parsing:** sample_manifest.json keys use the format `{regime}__{entry_band_idx}__{spread_band}__{volume_intensity}__{category}` where entry_band_idx is the integer index 0-9 into the ENTRY_BANDS constant from cell_key_helpers. Producer parses each key by splitting on `__`, then maps `entry_band_idx` to `(entry_band_lo, entry_band_hi)` via `ENTRY_BANDS[idx]` for output schema columns. The cell-key parsing logic must use the same ENTRY_BANDS constant from cell_key_helpers as Layer A used at aggregation time (refactored to shared module per commit 8174ec0).
2. For each cell:
   - Read sampled tickers from sample_manifest.json.
   - For each sampled ticker, first verify g9_metadata.parquet `result` column is in {"yes", "no"}; skip ticker (count in producer log) if "scalar". Then re-pull g9_candles row-group(s) for that ticker (column-projection: ticker, end_period_ts, yes_bid_close, yes_ask_close, volume_fp; per C28 streaming discipline). Filter pushdown is efficient because g9_candles row groups are ticker-sorted (probe confirmed disjoint ticker ranges per row group).
   - For each moment in cell (entry_band match), construct forward window of yes_bid_close / yes_ask_close from t through min(t + 240min, settlement).
   - For each policy in the parameter grid, walk the forward window, determine outcome (fired / horizon_expired / settled_unfired), record realized capture.
3. Per (cell, policy), aggregate capture distribution and write row to exit_policy_per_cell.parquet.
4. Generate visual PNGs.
5. Producer log to arb-executor/data/durable/layer_b_v1/build_layer_b_v1.log.

Memory discipline per LESSONS C28 / F13: stream g9_candles with row-group column projection. Do not materialize full g9_candles in memory. Per-cell trajectory cache cleared after cell processing.

## Validation gate (T31c, post-implementation)

Layer B v1 outputs require coherence read before consumption by Layer C. The four checks:

1. **Capture distributions are bounded by physical limits.** For a +5c limit policy, capture_p90 should not exceed +5c (modulo ±1c for the bid-cross at exit). Capture_p10 should be ≥ -100c (basic sanity).
2. **Fire rates trend with policy aggressiveness.** Tighter limits (1c) should fire more often than wider limits (20c). Monotonic check across the limit-policy grid.
3. **Time-stop policies at long horizons capture more than at short horizons** in cells with positive-mean bounce. Sanity check that horizon dimension is doing something.
4. **Premarket vs in-match capture distributions differ at matched (category, entry_band, spread, policy)** in the direction T21 Check 2 predicted (in_match > premarket). Cross-validation that Layer B inherits Layer A's regime distinction faithfully.

PASS verdict required before promoting Layer C (G11) to T-item.

## Foundation pointers

- **T28 ea84e74** — G9 parquets (sha256 in MANIFEST.md)
- **T29 1398c39** — Layer A v1 producer
- **T29 37a5216** — Layer A v1 MANIFEST sha256
- **T29 cf31903** — Layer A v1 ANALYSIS_LIBRARY entry
- **T21 faf51d9** — Layer A v1 coherence read PASS

## Open items for v2

- Settlement-zone Layer B variant (per scope-out above).
- Per-event paired exit policies via G12 producer.
- Sub-minute trade-tape resolution for fill-time precision.
- Per-moment volume rate as cell-key dimension (replacing volume_intensity per F30).

