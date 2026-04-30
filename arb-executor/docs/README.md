# OMI Operating Library — README

This directory contains the operating library for the OMI tennis trading operation. Future chat sessions and CC instances must read this README first, then read modules in the order listed.

**Repo:** github.com/OMIGROUPOPS/Omi-Workspace
**VPS:** root@104.131.191.95
**Working dir:** /root/Omi-Workspace/arb-executor/

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

2026-04-30 — Session 4. Initial creation of module scaffolding.
