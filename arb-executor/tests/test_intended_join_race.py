#!/usr/bin/env python3
"""[C-FEEDER FIX-2] intended_join keying race — decision-time capture.

THE QUESAM FRAME (2026-06-12 10:32:21 ET, ~2min after the QUE window opened):
an engagement join placed at 48 (decision-time best_bid 48); the book ticked
during the pre-post-guard/place_order awaits; the old keying re-read
book.best_bid post-await -> intended_join=False on a by-construction join ->
E3_missing_intended_join fired, the tripwire cancelled all five live joins and
disarmed engagement. The key is now derived from the placement DECISION
(captured snapshot + construction), never a live-book re-read.
Run: cd arb-executor && python3 tests/test_intended_join_race.py
"""
import sys, types, time, inspect
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails; print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

S = types.SimpleNamespace()  # the pure helper takes no instance state
key = lambda *a: M.LiveV3._intended_join_at_placement(S, *a)

# ---- 1. the pure key ----
check(key("resting_maker", 48, 48, "per_cell") is True,
      "normal resting-maker AT the decision bid -> join")
check(key("resting_maker", 47, 48, "per_cell") is False,
      "normal resting-maker below the decision bid (drift/offset) -> NOT a join")
check(key("marketable_clamp", 49, 48, "per_cell") is False,
      "normal marketable-clamp placement -> NOT a join")
check(key("resting_maker", 48, 49, "engagement_wave1") is True,
      "engagement join survives a book tick (target != post-move bid) -> True BY CONSTRUCTION")
check(key("marketable_clamp", 49, 50, "engagement_wave1") is True,
      "engagement join pushed down the clamp branch by a moving book -> still True")

# the old keying is demonstrably the bug on the QUESAM frame:
old_key = lambda entry_mode, target, live_bid: (entry_mode == "resting_maker"
                                                and target == live_bid)
check(old_key("resting_maker", 48, 49) is False and key("resting_maker", 48, 49, "engagement_wave1") is True,
      "QUESAM frame: old post-await keying False, new decision keying True")

# ---- 2. the exact frame through the E-guards: no E3 ----
ET = "KXWTACHALLENGERMATCH-26JUN12QUESAM"
SAM, QUE = ET + "-SAM", ET + "-QUE"
s = types.SimpleNamespace()
s.engagement_cells = {("WTA_CHALL", "T240_T60", "r45_54")}
s.engagement_band_gating = True  # band table consulted in this stub (E2 path live)
s.engagement_joinbid = True; s.engagement_disabled = False
s.regime_lookup = lambda cat, price: "r45_54"
s.positions = {QUE: M.Position(ticker=QUE, event_ticker=ET, category="WTA_CHALL",
                               direction="", cell_name="", cell_cfg={}, entry_price=51)}
s.books = {}; s.event_tickers = {ET: {SAM, QUE}}
s.logs = []; s._log = lambda ev, det=None, ticker="": s.logs.append((ev, det or {}))
for nm in ("_engagement_place_guards", "_engagement_bucket", "_paired_basis_ok",
           "_sibling_ticker", "_sibling_engageable"):
    setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))

pos = M.Position(ticker=SAM, event_ticker=ET, category="WTA_CHALL", direction="underdog",
                 cell_name="", cell_cfg={}, entry_price=48, target_price=48,
                 entry_mode="resting_maker", play_type="v4_engagement_join",
                 intended_join=key("resting_maker", 48, 49, "engagement_wave1"))
viol = s._engagement_place_guards(SAM, ET, "WTA_CHALL", pos, 238 * 60)
check(viol is None, "QUESAM frame through E1-E3 guards -> NO violation (E3 race closed)")

# the guard still catches a REAL regression (join machinery bypassed entirely)
pos_bad = M.Position(ticker=SAM, event_ticker=ET, category="WTA_CHALL", direction="underdog",
                     cell_name="", cell_cfg={}, entry_price=48, target_price=48,
                     entry_mode="resting_maker", play_type="v4_engagement_join",
                     intended_join=False)
viol = s._engagement_place_guards(SAM, ET, "WTA_CHALL", pos_bad, 238 * 60)
check(viol is not None and viol[0] == "E3_missing_intended_join",
      "E3 still fires on a genuinely unkeyed engagement placement")

# ---- 3. source pins: the placement block uses the captured snapshot ----
src = inspect.getsource(M.LiveV3._route_event)
check("placement_bid, placement_ask = book.best_bid, book.best_ask" in src,
      "decision-time capture present in the placement block")
check("target_bid == book.best_bid" not in src,
      "post-await live-book keying eliminated (source-pinned)")
check('"book_bid": placement_bid' in src and '"book_ask": placement_ask' in src,
      "v4_place book fields log the decision snapshot")
check("_intended_join_at_placement" in src,
      "Position keying routed through the pure decision-time helper")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
