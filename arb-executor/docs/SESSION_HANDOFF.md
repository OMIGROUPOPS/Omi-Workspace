# SESSION 5 HANDOFF — 2026-05-01

**Read order for next session:** README → this file → LESSONS → TAXONOMY → ANALYSIS_LIBRARY → ROADMAP. Then resume at Stage 1 validation when it finishes (or has finished).

---

## WHO YOU'RE WORKING WITH

Operator is Druid, co-founder OMI Group Holdings (trading division OMQS). Algorithmic prediction-market trading on Kalshi. Direct, technically precise, pushes back on premature conclusions and is consistently right when he does. Treat operator pushback as probe-trigger, not defend-trigger (per A32 added this session).

---

## SYSTEMS ACCESS

- **VPS:** `ssh root@104.131.191.95`
- **Workspace:** `/root/Omi-Workspace`, primary subdirs `arb-executor/` and `arb-executor/docs/`
- **GitHub:** `github.com/OMIGROUPOPS/Omi-Workspace`
- **CC (Claude Code):** primary server-side execution agent. Chat drafts and verifies; CC executes.

---

## WHAT SESSION 5 ACCOMPLISHED

### Phase 3 design — fully written and validated through Stage 0
- `arb-executor/docs/u4_phase3_design.md` (209 lines after seven review-pass commits)
- Reframes unit of analysis from per-match (Phase 1+2 approach) to per-moment (the unit a bot decides on)
- 11 sections: REFRAMING, CORE QUESTION, DATASET SCHEMA, SAMPLING CADENCE, DATA SOURCES & COVERAGE LIMITS, STREAMING PATTERN, EXECUTION PLAN, RISK ASSESSMENT, DELIVERABLES, OPEN QUESTIONS FOR OPERATOR, NEXT STEPS
- Stage 0 (pre-flight probes) ran 7 probes empirically; design corrected against all findings:
  - Drop bid_size/ask_size (bbo_log_v4 is 5-col schema, no sizes)
  - Drop trade-flow columns (no trade source for Mar 20 - Apr 10 — flagged G8 for retroactive backfill)
  - Output ceiling 8M -> 2M rows (62 active matches/day actual vs 250 estimate)
  - Add 2min as shortest forward window (Probe 7: 12% of bot exits complete <5min, P5 ~2min)
  - Hybrid rolling state: 1-second-resolution ring buffer + scalar trackers + 30-min eviction (Probe 8 caught design's 200-tick assumption was 142x off — would have OOM'd at ~27GB)

### match_facts_v3.csv — canonical match-start source built and validated
- Located at `arb-executor/data/match_facts_v3.csv` (durable, also `/tmp/match_facts_v3.csv` as ephemeral copy)
- Producer: `arb-executor/data/scripts/build_match_facts_v3.py` (durable)
- Three-pass builder: Kalshi API metadata + bbo_log volatility-jump detector + Pass 3 validation against match_facts_full overlap
- 2,714 markets in Mar 20 - Apr 10 window (vs match_facts_full's 1,167 — **2.3× coverage**)
- 81% jump-detected real volatility signal; 16% no_bbo_data (zero-tick markets, correct skip); 3% fallback
- Pass 3 validation: median delta vs match_facts_full reference 1.6min, P10 = 0.0 (exact matches at decile)
- **Caveat:** P90 delta is 326min and stdev 341min — ~10% of derived pregame_close_ts have wide deltas vs reference. Likely restarted/postponed matches where multiple volatility-jumps exist and detectors picked different ones. Acceptable for v1 bilateral/Layer-A analysis; flagged if downstream conclusions correlate with the noisy tail.

### Phase 3 Stage 1 — running in background as of session close
- PID 2566750 launched ~05:13 UTC May 1
- Source: `match_facts_v3.csv` (2,270 valid markets after no_bbo_data skip)
- Output: `/tmp/u4_phase3_state_pass1.parquet`
- Log: `/tmp/u4_phase3_stage1.log`
- Expected finish: ~9 hours from launch (515M bbo_log lines at ~16K/sec gzip-decode rate)
- **Next session: first action is to check Stage 1 status. If complete, validate output and proceed to Stage 2 (forward-window labels via parquet groupby).**

### 9 new LESSONS captured (147 → 156)
- A32: operator pushback is signal, not noise
- B15: flowing time series + per-moment unit of analysis
- B16: bounce/exit/returns separation (3 layers)
- C18: design docs must verify column names against schema
- C19: Kalshi market lifecycle timestamps don't track match start
- C20: multi-source joins require grain checks
- C21: A-tier features can't be retroactively synthesized from B-tier without overlap calibration
- C22: shell conditional exit codes after pipes check the wrong command
- D11: cheap probes prevent expensive mistakes — 5 failure modes (provenance, grain, unit, coverage, upstream-filter)

### ROADMAP additions
- G7: bounce/exit/returns analysis separation (architectural commitment)
- G8: trade-tape backfill via Kalshi `/historical/trades` endpoint (Liam-flagged data layer; pursue after Phase 3 v1 delivers)
- T16: CC bootstrap reads LESSONS.md every session (open, design at D8)
- D8: T16 design choice — chat recommends hybrid LESSONS_QUICKREF approach
- U4: closed (PARTIALLY ANALYZED 2026-04-30 superseded by Phase 3 design 2026-05-01)

---

## CURRENT STATE — WHAT'S OPEN

### Immediate (next session, action required)

**1. Verify Stage 1 finished cleanly.** Check process, log, parquet output. If anomalies in skipped-ticker count or rate, investigate before Stage 2.

**2. Stage 2: forward-window labels.** Reads pass1.parquet, computes max_mid_next_2min/5min/30min/2hr/until_settlement per row via parquet groupby+window. Write `/tmp/u4_phase3_state_pass2.parquet`. Estimated 30-60 min.

**3. Stage 3: paired-side join.** Reads pass2.parquet, joins companion ticker state at same timestamp with cadence-tolerance. Write `/tmp/u4_phase3_state.parquet` (final). Estimated 60+ min.

**4. Stage 4: validation.** Sanity-check aggregate bilateral_10c rate against Phase 2's 62.83% on synchronized subset (NOT against strata-conditional rates — Phase 2 strata used buggy variable). Aggregate-only validation is the correctness check.

**5. Stage 5: strategic queries.** Layer A bounce measurement per cell. Premarket vs in_match decomposition (B14/G17 closure). Then Layer B exit policy + Layer C returns once Layer A delivers.

### Open ROADMAP items

T11a/T11b (Bug 4 implementation + sandbox), T13 (B-tier OOM-resilient retry), T14 (kalshi_fills_history.json re-pull schedule — file is now ~36hr stale), T16 (CC bootstrap design + impl pending D8 decision)

F-items: ongoing flags, no action required this session

U-items: U1-U3, U5-U9 still open. U4 closed. Strategic decisions blocked on Phase 3 dataset delivery.

G-items: G1-G4 (existing data layer gaps), G7 (architectural), G8 (trade-tape backfill — pursue after Phase 3 v1)

D-items: D1-D7 awaiting operator decisions, D8 awaiting T16 design choice

---

## KEY FILES & SOURCES

### Trust (verified Session 5)
- `arb-executor/data/match_facts_v3.csv` — canonical match metadata Mar 20 - Apr 10. 2,714 markets. Use this for all match-start joins.
- `arb-executor/data/scripts/build_match_facts_v3.py` — producer. Re-runnable for window extension.
- `arb-executor/docs/u4_phase3_design.md` — Phase 3 design (209 lines, 11 sections, all Stage 0 findings applied)
- `/tmp/bbo_log_v4.csv.gz` — 515M-row B-tier source. 5-col schema (timestamp, ticker, bid, ask, spread). Mar 20 - Apr 17 ET. Single appending writer = timestamp-monotonic.
- LESSONS.md (156 entries, all sourced from probes or analysis)

### Don't trust without re-verifying
- `match_facts_full.csv` — 53.7% in-window coverage hole (Mar 24 etc.). **Superseded by match_facts_v3.csv.** Don't use for new analysis.
- `/tmp/extract_facts.py` — producer of match_facts_full's incomplete output. Reads from `step6_real/ticks/*.bin` upstream-filtered intermediate. Don't re-run.
- Anything in `/tmp` (F28 ephemerality)
- Pre-Session-5 framings in older docs that reference commence_time on historical_events (column doesn't exist)

### Watch for
- Stage 1 finish status — check first thing next session
- F28 /tmp ephemerality — kalshi_fills_history.json now ~36hr stale, build_match_facts_v3.py durable but `/tmp/match_facts_v3_metadata.csv` is not, may want to durable-copy
- D10 dynamic on-disk lesson numbering — LESSONS now at A32/B16/C22/D11/E30/F28/G17 on disk

---

## OPERATING PATTERNS REFINED THIS SESSION

### Probe-validate-probe-validate as core discipline
Every dataset interrogation hits five failure modes before analysis runs (D11): provenance, grain, unit, coverage, upstream-filter. Cheap probes (1 min) prevent expensive mistakes (9hr bad-foundation runs). Session 5 burned ~30min on a wrong-key Stage 1 launch + ~9.5hr on a producer build that was correct but long. Both were caught by probes; without them we'd have run analyses on broken foundations.

### Operator pushback (A32)
Two times Session 5: "50% skip rate makes no sense" and "matches hit 100K-1M volume" both caught real bugs Claude was about to launch heavy compute on. Pushback is probe-trigger.

### Single-concern commits maintained
17 commits this session, each single concern. Lesson commits split by category (A/B/C/D each separate). ROADMAP additions separate from LESSONS additions. Dynamic on-disk number reads (D10 pattern with `last_num()` regex) prevented chat-drift-from-disk numbering bugs.

### CC interaction
- One CC prompt per turn. Wait for CC to finish.
- File-staging via heredoc with sentinel `OMIDOCEND_4F4620FF` for content too long for command line.
- Splitting heredocs across two prompts when single heredoc gets truncated in transit (large doc creation).
- Raw GitHub URLs for byte-exact re-reading of recently committed files; CC echoes the URL after each commit.
- CC pastes raw URLs in commit confirmations — use those for review rather than stale GitHub CDN cache.

---

## NEXT-SESSION OPENING

1. Check Stage 1 status: `tail /tmp/u4_phase3_stage1.log` and `ls -la /tmp/u4_phase3_state_pass1.parquet`
2. If Stage 1 done: proceed to Stage 2 design + execution
3. If Stage 1 still running: wait, or work on Stage 2 script in parallel
4. After Stages 2-5 deliver per-moment dataset: Layer A bounce measurement is the first analysis to run

**End of handoff. Next session: verify Stage 1, then Stage 2, then Layer A.**
