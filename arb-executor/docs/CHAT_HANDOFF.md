# Chat Handoff — Next Session Start Doc

**Last updated:** 2026-05-15 ET, post-Rung-0 landing.
**Repo state at handoff:** HEAD at `3f7dc02c` (Plex Rung 1 archive). Prior in arc: `5ca2d89c` (Rung 0 MANIFEST), `807e0a8b` (LESSONS A39).
**Purpose:** Operational scaffolding for the next chat-side session. Not cumulative memory (that's SESSION_HANDOFF.md). Tells the next chat what's currently live, where to read on demand, what's known vs unknown, and what to do first.

Read order for a fresh chat: this doc → SESSION_HANDOFF.md (current state) → LESSONS.md Section 1 → relevant spec/doctrine on-demand only.

---

## Section 1 — Where things stand

**Rung 0 has LANDED.** `data/durable/rung0_cell_economics/cell_economics.parquet` is gate-validated, committed, and pushed.

- sha256: `6fdd019d08722d0afb5688181fb60394d73dc2b05765af74d6c5675edd17c992`
- 14,033 rows × 36 columns, 1.7 MB
- 71.55% coverage on the 19,614 binary-outcome subset (5,581 dropouts: 3,390 no_trade_near_t20m, 1,172 no_match_start, 407 no_pmf_rows, 583 extreme-band-excluded, 29 no_trades)
- All 5 C37 hard gates PASS (anchor consistency, band exclusion, peak monotonicity, settlement consistency, TZ correctness)
- All 72 cells (4 categories × 18 bands) populated; 54 cells n≥100, 8 cells 50≤n<100, 9 cells 30≤n<50, 1 cell n<30 (WTA_CHALL 0.15-0.20 at n=28 — weak-CI flag candidate)
- Phase state distribution at T-20m anchor: PHASE_2_STABLE 10,544 (75.1%), PHASE_3_SURGE 3,401 (24.2%), PHASE_1_FORMATION 88 (0.6%). The cell mark choice (T-20m per E32) is empirically validated by this distribution.

**Headline (top-10 cells by mean peak_bid_bounce_pre_resolution):**

| Rank | Cell | n | Mean bounce | Median | p90 |
|------|------|---|---|---|---|
| 1 | WTA_CHALL 0.30-0.35 | 55 | +33.98¢ | +30.00¢ | +64.60¢ |
| 2 | WTA_MAIN 0.25-0.30 | 204 | +32.90¢ | +26.50¢ | +69.00¢ |
| 3 | WTA_CHALL 0.45-0.50 | 48 | +32.71¢ | +41.00¢ | +50.00¢ |
| 4 | ATP_CHALL 0.40-0.45 | 326 | +32.53¢ | +41.00¢ | +56.00¢ |
| 5 | WTA_CHALL 0.35-0.40 | 61 | +32.08¢ | +36.00¢ | +61.00¢ |
| 6 | ATP_CHALL 0.45-0.50 | 320 | +32.07¢ | +41.00¢ | +51.00¢ |
| 7 | ATP_CHALL 0.15-0.20 | 251 | +31.76¢ | +20.00¢ | +79.00¢ |
| 8 | WTA_MAIN 0.30-0.35 | 217 | +31.59¢ | +30.00¢ | +65.00¢ |
| 9 | ATP_CHALL 0.25-0.30 | 256 | +30.40¢ | +24.00¢ | +68.00¢ |
| 10 | ATP_MAIN 0.25-0.30 | 239 | +30.22¢ | +22.00¢ | +69.00¢ |

**A39 complement (top-10 cells by mean ROI):**

| Rank | Cell | n | Mean ROI |
|------|------|---|---|
| 1 | WTA_MAIN 0.05-0.10 | 113 | +266% |
| 2 | ATP_CHALL 0.10-0.15 | 234 | +211% |
| 3 | ATP_MAIN 0.05-0.10 | 113 | +209% |
| 4 | WTA_MAIN 0.10-0.15 | 142 | +196% |
| 5 | WTA_CHALL 0.10-0.15 | 39 | +194% |
| 6 | ATP_CHALL 0.15-0.20 | 251 | +187% |
| 7 | ATP_CHALL 0.05-0.10 | 192 | +183% |
| 8 | WTA_MAIN 0.15-0.20 | 151 | +157% |
| 9 | ATP_MAIN 0.10-0.15 | 129 | +151% |
| 10 | WTA_CHALL 0.05-0.10 | 43 | +148% |

**Zero overlap between cents top-10 and ROI top-10** — concrete demonstration of A39. The two rankings answer different deployment-regime questions and Rung 1 must emit both, ranked separately, with CIs on every estimate.

---

## Section 2 — Canonical doc set (read on-demand, not on-load)

**Doctrine and strategy:**
- `docs/SIMONS_MODE.md` — alpha thesis (path-to-settlement variance capture), Problem 1 / Problem 2 split. Section 4 load-bearing. The CURRENT-STATE AMENDMENT at end of Section 4 resolves the cell/exit model to the locked specifics.
- `docs/LESSONS.md` — durable lessons in 7 categories. Critical for current work: A21 (Wall Street grade metrics), A32 (operator pushback as probe trigger), A37 (strict-entry coverage cost: 71.7% measured baseline), A38 (dual-peak vs settlement saturation), A39 (cents vs ROI as separate ranking metrics), E32 (locked cell/exit model — load-bearing anchor for all rung work), F33 (depth-chain gap, T38 forward-only), G21 (ET on operator surfaces).

**Planning artifacts:**
- `docs/ROADMAP.md` — T-items. T37 (per-minute foundation) done. T39 (recomputation ladder, Rung 0 done, Rung 1 next).
- `data/analysis/recomputation_ladder.json` — 6 rungs with Problem 1/Problem 2/bridge axis. Walk in order: Rung 0 → 1 → 2; Rung 3 (bridge) after; Rung 4 = CLOSE-do-not-rebuild; Rung 5 optional.
- `data/analysis/unit_of_analysis_audit.json` — 65-entry classification of prior analyses against GRAIN/VECTOR/OBJECTIVE axes.

**Specs:**
- `docs/rung0_cell_economics_spec.md` — v1.1 at commit 87103d0d. Section 5 = 36-column output schema. **Load-bearing for Rung 1 spec drafting** — every column reference in Rung 1 must match Section 5 exactly.
- `docs/per_minute_universe_spec.md` — T37 foundation spec.

**Reference / inventory:**
- `docs/ANALYSIS_LIBRARY.md` — 65 entries with disposition.
- `docs/TAXONOMY.md` — data tier definitions, GRAIN/VECTOR/OBJECTIVE classification axes (Section 2.5 load-bearing for audit work).
- `data/durable/MANIFEST.md` — sha256 lineage including Rung 0 entry (committed at 5ca2d89c).

**External synthesis archive:**
- `docs/external_synthesis/plex_rung1_metric_design_2026-05-15.md` (committed at 3f7dc02c). Plex's comprehensive Rung 1 metric design synthesis + chat-side open-question resolutions + Plex→Rung 0 column-name mappings verified against landed cell_economics.parquet. **LOAD-BEARING input for Rung 1 spec drafting.**

**Operating norms / longer-form memory:**
- `docs/SESSION_HANDOFF.md` — cumulative memory. Read only when this handoff doesn't have what you need.

---

## Section 3 — What's known (verified)

- **Foundation corpus:** `data/durable/per_minute_universe/per_minute_features.parquet` — 9,330,878 rows, 88 cols, sha256 `9fde4b5d30e56d99efa0637fe042cb6ca4505274e85e42769b4cedc25e3e5ff4`.
- **Trade tape:** `data/durable/g9_trades.parquet` — 33.7M rows, microsecond-precise, `taker_side` 100% populated.
- **Rung 0 output:** `data/durable/rung0_cell_economics/cell_economics.parquet` — sha256 above, 14,033 rows × 36 cols, validation_report.md + .meta.json sidecars.
- **Cell/exit model:** locked at E32. T-20m cell mark, 4 categories, 5¢ bands 5-95¢ (72 cells), no stop, two exit windows, settlement = first 99¢/1¢ touch.
- **Operator paths:** local commit path `C:\Users\omigr\OMI-Workspace\arb-executor`. VPS: `ssh root@104.131.191.95`, workspace `~/Omi-Workspace/arb-executor/`.
- **Commit chain this Rung 0 arc:**
  - `87103d0d` — Rung 0 spec v1.1 (decisions locked)
  - `356f25f4` — producer script v1.1
  - `52edf132` — pandas3 / pyarrow24 compat patch
  - `10322a8f` — int() truncation fix (the C37 gate-failure root cause; dropped exactly 21 boundary violators between failed attempt #1 and clean re-run)
  - `621bc5d8` — P1/P2 axis amendment to ladder + ROADMAP + SIMONS_MODE
  - `44c9ec68` — SESSION_HANDOFF stale liamm→omigr path fix
  - `9eb6cade` — LESSONS A37 + A38
  - `807e0a8b` — LESSONS A39
  - `5ca2d89c` — MANIFEST Rung 0 entry
  - `3f7dc02c` — Plex Rung 1 metric design archive (this commit chain's prior step)

---

## Section 4 — Plex column-name mappings verified against landed Rung 0

Plex's metric design uses some column names that don't match Rung 0 v1.1's actual schema. Verified mappings on disk against landed cell_economics.parquet (Rung 0 v1.1 spec Section 5):

- `contracts_at_best_bid_t20m` (Plex) → **`bbo_bid_size_at_t20m`** (Rung 0 col 32). Also `bbo_ask_size_at_t20m` (col 33).
- `settlement_price_cents` (Plex) → **does not exist as named**; use `realized_at_settlement` (col 28, = `settlement_value_dollars − t20m_trade_price`) for terminal-PnL-under-no-stop, or `settlement_value_dollars` (col 7, the raw 0.0/1.0) directly.
- `minutes_to_first_extreme_touch` (Plex's theta proxy gate) → **derivable in Rung 1 as `(first_extreme_touch_ts − t20m_trade_ts).total_seconds() / 60`** using cols 27 and 8. No upstream Rung 0 v1.2 amendment needed.

All other Plex-named columns map cleanly to Rung 0 v1.1: `peak_bid_bounce_full` (col 17), `peak_bid_bounce_pre_resolution` (col 18, HEADLINE), `band_n_count` at row level (col 13), `oi_at_t20m` (col 31), match identifiers (cols 1-3: ticker, event_ticker, paired_event_partner_ticker), `t20m_trade_ts` (col 8), `first_extreme_touch_ts` (col 27).

**The Plex inventory is canonical for METRIC SELECTION; Rung 0 v1.1 Section 5 is canonical for COLUMN NAMES.** Cross-check Plex's column references against Section 5 before locking any column name in the Rung 1 spec.

---

## Section 5 — Locked chat-side resolutions for Rung 1 spec drafting

Three open questions from Plex's synthesis are now locked. These resolutions are spec-level requirements for Rung 1 v0.1:

### Resolution 1 — Bootstrap design

**Within-cell metrics** (the vast majority of v1 metrics): row-level bootstrap, n=1000, BCa where computable with percentile fallback. Match-clustering is NOT required at this level because Rung 0 emits one row per N per side, and the two sides of a paired match fall in different price bands (their T-20m prices sum to ~$1). Within a single cell, rows are from different matches.

**Cross-cell aggregations** (e.g., `variance_across_cells_at_threshold`, any metric that aggregates across cells where both sides of a single match contribute): match-clustered resampling at `event_ticker` level. Rows sharing event_ticker either all appear in a bootstrap draw or all don't.

Bootstrap method: BCa where the implementation exists and converges; percentile fallback. BCa is more defensible at modest N and asymmetric distributions, which is Rung 1's operating regime.

### Resolution 2 — Sortino downside convention

The downside is realized return at the actual non-hit terminal value under E32's locked no-stop ride-to-settlement model. Plex's "zero-return downside" suggestion is INCORRECT for this corpus — under E32, a non-hit row settles at 1¢ or 99¢, which for a 30¢ entry is −29¢ or +69¢, not zero.

The terminal value is already in Rung 0 schema as **column 28 `realized_at_settlement`** = `settlement_value_dollars − t20m_trade_price`. Per row, Rung 1 computes:
- If `peak_bid_bounce_pre_resolution >= threshold`: realized_cents = threshold
- Else: realized_cents = `realized_at_settlement` (the actual ride-to-settlement value, negative for losing rides)

Then aggregate the realized_cents distribution per (cell, threshold) for mean, std, downside_std (negative-values-only-std), Sortino.

### Resolution 3 — Chronology retention

Verified on disk: Rung 0 v1.1 spec Section 5 emits both `match_start_ts` (col 5, ET tz-aware) and `settlement_ts` (col 6, ET tz-aware) per row. Chronology preserved by construction. `daily_opportunity_rate` and any other day-denominator metrics are computable directly from row-level timestamps; no secondary calendar input needed.

`unique_match_count` per (cell, threshold) = distinct `event_ticker` count among the rows in the group.

---

## Section 6 — What's NOT known (unresolved)

Active gaps that future work will resolve:

- **Per-cell EV and threshold-sweep results** — Rung 1 work. Builds on landed Rung 0. Next ladder step.
- **Bilateral capture rate recompute** — Rung 2 work (the 70.7% legacy anchor, joining Rung 0 on event_ticker, under exit-optimized scoring on the foundation corpus).
- **Maker fill probability per cell** — Rung 3 work (Problem 2 territory). Cannot proceed until Rung 1 establishes which cells have strategy-level edge.
- **Deep orderbook depth at non-BBO prices** — F33 structural gap. T38 (books daemon) closes forward-only. Doesn't bite at Rungs 0-2; bites at Rung 3 sizing decisions.
- **Theta Greek analog** — derivable in Rung 1 from Rung 0 cols 27 and 8 (no upstream change needed).
- **Vega Greek analog** — needs path-volatility descriptors not in Rung 0 v1.1. v2 / Rung 1.5 work.

**Open uncertainties from prior chats not yet closed:**

- Whether the ~6-27% stable-window coverage means one of the three attack vectors must shoulder most of the operation's coverage. Possibly answered by Rung 1's per-threshold realized-fraction results.
- Whether Challenger cells want a different mark (T-30m? T-40m?). T-20m locked for Main. The Rung 0 result shows WTA_CHALL punching above its weight (3× over-representation in cents top-10 despite being 6.3% of corpus), which argues against changing the WTA Challenger mark — it's working at T-20m.
- v0.3 phase_state amendment candidates (volume-based surge thresholds, PHASE_1→PHASE_2 trade-activity floor). Not blocking Rung 1.

---

## Section 7 — Operating norms (carry forward verbatim)

- **Single-concern commits**, dependency-ordered. Never bundle.
- **One App prompt per turn**, never bundled.
- **Probe-validate-probe-validate** before expensive compute.
- **Corpus mutations require C37 pre-replace validation gate** — compute to .new, run all hard gates against .new bytes, `os.replace` only on all-pass. Gate failures adjudicated with disk evidence, NOT narrative.
- **Streaming discipline on VPS** (~1.9 GB RAM available).
- **Verify every commit against origin/main** via /tmp/omi_check clone or equivalent. Don't trust App's summary uncritically.
- **State recommendations with conviction, not options.** When the right answer is clear, name it and let operator countermand. Operator-flagged this session: "stop with the subjective questions."
- **All operator-facing timestamps ET per G21.** UTC stays at raw-bytes layer only.
- **Full player names always.** Never abbreviations or 3-letter Kalshi codes.
- **Treat operator pushback as probe trigger per A32**, not as noise. Operator has been right every time they pushed back this session.
- **Codify principles when operator surfaces them.** A39 is the example from this session.
- **External synthesis from Plex (or any non-chat-side agent) gets committed to `docs/external_synthesis/<source>_<topic>_<date>.md` immediately**, not held in chat-side context only. Cross-chat-session continuity requires repo-backed canonical input.
- **Critical review of external synthesis must use disk evidence, not chat-side inference.** When auditing a synthesizer's output, pull the actual repo and verify column names, doctrine claims, and corpus assumptions against committed source. Chat-side inference about what the spec "probably says" produces partially-wrong corrections.
- **The "ct" unit is one contract, integer-indivisible.** A contract on Kalshi pays $1 at settlement. 1 ct at entry price P costs P dollars. Max payoff is $1 (technically 99¢ since first-99c-touch is the settlement event per E32). Operator-facing economics always in ct terms (cents per ct, ROI per ct, cts per day, cts per fire), never partial-contract or notional-dollar abstractions.

---

## Section 8 — Immediate next actions

In order:

1. Read this CHAT_HANDOFF.md. Done if you're reading this.
2. Verify HEAD on origin/main matches `3f7dc02c` (or beyond if commits landed after this handoff was written).
3. Read `docs/external_synthesis/plex_rung1_metric_design_2026-05-15.md` end-to-end, including chat-side resolution block. This is the canonical metric inventory for Rung 1.
4. Read `docs/rung0_cell_economics_spec.md` Section 5 to lock the actual column names that Rung 1 will reference.
5. Draft Rung 1 spec v0.1 at `docs/rung1_strategy_evaluation_spec.md`. Structural pattern follows Rung 0 spec. Key spec-level decisions already locked:
   - **Cell/threshold key:** 72 cells × candidate thresholds (proposed grid: +5¢, +10¢, +15¢, +20¢, +25¢, +30¢, +40¢, +50¢ — operator can amend before lock).
   - **Realized cents derivation per row:** hit → threshold; non-hit → realized_at_settlement (col 28).
   - **Bootstrap design:** within-cell row-level n=1000 BCa; cross-cell match-clustered on event_ticker. (Resolution 1.)
   - **Sortino downside:** computed over the full realized_cents distribution with negative values contributing to downside-std. (Resolution 2.)
   - **Chronology:** preserved via cols 5/6; `daily_opportunity_rate` and similar metrics computable directly. (Resolution 3.)
   - **Greek labels:** the Rung 1 spec drafter should consider whether to rename Plex's Greek-labeled metrics to honest descriptors (`execution_delta_proxy` → `hit_rate_threshold_slope`, etc.) — operator call.
   - **Metric count:** Plex's table has 50+ metrics; operator-recommended v1 is 12-15 critically-selected metrics. Spec drafter picks the v1 subset and documents the cut criteria.
6. Single-concern commit of the spec. Then App writes the producer (vectorized pandas pass on cell_economics.parquet; runtime seconds-to-minutes, not hours).
7. After Rung 1 lands: validation_report.md with per-cell-per-threshold results, ranked by both cents and ROI (A39), with CIs on every estimate (A21). Operator absorbs the headline, decides the cents-vs-ROI deployment-regime split.
8. After operator absorbs Rung 1 headline: Rung 2 spec draft (bilateral capture rate recompute on the foundation corpus). Then Rung 3 (the bridge rung — policy layer / revised T36).

**Bot deployment cannot proceed until at minimum Rung 2 lands** (per ladder doctrine: a rung that conflates P1 and P2 cannot drive deployment per E32 enforcement). Rung 3 unblocks deployment decisions.

---

End of CHAT_HANDOFF.md.
