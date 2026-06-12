#!/usr/bin/env python3
"""[C-CAP-REMOVAL] paired-basis cap flag-gated dormant (paired_cap_enforced).

Operator-ruled 2026-06-12: the foundation's own economics (combined T-20
taker ~101.9, positive per-cell expectancy) sit ABOVE the 99 cap -- the cap
forbade the strategy's structural cost by construction (zero maker pairs ever
completed). Three guards disarmed when the flag is False: (1) entry-placement
gate, (2) T-20 paired_basis_no_fallback, (3) T50 cancel-sibling-on-fill.
E1/V3 re-key to the per-leg sanity bound; _completion_target's cap term
becomes the per-leg 99 (attempt AND manage/cap_headroom_gone flow through
it). Per-leg sanity, exit cap, T-15 buffer, freshness, degenerate-book
untouched. Flag True (code default) = legacy behavior byte-identical.
Run: cd arb-executor && python3 tests/test_cap_removal.py
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
    return {"orders": []}
M.api_get = fake_api_get

def book(bid, ask):
    return types.SimpleNamespace(best_bid=bid, best_ask=ask, bids={}, asks={},
        updated=time.time(), last_trade_price=0, last_trade_ts=0.0)

def mk(tk, et, **kw):
    p = M.Position(ticker=tk, event_ticker=et, category="ATP_MAIN",
                   direction="", cell_name="", cell_cfg={})
    for k, v in kw.items(): setattr(p, k, v)
    return p

def make_bot(enforced):
    s = types.SimpleNamespace()
    s.paired_cap_enforced = enforced
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
    s.completion_cells = {}
    s.engagement_cells = set(); s.engagement_band_gating = False
    s.entry_table = {("ATP_MAIN", "r45_54"): (180, 1, 0, 0)}
    s.regime_lookup = lambda cat, price: "r45_54"
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
    for nm in ("_paired_basis_ok", "_sibling_ticker", "_sibling_engageable",
               "_cancel_sibling_if_paired_over_cap", "_attempt_completion_reprice",
               "_completion_target", "_completion_buffer_exempt",
               "_cancel_entry_and_resolve", "_parse_entry_fill", "_untombstone_entry",
               "_reprice_target", "_taker_spread_ok", "_fallback_order",
               "_resting_cancel_reason", "_is_match_live",
               "_v4_manage_resting", "_v4_manage_resting_inner",
               "_engagement_place_guards", "_engagement_bucket",
               "_completion_fill_guards", "_completion_tripwire",
               "_mechanism_tripwire", "_runway_status", "_fix6_reference"):
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

ET = "KXWTACHALLENGERMATCH-26JUN12SALKAW"; SAL, KAW = ET + "-SAL", ET + "-KAW"

# ---- 1. KAWA-SALKOVA FRAME: both legs REST through the T-20 evaluation ----
# last night: SAL killed paired_basis_no_fallback at combined 100 vs cap 99.
def salkaw_bot(enforced):
    s = make_bot(enforced)
    s.event_tickers = {ET: {SAL, KAW}}
    now = time.time()
    s.positions[KAW] = mk(KAW, ET, entry_price=48, target_price=48, entry_order_id="OK",
                          entry_mode="resting_maker", is_v4=True, phase="entry_resting",
                          match_start_ts=now + 1100, intended_join=True)
    s.positions[SAL] = mk(SAL, ET, entry_price=52, target_price=52, entry_order_id="OS",
                          entry_mode="resting_maker", is_v4=True, phase="entry_resting",
                          match_start_ts=now + 1100, intended_join=True)
    return s, now

s, now = salkaw_bot(enforced=False)
run(s._v4_manage_resting(SAL, s.positions[SAL], book(52, 53), now))
labels = [c["label"] for c in s.cancelled]
check("paired_basis_no_fallback" not in labels,
      "SALKAW frame, cap OFF: nothing killed at 100-vs-99")
check(s.positions[SAL].entry_order_id and s.positions[SAL].entry_mode == "fallback_maker",
      "SAL re-rests via the normal T-20 fallback_maker clamp (lives through T-20)")
check(s.positions[KAW].entry_order_id == "OK", "KAW untouched (both legs resting)")

s, now = salkaw_bot(enforced=True)
run(s._v4_manage_resting(SAL, s.positions[SAL], book(52, 53), now))
labels = [c["label"] for c in s.cancelled]
check("paired_basis_no_fallback" in labels,
      "flag ON restores the T-20 paired cancel (guard 2 byte-identical)")

# ---- 2. TIAFOE-LEHECKA FRAME: placeable at basis >= 100 ----
ET2 = "KXATPMATCH-26JUN12LEHTIA"; LEH, TIA = ET2 + "-LEH", ET2 + "-TIA"
s = make_bot(enforced=False)
s.event_tickers = {ET2: {LEH, TIA}}
s.positions[TIA] = mk(TIA, ET2, entry_price=46)   # sibling committed at 46
gate = lambda bot, price: (getattr(bot, "paired_cap_enforced", True)
                           and not bot._paired_basis_ok(LEH, ET2, price))
check(gate(s, 55) is False, "LEHTIA frame, cap OFF: 55+46=101 placeable (gate 1 inert)")
s.paired_cap_enforced = True
check(gate(s, 55) is True, "flag ON restores the placement gate (guard 1 byte-identical)")
check(gate(s, 53) is False, "flag ON: 53+46=99 <= cap still placeable (sanity)")
src = inspect.getsource(M.LiveV3._route_event)
check("[C-CAP-REMOVAL site 1]" in src and 'getattr(self, "paired_cap_enforced", True)' in src,
      "placement call-site uses the flag-gated form (source-pinned)")

# ---- 3. leg-1 fill does NOT cancel the resting sibling (T50 off) ----
ET3 = "KXATPMATCH-26JUN12KESMAR"; KES, MAR = ET3 + "-KES", ET3 + "-MAR"
def kesmar_bot(enforced, completion=False):
    s = make_bot(enforced)
    s.completion_reprice = completion
    s.event_tickers = {ET3: {KES, MAR}}
    s.positions[KES] = mk(KES, ET3, entry_price=75, entry_qty=5, is_v4=True,
                          phase="active", entry_order_id="OK1")
    s.positions[MAR] = mk(MAR, ET3, entry_price=37, target_price=37, entry_order_id="OM",
                          entry_mode="resting_maker", is_v4=True, phase="entry_resting")
    return s

s = kesmar_bot(enforced=False)
run(s._cancel_sibling_if_paired_over_cap(KES, ET3, 75))
check(not s.cancelled and s.positions[MAR].entry_order_id == "OM",
      "cap OFF: leg-1 fill at 75 does NOT cancel the resting 37 sibling (KESMAR rides)")
s = kesmar_bot(enforced=True)
run(s._cancel_sibling_if_paired_over_cap(KES, ET3, 75))
check(any(c["label"] == "paired_basis_cancel" for c in s.cancelled),
      "flag ON restores the T50 sibling cancel (guard 3 byte-identical)")

# ---- 4. completion reprice fires sane BOTH flag states ----
def completion_bot(enforced, basis):
    s = kesmar_bot(enforced, completion=True)
    s.positions[KES].entry_price = basis
    s.completion_cells = {("ATP_MAIN", 70): 10}
    s._window_open = {KES: {"price": 70, "cell": 70},
                      MAR: {"price": 30, "cell": 30}}
    s.books[MAR] = book(35, 60)
    return s

# cap OFF, over-cap pair: completion arm reached, s1 per-leg-bounded only
s = completion_bot(enforced=False, basis=75)
run(s._cancel_sibling_if_paired_over_cap(KES, ET3, 75))
att = [d for ev, d, _ in s.logs if ev == "completion_attempt"]
check(len(att) == 1 and att[0]["s1"] == 40,
      "cap OFF: over-cap pair reaches completion; s1 = min(s0+X=40, 99, ask-1=59) = 40")
check(att[0]["s1"] > 99 - 75,
      "s1 exceeds the old cap headroom (24) -> cap term gone, cell-valid level governs")
check(s.positions[MAR].entry_mode == "completion_reprice"
      and s.positions[MAR].entry_price == 40,
      "sibling repriced to the cell-valid level, combined 115 allowed (per-leg only)")
# cap ON, same over-cap pair: T50 cancel wins, no completion
s = completion_bot(enforced=True, basis=75)
run(s._cancel_sibling_if_paired_over_cap(KES, ET3, 75))
check(any(c["label"] == "paired_basis_cancel" for c in s.cancelled)
      and not [d for ev, d, _ in s.logs if ev == "completion_attempt"],
      "cap ON: over-cap pair cancelled, completion never attempted (legacy order)")
# cap ON, under-cap pair: legacy cap-bounded completion (byte-identical bound)
s = completion_bot(enforced=True, basis=60)
run(s._cancel_sibling_if_paired_over_cap(KES, ET3, 60))
att = [d for ev, d, _ in s.logs if ev == "completion_attempt"]
check(len(att) == 1 and att[0]["s1"] == 39,
      "cap ON: s1 = min(40, 99-60=39, 59) = 39 -- cap term byte-identical")
# pure bound both states
s = make_bot(enforced=True)
check(s._completion_target(30, 10, 60, 75) == 24, "pure: cap ON -> 99-75=24 bounds s1")
s.paired_cap_enforced = False
check(s._completion_target(30, 10, 60, 75) == 40, "pure: cap OFF -> per-leg 99 bound, s1=40")
check(s._completion_target(95, 10, None, 10) == 99, "pure: cap OFF -> s1 never exceeds per-leg 99")

# ---- 5. E1 / V3 re-key to the per-leg sanity check ----
s = make_bot(enforced=False)
s.event_tickers = {ET2: {LEH, TIA}}
s.positions[TIA] = mk(TIA, ET2, entry_price=46)
def epos(price):
    return mk(LEH, ET2, entry_price=price, target_price=price,
              entry_mode="resting_maker", play_type="v4_engagement_join",
              intended_join=True)
check(s._engagement_place_guards(LEH, ET2, "ATP_MAIN", epos(55), 120 * 60) is None,
      "E1 cap OFF: combined 101 placement -> NO violation (by design)")
v = s._engagement_place_guards(LEH, ET2, "ATP_MAIN", epos(100), 120 * 60)
check(v is not None and v[0] == "E1_per_leg_sanity_breach",
      "E1 cap OFF: per-leg sanity breach (price 100) FIRES")
s.paired_cap_enforced = True
v = s._engagement_place_guards(LEH, ET2, "ATP_MAIN", epos(55), 120 * 60)
check(v is not None and v[0] == "E1_paired_cap_bypass",
      "E1 cap ON: pair arithmetic restored (combined 101 fires)")
# V3
s = make_bot(enforced=False)
s.completion_cells = {("ATP_MAIN", 70): 10}   # keep V4 (cell-in-table) quiet
cpos = mk(MAR, ET3, completion_leg1_basis=75, completion_lookup_cell=70)
check(s._completion_fill_guards(cpos, 37, False) is None,
      "V3 cap OFF: 75+37=112 completion fill -> NO violation (by design)")
v = s._completion_fill_guards(cpos, 100, False)
check(v is not None and v[0] == "V3_per_leg_sanity_breach",
      "V3 cap OFF: per-leg sanity breach (fill 100) FIRES")
s.paired_cap_enforced = True
v = s._completion_fill_guards(cpos, 37, False)
check(v is not None and v[0] == "V3_cap_breach",
      "V3 cap ON: cap arithmetic restored (112 fires)")

# ---- 6. config default + kept guards (source pins) ----
src_init = inspect.getsource(M.LiveV3.__init__)
check('config.get("paired_cap_enforced", True)' in src_init,
      "code default True (legacy); deploy config flips to False")
src_route = inspect.getsource(M.LiveV3._route_event)
check("if entry_price <= 0 or entry_price >= 100:" in src_route,
      "per-leg sanity <=99 untouched")
src_mr = inspect.getsource(M.LiveV3._v4_manage_resting_inner)
check("[C-CAP-REMOVAL site 2]" in src_mr, "T-20 site flag-gated (source-pinned)")
src_cs = inspect.getsource(M.LiveV3._cancel_sibling_if_paired_over_cap)
check("[C-CAP-REMOVAL site 3]" in src_cs, "T50 sibling-cancel flag-gated (source-pinned)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
