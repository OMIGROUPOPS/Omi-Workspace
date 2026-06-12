#!/usr/bin/env python3
"""T51 regression test — match-live detection via volume acceleration.

[C-FEEDER FIX-1] contract update: the detector is now two-stage (a single
burst arms stage-1; the latch needs a second qualifying burst >= one full
window later). These checks pin the amended contract; the FIX-1 floor /
unlatch / re-evaluable-scratch behavior is covered by
tests/test_live_detect_floor.py.

Validates: no false-fire on a flat even book (TIAARN sat at 50-51c — the old
>=10c price proxy was blind), stage-1 arms on a burst, stage-2 confirms and
latches, stale trades don't count, threshold boundary.
Run: cd arb-executor && python3 tests/test_t51_match_live.py
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
def stub(tt, stage1=None):
    s = types.SimpleNamespace(event_tickers={ET: {TIA, ARN}}, _trade_times=tt,
                              _events_live=set(), _live_stage1=stage1 or {},
                              _live_skip_logged=set(),
                              event_start_time={},  # unknown start: floor cannot apply
                              _log=lambda *a, **k: None)
    s._is_match_live = types.MethodType(M.LiveV3._is_match_live, s)
    return s

# A — TIAARN flat: 3 trades / 60s -> NOT live (the key no-false-fire validation)
s = stub({TIA: deque([now - 5, now - 30]), ARN: deque([now - 10])})
check(s._is_match_live(ET) is False, "TIAARN flat (3 trades/60s) -> NOT live")
# B1 — volume burst, first sighting -> stage-1 armed, NOT yet live (FIX-1 two-stage)
s = stub({TIA: deque([now - i for i in range(0, 40, 3)]), ARN: deque([now - i for i in range(1, 30, 2)])})
check(s._is_match_live(ET) is False, "first burst -> stage-1 only, NOT yet live")
check(ET in s._live_stage1, "stage-1 armed on first burst")
# B2 — burst persisting one full window later -> LIVE + latched
s = stub({TIA: deque([now - i for i in range(0, 40, 3)]), ARN: deque([now - i for i in range(1, 30, 2)])},
         stage1={ET: now - M.LIVE_DETECT_CONFIRM_MIN_GAP_SEC - 1})
check(s._is_match_live(ET) is True, "second burst >= confirm gap -> LIVE")
check(ET in s._events_live, "live event latched in _events_live")
# B3 — stage-1 evidence past TTL re-arms instead of confirming
s = stub({TIA: deque([now - i for i in range(0, 40, 3)])},
         stage1={ET: now - M.LIVE_DETECT_CONFIRM_TTL_SEC - 5})
check(s._is_match_live(ET) is False, "stage-1 older than TTL -> re-arm, not latch")
check(abs(s._live_stage1[ET] - now) < 5, "stage-1 timestamp refreshed")
# C — latch persists after trades age out (a started match does not un-start
#     absent counter-evidence; unknown start time -> unlatch path can't fire)
s = stub({TIA: deque([now - 500]), ARN: deque()})
s._events_live = {ET}
check(s._is_match_live(ET) is True, "latched stays live after trades age out")
# D — stale trades outside the window don't count
s = stub({TIA: deque([now - 200 - i for i in range(15)])})
check(s._is_match_live(ET) is False, "15 trades all >60s old -> NOT live")
# E — exactly at threshold fires (with stage-1 pre-armed)
s = stub({TIA: deque([now - i for i in range(M.LIVE_TRADE_BURST)])},
         stage1={ET: now - M.LIVE_DETECT_CONFIRM_MIN_GAP_SEC - 1})
check(s._is_match_live(ET) is True, "exactly LIVE_TRADE_BURST trades -> live")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
