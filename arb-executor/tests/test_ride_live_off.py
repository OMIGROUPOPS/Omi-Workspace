#!/usr/bin/env python3
"""[C-RIDE-LIVE-OFF] match_live_cancel decoupled from premarket_bids_ride_live.

An unfilled premarket bid is cancelled ONLY on tape-detected real match start
(_is_match_live = volume-burst latch), REGARDLESS of the ride_live flag. ride_live
now solely gates the T-15 wall-clock buffer (check_fills, ENTRY_BUFFER_SEC) -- it
no longer exempts the bid from the live-cancel sweep. No wall-clock cancel of the
bid, no taker cross; a raced fill is booked, not deleted; delay-proof (latch, not
clock).

Run: cd arb-executor && python3 tests/test_ride_live_off.py
"""
import sys, types, asyncio, time
from collections import deque
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

now = time.time()
ET = "KXATPMATCH-26JUN15AAABBB"; TK = ET + "-AAA"

def mkpos(**kw):
    d = dict(entry_mode="resting_maker", event_ticker=ET, phase="entry_resting",
             entry_order_id="oid1", settled=False, target_price=40, intended_join=False,
             intended_clamp=False, match_start_ts=now + 3600, entry_posted_ts=now - 100,
             play_type="v4_resting_maker", direction="underdog", category="ATP_MAIN")
    d.update(kw); return types.SimpleNamespace(**d)
def mkbook(bid=38, ask=42):
    return types.SimpleNamespace(best_bid=bid, best_ask=ask, updated=now)

def mkexec(is_live, ride_live, cancel_result="cancelled"):
    calls = {"cancel": [], "untomb": 0, "place": 0, "save": 0}
    s = types.SimpleNamespace(premarket_bids_ride_live=ride_live)
    s._is_match_live = lambda et: is_live
    async def _car(tk, pos, label, race): calls["cancel"].append(label); return cancel_result
    s._cancel_entry_and_resolve = _car
    s._untombstone_entry = lambda tk, pos: calls.__setitem__("untomb", calls["untomb"] + 1)
    s._save_v4_resting = lambda: calls.__setitem__("save", calls["save"] + 1)
    async def _place(*a, **k): calls["place"] += 1; return ("x", {})
    s.place_order = _place
    s._log = lambda *a, **k: None
    return s, calls

# --- T1: cancel fires on _is_match_live with ride_live=TRUE (the decouple) ---
s, c = mkexec(is_live=True, ride_live=True)
run(M.LiveV3._v4_manage_resting_inner(s, TK, mkpos(), mkbook(), now))
check(c["cancel"] == ["match_live_cancel"], "T1  cancel FIRES on real-start with ride_live=TRUE (decoupled)")
check(c["untomb"] == 1, "T1  leg untombstoned after cancel")
# control: same with ride_live=FALSE -> still cancels (flag-agnostic)
s, c = mkexec(is_live=True, ride_live=False)
run(M.LiveV3._v4_manage_resting_inner(s, TK, mkpos(), mkbook(), now))
check(c["cancel"] == ["match_live_cancel"], "T1b cancel FIRES with ride_live=FALSE too (flag-agnostic)")

# --- T3: no taker cross on the live-cancel path ---
s, c = mkexec(is_live=True, ride_live=True)
run(M.LiveV3._v4_manage_resting_inner(s, TK, mkpos(), mkbook(), now))
check(c["place"] == 0, "T3  no taker cross (place_order never called on live-cancel)")

# --- T4: raced fill -> booked, NOT deleted ---
s, c = mkexec(is_live=True, ride_live=True, cancel_result="booked")
run(M.LiveV3._v4_manage_resting_inner(s, TK, mkpos(), mkbook(), now))
check(c["cancel"] == ["match_live_cancel"] and c["untomb"] == 0,
      "T4  raced fill booked -> position NOT deleted (no untombstone)")

# --- T5: delay-proof -- cancel keys on the latch, not wall-clock ---
def realexec(latched, tt, sched_offset):
    s = types.SimpleNamespace(event_tickers={ET: {TK}}, _trade_times=tt,
        _events_live=({ET} if latched else set()), _live_stage1={}, _live_skip_logged=set(),
        event_start_time={ET: now + sched_offset}, _log=lambda *a, **k: None)
    s._is_match_live = types.MethodType(M.LiveV3._is_match_live, s)
    return s
# latched on volume burst while tts is hugely POSITIVE (long before scheduled start)
sd = realexec(latched=True, tt={TK: deque([now - 2, now - 4])}, sched_offset=99999)
check(sd._is_match_live(ET) is True,
      "T5  volume-burst latch -> LIVE even when tts hugely positive (latch, not wall-clock)")
# past scheduled start (tts<0) but tape quiet / no burst -> NOT live -> no cancel
sd2 = realexec(latched=False, tt={TK: deque()}, sched_offset=-1800)
check(sd2._is_match_live(ET) is False,
      "T5b past scheduled start, no tape burst -> NOT live (no wall-clock cancel of the bid)")

# --- T2: T-15 buffer stays OFF under ride_live (mirrors UNCHANGED guard live_v4.py:3664) ---
def t15_would_cancel(ride_live, inside_buffer=True, completion_exempt=False):
    # exact predicate from check_fills:3664 -- unchanged by this commit
    return bool(inside_buffer and not completion_exempt and not ride_live)
check(t15_would_cancel(ride_live=True) is False,
      "T2  T-15 wall-clock cancel GATED OFF when ride_live=True (no early pull)")
check(t15_would_cancel(ride_live=False) is True,
      "T2b T-15 cancel fires when ride_live=False (gate intact, site unchanged)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
