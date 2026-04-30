# OMI Roadmap — Current State and Forward Work

**Purpose:** Source of truth for current to-do state of the OMI tennis trading operation. In-flight, queued, blocked, recently completed. Updated continuously as work progresses; future chats consult this to know what is happening now and what is next.

**Cross-references:**
- Foundational framing: LESSONS.md Section 1 (where we actually stand) and Section 6 (known unknowns).
- Classification language: TAXONOMY.md.
- Prior work: ANALYSIS_LIBRARY.md.

**Last updated:** 2026-04-30 ~14:00 ET, mid-Session 4.

---

## SECTION 1: PHASE

**Current phase: Foundational, not tactical.** Per LESSONS.md Section 1.

We are not optimizing config. We are not picking cells to enable. We are rebuilding our ability to trust per-cell metrics. Specifically: classifying data sources by tier, classifying analyses by depth, and re-validating prior anchor findings before any redeployment.

Within the foundational phase, current sub-phase is: **building the durable module library** (LESSONS / TAXONOMY / ANALYSIS_LIBRARY / ROADMAP) and populating it from systematic data probes. Once populated, we move to first analysis with intention.

---

## SECTION 2: IN FLIGHT

- **Tier-count CC probe** (background task ID bonjf68wx, started Apr 30 12:03 PM ET). Streaming 515M-row B-tier gzip plus A-tier file scan plus C-tier sqlite query. Output will populate TAXONOMY.md Section 1 (per-tier match counts per category, both-sides coverage) and Section 3 (depth × tier matrix refinements). Status: running ~2hrs as of 14:00 ET. Long pole was the gzip stream; contention with concurrent variable-inventory probe earlier may have slowed it.

---

## SECTION 3: QUEUED (drafted, awaiting send)

- **TZ follow-up probe.** Verify bbo_log_v4 timestamp tz (currently LIKELY ET, UNVERIFIED) and the naive polled_at columns in book_prices, kalshi_price_snapshots, live_scores. Method: grep tennis_v5.py for the actual write line that produces bbo_log_v4 timestamp; check VPS code for write paths into the polled_at columns. Send after tier-counter completes to avoid further contention.
- **TAXONOMY.md Section 4 full population.** Drafted in chat; needs verified tz labels per column from the TZ follow-up before final write. Will include full column listings for A-tier (27 columns), trades CSV (5 columns), B-tier (5 columns), C-tier historical_events (14 columns), book_prices (12 columns), kalshi_price_snapshots (9 columns), live_scores (11 columns) with A25 limit annotation, bookmaker_odds with F15 deprioritization annotation, edge_scores, dca_truth, matches with F17/F18 annotations, players, name_cache, betexplorer_staging.
- **TAXONOMY.md Section 1 match-count population.** Awaits tier-counter output. Will fill per-tier per-category match counts and tier-overlap matrix.
- **Depth-inventory CC probe.** Catalog every analysis script in /tmp and /root/Omi-Workspace by intent (read first comment lines), every result file with sample content. Output populates ANALYSIS_LIBRARY.md Section 2 (analyses-by-depth) and Section 3 (broken/invalid).
- **ANALYSIS_LIBRARY.md population.** After depth-inventory probe lands.

---

## SECTION 4: BLOCKED

- **70.7% reproduction analysis.** Blocked on TAXONOMY.md Section 4 being populated. Once unblocked, will pressure-test E18/E25 by reproducing the rate on current data and stratifying per-cell.
- **Per-cell bilateral double-cash rate.** Blocked on 70.7% reproduction completing.
- **Channel 2 attribution to game events.** Originally hoped for via live_scores, but live_scores is final-outcome only per A25/A27. Blocked pending alternative game-state source (Kalshi live_data API, ESPN scrape, or other).
- **Bug 4 (settlement event detection).** Lower priority than foundational classification work. Tracked in LESSONS.md Section 6.

---

## SECTION 5: KNOWN UNKNOWNS (from LESSONS.md Section 6)

These are open questions blocking strategic decisions. Not currently being worked on; tracked here for visibility.

- Magnitude and distribution of data corruption in the 977-fill matches table records. (F7 unresolved, partially expanded by F17 — entry_time NULL on live — and F18 — settlement_time two writers.)
- Right cell definition. Current scheme is tier × side × 5c price band. Open: granularity, redundancy of direction with price, tier as primary or secondary partition.
- Per-cell average bounce, decomposed by Channel 1 vs Channel 2, on uncorrupted data.
- Per-cell bilateral double-cash rate (extends April 14 finding).
- Bias correction reconciliation. Canonical bias file vs run1 vs operator memory disagreement.
- 30 UNCALIBRATED cells in rebuild scorecard.
- 58 still-resting Apr 24-29 positions: outcomes unknown until they exit or settle.
- Inverse-cell cross-check on real data.
- Apr 24 retune isolation problem.
- arb-executor-v2 directory contents.
- /tmp/bbo_aw1.csv and /tmp/bbo_aw2.csv vs canonical bias file.
- Channel 2 game-event attribution (added this session, blocked).

---

## SECTION 6: RECENTLY COMPLETED (Session 4, Apr 30)

Earliest first within the session.

- **LESSONS.md created** with foundational framing: bot is shut down, foundation not trustworthy, work is foundational not tactical. (Initial 91 lessons.)
- **LESSONS.md changelog count corrected** (98 lessons, math fix).
- **A24, E25, E26 added** (variable inventory as foundation, 70.7% reclassified as depth-0, depth and variables are parallel axes). 107 lessons.
- **Module scaffolding created:** README.md, TAXONOMY.md, ANALYSIS_LIBRARY.md, ROADMAP.md committed in single commit c794b26.
- **Variable-inventory CC probe completed.** Schemas of all tennis.db tables, premarket_ticks 27-column confirmation, trades CSV 5-column with taker_side confirmation, bbo_log_v4 5-column header confirmation. Findings: live_scores is final-outcome only (not in-match state); book_prices is canonical sharp-consensus source; bookmaker_odds is partial junk-drawer.
- **A25, A26, D7, D8, F13, F14, F15 added** from variable-inventory results. 114 lessons.
- **TZ probe completed.** Three timezone conventions identified across data sources: explicit ET (A-tier ts_et, JSONL ts), explicit UTC (historical_events first/last_ts, all commence_time fields), naive (B-tier bbo_log_v4 timestamp, polled_at columns — likely ET via VPS system clock but UNVERIFIED). Discovered: matches.entry_time NULL on every live/live_log row; matches.settlement_time has two writers with different formats.
- **F16, F17, F18 added** from TZ probe. 117 lessons.

Still in flight: tier-count CC probe (started 12:03 PM, ~2hrs running).

---

## SECTION 7: NEXT MOVES (immediately after current ROADMAP commit)

1. **Send TZ follow-up probe** to verify bbo_log_v4 timestamp tz and naive polled_at columns. (Section 3 queued item.)
2. **Wait for tier-counter to complete.** Integrate output into TAXONOMY.md Section 1 in single commit.
3. **Populate TAXONOMY.md Section 4** with full variable inventory + verified tz labels in single commit.
4. **Send depth-inventory probe.** Catalog prior analyses in /tmp and /root/Omi-Workspace.
5. **Populate ANALYSIS_LIBRARY.md** from depth-inventory results.
6. **First analysis with intention.** Once all four modules are populated, pick from Section 4 BLOCKED items (most likely 70.7% reproduction + per-cell stratification on B-tier data) and design the analysis grounded in TAXONOMY.

---

## SECTION 8: CHANGELOG

- 2026-04-30 ~13:21 ET: Initial scaffolding creation (commit c794b26). Sections 2, 3, 4, 6 populated with state at that moment.
- 2026-04-30 ~14:00 ET (this commit): Updated to reflect mid-session state. Variable-inventory and TZ probes completed; tier-counter still running. F16-F18 lessons landed. TAXONOMY Section 4 population queued pending TZ follow-up.
