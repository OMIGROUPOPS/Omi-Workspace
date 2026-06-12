#!/usr/bin/env python3
"""[C-PARTIAL-BOOKING P0v2] partial fills booked through the phase flip; exits
count-based; manual-order adoption; settlement with partial history.

THE TAN FRAME (NAETAN-TAN 2026-06-12, first partial ever): buy 5@40 filled
1/1/2/1 across ~5.5 min; the old check_fills scope (phase=="entry_resting"
only) booked increment 1, flipped phase to active, and never polled again ->
4 shares naked. Entry orders are now polled while NON-TERMINAL regardless of
phase; the exit re-sizes to OPEN shares each increment (atomic cancel-and-
repost, never both resting, exchange-clamped never-oversell); exit_filled is
a COUNT (complete only when the order executes); partial-exit remainders stay
managed; settlement prices only the still-open shares.
Run: cd arb-executor && python3 tests/test_partial_booking.py
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

# controllable exchange: order-id -> {status, fill_count_fp}; ticker -> open shares
ORDERS = {}
OPEN = {}
RESTING_BY_TICKER = {}
POSLIST = []   # for reconcile: market_positions payload
async def fake_api_get(sess, ak, pk, path, rl):
    if "/portfolio/orders/" in path and "?" not in path:
        oid = path.rsplit("/", 1)[1]
        return {"order": ORDERS.get(oid, {"status": "canceled", "fill_count_fp": 0})}
    if "/portfolio/positions?ticker=" in path:
        tk = path.split("ticker=")[1].split("&")[0]
        return {"market_positions": [{"ticker": tk, "position_fp": str(OPEN.get(tk, 0))}]}
    if "/portfolio/positions" in path:
        return {"market_positions": POSLIST}
    if "/portfolio/orders?ticker=" in path:
        tk = path.split("ticker=")[1].split("&")[0]
        return {"orders": RESTING_BY_TICKER.get(tk, [])}
    if "/portfolio/orders" in path:
        return {"orders": RESTING_BY_TICKER.get("_ALL_", [])}
    return {}
M.api_get = fake_api_get

def mk(tk, et, **kw):
    p = M.Position(ticker=tk, event_ticker=et, category="WTA_CHALL",
                   direction="underdog", cell_name="", cell_cfg={})
    for k, v in kw.items(): setattr(p, k, v)
    return p

BOUND = ("check_fills", "_book_v4_entry_fill", "_parse_entry_fill",
         "_v4_apply_exit", "_cancel_sibling_if_paired_over_cap",
         "_sibling_ticker", "_sibling_engageable", "_paired_basis_ok",
         "_completion_buffer_exempt", "_cancel_entry_and_resolve",
         "_untombstone_entry", "_is_match_live", "process_settlement",
         "exit_rule_for", "cell_lookup")

def make_bot():
    s = types.SimpleNamespace()
    s.positions = {}; s.books = {}; s.event_tickers = {}
    s._events_live = set(); s._trade_times = {}; s._window_open = {}
    s.event_start_time = {}; s._live_stage1 = {}; s._live_skip_logged = set()
    s.inflight_orders = set(); s._mgmt_inflight = set(); s._booking_inflight = set()
    s.processed_events = set(); s._save_processed = lambda: None
    s.session = None; s.ak = None; s.pk = None; s.rl = None
    s.entry_size = 5; s.n_entries = 0; s.n_exits = 0; s.n_settlements = 0
    s.paired_cap_enforced = True
    s.completion_reprice = False; s.completion_disabled = False
    s.completion_cells = {}
    s.exit_table = {"WTA_CHALL": {c: (7, "exit") for c in range(1, 99)}}
    s.regime_lookup = lambda cat, price: "r35_44"
    s.exit_depth_floor = 0
    s.dca_fill_floor = 0
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
    def exit_rule_for(cat, price):
        return (7, "exit")
    s.exit_rule_for = exit_rule_for
    s.cell_lookup = lambda cat, price: price
    for nm in BOUND:
        if nm in ("exit_rule_for", "cell_lookup"):
            continue
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

ET = "KXWTACHALLENGERMATCH-26JUN12NAETAN"; TAN = ET + "-TAN"

def sells_resting(s):
    posts = [p for p in s.placed if p["action"] == "sell"]
    cancels = [c for c in s.cancelled if c["oid"].startswith("OID_")]
    return len(posts) - len(cancels)

# ---- 1. THE TAN FRAME: 1/1/2/1 increments across the phase flip ----
s = make_bot()
s.event_tickers = {ET: {TAN}}
pos = mk(TAN, ET, entry_price=40, target_price=40, entry_order_id="OB",
         entry_mode="resting_maker", play_type="v4_marketable_clamp", is_v4=True,
         phase="entry_resting", match_start_ts=time.time() + 4 * 3600)
s.positions[TAN] = pos
for step, (fc, st, op) in enumerate(((1, "resting", 1), (2, "resting", 2),
                                     (4, "resting", 4), (5, "executed", 5)), 1):
    ORDERS["OB"] = {"status": st, "fill_count_fp": fc}
    OPEN[TAN] = op
    run(s.check_fills())
    exits = [p for p in s.placed if p["action"] == "sell"]
    check(pos.entry_qty == fc, "step %d: booked qty %d == exchange %d" % (step, pos.entry_qty, fc))
    check(exits and exits[-1]["count"] == fc and exits[-1]["price"] == 47,
          "step %d: exit re-sized to %d@47" % (step, fc))
    check(sells_resting(s) == 1, "step %d: exactly ONE sell resting" % step)
booked = [d for ev, d, _ in s.logs if ev == "entry_filled"]
check([d["new_fills"] for d in booked] == [1, 1, 2, 1],
      "increments booked 1/1/2/1 (idempotent delta booking)")
check(pos.phase == "active", "position active through every increment")
check(pos.entry_order_done is True,
      "entry order marked done in the executing pass (terminal + fully booked)")

# ---- 2. manual-order adoption (boot reconcile links, no second sell) ----
s = make_bot()
for nm in ("reconcile", "get_category"):
    setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
s.ticker_to_event = {TAN: ET}; s.ticker_category = {}
s.config = {}
s._legacy_cell_lookup = lambda cat, direction, price: (None, None)  # no DCA adoption
s.dca_size = 5
POSLIST[:] = [{"ticker": TAN, "position_fp": "4.00", "market_exposure_dollars": "1.60"}]
RESTING_BY_TICKER["_ALL_"] = [{"ticker": TAN, "order_id": "MANUAL47", "action": "sell",
                               "side": "yes", "yes_price": 47,
                               "remaining_count_fp": "4.00"}]
run(s.reconcile(quiet=True))
p = s.positions.get(TAN)
check(p is not None and p.entry_qty == 4 and p.exit_order_id == "MANUAL47"
      and p.exit_price == 47,
      "boot reconcile ADOPTS the manual sell as the exit (id linked, 4 shares)")
check(not any(x["action"] == "sell" for x in s.placed) and not s.cancelled,
      "no second sell posted, nothing cancelled (adopt-without-duplicating)")
POSLIST[:] = []; RESTING_BY_TICKER.clear()

# ---- 3. partial exit 1-of-5: remainder stays managed ----
s = make_bot()
s.event_tickers = {ET: {TAN}}
pos = mk(TAN, ET, entry_price=40, entry_qty=5, entry_order_done=True, is_v4=True,
         phase="active", exit_order_id="EX5", exit_price=47,
         match_start_ts=time.time() + 3600)
s.positions[TAN] = pos
ORDERS["EX5"] = {"status": "resting", "fill_count_fp": 1}
run(s.check_fills())
evs = [d for ev, d, _ in s.logs if ev == "exit_filled"]
check(len(evs) == 1 and evs[0]["new_fills"] == 1 and evs[0]["complete"] is False,
      "partial exit books the increment (1 of 5, complete=false)")
check(pos.exit_filled_qty == 1 and pos.phase == "active" and pos.exit_order_id == "EX5"
      and not s.cancelled,
      "remainder stays managed: order untouched, position open")
ORDERS["EX5"] = {"status": "executed", "fill_count_fp": 5}
run(s.check_fills())
evs = [d for ev, d, _ in s.logs if ev == "exit_filled"]
check(len(evs) == 2 and evs[1]["complete"] is True and pos.settled
      and pos.pnl_cents == 35 and s.n_exits == 1,
      "completion books the remaining 4, position settles, pnl 5x7=35c")

# ---- 4. SHESHI same-second multi-record (single poll sees the full count) ----
s = make_bot()
ET2 = "KXATPMATCH-26JUN12SHESHI"; SHE = ET2 + "-SHE"
s.event_tickers = {ET2: {SHE}}
pos = mk(SHE, ET2, entry_price=89, target_price=89, entry_order_id="OS",
         entry_mode="resting_maker", is_v4=True, phase="entry_resting",
         match_start_ts=time.time() + 4 * 3600)
s.positions[SHE] = pos
ORDERS["OS"] = {"status": "executed", "fill_count_fp": 5}
OPEN[SHE] = 5
run(s.check_fills())
booked = [d for ev, d, _ in s.logs if ev == "entry_filled"]
check(len(booked) == 1 and booked[0]["qty"] == 5 and booked[0]["new_fills"] == 5,
      "same-second multi-record books once at the full count (no regression)")

# ---- 5. settlement with partial history: only open shares priced ----
s = make_bot()
pos = mk(TAN, ET, entry_price=40, entry_qty=5, exit_filled_qty=1, pnl_cents=7,
         is_v4=True, phase="active", exit_order_id="", entry_order_done=True)
s.positions[TAN] = pos
run_settle = lambda: M.LiveV3.process_settlement(s, TAN, 100, time.time(), "rest_poll")
async def _settle():
    M.LiveV3.process_settlement(s, TAN, 100, time.time(), "rest_poll")
run(_settle())
sevs = [d for ev, d, _ in s.logs if ev == "settled"]
check(len(sevs) == 1 and sevs[0]["settled_qty"] == 4
      and sevs[0]["pnl_cents"] == (100 - 40) * 4 + 7,
      "settlement prices 4 open shares + keeps the 7c partial-exit pnl (no double count)")

# ---- source pins ----
src = inspect.getsource(M.LiveV3.check_fills)
check('pos.phase == "active" and pos.entry_order_id' in src
      and "not pos.entry_order_done" in src,
      "entry poll runs on active phase while order non-terminal (the 3427 scope defect)")
src_ae = inspect.getsource(M.LiveV3._v4_apply_exit)
check("open_qty = filled - pos.exit_filled_qty" in src_ae
      and "min(open_qty, ex_open)" in src_ae,
      "exit sizes to OPEN shares, exchange-clamped (never oversell)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
