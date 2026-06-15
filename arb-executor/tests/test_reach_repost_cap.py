#!/usr/bin/env python3
"""[C-CAP-DIFF] reach-repost cap: a resting entry bid is never reposted ABOVE its
conception cell (the drift-supported ceiling = set-once _window_open[tk]["cell"]).
Holds and down-moves pass through; only an up-walk past the ceiling is clamped.
Covers BOTH repost flavors (Gate 4): the join_late_runway override (new_target =
current_price) AND the ordinary move_repost offset target (current_price - offset).
Both converge at new_target before _reprice_target, so one clamp gates both.

Each case drives the REAL _v4_manage_resting_inner to its move-repost path and
asserts the placed price + whether reach_repost_capped fired. Dormant (flag OFF)
proves byte-identical.

Run: cd arb-executor && python3 tests/test_reach_repost_cap.py
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
    try: return loop.run_until_complete(coro)
    finally: loop.close()

async def _fake_api_get(sess, ak, pk, path, rl):
    return None   # the old-order fill pre-check (5315) -> no fill -> proceed
M.api_get = _fake_api_get

# entry_table rows: (placement_min, offset, _, _); offset>=1 so _fix6_reference's
# join_late_runway arm is eligible. Join path ignores offset (new_target=current);
# the offset path (Test 2) uses it: new_target = current_price - offset.
ENTRY_TABLE = {
    ("WTA_CHALL", "r55_64"): (120, 5, 0, 0),
    ("WTA_CHALL", "r65_74"): (120, 5, 0, 0),
    ("WTA_CHALL", "r75_84"): (240, 12, 0, 0),
}

def make_bot(flag, runway):
    s = types.SimpleNamespace()
    s.reach_repost_cap_enforced = flag
    s._runway = runway
    s._window_open = {}
    s.entry_table = ENTRY_TABLE
    s.inflight_orders = set()
    s.entry_size = 5
    s.v4_fallback_sec = 1200
    s.operator_manual_mode = False
    s.premarket_bids_ride_live = False
    s.session = s.ak = s.pk = s.rl = None
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s.placed = []
    async def place_order(tk, action, side, price, count, post_only=True):
        s.placed.append({"tk": tk, "action": action, "price": price, "count": count})
        return "OID", {"order": {"status": "resting"}}
    s.place_order = place_order
    s._is_match_live = lambda et: False
    s._resting_cancel_reason = lambda t, b, a: (False, None)
    s._runway_status = lambda pm, tts, late_tag="late_window": s._runway
    async def _cancel_entry_and_resolve(tk, pos, label, source):
        return "cancelled"
    s._cancel_entry_and_resolve = _cancel_entry_and_resolve
    s._save_v4_resting = lambda: None
    s._untombstone_entry = lambda tk, pos: None
    s._manual_owns_leg = lambda tk: False
    for nm in ("_v4_manage_resting_inner", "regime_lookup", "_fix6_reference",
               "_reprice_target"):
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

class Book:
    def __init__(self, bid, ask):
        self.best_bid = bid; self.best_ask = ask; self.last_trade_price = 0; self.last_trade_ts = 0

def make_pos(tk):
    return M.Position(ticker=tk, event_ticker="EV", category="WTA_CHALL",
        direction="", cell_name="", cell_cfg={}, is_v4=True,
        entry_mode="resting_maker", entry_order_id="BID1", entry_price=90,
        target_price=90, regime_at_posting="r75_84",
        reference_source="join_late_runway",  # -> price_basis = target_price (90)
        play_type="v4_resting_maker")          # != engagement_join -> _fix6_reference runs

NOW = 10000.0
def drive(flag, runway, conception, bid, ask, set_window=True):
    """Run the real move path once; return (placed_price_or_None, capped_logged)."""
    s = make_bot(flag, runway)
    tk = "KXWTACHALLENGERMATCH-26JUN14STRKAZ-STR"
    pos = make_pos(tk)
    pos.match_start_ts = NOW + 3000     # tts=3000 > v4_fallback_sec -> skip T-20 fallback
    pos.last_cancel_repost_ts = NOW - 100  # > 60 -> cadence gate passes
    if set_window:
        s._window_open[tk] = {"price": conception, "cell": conception, "ts": NOW, "ttm_min": 50.0}
    run(s._v4_manage_resting_inner(tk, pos, Book(bid, ask), NOW))
    placed = s.placed[-1]["price"] if s.placed else None
    capped = any(e == "reach_repost_capped" for (e, d, t) in s.logs)
    return placed, capped

# ── 1. STRKAZ chase blocked (join_late_runway 78 -> 75) ──────────────────────
print("--- 1. join_late_runway chase-up clamped to conception ceiling ---")
placed, capped = drive(True, "sub_60", conception=75, bid=77, ask=79)  # mid 78
check(placed == 75, "join chase 78 clamped to ceiling 75 (placed=%s)" % placed)
check(capped, "reach_repost_capped logged")

# ── 2. Phantom-correction blocked (ordinary move_repost 58 -> 6) ─────────────
print("--- 2. phantom-low correction (offset path) clamped to phantom ceiling ---")
placed, capped = drive(True, "full", conception=6, bid=62, ask=64)  # mid 63, offset 5 -> 58
check(placed == 6, "offset target 58 clamped to ceiling 6 (placed=%s)" % placed)
check(capped, "reach_repost_capped logged")

# ── 3. Down-repost UNAFFECTED (the load-bearing negative) ────────────────────
print("--- 3. down-repost passes through, no clamp, no log ---")
placed, capped = drive(True, "sub_60", conception=75, bid=64, ask=66)  # mid 65 < 75
check(placed == 65, "down-move 65 passes through unclamped (placed=%s)" % placed)
check(not capped, "no reach_repost_capped log on a down-move")

# ── 4. Hold UNAFFECTED (proposed < ceiling) ─────────────────────────────────
print("--- 4. hold below ceiling passes through, no clamp, no log ---")
placed, capped = drive(True, "sub_60", conception=75, bid=71, ask=73)  # mid 72 < 75
check(placed == 72, "hold 72 (<= ceiling) unchanged (placed=%s)" % placed)
check(not capped, "no log when proposed <= ceiling")

# ── 5. Already at/below ceiling (== and <) ──────────────────────────────────
print("--- 5. at-ceiling (==) and below-ceiling (<) untouched ---")
placed, capped = drive(True, "sub_60", conception=75, bid=74, ask=76)  # mid 75 == ceiling
check(placed == 75 and not capped, "== ceiling: unchanged, no clamp (placed=%s)" % placed)
placed2, capped2 = drive(True, "sub_60", conception=75, bid=69, ask=71)  # mid 70 < ceiling
check(placed2 == 70 and not capped2, "< ceiling: unchanged, no clamp (placed=%s)" % placed2)

# ── 6. Dormant byte-identical (flag OFF) ────────────────────────────────────
print("--- 6. flag OFF: chase-up case passes through unclamped (ship-safety) ---")
placed, capped = drive(False, "sub_60", conception=75, bid=77, ask=79)  # would-be 78->75
check(placed == 78, "flag OFF: 78 NOT clamped -- byte-identical (placed=%s)" % placed)
check(not capped, "flag OFF: no reach_repost_capped log emitted")

# ── 7. Conception-cell absent (_window_open has no tk) ──────────────────────
print("--- 7. no conception frame: conservative no-op, no crash ---")
placed, capped = drive(True, "sub_60", conception=75, bid=77, ask=79, set_window=False)
check(placed == 78, "no _window_open[tk]: no clamp, passes at 78 (placed=%s)" % placed)
check(not capped, "no _window_open[tk]: no log, no crash")

print("\n%s  (%d failures)" % ("ALL PASS" if fails == 0 else "FAILURES", fails))
sys.exit(1 if fails else 0)
