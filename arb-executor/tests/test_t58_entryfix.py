#!/usr/bin/env python3
"""T58 entry-fix levers regression: lever-3 cancel-on-marketable (A) vs legacy wide-spread,
lever-2 fallback timing config. Validates the surgical cancel change kills the churn (bid
resting safely below a wide book is NOT cancelled) while keeping the pick-off protection
(degenerate + marketable still cancel). Run: cd arb-executor && python3 tests/test_t58_entryfix.py"""
import sys, types
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

def ns(marketable_mode, buf=1):
    s = types.SimpleNamespace(cancel_on_marketable=marketable_mode, cancel_marketable_buffer=buf)
    s._resting_cancel_reason = types.MethodType(M.LiveV3._resting_cancel_reason, s)
    return s

# ---- (A) cancel_on_marketable: the churn fix ----
a = ns(True, 1)
# bid resting SAFELY BELOW a wide book -> NOT cancelled (the fix; legacy would cancel on spread 4)
c, r = a._resting_cancel_reason(40, 44, 48)
check(c is False, "A: bid 40 below wide book (bid44/ask48, spread4) -> REST (not cancelled) [churn fix]")
# bid gone marketable (within 1c of ask) -> cancel
c, r = a._resting_cancel_reason(47, 45, 48)
check(c is True and r == "bid_marketable_stale", "A: bid 47 vs ask 48 (within buffer 1) -> cancel marketable")
c, r = a._resting_cancel_reason(48, 45, 48)
check(c is True and r == "bid_marketable_stale", "A: bid 48 >= ask 48 (crossed) -> cancel marketable")
# degenerate book -> cancel
c, r = a._resting_cancel_reason(40, 0, 48)
check(c is True and r == "degenerate", "A: bid<=0 (degenerate) -> cancel")
c, r = a._resting_cancel_reason(40, 44, 100)
check(c is True and r == "degenerate", "A: ask>=100 (degenerate) -> cancel")
# tight book, bid below -> rest
c, r = a._resting_cancel_reason(40, 49, 51)
check(c is False, "A: bid 40 below tight book -> rest")

# ---- legacy (cancel_on_marketable off) ----
g = ns(False)
c, r = g._resting_cancel_reason(40, 44, 48)
check(c is True and r == "degenerate_or_wide_spread", "legacy: spread 4 (>2) -> cancel (the over-cancel proxy)")
c, r = g._resting_cancel_reason(40, 49, 51)
check(c is False, "legacy: spread 2 (==2) -> no cancel")
c, r = g._resting_cancel_reason(40, 44, 100)
check(c is True, "legacy: degenerate -> cancel")

# ---- buffer = 0 (only fully-crossed) ----
b0 = ns(True, 0)
c, r = b0._resting_cancel_reason(47, 45, 48)
check(c is False, "buffer0: bid 47 < ask 48 -> rest (only fully-crossed cancels)")
c, r = b0._resting_cancel_reason(48, 45, 48)
check(c is True, "buffer0: bid 48 >= ask 48 -> cancel")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
