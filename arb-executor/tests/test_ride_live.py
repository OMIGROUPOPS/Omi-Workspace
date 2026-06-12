#!/usr/bin/env python3
"""[C-RIDE-LIVE override #6] premarket_bids_ride_live: resting maker entry
bids persist into play.

Flag on: the T-15 buffer cancel and the match-live resting sweep exempt
resting entries; a rode-in bid HOLDS in-play (no fallback re-post, no
move-repost -- the Naef 13:40:00 re-post-into-play shape); economic cancels
(stale on drift bids) still govern; an in-play fill books normally and posts
its cell exit. Flag off (code default): both cancels byte-identical.
NEW placements in-play remain forbidden -- placement-time gates untouched.
Run: cd arb-executor && python3 tests/test_ride_live.py
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

ORDERS = {}
async def fake_api_get(sess, ak, pk, path, rl):
    if "/portfolio/orders/" in path and "?" not in path:
        oid = path.rsplit("/", 1)[1]
        return {"order": ORDERS.get(oid, {"status": "resting", "fill_count_fp": 0})}
    if "/portfolio/positions" in path:
        tk = path.split("ticker=")[1].split("&")[0] if "ticker=" in path else ""
        return {"market_positions": [{"ticker": tk, "position_fp": "99.00"}]}
    return {"orders": []}
M.api_get = fake_api_get

def book(bid, ask):
    return types.SimpleNamespace(best_bid=bid, best_ask=ask, bids={}, asks={},
        updated=time.time(), last_trade_price=0, last_trade_ts=0.0)

def mk(tk, et, **kw):
    p = M.Position(ticker=tk, event_ticker=et, category="WTA_CHALL",
                   direction="leader", cell_name="", cell_cfg={})
    for k, v in kw.items(): setattr(p, k, v)
    return p

def make_bot(ride):
    s = types.SimpleNamespace()
    s.premarket_bids_ride_live = ride
    s.paired_cap_enforced = False
    s.positions = {}; s.books = {}; s.event_tickers = {}
    s._events_live = set(); s._trade_times = {}; s._window_open = {}
    s.event_start_time = {}; s._live_stage1 = {}; s._live_skip_logged = set()
    s.inflight_orders = set(); s._mgmt_inflight = set(); s._booking_inflight = set()
    s.processed_events = set(); s._save_processed = lambda: None
    s.session = None; s.ak = None; s.pk = None; s.rl = None
    s.entry_size = 5; s.n_entries = 0; s.n_exits = 0
    s.cancel_on_marketable = True; s.cancel_marketable_buffer = 1
    s.v4_fallback_sec = 1200
    s.fallback_maker_clamp = True; s.maker_only_entry = True
    s.completion_reprice = False; s.completion_disabled = False
    s.completion_cells = {}
    s.entry_table = {("WTA_CHALL", "r55_64"): (180, 1, 0, 0)}
    s.regime_lookup = lambda cat, price: "r55_64"
    s.cell_lookup = lambda cat, price: price
    s.exit_rule_for = lambda cat, price: (14, "exit")
    s.exit_depth_floor = 0
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s.placed = []; s.cancelled = []
    async def place_order(tk, action, side, price, count, post_only=True):
        s.placed.append({"tk": tk, "action": action, "price": price, "count": count})
        return "OID_%d" % len(s.placed), {"order": {"status": "resting"}}
    s.place_order = place_order
    async def cancel_order(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        return True
    s.cancel_order = cancel_order
    s._save_v4_resting = lambda: None
    for nm in ("check_fills", "_book_v4_entry_fill", "_parse_entry_fill",
               "_v4_apply_exit", "_cancel_sibling_if_paired_over_cap",
               "_sibling_ticker", "_sibling_engageable", "_paired_basis_ok",
               "_completion_buffer_exempt", "_cancel_entry_and_resolve",
               "_untombstone_entry", "_is_match_live",
               "_v4_manage_resting", "_v4_manage_resting_inner",
               "_resting_cancel_reason", "_reprice_target", "_taker_spread_ok",
               "_fallback_order", "_runway_status", "_fix6_reference"):
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

ET = "KXWTACHALLENGERMATCH-26JUN12NAETAN"; NAE = ET + "-NAE"

def naef_pos(now):
    return mk(NAE, ET, entry_price=58, target_price=58, entry_order_id="ONAE",
              entry_mode="resting_maker", play_type="v4_resting_maker", is_v4=True,
              phase="entry_resting", match_start_ts=now + 600,  # inside T-15
              intended_join=True)

# ---- 1. flag ON: bid survives the T-15 buffer ----
s = make_bot(ride=True); now = time.time()
pos = naef_pos(now); s.positions[NAE] = pos
ORDERS["ONAE"] = {"status": "resting", "fill_count_fp": 0}
run(s.check_fills())
check(not s.cancelled and pos.entry_order_id == "ONAE" and pos.phase == "entry_resting",
      "flag ON: resting bid survives T-15 (no buffer cancel; poll continues)")

# ---- 2. flag ON: bid survives a live latch AND holds (no fallback/repost) ----
s = make_bot(ride=True); now = time.time()
pos = naef_pos(now); pos.match_start_ts = now - 120   # in play
s.positions[NAE] = pos
s._events_live = {ET}
run(s._v4_manage_resting(NAE, pos, book(56, 62), now))
check(not s.cancelled and not s.placed and pos.entry_order_id == "ONAE",
      "flag ON: live latch + in-play -> bid HOLDS (no sweep, no fallback re-post, no repost)")

# ---- 3. economic cancel still governs in-play (drift bid gone stale) ----
s = make_bot(ride=True); now = time.time()
pos = naef_pos(now); pos.match_start_ts = now - 120
pos.intended_join = False; pos.intended_clamp = False   # drift bid
s.positions[NAE] = pos
s._events_live = {ET}
run(s._v4_manage_resting(NAE, pos, book(57, 59), now))  # target 58 >= ask-1
check(any(c["label"] == "v4_cancel_bid_marketable_stale" for c in s.cancelled),
      "flag ON: drift bid gone marketable-stale in-play still cancels (named economic)")

# ---- 4. flag OFF: both cancels fire byte-identical ----
s = make_bot(ride=False); now = time.time()
pos = naef_pos(now); s.positions[NAE] = pos
ORDERS["ONAE"] = {"status": "canceled", "fill_count_fp": 0}
run(s.check_fills())
check(any(d.get("reason") == "match_start_buffer" for ev, d, _ in s.logs if ev == "entry_cancelled"),
      "flag OFF: T-15 buffer cancel restored")
s = make_bot(ride=False); now = time.time()
pos = naef_pos(now); s.positions[NAE] = pos
s._events_live = {ET}
run(s._v4_manage_resting(NAE, pos, book(56, 62), now))
check(any(ev == "match_live_resting_cancel" for ev, d, _ in s.logs),
      "flag OFF: match-live resting sweep restored")

# ---- 5. THE NAEF FRAME: in-play fill books normally, cell exit posts ----
s = make_bot(ride=True); now = time.time()
pos = naef_pos(now); pos.match_start_ts = now - 120
s.positions[NAE] = pos
s._events_live = {ET}
ORDERS["ONAE"] = {"status": "executed", "fill_count_fp": 5,
                  "average_fill_price_fp": 0.58}
run(s.check_fills())
fills = [d for ev, d, _ in s.logs if ev == "entry_filled"]
exits = [p for p in s.placed if p["action"] == "sell"]
check(len(fills) == 1 and fills[0]["qty"] == 5 and fills[0]["fill_price"] == 58,
      "in-play fill books normally (5 shares @58)")
check(len(exits) == 1 and exits[0]["count"] == 5 and exits[0]["price"] == 58 + 14,
      "cell exit posted at fill cell rule, full 5-share size")

# ---- 6. tripwires + placement gates untouched (source pins) ----
src_trip = inspect.getsource(M.LiveV3._mechanism_tripwire)
check("premarket_bids_ride_live" not in src_trip, "tripwire primitive does not consult the flag")
src_route = inspect.getsource(M.LiveV3._route_event)
check("premarket_bids_ride_live" not in src_route,
      "placement path untouched: NEW in-play placements remain forbidden")
src_init = inspect.getsource(M.LiveV3.__init__)
check('config.get("premarket_bids_ride_live", False)' in src_init,
      "code default False (legacy); deploy config ships true")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
