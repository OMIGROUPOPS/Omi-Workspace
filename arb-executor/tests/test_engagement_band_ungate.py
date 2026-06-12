#!/usr/bin/env python3
"""[C-FEEDER FIX-4] band-gating OFF engagement entry per LESSONS B22.

B22: cells are anchored at FILL, not predicted in advance — gating the
placement on the band at evaluation predicts the cell prospectively and built
the one-sided-by-construction class (2026-06-12 card: 8 pairs incl.
PLIVEK/SNIMON). Engagement now fires on ANY no-print leg inside the bucket
window; only the named economic gates remain (paired cap E1, T52, T-15
buffer, book-shape). The wave-1 table stays loaded DORMANT behind
engagement_band_gating (default OFF) for attribution + one-line rollback; E2
follows the flag; fill-time ledger carries cell-at-fill / band / table
membership for the band retrospective.
Run: cd arb-executor && python3 tests/test_engagement_band_ungate.py
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

def book(bid, ask):
    return types.SimpleNamespace(best_bid=bid, best_ask=ask, bids={}, asks={},
        updated=time.time(), last_trade_price=0, last_trade_ts=0.0)

CELLS = {("WTA_MAIN", "T240_T60", "r45_54")}  # PLI's r55_64 deliberately absent

def make_bot(gating):
    s = types.SimpleNamespace()
    s.engagement_joinbid = True; s.engagement_disabled = False
    s.engagement_band_gating = gating
    s.engagement_cells = set(CELLS)
    s.regime_lookup = lambda cat, price: ("r55_64" if 55 <= price <= 64 else
                                          "r45_54" if 45 <= price <= 54 else "r35_44")
    s.cell_lookup = lambda cat, price: price
    s.positions = {}; s.books = {}; s.event_tickers = {}
    s.logs = []
    s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}, ticker))
    for nm in ("_engagement_join_eligible", "_engagement_bucket",
               "_engagement_place_guards", "_paired_basis_ok",
               "_sibling_ticker", "_sibling_engageable"):
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s

TTS = 120 * 60  # T-120: T240_T60 bucket

# ---- 1. gating OFF (default): the PLI hole closes ----
s = make_bot(gating=False)
lvl = s._engagement_join_eligible("WTA_MAIN", book(57, 59), TTS)  # r55_64: NOT in table
check(lvl == 57, "band OFF: off-table no-print leg (PLI r55_64) -> JOIN fires at best_bid")
lvl = s._engagement_join_eligible("WTA_MAIN", book(49, 51), TTS)
check(lvl == 49, "band OFF: on-table leg still fires (no regression)")

# ---- 2. structural + economic gates remain ----
check(s._engagement_join_eligible("WTA_MAIN", book(50, 50), TTS) is None,
      "locked book still ineligible (join needs bid<ask)")
check(s._engagement_join_eligible("WTA_MAIN", book(57, 59), 10 * 60) is None,
      "inside T-15: outside the bucket window -> no join (structural envelope)")
check(s._engagement_join_eligible("WTA_MAIN", book(57, 59), 300 * 60) is None,
      "beyond T-240 -> no join (structural envelope)")
s.engagement_disabled = True
check(s._engagement_join_eligible("WTA_MAIN", book(57, 59), TTS) is None,
      "tripwire-disabled still blocks (fails closed)")

# ---- 3. gating ON: the dormant table still gates (one-line rollback) ----
s = make_bot(gating=True)
check(s._engagement_join_eligible("WTA_MAIN", book(57, 59), TTS) is None,
      "band ON: off-table band -> skip stands (dormant table functional)")
check(s._engagement_join_eligible("WTA_MAIN", book(49, 51), TTS) == 49,
      "band ON: on-table band -> join fires")

# ---- 4. E2 follows the flag; E1 (economic) fires either way ----
ET = "EV"; SAM, QUE = "EV-A", "EV-B"
def mkpos(price, intended=True):
    return M.Position(ticker=SAM, event_ticker=ET, category="WTA_MAIN", direction="",
                      cell_name="", cell_cfg={}, entry_price=price, target_price=price,
                      entry_mode="resting_maker", play_type="v4_engagement_join",
                      intended_join=intended)
s = make_bot(gating=False)
s.event_tickers = {ET: {SAM, QUE}}
s.positions[QUE] = M.Position(ticker=QUE, event_ticker=ET, category="WTA_MAIN",
                              direction="", cell_name="", cell_cfg={}, entry_price=40)
check(s._engagement_place_guards(SAM, ET, "WTA_MAIN", mkpos(57), TTS) is None,
      "band OFF: off-table placement -> NO E2 (by-design, attribution only)")
check(s._engagement_place_guards(SAM, ET, "WTA_MAIN", mkpos(57), 10 * 60)[0] == "E2_cell_off_table",
      "bucket-window breach still fires E2 with gating OFF (machinery regression)")
check(s._engagement_place_guards(SAM, ET, "WTA_MAIN", mkpos(70), TTS)[0] == "E1_paired_cap_bypass",
      "economic gate E1 (40+70=110 > cap) fires with gating OFF")
s2 = make_bot(gating=True)
s2.event_tickers = s.event_tickers; s2.positions = s.positions
check(s2._engagement_place_guards(SAM, ET, "WTA_MAIN", mkpos(57), TTS)[0] == "E2_cell_off_table",
      "band ON: off-table placement -> E2 fires (gate tripwire restored)")

# ---- 5. fill-time B22 attribution rides entry_filled ----
s = make_bot(gating=False)
s._booking_inflight = set(); s.n_entries = 0
s.exit_rule_for = lambda cat, price: (10, "hold")  # hold: no exit order needed
s.session = None; s.ak = None; s.pk = None; s.rl = None
for nm in ("_book_v4_entry_fill", "_v4_apply_exit", "_cancel_sibling_if_paired_over_cap",
           "_save_v4_resting"):
    setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
s._save_v4_resting = lambda: None
async def _no_cancel(tk, cid, label=""): return True
s.cancel_order = _no_cancel
import live_v4 as _m
async def _fake_get(sess, ak, pk, path, rl): return {"orders": []}
_m.api_get = _fake_get
pos = mkpos(57)
pos.is_v4 = True; pos.match_start_ts = time.time() + TTS
pos.entry_order_id = "OID1"
s.positions[SAM] = pos
run(s._book_v4_entry_fill(SAM, pos, 5, 58, "executed"))
fill_evs = [d for ev, d, _ in s.logs if ev == "entry_filled"]
check(len(fill_evs) == 1 and fill_evs[0].get("cell_at_fill") == 58
      and fill_evs[0].get("band_at_fill") == "r55_64"
      and fill_evs[0].get("band_on_table") is False
      and fill_evs[0].get("posted_level") == 57,
      "entry_filled carries cell-at-fill / band / table-membership / posted level")

# ---- 6. source pins: default OFF, table loaded regardless, placement attribution ----
src_init = inspect.getsource(M.LiveV3.__init__)
check('config.get("engagement_band_gating", False)' in src_init,
      "engagement_band_gating read from config, default False (dormant)")
src_route = inspect.getsource(M.LiveV3._route_event)
check('"band_on_table"' in src_route and '"bucket"' in src_route,
      "v4_place engagement dict carries band/bucket/table-membership attribution")
src_elig = inspect.getsource(M.LiveV3._engagement_join_eligible)
check("self.engagement_band_gating" in src_elig,
      "eligibility band check gated behind the flag (table dormant)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
