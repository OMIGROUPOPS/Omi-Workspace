#!/usr/bin/env python3
"""[C-MANUAL-FIRST OP-3] first trade on a leg owns it -- bot yields to
operator presence on a PER-LEG basis.

Gate fires on: resting manual bid (manual_bids registry) OR open
manual-attributed position. Covered paths: offset-table + engagement (one
placement-loop gate that precedes both), T-20 fallback + move-repost (one
manage-side gate). Withdrawal re-opens next pass; the sibling stays
bot-eligible; exits untouched (mixed-share sizing regression included).
Run: cd arb-executor && python3 tests/test_manual_first.py
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
        return {"order": {"status": "resting", "fill_count_fp": 0}}
    if "/portfolio/positions" in path:
        tk = path.split("ticker=")[1].split("&")[0] if "ticker=" in path else ""
        return {"market_positions": [{"ticker": tk, "position_fp": "99.00"}]}
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
    s.operator_manual_mode = True
    s.paired_cap_enforced = False; s.premarket_bids_ride_live = False
    s.manual_bids = {}; s._bot_order_ids = set(); s._bot_order_tickers = set()
    s.positions = {}; s.books = {}; s.event_tickers = {}
    s._events_live = set(); s._trade_times = {}; s._window_open = {}
    s.event_start_time = {}; s._live_stage1 = {}; s._live_skip_logged = set()
    s.inflight_orders = set(); s._mgmt_inflight = set(); s._booking_inflight = set()
    s.processed_events = set(); s._save_processed = lambda: None
    s.session = None; s.ak = None; s.pk = None; s.rl = None
    s.entry_size = 5; s.n_entries = 0; s.n_skips = 0
    s.cancel_on_marketable = True; s.cancel_marketable_buffer = 1
    s.v4_fallback_sec = 1200
    s.fallback_maker_clamp = True; s.maker_only_entry = True
    s.completion_reprice = False; s.completion_disabled = False
    s.entry_table = {("WTA_MAIN", "r75_84"): (180, 1, 0, 0)}
    s.regime_lookup = lambda cat, price: "r75_84"
    s.cell_lookup = lambda cat, price: price
    s.exit_rule_for = lambda cat, price: (7, "exit")
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
    for nm in ("_manual_owns_leg", "_v4_manage_resting", "_v4_manage_resting_inner",
               "_is_match_live", "_resting_cancel_reason", "_reprice_target",
               "_taker_spread_ok", "_fallback_order", "_cancel_entry_and_resolve",
               "_parse_entry_fill", "_untombstone_entry", "_v4_apply_exit",
               "_cancel_sibling_if_paired_over_cap", "_sibling_ticker",
               "_sibling_engageable", "_paired_basis_ok", "_completion_buffer_exempt",
               "_runway_status", "_fix6_reference"):
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

ET = "KXWTAMATCH-26JUN12RADRAK"; RAD, RAK = ET + "-RAD", ET + "-RAK"

# ---- 1. the ownership predicate + per-leg scope + re-open ----
s = make_bot()
s.manual_bids[RAD] = {"order_id": "OPERATOR-1", "price": 77, "qty": 5}
check(s._manual_owns_leg(RAD) is True, "resting manual bid -> leg owned")
check(s._manual_owns_leg(RAK) is False, "SIBLING leg stays bot-eligible (per-leg scope)")
s.manual_bids.pop(RAD)
check(s._manual_owns_leg(RAD) is False, "operator withdraws -> leg re-opens next pass")
s.positions[RAD] = mk(RAD, ET, entry_price=77, entry_qty=5, play_type="v4_manual")
check(s._manual_owns_leg(RAD) is True, "open manual-attributed position -> leg owned")
s.positions[RAD].play_type = "v4_resting_maker"
check(s._manual_owns_leg(RAD) is False, "bot-attributed position does NOT trigger the gate")
s.operator_manual_mode = False
s.manual_bids[RAD] = {"order_id": "OPERATOR-1", "price": 77, "qty": 5}
check(s._manual_owns_leg(RAD) is False, "mode off -> gate inert (legacy)")

# ---- 2. manage-side: no fallback re-post / move-repost onto his level ----
s = make_bot()
s.manual_bids[RAD] = {"order_id": "OPERATOR-1", "price": 77, "qty": 5}
now = time.time()
pos = mk(RAD, ET, entry_price=80, target_price=80, entry_order_id="OBOT",
         entry_mode="resting_maker", play_type="v4_resting_maker", is_v4=True,
         phase="entry_resting", match_start_ts=now + 1100,  # inside T-20 window
         intended_join=True)
s.positions[RAD] = pos
run(s._v4_manage_resting(RAD, pos, book(80, 82), now))
check(not s.placed and not s.cancelled and pos.entry_order_id == "OBOT",
      "manual-present leg: NO T-20 fallback re-post, bot bid holds as-is")
pos.match_start_ts = now + 3 * 3600
pos.last_cancel_repost_ts = 0
run(s._v4_manage_resting(RAD, pos, book(70, 72), now))   # 9c move: repost would fire
check(not s.placed and not s.cancelled,
      "manual-present leg: NO move-repost onto his level")
s.manual_bids.pop(RAD)
run(s._v4_manage_resting(RAD, pos, book(70, 72), now))
check(any(c["label"] == "v4_move_repost" for c in s.cancelled),
      "withdrawal re-opens: the same repost fires on the next pass")

# ---- 3. placement-loop gate: named skip precedes EVERY entry path ----
src = inspect.getsource(M.LiveV3._route_event)
i_gate = src.index('"reason": "manual_first"')
check(i_gate < src.index("tk in self.positions")
      and i_gate < src.index("_v4_entry_anchor")
      and i_gate < src.index("_engagement_join_eligible")
      and i_gate < src.index("_fix6_reference"),
      "manual_first gate precedes positions-check, offset anchor, engagement, FIX-6")
check('"reason": "manual_first"' in src, "named-skip vocabulary 'manual_first' in the journal")
src_mr = inspect.getsource(M.LiveV3._v4_manage_resting_inner)
check("_manual_owns_leg(tk)" in src_mr
      and src_mr.index("_manual_owns_leg(tk)") < src_mr.index("v4_fallback_sec"),
      "manage-side gate precedes the T-20 fallback and move-repost")

# ---- 4. exits untouched: mixed-share leg sizes to total open (regression) ----
s = make_bot()
s.manual_bids[RAD] = {"order_id": "OPERATOR-1", "price": 77, "qty": 5}
pos = mk(RAD, ET, entry_price=77, entry_qty=5, exit_filled_qty=0,
         play_type="v4_manual", is_v4=True, phase="active")
s.positions[RAD] = pos
run(s._v4_apply_exit(RAD, pos, 77, 5))
exits = [p for p in s.placed if p["action"] == "sell"]
check(len(exits) == 1 and exits[0]["count"] == 5 and exits[0]["price"] == 84,
      "exit machinery untouched by the gate: manual-owned leg still gets its 5-share exit")
src_ae = inspect.getsource(M.LiveV3._v4_apply_exit)
check("_manual_owns_leg" not in src_ae, "no manual-first logic anywhere in the exit path")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
