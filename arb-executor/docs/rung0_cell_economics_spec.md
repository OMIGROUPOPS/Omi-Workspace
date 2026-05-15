# Rung 0 Spec — Canonical Exit-Optimized Cell Economics

**Status:** Draft v0.1 — DECISIONS NAMED INLINE, resolution required before producer build.
**Anchored to:** per_minute_universe_spec.md (T37 foundation, checkpoint 3 sha256 9fde4b5d…); LESSONS E32 (locked cell/exit model); recomputation_ladder.json Rung 0; TAXONOMY Section 2.5 (GRAIN / VECTOR / OBJECTIVE).
**Output:** `data/durable/rung0_cell_economics/cell_economics.parquet`
**ROADMAP:** T39 chain.

---

## 1. Scope

Rung 0 produces the canonical exit-optimized per-cell economics table on the FOUNDATION-TIER corpus. It is the primitive that absorbs the six legacy entries (`baseline_econ`, `rebuilt_scorecard`, `pnl_by_cell_config`, `per_cell_real_economics`, `comparison_real_vs_analysis`, `post_retune_economics` base metrics) and closes LESSONS E27 (methodology drift cluster). All downstream rungs depend on this table; nothing else gets built first.

### 1.1 In scope
- Cell key = (category, T-20m price band). Grain (per-cell aggregated vs per-(cell, N)) is DECISION 1.
- Entry assumption: conservative humble entry at T-20m mark, every N eligible (tightness as cell attribute, not gate — per E32).
- Exit-optimized scoring: realized bounce from T-20m fill to an exit target.
- Average bounce per cell band as the headline metric; full judgment-metric set from ANALYSIS_LIBRARY.
- Phase attribution columns (PHASE_1/2/3/4 from per_minute_universe_spec Section 7 v0.2 classifier).
- Four categories (WTA Main / WTA Challenger / ATP Main / ATP Challenger); every output stratified across all four.

### 1.2 Out of scope (deferred to higher rungs)
- Exit target *selection* per band — Rung 1.
- Policy layer (DCA, limit/trailing/time_stop) — Rung 3.
- Anchor recomputation (70.7%, 977-fill P&L, etc.) — Rung 2.
- Fees, capital, queue position, sizing — downstream / Layer C.

---

## 2. The cell key

### 2.1 Definition
A cell is `(category, price_band_at_T-20m)`. Per E32: the cell is the N's Kalshi price at a fixed T-20m mark, one axis (price), partitioned by the four categories. Direction is NOT an axis (N and its inverse are two faces of one event).

### 2.2 Categories
Four, partitioning every output: `WTA_MAIN`, `WTA_CHALL`, `ATP_MAIN`, `ATP_CHALL`. The fifth `OTHER` bucket from `cell_key_helpers.CATEGORIES` is empirically empty in the tennis corpus — exclude it. If any ticker categorizes as `OTHER`, fail loud.

### 2.3 Price band

**DECISION 1 — Cell aggregation grain.** Two options:
- **Option A: per-cell aggregation (one row per (category, band) pair).** ~4 categories × ~10-20 bands = 40-80 rows. Compact; loses per-N detail.
- **Option B: per-(cell, N) grain (one row per N).** ~19,207 rows. Per-N detail preserved; cell aggregation becomes a downstream groupby; matches the T37 doctrine (no pre-aggregation, groupbys at consumption).

Lean **Option B** — matches the T37 validity-gate principle exactly, and Rungs 1/2/3 all need per-N detail.

### 2.4 Price band width

**DECISION 2 — Band width.**
- **5¢ bands** (0-5, 5-10, …, 95-100): 20 bands per category, ~80 cells total. Back-compatible with the legacy `cell_lookup` bucketing.
- **10¢ bands**: 10 bands per category, ~40 cells total. Coarser; more N's per cell.
- **Adaptive bands** by quantile within category. Statistically clean; back-incompatible.

Lean **5¢** — back-compat matters, and 5¢ is the granularity the operation has visually anchored on.

### 2.5 The T-20m anchor — exact column source
The N's price at T-20m comes from `per_minute_features.parquet`. The row to read is the one where `minute_ts == match_start_ts - timedelta(minutes=20)`. Price = `mid_close` at that row.

**DECISION 3 — Behavior when T-20m row doesn't exist.**
- **Option A**: drop the N (no cell assignment).
- **Option B**: use the nearest available minute within a tolerance window (e.g. ±2 min) + record method per N.
- **Option C**: forward-fill from the most recent earlier minute.

Lean **Option B with ±2-min tolerance + `t20m_anchor_method` column**. Honest, recoverable, auditable.

---

## 3. The exit-optimized objective — operational definition

### 3.1 What "exit-optimized realized bounce" means
Per LESSONS E32: highest risk-adjusted return from fill to exit. No stop — two outcomes only: reach the exit target, or ride to settlement.

For each N with a valid T-20m anchor:
- **Entry price** = `mid_close` at T-20m (or per Decision 3 fallback).
- **Entry assumption** is Decision 4.

**DECISION 4 — Entry mode for v0.1.**
- **Option A: taker buy at T-20m `mid_close`.** Pessimistic, clean, no fill-probability modeling. Matches "conservative humble" framing.
- **Option B: maker bid at `mid_close - 1¢` with fill-probability gate.** Realistic for the bot's actual mechanism; introduces a per-cell fill-probability term.
- **Option C: produce both side-by-side with an `entry_mode` column.**

Lean **Option A for v0.1** — getting the primitive built and validated matters more than fidelity to the bot's exact mechanism; Rung 3 handles fill-probability modeling. Taker-at-mid is honest and complete.

### 3.2 The forward tape per N
Once entry is set, the per-minute foundation already carries forward-looking labels: `max_yes_bid_forward_{5,15,30,60}min`, `min_yes_ask_forward_*`, `bounce_to_match_start`, `bounce_to_settlement`. Rung 0 reads them directly at the T-20m row; no need to walk the tape independently.

### 3.3 The exit grid (parameterizes Rung 1 already)
Rather than commit to a single exit threshold, Rung 0 emits per-N realized bounce **at a grid of exit targets**. For each N, for each `exit_c ∈ {5, 10, 15, 20, 25, 30, 35, 40}`:
- `bounce_realized_at_exit_c` = realized exit cents if a bid ≥ `entry + exit_c` is ever reached; else realized terminal value (`settlement_value_dollars - entry_price`).
- `hit_at_exit_c` = bool.
- `time_to_exit_at_exit_c` = minutes from T-20m to first hit, or NULL.
- `exit_window_at_exit_c` = `"premarket"` / `"in_match"` / `"settled_unhit"`.

This grid IS Rung 1's input — Rung 1's exit-sweep curve is just `bounce_realized_at_exit_c` grouped by cell over the grid.

**DECISION 5 — Exit grid range.** Proposed 5-40c. Per E32: ~95¢ band fails on geometry, ~5¢ on traction. Lean tight to plausible range to keep compute bounded.

### 3.4 Settlement reconstruction
LESSONS F8 (bot-side missing settlement events) does NOT bite here. Rung 0 reads `bounce_to_settlement` and `settlement_value_dollars` from the trade-tape ground truth in the foundation corpus, not from bot logs.

---

## 4. Output schema

One row per (cell, N) — pending Decision 1 → Option B.

### 4.1 Identity columns
`ticker`, `event_ticker`, `category`, `match_start_ts`, `settlement_ts`, `settlement_value_dollars`

### 4.2 T-20m anchor
`t20m_ts`, `t20m_anchor_method`, `entry_price`, `entry_mode`, `price_band`, `cell_key` (`{category}__{price_band}`)

### 4.3 Phase state at T-20m
`phase_state_at_t20m`, `spread_close_at_t20m`, `pair_gap_abs_at_t20m`, `mid_close_at_t20m` (tightness-as-cell-attribute preserved per E32)

### 4.4 The exit grid (per Decision 5: 5-40c)
For each `exit_c`: `bounce_realized_at_{exit_c}c`, `hit_at_{exit_c}c`, `time_to_exit_at_{exit_c}c_min`, `exit_window_at_{exit_c}c`

### 4.5 Settlement outcome
`settlement_outcome` (`"yes_win"` / `"no_win"` / `"scalar"` — exclude scalars), `bounce_to_settlement`, `realized_at_settlement` (`settlement_value_dollars - entry_price`)

### 4.6 Statistical
`n_minutes_from_t20m_to_settlement`, `paired_event_partner_ticker` (for Rung 2 paired-leg analysis)

---

## 5. Validation gates

### Hard gates
1. **Cell-assignment coverage:** every binary-outcome ticker in g9_metadata with a valid T-20m anchor lands in exactly one cell.
2. **Exit grid coherence:** `hit_at_5c ≥ hit_at_10c ≥ … ≥ hit_at_40c` for every N (monotone in threshold). Zero violations.
3. **Settlement consistency:** `realized_at_settlement = settlement_value_dollars - entry_price` exactly per N. Zero drift.
4. **Phase-state validity:** every `phase_state_at_t20m` is one of the four canonical labels.

### Informative measurements
- Distribution of `t20m_anchor_method` across the 4 categories (Decision 3 dropout rate per category).
- Per-cell N-count distribution (feeds Rung 1's per-band CI work).
- Distribution of `phase_state_at_t20m` per category — sanity check that T-20m IS the converged zone (predominantly PHASE_2/PHASE_3, not PHASE_1).

---

## 6. Producer architecture

Same shape as T37 producer: per-ticker streaming, kill-resilient incremental writes, phased rollout.

- **Input:** `per_minute_features.parquet` (read-only).
- **Phase 1:** single ticker — KXATPMATCH-25JUN18RUNMCD-RUN — visual inspection PASS criterion.
- **Phase 2:** ~160 paired tickers stratified by category × premarket-length quartile.
- **Phase 3:** full corpus (~19,207 binary-outcome tickers).
- **Output:** `data/durable/rung0_cell_economics/cell_economics.parquet`.
- **Validation report:** `cell_economics_validation_report.md`.

Runtime estimate: per-ticker work is a single-row read + constant-time exit-grid eval ≈ milliseconds. 19,207 × ~5ms = ~100 seconds total. Fast because the per-minute foundation already did the expensive work; Rung 0 just reads the T-20m row and the forward-label columns.

---

## 7. Cross-references
- Foundation: per_minute_universe_spec.md (T37); per_minute_features.parquet checkpoint 3 sha256 `9fde4b5d…`.
- Cell model: LESSONS E32.
- Classification axes: TAXONOMY Section 2.5.
- Ladder context: recomputation_ladder.json Rung 0; ROADMAP T39.
- Phase classifier: per_minute_universe_spec.md Section 7 v0.2.

---

## 8. Open decisions summary (must resolve before producer build)

1. **DECISION 1** — Per-cell aggregation grain (per-cell pre-aggregated / per-(cell, N)). Leaning per-(cell, N).
2. **DECISION 2** — Price band width (5¢ / 10¢ / adaptive). Leaning 5¢.
3. **DECISION 3** — T-20m row fallback when exact minute missing (drop / nearest-±2min / forward-fill). Leaning nearest-±2min with method column.
4. **DECISION 4** — v0.1 entry-mode (taker-at-mid / maker-with-fill-prob / both). Leaning taker-at-mid for v0.1; Rung 3 handles fill probability.
5. **DECISION 5** — Exit grid range (5-40c proposed). Leaning as proposed.

None of these are blocking for the spec to land in v0.1 with them named-and-pending. They block the producer build (T39 implementation).
