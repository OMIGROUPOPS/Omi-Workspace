#!/usr/bin/env python3
"""T50+T52 on the Challenger fat-spread path — the captured Shick/Hohmann failure.

Root cause of the old open paired book (operator dx 2026-06-01): on thin Challenger
books the maker bid never fills (no flow), so the taker fallback fires and crosses
the FAT spread on BOTH legs; ask+ask > 100 because the wide spread IS the overround.
Shick ask 82 + Hohmann ask 24 = 106 -> bought a binary pair for 106 that settles at
100 -> -6c locked before the match matters. The -2 to -4% bleed across these pairs.

This pins that the NEW config structurally CANNOT reproduce a both-legs->=100
Challenger pair, and that the guards are category-agnostic (fire on Challenger, not
just main-draw):
  T52 (_taker_spread_ok) refuses to cross a fat spread -> never lifts the wide ask.
  T50 (_paired_basis_ok) refuses the 2nd leg when leg1 + leg2 > V4_PAIRED_BASIS_CAP.
Either guard alone breaks the 106 pair; together they're belt-and-suspenders.

Therefore any both-legs->=100 Challenger pair observed tomorrow is, by definition,
OLD config (settling out, excluded from new-strategy P&L).

Run: cd arb-executor && python3 tests/test_t50_t52_challenger_fatspread.py
"""
import sys, types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m)
    fails += (0 if c else 1)

# The captured ATP Challenger pair.
ET = "KXATPCHALLENGERMATCH-26JUN01SHIHOH"
SHI = ET + "-SHI"; HOH = ET + "-HOH"

s = types.SimpleNamespace(_log=lambda *a, **k: None)
s.event_tickers = {ET: {SHI, HOH}}
s.positions = {}
s.books = {}
for nm in ("_sibling_ticker", "_paired_basis_ok", "_taker_spread_ok"):
    setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
pos = lambda price: types.SimpleNamespace(entry_price=price, settled=False)
bk = lambda b, a: types.SimpleNamespace(best_ask=a, best_bid=b)

print("V4_PAIRED_BASIS_CAP =", M.V4_PAIRED_BASIS_CAP, " MAX_TAKER_SPREAD =", M.MAX_TAKER_SPREAD)

# ---- T52: fat Challenger spreads block the taker cross (the wide ask is never lifted) ----
check(s._taker_spread_ok(75, 82) is False, "T52: Shick bid75/ask82 (spread 7) -> cross BLOCKED")
check(s._taker_spread_ok(16, 24) is False, "T52: Hohmann bid16/ask24 (spread 8) -> cross BLOCKED")
check(s._taker_spread_ok(58, 60) is True,  "T52: tight challenger spread 2 -> cross allowed (no over-block)")

# ---- T50: paired-basis refuses the 2nd leg; 82 + 24 = 106 > 99 ----
# (a) sibling HELD as a position at its old cross price 82 -> Hohmann@24 refused
s.positions = {SHI: pos(82)}
check(s._paired_basis_ok(HOH, ET, 24) is False, "T50: Shick held@82 + Hohmann@24 = 106 > 99 -> 2nd leg REFUSED")
# symmetric
s.positions = {HOH: pos(24)}
check(s._paired_basis_ok(SHI, ET, 82) is False, "T50: Hohmann held@24 + Shick@82 = 106 -> REFUSED (symmetric)")
# (b) sibling NOT held -> guard uses the sibling's current book ask (the level we'd pay)
s.positions = {}
s.books = {SHI: bk(75, 82)}
check(s._paired_basis_ok(HOH, ET, 24) is False, "T50: sibling book ask 82 + 24 = 106 -> REFUSED (pre-fill)")
# (c) a SAFE challenger pair is allowed -> no over-block
s.positions = {SHI: pos(60)}
check(s._paired_basis_ok(HOH, ET, 38) is True, "T50: 60 + 38 = 98 <= 99 -> safe pair allowed")

# ---- the joint claim: the 106 pair cannot be created ----
# leg1 cross blocked by T52 (fat spread) AND leg2 refused by T50 (sum>cap) -> impossible
s.positions = {SHI: pos(82)}
joint_blocked = (s._taker_spread_ok(16, 24) is False) and (s._paired_basis_ok(HOH, ET, 24) is False)
check(joint_blocked, "JOINT: both-legs->=100 Challenger pair structurally impossible under new config")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
