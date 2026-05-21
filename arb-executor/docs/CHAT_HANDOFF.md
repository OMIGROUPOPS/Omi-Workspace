# CHAT_HANDOFF.md — consolidated into SESSION_HANDOFF.md

This file's content was consolidated into `docs/SESSION_HANDOFF.md` during the Stage 0 reconcile of 2026-05-21 ET (commit `8772407`).

The prior two-doc pattern (SESSION_HANDOFF.md for cumulative memory + CHAT_HANDOFF.md for next-session-start orientation) had created a sync burden: both docs would drift stale in nearly identical ways. SESSION_HANDOFF.md now absorbs both functions — top section is orientation, middle is durable context, lower is current operational state + uncertainties + commit trail.

**Canonical successor:** `docs/SESSION_HANDOFF.md`.

**Historical:** Prior CHAT_HANDOFF.md content (last touched 2026-05-15 at commit `7911478`, "post-Rung-0-landing state with Plex column-name mappings") remains accessible via git history. The Rung 1 spec-drafting plan it described was bypassed when the atlas approach took over; see SESSION_HANDOFF.md "What just landed" + T39.1 in ROADMAP.md for current disposition.
