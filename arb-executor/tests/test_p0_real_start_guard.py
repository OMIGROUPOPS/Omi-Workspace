"""[P0 REAL-START ENTRY GUARD] regression for the MICMAY post-start-fill P0.

Real chronology (KXATPCHALLENGERMATCH-26JUL21MICMAY):
  ~19:00 ET   match actually starts (Michelsen wins set 1 6-3, set 2 underway)
  19:36:18.7  Mayo entry order CREATED (false 22:00 schedule -> engine in W1)
  19:36:21.5  Michelsen sibling order created
  19:36:21.7  Mayo FILLS (maker) -- ~36 min POST real start
  ~19:39:34   the tape/live signal first arrives (LATER than the fill)
  22:00       false schedule start (= expected_expiration_time, the match END)

The defect fired BEFORE any live signal, so the fix is: (1) a false end-as-start
never becomes a start; (2) proof-grade live sources override a future schedule;
(3) EVERY entry buy (maker+taker+completion) is refused unless CONFIRMED pre-
start; (4) already-resting entries are swept when the match is live/unknown/
past/conflicting -- at the manage pass, the gun, and at boot.

Requirement L: these tests drive PRODUCTION placement / order-status / receipt /
cancellation paths (real _place_order_unlocked, _cancel_entry_and_resolve,
cancel_order->api_delete, get-order poll, _book_v4_entry_fill) -- no cancellation
is faked with a lambda returning "cancelled".
"""
import os, sys, types, asyncio, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import live_v4 as M

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m)
    if not c:
        fails += 1

def run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)

EV = "KXATPCHALLENGERMATCH-26JUL21MICMAY"
MAY = EV + "-MAY"
MIC = EV + "-MIC"
FUT = time.time() + 8400.0   # false schedule ~140 min in the FUTURE (MICMAY 22:00)
PAST = time.time() - 3600.0

# ---- production API doubles (get-order poll / placement / DELETE cancel) ----
ORDERS = {}      # oid -> order object (get-order poll shape)
DELETED = []     # oids passed to api_delete (real cancel path)
POSTED = []      # (oid, payload) placements

async def _api_get(sess, ak, pk, path, rl):
    if "/portfolio/orders/" in path and "?" not in path:
        o = ORDERS.get(path.rsplit("/", 1)[-1])
        return {"order": o} if o is not None else None
    if "/portfolio/fills" in path:
        return {"fills": []}
    if "/portfolio/orders" in path:
        return {"orders": []}
    if "/portfolio/positions" in path:
        return {"market_positions": []}
    if "/markets/" in path:
        return {"market": {"status": "active"}}
    return {}

async def _api_post(sess, ak, pk, path, payload, rl):
    oid = "NEW-%d" % (len(POSTED) + 1)
    POSTED.append((oid, payload))
    ORDERS[oid] = {"order_id": oid, "status": "resting", "fill_count_fp": 0}
    return {"order": {"order_id": oid, "status": "resting"}}

async def _api_delete(sess, ak, pk, path, rl):
    oid = path.rsplit("/", 1)[-1]
    DELETED.append(oid)
    o = ORDERS.get(oid)
    if o is not None and str(o.get("status")) not in ("executed", "filled"):
        o["status"] = "canceled"          # exchange confirms the cancel
    return True

M.api_get, M.api_post, M.api_delete = _api_get, _api_post, _api_delete

def reset():
    ORDERS.clear(); DELETED[:] = []; POSTED[:] = []

REAL = ("_entry_start_gate", "_strong_live_evidence", "_gun_stamp",
        "_place_order_unlocked", "place_order", "_cancel_entry_and_resolve",
        "_start_gate_cancel_resting", "cancel_order", "_untombstone_entry",
        "_parse_entry_fill", "_book_v4_entry_fill", "_gun_sweep_entry_bids",
        "_v4_manage_resting_inner")

def make_bot():
    s = types.SimpleNamespace()
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s.session = s.ak = s.pk = s.rl = None
    s.positions = {}
    s.event_tickers = {}
    s.books = {}
    s.event_start_time = {}
    s._events_live = set()
    s._start_conflict = set()
    s._gun_state = {}
    s._gun_void_pending = {}
    s._gun_void_logged = set()
    s._pm_honest = {}
    s._trade_times = {}
    s._booking_inflight = set()
    s._fv_burst = {}
    s.n_entries = 0
    s.processed_events = set()
    s.fused_gun = False
    s._conception_halt = False
    s._completion_cross_allow = set()
    s._horizon_state = lambda et, now=None: (False, 0)
    s._save_v4_resting = lambda: None
    s._save_processed = lambda: None
    s.completion_calls = []
    async def _noop(*a, **k):
        return None
    async def _mc(tk, pos, book, now):
        s.completion_calls.append(tk)
    s._v4_apply_exit = _noop
    s._cancel_sibling_if_paired_over_cap = _noop
    s._reaim_sibling_on_arrival = _noop
    s._v4_manage_completion = _mc
    async def _taker(tk, oid):
        return False
    s._fill_is_taker = _taker
    s._join_trial_resolve = lambda *a, **k: None
    s._staircase_resolve = lambda *a, **k: None
    for nm in REAL:
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

def mkpos(tk, order_id, qty=0, mode="resting_maker", price=85):
    p = M.Position(ticker=tk, event_ticker=EV, category="ATP_CHALL",
                   direction="", cell_name="", cell_cfg={})
    p.is_v4 = True
    p.phase = "entry_resting"
    p.entry_order_id = order_id
    p.entry_qty = qty
    p.entry_mode = mode
    p.entry_price = price
    p.play_type = "v4"
    p.target_price = price
    p.walk_ref = price
    p.staircase_ref = price
    p.match_start_ts = 0
    return p

def evs(s, name):
    return [d for (e, d, t) in s.logs if e == name]

# ======================================================================
print("--- FIX 1: expected_expiration_time is NEVER a start ---")
# ======================================================================
_src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "live_v4.py"), encoding="utf-8").read()
_occ = [l for l in _src.splitlines() if "occ_str = m.get(" in l]
check(bool(_occ) and all("expected_expiration_time" not in l for l in _occ),
      "F1 event_kalshi_occ derives from occurrence_datetime ONLY")
check("await self._start_gate_cancel_resting(_tk, _pos, \"boot_\" + _bwy)" in _src,
      "F1b boot sequence applies the start gate after adoption (regression K hook)")

# ======================================================================
print("--- B: missing occurrence + false 22:00 -> unknown start; maker AND taker refuse ---")
# ======================================================================
# occurrence_datetime missing => event_start_time never set => UNKNOWN start.
s = make_bot(); reset()   # event_start_time {} == unknown
oid, resp = run(s._place_order_unlocked(MAY, "buy", "yes", 85, 5, post_only=True))
check(oid == "" and resp.get("_error") == "post_start_entry_refused",
      "B.1 MAKER entry buy refused (unknown start)")
oid, resp = run(s._place_order_unlocked(MAY, "buy", "yes", 85, 5, post_only=False))
check(oid == "" and resp.get("_error") == "post_start_entry_refused",
      "B.2 ORDINARY TAKER (post_only=False) entry buy ALSO refused (unknown start)")
check(POSTED == [], "B.3 nothing placed -- Mayo never fills")

# ======================================================================
print("--- A: exact chronology -- placement REFUSED before any tape signal ---")
# ======================================================================
s = make_bot(); reset()
# 19:36 placement: no gun has fired yet, start is UNKNOWN (false end-as-start
# removed by FIX 1). The maker entry is refused HERE, before the 19:39 signal.
oid, resp = run(s._place_order_unlocked(MAY, "buy", "yes", 85, 5, post_only=True))
check(resp.get("_error") == "post_start_entry_refused" and
      evs(s, "post_start_entry_refused")[0]["reason"] == "unknown_start",
      "A.1 Mayo 19:36 placement refused (unknown_start) BEFORE the 19:39 signal")
# 19:39 the tape signal arrives afterwards (no schedule to clamp against -> fires)
fired = s._gun_stamp(EV, "tape_flow", {"ref_rise_cents": 71, "prints_30m": 28, "threshold": 16})
check(fired and EV in s._events_live, "A.2 the later tape signal fires the gun")
check(POSTED == [], "A.3 no Mayo order ever placed -> no post-start fill")

# ======================================================================
print("--- E: post_only=False entry refused on a LIVE / past start ---")
# ======================================================================
s = make_bot(); reset(); s._events_live = {EV}; s.event_start_time[EV] = FUT
oid, resp = run(s._place_order_unlocked(MAY, "buy", "yes", 85, 5, post_only=False))
check(resp.get("_error") == "post_start_entry_refused", "E.1 taker refused on a live event")
s = make_bot(); reset(); s.event_start_time[EV] = PAST
oid, resp = run(s._place_order_unlocked(MAY, "buy", "yes", 85, 5, post_only=False))
check(resp.get("_error") == "post_start_entry_refused", "E.2 taker refused on a past-start event")

# ======================================================================
print("--- C: already-resting maker bid cancels (production cancel path) ---")
# ======================================================================
for label, setup in (("unknown", lambda s: None),
                     ("past", lambda s: s.event_start_time.__setitem__(EV, PAST)),
                     ("conflict", lambda s: s._start_conflict.add(EV))):
    s = make_bot(); reset()
    setup(s)
    p = mkpos(MAY, "MAY-OID")
    s.positions[MAY] = p
    ORDERS["MAY-OID"] = {"order_id": "MAY-OID", "status": "resting", "fill_count_fp": 0}
    run(s._v4_manage_resting_inner(MAY, p, None, time.time()))
    check("MAY-OID" in DELETED, "C.%s resting maker bid CANCELLED via api_delete (real path)" % label)
    check(MAY not in s.positions, "C.%s leg untombstoned after confirmed cancel" % label)
    check(bool(evs(s, "post_start_entry_cancelled")), "C.%s post_start_entry_cancelled logged" % label)

# ======================================================================
print("--- D: resting completion_reprice bid ALSO cancels after real start ---")
# ======================================================================
s = make_bot(); reset(); s._events_live = {EV}
p = mkpos(MIC, "MIC-COMP", mode="completion_reprice")
s.positions[MIC] = p
ORDERS["MIC-COMP"] = {"order_id": "MIC-COMP", "status": "resting", "fill_count_fp": 0}
run(s._v4_manage_resting_inner(MIC, p, None, time.time()))
check("MIC-COMP" in DELETED and MIC not in s.positions,
      "D.1 completion_reprice bid cancelled at the manage pass (no exemption)")
check(s.completion_calls == [], "D.2 start-gate ran BEFORE the completion dispatch")
# the gun sweep also no longer skips completion bids
s = make_bot(); reset(); s.event_tickers[EV] = {MIC}
p = mkpos(MIC, "MIC-COMP2", mode="completion_reprice"); s.positions[MIC] = p
ORDERS["MIC-COMP2"] = {"order_id": "MIC-COMP2", "status": "resting", "fill_count_fp": 0}
run(s._gun_sweep_entry_bids(EV, "tape_flow"))
check("MIC-COMP2" in DELETED, "D.3 gun sweep cancels a completion_reprice bid (exemption removed)")

# ======================================================================
print("--- I: raced fill booked EXACTLY once while the sibling is canceled ---")
# ======================================================================
s = make_bot(); reset(); s._events_live = {EV}; s.event_tickers[EV] = {MAY, MIC}
may = mkpos(MAY, "MAY-RACED"); mic = mkpos(MIC, "MIC-CLEAN")
s.positions = {MAY: may, MIC: mic}
# MAY raced-filled during the cancel window; MIC cancels clean
ORDERS["MAY-RACED"] = {"order_id": "MAY-RACED", "status": "executed",
                       "fill_count_fp": 5, "yes_price": 85}
ORDERS["MIC-CLEAN"] = {"order_id": "MIC-CLEAN", "status": "resting", "fill_count_fp": 0}
run(s._gun_sweep_entry_bids(EV, "tape_flow"))
check(may.entry_qty == 5 and may.phase == "active", "I.1 raced Mayo fill BOOKED (qty 5, active)")
check(len([1 for (e, d, t) in s.logs if e == "entry_filled"]) == 1,
      "I.2 entry_filled booked exactly once")
check("MIC-CLEAN" in DELETED and MIC not in s.positions, "I.3 clean sibling cancelled")
# re-sweep MAY: idempotent, no second booking, position not deleted (raced fill kept)
_n_before = len([1 for (e, d, t) in s.logs if e == "entry_filled"])
run(s._cancel_entry_and_resolve(MAY, may, "resweep", "resweep"))
check(len([1 for (e, d, t) in s.logs if e == "entry_filled"]) == _n_before,
      "I.4 re-resolve is idempotent -- the raced fill is never re-booked or deleted")
check(may.entry_qty == 5, "I.5 raced fill preserved (never deleted)")

# ======================================================================
print("--- J: protective exits and foreign orders are NEVER touched ---")
# ======================================================================
s = make_bot(); reset(); s._events_live = {EV}; s.event_tickers[EV] = {MAY}
may = mkpos(MAY, "MAY-ENTRY"); may.exit_order_id = "MAY-EXIT"
s.positions[MAY] = may
ORDERS["MAY-ENTRY"] = {"order_id": "MAY-ENTRY", "status": "resting", "fill_count_fp": 0}
ORDERS["MAY-EXIT"] = {"order_id": "MAY-EXIT", "status": "resting", "fill_count_fp": 0}
ORDERS["FOREIGN-1"] = {"order_id": "FOREIGN-1", "status": "resting", "fill_count_fp": 0}
run(s._gun_sweep_entry_bids(EV, "tape_flow"))
check("MAY-ENTRY" in DELETED, "J.1 the entry bid is cancelled")
check("MAY-EXIT" not in DELETED, "J.2 the protective exit (sell) is NEVER cancelled")
check("FOREIGN-1" not in DELETED, "J.3 a foreign order is NEVER cancelled")

# ======================================================================
print("--- K: boot fail-closed -- pre-existing resting entries cancelled ---")
# ======================================================================
# replicate the boot post-adoption loop body (same production call it makes)
s = make_bot(); reset()   # unknown start (as MICMAY after FIX 1)
may = mkpos(MAY, "MAY-BOOT"); mic = mkpos(MIC, "MIC-BOOT")
s.positions = {MAY: may, MIC: mic}
ORDERS["MAY-BOOT"] = {"order_id": "MAY-BOOT", "status": "resting", "fill_count_fp": 0}
ORDERS["MIC-BOOT"] = {"order_id": "MIC-BOOT", "status": "resting", "fill_count_fp": 0}
for _tk, _pos in list(s.positions.items()):
    if (_pos.is_v4 and _pos.phase == "entry_resting" and _pos.entry_order_id):
        _rf, _wy = s._entry_start_gate(_pos.event_ticker)
        if _rf:
            run(s._start_gate_cancel_resting(_tk, _pos, "boot_" + _wy))
check("MAY-BOOT" in DELETED and "MIC-BOOT" in DELETED,
      "K.1 both pre-existing resting entries cancelled at boot (fail closed)")
check(not s.positions, "K.2 both legs untombstoned")

# ======================================================================
print("--- F/G/H: proof-grade sources override a FALSE FUTURE schedule ---")
# ======================================================================
def override_case(source, detail, label):
    s = make_bot(); reset(); s.event_start_time[EV] = FUT   # false future schedule
    fired = s._gun_stamp(EV, source, detail)
    check(fired is True, "%s %s fires despite the false future schedule" % (label, source))
    check(EV in s._events_live, "%s event live" % label)
    check(bool(evs(s, "sched_liar_override")) and not evs(s, "phantom_bell_void"),
          "%s sched_liar_override (NOT voided)" % label)
    check(s._strong_live_evidence(source, detail) is True, "%s classified proof-grade" % label)
override_case("te_scoreboard", {"te_match_id": "X", "te_first_inplay": True}, "F")
override_case("schedule_live", {"sched_source": "te", "sched_method": "status"}, "G")
override_case("milestone_official", {"ms_status": "live", "official_start": "x"}, "H")
# ambiguous milestone status stays fail-closed (voided, not proof-grade)
s = make_bot(); reset(); s.event_start_time[EV] = FUT
fired = s._gun_stamp(EV, "milestone_official", {"ms_status": "SCH"})
check(fired is False and s._strong_live_evidence("milestone_official", {"ms_status": "SCH"}) is False,
      "H.amb ambiguous milestone status is NOT proof-grade (fail closed, voided)")

print("\n%s" % ("ALL P0 REAL-START GUARD TESTS PASS" if not fails else "*** %d FAILURE(S)" % fails))
sys.exit(1 if fails else 0)
