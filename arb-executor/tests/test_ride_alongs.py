#!/usr/bin/env python3
"""[C-FEEDER RIDE-ALONGS] depth_ahead read fix + move_repost play_type
preservation + depth_ok semantics.

(1) depth_ahead: read at OUR final target level in the synchronous decision
slice (old read: post-await best_bid level -- wrong level on any tick; the
exact-500 cluster was real MM quote size, G2 median 499, not a sentinel).
(2) move_repost preserved play_type: 2 of last night's 3 engagement-origin
fills (PLIVEK-VEK join@36->repost->fill@49, MEDCIL-CIL join@28->repost->
fill@35) booked as v4_resting_maker -- 3x scorecard undercount.
(3) depth_ok: the old key compared single-level ask size AT our exit price
(we are first there -> 0/1, false on every healthy exit, all 5 last night);
now keyed on ask-side size in (entry, exit_target] -- the realization-
liquidity proxy the gated-optima floor means. Observational only.
Run: cd arb-executor && python3 tests/test_ride_alongs.py
"""
import sys, types, time, asyncio, inspect
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

async def fake_api_get(sess, ak, pk, path, rl):
    if "/portfolio/orders/" in path and "?" not in path:
        return {"order": {"status": "canceled", "fill_count_fp": 0}}
    if "/portfolio/positions" in path:
        # [C-PARTIAL-BOOKING P0v2] the exit path now clamps to the exchange
        # position (never-oversell); report ample open shares.
        tk = path.split("ticker=")[1].split("&")[0] if "ticker=" in path else ""
        return {"market_positions": [{"ticker": tk, "position_fp": "99.00"}]}
    return {"orders": []}
M.api_get = fake_api_get

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
    s.entry_table = {("ATP_MAIN", "r25_34"): (180, 1, 0, 0),
                     ("ATP_MAIN", "r45_54"): (180, 1, 0, 0)}
    s.regime_lookup = lambda cat, price: ("r45_54" if 45 <= price <= 54 else "r25_34")
    s.cell_lookup = lambda cat, price: price
    s.exit_rule_for = lambda cat, price: (10, "exit")
    s.exit_depth_floor = 250
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s.placed = []; s.cancelled = []
    async def place_order(tk, action, side, price, count, post_only=True):
        s.placed.append({"tk": tk, "price": price, "post_only": post_only,
                         "action": action})
        return "OID_%d" % len(s.placed), {"order": {"status": "resting"}}
    s.place_order = place_order
    async def cancel_order(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        return True
    s.cancel_order = cancel_order
    s._save_v4_resting = lambda: None
    for nm in ("_runway_status", "_fix6_reference",
               "_v4_manage_resting", "_v4_manage_resting_inner", "_is_match_live",
               "_resting_cancel_reason", "_reprice_target", "_taker_spread_ok",
               "_fallback_order", "_cancel_entry_and_resolve", "_parse_entry_fill",
               "_sibling_ticker", "_sibling_engageable", "_paired_basis_ok",
               "_untombstone_entry", "_v4_apply_exit",
               "_cancel_sibling_if_paired_over_cap", "_completion_buffer_exempt"):
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

def book(bid, ask, asks=None):
    return types.SimpleNamespace(best_bid=bid, best_ask=ask, bids={}, asks=asks or {},
        updated=time.time(), last_trade_price=0, last_trade_ts=0.0)

def mk(tk, et, **kw):
    p = M.Position(ticker=tk, event_ticker=et, category="ATP_MAIN",
                   direction="", cell_name="", cell_cfg={})
    for k, v in kw.items(): setattr(p, k, v)
    return p

ET = "EV"; A = "EV-A"

# ---- 1. move_repost preserves the engagement label ----
s = make_bot()
pos = mk(A, ET, entry_price=28, target_price=28, entry_order_id="O1",
         entry_mode="resting_maker", play_type="v4_engagement_join", is_v4=True,
         phase="entry_resting", match_start_ts=time.time() + 4 * 3600,
         regime_at_posting="r25_34", last_cancel_repost_ts=0, intended_join=True)
s.positions[A] = pos
# price moved 28->35 (>5c): the VEK/CIL frame -- repost must keep the label
run(s._v4_manage_resting(A, pos, book(35, 36), time.time()))
check(any(c["label"] == "v4_move_repost" for c in s.cancelled), "repost path exercised")
check(pos.play_type == "v4_engagement_join",
      "engagement-origin bid keeps play_type through move_repost (VEK/CIL wart closed)")
check(pos.entry_mode == "resting_maker", "manage semantics still key on entry_mode")
# a normal bid still labels v4_resting_maker
s = make_bot()
pos2 = mk(A, ET, entry_price=28, target_price=27, entry_order_id="O1",
          entry_mode="resting_maker", play_type="v4_resting_maker", is_v4=True,
          phase="entry_resting", match_start_ts=time.time() + 4 * 3600,
          regime_at_posting="r25_34", last_cancel_repost_ts=0)
s.positions[A] = pos2
run(s._v4_manage_resting(A, pos2, book(35, 36), time.time()))
check(pos2.play_type == "v4_resting_maker", "normal repost labels v4_resting_maker")

# ---- 2. depth_ok semantics: keyed on within-band ask liquidity ----
s = make_bot()
pos = mk(A, ET, entry_price=50, entry_order_id="O1", entry_mode="resting_maker",
         is_v4=True, phase="active")
s.positions[A] = pos
s.books[A] = book(50, 51, asks={51: 100, 55: 200, 60: 80, 75: 999})  # exit target 60
run(s._v4_apply_exit(A, pos, 50, 5))
evs = [d for ev, d, _ in s.logs if ev == "v4_exit_posted"]
check(len(evs) == 1, "exit posted")
d = evs[0]
check(d.get("depth_within_band") == 380,  # 51:100 + 55:200 + 60:80; 75 outside band
      "depth_within_band sums ask size in (entry, exit_target]")
check(d.get("depth_ok") is True and d.get("depth_floor") == 250,
      "depth_ok keyed on within-band liquidity vs the floor")
check(d.get("depth_at_exit") == 80, "single-level depth still reported (continuity)")
# thin book: ok flips false
s = make_bot()
pos = mk(A, ET, entry_price=50, entry_order_id="O1", entry_mode="resting_maker",
         is_v4=True, phase="active")
s.positions[A] = pos
s.books[A] = book(50, 51, asks={55: 30})
run(s._v4_apply_exit(A, pos, 50, 5))
d = [x for ev, x, _ in s.logs if ev == "v4_exit_posted"][0]
check(d.get("depth_within_band") == 30 and d.get("depth_ok") is False,
      "thin within-band book -> depth_ok false (meaningfully, not structurally)")

# ---- 3. depth_ahead: decision-slice read at OUR target level (source pins) ----
src = inspect.getsource(M.LiveV3._route_event)
check("placement_depth_ahead = int(book.bids.get(int(round(target_bid)), 0) or 0)" in src,
      "depth_ahead read at the final target level")
check('"depth_ahead": placement_depth_ahead' in src
      and "book.bids.get(int(round(book.best_bid))" not in src,
      "post-await best_bid-level read eliminated")
i_cap = src.index("placement_depth_ahead = ")
seg_code = "\n".join(l for l in src[src.index("placement_bid, placement_ask"):i_cap]
                     .splitlines() if not l.strip().startswith("#"))
check("await" not in seg_code,
      "depth captured in the same synchronous decision slice as the book snapshot")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
