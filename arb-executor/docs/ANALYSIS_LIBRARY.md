# OMI Analysis Library — Catalog of Prior Analyses

**Purpose:** Catalog every prior analysis script and result file in the OMI tennis trading operation, classified by analysis depth, data tier, variables used, question answered, validity status, and output location. Source of truth for "what has already been done." Future chats consult this before designing any new analysis to avoid redoing work and to know which prior conclusions are valid vs invalidated.

**Cross-references:**
- Taxonomy used for classification: TAXONOMY.md.
- Lessons that motivate this library: A23 (sources pulled from but not fully extracted), A28 (D1/D2 fragmentation), C14 (canonical output paths), E25 (70.7% as depth-0), E26 (depth and variable inventory parallel axes), E27 (D5 methodology drift), F19 (bias reconciliation fragmented).

**Last populated:** 2026-04-30 ~14:30 ET, mid-Session 4, from depth-inventory probe results.

---

## SECTION 1: ENTRY FORMAT

Each analysis is one entry with the following fields:[Analysis name]

File path: [VPS path]
Producer script: [VPS path of code]
Date created: [date or git commit date]
Depth: [0-6 per TAXONOMY.md Section 2]
Data tier used: [A / B / C / mixed / N/A]
Variables used: [columns from TAXONOMY Section 4]
Question answered: [one sentence]
Validity status: [valid / partial / broken / unverified / superseded]
Notes: [known issues, dependencies, supersession info]


Canonical-path rules (post-Session-6 Phase 1B/1C). For preserved DATA files: arb-executor/data/durable/ is canonical (sha256-verified per MANIFEST.md, not in git due to size, but durable on disk). For preserved SCRIPTS: tmp/ is canonical (git-tracked, multiple curation batches Mar 13 - Apr 29 plus Session 6 Phase 1A/1C additions). /tmp/ is now the producer WORKING DIRECTORY for live operations (e.g., kalshi_fills_history.json gets re-pulled to /tmp by fills_history_pull.py, then copied to durable/ to update canonical). For files in multiple locations: durable/ wins for data, tmp/ wins for scripts; /tmp serves as producer working file only. F1 PARTIAL CLOSURE in ROADMAP tracks the broader durability migration across this corpus.

---

## SECTION 2: ANALYSES BY DEPTH

### Depth 0 — Existence

#### April 14 paired analysis (the 70.7% double-cash rate)
- **File path:** Reconstructed from chat memory; original output not located in /tmp inventory.
- **Producer script:** Unknown; possibly /tmp/per_cell_verification or ad-hoc one-off.
- **Date created:** ~April 14 2026.
- **Depth:** 0 (existence proof).
- **Data tier used:** C (historical_events).
- **Variables used:** first_price_winner, max_price_winner, first_price_loser, max_price_loser.
- **Question answered:** Did both sides of paired matches ever reach +10c above first observed price.
- **Validity status:** Partial — see E25. Valid as existence proof; invalid as edge validation. Not reproduced on current data.
- **Notes:** Cited as "70.7% across 458 paired matches" in LESSONS.md E18. First pressure test in queue (ROADMAP Section 4).

#### Heartbeat / operational health checks
- **File paths:** /tmp/heartbeat_*.json (live_v3, kalshi_price, fv_monitor, betexplorer, tennis_odds).
- **Depth:** 0 (operational, not strategy).
- **Notes:** Real-time health checks, not analysis. Excluded from strategic catalog but flagged here for completeness.

---

### Depth 1 — Distribution

#### exit_sweep_grid
- **File path:** /tmp/exit_sweep_grid.csv (85.7 KB).
- **Producer:** /tmp/exit_sweep.py.
- **Depth:** 1.
- **Data tier used:** mixed (matches table + BBO).
- **Variables used:** Per-cell ROI and hit_rate at every exit_c from 1c to 49c.
- **Question answered:** What is the optimal exit_c per cell, and how does ROI change across exit_c?
- **Validity status:** Unverified — uses fixed exit baseline; classifier threshold not surfaced.
- **Notes:** Underdog only (leaders absent). N at least 30 per cell.

#### exit_sweep_curves
- **File path:** /tmp/exit_sweep_curves.csv (15.8 KB).
- **Producer:** /tmp/exit_sweep.py.
- **Depth:** 1.
- **Notes:** Wider variant of exit_sweep_grid including band_width and N. Same producer.

#### optimal_exits
- **File path:** /tmp/optimal_exits.csv (9.8 KB).
- **Producer:** /tmp/exit_sweep.py.
- **Depth:** 1.
- **Variables used:** Per-cell optimal_exit, optimal_ROI, hit_at_opt with 15c baseline comparison.
- **Validity status:** Partial — same caveats as exit_sweep_grid.

#### baseline_econ
- **File path:** /tmp/baseline_econ.csv (2.5 KB).
- **Depth:** 1.
- **Variables used:** Per-cell status (ACTIVE/disabled), exit_cents, N, avg_entry, scalp_WR_pct, ROI_pct, daily_dollar, confidence.
- **Validity status:** Partial — pre-V3 baseline, predates Mona Lisa retune.

#### bootstrap_ci_results
- **File path:** /tmp/bootstrap_ci_results.csv (1.3 KB).
- **Producer:** /tmp/bootstrap_ci.py and /tmp/bootstrap_negative.py.
- **Depth:** 1.
- **Variables used:** Per-cell bootstrap mean/std/CI vs analytical CI; ci_match flag.
- **Validity status:** Valid for the cells included (subset of total cells).
- **Notes:** Per B4, validates that analytical CIs align with bootstrap on existing data.

#### rebuilt_scorecard
- **File path:** /tmp/rebuilt_scorecard.csv (8.5 KB).
- **Producer:** /tmp/rebuilt_scorecard_script.py.
- **Depth:** 1 (with classification on top).
- **Variables used:** TWP, Sw, Sl, decomposed_ROI per 67-cell scorecard.
- **Validity status:** Partial — methodology issues per LESSONS (uses fixed 15c exit, classifier threshold not surfaced, bias correction undersized vs operator memory).
- **Notes:** 67-cell SCALPER_EDGE / SCALPER_BREAK_EVEN / SCALPER_NEGATIVE / MIXED_BREAK_EVEN / SETTLEMENT_RIDE_CONTAMINATED / UNCALIBRATED classification.

#### post_retune_economics
- **File path:** /tmp/per_cell_verification/post_retune_economics.csv.
- **Depth:** 1.
- **Variables used:** Per-cell N / avg_fill_price / realized_pnl / CI for the post-retune window.
- **Validity status:** Unverified — must re-derive entry timing per F17.

#### pnl_by_cell_config
- **File path:** /tmp/per_cell_verification/pnl_by_cell_config.csv.
- **Depth:** 1.
- **Variables used:** Per-cell per-config-hash N_fills, avg_pnl_pct, total_pnl_dollars.
- **Validity status:** Unverified.
- **Notes:** Distinct config hashes visible — implements F2 (config drift contamination tracking).

#### per_cell_real_economics
- **File path:** /tmp/per_cell_verification/per_cell_real_economics.csv.
- **Depth:** 1.
- **Variables used:** Per-cell scalps / settle_wins / settle_losses / scalp_WR_pct / total_pnl_dollars / daily_fills.
- **Validity status:** Partial — settlement detection broken per F8 (Bug 4).

#### comparison_real_vs_analysis
- **File path:** /tmp/per_cell_verification/comparison_real_vs_analysis.csv.
- **Depth:** 1.
- **Variables used:** Per-cell delta between realized P&L and analysis-predicted P&L; assessment column flags REAL_WORSE / REAL_BETTER / TOO_FEW_FILLS.
- **Validity status:** Valid for diagnostic purposes; the deltas themselves carry F8 caveat.

#### u4_phase1_match_landscape (U4 Phase 1)
- **File path:** tmp/u4_phase1_match_landscape.csv (1.04 MB, 5,879 matches; durable per Phase 1C-iv Session 6, commit f36691c).
- **Producer script:** tmp/u4_phase1_match_landscape.py (durable per Phase 1C-i Session 6, commit d0462c8).
- **Date created:** 2026-04-30 (Session 4).
- **Depth:** 1.
- **Data tier used:** C (historical_events) + attempted joins to book_prices and kalshi_price_snapshots.
- **Variables used:** first_price_winner, min_price_winner, max_price_winner, last_price_winner, first_price_loser, min_price_loser, max_price_loser, last_price_loser, total_trades, category, commence_time, duration.
- **Question answered:** What does the match landscape look like across all relevant variables, with no pre-defined cell scheme?
- **Validity status:** Valid for population-level characterization; Pinnacle FV join FAILED (book_prices Apr 19+ vs historical_events Jan 2 - Apr 10 = zero date overlap) and volume_24h join FAILED (kalshi_price_snapshots Apr 21+ only).
- **Notes:** Foundation for U4 Phase 2 stratification. Confirms bounce asymmetry at population level: winner median ~35c, loser median ~12-16c. 33% of matches have first_price_winner + first_price_loser >5c off 100 (per A19 — first_price unsynchronized between sides). F28 /tmp ephemerality MITIGATED for this entry per Phase 1C Session 6 — both producer and output durable in tmp/. **CAVEAT per B14:** uses match-level aggregates conflating premarket vs in-match windows.

#### u4_phase2_loser_bounce_predictors (U4 Phase 2)
- **File path:** tmp/u4_phase2_loser_bounce_by_strata.csv (8.1 KB, 92 strata) + tmp/u4_phase2_loser_bounce_summary.txt (2.9 KB; both durable per Phase 1C-iv Session 6, commit f36691c).
- **Producer script:** tmp/u4_phase2_loser_bounce_predictors.py (durable per Phase 1C-i Session 6, commit d0462c8).
- **Date created:** 2026-04-30 (Session 4).
- **Depth:** 1 (distribution stratified).
- **Data tier used:** C (synchronized subset of historical_events: 3,936 matches where first_price_winner + first_price_loser within 5c of 100).
- **Variables used:** total_trades, category, duration, skew (first_price_winner - 50), first_price_loser, leg span, plus loser-side bounce magnitudes.
- **Question answered:** Which match-level variables predict loser-side bounce capture, and at what magnitudes?
- **Validity status:** Valid as stratified distribution finding on synchronized subset. Strategically useful: volume is canonical predictor.
- **Notes:** Key finding — **volume is primary predictor of bilateral capture** (33pp swing across volume strata: 50-99 trades = 34.3% bilateral capture at +10c, 1000+ trades = 76.4%). Categories track within 6pp (ATP_CHALL=63.1%, ATP_MAIN=63.5%, WTA_MAIN=64.3%, WTA_CHALL=56.8%). Skew >35 cliff partially CEILING ARTIFACT per B13 (heavy side at 85-89c can't bounce 15c without exceeding 99c). Aggregate +10c bilateral on synchronized subset: 62.83%. Duration 2-4h matches strongest (68.3%). **Reframes the 70.7% April 14 anchor per E30 — that figure was subset-averaged; high-volume regime is 76.4% and low-volume is much lower.** Operator-validated strategic conclusion: high-volume matches (1000+ trades) are bilateral candidates; low-volume are single-side or skip. **CAVEAT per B14/G17:** uses match-level aggregates conflating premarket vs in-match. Decomposition required for strategy-actionable findings (U4 Phase 3, next analysis target). F28 /tmp ephemerality MITIGATED for this entry per Phase 1C Session 6 — producer and outputs durable in tmp/.

---

### Depth 2 — Trajectory

#### entry_price_bias (canonical run)
- **File path:** /tmp/per_cell_verification/entry_price_bias.csv (320 KB).
- **Depth:** 2.
- **Data tier used:** B + matches.
- **Variables used:** Per-ticker first_mid / first_bid vs T-15m / T-1h / T-2h / T-4h mid and bid.
- **Question answered:** What is the bias between bot fill price and pre-match BBO at various windows?
- **Validity status:** Unverified canonical — F19 fragmentation; multiple bias files exist measuring overlapping concepts.
- **Notes:** Bias-correction primary source per Mona Lisa work. The "operator memory says +21-37c, file shows max 10.6c" mystery in known unknowns originates here.

#### entry_price_bias_by_cell
- **File path:** /tmp/per_cell_verification/entry_price_bias_by_cell.csv (2.6 KB).
- **Depth:** 2.
- **Variables used:** Per-cell aggregate (mean / median / stddev / pct_within_3c / pct_within_5c).
- **Validity status:** Same as entry_price_bias.

#### entry_price_bias.run1
- **File path:** /tmp/per_cell_verification/entry_price_bias.run1.csv + entry_price_bias_by_cell.run1.csv.
- **Depth:** 2.
- **Validity status:** Earlier run, identical schema. Per F19, exact relation to canonical run undocumented.
- **Notes:** Source of fragmentation per F19.

#### bias_by_cell_from_matches
- **File path:** /tmp/per_cell_verification/bias_by_cell_from_matches.csv.
- **Depth:** 2.
- **Data tier used:** matches table.
- **Variables used:** Per-cell bias from matches table (bot_entry_price vs first_price_historical).
- **Validity status:** Partial — uses matches.entry_time which is NULL on live rows per F17.

#### linkage_sanity_check
- **File path:** /tmp/per_cell_verification/linkage_sanity_check.csv.
- **Depth:** 2.
- **Variables used:** Per-fill linkage diagnostic comparing cell_by_first_price vs cell_by_bot_entry; flags cell_mismatch.
- **Validity status:** Valid — implements A11 (cell mismatches at boundaries contaminate per-cell numbers).

#### swing_script
- **File path:** /tmp/swing_script.py (script only; outputs not located).
- **Depth:** 2.
- **Variables used:** first_mid, pre-commence_max_mid, post-commence_max_mid per ticker.
- **Question answered:** Channel 1 vs Channel 2 trajectory primitive — separate the pregame max from the in-match max per ticker.
- **Validity status:** Unverified; not located as committed output.

#### channel_decomp (current session)
- **File path:** /tmp/channel_decomp.py.
- **Depth:** 2.
- **Variables used:** JSONL log entry_filled and exit_filled events; ts_et fields.
- **Question answered:** What fraction of bot fills exit via Channel 1 (pregame) vs Channel 2 (in-game)?
- **Validity status:** Valid — produced the 4.7% / 95.3% split that anchors LESSONS Section 2.
- **Notes:** Reads from JSONL logs which are tz-clean per F16.

#### replay_inplay
- **File path:** /tmp/replay_inplay.py.
- **Depth:** 2.
- **Notes:** Replay of in-play trajectory. Output not located.

---

### Depth 3 — Capacity

#### fill_asymmetry_per_fill
- **File path:** /tmp/per_cell_verification/fill_asymmetry_per_fill.csv (17.8 KB).
- **Producer:** /tmp/fill_asymmetry.py.
- **Depth:** 3 (top-of-book only — does NOT use 5-deep depth).
- **Data tier used:** A or B (top-of-book).
- **Variables used:** Per-fill bid_at_fill / ask_at_fill / spread_at_fill, mid 30 min before, oscillation_range, n_window_snaps, paired flag.
- **Validity status:** Partial — implements only level-1 capacity; A22 unfulfilled at Depth 3 because 5-deep depth columns from premarket_ticks remain unused.

#### fill_asymmetry_summary
- **File path:** /tmp/per_cell_verification/fill_asymmetry_summary.csv.
- **Depth:** 3 (level-1 only).
- **Variables used:** Leader vs underdog aggregate (% trending up / down / oscillating / flat, paired_pct).

**Depth 3 capacity-with-full-depth: NONE EXIST.** No prior analysis uses bid_2 through bid_5 with sizes from premarket_ticks. A22 + A26 unfulfilled at Depth 3.

---

### Depth 4 — Microstructure

#### Greeks decomposition (BROKEN per F11)
- **File path:** /tmp/per_cell_verification/greeks_decomposition.csv.
- **Producer:** /tmp/greeks_decomposition.py and /tmp/greeks_check.py.
- **Depth:** 4.
- **Variables used:** Per-cell theta_pregame, theta_early_match, gamma_excursion, realized_vega, scalp-phase distribution.
- **Validity status:** **BROKEN.** Degenerate first-bid bug per F11. Schema is correct; numbers are not trusted.
- **Notes:** Listed in Section 3.

#### greeks_per_match
- **File path:** /tmp/per_cell_verification/greeks_per_match.csv.
- **Depth:** 4.
- **Validity status:** **BROKEN.** Same degenerate first-bid bug. Per-ticker version of decomposition.

**Depth 4 microstructure-beyond-Greeks: NONE EXIST.** No volume-profile, VWAP, autocorrelation, market impact, or order-flow microstructure analyses exist despite trade CSVs having taker_side per A26.

---

### Depth 5 — Strategy simulation

#### fill_outcomes
- **File path:** /tmp/fill_outcomes.csv (23.7 KB).
- **Producer:** /tmp/fill_outcomes_analysis.py.
- **Depth:** 5.
- **Variables used:** Per-fill cell, direction, play_type, entry_price, qty, terminal_event (exit_filled / settled), exit_price, pnl_cents_total, ROI%.
- **Validity status:** Partial — uses fill records that may be subject to F8 (settlement detection broken).

#### dca_event_test / dca_event_analysis
- **File paths:** /tmp/dca_event_test.py / /tmp/dca_event_analysis.py (26.4 KB each).
- **Output:** /tmp/validation5/dca_event_matched.csv (23.7 KB).
- **Depth:** 5.
- **Variables used:** Per-cell DCA fire_rate_pct, win_rate_pct, dca_ev_per_fire_c, cell_roi_delta_pct across multiple trigger thresholds and combo variants.
- **Validity status:** Unverified.

#### dca_bbo_v3 + variants
- **File paths:** /tmp/dca_bbo_v3.py + variants, /tmp/dca_bbo_v3_test.py, /tmp/dca_bbo_v3_test5m.py.
- **Promoted version:** /root/Omi-Workspace/arb-executor/dca_bbo_timeorder.py.
- **Depth:** 5.
- **Validity status:** Promoted version addresses A3 (time-order enforcement). Earlier variants superseded.

#### scalp_constrained_optimize
- **File path:** /tmp/scalp_constrained_optimize.py.
- **Depth:** 5.
- **Implements:** A9 (exit target must be scalp-achievable: entry + exit_cents at most 95c).

#### Multiple "ultimate cell economics" implementations (E27 — methodology drift)
- /tmp/validate_and_optimize.py
- /tmp/corrected_cell_economics.py
- /tmp/ultimate_cell_economics.py
- /tmp/ultimate_cell_economics_csv.py
- **Depth:** 5.
- **Validity status:** Unknown which is canonical. Per E27, this is methodology drift, not iteration. Before re-running strategy simulation, must designate canonical or retire others.

---

### Depth 6 — Cross-sectional context

#### fv_convergence_monitor (live operational, not closed analysis)
- **File path:** /tmp/fv_convergence_monitor.csv (14.2 MB, actively growing).
- **Depth:** 6.
- **Variables used:** Live FV vs Kalshi convergence with per-side gap_cents, gap_pct, time_to_start_hrs, fv_source, fv_tier.
- **Validity status:** Valid as live operational dashboard; not closed retrospective analysis.

#### bias_from_bbo / bias_check / bias_check2
- **File paths:** /tmp/bias_from_bbo.py / /tmp/bias_check.py / /tmp/bias_check2.py.
- **Depth:** 6.
- **Notes:** Sharp-bias measurement vs BBO. Multiple iterations; canonical not designated. Part of F19 fragmentation.

#### rebuild_vs_paper_diff
- **File path:** /root/Omi-Workspace/arb-executor/docs/rebuild_vs_paper_diff.md (41.3 KB).
- **Producer:** /tmp/rebuild_diff_analysis.py (34.5 KB).
- **Depth:** 6 (config-vs-config narrative comparison).
- **Validity status:** Valid — narrative documentation of strategy variants.

**Depth 6 systematic external-data analysis: NONE EXIST.** No closed-form analyses of edge by tournament tier, by surface, by ranking, by day of week, or by Kalshi-vs-DraftKings lag. All depth-6 work to date is operational (fv_monitor) or narrative (rebuild_diff).

---

### Variable-isolation / retune forensics (cross-cutting)

These analyses isolate the impact of specific changes (cell additions, retunes, code changes). They do not fit cleanly into the depth taxonomy because they are diagnostic rather than measuring price/execution properties.

#### variable_isolation
- **File path:** /tmp/per_cell_verification/variable_isolation.csv.
- **Implements:** E7 / E8 (isolate variable impact across the Apr 24 retune).
- **Notes:** Bleed period vs recovery period. active_cell_count went 39 to 25, with itemized cells_added and cells_removed lists.

#### cell_groupings
- **File path:** /tmp/per_cell_verification/cell_groupings.csv.
- **Implements:** A12 (sub-cell statistical power vs wider groupings).
- **Notes:** Grouping vs subcell ROI; flags GROUP_BETTER vs SUBCELL_BETTER.

#### bleed_decomposition
- **File path:** /tmp/per_cell_verification/bleed_decomposition.csv.
- **Notes:** Per-cell bleed contribution to -$228.80 with status_change (KEPT / ADDED_LATER / REMOVED) and pre/post-exit_cents columns.

#### exit_sweep_leader_70_74
- **File path:** /tmp/per_cell_verification/exit_sweep_leader_70_74.csv.
- **Notes:** Per-c exit sweep at 1c granularity for one cell (drilldown). Implements A13 (granularity matters).

#### config_history_trace
- **File path:** /tmp/config_history_trace.py + duplicate.
- **Notes:** Traces config changes over time relative to bleed periods.

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

### Canonical foundation: G9 parquets (T17 + T27, foundation-commit anchor)

These three parquets are the canonical foundation for all Layer A/B/C work going forward
per LESSONS C27 (analytical-foundation discipline). Every downstream analysis entry below
must reference this foundation explicitly via T28 commit pointer.

#### g9_candles.parquet
- **File path:** arb-executor/data/durable/g9_candles.parquet
- **Producer script:** arb-executor/data/scripts/build_g9_parquets.py (commit bd83412)
- **Source data:** arb-executor/data/historical_pull/candlesticks/*.csv (19,687 files)
- **Date created:** 2026-05-04 (Session 6 T17)
- **Depth:** N/A (canonical source, not analysis)
- **Data tier used:** G-tier source → canonical parquet
- **Schema:** 18 columns — ticker (injected), end_period_ts, open_interest_fp, price_close, price_high, price_low, price_mean, price_open, price_previous, volume_fp, yes_ask_close, yes_ask_high, yes_ask_low, yes_ask_open, yes_bid_close, yes_bid_high, yes_bid_low, yes_bid_open. Bare names canonical (era variation per F29 normalized at producer).
- **Row count:** 9,500,168
- **Validity status:** VERIFIED per T27 verification probe (Session 6, 9/9 checks passed including row count parity, schema normalization, reconstruction equivalence, no all-null era columns).
- **Notes:** ~65% of minutes have null price_close/volume_fp/open_interest_fp (no-trade minutes per G19); yes_bid_close/yes_ask_close are 100% populated. sha256 in arb-executor/data/durable/MANIFEST.md.

#### g9_trades.parquet
- **File path:** arb-executor/data/durable/g9_trades.parquet
- **Producer script:** arb-executor/data/scripts/build_g9_parquets.py (commit bd83412)
- **Source data:** arb-executor/data/historical_pull/trades/*.csv (20,018 files)
- **Date created:** 2026-05-04 (Session 6 T17)
- **Depth:** N/A (canonical source)
- **Data tier used:** G-tier source → canonical parquet
- **Schema:** 7 columns — count_fp, created_time (ISO 8601 microsecond UTC), no_price_dollars, taker_side ({yes, no}), ticker, trade_id, yes_price_dollars.
- **Row count:** 33,727,162
- **Validity status:** VERIFIED per T27 (taker_side enum: only {yes, no}, 0 nulls; row count parity exact).
- **Notes:** Microsecond-precision trade tape. sha256 in MANIFEST.md.

#### g9_metadata.parquet
- **File path:** arb-executor/data/durable/g9_metadata.parquet
- **Producer script:** arb-executor/data/scripts/build_g9_parquets.py (commit bd83412)
- **Source data:** arb-executor/data/historical_pull/market_metadata/*.json (20,110 files)
- **Date created:** 2026-05-04 (Session 6 T17)
- **Depth:** N/A (canonical source)
- **Data tier used:** G-tier source → canonical parquet
- **Schema:** 48 columns including ticker, event_ticker, custom_strike (JSON-stringified, contains tennis_competitor UUIDs per T25), settlement_ts, settlement_value_dollars, result, status, volume_fp, open_interest_fp, plus all metadata fields per market.
- **Row count:** 20,110
- **Validity status:** VERIFIED per T27 (custom_strike round-trip: 20,110/20,110 parse back to dict cleanly).
- **Notes:** sha256 in MANIFEST.md.

---

### Layer A v1 outputs (T29, foundation T28 ea84e74)

Per-cell forward-bounce distributions aggregated from G9 candles. Property of the market, not strategy — Layer A per LESSONS B16. No exit logic, no fees, no fill probability. Foundation pointer: T28 commit ea84e74. Producer commit: 1398c39. MANIFEST commit: 37a5216 (sha256-pinned). Validity status: PASSED T21 coherence read 2026-05-04 (4 PASS / 2 INCONCLUSIVE / 0 FAIL). The six-check methodology validation gate from ROADMAP T21 ran in Session 6 Phase 5-ii; 4 cleanly pass (Check 2 premarket vs in_match, Check 3 settlement asymmetry, Check 4 category liquidity-tier dominance, Check 6 YES/NO fold symmetry); 2 inconclusive in informative ways (Check 1 hypothesis shape mismatch per LESSONS B20, Check 5 volume_intensity in_match collapse per LESSONS F30). Downstream Layer B (ROADMAP T31, promoted from G10) and Layer C (ROADMAP G11) cleared to consume. Findings cross-referenced in LESSONS A36, B19, B20, F30.

#### cell_stats.parquet

- File path: arb-executor/data/durable/layer_a_v1/cell_stats.parquet
- Producer script: arb-executor/data/scripts/build_layer_a_v1.py at commit 1398c39
- Source data: g9_candles.parquet + g9_metadata.parquet (T28 foundation, commit ea84e74)
- Date created: 2026-05-04 (Session 6, 60.7 min producer runtime)
- Depth: 1 (Distribution per TAXONOMY Section 2)
- Data tier used: G
- Schema: 671 cells x ~80 metric columns. Cell key: (category, regime, entry_price_band, spread_band, volume_intensity). Metrics: forward-bounce distribution at horizons {5, 15, 30, 60 min, settlement}, drawdown distribution, breakeven-threshold fractions at {1c, 2c, 5c, 10c, 20c}, n_markets, n_moments per cell.
- Row count: 671 cells (aggregated from 8,981,594 moments across 19,603 markets)
- Validity status: PASSED T21 coherence read 2026-05-04 (4 PASS / 2 INCONCLUSIVE / 0 FAIL)
- Notes: volume_intensity is per-market not per-moment — known v1 caveat documented for v2 follow-up. OTHER category included as fifth bucket beyond ATP_MAIN/ATP_CHALL/WTA_MAIN/WTA_CHALL. **T21 verification findings (2026-05-04, commit pointer in CHANGELOG):** (1) Producer is YES-only — reads yes_bid_close + yes_ask_close exclusively, no_* columns ignored. NO-side distributional questions answerable via fold symmetry per LESSONS A36. (2) Bounce definition is forward_max_excursion_excluding_t (max(yes_ask[i+1:i+window]) - yes_ask[i]) — can be negative for monotonically declining trajectories near settlement. 52% of settlement_zone cells have negative bounce_5min_p25; not a bug, definitional choice consistent with B16 Layer A scoping. (3) Reservoir sampling implements Vitter algorithm (line 167-172) — unbiased percentile estimators. (4) volume_intensity collapses to single bucket (high) within in_match regime per LESSONS F30 — uninformative as in_match stratifier; valid for premarket. (5) No event_ticker preserved per LESSONS B19 — per-event analyses require G12 producer.

#### sample_manifest.json

- File path: arb-executor/data/durable/layer_a_v1/sample_manifest.json
- Producer script: arb-executor/data/scripts/build_layer_a_v1.py at commit 1398c39
- Source data: same as cell_stats.parquet (T28 foundation)
- Date created: 2026-05-04 (Session 6)
- Depth: 0 (manifest, not analysis)
- Data tier used: G
- Schema: per-cell list of sampled tickers used for visual reproduction
- Row count: 671 cells (one entry per populated cell)
- Validity status: PASSED T21 2026-05-04 (paired with cell_stats.parquet)
- Notes: enables reproducing visual PNGs deterministically; tickers were sampled at producer runtime, not at coherence-read time.

#### build_layer_a_v1.log

- File path: arb-executor/data/durable/layer_a_v1/build_layer_a_v1.log
- Producer script: arb-executor/data/scripts/build_layer_a_v1.py at commit 1398c39
- Source data: producer stdout/stderr only
- Date created: 2026-05-04 (Session 6)
- Depth: n/a (operational log)
- Data tier used: n/a
- Schema: text log
- Row count: n/a
- Validity status: n/a (log artifact)
- Notes: 60.7 min runtime, clean exit, memory pressure at 67% during visual phase (paged but did not OOM).

#### visual PNGs (15 files)

- File path: arb-executor/data/durable/layer_a_v1/visual_*.png (15 files)
- Producer script: arb-executor/data/scripts/build_layer_a_v1.py at commit 1398c39
- Source data: cell_stats.parquet + sample_manifest.json
- Date created: 2026-05-04 (Session 6)
- Depth: 0 (visual sanity check, not statistical analysis)
- Data tier used: G
- Schema: 5 categories (ATP_MAIN, ATP_CHALL, WTA_MAIN, WTA_CHALL, OTHER) x 3 regimes (premarket, in_match, settlement_zone)
- Row count: 15 PNG files, 8,758,898 bytes total (per MANIFEST commit 37a5216)
- Validity status: PASSED T21 visual review 2026-05-04
- Notes: dense PNGs (ATP/WTA tour-level premarket+in_match) are 800KB-1.1MB each; sparse PNGs (settlement_zone subcategories, OTHER) are 44-273KB. File-size pattern itself is a coverage signal — sparse cells reach the 5-min-pre-settle window or fall into OTHER ticker prefix less often.

---


### Layer B v1 outputs (T31b-gamma, foundation T28 ea84e74 + T29 1398c39)

[#layer-b-v1-outputs-t31b-gamma-foundation-t28-ea84e74--t29-1398c39](#layer-b-v1-outputs-t31b-gamma-foundation-t28-ea84e74--t29-1398c39)

Per-cell exit-policy capture distributions across 54-policy parameter grid. Property of strategy given Layer A bounce distribution — Layer B per LESSONS B16. No fees, no fill probability, no slippage; those live in Layer C (G11). Foundation pointer: T28 commit ea84e74 (G9 parquets) + T29 commit 1398c39 (Layer A v1 cell_stats). Producer commit: 28e8ab7. MANIFEST commit: this commit. Validity status: PASSED T31c coherence read 2026-05-05 ET (commit 5cf45e0). 4/4 gating-checks PASS. Cleared for downstream Layer C (G11) consumption.

#### exit_policy_per_cell.parquet

[#exit_policy_per_cellparquet](#exit_policy_per_cellparquet)

- File path: arb-executor/data/durable/layer_b_v1/exit_policy_per_cell.parquet
- Producer script: arb-executor/data/scripts/build_layer_b_v1.py at commit 28e8ab7
- Source data: g9_candles.parquet + g9_metadata.parquet (T28 foundation, commit ea84e74) + sample_manifest.json (T29 commit 1398c39)
- Date created: 2026-05-05 ET (Session 7 T31b-gamma-1)
- Depth: 5 (strategy simulation per TAXONOMY Section 2)
- Data tier used: G
- Schema: 21 columns. Cell key: (channel, category, entry_band_lo, entry_band_hi, spread_band, volume_intensity). Policy: (policy_type, policy_params). Counts: n_simulated, n_fired, n_horizon_expired, n_settled_unfired. Distributions: fire_rate, capture_mean, capture_p10/p25/p50/p75/p90. Misc: median_time_to_fire, capital_utilization.
- Row count: 19170 ((cell, policy) tuples; 355 cells × 54 policies)
- Validity status: PASSED T31c coherence read 2026-05-05 ET (script commit 5cf45e0, report sha256 72f1747b). 4/4 gating-checks PASS (Check 1 capture-bounded spot-check, Check 2 fire-rate monotonic, Check 3a limit-policy capture_p90 trend, Check 4 premarket vs in_match). 1 informative-only Check 3b INCONCLUSIVE (time-stop horizon trend, empirical signature of mean reversion per LESSONS B21 — not gating). Cleared for downstream Layer C (G11) consumption.
- Notes: 1 cells excluded from output by 50-trajectory threshold (per spec Decision 2 patch 3). 278208 total entry moments evaluated. capital_utilization convention documented inline in producer aggregate_cell_results: held_minutes / denominator (clamped to [0, 1]); denominator = horizon_min for time_stop/limit_time_stop, else 240. T31a patch 5 corrected the validation-gate formulation post-spec; T31a patch 6 dropped sub-minute (30s) horizon, leaving 54 policies in v1.

### Layer C v1 specification (T32a, foundation T28 ea84e74 + T29 1398c39 + T31b 28e8ab7)

[#layer-c-v1-specification-t32a-foundation-t28-ea84e74--t29-1398c39--t31b-28e8ab7](#layer-c-v1-specification-t32a-foundation-t28-ea84e74--t29-1398c39--t31b-28e8ab7)

Realized economics from empirical fees on top of Layer B v1's idealized-fill capture distributions. Per LESSONS B16 layered-realism discipline, Layer C has its own v1/v2/v3/v4 sub-staging; v1 adds ONE modeling concept (empirical fees from kalshi_fills_history.json per A30) and inherits idealized fills from Layer B v1. v1 strictly per-cell per E20, single-leg per E18, channel-preserving per E16/B14/E31, ROI on cost basis per G1. Foundation pointers: T28 commit ea84e74 (G9 parquets, sha256-pinned) + T29 commit 1398c39 (Layer A v1 cell_stats) + T31b commit 28e8ab7 (Layer B v1 exit_policy_per_cell.parquet, sha256 d94bc56c..., validated by T31c PASS at 5cf45e0). Spec commit: 4bed07f. MANIFEST entry: PENDING T32b/T32c (no output artifacts yet — spec only). Validity status: SPEC (not output-bearing). T32b (producer build_layer_c_v1.py) and T32c (coherence read check_layer_c_v1_coherence.py + report) will add output artifacts in subsequent commits.

#### docs/layer_c_spec.md

[#docs-layer-c-spec-md](#docs-layer-c-spec-md)

- File path: docs/layer_c_spec.md
- Authored: 2026-05-05 ET (Session 8, T32a)
- Author commit: 4bed07f
- Length: 189 lines, 9 sections
- Structure: Scope (v1) + Foundation pointers + Operational decisions (6 numbered) + Output schema (32 columns) + Producer architecture + Validation gate (4 gating + 1 informative checks) + Open items for v2/v3/v4 + Cross-references (16 keystone lessons) + Outstanding ROADMAP correction
- Key decisions: D1 empirical fee derivation per (is_taker, yes_price_bucket) from kalshi_fills_history.json — NOT maker-zero (37.7% of bot maker fills are non-zero, parabolic per Kalshi schedule); D2 maker-maker production model with policy-class taker-exposure for time-stop horizon-fired exits; D3 1:1 row mapping to Layer B (no posting_strategy or capital_size sweep dimensions); D6 formation-period contamination per E12 inherited explicitly with Check 5 measuring impact informatively
- Validation gate: Check 1 realized_capture ≤ capture; Check 2 parabolic-shape match; Check 3 policy-class taxonomic match; Check 4 Layer B → Layer C ranking preservation (≥90% cells Spearman ≥ 0.99); Check 5 (informative-only) formation-period contamination measurement
- Validity status: SPEC stable post-author. Closes T32a when this ANALYSIS_LIBRARY entry lands.
- Notes: Spec Section 9 explicitly flags ROADMAP T32 entry (commit f048267) as needing correction — currently states "maker-zero canonical confirmed empirically" which is empirically wrong per Decision 1. Correction follows in separate single-concern commit.

## SECTION 3: BROKEN OR INVALID ANALYSES

Analyses that ran but produced invalid results due to bugs, methodology errors, or data corruption. Listed here so future chats know not to cite their conclusions.

#### Greeks decomposition (Depth 4)
- **Files:** /tmp/per_cell_verification/greeks_decomposition.csv, /tmp/per_cell_verification/greeks_per_match.csv.
- **Lesson:** F11.
- **Issue:** Degenerate first-bid bug. Schema is correct; numbers are not trusted.
- **Status:** Awaiting rebuild on cleaner data.

#### Bias reconciliation fragmentation (Depth 2 + 6)
- **Files:** Six+ entries in F19 cluster above.
- **Lesson:** F19.
- **Issue:** Multiple files measuring overlapping but non-identical concepts; "operator memory says +21-37c, file shows max 10.6c" discrepancy persists.
- **Status:** Awaiting canonical designation.

#### matches.entry_time-dependent analyses
- **Files:** Any analysis depending on matches.entry_time on live/live_log rows.
- **Lesson:** F17.
- **Issue:** Column is NULL on every live and live_log row sampled.
- **Status:** Re-derive entry timing from JSONL logs (tz-clean per F16) or cell_match events.

#### Pre-Bug-3-fix entry_price-dependent analyses
- **Files:** Any analysis using entry_price from bot reconcile-path-affected windows.
- **Lesson:** F6.
- **Issue:** Reconcile path was unconditionally overwriting Position.entry_price every 60 seconds before the Apr 29 fix.
- **Status:** Validity depends on fill date relative to fix.

#### Settlement-event-dependent P&L
- **Files:** Any per-cell P&L analysis using log-based settlement detection.
- **Lesson:** F8.
- **Issue:** When bot resting sell is unfilled at market close, NO settlement event is logged. Position loss is invisible.
- **Status:** Bug 4 remediation in progress; analyses await fix.

---

## SECTION 4: NOTABLE PRIOR FINDINGS (currently asserted)

Findings from prior analyses that are currently treated as anchor evidence in the operation. Each must be classified to its proper depth and noted with the limits of that depth.

#### 70.7% bilateral double-cash rate at +10c (April 14, 458 paired matches)
- **Depth:** 0 (existence proof).
- **Variables used:** first_price and max_price both sides.
- **Tier:** C (historical_events).
- **Strict reading:** Bilateral oscillation exists at the +10c threshold across 458 matches.
- **Does NOT establish:** Capturability, fillability, profitability, or per-cell consistency.
- **References:** LESSONS.md E18 (assertion), E25 (depth-0 caveat).
- **Reproduction status:** Pending. ROADMAP Section 4 BLOCKED.

#### Channel 1 vs Channel 2 split (4.7% / 95.3%)
- **Depth:** 2 (trajectory).
- **Producer:** /tmp/channel_decomp.py (current session).
- **Variables used:** JSONL log entry_filled and exit_filled events; ts_et fields.
- **Strict reading:** Of the 977 fills with exit_filled events, 4.7% exited before match start (Channel 1) and 95.3% exited after (Channel 2).
- **Does NOT establish:** Whether this distribution holds for cells that have higher pregame oscillation; whether the 95.3% reflects desired bot behavior or accidental settlement-ride.
- **References:** LESSONS.md E15, E16, E17.

#### 977-fill realized P&L (Mar 26 to Apr 17): -$1,339.52
- **Depth:** 5 (strategy simulation, retrospective).
- **Variables used:** matches table fill records (live + live_log).
- **Strict reading:** Bimodal P&L distribution confirms riding-to-settlement mechanism.
- **Caveats:** F7 (some fills recorded wrong), F8 (settlement events sometimes unlogged), F17 (entry_time NULL).
- **References:** LESSONS.md Section 2.

#### Apr 24 to Apr 29 post-retune: 106 resolved at +$17.21 net
- **Depth:** 5.
- **Caveats:** 58 still resting (unknown outcome); E8 (retune isolation problem — 14 cell disables + 8 exit retunes + 12 code changes simultaneously).

---


#### Combined-trade-price distortion absence (Cat 9, Session 9, commit 631e653)
- **Depth:** 0 (existence proof — null result).
- **Producer:** data/scripts/diagnostics_session_8/cat_09_distortion_events.py (sha256 `653e9d74888376f1`, runtime 643s).
- **Data tier used:** G (g9_trades.parquet + g9_candles.parquet).
- **Variables used:** g9_trades (33,727,162 rows × 20,018 markets), g9_candles per-minute close prices, derived combined = yes_close + no_close per minute.
- **Question answered:** Across the full G9 corpus, do any per-minute candle bins exhibit combined trade price exceeding $1.00 + ε (ε=$0.01)?
- **Strict reading:** Zero events found. Zero of 20,018 markets had even one flagged minute. Per-tier: historical 0 of 1,838,273 minutes; live 0 of 1,397,886 minutes. Per-stage (formation / post-formation / in-match) distribution: empty.
- **Does NOT establish:** Absence at finer ε (e.g., $0.005, half-tick), absence of sub-minute distortions resolved before per-minute close binning, absence of microsecond intraminute distortions, absence of the converse direction (combined < $1.00 bilateral discount, which is B23's mechanism and was not Cat 9's measurement target).
- **Strategic implication:** F32's sub-claim (1) — combined > $1.00 over-pay distortions as direct alpha — is downgraded from alpha signal to alpha hypothesis pending deeper-probe disambiguation. T34 closed as superseded.
- **References:** LESSONS.md F32 (amended), LESSONS.md C31 (new — meta-lesson), ROADMAP.md T34 (closed), SIMONS_MODE.md Section 8.


#### Premarket trajectory width and bilateral feasibility (Cat 6, Session 9, commit 631e653)
- **Depth:** 0–1 (existence + distribution of trajectory width across the corpus).
- **Producer:** data/scripts/diagnostics_session_8/cat_06_trajectory_width.py (sha256 `c5280167c244eefb`, runtime 236s).
- **Data tier used:** G (g9_candles.parquet + g9_metadata.parquet for filtering to markets with sufficient premarket coverage).
- **Variables used:** g9_candles per-market premarket bid/ask, derived trajectory width = max(yes_close) − min(yes_close) over each market's premarket window; g9_metadata _tier for historical / live partition.
- **Question answered:** Across the G9 corpus, what is the distribution of premarket trajectory width per market, and what fraction of markets meet the B23 bilateral-mechanism feasibility bar (≥$0.10 trajectory width)?
- **Strict reading:** 9,238 markets had sufficient premarket data. Distribution: median $0.05, p25 $0.02, p75 $0.12, p95 $0.51, mean $0.116. Per-threshold: ≥$0.05 → 48.8% (4,505); **≥$0.10 → 29.8% (2,755)**; ≥$0.20 → 16.7% (1,545); ≥$0.30 → 11.1% (1,027). Per-tier: historical 33.2%, live 28.2%. Top-20 widest trajectories all >$0.90 (extreme favorite settlements).
- **Does NOT establish:** Bilateral-fill probability at any cell or price (orderbook depth at non-BBO is the F33/G13 gap), conditional double-cash rate given paired entries (that is the E18/E30 layer of the funnel), per-cell bilateral capture rate (Layer A/B aggregations don't stratify on trajectory width yet — gap), why the live-vs-historical 5pp gap exists structurally.
- **Strategic implication:** B23's bilateral-mechanism prevalence is empirically 29.8% of markets, not "broadly applicable." Funnel structure named explicitly: 29.8% feasibility × ~70-76% conditional success ≈ ~21-23% unconditional double-cash rate. Forensic replay's bilateral evaluation should compute cell-level applicability against the 29.8% feasibility bound. Trajectory width should be a Layer A v2 / B v2 cell-key partition axis or filter for bilateral-relevant analyses.
- **References:** LESSONS.md B23 (amended this commit), LESSONS.md E18 / E25 / E30 (the conditional-rate funnel layer — separate amendment trajectory), SIMONS_MODE.md Section 3 paragraph 4 + Section 8 (forward-references that this commit backfills), F33 (depth-chain gap — independent measurement bottleneck for the next funnel layer).


#### Cross-ticker OI asymmetry distribution (Cat 10, Session 9, commit 631e653)
- **Depth:** 0–1 (existence + distribution of cross-ticker OI asymmetry across the corpus).
- **Producer:** data/scripts/diagnostics_session_8/cat_10_oi_asymmetry.py (sha256 `c09956376f9745ba`, runtime 43s).
- **Data tier used:** G (g9_metadata.parquet for paired-match enumeration + g9_candles.parquet for per-ticker final OI via candle.open_interest_fp).
- **Variables used:** g9_metadata event_ticker for pairing, derived OI_asymmetry = max(OI_yes_a, OI_yes_b) / min(OI_yes_a, OI_yes_b) per paired event in the live tier (historical tier omitted per F31's known OI-zero coverage gap).
- **Question answered:** Across the G9 corpus, what is the distribution of cross-ticker OI asymmetry for paired matches with non-zero OI both sides, and at what threshold does the asymmetry begin to be strategically applicable for ladder-on-deeper-side strategy?
- **Strict reading:** 8,106 tickers with OI data; 4,053 paired events with both tickers carrying OI; 4,044 paired matches with non-zero OI both sides used for distribution. Distribution: median 1.48×, p75 2.01×, p95 3.36×, max 38.68× (KXWTACHALLENGERMATCH-26APR26SIDZHU: SID 31 vs ZHU 1199). Per-threshold: **≥2× → 1,024 (25.3%, strategic threshold)**; ≥4× → 97 (2.4%, original anchor tail location); ≥10× → 10 (0.2%, extreme tail). DZU/MAN corpus reproduction: 38 paired matches in corpus, max observed 4.23× (KXATPMATCH-26APR22BUSMAN); the original Dzumhur/Mannarino ATP Rome screenshot (4.15×) pre-dates corpus cutoff and is not directly reproducible.
- **Does NOT establish:** Why specific paired matches exhibit higher asymmetry (no model linking match-level features to expected asymmetry); whether asymmetry persists or oscillates within a market's lifetime (Cat 10 measures final OI only, not trajectory); per-cell asymmetry breakdown (Layer A/B/C aggregations don't stratify on cross-ticker OI asymmetry yet — gap); depth-level asymmetry beyond OI (F33/G13 gap); asymmetry in historical tier (excluded due to F31 OI coverage gap).
- **Strategic implication:** B24's "ladder-on-deeper-side" strategy threshold shifts from 4× (rare-tail, 2.4% applicability) to 2× (strategic-threshold, 25.3% applicability) for design purposes. The original 4× anchor remains valid as a single-event operator-witnessed observation but sits at the top 2-3% tail of the distribution rather than being typical. Forensic replay evaluation (per SIMONS_MODE.md Section 6) of ladder-on-deeper-side cells should surface both 2× threshold (strategic mass) and 4× threshold (tail-event sensitivity) coverage rates.
- **References:** LESSONS.md B24 (amended this commit), LESSONS.md B22 / B23 / C31 (mechanism context, adjacent amendments), F31 (per-minute OI partially tracked at candle level — Cat 10's data source), F33 (depth-chain asymmetry separate gap, not addressable from current data), T33 (B24 4× anchor reference — Cat 10 contextualizes without invalidating), SIMONS_MODE.md Section 8 (forward-reference that this commit backfills).


#### Per-(cell, policy) EV distribution by channel (Cat 5, Session 9, commit 631e653)
- **Depth:** 1 (distribution of per-(cell, policy) capture_mean across the simulator's full output, partitioned by channel).
- **Producer:** data/scripts/diagnostics_session_8/cat_05_alpha_discovery.py (sha256 `df8257a183e4c637`, runtime 1s).
- **Data tier used:** Derived from layer_b_v1/exit_policy_per_cell.parquet (which derives from G-tier g9_trades + g9_candles).
- **Variables used:** capture_mean per (channel, category, entry_band_lo, entry_band_hi, spread_band, volume_intensity, policy_type, policy_params); 19,170 rows total across 3 channels (premarket / in_match / settlement_zone).
- **Question answered:** Across the simulator's full (cell, policy) output, what is the distribution of capture_mean by channel, and where do the top-EV cells concentrate?
- **Strict reading:** Channel-level summary: in_match 6,480 cells (mean −$0.034, median −$0.026, max $0.393); premarket 12,690 cells (mean −$0.069, median −$0.034, max $0.509). **Aggregate statistics favor in_match (typical cell less negative); right-tail statistics favor premarket (top-EV cells concentrate there — 7 of top 10 overall, max 0.509 vs 0.393).** Top premarket cell: WTA_MAIN 40-50 / tight / low / time_stop. Both channels have negative cell-level mean and median — the strategic distinction lives at the right tail, not at the aggregate.
- **Does NOT establish:** Why the top-tail premarket cells achieve their EV (Cat 5 reports the EV but not the underlying retail-behavior pattern that creates the bouncability); fee-adjusted EV (Layer B v1 is gross; Cat 2 fees apply post-hoc per Layer C v1 spec); execution feasibility at simulated EV (queue position, F33/G13 depth-chain gap); per-cell variance, fill speed, drawdown (Cat 5 measures capture_mean / capture_p90 only); whether realized EV under forensic replay tracks simulated EV (the deliverable per SIMONS_MODE.md Section 6).
- **Strategic implication:** E16's original "in_match dominance" framing reflects retrospective bot-realized P&L conditioning, not per-moment per-cell EV. Forward-looking cell-selection must evaluate both channels separately because aggregate (favoring in_match) and right-tail (favoring premarket) tell different strategic stories on the same data. Per the Simons-mode discipline (SIMONS_MODE.md Section 7 rollback question 5), the strategic concentration is on top-tail verified cells, not aggregate channel routing. Forensic replay should rank cells per-channel separately and validate top-N from each against tick-level reality.
- **References:** LESSONS.md E16 (amended this commit), LESSONS.md B14 / E31 (channel preservation discipline), LESSONS.md B23 / B24 / F32 (sibling Session 9 amendments — same chain), C31 (adjacent epistemic pattern — multi-frame empirical disambiguation), SIMONS_MODE.md Section 7 (5%-vs-95% sea discipline applied at cell-selection level), SIMONS_MODE.md Section 8 (forward-reference that this commit backfills).

## SECTION 5: CHANGELOG

- 2026-04-30 ~13:21 ET: Initial scaffolding (commit c794b26). Section 4 had one entry (70.7%); Sections 2 and 3 placeholder.
- 2026-04-30 ~14:30 ET (this commit): Sections 2, 3, 4 fully populated from depth-inventory CC probe. Catalog covers ~40 distinct analyses across 6 depth levels plus broken/meta categories.
- 2026-04-30 (item 5 closure): Corrected mischaracterization of /root/Omi-Workspace/tmp/ — it is a curated git-tracked archive with multiple curation batches, not a single Apr 29 snapshot. Canonical-source rules updated.
- 2026-05-04 (Session 6 T28): G9 parquets (g9_candles, g9_trades, g9_metadata) added as canonical foundation per LESSONS C27. T17 producer commit bd83412, T27 verification 9/9 PASS. sha256 in MANIFEST.md.
- 2026-05-04 (Session 6 T29): Layer A v1 outputs (cell_stats.parquet, sample_manifest.json, build_layer_a_v1.log, 15 visual PNGs) added under new subsection in Section 2. Foundation pointer T28 commit ea84e74. Producer commit 1398c39. MANIFEST commit 37a5216. Validity: PASSED T21 coherence read 2026-05-04 (4 PASS / 2 INCONCLUSIVE / 0 FAIL).
- 2026-05-04 (Session 6 Phase 5-ii / T21 closure): cell_stats.parquet Notes field updated with T21 verification findings (YES-only producer, bounce-def explanation, Vitter reservoir confirmed unbiased, volume_intensity in_match collapse, no event_ticker preserved). Validity status flipped from PENDING T21 to PASSED T21 2026-05-04 across cell_stats.parquet narrative + Notes line, sample_manifest.json, and visual PNG block. Cross-references to LESSONS A36, B19, B20, F30 and ROADMAP F13, G12, T31.
- 2026-05-05 ET (Session 8 / T32a-followup): Layer C v1 specification entry registered. Foundation pointers T28 ea84e74 + T29 1398c39 + T31b 28e8ab7. Spec at docs/layer_c_spec.md (commit 4bed07f, 189 lines, 9 sections, 6 numbered Decisions, 5 validation checks). Validity status SPEC (not output-bearing — T32b producer and T32c coherence read add output artifacts in subsequent commits). Closes T32a per its own definition (spec lands and is referenced in ANALYSIS_LIBRARY).
