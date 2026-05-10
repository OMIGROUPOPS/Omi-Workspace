# Layer B v2 specification — tick-level fill semantics on the full non-settle premarket corpus

**Status:** SPEC (T36a). Implementation gated on this spec's closure (T36b producer build + T36c coherence read).

**Foundation pointers:**
- **T28 G9 parquets** (commit `ea84e74`, sha256-pinned per MANIFEST.md). `g9_trades.parquet` is the tick-level taker-fill source; `g9_candles.parquet` is the per-minute bid/ask source; `g9_metadata.parquet` is the settlement source.
- **Layer A v1** `sample_manifest.json` (T29 producer commit `1398c39`, MANIFEST commit `37a5216`, ANALYSIS_LIBRARY entry commit `cf31903`, T21 PASS verdict commit `faf51d9`). Per-cell sampled tickers.
- **Layer B v1** `exit_policy_per_cell.parquet` (T31b producer commit `28e8ab7`, T31c PASS verdict commit `2654a54`). Defines the (cell, policy) tuple universe that v2 re-evaluates; v2 supersedes v1's `capture_mean` for the non-settle premarket subset as the canonical cell-ranking truth.
- **Forensic replay v1** `phase3/candidate_summary.parquet` (Phase 3 corrected outputs commit `73de3a6`, producer commit `a058212` with taker_side convention fix, spec Section 10 verdict commit `827fc22`). The 80-candidate tick-level realized truth that v2 must reproduce on the same candidates within calibration tolerance.

**Per LESSONS B16 + B25:** Layer B is property of strategy given Layer A's cell aggregates. v1's `walk_trajectory` realized strategy-side capture distributions using minute-cadence candle reads as the fill-detection grain. **B25 (commit `033fb8a`) named the structural defect:** in `capture_mean ≈ fire_rate × capture_per_fired`, the `capture_per_fired` term is correct under v1 (limit policies fire at exactly +limit_c when they fire), but the `fire_rate` term systematically undercounts because between consecutive minute candles the bid can spike to threshold and back without trace in the minute close. **Layer B v2 folds forensic replay v1's tick-level fill mechanism (commit `73de3a6`, ANALYSIS_LIBRARY Cat 11) back into the simulator at the source.** Per B16 layered-realism discipline, v2 adds exactly one concept relative to v1: tick-level fill semantics. Fees remain Layer C's concern (T32, demoted by Cat 11 / B25 — layered on top of v2 outputs once T36c PASSes). Capital constraints, queue position, in-match channel, settle-horizon time_stops all remain deferred per the v3 scoping at Section 8.

**Per Cat 11 (commit `4e36f30`):** Forensic replay v1 Phase 3 corrected measured Spearman ρ=0.136 between v1 simulated and tick-level realized capture across the 80 top-N candidates; 76.2% of candidates have realized > simulated; limit policies (n=39, 49% of evaluated corpus) realize +$0.072/+$0.081 over simulated (2.4× understatement on the dominant policy class). v2's empirical mandate is to reproduce the tick-level realized distribution within ±$0.01 at the calibration anchor (ATP_MAIN 50-60 tight low / limit_c=30, $0.2610/moment, n=2914) and to generalize the methodology from the 80 hand-picked top-N candidates to the full non-settle premarket (cell, policy) universe.

---

## 1. Scope (v2)

**Per-(cell, policy) tick-level realized capture across the full non-settle premarket corpus.**

In-scope:
- **Premarket channel only.** Inherits forensic replay v1 Section 1 disposition: premarket has the highest top-tail EV per Cat 5 frame 3, no gap-risk to model, and the simpler entry-state evolution (minute-cadence premarket vs point-by-point in-match). v1's `replay_capture_B_net_mean` is empirically validated against tick reality on the 80 evaluated candidates per Cat 11; v2 generalizes the methodology, not the channel.
- **Non-settle policies.** All Layer B v1 policy types except `time_stop horizon == "settle"` and `limit_time_stop horizon == "settle"`. Per spec Section 3.2 of forensic_replay_v1, settle-horizon time_stops collapse Scenarios A and B by construction and require a settlement-zone-aware replay variant (forensic replay v2 deliverable). Layer B v2 inherits forensic replay v1's exclusion — settle-horizon policies are scoped out at the producer level, not silently passed through.
- **Substantial cells only.** Inherits Layer B v1's substantial-cell threshold (n_markets ≥ 20 from T21) and 50-trajectory secondary threshold per cell. Producer logs the cell-population breakdown; cells below threshold are excluded with a producer-log entry, not silently dropped.

Out of scope for v2:
- **In-match channel.** Deferred to v3 (forensic replay v2 + Layer B v3 joint deliverable). Same gap-risk haircut concern as forensic replay v1 Section 1 — between consecutive in-match ticks the score may have changed and the cell at fill may differ from the cell at posting in ways unreconstructable from price alone. v2 stays premarket-only, mirroring forensic replay v1.
- **Settle-horizon time_stop policies.** Deferred to forensic replay v2 settle-horizon variant. Cat 5's predicted top cell (WTA_MAIN 40-50 tight low / time_stop "settle", $0.509 simulated) remains forensic-replay-unvalidated and is the highest-impact open gap; v2 does not pretend to evaluate it.
- **Settlement-zone cells.** Inherits Layer B v1 spec scope-out (T21 Check 3 structural directional asymmetry). Separate v2-of-Layer-B-settlement-zone-spec, not in this v2.
- **Fees integration.** T32 / Layer C v1 scope. v2 outputs `capture_*_gross_dollars` only; fees layer on at consumption time. Per Cat 2 fee table, fees are a 1-2¢ correction that does not affect v2's structural validation (B25 mechanism fix dominates).
- **Capital constraints / portfolio sizing.** Layer D scope per LESSONS E20 + B16.
- **Queue position modeling.** Forensic replay v1 Section 7 calibration probe against `kalshi_fills_history.json` was DEFERRED when Phase 3 surfaced the B25 mechanism. v2 inherits the deferral — idealized tick-level fills (price-touched-by-correct-side-taker = filled) are the v2 fill semantic. Queue-effect calibration becomes a v3 concern, the same as in forensic replay v1's open items.
- **Bilateral/paired-leg replay.** G12-blocked. Single-leg only.
- **Scalar-outcome markets.** Inherits Layer B v1 spec scope-out (`result == "scalar"` markets excluded per producer-time verification).

---

## 2. The candidate set — full non-settle premarket corpus

**Decision 1: every (cell, policy) tuple in Layer B v1's `exit_policy_per_cell.parquet` where channel == "premarket" and the policy is not a settle-horizon time_stop.**

Layer B v1 produces 19,170 (cell, policy) rows. The non-settle premarket subset is ~12,455 rows (per ROADMAP T36 entry, Session 9 anchor). Per cell, the policy grid is ~53 non-settle policies (54 total minus 1 settle-horizon time_stop). The cell count is ~235 substantial premarket cells. v2 evaluates the full universe; forensic replay v1's "top-N per (channel, category) = 80 candidates" pre-filter is dropped — that was an N-bound imposed by per-candidate streaming compute, which v2's architecture (Section 5) removes.

**Pre-filter (inherited from v1 Decision 2):**
- Layer B v1 cells with `n_simulated < 50` excluded (insufficient trajectory mass).
- Cells where the actual moment count after entry-cell-key filtering falls below 50 are excluded with a producer-log entry.

**Sampling note (no top-N sampling at v2 producer level):** v1's `sample_manifest.json` ticker cap (SAMPLE_PER_CELL=30 from Layer A v1) is the only sampling pre-filter applied. Within a cell's sampled tickers, all entry moments are evaluated. v2 deliberately does not introduce a second-stage moment-sampler — per Section 5 the per-cell-vectorized-policy architecture makes evaluating all moments compute-tractable, and the spec's tick-level mandate would be undermined by a stochastic moment sampler (we cannot afford a second sampling source beyond Layer A's already-fixed ticker sample).

---

## 3. The replay methodology

### 3.1 Per-moment tick-level fill procedure

v2 inherits forensic replay v1 Section 3.1's 9-step per-moment procedure with one architectural change in step 5-6 (policy evaluation is vectorized across the policy grid at each moment, not single-policy per call). The convention invariants from forensic replay v1 Section 3.1 step 1 (taker_side semantics anchored on the Session 9 5,878-trade-pair empirical probe) are inherited unchanged:
- **Entry-fill check:** a hypothetical maker BID for yes is filled by `taker_side == "no"` (taker buys no = sells yes, hits our bid).
- **Exit-fill check:** a hypothetical maker SELL for yes is filled by `taker_side == "yes"` (taker buys yes, pays our ask).

Per-moment procedure for each (cell, ticker, T0) entry moment:

1. **Identify the moment.** From `g9_candles`, find every minute T where `regime_for_moment(T)`, `entry_band_idx(yes_ask_close[T])`, `spread_band_name(yes_bid_close[T], yes_ask_close[T])`, `volume_intensity_for_market`, and `categorize(ticker)` all match the cell key. Producer mirrors `walk_trajectory` in `build_layer_b_v1.py` (lines 303-470) and `build_forensic_replay_v1.py:cell_state_at_minute` (lines 162-235). Schema invariants and NaN-preservation invariant inherited from forensic replay v1 Section 3.1 step 1.

2. **Hypothetically post a maker bid at T0.** Post at `yes_bid_close[T0]` for unit size (sizing is Layer D's concern).

3. **Walk `g9_trades` forward second-by-second from T0.** Stream rows for this ticker with `created_time >= T0` ordered ascending. For each trade event:
   - **Cell drift recording:** at every minute boundary `floor(created_time / 60)`, recompute the cell state from the bid/ask snapshot in g9_candles and record whether the cell still matches.
   - **Entry-fill check:** if `taker_side == "no"` AND `yes_price_dollars <= our_bid_price`, the trade hits our bid — record `fill_time`, `fill_price = our_bid_price`. Stop walking forward for fill purposes.
   - **Entry timeout:** if the bid has not filled within `entry_timeout_minutes` (default 240, the same `DEFAULT_HORIZON_MIN` used in v1's `evaluate_policy`) or the market settles, record `outcome = "unfilled"` for this moment across ALL policies on this cell. Skip steps 5-8.

4. **Record fill-time cell state.** At `fill_time`, recompute the cell state from g9_candles at `floor(fill_time / 60)`. Store as `fill_time_cell`.

5. **Construct per-policy exit targets (vectorized).** For each policy in the cell's policy grid, compute:
   - **Scenario A target** (post-time anchor): `T0_cell.exit_target(policy)` per Layer B's `evaluate_policy` semantics — `exit_target = fill_price + policy_threshold_dollars` for limit / limit_time_stop / limit_trailing policies; trailing offset from fill_price for trailing / limit_trailing policies; horizon timestamp `fill_time + policy.horizon_minutes` for time_stop / limit_time_stop policies.
   - **Scenario B target** (fill-time anchor): same construction using `fill_time_cell`'s policy parameters. For threshold-based policies, B's target differs from A's only if the cell drifted between T0 and fill_time. For time-stop and trailing-stop policies, A and B agree by construction at the time horizon level (the horizon is a clock cap, not a price cap), but the path-walked metrics (trailing running-max, time-stop cap-bid) are evaluated against the same tick stream so per-policy aggregates may differ slightly via the cell-state policy parameters bound at A's vs B's anchor.

6. **Walk `g9_trades` forward from `fill_time` looking for kisses (vectorized across policy grid).** Continue streaming g9_trades with `created_time >= fill_time` ordered ascending. Maintain per-policy state (`exited_A`, `exited_B`, `running_max_bid_A`, `running_max_bid_B` for trailing types). For each trade:
   - **`taker_side == "yes"` (exit-fill candidates):** for each policy not yet exited under Scenario A, if `yes_price_dollars >= scenario_A_target[policy]`, record exit. Same for Scenario B.
   - **`taker_side == "no"` (price observations for cap-side and trailing):** observe `yes_price_dollars` as a bid-side print; update trailing `running_max_bid` for trailing/limit_trailing policies (running max of all observed bid prints in the post-fill tape).
   - **Horizon check (vectorized):** for each policy not yet exited, if `current_trade_ts >= fill_time + policy.horizon_minutes` and the policy is time_stop or limit_time_stop, record `outcome = "horizon_fired"` at the most recent observed bid (or settle value if past settlement).
   - **Settlement:** if a settlement event in `g9_metadata` is reached before any policy exits, record `outcome = "settled_unfired"` for each unexited policy under both scenarios; `capture = settlement_value - fill_price`.

   The vectorized walk visits each post-fill trade exactly once and evaluates the full policy grid against it. Compared to forensic replay v1's per-candidate streaming (~one trade walk per (cell, policy)), this amortizes the trade I/O across the ~53 policies per cell.

7. **Record per-moment outcomes (vectorized).** For each policy in the cell's grid, record `(outcome_A, capture_A_gross_dollars, time_to_exit_A_minutes, outcome_B, capture_B_gross_dollars, time_to_exit_B_minutes)`. Per-moment common columns: `time_to_fill_minutes`, `cell_drift_at_fill`, `fill_price_dollars`, `T0_cell_key`, `fill_time_cell_key`.

8. **(Reserved for fees, deferred.)** v2 outputs `capture_*_gross_dollars` only. Step 8 of forensic replay v1 (fee schedule application) is skipped at v2 producer level; fees are layered on at T32 (Layer C v1) consumption time. The output schema records `capture_*_gross_dollars`; downstream consumers compute `capture_*_net_dollars` from the Cat 2 fee table or layer_c_v1 outputs.

9. **Aggregate across all moments for this (cell, policy).** Produce per-(cell, policy) summary: moment count, fill rate, mean/p10/p25/p50/p75/p90 of capture_A_gross and capture_B_gross, mean time_to_fill, mean time_to_exit per scenario, cell-drift distribution, win rate (capture_*_gross > 0).

### 3.2 Cell-target convention — inherited from forensic replay v1

Both Scenario A (post-time anchor) and Scenario B (fill-time anchor) are evaluated in parallel, mirroring forensic replay v1 Section 3.2. Per Cat 11, Scenario B > Scenario A in 78.8% of candidates with mean delta $0.0158/moment across the 80 evaluated. v2 preserves both scenarios on the full corpus so the per-cell A-vs-B distinction can be re-measured at scale; cells where A > B at full-corpus scale (a tail-of-the-tail finding given the 78.8% B-dominance at top-N) become a v3 stratification dimension.

### 3.3 Calibration invariant — v2's mandate

Within tolerance ±$0.01/moment, v2 must reproduce forensic replay v1 phase3 `replay_capture_B_net_mean` and `replay_capture_A_net_mean` on the 80 candidates that forensic replay v1 evaluated. If v2 ≈ forensic replay v1 on the calibration anchor (ATP_MAIN 50-60 tight low / limit_c=30 = $0.2610/moment realized B), v2's tick-level fill mechanism is empirically equivalent to forensic replay v1's at the candidate level. Phase 1 (Section 5.2) is the calibration probe; Phase 3 PASS (Section 6 Check 1) requires the 80 to reproduce.

---

## 4. Outputs

Output directory: `data/durable/layer_b_v2/`

### Output 1: Per-(cell, policy) summary (parquet) — primary deliverable

`data/durable/layer_b_v2/exit_policy_per_cell.parquet`

One row per (cell, policy) tuple (~12,455 rows). Schema mirrors Layer B v1's `exit_policy_per_cell.parquet` + adds the tick-level realized columns (paralleling forensic replay v1 phase3 `candidate_summary.parquet`):

| Column | Type | Source |
|---|---|---|
| channel | string | inherited from v1 (constant "premarket" in v2 scope) |
| category | string | inherited from v1 |
| entry_band_lo | int | inherited from v1 |
| entry_band_hi | int | inherited from v1 |
| spread_band | string | inherited from v1 |
| volume_intensity | string | inherited from v1 |
| policy_type | string | inherited from v1 |
| policy_params | string (JSON) | inherited from v1 |
| n_simulated | int | inherited from v1 (Layer B v1's trajectory count for the cell) |
| capture_mean_simulated | float | v1's `capture_mean` carried forward for delta computation |
| capture_p10/p25/p50/p75/p90_simulated | float | v1's percentiles carried forward |
| fire_rate_simulated | float | v1's `fire_rate` carried forward |
| n_replay_moments | int | v2 moment count (per (cell, policy)) |
| replay_fill_rate | float | fraction of moments where the maker bid filled |
| replay_capture_A_gross_mean | float | v2 Scenario A realized capture mean (gross, no fees) |
| replay_capture_A_gross_p10/p25/p50/p75/p90 | float | v2 Scenario A percentiles |
| replay_capture_B_gross_mean | float | v2 Scenario B realized capture mean (gross, no fees) |
| replay_capture_B_gross_p10/p25/p50/p75/p90 | float | v2 Scenario B percentiles |
| replay_win_rate_A | float | fraction with capture_A_gross > 0 |
| replay_win_rate_B | float | fraction with capture_B_gross > 0 |
| replay_time_to_fill_p50 | float | minutes |
| replay_time_to_exit_A_p50 | float | minutes |
| replay_time_to_exit_B_p50 | float | minutes |
| cell_drift_rate_at_fill | float | fraction of fills where the cell drifted between T0 and fill_time |
| simulated_vs_realized_delta_A | float | `capture_mean_simulated - replay_capture_A_gross_mean` |
| simulated_vs_realized_delta_B | float | `capture_mean_simulated - replay_capture_B_gross_mean` |

Schema is intentionally a strict superset of forensic replay v1 phase3 `candidate_summary.parquet` minus the fee-bearing `*_net_*` columns (deferred to T32 consumption). v1-of-Layer-B columns are preserved verbatim for diff-against-v1 audits.

### Output 2: Per-cell drift dynamics (parquet)

`data/durable/layer_b_v2/cell_drift_per_minute.parquet`

For each cell (not (cell, policy) — drift is a cell-keyed property), per minute relative to T0 (0 to 240), count of moments where the cell still matches. Schema mirrors forensic replay v1 Output 4 (commit `73de3a6`'s `cell_drift_per_minute.parquet`).

### Output 3: A-vs-B comparison (parquet)

`data/durable/layer_b_v2/scenario_comparison.parquet`

One row per (cell, policy). Schema:
- cell_key + policy columns (same as Output 1)
- `corr_A_B`: Spearman rank correlation between capture_A_gross and capture_B_gross across moments
- `mean_delta_A_B`: `mean(capture_A_gross - capture_B_gross)`
- `cells_diverged_count`, `cells_diverged_pct`: count and fraction of moments where cell_drift_at_fill is true

### Output 4: Run summary (json)

`data/durable/layer_b_v2/run_summary.json`

Producer metadata: runtime per phase, candidate count, total moments, total fills, sha256 of inputs (g9_trades, g9_candles, g9_metadata, sample_manifest.json, exit_policy_per_cell.parquet), git commit of producer, peak working-set memory, validation-gate check results.

### Output 5: Build log

`data/durable/layer_b_v2/build_log.txt`

Per-cell runtime, per-cell moment count, fill rate, memory snapshots, warnings on drift outliers (>50% drift within 5 minutes — likely producer bug; threshold inherited from forensic replay v1 Section 5.3).

### Output 6 (optional, behind producer flag): Per-moment replay tape

`data/durable/layer_b_v2/replay_tape.parquet`

One row per (cell, policy, ticker, T0_unix). Schema mirrors forensic replay v1 Output 1 minus fee columns. **Not produced by default at full corpus scale** — would be ~12,455 × ~950 moments × ~150 bytes = ~1.7 GB on disk, exceeding usable VPS storage budget per the durable-archive discipline. Producer flag `--write-replay-tape <cell_key_pattern>` writes the tape for a single cell or pattern-matched cells (the 80-candidate calibration subset would be the natural default invocation, giving a ~5MB byte-comparable diff against forensic replay v1's `replay_tape.parquet`).

---

## 5. Producer architecture

`data/scripts/build_layer_b_v2.py` — single-file producer. Uses `cell_key_helpers.py` (shared with Layer A v1, Layer B v1, forensic replay v1). Inherits the per-cell streaming idiom from `build_layer_b_v1.py` (per-ticker g9_candles row-group reads under C28 streaming discipline) and the per-moment tick-walk idiom from `build_forensic_replay_v1.py:replay_one_moment` (lines 271-371) with the convention invariants from commit `a058212`.

### 5.1 Architecture decision — per-cell streaming with vectorized policy evaluation

**Per-cell streaming, single trade-walk per (cell, ticker, moment), all policies evaluated in vector at each tick event.**

The architecture decision is the load-bearing decision in this spec (per ROADMAP T36 entry: "decision commits the architecture for several sessions; chat-side sign-off matters at this gate"). Two reasonable architectures considered:

- **Architecture A — per-candidate streaming (forensic replay v1's pattern, naive port).** For each (cell, policy) tuple separately, stream g9_trades, walk per the 9-step procedure. **Compute cost:** Phase 3 measured 258.21 min for 80 candidates × 75,833 moments = **0.204 s/moment**. Extrapolated to the full v2 universe of 12,455 (cell, policy) tuples × ~950 moments avg per cell = ~11.8M tuple-moments × 0.204 s = **~670 hours single-threaded**. Per-cell parallelization of ~8 processes (the realistic VPS bound given disk I/O contention on a single-disk parquet read) gets this to ~85 hours = 3.5 days, marginal but tractable. **Rejected** because most of the trade I/O is redundant: same-cell-different-policy tuples re-read the same trade tape ~53 times per cell.

- **Architecture B — per-cell streaming with vectorized policy evaluation (chosen).** For each cell, stream g9_trades once per (ticker, T0) entry moment, evaluate all ~53 policies in vector against the single tick walk. **Compute cost:** ~235 cells × ~950 moments/cell × 0.204 s = ~218,000 cell-moments × 0.204 s = **~12.4 hours single-threaded**, before counting the vectorization overhead at each tick (a per-policy O(1) update — running max for trailing types, target comparison for limit / limit_time_stop, horizon clock check for time_stop / limit_time_stop). Per-tick overhead is bounded by ~53 floating-point comparisons + array updates: in practice <0.5 ms additional per tick, well under the trade-walk dominant cost. **Total estimate ~13-16 hours single-threaded.** No parallelization needed for v2; parallelization remains a v3 lever if corpus expansion (in-match channel, settle-horizon) raises the budget meaningfully.

**Sampling NOT used.** Per Section 2 Decision 1, the per-cell ticker sample is inherited from Layer A v1's `sample_manifest.json` (SAMPLE_PER_CELL=30). v2 does not introduce a second-stage moment sampler. The vectorized-policy architecture makes the full moment universe per cell compute-tractable.

**Parallelization NOT used.** Single-process keeps the determinism guarantee (Section 5.4 below) simple. If v3 (in-match + settle-horizon variants) raises the budget, parallelization across cells is the natural extension — but unnecessary at v2 scope.

### 5.2 Compute envelope (RAM-constrained)

VPS RAM budget per forensic replay v1 Section 5.1: ~1.3 GiB effective, <500 MiB working set target.

Per-cell working set:
- Cell's sampled ticker list (from sample_manifest.json): tens of strings, negligible.
- For each ticker in cell: per-ticker g9_candles row group (column-projected to ticker, end_period_ts, yes_bid_close, yes_ask_close, volume_fp). Per forensic replay v1 Section 5.1 disk probe: g9_candles row groups are ticker-sorted; per-ticker read is ~4 KB. 30 tickers × 4 KB = ~120 KB.
- For each ticker × T0 moment: g9_trades predicate-pushdown read with filter `(ticker, created_time >= T0)`. Per forensic replay v1 measurement: per-ticker trade-tape slices are small (<1 MB per ticker for typical premarket-into-settlement windows).
- Per-moment per-policy state: ~53 policies × per-policy state (fill flag, exit flag, target, running max) × 2 scenarios = ~1 KB per moment, transient.
- Output accumulator: ~12,455 rows × ~32 columns × 16 bytes = ~6 MB, in-memory until end of run.

Working set << 500 MiB. Comfortable.

### 5.3 Phased rollout

- **Phase 1 (calibration probe):** single candidate × 100 moments. Phase 1 candidate: **ATP_MAIN 50-60 tight low / limit_c=30** (the Cat 11 / forensic replay v1 rank-1 deployable cell, `replay_capture_B_net_mean = $0.2610` at n=2914 moments — `data/durable/forensic_replay_v1/phase3/candidate_summary.parquet`). v2 Phase 1 must produce `capture_B_gross_mean within $0.2610 ± $0.01` (v2 is gross, v1 phase3 is net but used zero-fee placeholder per producer Phase 1/2/3 scope; values are byte-equivalent until fees integrate at T32). Output written to `data/durable/layer_b_v2/probe/`. **Runtime budget: <5 minutes.** Gates Phase 2.
- **Phase 2 (single-cell, all policies, all moments):** ATP_MAIN 50-60 tight low × all ~53 non-settle policies × ~2914 moments. Validates vectorized-policy correctness at full per-cell moment scale. Reproduces forensic replay v1's 5 candidates for this cell (limit_c ∈ {7, 10, 15, 20, 30}) within ±$0.01 each. Cross-checks the other ~48 policies on this cell against Layer B v1's `capture_mean_simulated` and reports the per-policy gap distribution. **Runtime budget: <15 minutes.** Gates Phase 3.
- **Phase 3 (full corpus):** all ~12,455 non-settle premarket (cell, policy) tuples. **Runtime budget: <20 hours** (with 16-hour central estimate per Section 5.1 plus ~25% slack). Output to `data/durable/layer_b_v2/` final paths. Per-cell incremental writes (mirror forensic replay v1 commit `db1d249`'s kill-resilience pattern) so a mid-run interruption preserves completed cells.

Each phase's output is gated by the prior phase's PASS verdict per LESSONS C28 + D11.

### 5.4 Determinism

Producer is deterministic given fixed inputs. sha256 of inputs (g9_trades, g9_candles, g9_metadata, sample_manifest.json, exit_policy_per_cell.parquet) recorded in `run_summary.json`. Re-running on the same inputs produces byte-identical Outputs 1-3. (Output 4 build_log timestamps and Output 5 working-memory snapshots are non-deterministic by construction.)

### 5.5 Logging

Producer writes `data/durable/layer_b_v2/build_log.txt` with timestamps, per-cell runtime, per-cell moment count, per-cell fill rate, memory snapshots (free -h every N cells; N tuned in Phase 2), warnings on cell-drift outliers (>50% drift within 5 minutes is a likely producer bug per forensic replay v1 Section 5.3 threshold).

---

## 6. Validation gate (T36c)

PASS verdict requires Checks 1-5 PASS (gating); Check 6 is informative-only (drives v3 prioritization). Sibling shape to forensic replay v1 Section 6 and layer_b_spec.md validation gate.

**Check 1 (gating, calibration anchor): v2 reproduces forensic replay v1 Phase 3 corrected within tolerance on the 80 evaluated candidates.** PASS criterion: for each of the 80 candidates in `data/durable/forensic_replay_v1/phase3/candidate_summary.parquet`, `|v2.replay_capture_B_gross_mean - v1_phase3.replay_capture_B_net_mean| ≤ $0.01` (v1 phase3 used zero-fee placeholder so gross ≈ net to within rounding). Rank-1 anchor: ATP_MAIN 50-60 tight low / limit_c=30 must produce $0.2610 ± $0.01. Failure on this check means v2's tick-level fill semantics diverge from forensic replay v1's — a producer bug, not a strategy finding. **This check is the load-bearing gate** — Check 1 PASS is the empirical proof that v2's mechanism matches the tick-level reality that Cat 11 measured.

**Check 2 (gating): replay_fill_rate is plausible across the corpus.** PASS criterion: ≥ 95% of (cell, policy) tuples have `0.05 ≤ replay_fill_rate ≤ 0.95`. Outliers above 0.95 (deep-favorite cells with bid floor at maker-prices, the forensic replay v1 Check 2 failure mode on 5 WTA_CHALL cells) are a known cell-class limitation, not a producer bug. Producer log surfaces the per-cell outlier list. Threshold relaxed from 100% (forensic replay v1) to 95% because at corpus scale, deep-favorite outliers are an expected ~5% population at the cell-class level.

**Check 3 (gating): A-vs-B coherence preserved at corpus scale.** Per Cat 11 the post-vs-fill distinction is empirically robust (B > A 78.8% of 80 candidates, mean delta $0.0158/moment). PASS criterion at corpus scale: `mean(|capture_A_gross_mean - capture_B_gross_mean|) < $0.02` across all ~12,455 tuples, AND the sign of `capture_B_gross_mean - capture_A_gross_mean` is consistent (>60% of tuples have B > A). Threshold relaxed from forensic replay v1's $0.01 because corpus-wide tail cells include lower-fill-rate, higher-drift candidates where A vs B can diverge more under cell-state policy parameter shifts.

**Check 4 (gating): v2 dominates v1 on limit policies on average; calibrated within tolerance on time_stop and trailing.** Per Cat 11 by-policy structural pattern (limit: +$0.072 v1-undercount; time_stop: $0.008 calibrated; trailing: −$0.005). PASS criterion:
- Limit + limit_time_stop + limit_trailing policies (combined ~49% of corpus per Cat 11): `mean(capture_B_gross_mean - capture_mean_simulated) > $0.03` (the v1-undercount is real and v2 captures it).
- Time_stop (non-settle) policies: `mean(|capture_B_gross_mean - capture_mean_simulated|) < $0.03`.
- Trailing policies: `mean(capture_B_gross_mean - capture_mean_simulated) ∈ [-$0.03, $0.03]`.

If limit-class policies under-realize v1 (delta < 0), v2 has a producer bug — that's not the B25 mechanism direction. If time_stop policies show >$0.03 absolute deviation from v1, the producer's horizon-clock logic has drifted from `evaluate_policy` semantics.

**Check 5 (gating): rank ordering on limit policies is meaningfully different from v1 (B25 mechanism propagation).** Per Cat 11, v1's `capture_mean` is not a deployment-ready ranking source for limit-policy cells. PASS criterion: Spearman rank correlation between `capture_mean_simulated` and `replay_capture_B_gross_mean` across all limit-policy tuples (~6,000 of the ~12,455) is **< 0.5**. This is the inverse of forensic replay v1 Check 5's PASS direction — forensic replay v1 required ρ ≥ 0.75 to PASS (simulator-realized agreement); v2 requires ρ < 0.5 on limit policies to PASS (simulator-realized disagreement, confirming B25 propagates to the full corpus, not just the top-N 80). For non-limit policy classes (time_stop, trailing), the v2-vs-v1 rank correlation should be ≥ 0.75 (corpus-wide calibration coherence on the policy classes that B25 named as v1-calibrated).

**Check 6 (informative-only): cell-drift dynamics scale.** Reports `cell_drift_per_minute.parquet`-derived median drift at T+30 across the corpus. Cat 11 measured 51.7% median drift at T+30 across 80 candidates. PASS direction: corpus-wide median drift at T+30 ∈ [40%, 65%] (sanity bound). Result drives v3 cell-key refinement (wider entry bands, longer-window spread bands) and is forwarded to the next Layer-A-spec revision.

---

## 7. Calibration against forensic replay v1 phase3

Per Section 6 Check 1 — v2's mandate is byte-equivalent reproduction of forensic replay v1 phase3 on the 80 evaluated candidates. The calibration data lives at:

`data/durable/forensic_replay_v1/phase3/candidate_summary.parquet` — commit `73de3a6`

Spot-check anchors (commit `73de3a6` parquet, verified Session 10 read):
- **Rank-1 calibration anchor:** ATP_MAIN 50-60 tight low / limit_c=30. v1 phase3 `replay_capture_B_net_mean = $0.2610`, fill rate = 0.757, cell drift at fill = 0.093, n_moments = 2914.
- **Cat 11 by-policy by-class anchor** (must reproduce on the 80):
  - limit (n=39): mean(B - sim) = +$0.0810 in phase3.
  - limit_time_stop (n=8): mean(B - sim) = +$0.0262 in phase3.
  - limit_trailing (n=2): mean(B - sim) = −$0.0785 in phase3.
  - time_stop (n=21, non-settle subset only — settle-horizon time_stops were excluded by forensic replay v1 Phase 3 candidate selection per spec Section 1): mean(B - sim) = +$0.0260 in phase3.
  - trailing (n=10): mean(B - sim) = +$0.0256 in phase3.
- **Validation-gate-by-check anchors** (commit `73de3a6` run_summary.json): check1 PASS (80/80 ≥ 50 moments); check2 FAIL at 75/80 (5 WTA_CHALL deep-favorite outliers > 0.95); check3 PASS (mean abs A-B delta 0.0158, B>A 78.75%); check4 FAIL at 23.75% (76.25% have realized > simulated); check5 FAIL at ρ=0.136 (p=0.228); check6 median drift T+30 = 51.7%.

v2 Phase 1 (single candidate × 100 moments) and Phase 2 (single candidate × all moments) calibrate against the rank-1 anchor. Phase 3 calibration check operates across all 80 candidates per Section 6 Check 1.

---

## 8. Open items for v3

- **v3: in_match channel.** Forensic replay v2 settles the gap-risk haircut measurement; once that lands, Layer B v3 inherits the methodology and extends the corpus to in_match cells. The in_match cell key (4-dim per F30) drops volume_intensity at consumer time; Layer B v3 inherits the 5-dim key for invariant preservation, same as v1 / v2.
- **v3: settle-horizon time_stop policies.** Forensic replay v2 settle-horizon variant covers Cat 5's predicted top cell (WTA_MAIN 40-50 tight low / time_stop "settle", $0.509 simulated). Once that variant validates the mechanism, Layer B v3 adds the settle-horizon policies back to the corpus.
- **v3: queue position modeling.** Inherits forensic replay v1 Section 7 deferral. If kalshi_fills_history calibration probe (deferred from forensic replay v1 phase3) reveals queue effects > $0.05/moment, v3 adds queue-position fill probability.
- **v3: parallelization across cells.** If v2 Phase 3 runtime materially exceeds the 20-hour budget, or if v3 corpus expansion (in_match + settle-horizon) raises the budget, parallelization across cells via multiprocessing is the natural extension. Single-process determinism in v2 is a deliberate simplicity choice, not an architectural constraint.
- **v3: per-(cell, policy) fee derivation.** Layer C v1 (T32) integrates fees on top of v2's `*_gross_*` columns. If layer_c_spec.md Decision 5 promotes (per-cell fee variation observed), v3 produces `*_net_*` columns directly.
- **v3: replay_tape full corpus.** v2 writes Output 6 (`replay_tape.parquet`) only behind producer flag for selected cell patterns. v3 considers full-corpus replay_tape if storage budget allows or per-moment downstream consumers emerge.

---

## 9. Cross-references

- **ROADMAP.md T36** (commit `fb3f976`) — origin specification of this spec. T36 chain: T36a (this spec), T36b (producer build), T36c (coherence read).
- **ROADMAP.md T32** (Amendment 2026-05-10) — Layer C v1 demoted by Cat 11 / B25; T32a spec (commit `4bed07f`) remains valid; T32b/c re-prioritize after T36c PASS. Layer B v2 supersedes Layer B v1 as Layer C's input.
- **LESSONS.md B25** (commit `033fb8a`) — minute-cadence fire_rate undercount mechanism. v2 fixes this at the source.
- **LESSONS.md B16** — Layer A / B / C separation principle. v2 adds exactly one concept (tick-level fill semantics) on top of v1; fees remain Layer C's concern.
- **LESSONS.md B21** — Layer A→B metric semantics didn't transfer (MFE vs endpoint); v2's coherence read (Section 6 Check 4) inherits the policy-class-aware validation pattern.
- **LESSONS.md C28** — streaming discipline on large parquets. v2 inherits the per-ticker row-group projection idiom from v1 (`build_layer_b_v1.py` row-group reads) + the per-moment predicate-pushdown idiom from forensic replay v1 (`build_forensic_replay_v1.py:load_ticker_trades`).
- **LESSONS.md C30, D11** — probe-before-assume / read-source-before-spec. This spec is anchored on Session 10 reads of the v1 producer code (`evaluate_policy` lines 180-300), forensic replay v1 producer code (`replay_one_moment` lines 271-371), Phase 3 run_summary.json runtime measurement (258.21 min for 80×75833 moments = 0.204 s/moment), and candidate_summary.parquet calibration anchor (ATP_MAIN 50-60 tight low limit_c=30 = $0.2610 verified).
- **LESSONS.md C31** — mechanism-coherent ≠ empirically correct. v2's calibration mandate (Section 6 Check 1) is a defense against the v1→v2 port reproducing the same mechanism mistake at a different scale.
- **LESSONS.md E16, E18, E20, E27, E28** — channel preservation, bilateral funnel, per-cell discipline, methodology drift. v2 inherits all of v1's discipline.
- **LESSONS.md F31, F33** — OI partially tracked, depth-chain gap. v2 does not consume OI; queue modeling deferred to v3.
- **forensic_replay_v1_spec.md Sections 3, 5, 6, 10** — sibling spec; v2 inherits Section 3.1's 9-step per-moment procedure, Section 5.1's compute-envelope discipline, Section 6's check pattern, and Section 10's verdict.
- **layer_b_spec.md** — v1 spec; v2 supersedes v1's `exit_policy_per_cell.parquet` as canonical cell-ranking source for non-settle premarket once T36c PASSes. v1 outputs remain valid for in-match / settle-horizon cells until v3 supersedes those.
- **layer_c_spec.md** — sibling spec; T32 (demoted by Cat 11) integrates fees on top of v2's `*_gross_*` columns once T36c PASSes.
- **ANALYSIS_LIBRARY.md Cat 11** (commit `4e36f30`) — empirical anchor for v2's strategic mandate. v2 reproduces and generalizes Cat 11.
- **SIMONS_MODE.md Section 6** — origin specification of forensic replay framework. v2 closes the second forward-reference Section 6 opened (the first was forensic replay v1's deliverable, closed in commit `c87e797`; the second is the simulator revision once forensic replay v1's FAIL verdict named B25).
- **SIMONS_MODE.md Section 8** — Cat-chain anchor evidence; T32 demotion + T36 promotion landed at commit `fb3f976`.

---

*Spec authored 2026-05-10 ET (Session 10). T36a → spec lands at this commit → Coordination Point 1 STOP per docs/SESSION10_HANDOFF.md. T36b (producer build) gated on chat-side spec review. T36c (coherence read + report) gated on T36b output landing.*
