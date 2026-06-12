#!/usr/bin/env python3
"""[C-FEEDER FIX-6] (offset, placement_minute) is indivisible — a late runway
invalidates the deep offset; the bid joins the reference level instead.

A1 boundary: sub_60 (placement inside T-60) OR available runway < 0.5x the
row's validated runway, whichever first. A2: late window-open tags the
affected legs (late_window); a late remap tags THAT BID ONLY (late_remap).
A3: deep-offset placements/reposts only — engagement joins untouched.
A4: flag route (reference_source=join_late_runway); engagement-path-proper
routing infeasible (no-print precondition + wave-1 attribution).
A5: runway_status on every placement; tags survive restart.
Run: cd arb-executor && python3 tests/test_fix6_late_runway.py
"""
import sys, types, time, asyncio, json, tempfile, inspect
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails; print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

def run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

TMP = Path(tempfile.mkdtemp())
M.V4_RESTING_FILE = TMP / "resting.json"

async def fake_api_get(sess, ak, pk, path, rl):
    if "/portfolio/orders/" in path and "?" not in path:
        return {"order": {"status": "canceled", "fill_count_fp": 0}}
    return {"orders": []}
M.api_get = fake_api_get

def book(bid, ask):
    return types.SimpleNamespace(best_bid=bid, best_ask=ask, bids={}, asks={},
        updated=time.time(), last_trade_price=0, last_trade_ts=0.0)

def mk(tk, et, **kw):
    p = M.Position(ticker=tk, event_ticker=et, category="WTA_MAIN",
                   direction="", cell_name="", cell_cfg={})
    for k, v in kw.items(): setattr(p, k, v)
    return p

def make_bot():
    s = types.SimpleNamespace()
    s.positions = {}; s.books = {}; s.event_tickers = {}
    s._events_live = set(); s._trade_times = {}; s._window_open = {}
    s.event_start_time = {}; s._live_stage1 = {}; s._live_skip_logged = set()
    s.inflight_orders = set(); s._mgmt_inflight = set(); s._booking_inflight = set()
    s.processed_events = set(); s._save_processed = lambda: None
    s.session = None; s.ak = None; s.pk = None; s.rl = None
    s.entry_size = 5; s.n_entries = 0
    s.cancel_on_marketable = True; s.cancel_marketable_buffer = 1
    s.v4_fallback_sec = 1200
    s.fallback_maker_clamp = True; s.maker_only_entry = True
    s.completion_reprice = False; s.completion_disabled = False
    s.entry_table = {("WTA_MAIN", "r25_34"): (180, 1, 0, 0),
                     ("WTA_MAIN", "r35_44"): (180, 1, 0, 0)}
    s.regime_lookup = lambda cat, price: ("r35_44" if 35 <= price <= 44 else "r25_34")
    s.cell_lookup = lambda cat, price: price
    s.exit_rule_for = lambda cat, price: (10, "exit")
    s.exit_depth_floor = 0
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s.placed = []; s.cancelled = []
    async def place_order(tk, action, side, price, count, post_only=True):
        s.placed.append({"tk": tk, "price": price, "post_only": post_only})
        return "OID_%d" % len(s.placed), {"order": {"status": "resting"}}
    s.place_order = place_order
    async def cancel_order(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        return True
    s.cancel_order = cancel_order
    s._save_v4_resting = lambda: None
    for nm in ("_runway_status", "_fix6_reference", "_v4_manage_resting",
               "_v4_manage_resting_inner", "_is_match_live", "_resting_cancel_reason",
               "_reprice_target", "_taker_spread_ok", "_fallback_order",
               "_cancel_entry_and_resolve", "_parse_entry_fill",
               "_sibling_ticker", "_sibling_engageable", "_paired_basis_ok",
               "_untombstone_entry", "_v4_apply_exit",
               "_cancel_sibling_if_paired_over_cap", "_completion_buffer_exempt"):
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

s = make_bot()

# ---- TEST 1: RAD replay pinned to today's match ----
# RADRAK 2026-06-12: window opened T-56 (start 12:00 ET); 180-min row, offset
# 1, fresh print 79, book 73/80 -> old machinery posted 78; the 79 dip traded
# and the bid missed by 1 tick (resting unfilled at the 11:00 read).
rs = s._runway_status(180, 56 * 60)
check(rs == "sub_60", "RAD frame: T-56 placement -> sub_60 (whichever-first: inside T-60)")
tgt, src_ = s._fix6_reference(rs, 1, "per_cell", 79, 78)
check(tgt == 79 and src_ == "join_late_runway",
      "RAD frame: deep offset invalidated -> JOIN reference at 79")
DIP = 79  # the dip printed at 79: a maker bid AT 79 is hit; 78 is traded through
check(tgt >= DIP and 78 < DIP, "the 79 dip FILLS the join (old 78 missed by 1 tick)")

# ---- TEST 2: in-regime non-trigger (full validated envelope) ----
rs = s._runway_status(240, 238 * 60)
check(rs == "full", "window opens on time at T-238 for a 240-row -> full")
tgt, src_ = s._fix6_reference(rs, 2, "per_cell", 50, 48)
check(tgt == 48 and src_ == "", "full runway: deep offset stands (no reference switch)")
# boundary arithmetic: 180-row, validated 165min, half = 82.5min (+15 buffer -> T-97.5)
check(s._runway_status(180, 99 * 60) == "full", "available 84min >= 82.5min -> full")
check(s._runway_status(180, 96 * 60) == "late_window", "available 81min < 82.5min -> late_window")

# ---- TEST 3: late-remap scope -- THAT BID ONLY ----
ET = "EV"; A, B = "EV-A", "EV-B"
s = make_bot()
now = time.time()
posA = mk(A, ET, entry_price=27, target_price=27, entry_order_id="OA",
          entry_mode="resting_maker", play_type="v4_resting_maker", is_v4=True,
          phase="entry_resting", match_start_ts=now + 70 * 60,   # tts 70min: late_remap
          regime_at_posting="r25_34", last_cancel_repost_ts=0)
s.positions[A] = posA
run(s._v4_manage_resting(A, posA, book(34, 36), now))            # mid 35, move 7c -> repost
check(s.placed and s.placed[-1]["price"] == 35 and posA.reference_source == "join_late_runway"
      and posA.runway_status == "late_remap",
      "late remap: deep offset dropped, bid joins the reference (35, not 34)")
s2 = make_bot()
posB = mk(B, ET, entry_price=27, target_price=27, entry_order_id="OB",
          entry_mode="resting_maker", play_type="v4_resting_maker", is_v4=True,
          phase="entry_resting", match_start_ts=now + 170 * 60,  # tts 170min: full
          regime_at_posting="r25_34", last_cancel_repost_ts=0)
s2.positions[B] = posB
run(s2._v4_manage_resting(B, posB, book(34, 36), now))
check(s2.placed and s2.placed[-1]["price"] == 34 and posB.reference_source == ""
      and posB.runway_status == "full",
      "same-shape bid with full runway reposts the offset unchanged (scope: that bid only)")

# ---- TEST 4: engagement-interaction cap accounting ----
# the join reference RAISES the leg's committed price; the paired cap must
# account at the OVERRIDDEN price (engagement-equivalent treatment).
s = make_bot()
s.event_tickers = {ET: {A, B}}
s.positions[B] = mk(B, ET, entry_price=60)   # sibling committed at 60
tgt, src_ = s._fix6_reference("sub_60", 1, "per_cell", 45, 44)
check(tgt == 45, "join reference at 45 (overrides 44)")
check(s._paired_basis_ok(A, ET, tgt) is False,
      "cap accounts the overridden price: 45+60=105 > cap -> placement refused")
check(s._paired_basis_ok(A, ET, 39) is True, "39+60=99 <= cap -> allowed (sanity)")
# A3: engagement joins untouched by the reference switch
tgt, src_ = s._fix6_reference("sub_60", 0, "engagement_wave1", 48, 48)
check(tgt == 48 and src_ == "", "engagement join (offset-0, wave1) untouched by FIX-6")
src_mr = inspect.getsource(M.LiveV3._v4_manage_resting_inner)
check('if pos.play_type != "v4_engagement_join":' in src_mr
      and "_fix6_reference(" in src_mr,
      "repost-side reference switch skips engagement joins (source-pinned)")

# ---- TEST 5: ledger tag recovery across restart ----
s = make_bot()
s._save_v4_resting = types.MethodType(M.LiveV3._save_v4_resting, s)
s._load_v4_resting = types.MethodType(M.LiveV3._load_v4_resting, s)
s.positions = {
    "EV-L": mk("EV-L", "EV", entry_price=35, target_price=35, entry_order_id="O1",
               entry_mode="resting_maker", is_v4=True, phase="entry_resting",
               runway_status="late_window", reference_source="join_late_runway"),
    "EV-F": mk("EV-F", "EV", entry_price=30, target_price=29, entry_order_id="O2",
               entry_mode="resting_maker", is_v4=True, phase="entry_resting"),
}
s._save_v4_resting()
raw = json.loads(open(M.V4_RESTING_FILE).read())
legs = raw.get("legs", raw)
check(legs["EV-L"].get("runway_status") == "late_window"
      and legs["EV-L"].get("reference_source") == "join_late_runway"
      and "runway_status" not in legs["EV-F"] and "reference_source" not in legs["EV-F"],
      "sparse persistence: tags present only when non-default")
s3 = make_bot()
s3._load_v4_resting = types.MethodType(M.LiveV3._load_v4_resting, s3)
s3._load_v4_resting()
check(s3.positions["EV-L"].runway_status == "late_window"
      and s3.positions["EV-L"].reference_source == "join_late_runway"
      and s3.positions["EV-F"].runway_status == "full"
      and s3.positions["EV-F"].reference_source == "",
      "restart: A5 ledger tags recovered exactly")

# ---- A5 on every placement: source pin ----
src_route = inspect.getsource(M.LiveV3._route_event)
check('"runway_status": runway_status' in src_route,
      "v4_place carries runway_status on EVERY placement")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
