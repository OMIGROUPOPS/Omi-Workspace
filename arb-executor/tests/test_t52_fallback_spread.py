#!/usr/bin/env python3
"""T52 regression test — spread-width gate + market-state-gated fallback.

Validates that the T-20m taker fallback and marketable-taker crosses are
blocked on (a) a fat spread (the KESMAR fat-spread cross mechanism) and (b) a
live match (T51). Run: cd arb-executor && python3 tests/test_t52_fallback_spread.py
"""
import sys, types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails; print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

s = types.SimpleNamespace(_log=lambda *a, **k: None)
s._taker_spread_ok = types.MethodType(M.LiveV3._taker_spread_ok, s)

# spread-width gate
check(s._taker_spread_ok(50, 52) is True,  "tight spread 2 -> allow cross")
check(s._taker_spread_ok(70, 75) is True,  "spread 5 (==cap) -> allow cross")
check(s._taker_spread_ok(69, 75) is False, "fat spread 6 (KESMAR MAR-like) -> BLOCK cross")
check(s._taker_spread_ok(60, 75) is False, "fat spread 15 -> BLOCK cross")

# combined T-20m fallback decision: block = match_live OR not spread_ok
ET = "E"; s.event_tickers = {ET: set()}; s._trade_times = {}; s._events_live = set()
s._is_match_live = types.MethodType(M.LiveV3._is_match_live, s)
def fallback_blocked(live_latched, bid, ask):
    s._events_live = {ET} if live_latched else set()
    return s._is_match_live(ET) or (not s._taker_spread_ok(bid, ask))
check(fallback_blocked(False, 70, 72) is False, "not-live + tight -> fallback ALLOWED")
check(fallback_blocked(False, 68, 75) is True,  "not-live + fat(7) -> fallback BLOCKED (fat_spread)")
check(fallback_blocked(True, 70, 72) is True,   "live + tight -> fallback BLOCKED (match_live)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
