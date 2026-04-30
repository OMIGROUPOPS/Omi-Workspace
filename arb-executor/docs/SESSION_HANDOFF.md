# SESSION 4 HANDOFF — 2026-04-30

**Read order for next session:** README → this file → LESSONS → TAXONOMY → ANALYSIS_LIBRARY → ROADMAP. Then resume at U4 ROADMAP closure commit, then U4 Phase 3 design.

---

## WHO YOU'RE WORKING WITH

Operator is Druid, co-founder OMI Group Holdings (trading division OMQS). Algorithmic prediction-market trading on Kalshi. Direct, technically precise, pushes back on premature conclusions and is consistently right when he does. Expects honest evaluation, not validation. Carries conviction; expects the same.

---

## SYSTEMS ACCESS

- **VPS:** `ssh root@104.131.191.95`
- **Workspace:** `/root/Omi-Workspace`, primary subdirs `arb-executor/` and `arb-executor/docs/`
- **GitHub:** `github.com/OMIGROUPOPS/Omi-Workspace`
- **tmux:** `tmux attach -t arb` for live trading session
- **CC (Claude Code):** primary server-side execution agent. Chat drafts and verifies; CC executes.

### Key data sources (read-only unless flagged)
SQLite. Key tables:
- `historical_events` — C-tier match-level aggregates (Jan 2 – Apr 10), 14 cols incl first/min/max/last per side, total_trades
- `matches` — operational records (live + live_log + backfill), entry_time NULL on every live row per F17
- `book_prices` — sharp consensus (Pinnacle especially), 3M rows, Apr 19+ ONLY (no overlap with historical_events)
- `kalshi_price_snapshots` — 290K rows incl volume_24h, Apr 21+ ONLY
- `live_scores` — final outcomes only per A25/A27, p1_games/p2_games empty
- Plus 4 underexplored tables (bookmaker_odds=junk per F15, edge_scores, dca_truth, players)

### Ephemeral working files (/tmp)
Per F28 these can disappear. Critical ones:
- `/tmp/kalshi_fills_history.json` — Tier-A fact source (re-pullable)
- `/tmp/u4_phase1_match_landscape.csv` (1.04 MB, 5,879 matches) — Session 4 analysis output
- `/tmp/u4_phase1_match_landscape.py` — script
- `/tmp/u4_phase2_loser_bounce_by_strata.csv` (8.1 KB, 92 strata) — Session 4 analysis output
- `/tmp/u4_phase2_loser_bounce_predictors.py` — script
- `/tmp/u4_phase2_loser_bounce_summary.txt` — text summary
- `/tmp/harmonized_analysis/DEPRECATED_USE_corrected_analysis.txt` — deprecation marker placed Session 4
- `/tmp/corrected_cell_economics.py` — canonical cell economics methodology (Sw/Sl decomposition)
- `/tmp/validate_and_optimize.py` — canonical portfolio optimization
- `/tmp/bug4_brief.md` v3 — Bug 4 design (no implementation)
- `/tmp/bug4_probe.md` — pre-impl probe (sandbox test deferred)
- `/tmp/fills_history_pull.py` — Tier-A fact source producer

---

## WHAT SESSION 4 ACCOMPLISHED

### Phase 1: Built the durable doc system
Five interconnected files matching same discipline (categorized, indexed, append-only):
- LESSONS.md grew from 91 → 147 lessons
- TAXONOMY.md scaffolded and fully populated
- ANALYSIS_LIBRARY.md cataloged ~30 prior analyses with per-question canonicals
- ROADMAP.md restructured from flat list to categorized T/F/U/G/D system

### Phase 2: Closed all 12 foundational items (T1-T12)
- T1: ROADMAP refresh (CLOSED)
- T2: Tier-counter (PARTIALLY CLOSED — A-tier landed 854 events, B-tier OOM'd at 515M rows, see T13)
- T3: executor_core.py write target (CLOSED — legacy cross-platform arb code, no tennis impact)
- T4: arb-executor-v2 inventory (CLOSED — legacy fork, zero tennis content)
- T5: Snapshot dir investigation (CLOSED — /root/Omi-Workspace/tmp/ is curated git-tracked archive, NOT single snapshot)
- T6: bbo_aw1/aw2 inventory (CLOSED — paired-snapshot drift framework, distinct from entry_price_bias)
- T7: Canonical bias file (CLOSED — entry_price_bias.csv canonical for B-tier era; +21-37c vs 10.6c was aggregation-level difference not contradiction)
- T8: Canonical scorecard (CLOSED — 8 scorecard files answer 8 distinct questions, per-question canonicals not fragmentation. UNCALIBRATED count verified 30/67)
- T9: Canonical "ultimate cell economics" (CLOSED — corrected_cell_economics.py canonical for methodology, validate_and_optimize.py canonical for portfolio. 2 superseded scripts marked. Deprecation marker placed at /tmp/harmonized_analysis/)
- T10: Entry-time derivation (CLOSED — MAJOR DISCOVERY: kalshi_fills_history.json is Tier-A fact source. Closes F17/F9/F8/A26/F10 partially or fully)
- T11: Bug 4 status (CLOSED — fully designed, ZERO implementation written. Split into T11a impl + T11b sandbox. Analytical impact mitigated by T10; operational remains)
- T12: Security exposures (AUDITED, DEFERRED to operator timing — not blocking analysis)

### Phase 3: First analysis with intention (U4)
**U4 Phase 1: Match landscape characterization.**
Continuous, no pre-defined cells. 5,879 matches with all relevant variables.
- Bounce asymmetry confirmed at population level: winner median ~35c, loser median ~12-16c
- 33% of matches have first_price_winner + first_price_loser >5c off 100 (per A19, first_price unsynchronized between sides)
- Pinnacle FV join FAILED: book_prices Apr 19+ vs historical_events Jan 2 - Apr 10 = zero date overlap
- volume_24h same problem: kalshi_price_snapshots Apr 21+ only

**U4 Phase 2: Loser-bounce predictors.**
Stratified the synchronized subset (3,936 matches) by 7 dimensions.
- **Volume is the canonical predictor.** 33pp swing: 50-99 trades = 34.3% bilateral capture at +10c, 1000+ trades = 76.4%
- 70.7% April 14 anchor was subset-averaged. High-volume regime is 76.4%; low-volume is much lower
- Skew cliff at >35 is partially CEILING ARTIFACT (heavy side at 85-89c can't bounce 15c without exceeding 99c). Per E21 confirmed structurally but reason is math not edge
- Aggregate +10c on synchronized subset: 62.83%
- Categories track within 6pp; ATP_CHALL=63.1%, ATP_MAIN=63.5%, WTA_MAIN=64.3%, WTA_CHALL=56.8%
- Duration 2-4h matches strongest for bilateral (68.3%)

**Strategic conclusion (operator-validated):** High-volume matches (1000+ trades) are bilateral candidates. Low-volume are single-side or skip. Volume should be primary partition axis going forward.

**CRITICAL CAVEAT (operator-flagged late session):** U4 used historical_events match-level aggregates (first/min/max/last across entire match window). This conflates **premarket scalping** and **in-match scalping** — two structurally different opportunities. The 76.4% high-volume figure is unioned across both. Decomposition required for strategy-actionable findings. Captured in B14 + G17 + U4 Phase 3 (next-session priority).

### Phase 4: Lessons that emerged from this session

Notable additions beyond the 91 → 147 jump:
- **A30:** server-side fill history is canonical source for operational bot questions
- **A31:** volume is primary predictor of bilateral capture (33pp swing across volume strata)
- **B13:** threshold metrics on bounded variables produce ceiling artifacts
- **B14 (operator-flagged):** match-level aggregate columns conflate premarket vs in-match opportunities
- **C16:** methodology-correction commits should mark prior outputs (deprecation marker pattern)
- **C17:** security audits must redact credentials within audit script (Session 4 audit leaked the PAT it was measuring)
- **D10:** chat-drafted lesson numbers drift from on-disk after Path 1 renames; pre-flight with dynamic on-disk reads
- **E29:** foundational close-out items can produce findings that close OTHER lessons (T10's discovery of kalshi_fills_history.json closed F17/F9/F8/A26/F10)
- **E30:** aggregate findings from prior analyses may be subset-averaged in ways that obscure strategic structure (the 70.7% headline)
- **F26:** live_v3 JSONL covers Apr 24+ only; Apr 17-23 had 0 entry events despite 393MB log content
- **F27:** scanner_pendulum.log cited in LESSONS Section 4 does not exist on disk
- **F28:** /tmp is ephemeral on this VPS
- **G17 (operator-flagged):** Premarket vs in-match bounce decomposition is required for strategy-actionable findings (U4 Phase 3 candidate)

---

## CURRENT STATE — WHAT'S OPEN

### ROADMAP T-items (To-Do, OPEN)
- **T11a:** Bug 4 implementation per bug4_brief.md v3. WS lifecycle handler + REST settlements poll fallback + partial-exit P&L formula + paper-mode gating + B4-T1..T11 test suite. Deferred per D6.
- **T11b:** Bug 4 sandbox test. Capture real settled event from Kalshi sandbox. Depends on T11a.
- **T13:** Tier-counter B-tier OOM-resilient retry. Stream tickers to disk (jsonl append) instead of in-memory set. Populates TAXONOMY Section 1 B-tier match counts.
- **T14:** kalshi_fills_history.json re-pull schedule. Per F28 ephemerality risk. File is currently 17+ hours stale.
- **T16 (implicit, not yet added):** CC bootstrap reads LESSONS.md at start of every session. Currently chat is the only filter applying lessons; CC just executes prompts. This is a real gap — chat-side filter-failure mode is real risk.

### ROADMAP F-items (Flags, ongoing)
F1 /tmp ephemerality | F2 harmonized_analysis files retained on disk | F3 stale references in LESSONS Section 4 | F4 Apr 17-23 fill detection broken locally (mitigated by T10) | F5 bookmaker_odds junk-drawer | F6 live_scores final-only | F7 matches.entry_time NULL | F8 matches.settlement_time two writers | F9 players.last_updated UTC outlier | F10 Path 1 lesson-number renames

### ROADMAP U-items (Unknowns, blocking strategic decisions)
U1 matches table corruption magnitude | U2 right cell definition | U3 Channel 1 vs Channel 2 bounce decomposition | **U4 (PARTIALLY ANALYZED Session 4 — see strategic conclusion above)** | U5 30 UNCALIBRATED cells (count VERIFIED 30/67) | U6 58 still-resting Apr 24-29 positions | U7 Channel 2 attribution to game events | U8 inverse-cell cross-check | U9 Apr 24 retune isolation problem

### ROADMAP G-items (Gaps, work that doesn't exist)
- **G1:** A-tier-era bias measurement (Apr 18+ window using 27-col premarket_ticks)
- **G2:** Depth-3 capacity analysis using 5-deep depth columns
- **G3:** Depth-4 microstructure using is_taker (now available per T10)
- **G4:** Per-cell economics on cleaned data
- **G17 (operator-flagged):** Premarket vs in-match bounce decomposition (U4 Phase 3 candidate)

### ROADMAP D-items (Decisions awaiting operator)
- **D1:** Delete /tmp/harmonized_analysis/ outputs
- **D2:** Kill heavy collectors during analysis
- **D3-D4:** Rotate GitHub PAT and Kalshi key (deferred)
- **D5:** /tmp ephemerality migration (which files to make durable)
- **D6:** Bug 4 implementation prioritization
- **D7:** Security rotation execution playbook (when prioritized)

---

## NEXT-SESSION PRIORITIES

**1. U4 Phase 3 — premarket vs in-match decomposition.** This is operator-flagged (B14, G17). The 76.4% high-volume figure from U4 Phase 2 is unioned across both windows. Decomposition is required to design strategy for either window because they have distinct risk profiles.

Approach: Use B-tier `bbo_log_v4.csv.gz` (515M rows, Mar 20 - Apr 17 ET) with `commence_time` filter from historical_events to split each match's BBO ticks into premarket (timestamp < commence_time) vs in-match (timestamp >= commence_time). Compute bounce magnitudes separately for each window. Decomposed bilateral capture rates should reveal whether the U4 Phase 2 finding holds for premarket alone, in-match alone, or only their union.

Memory consideration: B-tier OOM'd in T2 at 515M-row set accumulation. Must use streaming pattern (jsonl append, aggregate post-stream).

**2. U4 ROADMAP closure commit.** This was being drafted when session ended. Should:
- Update U4 status from "Analysis target" to "PARTIALLY ANALYZED 2026-04-30" with strategic conclusion
- Add U4 Phase 3 placeholder pointing at G17
- Add ANALYSIS_LIBRARY entry for u4_phase1 + u4_phase2 scripts and outputs

**3. T16 (CC-LESSONS-bootstrap).** Operator-flagged: CC isn't reading LESSONS on every run, chat is. Add ROADMAP item for CC bootstrap pattern (CC reads LESSONS.md as first action of every session, OR analysis scripts read relevant LESSONS sections inline). This is the kind of discipline gap that compounds — fix now while operator's awareness is fresh.

**4. T13 (B-tier tier-counter retry)** if Phase 3 needs B-tier match counts populated in TAXONOMY.

**5. T14 (kalshi_fills_history.json re-pull schedule)** for any operational fill analysis. File is 17+ hours stale.

---

## KEY OPERATING PATTERNS (Session 4 learnings)

### CC interaction
- One CC prompt per turn. Never bundle. Wait for CC to finish.
- CC prompt format: opens with "Read-only." or describes the action; gives ssh command; ends with "Stop there." or similar.
- File-staging pattern when content too long for command line: write to /tmp via heredoc with sentinel `OMIDOCEND_4F4620FF`, then act on the file.
- CC executes server-side; chat drafts and verifies.

### Pre-flight assertion pattern (D10)
Every multi-anchor str_replace or lesson-insertion script must use **dynamic on-disk number reads** via `last_num()` function pattern. Never hardcode lesson numbers from chat history — chat-drafted numbers drift one ahead of on-disk after Path 1 renames. This was discovered three times in Session 4 before D10 was codified. After D10 + dynamic reads adopted, no further drift.

```python
def last_num(cat):
    matches = re.findall(rf'^{cat}(\d+)\.', doc, re.MULTILINE)
    return max(int(n) for n in matches) if matches else 0
```

### Single-concern commits
Each commit single concern (factual additions land immediately, structural batch later). Never combine "add lesson X" + "rename roadmap" + "fix typo" in one commit.

### When operator pushes back
Operator pushes back when chat shows low-confidence framing or when chat asks for pushback as a habit. **Carry conviction, don't bounce decisions back.** When you have a read, state it. Disagreement should be substantive, not procedural.

### Pre-rotation security awareness
T12 audit script leaked the PAT it was measuring. Every audit command touching credentials must include redaction in the same command. `git remote -v | sed 's|//[^@]*@|//[REDACTED]@|'` not raw `git remote -v`.

---

## CHANGES NOT YET COMMITTED

Nothing — every commit landed. Last commit: `d182393` (G17 reposition).

The U4 ROADMAP closure was drafted but interrupted at "wait actually let me stop you. time to handoff." Drafts to recreate next session:
- ROADMAP U4: change "Analysis target." to "PARTIALLY ANALYZED 2026-04-30" + strategic conclusion + Phase 3 pointer
- ANALYSIS_LIBRARY: add entries for u4_phase1_match_landscape.py and u4_phase2_loser_bounce_predictors.py with input/output/methodology

These are not blocking; can land first thing next session.

---

## WHAT'S WORKING / WHAT TO TRUST

### Trust
- LESSONS.md content (147 lessons). Every one is sourced from a probe or analysis result, not memory.
- TAXONOMY.md TZ labels (verified ET / verified UTC / verified tz-agnostic flagged explicitly per source per column).
- ANALYSIS_LIBRARY.md per-question canonicals (each entry verified against producer script).
- kalshi_fills_history.json as Tier-A fact source for fill questions.
- corrected_cell_economics.py as canonical methodology (Sw/Sl decomposition).
- entry_price_bias.csv as canonical bias for B-tier era only.

### Don't trust without re-verifying
- Anything in /tmp (per F28 ephemerality)
- Pre-Session-4 ROADMAP framings (some were superseded mid-session, e.g. A28 partially superseded by A29)
- "977 fills" headline (per F26 the universe split across 4 time windows with different recovery sources)
- Match-level aggregates (per B14 conflate time windows)
- Aggregate findings from undocumented subsets (per E30)

### Watch for
- Path 1 renames (per D10 pattern)
- Off-by-one drift between chat-drafted and on-disk lesson numbers
- Pinnacle/volume_24h join silently failing on date-overlap mismatch
- Premarket vs in-match conflation in any new analysis
- /tmp file disappearance

---

## OPERATOR'S SESSION 4 NOTES

Druid raised these mid-session:
- "no current way of doing anything is locked. lets get creative" — applied to U4 cell-definition decision
- "you and asking me for pushbacks. where is your conviction" — chat pattern correction
- "again, objective answers here for what ive told you to be" — operator-stance alignment
- "this is why weve been pushing the lessons" — affirmation of doc-system value
- "remember there are 2 opportunities to cash a scalp. premarket and full game" — late-session insight that became B14/G17

These shape next-session expectations.

---

**End of handoff. Next session: read README → this file → LESSONS → TAXONOMY → ANALYSIS_LIBRARY → ROADMAP. Then resume at U4 ROADMAP closure commit, then U4 Phase 3 design.**
