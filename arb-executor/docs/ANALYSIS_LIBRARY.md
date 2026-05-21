# OMI Analysis Library — Catalog of Prior Analyses

**Purpose:** Catalog every prior analysis script and result file in the OMI tennis trading operation, classified by analysis depth, data tier, variables used, question answered, validity status, and output location. Source of truth for "what has already been done." Future chats consult this before designing any new analysis to avoid redoing work and to know which prior conclusions are valid vs invalidated.

**Cross-references:**
- Taxonomy used for classification: TAXONOMY.md.
- Lessons that motivate this library: A23 (sources pulled from but not fully extracted), A28 (D1/D2 fragmentation), C14 (canonical output paths), E25 (70.7% as depth-0), E26 (depth and variable inventory parallel axes), E27 (D5 methodology drift), F19 (bias reconciliation fragmented).

**Last populated:** 2026-05-14 ET — unit-of-analysis audit applied; all 65 entries classified inline (GRAIN/VECTOR/OBJECTIVE + disposition).

**FOUNDATION-REBUILD NOTICE (2026-05-14):** Every entry below dated before 2026-05-14 predates the T37 foundation rebuild. The canonical analysis foundation is now per_minute_features.parquet (FOUNDATION-TIER, checkpoint 3 sha256 9fde4b5d...) — NOT the Layer A v1 / G9 parquet anchors that older entries reference as 'canonical foundation.' This catalog is the input to the unit-of-analysis audit, which will (a) tag every entry with the GRAIN / VECTOR / OBJECTIVE axes per TAXONOMY Section 2.5, and (b) surface every settlement-scored finding as needing recomputation against the exit-optimized model (LESSONS E32), not silent reclassification. Until the audit runs, treat pre-rebuild entries' validity status and conclusions as provisional.

---

## SECTION 1: ENTRY FORMAT

Each analysis is one entry with the following fields:[Analysis name]

File path: [VPS path]
Producer script: [VPS path of code]
Date created: [date or git commit date]
Depth: [0-6 per TAXONOMY.md Section 2]
Grain: [match-aggregate / per-minute / per-tick / per-cell — per TAXONOMY Section 2.5]
Vector: [vector-A / vector-B / vector-C / vector-agnostic — per TAXONOMY Section 2.5]
Objective: [settlement-scored / exit-optimized / objective-agnostic — per TAXONOMY Section 2.5]
Data tier used: [A / B / C / mixed / N/A]
Variables used: [columns from TAXONOMY Section 4]
Question answered: [one sentence]
Validity status: [valid / partial / broken / unverified / superseded]
Notes: [known issues, dependencies, supersession info]

The GRAIN / VECTOR / OBJECTIVE triple is mandatory for every entry as of 2026-05-14 (TAXONOMY Section 2.5). Entries created before that date do not yet carry the triple; populating them is the unit-of-analysis audit's job. New entries created after that date must carry all three at creation.

Canonical-path rules (post-Session-6 Phase 1B/1C). For preserved DATA files: arb-executor/data/durable/ is canonical (sha256-verified per MANIFEST.md, not in git due to size, but durable on disk). For preserved SCRIPTS: tmp/ is canonical (git-tracked, multiple curation batches Mar 13 - Apr 29 plus Session 6 Phase 1A/1C additions). /tmp/ is now the producer WORKING DIRECTORY for live operations (e.g., kalshi_fills_history.json gets re-pulled to /tmp by fills_history_pull.py, then copied to durable/ to update canonical). For files in multiple locations: durable/ wins for data, tmp/ wins for scripts; /tmp serves as producer working file only. F1 PARTIAL CLOSURE in ROADMAP tracks the broader durability migration across this corpus.

---

## SECTION 2: ANALYSES BY DEPTH

### Depth 0 — Existence

#### April 14 paired analysis (the 70.7% double-cash rate)
- **File path:** Reconstructed from chat memory; original output not located in /tmp inventory.
- **Producer script:** Unknown; possibly /tmp/per_cell_verification or ad-hoc one-off.
- **Date created:** ~April 14 2026.
- **Depth:** 0 (existence proof).
- **Grain:** match-aggregate
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Data tier used:** C (historical_events).
- **Variables used:** first_price_winner, max_price_winner, first_price_loser, max_price_loser.
- **Question answered:** Did both sides of paired matches ever reach +10c above first observed price.
- **Validity status:** Partial — see E25. Valid as existence proof; invalid as edge validation. Not reproduced on current data.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Existence proof both sides reached +10c in many paired matches; recompute as exit-optimized bounce per cell band with prematch/in-match decomposition.
- **Notes:** Cited as "70.7% across 458 paired matches" in LESSONS.md E18. First pressure test in queue (ROADMAP Section 4).

#### Heartbeat / operational health checks
- **File paths:** /tmp/heartbeat_*.json (live_v3, kalshi_price, fv_monitor, betexplorer, tennis_odds).
- **Depth:** 0 (operational, not strategy).
- **Grain:** N/A
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Notes:** Real-time health checks, not analysis. Excluded from strategic catalog but flagged here for completeness.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Live health checks for feeds and services; operational monitoring, not strategy or market analysis.

---

### Depth 1 — Distribution

#### exit_sweep_grid
- **File path:** /tmp/exit_sweep_grid.csv (85.7 KB).
- **Producer:** /tmp/exit_sweep.py.
- **Depth:** 1.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Data tier used:** mixed (matches table + BBO).
- **Variables used:** Per-cell ROI and hit_rate at every exit_c from 1c to 49c.
- **Question answered:** What is the optimal exit_c per cell, and how does ROI change across exit_c?
- **Validity status:** Unverified — uses fixed exit baseline; classifier threshold not surfaced.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Per-cell ROI and hit rates over an exit_c grid using matches+BBO and a fixed baseline; recompute as exit-optimized bounce per cell band on the FOUNDATION-TIER corpus.
- **Notes:** Underdog only (leaders absent). N at least 30 per cell.

#### exit_sweep_curves
- **File path:** /tmp/exit_sweep_curves.csv (15.8 KB).
- **Producer:** /tmp/exit_sweep.py.
- **Depth:** 1.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Notes:** Wider variant of exit_sweep_grid including band_width and N. Same producer.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Aggregated curves over the same exit_sweep grid on the legacy matches table; recompute as exit-optimized bounce per cell band on the FOUNDATION-TIER corpus.

#### optimal_exits
- **File path:** /tmp/optimal_exits.csv (9.8 KB).
- **Producer:** /tmp/exit_sweep.py.
- **Depth:** 1.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Variables used:** Per-cell optimal_exit, optimal_ROI, hit_at_opt with 15c baseline comparison.
- **Validity status:** Partial — same caveats as exit_sweep_grid.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Summarizes per-cell optimal exit and ROI relative to a fixed baseline on settlement-contaminated data; recompute as exit-optimized bounce per cell band on the FOUNDATION-TIER corpus.

#### baseline_econ
- **File path:** /tmp/baseline_econ.csv (2.5 KB).
- **Depth:** 1.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Variables used:** Per-cell status (ACTIVE/disabled), exit_cents, N, avg_entry, scalp_WR_pct, ROI_pct, daily_dollar, confidence.
- **Validity status:** Partial — pre-V3 baseline, predates Mona Lisa retune.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Pre-V3 baseline per-cell economics using fixed exit and settlement-contaminated regime; recompute as exit-optimized ROI per cell on foundation-tier data.

#### bootstrap_ci_results
- **File path:** /tmp/bootstrap_ci_results.csv (1.3 KB).
- **Producer:** /tmp/bootstrap_ci.py and /tmp/bootstrap_negative.py.
- **Depth:** 1.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Variables used:** Per-cell bootstrap mean/std/CI vs analytical CI; ci_match flag.
- **Validity status:** Valid for the cells included (subset of total cells).
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Compares bootstrap vs analytical CIs for per-cell estimates; a measurement-method validation, not a strategy objective.
- **Notes:** Per B4, validates that analytical CIs align with bootstrap on existing data.

#### rebuilt_scorecard
- **File path:** /tmp/rebuilt_scorecard.csv (8.5 KB).
- **Producer:** /tmp/rebuilt_scorecard_script.py.
- **Depth:** 1 (with classification on top).
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Variables used:** TWP, Sw, Sl, decomposed_ROI per 67-cell scorecard.
- **Validity status:** Partial — methodology issues per LESSONS (uses fixed 15c exit, classifier threshold not surfaced, bias correction undersized vs operator memory).
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — 67-cell classification using fixed 15c exit and legacy scorecard; recompute as exit-optimized per-cell scorecard with explicit thresholds on foundation-tier cells.
- **Notes:** 67-cell SCALPER_EDGE / SCALPER_BREAK_EVEN / SCALPER_NEGATIVE / MIXED_BREAK_EVEN / SETTLEMENT_RIDE_CONTAMINATED / UNCALIBRATED classification.

#### post_retune_economics
- **File path:** /tmp/per_cell_verification/post_retune_economics.csv.
- **Depth:** 1.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Variables used:** Per-cell N / avg_fill_price / realized_pnl / CI for the post-retune window.
- **Validity status:** Unverified — must re-derive entry timing per F17.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Per-cell realized_pnl and CI in post-retune window; recompute as exit-optimized bounce/ROI per cell with corrected entry timing and settlement handling.

#### pnl_by_cell_config
- **File path:** /tmp/per_cell_verification/pnl_by_cell_config.csv.
- **Depth:** 1.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Variables used:** Per-cell per-config-hash N_fills, avg_pnl_pct, total_pnl_dollars.
- **Validity status:** Unverified.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Per-cell per-config-hash P&L; recompute with exit-optimized metrics and clean config lineage on foundation-tier corpus.
- **Notes:** Distinct config hashes visible — implements F2 (config drift contamination tracking).

#### per_cell_real_economics
- **File path:** /tmp/per_cell_verification/per_cell_real_economics.csv.
- **Depth:** 1.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Variables used:** Per-cell scalps / settle_wins / settle_losses / scalp_WR_pct / total_pnl_dollars / daily_fills.
- **Validity status:** Partial — settlement detection broken per F8 (Bug 4).
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Per-cell scalps/settlements and P&L built on broken settlement detection; rebuild with correct settlement visibility and exit-optimized objective.

#### comparison_real_vs_analysis
- **File path:** /tmp/per_cell_verification/comparison_real_vs_analysis.csv.
- **Depth:** 1.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Variables used:** Per-cell delta between realized P&L and analysis-predicted P&L; assessment column flags REAL_WORSE / REAL_BETTER / TOO_FEW_FILLS.
- **Validity status:** Valid for diagnostic purposes; the deltas themselves carry F8 caveat.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Compares realized vs predicted per-cell P&L under settlement-contaminated baseline; useful diagnostic pattern but recompute under exit-optimized per-cell metrics.

#### u4_phase1_match_landscape (U4 Phase 1)
- **File path:** tmp/u4_phase1_match_landscape.csv (1.04 MB, 5,879 matches; durable per Phase 1C-iv Session 6, commit f36691c).
- **Producer script:** tmp/u4_phase1_match_landscape.py (durable per Phase 1C-i Session 6, commit d0462c8).
- **Date created:** 2026-04-30 (Session 4).
- **Depth:** 1.
- **Grain:** match-aggregate
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Data tier used:** C (historical_events) + attempted joins to book_prices and kalshi_price_snapshots.
- **Variables used:** first_price_winner, min_price_winner, max_price_winner, last_price_winner, first_price_loser, min_price_loser, max_price_loser, last_price_loser, total_trades, category, commence_time, duration.
- **Question answered:** What does the match landscape look like across all relevant variables, with no pre-defined cell scheme?
- **Validity status:** Valid for population-level characterization; Pinnacle FV join FAILED (book_prices Apr 19+ vs historical_events Jan 2 - Apr 10 = zero date overlap) and volume_24h join FAILED (kalshi_price_snapshots Apr 21+ only).
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Population-level match landscape over winner/loser price trajectories and volume/duration; structural characterization, not strategy scoring (prematch/in-match conflation caveat).
- **Notes:** Foundation for U4 Phase 2 stratification. Confirms bounce asymmetry at population level: winner median ~35c, loser median ~12-16c. 33% of matches have first_price_winner + first_price_loser >5c off 100 (per A19 — first_price unsynchronized between sides). F28 /tmp ephemerality MITIGATED for this entry per Phase 1C Session 6 — both producer and output durable in tmp/. **CAVEAT per B14:** uses match-level aggregates conflating premarket vs in-match windows.

#### u4_phase2_loser_bounce_predictors (U4 Phase 2)
- **File path:** tmp/u4_phase2_loser_bounce_by_strata.csv (8.1 KB, 92 strata) + tmp/u4_phase2_loser_bounce_summary.txt (2.9 KB; both durable per Phase 1C-iv Session 6, commit f36691c).
- **Producer script:** tmp/u4_phase2_loser_bounce_predictors.py (durable per Phase 1C-i Session 6, commit d0462c8).
- **Date created:** 2026-04-30 (Session 4).
- **Depth:** 1 (distribution stratified).
- **Grain:** match-aggregate
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Data tier used:** C (synchronized subset of historical_events: 3,936 matches where first_price_winner + first_price_loser within 5c of 100).
- **Variables used:** total_trades, category, duration, skew (first_price_winner - 50), first_price_loser, leg span, plus loser-side bounce magnitudes.
- **Question answered:** Which match-level variables predict loser-side bounce capture, and at what magnitudes?
- **Validity status:** Valid as stratified distribution finding on synchronized subset. Strategically useful: volume is canonical predictor.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Stratified loser-side bounce distributions and bilateral capture rates by volume/category/skew; describes bounce structure, not a particular strategy's outcome.
- **Notes:** Key finding — **volume is primary predictor of bilateral capture** (33pp swing across volume strata: 50-99 trades = 34.3% bilateral capture at +10c, 1000+ trades = 76.4%). Categories track within 6pp (ATP_CHALL=63.1%, ATP_MAIN=63.5%, WTA_MAIN=64.3%, WTA_CHALL=56.8%). Skew >35 cliff partially CEILING ARTIFACT per B13 (heavy side at 85-89c can't bounce 15c without exceeding 99c). Aggregate +10c bilateral on synchronized subset: 62.83%. Duration 2-4h matches strongest (68.3%). **Reframes the 70.7% April 14 anchor per E30 — that figure was subset-averaged; high-volume regime is 76.4% and low-volume is much lower.** Operator-validated strategic conclusion: high-volume matches (1000+ trades) are bilateral candidates; low-volume are single-side or skip. **CAVEAT per B14/G17:** uses match-level aggregates conflating premarket vs in-match. Decomposition required for strategy-actionable findings (U4 Phase 3, next analysis target). F28 /tmp ephemerality MITIGATED for this entry per Phase 1C Session 6 — producer and outputs durable in tmp/.

---

### Depth 2 — Trajectory

#### entry_price_bias (canonical run)
- **File path:** /tmp/per_cell_verification/entry_price_bias.csv (320 KB).
- **Depth:** 2.
- **Grain:** per-tick
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Data tier used:** B + matches.
- **Variables used:** Per-ticker first_mid / first_bid vs T-15m / T-1h / T-2h / T-4h mid and bid.
- **Question answered:** What is the bias between bot fill price and pre-match BBO at various windows?
- **Validity status:** Unverified canonical — F19 fragmentation; multiple bias files exist measuring overlapping concepts.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Measures bias between bot fill prices and BBO at multiple prematch windows; structural entry-price bias diagnostic, conceptually objective-agnostic.
- **Notes:** Bias-correction primary source per Mona Lisa work. The "operator memory says +21-37c, file shows max 10.6c" mystery in known unknowns originates here.

#### entry_price_bias_by_cell
- **File path:** /tmp/per_cell_verification/entry_price_bias_by_cell.csv (2.6 KB).
- **Depth:** 2.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Variables used:** Per-cell aggregate (mean / median / stddev / pct_within_3c / pct_within_5c).
- **Validity status:** Same as entry_price_bias.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Cell-level aggregation of the same entry-price bias; structural bias measurement, carries forward though execution should be de-fragmented.

#### entry_price_bias.run1
- **File path:** /tmp/per_cell_verification/entry_price_bias.run1.csv + entry_price_bias_by_cell.run1.csv.
- **Depth:** 2.
- **Grain:** per-tick
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Validity status:** Earlier run, identical schema. Per F19, exact relation to canonical run undocumented.
- **Audit disposition (2026-05-14):** SUPERSEDED — Earlier fragment of entry-bias measurement, same schema; superseded by the canonical run, needs no independent rebuild.
- **Notes:** Source of fragmentation per F19.

#### bias_by_cell_from_matches
- **File path:** /tmp/per_cell_verification/bias_by_cell_from_matches.csv.
- **Depth:** 2.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Data tier used:** matches table.
- **Variables used:** Per-cell bias from matches table (bot_entry_price vs first_price_historical).
- **Validity status:** Partial — uses matches.entry_time which is NULL on live rows per F17.
- **Audit disposition (2026-05-14):** BROKEN — Uses matches.entry_time (null on live rows); conceptually useful but rebuild using JSONL log times and foundation-tier joins.

#### linkage_sanity_check
- **File path:** /tmp/per_cell_verification/linkage_sanity_check.csv.
- **Depth:** 2.
- **Grain:** per-fill
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Variables used:** Per-fill linkage diagnostic comparing cell_by_first_price vs cell_by_bot_entry; flags cell_mismatch.
- **Validity status:** Valid — implements A11 (cell mismatches at boundaries contaminate per-cell numbers).
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Valid linkage diagnostic comparing cell_by_first_price vs cell_by_bot_entry; structural hygiene check enforcing correct cell assignment.

#### swing_script
- **File path:** /tmp/swing_script.py (script only; outputs not located).
- **Depth:** 2.
- **Grain:** match-aggregate
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Variables used:** first_mid, pre-commence_max_mid, post-commence_max_mid per ticker.
- **Question answered:** Channel 1 vs Channel 2 trajectory primitive — separate the pregame max from the in-match max per ticker.
- **Validity status:** Unverified; not located as committed output.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Separates pregame vs in-match max mid per ticker for channel-trajectory decomposition; output missing, question still important, re-run on foundation data.

#### channel_decomp (current session)
- **File path:** /tmp/channel_decomp.py.
- **Depth:** 2.
- **Grain:** per-fill
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Variables used:** JSONL log entry_filled and exit_filled events; ts_et fields.
- **Question answered:** What fraction of bot fills exit via Channel 1 (pregame) vs Channel 2 (in-game)?
- **Validity status:** Valid — produced the 4.7% / 95.3% split that anchors LESSONS Section 2.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Computes fraction of fills exiting via Channel 1 vs 2; routing/flow-allocation statistic, not a performance score; matches the Section 4 Channel 1 vs 2 split.
- **Notes:** Reads from JSONL logs which are tz-clean per F16.

#### replay_inplay
- **File path:** /tmp/replay_inplay.py.
- **Depth:** 2.
- **Grain:** match-aggregate
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Notes:** Replay of in-play trajectory. Output not located.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Replay of in-play trajectories, output missing; structurally useful for trajectory understanding, not itself an objective score.

---

### Depth 3 — Capacity

#### fill_asymmetry_per_fill
- **File path:** /tmp/per_cell_verification/fill_asymmetry_per_fill.csv (17.8 KB).
- **Producer:** /tmp/fill_asymmetry.py.
- **Depth:** 3 (top-of-book only — does NOT use 5-deep depth).
- **Grain:** per-fill
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Data tier used:** A or B (top-of-book).
- **Variables used:** Per-fill bid_at_fill / ask_at_fill / spread_at_fill, mid 30 min before, oscillation_range, n_window_snaps, paired flag.
- **Validity status:** Partial — implements only level-1 capacity; A22 unfulfilled at Depth 3 because 5-deep depth columns from premarket_ticks remain unused.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Per-fill spread/pre-window-mid/oscillation/paired flag at level-1 depth; structural capacity primitive, extend to full depth when T38 lands.

#### fill_asymmetry_summary
- **File path:** /tmp/per_cell_verification/fill_asymmetry_summary.csv.
- **Depth:** 3 (level-1 only).
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Variables used:** Leader vs underdog aggregate (% trending up / down / oscillating / flat, paired_pct).
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Summarizes leader vs underdog capacity/oscillation patterns; structural capacity view needing full-depth augmentation in v2.

**Depth 3 capacity-with-full-depth: NONE EXIST.** No prior analysis uses bid_2 through bid_5 with sizes from premarket_ticks. A22 + A26 unfulfilled at Depth 3.

---

### Depth 4 — Microstructure

#### Greeks decomposition (BROKEN per F11)
- **File path:** /tmp/per_cell_verification/greeks_decomposition.csv.
- **Producer:** /tmp/greeks_decomposition.py and /tmp/greeks_check.py.
- **Depth:** 4.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Variables used:** Per-cell theta_pregame, theta_early_match, gamma_excursion, realized_vega, scalp-phase distribution.
- **Validity status:** **BROKEN.** Degenerate first-bid bug per F11. Schema is correct; numbers are not trusted.
- **Audit disposition (2026-05-14):** BROKEN — theta/gamma/vega-style microstructure metrics per cell, invalid due to first-bid bug; worth rebuilding on foundation-tier data plus T38 depth.
- **Notes:** Listed in Section 3.

#### greeks_per_match
- **File path:** /tmp/per_cell_verification/greeks_per_match.csv.
- **Depth:** 4.
- **Grain:** match-aggregate
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Validity status:** **BROKEN.** Same degenerate first-bid bug. Per-ticker version of decomposition.
- **Audit disposition (2026-05-14):** BROKEN — Per-match version of the same broken Greeks decomposition; regenerate after fixing the underlying bug, only if the cell-level rebuild proves useful.

**Depth 4 microstructure-beyond-Greeks: NONE EXIST.** No volume-profile, VWAP, autocorrelation, market impact, or order-flow microstructure analyses exist despite trade CSVs having taker_side per A26.

---

### Depth 5 — Strategy simulation

#### fill_outcomes
- **File path:** /tmp/fill_outcomes.csv (23.7 KB).
- **Producer:** /tmp/fill_outcomes_analysis.py.
- **Depth:** 5.
- **Grain:** per-fill
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Variables used:** Per-fill cell, direction, play_type, entry_price, qty, terminal_event (exit_filled / settled), exit_price, pnl_cents_total, ROI%.
- **Validity status:** Partial — uses fill records that may be subject to F8 (settlement detection broken).
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Per-fill exit_filled vs settled and ROI% built on broken settlement detection; recompute as exit-optimized realized bounce/ROI with correct settlement and phase attribution.

#### dca_event_test / dca_event_analysis
- **File paths:** /tmp/dca_event_test.py / /tmp/dca_event_analysis.py (26.4 KB each).
- **Output:** /tmp/validation5/dca_event_matched.csv (23.7 KB).
- **Depth:** 5.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Variables used:** Per-cell DCA fire_rate_pct, win_rate_pct, dca_ev_per_fire_c, cell_roi_delta_pct across multiple trigger thresholds and combo variants.
- **Validity status:** Unverified.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Per-cell DCA fire/win rates and EV per fire across thresholds; exit-optimized re-run on foundation-tier cells, with clear vector-specific triggering if kept.

#### dca_bbo_v3 + variants
- **File paths:** /tmp/dca_bbo_v3.py + variants, /tmp/dca_bbo_v3_test.py, /tmp/dca_bbo_v3_test5m.py.
- **Promoted version:** /root/Omi-Workspace/arb-executor/dca_bbo_timeorder.py.
- **Depth:** 5.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Validity status:** Promoted version addresses A3 (time-order enforcement). Earlier variants superseded.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Promoted DCA policy implementation enforcing time order; strategy logic fine, but any v1 performance numbers must be recomputed under exit-optimized metrics on the new corpus.

#### scalp_constrained_optimize
- **File path:** /tmp/scalp_constrained_optimize.py.
- **Depth:** 5.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Implements:** A9 (exit target must be scalp-achievable: entry + exit_cents at most 95c).
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Implements the A9 constraint that exit targets must be ≤95c; a producer-side guardrail for exit search, not a scored analysis.

#### Multiple "ultimate cell economics" implementations (E27 — methodology drift)
- /tmp/validate_and_optimize.py
- /tmp/corrected_cell_economics.py
- /tmp/ultimate_cell_economics.py
- /tmp/ultimate_cell_economics_csv.py
- **Depth:** 5.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Validity status:** Unknown which is canonical. Per E27, this is methodology drift, not iteration. Before re-running strategy simulation, must designate canonical or retire others.
- **Audit disposition (2026-05-14):** BROKEN — Competing implementations of per-cell economics; methodology-drift cluster, replace entirely with a single exit-optimized canonical cell-economics pipeline on foundation-tier data.

---

### Depth 6 — Cross-sectional context

#### fv_convergence_monitor (live operational, not closed analysis)
- **File path:** /tmp/fv_convergence_monitor.csv (14.2 MB, actively growing).
- **Depth:** 6.
- **Grain:** per-minute
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Variables used:** Live FV vs Kalshi convergence with per-side gap_cents, gap_pct, time_to_start_hrs, fv_source, fv_tier.
- **Validity status:** Valid as live operational dashboard; not closed retrospective analysis.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Live FV vs Kalshi convergence dashboard with gap and time-to-start; operational cross-sectional context, not a retrospective performance analysis.

#### bias_from_bbo / bias_check / bias_check2
- **File paths:** /tmp/bias_from_bbo.py / /tmp/bias_check.py / /tmp/bias_check2.py.
- **Depth:** 6.
- **Grain:** per-tick
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Notes:** Sharp-bias measurement vs BBO. Multiple iterations; canonical not designated. Part of F19 fragmentation.
- **Audit disposition (2026-05-14):** BROKEN — Fragmented sharp-bias measurement vs BBO; consolidate into a single canonical bias analysis on foundation-tier data and T38 depth.

#### rebuild_vs_paper_diff
- **File path:** /root/Omi-Workspace/arb-executor/docs/rebuild_vs_paper_diff.md (41.3 KB).
- **Producer:** /tmp/rebuild_diff_analysis.py (34.5 KB).
- **Depth:** 6 (config-vs-config narrative comparison).
- **Grain:** N/A
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Validity status:** Valid — narrative documentation of strategy variants.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Narrative comparison of strategy configs; documentation rather than numeric objective scoring, remains valid as a config-history artifact.

**Depth 6 systematic external-data analysis: NONE EXIST.** No closed-form analyses of edge by tournament tier, by surface, by ranking, by day of week, or by Kalshi-vs-DraftKings lag. All depth-6 work to date is operational (fv_monitor) or narrative (rebuild_diff).

---

### Variable-isolation / retune forensics (cross-cutting)

These analyses isolate the impact of specific changes (cell additions, retunes, code changes). They do not fit cleanly into the depth taxonomy because they are diagnostic rather than measuring price/execution properties.

#### variable_isolation
- **File path:** /tmp/per_cell_verification/variable_isolation.csv.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Implements:** E7 / E8 (isolate variable impact across the Apr 24 retune).
- **Notes:** Bleed period vs recovery period. active_cell_count went 39 to 25, with itemized cells_added and cells_removed lists.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Decomposes Apr 24 retune bleed vs recovery at cell level; recompute with exit-optimized per-cell metrics and clean config lineage.

#### cell_groupings
- **File path:** /tmp/per_cell_verification/cell_groupings.csv.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Implements:** A12 (sub-cell statistical power vs wider groupings).
- **Notes:** Grouping vs subcell ROI; flags GROUP_BETTER vs SUBCELL_BETTER.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Compares GROUP vs SUBCELL ROI; grouping logic useful, but outcomes must be regenerated as exit-optimized returns and CIs.

#### bleed_decomposition
- **File path:** /tmp/per_cell_verification/bleed_decomposition.csv.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Notes:** Per-cell bleed contribution to -$228.80 with status_change (KEPT / ADDED_LATER / REMOVED) and pre/post-exit_cents columns.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Attributes -$228.80 bleed by cell and status_change; recompute as exit-optimized per-cell contribution with correct settlement and entry timing.

#### exit_sweep_leader_70_74
- **File path:** /tmp/per_cell_verification/exit_sweep_leader_70_74.csv.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Notes:** Per-c exit sweep at 1c granularity for one cell (drilldown). Implements A13 (granularity matters).
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — One-cell exit_sweep drilldown on legacy matches+BBO and fixed exits; recompute as exit-optimized bounce per cell band on the FOUNDATION-TIER corpus.

#### config_history_trace
- **File path:** /tmp/config_history_trace.py + duplicate.
- **Grain:** N/A
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Notes:** Traces config changes over time relative to bleed periods.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Traces config changes vs bleed periods; operational forensic tool, not itself an objective-scored analysis.

---

### Bias reconciliation cluster (F19)

Six+ files measuring overlapping concepts. Per F19, before reconciling: inventory what each measures (which mid: T-15m vs T-1h vs T-2h vs T-4h; which baseline: first_mid vs first_bid vs first_price), then designate canonical.

- /tmp/per_cell_verification/entry_price_bias.csv (canonical candidate)
- /tmp/per_cell_verification/entry_price_bias.run1.csv (earlier run)
- /tmp/per_cell_verification/bias_by_cell_from_matches.csv (matches-table-derived)
- /tmp/per_cell_verification/per_fill_first_price_lookup.csv (per-fill historical_events lookup; many rows show first_price=NULL)
- /tmp/per_cell_verification/real_per_fill_check.csv (duplicate)
- /tmp/real_per_fill_check.csv (duplicate)

**No designated canonical.** ROADMAP item: pick canonical before reconciling +21-37c vs 10.6c discrepancy.

---

### Remediation / meta / infrastructure (not strategy depth, listed for completeness)

- /tmp/bug4_brief.md (32 KB), /tmp/bug4_probe.md (14 KB), /root/Omi-Workspace/arb-executor/docs/* duplicates — Bug 4 remediation design.
- /tmp/bug3_guard.txt — Bug 3 reconcile-overwrite fix snippet.
- /tmp/paper_mode_spec.md (41 KB), /tmp/paper_mode_impl.py (32.8 KB), /tmp/paper_mode_unit_tests.py (25.4 KB) — paper-mode design + implementation + tests.
- /tmp/apply_bug2.py, /tmp/apply_patch.py, /tmp/test_bug2.py, /tmp/test_date_guard.py — patch-application + tests.
- /tmp/live_v3_patched.py / /tmp/live_v3_paper.py / /root/Omi-Workspace/arb-executor/live_v3.py / live_v3_paper_REVIEW.py — bot version artifacts.
- /tmp/raw_live_v3.py — pre-patch baseline.
- /tmp/spec_review_dump.txt — spec review output.

---

### G9 parquets (T17 + T27) — [SUPERSEDED 2026-05-14 as 'canonical foundation' — now an intermediate source; the canonical foundation is FOUNDATION-TIER per_minute_features.parquet, see TAXONOMY Section 1]

These three parquets are the canonical foundation for all Layer A/B/C work going forward
per LESSONS C27 (analytical-foundation discipline). Every downstream analysis entry below
must reference this foundation explicitly via T28 commit pointer.

#### g9_candles.parquet
- **File path:** arb-executor/data/durable/g9_candles.parquet
- **Producer script:** arb-executor/data/scripts/build_g9_parquets.py (commit bd83412)
- **Source data:** arb-executor/data/historical_pull/candlesticks/*.csv (19,687 files)
- **Date created:** 2026-05-04 (Session 6 T17)
- **Depth:** N/A (canonical source, not analysis)
- **Grain:** per-minute
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Data tier used:** G-tier source → canonical parquet
- **Schema:** 18 columns — ticker (injected), end_period_ts, open_interest_fp, price_close, price_high, price_low, price_mean, price_open, price_previous, volume_fp, yes_ask_close, yes_ask_high, yes_ask_low, yes_ask_open, yes_bid_close, yes_bid_high, yes_bid_low, yes_bid_open. Bare names canonical (era variation per F29 normalized at producer).
- **Row count:** 9,500,168
- **Validity status:** VERIFIED per T27 verification probe (Session 6, 9/9 checks passed including row count parity, schema normalization, reconstruction equivalence, no all-null era columns).
- **Audit disposition (2026-05-14):** SUPERSEDED — Canonical G9 candle parquet, superseded as the foundation by per_minute_features; remains a verified intermediate source feeding foundation-tier builds.
- **Notes:** ~65% of minutes have null price_close/volume_fp/open_interest_fp (no-trade minutes per G19); yes_bid_close/yes_ask_close are 100% populated. sha256 in arb-executor/data/durable/MANIFEST.md.

#### g9_trades.parquet
- **File path:** arb-executor/data/durable/g9_trades.parquet
- **Producer script:** arb-executor/data/scripts/build_g9_parquets.py (commit bd83412)
- **Source data:** arb-executor/data/historical_pull/trades/*.csv (20,018 files)
- **Date created:** 2026-05-04 (Session 6 T17)
- **Depth:** N/A (canonical source)
- **Grain:** per-tick
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Data tier used:** G-tier source → canonical parquet
- **Schema:** 7 columns — count_fp, created_time (ISO 8601 microsecond UTC), no_price_dollars, taker_side ({yes, no}), ticker, trade_id, yes_price_dollars.
- **Row count:** 33,727,162
- **Validity status:** VERIFIED per T27 (taker_side enum: only {yes, no}, 0 nulls; row count parity exact).
- **Audit disposition (2026-05-14):** SUPERSEDED — G9 trade parquet, superseded as canonical foundation, still the verified microsecond trade tape behind T37 and replay.
- **Notes:** Microsecond-precision trade tape. sha256 in MANIFEST.md.

#### g9_metadata.parquet
- **File path:** arb-executor/data/durable/g9_metadata.parquet
- **Producer script:** arb-executor/data/scripts/build_g9_parquets.py (commit bd83412)
- **Source data:** arb-executor/data/historical_pull/market_metadata/*.json (20,110 files)
- **Date created:** 2026-05-04 (Session 6 T17)
- **Depth:** N/A (canonical source)
- **Grain:** match-aggregate
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Data tier used:** G-tier source → canonical parquet
- **Schema:** 48 columns including ticker, event_ticker, custom_strike (JSON-stringified, contains tennis_competitor UUIDs per T25), settlement_ts, settlement_value_dollars, result, status, volume_fp, open_interest_fp, plus all metadata fields per market.
- **Row count:** 20,110
- **Validity status:** VERIFIED per T27 (custom_strike round-trip: 20,110/20,110 parse back to dict cleanly).
- **Audit disposition (2026-05-14):** SUPERSEDED — G9 metadata parquet, no longer the canonical foundation, remains a verified intermediate metadata source referenced by later tiers.
- **Notes:** sha256 in MANIFEST.md.

---

### Layer A v1 outputs (T29, foundation T28 ea84e74) — [pre-rebuild; superseded as canonical by FOUNDATION-TIER, retained as regression cross-check]

Per-cell forward-bounce distributions aggregated from G9 candles. Property of the market, not strategy — Layer A per LESSONS B16. No exit logic, no fees, no fill probability. Foundation pointer: T28 commit ea84e74. Producer commit: 1398c39. MANIFEST commit: 37a5216 (sha256-pinned). Validity status: PASSED T21 coherence read 2026-05-04 (4 PASS / 2 INCONCLUSIVE / 0 FAIL). The six-check methodology validation gate from ROADMAP T21 ran in Session 6 Phase 5-ii; 4 cleanly pass (Check 2 premarket vs in_match, Check 3 settlement asymmetry, Check 4 category liquidity-tier dominance, Check 6 YES/NO fold symmetry); 2 inconclusive in informative ways (Check 1 hypothesis shape mismatch per LESSONS B20, Check 5 volume_intensity in_match collapse per LESSONS F30). Downstream Layer B (ROADMAP T31, promoted from G10) and Layer C (ROADMAP G11) cleared to consume. Findings cross-referenced in LESSONS A36, B19, B20, F30.

#### cell_stats.parquet

- File path: arb-executor/data/durable/layer_a_v1/cell_stats.parquet
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- Producer script: arb-executor/data/scripts/build_layer_a_v1.py at commit 1398c39
- Source data: g9_candles.parquet + g9_metadata.parquet (T28 foundation, commit ea84e74)
- Date created: 2026-05-04 (Session 6, 60.7 min producer runtime)
- Depth: 1 (Distribution per TAXONOMY Section 2)
- Data tier used: G
- Schema: 671 cells x ~80 metric columns. Cell key: (category, regime, entry_price_band, spread_band, volume_intensity). Metrics: forward-bounce distribution at horizons {5, 15, 30, 60 min, settlement}, drawdown distribution, breakeven-threshold fractions at {1c, 2c, 5c, 10c, 20c}, n_markets, n_moments per cell.
- Row count: 671 cells (aggregated from 8,981,594 moments across 19,603 markets)
- Validity status: PASSED T21 coherence read 2026-05-04 (4 PASS / 2 INCONCLUSIVE / 0 FAIL)
- Notes: volume_intensity is per-market not per-moment — known v1 caveat documented for v2 follow-up. OTHER category included as fifth bucket beyond ATP_MAIN/ATP_CHALL/WTA_MAIN/WTA_CHALL. **T21 verification findings (2026-05-04, commit pointer in CHANGELOG):** (1) Producer is YES-only — reads yes_bid_close + yes_ask_close exclusively, no_* columns ignored. NO-side distributional questions answerable via fold symmetry per LESSONS A36. (2) Bounce definition is forward_max_excursion_excluding_t (max(yes_ask[i+1:i+window]) - yes_ask[i]) — can be negative for monotonically declining trajectories near settlement. 52% of settlement_zone cells have negative bounce_5min_p25; not a bug, definitional choice consistent with B16 Layer A scoping. (3) Reservoir sampling implements Vitter algorithm (line 167-172) — unbiased percentile estimators. (4) volume_intensity collapses to single bucket (high) within in_match regime per LESSONS F30 — uninformative as in_match stratifier; valid for premarket. (5) No event_ticker preserved per LESSONS B19 — per-event analyses require G12 producer.
- **Audit disposition (2026-05-14):** SUPERSEDED — Pre-rebuild Layer A v1 per-cell distribution outputs, superseded by FOUNDATION-TIER per_minute_features; retained only as a regression cross-check against new Layer A.

#### sample_manifest.json

- File path: arb-executor/data/durable/layer_a_v1/sample_manifest.json
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- Producer script: arb-executor/data/scripts/build_layer_a_v1.py at commit 1398c39
- Source data: same as cell_stats.parquet (T28 foundation)
- Date created: 2026-05-04 (Session 6)
- Depth: 0 (manifest, not analysis)
- Data tier used: G
- Schema: per-cell list of sampled tickers used for visual reproduction
- Row count: 671 cells (one entry per populated cell)
- Validity status: PASSED T21 2026-05-04 (paired with cell_stats.parquet)
- Notes: enables reproducing visual PNGs deterministically; tickers were sampled at producer runtime, not at coherence-read time.
- **Audit disposition (2026-05-14):** SUPERSEDED — Manifest of sampled tickers for visual reproduction; superseded with Layer A v1, relevant only for regression.

#### build_layer_a_v1.log

- File path: arb-executor/data/durable/layer_a_v1/build_layer_a_v1.log
- **Grain:** N/A
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- Producer script: arb-executor/data/scripts/build_layer_a_v1.py at commit 1398c39
- Source data: producer stdout/stderr only
- Date created: 2026-05-04 (Session 6)
- Depth: n/a (operational log)
- Data tier used: n/a
- Schema: text log
- Row count: n/a
- Validity status: n/a (log artifact)
- Notes: 60.7 min runtime, clean exit, memory pressure at 67% during visual phase (paged but did not OOM).
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Build log for Layer A v1; operational artifact with no objective dimension.

#### visual PNGs (15 files)

- File path: arb-executor/data/durable/layer_a_v1/visual_*.png (15 files)
- **Grain:** N/A
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- Producer script: arb-executor/data/scripts/build_layer_a_v1.py at commit 1398c39
- Source data: cell_stats.parquet + sample_manifest.json
- Date created: 2026-05-04 (Session 6)
- Depth: 0 (visual sanity check, not statistical analysis)
- Data tier used: G
- Schema: 5 categories (ATP_MAIN, ATP_CHALL, WTA_MAIN, WTA_CHALL, OTHER) x 3 regimes (premarket, in_match, settlement_zone)
- Row count: 15 PNG files, 8,758,898 bytes total (per MANIFEST commit 37a5216)
- Validity status: PASSED T21 visual review 2026-05-04
- Notes: dense PNGs (ATP/WTA tour-level premarket+in_match) are 800KB-1.1MB each; sparse PNGs (settlement_zone subcategories, OTHER) are 44-273KB. File-size pattern itself is a coverage signal — sparse cells reach the 5-min-pre-settle window or fall into OTHER ticker prefix less often.
- **Audit disposition (2026-05-14):** SUPERSEDED — Visual sanity checks for Layer A v1; superseded as canonical view, still useful for comparison against regenerated visuals from the new foundation.

---


### Layer B v1 outputs (T31b-gamma, foundation T28 ea84e74 + T29 1398c39)

[#layer-b-v1-outputs-t31b-gamma-foundation-t28-ea84e74--t29-1398c39](#layer-b-v1-outputs-t31b-gamma-foundation-t28-ea84e74--t29-1398c39)

Per-cell exit-policy capture distributions across 54-policy parameter grid. Property of strategy given Layer A bounce distribution — Layer B per LESSONS B16. No fees, no fill probability, no slippage; those live in Layer C (G11). Foundation pointer: T28 commit ea84e74 (G9 parquets) + T29 commit 1398c39 (Layer A v1 cell_stats). Producer commit: 28e8ab7. MANIFEST commit: this commit. Validity status: PASSED T31c coherence read 2026-05-05 ET (commit 5cf45e0). 4/4 gating-checks PASS. Cleared for downstream Layer C (G11) consumption.

#### exit_policy_per_cell.parquet

[#exit_policy_per_cellparquet](#exit_policy_per_cellparquet)

- File path: arb-executor/data/durable/layer_b_v1/exit_policy_per_cell.parquet
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- Producer script: arb-executor/data/scripts/build_layer_b_v1.py at commit 28e8ab7
- Source data: g9_candles.parquet + g9_metadata.parquet (T28 foundation, commit ea84e74) + sample_manifest.json (T29 commit 1398c39)
- Date created: 2026-05-05 ET (Session 7 T31b-gamma-1)
- Depth: 5 (strategy simulation per TAXONOMY Section 2)
- Data tier used: G
- Schema: 21 columns. Cell key: (channel, category, entry_band_lo, entry_band_hi, spread_band, volume_intensity). Policy: (policy_type, policy_params). Counts: n_simulated, n_fired, n_horizon_expired, n_settled_unfired. Distributions: fire_rate, capture_mean, capture_p10/p25/p50/p75/p90. Misc: median_time_to_fire, capital_utilization.
- Row count: 19170 ((cell, policy) tuples; 355 cells × 54 policies)
- Validity status: PASSED T31c coherence read 2026-05-05 ET (script commit 5cf45e0, report sha256 72f1747b). 4/4 gating-checks PASS (Check 1 capture-bounded spot-check, Check 2 fire-rate monotonic, Check 3a limit-policy capture_p90 trend, Check 4 premarket vs in_match). 1 informative-only Check 3b INCONCLUSIVE (time-stop horizon trend, empirical signature of mean reversion per LESSONS B21 — not gating). Cleared for downstream Layer C (G11) consumption.
- Notes: 1 cells excluded from output by 50-trajectory threshold (per spec Decision 2 patch 3). 278208 total entry moments evaluated. capital_utilization convention documented inline in producer aggregate_cell_results: held_minutes / denominator (clamped to [0, 1]); denominator = horizon_min for time_stop/limit_time_stop, else 240. T31a patch 5 corrected the validation-gate formulation post-spec; T31a patch 6 dropped sub-minute (30s) horizon, leaving 54 policies in v1.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Layer B v1 per-(cell, policy) simulated capture/fire-rate table; rebuild as exit-optimized realized metrics using foundation-tier per-minute and T38 depth, with vector-specific policies.

### n_profile_v1 — FOUNDATION-TIER per-N measurement universe (Phase-3 full-corpus, gate-validated)

The canonical per-N measurement-universe foundation: one row per player-binary market N, the universe every downstream stratification (Rung 0/1/2) and deployment N-selection screens against. NOT strategy-anchored (distinct from Rung-0 cell_economics which is T-20m strategy-anchored). Foundation pointer: per_minute_features T37 ckpt-3 (inputs sha256 9fde4b5d). Producer commit: a28840e (the Pass-1 per-iteration del + gc-every-200 OOM remediation, probe-proven regimes B+C, validated at full-corpus heavy-tail scale — the only scale that could test it). Spec: docs/n_profile_v1_spec.md (commit chain b43fbaf→ef3add7; both_sides_active_minutes corpus-scoped per G23, §7 row 13). MANIFEST entry: PENDING (data/durable/MANIFEST.md on-disk append, App action — sha256 a7ed1155 preserved in meta.json sidecar + App Phase-3 report). Validity status: PASSED — all 7 gates at full corpus (gate1 row-parity 19614=19614 0-dropout, gate2 0 orphans, gate3 phase-partition-exhaustiveness a/b/c all 0, gate4-7 0 violations), re-validated vs on-disk .new bytes pre-replace (C37). Memory OOM remediation validated at full-corpus heavy-tail scale (~5.7h continuous watch, bounded ~700-720MB plateau, zero OOM — categorically unlike the pre-fix unbounded climb). Lessons earned this arc: LESSONS F35 (tier-3 calibration defect → T37-RECAL deferred), G23 (both_sides_active batch→corpus scoping correction), C38 (operation systematically mistakes sub-corpus bugs for sampling artifacts — 4/4 instances). Cross-reference spec §7 rows 10-13, ROADMAP T37-RECAL.

#### n_profile.parquet

- File path: arb-executor/data/durable/n_profile_v1/n_profile.parquet
- **Grain:** per-N (one row per player-binary market)
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic (measurement universe, not scored)
- Producer script: arb-executor/data/scripts/build_n_profile_v1.py at commit a28840e
- Source data: per_minute_features.parquet (T37 ckpt-3, sha256 9fde4b5d) + g9_trades + g9_candles + g9_metadata, per-ticker pushdown I/O
- Date created: 2026-05-18 (Phase-3 full corpus, ~5h41m detached runtime)
- Depth: 0 (Foundation / measurement universe per TAXONOMY)
- Data tier used: FOUNDATION-TIER (per_minute_features) + G (g9)
- Schema: 19,614 rows x 45 cols, one row per binary N. Sample-quality family incl match_start_method (col 45, F35 tier-3 filter); both_sides_active_minutes (col 40, corpus-scoped per G23); n_minutes_observed (col 44, gate-3 RHS).
- Row count: 19,614 N's (0 dropouts; unique tickers == rows, gate-1 parity exact)
- sha256: a7ed11550e8226f18c22069cc5937d35b184e7f0d2a9264435604a0270c1837e (3,423,678 bytes)
- Validity status: PASSED — 7/7 gates at full corpus 2026-05-18; OOM remediation validated at full-corpus heavy-tail scale
- Notes: match_start_method corpus dist tier-1/2 85.7% / tier-3 6.3% / unknown 6.0% / null 2.1% (tracks F35 ~87.5/6.4/6.1 within the expected shift from 407 no-PMF binary tickers). In-match path exercised 91.5% (the ~1,658 zeros = the F35-characterized irreducible cohort). both_sides_active_minutes corpus-scoped (G23): 97.3% >0, median 95, max 1,354 (≫ the 72/1000 batch-scoped artifact — the adjudicated correction manifest at full corpus). First corpus-scale numbers: in-match volume ~8x premarket at median; ATP_MAIN highest-volume category. timestamps all 2025-06→2026-05 ET (zero 1970 — the 4c100f7 parse fix holds at full scale).
- **Audit disposition (2026-05-18):** CANONICAL — the live per-N measurement-universe foundation; all downstream (Rung 0/1/2 stratification, deployment N-selection, band-free in-match bounce analysis) reads from this.

### inmatch_bounce_surface_v1 — first analytical deliverable (band-free in-match bounce surface, Layer-A-equivalent, gate-validated)

The first analytical deliverable built on the n_profile_v1 foundation. Layer-A-equivalent per LESSONS B16 (property of market — band-free in-match forward-bounce surface as a continuous function of price-level dislocation; NO exit/fees/fills). Spec: docs/inmatch_bounce_surface_v1_spec.md (committed 11dce1c, v0.2 G2-corrected 85118d4, v0.3 classifier-fixed 0e94959). Every structural decision probe-resolved (C38): organizing axis = band-free price-level |mid_close−0.50| (probe-1; bilateral axis near-degenerate, recorded as measured negative in spec §5); pooled with category as level-covariate (probe-2; the operation's ATP_CHALL-tracks-WTA prior does NOT transfer to this axis); A39 dual-metric structurally mandatory (cents↔ROI inversion is category-universal load-bearing structure); A38-safe finite-horizon 30min headline (firewalled gate G3). Foundations pinned: n_profile.parquet sha256 a7ed1155 (lineage c76eee5 / MANIFEST c9a0f3e), per_minute_features.parquet sha256 9fde4b5d (T37 ckpt-3). MANIFEST entry: this commit. Validity status: VALID — all 7 gates PASS at full cohort 2026-05-18 (G1 phase-aware parity 7369+14==7383, G2 regime-purity, G3 A38 ratio 1.866, G4-G7), C37 triple-consistent (on-disk sha == meta == DONE-log). Science reproduces probe-1/2 at full corpus: Spearman(price-level,cents)=−0.995 MONOTONE-DOWN, Spearman(price-level,roi)=+0.722 MONOTONE-UP, cents↔ROI inversion present (A39 vindicated). Provenance: surface built by v0.2 85118d4 (validated Phase-2); validation_report.md regenerated by v0.3 0e94959 (Spearman-classifier fix correcting the v0.2 brittle argmin≤1 false-negative — surface.parquet byte-identical, sha 14241db0 proven unchanged). Lessons this arc: G1/G2 gate-spec defects probe-corrected (v0.2), brittle-classifier false-negative fixed (v0.3, same C38/B20 pattern as the probe-2 classifier). Phase-2 exit-optimization (spec §6, E32) is the defined-not-implemented next stage (B16 staging).

#### surface.parquet

- File path: arb-executor/data/durable/inmatch_bounce_surface_v1/surface.parquet
- **Grain:** per-(price-level-bin × horizon × category) aggregate over in-match minutes (the surface)
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic (descriptive market property — Layer-A-equivalent; exit-optimized is the defined Phase-2 interface, spec §6)
- Producer: arb-executor/data/scripts/build_inmatch_bounce_surface_v1.py — surface built at commit 85118d4 (v0.2), validation_report regenerated at commit 0e94959 (v0.3 classifier fix, surface byte-unchanged)
- Source: n_profile.parquet (cohort screen, sha256 a7ed1155, F35-reliable tier-1/2 live-era) + per_minute_features.parquet (bounce source, sha256 9fde4b5d, T37 ckpt-3), per-ticker pushdown
- Date created: 2026-05-18 (Phase-2 full cohort, ~40min)
- Depth: 1 (first analytical deliverable on the Depth-0 n_profile_v1 foundation)
- Data tier used: FOUNDATION-TIER (per_minute_features) + the n_profile_v1 foundation
- Schema: 800 rows — per (price_level_bin × horizon × category=ALL pooled + 4 category strata). Bounce families: A39 cents (mean/median/p25/p75/p90/frac_positive) AND ROI (same), both mandatory every row; A38 to-settlement diagnostic-only; support (n_minutes/n_tickers/low_support); B22 fill-distribution (time_to_match_start_min quantiles).
- Row count: 800 (40 quantile price-level bins × 4 finite horizons × 5 category-levels, minus empty cells)
- sha256: 14241db05183ff214aec80b0cbf72d3d194c931d6e8548ec493941bdf8a5f655 (65903 bytes)
- Validity status: VALID — 7/7 gates at full cohort 2026-05-18; science reproduces probe-1/2
- Notes: cohort 7,369 contributing / 14 dropouts (7,383 screened); 692,034 in-match minutes. Pooled-30min: cents MONOTONE-DOWN ρ=−0.995 (max at coin-flip ~0.199, → ~0.018 at price extreme), ROI MONOTONE-UP ρ=+0.722 (rising to cheap extreme ~0.83), ROI second-order mid-trough at bin 14/39 (characterized per B20, not assumed). G3 A38 saturation 1.866× (to-settlement diagnostic-only). SCALP sensitivity strengthens with horizon (cents 0.035→0.166, roi 0.104→0.572 over 5→60min).
- **Audit disposition (2026-05-18):** CANONICAL — the validated band-free in-match bounce surface; the descriptive (Layer-A-equivalent) foundation that the Phase-2 exit-optimization layer (spec §6, E32) will be built on. First analytical deliverable post foundation-rebuild.

### spike_volatility_map_v1 — four-category exit-or-hold descriptive atlas (T42, gate-validated, strategy-anchored Layer-A-equivalent)

The strategy-anchored descriptive lock-down of per-cell hindsight-optimal exit-or-hold rules across the four tennis categories (ATP_MAIN, WTA_MAIN, ATP_CHALL, WTA_CHALL). Layer-A-equivalent per LESSONS B16 (descriptive market measurement; NO predictive claim, NO realized-fill assumption beyond taker-floor anchoring, NO Layer C economics). Operationally distinct from inmatch_bounce_surface_v1: that surface is band-free in-match bounce as a market property; the atlas is per-cell × exit-or-hold ROI from T-20m taker anchors with the cells as the primary axis. The two are siblings, not nested. Both serve as the descriptive foundation the execution-lock arc will be validated against.

Spec: methodology described inline in the four LOCKED_DOWN.md files (no standalone .md spec — methodology was iterated through Plex rounds 1-4 and the canonical version is what the LOCKED_DOWN files describe). Canonical reproducible producer: `arb-executor/data/scripts/build_spike_perN.py` at commit `c5e377f`. Methodology summary: per-cell argmax over reachable exit targets +X cents (X capped at 99-anchor_cents); per-N payoff = spike-to-+X-with-≥250ct realized as +X, else hold-to-settlement (winner = +(99-anchor), loser = -(anchor-1)). Three cell resolutions reported side-by-side per Plex round-2 recommendation (1c / 2c / 3c) — neither "more correct," they describe corpus pay-outs at three cell-granularity levels. Foundations pinned: n_profile.parquet sha256 `a7ed1155` (lineage c76eee5 / MANIFEST c9a0f3e), per_minute_features.parquet sha256 `9fde4b5d` (T37 ckpt-3), g9_trades.parquet (T28 ea84e74) for spike measurement. MANIFEST entry: PENDING (Stage 0 Commit 5 will add the atlas to MANIFEST.md with full sha256 lineage). Validity status: LOCKED — four-category byte-verified on origin/main at HEAD `d99c6e9`; producer reproduces ATP_MAIN + WTA_MAIN parquets byte-identical to commit `9912660` artifacts. Methodology Plex-confirmed in round 4 dialogue. Lessons this arc: A39 cent-vs-ROI geometry confirmed empirically (cheap-cell ROI dominance), 2c pooling diagnostic showed real cell-by-cell heterogeneity (not pure over-optimization), OOS rabbit-hole produced LESSONS-level clarification that the descriptive deliverable is well-posed without predictive testing. Subsequent: deployment philosophy locked at "trade all 90 cells per category, do not cherry-pick" — volume is the operational constraint, execution work resolves marginals.

#### spike_volatility_map atlas (six commits 481de7f → d99c6e9)

- **File paths:** arb-executor/data/durable/spike_volatility_map/{ATP_MAIN,WTA_MAIN,ATP_CHALL,WTA_CHALL}_spike_perN.parquet (4 files), {atp_main,wta_main,atp_chall,wta_chall}_descriptive_{1c,2c,3c}.parquet (12 files), {ATP_MAIN,WTA_MAIN,ATP_CHALL,WTA_CHALL}_LOCKED_DOWN.md (4 files), PAIRING_DIAGNOSTIC.md, CROSS_CATEGORY_MAP.md (pre-Challenger; flagged stale; deprecation pending in Stage 0 Commit 6).
- **Grain:** per-N for spike per-N parquets (one row per qualifying N with anchor/spike/peak/settlement); per-cell for descriptive parquets (one row per cell at the given resolution).
- **Vector:** vector-agnostic
- **Objective:** exit-optimized (the descriptive primitive emits per-cell hindsight-optimal exit-or-hold rules)
- Producer: arb-executor/data/scripts/build_spike_perN.py at commit `c5e377f` — canonical reproducible. Takes --category {ATP_MAIN,WTA_MAIN,ATP_CHALL,WTA_CHALL} --output /path.parquet. Reproduces ATP_MAIN + WTA_MAIN byte-identical to commit `9912660` artifacts.
- Source: n_profile.parquet (cohort screen) + per_minute_features.parquet (entry-anchor context) + g9_trades.parquet (spike measurement walk over [t20m_trade_ts, settlement_ts]).
- Date created: 2026-05-19 (ATP_MAIN + WTA_MAIN initial, commit 9912660) through 2026-05-20 (full four-category lock, atlas HEAD d99c6e9).
- Depth: 1 (descriptive aggregation across full corpus; first analytical deliverable that produces deployment-ready per-cell rules).
- Data tier used: FOUNDATION-TIER (per_minute_features) + G (g9_trades) + n_profile_v1 cohort.
- Schema (spike per-N parquets): per-N rows with ticker, event_ticker, category, t20m_anchor_price, spike_cents, spike_pct, peak_yes_bid, size_qual_max_250, settlement_value, realized_at_settlement, truncation_delta_cents.
- Schema (descriptive parquets): per-cell rows with cell_key (1c/2c/3c resolution), anchor_band, n, best_X, total_$, capital_$, ROI%, hold_count, negative_flag.
- Row counts: 14,033 total spike per-N rows across four categories (ATP_MAIN 4,137; WTA_MAIN 3,683; ATP_CHALL 5,326; WTA_CHALL 887). 4 × 90 = 360 descriptive rows at 1c resolution; 4 × 45 = 180 at 2c; 4 × 30 = 120 at 3c.
- Validity status: LOCKED — four LOCKED_DOWN.md files committed on origin/main at HEAD d99c6e9; PAIRING_DIAGNOSTIC committed at d99c6e9 confirms 79.3% event-level paired rate (6,208 of 7,825 events). Canonical producer reproduces atlas byte-identical for ATP_MAIN + WTA_MAIN.
- Notes: Three-axis caveat (load-bearing for every headline number) recorded verbatim in each LOCKED_DOWN.md and in SESSION_HANDOFF.md. AXIS 1 exit-side fill realism pushes DOWN (expected realized 0.4-0.8× of simulated per B25/Cat-11). AXIS 2 entry-side maker improvement pushes UP (expected ~+10-30% on headline; the bot's 97%-Scenario-C_discount thesis lives here). AXIS 3 arrival frequency (G22) not collapsed (N/day × ct/N never combined into a single number). Corpus blended +8.70% per-trade ROI at 10ct; max-overlap operational picture ~91 N/day, ~$460 capital/day, ~$40.62 earnings/day before execution adjustments.
- **Audit disposition (2026-05-20):** CANONICAL — the strategy-anchored descriptive deliverable. Per-cell hindsight-optimal rules at three resolutions. NOT a predictive rule (the deployable rule shape is an open question pending paper-mode validation). NOT deployable dollars (three-axis caveat between headline and realized PnL). The execution-lock arc validates against these hindsight rules; the deployable rule shape is downstream.

### exit_optimized_bounce_v1 — Phase-1 PASS, Phase-2 halted-then-gate-fixed, not re-run (T39.2, superseded by T42 atlas)

Phase-2 exit-optimization producer per spec v0.1 → v0.4 (commits `de62d7f`, `8e8f46e`, `5020f10`, `d23fff5`). Layer-B-equivalent per LESSONS B16 (descriptive market measurement at the band level with exit-optimization, downstream of validated Layer A `inmatch_bounce_surface_v1` at commit `6f1d4bd`). Dual conservative-fill frame design (per operator decision option 3): both Frame I (idealized) and Frame P (probabilistic) emitted with cross-frame robustness as headline. T-20m reinterpreted as conservative FV-anchored fill assumption (not axiom). Foundations pinned at producer level: per_minute_features `9fde4b5d` / n_profile `a7ed1155` / Layer-A surface `14241db0`.

**Status: Phase-1 PASS, Phase-2 halted then gate-fixed, never re-run.** Phase-1 (direction-sanity smoke) PASSED with byte-identical 0/40 violations (Frame-I exit-opt ≤ Layer-A unconditional, A38/no-stop/ranking-integrity all PASS). Phase-2 v0.3 halted with n_violations=1, exactly the lone extreme-dislocation Frame-P band (idx39, n=27) that the G7 probe predicted; producer correctly set low_support=True but the gate still hard-counted it. v0.4 (commit `d23fff5`) fixed the G7 exemption logic (violation count excludes low_support=True bands). Phase-2 not re-run after the v0.4 gate-fix landed because the atlas (T42) approach was prioritized and ate the deployment-ranking lane between 2026-05-18 and 2026-05-20.

Spec/producer iteration this arc: spec v0.1 `de62d7f` → producer v0.2 G2/G7 probe-grounded fixes `8e8f46e` → producer v0.3 G7 Frame-P phase-aware `5020f10` (corrects v0.2 phase-blindness) → producer v0.4 G7 low_support exemption `d23fff5` (corrects v0.3 spec-contradicting hard-count). Producer sha256 of v0.2 canonical (the file that ran Phase-1): `fea91dc085e241e37389cf516fb08dd4b26069482f878c5fc5d1330172f5b59a`.

#### build_exit_optimized_bounce_v1.py (T39.2, Phase-2-halted)

- **File path:** arb-executor/data/scripts/build_exit_optimized_bounce_v1.py (commit `d23fff5` v0.4)
- **Output:** would write to arb-executor/data/durable/exit_optimized_bounce_v1/ on Phase-2 re-execution; directory does not exist on origin/main; MANIFEST entry never landed.
- **Grain:** per-band (40 band × 2 frame × per-band exit-opt result)
- **Vector:** vector-agnostic
- **Objective:** exit-optimized (Phase-2 exit-optimization at band level with dual conservative-fill frame)
- Producer script: arb-executor/data/scripts/build_exit_optimized_bounce_v1.py at commit `d23fff5` (v0.4 — G7 gate-exemption aligned to spec design).
- Spec: arb-executor/docs/exit_optimized_bounce_v1_spec.md at commit `de62d7f` (v0.1, ASCII-clean, single-concern).
- Source data: inmatch_bounce_surface_v1 surface.parquet (sha256 `14241db0`) + n_profile.parquet (sha256 `a7ed1155`) + per_minute_features.parquet (sha256 `9fde4b5d`).
- Date created: 2026-05-19 ET (spec v0.1 + producer v0.2 ran Phase-1 successfully) through 2026-05-20 ET (v0.4 gate-fix landed, Phase-2 not re-run).
- Depth: 2 (Layer-B-equivalent per B16; exit-optimization downstream of Layer A descriptive surface).
- Data tier used: derived from FOUNDATION-TIER (per_minute_features) via n_profile_v1 + inmatch_bounce_surface_v1 lineage.
- Schema: dual Frame I + Frame P emission with cross-frame robustness as headline. Band-level rows with exit-optimized bounce metrics, low_support flag, gate status per spec.
- Validity status: **superseded** (preserved-not-deprecated). Phase-1 PASSED; Phase-2 v0.3 halted at G7 violation (correctly flagged extreme-dislocation band); v0.4 gate-fix landed but Phase-2 never re-run. Direction-sanity invariant holds (0/40 bands; gate edits cannot alter exit_bounce_c_mean). Science untouched per v0.2/v0.3/v0.4 commit messages.
- Notes: This and Rung 1 (T39.1) are the two superseded parallel attempts that the atlas (T42) ate. Different methodology than atlas: band-level rather than cell-level, dual conservative-fill frame rather than taker-floor anchoring, Layer-B-equivalent rather than Layer-A-equivalent. Operator decision: preserve-not-deprecate. Code available if future work wants the dual-frame approach or the band-level Phase-2 exit-optimization framing.
- **Audit disposition (2026-05-21, Stage 0):** SUPERSEDED-PRESERVED — committed code on origin/main, Phase-1 PASSED, Phase-2 halted-then-gate-fixed but never re-run. Open question on formal retirement vs retroactive Phase-2 run tracked at SESSION_HANDOFF.md Open Uncertainty #7.

### rung1_strategy_evaluation_v0.3.2 — committed producer, never run (T39.1, superseded by T42 atlas)

The Rung 1 strategy_evaluation producer per the recomputation ladder framework (data/analysis/recomputation_ladder.json), built to spec v0.3.2 at commit `5fc6d40`. Two-artifact continuous design: dense per-cell exit curve Artifact A (cell_key × 1-98c exit lines, 7,056 rows full) plus per-cell argmax optimum Artifact B (72 rows, cents/ROI/Sharpe per A39, pure deterministic read of A). Three statistical functions implemented at v0.3.2: Wilson CI (closed-form, unit-verified), BCa bootstrap (n=1,000, jackknife accel, Acklam-ppf fallback when scipy absent), ratio-direct BCa Sharpe/Sortino. Seven hard gates + one soft per spec §6.1 including load-bearing gate-7 summary-derivation-consistency. C37 two-`.new` discipline + meta sidecar. ARTIFACT_A_COLUMNS=28, ARTIFACT_B_COLUMNS=32, EXIT_LINES_CENTS=98 per spec §3.2.

**Status: committed-but-never-run.** Per commit message `5fc6d40`: "PHASE-1 DATA SMOKE PENDING: Rung 0 corpus cell_economics.parquet (sha256 6fdd019d...) is VPS-resident, not git-tracked by design; phase-1 integration smoke + phase-3 full run both execute on VPS via App where the corpus lives. Operator explicitly waived the local-smoke gate (data physically VPS-only)." Phase-1 smoke and Phase-3 full run were intended for subsequent App-driven execution that never happened — the atlas approach (T42) took over the per-cell exit-rule lane between 2026-05-18 and 2026-05-20 with different methodology (taker-floor anchoring, 1c/2c/3c resolutions, four-category sweep rather than the 72-cell × continuous-exit-axis design).

Spec arc: v0.1 → v0.2 → v0.3 → v0.3.1 → v0.3.2 (commits `92198d6`, `59c3f14`, `ba09107`, `c916c50`, `3bbac37`). Producer iteration: `6d284bb` (Phase-A skeleton) → `168728d` (pandas 3.0 + pyarrow 24 compat) → `4d1cec3` (corpus_active_days bugfix) → `5fc6d40` (Phase-B real Wilson + BCa, build-ready at v0.3.2). G22 alignment landed at spec commit `2e1d49e9` (daily_opportunity_rate corrected from cts/day to N's/day).

#### build_rung1_strategy_evaluation.py (T39.1, committed not run)

- **File path:** arb-executor/data/scripts/build_rung1_strategy_evaluation.py (commit `5fc6d40`)
- **Output:** would write to arb-executor/data/durable/rung1_strategy_evaluation/ on execution; directory does not exist on origin/main; MANIFEST entry never landed.
- **Grain:** per-cell (Artifact A 7,056 rows = 72 cells × 98 exit lines; Artifact B 72 rows = 72 cells × per-cell-optimum)
- **Vector:** vector-agnostic
- **Objective:** exit-optimized (per-cell argmax over continuous exit axis)
- Producer script: arb-executor/data/scripts/build_rung1_strategy_evaluation.py at commit `5fc6d40`, build-ready against spec v0.3.2.
- Spec: arb-executor/docs/rung1_strategy_evaluation_spec.md at commit `3bbac37` (v0.3.2, internally consistent and build-ready).
- Source data (would be): arb-executor/data/durable/rung0_cell_economics/cell_economics.parquet (sha256 `6fdd019d`, Rung 0 output — VPS-resident, not git-tracked).
- Date created: 2026-05-15 ET (initial Phase-A skeleton) through 2026-05-19 ET (Phase-B v0.3.2 build-ready).
- Depth: 1 (descriptive aggregation per cell with CI intervals).
- Data tier used: Rung 0 output (downstream of FOUNDATION-TIER per_minute_features).
- Schema: documented in spec v0.3.2 §3.2. Artifact A: 28 columns (cell_key, exit_line_c, plus 26 metric columns per spec §3.1). Artifact B: 32 columns (cell-level summary + per-A39-axis argmax point with CIs).
- Validity status: **superseded** (preserved-not-deprecated). Code committed and build-ready; Phase-1 smoke + Phase-3 full run never executed. The atlas (T42) ate the lane this would have occupied with different methodology.
- Notes: Operator-decision per SESSION_HANDOFF.md Open Uncertainty #7 — "do we ever want to run them retroactively for cross-validation? Or formally retire? Operator call." Preserved-not-deprecated status reflects current ambiguity: code is available if future work wants the Rung-framing (continuous exit axis at fixed 72-cell resolution, Wilson + BCa intervals, A39 cents/ROI/Sharpe separated optima). Different shape than atlas (atlas uses taker-floor anchoring + 1c/2c/3c resolutions; Rung 1 used mid-price entry + continuous exit-axis at 5¢ bands).
- **Audit disposition (2026-05-21, Stage 0):** SUPERSEDED-PRESERVED — committed code on origin/main, never executed, lane eaten by T42 atlas. Open question on formal retirement vs retroactive run tracked at SESSION_HANDOFF.md Open Uncertainty #7.

### Layer C v1 specification (T32a, foundation T28 ea84e74 + T29 1398c39 + T31b 28e8ab7)

[#layer-c-v1-specification-t32a-foundation-t28-ea84e74--t29-1398c39--t31b-28e8ab7](#layer-c-v1-specification-t32a-foundation-t28-ea84e74--t29-1398c39--t31b-28e8ab7)

Realized economics from empirical fees on top of Layer B v1's idealized-fill capture distributions. Per LESSONS B16 layered-realism discipline, Layer C has its own v1/v2/v3/v4 sub-staging; v1 adds ONE modeling concept (empirical fees from kalshi_fills_history.json per A30) and inherits idealized fills from Layer B v1. v1 strictly per-cell per E20, single-leg per E18, channel-preserving per E16/B14/E31, ROI on cost basis per G1. Foundation pointers: T28 commit ea84e74 (G9 parquets, sha256-pinned) + T29 commit 1398c39 (Layer A v1 cell_stats) + T31b commit 28e8ab7 (Layer B v1 exit_policy_per_cell.parquet, sha256 d94bc56c..., validated by T31c PASS at 5cf45e0). Spec commit: 4bed07f. MANIFEST entry: PENDING T32b/T32c (no output artifacts yet — spec only). Validity status: SPEC (not output-bearing). T32b (producer build_layer_c_v1.py) and T32c (coherence read check_layer_c_v1_coherence.py + report) will add output artifacts in subsequent commits.

#### docs/layer_c_spec.md

[#docs-layer-c-spec-md](#docs-layer-c-spec-md)

- File path: docs/layer_c_spec.md
- **Grain:** N/A
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- Authored: 2026-05-05 ET (Session 8, T32a)
- Author commit: 4bed07f
- Length: 189 lines, 9 sections
- Structure: Scope (v1) + Foundation pointers + Operational decisions (6 numbered) + Output schema (32 columns) + Producer architecture + Validation gate (4 gating + 1 informative checks) + Open items for v2/v3/v4 + Cross-references (16 keystone lessons) + Outstanding ROADMAP correction
- Key decisions: D1 empirical fee derivation per (is_taker, yes_price_bucket) from kalshi_fills_history.json — NOT maker-zero (37.7% of bot maker fills are non-zero, parabolic per Kalshi schedule); D2 maker-maker production model with policy-class taker-exposure for time-stop horizon-fired exits; D3 1:1 row mapping to Layer B (no posting_strategy or capital_size sweep dimensions); D6 formation-period contamination per E12 inherited explicitly with Check 5 measuring impact informatively
- Validation gate: Check 1 realized_capture ≤ capture; Check 2 parabolic-shape match; Check 3 policy-class taxonomic match; Check 4 Layer B → Layer C ranking preservation (≥90% cells Spearman ≥ 0.99); Check 5 (informative-only) formation-period contamination measurement
- Validity status: SPEC stable post-author. Closes T32a when this ANALYSIS_LIBRARY entry lands.
- Notes: Spec Section 9 explicitly flags ROADMAP T32 entry (commit f048267) as needing correction — currently states "maker-zero canonical confirmed empirically" which is empirically wrong per Decision 1. Correction follows in separate single-concern commit.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Layer C v1 spec codifying fee model and realized_capture definition; aligned with exit-optimized thinking, remains valid as design pending fee-table and input updates.

## SECTION 3: BROKEN OR INVALID ANALYSES

Analyses that ran but produced invalid results due to bugs, methodology errors, or data corruption. Listed here so future chats know not to cite their conclusions.

#### Greeks decomposition (Depth 4)
- **Files:** /tmp/per_cell_verification/greeks_decomposition.csv, /tmp/per_cell_verification/greeks_per_match.csv.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Lesson:** F11.
- **Issue:** Degenerate first-bid bug. Schema is correct; numbers are not trusted.
- **Status:** Awaiting rebuild on cleaner data.
- **Audit disposition (2026-05-14):** BROKEN — Degenerate first-bid bug invalidates numbers; rebuild under exit-optimized model: YES — a cleaned Greeks-style microstructure panel over foundation+T38 would be valuable if tightly scoped.

#### Bias reconciliation fragmentation (Depth 2 + 6)
- **Files:** Six+ entries in F19 cluster above.
- **Grain:** per-tick
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Lesson:** F19.
- **Issue:** Multiple files measuring overlapping but non-identical concepts; "operator memory says +21-37c, file shows max 10.6c" discrepancy persists.
- **Status:** Awaiting canonical designation.
- **Audit disposition (2026-05-14):** BROKEN — Fragmented bias-from-BBO analyses leave a key discrepancy unresolved; rebuild under exit-optimized model: YES — a single canonical bias-reconciliation using FOUNDATION-TIER + T38 is worth queuing.

#### matches.entry_time-dependent analyses
- **Files:** Any analysis depending on matches.entry_time on live/live_log rows.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Lesson:** F17.
- **Issue:** Column is NULL on every live and live_log row sampled.
- **Status:** Re-derive entry timing from JSONL logs (tz-clean per F16) or cell_match events.
- **Audit disposition (2026-05-14):** BROKEN — Any analysis relying on matches.entry_time is structurally invalid; rebuild under exit-optimized model: YES — must reconstruct entry times from JSONL logs then re-score under exit-optimized metrics.

#### Pre-Bug-3-fix entry_price-dependent analyses
- **Files:** Any analysis using entry_price from bot reconcile-path-affected windows.
- **Grain:** per-fill
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Lesson:** F6.
- **Issue:** Reconcile path was unconditionally overwriting Position.entry_price every 60 seconds before the Apr 29 fix.
- **Status:** Validity depends on fill date relative to fix.
- **Audit disposition (2026-05-14):** BROKEN — entry_price overwritten by the reconcile path pre-fix; rebuild under exit-optimized model: PARTIAL — contaminated windows re-run with corrected entry fields and exit-optimized scoring, uncontaminated windows retained.

#### Settlement-event-dependent P&L
- **Files:** Any per-cell P&L analysis using log-based settlement detection.
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Lesson:** F8.
- **Issue:** When bot resting sell is unfilled at market close, NO settlement event is logged. Position loss is invisible.
- **Status:** Bug 4 remediation in progress; analyses await fix.
- **Audit disposition (2026-05-14):** BROKEN — Log-based settlement omission makes P&L under-report losses; rebuild under exit-optimized model: YES — recompute from reconstructed positions with correct settlement and exit-optimized objective once Bug 4 remediation lands.

---

## SECTION 4: NOTABLE PRIOR FINDINGS (currently asserted)

Findings from prior analyses that are currently treated as anchor evidence in the operation. Each must be classified to its proper depth and noted with the limits of that depth.

#### 70.7% bilateral double-cash rate at +10c (April 14, 458 paired matches)
- **Depth:** 0 (existence proof).
- **Grain:** match-aggregate
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Variables used:** first_price and max_price both sides.
- **Tier:** C (historical_events).
- **Strict reading:** Bilateral oscillation exists at the +10c threshold across 458 matches.
- **Does NOT establish:** Capturability, fillability, profitability, or per-cell consistency.
- **References:** LESSONS.md E18 (amended Session 9 — names this finding as the conditional-rate layer of the bilateral funnel; B23 amendment commit d56edfd introduces the upstream feasibility layer at 29.8%; multiplicative composition ~21-23% unconditional double-cash rate), E25 (depth-0 caveat — applies to the conditional-rate layer), E30 (subset-averaging caveat — applies to the conditional-rate layer).
- **Reproduction status:** Pending. ROADMAP Section 4 BLOCKED.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Pre-vector legacy bilateral existence proof; recompute as exit-optimized average realized bounce per cell band from T-20m entry, with prematch/in-match phase attribution.

#### Channel 1 vs Channel 2 split (4.7% / 95.3%)
- **Depth:** 2 (trajectory).
- **Grain:** match-aggregate
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Producer:** /tmp/channel_decomp.py (current session).
- **Variables used:** JSONL log entry_filled and exit_filled events; ts_et fields.
- **Strict reading:** Of the 977 fills with exit_filled events, 4.7% exited before match start (Channel 1) and 95.3% exited after (Channel 2).
- **Does NOT establish:** Whether this distribution holds for cells that have higher pregame oscillation; whether the 95.3% reflects desired bot behavior or accidental settlement-ride.
- **References:** LESSONS.md E15, E16, E17.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Routing/flow-allocation statistic by channel; describes traffic distribution, not performance vs any objective.

#### 977-fill realized P&L (Mar 26 to Apr 17): -$1,339.52
- **Depth:** 5 (strategy simulation, retrospective).
- **Grain:** match-aggregate
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Variables used:** matches table fill records (live + live_log).
- **Strict reading:** Bimodal P&L distribution confirms riding-to-settlement mechanism.
- **Caveats:** F7 (some fills recorded wrong), F8 (settlement events sometimes unlogged), F17 (entry_time NULL).
- **References:** LESSONS.md Section 2.
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Legacy live-bot hold-to-settlement P&L on 977 fills; recompute as exit-optimized ROI/bounce per cell band with phase-state breakdown on the foundation corpus.

#### Apr 24 to Apr 29 post-retune: 106 resolved at +$17.21 net
- **Depth:** 5.
- **Grain:** match-aggregate
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Caveats:** 58 still resting (unknown outcome); E8 (retune isolation problem — 14 cell disables + 8 exit retunes + 12 code changes simultaneously).
- **Audit disposition (2026-05-14):** NEEDS RECOMPUTATION — Legacy live-bot settlement-scored slice; recompute as exit-optimized realized ROI/bounce per cell band over that window with PHASE_1/2/3 attribution.

---


#### Combined-trade-price distortion absence (Cat 9, Session 9, commit 631e653)
- **Depth:** 0 (existence proof — null result).
- **Grain:** per-tick
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Producer:** data/scripts/diagnostics_session_8/cat_09_distortion_events.py (sha256 `653e9d74888376f1`, runtime 643s).
- **Data tier used:** G (g9_trades.parquet + g9_candles.parquet).
- **Variables used:** g9_trades (33,727,162 rows × 20,018 markets), g9_candles per-minute close prices, derived combined = yes_close + no_close per minute.
- **Question answered:** Across the full G9 corpus, do any per-minute candle bins exhibit combined trade price exceeding $1.00 + ε (ε=$0.01)?
- **Strict reading:** Zero events found. Zero of 20,018 markets had even one flagged minute. Per-tier: historical 0 of 1,838,273 minutes; live 0 of 1,397,886 minutes. Per-stage (formation / post-formation / in-match) distribution: empty.
- **Does NOT establish:** Absence at finer ε (e.g., $0.005, half-tick), absence of sub-minute distortions resolved before per-minute close binning, absence of microsecond intraminute distortions, absence of the converse direction (combined < $1.00 bilateral discount, which is B23's mechanism and was not Cat 9's measurement target).
- **Strategic implication:** F32's sub-claim (1) — combined > $1.00 over-pay distortions as direct alpha — is downgraded from alpha signal to alpha hypothesis pending deeper-probe disambiguation. T34 closed as superseded.
- **References:** LESSONS.md F32 (amended), LESSONS.md C31 (new — meta-lesson), ROADMAP.md T34 (closed), SIMONS_MODE.md Section 8.
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Microstructure correctness check; confirms no systematic combined-price distortion in the tape.


#### Premarket trajectory width and bilateral feasibility (Cat 6, Session 9, commit 631e653)
- **Depth:** 0–1 (existence + distribution of trajectory width across the corpus).
- **Grain:** per-minute
- **Vector:** vector-B
- **Objective:** objective-agnostic
- **Producer:** data/scripts/diagnostics_session_8/cat_06_trajectory_width.py (sha256 `c5280167c244eefb`, runtime 236s).
- **Data tier used:** G (g9_candles.parquet + g9_metadata.parquet for filtering to markets with sufficient premarket coverage).
- **Variables used:** g9_candles per-market premarket bid/ask, derived trajectory width = max(yes_close) − min(yes_close) over each market's premarket window; g9_metadata _tier for historical / live partition.
- **Question answered:** Across the G9 corpus, what is the distribution of premarket trajectory width per market, and what fraction of markets meet the B23 bilateral-mechanism feasibility bar (≥$0.10 trajectory width)?
- **Strict reading:** 9,238 markets had sufficient premarket data. Distribution: median $0.05, p25 $0.02, p75 $0.12, p95 $0.51, mean $0.116. Per-threshold: ≥$0.05 → 48.8% (4,505); **≥$0.10 → 29.8% (2,755)**; ≥$0.20 → 16.7% (1,545); ≥$0.30 → 11.1% (1,027). Per-tier: historical 33.2%, live 28.2%. Top-20 widest trajectories all >$0.90 (extreme favorite settlements).
- **Does NOT establish:** Bilateral-fill probability at any cell or price (orderbook depth at non-BBO is the F33/G13 gap), conditional double-cash rate given paired entries (that is the E18/E30 layer of the funnel), per-cell bilateral capture rate (Layer A/B aggregations don't stratify on trajectory width yet — gap), why the live-vs-historical 5pp gap exists structurally.
- **Strategic implication:** B23's bilateral-mechanism prevalence is empirically 29.8% of markets, not "broadly applicable." Funnel structure named explicitly: 29.8% feasibility × ~70-76% conditional success ≈ ~21-23% unconditional double-cash rate. Forensic replay's bilateral evaluation should compute cell-level applicability against the 29.8% feasibility bound. Trajectory width should be a Layer A v2 / B v2 cell-key partition axis or filter for bilateral-relevant analyses.
- **References:** LESSONS.md B23 (amended this commit), LESSONS.md E18 / E25 / E30 (the conditional-rate funnel layer — separate amendment trajectory), SIMONS_MODE.md Section 3 paragraph 4 + Section 8 (forward-references that this commit backfills), F33 (depth-chain gap — independent measurement bottleneck for the next funnel layer).
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Characterizes prematch price-path width and structural bilateral feasibility; a market-trajectory property, not a strategy return.


#### Cross-ticker OI asymmetry distribution (Cat 10, Session 9, commit 631e653)
- **Depth:** 0–1 (existence + distribution of cross-ticker OI asymmetry across the corpus).
- **Grain:** match-aggregate
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Producer:** data/scripts/diagnostics_session_8/cat_10_oi_asymmetry.py (sha256 `c09956376f9745ba`, runtime 43s).
- **Data tier used:** G (g9_metadata.parquet for paired-match enumeration + g9_candles.parquet for per-ticker final OI via candle.open_interest_fp).
- **Variables used:** g9_metadata event_ticker for pairing, derived OI_asymmetry = max(OI_yes_a, OI_yes_b) / min(OI_yes_a, OI_yes_b) per paired event in the live tier (historical tier omitted per F31's known OI-zero coverage gap).
- **Question answered:** Across the G9 corpus, what is the distribution of cross-ticker OI asymmetry for paired matches with non-zero OI both sides, and at what threshold does the asymmetry begin to be strategically applicable for ladder-on-deeper-side strategy?
- **Strict reading:** 8,106 tickers with OI data; 4,053 paired events with both tickers carrying OI; 4,044 paired matches with non-zero OI both sides used for distribution. Distribution: median 1.48×, p75 2.01×, p95 3.36×, max 38.68× (KXWTACHALLENGERMATCH-26APR26SIDZHU: SID 31 vs ZHU 1199). Per-threshold: **≥2× → 1,024 (25.3%, strategic threshold)**; ≥4× → 97 (2.4%, original anchor tail location); ≥10× → 10 (0.2%, extreme tail). DZU/MAN corpus reproduction: 38 paired matches in corpus, max observed 4.23× (KXATPMATCH-26APR22BUSMAN); the original Dzumhur/Mannarino ATP Rome screenshot (4.15×) pre-dates corpus cutoff and is not directly reproducible.
- **Does NOT establish:** Why specific paired matches exhibit higher asymmetry (no model linking match-level features to expected asymmetry); whether asymmetry persists or oscillates within a market's lifetime (Cat 10 measures final OI only, not trajectory); per-cell asymmetry breakdown (Layer A/B/C aggregations don't stratify on cross-ticker OI asymmetry yet — gap); depth-level asymmetry beyond OI (F33/G13 gap); asymmetry in historical tier (excluded due to F31 OI coverage gap).
- **Strategic implication:** B24's "ladder-on-deeper-side" strategy threshold shifts from 4× (rare-tail, 2.4% applicability) to 2× (strategic-threshold, 25.3% applicability) for design purposes. The original 4× anchor remains valid as a single-event operator-witnessed observation but sits at the top 2-3% tail of the distribution rather than being typical. Forensic replay evaluation (per SIMONS_MODE.md Section 6) of ladder-on-deeper-side cells should surface both 2× threshold (strategic mass) and 4× threshold (tail-event sensitivity) coverage rates.
- **References:** LESSONS.md B24 (amended this commit), LESSONS.md B22 / B23 / C31 (mechanism context, adjacent amendments), F31 (per-minute OI partially tracked at candle level — Cat 10's data source), F33 (depth-chain asymmetry separate gap, not addressable from current data), T33 (B24 4× anchor reference — Cat 10 contextualizes without invalidating), SIMONS_MODE.md Section 8 (forward-reference that this commit backfills).
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Structural market property — how open interest distributes between paired sides; informs opportunity structure, not outcomes.


#### Per-(cell, policy) EV distribution by channel (Cat 5, Session 9, commit 631e653)
- **Depth:** 1 (distribution of per-(cell, policy) capture_mean across the simulator's full output, partitioned by channel).
- **Grain:** per-cell
- **Vector:** vector-agnostic
- **Objective:** settlement-scored
- **Producer:** data/scripts/diagnostics_session_8/cat_05_alpha_discovery.py (sha256 `df8257a183e4c637`, runtime 1s).
- **Data tier used:** Derived from layer_b_v1/exit_policy_per_cell.parquet (which derives from G-tier g9_trades + g9_candles).
- **Variables used:** capture_mean per (channel, category, entry_band_lo, entry_band_hi, spread_band, volume_intensity, policy_type, policy_params); 19,170 rows total across 3 channels (premarket / in_match / settlement_zone).
- **Question answered:** Across the simulator's full (cell, policy) output, what is the distribution of capture_mean by channel, and where do the top-EV cells concentrate?
- **Strict reading:** Channel-level summary: in_match 6,480 cells (mean −$0.034, median −$0.026, max $0.393); premarket 12,690 cells (mean −$0.069, median −$0.034, max $0.509). **Aggregate statistics favor in_match (typical cell less negative); right-tail statistics favor premarket (top-EV cells concentrate there — 7 of top 10 overall, max 0.509 vs 0.393).** Top premarket cell: WTA_MAIN 40-50 / tight / low / time_stop. Both channels have negative cell-level mean and median — the strategic distinction lives at the right tail, not at the aggregate.
- **Does NOT establish:** Why the top-tail premarket cells achieve their EV (Cat 5 reports the EV but not the underlying retail-behavior pattern that creates the bouncability); fee-adjusted EV (Layer B v1 is gross; Cat 2 fees apply post-hoc per Layer C v1 spec); execution feasibility at simulated EV (queue position, F33/G13 depth-chain gap); per-cell variance, fill speed, drawdown (Cat 5 measures capture_mean / capture_p90 only); whether realized EV under forensic replay tracks simulated EV (the deliverable per SIMONS_MODE.md Section 6) — **closed by Cat 11 (commit 73de3a6, Phase 3 corrected forensic replay): realized EV does NOT track simulated EV at scale; Spearman ρ=0.136 across 80 candidates; by-policy structural divergence with limit policies systematically understated 2.4× by the simulator (`fire_rate` undercount due to candle-cadence threshold detection missing sub-minute bid spikes). Cat 5's simulated top-cell predictions are superseded by `replay_capture_B_net_mean` (commit 73de3a6) for the 80 evaluated candidates; Cat 5's named top cell (WTA_MAIN 40-50 tight low / time_stop "settle") remains forensic-replay-unvalidated because Phase 3 excluded settle-horizon policies (A/B scenarios collapse). See Cat 11 entry for full result.**
- **Strategic implication:** E16's original "in_match dominance" framing reflects retrospective bot-realized P&L conditioning, not per-moment per-cell EV. Forward-looking cell-selection must evaluate both channels separately because aggregate (favoring in_match) and right-tail (favoring premarket) tell different strategic stories on the same data. Per the Simons-mode discipline (SIMONS_MODE.md Section 7 rollback question 5), the strategic concentration is on top-tail verified cells, not aggregate channel routing. Forensic replay should rank cells per-channel separately and validate top-N from each against tick-level reality.
- **References:** LESSONS.md E16 (amended this commit), LESSONS.md B14 / E31 (channel preservation discipline), LESSONS.md B23 / B24 / F32 (sibling Session 9 amendments — same chain), C31 (adjacent epistemic pattern — multi-frame empirical disambiguation), SIMONS_MODE.md Section 7 (5%-vs-95% sea discipline applied at cell-selection level), SIMONS_MODE.md Section 8 (forward-reference that this commit backfills).
- **Audit disposition (2026-05-14):** PARTIALLY SUPERSEDED / PARTIALLY NEEDS RECOMPUTATION — Cat 5's simulated top-cell predictions for 80 candidates are superseded by Cat 11; its structural channel-distribution result still stands but must be recomputed under the exit-optimized objective on the foundation corpus.


#### Empirical fee table by is_taker × price bucket (Cat 2, Session 9, commit 631e653)
- **Depth:** 1 (distribution of per-fill fee_cost across kalshi_fills_history.json, partitioned by is_taker and price bucket).
- **Grain:** per-tick
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Producer:** data/scripts/diagnostics_session_8/cat_02_fee_table.py (sha256 `c11c9ba01c014ecb`, runtime 2s).
- **Data tier used:** Tier-A fact source (kalshi_fills_history.json per LESSONS A30).
- **Variables used:** is_taker (boolean), yes_price_dollars / no_price_dollars (per-fill executed price), fee_cost (per-fill fee in dollars), count_fp (executed quantity); 7,489 fills total.
- **Question answered:** What is the per-fill fee distribution for the bot's executed trades, partitioned by maker/taker leg and price bucket, suitable for fee-adjusted EV computation in Layer C v1 / forensic replay net-vs-gross split (per SIMONS_MODE.md Section 6)?
- **Strict reading:** **Taker leg:** 1,994 fills, median $0.17, mean $0.34, max $23.91, **99.9% non-zero**. **Maker leg:** 5,495 fills, median $0.00, mean $0.017, max $1.65, **37.7% non-zero**. Per-bucket parabolic shape confirmed for both legs (peak fees at 50-65¢ price bucket, where contract directional ambiguity is maximum). Taker:maker ratio at 50¢ peak: $0.21 / $0.00 (effectively infinite, well above the ≥3 spec gate per layer_c_spec.md Check 2). Four anomalous maker fills above $0.50 flagged (max $1.65 at 75¢ price); operational fee schedule is not a strict zero-cost-maker assumption.
- **Does NOT establish:** Whether the fee schedule is stable forward (Kalshi may change fee structure; this snapshot reflects Mar 1 — Apr 29 2026); whether the parabolic shape extrapolates to price buckets with low fill density (some buckets had small N); fee-adjusted EV at any specific cell (this is the empirical input, not the per-cell application — that lives in Layer C v1 producer per T32b).
- **Strategic implication:** The 37.7% non-zero maker fee rate empirically refutes a strict zero-fee-maker model. Forensic replay's gross-vs-net EV split (per SIMONS_MODE.md Section 6) must apply this fee schedule, not assume zero maker cost. Layer C v1 producer (per layer_c_spec.md Decision 1, T32b when built) consumes the same kalshi_fills_history.json → same fee table → same Decision 1 application; the producer-output `data/durable/layer_c_v1/empirical_fee_table.json` will be Cat 2's persisted form for downstream consumption.
- **Determinism note:** Cat 2 ran on Session 8 and Session 9 with byte-identical output (sha256 unchanged across runs); reproducible from kalshi_fills_history.json without nondeterminism. The Session 9 chain re-run confirmed the spec authoring was empirically grounded rather than memory-cited.
- **References:** LESSONS.md A30 (kalshi_fills_history.json as Tier-A fact source — Cat 2's data origin), ROADMAP T32 / T32a / T32b / T32c (Layer C v1 producer chain — Cat 2 is the upstream empirical anchor for T32b's persisted fee table), layer_c_spec.md Decision 1 + Check 2 (fee schedule application + ratio gate), SIMONS_MODE.md Section 5 + Section 6 (fee floor + costs framing; forensic replay net-vs-gross split). Sibling Cat 5 / Cat 6 / Cat 9 / Cat 10 entries (Session 9 diagnostic chain anchor evidence).
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Structural fee measurement by side and price bucket; an EV input, not itself scored vs settlement or exit.


#### Per-ticker OI reconstruction — candle direct read + trade-tape per-side flow (Cat 7, Session 9, commit 631e653)
- **Depth:** 1 (per-ticker OI distribution + per-side directional flow distribution across the corpus).
- **Grain:** per-minute
- **Vector:** vector-agnostic
- **Objective:** objective-agnostic
- **Producer:** data/scripts/diagnostics_session_8/cat_07_oi_reconstruction.py (sha256 `501752facfb3e700`, runtime 582s; rewritten in commit 3e752a8 patch gamma to align with F31 amendment design — original Cat 7 used pure trade-tape cumsum).
- **Data tier used:** G (g9_candles.parquet for total OI primary + g9_trades.parquet for per-side directional flow secondary + g9_metadata.parquet for ticker enumeration).
- **Variables used:** g9_candles.open_interest_fp (per-minute total OI per ticker — primary source per F31 amendment), g9_trades taker_side + count_fp (per-side flow signed cumsum — secondary), g9_metadata _tier for live/historical partition. 9.5M candle rows + 33.7M trade rows streamed.
- **Question answered:** What is the per-ticker OI distribution across the G9 corpus, and what fraction of tickers can have OI sourced from candle direct read vs requiring trade-tape reconstruction?
- **Strict reading:** **Source distribution: 8,093 tickers (40.3%) sourced from candle.open_interest_fp; 11,925 tickers (59.3%) fall back to trade-tape per-side cumsum reconstruction; 92 tickers (0.5%) no_data.** The 60% fallback rate is the historical-tier OI=0 coverage gap per F31 amendment — historical-tier markets show OI=0 throughout despite massive volume_fp, requiring trade-tape derivation. Live-tier OI distribution: median 133,329, p75 293,550, p95 699,650, max 2,949,331. Per-side directional flow: 19,997 tickers with yes-side trades, 19,902 with no-side trades. B24 anchor reproduction (Section D): 28 DZU + 48 MAN tickers in corpus; none reproduce the original Dzumhur/Mannarino screenshot anchor (2,070 / 8,594 ≈ 4.15×) — screenshot pre-dates G9 corpus cutoff per B24 amendment commit 2093539. Largest DZU OI: 788,622 (BORDZU-BOR).
- **Does NOT establish:** Per-minute OI trajectory shape (Cat 7 outputs per-ticker summary, not full per-minute parquet — that lives in T33b producer when built); causal model linking ticker properties to source-distribution membership (why historical-tier markets backfill with OI=0 is a Kalshi-side data-population question, not a Cat 7 measurement); per-cell OI breakdown (cells aggregate across tickers; Cat 7 is per-ticker, not per-cell).
- **Strategic implication:** Cat 7 is the empirical prototype of T33b (Layer C v1 OI producer) at coarser per-ticker grain. T33b produces the same source-distribution pattern (40% candle / 60% fallback / <1% no-data) at per-(ticker, ts_minute) grain when built. Cat 7 confirms the F31-amended T33 design (candle direct read + trade-tape per-side flow) is implementable and produces sensible per-tier OI ranges; the design is empirically validated rather than memory-cited.
- **Determinism note:** Cat 7's Session 9 sha256 (`501752facfb3e700`) differs from Session 8 sha256 because the producer was rewritten in patch gamma (commit 3e752a8) to align with F31 amendment — they are different producers, not the same producer producing different output. Going forward, the Session 9 design is canonical.
- **References:** LESSONS.md F31 amendment (Cat 7's design IS F31's "what is still missing and DOES require reconstruction" subsection — per-side directional flow from trade-tape signed cumsum), LESSONS.md C30 (schema-probe-depth — motivated F31 amendment which motivated Cat 7's redesign), ROADMAP T33 / T33b (Layer C v1 OI producer chain — Cat 7 is the empirical prototype; T33b will produce per-(ticker, ts_minute) at finer grain), B24 amendment + Cat 10 anchor (Section D's DZU/MAN reproduction failure aligns with B24 amendment's anchor-pre-dates-corpus-cutoff finding), SIMONS_MODE.md Section 5 (F31 amendment caveats already cited). Sibling Cat 2 / Cat 5 / Cat 6 / Cat 9 / Cat 10 entries (Session 9 diagnostic chain anchor evidence).
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Data-integrity/microstructure reconstruction of OI time series; not a performance measure.


#### Per-market formation gate distribution (Cat 8, Session 9, commit 631e653)
- **Depth:** 1 (per-market formation gate distribution + per-tier breakdown across the corpus).
- **Grain:** match-aggregate
- **Vector:** vector-A
- **Objective:** objective-agnostic
- **Producer:** data/scripts/diagnostics_session_8/cat_08_formation_gate.py (sha256 `621ee40969216f60`, runtime 68s; modified in patch alpha commit de63b0b for `category` → `_tier` column rename — Session 9 was the first valid run; no Session 8 sha256 comparison applicable).
- **Data tier used:** G (g9_metadata.parquet open_time + g9_trades.parquet first-row-per-ticker created_time).
- **Variables used:** g9_metadata.open_time (market creation timestamp per ticker), g9_trades.created_time min per ticker (first observed trade), g9_metadata._tier for live/historical partition. Derived formation_gate_minutes = (first_trade_ts − market_open_ts) / 60.
- **Question answered:** Across the G9 corpus, what is the distribution of per-market formation gate width (time from market open to first trade), and how does it stratify by tier?
- **Strict reading:** 20,018 of 20,110 markets had sufficient data. **Overall: median 164.6 min (2.74 hr), mean 311.0 min, p25 49.0 min, p75 374.8 min, p95 1,045.1 min, max 5,232 min (87 hr).** **Markets with formation gate ≤ 4hr (the bot's uniform threshold): 12,136 (60.6%) — 39.4% fall outside.** Per-tier asymmetry: historical 11,909 markets, median 211 min, p95 1,555 min, ≤4hr=53.8%; live 8,109 markets, median 121.3 min, p95 566 min, ≤4hr=70.6%. **17pp gap in 4hr-gate coverage between tiers — live markets form noticeably faster.** Bucketed distribution (8 buckets): <5min 4.4%, 5-30min 13.9%, 30-60min 10.0%, 1-2hr 13.7%, 2-4hr 18.6%, 4-8hr 21.6%, 8-24hr 14.4%, >24hr 3.4%. Zero negative gates (clock alignment validates). 673 multi-day gates (>24hr), all historical-tier (Jan / Jun 2026 markets).
- **Does NOT establish:** Whether formation-gate threshold optimality is per-tier (Cat 8 measures distribution; the optimal threshold is a strategy-design question that lives in T35's downstream work); causal model for the live-vs-historical 17pp gap (data-population dynamics, not measured here); per-cell formation gate breakdown (cells aggregate across tickers; Cat 8 is per-ticker).
- **Strategic implication:** F34 (formation gate reconstructable from g9_metadata + g9_trades) is empirically confirmed at per-ticker summary grain. The bot's uniform 4-hour gate covers 60.6% of markets but excludes 39.4% — including 21.6% in the 4-8hr bucket (markets forming just past the threshold). Per-tier adaptive gating (T35 follow-on work) is empirically motivated: live-tier markets could safely use a tighter gate (~2hr captures most), while historical-tier markets need wider tolerance. Cat 8 is the empirical prototype of T35 (formation gate per-market field producer) at per-ticker summary grain. T35 when built will produce the same data at per-(ticker, market_open_ts, first_trade_ts, formation_gate_minutes) granularity for downstream layer_c_spec.md Decision 6 / Check 5 (formation contamination measurement) consumption.
- **References:** LESSONS.md F34 (formation gate is reconstructable — Cat 8 IS the reconstruction at per-ticker grain), LESSONS.md E12 (premarket has internal phases — Cat 8 quantifies the bot's 4hr gate accuracy against the empirical distribution), ROADMAP T35 / T35a / T35b / T35c (formation gate per-market field producer chain — Cat 8 is the empirical prototype), layer_c_spec.md Decision 6 + Check 5 (formation contamination measurement, downstream consumer of T35 output), SIMONS_MODE.md Section 8 line 223 (already cites this Cat 8 finding: "30-40% of markets fall outside uniform 4hr gate"). Sibling Cat 2 / Cat 5 / Cat 6 / Cat 7 / Cat 9 / Cat 10 entries (Session 9 diagnostic chain anchor evidence).
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Characterizes formation-gate width per market; informs when vector-A can consider entering, independent of payoff objective.


#### Forensic replay realized capture (Cat 11, Session 9, commit 73de3a6)
- **Depth:** 2 (per-(cell, policy) realized capture distribution across 80 candidates, paired against Layer B v1 simulated capture distribution; Spearman ρ rank-correlation of simulated vs realized as the load-bearing scalar).
- **Grain:** per-tick
- **Vector:** vector-agnostic
- **Objective:** exit-optimized
- **Producer:** data/scripts/build_forensic_replay_v1.py (commit `a058212` — taker_side convention corrected via Session 9 empirical 5,878-pair probe; entry-fill check uses `taker_side == "no"`, exit-fill check uses `taker_side == "yes"`). Phase 3 runtime 258 min (4.3 hr) for 75,833 moments across 80 candidates. Per-candidate streaming with incremental writes (resilience to mid-loop kill); merge-from-disk at end of loop.
- **Data tier used:** G (g9_trades.parquet tick-level taker fills + g9_candles.parquet minute bid/ask + g9_metadata.parquet settlement) + B (Layer B v1 exit_policy_per_cell.parquet candidate selection) + Tier-A reference (kalshi_fills_history.json fee table integration deferred to v2; Phase 3 uses zero-fee placeholder).
- **Variables used:** Layer B v1 exit_policy_per_cell.parquet top-20 per (channel="premarket", category) ranked by capture_mean with `n_simulated >= 50` and settle-horizon time_stops excluded (4 categories × 20 = 80 candidates); per-cell sample_manifest.json tickers; g9_trades (taker_side, yes_price_dollars, created_time, ticker); g9_candles (yes_bid_close, yes_ask_close, volume_fp, end_period_ts); g9_metadata (settlement_ts, result, ticker). Per-moment 9-step replay procedure per docs/forensic_replay_v1_spec.md Section 3.1.
- **Question answered:** Does Layer B v1's idealized-fill simulator (methodology-A `capture_mean` over per-trajectory walks at minute-cadence) produce a deployment-ready ranking of (cell, policy) candidates under tick-level reality?
- **Strict reading:** No, not at the spec's PASS threshold. Spearman ρ between simulated `capture_mean` and realized `replay_capture_A_net_mean` across 80 candidates = **0.136 (p=0.23, n=80)** — not significantly different from zero, far below the spec's 0.75 PASS threshold. **76.2% of candidates have realized > simulated** (Check 4 PASS rate 23.8%, expected ≥ 90%). By-policy structural pattern: **limit policies (n=39, 49% of corpus) realize +$0.072 over simulated** (mean realized $0.124 vs mean simulated $0.052, 2.4× understatement); **time_stop (n=21) calibrated within +$0.008**; **trailing (n=10) realize −$0.005**; **limit_trailing (n=2) realize −$0.084**; **limit_time_stop (n=8) realize +$0.023**. Scenario B (fill-time exit anchor) > Scenario A (post-time anchor) in **78.8%** of candidates (mean delta $0.0158/moment) — the post-vs-fill distinction is empirically robust under both convention readings (corrupted run had B>A=66.2%; corrected run strengthens). Median cell drift at T+30 minutes = **51.7%** (Check 6 informative). Validation gate verdict: Check 1 PASS (80/80 ≥50 moments), Check 2 FAIL (75/80 in [0.05, 0.95] band — 5 WTA_CHALL deep-favorite outliers above 0.95), Check 3 PASS (A/B coherence), Check 4 FAIL (23.8%), Check 5 FAIL (ρ=0.136). **Deployable cohort criterion (fill_rate ≥ 0.40 AND cell_drift_at_fill ≤ 0.50): 40 of 80 candidates qualify.** Top deployable by Scenario B: **ATP_MAIN 50-60 tight low / limit_c=30 (B=$0.261, fill=0.76, drift=0.09, win=94%, n=2,914 moments)** — most production-ready cell in the evaluated set. Rank-1 by Scenario B overall: WTA_MAIN 60-70 tight high / limit_c=30 (B=$0.310, fill=0.31, drift=0.79, win=100%, n=427).
- **Mechanism (load-bearing — names the structural defect in Layer B v1's idealized-fill simulator):** **Candle-cadence fire_rate undercount.** Layer B's `walk_trajectory` detects threshold crosses by checking `yes_bid_close` at minute boundaries; tick-level reality has trades happening at sub-minute granularity. Between consecutive candle minutes, the bid can spike to (or above) the threshold and back down within ≪60 seconds, hitting a hypothetical resting sell at the spike, with no trace in the minute-close candle. Layer B undercounts those fires. The undercount scales with threshold distance from settlement: limit_c=30 cells bounce more sub-minutely than limit_c=10 cells (where settlement-zone proximity collapses the gap). Within the simulator, `capture_mean ≈ fire_rate × capture_per_fired`; the `capture_per_fired` term is correct (limit policies fire at exactly +limit_c with zero overshoot under the corrected convention), but the `fire_rate` term is the empirically-broken component. This explains the by-policy heterogeneity: limit policies (which depend on threshold-cross detection) systematically undercount; time_stop / horizon-based policies (which fire by clock, not by price-cross) calibrate cleanly; trailing-stop policies (which depend on running-max MFE detection) under-realize because the simulator's idealized trailing assumes the running max persists between candles, but tick reality has the trail bouncing.
- **Does NOT establish:** Whether settle-horizon time_stop policies share the same bias — Phase 3 excluded them per spec (A/B scenarios collapse for `horizon_min == "settle"`); Cat 5's predicted top cell (WTA_MAIN 40-50 / tight / low / time_stop "settle", $0.509 simulated) remains forensic-replay-unvalidated and is the highest-impact open gap. Whether the candle-cadence undercount mechanism generalizes beyond the 80 evaluated cells — the corpus has 12,455 non-settle premarket cells; the evaluated 80 are top-20-per-category by simulated capture_mean (biased toward high-EV cells; the gap could be larger or smaller in low-EV cells). In-match channel behavior — Phase 3 is premarket-only; spec Section 1 defers in_match to v2 with explicit gap-risk haircut measurement. Whether Scenario B's superiority survives alternative exit-policy reformulations (only the post-time-vs-fill-time anchor distinction was tested; richer policy reformulations like dynamic-threshold-based-on-current-spread were not). Fee impact on realized capture — Phase 3 used zero-fee placeholder per producer Phase 1/2/3 scope; Cat 2's fee table integration was deferred to v2 of the producer.
- **Strategic implication:** Layer B v1's `capture_mean` is not a deployment-ready cell-ranking source for limit-policy cells. Forensic replay v1's `replay_capture_B_net_mean` (commit `73de3a6`, `data/durable/forensic_replay_v1/phase3/candidate_summary.parquet`) is the canonical cell-ranking truth for the 80 evaluated candidates until a Layer B v2 producer with empirical fill probability lands. **The path-forward priority shifts:** Layer B v2 (tick-level fill semantics, folding forensic replay's mechanism back into the simulator) becomes the higher-leverage deliverable than ROADMAP T32's previously-planned Layer C v1 (fees on top of idealized fills) — fees are a 1-2¢ correction; the candle-cadence undercount is a 7¢+ correction on the dominant policy class (limit, 49% of corpus). Production execution should use Scenario B's fill-time-anchored exit policy (re-evaluate at fill, not commit at posting) — empirically B > A in 78.8% of candidates with mean delta $0.0158/moment. The deployable-cohort top 10 (operational-clean subset) are tight-spread / favorite-side / low-volume / limit-policy cells with limit_c ≥ 15 — specifically WTA_MAIN/ATP_MAIN tight-low cells in 40-70¢ entry bands and ATP_CHALL 80-90 tight-low limit_time_stops with horizon 60-120 min.
- **References:** Outputs commit `73de3a6` (`data/durable/forensic_replay_v1/phase3/{run_summary.json, candidate_summary.parquet, scenario_comparison.parquet, cell_drift_per_minute.parquet}` + on-disk-only intermediates per `data/durable/forensic_replay_v1/NOTE.md`); producer commit `a058212` (taker_side convention fix on both legs); spec commit `40db959` (initial) + `3b62039` (column-name + NaN invariant) + `a058212` (convention invariant); empirical convention probe (5,878 trade-candle pairs across 5 tickers — 3 ATP_CHALL + 2 WTA_MAIN — `taker_side="yes"` clusters AT_ASK 56% vs AT_BID 24%; `taker_side="no"` clusters AT_BID 49% vs AT_ASK 26%); OSO/KAL forensic single-moment evidence (`KXWTAMATCH-25SEP26OSOKAL-OSO`, fill at $0.61, target $0.91; producer matched `taker_side="no"` at $0.99 settlement-bid-clearing event when real fill was `taker_side="yes"` at $0.91 22 seconds earlier — diagnostic that surfaced the convention bug). Archived corrupted Phase 3 (`db1d249` era, on-disk at `data/durable/forensic_replay_v1/phase3_pre_convention_fix/`, not committed; preserved for audit comparison). **Forward-reference closures (this commit):** Cat 5 ("whether realized EV under forensic replay tracks simulated EV — the deliverable per SIMONS_MODE Section 6") — Cat 11 IS that deliverable; Cat 5's "Does NOT establish" sentence amended in this commit to point forward to Cat 11. **Forward-references opened (this commit):** forensic replay v2 settle-horizon variant for Cat 5's predicted top cell (WTA_MAIN 40-50 tight low / time_stop "settle"); Layer B v2 spec authoring (tick-level fill semantics, the next strategic deliverable post-Cat-11). LESSONS.md C30 (schema-probe-depth — sibling pattern: empirical convention probe surfaced bug that survived schema-name correction); LESSONS.md C31 (mechanism-coherent ≠ empirically correct — convention bug ran cleanly through Phase 1/2/3 corrupted before forensic OSO/KAL probe surfaced it); LESSONS.md D11 (probe-before-assume — applied successfully here). Sibling Cat 2 / Cat 5 / Cat 6 / Cat 7 / Cat 8 / Cat 9 / Cat 10 entries (Session 9 diagnostic chain anchor evidence; Cat 11 is the post-diagnostic-chain forensic replay deliverable).
- **Audit disposition (2026-05-14):** CARRIES FORWARD — Canonical exit-optimized realized-capture benchmark from tick-level replay; already measures the right objective and grain, anchors how cell-level policies should be evaluated.

#### Spike volatility map atlas — four-category corpus +$6,158.20 hindsight-optimal P&L (T42, HEAD d99c6e9)

- **Depth:** 1 (corpus-scale descriptive aggregation).
- **Grain:** per-cell (with three resolutions: 1c / 2c / 3c reported side-by-side).
- **Vector:** vector-agnostic
- **Objective:** exit-optimized (per-cell hindsight-optimal exit-or-hold from T-20m taker anchors).
- **Producer:** data/scripts/build_spike_perN.py at commit `c5e377f` (canonical reproducible), atlas commits 481de7f → d99c6e9.
- **Data tier used:** FOUNDATION-TIER (per_minute_features) + G (g9_trades) + n_profile_v1 cohort.
- **Variables used:** T-20m anchor price, spike-to-+X-with-≥250ct walk over [t20m, settlement_ts], settlement_value, derived per-cell argmax exit target.
- **Strict reading:** Across 14,033 N's (ATP_MAIN 4,137 / WTA_MAIN 3,683 / ATP_CHALL 5,326 / WTA_CHALL 887) over a 10-month corpus, per-cell hindsight-optimal exit-or-hold rules at 1c resolution would have paid +$6,158.20 on $70,813.20 capital deployed at 10ct sizing — blended +8.70% per-trade ROI. Per-category: ATP_MAIN +$1,658.80/+7.90% (252 days), WTA_MAIN +$1,824.90/+9.84% (248 days), ATP_CHALL +$2,029.20/+7.57% (109 days), WTA_CHALL +$645.30/+14.52% (80 days). Cheap regime (anchor 5-30¢) generates 30-40% of dollar profit on ~8-9% of capital across all four categories. Highest-ROI single cell across corpus: ATP_MAIN anchor=9¢, hold-to-settlement, +242% ROI on $20.70 capital (N=23). Pairing rate (event-level): 79.3% of events have both N's anchored (6,208 of 7,825); 88.5% of N's in paired events.
- **Does NOT establish:** Realized P&L net of fills (B25 fill-realism axis pushes DOWN 0.4-0.8×; Layer C work pending). Realized P&L net of entry-side execution (Axis 2 maker improvement pushes UP +10-30%; net direction unmeasured). Predictive rule shape (atlas measures hindsight-optimal per cell; per-cell argmax does NOT generalize forward per OOS work this session — deployable rule shape is an open question pending paper-mode validation). Daily realization on non-max-overlap days (the ~$40/day picture assumes all four categories active concurrently; tour calendars don't always align). Bilateral capture economics (atlas is single-leg; B23 bilateral mechanism not yet layered in).
- **Strategic implication:** The strategy's opportunity floor on the corrected foundation. Three axes between this and realized PnL (AXIS 1 fill realism DOWN, AXIS 2 entry-side maker improvement UP, AXIS 3 arrival frequency separate). Headline stays conservative; operational hand reads ~+25-50% better than headline once execution work measures fills per cell. Deployment philosophy: trade all 90 cells per category, do not cherry-pick to high-ROI cells — volume is the operational constraint; execution work resolves marginal cells; cell selection does not. Capital position not the binding constraint (operator-stated); binding constraints are (a) execution mechanics and (b) market depth (F33).
- **References:** LESSONS.md A39 (cent-vs-ROI geometry empirically confirmed), B16 (Layer A descriptive deliverable separation), B25 (minute-cadence simulator undercount that motivates Axis 1 conservative framing), B23 (bilateral mechanism — pairing diagnostic measures 79.3% upstream feasibility), E32 (locked cell/exit model the atlas operationalizes), G22 (three-axis deployment math never collapsed). SESSION_HANDOFF.md "Atlas headline" + "Three-axis caveat" + "Structural patterns observed in the atlas" sections. Four LOCKED_DOWN.md files in data/durable/spike_volatility_map/. PAIRING_DIAGNOSTIC.md in the same directory.
- **Audit disposition (2026-05-20):** CANONICAL HEADLINE — the strategy-phase deliverable. The execution-lock arc validates against this. Treat as opportunity floor, never as deployable dollars or pure upper bound.

## SECTION 5: CHANGELOG

- 2026-04-30 ~13:21 ET: Initial scaffolding (commit c794b26). Section 4 had one entry (70.7%); Sections 2 and 3 placeholder.
- 2026-04-30 ~14:30 ET (this commit): Sections 2, 3, 4 fully populated from depth-inventory CC probe. Catalog covers ~40 distinct analyses across 6 depth levels plus broken/meta categories.
- 2026-04-30 (item 5 closure): Corrected mischaracterization of /root/Omi-Workspace/tmp/ — it is a curated git-tracked archive with multiple curation batches, not a single Apr 29 snapshot. Canonical-source rules updated.
- 2026-05-04 (Session 6 T28): G9 parquets (g9_candles, g9_trades, g9_metadata) added as canonical foundation per LESSONS C27. T17 producer commit bd83412, T27 verification 9/9 PASS. sha256 in MANIFEST.md.
- 2026-05-04 (Session 6 T29): Layer A v1 outputs (cell_stats.parquet, sample_manifest.json, build_layer_a_v1.log, 15 visual PNGs) added under new subsection in Section 2. Foundation pointer T28 commit ea84e74. Producer commit 1398c39. MANIFEST commit 37a5216. Validity: PASSED T21 coherence read 2026-05-04 (4 PASS / 2 INCONCLUSIVE / 0 FAIL).
- 2026-05-04 (Session 6 Phase 5-ii / T21 closure): cell_stats.parquet Notes field updated with T21 verification findings (YES-only producer, bounce-def explanation, Vitter reservoir confirmed unbiased, volume_intensity in_match collapse, no event_ticker preserved). Validity status flipped from PENDING T21 to PASSED T21 2026-05-04 across cell_stats.parquet narrative + Notes line, sample_manifest.json, and visual PNG block. Cross-references to LESSONS A36, B19, B20, F30 and ROADMAP F13, G12, T31.
- 2026-05-05 ET (Session 8 / T32a-followup): Layer C v1 specification entry registered. Foundation pointers T28 ea84e74 + T29 1398c39 + T31b 28e8ab7. Spec at docs/layer_c_spec.md (commit 4bed07f, 189 lines, 9 sections, 6 numbered Decisions, 5 validation checks). Validity status SPEC (not output-bearing — T32b producer and T32c coherence read add output artifacts in subsequent commits). Closes T32a per its own definition (spec lands and is referenced in ANALYSIS_LIBRARY).
- 2026-05-14 ET: Structural readiness pass. Entry format extended with the GRAIN / VECTOR / OBJECTIVE triple (TAXONOMY Section 2.5). FOUNDATION-REBUILD NOTICE added to header. G9-parquets and Layer-A-v1 'canonical foundation' subsection headers flagged as superseded (canonical foundation is now FOUNDATION-TIER per_minute_features.parquet). NO entry content reclassified — that is the unit-of-analysis audit, which runs separately against this now-structurally-ready catalog.
- 2026-05-14 ET: Unit-of-analysis audit applied. All 65 entries (Sections 2/3/4) classified inline with GRAIN/VECTOR/OBJECTIVE + disposition per TAXONOMY Section 2.5. Section 6 added with the disposition summary. Source: data/analysis/unit_of_analysis_audit.json (commit 2547f6a).
- 2026-05-18 ET (n_profile_v1 FOUNDATION landed): n_profile_v1 registered in Section 2 as the canonical FOUNDATION-TIER per-N measurement universe. Phase-3 full-corpus run COMPLETE 2026-05-18 02:37 ET (~5h41m, detached on producer a28840e). Artifact: n_profile.parquet, sha256 a7ed1155, 19,614 x 45, 0 dropouts. All 7 gates PASS at full corpus. OOM remediation (Pass-1 del + gc-every-200, a28840e) validated at full-corpus heavy-tail scale — the defect class that killed two prior Phase-3 attempts (whole-PMF residency 51b1cd6, then per-ticker allocator accumulation a28840e). Foundation pointer per_minute_features 9fde4b5d (T37 ckpt-3). Lessons this arc: F35, G23, C38. MANIFEST.md on-disk sha256 append PENDING (App action; sha256 preserved in meta.json sidecar). Cleared for downstream consumption (Rung 0/1/2, band-free in-match bounce analysis).

---

## SECTION 6: UNIT-OF-ANALYSIS AUDIT (2026-05-14)

Every entry in Sections 2, 3, and 4 has been classified against the GRAIN / VECTOR / OBJECTIVE axes (TAXONOMY Section 2.5) and assigned a disposition keyed to the locked cell/exit model (LESSONS E32). The per-entry classification is recorded inline in each entry's bullet block (Grain / Vector / Objective / Audit disposition). The full structured audit is at data/analysis/unit_of_analysis_audit.json (commit 2547f6a).

Disposition summary across 65 entries:
- CARRIES FORWARD (26): usable as-is under the locked model — mostly structural-property findings (trajectory width, OI distribution, formation gates, fee tables, channel routing splits) and the one exit-optimized anchor (Cat 11 forensic replay).
- NEEDS RECOMPUTATION (21): settlement-scored analyses that measured the wrong objective; must be re-scored as exit-optimized average bounce per cell band on the FOUNDATION-TIER corpus. Includes the 70.7% anchor, the legacy live-bot P&L slices, and the full legacy per-cell economics cluster.
- BROKEN (10): structurally invalid under the new model (Greeks first-bid bug, fragmented bias cluster, matches.entry_time dependencies, pre-Bug-3-fix entry_price contamination, settlement-event-omission P&L).
- SUPERSEDED (7): pre-rebuild canonical artifacts retained only as regression cross-checks (G9 parquets, Layer A v1 outputs).
- PARTIALLY SUPERSEDED / PARTIALLY NEEDS RECOMPUTATION (1): Cat 5 — the 80-candidate simulation is superseded by Cat 11, but the structural channel-distribution result still stands and needs exit-optimized recomputation.
