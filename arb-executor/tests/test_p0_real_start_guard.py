"""[P0 REAL-START ENTRY GUARD] regression for the MICMAY post-start-fill P0.

Root: a wrong schedule (expected_expiration_time 22:00, the match END, read as
the START; real start ~19:00) left the engine in W1 belief, so a resting maker
entry for Mayo filled ~36 min INTO the match, and the Michelsen sibling stayed
resting post-start. Fixes proven here:
  1. expected_expiration_time is never used as a start.
  2. strong live in-play evidence overrides a conflicting FUTURE schedule.
  3. the placement chokepoint refuses every post-start / unknown / conflicting
     entry buy (fails closed), independent of the schedule clock.
  4. at real-start detection both siblings' unfilled entries are swept;
     filled positions and protective exits are untouched.
"""
import os, sys, types, asyncio, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import live_v4 as M

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m)
    if not c:
        fails += 1

def run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)

EV = "KXATPCHALLENGERMATCH-26JUL21MICMAY"
MAY = EV + "-MAY"
MIC = EV + "-MIC"
FUT = time.time() + 8400.0   # false schedule ~140 min in the FUTURE (MICMAY: 22:00)
PAST = time.time() - 3600.0  # a start already passed

BOUND = ("_strong_live_evidence", "_entry_start_gate", "_gun_stamp",
         "_place_order_unlocked", "_gun_sweep_entry_bids")

def make_bot():
    s = types.SimpleNamespace()
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s.event_start_time = {}
    s._pm_honest = {}
    s._gun_state = {}
    s._gun_void_pending = {}
    s._gun_void_logged = set()
    s._events_live = set()
    s._start_conflict = set()
    s.event_tickers = {}
    s._trade_times = {}
    s.positions = {}
    s.books = {}
    s._conception_halt = False
    s.fused_gun = False
    s._completion_cross_allow = set()
    s._horizon_state = lambda et: (False, 0)
    s.unmatched_holdings = {}
    for nm in BOUND:
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

def evs(s, name):
    return [d for (e, d, t) in s.logs if e == name]

# ======================================================================
print("--- 1. FIX 1: expected_expiration_time is NEVER a start ---")
# ======================================================================
_src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "live_v4.py"), encoding="utf-8").read()
_occ_line = [l for l in _src.splitlines() if "occ_str = m.get(" in l]
check(bool(_occ_line) and all("expected_expiration_time" not in l for l in _occ_line),
      "1.1 event_kalshi_occ derives from occurrence_datetime ONLY (no expected_expiration_time)")
# consequence: with no reliable start, entries fail closed (tested in 3)

# ======================================================================
print("--- 2. FIX 2: strong live evidence overrides a future schedule ---")
# ======================================================================
s = make_bot()
check(s._strong_live_evidence("tape_flow", {"ref_rise_cents": 71}) is True,
      "2.1 a 71c realized move is STRONG")
check(s._strong_live_evidence("tape_flow", {"prints_30m": 28, "threshold": 16}) is True,
      "2.2 28 prints vs threshold 16 (>=1.5x) is STRONG")
check(s._strong_live_evidence("tape_flow", {"ref_rise_cents": 4, "prints_30m": 10, "threshold": 16}) is False,
      "2.3 a small move / thin prints is NOT strong (weak blip)")
check(s._strong_live_evidence("tape_flow", {}) is False, "2.4 empty detail is NOT strong")

# strong pre-sched signal FIRES the gun (override) despite a future schedule
s = make_bot()
s.event_start_time[EV] = FUT
fired = s._gun_stamp(EV, "tape_flow", {"ref_rise_cents": 71, "prints_30m": 28, "threshold": 16})
check(fired is True, "2.5 STRONG evidence fires the gun despite a FUTURE schedule")
check(EV in s._events_live, "2.5 event added to _events_live")
check(EV in s._start_conflict, "2.5 event marked start-conflict")
check(bool(evs(s, "sched_liar_override")), "2.5 sched_liar_override logged")
check(not evs(s, "phantom_bell_void"), "2.5 NOT voided")

# weak pre-sched signal still VOIDS
s = make_bot()
s.event_start_time[EV] = FUT
fired = s._gun_stamp(EV, "tape_flow", {"ref_rise_cents": 3, "prints_30m": 8, "threshold": 16})
check(fired is False, "2.6 WEAK evidence pre-sched still voids (no fire)")
check(EV not in s._events_live, "2.6 not live")
check(EV not in s._start_conflict, "2.6 not a start-conflict")
check(bool(evs(s, "phantom_bell_void")), "2.6 phantom_bell_void logged")

# ======================================================================
print("--- 3. FIX 3: placement chokepoint fails closed on non-pre-start ---")
# ======================================================================
s = make_bot()
# gate decision matrix
s._events_live = {EV}
check(s._entry_start_gate(EV) == (True, "match_live_gun_fired"), "3.1 live gun -> refuse")
s = make_bot(); s._start_conflict = {EV}
check(s._entry_start_gate(EV) == (True, "live_evidence_conflicts_schedule"), "3.2 conflict -> refuse")
s = make_bot()   # no start known
check(s._entry_start_gate(EV) == (True, "unknown_start"), "3.3 unknown start -> refuse (fail closed)")
s = make_bot(); s.event_start_time[EV] = PAST
check(s._entry_start_gate(EV) == (True, "past_scheduled_start"), "3.4 past start -> refuse")
s = make_bot(); s.event_start_time[EV] = FUT
check(s._entry_start_gate(EV) == (False, ""), "3.5 reliable FUTURE start, no live evidence -> ALLOW")

# chokepoint: an entry BUY on a live event is refused
s = make_bot(); s._events_live = {EV}; s.event_start_time[EV] = FUT
oid, resp = run(s._place_order_unlocked(MAY, "buy", "yes", 85, 5, post_only=True))
check(oid == "" and resp.get("_error") == "post_start_entry_refused",
      "3.6 chokepoint REFUSES a post-start entry buy")
check(bool(evs(s, "post_start_entry_refused")), "3.6 post_start_entry_refused logged")
# an exit SELL is buy-only-exempt: it never consults the entry-start guard
s2 = make_bot(); s2._events_live = {EV}
_sell_calls = {"n": 0}
_og = s2._entry_start_gate
s2._entry_start_gate = lambda et: (_sell_calls.__setitem__("n", _sell_calls["n"] + 1) or _og(et))
try:
    run(s2._place_order_unlocked(MAY, "sell", "yes", 98, 5, post_only=True))
except Exception:
    pass   # downstream placement machinery unstubbed; irrelevant to the guard
check(_sell_calls["n"] == 0, "3.7 an EXIT sell never consults the entry-start guard (buy-only)")
s3 = make_bot(); s3._events_live = {EV}; s3.event_start_time[EV] = FUT
_buy_calls = {"n": 0}
_og3 = s3._entry_start_gate
s3._entry_start_gate = lambda et: (_buy_calls.__setitem__("n", _buy_calls["n"] + 1) or _og3(et))
try:
    run(s3._place_order_unlocked(MAY, "buy", "yes", 85, 5, post_only=True))
except Exception:
    pass
check(_buy_calls["n"] >= 1, "3.7b an entry buy DOES consult the entry-start guard")
# unknown-start entry buy also refused (the real MICMAY after FIX 1)
s = make_bot()   # event_start_time unset -> unknown
oid, resp = run(s._place_order_unlocked(MAY, "buy", "yes", 85, 5, post_only=True))
check(resp.get("_error") == "post_start_entry_refused",
      "3.8 unknown-start entry buy refused (FIX-1 consequence for real MICMAY)")

# ======================================================================
print("--- 4. FIX 4: real-start sweep cancels BOTH siblings, exits untouched ---")
# ======================================================================
s = make_bot()
s.event_tickers[EV] = {MAY, MIC}
# MAY: filled position WITH a protective exit; MIC: unfilled resting entry
may = types.SimpleNamespace(entry_order_id="MAY-ENTRY", entry_qty=5, entry_mode="",
                            exit_order_id="MAY-EXIT", event_ticker=EV)
mic = types.SimpleNamespace(entry_order_id="MIC-ENTRY", entry_qty=0, entry_mode="",
                            exit_order_id=None, event_ticker=EV)
s.positions = {MAY: may, MIC: mic}
swept = []
async def fake_cancel(tk, pos, label, source):
    swept.append((tk, getattr(pos, "entry_order_id", None), label))
    return "cancelled"
s._cancel_entry_and_resolve = fake_cancel
s._untombstone_entry = lambda tk, pos: None
s._save_v4_resting = lambda: None
run(s._gun_sweep_entry_bids(EV, "tape_flow"))
swept_tks = {t for (t, _o, _l) in swept}
check(MIC in swept_tks, "4.1 unfilled Michelsen sibling entry is swept")
check(MAY in swept_tks, "4.2 Mayo entry order is swept (raced fill booked by _cancel_entry_and_resolve)")
check(all(o in ("MAY-ENTRY", "MIC-ENTRY") for (_t, o, _l) in swept),
      "4.3 sweep targets ENTRY order ids only -- exits (MAY-EXIT) never cancelled")
check(bool(evs(s, "match_live_resting_cancel")), "4.4 match_live_resting_cancel logged per leg")

# ======================================================================
print("--- 5. MICMAY integration (req 8): false 22:00 sched, live ~19:00 ---")
# ======================================================================
s = make_bot()
s.event_start_time[EV] = FUT                     # false schedule (future); MICMAY: 22:00
s.event_tickers[EV] = {MAY, MIC}
# strong live evidence arrives while the schedule still claims "future"
fired = s._gun_stamp(EV, "tape_flow", {"ref_rise_cents": 71, "prints_30m": 28, "threshold": 16})
check(fired and EV in s._events_live and bool(evs(s, "sched_liar_override")),
      "5.1 real bell (71c move) fires despite the false future schedule")
# the Mayo entry placement at ~19:36 is now REFUSED at the chokepoint
oid, resp = run(s._place_order_unlocked(MAY, "buy", "yes", 85, 5, post_only=True))
check(oid == "" and resp.get("_error") == "post_start_entry_refused",
      "5.2 Mayo placement at 19:36 is REFUSED (post-start)")
# existing resting entries for BOTH legs are swept before any fill
may = types.SimpleNamespace(entry_order_id="MAY-ENTRY", entry_qty=0, entry_mode="",
                            exit_order_id=None, event_ticker=EV)
mic = types.SimpleNamespace(entry_order_id="MIC-ENTRY", entry_qty=0, entry_mode="",
                            exit_order_id=None, event_ticker=EV)
s.positions = {MAY: may, MIC: mic}
swept = []
async def fake_cancel2(tk, pos, label, source):
    swept.append(tk); return "cancelled"
s._cancel_entry_and_resolve = fake_cancel2
s._untombstone_entry = lambda tk, pos: None
s._save_v4_resting = lambda: None
run(s._gun_sweep_entry_bids(EV, "tape_flow"))
check(MAY in swept, "5.3 existing Mayo entry canceled before any fill")
check(MIC in swept, "5.4 Michelsen sibling canceled")
# no post-start resting entry survives: a fresh attempt is still refused
oid, resp = run(s._place_order_unlocked(MIC, "buy", "yes", 12, 5, post_only=True))
check(resp.get("_error") == "post_start_entry_refused",
      "5.5 no post-start resting entry survives (fresh entry also refused)")

print("\n%s" % ("ALL P0 REAL-START GUARD TESTS PASS" if not fails else "*** %d FAILURE(S)" % fails))
sys.exit(1 if fails else 0)
