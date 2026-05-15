# OMI Operating Library — README

This directory contains the operating library for the OMI tennis trading operation. Future chat sessions and CC instances must read this README first, then read modules in the order listed.

**Repo:** github.com/OMIGROUPOPS/Omi-Workspace
**VPS:** root@104.131.191.95
**Working dir:** /root/Omi-Workspace/arb-executor/

## Current state (read before the modules)

The operation is in a foundation-rebuild arc. The live bot is intentionally PAUSED — all prior bot versions traded on a foundation now known to be broken. Current work is rebuilding the analytical foundation, not tactical trading.

As of 2026-05-14:
- The canonical analysis foundation is **per_minute_features.parquet** (TAXONOMY FOUNDATION-TIER, 9.33M ticker-minute rows, checkpoint 3 sha256 9fde4b5d...). It supersedes the older Layer A v1 / G9-parquet anchors.
- The cell/exit model is **locked**: the cell is the N's Kalshi price at a fixed T-20m-before-match-start mark; objective is average bounce per cell band; no stop; two exit windows; settlement is the answer key, not the objective. Full model in LESSONS E32.
- The next major analytical step is the **unit-of-analysis audit** — reclassifying every prior finding in ANALYSIS_LIBRARY against the GRAIN / VECTOR / OBJECTIVE axes (TAXONOMY Section 2.5).

Read LESSONS Section 1, ROADMAP T37, and SIMONS_MODE in full before any tactical work.

## Module index (read in this order)

1. **LESSONS.md** — Durable principles. How to behave, what mistakes to avoid, what we have learned not to repeat. Append-only with categorized indexing (A-G).

2. **TAXONOMY.md** — Formal definitions and shared language. Data tier definitions (A/B/C and beyond), analysis depth levels (0 through 6), variable inventory per source. The classification system any analysis must reference.

3. **ANALYSIS_LIBRARY.md** — Catalog of every prior analysis classified by depth, data tier, variables used, question answered, validity status, output location. Source of truth for "what has already been done."

4. **ROADMAP.md** — Current to-do state. In-flight, queued, blocked, recently-completed. Source of truth for "what is next."

## Operating principles

- Read all four modules before doing tactical work.
- Never reinvent context the modules already have.
- New lessons get categorized and added to LESSONS.md at the moment they land in conversation, not retroactively.
- New taxonomy refinements update TAXONOMY.md.
- New analyses (and re-classifications of existing ones) update ANALYSIS_LIBRARY.md.
- Plans, blockers, and status changes update ROADMAP.md.
- Each module commit has a single concern. Do not bundle module updates.

## Raw URLs (for new chats to bootstrap from)

- README: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/main/arb-executor/docs/README.md
- LESSONS: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/main/arb-executor/docs/LESSONS.md
- TAXONOMY: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/main/arb-executor/docs/TAXONOMY.md
- ANALYSIS_LIBRARY: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/main/arb-executor/docs/ANALYSIS_LIBRARY.md
- ROADMAP: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/main/arb-executor/docs/ROADMAP.md

## Last updated

2026-05-14 — brought current with the T37 foundation rebuild. Added current-state orientation block. Module index and operating principles unchanged from Session 4 — they remain correct.
