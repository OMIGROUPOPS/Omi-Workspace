#!/usr/bin/env python3
"""[C-JOINBID WAVE-1] engagement join-bid for the no-print hole — dormant build.

skip->join on an eligible quiet leg; ineligible cell still skips; printed legs
structurally untouched; cap-blocked join -> named skip; intended_join inherited
by construction; depth_ahead logged; flag-off byte-identical; CSV loads (30
rows, sha-pinned); sparse play_type save/restore.
Run: cd arb-executor && python3 tests/test_engagement_joinbid.py
"""
import sys, types, time, asyncio, json, tempfile, inspect, hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails; print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

TMP = Path(tempfile.mkdtemp())
M.V4_RESTING_FILE = TMP / "resting.json"
M.ENGAGEMENT_INCIDENT_FILE = TMP / "engagement_incident.json"
M.COMPLETION_INCIDENT_FILE = TMP / "completion_incident.json"

def run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def book(bid, ask, bids=None):
    return types.SimpleNamespace(best_bid=bid, best_ask=ask,
        bids=bids or {}, asks={}, updated=time.time(),
        last_trade_price=0, last_trade_ts=0.0)

BOUND = ("_load_engagement_cells", "_engagement_bucket", "_engagement_join_eligible",
         "regime_lookup", "_sibling_ticker", "_sibling_engageable", "_paired_basis_ok",
         "_save_v4_resting", "_load_v4_resting",
         # [C-JOINBID AMEND] tripwire surface
         "_mechanism_tripwire", "_completion_tripwire", "_engagement_tripwire",
         "_engagement_place_guards", "_engagement_arm_check",
         "_cancel_entry_and_resolve", "_parse_entry_fill", "_book_v4_entry_fill",
         "_untombstone_entry")

def make_bot(flag=True, cells=None):
    s = types.SimpleNamespace()
    s.engagement_joinbid = flag
    s.engagement_disabled = False
    s.completion_disabled = False
    s.engagement_cells = cells if cells is not None else {
        ("ATP_CHALL", "T240_T60", "r25_34"), ("WTA_MAIN", "T60_T15", "r35_44")}
    s.completion_reprice = False
    s.positions = {}; s.books = {}; s.event_tickers = {}
    s._window_open = {}
    s._booking_inflight = set()
    s.n_entries = 0
    s.session = None; s.ak = None; s.pk = None; s.rl = None
    s.processed_events = set(); s._save_processed = lambda: None
    s.config = {}
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    s.cancelled = []
    async def cancel_order(tk, oid, label=""):
        s.cancelled.append({"tk": tk, "oid": oid, "label": label})
        return True
    s.cancel_order = cancel_order
    for nm in BOUND:
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

async def _fake_api_get(sess, ak, pk, path, rl):
    if "/portfolio/orders/" in path and "?" not in path:
        return {"order": {"status": "canceled", "fill_count_fp": 0}}
    return {"orders": []}
M.api_get = _fake_api_get

# ---- 1. skip -> join on an eligible quiet leg ----
s = make_bot()
lvl = s._engagement_join_eligible("ATP_CHALL", book(28, 30), 7200)   # T-120, r25_34
check(lvl == 28, "eligible quiet leg: join level = best_bid (28)")
lvl = s._engagement_join_eligible("WTA_MAIN", book(38, 39), 1800)    # T-30, r35_44
check(lvl == 38, "eligible T60_T15 leg: join at 38")

# ---- 2. ineligible cell / bucket still skips ----
check(s._engagement_join_eligible("ATP_CHALL", book(48, 50), 7200) is None,
      "off-table band (r45_54 not in wave-1 fixture): skip stands")
check(s._engagement_join_eligible("WTA_MAIN", book(38, 39), 7200) is None,
      "right band, wrong bucket: skip stands")
check(s._engagement_join_eligible("ATP_CHALL", book(28, 30), 600) is None,
      "inside T-15: no engagement bucket")
check(s._engagement_join_eligible("ATP_CHALL", book(28, 30), 15000) is None,
      "outside T-240: no engagement bucket")

# ---- 2b. no-bid / locked / degenerate books: skip stands (named upstream) ----
check(s._engagement_join_eligible("ATP_CHALL", book(0, 30), 7200) is None, "no bid: skip")
check(s._engagement_join_eligible("ATP_CHALL", book(30, 30), 7200) is None, "locked book: skip")
check(s._engagement_join_eligible("ATP_CHALL", book(28, 100), 7200) is None, "ask 100: skip")

# ---- 3. flag off = byte-identical (helper inert; loader gated at init) ----
s_off = make_bot(flag=False)
check(s_off._engagement_join_eligible("ATP_CHALL", book(28, 30), 7200) is None,
      "flag OFF: helper inert")
init_src = inspect.getsource(M.LiveV3.__init__)
check("if self.engagement_joinbid:" in init_src and "_load_engagement_cells" in init_src,
      "loader called only under the flag (no table, no event when OFF)")

# ---- 4. bucket boundaries (replay parity) ----
s = make_bot()
check(s._engagement_bucket(3601) == "T240_T60" and s._engagement_bucket(14400) == "T240_T60",
      "bucket (60,240] min")
check(s._engagement_bucket(3600) == "T60_T15" and s._engagement_bucket(901) == "T60_T15",
      "bucket (15,60] min")
check(s._engagement_bucket(900) is None and s._engagement_bucket(14401) is None,
      "outside buckets -> None")

# ---- 5. real CSV loads: 30 rows, sha-pinned ----
s = make_bot(cells=set())
s.config = {}
M.LiveV3._load_engagement_cells(s)
check(len(s.engagement_cells) == 30, "wave-1 CSV: 30 rows loaded")
ev = [d for (e, d, t) in s.logs if e == "engagement_cells_loaded"]
check(ev and ev[0]["rows"] == 30 and ev[0]["provenance_sha"] == "b601b5e89e04955a",
      "engagement_cells_loaded telemetry w/ replay parquet sha prefix")
check(("ATP_CHALL", "T240_T60", "r05_14") in s.engagement_cells
      and ("WTA_MAIN", "T60_T15", "r65_74") in s.engagement_cells
      and ("WTA_CHALL", "T60_T15", "r25_34") not in s.engagement_cells,
      "spot-check: strict-cleared rows in, non-cleared row out")
# sha pinned on LF-normalized content (= the git blob = what prod checks out;
# Windows working trees may carry CRLF via autocrlf)
csv_lf = open(REPO / "docs/policy/engagement_cells_v1.csv", "rb").read().replace(b"\r\n", b"\n")
check(hashlib.sha256(csv_lf).hexdigest()
      == "ed1a3788bad01cbc36737d69cfb661d86df8dc6e164fefb898d3f27761d2934d",
      "engagement_cells_v1.csv sha pinned (LF-canonical)")

# ---- 6. cap-blocked join -> named skip (paired guard, real composition) ----
s = make_bot()
ET = "EV"; A = "EV-AAA"; Z = "EV-ZZZ"
s.event_tickers = {ET: {A, Z}}
held = M.Position(ticker=Z, event_ticker=ET, category="ATP_CHALL", direction="",
                  cell_name="", cell_cfg={})
held.entry_price = 75; held.entry_qty = 5; held.phase = "active"; held.settled = False
s.positions = {Z: held}
jl = s._engagement_join_eligible("ATP_CHALL", book(28, 30), 7200)
check(jl == 28 and s._paired_basis_ok(A, ET, jl) is False
      and any(e == "paired_basis_skip" for (e, d, t) in s.logs),
      "cap-blocked join (28+75=103>99): paired guard declines, NAMED")

# ---- 7. source pins: wiring + inheritance + depth + printed-leg isolation ----
src = inspect.getsource(M.LiveV3)
check('"engagement_wave1")' in src and "if no_trade:" in src
      and src.index("_engagement_join_eligible(cat, book, time_to_start)") >
          src.index("ent = self._v4_entry_anchor"),
      "override wired ONLY inside the ent-is-None/no_trade branch (printed legs untouched)")
check('intended_join=(entry_mode == "resting_maker"' in src,
      "join inherits intended_join by construction (target_bid == best_bid)")
check('"depth_ahead": int(book.bids.get(int(round(book.best_bid)), 0) or 0)' in src
      and 'if table_src == "engagement_wave1"' in src,
      "depth_ahead logged on engagement placements only")
check('pos.play_type = "v4_engagement_join"' in src,
      "ledger separability: engagement play_type distinguishable")

# ---- 8. sparse play_type save/restore + legacy key set preserved ----
s = make_bot()
s.positions = {}
now = time.time()
def mkleg(tk, ptype):
    p = M.Position(ticker=tk, event_ticker=tk[:-4], category="ATP_CHALL", direction="",
                   cell_name="", cell_cfg={})
    p.entry_price = 28; p.entry_order_id = "o" + tk; p.entry_posted_ts = now
    p.phase = "entry_resting"; p.is_v4 = True; p.target_price = 28
    p.regime_at_posting = "r25_34"; p.placement_minute = 240
    p.entry_mode = "resting_maker"; p.match_start_ts = now + 7200
    p.play_type = ptype
    return p
s.positions = {"EV1-AAA": mkleg("EV1-AAA", "v4_engagement_join"),
               "EV2-BBB": mkleg("EV2-BBB", "v4_resting_maker")}
M.LiveV3._save_v4_resting(s)
raw = json.load(open(M.V4_RESTING_FILE))
LEGACY = {"order_id", "event_ticker", "category", "direction", "posted_at", "posted_price",
          "target_price", "regime_at_posting", "placement_minute", "entry_mode", "match_start_ts"}
check(set(raw["EV2-BBB"].keys()) == LEGACY, "normal leg: EXACT legacy key set (sparse)")
check(raw["EV1-AAA"].get("play_type") == "v4_engagement_join", "engagement leg: play_type persisted")
s2 = make_bot(); s2.positions = {}
M.LiveV3._load_v4_resting(s2)
check(s2.positions["EV1-AAA"].play_type == "v4_engagement_join"
      and s2.positions["EV2-BBB"].play_type == "v4_resting_maker",
      "restart: play_type restored (engagement label survives)")

# ============================================================
# [C-JOINBID AMEND] engagement tripwire E1-E3, shared primitive
# ============================================================
def eng_pos(tk, et, price=28, join=True):
    p = M.Position(ticker=tk, event_ticker=et, category="ATP_CHALL", direction="",
                   cell_name="", cell_cfg={})
    p.entry_price = price; p.entry_order_id = "o_" + tk; p.phase = "entry_resting"
    p.is_v4 = True; p.entry_mode = "resting_maker"; p.target_price = price
    p.play_type = "v4_engagement_join"; p.intended_join = join
    return p

def fresh_inc():
    for f in (M.ENGAGEMENT_INCIDENT_FILE, M.COMPLETION_INCIDENT_FILE):
        if f.exists(): f.unlink()

# ---- T1. E1 paired-cap bypass fires; sweep cancels the engagement bid ----
fresh_inc()
s = make_bot()
ET2 = "EVX"; A2 = "EVX-AAA"; Z2 = "EVX-ZZZ"
s.event_tickers = {ET2: {A2, Z2}}
held = M.Position(ticker=Z2, event_ticker=ET2, category="ATP_CHALL", direction="",
                  cell_name="", cell_cfg={})
held.entry_price = 75; held.entry_qty = 5; held.phase = "active"
p = eng_pos(A2, ET2, 28)
s.positions = {Z2: held, A2: p}
v = s._engagement_place_guards(A2, ET2, "ATP_CHALL", p, 7200)
check(v is not None and v[0] == "E1_paired_cap_bypass", "E1: cap bypass detected (28+75>99)")
run(s._engagement_tripwire(v[0], v[1], tk=A2))
check(s.engagement_disabled is True, "E1 fire: engagement self-disabled in-process")
check(M.ENGAGEMENT_INCIDENT_FILE.exists()
      and json.load(open(M.ENGAGEMENT_INCIDENT_FILE))["violation"] == "E1_paired_cap_bypass",
      "E1 fire: incident file persisted atomically w/ violation")
check(any(c["tk"] == A2 and c["label"] == "engagement_tripwire" for c in s.cancelled),
      "E1 fire: resting engagement bid swept (cancel-only)")
check(any(e == "engagement_reverted" for (e, d, t) in s.logs)
      and any(e == "engagement_tripwire_fired" for (e, d, t) in s.logs),
      "E1 fire: engagement_tripwire_fired + engagement_reverted logged")
check(s.completion_disabled is False and not M.COMPLETION_INCIDENT_FILE.exists(),
      "completion mechanism UNTOUCHED by engagement fire")
check(s._engagement_join_eligible("ATP_CHALL",
      types.SimpleNamespace(best_bid=28, best_ask=30, bids={}), 7200) is None,
      "disabled state: eligibility no-ops the mechanism")
before = len(s.cancelled)
run(s._engagement_tripwire("E1_paired_cap_bypass", {}, tk=A2))
check(len(s.cancelled) == before, "fire-once: second fire is a no-op")

# ---- T2. E2 off-table fires ----
fresh_inc()
s = make_bot()
p = eng_pos("EVY-AAA", "EVY", 48)   # r45_54 not in fixture table
s.positions = {"EVY-AAA": p}; s.event_tickers = {"EVY": {"EVY-AAA"}}
v = s._engagement_place_guards("EVY-AAA", "EVY", "ATP_CHALL", p, 7200)
check(v is not None and v[0] == "E2_cell_off_table", "E2: off-table cell detected")
run(s._engagement_tripwire(v[0], v[1], tk="EVY-AAA"))
check(s.engagement_disabled and M.ENGAGEMENT_INCIDENT_FILE.exists(), "E2 fire: disable + incident")

# ---- T3. E3 missing intended_join fires; clean placement passes all three ----
fresh_inc()
s = make_bot()
p3 = eng_pos("EVZ-AAA", "EVZ", 28, join=False)
s.positions = {"EVZ-AAA": p3}; s.event_tickers = {"EVZ": {"EVZ-AAA"}}
v = s._engagement_place_guards("EVZ-AAA", "EVZ", "ATP_CHALL", p3, 7200)
check(v is not None and v[0] == "E3_missing_intended_join", "E3: missing intended_join detected")
ok_pos = eng_pos("EVZ-BBB", "EVZ2", 28, join=True)
s.positions = {"EVZ-BBB": ok_pos}; s.event_tickers = {"EVZ2": {"EVZ-BBB"}}
check(s._engagement_place_guards("EVZ-BBB", "EVZ2", "ATP_CHALL", ok_pos, 7200) is None,
      "clean engagement placement: all three guards pass")

# ---- T4. incident survives restart (arm check blocks; fails closed) ----
fresh_inc()
s = make_bot()
run(s._engagement_tripwire("E2_cell_off_table", {"x": 1}, tk="T"))
s2 = make_bot()   # "restart"
M.LiveV3._engagement_arm_check(s2)
check(s2.engagement_disabled is True
      and any(e == "engagement_incident_block" for (e, d, t) in s2.logs),
      "restart with incident file: mechanism stays DISABLED (blocked at arm)")
M.ENGAGEMENT_INCIDENT_FILE.write_text("not json{{{")
s3 = make_bot()
M.LiveV3._engagement_arm_check(s3)
check(s3.engagement_disabled is True, "unreadable incident: fails CLOSED")
fresh_inc()
s4 = make_bot()
M.LiveV3._engagement_arm_check(s4)
check(s4.engagement_disabled is False
      and any(e == "engagement_tripwire_armed" for (e, d, t) in s4.logs),
      "no incident: tripwire arms (E1-E3)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
