# PLEX EXPRESSION INVARIANT RULING — (relayed 2026-07-07 with the net-of-self build dispatch)

**Provenance:** cited by the operator inside the C-EX-SELF build dispatch; committed here
verbatim-as-relayed (REANCHOR slot precedent if a fuller body exists).

## Ruled (as relayed)
- **JOIN/IMPROVE ratified**: expression vs the NON-SELF chain — rest AT target when
  target <= bid_ex_self; a target above the chain joins it or improves by EXACTLY 1c.
- **NEVER-MARKETABLE: unconditional, immediate** — no maker buy posts at >= best_ask,
  every placement site.
- **Mid-spread creation: DEFERRED** (census says rare/cheap; ruled later with shadow evidence).

## Implementation (C-EX-SELF build, this push)
- Root: `_book_ex_self` (book NET of own resting order; level fall-through; bids only) +
  `_express_target` (gated `expression_invariant`, default OFF) — unit-tested vs the
  recount math (tests/test_ex_self.py, 11/11 incl. the own-reflection walk case).
- Never-marketable clamp ARMED at the place_order maker chokepoint (post_only=True);
  deliberate taker paths (complete_cross <=100, gated marketable_taker) bypass by design.
- Shadow dual-logs posture_raw + posture_ex_self from tonight (arm evidence measured
  against the market, not our mirror).
- **ARM of the invariant flag waits on:** the recount's corrected shares (Plex-basis
  survival stated) + shadow nights showing converted placements hold <=97 + the standing
  four-bar gate. Walk-cap sizing rides separately (Plex pending); invariant = step law,
  cap = journey bound.
