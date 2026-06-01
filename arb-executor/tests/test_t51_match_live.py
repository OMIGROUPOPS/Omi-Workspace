#!/usr/bin/env python3
"""T51 regression test — match-live detection via volume acceleration.

Validates the rebuilt detector (_is_match_live): no false-fire on a flat even
book (TIAARN sat at 50-51c — the old >=10c price proxy was blind), fires on a
trade-volume burst, and latches. Run: cd arb-executor && python3 tests/test_t51_match_live.py
"""
import sys, types, time
from collections import deque
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails; print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

now = time.time()
ET = "KXATPMATCH-26JUN01TIAARN"; TIA = ET + "-TIA"; ARN = ET + "-ARN"
def stub(tt):
    s = types.SimpleNamespace(event_tickers={ET: {TIA, ARN}}, _trade_times=tt,
                              _events_live=set(), _log=lambda *a, **k: None)
    s._is_match_live = types.MethodType(M.LiveV3._is_match_live, s)
    return s

# A — TIAARN flat: 3 trades / 60s -> NOT live (the key no-false-fire validation)
s = stub({TIA: deque([now - 5, now - 30]), ARN: deque([now - 10])})
check(s._is_match_live(ET) is False, "TIAARN flat (3 trades/60s) -> NOT live")
# B — volume burst -> live + latched
s = stub({TIA: deque([now - i for i in range(0, 40, 3)]), ARN: deque([now - i for i in range(1, 30, 2)])})
check(s._is_match_live(ET) is True, "volume burst -> LIVE")
check(ET in s._events_live, "live event latched in _events_live")
# C — latch persists after trades age out (a match does not un-start)
s._trade_times = {TIA: deque([now - 500]), ARN: deque()}
check(s._is_match_live(ET) is True, "latched stays live after trades age out")
# D — stale trades outside the window don't count
s = stub({TIA: deque([now - 200 - i for i in range(15)])})
check(s._is_match_live(ET) is False, "15 trades all >60s old -> NOT live")
# E — exactly at threshold fires
s = stub({TIA: deque([now - i for i in range(M.LIVE_TRADE_BURST)])})
check(s._is_match_live(ET) is True, "exactly LIVE_TRADE_BURST trades -> live")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
