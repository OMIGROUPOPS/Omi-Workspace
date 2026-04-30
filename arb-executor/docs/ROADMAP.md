# OMI Roadmap — Current State and Forward Work

**Purpose:** Source of truth for current to-do state of the OMI tennis trading operation. In-flight, queued, blocked, recently completed. Updated continuously as work progresses; future chats consult this to know what is happening now and what is next.

**Cross-references:**
- Foundational framing: LESSONS.md Section 1 (where we actually stand) and Section 6 (known unknowns).
- Classification language: TAXONOMY.md.
- Prior work: ANALYSIS_LIBRARY.md.

**Last updated:** 2026-04-30 ~15:10 ET, mid-Session 4.

---

## SECTION 1: PHASE

**Current phase: Foundational, not tactical.** Per LESSONS.md Section 1.

We are not optimizing config. We are not picking cells to enable. We are rebuilding our ability to trust per-cell metrics. Specifically: classifying data sources by tier, classifying analyses by depth, and re-validating prior anchor findings before any redeployment.

Within the foundational phase, current sub-phase is: **closing every outstanding foundational item before running any analysis.** The four content modules are populated (LESSONS, TAXONOMY, ANALYSIS_LIBRARY, ROADMAP). The remaining work is resolving the foundational unknowns and canonical-source designations cataloged in this ROADMAP. Only after every item below is closed do we proceed to first analysis with intention.

---

## SECTION 2: IN FLIGHT

- **Tier-count CC probe** (background task ID bonjf68wx, started Apr 30 12:03 PM ET, now ~3hr running). Streaming 515M-row B-tier gzip plus A-tier file scan plus C-tier sqlite query. Output will populate TAXONOMY.md Section 1 (per-tier match counts per category, both-sides coverage). CPU-starved by concurrent collectors (mlb_bbo_logger, live_v3 paper, te_live, etc.) — operator decision: let it grind. Status: healthy, slow.

---

## SECTION 3: FOUNDATIONAL TO-DO (every item below must close before analysis)

Order is dependency-driven. Items reference lessons that motivate them.

1. **ROADMAP refresh** (this commit). Lock in current state.
2. **Tier-counter completion.** Wait. Populate TAXONOMY Section 1 match counts on landing. Currently running.
3. **executor_core.py write target.** Per TZ probe finding: line 1023 has `datetime.utcnow().isoformat() + "Z"` write. Determine what column/file this writes. If a current DB writer, TZ inventory is not final until this column is classified. Per F16/F20.
4. **arb-executor-v2/ directory inventory.** Per LESSONS Section 6: contents not yet inventoried. Could contain canonical implementations of analyses currently fragmented across /tmp. Must inspect before designating canonical sources.
5. **Snapshot dir investigation.** /root/Omi-Workspace/tmp/ has single-mtime snapshot from Apr 29 17:43 per depth-inventory probe. Understand what triggered the snapshot before treating /tmp as canonical for ANALYSIS_LIBRARY entries.
6. **/tmp/bbo_aw1.csv and /tmp/bbo_aw2.csv inventory.** Per LESSONS Section 6: "first observed vs late-game BBO snapshot pairs, likely the source for bias correction." Compare against canonical bias file before designating canonical.
7. **Canonical bias file designation.** Per F19: six+ bias files exist measuring overlapping concepts. Inventory what each file measures (which baseline, which window, which subset). Designate canonical. Document in ANALYSIS_LIBRARY. Resolves the +21-37c vs 10.6c known unknown.
8. **Canonical scorecard designation.** Per A28: multiple competing scorecards (rebuilt_scorecard, bootstrap_ci_results, optimal_exits) with no source-of-truth tracking. Designate canonical. Document in ANALYSIS_LIBRARY.
9. **Canonical "ultimate cell economics" designation.** Per E27: multiple competing implementations (ultimate_cell_economics, ultimate_cell_economics_csv, corrected_cell_economics, validate_and_optimize, scalp_constrained_optimize). Designate canonical or explicitly retire others.
10. **Entry-time derivation from JSONL.** Per F17: matches.entry_time NULL on 977 live/live_log rows. Derive clean entry-time column from JSONL ts (verified ET) for each of the 977 fills. Output as portable CSV/parquet for downstream analysis use.
11. **Bug 4 status check.** Per F8: settlement event detection broken when bot resting sell unfilled at market close. Either blocking ongoing analysis or actively being remediated. Determine current status; if remediation in progress, document expected completion.
12. **Security exposures rotation.** Per session note: GitHub PAT in git remote URL plus plaintext Kalshi API key in probe_kalshi_api2.py. Both in public repo. Rotate both keys. Verify no other exposed secrets.

---

## SECTION 4: BLOCKED — DEPENDS ON SECTION 3 COMPLETION

- **70.7% reproduction analysis.** Per E18/E25.
- **Per-cell bilateral double-cash rate.** Per E18/E21/E22.
- **Channel 2 attribution to game events.** Per A25/A27 — also needs alternative game-state source.
- **First analysis with intention** (whatever it turns out to be).

---

## SECTION 5: KNOWN UNKNOWNS (from LESSONS.md Section 6)

These are open questions blocking strategic decisions. Some are absorbed into Section 3 above; others stay tracked here for visibility.

- Magnitude and distribution of data corruption in the 977-fill matches table records (partially expanded by F7, F17, F18; full magnitude still unmeasured)
- Right cell definition (strategic question, not foundational; deferred until foundation complete)
- Per-cell average bounce decomposed by Channel 1 vs Channel 2 (analysis target, not foundation)
- 30 UNCALIBRATED cells in rebuild scorecard (depends on canonical scorecard — Section 3 #8)
- 58 still-resting Apr 24-29 positions (wait-and-see)
- Inverse-cell cross-check on real data (analysis target, not foundation)
- Apr 24 retune isolation problem (historical forensics, deferred)

---

## SECTION 6: RECENTLY COMPLETED (Session 4, Apr 30)

- **LESSONS.md created.** 122 lessons across 7 categories: A=27, B=10, C=14, D=8, E=27, F=20, G=16.
- **Module scaffolding** (README, TAXONOMY, ANALYSIS_LIBRARY, ROADMAP) created.
- **Variable-inventory CC probe** completed. tennis.db full schemas, premarket_ticks 27-column confirmation, trades CSV taker_side confirmation. Findings: live_scores final-outcome only; book_prices canonical sharp consensus; bookmaker_odds junk-drawer.
- **TZ probe** completed. Three timezone conventions identified. Verified bbo_log_v4 ET, all polled_at columns ET, live_scores.last_updated ET, players.last_updated UTC (F20 outlier).
- **TZ follow-up probe** completed. Inferred rows promoted to VERIFIED.
- **Depth-inventory CC probe** completed. ~30 distinct analyses cataloged across 6 depth levels.
- **TAXONOMY.md Section 4** fully populated with verified TZ labels (commit 49613eb).
- **ANALYSIS_LIBRARY.md Sections 2-4** fully populated (commit 85daa0a).
- **Lessons added this session** in order: changelog correction, A24 + E25 + E26, A25 + A26 + D7 + D8 + F13 + F14 + F15, F16 + F17 + F18, A27 + C14 + E27 + F19, F20.

---

## SECTION 7: NEXT MOVES (after this ROADMAP commit)

Per Section 3 dependency order:

1. (this commit completes item 1)
2. Wait on tier-counter (item 2). Concurrent work below does not contend with it (no gzip reads).
3. Run executor_core.py write target probe (item 3).
4. Run arb-executor-v2 inventory probe (item 4).
5. Run snapshot dir investigation probe (item 5).
6. Run bbo_aw1/aw2 inventory probe (item 6).
7. Designate canonical bias file (item 7) after items 4-6 complete.
8. Designate canonical scorecard (item 8).
9. Designate canonical "ultimate" economics (item 9).
10. Run entry-time derivation script (item 10).
11. Bug 4 status probe (item 11).
12. Security rotation (item 12).
13. ALL ITEMS CLOSED. Re-read ROADMAP. Pick first analysis.

Each item resolves to either a CC probe + finding, or a designation + ANALYSIS_LIBRARY update, or a code change. Each closes with a commit so progress is durable.

---

## SECTION 8: CHANGELOG

- 2026-04-30 ~13:21 ET: Initial scaffolding (commit c794b26).
- 2026-04-30 ~14:00 ET: First update reflecting variable-inventory and TZ probes complete (commit cac13c4).
- 2026-04-30 ~15:10 ET (this commit): Section 3 added — full foundational to-do list with dependency ordering. 12 items must close before any analysis. Section 6 reflects all module population complete. Section 7 sequences the close-out.
