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

### Category D — Memory / context discipline

D1. Compaction summaries lose strategic framing while preserving tactical bullets. When operator references "what we concluded," check the actual conversation, not the summary.
D2. Memory bullets describing concepts ("scalping AND inversion cells are BOTH a thing") are not the same as conclusions about which cells fall into which category. The lens is not the verdict.
D3. Memory bullets describing scorecards by counts ("11 confirmed SCALPER_EDGE, 4 bleed, 30 UNCALIBRATED") may be summary-of-summary, not ground truth. Verify against the actual artifact before designing analysis around the asserted shape.
D4. When operator pushes back, do not generate another plausible-sounding framework. Stop. Ask. Re-anchor. Pattern-matched fabrication compounds.
D5. Diligence means thinking through the response shape and what could be missing BEFORE the response lands, not after.
D6. This LESSONS.md is the durable memory. Future chats start by reading this file. Do not reinvent context the file already has.

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

### Superseded
- A19 (original from session 3, Apr 30): "Entry mechanism defines what swings are capturable. Premarket-only capture." Replaced by E16 (the bot captures in-game spikes via passive resting sells; premarket scalping is 4.7% of mechanism).

---

## SECTION 6: KNOWN UNKNOWNS (open questions blocking strategic decisions)

- Magnitude and distribution of data corruption in the 977-fill matches table records. Which fills are accurate vs corrupted, and by how much.
- Right cell definition. Current scheme is tier times side times 5c price band. Open: is 5c the right granularity, is direction redundant with price, should tier be primary or secondary partition.
- Per-cell average bounce, decomposed by Channel 1 vs Channel 2, measured cleanly on uncorrupted data.
- Per-cell bilateral double-cash rate (extends April 14 finding from category-level to cell-level).
- Bias correction reconciliation. Canonical bias file vs run1 vs operator memory disagreement. The +21-37c bias bullet from earlier does not reproduce in canonical file (max absolute bias there is 10.6c).
- 30 UNCALIBRATED cells in the rebuild scorecard: edge, no edge, or insufficient data?
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
