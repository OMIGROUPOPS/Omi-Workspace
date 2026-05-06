# Layer C v1 specification — realized economics from empirical fees

**Authored:** 2026-05-05 ET (Session 8, T32a)
**Foundation:** T28 ea84e74 (G9 parquets) + T29 1398c39 (Layer A v1 cell_stats) + T31b 28e8ab7 (Layer B v1 exit_policy_per_cell.parquet) + A30 (kalshi_fills_history.json as canonical execution truth)
**Layered staging:** Per LESSONS B16. Layer C has its own v1/v2/v3/v4 sub-staging per Session 7→8 handoff. v1 adds ONE modeling concept (empirical fees) on top of Layer B's idealized-fill capture distributions.
**v1 status:** PRE-IMPLEMENTATION. T32a closes when this spec lands and is referenced in ANALYSIS_LIBRARY. T32b (producer) and T32c (coherence read) follow.

---

## 1. Scope (v1)

**One concept added:** empirical fees per fill, derived from the bot's own historical fill record at data/durable/kalshi_fills_history.json. Fee schedule is parabolic per Kalshi's published rules (fee = coefficient × P × (1−P), where P is contract price in dollars), but **NOT zero for makers** — empirical fee_cost on bot's own maker fills shows 37.7% non-zero rate with a parabolic shape consistent with a maker coefficient roughly 25% of the taker coefficient. Layer C v1 derives the fee per fill empirically from this distribution; no a-priori "maker is free" assumption is permitted (per LESSONS A4: per-cell empirical math, no global assumption).

**Out of scope for v1** (each its own future T32 sub-version; per LESSONS B16 layered staging):
- v2: entry fill probability (does the maker post fill?). From g9_trades streaming join per LESSONS C28.
- v3: exit fill probability (does the maker exit fill before settlement / horizon?).
- v4: capital constraints, concurrent positions, portfolio-level realism.
- Layer D (separate from Layer C entirely): bot-execution policy, taker-fallback near-game-start, queue position, partial fills.

**v1 idealized-fill assumption** (inherited from Layer B v1, NOT relaxed): every (cell, policy) trajectory in Layer B's parquet assumes entry filled at the cell's entry_ask_close and exit filled at the policy's exit price (limit threshold or time-stop horizon-minute close). v1 does NOT model whether those fills actually would have occurred; that's v2/v3 work.

**v1 strictly per-cell output** (per LESSONS E20: each cell requires its own treatment, no global config).

**v1 single-leg only** (per LESSONS E18: bilateral capture analysis is G12-blocked; v1 does not model paired YES/NO leg capture).

**v1 channel preservation** (per LESSONS E16, B14, E31: premarket and in_match are structurally different opportunities with 5-10x economic-edge separation; Layer C v1 must report per-channel, never aggregate across channels).

---

## 2. Foundation pointers

- **G9 parquets** (T28 ea84e74, sha256-pinned in MANIFEST): g9_metadata, g9_candles, g9_trades. v1 does not consume g9_trades directly (that's v2); v1 consumes only via Layer B's already-computed cell aggregations.
- **Layer A v1 cell_stats** (T29 1398c39): per-cell bounce distributions. Layer C v1 reads bounce_60min_mean for the formation-contamination Check 5 cross-reference; does not otherwise consume.
- **Layer B v1 exit_policy_per_cell.parquet** (T31b 28e8ab7, sha256 d94bc56c..., validated by T31c PASS at 5cf45e0): primary input. 19,170 rows, per (cell, policy) capture distributions assuming idealized fills.
- **kalshi_fills_history.json** (per A30: canonical execution truth, supersedes matches.matches and all local logs; per E29: closes A26 + F8 + F9 + F10 + F17): source of empirical fee distribution. 7,489 fills. Schema: action, count_fp, created_time, fee_cost, is_taker, market_ticker, side (yes/no), yes_price_dollars, no_price_dollars, ts, order_id, fill_id, trade_id.

---

## 3. Operational decisions

**Decision 1: Fee derivation methodology.** Empirical, not theoretical. For each fill in kalshi_fills_history.json restricted to tennis tiers (ATP, ATP_CHALL, WTA, TENNIS_GS), bucket by (is_taker, yes_price_dollars rounded to nearest cent). Compute median fee_cost per bucket. This bucket-median fee is applied to each (cell, policy) row's entry leg and exit leg in the producer.

Rationale: the bot's own historical fill record is canonical execution truth (A30) and includes Kalshi's actual schedule (which has heterogeneity — some tennis markets carry maker fees, others don't, per Kalshi help center). Deriving from observed fills captures both the parabolic schedule AND any tier-or-market-specific maker-fee differences without our needing to model them separately.

Reject alternative: published fee schedule. Sacra says "maker = $0", MarketMath says "maker ≈ 25% of taker". The literature disagrees because Kalshi's fee schedule has per-market heterogeneity. Use disk-of-truth from bot fills, not literature.

**Decision 2: Maker-vs-taker disposition per policy class.** For each (cell, policy) row in Layer B output, classify the entry and exit legs as maker or taker. Operator-stated production constraint (Session 7 conversation): both legs are maker by design. Cross-the-spread (taker) only happens as a near-game-start fallback when a maker post hasn't filled, and that fallback lives at Layer D (bot-execution policy), not Layer C.

Therefore for Layer C v1:
- **Entry leg:** maker for all policies.
- **Exit leg by policy class:**
  - Limit policies (38 of 54): exit is maker (passive sell at limit price). Maker fee applies.
  - Time-stop policies (8 of 54, post T31a patch 6): exit is taker by definition (forced cross at horizon expiry). Taker fee applies.
  - limit_time_stop policies (8 of 54): conditional. If fired on the limit leg, maker exit. If fired on the time-stop leg, taker exit. Producer must distinguish using Layer B's existing fired-policy-counts columns.
- **Settled-unfired trajectories:** no exit trade (settles at $0 or $1, no fee event). entry-leg fee was paid; exit-leg fee = $0.

**Decision 3: Output unit.** Per (cell, policy) row, mirroring Layer B's grain. Does NOT add posting_strategy as a sweep dimension (operator constraint: maker-maker only is the production model; taker-fallback is Layer D's job). Does NOT add capital_size as a sweep dimension (v4).

Layer C v1 is a 1:1 row mapping with Layer B's 19,170 rows, plus added columns.

**Decision 4: Output schema additions to Layer B's columns.** Add the following per (cell, policy):
- `entry_fee_dollars`: empirical maker fee at entry_ask_close price (Decision 1 lookup).
- `exit_fee_dollars`: weighted average across the trajectory's outcomes — n_fired * fired_exit_fee + n_horizon_expired * horizon_exit_fee + n_settled_unfired * 0 (no exit fee on settlement). Where fired_exit_fee depends on policy class per Decision 2.
- `realized_capture_mean_dollars`: capture_mean - entry_fee - exit_fee.
- `realized_capture_p10_dollars`, `realized_capture_p25_dollars`, ..., `realized_capture_p90_dollars`: percentiles on the same fee-adjusted basis.
- `realized_capture_pct_of_cost_basis`: realized_capture_mean / entry_ask_close. Per LESSONS G1 (operator-stated: ROI on cost basis, not raw dollars).
- `policy_class_taker_exposure_flag`: enum {pure_maker, mixed_horizon_taker, pure_horizon_taker} for downstream analytical convenience.
- `formation_contamination_window_minutes`: per Check 5 (Decision 6), exposes formation-period stratification metadata; not a primary economic metric.

**Decision 5: Cell-level fee derivation refinement (deferred to v2 if needed).** Decision 1 derives fee per (is_taker, yes_price_bucket) globally. v1 does not stratify fee derivation by cell. If v1 coherence read shows fee distributions vary materially by cell-key dimensions (channel, category, regime), v2 spec adds per-(cell, is_taker, price_bucket) derivation.

**Decision 6: Formation-period contamination — Check 5 strategy (per E12).** Layer A v1 regime classification has 3 buckets (premarket / in_match / settlement_zone). Per LESSONS E12, premarket has internal phases (pre-formation / formation period / post-formation) that Layer A does not separate. The bot's 4-hour entry gate operationally discriminates pre/post-formation; Layer A v1 does NOT model this gate. Layer B v1 inherits the conflation; Layer C v1 inherits it from Layer B.

**v1 disposition: option (a)+Check-5.** v1 inherits the conflation explicitly (no entry-time filter; no upstream re-run). v1 adds a coherence-read Check 5 that *measures* whether pre-formation entries materially distort premarket cell capture distributions, by computing entry_minutes_since_market_open per entry moment (g9_metadata join) and comparing capture_mean for entries within first 4 hours of market open vs entries after 4 hours, within premarket cells.

If Check 5 shows formation contamination is statistically meaningful (e.g., capture_mean differs by > some threshold across the 4-hour boundary in > 20% of premarket cells), v2 inherits a clear mandate to add formation-regime split at Layer A producer level. If Check 5 shows minimal contamination, v1 premarket cells are usable as-is.

Check 5 is **gating-INFORMATIVE** (does not block T32c PASS verdict, but its result determines v2 prioritization).

---

## 4. Output schema

Output: `data/durable/layer_c_v1/realized_economics_per_cell.parquet`

Columns (inherited from Layer B + new):

**Cell key (6 columns, inherited):** channel, category, entry_band_lo, entry_band_hi, spread_band, volume_intensity.

**Policy (2 columns, inherited):** policy_type, policy_params.

**Layer B inherited counts (4 columns):** n_simulated, n_fired, n_horizon_expired, n_settled_unfired.

**Layer B inherited capture distributions (8 columns):** fire_rate, capture_mean, capture_p10, capture_p25, capture_p50, capture_p75, capture_p90, median_time_to_fire.

**Layer B inherited misc (1 column):** capital_utilization.

**Layer C v1 added (10 new columns):**
- entry_fee_dollars
- exit_fee_dollars
- realized_capture_mean_dollars
- realized_capture_p10_dollars
- realized_capture_p25_dollars
- realized_capture_p50_dollars
- realized_capture_p75_dollars
- realized_capture_p90_dollars
- realized_capture_pct_of_cost_basis
- policy_class_taker_exposure_flag

**Layer C v1 metadata column (1 new column):**
- formation_contamination_window_minutes (per Check 5)

**Total schema: 32 columns, ~19,170 rows** (1:1 with Layer B).

Companion artifact: `data/durable/layer_c_v1/empirical_fee_table.json` — the per-(is_taker, price_bucket) fee table derived from kalshi_fills_history.json under Decision 1. sha256-pinned in MANIFEST. Producer-immutable input to all downstream Layer C economics.

---

## 5. Producer architecture

`data/scripts/build_layer_c_v1.py` — single-file producer, no shared helpers needed beyond cell_key_helpers.py (already shared with Layer A/B). Memory profile is small (Layer B parquet is 646 KB, fills JSON is 4.5 MB, no g9_trades or g9_candles consumed in v1).

**Phases:**
1. Load Layer B parquet (Pandas DataFrame, full materialize OK at this size).
2. Load kalshi_fills_history.json. Filter to tennis tiers (ATP / ATP_CHALL / WTA / TENNIS_GS). Build empirical fee table per (is_taker, yes_price_bucket_cents). Persist to empirical_fee_table.json.
3. For each Layer B row, compute entry_fee_dollars (lookup at entry_ask_close, is_taker=False per Decision 2 entry-leg constraint) and exit_fee_dollars (weighted by trajectory outcomes per Decision 2 exit-leg classification).
4. Compute realized_capture columns by subtracting fee columns from Layer B's capture columns. Compute realized_capture_pct_of_cost_basis.
5. Compute Check 5 metadata: for each premarket cell, run a streaming pass over g9_metadata + Layer A v1 cell_stats to compute formation_contamination_window_minutes (planned: stratify entries into pre-/post-4-hour, compute capture_mean delta).
6. Write parquet. Log row count, fee-table row count, runtime.

**Streaming discipline (per LESSONS C28):** v1 producer does not consume g9_trades or g9_candles directly. Memory-safe by construction.

**Output validation:** producer prints per-cell-key-dim row count match with Layer B (must be 1:1) before writing.

---

## 6. Validation gate (T32c coherence-read criteria)

Five checks. PASS verdict requires Checks 1-4 PASS (gating); Check 5 is informative-only (does not block PASS, drives v2 prioritization).

**Check 1 (gating): realized_capture ≤ capture for every (cell, policy) row.** Fees are non-negative; realized capture cannot exceed pre-fee capture. PASS criterion: 100% of rows satisfy.

**Check 2 (gating): empirical fee schedule matches Kalshi's parabolic shape.** Compute Spearman rank correlation between yes_price_bucket and median fee_cost per bucket within each is_taker stratum. Both maker and taker should show parabolic shape (rho > 0 for prices < 50¢, rho < 0 for prices > 50¢; or equivalent: |rho| against |P-0.50|). PASS criterion: maker fees and taker fees both exhibit parabolic shape, taker median exceeds maker median at the 50¢ peak by a factor of ≥ 3 (consistent with published 4:1 taker:maker ratio).

**Check 3 (gating): policy class taker-exposure flag matches policy taxonomy.** Limit policies → pure_maker. Time-stop policies → pure_horizon_taker. limit_time_stop policies → mixed_horizon_taker. PASS criterion: 100% taxonomic match across all 19,170 rows.

**Check 4 (gating): Layer B → Layer C ranking preservation per cell.** Within each cell, rank-correlate Layer B's capture_mean with Layer C's realized_capture_mean_dollars across the 54 policies. PASS criterion: ≥ 90% of cells have Spearman rho ≥ 0.99 (fees are small relative to capture; ranking should be near-identical). Cells where the correlation drops below 0.99 are interesting: they're cells where fee differentiation between policy classes (limit vs time-stop) outweighs capture differentiation, meaning fee structure dominates strategy choice for those cells.

**Check 5 (informative-only): formation-period contamination in premarket cells.** For each premarket cell with ≥ 50 entry moments, partition entries by entry_minutes_since_market_open ≤ 240 (pre/at-formation) vs > 240 (post-formation). Compute capture_mean delta. If > 20% of premarket cells show |delta| > some threshold (TBD in T32b producer testing; placeholder 1¢), Check 5 returns INFORMATIVE-FLAGGED. Otherwise INFORMATIVE-CLEAN. Result drives v2 prioritization (formation regime split at Layer A producer) but does NOT gate T32c PASS.

---

## 7. Open items for v2 / v3 / v4

- **v2: entry fill probability.** Per (cell, entry_price), historical fraction of moments where bid touched the entry price within the cell's regime window. Streaming join over g9_trades or g9_candles per C28 discipline. Adds entry_fill_prob column.
- **v2: formation regime split (if Check 5 flagged).** Layer A producer adds premarket_pre_formation / premarket_post_formation to regime taxonomy. Cascades through Layer B and Layer C.
- **v3: exit fill probability.** Per (cell, policy, exit_price), historical fraction of forward windows where bid reached exit price before horizon/settlement. Adds exit_fill_prob column. Realized expected value per attempt = entry_fill_prob × exit_fill_prob × realized_capture.
- **v3: per-cell fee derivation.** Decision 5 promotion if v1 shows fee distributions vary materially by cell-key dimensions.
- **v4: capital constraints.** Portfolio-level concurrent-position limit, per-trade size constraint, bankroll fraction sizing. Per E20: per-cell sizing decisions, no global config.
- **G12-blocked: bilateral capture.** Per E18 / E21, strategy goal is bilateral capture (cash both YES and NO sides). Requires per-event paired moments dataset at G12. v2 / v3 of Layer C with G12 enables bilateral analysis.
- **Layer D (separate track):** bot-execution policy. Taker-fallback near-game-start. Queue position. Partial-fill modeling. Not a Layer C concern.

---

## 8. Cross-references

- **B16:** Layer A / B / C separation principle. v1 adds one modeling concept on top of the layer below.
- **B14, E16, E31:** premarket vs in_match are structurally different opportunities, 5-10x economic-edge separation. Layer C v1 preserves channel.
- **A4:** uniform breakeven math across heterogeneous cells is wrong; per-cell empirical math required. Decision 1 + Decision 5 honor this.
- **A30, E29:** kalshi_fills_history.json is canonical execution truth.
- **E12:** premarket internal phases (pre-formation / formation / post-formation). Decision 6 + Check 5 address.
- **E18, E21:** bilateral capture is G12-blocked. v1 single-leg.
- **E20:** per-cell treatment, no global config. Output is strictly per-cell.
- **E27, E28:** methodology drift. v1 designates ONE canonical fee derivation (Decision 1); prohibits alternative fee assumptions in derivative analyses.
- **E30:** aggregate hides stratum-level variation. v1 reports per-cell, never aggregated.
- **G1:** ROI on cost basis, not raw dollars. realized_capture_pct_of_cost_basis column honors this.
- **C27:** every analysis carries its foundational-data dependency explicitly. Foundation pointers section (§2) honors this.
- **C28:** streaming discipline on large parquets. v1 producer does not consume large parquets; constraint inherited for v2+.
- **B21:** MFE vs endpoint-capture metric distinction. v1 inherits Layer B's policy-specific capture semantics; no new MFE/endpoint distinction needed at v1.

---

## 9. Outstanding ROADMAP correction (separate commit)

T32 ROADMAP entry (commit f048267) currently states "v1 scope: empirical fees from bot kalshi_fills_history.json (maker-zero canonical confirmed empirically)." This is empirically wrong (37.7% of bot maker fills are non-zero, parabolic schedule). A follow-up commit must amend the ROADMAP T32 entry to reflect Decision 1's empirical-derivation framing without the maker-zero claim. **This spec is canonical truth; ROADMAP is summary.** ROADMAP correction follows in a separate single-concern commit.

---

*Spec authored 2026-05-05 ET. Closes T32a when committed and referenced in ANALYSIS_LIBRARY. T32b (producer) and T32c (coherence read) follow.*
