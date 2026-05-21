# OMI Operating Library — README

This directory contains the operating library for the OMI tennis trading operation. Future chat sessions and CC instances must read this README first, then read modules in the order listed.

**Repo:** github.com/OMIGROUPOPS/Omi-Workspace
**VPS:** root@104.131.191.95
**Working dir:** /root/Omi-Workspace/arb-executor/

## Current state (read before the modules)

The operation has completed the strategy-phase rebuild. The live bot is intentionally PAUSED. The next arc is execution-lock — surfacing bugs in paper mode before deploying capital.

As of 2026-05-21:
- The strategy-phase deliverable is **LOCKED**: the four-category spike volatility map atlas (T42, HEAD `d99c6e9`). 14,033 N's across ATP_MAIN / WTA_MAIN / ATP_CHALL / WTA_CHALL. Per-cell hindsight-optimal exit-or-hold rules paid +$6,158.20 on $70,813.20 capital at 10ct (blended +8.70% per-trade ROI). The strategy's opportunity floor on the corrected foundation; the execution-lock arc validates against this. Read the four LOCKED_DOWN.md files in `data/durable/spike_volatility_map/` and SESSION_HANDOFF.md's "Atlas headline" + "Three-axis caveat" sections for the canonical version.
- Foundation chain: per_minute_features T37 ckpt-3 (sha256 `9fde4b5d`) → n_profile_v1 T40 (sha256 `a7ed1155`) → inmatch_bounce_surface_v1 T41 (sha256 `14241db0`) → spike volatility map atlas T42 (HEAD `d99c6e9`). The atlas sits on this chain; treating it as if it sits directly on G9 trades misses the load-bearing intermediates.
- The cell/exit model is **locked**: cell is the N's Kalshi price at a fixed T-20m-before-match-start anchor; objective is per-cell hindsight-optimal exit-or-hold at 1c / 2c / 3c resolutions reported side-by-side; settlement is the answer key, not the objective. Full model in LESSONS E32.
- The next major step is **execution-lock**: Bug 4 (T11a/T11b) → Layer B v2 (T36) → hot-reload mechanism → paper-mode integration test suite → paper-mode run against live tape → capital deployment with safety rails. Sequence locked in SESSION_HANDOFF.md "What's next" section; full T-item detail in ROADMAP.md Section 8 "Execution-lock sequence."

Read **SESSION_HANDOFF.md in full first** before any tactical work — it's the canonical current-state doc and absorbs the orientation + durable context + current operational state that earlier versions split between SESSION_HANDOFF and CHAT_HANDOFF.

## Module index (read in this order)

0. **SESSION_HANDOFF.md** — Canonical current-state doc. Top-section orientation (what just landed, what's next), middle durable context (agent topology, working norms), bottom current operational state + open uncertainties + recent commit trail. ALWAYS the current handoff — overwrite in place at end of each session. Numbered SESSION{N}_HANDOFF.md files in `handoffs/` are frozen historical snapshots.

1. **LESSONS.md** — Durable principles. How to behave, what mistakes to avoid, what we have learned not to repeat. Append-only with categorized indexing (A-G). 558+ lessons as of Stage 0.

2. **TAXONOMY.md** — Formal definitions and shared language. Data tier definitions (A/B/C, G, FOUNDATION-TIER), analysis depth levels (0 through 6), Section 2.5 GRAIN / VECTOR / OBJECTIVE classification axes.

3. **ANALYSIS_LIBRARY.md** — Catalog of every prior analysis classified by depth, data tier, variables used, question answered, validity status, output location. Section 2 deliverables catalog + Section 4 currently-asserted findings. Source of truth for "what has already been done."

4. **ROADMAP.md** — Current to-do state. T (To-Do) / F (Flag) / U (Unknown) / G (Gap) / D (Decision) categorized indexing. Source of truth for "what is next" (Section 8 "Execution-lock sequence").

5. **SIMONS_MODE.md** — Operating philosophy. Simons-style alpha selection, peer-to-peer market structure axioms, Problem 1 (cell selection / strategy) vs Problem 2 (execution / fills) prioritization. Reference for how to think about new strategic decisions.

## Operating principles

- Read all modules before doing tactical work. SESSION_HANDOFF.md is mandatory first; the numbered modules follow as needed.
- Never reinvent context the modules already have.
- New lessons get categorized and added to LESSONS.md at the moment they land in conversation, not retroactively.
- New taxonomy refinements update TAXONOMY.md.
- New analyses (and re-classifications of existing ones) update ANALYSIS_LIBRARY.md.
- Plans, blockers, and status changes update ROADMAP.md.
- Each module commit has a single concern. Do not bundle module updates.

## Raw URLs (for new chats to bootstrap from)

- README: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/main/arb-executor/docs/README.md
- SESSION_HANDOFF: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/main/arb-executor/docs/SESSION_HANDOFF.md
- LESSONS: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/main/arb-executor/docs/LESSONS.md
- TAXONOMY: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/main/arb-executor/docs/TAXONOMY.md
- ANALYSIS_LIBRARY: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/main/arb-executor/docs/ANALYSIS_LIBRARY.md
- ROADMAP: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/main/arb-executor/docs/ROADMAP.md
- SIMONS_MODE: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/main/arb-executor/docs/SIMONS_MODE.md

## Last updated

2026-05-21 — Stage 0 reconcile commit 8 of 9. Current-state block updated for atlas lock (HEAD `d99c6e9`); module index expanded to include SESSION_HANDOFF.md (now canonical current-state doc absorbing the old CHAT_HANDOFF pattern) and SIMONS_MODE.md (operating philosophy reference); raw URLs updated correspondingly. Module-index read order shifted to place SESSION_HANDOFF first as the read-before-anything doc.
