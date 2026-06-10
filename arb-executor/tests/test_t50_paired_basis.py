#!/usr/bin/env python3
"""T50 regression test — paired-basis guaranteed-loss guard.

Exercises the REAL live_v4 helpers (_paired_basis_ok / _cancel_sibling_if_paired_over_cap)
against the live KESMAR scenario (KES 37c + MAR 75c = 112c paired basis, a locked
-12c/pair loss). Run: cd arb-executor && python3 tests/test_t50_paired_basis.py
"""
import sys, types, asyncio
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent  # arb-executor/
sys.path.insert(0, str(REPO))                  # repo first -> repo fv.py, not /tmp/fv.py
import live_v4 as M

class Book:
    def __init__(self, bid, ask): self.best_bid = bid; self.best_ask = ask; self.updated = 1e18

def mk(ticker, et, entry_price=0, entry_qty=0, oid="", phase="entry_resting"):
    p = M.Position(ticker=ticker, event_ticker=et, category="ATP_CHALL",
                   direction="", cell_name="", cell_cfg={})
    p.entry_price = entry_price; p.entry_qty = entry_qty
    p.entry_order_id = oid; p.phase = phase; p.settled = False
    return p

ET = "KXATPCHALLENGERMATCH-26JUN01KESMAR"; KES = ET + "-KES"; MAR = ET + "-MAR"
cancels = []
s = types.SimpleNamespace(event_tickers={ET: {KES, MAR}}, positions={}, books={},
    _log=lambda *a, **k: None, _save_v4_resting=lambda: None,
    _untombstone_entry=lambda tk, pos: None,
    completion_reprice=False)  # PART-2: flag OFF -> handler is the pre-Part-2 T50 backstop
async def fake_cancel(tk, oid, label): cancels.append((tk, oid, label))
s.cancel_order = fake_cancel
for n in ("_sibling_ticker", "_paired_basis_ok", "_cancel_sibling_if_paired_over_cap"):
    setattr(s, n, types.MethodType(getattr(M.LiveV3, n), s))

fails = 0
def check(c, m):
    global fails; print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

# A — placement guard refuses the KESMAR pair (MAR resting @75, placing KES @37 -> 112 > 99)
s.positions = {MAR: mk(MAR, ET, entry_price=75, oid="mar1")}; s.books = {KES: Book(35, 38), MAR: Book(73, 76)}
check(s._paired_basis_ok(KES, ET, 37) is False, "refuse KES@37 when MAR resting@75 (112>99)")
# B — allow when combined under cap (MAR @45, KES @40 = 85)
s.positions = {MAR: mk(MAR, ET, entry_price=45, oid="mar1")}
check(s._paired_basis_ok(KES, ET, 40) is True, "allow KES@40 when MAR resting@45 (85<=99)")
# C — no sibling position -> use sibling current ask (MAR ask 76, KES @37 = 113 -> refuse)
s.positions = {}; s.books = {KES: Book(35, 38), MAR: Book(73, 76)}
check(s._paired_basis_ok(KES, ET, 37) is False, "refuse KES@37 when MAR ask=76 (113>99)")
# D — cancel-on-fill: MAR fills @75 -> cancel KES still-resting bid @37 (112 > 99)
cancels.clear(); kp = mk(KES, ET, entry_price=37, oid="kes1", entry_qty=0); s.positions = {KES: kp}; s.books = {}
asyncio.run(s._cancel_sibling_if_paired_over_cap(MAR, ET, 75))
check(len(cancels) == 1 and cancels[0][0] == KES and cancels[0][1] == "kes1", "cancel-on-fill: MAR@75 cancels KES bid@37")
check(kp.entry_order_id == "", "KES entry_order_id cleared after cancel")
# E — no cancel when pair under cap (MAR @40, KES resting @45 = 85)
cancels.clear(); s.positions = {KES: mk(KES, ET, entry_price=45, oid="kes2", entry_qty=0)}
asyncio.run(s._cancel_sibling_if_paired_over_cap(MAR, ET, 40))
check(len(cancels) == 0, "no cancel when 85<=99")
# F — no cancel if sibling already filled (race lost, nothing to cancel)
cancels.clear(); s.positions = {KES: mk(KES, ET, entry_price=37, oid="kes3", entry_qty=5)}
asyncio.run(s._cancel_sibling_if_paired_over_cap(MAR, ET, 75))
check(len(cancels) == 0, "no cancel when sibling already filled (entry_qty>0)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
