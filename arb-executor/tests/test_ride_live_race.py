#!/usr/bin/env python3
"""[C-RIDE-LIVE-RACE-FIX] The reconcile x check_fills race surfaced by
premarket_bids_ride_live. A fallback_maker clamp bid that fills as a maker while
ride-live keeps it resting can be reached by the 60s steady-state reconcile
BEFORE check_fills books it. The pre-fix reconcile bumped entry_qty 0->N on a
still-phase=entry_resting Position and `continue`d without booking or posting the
exit -- permanently blocking check_fills (filled N > entry_qty N == False) and
skipping the naked-adoption path below the continue. Live victims 2026-06-13:
MARITO-MAR (Marcinko), SINYUA-YUA (Yuan), BERJAN-JAN (Jansen), OKOGRE-OKO
(Okonkwo) -- each a filled-but-unbooked clamp leg with no resting exit.

Burden:
  1. RACE: reconcile reaches an unbooked ride-live fill first -> it BOOKS the
     fill and POSTS the cell exit (not a silent entry_qty bump + continue).
  2. check_fills-FIRST: a position already booked (phase=active, exit posted)
     is left untouched by reconcile -- no re-book, no double exit.
  3. genuinely RESTING unfilled bid (no exchange position) is untouched.
  4. MANUAL exit already on the book -> adopted (reconcile_v4_exit_found), the
     bot does NOT double-post over the operator's sell.

Run: cd arb-executor && python3 tests/test_ride_live_race.py
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
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# ---- scenario-driven api_get stub ------------------------------------------
# SCN: {"positions":[mp...], "resting":[ord...], "ticker_sells":{tk:[ord...]}}
SCN = {"positions": [], "resting": [], "ticker_sells": {}}
async def _fake_api_get(sess, ak, pk, path, rl):
    if "/portfolio/positions" in path:
        return {"market_positions": SCN["positions"]}
    if "orders?ticker=" in path:
        # per-ticker resting sells check (used by _v4_reconcile_naked)
        for tk, lst in SCN["ticker_sells"].items():
            if ("ticker=%s" % tk) in path:
                return {"orders": lst}
        return {"orders": []}
    if "/portfolio/orders?status=resting" in path:
        return {"orders": SCN["resting"]}
    if "/portfolio/orders/" in path:
        return None
    return {}
M.api_get = _fake_api_get

def mp(tk, qty, avg):
    # market_position shape (cents avg -> dollars exposure)
    return {"ticker": tk, "position_fp": "%d.00" % qty,
            "market_exposure_dollars": "%.6f" % (qty * avg / 100.0),
            "total_traded_dollars": "%.6f" % (qty * avg / 100.0)}

def sell_order(tk, price, qty=5, oid="MANUAL_SELL"):
    return {"ticker": tk, "action": "sell", "side": "yes",
            "yes_price_dollars": "%.4f" % (price / 100.0),
            "remaining_count_fp": "%d.00" % qty, "order_id": oid}

def buy_order(tk, price, qty=5, oid="BID1"):
    return {"ticker": tk, "action": "buy", "side": "yes",
            "yes_price_dollars": "%.4f" % (price / 100.0),
            "remaining_count_fp": "%d.00" % qty, "order_id": oid}

def make_pos(tk, et="EV", cat="ATP_CHALL", **kw):
    return M.Position(ticker=tk, event_ticker=et, category=cat,
                      direction="", cell_name="", cell_cfg={}, **kw)

BOUND = ("reconcile", "_v4_reconcile_naked", "_book_v4_entry_fill",
         "_v4_apply_exit", "_cancel_sibling_if_paired_over_cap",
         "_sibling_ticker", "_paired_basis_ok", "_untombstone_entry")

def make_bot(band=(20, "exit")):
    s = types.SimpleNamespace()
    s.positions = {}
    s.books = {}
    s.event_tickers = {}
    s.ticker_to_event = {}
    s.event_start_time = {}
    s.processed_events = set()
    s.inflight_orders = set()
    s._booking_inflight = set()
    s.entry_size = 5
    s.n_entries = 0
    s.session = None; s.ak = None; s.pk = None; s.rl = None
    s.completion_reprice = False
    s.completion_cells = {}
    s.categories_enabled = {"ATP_CHALL", "ATP_MAIN", "WTA_CHALL", "WTA_MAIN"}
    s.fv_scenarios_enabled = False
    s.operator_manual_mode = True
    s.manual_bids = {}
    s._bot_order_tickers = set()
    s._bot_order_ids = set()
    s.fv_observe = False
    s.config = {}
    s.dca_fill_floor = 0
    s.dca_size = 5
    s.cell_lookup = lambda cat, price: price
    s.exit_rule_for = lambda cat, price: band
    s.exit_depth_floor = 0
    s.get_category = lambda tk: ("ATP_CHALL" if "CHALLENGER" in tk
                                 else "WTA_MAIN" if tk.startswith("KXWTAMATCH")
                                 else "ATP_MAIN")
    s._legacy_cell_lookup = lambda cat, d, p: (p, {"exit_cents": 20, "strategy": "noDCA"})
    s.paired_cap_enforced = False
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s._save_processed = lambda: None
    s._save_v4_resting = lambda: None
    s.placed = []
    s.cancelled = []
    async def place_order(tk, action, side, price, count, post_only=True):
        s.placed.append({"tk": tk, "action": action, "price": price, "count": count})
        return "OID_%d" % len(s.placed), {"order": {"status": "resting"}}
    s.place_order = place_order
    async def cancel_order(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        return True
    s.cancel_order = cancel_order
    for nm in BOUND:
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

def events(s, name):
    return [d for (e, d, t) in s.logs if e == name]
def sells_placed(s):
    return [p for p in s.placed if p["action"] == "sell"]

TK = "KXATPCHALLENGERMATCH-26JUN13BERJAN-JAN"
ET = "KXATPCHALLENGERMATCH-26JUN13BERJAN"

# ── 1. RACE: reconcile reaches the unbooked ride-live fill first ─────────────
print("--- 1. reconcile-first on an unbooked ride-live clamp fill ---")
s = make_bot()
s.ticker_to_event = {TK: ET}
s.positions[TK] = make_pos(TK, et=ET, cat="ATP_CHALL", entry_price=34,
                           entry_order_id="CLAMP_OID", entry_qty=0,
                           phase="entry_resting", is_v4=True,
                           entry_mode="fallback_maker", intended_join=True)
SCN.update({"positions": [mp(TK, 5, 34)], "resting": [], "ticker_sells": {}})
run(s.reconcile(quiet=True))
p = s.positions[TK]
check(p.phase == "active" and p.entry_qty == 5,
      "race: fill BOOKED (phase active, qty 5) -- not a silent entry_qty bump")
ef = events(s, "entry_filled")
check(len(ef) == 1 and ef[0]["source"] == "reconcile_adoption",
      "race: entry_filled emitted via reconcile_adoption")
sp = sells_placed(s)
check(len(sp) == 1 and sp[0]["count"] == 5 and sp[0]["price"] == min(34 + 20, M.EXIT_PRICE_CAP),
      "race: exactly one cell exit posted at filled size (gated_optima band)")

# ── 2. check_fills-FIRST: already-booked position left untouched ─────────────
print("--- 2. check_fills booked first -> reconcile no-ops ---")
s = make_bot()
s.ticker_to_event = {TK: ET}
s.positions[TK] = make_pos(TK, et=ET, cat="ATP_CHALL", entry_price=34,
                           entry_order_id="CLAMP_OID", entry_qty=5,
                           phase="active", is_v4=True,
                           exit_order_id="EXIT_OID", exit_price=54)
SCN.update({"positions": [mp(TK, 5, 34)], "resting": [], "ticker_sells": {}})
run(s.reconcile(quiet=True))
p = s.positions[TK]
check(p.phase == "active" and p.entry_qty == 5 and p.exit_order_id == "EXIT_OID",
      "check_fills-first: booked position unchanged")
check(not events(s, "entry_filled"), "check_fills-first: no re-book")
check(not sells_placed(s), "check_fills-first: no double exit posted")

# ── 3. genuinely resting UNFILLED bid (no exchange position) untouched ───────
print("--- 3. unfilled resting bid is untouched ---")
s = make_bot()
s.ticker_to_event = {TK: ET}
s.positions[TK] = make_pos(TK, et=ET, cat="ATP_CHALL", entry_price=34,
                           entry_order_id="BID1", entry_qty=0,
                           phase="entry_resting", is_v4=True,
                           entry_mode="fallback_maker", intended_join=True)
SCN.update({"positions": [], "resting": [buy_order(TK, 34, oid="BID1")],
            "ticker_sells": {}})
run(s.reconcile(quiet=True))
p = s.positions[TK]
check(p.phase == "entry_resting" and p.entry_qty == 0,
      "unfilled bid: position still entry_resting, entry_qty 0")
check(not events(s, "entry_filled") and not sells_placed(s),
      "unfilled bid: no booking, no exit")
check(not any(c["oid"] == "BID1" for c in s.cancelled),
      "unfilled bid: entry_resting bid NOT orphan-cancelled")

# ── 4. MANUAL exit already on the book -> adopt, no double-post ──────────────
print("--- 4. operator's manual sell present -> adopted, not double-posted ---")
s = make_bot()
s.ticker_to_event = {TK: ET}
s.positions[TK] = make_pos(TK, et=ET, cat="ATP_CHALL", entry_price=34,
                           entry_order_id="CLAMP_OID", entry_qty=0,
                           phase="entry_resting", is_v4=True,
                           entry_mode="fallback_maker", intended_join=True)
SCN.update({"positions": [mp(TK, 5, 34)],
            "resting": [sell_order(TK, 60, oid="OP_SELL")],
            "ticker_sells": {TK: [sell_order(TK, 60, oid="OP_SELL")]}})
run(s.reconcile(quiet=True))
p = s.positions[TK]
check(p.exit_order_id == "OP_SELL" and p.exit_price == 60,
      "manual: adopted the operator's resting sell (exit linked to OP_SELL @60)")
check(len(events(s, "reconcile_v4_exit_found")) == 1,
      "manual: reconcile_v4_exit_found emitted")
check(not sells_placed(s),
      "manual: bot did NOT double-post a sell over the operator's exit")

print("\n%s  (%d failures)" % ("ALL PASS" if fails == 0 else "FAILURES", fails))
sys.exit(1 if fails else 0)
