# OMI Roadmap — Current State and Forward Work

**Purpose:** Source of truth for current to-do state of the OMI tennis trading operation. In-flight, queued, blocked, recently completed. Updated continuously as work progresses; future chats consult this to know what is happening now and what is next.

**Cross-references:**
- Foundational framing: LESSONS.md Section 1 (where we actually stand) and Section 6 (known unknowns).
- Classification language: TAXONOMY.md.
- Prior work: ANALYSIS_LIBRARY.md.

---

## SECTION 1: PHASE

**Current phase: Foundational, not tactical.** Per LESSONS.md Section 1.

We are not optimizing config. We are not picking cells to enable. We are rebuilding our ability to trust per-cell metrics. Specifically: classifying data sources by tier, classifying analyses by depth, and re-validating prior anchor findings before any redeployment.

---

## SECTION 2: IN FLIGHT

[Currently running CC tasks or in-progress chat threads.]

- **Tier-count CC probe** (background task ID bonjf68wx, started Apr 30 ~12:03 PM ET). Counting matches per data tier (A/B/C) and per category. Long pole is streaming the 515M-row B-tier gzip. Expected output: per-tier match counts, per-category breakdown, both-sides coverage. Status: running.

---

## SECTION 3: QUEUED (drafted, awaiting send)

- **Variable-inventory CC probe.** Drafted in chat. Will send after tier-count completes. Goal: full schemas of tennis.db tables, analysis/trades CSV columns, premarket_ticks columns, bbo_log_v4 header. Output populates TAXONOMY.md Section 4.
- **Depth-inventory CC probe.** Drafted in chat. Will send after variable-inventory completes. Goal: catalog every analysis script in /tmp and /root/Omi-Workspace by intent (read first comment lines), every result file with sample content. Output populates ANALYSIS_LIBRARY.md Section 2.

---

## SECTION 4: BLOCKED

- **70.7% reproduction analysis.** Blocked on TAXONOMY.md Section 4 being populated (need to know variable inventory before designing the reproduction). Once unblocked, will pressure-test E18/E25 by reproducing the rate on current data and stratifying per-cell.
- **Per-cell bilateral double-cash rate.** Blocked on 70.7% reproduction completing.
- **Bug 4 (settlement event detection).** Blocked on prior bug brief v3 update; lower priority than foundational classification work.

---

## SECTION 5: KNOWN UNKNOWNS (from LESSONS.md Section 6)

These are open questions blocking strategic decisions. Not currently being worked on; tracked here for visibility.

- Magnitude and distribution of data corruption in the 977-fill matches table records.
- Right cell definition. Current scheme is tier x side x 5c price band. Open: granularity, redundancy of direction with price, tier as primary or secondary partition.
- Per-cell average bounce, decomposed by Channel 1 vs Channel 2, on uncorrupted data.
- Per-cell bilateral double-cash rate (extends April 14 finding).
- Bias correction reconciliation. Canonical bias file vs run1 vs operator memory disagreement.
- 30 UNCALIBRATED cells in rebuild scorecard.
- 58 still-resting Apr 24-29 positions: outcomes unknown until they exit or settle.
- Inverse-cell cross-check on real data.
- Apr 24 retune isolation problem.
- arb-executor-v2 directory contents.
- /tmp/bbo_aw1.csv and /tmp/bbo_aw2.csv vs canonical bias file.

---

## SECTION 6: RECENTLY COMPLETED (Session 4, Apr 30)

- LESSONS.md created and committed (107 lessons across 7 categories: A=24, B=10, C=13, D=6, E=26, F=12, G=16).
- Doc framing landed: bot is shut down, foundation not trustworthy, work is foundational not tactical.
- Channel 1 vs Channel 2 decomposition completed: 4.7% vs 95.3% of fills, confirming bot is in-game spike capture mechanism via passive resting sells.
- 977-fill realized P&L analysis completed: -$1,339.52 net on Mar 26 - Apr 17 operations. Bimodal distribution confirms riding-to-settlement mechanism.
- Variable inventory expanded in chat: A-tier has 27 columns, used 6; tennis.db has 7 underexplored tables.
- 70.7% double-cash rate reclassified as depth-0 existence proof, not edge validation.
- Module scaffolding (this file, README, TAXONOMY, ANALYSIS_LIBRARY) created.

---

## SECTION 7: CHANGELOG

- 2026-04-30: Initial creation. Session 4. Reflects state as of LESSONS.md commit f354e9c (107 lessons) plus this scaffolding commit.
