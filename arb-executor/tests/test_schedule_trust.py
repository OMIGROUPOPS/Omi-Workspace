#!/usr/bin/env python3
"""[C-SCHEDULE-TRUST-FIX] event_start_time accepts pre-start, source-prioritised
corrections instead of locking set-once. Root: the JOVANI/Berlin frame --
direct_6char locked a 06-13 start that the schedule later corrected to 06-14
(real, ~24h later), and the :2503 set-once guard + _date_ok cross-day reject
both refused the correction.

Burden:
  1. set-once start corrected by a corroborated refresh, pre-start.
  2. a live/latched match's start is NOT rewritten.
  3. a correction moving the start beyond T-240m closes the window and clears
     an early resting entry bid (filled positions untouched).
  4. source priority: a weaker source may NOT override a stronger-sourced start;
     a stronger one may.
  5. JOVANI/Berlin frame: stored None -> schedule 06-14 reloads to the real start.

Run: cd arb-executor && python3 tests/test_schedule_trust.py
"""
import sys, types, asyncio
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails; print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)
def run(coro):
    loop = asyncio.new_event_loop()
    try: return loop.run_until_complete(coro)
    finally: loop.close()

NOW = 1_781_000_000.0  # fixed test clock
H = 3600.0
def make_pos(tk, et, **kw):
    return M.Position(ticker=tk, event_ticker=et, category="WTA_MAIN",
                      direction="", cell_name="", cell_cfg={}, **kw)

def make_bot(live=False):
    s = types.SimpleNamespace()
    s.schedule = {}
    s.event_start_time = {}
    s.event_start_source = {}
    s.positions = {}
    s.processed_events = set()
    s._live = live
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s._is_match_live = lambda et: s._live
    s._save_v4_resting = lambda: None
    s._save_processed = lambda: None
    s.cancelled = []
    async def _cancel_entry_and_resolve(tk, pos, label, source):
        s.cancelled.append((tk, label)); return "cancelled"
    s._cancel_entry_and_resolve = _cancel_entry_and_resolve
    # real methods under test
    s._reconcile_event_start = types.MethodType(M.LiveV3._reconcile_event_start, s)
    s._untombstone_entry = types.MethodType(M.LiveV3._untombstone_entry, s)
    return s
def events(s, name): return [d for (e, d, t) in s.logs if e == name]

ET = "KXWTAMATCH-26JUN13MARITO"

# 1. set-once corrected by corroborated refresh, pre-start
s = make_bot()
s.event_start_time[ET] = NOW + 4*H            # stale "today"
s.event_start_source[ET] = "direct_6char"
s.schedule["MARITO"] = {"start_time": "2026-06-14T10:30:00Z", "source": "tennisexplorer"}
# new start = a real epoch ~24h later than stored; force via a known iso:
run(s._reconcile_event_start(ET, NOW))
sc = events(s, "schedule_corrected")
check(len(sc) == 1 and sc[0]["new_source"] == "tennisexplorer" and sc[0]["old_source"] == "direct_6char",
      "1. set-once start corrected by corroborated (tennisexplorer) refresh")
check(s.event_start_time[ET] != NOW + 4*H, "1. event_start_time actually updated")

# 2. live/latched match NOT rewritten
s = make_bot(live=True)
s.event_start_time[ET] = NOW + 4*H
s.event_start_source[ET] = "direct_6char"
s.schedule["MARITO"] = {"start_time": "2026-06-14T10:30:00Z", "source": "espn"}
run(s._reconcile_event_start(ET, NOW))
check(not events(s, "schedule_corrected") and s.event_start_time[ET] == NOW + 4*H,
      "2. live-latched match: start NOT rewritten")

# 3. correction beyond T-240m closes window + clears early resting bid
s = make_bot()
s.event_start_time[ET] = NOW + 3*H            # bid was placed in-window
s.event_start_source[ET] = "direct_6char"
s.processed_events.add(ET)
s.positions[ET + "-MAR"] = make_pos(ET + "-MAR", ET, entry_price=63,
                                    entry_order_id="BID1", entry_qty=0,
                                    phase="entry_resting", is_v4=True)
# new start ~ +20h -> far beyond T-240m
s.schedule["MARITO"] = {"start_time": "2026-06-14T10:30:00Z", "source": "espn"}
# stretch: make new_start clearly > NOW + 240m by using a real future iso vs NOW clock
import datetime as _dt
new_ts = _dt.datetime.fromisoformat("2026-06-14T10:30:00+00:00").timestamp()
# only meaningful if new_ts - NOW > 14400; assert the fixture holds
check(new_ts - NOW > M.V4_MAX_PLACEMENT_SEC, "3. fixture: corrected start is beyond T-240m")
run(s._reconcile_event_start(ET, NOW))
sc = events(s, "schedule_corrected")
check(sc and sc[0]["action"] == "early_bids_cancelled" and (ET + "-MAR") in sc[0]["cancelled_bids"],
      "3. window deferred -> early resting bid cancelled")
check((ET + "-MAR") not in s.positions and ET not in s.processed_events,
      "3. cancelled bid removed + event un-processed for re-entry at real window")

# 4. source priority -- weaker may not override stronger; stronger may
s = make_bot()
s.event_start_time[ET] = NOW + 4*H
s.event_start_source[ET] = "espn"             # strong stored
s.schedule["MARITO"] = {"start_time": "2026-06-14T10:30:00Z", "source": "direct_6char"}  # weak new
run(s._reconcile_event_start(ET, NOW))
check(not events(s, "schedule_corrected") and s.event_start_time[ET] == NOW + 4*H,
      "4a. weaker source (direct_6char) does NOT override stronger (espn)")
s = make_bot()
s.event_start_time[ET] = NOW + 4*H
s.event_start_source[ET] = "direct_6char"     # weak stored
s.schedule["MARITO"] = {"start_time": "2026-06-14T10:30:00Z", "source": "espn"}           # strong new
run(s._reconcile_event_start(ET, NOW))
check(len(events(s, "schedule_corrected")) == 1, "4b. stronger source (espn) DOES correct weaker (direct_6char)")

# 5. JOVANI/Berlin frame: stored None -> reloads to the real 06-14 start
s = make_bot()
s.schedule["MARITO"] = {"start_time": "2026-06-14T10:30:00Z", "source": "espn"}
run(s._reconcile_event_start(ET, NOW))
sc = events(s, "schedule_corrected")
check(sc and sc[0]["old_start"] is None and sc[0]["action"] in ("start_set", "window_deferred"),
      "5. stored None -> start_set from corroborated schedule (06-14 reload)")
check(abs(s.event_start_time[ET] - new_ts) < 1, "5. event_start_time set to the real 06-14 epoch")

# 6. stale/past schedule row (wrong-code collision) is NOT adopted
s = make_bot()
s.schedule["MARITO"] = {"start_time": "2026-06-08T06:55:00Z", "source": "espn"}  # 5 days before NOW
run(s._reconcile_event_start(ET, NOW))
check(not events(s, "schedule_corrected") and ET not in s.event_start_time,
      "6. stale PAST schedule row (already-started) is NOT adopted as a start")

print("\n%s  (%d failures)" % ("ALL PASS" if fails == 0 else "FAILURES", fails))
sys.exit(1 if fails else 0)
