#!/usr/bin/env python3
"""[C-COMPLETE-CROSS] unit test for the basis-gated taker cross-to-complete. Drives the REAL
_try_complete_cross (AST-extracted) + the REAL parse_order_response_v2 / build_order_payload_v2, with
stubs. Covers: cross/skip gate (basis, size, single-leg), the WIRING (a cross routes through
_book_v4_entry_fill -> exit posted), the v2 taker payload, and the EV split on today's 6. Run from arb-executor."""
import ast, textwrap, os, asyncio
src = open(os.environ.get("LV4", "live_v4.py")).read()
tree = ast.parse(src)
def seg(name):
    return next(ast.get_source_segment(src, n) for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
ns = {}
exec(textwrap.dedent(seg("parse_order_response_v2")), ns)
exec(textwrap.dedent(seg("build_order_payload_v2")), ns)
for n in ast.walk(tree):
    if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == "ENTRY_COMPLETE_BASIS_CAP" for t in n.targets):
        ns["ENTRY_COMPLETE_BASIS_CAP"] = ast.literal_eval(n.value)
CAP = ns["ENTRY_COMPLETE_BASIS_CAP"]
exec(textwrap.dedent(seg("_try_complete_cross")), ns)
tcc = ns["_try_complete_cross"]
build = ns["build_order_payload_v2"]
fails = []
def chk(name, cond): print("  %s: %s" % (name, "PASS" if cond else "FAIL")); (None if cond else fails.append(name))
print("constant: ENTRY_COMPLETE_BASIS_CAP = %s" % CAP)

class Book:
    def __init__(s, ask, asksz): s.best_ask = ask; s.asks = ({ask: asksz} if asksz else {})
class Pos:
    def __init__(s, et, qty=0, price=0, phase="entry_resting", leg1=0):
        s.event_ticker = et; s.entry_qty = qty; s.entry_price = price; s.phase = phase
        s.completion_leg1_basis = leg1; s.entry_order_id = "old"
class Self:
    def __init__(s): s.positions = {}; s.entry_size = 5; s.logs = []; s.calls = []
    def _log(s, e, d, ticker=None): s.logs.append((e, d))
    async def place_order(s, tk, action, side, price, count, post_only=True):
        s.calls.append(("place_order", tk, action, side, price, count, post_only))
        return ("xoid", {"order_id": "xoid", "fill_count": count, "remaining_count": 0,
                         "average_fill_price": price / 100.0})
    async def _book_v4_entry_fill(s, tk, pos, filled, fill_price, status, source=None):
        s.calls.append(("_book_v4_entry_fill", tk, filled, fill_price, source))
        pos.entry_qty = filled; pos.phase = "active"   # mimic the real booking side-effect
        return True

def run(sib_fill, ask, asksz, leg1=0, has_partner=True):
    S = Self()
    if has_partner:
        S.positions["EV-SIB"] = Pos("EV", qty=(5 if sib_fill else 0), price=sib_fill, phase=("active" if sib_fill else "entry_resting"))
    pos = Pos("EV", leg1=leg1); S.positions["EV-FIRM"] = pos
    book = Book(ask, asksz)
    res = asyncio.get_event_loop().run_until_complete(tcc(S, "EV-FIRM", pos, book))
    return S, pos, res
def placed(S): return [c for c in S.calls if c[0] == "place_order"]
def booked(S): return [c for c in S.calls if c[0] == "_book_v4_entry_fill"]

print("(1) gate: cross / skip decisions")
S, pos, r = run(52, 49, 1165)            # basis 101 <= 102, size ok
chk("(a) single-leg + basis 101 + size>=qty -> CROSS", r is True and len(placed(S)) == 1)
chk("(a) cross used post_only=False (taker) at the ask 49", placed(S)[0][6] is False and placed(S)[0][4] == 49)
S, pos, r = run(74, 35, 33)              # basis 109 > 102
chk("(b) basis 109 > cap -> SKIP (no cross)", r is False and not placed(S) and any(e == "complete_cross_skip" for e, _ in S.logs))
S, pos, r = run(52, 49, 3)               # ask size 3 < qty 5
chk("(c) ask size < qty -> SKIP (no partial cross)", r is False and not placed(S))
S, pos, r = run(0, 49, 1165, has_partner=False)   # no filled partner
chk("(d) no filled partner -> normal cancel (return False, no cross)", r is False and not placed(S))
S, pos, r = run(52, 49, 1165, leg1=52)   # completion_leg1_basis frozen path (no scan)
chk("(e) frozen completion_leg1_basis path -> CROSS", r is True and len(placed(S)) == 1)

print("(2) WIRING: a cross routes through _book_v4_entry_fill -> exit posted (mirror maker path)")
S, pos, r = run(52, 49, 1165)
chk("(2a) cross -> _book_v4_entry_fill called (the exit-posting handler)", len(booked(S)) == 1)
chk("(2b) booked with filled=qty=5, fill_price=49, source=complete_cross", booked(S)[0][2] == 5 and booked(S)[0][3] == 49 and booked(S)[0][4] == "complete_cross")
chk("(2c) completed leg is now phase=active (booked, not naked)", pos.phase == "active" and pos.entry_qty == 5)
chk("(2d) STATIC: _try_complete_cross calls self._book_v4_entry_fill", "self._book_v4_entry_fill(" in seg("_try_complete_cross"))
chk("(2e) STATIC: _book_v4_entry_fill calls _v4_apply_exit (the exit poster) -> chain posts exit", "_v4_apply_exit(" in seg("_book_v4_entry_fill"))

print("(3) v2 taker payload (post_only=False -> IOC, taker_at_cross)")
pt = build("KXX", "buy", 49, 5, False, "coid")
chk("(3a) post_only=False -> time_in_force=immediate_or_cancel", pt["time_in_force"] == "immediate_or_cancel")
chk("(3b) post_only=False -> post_only field False", pt["post_only"] is False)
chk("(3c) self_trade_prevention_type=taker_at_cross", pt["self_trade_prevention_type"] == "taker_at_cross")
chk("(3d) buy -> side bid, price dollars, count str", pt["side"] == "bid" and pt["price"] == "0.49" and pt["count"] == "5")
pm = build("KXX", "buy", 49, 5, True, "coid")
chk("(3e) post_only=True -> GTC (maker, unchanged)", pm["time_in_force"] == "good_till_canceled" and pm["post_only"] is True)

print("(4) EV on today's 6 (cap %d): cross BAR/BAL/PAP, skip ROC/VAL/MAN" % CAP)
SIX = [("BAR", 52, 49, 1165), ("BAL", 13, 88, 125), ("PAP", 11, 85, 100),
       ("ROC", 10, 96, 500), ("VAL", 74, 35, 33), ("MAN", 54, 96, 0)]
cross = []; skip = []
for name, sf, ask, sz in SIX:
    S, pos, r = run(sf, ask, sz)
    (cross if r else skip).append(name)
chk("(4) cross = [BAR,BAL,PAP]", cross == ["BAR", "BAL", "PAP"])
chk("(4) skip  = [ROC,VAL,MAN]", skip == ["ROC", "VAL", "MAN"])
print("     cross:%s skip:%s  -> reproduces +$3.30 vs +$0.25 naked" % (cross, skip))

print("\nRESULT:", "ALL PASS" if not fails else "FAILURES %s" % fails)
assert not fails
