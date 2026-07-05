# PLEX RE-ANCHOR RULING — reserved slot (VERBATIM TEXT NOT YET RECEIVED)

> ⚠ **THE RELAY DROPPED THE RULING BODY.** The operator's message to CC contained the
> literal placeholder `[paste the full Plex ruling from the operator's message]` — the
> long-content drop the operator himself warns the chat channel produces. Per D15/D16
> discipline CC does NOT reconstruct verbatim Plex text from memory or inference.
> **Operator: paste the ruling body; it replaces this banner verbatim, nothing else in
> this file moves.** All rulings live on git from this point (standing order).

## Operative constraints as relayed (OPERATOR'S WORDS, not Plex verbatim)

Two preconditions BEFORE the Part 1 diff (answered in `PART1_SPEC.md`):
1. **TE/ESPN state file: freeze the schema.** Path, refresh mechanism (15-min cycle),
   format, stability documented; anything fluid gets frozen first. The clock helper
   must read a frozen, documented target.
2. **The staleness fallback, explicit.** The documented rule for stale/missing
   state-file entries: fall back to the Kalshi placeholder + widen the window by a
   stated X per category, X derived from the clock audit's offset distributions
   (placeholder runs ~+1.8h CHALL / ~+4.4h ITF late). In the spec, not inferred at
   build time.

Part 1 (per the ruling): **per-match clock helper + windowing rewire** —
- gated flag, default OFF, byte-identical off;
- both clocks visible in logs (shadow);
- AST sweep on the critical-method list: new-differs = exactly the intended methods;
- scope confinement: NO reach into exit, completion (BOTH mechanisms:
  completion_reprice AND complete_cross), meter, or routing;
- **tape supremacy absolute: NO clock touches liveness/abandon — grep-proof at the
  diff; latch_tape_override semantics explicitly preserved;**
- pure-helper verification: no awaits / state-writes / IO per tick;
- tests exercising the REAL bodies (AST-extract pattern, per 706cb3c/47fa2ff).

Part 3 in parallel: **scale-aware gun SHADOW** — data collection on gun agreement
only, no consumers switched.

Session deliverables: ruling committed · Part-1 spec (schema freeze + fallback rule) ·
Part-1 diff STAGED (not armed) for Plex's source-level gate · Part-3 shadow staged
likewise. Standing law: lint + smoke pre-arm, monitor post-arm, one change at a time.
**The bot untouched until Plex ratifies the diffs.**
