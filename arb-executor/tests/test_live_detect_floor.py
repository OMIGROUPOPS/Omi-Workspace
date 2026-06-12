#!/usr/bin/env python3
"""[C-FEEDER FIX-1] live-detect TTS floor + two-stage latch + counter-evidence
unlatch + re-evaluable scratch.

The 2026-06-12 5AM block: premarket volume bursts latched ZHAMAN (19 trades/60s
at T-4.0h, 01:04 ET), MPEBUB (13 at T-3.8h, 01:13 ET) and BLAJOR (20 at T-3.5h,
00:58 ET) as live and PERMANENTLY scratched all six legs (processed_events).
These three frames are replayed here and must no longer latch; a real start
still latches via the two-stage path; a false latch with the schedule still
saying tts > floor and a quiet tape clears itself (counter-evidence; time-based
clears rejected); the route-site scratch no longer touches processed_events.
Run: cd arb-executor && python3 tests/test_live_detect_floor.py
"""
import sys, types, time, inspect, re
from collections import deque
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails; print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

now = time.time()

def stub(et, legs, tt, tts_sec, stage1=None, latched=False):
    s = types.SimpleNamespace(
        event_tickers={et: set(legs)}, _trade_times=tt,
        _events_live=({et} if latched else set()),
        _live_stage1=stage1 or {}, _live_skip_logged=set(),
        event_start_time=({et: now + tts_sec} if tts_sec is not None else {}),
        logs=[])
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s._is_match_live = types.MethodType(M.LiveV3._is_match_live, s)
    return s

def burst(n):
    return deque([now - i * (50.0 / max(n, 1)) for i in range(n)])

# ---- 1. THE THREE 5AM-BLOCK FRAMES: reproduce, must no longer scratch ----
FRAMES = [
    ("KXATPMATCH-26JUN12ZHAMAN", 19, 4.0 * 3600),    # 01:04 ET, start 05:10 ET
    ("KXATPMATCH-26JUN12MPEBUB", 13, 3.8 * 3600),    # 01:13 ET, start ~05:00 ET
    ("KXATPCHALLENGERMATCH-26JUN12BLAJOR", 20, 3.5 * 3600),  # 00:58 ET, start 04:30 ET
]
for et, n, tts in FRAMES:
    legs = (et + "-A", et + "-B")
    s = stub(et, legs, {legs[0]: burst(n)}, tts)
    r1 = s._is_match_live(et)
    r2 = s._is_match_live(et)   # repeated evaluation: still floored
    check(r1 is False and r2 is False,
          "%s frame (%d trades/60s at T-%.1fh) -> NOT live (floor)" % (et[-6:], n, tts / 3600))
    check(et not in s._events_live and et not in s._live_stage1,
          "%s: no latch AND no stage-1 arm above the floor" % et[-6:])

# ---- 2. real start still latches (two-stage, inside the floor) ----
ET2 = "KXATPMATCH-26JUN12REAL"; L2 = (ET2 + "-A", ET2 + "-B")
s = stub(ET2, L2, {L2[0]: burst(12), L2[1]: burst(8)}, 120.0)  # T-2min, flow on both legs
check(s._is_match_live(ET2) is False and ET2 in s._live_stage1,
      "real start, first burst -> stage-1 armed")
s._live_stage1[ET2] = now - M.LIVE_DETECT_CONFIRM_MIN_GAP_SEC - 1  # one window later, flow persists
check(s._is_match_live(ET2) is True and ET2 in s._events_live,
      "real start, sustained burst -> LATCHED")
# in-play (tts negative) latches the same way
ET3 = "KXATPMATCH-26JUN12INPLAY"; L3 = (ET3 + "-A",)
s = stub(ET3, L3, {L3[0]: burst(15)}, -300.0,
         stage1={ET3: now - M.LIVE_DETECT_CONFIRM_MIN_GAP_SEC - 1})
check(s._is_match_live(ET3) is True, "in-play burst (tts<0) -> latched")

# ---- 3. counter-evidence unlatch: latched + tts>floor + quiet tape -> clears ----
ET4 = "KXATPMATCH-26JUN12FALSE"; L4 = (ET4 + "-A", ET4 + "-B")
s = stub(ET4, L4, {L4[0]: deque(), L4[1]: deque()}, 2.5 * 3600, latched=True)
s._live_skip_logged = {ET4}
check(s._is_match_live(ET4) is False, "false latch + quiet tape + tts>floor -> UNLATCHED")
check(ET4 not in s._events_live, "unlatch removed the event from _events_live")
check(ET4 not in s._live_skip_logged, "unlatch cleared the skip-log key (scratch re-evaluable)")
check(any(ev == "match_live_unlatched" and d.get("reason") == "counter_evidence_quiet"
          for ev, d, _ in s.logs), "match_live_unlatched logged with counter_evidence_quiet")
# still-printing latched event does NOT unlatch even with tts>floor
s = stub(ET4, L4, {L4[0]: deque([now - 30])}, 2.5 * 3600, latched=True)
check(s._is_match_live(ET4) is True, "latched + recent print -> stays live (no unlatch)")
# latched event inside the floor stays latched regardless of quiet (matches go quiet between points)
s = stub(ET4, L4, {L4[0]: deque(), L4[1]: deque()}, 600.0, latched=True)
check(s._is_match_live(ET4) is True, "latched inside floor + quiet -> stays live")

# ---- 4. route-site scratch is re-evaluable: no processed_events mutation ----
src = inspect.getsource(M.LiveV3._route_event)
seg = src[src.index("_is_match_live(et)"):]
seg = seg[:seg.index("identify_sides")]
check("processed_events.add" not in seg and "_save_processed" not in seg,
      "live-skip branch no longer marks the event processed (source-pinned)")
check("skip_live_match" in seg and "_live_skip_logged" in seg,
      "skip_live_match logged once per latch via _live_skip_logged")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
