#!/usr/bin/env python3
"""[C-FEEDER FIX-3] Option (a): intended_clamp — deliberate ask-1 rests exempt
from bid_marketable_stale; buffer stays 1; drift bids still cancel.

THE AUGMAJ FRAME (2026-06-12 overnight): locked 35/35 main-tour book, table
target 34 = ask-1, knowingly posted, then bid_marketable_stale killed it next
tick -> 206 place/cancel cycles on one event (98 on the sibling; KRERUS 61).
The placement was INTENTIONAL: the flag is keyed at placement from the
decision-time book and the bid now rests. A bid placed at safe distance that
the book then drifts onto keeps the full stale rule.
Run: cd arb-executor && python3 tests/test_intended_clamp.py
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

def book(bid, ask):
    return types.SimpleNamespace(best_bid=bid, best_ask=ask, bids={}, asks={},
        updated=time.time(), last_trade_price=0, last_trade_ts=0.0)

def mk(tk, et, **kw):
    p = M.Position(ticker=tk, event_ticker=et, category="ATP_MAIN",
                   direction="", cell_name="", cell_cfg={})
    for k, v in kw.items(): setattr(p, k, v)
    return p

BOUND = ("_sibling_ticker", "_sibling_engageable", "_paired_basis_ok",
         "_resting_cancel_reason", "_is_match_live", "_taker_spread_ok",
         "_fallback_order", "_reprice_target", "_completion_buffer_exempt",
         "_v4_manage_resting", "_v4_manage_resting_inner",
         "_cancel_entry_and_resolve", "_parse_entry_fill", "_book_v4_entry_fill",
         "_v4_apply_exit", "_cancel_sibling_if_paired_over_cap", "_untombstone_entry",
         "_save_v4_resting", "_load_v4_resting",
         "_intended_clamp_at_placement", "_intended_join_at_placement")

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
    s.entry_table = {("ATP_MAIN", "r25_34"): (180, 1, 0, 0)}
    s.regime_lookup = lambda cat, price: "r25_34"
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
    for nm in BOUND:
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

async def fake_api_get(sess, ak, pk, path, rl):
    if "/portfolio/orders/" in path and "?" not in path:
        return {"order": {"status": "canceled", "fill_count_fp": 0}}
    return {"orders": []}
M.api_get = fake_api_get

ET = "KXATPMATCH-26JUN12AUGMAJ"; A = ET + "-MAJ"

# ---- 1. the pure key ----
s = make_bot()
check(s._intended_clamp_at_placement("resting_maker", 34, 35) is True,
      "resting-maker at ask-1 (locked 35/35 -> target 34) -> intended_clamp")
check(s._intended_clamp_at_placement("resting_maker", 34, 37) is False,
      "resting-maker at safe distance (ask 37) -> NOT clamped")
check(s._intended_clamp_at_placement("marketable_clamp", 34, 35) is False,
      "marketable_clamp mode not keyed here (entry_mode already RUN-7-exempt)")

# ---- 2. THE AUGMAJ FRAME: clamp bid RESTS through the stale rule ----
s = make_bot()
pos = mk(A, ET, entry_price=34, target_price=34, entry_order_id="OID_A",
         entry_mode="resting_maker", play_type="v4_resting_maker", is_v4=True,
         phase="entry_resting", match_start_ts=time.time() + 4 * 3600,
         intended_clamp=True)
s.positions[A] = pos
run(s._v4_manage_resting(A, pos, book(35, 35), time.time()))
check(not s.cancelled, "AUGMAJ frame: intended-clamp bid at ask-1 RESTS (no stale cancel)")
check(pos.entry_order_id == "OID_A", "order untouched after manage pass")

# ---- 3. genuine drift bid still cancels (buffer stays 1) ----
s = make_bot()
pos = mk(A, ET, entry_price=34, target_price=34, entry_order_id="OID_D",
         entry_mode="resting_maker", play_type="v4_resting_maker", is_v4=True,
         phase="entry_resting", match_start_ts=time.time() + 4 * 3600,
         intended_clamp=False)  # placed when ask was 37: not a clamp
s.positions[A] = pos
run(s._v4_manage_resting(A, pos, book(33, 35), time.time()))
check(any(c["label"] == "v4_cancel_bid_marketable_stale" for c in s.cancelled),
      "drift bid (flag unset) the book moved onto -> still cancelled")
check(s.cancel_marketable_buffer == 1, "buffer untouched at 1")

# ---- 4. save/restore: sparse key round-trips; non-clamp legs keep legacy keys ----
s = make_bot()
s.positions = {
    "EV-C": mk("EV-C", "EV", entry_price=34, target_price=34, entry_order_id="O1",
               entry_mode="resting_maker", is_v4=True, phase="entry_resting",
               intended_clamp=True),
    "EV-N": mk("EV-N", "EV", entry_price=30, target_price=30, entry_order_id="O2",
               entry_mode="resting_maker", is_v4=True, phase="entry_resting"),
}
s._save_v4_resting()
raw = json.loads(open(M.V4_RESTING_FILE).read())
legs = raw.get("legs", raw)
check(legs["EV-C"].get("intended_clamp") is True and "intended_clamp" not in legs["EV-N"],
      "sparse persistence: key present only when True")
s2 = make_bot()
s2._load_v4_resting()
check(s2.positions["EV-C"].intended_clamp is True
      and s2.positions["EV-N"].intended_clamp is False,
      "restart: intended_clamp restored True/False correctly")

# ---- 5. source pins: exemption shape + repost re-key from decision snapshot ----
src = inspect.getsource(M.LiveV3)
seg = src[src.index('creason == "bid_marketable_stale" and pos.intended_clamp'):]
check("should_cancel, creason = False, None" in seg[:200],
      "exemption wired in _v4_manage_resting_inner, same shape as intended_join")
check("pos.intended_clamp = (new_target == max(1, current_ask - 1))" in src
      and "pos.intended_join = (new_target == repost_bid)" in src,
      "move_repost re-keys BOTH flags from the decision-time snapshot")
check("intended_clamp=self._intended_clamp_at_placement(" in src,
      "placement keys the flag via the pure decision-time helper")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
