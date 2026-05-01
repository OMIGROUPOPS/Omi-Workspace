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

---

## SECTION 3: F (FLAG) — operational risks and attention items

F1. /tmp ephemerality risk. Per LESSONS F28: bare /tmp files can be lost over time without warning. Files currently sitting on /tmp that are canonical sources: kalshi_fills_history.json (per A30), bbo_log_v4.csv.gz (B-tier), entry_price_bias.csv cluster, bbo_aw1/aw2, harmonized_analysis/ deprecated outputs. Mitigation tracked at T14 for kalshi_fills_history; broader durability migration not yet planned.

F2. /tmp/harmonized_analysis/ outputs retained on disk. Per LESSONS F25: methodology-incorrect data, deprecation marker placed but actual files not deleted. Future readers may consume them despite the marker. Mitigation: depends on D1 (deletion authorization).

F3. Stale references in LESSONS Section 4. Per LESSONS F27: scanner_pendulum.log cited as legacy bot log but does not exist on disk. Reference must be removed in next doc-cleanup pass. Other LESSONS Section 4 entries should also be re-verified given /tmp ephemerality (F1).

F4. Apr 17 - Apr 23 fill detection broken locally. Per LESSONS F10/F26: live_v3 JSONL had 0 entry_filled events in this 6-day window despite 393MB of log content (763 cell_match events, 0 entry_filled). Now partially mitigated by T10 closure (kalshi_fills_history.json has server-side fills regardless). But: the local-bot-state for what the bot DECIDED to enter is preserved; the local fill confirmations were lost. For analyses that need both decision intent AND execution, the join is fragile in this window.

F5. bookmaker_odds table is junk-drawer per LESSONS F15. Player1/player2 fields '?' in samples, kalshi_ticker/kalshi_price/edge_pct NULL in samples. Use book_prices for sharp consensus. F15 implies "do not use bookmaker_odds" but the table still exists; if any future code accidentally reads it, results will be invalid.

F6. live_scores table has only final set scores per A25/A27. Schema columns p1_games/p2_games suggest per-game state but are empty in samples. For Channel 2 game-event attribution work (currently blocked, see U7), live_scores is insufficient.

F7. matches.entry_time NULL on every live/live_log row per F17. Even with T10 closed and kalshi_fills_history.json canonical, the matches table itself remains broken on this column. Any code that joins to matches.entry_time should be flagged.

F8. matches.settlement_time has two writers per F18. Live rows naive ET, backfill rows ISO no-Z. Per-row format detection required. Future joins on this column are fragile.

F9. players.last_updated is UTC via SQLite date('now') per F20, while every other te_live.py-written column is ET. Same-writer-different-tz outlier. If any cross-table join uses players.last_updated as if ET, results are wrong by N hours.

F10. Path 1 lesson-number renames. Three off-by-one drift events occurred in Session 4. D10 added to mitigate; subsequent commits used dynamic on-disk number reads which worked. Still a flag because future Claude sessions need to internalize the pattern.

---

## SECTION 4: U (UNKNOWN) — open questions blocking strategic decisions

U1. Magnitude and distribution of data corruption in matches table records. Per LESSONS Section 6 known unknown #1. Partially expanded by F7 (entry_time NULL), F8 (settlement_time two writers), F17, F18. Full magnitude still unmeasured. T10 closure provides a cleaner alternative source (kalshi_fills_history.json) so this unknown becomes lower priority for forward analysis.

U2. Right cell definition. Per LESSONS Section 6 known unknown #2. Current scheme is tier × side × 5c price band. Open: is 5c the right granularity, is direction redundant with price, should tier be primary or secondary partition. Strategic question, not foundational; deferred until foundation complete.

U3. Per-cell average bounce decomposed by Channel 1 vs Channel 2 on uncorrupted data. Per LESSONS Section 6 known unknown #3. Analysis target.

U4. Per-cell bilateral double-cash rate. Per LESSONS E18/E21/E22. Extends April 14 paired analysis. **PARTIALLY ANALYZED 2026-04-30 (Session 4):** U4 Phase 1 characterized 5,879-match landscape; U4 Phase 2 stratified 3,936-match synchronized subset by 7 dimensions. Volume is canonical predictor: 33pp swing across volume strata (50-99 trades = 34.3% bilateral capture at +10c; 1000+ trades = 76.4%). Categories track within 6pp (ATP_CHALL=63.1%, ATP_MAIN=63.5%, WTA_MAIN=64.3%, WTA_CHALL=56.8%). Skew >35 cliff partially ceiling artifact per B13. Strategic conclusion (operator-validated): high-volume matches (1000+ trades) are bilateral candidates; low-volume are single-side or skip; volume should be primary partition axis going forward. **CRITICAL CAVEAT per B14/G17:** Phase 1+2 used historical_events match-level aggregates (first/min/max/last across entire match window), conflating premarket vs in-match opportunities. Decomposition required for strategy-actionable findings. See U4 Phase 3 (next analysis target, references G17). Producer scripts: /tmp/u4_phase1_match_landscape.py, /tmp/u4_phase2_loser_bounce_predictors.py. ANALYSIS_LIBRARY entries pending separate commit.

U5. 30 UNCALIBRATED cells: edge, no edge, or insufficient data? Per LESSONS Section 6 known unknown #6. **COUNT VERIFIED 2026-04-30 (commit 82809ad):** 30/67 confirmed. Open question reframed: does re-running classification with corrected methodology (canonical bias per F22, scalp-achievable constraint per A9) reduce UNCALIBRATED count or move cells into known-mechanism buckets?

U6. 58 still-resting Apr 24-29 positions outcomes. Per LESSONS Section 6 known unknown #8. Wait-and-see; resolves when positions exit or settle.

U7. Channel 2 attribution to game events. Originally hoped for via live_scores; insufficient per A25/A27. Blocked pending alternative game-state source (Kalshi live_data API, ESPN scraper, or other).

U8. Inverse-cell cross-check on real data. Per LESSONS Section 6 known unknown #9. Does Cell X bouncing +5c correlate with its inverse cell dipping ~minus 5c at the same moment? Analysis target.

U9. Apr 24 retune isolation problem. Per LESSONS Section 6 known unknown #10. 14 cell disables + 8 exit retunes + 12 code changes simultaneously. Cannot determine which intervention drove subsequent improvement. Historical forensics, deferred.

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

1. T11 (Bug 4 status check) — probe to determine fix state.
2. T12 (security rotation) — operator action.
3. T13 (B-tier OOM-resilient retry) — populate TAXONOMY Section 1 B-tier match counts.
4. T14 (kalshi_fills_history.json re-pull schedule) — durability mitigation.
5. ALL T-items closed. Re-read this ROADMAP. Pick first analysis with intention from G-items (most strategic) or U-items (most blocking).

---

## SECTION 9: CHANGELOG

- 2026-04-30 ~13:21 ET: Initial scaffolding (commit c794b26).
- 2026-04-30 ~14:00 ET: First update reflecting variable-inventory and TZ probes complete (commit cac13c4).
- 2026-04-30 ~15:10 ET: Section 3 added — flat to-do list with dependency ordering, 12 items (commit 7ce7359).
- 2026-04-30 ~18:30 ET: T12 audited and deferred. All 12 foundational close-out items resolved. T11a/T11b/T13/T14 stay OPEN as deferred work, not blockers. D7 added (staged security rotation playbook). C17 lesson added (security audits must redact credentials within the audit itself).
- 2026-04-30 ~18:00 ET: T11 closed — Bug 4 fully designed but zero implementation written. Split into T11a (implementation, OPEN) and T11b (sandbox test, OPEN). Analytical impact mitigated by T10 closure; operational impact remains. D6 added (Bug 4 prioritization decision).
- 2026-04-30 ~17:45 ET (prior commit): Restructured into T/F/U/G/D categorized indexed system, same model as LESSONS.md. T1-T15 indexed (T1-T10, T15 closed; T2 partial; T11-T14 open). F1-F10 flagged. U1-U9 unknown. G1-G6 (G5/G6 closed historical). D1-D5 awaiting decision. Current state captured comprehensively for handoff durability.
