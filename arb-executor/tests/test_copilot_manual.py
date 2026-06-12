#!/usr/bin/env python3
"""[C-COPILOT] operator_manual_mode: foreign bids adopted, never killed; ITF
see-not-trade.

LIVE EXHIBIT (2026-06-12): the orphan sweep cancelled the operator's manual
Raducanu bids on every reconcile pass (orphan_buy_cancelled 14:59:34 ET 5@79,
15:01:35 ET 5@77) -- id-guarding useless, re-posts carry new ids.
Plex's three required tests: (1) a foreign resting buy survives the sweep;
(2) a foreign fill books a complete ledger row at the FILL cell with a
per-cell exit at filled size, attribution=manual via the bot's own order-id
registry (unknown order = manual by definition); (3) operator pulls his own
bid -> untracked cleanly, NO orphan-exit attempt. Plus ITF: visibility-only
mapping (zero bot placements) with manual fills adopted and exits borrowed
from the Challenger surface at the fill cent.
Run: cd arb-executor && python3 tests/test_copilot_manual.py
"""
import sys, types, time, asyncio, inspect, json
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

POSLIST = []
RESTING_ALL = []
async def fake_api_get(sess, ak, pk, path, rl):
    if "/portfolio/orders/" in path and "?" not in path:
        return {"order": {"status": "resting", "fill_count_fp": 0}}
    if "/portfolio/positions" in path:
        if "ticker=" in path:
            tk = path.split("ticker=")[1].split("&")[0]
            return {"market_positions": [p for p in POSLIST if p["ticker"] == tk]}
        return {"market_positions": POSLIST}
    if "/portfolio/orders?ticker=" in path:
        tk = path.split("ticker=")[1].split("&")[0]
        return {"orders": [o for o in RESTING_ALL if o.get("ticker") == tk]}
    if "/portfolio/orders" in path:
        return {"orders": RESTING_ALL}
    return {}
M.api_get = fake_api_get

def make_bot():
    s = types.SimpleNamespace()
    s.operator_manual_mode = True
    s.paired_cap_enforced = False
    s.premarket_bids_ride_live = True
    s.fv_scenarios_enabled = False
    s.categories_enabled = ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"]
    s._bot_order_ids = set(); s._bot_order_tickers = set(); s.manual_bids = {}
    s.positions = {}; s.books = {}; s.event_tickers = {}
    s._events_live = set(); s._trade_times = {}; s._window_open = {}
    s.event_start_time = {}; s._live_stage1 = {}; s._live_skip_logged = set()
    s.inflight_orders = set(); s._mgmt_inflight = set(); s._booking_inflight = set()
    s.processed_events = set(); s._save_processed = lambda: None
    s.session = None; s.ak = None; s.pk = None; s.rl = None
    s.entry_size = 5; s.n_entries = 0; s.n_exits = 0
    s.completion_reprice = False; s.completion_disabled = False
    s.completion_cells = {}
    s.ticker_to_event = {}; s.ticker_category = {}
    s.config = {}; s.dca_size = 5; s.dca_fill_floor = 0
    s.exit_table = {"WTA_MAIN": {c: (7, "exit") for c in range(5, 95)},
                    "WTA_CHALL": {c: (9, "exit") for c in range(5, 95)},
                    "ATP_CHALL": {c: (11, "exit") for c in range(5, 95)}}
    s.regime_lookup = lambda cat, price: "r75_84"
    s._legacy_cell_lookup = lambda cat, direction, price: (None, None)
    s.exit_depth_floor = 0
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s.placed = []; s.cancelled = []
    async def place_order(tk, action, side, price, count, post_only=True):
        s.placed.append({"tk": tk, "action": action, "price": price, "count": count})
        oid = "BOT_%d" % len(s.placed)
        s._bot_order_ids.add(oid); s._bot_order_tickers.add(tk)
        return oid, {"order": {"status": "resting"}}
    s.place_order = place_order
    async def cancel_order(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        return True
    s.cancel_order = cancel_order
    s._save_v4_resting = lambda: None
    for nm in ("reconcile", "get_category", "cell_lookup", "exit_rule_for",
               "_v4_reconcile_naked", "_book_v4_entry_fill", "_parse_entry_fill",
               "_v4_apply_exit", "_cancel_sibling_if_paired_over_cap",
               "_sibling_ticker", "_sibling_engageable", "_paired_basis_ok",
               "_untombstone_entry", "_cancel_entry_and_resolve"):
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

RAD = "KXWTAMATCH-26JUN12RADRAK-RAD"

# ---- 1. foreign resting buy survives the sweep ----
s = make_bot()
POSLIST[:] = []
RESTING_ALL[:] = [{"ticker": RAD, "order_id": "OPERATOR-1", "action": "buy",
                   "side": "yes", "yes_price": 81, "remaining_count_fp": "5.00"}]
run(s.reconcile(quiet=True))
check(not s.cancelled, "foreign resting buy 5@81 SURVIVES the sweep (the live-exhibit kill path)")
obs = [d for ev, d, _ in s.logs if ev == "manual_bid_observed"]
check(len(obs) == 1 and obs[0]["order_id"] == "OPERATOR-1" and obs[0]["price"] == 81,
      "manual_bid_observed logged with the foreign order id")
check(s.manual_bids.get(RAD, {}).get("order_id") == "OPERATOR-1", "tracked in manual_bids")
run(s.reconcile(quiet=True))
check(len([d for ev, d, _ in s.logs if ev == "manual_bid_observed"]) == 1,
      "observed once per order id (no log spam across passes)")
# a BOT-registry id in the orphan list keeps the legacy cancel (regression guard)
s2 = make_bot()
s2._bot_order_ids.add("BOTLEAK-1")
RESTING_ALL[:] = [{"ticker": RAD, "order_id": "BOTLEAK-1", "action": "buy",
                   "side": "yes", "yes_price": 50, "remaining_count_fp": "5.00"}]
run(s2.reconcile(quiet=True))
check(any(c["label"] == "orphan_buy_reconcile_cleanup" for c in s2.cancelled),
      "a bot-registry id in the orphan list still gets the legacy cancel")

# ---- 2. foreign fill -> complete ledger row, cell exit, attribution=manual ----
s = make_bot()
s.manual_bids[RAD] = {"order_id": "OPERATOR-1", "price": 81, "qty": 5,
                      "first_seen": time.time()}
POSLIST[:] = [{"ticker": RAD, "position_fp": "5.00", "market_exposure_dollars": "4.05"}]
RESTING_ALL[:] = []
run(s.reconcile(quiet=True))
adopt = [d for ev, d, _ in s.logs if ev == "reconcile_v4_adopted"]
fills = [d for ev, d, _ in s.logs if ev == "entry_filled"]
exits = [p for p in s.placed if p["action"] == "sell"]
check(len(adopt) == 1 and adopt[0]["attribution"] == "manual" and adopt[0]["avg"] == 81,
      "adoption row attribution=manual at the FILL cell (81)")
check(len(fills) == 1 and fills[0]["qty"] == 5 and fills[0]["source"] == "reconcile_adoption"
      and fills[0]["play_type"] == "v4_manual",
      "entry_filled ledger row complete (5 shares @81, play_type v4_manual)")
check(len(exits) == 1 and exits[0]["count"] == 5 and exits[0]["price"] == 81 + 7,
      "per-cell exit posted at FILLED size (5@88, WTA_MAIN band +7)")
check(RAD not in s.manual_bids, "manual_bids entry consumed by the adoption")
# attribution falls back to the id/ticker registry when the bid was never observed
s = make_bot()
POSLIST[:] = [{"ticker": RAD, "position_fp": "5.00", "market_exposure_dollars": "4.05"}]
RESTING_ALL[:] = []
run(s.reconcile(quiet=True))
adopt = [d for ev, d, _ in s.logs if ev == "reconcile_v4_adopted"]
check(adopt and adopt[0]["attribution"] == "manual",
      "unknown order = manual by definition (no bot orders for the ticker)")

# ---- 3. OPERATOR-CANCEL: pulled bid -> untracked, NO orphan-exit attempt ----
s = make_bot()
s.manual_bids[RAD] = {"order_id": "OPERATOR-1", "price": 81, "qty": 5,
                      "first_seen": time.time()}
POSLIST[:] = []; RESTING_ALL[:] = []
run(s.reconcile(quiet=True))
wd = [d for ev, d, _ in s.logs if ev == "manual_bid_withdrawn"]
check(len(wd) == 1 and wd[0]["order_id"] == "OPERATOR-1", "manual_bid_withdrawn logged")
check(RAD not in s.manual_bids, "untracked cleanly")
check(not s.placed and not s.cancelled, "NO orphan-exit attempt, nothing placed or cancelled")

# ---- 4. ITF see-not-trade ----
s = make_bot()
check(s.get_category("KXITFMATCH-26JUN12FOOBAR-FOO") == "ITF_M"
      and s.get_category("KXITFWMATCH-26JUN12BAZQUX-BAZ") == "ITF_W",
      "ITF series mapped: KXITFMATCH -> ITF_M, KXITFWMATCH -> ITF_W")
check(s.exit_rule_for("ITF_W", 62) == s.exit_rule_for("WTA_CHALL", 62)
      and s.exit_rule_for("ITF_M", 62) == s.exit_rule_for("ATP_CHALL", 62),
      "ITF exits BORROW the Challenger surface at the fill cent")
check("ITF_M" not in s.exit_table and "ITF_W" not in s.exit_table,
      "native CHALL cells never polluted (no ITF keys in the exit table)")
ITF = "KXITFWMATCH-26JUN12BAZQUX-BAZ"
POSLIST[:] = [{"ticker": ITF, "position_fp": "3.00", "market_exposure_dollars": "1.86"}]
RESTING_ALL[:] = []
run(s.reconcile(quiet=True))
adopt = [d for ev, d, _ in s.logs if ev == "reconcile_v4_adopted"]
exits = [p for p in s.placed if p["action"] == "sell"]
check(adopt and adopt[0]["attribution"] == "manual" and adopt[0]["category"] == "ITF_W",
      "manual ITF fill adopted with attribution ITF_W/manual")
check(exits and exits[0]["count"] == 3 and exits[0]["price"] == 62 + 9,
      "ITF exit posted at filled size from the borrowed WTA_CHALL band (+9)")
check(s.positions[ITF].category == "ITF_W", "position keeps its ITF category (ledger separability)")
check(not [p for p in s.placed if p["action"] == "buy"], "zero bot BUY placements on ITF")

# ---- 5. placement exclusion + config + registry (source/config pins) ----
src = inspect.getsource(M.LiveV3._route_event)
check(src.index("cat not in self.categories_enabled") < src.index("_engagement_join_eligible"),
      "categories gate precedes engagement/anchor/FIX-6: ITF can never place")
check("ITF" not in src, "no ITF special-casing in the placement path")
cfg = json.load(open(Path(REPO) / "config" / "deploy_v5_live.json"))
check(cfg["categories_enabled"] == ["ATP_MAIN", "WTA_MAIN", "ATP_CHALL", "WTA_CHALL"]
      and cfg.get("operator_manual_mode") is True,
      "config: categories_enabled untouched; operator_manual_mode ships true")
src_po = inspect.getsource(M.LiveV3.place_order)
check('_bot_order_ids", set()).add(oid)' in src_po,
      "every bot-placed order id enters the registry (the manual-by-definition source)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
