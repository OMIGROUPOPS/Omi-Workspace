# OMI Roadmap — Categorized Tracking System

**Purpose:** Source of truth for current operational state of the OMI tennis trading operation. Append-only categorized indexed tracking, same model as LESSONS.md. Future chats consult this to know what is open, what needs attention, what is unknown, what is missing, and what is awaiting authorization.

**Categories:**
- **T (To-Do):** actionable items with a clear close condition. Status: OPEN / IN_PROGRESS / CLOSED.
- **F (Flag):** operational risks or attention items that are not yet actionable, or are ongoing concerns to track.
- **U (Unknown):** open questions blocking strategic decisions.
- **G (Gap):** work that does not yet exist but should.
- **D (Decision):** items awaiting operator authorization or operational call.

Same rules as LESSONS.md: append-only with indexed numbering. Closed items get a CLOSED tag, date, and pointer to the resolution; never delete. Superseded items get a SUPERSEDED tag and a pointer to the replacement.

**Cross-references:**
- Foundational framing: LESSONS.md Section 1.
- Classification language: TAXONOMY.md.
- Prior work: ANALYSIS_LIBRARY.md.

**Last updated:** 2026-04-30 (Session 4, mid-session foundational close-out).

---

## SECTION 1: PHASE

**Current phase: Foundational, not tactical.** Per LESSONS.md Section 1.

We are not optimizing config. We are not picking cells to enable. We are rebuilding our ability to trust per-cell metrics. Within the foundational phase, the current sub-phase is: **closing every outstanding foundational item before running any analysis.**

T1-T12 (the foundational close-out list) are the gating items. Most are CLOSED as of this commit; T11, T12 remain OPEN.

---

## SECTION 2: T (TO-DO) — actionable items with close condition

T1. ROADMAP refresh — initial scaffolded version. **CLOSED 2026-04-30 (commit c794b26).** Replaced by this restructure (T16 placeholder for self).

T2. Tier-counter completion. Started Apr 30 12:03 PM ET, populates TAXONOMY Section 1 match counts. **PARTIALLY CLOSED 2026-04-30:** A-tier landed (854 events; commit 1084503). B-tier failed mid-stream with OOM after ~3hrs; C-tier did not run. See T13.

T3. executor_core.py write target verification. **CLOSED 2026-04-30 (commit 58de738):** legacy cross-platform arb code, writes to JSON state files not DB columns, no tennis-stack TZ impact. Ref C15.

T4. arb-executor-v2/ directory inventory. **CLOSED 2026-04-30 (commit 58de738):** 30 Python files, zero tennis content, fresh checkout of legacy cross-platform arb code, out of scope per E19.

T5. Snapshot dir investigation (/root/Omi-Workspace/tmp/). **CLOSED 2026-04-30 (commit 596aaf2):** curated git-tracked archive with multiple curation batches across multiple dates, NOT a single Apr 29 17:43 snapshot. ANALYSIS_LIBRARY corrected. Ref D9.

T6. /tmp/bbo_aw1.csv and /tmp/bbo_aw2.csv inventory. **CLOSED 2026-04-30 (commit c791c46):** paired-snapshot drift measurement framework, distinct from entry_price_bias canonical, complementary not redundant. Ref F21.

T7. Canonical bias file designation. **CLOSED 2026-04-30 (commit 7d7b7fd):** entry_price_bias.csv canonical for B-tier era (Mar 20 - Apr 17). bias_by_cell_from_matches.csv structurally broken post-Apr-10 due to historical_events C-tier coverage limit. Pre-Mar-20 bias and Apr 18+ bias both require separate tier-appropriate implementations (per A28). +21-37c vs 10.6c "discrepancy" was level-of-aggregation difference, not contradiction. Ref A28, B11, F22, F23.

T8. Canonical scorecard designation. **CLOSED 2026-04-30 (commit 82809ad):** 8 scorecard files answer 8 distinct questions, per-question canonical-designation table is the artifact (not pick-one-and-retire-others). Original A28 framing of "fragmentation" partially superseded by A29. UNCALIBRATED count verified 30/67. Ref A29, B12.

T9. Canonical "ultimate cell economics" designation. **CLOSED 2026-04-30 (commit de3e6a3):** 4 producer scripts in iteration sequence on Apr 28, with corrected_cell_economics.py methodology canonical (Sw/Sl decomposition). validate_and_optimize.py canonical for portfolio optimization. ultimate_cell_economics.py and ultimate_cell_economics_csv.py SUPERSEDED. /tmp/harmonized_analysis/ outputs carry methodology-incorrect data; deprecation marker placed. Ref C16, E28, F25.

T10. Entry-time derivation. **CLOSED 2026-04-30 (commit ae685e9 + 952da9c):** /tmp/kalshi_fills_history.json discovered as Tier-A fact source (7,489 server-side fills, Mar 1 - Apr 29). Closes F17/F9/F8/A26/F10 partially-or-fully. Original framing of "derive from JSONL" wrong (live_v3 only covers Apr 24+); kalshi_fills_history.json is the canonical entry-time source. Ref A30, E29, F26, F27.

T11. Bug 4 (settlement event detection) status check. **CLOSED 2026-04-30:** probe completed — Bug 4 is fully designed (bug4_brief.md v3 + bug4_probe.md, both Apr 29) but ZERO implementation code has been written. Brief explicitly states "investigation complete, design proposed, no code written." Frequency from log analysis: 8 of 130 entry_filled positions are PHANTOM-ACTIVE (6%); 17% of non-exit-fill positions slip past the BBO heuristic. Split into T11a (implementation work) and T11b (sandbox test). Analytical impact MITIGATED by T10 closure (kalshi_fills_history.json). Operational impact remains open per T11a. Decision on prioritization tracked at D6.

T11a. Bug 4 implementation. **OPEN.** Write code per bug4_brief.md v3: WS "market_lifecycle_v2" handler + REST "/portfolio/settlements" poll fallback + partial-exit P&L formula correction + paper-mode gating + persistence verification + test suite B4-T1..T11. Significant work. Operational impact: phantom positions hold resting exit orders past settlement, pollute n_active counts, may cause duplicate-entry attempts. Mitigation precondition: bot is shut down per LESSONS Section 1, so operational bug isn't actively burning state right now.

T11b. Bug 4 sandbox test. **OPEN, depends on T11a partial completion.** Capture real settled event from Kalshi sandbox to validate WS payload schema before production deployment. Probe found settled-event payload is MINIMAL (no market_result or settlement value); REST per-record key is "value" (cents int, nullable), not "settlement_value" as brief originally said. Brief adjustment required.

T12. Security exposures rotation. **AUDITED 2026-04-30, DEFERRED to operator timing.** Comprehensive security audit completed. Findings:
1. GitHub PAT confirmed embedded in /root/Omi-Workspace/.git/config remote URL. Repo is public; assume already harvested.
2. probe_kalshi_api2.py: 0 grep matches for KALSHI_ACCESS_KEY pattern in this specific file (variable name pattern may differ from prior framing; manual eyeball recommended pre-rotation). Treat as exposed regardless.
3. /root/Omi-Workspace/backend/.env IS TRACKED IN GIT despite .gitignore (gitignore only applies to NEW files). Whatever was committed to that file lives in git history forever. Public repo means anything ever in backend/.env is also burnt.
4. /root/Omi-Workspace/arb-executor/kalshi.pem (RSA private key) and arb-executor/fix_key.py (RSA key embedded as string) on disk; both gitignored for new files. Need to verify never historically committed.
5. 14 hardcoded secret-pattern matches across 12 active tennis-stack files (tennis_odds.py, kalshi_reconciler.py, bot_server.py, etc.). Refactor to env-vars eventually.
6. AWS-style keys: zero matches.
7. /tmp has 69 secret-pattern matches across many ephemeral working scripts.

Audit itself created a new exposure: the probe echoed the PAT in its own output, leaking it into chat transcript. See C17 for prevention.

Status: deferred. Exposures don't block analysis (analysis is read-only on data we already have). Operator will rotate at their own timing. Until rotation: keys remain compromised, repo continues operating with embedded PAT, no production trading active so no ongoing financial exposure beyond credential theft. When rotation happens: see D6, D7 for staged playbook.

T13. Tier-counter B-tier OOM-resilient retry. **OPEN.** Replaces the failed portion of T2. Approach: stream tickers to disk (jsonl append) instead of accumulating in-memory set, aggregate post-stream. Output populates TAXONOMY Section 1 B-tier match counts.

T14. Re-pull schedule for kalshi_fills_history.json. **OPEN.** Per F28: file is on /tmp (ephemeral). Source data extends through Apr 29 13:02 UTC; fill history continues to grow. Need: scheduled re-pull (e.g., daily) or copy to durable storage, or both.

T15. ROADMAP restructure — categorized T/F/U/G/D system. **CLOSED 2026-04-30 (this commit).** Replaces flat sections with append-only indexed structure.

T16. CC bootstrap reads LESSONS.md every session. **OPEN.** Currently chat is the only filter applying lessons; CC just executes prompts. Real gap — chat-side filter-failure mode is real risk (Session 4 had three off-by-one drift events on lesson numbers before D10 codified the fix). Three candidate designs: (a) CC reads full LESSONS.md at session start (~70KB context cost every session); (b) chat injects relevant lesson sections inline per prompt (preserves the gap — chat is exactly where failure lives); (c) hybrid — CC reads short LESSONS_QUICKREF.md (~10KB summary of CC-actionable patterns: D10 dynamic numbering, F28 /tmp ephemerality, C17 credential redaction, single-concern commits) at session start, chat injects specific lessons inline as needed. Design choice tracked at D8.

T17. **G9 dataset parquet conversion.** **OPEN.** Convert `arb-executor/data/historical_pull/` (20K CSV + 20K JSON files) to consolidated parquet. Three target outputs: `g9_trades.parquet` (~20M rows: ticker, created_time microsecond, yes_price, no_price, count_fp, taker_side, trade_id), `g9_candles.parquet` (~5M rows: ticker, end_period_ts, OHLC + bid/ask + volume + OI), `g9_metadata.parquet` (~20K rows: full market metadata with category derivation per match_facts_v3 pattern). Estimated ~30-60 min runtime, ~2 GB consolidated output (vs 5 GB raw). Enables groupby-based analysis instead of per-file opens. Blocking for Layer A bounce measurement on G9 dataset.

T18. **Candles semantics probe.** **OPEN.** Verify Kalshi candlestick `yes_bid` / `yes_ask` semantics before T17 parquet conversion locks in flattened schema. Hypothesis: best-bid/best-ask snapshot at open/close/high of period (per ANALYSIS_LIBRARY description language). Alternative: VWAP across period, or other aggregation. Probe shape: pick one high-volume Kalshi market with dense trade tape, compare candle `yes_bid_close` to (a) last bid-side trade in window, (b) VWAP of bid-side trades in window, (c) any other plausible interpretation. ~10 min. Gates T17. If semantics are non-snapshot, every analysis using candle bid/ask is on a noisy quote.

T19. **Layer A v1 specification.** **OPEN.** Per G7 architectural commitment + LESSONS B16 (bounce/exit/returns separation). Layer A is pure bounce per cell, no exit logic, no fill assumptions, no P&L. Operational decisions to make explicit:
  - Bounce definition: MFE only for v1 (max favorable excursion, parameter-free given a forward window). Defer return-to-pre-dip and mean-reversion-to-fair to v2.
  - Forward windows: 2/5/10/30/60/120min + until_settlement. 2/5/30/120 anchored on Stage 0 Probe 7 exit-time distribution; 10/60 fill bounce-decay-curve gaps. Annotate which is which in the output schema.
  - Cell granularity: v1 starts at price decile × TTC quintile × volume-bucket × category. Per LESSONS A31 volume is the primary predictor (33pp swing across volume strata vs 6pp across categories). Per B14/G17 decompose by premarket vs in-match time window — strategy-actionable findings require it. Per B13 check threshold ceiling math before interpreting cliffs.
  - Source: candle close prices only. No trades-candles join in v1 (gated on T18 semantics verification).
  - Cell minimum sample size: N_min (e.g., 100 obs) below which cells collapse to coarser bins.
  Output: `arb-executor/docs/layer_a_spec.md`. Blocks T20.

T20. **Layer A v1 implementation.** **OPEN.** Code per T19 spec. Reads `g9_candles.parquet` + `g9_metadata.parquet` (post-T17). Computes MFE per (ticker, candle_minute) for each forward window. Stratifies by cell. Output: `arb-executor/analysis/layer_a/bounce_distribution_per_cell.parquet` + per-cell summary CSV. Blocks T21.

T21. **Layer A coherence read.** **CLOSED 2026-05-04 (Session 6 Phase 5-ii):** PASS verdict. T21 Phase 2 ran 6 coherence checks against cell_stats.parquet (371 substantial cells, n_markets >= 20). 4 PASS cleanly: Check 2 premarket vs in_match (in_match > premarket in 91% of 112 matched pairs, Wilcoxon p<0.0001, +5c median diff per B14/E31); Check 3 settlement asymmetry (high-entry pin + low-entry crash both confirmed in ATP cells); Check 4 category sanity (MAIN/CHALL liquidity gap 0.11c is 5x ATP/WTA tour gap 0.02c); Check 6 YES/NO fold (57 mirror pairs, median fold diff +0.01c, std 0.03c — strongest single confirmation, see LESSONS A36). 2 INCONCLUSIVE in informative ways: Check 1 (asymptote hypothesis wrong shape — data shows inverted-U centered on 50c, lesson B20 added); Check 5 (volume_intensity collapses to single bucket within in_match per F30). No data integrity bugs surfaced. Layer A v1 foundation methodology validated. Promotes G10 to T31 (Layer B exit-policy parameter sweep).

**Original spec retained for reference:** Sanity checks on T20 output. Methodology validation gate. Checks: Sanity checks on T20 output. Methodology validation gate. Checks:
  - Higher leader-prices have lower bounce magnitudes (asymptote near 100c)?
  - In-match volatility higher than premarket (per B14 decomposition)?
  - Settlement-conditioned reversion present (matches ending at YES=$1 spent significant time above $0.85 in final window)?
  - Per-category differences sensible (ATP main vs Challenger, WTA mirror)?
  - Volume-bucket monotonicity (higher-volume cells should have lower variance per A31)?
  If coherent: continue to G10 (Layer B exit-policy sweep). If incoherent: investigate dataset before further analysis. Possibilities: candles semantics wrong (T18 missed something), cell granularity too fine, MFE definition wrong, hidden upstream-filter in G9 producer. Session 6 success metric.

T22. **TAXONOMY refactor for multi-tier-as-feature framing.** **OPEN.** Per LESSONS E23 the A/B/C tier framework treats data as richer/thinner versions of the same thing. The right framing is multi-tier-as-feature: tiers serve different question classes (per-minute candles → game-state-level analysis; per-tick BBO → microstructure; microsecond trade tape → aggressor flow). G9 introduces a fourth tier: per-minute candles + microsecond trades, retroactively pullable from `/historical/*`, coverage Jun 2025+. TAXONOMY needs the G9 tier explicitly defined and the multi-tier-as-feature framing landed. Prerequisite: read existing TAXONOMY content before reframe (verified Session 6).

T23. **Phase 3 v1 design doc disposition.** **OPEN.** Pending D12. The Phase 3 v1 design doc (`arb-executor/docs/u4_phase3_design.md`, 209 lines) is partially obsolete: Stage 0 findings still valid, 30s cadence retired (see B15/B16), G9 architecture supersedes the bbo_log_v4 source. Three options: (a) rewrite as Phase 3 v2 design doc reflecting native-resolution + G9 architecture, (b) formally retire Phase 3 v1 with a SUPERSEDED tag and pointer, (c) leave as-is with Session 5 architectural learnings appended. Operator decision tracked at D12; this T-item is the implementation work after D12 resolves.

T24. **Per-match visualization tool.** **OPEN, optional.** Templated `plot_match(ticker)` function reproducing the chart format that originally surfaced G9 (Liam's Jun 2025 ticker chart): `yes_bid` / `yes_ask` step functions + trade scatter colored by `taker_side` + taker flow panel + volume panel. Reads from `g9_trades.parquet` + `g9_candles.parquet` post-T17. Sanity-check companion to aggregate Layer A — lets us visually inspect any cell's worth of matches when Layer A surfaces something surprising. Not blocking analysis; valuable for debugging.

T25. **Fair-value model integration scoping.** **OPEN.** Per user-memory, Klaassen-Magnus tennis win probability model exists at `omi-workspace/ESPNData/tennis_scraper.py` (ATP serve f=0.64, WTA f=0.56). Whether output is joined to any market_id is unknown. Prerequisite for Layer A v2 (fair-value-conditioned bounce definitions) and V4 game-state mispricing thesis. Player-identity cross-walk between Kalshi UUIDs (`custom_strike.tennis_competitor`) and ESPN/ATP/WTA player IDs may be its own multi-hour task. 5-min scoping probe before committing to integration work.

T26. **Live trading deployment plan.** **OPEN, far-future tracking.** Path back to live trading requires: Layer A coherence validated (T21 gate), Layer B exit policy chosen (G10), Layer C economics positive (G11), bot architecture updated to consume Phase 3 v2 / G9-derived dataset (not deprecated 30s-cadence pipeline), auth separation so heavy backfill doesn't share rate-limit bucket with live trading (per L2 lesson when added), Bug 4 implementation per T11a if operator prioritizes (D6). Not Session 6 scope; tracked here so the path is explicit and not assumed.

T27. **G9 parquet verification probe.** **OPEN, immediate.** Gate before any Layer A work per LESSONS C27. Verify the T17 producer outputs (g9_candles.parquet, g9_trades.parquet, g9_metadata.parquet) against the source CSVs/JSONs:
- Row count parity: sum of all source CSV rows == parquet row count, per file type
- Schema normalization: zero `_dollars`-suffixed column names survived in candles parquet (per F29)
- Reconstruction equivalence: sample 10 random markets, reconstruct each market's CSV from the parquet, byte-compare against original — must match exactly modulo column ordering
- Era distribution: 2025 vs 2026 split matches what producer log reported during run
- Trade taker_side: all values in {`yes`, `no`}, no nulls
- Metadata custom_strike: JSON-stringified, parses back to dict cleanly
- No NaN columns where era detection went wrong (i.e., a column having all-null in one era and all-populated in the other — would indicate normalize_candle_row missed a key)
Probe runtime ~5-10 min. Output: pass/fail per check + diagnostic detail. If any FAIL, T17 producer needs fix + re-run before T28 proceeds.

T28. **Foundation commit + ANALYSIS_LIBRARY G9 entry.** **OPEN, gated on T27.** Per LESSONS C27 step 2-3:
- Compute sha256 for each of the 3 parquets
- Append to arb-executor/data/durable/MANIFEST.md with parquet checksums + producer commit pin (build_g9_parquets.py at bd83412) + verification commit pin (T27 commit)
- Append G9 parquets entry to ANALYSIS_LIBRARY.md cross-cutting Canonical Sources subsection (or new subsection) with: file paths, producer pointer, verification pointer, schema normalization summary, validity status (verified per T27 commit), date created
- This commit becomes the foundation-commit pointer that all downstream Layer A/B/C entries reference

T29. **Layer A v1 visual producer.** **OPEN, gated on T28.** Per LESSONS C27 step 4-5 + B16 (Layer A separation) + E31 (regime-aware) + B17 (one-sided book filtering) + G18 (candle close fields = BBO snapshots):
- Producer: arb-executor/data/scripts/build_layer_a_visuals.py
- Cell schema: regime (premarket / in_match / settlement_zone via volume-jump heuristic per A35) × entry_price_band (10c bins) × spread_band (tight/medium/wide) × volume_intensity (low/mid/high) × category (ATP_MAIN / ATP_CHALL / WTA_MAIN / WTA_CHALL / other)
- Output: PNG grid per category (4 PNGs total), each PNG showing 6 cells (price-band × spread-band sample) with 30-market trajectory overlays, median + p25/p75 envelopes, regime-boundary marker per market, regime-region tinting
- One-sided-book filter applied per B17; settlement-zone filter applied per G18
- Output dir: arb-executor/data/durable/layer_a_v1_visuals/
- ANALYSIS_LIBRARY entry registers each PNG with: source-foundation pointer (T28 commit), producer pointer (T29 commit), cell parameters, sample size, sample manifest (which tickers were sampled per cell)

T30. **Layer A v1 tabular metrics.** **OPEN, gated on T29 visual review.** Per LESSONS C27 step 6 + B16. After T29 visuals reveal which cells show clean signal, run the tabular metrics producer on those cells specifically (or all cells with sufficient sample size):
- Producer: arb-executor/data/scripts/build_layer_a_v1_metrics.py
- Output: arb-executor/data/durable/layer_a_v1_metrics.parquet — one row per cell with forward-bounce distribution stats (count, mean, median, p25/p50/p75/p90/p95) at horizons {5, 15, 30, 60 min, settlement}, plus drawdown stats, plus breakeven-threshold fractions at {1c, 2c, 5c, 10c, 20c}
- Output measures BOTH yes-side and no-side bounces independently per operator E31 framing (a market that settles YES_WIN can still have a NO-side scalp opportunity)
- ANALYSIS_LIBRARY entry references T28 foundation + T29 visual review + T30 producer commit
- Gates Layer B (T31 future, exit policy optimization)
T31. **Layer B exit-policy parameter sweep.** Per LESSONS B16 + ROADMAP G10 (now promoted from Gap to To-Do per T21 PASS verdict). T21 Phase 2 outcome: 4 of 6 coherence checks PASS cleanly (premarket-vs-in_match, settlement asymmetry, category sanity, YES/NO fold), 2 INCONCLUSIVE in informative ways (Check 1 hypothesis-shape mismatch per LESSONS B20, Check 5 volume_intensity in_match collapse per LESSONS F30). Foundation methodology validated. Layer B can proceed.

Two-channel scope per LESSONS E31: premarket and in_match run as separate sweeps (different fill dynamics, latency tolerances, gross-edge-per-round-trip ratios). Settlement_zone may be its own third channel given the directional asymmetry confirmed in T21 Check 3.

Exit policy parameter space: limit thresholds +1c to +30c at 1c granularity; time-stops at 30s, 1min, 5min, 15min, 30min, 60min, 120min, 240min; trailing-stops at every offset 1-20c; combined policies (limit + time-stop, limit + trailing). For each (cell, exit_policy) tuple, simulate forward across all matching observations in cell_stats reservoir samples, output: expected_capture (mean realized bounce captured), p10/p25/p50/p75/p90 capture, hit rate (fraction of observations where exit fired vs settled), capital utilization.

Substantial-cell scope only (n_markets >= 20, 371 cells per Phase 1 finding). Within in_match regime, drop volume_intensity from cell key (uninformative per F30); use 4-dim key (regime, entry_band, spread, category). Premarket retains 5-dim key.

Output: arb-executor/data/durable/layer_b_v1/exit_policy_per_cell.parquet + per-cell summary visuals. Producer pointer + ANALYSIS_LIBRARY entry per LESSONS C27.

Gates Layer C (G11) realized economics work.

---

## SECTION 3: F (FLAG) — operational risks and attention items


F1. /tmp ephemerality risk. Per LESSONS F28: bare /tmp files can be lost over time without warning. Files currently sitting on /tmp that are canonical sources: kalshi_fills_history.json (per A30), bbo_log_v4.csv.gz (B-tier), entry_price_bias.csv cluster, bbo_aw1/aw2, harmonized_analysis/ deprecated outputs. Mitigation tracked at T14 for kalshi_fills_history; broader durability migration not yet planned.

**PARTIAL CLOSURE 2026-05-04 (Session 6 Phase 1B/1C):** Canonical /tmp sources now durable-copied: kalshi_fills_history.json, bbo_log_v4.csv.gz, entry_price_bias cluster, match_facts_v3_metadata.csv, u4_phase3_state_pass1.parquet (durable archive at arb-executor/data/durable/, sha256-verified, MANIFEST.md). bbo_aw1/aw2 + harmonized_analysis outputs preserved durably under tmp/ (Phase 1C). Remaining /tmp ephemerality risks: ongoing growth files (e.g., fv_convergence_monitor.csv if present, future kalshi_fills_history.json refreshes per T14). New batch-fragmentation flags surfaced: F11 (per_cell_verification), F12 (harmonized_analysis).

F2. /tmp/harmonized_analysis/ outputs retained on disk. Per LESSONS F25: methodology-incorrect data, deprecation marker placed but actual files not deleted. Future readers may consume them despite the marker. Mitigation: depends on D1 (deletion authorization).

F3. Stale references in LESSONS Section 4. Per LESSONS F27: scanner_pendulum.log cited as legacy bot log but does not exist on disk. Reference must be removed in next doc-cleanup pass. Other LESSONS Section 4 entries should also be re-verified given /tmp ephemerality (F1).

F4. Apr 17 - Apr 23 fill detection broken locally. Per LESSONS F10/F26: live_v3 JSONL had 0 entry_filled events in this 6-day window despite 393MB of log content (763 cell_match events, 0 entry_filled). Now partially mitigated by T10 closure (kalshi_fills_history.json has server-side fills regardless). But: the local-bot-state for what the bot DECIDED to enter is preserved; the local fill confirmations were lost. For analyses that need both decision intent AND execution, the join is fragile in this window.

F5. bookmaker_odds table is junk-drawer per LESSONS F15. Player1/player2 fields '?' in samples, kalshi_ticker/kalshi_price/edge_pct NULL in samples. Use book_prices for sharp consensus. F15 implies "do not use bookmaker_odds" but the table still exists; if any future code accidentally reads it, results will be invalid.

F6. live_scores table has only final set scores per A25/A27. Schema columns p1_games/p2_games suggest per-game state but are empty in samples. For Channel 2 game-event attribution work (currently blocked, see U7), live_scores is insufficient.

F7. matches.entry_time NULL on every live/live_log row per F17. Even with T10 closed and kalshi_fills_history.json canonical, the matches table itself remains broken on this column. Any code that joins to matches.entry_time should be flagged.

F8. matches.settlement_time has two writers per F18. Live rows naive ET, backfill rows ISO no-Z. Per-row format detection required. Future joins on this column are fragile.

F9. players.last_updated is UTC via SQLite date('now') per F20, while every other te_live.py-written column is ET. Same-writer-different-tz outlier. If any cross-table join uses players.last_updated as if ET, results are wrong by N hours.

F10. Path 1 lesson-number renames. Three off-by-one drift events occurred in Session 4. D10 added to mitigate; subsequent commits used dynamic on-disk number reads which worked. Still a flag because future Claude sessions need to internalize the pattern.

F11. **per_cell_verification batch fragmentation.** Two batches preserved durably (Phase 1C-vi), neither designated canonical for downstream consumption. Batch A: /tmp/per_cell_verification/ Apr 28 mtimes (33 files, preserved at /root/Omi-Workspace/tmp/per_cell_verification_tmp_apr28/ per Phase 1C-vi). Batch B: archive Apr 29 17:43 curation batch (30 files, in /root/Omi-Workspace/tmp/per_cell_verification/, predating Session 6). 28 of 30 same-named files have DIFFERENT sha256 hashes between batches. Hypothesis: Batch B is re-derived methodology run, not /tmp file copy. Resolving which batch is canonical for which question deferred to U10 + D9. Forward analysis must be batch-aware.

F12. **harmonized_analysis batch fragmentation.** Similar finding to F11. Two batches: /tmp/harmonized_analysis/ and archive /root/Omi-Workspace/tmp/harmonized_analysis/. Both methodology-incorrect per F25 (T9 closure). Mtime difference and sha256 mismatch on overlapping files suggest two methodology-incorrect runs, not one canonical preserved copy. Both preserved durably; neither designated canonical. Resolution at D10 (probably "leave both, no canonical, do not consume" per F25 deprecation marker).
F13. cell_stats.parquet does not preserve event_ticker. Per LESSONS B19. Cells are aggregates across many markets keyed on (regime, entry_band, spread, volume, category); per-event pairing key is not a column. Per-event analyses (U8 inverse-cell cross-check, E18 bilateral capture, future game-state attribution) cannot be answered from this artifact and require a different per-moment dataset with event_ticker preserved (see G12). The pairing convention is trivial at source level: event_ticker = ticker.rsplit("-", 1)[0]. Future analytical layers must compute from g9_trades + g9_candles + g9_metadata directly when per-event pairing is required.

---

## SECTION 4: U (UNKNOWN) — open questions blocking strategic decisions

U1. Magnitude and distribution of data corruption in matches table records. Per LESSONS Section 6 known unknown #1. Partially expanded by F7 (entry_time NULL), F8 (settlement_time two writers), F17, F18. Full magnitude still unmeasured. T10 closure provides a cleaner alternative source (kalshi_fills_history.json) so this unknown becomes lower priority for forward analysis.

U2. Right cell definition. Per LESSONS Section 6 known unknown #2. Current scheme is tier × side × 5c price band. Open: is 5c the right granularity, is direction redundant with price, should tier be primary or secondary partition. Strategic question, not foundational; deferred until foundation complete.

U3. Per-cell average bounce decomposed by Channel 1 vs Channel 2 on uncorrupted data. Per LESSONS Section 6 known unknown #3. Analysis target.

U4. Per-cell bilateral double-cash rate. Per LESSONS E18/E21/E22. Extends April 14 paired analysis. **PARTIALLY ANALYZED 2026-04-30 (Session 4):** U4 Phase 1 characterized 5,879-match landscape; U4 Phase 2 stratified 3,936-match synchronized subset by 7 dimensions. Volume is canonical predictor: 33pp swing across volume strata (50-99 trades = 34.3% bilateral capture at +10c; 1000+ trades = 76.4%). Categories track within 6pp (ATP_CHALL=63.1%, ATP_MAIN=63.5%, WTA_MAIN=64.3%, WTA_CHALL=56.8%). Skew >35 cliff partially ceiling artifact per B13. Strategic conclusion (operator-validated): high-volume matches (1000+ trades) are bilateral candidates; low-volume are single-side or skip; volume should be primary partition axis going forward. **CRITICAL CAVEAT per B14/G17:** Phase 1+2 used historical_events match-level aggregates (first/min/max/last across entire match window), conflating premarket vs in-match opportunities. Decomposition required for strategy-actionable findings. See U4 Phase 3 (next analysis target, references G17). Producer scripts: /tmp/u4_phase1_match_landscape.py, /tmp/u4_phase2_loser_bounce_predictors.py. ANALYSIS_LIBRARY entries pending separate commit.

**CLOSED 2026-05-04 (Session 6).** Superseded by Phase 3 architecture (Session 5) and G9 dataset delivery. Phase 3 Stage 1 delivered the pass1 parquet (28 MB, 1.2M rows, May 1 2026) covering Mar 20 - Apr 10 window with per-moment unit of analysis per LESSONS B15. G9 dataset (DELIVERED per G9) extends per-moment coverage retroactively to Jun 2025 across full Kalshi tennis archive (20,110 markets, 5.0 GB). U4 per-cell bilateral double-cash question continues at G7 Layer A v1 (T19 spec, T20 implementation, T21 coherence read), with B14/G17 time-window decomposition baked in from the start. Pass1 parquet durable-copied to arb-executor/data/durable/u4_phase3_state_pass1.parquet per Phase 1B Session 6. Phase 3 Stages 2-5 disposition (continue or supersede entirely by G9-based Layer A) tracked at D12.

U5. 30 UNCALIBRATED cells: edge, no edge, or insufficient data? Per LESSONS Section 6 known unknown #6. **COUNT VERIFIED 2026-04-30 (commit 82809ad):** 30/67 confirmed. Open question reframed: does re-running classification with corrected methodology (canonical bias per F22, scalp-achievable constraint per A9) reduce UNCALIBRATED count or move cells into known-mechanism buckets?

U6. 58 still-resting Apr 24-29 positions outcomes. Per LESSONS Section 6 known unknown #8. Wait-and-see; resolves when positions exit or settle.

U7. Channel 2 attribution to game events. Originally hoped for via live_scores; insufficient per A25/A27. Blocked pending alternative game-state source (Kalshi live_data API, ESPN scraper, or other).

U8. Inverse-cell cross-check on real data. Per LESSONS Section 6 known unknown #9. Does Cell X bouncing +5c correlate with its inverse cell dipping ~minus 5c at the same moment? Analysis target.

U9. Apr 24 retune isolation problem. Per LESSONS Section 6 known unknown #10. 14 cell disables + 8 exit retunes + 12 code changes simultaneously. Cannot determine which intervention drove subsequent improvement. Historical forensics, deferred.

U10. **per_cell_verification canonical designation.** Per F11. Two batches durably preserved (Apr 28 /tmp at per_cell_verification_tmp_apr28/, Apr 29 17:43 archive at per_cell_verification/), 28 of 30 same-named files differ by sha256. Question for each file in the overlap set: which batch is canonical for which downstream question? Per A29 pattern, expected answer is per-question canonical-designation table, not pick-one-batch-and-retire. Likely 5-10 minutes per file once methodology-difference is understood; total scope ~5 hours if exhaustive. Operator decision on whether to do this work now (D9) or accept both batches as evidence with no single canonical and consume neither for production analysis until resolved.

---

## SECTION 5: G (GAP) — work that does not exist but should

G1. A-tier-era bias measurement. Per LESSONS A28 (now A29 after Path 1 rename — being explicit about file-on-disk number). Bias file for Apr 18+ fills using A-tier premarket_ticks 27-column baseline does not exist. Required for trustworthy per-cell analysis on the post-Apr-18 window.

G2. Depth-3 capacity analysis using 5-deep depth columns. Per LESSONS A22/A26 and ANALYSIS_LIBRARY findings. We have A-tier data with bid_2-5 / ask_2-5 with sizes; no analysis uses them. Capacity-for-size, market-impact, book-imbalance dynamics all blocked here.

G3. Depth-4 microstructure analysis using is_taker. Per A26 + T10 closure: trade CSVs have taker_side, kalshi_fills_history.json has is_taker. No volume profile, VWAP, autocorrelation, market impact, or order-flow microstructure analyses exist.

G4. Per-cell economics on cleaned data (post-T7-canonical bias, post-T10 entry-time). corrected_cell_economics.py methodology is canonical (per T9) but has not been re-run with the canonical bias designation from T7 + canonical entry-time from T10.

G5. arb-executor-v2 directory contents. Per LESSONS Section 6 known unknown #11. **CLOSED 2026-04-30:** confirmed legacy cross-platform arb code, no tennis content (T4). Listed here as historical because the gap is now resolved.

G6. /tmp/bbo_aw1.csv and /tmp/bbo_aw2.csv vs canonical bias file. Per LESSONS Section 6 known unknown #12. **CLOSED 2026-04-30:** aw1/aw2 measure premarket-to-late drift, distinct from entry_price_bias canonical. Complementary not redundant. Listed here as historical.

G7. **Bounce / exit / returns analysis separation.** Operator-flagged 2026-04-30 (Session 5). The current `corrected_cell_economics.py` and scorecard family conflate three distinct analysis layers, which is why per-cell metrics can't be reasoned about cleanly. The separation principle:

  **Layer A — Pure bounce per cell.** Property of the market. Measure forward bounce distribution (max_mid_next_X minus mid_at_t) per cell from the per-moment dataset. No exit logic. No fill assumptions. No P&L. Outputs: per-cell bounce distribution at each forward window (2min/5min/30min/2hr/until_settlement).

  **Layer B — Exit policy optimization.** Property of strategy. Given Layer A bounce distribution, what exit policy (limit at +Xc, time-stop at Y, trailing stop, etc.) maximizes expected capture? Outputs: per-cell optimal exit policy + expected capture rate.

  **Layer C — Realized returns.** Layer A + Layer B + fees + slippage + fill probability + capital utilization. Outputs: per-cell economics.

  Phase 3 (per-moment dataset) is the foundation for Layer A. Layer B and Layer C build on top. All three layers stay in separate scripts; never cross-conflate. Validates by showing each layer can be re-run with different parameters without recomputing the others (e.g., changing exit policy in Layer B should not require re-running Layer A bounce measurement).

  Captured here so the analysis sequence after Phase 3 doesn't drift back into the conflation pattern that broke prior cell-economics work.

G8. **Trade-tape backfill via Kalshi /historical/trades endpoint.** Operator-flagged Session 5 (via Liams API schema research). Phase 3 v1 ships without trade-flow columns because tennis.db has no trade table for Mar 20 - Apr 10. Stage 0 Probe 2 confirmed: zero trade tables; JSONL trade events Apr 17+ only; kalshi_fills_history.json is sparse bot fills not continuous trade tape.

  **Available source (newly identified):** `/trade-api/v2/historical/trades?ticker=X` returns retroactive trade events with: ticker, trade_id, yes_price_dollars, no_price_dollars, count_fp (size), **taker_side** (yes/no - which side initiated), created_time (millisecond precision).

  **What this unlocks:**
  - cum_trades_so_far per moment (closes the gap dropped from Phase 3 v1 schema)
  - trades_last_5min, trades_last_30min flow-rate signals (the volume-at-decision-time strata variable)
  - taker_side imbalance - fundamental microstructure signal for order flow direction
  - per-minute volume time-series (alternative: /historical/markets/{ticker}/candlesticks for 1-minute aggregate fallback if full trade tape is too expensive)

  **Cost estimate:** ~2,714 markets x avg 1,500-3,000 trades each = 4M-8M total trades. At Kalshis ~20 req/s rate limit with paginated fetches, ~30-90 minutes of API calls + storage of trade tape (~500MB CSV). Single retroactive build similar to match_facts_v3 producer.

  **Sequencing:** Wait until Phase 3 v1 Stage 1 delivers per-moment BBO state vector and Layer A bounce analysis runs. If "lack of trade-flow signal" is the most common limitation hit in real strategic queries, thats when Phase 3 v2 trade-tape backfill becomes priority. Otherwise lower-priority - dont build synthesis machinery before knowing which gaps it actually fills.

  **Blocked by:** none. Can be implemented anytime after Stage 1 finishes.

G9. **Historical-scale dataset extension - full Kalshi tennis archive.** Operator-flagged Session 5 (via Liams per-match visualization on a 2025 match). The per-moment dataset Phase 3 v1 builds for Mar 20 - Apr 10 2026 is methodology validation, not final scope. Liams chart on KXATPMATCH-25JUN18RUNMCD-RUN proves Kalshis `/historical/trades` and `/historical/markets/{ticker}/candlesticks` endpoints work retroactively for matches at least back to mid-2025, and likely the full Kalshi tennis archive (~50K-100K markets). This makes the canonical Phase 3 dataset roughly 20x what v1 produces.

  **What this unlocks:**
  - Statistical power at fine-grained cell resolution. Mar 20 - Apr 10 is borderline for fine state-vector stratification; 20x scale makes it viable.
  - **Two-channel scope made explicit.** Each market has two structurally different scalping windows: (1) premarket - typically T-24hr before match through commence_time, expectations-driven price formation, no game state; (2) in-match - commence through settlement, game-state-driven volatility and recovery. Historical pulls from `created_time` give us the full premarket arc per market, not just active hours. Premarket window is ~12x longer per match than in-match (24hr vs 2hr typical), so historical scale makes premarket-specific stratification viable that Phase 3 v1s small dataset cant support: volume buildup curves, late-premarket drift, premarket reversion patterns, premarket-to-match-start price stability filters.
  - **Layer B exit policy parameter sweeps run separately per channel.** Premarket and in-match have different fill dynamics (premarket thinner book), different latency tolerances (premarket slower price changes), and different price-formation processes (expectations vs game-state). Single exit-policy optimization across both windows would average across regimes; separate optimizations per channel are the right unit. For each channel: every (state vector, exit policy) combination - limit thresholds from +1c to +30c at 1c granularity, time-stops from 30s to 4hr, trailing-stops at every offset - simulated forward across all matching observations.
  - Layer A bounce measurement at higher confidence per cell, conditional on channel.
  - Layer C realized economics with fee/slippage/fill probability across enough samples that distributions are stable.

  **Tier reframe:** What we labeled C-tier (`historical_events` aggregates) is actually the most-lossy summary of what Kalshi has. The richness was always there in Kalshis archive - `/historical/trades` returns trade-by-trade with taker_side and ms timestamps; `/historical/markets/{ticker}/candlesticks` returns per-minute OHLC bid/ask/volume/OI. Tier framework should be re-described in TAXONOMY post-v2 to reflect this: "historical archive" is its own tier above C, retroactively pullable, richer than B-tier in some dimensions (taker_side, full volume time-series) and equal-or-coarser in others (per-minute candle vs per-tick BBO).

  **Pipeline shape (different from Phase 3 v1):**
  - Per-market API pulls, not single-file streaming. Each market: 1 candlestick call + paginated trade-tape calls. ~10-30 trade calls per market.
  - Cost estimate: ~50K-100K markets x ~15 calls avg = 750K-1.5M API calls. At Kalshis ~20 req/s, ~10-30 hours of throughput-bound API time.
  - Storage: trade tape ~5-10GB CSV; candlesticks ~500MB-1GB.
  - Per-minute resolution for the historical extension. Per-tick fidelity remains in current bbo_log_v4 22-day window for microstructure questions.

  **Sequencing - strict:**
  1. Phase 3 v1 Stage 1 finishes (currently running).
  2. Stages 2-5 deliver, Layer A bounce measurement runs and produces sensible numbers on the small dataset. **This is methodology validation.** If Layer A doesnt reproduce coherent conclusions on the small dataset, scaling 20x would waste 30 hours of API + analysis on a broken methodology. Dont skip this gate.
  3. **Then** build the historical extension. Producer is similar to `build_match_facts_v3.py` - three-pass (event enumeration via API, per-market trade tape pull, per-market candlestick pull) with pagination and rate-limit handling.
  4. Layer B exit-policy parameter sweep runs on the v2 dataset, separately for premarket and in-match channels.
  5. Layer C realized economics with fees/slippage/fill prob.

  **Blocked by:** Phase 3 v1 methodology validation (Layer A on small dataset). Premature scaling without that gate is the same anti-pattern that broke prior cell-economics work.

  **STATUS: DELIVERED 2026-05-02.** Producer `arb-executor/data/scripts/build_g9_archive.py` ran cleanly via `/historical/*` endpoint family (the route Liams chart used, discovered late Session 5 after the wrong-endpoint-family bisection had been corrected). Final scope:

  | dimension | delivered |
  |---|---|
  | markets pulled | 20,110 (vs 14,700 enumeration estimate; archive grew during pull, plus live-tier was larger than projected) |
  | runtime | 12.6 hours (vs 3-4hr projected; high-volume tail dominated single-market extrapolation) |
  | storage | 5.0 GB |
  | errors | 0 |
  | failures | 0 |
  | output location | `arb-executor/data/historical_pull/` |
  | output structure | per-market: metadata JSON + trades CSV + candlesticks CSV |
  | trades coverage | 20,018 markets had trades (92 zero-volume markets correctly skipped) |
  | candles coverage | 19,687 markets had candles (423 sub-1-minute lifetime markets correctly skipped) |

  **Bug caught and fixed pre-production:** CUTOFF_TS was originally hardcoded as 1772582400 (Mar 4 UTC) when intended Mar 2 UTC = 1772409600. Caught after 30s of producer runtime via CC review. Captured as LESSONS C23: derive epoch constants from ISO strings inline, never from hardcoded numbers with date comments.

  **Pre-Mar-2026 endpoint discovery (load-bearing):** The earlier bisection probe declared horizon-blocked at Mar 2026 because it tested the live endpoint family (`/markets/*`, `/markets/trades`). Liams chat surfaced that Kalshi has a separate `/historical/*` endpoint family - `/historical/cutoff`, `/historical/markets/*`, `/historical/trades`, `/historical/markets/{ticker}/candlesticks` - that serves retired markets. Once probed, this opened up the full archive. Captured as the methodology gap to interrogate the API surface, not just one endpoint family, before declaring horizon-blocked. Worth a LESSONS follow-up.

  **Open follow-on:** Dataset is currently 20K CSVs + 20K JSON files. Querying requires per-file opens. Natural next step is parquet conversion (one big trade-tape parquet, one big candles parquet, one big metadata parquet) for groupby-based analysis. ROADMAP T17 added separately for this work.

G10. **Layer B exit-policy parameter sweep.** Per LESSONS B16. Property of strategy given Layer A bounce distribution. For every (state vector, exit policy) combination, simulate forward across all matching observations and back-derive expected return per combination. Two-channel scope per LESSONS G17: premarket and in-match run as separate sweeps (different fill dynamics, latency tolerances, price-formation processes). Exit policy parameter space: limit thresholds +1c to +30c at 1c granularity, time-stops 30s to 4hr at multiple resolutions, trailing-stops at every offset, combined policies. For each (state vector, policy) combination, output: expected return, P10/P90 return, hit rate (fraction of observations where policy triggered), capital utilization. Gated on T21 Layer A coherence read.

G11. **Layer C realized economics.** Per LESSONS B16. Property of operation: Layer A + Layer B + fees + slippage + fill probability + capital constraints. Final expected P&L per (state vector, exit policy). Where the rubber meets the road on whether a Layer-B-optimal policy survives realistic execution friction. Gated on G10 delivery.
G12. **Per-event paired moments dataset.** Per LESSONS B19 + ROADMAP F13. Producer would consume g9_trades + g9_candles + g9_metadata, output per-moment records with: event_ticker (derived via rsplit), side (yes/no), end_period_ts, yes_bid/ask, no_bid/ask, time-aligned counterpart price from the inverse ticker, volume_in_window. Enables U8 (inverse-cell cross-check at per-moment grain), E18 bilateral capture per-event, and any game-state work where simultaneous per-side observations are required. Not blocking T21 to Layer B (T31): T21 Check 6 (LESSONS A36) confirmed cell-aggregate distributional fold is clean, so Layer B can proceed on cell_stats.parquet for distributional exit-policy work. G12 is required for U8 and per-event questions specifically. Estimated scope: 1-2 hour producer (similar architecture to build_g9_parquets.py + a paired-side join), output ~10M rows across ~10K matches.

---

## SECTION 6: D (DECISION) — operator authorization or operational call required

D1. Delete /tmp/harmonized_analysis/*.csv methodology-incorrect outputs. Per F2. Currently retained with deprecation marker. Decision: delete entirely, retain indefinitely as forensic reference, or copy to durable archive then delete from /tmp.

D2. Kill mlb_bbo_logger / live_v3.py paper session to free CPU+RAM during heavy analysis. Per Session 4 finding (CPU contention slowed tier-counter to 25% efficiency). Decision: not worth killing to accelerate doc/probe work; revisit if heavy compute needed.

D3. Rotate GitHub PAT exposed in git remote URL. Per T12. Operator action only — generate new PAT, update remote, force-push history rewrite or accept exposure.

D4. Rotate Kalshi API key in /tmp/probe_kalshi_api2.py. Per T12. Operator action only — generate new key, update .env, ensure no plaintext copies remain.

D5. /tmp ephemerality migration. Per F1. Decision: which /tmp files are canonical enough to migrate to durable storage now, vs accept the ephemerality risk?

D7. Security rotation execution (when operator chooses). Staged playbook for T12: (1) generate new GitHub PAT or switch to SSH remote (`git remote set-url origin git@github.com:OMIGROUPOPS/Omi-Workspace.git`), revoke old PAT in github.com/settings/tokens. (2) Generate new Kalshi API credentials in Kalshi dashboard, replace /root/Omi-Workspace/arb-executor/kalshi.pem with new RSA private key, update KALSHI_ACCESS_KEY in /root/Omi-Workspace/arb-executor/.env. (3) Audit `git log -p -- backend/.env` for every credential ever committed to that file; rotate each independently. (4) `git rm --cached backend/.env` to untrack while keeping local copy. (5) Refactor 14 hardcoded-secret files to use os.environ. (6) Optionally rewrite git history with git-filter-repo or BFG (or accept exposure since repo is public anyway). Estimated time when prioritized: 30-90 minutes.

D6. Bug 4 implementation prioritization. Per T11a. Two paths: (a) implement now to clean up the operational state for any future redeploy, or (b) defer until pre-redeploy phase since bot is shut down and operational state isn't actively burning. Analytical impact already mitigated by T10 closure — forward measurement work doesn't block on this fix.

D8. CC-LESSONS-bootstrap design choice. Per T16. Three options on the table: (a) CC reads full LESSONS.md every session; (b) chat-side inline injection per prompt; (c) hybrid LESSONS_QUICKREF.md + selective inline. Chat recommendation: (c) — load-bearing CC-actionable patterns on disk for CC, chat retains discretion for context-specific lessons. Operator decision required before any T16 implementation work.

D9. **per_cell_verification canonical designation execution.** Per U10 + F11. Two batches preserved (Apr 28 /tmp at per_cell_verification_tmp_apr28/, Apr 29 17:43 archive at per_cell_verification/), 28 of 30 same-named files differ by sha256. Decision: (a) do the per-question canonical-designation work now (~5 hours scope per U10), or (b) accept both batches as forensic evidence with no single canonical designated; do not consume per_cell_verification outputs for production analysis until resolved. Default to (b) until forward analysis genuinely needs a per_cell_verification number, at which point (a) becomes a prerequisite for that downstream work.

D10. **harmonized_analysis canonical designation.** Per F12 + F25 + F2. Both /tmp and archive batches are methodology-incorrect per F25 (T9 closure marker). Mtime/sha256 mismatch between batches indicates two different methodology-incorrect runs. Decision: (a) leave both, no canonical designated, do not consume per F25 deprecation marker, or (b) delete both per F2 / D1 to reduce future confusion. Default to (a) — preserved forensic evidence is cheap, accidental consumption already mitigated by F25 marker.

D11. **Liam chart-iteration thread reconciliation.** Liam works in parallel AI chat sessions on chart-iteration / per-match visualization (per user-memory). Coordination route: through operator, not chat-to-chat. Decision required when Liam's work product is ready to merge into Phase 3 v2 / G7 architecture: (a) Liam's chart code becomes T24 implementation directly, (b) Liam's chart code is reference for separate chat-implemented T24, or (c) other arrangement. Currently no merge needed; tracked here so the path exists.

D12. **Phase 3 v1 design doc disposition.** Per T23. Phase 3 v1 design doc (arb-executor/docs/u4_phase3_design.md, 209 lines) is partially obsolete: Stage 0 findings still valid, 30s cadence retired (B15/B16), G9 architecture supersedes bbo_log_v4 source. Three options:
  - (a) rewrite as Phase 3 v2 design doc reflecting native-resolution + G9 architecture (substantial work, supersedes v1)
  - (b) formally retire Phase 3 v1 with SUPERSEDED tag and pointer to G7 + Layer A v1 spec (T19); Phase 3 v2 only exists as G7/T19/T20/T21 distributed across ROADMAP entries
  - (c) leave v1 as-is with Session 5 architectural learnings appended; do not write a v2 doc; rely on G7/T19/T20/T21 + ROADMAP for forward design
Default to (c) — least work, retains v1 as historical record, forward design lives in ROADMAP indices not in a single design doc. Operator countermand if (a) or (b) preferred.

---

## SECTION 7: RECENTLY COMPLETED (Session 4, Apr 30) — high-level

Earliest first within the session.

- LESSONS.md created and grew from 91 to 140 lessons across 7 categories (A=30, B=12, C=16, D=10, E=29, F=27, G=16).
- Module scaffolding created: README.md, TAXONOMY.md, ANALYSIS_LIBRARY.md, ROADMAP.md.
- Variable-inventory probe + TZ probe + TZ follow-up probe completed; all known timestamp columns classified.
- Depth-inventory probe completed; ~30 prior analyses cataloged.
- ANALYSIS_LIBRARY.md fully populated with per-question canonical designations.
- TAXONOMY.md fully populated: tier definitions, depth taxonomy, depth × tier matrix, full variable inventory with verified TZ labels, kalshi_fills_history.json added as Tier-A fact source.
- T1-T10 closed (10 of 12 foundational items). T11/T12 remain.
- T13/T14/T15 added during foundational close-out as emergent items.
- Major discovery: kalshi_fills_history.json closes F17/F9/F8/A26/F10 partially-or-fully (E29 cross-reference closure pattern documented).

---

## SECTION 8: NEXT MOVES

Current path forward post-Session-6: foundational data layer is durable, ROADMAP cleanup is the active work. After Phase 1D-ix and 1D-x close (Section 8 refresh + Section 9 changelog refresh), the analysis path resumes with Layer A v1 on G9 dataset.

**Immediate sequence (gates Layer A coherence read = Session 6 success metric):**

1. T18 (candles semantics probe) — gates T17. ~10 min. If candle bid/ask are not best-bid/best-ask snapshots, schema choice for T17 changes.
2. T17 (G9 dataset parquet conversion) — gates Layer A. ~30-60 min runtime.
3. T19 (Layer A v1 specification) — design choices explicit, blocks T20.
4. T20 (Layer A v1 implementation) — code per T19 spec, reads g9_*.parquet.
5. T21 (Layer A coherence read) — sanity-check methodology. Session 6 success metric.

**Post-T21 if coherent:**

6. G10 (Layer B exit-policy parameter sweep) — property of strategy given Layer A bounce distribution.
7. G11 (Layer C realized economics) — Layer A + Layer B + fees + slippage + fill probability + capital constraints.

**Parallel deferred items:**

- T22 (TAXONOMY refactor for multi-tier-as-feature framing) — doc work, can run any time.
- T23 (Phase 3 v1 design doc disposition) — pending D12 decision; default (c) leave-as-is is currently authoritative until operator countermand.
- T24 (per-match visualization tool) — sanity-check companion to Layer A; not blocking.
- T25 (fair-value model integration scoping) — prerequisite for Layer A v2.
- T26 (live trading deployment plan tracker) — far-future, not Session 6 scope.
- T11a/T11b (Bug 4 implementation + sandbox test) — operational, not analytical; defer per D6 default.
- T12 (security rotation) — operator action only per D7 staged playbook.
- T13 (B-tier OOM-resilient retry) — populates TAXONOMY Section 1 B-tier match counts; lower priority than T22 refactor since multi-tier-as-feature framing supersedes the question.
- T14 (kalshi_fills_history.json re-pull schedule) — durability mitigation; deferred since file is now durable-copied per F1 partial closure.

**Open decisions blocking nothing immediately:**

- D6 (Bug 4 implementation prioritization) — no impact on Layer A path.
- D9 (per_cell_verification canonical designation work) — default defer until forward analysis genuinely needs a per_cell number.
- D10 (harmonized_analysis canonical designation) — default leave both, do not consume.
- D11 (Liam chart-iteration thread reconciliation) — coordination, not chat-side decision.
- D12 (Phase 3 v1 design doc disposition) — default leave-as-is, forward design lives in ROADMAP indices.

---

## SECTION 9: CHANGELOG

- 2026-04-30 ~13:21 ET: Initial scaffolding (commit c794b26).
- 2026-04-30 ~14:00 ET: First update reflecting variable-inventory and TZ probes complete (commit cac13c4).
- 2026-04-30 ~15:10 ET: Section 3 added — flat to-do list with dependency ordering, 12 items (commit 7ce7359).
- 2026-04-30 ~18:30 ET: T12 audited and deferred. All 12 foundational close-out items resolved. T11a/T11b/T13/T14 stay OPEN as deferred work, not blockers. D7 added (staged security rotation playbook). C17 lesson added (security audits must redact credentials within the audit itself).
- 2026-04-30 ~18:00 ET: T11 closed — Bug 4 fully designed but zero implementation written. Split into T11a (implementation, OPEN) and T11b (sandbox test, OPEN). Analytical impact mitigated by T10 closure; operational impact remains. D6 added (Bug 4 prioritization decision).
- 2026-04-30 ~17:45 ET (prior commit): Restructured into T/F/U/G/D categorized indexed system, same model as LESSONS.md. T1-T15 indexed (T1-T10, T15 closed; T2 partial; T11-T14 open). F1-F10 flagged. U1-U9 unknown. G1-G6 (G5/G6 closed historical). D1-D5 awaiting decision. Current state captured comprehensively for handoff durability.
- 2026-05-01 (Session 5): Phase 3 design doc + Stage 1 producer (`/tmp/u4_phase3_state_pass1.parquet`, 28 MB, 1.2M rows, ~7.4hr runtime). 9 LESSONS additions: B13/B14/B15/B16, A31, E29, F26/F27/F28. match_facts_v3.csv produced (`arb-executor/data/match_facts_v3.csv` durable). U4 PARTIALLY ANALYZED → strategic conclusion (volume primary partition). Architectural pivot: native-resolution per-tick over 30s cadence binning.
- 2026-05-02 (Session 5): G9 dataset DELIVERED. 20,110 markets / 5.0 GB / Jun 2025 - May 2026 / Kalshi /historical/* endpoints / build_g9_archive.py at arb-executor/data/scripts/. ROADMAP G7 (Layer A/B/C separation), G8 (trade-tape backfill, SUPERSEDED-BY-G9), G9 (delivered) added. T16 (CC bootstrap), T17 (parquet conversion) added. D8 (CC-LESSONS-bootstrap design choice) added.
- 2026-05-04 (Session 6): Foundational preservation + ROADMAP cleanup work.
  Phase 1A (commit ce0cd19): 36 untracked archive scripts committed to git.
  Phase 1B: 2.3 GB of irreplaceable /tmp data files copied to arb-executor/data/durable/ with sha256 verification + MANIFEST.md (parquet, bbo_log_v4.csv.gz, kalshi_fills_history.json, match_facts_v3_metadata.csv, u4_phase3_stage1.log, validation4_ticks/).
  Phase 1C (commits d0462c8, e067c18, 983444f, f36691c, e7e1ddc, d088cf3): 143 files preserved across 6 single-concern commits — 23 producer scripts + 10 V3-era artifacts + 11 validation4 helpers + 14 outputs + 50 v3_analysis/validation5 + 35 per_cell_verification (Apr 28 batch + 2 TMP_ONLY canonical fills).
  Phase 1D (commits b855e15, 070a410, 0ded25c, 6957f28, 765e5e1, 7584ede, 4964ae1, 69e6862, this commit): T17 placement fix; T18-T26 added; G10/G11 added; F11/F12 added with F1 partial closure; U10 added; D9-D12 added; U4 closed with G7 Layer A continuation pointer; Section 8 NEXT MOVES refreshed with current Layer A pipeline; Section 9 CHANGELOG refreshed (this entry).
- 2026-05-04 (Session 6 Phase 1D-xi): T27-T30 added (foundation->analysis sequence per LESSONS C27: parquet verification, foundation commit, Layer A v1 visuals, Layer A v1 tabular metrics).
- 2026-05-04 (Session 6 Phase 5-ii / T21 closure): T21 CLOSED with PASS verdict — Layer A v1 foundation methodology validated. F13 added (cell_stats event_ticker gap). G12 added (per-event paired moments dataset). T31 added (Layer B exit-policy sweep promoted from G10). LESSONS A36, B19, B20, F30 added in same commit. Section 8 NEXT MOVES requires update (separate commit) to reflect T21 closure and T31 as new active analytical work.
