# Forensic replay v1 specification — tick-level realized economics per (cell, policy)

**Status:** SPEC (Session 9). Implementation gated on this spec's closure.

**Foundation pointer:** T28 G9 parquets (commit ea84e74), sha256-pinned. Layer A v1 cell_stats.parquet (T29 producer commit 1398c39, MANIFEST commit 37a5216, ANALYSIS_LIBRARY entry commit cf31903, T21 PASS verdict commit faf51d9). Layer B v1 exit_policy_per_cell.parquet (T31b producer commit pending; sample_manifest.json T29 commit 1398c39).

**Per SIMONS_MODE.md Section 6:** Forensic replay is the first concrete analytical deliverable of post-Session-9 strategy work. It uses g9_trades and g9_candles directly to measure realized economics per (cell, policy) candidate, validating Layer B v1's simulated capture distributions against tick-level reality and producing a ranked actionable cell list for forward deployment.

**Per LESSONS B16:** Forensic replay sits adjacent to Layer C (G11 — fees, fill probability, queue position). Layer C v1 (per docs/layer_c_spec.md) computes economics on Layer B's simulator outputs. Forensic replay computes economics on tick-level reality. The two are complementary: Layer C tells you what fee schedule applies to Layer B's simulated trajectories; forensic replay tells you whether Layer B's simulated trajectories track empirical fills at all. Both are required for forward deployment confidence.

---

## 1. Scope (v1)

**Top-N (cell, policy) candidates from Layer B v1 evaluated against tick-level g9_trades reality.**

In-scope per channel (premarket and in_match, per LESSONS E16/E31 channel-preservation discipline):

- **Premarket channel.** Top-N premarket cells ranked by Layer B v1 capture_mean per (channel, category). Per Cat 5 finding (commit 8b3a3a6, sha256 `df8257a183e4c637`): premarket top-cell EV is the highest in the corpus (top: WTA_MAIN 40-50/tight/low/time_stop at $0.509). Premarket-first is the SIMONS-mode discipline frame per Section 7 rollback question 5.
- **In-match channel.** Top-N in_match cells ranked the same way per (channel, category). Per Cat 5 frame 3 (right-tail), in_match top is $0.393 — lower peak than premarket but still substantial; deferred to v2 second-pass with gap-risk haircut measured separately.

**v1 disposition: premarket-only.** Premarket cells have higher top-tail EV per Cat 5 frame 3, no gap-risk to model, and the simpler entry-state evolution (point-by-point in-match vs minute-cadence premarket) means v1 can establish the methodology before adding the in-match second-pass.

Out of scope for v1:

- **In-match cells.** Deferred to v2. Same methodology, plus gap-risk haircut measurement (between two consecutive g9_trades for an in-match ticker, the score may have changed; the cell-state at fill time may differ from the cell-state at the prior observed trade in ways that cannot be reconstructed from price alone).
- **Settlement-zone cells.** Per Layer B v1 spec scope, settlement-zone is a separate v2 spec — structural directional asymmetry requires structurally different forensic replay logic. Excluded here.
- **Bilateral/paired-leg replay.** Per LESSONS E18/E21, bilateral capture is G12-blocked. Forensic replay v1 is single-leg. Bilateral forensic replay is a v3 deliverable contingent on the per-event paired moments dataset.
- **Queue position modeling.** Per SIMONS_MODE Section 6 caveat, v1 uses idealized maker fills (price-touched = filled). Queue-position fill probability is a Layer C v3 concern. Calibration against kalshi_fills_history.json (Section 7 of this spec) provides a sanity check on the queue-effect magnitude.
- **Capital constraints / portfolio sizing.** Per LESSONS E20 + B16, v1 is per-(cell, policy) economics; portfolio-level sizing is a downstream Layer D concern.
- **Scalar-outcome markets.** Inherited from Layer B v1 spec scope. Markets with `result == "scalar"` (496 of 20,110 per disk probe) are excluded.

---

## 2. The candidate list — input from Layer B v1

**Decision 1: Top-N per (channel, category) ranked by Layer B v1 capture_mean.**

Layer B v1 produces 19,170 (cell, policy) rows. v1 forensic replay does not evaluate all of them — it evaluates only the top-N candidates per (channel, category), where N is the spec parameter chosen against the realistic compute envelope (see Section 5).

**Channel:** premarket (in_match deferred to v2 per scope above).

**Categories (4 in_scope per cell taxonomy):** ATP_MAIN, ATP_CHALL, WTA_MAIN, WTA_CHALL.

**Ranking metric:** Layer B v1 `capture_mean` (gross, no fees). Per Cat 5 finding, top-tail favors premarket; v1 selects from the right tail of the per-channel distribution.

**N parameter:** **N=20 per (channel, category)** in v1, total 4 × 20 = 80 candidate (cell, policy) tuples. Sized against the realistic compute envelope per Section 5 (per-cell streaming, ~5-10 minutes per candidate at expected moment count under predicate-pushdown reads) → ~6-12 hours total replay runtime, scaling-resilient via Phase 2 single-candidate gate. If v1 results justify scaling, v2 expands N or relaxes channel restriction.

**Pre-filter:** Layer B v1 cells with `n_simulated < 50` excluded (insufficient trajectory mass; ranking unreliable per Layer B v1 spec Decision 2 trajectory threshold).

---

## 3. The replay methodology

### 3.1 Per-moment replay procedure (the 9 steps)

Per SIMONS_MODE Section 6, for each candidate (cell, policy) and each entry moment T0 in the candidate's market history where the cell conditions hold:

1. **Identify the moment.** From g9_candles, find every minute T where `regime_for_moment(T)`, `entry_band_idx(yes_ask_close[T])`, `spread_band_name(yes_bid_close[T], yes_ask_close[T])`, `volume_intensity_for_market`, and `categorize(ticker)` all match the cell key. Producer mirrors `walk_trajectory` in `build_layer_b_v1.py`.

2. **Hypothetically post a maker bid.** At T0, post a hypothetical maker bid at `yes_bid_close[T0]` for size = unit (1 contract; sizing is Layer D's concern). The bid sits at the cell's prevailing bid price.

3. **Walk g9_trades forward second-by-second from T0.** Stream `g9_trades` rows for this ticker with `created_time >= T0` ordered ascending. For each trade event:
   - **Cell drift recording:** every minute boundary (`floor(created_time / 60)`), recompute the cell state using the bid/ask snapshot at that minute (from g9_candles) and record whether the cell still matches. Outputs the cell-drift distribution (Output 4 in Section 4).
   - **Fill check:** if `taker_side == "yes"` and `yes_price <= our_bid_price`, the trade hits our bid — we are filled. Record `fill_time = trade.created_time`, `fill_price = our_bid_price`. Stop walking forward for fill purposes.
   - **Maximum hold:** if the bid has not filled within `policy.entry_timeout_minutes` (default: 240 minutes, the same `DEFAULT_HORIZON_MIN` used in `evaluate_policy`) or the market settles, record `outcome = "unfilled"` and skip steps 5-8 for this moment.

4. **Record fill-time cell state.** At `fill_time`, recompute the cell state from g9_candles bid/ask at `floor(fill_time / 60)`. Store as `fill_time_cell` (may differ from the post-time `T0_cell`).

5. **Post the resting sell — TWO parallel scenarios.** Per SIMONS_MODE Section 6 the load-bearing question is whether post-time vs fill-time cell determination matters. Both are simulated in parallel:
   - **Scenario A (post-time target):** sell at `T0_cell.exit_target` where `exit_target = fill_price + policy_threshold_dollars` per Layer B's `evaluate_policy` semantics, using `T0_cell`'s policy parameters.
   - **Scenario B (fill-time target):** sell at `fill_time_cell.exit_target` using the cell-state observed at fill_time. If `fill_time_cell == T0_cell`, scenarios A and B post the same sell price (no drift); if they differ, the targets diverge.
   
   For policy types that are not threshold-based (time_stop, trailing): scenario A applies the policy's parameters as set at T0; scenario B applies the policy's parameters as set at fill_time. For settle-horizon time_stops, A and B converge by construction.

6. **Walk g9_trades forward from fill_time looking for the kiss.** Continue streaming g9_trades with `created_time >= fill_time` ordered ascending. For each trade:
   - **Scenario A exit check:** if `taker_side == "no"` (taker sells; our resting sell would fill) and `yes_price >= scenario_A_target`, scenario A exits. Record `exit_time_A`, `exit_price_A`, `capture_A_dollars = exit_price_A - fill_price`.
   - **Scenario B exit check:** same logic against `scenario_B_target`. Both scenarios may fire at different trades.
   - **Horizon:** if neither has fired by `fill_time + policy.horizon_minutes` (per the policy's horizon, mirroring `evaluate_policy`), record outcome at horizon. Time-stop policies fire at horizon for both scenarios.
   - **Settlement:** if the market settles before either fires, record `outcome = "settled_unfired"`, `capture = settlement_value - fill_price`.

7. **Record per-moment outcome.** For this (cell, policy, ticker, T0) tuple:
   - `outcome_A`, `capture_A_dollars`, `time_to_exit_A_minutes`
   - `outcome_B`, `capture_B_dollars`, `time_to_exit_B_minutes`
   - `time_to_fill_minutes = (fill_time - T0) / 60`
   - `cell_drift_at_fill` (boolean: did the cell still match at fill_time?)
   - `fill_price`, `fill_time_unix`
   - `T0_cell_key`, `fill_time_cell_key` (the two cell keys for diagnostic-only audit)

8. **Apply the fee schedule (Cat 2 / layer_c_v1 empirical_fee_table).** Compute `entry_fee_dollars` (maker fee at fill_price, is_taker=False) and `exit_fee_dollars` (maker fee at exit_price for scenarios that exited via maker fill; taker fee for time_stop horizon exits). Compute `capture_A_net_dollars` and `capture_B_net_dollars` by subtracting per-leg fees. Per layer_c_spec.md Decision 1: tennis-tier filtered fee table required (multi-sport corpus contamination risk). v1 uses Cat 2 fee table directly if `data/durable/layer_c_v1/empirical_fee_table.json` is not yet built; otherwise uses the persisted layer_c artifact.

9. **Aggregate across all moments for this (cell, policy).** Produce per-candidate summary: count of moments, fill rate, mean/p10/p25/p50/p75/p90 of capture_A_net and capture_B_net, mean time_to_fill, mean time_to_exit (per scenario), cell-drift distribution, win rate (capture_*_net > 0).

### 3.2 Cell-target convention — resolved

The post-vs-fill scenario distinction (step 5) is the load-bearing convention question. Layer B v1's `evaluate_policy` is fill-time-anchored: thresholds are computed against `entry_ask_dollars` (the ask at the entry moment) and the cell at the entry moment determines policy parameters. **Forensic replay v1 evaluates BOTH conventions in parallel** because the post-fill-vs-fill-time gap is itself an empirical unknown — Layer B's fill-time convention assumes the cell at the entry moment is the cell to which the policy applies, but in reality our maker bid is *posted* against the cell at posting time and *filled* at some later moment when the cell may have drifted. Section 6's two-scenario design measures whether this drift matters.

If A vs B captures agree across the candidate set (correlation ≥ 0.95, mean delta < $0.005), Layer B's fill-time convention is empirically validated and v2 strategies can use either with confidence. If they diverge, the bot has a real production decision: post-time-anchored exit policy (commit at posting) vs fill-time-anchored exit policy (re-evaluate at fill).

---

## 4. Outputs

Output directory: `data/durable/forensic_replay_v1/`

### Output 1: Per-moment replay tape (parquet)

`data/durable/forensic_replay_v1/replay_tape.parquet`

One row per (candidate_id, ticker, T0_unix). Schema:

- `candidate_id` (string) — composite of (channel, category, entry_band, spread_band, volume_intensity, policy_type, policy_params); 1:1 with the 80 candidates.
- `ticker` (string)
- `T0_unix` (int64) — entry moment in unix seconds
- `T0_cell_key` (string)
- `fill_time_unix` (int64, nullable — null if unfilled)
- `fill_price_dollars` (float64, nullable)
- `fill_time_cell_key` (string, nullable)
- `cell_drift_at_fill` (bool, nullable) — did `T0_cell_key == fill_time_cell_key` at fill time
- `time_to_fill_minutes` (float64, nullable)
- `outcome_A` (string) — one of {fired_at_target, horizon_expired, settled_unfired, unfilled}
- `capture_A_gross_dollars` (float64, nullable)
- `capture_A_net_dollars` (float64, nullable) — fee-adjusted
- `time_to_exit_A_minutes` (float64, nullable)
- `outcome_B` (string)
- `capture_B_gross_dollars` (float64, nullable)
- `capture_B_net_dollars` (float64, nullable)
- `time_to_exit_B_minutes` (float64, nullable)
- `entry_fee_dollars` (float64)
- `exit_fee_A_dollars` (float64, nullable)
- `exit_fee_B_dollars` (float64, nullable)

Expected size: 80 candidates × ~thousands of moments per candidate × ~150 bytes/row → low single-digit MB. Comfortable.

### Output 2: Per-candidate summary (parquet)

`data/durable/forensic_replay_v1/candidate_summary.parquet`

One row per candidate (80 rows). Schema mirrors Layer B v1 + adds the realized columns:

- All Layer B v1 cell-key + policy + simulated columns (channel, category, entry_band_lo/hi, spread_band, volume_intensity, policy_type, policy_params, n_simulated, fire_rate, capture_mean, capture_p10/p25/p50/p75/p90, capital_utilization).
- `n_replay_moments` (int) — moments evaluated in forensic replay
- `replay_fill_rate` (float) — fraction of moments where the maker bid filled
- `replay_capture_A_gross_mean`, `replay_capture_A_gross_p10/p25/p50/p75/p90` (float)
- `replay_capture_A_net_mean`, `replay_capture_A_net_p10/p25/p50/p75/p90` (float)
- `replay_capture_B_gross_mean`, `replay_capture_B_gross_p10/p25/p50/p75/p90` (float)
- `replay_capture_B_net_mean`, `replay_capture_B_net_p10/p25/p50/p75/p90` (float)
- `replay_win_rate_A`, `replay_win_rate_B` (float) — fraction of moments with capture_*_net > 0
- `replay_time_to_fill_p50`, `replay_time_to_exit_A_p50`, `replay_time_to_exit_B_p50` (float)
- `cell_drift_rate` (float) — fraction of fills where cell drifted between T0 and fill_time
- `simulated_vs_realized_delta_A`, `simulated_vs_realized_delta_B` (float) — `capture_mean - replay_capture_*_net_mean`

### Output 3: A-vs-B comparison (parquet)

`data/durable/forensic_replay_v1/scenario_comparison.parquet`

One row per candidate. Schema:

- `candidate_id`
- `corr_A_B` — Spearman rank correlation between capture_A_net and capture_B_net across moments
- `mean_delta_A_B` — mean(capture_A_net - capture_B_net)
- `cells_diverged_count` — count of moments where cell_drift_at_fill is true
- `cells_diverged_pct` — `cells_diverged_count / n_replay_moments`

### Output 4: Cell-drift distribution (parquet)

`data/durable/forensic_replay_v1/cell_drift_per_minute.parquet`

For each candidate, per minute relative to T0 (0 to 240), the count of moments where the cell still matches at that minute. Schema:

- `candidate_id`
- `minutes_since_T0` (int, 0-240)
- `n_moments_total` (int)
- `n_moments_cell_still_matches` (int)
- `pct_still_matches` (float)

Outputs cell-drift dynamics directly: how fast does the cell decay from the post moment?

### Output 5: Run summary (json)

`data/durable/forensic_replay_v1/run_summary.json`

Producer metadata: runtime, candidate count, total moments, total fills, sha256 of inputs, git commit, free-RAM at start/end.

---

## 5. Producer architecture

`data/scripts/build_forensic_replay_v1.py` — single-file producer; uses `cell_key_helpers.py` (shared with Layer A/B). 

### 5.1 Compute envelope (RAM-constrained)

**Per disk probe (Session 9, May 6 ET):** RAM = 1.9 GiB total, ~1.3 GiB effective (102 MiB free + 1.4 GiB buff/cache available); swap 863 MiB used out of 2 GiB (43%). Live trading bots and daemons account for the baseline. Forensic replay must operate in <500 MiB working memory to avoid swap-thrash.

**Naive approach (rejected):** load g9_trades fully (1.5 GB) or build per-(ticker, time-bucket) trade-tape index in memory. Both OOM-thrash on this VPS.

**Chosen approach: per-candidate streaming.** For each of 80 candidates, the producer:

1. Loads the candidate's cell sample (the tickers from sample_manifest.json that match the cell key).
2. For each ticker in the sample, reads g9_candles filtered to that ticker (small — 82 MB total candles file divided across 20K tickers ≈ ~4 KB per ticker).
3. Identifies entry moments (cell-matching minutes) via Layer B's `walk_trajectory` logic.
4. For each entry moment, reads g9_trades filtered to (ticker, created_time >= T0) using parquet predicate pushdown. Streams trades row-by-row.
5. Walks the trade tape per Section 3.1 steps 3-8. Per-moment state is small (~ a few floats and timestamps).
6. Writes per-moment output rows incrementally (append to an in-progress parquet writer, flushed every N moments).

**Memory profile:** g9_trades parquet predicate-pushdown reads only the ticker's row groups, not the full file. Per-ticker row group size is bounded by g9_trades's row group structure (per disk probe Section 2 schema bundle — confirms per-row-group sizes are well below RAM ceiling). Working set: one ticker's candles + one ticker's recent trades + per-moment outcome buffer ≈ <100 MB.

**Reference compute envelope:** Cat 7 streamed 33.7M trade rows in 487 seconds (sha256 `501752facfb3e700`); Cat 9 streamed the same in 643s. Forensic replay reads a fraction of g9_trades (predicate-filtered to top-N candidates' tickers only) at most a couple times per candidate. Per-candidate runtime estimate: 5-15 minutes. **Total estimate: 6-12 hours for 80 candidates.** Calibration probe in Section 5.2 verifies before full run.

### 5.2 Phased rollout

- **Phase 1 (calibration probe):** 1 candidate × 100 moments. Smoke-test the per-moment 9-step procedure end-to-end. Validate trade-tape predicate-pushdown actually limits reads. Measure per-moment runtime. Output written to `data/durable/forensic_replay_v1/probe/`. **Runtime budget: <5 minutes.** Gating for Phase 2.
- **Phase 2 (single-candidate full run):** 1 candidate × all moments. Confirms per-candidate runtime estimate scales linearly with moment count. Memory profile validated under realistic load. **Runtime budget: <30 minutes.** Gating for Phase 3.
- **Phase 3 (full run, 80 candidates):** all 80 candidates. **Runtime budget: <12 hours.** Output to `data/durable/forensic_replay_v1/` final paths.

Each phase's output is gated by the prior phase's PASS verdict per LESSONS C28 streaming discipline + LESSONS D11 probe-before-assume.

### 5.3 Logging

Producer writes `data/durable/forensic_replay_v1/build_log.txt` with timestamps, per-candidate runtime, per-candidate moment count, fill rate, memory snapshots (free -h every N candidates), warnings on cell-drift outliers (>50% drift within 5 minutes is a likely producer bug, not strategy signal).

### 5.4 Determinism

Producer is deterministic given fixed inputs. sha256 of inputs (g9_trades, g9_candles, sample_manifest.json, exit_policy_per_cell.parquet, kalshi_fills_history.json) recorded in run_summary.json. Re-running produces byte-identical outputs.

---

## 6. Validation gate (T-coherence-read criteria)

Six checks. PASS verdict requires Checks 1-5 PASS (gating); Check 6 is informative-only (drives v2 prioritization).

**Check 1 (gating): every candidate replay produces ≥ 50 moments.** Fewer than 50 moments per candidate signals that the candidate's cell doesn't have enough market presence to evaluate forensically. PASS criterion: 100% of 80 candidates have n_replay_moments ≥ 50.

**Check 2 (gating): replay_fill_rate is plausible.** Maker fill rate per moment should fall in a physically meaningful range. PASS criterion: every candidate has 0.05 ≤ replay_fill_rate ≤ 0.95. If a candidate has fill_rate < 5%, the maker bid is at an unrealistic price (the cell-band is too narrow to ever fill); if fill_rate > 95%, the bid is set below the bid-floor (always filled, effectively a taker order). Either signals a producer bug or a cell-key bug, not strategy.

**Check 3 (gating): scenarios A and B agree on average.** Per Section 3.2's load-bearing question, A vs B convergence determines whether the post/fill distinction matters. PASS criterion: across all candidates, mean |capture_A_net_mean - capture_B_net_mean| < $0.01 OR the divergence pattern is consistent (one scenario always dominates by direction). If A and B disagree randomly per candidate, the two-scenario methodology is broken. Note: this check does NOT require A and B to be identical — it requires their relationship to be coherent.

**Check 4 (gating): realized capture ≤ simulated capture for the same candidate (ranking preservation).** Layer B v1's `capture_mean` is gross (no fees) and assumes idealized fills (Methodology A: instant fills at limit price); forensic replay's `replay_capture_*_net` is fee-adjusted and uses tick-level fill semantics (a moment fills only if a taker actually crossed at our bid). Realized capture should not systematically exceed simulated capture. PASS criterion: `replay_capture_A_net_mean ≤ capture_mean` for ≥ 90% of candidates. If realized exceeds simulated for >10% of candidates, the producer logic is suspect.

**Check 5 (gating): rank correlation between simulated and realized captures.** Per-channel ranking should hold across simulator → replay. Simulator may overstate the absolute capture, but the *ordering* of candidates by EV should be preserved. PASS criterion: Spearman rank correlation between `capture_mean` and `replay_capture_A_net_mean` across the 80 candidates ≥ 0.75. Below 0.75 signals the simulator and reality disagree on more than ~25% of candidate ordering — Layer B v1's strategic conclusions are not deployment-ready and require simulator refinement before forward use. The 0.75 threshold is calibrated to "mostly agreed but with meaningful tail divergence" rather than "mostly random."

**Check 6 (informative-only): cell-drift dynamics.** For each candidate, plot `pct_still_matches` vs `minutes_since_T0` from Output 4. If most candidates show >50% drift within 30 minutes, the cell-key resolution is fragile — operators posting at T0 should expect to fill into a different cell most of the time. This drives v2 cell-key refinement (e.g., wider entry bands; longer-window spread bands). Result drives v2 prioritization but does NOT gate v1 PASS.

---

## 7. Calibration against kalshi_fills_history.json

Per SIMONS_MODE Section 6 caveat — forensic replay's idealized maker fills (price-touched = filled, no queue model) need a sanity check against the bot's actual realized fills.

**Calibration probe:**

1. Filter `kalshi_fills_history.json` to tennis-tier maker fills (per layer_c_spec.md Decision 1 tennis filter — `market_ticker` prefix in `{KXATPMATCH, KXATPCHALLENGERMATCH, KXWTAMATCH, KXTENNISGS}` or equivalent prefix list; the multi-sport corpus contamination risk is explicit per disk probe finding).
2. For each filtered fill, identify the cell-key at fill time using the same `cell_key_helpers` logic. Bin fills by cell.
3. For cells that overlap with v1's 80 candidates, compare:
   - Empirical fill rate (fraction of bot's posted maker bids that filled, derived from kalshi_fills_history) vs replay_fill_rate.
   - If empirical fill rate is materially lower than replay_fill_rate (delta > 0.2), queue position effects dominate and v2 must add queue modeling. If they agree (delta < 0.1), idealized maker fills are an acceptable v1 approximation.

**Calibration output:** `data/durable/forensic_replay_v1/calibration_vs_kalshi_fills.json`. Reports per-candidate fill-rate delta and overall summary statistic.

This check is informative — does NOT gate v1 PASS — but informs deployment confidence.

---

## 8. Open items for v2 / v3

- **v2: in_match channel.** Add in_match candidates with explicit gap-risk haircut measurement. Methodology extension: between consecutive g9_trades for an in_match ticker, the score may have changed; cell-state at fill time may not be reconstructable from price alone. v2 measures the haircut empirically by comparing in_match capture realizations against simulator predictions.
- **v2: queue position modeling.** If Section 7 calibration shows queue effects dominate, v2 adds explicit queue modeling — at each tick, estimate position in the maker queue based on accumulated bid volume at our price level and only credit a fill when the queue-adjusted position would have been served.
- **v2: relax N or expand to settlement-zone.** Given v1's empirical cell-drift and A-vs-B findings, expand candidate set if the v1 results justify deeper exploration.
- **v3: bilateral (paired-leg) replay.** G12-blocked. Replay simultaneous yes/no leg pairs to measure double-cash empirical rate against Cat 6 / E18 funnel-layer prediction. Validates the ~21-23% unconditional double-cash rate from B23 amendment + E18 funnel completion.
- **v3: per-cell fee derivation.** If layer_c_spec.md Decision 5 promotes (cell-level fee variation observed), forensic replay v3 uses per-(cell, is_taker, price_bucket) fee table.

---

## 9. Cross-references

- **SIMONS_MODE.md Section 6** — origin specification of forensic replay framework. This spec is the operational implementation of Section 6's 9-step procedure.
- **SIMONS_MODE.md Section 7** — rollback question 5 (5%-vs-95% sea discipline at cell-selection level). Forensic replay v1 ranks the top-N tail per channel.
- **SIMONS_MODE.md Section 8** — Cat 5 / Cat 6 / Cat 9 / Cat 10 anchor evidence backfilled this session. Top-cell selection per Cat 5 (commit 8b3a3a6).
- **LESSONS B16** — Layer A / B / C separation principle. Forensic replay sits adjacent to Layer C, not within it.
- **LESSONS B14, E16, E31** — channel preservation (premarket vs in_match are structurally different). v1 evaluates both per-channel; v1 deploys premarket only.
- **LESSONS C28** — streaming discipline on large parquets. Per-candidate streaming approach honors the constraint on this VPS's 1.3 GiB effective RAM.
- **LESSONS C30, D11** — probe-before-assume / read-source-before-spec. This spec is anchored on the `build_layer_b_v1.py` cell-target convention reading + RAM ceiling probe + kalshi_fills_history.json field schema.
- **LESSONS C31** — mechanism-coherent hypothesis ≠ empirical alpha presence. Forensic replay validates Layer B v1's simulator outputs against tick-level reality; Check 4 + Check 5 are the validation gates.
- **LESSONS E12** — premarket has internal phases. v1 inherits Layer B's regime taxonomy (premarket / in_match / settlement_zone) without sub-phase split; layer_c_spec.md Check 5 (formation contamination) is the parallel measurement.
- **LESSONS E16 amended (commit 8b3a3a6)** — three-frame disambiguation of premarket vs in_match. Forensic replay v1 selects from top-tail (frame 3) not aggregate (frame 2); per-channel ranking, not pooled.
- **LESSONS E18 amended (commit 35092f3)** — bilateral funnel layers. Forensic replay v1 is single-leg; bilateral replay is v3 contingent on G12.
- **LESSONS E20** — per-cell treatment, no global config. Output is strictly per-(cell, policy).
- **LESSONS E27, E28** — methodology drift. v1 designates ONE canonical replay procedure (Section 3); future v2/v3 extend, do not replace.
- **LESSONS F31 amended (commit 9c93505)** — OI partially tracked at g9_candles.open_interest_fp. v1 does not consume OI; v2 may add OI as a cell-stratification dimension.
- **LESSONS F33** — depth-chain measurement gap. v1 idealizes maker fills; queue modeling is v2 if Section 7 calibration flags it.
- **LESSONS G1** — ROI on cost basis. capture columns are dollars per unit contract; ROI conversion is downstream consumer responsibility.
- **layer_b_spec.md** — sibling spec; v1 forensic replay consumes Layer B v1's `exit_policy_per_cell.parquet` as candidate input.
- **layer_c_spec.md** — sibling spec; v1 forensic replay consumes Layer C v1's `empirical_fee_table.json` for net-EV computation if available; otherwise applies Cat 2 fee table directly with tennis-tier filter.
- **ANALYSIS_LIBRARY.md Section 4** — Cat 2 fee table anchor (commit 67eb076) is the empirical fee schedule v1 depends on; Cat 5 anchor (commit 8b3a3a6) is the top-tail-cell distribution v1 selects from.

---

*Spec authored 2026-05-06 ET (Session 9). Closes the SIMONS_MODE Section 6 first-deliverable forward reference when committed and producer (build_forensic_replay_v1.py) implementation lands.*
