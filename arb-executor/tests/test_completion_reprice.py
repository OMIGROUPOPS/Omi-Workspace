#!/usr/bin/env python3
"""PART-2 completion_reprice regression (flag-gated, default OFF).

Validates (spec item 8):
  (1) reprice clamp: s1 = min(s0+X, sib_ask-1, 99-leg1_basis); ask absent drops the
      ask term (replay parity); _reprice_target post_only always True.
  (2) cap headroom: leg1_basis + s1 <= 99 over a sweep (the T50 invariant).
  (3) never-cross: s1 <= sib_ask - 1 whenever an ask exists.
  (4) qty matching: completion order count = leg-1 FILLED qty (not entry_size).
  (5) buffer-exemption scoping: completion bids ONLY (all legacy modes keep T-15).
  (6) freshness re-evaluation: <10min no-op; >=10min re-place on ask move; ts-refresh
      when unchanged; cancel-and-revert when cap headroom gone; t0 cancel-only.
  (7) window_open_cell: set at/after T-240 by the tick path (last-trade discipline,
      NEVER mid, set-once, stale print rejected); pre-T-240-fill (unset frame) ->
      NO completion attempt; serialization round-trip (v2 shape + legacy back-compat).
  (8) flag-OFF byte-identical: T50 cancel preserved verbatim, completion arm
      unreachable, no window-open tracking, legacy state-file shape.

Run: cd arb-executor && python3 tests/test_completion_reprice.py
"""
import sys, types, json, time, asyncio, tempfile, os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m)
    fails += (0 if c else 1)

def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# ---- api_get stub (order-status poll inside the fill-race checks) ----
FAKE_OLD_FILLED = [0]
async def _fake_api_get(sess, ak, pk, path, rl):
    if "/portfolio/orders/" in path:
        return {"order": {"fill_count_fp": FAKE_OLD_FILLED[0]}}
    if "/portfolio/fills" in path:
        return {"fills": []}
    return {}
M.api_get = _fake_api_get


def book(bid, ask, last_trade=0, lt_age=5.0):
    return types.SimpleNamespace(
        best_bid=bid, best_ask=ask, bids={}, asks={},
        last_trade_price=last_trade,
        last_trade_ts=(time.time() - lt_age) if last_trade else 0.0)


def make_pos(tk, et="EV", cat="ATP_MAIN", **kw):
    return M.Position(ticker=tk, event_ticker=et, category=cat,
                      direction="", cell_name="", cell_cfg={}, **kw)


BOUND = ("_sibling_ticker", "_cancel_sibling_if_paired_over_cap",
         "_attempt_completion_reprice", "_completion_target",
         "_completion_buffer_exempt", "_reprice_target",
         "_maybe_set_window_open", "_v4_manage_completion",
         "_completion_revert", "_log_orphan_outcome", "_untombstone_entry",
         "_is_match_live", "_save_v4_resting", "_load_v4_resting",
         "_fill_is_taker", "_completion_tripwire", "_completion_fill_guards",
         # [C-P0-RACE] cancel sites resolve against exchange truth via these:
         "_cancel_entry_and_resolve", "_parse_entry_fill",
         "_book_v4_entry_fill", "_v4_apply_exit")

def make_bot(flag=True):
    s = types.SimpleNamespace()
    s.completion_reprice = flag
    s.completion_disabled = False   # [C-TRIPWIRE] armed state (handler dependency)
    s.completion_cells = {}
    s._window_open = {}
    s.positions = {}
    s.books = {}
    s.event_tickers = {}
    s.ticker_to_event = {}
    s.event_start_time = {}
    s.inflight_orders = set()
    s.entry_size = 10
    s.session = None; s.ak = None; s.pk = None; s.rl = None
    s.processed_events = set()
    s._save_processed = lambda: None
    s._trade_times = {}
    s._events_live = set()
    # [C-P0-RACE] booking-handler dependencies (raced fills book via _book_v4_entry_fill)
    s._booking_inflight = set()
    s.n_entries = 0
    s.cell_lookup = lambda cat, price: 0
    s.exit_rule_for = lambda cat, price: (10, "exit")
    s.exit_depth_floor = 0
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s.placed = []
    s.cancelled = []
    async def place_order(tk, action, side, price, count, post_only=True):
        s.placed.append({"tk": tk, "action": action, "price": price,
                         "count": count, "post_only": post_only})
        return "OID_NEW", {"order": {"status": "resting"}}
    s.place_order = place_order
    async def cancel_order(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        return True
    s.cancel_order = cancel_order
    for nm in BOUND:
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    s._save_v4_resting_real = s._save_v4_resting
    s._save_v4_resting = lambda: None   # stub by default; round-trip test uses real
    return s


def paired_setup(flag=True, leg1_qty=7, sib_bid=38, sib_ask=60,
                 wo1_cell=41, wo2_price=40, x=2, cells=None, sib_mode="resting_maker"):
    s = make_bot(flag)
    s.event_tickers = {"EV": {"L1", "SB"}}
    leg1 = make_pos("L1", entry_price=35, entry_qty=leg1_qty, phase="active",
                    entry_order_id="LEG1OID", is_v4=True)
    sib = make_pos("SB", entry_price=sib_bid, entry_qty=0, phase="entry_resting",
                   entry_order_id="SIBOID", is_v4=True, entry_mode=sib_mode,
                   target_price=sib_bid)
    s.positions = {"L1": leg1, "SB": sib}
    s.books = {"SB": book(sib_bid, sib_ask)}
    if wo1_cell is not None:
        s._window_open["L1"] = {"price": wo1_cell, "cell": wo1_cell, "ts": time.time()}
    if wo2_price is not None:
        s._window_open["SB"] = {"price": wo2_price, "cell": wo2_price, "ts": time.time()}
    s.completion_cells = cells if cells is not None else {("ATP_MAIN", wo1_cell): x}
    return s, leg1, sib


# =====================================================================
# (1)/(2)/(3) reprice clamp / cap headroom / never-cross (pure)
# =====================================================================
s = make_bot()
check(s._completion_target(40, 2, 60, 35) == 42, "clamp: min(42,59,64) -> s0+X wins (42)")
check(s._completion_target(40, 2, 42, 35) == 41, "never-cross: ask 42 -> s1=41 (ask-1 binds)")
check(s._completion_target(40, 2, 60, 58) == 41, "cap: basis 58 -> s1=41 (99-58 binds)")
check(s._completion_target(40, 2, None, 35) == 42, "no real ask -> ask term dropped (replay parity)")
ok_cap = ok_cross = True
for s0 in (5, 25, 40, 55, 90):
    for x in (1, 2, 3):
        for ask in (None, 3, 41, 42, 60, 99):
            for basis in (1, 20, 35, 58, 90, 98):
                s1 = s._completion_target(s0, x, ask, basis)
                if basis + s1 > 99:
                    ok_cap = False
                if ask is not None and s1 > ask - 1:
                    ok_cross = False
check(ok_cap, "cap invariant sweep: leg1_basis + s1 <= 99 for ALL combos")
check(ok_cross, "never-cross sweep: s1 <= sib_ask-1 whenever an ask exists")
p, po = s._reprice_target(42, 60)
check(p == 42 and po is True, "_reprice_target: sub-ask target unchanged, post_only=True")
p, po = s._reprice_target(60, 60)
check(p == 59 and po is True, "_reprice_target: marketable target clamped to ask-1, post_only=True")

# =====================================================================
# (4) full attempt: reprice fires, qty = leg-1 FILLED qty
# =====================================================================
s, leg1, sib = paired_setup(leg1_qty=7)
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
check(len(s.cancelled) == 1 and s.cancelled[0]["oid"] == "SIBOID"
      and s.cancelled[0]["label"] == "completion_reprice",
      "attempt: sibling's original bid cancelled (completion_reprice label)")
check(len(s.placed) == 1 and s.placed[0]["tk"] == "SB" and s.placed[0]["price"] == 42
      and s.placed[0]["count"] == 7 and s.placed[0]["post_only"] is True,
      "attempt: completion bid at s1=42, qty=7 (leg-1 FILLED qty, not entry_size=10), post_only")
check(sib.entry_mode == "completion_reprice" and sib.entry_price == 42
      and sib.entry_order_id == "OID_NEW" and sib.completion_s0 == 40
      and sib.completion_x == 2 and sib.completion_leg1_basis == 35
      and sib.completion_qty == 7 and sib.completion_prev_price == 38
      and sib.completion_prev_mode == "resting_maker" and sib.completion_lookup_cell == 41,
      "attempt: sibling Position bookkeeping (mode/s0/X/basis/qty/prev/lookup_cell)")
att = [l for l in s.logs if l[0] == "completion_attempt"]
check(len(att) == 1 and att[0][1]["s0"] == 40 and att[0][1]["s1"] == 42
      and att[0][1]["x"] == 2 and att[0][1]["cap_headroom"] == 64
      and att[0][1]["trigger_fill_id"] == "LEG1OID"
      and att[0][1]["cell_at_completion_lookup"] == 41,
      "attempt: completion_attempt log carries s0/s1/X/cap_headroom/trigger_fill_id/cell")

# partial leg-1 fill -> completion qty follows the FILLED amount
s, leg1, sib = paired_setup(leg1_qty=3)
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
check(s.placed[0]["count"] == 3, "attempt: partial leg-1 fill (3) -> completion qty 3")

# idempotence: a second leg-1 fill does NOT double-reprice
s.placed.clear(); s.cancelled.clear()
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
check(not s.placed and not s.cancelled,
      "attempt: already completion_reprice -> idempotent no-op on later leg-1 fills")

# fill-race: sibling's original order already filled -> abort (no cancel)
s, leg1, sib = paired_setup()
FAKE_OLD_FILLED[0] = 5
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
check(not s.cancelled and not s.placed and sib.entry_mode == "resting_maker",
      "attempt: sibling filled in-flight -> abort, pair completed naturally")
FAKE_OLD_FILLED[0] = 0

# =====================================================================
# T50 arm unchanged + mutual exclusion by cap arithmetic
# =====================================================================
s, leg1, sib = paired_setup()
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 62))   # 62+38=100 > 99
check(len(s.cancelled) == 1 and s.cancelled[0]["label"] == "paired_basis_cancel"
      and not s.placed and "SB" not in s.positions,
      "T50: over-cap (62+38=100) -> cancel arm fires, NO completion (mutually exclusive)")
pb = [l for l in s.logs if l[0] == "paired_basis_cancel"]
check(len(pb) == 1 and pb[0][1]["combined"] == 100, "T50: paired_basis_cancel log unchanged")

s, leg1, sib = paired_setup()
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 61))   # 61+38=99 == cap -> completion arm
# at basis 61: s1 = min(40+2, 60-1, 99-61=38) = 38 <= s0=40 -> no_headroom no-op
noat = [l for l in s.logs if l[0] == "completion_no_attempt"]
check(len(s.placed) == 0 and len(noat) == 1 and noat[0][1]["reason"] == "no_headroom",
      "boundary: at-cap basis 61 -> s1 clamps to 38 <= s0 -> no-op (cap term protects)")

# genuine already_at_s1: sibling already resting exactly at s1 > s0
s, leg1, sib = paired_setup(sib_bid=43, wo2_price=40, x=3)  # s1 = min(43,59,64) = 43 == bid
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
noat = [l for l in s.logs if l[0] == "completion_no_attempt"]
check(not s.placed and not s.cancelled and len(noat) == 1
      and noat[0][1]["reason"] == "already_at_s1",
      "boundary: bid already resting AT s1 -> inert skip (queue priority kept)")

# =====================================================================
# (5)+(7) no-attempt edges: window-open frames + eligibility
# =====================================================================
s, leg1, sib = paired_setup(wo1_cell=None)
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
noat = [l for l in s.logs if l[0] == "completion_no_attempt"]
check(not s.placed and not s.cancelled and len(noat) == 1
      and noat[0][1]["reason"] == "leg1_window_open_unset",
      "edge: leg-1 window_open UNSET (pre-T-240 fill) -> NO attempt (conservative edge)")

s, leg1, sib = paired_setup(wo2_price=None)
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
noat = [l for l in s.logs if l[0] == "completion_no_attempt"]
check(not s.placed and len(noat) == 1 and noat[0][1]["reason"] == "sibling_window_open_unset",
      "edge: sibling window_open unset (no s0) -> NO attempt")

s, leg1, sib = paired_setup(cells={("ATP_MAIN", 99): 1})   # cell 41 absent
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
noat = [l for l in s.logs if l[0] == "completion_no_attempt"]
check(not s.placed and len(noat) == 1 and noat[0][1]["reason"] == "cell_not_eligible",
      "edge: absent (category,cell) in completion_cells -> never attempt")

s, leg1, sib = paired_setup(x=1, sib_ask=41)   # s1 = min(41, 40, 64) = 40 <= s0
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
noat = [l for l in s.logs if l[0] == "completion_no_attempt"]
check(not s.placed and len(noat) == 1 and noat[0][1]["reason"] == "no_headroom",
      "edge: s1 <= s0 (ask collapse) -> no-op per spec")

# sibling not entry_resting -> handler precondition stops everything
s, leg1, sib = paired_setup()
sib.phase = "active"; sib.entry_qty = 5
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
check(not s.placed and not s.cancelled and not s.logs,
      "edge: sibling already filled/active -> handler no-op (pair locked)")

# =====================================================================
# (5) buffer-exemption scoping: completion bids ONLY
# =====================================================================
s = make_bot()
for mode in ("", "resting_maker", "miss_fallback", "fallback_maker",
             "marketable_clamp", "marketable_taker"):
    p = make_pos("T", entry_mode=mode)
    if s._completion_buffer_exempt(p):
        check(False, "buffer exemption leaked to entry_mode=%r" % mode)
        break
else:
    check(True, "buffer exemption: ALL legacy entry modes keep the T-15 cancel")
p = make_pos("T", entry_mode="completion_reprice")
check(s._completion_buffer_exempt(p) is True,
      "buffer exemption: completion_reprice bid IS exempt (rides to T-0)")

# =====================================================================
# (7) window_open: tick-loop discipline
# =====================================================================
now = time.time()
def wo_bot(tts_min, lt=44, lt_age=5.0, flag=True, bid=10, ask=90):
    s = make_bot(flag)
    s.ticker_to_event = {"TK": "EV"}
    s.event_tickers = {"EV": {"TK"}}
    s.event_start_time = {"EV": now + tts_min * 60}
    s.books = {"TK": book(bid, ask, last_trade=lt, lt_age=lt_age)}
    return s

s = wo_bot(300)   # T-300 > T-240
s._maybe_set_window_open("TK", now)
check("TK" not in s._window_open, "window_open: NOT set before T-240 (tts=300min)")

s = wo_bot(230)
s._maybe_set_window_open("TK", now)
check(s._window_open.get("TK", {}).get("price") == 44
      and s._window_open["TK"]["cell"] == 44,
      "window_open: set at T-230 from the fresh last-traded print (44)")
wos = [l for l in s.logs if l[0] == "window_open_set"]
check(len(wos) == 1, "window_open: window_open_set telemetry emitted")

# NEVER mid: book mid is 50 (10/90), print is 44 -> 44, not 50
check(s._window_open["TK"]["price"] != 50, "window_open: last-trade discipline, NEVER the BBO mid")

# set-once: a later print does not overwrite
s.books["TK"].last_trade_price = 70
s.books["TK"].last_trade_ts = time.time()
s._maybe_set_window_open("TK", now + 60)
check(s._window_open["TK"]["price"] == 44, "window_open: set-once (later print ignored)")

s = wo_bot(230, lt_age=2000)
s._maybe_set_window_open("TK", now)
check("TK" not in s._window_open, "window_open: stale print (>1800s) rejected -> stays unset")

s = wo_bot(230, lt=0)
s._maybe_set_window_open("TK", now)
check("TK" not in s._window_open, "window_open: no print ever -> stays unset (no mid fallback)")

s = wo_bot(-5)
s._maybe_set_window_open("TK", now)
check("TK" not in s._window_open, "window_open: match started (tts<=0) -> not set")

s = wo_bot(230, lt=2)
s._maybe_set_window_open("TK", now)
check(s._window_open["TK"]["price"] == 2 and s._window_open["TK"]["cell"] == 5,
      "window_open: cell clamped to [5,94] while raw price kept for s0")

s = wo_bot(230, flag=False)
s._maybe_set_window_open("TK", now)
check("TK" not in s._window_open and not s.logs,
      "flag OFF: window_open tracking fully inert (no state, no logs)")

# =====================================================================
# (6) freshness re-evaluation (_v4_manage_completion)
# =====================================================================
def comp_setup(reprice_age=700, sib_ask=60, start_in_min=120, leg1_qty=7):
    s = make_bot(True)
    s.event_tickers = {"EV": {"L1", "SB"}}
    leg1 = make_pos("L1", entry_price=35, entry_qty=leg1_qty, phase="active",
                    entry_order_id="LEG1OID", is_v4=True)
    sib = make_pos("SB", entry_price=42, entry_qty=0, phase="entry_resting",
                   entry_order_id="COMPOID", is_v4=True,
                   entry_mode="completion_reprice", play_type="v4_completion_reprice",
                   target_price=42, completion_s0=40, completion_x=2,
                   completion_leg1_basis=35, completion_qty=7,
                   completion_reprice_ts=time.time() - reprice_age,
                   completion_prev_price=38, completion_prev_mode="resting_maker",
                   completion_prev_target=38, completion_lookup_cell=41,
                   match_start_ts=time.time() + start_in_min * 60)
    s.completion_cells = {("ATP_MAIN", 41): 2}   # lookup cell in-table (V4 clean)
    s.positions = {"L1": leg1, "SB": sib}
    s.books = {"SB": book(38, sib_ask), "L1": book(30, 40)}
    s.event_start_time = {"EV": sib.match_start_ts}
    return s, leg1, sib

s, leg1, sib = comp_setup(reprice_age=300)
run(s._v4_manage_completion("SB", sib, s.books["SB"], time.time()))
check(not s.cancelled and not s.placed, "freshness: <10min resting -> no re-evaluation")

s, leg1, sib = comp_setup(reprice_age=700, sib_ask=60)
run(s._v4_manage_completion("SB", sib, s.books["SB"], time.time()))
fr = [l for l in s.logs if l[0] == "completion_freshness"]
check(not s.cancelled and len(fr) == 1 and fr[0][1]["unchanged"] is True
      and abs(sib.completion_reprice_ts - time.time()) < 5,
      "freshness: >=10min, s1 unchanged -> ts refreshed only (no churn)")

s, leg1, sib = comp_setup(reprice_age=700, sib_ask=43)   # s1 -> min(42, 42, 64) = 42 == current... use 41
s.books["SB"].best_ask = 42                               # s1 = min(42, 41, 64) = 41 != 42
run(s._v4_manage_completion("SB", sib, s.books["SB"], time.time()))
check(len(s.cancelled) == 1 and s.cancelled[0]["label"] == "completion_freshness_reprice"
      and len(s.placed) == 1 and s.placed[0]["price"] == 41 and s.placed[0]["count"] == 7
      and s.placed[0]["post_only"] is True and sib.entry_price == 41,
      "freshness: ask moved -> cancel + re-place at re-evaluated s1=41 (maker)")

s, leg1, sib = comp_setup(reprice_age=700, leg1_qty=7)
leg1.entry_qty = 9                                        # later partial leg-1 fills
run(s._v4_manage_completion("SB", sib, s.books["SB"], time.time()))
check(len(s.placed) == 1 and s.placed[0]["count"] == 9 and sib.completion_qty == 9,
      "freshness: leg-1 filled more (7->9) -> completion qty refreshed to FILLED qty")

s, leg1, sib = comp_setup(reprice_age=700, sib_ask=40)    # s1 = min(42, 39, 64) = 39 <= s0=40
run(s._v4_manage_completion("SB", sib, s.books["SB"], time.time()))
rv = [l for l in s.logs if l[0] == "completion_reverted"]
orp = [l for l in s.logs if l[0] == "orphan_outcome"]
check(len(s.cancelled) == 1 and s.cancelled[0]["label"] == "completion_revert_cap_headroom_gone"
      and len(rv) == 1 and rv[0][1]["reason"] == "cap_headroom_gone" and len(orp) == 1,
      "freshness: cap headroom gone -> cancel-and-revert + orphan_outcome snapshot")
check(len(s.placed) == 1 and s.placed[0]["price"] == 38 and s.placed[0]["count"] == 10
      and sib.entry_mode == "resting_maker" and sib.completion_s0 == 0,
      "revert: pre-completion bid re-placed (38 x entry_size), mode restored, fields cleared")

s, leg1, sib = comp_setup(reprice_age=700, start_in_min=-1)   # past T-0
run(s._v4_manage_completion("SB", sib, s.books["SB"], time.time()))
rv = [l for l in s.logs if l[0] == "completion_reverted"]
check(len(rv) == 1 and rv[0][1]["reason"] == "t0_reached" and not s.placed
      and "SB" not in s.positions,
      "T-0 reached: cancel-only (no re-place into live play), leg freed")

s, leg1, sib = comp_setup(reprice_age=700, start_in_min=10)   # inside T-15 buffer
s.books["SB"].best_ask = 40                                   # force cap_headroom_gone
run(s._v4_manage_completion("SB", sib, s.books["SB"], time.time()))
check(not s.placed and "SB" not in s.positions,
      "revert inside T-15 buffer: cancel-only (re-place would be instantly buffer-cancelled)")

s, leg1, sib = comp_setup(reprice_age=60)
s.completion_reprice = False
run(s._v4_manage_completion("SB", sib, s.books["SB"], time.time()))
rv = [l for l in s.logs if l[0] == "completion_reverted"]
check(len(rv) == 1 and rv[0][1]["reason"] == "flag_off" and sib.entry_mode == "resting_maker",
      "flag walked off mid-flight: completion bid reverted to normal entry handling")

s, leg1, sib = comp_setup(reprice_age=700)
FAKE_OLD_FILLED[0] = 7                                        # completion order just filled
run(s._v4_manage_completion("SB", sib, s.books["SB"], time.time()))
check(not s.cancelled and not s.placed,
      "freshness fill-race: completion order filled -> never cancelled (check_fills books it)")
FAKE_OLD_FILLED[0] = 0

# =====================================================================
# (7) serialization round-trip (v2 shape) + legacy back-compat
# =====================================================================
tmpdir = tempfile.mkdtemp()
orig_file = M.V4_RESTING_FILE
M.V4_RESTING_FILE = Path(tmpdir) / "resting.json"

s, leg1, sib = comp_setup(reprice_age=100)
s._window_open = {"L1": {"price": 41, "cell": 41, "ts": time.time(), "ttm_min": 200.0},
                  "SB": {"price": 40, "cell": 40, "ts": time.time(), "ttm_min": 199.0}}
s._save_v4_resting_real()
raw = json.loads(open(M.V4_RESTING_FILE).read())
check(raw.get("_shape") == "v2" and "SB" in raw["legs"] and "L1" in raw["window_open"],
      "save (flag ON): v2 shape with legs + window_open frames")
check(raw["legs"]["SB"]["entry_mode"] == "completion_reprice"
      and raw["legs"]["SB"]["completion_s0"] == 40
      and raw["legs"]["SB"]["completion_qty"] == 7
      and raw["legs"]["SB"]["completion_prev_price"] == 38,
      "save: completion fields serialized on the completion leg")

s2 = make_bot(True)
s2._load_v4_resting()
rp = s2.positions.get("SB")
check(rp is not None and rp.entry_mode == "completion_reprice" and rp.completion_s0 == 40
      and rp.completion_x == 2 and rp.completion_leg1_basis == 35 and rp.completion_qty == 7
      and rp.completion_prev_price == 38 and rp.completion_prev_mode == "resting_maker",
      "restore: completion Position rebuilt with all completion fields (lifecycle d)")
check(s2._window_open.get("L1", {}).get("cell") == 41
      and s2._window_open.get("SB", {}).get("price") == 40,
      "restore: window_open frames rebuilt (lifecycle d)")

# legacy bare-legs file still loads (back-compat)
with open(M.V4_RESTING_FILE, "w") as f:
    json.dump({"TKX": {"order_id": "O1", "event_ticker": "EVX", "category": "ATP_MAIN",
                       "direction": "", "posted_at": 1.0, "posted_price": 30,
                       "target_price": 30, "regime_at_posting": "r25_34",
                       "placement_minute": 120, "entry_mode": "resting_maker",
                       "match_start_ts": 0.0}}, f)
s3 = make_bot(True)
s3._load_v4_resting()
check("TKX" in s3.positions and s3.positions["TKX"].entry_price == 30
      and s3.positions["TKX"].completion_s0 == 0,
      "restore: legacy bare-legs state file loads unchanged (back-compat)")

# =====================================================================
# (8) flag-OFF byte-identical regression (the load-bearing one)
# =====================================================================
# completion arm unreachable; T50 cancel preserved verbatim
s, leg1, sib = paired_setup(flag=False)
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
check(not s.cancelled and not s.placed and not s.logs
      and sib.entry_mode == "resting_maker" and sib.entry_price == 38,
      "flag OFF: under-cap fill -> handler is a pure no-op (no completion, no logs)")

s, leg1, sib = paired_setup(flag=False)
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 62))
check(len(s.cancelled) == 1 and s.cancelled[0]["label"] == "paired_basis_cancel"
      and "SB" not in s.positions and "EV" not in s.processed_events,
      "flag OFF: over-cap -> T50 cancel byte-identical (cancel + untombstone)")

# state file: legacy shape, byte-identical key set
s, leg1, sib = paired_setup(flag=False)
s._save_v4_resting_real()
raw = json.loads(open(M.V4_RESTING_FILE).read())
LEGACY_KEYS = {"order_id", "event_ticker", "category", "direction", "posted_at",
               "posted_price", "target_price", "regime_at_posting",
               "placement_minute", "entry_mode", "match_start_ts"}
check("_shape" not in raw and set(raw.keys()) == {"SB"}
      and set(raw["SB"].keys()) == LEGACY_KEYS,
      "flag OFF: state file keeps the legacy bare-legs shape, exact legacy key set")

M.V4_RESTING_FILE = orig_file

# buffer condition: flag OFF -> no v4 entry mode is exempt (T-15 unchanged)
s = make_bot(False)
for mode in ("resting_maker", "miss_fallback", "fallback_maker", "marketable_clamp"):
    if s._completion_buffer_exempt(make_pos("T", entry_mode=mode)):
        check(False, "flag OFF: buffer exemption leaked to %r" % mode)
        break
else:
    check(True, "flag OFF: T-15 match_start_buffer applies to every entry bid (unchanged)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
