#!/usr/bin/env python3
"""[C-TRIPWIRE] regression: runtime completion-mechanism tripwire (V1-V4) with
self-disable, incident-file persistence across restart, disabled-state no-ops,
and flag-OFF byte-identity preserved.

Run: cd arb-executor && python3 tests/test_completion_tripwire.py"""
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

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

FAKE_OLD_FILLED = [0]
async def _fake_api_get(sess, ak, pk, path, rl):
    if "/portfolio/orders/" in path:
        return {"order": {"fill_count_fp": FAKE_OLD_FILLED[0]}}
    return {}
M.api_get = _fake_api_get

TMP = Path(tempfile.mkdtemp())
ORIG_INCIDENT = M.COMPLETION_INCIDENT_FILE
M.COMPLETION_INCIDENT_FILE = TMP / "completion_incident.json"
ORIG_RESTING = M.V4_RESTING_FILE
M.V4_RESTING_FILE = TMP / "resting.json"

def book(bid, ask):
    return types.SimpleNamespace(best_bid=bid, best_ask=ask, bids={}, asks={},
                                 last_trade_price=0, last_trade_ts=0.0)

def make_pos(tk, et="EV", cat="ATP_MAIN", **kw):
    return M.Position(ticker=tk, event_ticker=et, category=cat,
                      direction="", cell_name="", cell_cfg={}, **kw)

BOUND = ("_sibling_ticker", "_cancel_sibling_if_paired_over_cap",
         "_attempt_completion_reprice", "_completion_target",
         "_completion_buffer_exempt", "_reprice_target", "_maybe_set_window_open",
         "_v4_manage_completion", "_completion_revert", "_log_orphan_outcome",
         "_untombstone_entry", "_is_match_live", "_save_v4_resting",
         "_completion_tripwire", "_completion_fill_guards", "_completion_arm_check")

def make_bot(flag=True, disabled=False):
    s = types.SimpleNamespace()
    s.completion_reprice = flag
    s.completion_disabled = disabled
    s.completion_cells = {("ATP_MAIN", 41): 2}
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
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s.placed = []
    s.cancelled = []
    async def place_order(tk, action, side, price, count, post_only=True):
        s.placed.append({"tk": tk, "price": price, "count": count, "post_only": post_only})
        return "OID_NEW", {"order": {"status": "resting"}}
    s.place_order = place_order
    async def cancel_order(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        return True
    s.cancel_order = cancel_order
    for nm in BOUND:
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    s._save_v4_resting = lambda: None
    return s

def paired(flag=True, disabled=False):
    s = make_bot(flag, disabled)
    s.event_tickers = {"EV": {"L1", "SB"}}
    leg1 = make_pos("L1", entry_price=35, entry_qty=7, phase="active",
                    entry_order_id="LEG1OID", is_v4=True)
    sib = make_pos("SB", entry_price=38, entry_qty=0, phase="entry_resting",
                   entry_order_id="SIBOID", is_v4=True, entry_mode="resting_maker",
                   target_price=38)
    s.positions = {"L1": leg1, "SB": sib}
    s.books = {"SB": book(38, 60)}
    s._window_open = {"L1": {"price": 41, "cell": 41, "ts": time.time()},
                      "SB": {"price": 40, "cell": 40, "ts": time.time()}}
    return s, leg1, sib

def comp_pos(**kw):
    d = dict(entry_price=42, entry_qty=0, phase="entry_resting",
             entry_order_id="COMPOID", is_v4=True, entry_mode="completion_reprice",
             target_price=42, completion_s0=40, completion_x=2,
             completion_leg1_basis=35, completion_qty=7,
             completion_reprice_ts=time.time() - 700, completion_prev_price=38,
             completion_prev_mode="resting_maker", completion_prev_target=38,
             completion_lookup_cell=41, match_start_ts=time.time() + 7200)
    d.update(kw)
    return make_pos("SB", **d)

def rm_incident():
    if M.COMPLETION_INCIDENT_FILE.exists():
        os.remove(M.COMPLETION_INCIDENT_FILE)

# ===== V1: post_only breach at the attempt site =====
rm_incident()
s, leg1, sib = paired()
s._reprice_target = lambda t, a: (t, False)   # force a non-post-only output
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
fired = [l for l in s.logs if l[0] == "completion_tripwire_fired"]
check(len(fired) == 1 and fired[0][1]["violation"] == "V1_post_only_breach"
      and s.completion_disabled is True,
      "V1(attempt): non-post-only completion order -> tripwire fires, mechanism disabled")
check(not s.placed and not any(c["oid"] == "SIBOID" for c in s.cancelled),
      "V1(attempt): fires BEFORE touching the sibling's resting bid (no cancel, no place)")
check(M.COMPLETION_INCIDENT_FILE.exists()
      and json.load(open(M.COMPLETION_INCIDENT_FILE))["violation"] == "V1_post_only_breach",
      "V1: incident file written with violation payload")

# disabled-state no-op on a subsequent attempt
s.logs.clear(); s.placed.clear(); s.cancelled.clear()
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
check(not s.placed and not s.cancelled and not s.logs,
      "disabled: subsequent leg-1 fills -> completion arm fully no-ops")

# ===== V1 at the freshness re-place site =====
rm_incident()
s = make_bot()
s.event_tickers = {"EV": {"L1", "SB"}}
leg1 = make_pos("L1", entry_price=35, entry_qty=7, phase="active", is_v4=True)
pos = comp_pos()
s.positions = {"L1": leg1, "SB": pos}
s.books = {"SB": book(38, 42)}   # ask moved -> s1 changes -> re-place path
s._reprice_target = lambda t, a: (t, False)
run(s._v4_manage_completion("SB", pos, s.books["SB"], time.time()))
fired = [l for l in s.logs if l[0] == "completion_tripwire_fired"]
check(len(fired) == 1 and fired[0][1]["context"]["site"] == "freshness"
      and s.completion_disabled,
      "V1(freshness): non-post-only re-place -> tripwire fires at the freshness site")
check(any(c["label"] == "completion_tripwire" for c in s.cancelled),
      "V1(freshness): tripwire cancels the resting completion bid (cancel-only)")

# ===== V2/V3/V4 fill guards (pure) =====
s = make_bot()
p = comp_pos()
v = s._completion_fill_guards(p, 42, True)
check(v is not None and v[0] == "V2_is_taker_completion_fill", "V2: is_taker=True -> violation")
check(s._completion_fill_guards(p, 42, None) is None,
      "V2: is_taker=None (lookup failed) does NOT fire (fail-open on transient API error)")
check(s._completion_fill_guards(p, 42, False) is None, "V2: maker fill -> clean")
v = s._completion_fill_guards(p, 65, False)
check(v is not None and v[0] == "V3_cap_breach" and v[1]["combined"] == 100,
      "V3: leg1_basis 35 + fill 65 = 100 > 99 -> violation")
p2 = comp_pos(completion_lookup_cell=88)
v = s._completion_fill_guards(p2, 42, False)
check(v is not None and v[0] == "V4_cell_not_in_table", "V4(fill): cell 88 not in table -> violation")

# ===== V4 at the manage site =====
rm_incident()
s = make_bot()
s.event_tickers = {"EV": {"L1", "SB"}}
pos = comp_pos(completion_lookup_cell=88)
s.positions = {"SB": pos}
s.books = {"SB": book(38, 60)}
run(s._v4_manage_completion("SB", pos, s.books["SB"], time.time()))
fired = [l for l in s.logs if l[0] == "completion_tripwire_fired"]
check(len(fired) == 1 and fired[0][1]["violation"] == "V4_cell_not_in_table"
      and any(c["label"] == "completion_tripwire" for c in s.cancelled)
      and "SB" not in s.positions,
      "V4(manage): resting completion order with off-table cell -> fire + cancel + leg freed")

# ===== tripwire fires once (idempotent) =====
rm_incident()
s = make_bot()
run(s._completion_tripwire("V3_cap_breach", {"x": 1}, tk="T"))
n1 = len([l for l in s.logs if l[0] == "completion_tripwire_fired"])
run(s._completion_tripwire("V2_is_taker_completion_fill", {"y": 2}, tk="T"))
n2 = len([l for l in s.logs if l[0] == "completion_tripwire_fired"])
check(n1 == 1 and n2 == 1 and json.load(open(M.COMPLETION_INCIDENT_FILE))["violation"] == "V3_cap_breach",
      "tripwire fires ONCE; first violation owns the incident file")

# ===== incident file blocks re-arm across restart =====
s2 = make_bot()                      # fresh "boot" with the incident file present
s2.completion_disabled = False
s2._completion_arm_check()
check(s2.completion_disabled is True
      and any(l[0] == "completion_incident_block" for l in s2.logs),
      "boot with incident file -> mechanism stays DISABLED (blocked until removed by hand)")
rm_incident()
s3 = make_bot()
s3.completion_disabled = False
s3._completion_arm_check()
check(s3.completion_disabled is False
      and any(l[0] == "completion_tripwire_armed" for l in s3.logs),
      "boot without incident file -> tripwire ARMED, mechanism enabled")

# ===== disabled no-ops everywhere =====
s = make_bot(disabled=True)
s.ticker_to_event = {"TK": "EV"}
s.event_tickers = {"EV": {"TK"}}
s.event_start_time = {"EV": time.time() + 230 * 60}
s.books = {"TK": book(10, 90)}
s.books["TK"].last_trade_price = 44
s.books["TK"].last_trade_ts = time.time() - 5
s._maybe_set_window_open("TK", time.time())
check("TK" not in s._window_open and not s.logs,
      "disabled: window-open tracking no-ops")
s, leg1, sib = paired(disabled=True)
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
check(not s.placed and not s.cancelled, "disabled: attempt arm no-ops (T50 path untouched)")
s, leg1, sib = paired(disabled=True)
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 62))   # over cap
check(len(s.cancelled) == 1 and s.cancelled[0]["label"] == "paired_basis_cancel",
      "disabled: T50 over-cap cancel still fires (only the completion mechanism died)")
s = make_bot(disabled=True)
s.event_tickers = {"EV": {"L1", "SB"}}
pos = comp_pos()
s.positions = {"SB": pos}
s.books = {"SB": book(38, 60)}
run(s._v4_manage_completion("SB", pos, s.books["SB"], time.time()))
rv = [l for l in s.logs if l[0] == "completion_reverted"]
check(len(rv) == 1 and rv[0][1]["reason"] == "completion_disabled",
      "disabled: restored resting completion bid is reverted on first manage pass")

# ===== flag-OFF byte-identity =====
s, leg1, sib = paired(flag=False)
run(s._cancel_sibling_if_paired_over_cap("L1", "EV", 35))
check(not s.placed and not s.cancelled and not s.logs,
      "flag OFF: handler remains a pure no-op under cap (tripwire adds no behavior)")
s = make_bot(flag=False)
s._maybe_set_window_open("TK", time.time())
check(not s.logs, "flag OFF: window-open path unchanged")

M.COMPLETION_INCIDENT_FILE = ORIG_INCIDENT
M.V4_RESTING_FILE = ORIG_RESTING
print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
