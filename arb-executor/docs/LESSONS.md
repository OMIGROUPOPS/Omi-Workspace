# OMI Operating Library

Last updated: 2026-04-30
Maintainer: Druid (operator) + Claude (chat) + CC (Claude Code on VPS)
Purpose: Master library for the OMI tennis trading operation. Captures lessons learned, current state, what we know, what we do not know, and where the analytical artifacts live. Future chat sessions and CC instances must read this file first before doing anything else.

Repo: github.com/OMIGROUPOPS/Omi-Workspace
VPS: root@104.131.191.95
Working dir: /root/Omi-Workspace/arb-executor/
This file: /root/Omi-Workspace/arb-executor/docs/LESSONS.md
Raw URL for new chats: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/main/arb-executor/docs/LESSONS.md

---

## SECTION 1: WHERE WE ACTUALLY STAND (READ THIS FIRST)

The bot is shut down. Live trading is not active. Paper mode is running on a config that is explicitly an artifact of broken methodology, not a working baseline.

We know there is a strategy that works. We do not know exactly what it is yet. We have evidence that the structural opportunity exists (e.g., 70.7% double-cash rate at +10c bilateral exits across 458 leader/underdog pairs from April 14 analysis). We have hunches about which directions are strong. But we have not been able to validate them with confidence because the data we have been analyzing on has been compromised in ways we are still discovering.

Why the foundation is not trustworthy:
- Some games recorded entries and exits wrong, which deflated metrics on cells/strategies the operator suspected were strong.
- Multiple bot iterations across months produced layered logs/data with different schemas and different bugs.
- Earlier "rebuild" attempts inherited assumptions from broken methodology without fully realizing it.
- Several measurement methodology errors compounded each other (see Section 5 lessons A, B, F).
- Specific known data corruption: reconcile path overwriting entry_price every 60s (Bug 3, fixed Apr 29); fill quantity under-reporting (POTRYB qty=1 logged, actual=10); missing settlement events when bot resting sell unfilled (Bug 4, in progress).

We cannot reconfigure or redeploy until we trust the foundation. Every config change depends on cell-level data being accurate. Cell-level data depends on entries/exits being recorded accurately. Those records have known errors we have not fully cataloged or corrected.

Wall Street-grade metrics are the bar. Acceptable measurement includes Sharpe, expected value with confidence intervals, drawdown and tail risk, capital efficiency, hit rate times profit at each exit, variance across cells, settlement-loss frequency, Greeks adapted for binary contracts (delta, gamma, theta, vega). Not acceptable: small-N pattern matching, single-metric optimization, per-cell numbers without confidence bounds.

The work right now is foundational, not tactical. We are not optimizing exit_cents. We are not picking which cells to enable. We are rebuilding our ability to trust any per-cell metric at all.

The temptation to start tactical work is the trap. Multiple chats have spun out by skipping this section.

---

## SECTION 2: WHAT WE KNOW (with current evidence)

### Strategy structure
- The bot is operationally an in-game spike capture mechanism via passively resting sells, not a premarket scalper. Channel 1 (premarket exit) fires 4.7% of the time; Channel 2 (in-game exit) fires 95.3% of the time, median 3.75 hours after entry. The bot has no live game-state intelligence — Channel 2 fires whenever an in-game price move rips through the resting sell, regardless of why.
- Goal: cash both sides of a binary market before settlement when EV supports it. Not every game can double-cash; the strategy edge is positive aggregate EV across all games. April 14 paired analysis (458 leader/underdog pairs) found 70.7% bilateral double-cash rate at +10c bilateral exits — concrete evidence the oscillation edge exists structurally.
- Per-cell calibration is required. Across-the-board uniform exits underperform per-cell tuning. ATP_CHALL both-sides hybrid analysis shows wildly different bilateral capture rates per entry bucket: 5-15c bucket reaches entry times 2 in 76.9% of cases; 80-95c bucket reaches entry times 2 in 0% of cases (but reaches entry+10c in 54.5%). Some cells will be skip-or-single-side, not bilateral.
- Premarket has internal phases: pre-formation (right after Kalshi market open, wild moves), formation period (lines moving as price discovery happens), post-formation/settled premarket (consensus established). Bot uses a 4-hour entry gate to ensure entries are post-formation and FV anchors are reliable. Not perfect — formation timing varies.
- Bot edge thesis (per code) is anchor-relative discount capture. Buys when Kalshi mid is meaningfully below an FV anchor (Scenario C_discount, 97% of fills). Scenarios A_premium and B_take are theoretical in practice.

### Realized P&L history
- Mar 26 to Apr 17 (977 fills, source = live + live_log): minus $1,339.52, mean minus 137c per fill. Bimodal P&L (heavy +500c wins, heavy minus 500c losses, almost nothing in between) confirms bot was riding to settlement, not scalping.
- Apr 24 to Apr 29 (131 JSONL fills, post-bot-retune): 106 resolved at +$17.21 net, mean +16.6c. 58 still resting (unknown outcome). Caveat: if those rest into settlement losses, the post-retune number degrades.
- Leaders carry 84% of dollar bleed despite being 79% of fills. Per-cell concentration: leader_50-54 catastrophic at minus $22.52 per fill, leader_55-59 / 60-64 / 80-84 also bleeding. Worst single fill: leader_80-84 entered at 79c, settled at 1c.

### Bot mechanics
- Bot version: live_v3.py (current). Earlier versions (tennis_v5, arb_executor_v7, swing_ladder) wrote logs/data in different formats now considered legacy.
- Entry logic: Schedule gate, then Intelligence-window gate (4-12hr cap depending on tier), then BBO freshness, then Per-side gates, then Anchor resolution, then Cell lookup, then Scenario classification (A/B/C), then Pre-post race guard, then Place buy.
- Exit logic: After entry_filled, place static resting sell at fill_price + cell_cfg["exit_cents"]. Sell stays in place through pre-match, match start, and the match itself. NEVER cancelled or repriced based on game progression. Position closes when sell fills OR market settles.
- Three scenarios: A_premium (kalshi above anchor, only within 1h of match), B_take (kalshi 8c+ below anchor, take the ask), C_discount (kalshi at-or-slightly-below anchor, post maker). 97% of historical fills are C_discount.
- No live game-state ingestion. Bot has no awareness of score, sets, breaks. Channel 2 capture is purely passive.
- Apr 24 retune disabled 14 cells, retuned 8 exits, made 12 code changes simultaneously. Cannot isolate which intervention drove subsequent improvement.

---

## SECTION 3: HUNCHES WORTH PROTECTING

These are operator intuitions that may have been deflated by suspect data and may be stronger than current measurements suggest. Treat with care; do not dismiss without re-testing on cleaned data.

- Specific cells the operator suspected were strong have shown weak metrics. The underlying entry/exit records in those cells may have been recorded wrong. Worth re-measuring on cleaned data.
- Strategy thesis evolution suggests real underlying intuition. Cross-platform arb v1 (now retired), then Pendulum paired vol, then STB/Pendulum directional v3, then V4 game-state. The operator has been iterating on a real underlying intuition that has not been cleanly captured in any single config.
- Two-channel exit is an unutilized asset. Operator explicitly stated: having both Channel 1 (premarket) and Channel 2 (in-game) available on the same resting sell is an advantage. Most prior analyses focused only on Channel 1; Channel 2 is where 95% of P&L lives.
- Cell inversion is structural. Every market has 2 cells (one per player). The two cells of a game are inverted (sum to ~$1). This is a property of the data we want to use for cross-check and bilateral capture analysis. Not the strategy itself, but a structural feature the strategy can exploit.

---

## SECTION 4: DATA SOURCES & ARTIFACT INVENTORY

### Operational data
- tennis.db (1.29 GB, /root/Omi-Workspace/arb-executor/tennis.db):
  - historical_events (5,889 rows, Jan 2 to Apr 10): match summaries with first/min/max/last prices both sides. Includes in-game movement.
  - book_prices (2.99M rows, Apr 19 to Apr 29): timestamped book prices.
  - kalshi_price_snapshots (274K rows, Apr 21 to Apr 29).
  - matches (3,627 rows, Feb 5 to Apr 17): per-fill operational history. 977 are real fills (live + live_log, but NULL event_ticker on every row); 2,650 are backfill reconstructions.

### Tick-level data (A-tier)
- /root/Omi-Workspace/arb-executor/analysis/premarket_ticks/ (5.42 GB, Apr 18 to ongoing): 1,712 CSVs, one per ticker. 27 columns including 5-deep orderbook both sides with sizes, mid, depth_ratio, last_trade. This is the highest-fidelity data we have. Treat as primary source for any tick-level analysis.
- /root/Omi-Workspace/arb-executor/analysis/trades/ (180 MB, Apr 19+): 1,693 per-ticker trade records.
- /tmp/bbo_log_v4.csv.gz (838 MB compressed, Mar 20 to Apr 17): 515M-row BBO archive, schema timestamp, ticker, bid, ask, spread. Source for prior 515M-row DCA analysis.
- /tmp/validation4/step6_real/ticks/*.bin (Mar 17 to Apr 17): 1,678 binary tick files. Format is little-endian I-B-B (4-byte ts + 1-byte bid + 1-byte ask). Producer code exists at /tmp/validation4/step6_real/replay_v5.py.

### Pre-March data (lower tier)
- No tick-level data locally for Jan to Mar 19. Only historical_events summary table (first/min/max/last per match).
- Backfillable from Kalshi candles API if needed (/trade-api/v2/markets/{ticker}/candlesticks). Endpoint exists and is auth'd; not currently in active use by the bot.

### Data tiering principle
A-tier data (post-Apr 18 with full depth ticks) is significantly richer than older data. Analyses that blend tiers as if equivalent will dilute A-tier signal. Treat A-tier as primary; older tiers as supplementary. When bbo_log_v4 (Mar 20 to Apr 17) is involved, it is higher tier than historical_events summaries but lower than the depth-aware Apr 18+ CSVs.

### Prior analytical artifacts (rich content, partial trust)
- /tmp/v3_analysis/paired_v3optimal_summary.md — V3 Paired Optimal Analysis. Per-category rollup (ATP_MAIN, ATP_CHALL, WTA_MAIN, WTA_CHALL) with Both_clip% (double-cash rate), Combined_EV, Combined_ROI%, Sharpe (EV/std). Three scenarios per category (V3_OPTIMAL / BASELINE_10C / WORST_CASE). Per-cell marginal contribution table with V3_exit, N, V3_EV, KEEP/CONSIDER_10C verdict (38 rows).
- /tmp/atp_chall_both_sides_hybrid.txt — Per-entry-bucket bilateral capture analysis. Avg max bid, avg min bid, % reach entry times 2, times 1.5, times 1.3, % reach entry+10c, +20c, % settle at 99c.
- /tmp/atp_main_paired_analysis.txt — 496 events, 35 days. Dip threshold buckets, recovery rates, dip-buy strategies A/B/C/D and combinations. Includes drawdown (avg max 39.6c, 77% of events see at least 10c drawdown).
- /tmp/per_cell_verification/greeks_decomposition.csv — 25 cells, columns: theta_pregame_per_min, theta_early_match_per_min, gamma_avg_excursion_pct, realized_vega, pct_scalps_pregame/early/mid/late/at_settlement/no_scalp. Source flagged as broken (degenerate first-bid bug); schema is correct, numbers are not yet trusted.
- /tmp/per_cell_verification/greeks_per_match.csv — 668 rows, per-ticker. Same Greeks columns at finer granularity.
- /tmp/ev_delta.py — Deploy V3 EV-delta calculator. Per-cell gate_extend / disables blocks with (n, ev_a, ev_b) tuples. Computes daily $ delta and weekly $ delta.
- /tmp/rebuilt_scorecard.csv (67 cells, Apr 28) — Mechanism classification: SCALPER_EDGE / SCALPER_BREAK_EVEN / SCALPER_NEGATIVE / MIXED_BREAK_EVEN / SETTLEMENT_RIDE_CONTAMINATED / UNCALIBRATED. Methodology has known issues (uses fixed 15c exit, classifier threshold not surfaced, bias correction undersized vs operator memory).
- /tmp/exit_sweep_curves.csv — Per-cell ROI at every exit_c from 1c to 49c. Underdog only (leaders absent). N at least 30 per cell.
- arb-executor/analysis/cell_profiles/ (recovered from git commit bd9dd47) — 33 cells with by_exit dict (1c through 70c) including hit_rate, dpd_baby, dpd_25ct, dpd_80ct, total_pnl_cents, avg_pnl_per_match. Producer script lost.

### Logs (operational truth)
- /root/Omi-Workspace/arb-executor/logs/live_v3_*.jsonl — current bot structured log. cell_match, entry_filled, scalp_filled, exit_filled, exit_posted, paper_fill, paper_exit_fill events. Date range Apr 17 to ongoing.
- /tmp/scanner_pendulum.log — legacy bot log, contains March-era fills (e.g., KXATPMATCH-26MAR04ROYBON-BON visible).

---

## SECTION 5: LESSONS

Lessons are categorized A through G. New lessons get added at the end of their category with the next index. Lessons that are superseded get a SUPERSEDED tag and a pointer to the replacement; never deleted.

### Category A — Measurement methodology

A1. Settlement-inclusive EV double-counts wins not collected.
A2. Aggregate "pair completion %" varies per cell — never report it as a single number.
A3. DCA sweep ROI had time-ordering flaw — counted "max reached target" without enforcing it happened after DCA trigger.
A4. Uniform breakeven math across heterogeneous cells is wrong; per-cell specific math required.
A5. DCA trigger conditions create selection bias on scenarios sampled.
A6. Strategy layers must be analyzed harmonized, not independent.
A7. Match data resolution to question time scale (DCA fires on second-scale moves; 5-min snapshots miss them).
A8. Blended metrics that mix mechanically-different subsamples (winner vs loser scalps) are dangerous. Loser-side scalp economics is the variable that matters most.
A9. Exit target optimization must be scalp-achievable constrained (entry + exit_cents at most 95c).
A10. Cell classification can disagree at fill time vs at price-bucket time.
A11. Cell mismatches at boundaries (FV-cell vs fill-cell) contaminate per-cell numbers. Verify per-cell N is real.
A12. Sub-cell statistical power may be inadequate. Wider groupings can reveal signal hidden in noisy 5c partitions.
A13. Optimization granularity matters. 5c grid steps miss 2-3c precision improvements.
A14. "Entry price" must be defined relative to bot operational reality, not abstract "earliest trade."
A15. Ground truth from actual bot operations beats simulated entry prices from external data sources.
A16. Maker fills are not symmetric across market sides — verify the bot ACTUALLY trades each cell as designed before trusting cell economics.
A17. FV anchor freshness is necessary but not sufficient. FV accuracy (systematic alignment with sharp consensus) is a separate dimension.
A18. The strategy is not just "buy mispriced binaries" — it is "capture spread between retail-influenced Kalshi consensus and aggregated sharp-book consensus."
A19. The cell label only matches reality if the price used for binning is the actual price at our entry window. first_price from historical_events is the first market trade — possibly hours before our entry — not the premarket BBO at the time we would enter.
A20. Data tiers are not equivalent. Pre-March data is summary-level only; Apr 18+ is tick-level with 5-deep orderbook. Treat A-tier as primary; older tiers as supplementary.
A21. Wall Street-grade metrics are the bar. Acceptable: Sharpe-like risk-adjusted returns, EV with confidence intervals, drawdown, capital efficiency, hit rate times profit, variance across cells, settlement-loss frequency, Greeks adapted for binary contracts. Not acceptable: small-N pattern matching, single-metric optimization, per-cell numbers without confidence bounds.
A22. The measurement universe is not bid/ask/mid/spread. Real edge analysis requires: volume and trade flow (aggressor side, VWAP, volume profile), order book dynamics (iceberg detection, fade vs absorb, depth trajectory), realized volatility and autocorrelation, the Greeks (delta/gamma/theta/vega) properly computed, paired-cell lead-lag and slippage, calendar and contextual variables (time of day, tournament stage, surface, format), order flow microstructure (effective spread, realized spread, market impact). Defaulting to top-of-book bid/ask/spread analyses leaves most signal on the table. When designing measurement, ask: "what dimension of this data have we NOT touched yet?"

A23. Data sources are pulled from but not fully extracted. A-tier CSVs have 5-deep orderbook depth with sizes; we have been using only level 1. tennis.db has 7 underexplored tables (book_prices, kalshi_price_snapshots, live_scores, bookmaker_odds, betexplorer_staging, dca_truth, edge_scores) whose schemas we have not inventoried. The analysis/trades/ directory has 2.75M trade records we have barely touched. Before designing analysis, inventory what fields exist in each source, not just what we have been using.
A24. The variable inventory per data tier is the foundation of analysis design. Every analysis can only access the variables present in its source. We have systematically used 6 of 27 columns from A-tier, ignored min/last/total_trades/timestamps in C-tier, and never inventoried 7 underexplored tables in tennis.db (book_prices, kalshi_price_snapshots, live_scores, bookmaker_odds, betexplorer_staging, dca_truth, edge_scores). Before designing analysis at any depth, enumerate variables available at each tier. Analysis questions that seemed impossible may be answerable from data we already have, and questions we have been answering at depth-1 may be answerable at depth-3+ from the same source.
A25. live_scores has only final set-score outcomes, not in-match state. The columns p1_sets, p2_sets, p1_games, p2_games SUGGEST per-set and per-game tracking, but in samples p1_games/p2_games are empty strings and status is 'finished'. live_scores is insufficient for game-event-level Channel 2 attribution. To attribute Channel 2 captures to specific game events, we would need to source live in-match state from elsewhere (Kalshi live_data API, external scrapers like ESPN). Schema-promised capability does not equal data-populated reality.

A26. Trade-level data with taker_side is already collected in analysis/trades/ CSVs. Schema: ts_et, ticker, price, count, taker_side. 1,693 files, ~2.75M trade records, Apr 19+. Aggressor-side, VWAP, volume profile, and buying-pressure-vs-selling-pressure questions (depth-3 and depth-4 microstructure) are answerable from already-collected data, not requiring new collection.
A27. [PARTIALLY SUPERSEDED — see A29] Depth-1 and Depth-2 analyses exist in multiple revisions without canonical source-of-truth tracking. Per the depth-inventory probe: 8+ per-cell distribution files (exit_sweep_grid, exit_sweep_curves, optimal_exits, baseline_econ, bootstrap_ci_results, rebuilt_scorecard, post_retune_economics, per_cell_real_economics) and 5+ trajectory/bias files (entry_price_bias, entry_price_bias.run1, bias_by_cell_from_matches, swing_script outputs, channel_decomp). Multiple files measure overlapping concepts. Before any new Depth-1 or Depth-2 analysis: identify which prior analysis is canonical, or designate a canonical one explicitly. Do not stack new analysis on fragmented prior work.
A28. Bias measurement requires a tier-appropriate baseline. Three tier-specific implementations are required for full coverage of the operation period. Pre-Mar-20: C-tier limited; bias measurement from historical_events.first_price only, no tick-level baseline available. Mar 20 - Apr 17: B-tier bbo_log_v4 baseline; entry_price_bias.csv is canonical (per F22). Apr 18+: A-tier premarket_ticks 27-column baseline; NO bias measurement exists yet, must be built. Same conceptual measurement, three tier-specific implementations required. Treating a single bias file as universally canonical is wrong; the file's tier-coverage window must match the analysis window.
A29. Per-question canonical designation pattern. When multiple analysis files appear to overlap, check whether they answer overlapping questions or different questions on overlapping data. Eight scorecard files initially read as fragmentation per A27 turned out to be 8 distinct measurements: rebuilt_scorecard.csv (mechanism classification), optimal_exits.csv (exit-cents optimization), baseline_econ.csv (currently-active-config baseline), bootstrap_ci_results.csv (CI validation subset), post_retune_economics.csv (post-retune realized P&L), per_cell_real_economics.csv (operational realized P&L), comparison_real_vs_analysis.csv (predicted-vs-realized diagnostic), pnl_by_cell_config.csv (per-config-version P&L). Cell-coverage overlap between them is structural (each scope is a justified subset of the universe). Per-question canonical-designation table is the correct artifact, not pick-one-and-retire-others. Apply this lens before declaring fragmentation: if N files answer M questions where N=M, they are not fragmented.
A30. Server-side fill history is the canonical source for operational bot questions. /tmp/kalshi_fills_history.json (producer: /tmp/fills_history_pull.py) holds 7,489 server-side fills covering Mar 1 - Apr 29 (re-runnable to refresh). Per-fill schema: action (buy/sell), count_fp (actual executed quantity), created_time (UTC ISO Z), fee_cost, fill_id, is_taker (boolean), market_ticker, no_price_dollars, yes_price_dollars, order_id, side (yes/no), subaccount_number, ticker, trade_id, ts (Unix epoch). For any per-fill-level question — entry timing, actual fill quantity, taker vs maker, settlement reconciliation — this file supersedes matches.matches and all local logs. Local logs (live_v3 JSONL, tennis_v5.log) remain useful for non-fill events like cell_match decisions and bot-side reasoning, but for ground truth on what executed, kalshi_fills_history.json is canonical.

### Category B — Statistical confidence

B1. N must be statistically meaningful before drawing conclusions. N=8 is variance, not signal.
B2. Two days of live data is confirmation, not evaluation. Historical N=100+ evaluates a config.
B3. Do not conflate evaluation with confirmation. Historical evaluates, live confirms.
B4. CIs computed on per-trade variance vs aggregate-mean variance are different things. Verify which.
B5. Std deviations greater than 100% suggest asymmetric distributions where symmetric CI calculations misrepresent reality.
B6. CIs that are tight on small N can be artifacts of low-variance outcomes (e.g., 5 of 5 same outcome) — not real edge.
B7. Optimization results at the maximum tested value are likely artifacts of testing range, not real optima.
B8. Results that "look too clean" (Sharpe 1.12 across 28 days, 100% scalp WR cells) are suspicious.
B9. "X% improvement" claims without baseline confidence intervals mean nothing.
B10. Settlement events being counted as "scalps" via wide exit targets — verify any optimal exit greater than entry+25c is not a settlement-ride artifact.
B11. "Discrepancies" between numbers cited from different sources may be level-of-aggregation differences, not measurement errors. The +21-37c bias number (operator memory) vs 10.6c (canonical file max) was reconcilable as the same data at different aggregation levels: per-ticker raw values vs per-cell aggregate medians. Before treating a discrepancy as a contradiction or fragmentation: check whether the two cited numbers operate at the same aggregation level (per-fill vs per-ticker vs per-cell vs per-category). When they don't match in granularity, the discrepancy may be illusory.
B12. Derived columns may be redundant flags of categorical columns. The uncalibrated boolean column in rebuilt_scorecard.csv is 1:1 with mechanism=UNCALIBRATED — perfect partition, no information added. Reading "30 cells with uncalibrated=True" and "30 cells with mechanism=UNCALIBRATED" as separate findings would be double-counting the same fact. Before treating two derived statistics as independent signals, verify they are not just two views of the same underlying column.

### Category C — Process / workflow

C1. One question per prompt to CC. Methodical. Not throwing things at the wall.
C2. Always be suspicious. Never assume CC is correct. Every output gets cross-examined.
C3. Verify before deploying. Hundreds of past deploys happened on bad math.
C4. No interpretive deletions. Explicit authorization only for any destructive action.
C5. CC executes only explicitly authorized actions; no inferences.
C6. Pre-flight every CC prompt: what could the response be missing that I would want, what could come back ambiguous, what would make me re-prompt. If non-trivial, fold it into the prompt before sending.
C7. Verify infrastructure assumptions before launching long jobs (memory, disk).
C8. CC time estimates are unreliable. Do not accept "5 hours" or "1 AM" without verification.
C9. Single CC prompts means literally one — not "one main and one quick check alongside."
C10. Never propose config changes without reading the actual config file first. The diff report summary of a config is not the config.
C11. Pre-implementation probes catch real design issues before they ship. Make probes a default step on any design that touches an external API.
C12. Lessons go into LESSONS.md at the moment they land in conversation, not retroactively. New lesson, then categorize, then next index, then write to file. End of session: commit.
C13. Verify file existence before designing append/modify operations. Assuming a prior write succeeded without checking is the same class of error as not reading a config before changing it (C10).
C14. Analysis output paths should be canonical or explicitly versioned. Multiple competing implementations of the same analysis (ultimate_cell_economics vs corrected_cell_economics vs ultimate_cell_economics_csv) without versioning convention causes downstream consumers to not know which to trust. For future analyses: either overwrite the canonical path with the new run, or use explicit version suffix (_v2, _v3) with the latest version documented in ANALYSIS_LIBRARY.md.
C15. Legacy code paths remain on disk and remain searchable by grep. The arb-executor stack contains executor_core.py, arb_executor_ws.py, reconcile.py, and arb-executor-v2/ — all retired cross-platform arb code per E19. They still appear in find, grep, and probe results indistinguishable from active tennis code. Risk: citing a line number or behavior from legacy code as if it applies to the active tennis stack (this happened once already this session — a "line 1023 utcnow write" cited as a TZ concern turned out to be in legacy cross-platform code with no tennis-stack impact). Mitigation: when probing, explicitly scope grep paths to active tennis files (live_v3.py, tennis_v5.py, te_live.py, tennis_odds.py, kalshi_price_scraper.py, fv_monitor_v3.py, betexplorer.py) and exclude executor_core/arb_executor/reconcile/arb-executor-v2 unless the question is specifically about legacy. When a finding cites a legacy file, treat as out-of-scope unless proven otherwise.
C16. Methodology-correction commits should always inventory and mark prior outputs produced from the superseded methodology. When a later script supersedes earlier methodology (as corrected_cell_economics.py superseded ultimate_cell_economics_csv.py within an 80-minute iteration window), the on-disk outputs from the earlier methodology do not get auto-invalidated. Filenames alone do not signal validity to future readers. Mitigation: when designating a superseded methodology, write a deprecation marker (e.g., DEPRECATED_USE_X.txt) in the output directory so downstream consumers see it on directory listing.

### Category D — Memory / context discipline

D1. Compaction summaries lose strategic framing while preserving tactical bullets. When operator references "what we concluded," check the actual conversation, not the summary.
D2. Memory bullets describing concepts ("scalping AND inversion cells are BOTH a thing") are not the same as conclusions about which cells fall into which category. The lens is not the verdict.
D3. Memory bullets describing scorecards by counts ("11 confirmed SCALPER_EDGE, 4 bleed, 30 UNCALIBRATED") may be summary-of-summary, not ground truth. Verify against the actual artifact before designing analysis around the asserted shape.
D4. When operator pushes back, do not generate another plausible-sounding framework. Stop. Ask. Re-anchor. Pattern-matched fabrication compounds.
D5. Diligence means thinking through the response shape and what could be missing BEFORE the response lands, not after.
D6. This LESSONS.md is the durable memory. Future chats start by reading this file. Do not reinvent context the file already has.
D7. Schema columns suggest capability; populated content determines reality. A column named p1_games does not mean per-game state is captured if the column is empty in practice. A column named bookmaker_price does not mean sharp consensus is available if 100% of values are NULL. Before designating a table as a strategic source, verify population status (NULL rate, sample distribution, distinct value count) for the columns that matter. The schema is a promise; the data is the truth.

D8. Before drafting any additive change to LESSONS.md or any module file, first verify on-disk state of that file. Drafted-in-chat content is not on-disk content. A commit prompt drafted N turns ago may not have been executed; the user response may have been about a different topic. Verify before designing operations that depend on prior commits having landed. CC's pre-flight check (read current state, confirm preconditions) is the model to follow.
D9. Confident characterization without verification produces silent misinformation that future sessions inherit. The depth-inventory probe casually described /root/Omi-Workspace/tmp/ as a "single-mtime snapshot from Apr 29 17:43" — partially true (one large batch had that mtime) but wholly wrong as characterization (it's a multi-batch git-tracked curated archive with batches across Mar 13-15, Apr 20, Apr 29, and other dates). I wrote that characterization into ANALYSIS_LIBRARY.md uncorrected. Future Claude would have inherited the error. Mitigation: when a probe output contains a structural characterization (this directory is X kind of thing), verify the characterization with a targeted follow-up before it lands in durable docs. Sampling more than one mtime, more than one file, more than one signal. Same class as D5 (think through response shape before it lands), D7 (schema vs population), C2 (always be suspicious of CC output).
D10. After CC renames a drafted lesson via Path 1 rewrite, the on-disk lesson number differs from the originally-drafted number. Future drafts must read on-disk state and number from there, not from chat history of what was drafted. Session 4 had three such off-by-one drift events: drafted A28 landed as A27 (D1/D2 fragmentation lesson), drafted A29 landed as A28 (tier-appropriate bias baseline), drafted A30 landed as A29 (per-question canonical pattern). Each draft was one ahead because the chat-side mental model did not track the rename. Mitigation: before drafting any new numbered lesson, treat the on-disk file as authoritative; either read it via CC pre-flight or query before drafting. Do not infer the next number from chat history. Pre-flight assertions in the write script (asserting "Nxx in doc" and "Nyy not in doc") catch the drift but cost a Path 1 round-trip every time. Better to draft from on-disk state in the first place.

### Category E — Strategic framing

E1. Cell pairing is deployment artifact, not strategy property. Every cell has an inverse cell that exists whether or not we deploy it.
E2. Scalping AND inversion cells are both a thing. Always. Cells are not generic "edge or no edge" — they operate under different mechanisms. [REVISED — see E16]
E3. Bleed cells are not a uniform set, neither are SCALPER_EDGE cells. Magnitude matters. minus 1% ROI bleed at N=10 and minus 30% ROI bleed at N=50 are different findings requiring different responses.
E4. Strategy edge may exist on multiple surfaces simultaneously — decompose by surface before optimizing.
E5. Failed hypothesis tests ARE findings.
E6. Live performance feedback during config experimentation is itself diagnostic — but not statistically conclusive.
E7. When a config change "fixes" something, isolate the variable. Multiple things change in retunes.
E8. Multiple simultaneous interventions cannot be deconstructed without controlled testing.
E9. Adding untested cells creates immediate variance risk. New cells should be paper-traded or small-sized first.
E10. Bleed periods may be variance, not signal. Diagnose root cause before corrective action.
E11. The very framing of "what is our edge" may be wrong. Strategy may be capturing pregame oscillation, theta decay, vol mispricing, or sharp-consensus arbitrage. We do not know which.
E12. Premarket has internal phases: pre-formation (right after Kalshi market open, wild moves, FV anchors often unavailable), formation period (lines moving as price discovery happens), post-formation/settled premarket (consensus established). The bot 4-hour entry gate exists to ensure post-formation entries with reliable FV anchors. Not perfect — formation timing varies.
E13. Bot entry logic conditions on three axes (anchor delta, anchor source, time-to-match) and triggers under three scenarios (A_premium, B_take, C_discount). In practice 97% of fills are C_discount; A and B are theoretical.
E14. Every market has an inversion partner on the same match. Inversion is a property of the price data, not a strategy choice. Each cell stands as its own analysis unit; the inverse cell is supplementary cross-check data.
E15. Once a position is entered, the resting exit order has two independent capture windows: Channel 1 (premarket oscillation before match start) and Channel 2 (in-game price moves driven by game state). Both windows can fire on the same passively resting sell. The bot has no game-state intelligence — Channel 2 fires whenever a market move happens to rip through the resting sell, regardless of why.
E16. The bot is operationally an in-game spike capture mechanism via passively resting sells, not a premarket scalper. Channel 1 fires 4.7% of the time. Channel 2 carries 95.3% of fills and 95%+ of P&L. Premarket entry positions us cheaply in cells we want to be in; edge does NOT come from premarket scalping. Strategic levers that materially affect P&L: cell selection and exit_cents. (Replaces E2 framing of "scalping vs inversion cells.")
E17. Settlement losses are the tail risk of in-game capture. When in-game spikes do not reach the resting sell target before settlement, the position rides to 1c (full loss) or 99c (full win). Bimodal P&L distribution observed in 977 fills confirms this.
E18. Goal of the strategy is to cash both sides of a binary market before settlement when EV supports it. April 14 paired analysis (458 leader/underdog pairs) found 70.7% bilateral double-cash rate at +10c bilateral exits — concrete evidence the oscillation edge exists structurally. Not every game can double-cash; the strategy edge is positive aggregate EV across all games.
E19. Cross-platform arbitrage is no longer in scope. Current strategic frame is intra-book Kalshi only. Past iterations (Polymarket cross-arb, Pendulum paired vol) are historical context, not active threads.
E20. Each cell requires its own treatment. No global config. Per-cell calibration of entry conditions, exit_cents, sizing, and channel preference (C1 vs C2 expected fire rate) is required.
E21. Bilateral capture rate is per-cell, not uniform. Deep-skew cells (95c vs 5c) likely have near-zero bilateral capture because the underdog never bounces enough to fire. Per-cell decision: bilateral deploy, single-sided deploy, or skip.
E22. Per-cell analysis vs per-game analysis are different. Per-cell asks: across all matches, what does this cell bounce distribution look like? Per-game asks: for this single match, did both cells produce capturable spikes? The double-cash goal requires per-game analysis; per-cell is necessary input but not sufficient.
E23. Data tier definition (formal). A-tier: analysis/premarket_ticks/*.csv, Apr 18+. 27 columns, 5-deep orderbook with sizes, mid, depth_ratio, last_trade. Highest fidelity. B-tier: /tmp/bbo_log_v4.csv.gz, Mar 20-Apr 17. 5 columns: timestamp, ticker, bid, ask, spread. Top-of-book only, 515M rows. C-tier: historical_events table, Jan 2-Apr 10. Match summaries: first/min/max/last prices both sides, total_trades, first_ts, last_ts. No timing decomposition possible. A-tier and B-tier can both answer "did price reach +X" and Channel 1 vs Channel 2 timing. Only A-tier can answer order book depth, capacity for size, or microstructure questions. Only C-tier can extend N back to January at the cost of timing decomposition.

E24. The 70.7% double-cash rate from April 14 paired analysis is an aggregate across categories, not validated per-cell. Reproducing it on current data is the doc first pressure test. Per-cell decomposition (which cells contribute to the 70.7% and which drag) is a separate open question. Some cells (deep-skew like 95c vs 5c) likely have near-zero bilateral capture even if aggregate is 70.7%.
E25. The 70.7% double-cash rate from April 14 paired analysis is a depth-0 existence proof, not edge validation. It says bilateral oscillation exists at the +10c threshold across 458 matches; it does NOT say capturable, fillable, profitable, or per-cell consistent. Do not cite it as evidence of strategy validity. Cite it as evidence the structural opportunity exists at first reading; deeper validation is a separate question.

E26. Analysis depth and variable inventory are two parallel classification axes; neither dismisses the other. Depth describes what class of question is being asked (existence / distribution / trajectory / capacity / microstructure / strategy simulation / cross-sectional context). Variable inventory describes what raw signals exist in each data source. Variables enable depth, depth requires variables. Both must be classified explicitly when designing or cataloging analysis. Operator raising one dimension does not mean dismissing the other.
E27. Depth-5 strategy simulation has multiple competing "ultimate" implementations (ultimate_cell_economics, ultimate_cell_economics_csv, corrected_cell_economics, validate_and_optimize, scalp_constrained_optimize, dca_bbo_v3 and variants). This is methodology drift, not iteration. Before re-running strategy simulation, either pick one canonical implementation and document why, or explicitly retire the others. The pattern of "let me write yet another one" is what created the foundation we cannot trust.
E28. E27 (D5 methodology drift) has two components, not one. Component 1: producer-script drift (multiple competing implementations, e.g., ultimate / ultimate_csv / corrected / validate_and_optimize). Component 2: residual on-disk outputs from superseded methodology (e.g., /tmp/harmonized_analysis/*.csv carrying ultimate_cell_economics_csv methodology that was later corrected). Cleaning up component 1 without component 2 leaves landmines for downstream consumers who read methodology-incorrect data without knowing it is incorrect. Always close both components when resolving methodology drift.
E29. Foundational close-out items can produce findings that close other known unknowns and lessons. Item 10 was framed as "derive entry-time from JSONL," but the closure discovered /tmp/kalshi_fills_history.json which closes F17 (matches.entry_time NULL — server-side has created_time), F9 (POTRYB qty under-reporting — server-side has count_fp), F8 partially (server-side has every fill including settlement-adjacent ones), A26 (taker_side underused — is_taker available at execution level), and F10 (Apr 17-23 fill detection broken locally — server-side has fills regardless). Each foundational close-out should be evaluated for cross-reference closure on other open lessons and unknowns. Items are not isolated.

### Category F — Data integrity

F1. Code-config-data triangulation is essential.
F2. Config drift contaminates retroactive analysis. Per-fill config version tracking required.
F3. Settlement-inclusive metrics on heterogeneous outcomes need careful decomposition.
F4. WS event payloads do not always carry the data their event names suggest. Verify field shapes from docs before designing handlers around assumed payloads.
F5. Column names that sound like they describe one thing (exit_price) may describe another (exit_target_price). Verify what each column actually represents before computing on it.
F6. The bot reconcile path was unconditionally overwriting in-memory Position objects every 60 seconds, corrupting entry_price values. Bug 3 in the Apr 29 session addresses this.
F7. Some games recorded entries and exits wrong, deflating metrics on cells/strategies the operator suspected were strong. Full extent of this corruption is not yet cataloged.
F8. When bot resting sell is unfilled at market close, NO settlement event is logged. Position loss is invisible to log-based P&L. Bug 4 (in progress).
F9. Bot has under-reported fill quantity at least once (POTRYB qty=1 logged, actual=10 — 10x risk model error).
F10. Apr 17 to Apr 23 had 763 cell_match events but 0 entry_filled events — fill detection was broken in that window.
F11. Greeks decomposition analysis flagged as broken (degenerate first-bid bug). Schema is correct (theta_pregame_per_min, theta_early_match_per_min, gamma_avg_excursion_pct, realized_vega, scalp-phase distribution); numbers are not yet trusted.
F12. Pre-March data exists locally only as historical_events summaries. Tick-level data for Jan 2 - Mar 19 is not on the VPS. Backfillable from Kalshi candlesticks API if needed but not currently pulled.
F13. Multi-source data integrity requires per-field validity checks. The bookmaker_odds table has player1 field showing '?' literal placeholders in sampled rows, suggesting join failures during scrape. Before using bookmaker_odds (or any scraped/backfilled source) for analysis, verify how many rows have valid values in the columns that matter.

F14. The matches table backfill rows have timestamp issues (settlement_time earlier than entry_time, negative time_to_settle_min in samples). Reinforces F7: backfill data is reconstructed and has known errors. Always treat source='backfill' rows in matches as lower-fidelity than source='live' or source='live_log'.

F15. book_prices is the canonical sharp-consensus source. 3M rows with explicit book_key (pinnacle, gtbets, etc.) and per-event FV cents derived from raw odds with vig stripped, plus polled_at timestamp. bookmaker_odds is a separate table that looks similar but is partially populated junk-drawer data: '?' literal placeholders in player1/player2 fields, no bookmaker provenance column, NULL kalshi_price and edge_pct in samples. Use book_prices for sharp consensus analysis; do not use bookmaker_odds.
F16. Timestamp timezone is not uniform across our data sources. Three conventions present: ET (A-tier ts_et columns explicit, JSONL ts field with literal ET suffix), UTC (historical_events first_ts/last_ts and any commence_time field with ISO Z suffix), and naive (no tz indicator, likely ET via VPS system clock but UNVERIFIED for bbo_log_v4 timestamp, book_prices polled_at, kalshi_price_snapshots polled_at, live_scores last_updated). Always verify timestamp tz before joining sources or computing time deltas. Naive timestamps from the same writer process may all be ET but cannot be assumed without code inspection. Operationally we work in ET; UTC sources require conversion before they are joined to ET sources. Off-by-N-hours is a class of bug to actively prevent.

F17. [REFINED — see A30] The matches table entry_time column is NULL on every live and live_log row sampled. Only source='backfill' rows have entry_time populated, and per F14 those values are unreliable (settlement_time earlier than entry_time in samples). For analyzing the 977 real fills' entry timing (Channel 1 vs Channel 2 split, Window A vs Window B distribution, time-to-exit), the matches table's entry_time column is unusable. Entry timing must be derived from JSONL logs (live_v3_*.jsonl ts field is ET-verified) or cross-referenced via cell_match events. Any analysis that assumed matches.entry_time was populated needs re-derivation.

F18. The matches table settlement_time column has two different writers producing two different formats. Live and live_log rows show naive format (e.g., '2026-04-02 22:01:44'). Backfill rows show ISO format with no Z (e.g., '2026-02-05T15:03:14'). Indicates separate write paths in the bot's history with no schema enforcement. Mixing these without per-row format detection produces silent errors. Treat matches.settlement_time as requiring per-row tz/format inference based on the source column.
F19. Bias reconciliation work is fragmented across 6+ files (entry_price_bias.csv, entry_price_bias.run1.csv, bias_by_cell_from_matches.csv, real_per_fill_check.csv, per_fill_first_price_lookup.csv, real_per_fill.csv). The "operator memory says +21-37c bias, canonical file shows max 10.6c" discrepancy in LESSONS Section 6 known unknowns is consistent with this fragmentation. Before reconciling bias values: inventory what each file measures (which mid: T-15m vs T-1h vs T-2h vs T-4h; which baseline: first_mid vs first_bid vs first_price), then pick canonical. Multiple bias files measuring different things will not reconcile because they are not measuring the same thing.
F20. Same writer, two timezone conventions on different columns. The te_live.py script writes live_scores.last_updated as ET (Python datetime, naive, system tz America/New_York) but writes players.last_updated as UTC (SQLite date('now') returns UTC by default). Same file, same writer process, two columns, two tz conventions. This is exactly the F16-class bug at finer granularity. Lesson: do not assume tz uniformity within a single writer. SQLite date('now') and datetime('now') always return UTC; Python datetime.now() with no arg returns system local. Mixing these in the same script silently produces mixed-tz columns. When auditing tz, audit per-column not per-writer.
F21. /tmp/bbo_aw1.csv and /tmp/bbo_aw2.csv are a separate paired-snapshot measurement framework, not duplicates or alternative implementations of the canonical bias file (entry_price_bias.csv). They measure premarket-to-late drift per ticker (paired observations, first observed BBO vs later observed BBO including settlement-adjacent terminal states bid=0/ask=100). Schema is 7 columns: ticker, ts1, bid1, ask1, ts2, bid2, ask2. Coverage: aw1 = March 5-9 2026 (epoch ts, 364 tickers); aw2 = Mar 20 - Apr 10 2026 (human-readable ts, 1,259 tickers). Zero ticker overlap between the two. Two different timestamp formats indicate two writer runs with no consistent convention; producer code was not preserved. entry_price_bias.csv measures pregame-window bias (first_mid vs T-15m/T-1h/T-2h/T-4h). aw1/aw2 measures something else: full-trajectory drift including post-match. They are COMPLEMENTARY measurements, not redundant. Do not merge them under "bias files" in canonical-designation work; treat as distinct measurement frameworks.
F22. entry_price_bias.csv (per-ticker, B-tier-derived) and entry_price_bias_by_cell.csv (per-cell aggregate) are canonical pregame-window bias measurement for the Mar 20 - Apr 17 period. Producer scripts: /tmp/bias_from_bbo.py, /tmp/bias_check.py, /tmp/bias_check2.py. Schema captures first_mid/first_bid vs T-15m/T-1h/T-2h/T-4h pre-match windows. The .run1 versions of these files are EXACT MD5 DUPLICATES of the primary files (verified) — redundant cached output, not different measurements; can be ignored or deleted. Real samples show per-ticker biases up to -28c/-40c, per-cell stddev ~30c, per-cell median ~10c. Aggregate-level interpretation differs sharply from per-ticker-level interpretation; specify which level when citing values.

F23. The bot-fill vs historical_events.first_price bias framework is fundamentally limited by C-tier coverage (Jan 2 - Apr 10). Files in this framework — bias_by_cell_from_matches.csv (36 usable rows), per_fill_first_price_lookup.csv (131 rows mostly with in_historical_events=NO), real_per_fill_check.csv — cannot serve as canonical bias for the 977-fill window because most fills are post-Apr-10 and historical_events does not cover that range. The framework is structurally broken for the analysis window we care about, not because of a bug, but because of date-range mismatch between source and target. For post-Apr-10 fills, bias must be measured against A-tier premarket_ticks first-observed BBO, which is a separate framework that does not yet exist (per A28).
F24. Kalshi ticker regex assumptions undercount events. The tier-counter regex assumed 6-letter pair codes in tickers like KXATPMATCH-26APR20{6_LETTER_PAIR}-{SIDE}, but at least 24 A-tier filenames use 5-letter pair codes (e.g., KXATPCHALLENGERMATCH-26APR20LAOST-OST.csv with "LAOST" as a 5-letter pair). Likely a "LA" qualifier prefix or special-round case. Pattern is not strictly 6-letter. Any analysis using regex-based ticker parsing must widen the pair-code character class to {5,7} or longer, or count will undercount by the unparsed-filenames bucket. The 854 A-tier match count is therefore a floor, not a ceiling — true count likely 866-878.
F25. /tmp/harmonized_analysis/*.csv outputs were produced by ultimate_cell_economics_csv.py on Apr 28 12:24, whose methodology was SUPERSEDED 55 minutes later by corrected_cell_economics.py (introduced Sw/Sl decomposition implementing A8). The corrected methodology writes to /tmp/corrected_analysis/. Files in /tmp/harmonized_analysis/ carry methodology-incorrect data. Deprecation marker DEPRECATED_USE_corrected_analysis.txt placed in that directory. Files retained on disk for forensic reference only; do NOT consume for analysis. Canonical cell economics methodology: corrected_cell_economics.py. Canonical portfolio optimization: validate_and_optimize.py.
F26. /tmp/scanner_pendulum.log referenced in LESSONS Section 4 does not exist on disk. Confirmed via filesystem-wide find. The reference was either stale (file rotated/deleted from /tmp) or wrong from inception. Same class as D9 (confident characterization without verification produces silent misinformation). LESSONS Section 4 reference to scanner_pendulum.log must be removed in next doc-cleanup pass; tennis_v5.log (Apr 10-17 ET, 6.77 MB, bracketed text format with PREGAME_FILL/DCA_FILL/ENTRY_FULL/TAKER_FILLED tags) is the legitimate text-format legacy bot log.

F27. /tmp is ephemeral on this VPS. Logs and analysis outputs written to /tmp without rotation to durable storage WILL be lost over time. Files committed to git or copied to /root/Omi-Workspace/tmp/ (curated archive per item 5 closure) are durable. Bare /tmp files are not. Older log files cited in any session-state document must be re-verified to still exist before being treated as canonical. When designating a /tmp path as canonical for any analysis (e.g., kalshi_fills_history.json per A32), the operational risk is real — schedule periodic re-pulls or copy to durable storage.
F28. A bug can have separate analytical and operational impacts that resolve independently. Bug 4 (settlement event detection) has two distinct impacts: (1) ANALYTICAL — log-based P&L underreports settlement losses because BBO threshold heuristic fails to fire when WS book stops updating; (2) OPERATIONAL — phantom-active positions hold resting exit orders past settlement, pollute n_active counts, may cause duplicate-entry attempts. The analytical impact is now mitigated by /tmp/kalshi_fills_history.json (per A30) which gives ground-truth fills regardless of bot-side detection. The operational impact remains and requires actual code per bug4_brief.md v3. When evaluating bug priority: separate the analytical and operational dimensions and check whether each is independently mitigated by other work.

### Category G — Operator-relationship signals

G1. Operator pushes back hard when Claude reports raw $ instead of cost-basis %.
G2. Operator pushes back hard when Claude summarizes instead of showing raw data.
G3. Operator pushes back hard when Claude makes assumptions Druid has previously corrected.
G4. Operator pushes back hard when Claude jumps to conclusions on small N.
G5. Operator pushes back hard when Claude proposes deploys without verification.
G6. Operator pushes back hard when Claude misses obvious checkpoints that should have been internal.
G7. Operator pushes back hard when Claude defaults to defensive framing when offensive is warranted.
G8. Operator pushes back hard when Claude treats live small-sample data as definitive.
G9. Operator pushes back hard when Claude bundles two prompts in one response.
G10. Operator pushes back hard when Claude proposes config changes without reading the config file.
G11. Operator pushes back hard when Claude claims memory of conclusions without checking the source.
G12. Operator pushes back hard when Claude generates plausible-sounding frameworks instead of stopping to ask.
G13. Druid is consistently right when pushing back. Treat any disagreement as Druid having insight Claude is missing.
G14. Operator wants Claude to do the verification work, not ask Druid to be a search engine. CC and GitHub are the authoritative sources; do not ask Druid to recall things that are queryable.
G15. Operator wants copy-paste-ready CC prompts in fenced blocks, not narrated commands. Format: first line "Read-only.", then ssh command, then commands, then literal phrase indicating end of CC instructions.
G16. When operator asks a clarifying question that surfaces an analytical gap, that gap likely points at a real lesson to add. Operator question "you ever think about what the gap of understanding currently is?" was the prompt that surfaced A22 (measurement universe is not bid/ask/spread). Future Claude sessions should treat operator clarifying questions as diagnostic of missing framework, not just as requests for clarification.

### Superseded
- A19 (original from session 3, Apr 30): "Entry mechanism defines what swings are capturable. Premarket-only capture." Replaced by E16 (the bot captures in-game spikes via passive resting sells; premarket scalping is 4.7% of mechanism).
- A27 (initial framing, Apr 30): asserted scorecard files were fragmented without canonical source-of-truth. Closer probe revealed the 8 scorecard files answer 8 distinct questions with structurally-justified cell-coverage overlap. PARTIALLY SUPERSEDED by A29 (per-question canonical designation pattern). A27 still applies to the producer-script methodology drift in the "ultimate cell economics" cluster (E27); does not apply to the output scorecard files.

---

## SECTION 6: KNOWN UNKNOWNS (open questions blocking strategic decisions)

- Magnitude and distribution of data corruption in the 977-fill matches table records. Which fills are accurate vs corrupted, and by how much.
- Right cell definition. Current scheme is tier times side times 5c price band. Open: is 5c the right granularity, is direction redundant with price, should tier be primary or secondary partition.
- Per-cell average bounce, decomposed by Channel 1 vs Channel 2, measured cleanly on uncorrupted data.
- Per-cell bilateral double-cash rate (extends April 14 finding from category-level to cell-level).
- Bias correction reconciliation. Canonical bias file vs run1 vs operator memory disagreement. The +21-37c bias bullet from earlier does not reproduce in canonical file (max absolute bias there is 10.6c).
- 30 UNCALIBRATED cells in the rebuild scorecard: edge, no edge, or insufficient data? [COUNT VERIFIED Apr 30 2026: 30/67 = 44.8% of cells classified UNCALIBRATED. Other mechanisms: SCALPER_EDGE=15, SCALPER_BREAK_EVEN=10, SCALPER_NEGATIVE=6, MIXED_BREAK_EVEN=3, SETTLEMENT_RIDE_CONTAMINATED=3. Open question reframed: does re-running classification with corrected methodology (canonical bias per F22, scalp-achievable constraint per A9) reduce UNCALIBRATED count or move cells into known-mechanism buckets?]
- Bug 4 (settlement event detection): until fixed, all log-based P&L underreports settlement losses.
- 58 still-resting Apr 24 to Apr 29 positions: outcomes unknown until they exit or settle.
- Inverse-cell cross-check on real data: never run — does Cell X bouncing +5c correlate with its inverse cell dipping ~minus 5c at the same moment?
- The Apr 24 retune isolation problem: 14 cell disables + 8 exit retunes + 12 code changes simultaneously. Cannot determine which intervention drove subsequent improvement.
- arb-executor-v2/ directory: parallel rebuild branch from Apr 24, contents not yet inventoried.
- /tmp/bbo_aw1.csv and /tmp/bbo_aw2.csv: "first observed vs late-game" BBO snapshot pairs, likely the source for bias correction. Not yet diffed against canonical bias file.

---

## SECTION 7: PROTOCOLS

### How new chats should start
1. Read this file.
2. Confirm with operator what session goal is before doing anything.
3. Do not propose tactical work (config changes, deploys, sweeps) until Section 1 framing is internalized.
4. Ask CC to verify any factual claim about data/code before reasoning on it.

### How CC sessions should start
A new CC session has no chat memory. Future chats should bootstrap CC by pointing at the GitHub raw URL of this file.

### CC prompt format (operator preference, G15)
First line is the literal phrase "Read-only." (period included). Second blank line. Third line is the ssh command to root at the VPS IP. Then the commands. The final line is a literal phrase that signals the end of CC instructions — operator uses "Stop there." period included. When this format example needs to appear inside written content (like this doc), describe it in prose rather than as a literal block, because heredoc and multi-line write tools may parse the literal end phrase as a stop signal and truncate the write.

### When new lessons land in conversation
1. Categorize (A through G).
2. Next index in that category.
3. Write to this file at end of session, OR mid-session for batch updates.
4. Commit to git with meaningful message.
5. Lessons that supersede earlier lessons get marked as SUPERSEDED with a pointer to the replacement; never delete.

### When things spin out
Re-read Section 1. If we are drifting tactical, the foundation is not trustworthy yet. Pause and re-anchor.

### Communication style (from operator preferences)
- Direct, high-urgency, technically precise.
- Push back when wrong; operator is consistently right when pushing back (G13).
- ROI on cost basis, not raw dollars (G1).
- Per-cell math, not aggregates (A4).
- All times ET; full player names always.
- One CC prompt at a time, not bundled (C1, C9).

---

## SECTION 8: CHANGELOG

- 2026-04-30: Initial creation. Session 4 (Druid + Claude). Consolidated handoff doc lessons (A1-A18, B1-B10, C1-C11, D1-D5, E1-E11, F1-F6, G1-G13) plus session 4 additions (A19-A21, C12-C13, D6, E12-E22, F7-F11, G14-G15). Total: 98 lessons across 7 categories. (Math correction: A=21, B=10, C=13, D=6, E=22, F=11, G=15.)
- 2026-04-30 (later same day): Session 4 mid-session additions: A22-A23 (measurement universe, undersampled sources), E23-E24 (formal tier definition, 70.7% as aggregate-not-cell), F12 (pre-March data limits), G16 (clarifying questions as diagnostic). Total: 104 lessons. (Updated counts: A=23, B=10, C=13, D=6, E=24, F=12, G=16.)
- 2026-04-30 (later same day, taxonomy framing): A24 (variable inventory as foundation), E25 (70.7% reclassified as depth-0 existence proof not edge validation), E26 (depth and variable inventory are parallel axes). Total: 107 lessons. (Updated counts: A=24, B=10, C=13, D=6, E=26, F=12, G=16.)
- 2026-04-30 (variable inventory probe results, fully landed): A25 (live_scores final-outcome only despite suggestive schema), A26 (trade CSVs have taker_side), D7 (schema vs populated reality), D8 (verify on-disk state before drafting additive changes), F13 (multi-source per-field validity check), F14 (matches backfill timestamp errors), F15 (book_prices is canonical sharp-consensus source not bookmaker_odds). Total: 114 lessons. (Updated counts: A=26, B=10, C=13, D=8, E=26, F=15, G=16.)
- 2026-04-30 (timezone probe results): F16 (three tz conventions across sources, verify before joining), F17 (matches.entry_time NULL on live rows; derive from JSONL), F18 (matches.settlement_time has two writers with different formats). Total: 117 lessons. (Updated counts: A=26, B=10, C=13, D=8, E=26, F=18, G=16.)
- 2026-04-30 (depth-inventory probe results): A27 (D1/D2 analyses fragmented without canonical source), C14 (analysis output paths should be canonical or versioned), E27 (D5 has methodology drift across multiple "ultimate" implementations), F19 (bias reconciliation fragmented across 6+ files). Total: 121 lessons. (Updated counts: A=27, B=10, C=14, D=8, E=27, F=19, G=16.)
- 2026-04-30 (TZ final verification): F20 (same writer, two tz conventions on different columns — te_live.py writes live_scores.last_updated ET but players.last_updated UTC). Total: 122 lessons. (Updated counts: A=27, B=10, C=14, D=8, E=27, F=20, G=16.)
- 2026-04-30 (executor_core probe / item 3 close): C15 (legacy code paths remain searchable, must be excluded from grep when probing active tennis stack). Total: 123 lessons. (Updated counts: A=27, B=10, C=15, D=8, E=27, F=20, G=16.)
- 2026-04-30 (item 5 closure / snapshot dir investigation): D9 (confident characterization without verification produces silent misinformation — caught when /root/Omi-Workspace/tmp/ turned out to be multi-batch curated archive, not single snapshot). Total: 124 lessons. (Updated counts: A=27, B=10, C=15, D=9, E=27, F=20, G=16.)
- 2026-04-30 (item 6 closure / bbo_aw1+aw2 inventory): F21 (aw1/aw2 are paired-snapshot drift measurement, distinct from entry_price_bias canonical bias file; complementary not redundant). Total: 125 lessons. (Updated counts: A=27, B=10, C=15, D=9, E=27, F=21, G=16.)
- 2026-04-30 (item 7 closure / canonical bias designation): A28 (bias measurement requires tier-appropriate baseline; 3 implementations needed across pre-Mar-20 / Mar 20-Apr 17 / Apr 18+), B11 (discrepancies may be aggregation-level differences not contradictions), F22 (entry_price_bias canonical for B-tier era; .run1 files are exact MD5 duplicates), F23 (historical_events bias framework structurally broken for post-Apr-10 due to C-tier coverage limit). Total: 129 lessons. (Updated counts: A=28, B=11, C=15, D=9, E=27, F=23, G=16.)
- 2026-04-30 (TAXONOMY A-tier partial-populate + F24): F24 (regex undercount on 5-letter pair codes; A-tier 854 is floor not ceiling). Total: 130 lessons. (Updated counts: A=28, B=11, C=15, D=9, E=27, F=24, G=16.)
- 2026-04-30 (item 8 closure / canonical scorecard designation): A29 (per-question canonical designation pattern; scorecard cluster is not fragmentation), B12 (derived columns may be redundant flags), A27 partially superseded, UNCALIBRATED count verified 30/67. Total: 132 lessons. (Updated counts: A=29, B=12, C=15, D=9, E=27, F=24, G=16.)
- 2026-04-30 (chat-side pattern lesson): D10 (chat-drafted lesson numbers drift from on-disk numbers after Path 1 renames; three off-by-one events in Session 4; draft from on-disk state, not chat history). Total: 133 lessons. (Updated counts: A=29, B=12, C=15, D=10, E=27, F=24, G=16.)
- 2026-04-30 (item 9 closure / canonical ultimate cell economics): C16 (methodology-correction commits should mark prior outputs), E28 (methodology drift has 2 components: producer + residual outputs), F25 (/tmp/harmonized_analysis/ outputs are methodology-incorrect; deprecation marker placed; corrected_cell_economics.py canonical, validate_and_optimize.py portfolio canonical). Total: 136 lessons. (Updated counts: A=29, B=12, C=16, D=10, E=28, F=25, G=16.)
- 2026-04-30 (item 10 closure / kalshi_fills_history.json discovered): A30 (server-side fill history canonical; closes F17/F9/F8/A26/F10), E29 (foundational close-outs cross-reference other lessons), F26 (scanner_pendulum.log does not exist), F27 (/tmp is ephemeral); F17 marked [REFINED]. Total: 140 lessons. (Counts: A=30, B=12, C=16, D=10, E=29, F=27, G=16.)
- 2026-04-30 (T11 closure / Bug 4 status): F28 (a bug can have separate analytical and operational impacts; Bug 4 analytical impact mitigated by T10 / kalshi_fills_history.json, operational impact remains). Total: 141 lessons. (Counts: A=30, B=12, C=16, D=10, E=29, F=28, G=16.)
