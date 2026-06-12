#!/usr/bin/env python3
"""[C-BID-SURVIVAL DIFF-2] intended_join exemption from bid_marketable_stale.

The Coria 2026-06-11 frame (29 place/cancel cycles on a 32/33 book, anchor age
marched 674->1759s, leg dead at the 1800s wall): a join bid now rests through
the window; drift bids (flag unset) keep the full stale rule; the flag is set
at PLACEMENT only (the cheap target==best_bid-at-evaluation key is NOT
implemented -- source-pinned); survives state save/restore; RUN-7's exemption
untouched. Run: cd arb-executor && python3 tests/test_join_bid_exemption.py
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
    p = M.Position(ticker=tk, event_ticker=et, category="ATP_CHALL",
                   direction="", cell_name="", cell_cfg={})
    for k, v in kw.items(): setattr(p, k, v)
    return p

BOUND = ("_sibling_ticker", "_sibling_engageable", "_paired_basis_ok",
         "_resting_cancel_reason", "_is_match_live", "_taker_spread_ok",
         "_fallback_order", "_reprice_target", "_completion_buffer_exempt",
         "_v4_manage_resting", "_v4_manage_resting_inner",
         "_cancel_entry_and_resolve", "_parse_entry_fill", "_book_v4_entry_fill",
         "_v4_apply_exit", "_cancel_sibling_if_paired_over_cap", "_untombstone_entry",
         "_save_v4_resting", "_load_v4_resting")

def make_bot():
    s = types.SimpleNamespace()
    s.positions = {}; s.books = {}; s.event_tickers = {}
    s._events_live = set(); s._trade_times = {}; s._window_open = {}
    s.inflight_orders = set(); s._mgmt_inflight = set(); s._booking_inflight = set()
    s.processed_events = set(); s._save_processed = lambda: None
    s.session = None; s.ak = None; s.pk = None; s.rl = None
    s.entry_size = 5; s.n_entries = 0
    s.cancel_on_marketable = True; s.cancel_marketable_buffer = 1
    s.v4_fallback_sec = 1200
    s.fallback_maker_clamp = True; s.maker_only_entry = True
    s.completion_reprice = False; s.completion_disabled = False
    s.entry_table = {("ATP_CHALL", "r25_34"): (180, 1, 0, 0)}
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

ET = "EV"; A = "EV-COR"

# ---- 1. CORIA FRAME: join bid rests through the window, never churns ----
s = make_bot()
now = time.time()
cor = mk(A, ET, entry_price=32, entry_order_id="cor1", phase="entry_resting", is_v4=True,
         target_price=32, entry_mode="resting_maker", intended_join=True,
         match_start_ts=now + 7200, entry_posted_ts=now)
s.positions = {A: cor}
b = book(32, 33)   # the exact 1c-spread book that churned 29 cycles
for i in range(30):  # 30 manage passes (the loop that produced 29 cancels)
    run(s._v4_manage_resting_inner(A, cor, b, now + i * 110))
check(len(s.cancelled) == 0 and len(s.placed) == 0 and cor.entry_order_id == "cor1",
      "Coria frame: join bid placed once, rests 30 manage passes, ZERO churn")
check(not [d for (e, d, t) in s.logs if e == "v4_resting_cancel"],
      "no v4_resting_cancel emitted for the resting join bid")

# ---- 2. DRIFT bid (flag unset) on the same book: full stale rule applies ----
s = make_bot()
drift = mk(A, ET, entry_price=32, entry_order_id="dr1", phase="entry_resting", is_v4=True,
           target_price=32, entry_mode="resting_maker", intended_join=False,
           match_start_ts=now + 7200)
s.positions = {A: drift}
run(s._v4_manage_resting_inner(A, drift, book(32, 33), now))
check(any(c["label"] == "v4_cancel_bid_marketable_stale" for c in s.cancelled),
      "drift bid (flag unset): bid_marketable_stale still cancels")

# ---- 3. degenerate book still cancels EVEN for join bids ----
s = make_bot()
j2 = mk(A, ET, entry_price=32, entry_order_id="j2", phase="entry_resting", is_v4=True,
        target_price=32, entry_mode="resting_maker", intended_join=True,
        match_start_ts=now + 7200)
s.positions = {A: j2}
run(s._v4_manage_resting_inner(A, j2, book(0, 100), now))
check(any("degenerate" in c["label"] for c in s.cancelled),
      "degenerate book: join bid still cancelled (exemption is stale-only)")

# ---- 4. RUN-7 exemption untouched ----
s = make_bot()
fb = mk(A, ET, entry_price=32, entry_order_id="fb1", phase="entry_resting", is_v4=True,
        target_price=32, entry_mode="fallback_maker", intended_join=False,
        match_start_ts=now + 7200)
s.positions = {A: fb}
run(s._v4_manage_resting_inner(A, fb, book(32, 33), now))
check(len(s.cancelled) == 0, "RUN-7 exemption (fallback_maker) untouched: still exempt")

# ---- 5. flag survives state save/restore (sparse key; legacy shape preserved) ----
s = make_bot()
jp = mk("EV-J", "EVJ", entry_price=32, entry_order_id="oj", phase="entry_resting", is_v4=True,
        target_price=32, entry_mode="resting_maker", intended_join=True,
        entry_posted_ts=now, match_start_ts=now + 7200, regime_at_posting="r25_34",
        placement_minute=180)
np_ = mk("EV-N", "EVN", entry_price=40, entry_order_id="on", phase="entry_resting", is_v4=True,
         target_price=40, entry_mode="resting_maker", intended_join=False,
         entry_posted_ts=now, match_start_ts=now + 7200, regime_at_posting="r35_44",
         placement_minute=180)
s.positions = {"EV-J": jp, "EV-N": np_}
M.LiveV3._save_v4_resting(s)
raw = json.load(open(M.V4_RESTING_FILE))
LEGACY_KEYS = {"order_id", "event_ticker", "category", "direction", "posted_at",
               "posted_price", "target_price", "regime_at_posting",
               "placement_minute", "entry_mode", "match_start_ts"}
check(set(raw["EV-N"].keys()) == LEGACY_KEYS,
      "non-join leg: EXACT legacy key set (sparse key absent)")
check(raw["EV-J"].get("intended_join") is True, "join leg: intended_join persisted")
s2 = make_bot()
M.LiveV3._load_v4_resting(s2)
check(s2.positions["EV-J"].intended_join is True and s2.positions["EV-N"].intended_join is False,
      "restart: flag restored True/False correctly")

# ---- 6. placement-site key is the PRECISE one (source pin; cheap key rejected) ----
src = inspect.getsource(M.LiveV3)
# [C-FEEDER FIX-2] the key derives from the placement DECISION (captured
# snapshot + construction), never a post-await live-book re-read.
check("intended_join=self._intended_join_at_placement(" in src
      and 'return entry_mode == "resting_maker" and target_bid == placement_bid' in src,
      "source pin: flag computed at PLACEMENT from the decision-time snapshot")
# the exemption must read the flag, never recompute from the current book
seg = src.split("and pos.intended_join")[0].rsplit("if should_cancel", 1)[1]
check("best_bid" not in seg, "source pin: exemption keyed on pos.intended_join, not current book")

# ---- 7. move-repost re-keys the flag from the re-placement book ----
# [C-FEEDER FIX-2/3] re-key reads the decision-time snapshot (repost_bid,
# captured before the cancel/place awaits), not a post-await book re-read.
src_mr = inspect.getsource(M.LiveV3._v4_manage_resting_inner)
check("pos.intended_join = (new_target == repost_bid)" in src_mr
      and "repost_bid = book.best_bid" in src_mr,
      "source pin: move-repost re-keys intended_join at re-placement")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
