#!/usr/bin/env python3
"""RUN-7 regression: the universal anti-degenerate entry guard must SKIP only genuinely crossed
books (bid > ask, a real book artifact) and true degenerates (bid <= 0, or ask >= 100), and must
ALLOW a LOCKED book (bid == ask) through to placement -- a lock is a tight, fully-priced two-sided
market, not degenerate. The pre-fix `>=` collapsed locked books into the skip and discarded ~22
investable entries/day (Challengers + a Roland Garros main-draw, KXWTAMATCH-26JUN04KOSAND 43/43).

Two layers: (1) source-pin -- the production guard at the degenerate-skip site uses `> book.best_ask`
and NOT `>=` (catches a silent regression of the exact one-char fix); (2) truth-table of the guard
predicate (mirrored from that line, trust established by layer 1).
Run: cd arb-executor && python3 tests/test_run7_locked_book.py"""
import re, sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

# ---- Layer 1: source-pin the production guard (no silent revert to >=) ----
src = (REPO / "live_v4.py").read_text(encoding="utf-8", errors="ignore")
m = re.search(r'if book\.best_bid <= 0 or book\.best_ask >= 100 or book\.best_bid (>=?) book\.best_ask:'
              r'\s*\n\s*self\._log\("skipped", \{"reason": "degenerate_book_skip"', src)
check(m is not None, "degenerate_book_skip guard located in live_v4.py")
if m:
    check(m.group(1) == ">", "guard uses CROSSED-only `book.best_bid > book.best_ask` (NOT `>=`)")

# ---- Layer 2: predicate truth-table (mirror of the pinned production line) ----
# skip == genuinely-not-investable. Mirrors: bid<=0 or ask>=100 or bid>ask
def skips(bid, ask):
    return bid <= 0 or ask >= 100 or bid > ask

check(skips(51, 50) is True,  "CROSSED (bid 51 > ask 50) -> SKIP (real artifact)")
check(skips(50, 50) is False, "LOCKED  (bid 50 == ask 50) -> PLACE (tight two-sided market, the fix)")
check(skips(43, 43) is False, "LOCKED  Roland Garros main-draw case (43/43) -> PLACE")
check(skips(49, 51) is False, "NORMAL  (bid 49 < ask 51) -> PLACE")
check(skips(0, 50)  is True,  "DEGENERATE no-bid (bid 0) -> SKIP")
check(skips(-1, 50) is True,  "DEGENERATE neg bid -> SKIP")
check(skips(50, 100) is True, "DEGENERATE ask pinned 100 -> SKIP")
check(skips(50, 101) is True, "DEGENERATE ask > 100 -> SKIP")

# byte-identical on every non-locked book: fixed `>` and legacy `>=` agree unless bid==ask
def skips_legacy(bid, ask):
    return bid <= 0 or ask >= 100 or bid >= ask
diffs = [(b, a) for b in range(0, 101) for a in range(0, 101)
         if skips(b, a) != skips_legacy(b, a)]
check(all(b == a for b, a in diffs),
      "fix differs from legacy ONLY on locked books (bid==ask); byte-identical elsewhere")
check(len(diffs) > 0, "the fix actually changes locked-book behavior (non-empty diff set)")

print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
