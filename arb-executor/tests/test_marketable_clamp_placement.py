#!/usr/bin/env python3
"""Regression: the 3rd cross site (initial marketable placement) clamps to ask-1 MAKER when
`marketable_clamp_placement` is ON, instead of crossing taker at the ask -- the same clamp
_reprice_target and _fallback_order already apply on the other two cross sites. Gated: byte-identical
(taker cross) when OFF. force_cross (round5) is preserved (still crosses) even when ON. The late
T-20m miss_fallback cross (time_to_start <= V4_T20M_SEC) is UNTOUCHED (the buffer-futility path).

Two layers: (1) source-pin the gated clamp branch + config flag + manage-side exemptions; (2)
truth-table of the placement-mode decision (mirrored from the pinned branch).
Run: cd arb-executor && python3 tests/test_marketable_clamp_placement.py"""
import re, sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M
V4_T20M = M.V4_T20M_SEC

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

src = (REPO / "live_v4.py").read_text(encoding="utf-8", errors="ignore")

# ---- Layer 1: source-pins ----
check("self.marketable_clamp_placement = self.config.get(\"marketable_clamp_placement\", False)" in src,
      "config flag marketable_clamp_placement present (default False = byte-identical off)")
# the gated clamp branch: ask-1 maker, guarded by flag AND not force_cross
clamp = re.search(
    r"if self\.marketable_clamp_placement and not force_cross:.*?"
    r"target_bid = max\(1, current_ask - 1\).*?"
    r'entry_price, post_only, entry_mode = target_bid, True, "marketable_clamp"',
    src, re.S)
check(clamp is not None, "clamp branch: gated on (marketable_clamp_placement and not force_cross) -> ask-1, post_only=True, marketable_clamp")
# the else still crosses taker (byte-identical off / force_cross path)
check(re.search(r'else:\s*\n\s*# MARKETABLE TAKER.*?\n\s*entry_price, post_only, entry_mode = current_ask, False, "marketable_taker"', src, re.S) is not None,
      "else branch preserved: marketable_taker cross at current_ask (gate off / force_cross)")
# late-fallback untouched
check('entry_price, post_only, entry_mode = current_ask, False, "miss_fallback"' in src,
      "late T-20m miss_fallback cross UNTOUCHED")
# manage-side exemptions extended to marketable_clamp
check('pos.entry_mode in ("fallback_maker", "marketable_clamp")' in src,
      "cancel-on-marketable exemption extended to marketable_clamp (clamp bid rests, not instant-cancel)")
check('pos.entry_mode not in ("miss_fallback", "fallback_maker", "marketable_clamp")' in src,
      "T-20m re-fallback excludes marketable_clamp (rests like fallback_maker until T-15m/fill)")

# ---- Layer 2: truth-table of the placement-mode decision (mirror of the pinned branch) ----
def mode(t2s, target_bid, ask, force_cross, clamp_on):
    if t2s <= V4_T20M:
        return (ask, False, "miss_fallback")
    if target_bid >= ask or force_cross:
        if clamp_on and not force_cross:
            return (max(1, ask - 1), True, "marketable_clamp")
        return (ask, False, "marketable_taker")
    return (target_bid, True, "resting_maker")

LATE = V4_T20M - 1; OPEN = V4_T20M + 600   # well inside vs before the T-20m line
# the fix: marketable placement, gate ON, not force_cross -> ask-1 MAKER, never a cross
check(mode(OPEN, 62, 60, False, True) == (59, True, "marketable_clamp"),
      "ON: target_bid(62) >= ask(60), not late, not force -> (59, MAKER, marketable_clamp)")
check(mode(OPEN, 60, 60, False, True) == (59, True, "marketable_clamp"),
      "ON: target_bid == ask edge -> ask-1 maker clamp")
check(mode(OPEN, 1, 1, False, True) == (1, True, "marketable_clamp"),
      "ON: ask=1 edge -> max(1, ask-1)=1, still maker (no cross, no <=0 price)")
# gate OFF -> byte-identical taker cross
check(mode(OPEN, 62, 60, False, False) == (60, False, "marketable_taker"),
      "OFF: marketable -> taker cross at ask (byte-identical)")
# force_cross preserved even when ON
check(mode(OPEN, 40, 60, True, True) == (60, False, "marketable_taker"),
      "ON + force_cross(round5) -> STILL taker cross at ask (force_cross preserved)")
check(mode(OPEN, 62, 60, True, True) == (60, False, "marketable_taker"),
      "ON + marketable + force_cross -> force_cross wins, taker cross")
# resting maker unaffected (target below ask)
check(mode(OPEN, 56, 60, False, True) == (56, True, "resting_maker"),
      "target_bid(56) < ask(60) -> normal resting_maker (unaffected by clamp)")
check(mode(OPEN, 56, 60, False, False) == (56, True, "resting_maker"),
      "resting_maker identical with gate off")
# late-fallback untouched by the gate
check(mode(LATE, 62, 60, False, True) == (60, False, "miss_fallback"),
      "late (t<=V4_T20M_SEC) -> miss_fallback cross, UNCHANGED by the clamp gate")
check(mode(LATE, 62, 60, False, False) == (60, False, "miss_fallback"),
      "late-fallback identical with gate off")

# INVARIANT: with the gate ON, the marketable (non-late, non-force) case is ALWAYS a maker rest below ask
inv = all(mode(OPEN, tb, ak, False, True)[1] is True and mode(OPEN, tb, ak, False, True)[0] < ak
          for ak in range(2, 100) for tb in range(ak, 100))
check(inv, "INVARIANT ON: every marketable non-force placement rests post_only=True BELOW the ask (never crosses)")
# INVARIANT: gate OFF reproduces a taker cross for every marketable case (byte-identical)
inv_off = all(mode(OPEN, tb, ak, False, False) == (ak, False, "marketable_taker")
              for ak in range(2, 100) for tb in range(ak, 100))
check(inv_off, "INVARIANT OFF: every marketable case crosses taker at ask (byte-identical to pre-fix)")

print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
