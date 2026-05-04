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

## SECTION 5: CHANGELOG

- 2026-04-30 ~13:21 ET: Initial scaffolding (commit c794b26). Section 4 had one entry (70.7%); Sections 2 and 3 placeholder.
- 2026-04-30 ~14:30 ET (this commit): Sections 2, 3, 4 fully populated from depth-inventory CC probe. Catalog covers ~40 distinct analyses across 6 depth levels plus broken/meta categories.
- 2026-04-30 (item 5 closure): Corrected mischaracterization of /root/Omi-Workspace/tmp/ — it is a curated git-tracked archive with multiple curation batches, not a single Apr 29 snapshot. Canonical-source rules updated.
