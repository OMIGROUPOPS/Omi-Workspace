#!/usr/bin/env python3
"""Fix-3 (reprice-maker-only) regression: a significant-move reprice NEVER crosses as taker.
_reprice_target must ALWAYS return post_only=True, clamping a marketable target to one below the
ask. Also a source guard: the reprice section of _v4_manage_resting_inner must contain no
post_only=False / cross_on_move / marketable_taker. The T-20m fallback stays the only taker entry.
Run: cd arb-executor && python3 tests/test_t59_reprice_maker_only.py"""
import sys, types, re
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

s = types.SimpleNamespace()
s._reprice_target = types.MethodType(M.LiveV3._reprice_target, s)

# 1. marketable reprice (new_target >= ask) -> clamp to ask-1, NEVER cross
price, po = s._reprice_target(60, 58)
check(po is True, "marketable (target 60 >= ask 58): post_only TRUE (no cross)")
check(price == 57, "marketable: clamped to ask-1 = 57 (one below ask)")
price, po = s._reprice_target(58, 58)
check(po is True and price == 57, "target == ask (58/58): clamp to 57, maker")

# 2. non-marketable reprice -> target unchanged, still maker
price, po = s._reprice_target(50, 58)
check(po is True and price == 50, "non-marketable (50 < ask 58): unchanged 50, post_only TRUE")

# 3. edge: ask = 1 -> max(1, 0) = 1 (never below 1)
price, po = s._reprice_target(5, 1)
check(po is True and price == 1, "ask=1 edge: clamp floor to 1, maker")

# 4. INVARIANT: post_only is True for EVERY (target, ask) combination
allmaker = all(s._reprice_target(t, a)[1] is True for t in range(1, 100) for a in range(1, 100))
check(allmaker, "INVARIANT: _reprice_target post_only==True for all target x ask (never a taker cross)")
# and the clamped price is always strictly below ask when it was marketable
below = all((lambda p: p < a or t < a)(s._reprice_target(t, a)[0]) for t in range(1, 100) for a in range(2, 100))
check(below, "INVARIANT: reprice price never >= ask when clamped (rests, cannot cross)")

# 5. SOURCE GUARD: the reprice section must not reintroduce a taker cross
src = (REPO / "live_v4.py").read_text(errors="replace")
inner = src.split("async def _v4_manage_resting_inner", 1)[1].split("async def ", 1)[0]
reprice = inner.split("Significant-move re-post", 1)[1]   # from the reprice comment onward
check("post_only=False" not in reprice, "reprice section: no post_only=False")
check("cross_on_move" not in reprice, "reprice section: no cross_on_move tag")
check("marketable_taker" not in reprice, "reprice section: no marketable_taker tag")
check("_reprice_target(" in reprice, "reprice section: uses _reprice_target() helper")

# 6. the T-20m fallback (sanctioned taker) is unchanged -- still crosses post_only=False
check("post_only=False" in inner, "T-20m fallback path still present (the only sanctioned taker cross)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
