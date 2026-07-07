# C-EX-SELF — C46 proof (candidate SHA 479d9bdd)

## LANE 1 — mechanism, by construction + tests
- **Flag-OFF paths byte-identical:** `_express_target` returns its input unless
  `expression_invariant` (absent from config = False). Three call sites are
  pass-throughs flag-off. tests/test_ex_self.py case 10 proves it; 11/11 pass,
  math mirrored from the recount engine (one source of truth), incl. the
  own-reflection walk case (own 70 top -> clamp vs real chain 62 -> 63).
- **ARMED delta = the never-marketable clamp ONLY:** maker buys (post_only=True)
  at >= best_ask clamp to ask-1 with a log line. This is the Plex-ruled
  unconditional invariant; deliberate taker paths (post_only=False:
  complete_cross <=100, gated marketable_taker) bypass by design. The clamp can
  only LOWER a maker price that would have been rejected-or-crossed — it cannot
  create an order, raise a price, or touch sells/cancels.
- Shadow fields are logging-only inside the try-swallowed helper (standing proof).

## LANE 2 — n/a for the OFF flag; the armed clamp's only effect is replacing
would-be-marketable maker posts with ask-1 rests (the never-cross rule the walk
path already had, now universal). Lint PASS; differential suite: zero new failures.
