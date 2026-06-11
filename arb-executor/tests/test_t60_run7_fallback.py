#!/usr/bin/env python3
"""RUN-7 regression: (1) the T-20m fallback is MAKER-ONLY when fallback_maker_clamp is on (no
post_only=False / no taker cross on that path) — ask-1 clamp via _fallback_order; gate-off keeps the
taker cross byte-identical. (2) the cancel-on-marketable exemption is FALLBACK-SCOPED (only the
ask-1 fallback bid is exempt; a normal drifted-marketable bid is still cancelled; degenerate always
cancels). Run: cd arb-executor && python3 tests/test_t60_run7_fallback.py"""
import sys, types
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

def ns(clamp, com=True, buf=1):
    # [test-hygiene 2026-06-11] Stage-1 (a313b6fb) made _fallback_order read
    # maker_only_entry; False preserves the original RUN-7 assertions (clamp
    # behavior driven purely by fallback_maker_clamp as this suite sweeps it).
    s = types.SimpleNamespace(fallback_maker_clamp=clamp, cancel_on_marketable=com, cancel_marketable_buffer=buf,
                              maker_only_entry=False)
    s._reprice_target = types.MethodType(M.LiveV3._reprice_target, s)
    s._fallback_order = types.MethodType(M.LiveV3._fallback_order, s)
    s._resting_cancel_reason = types.MethodType(M.LiveV3._resting_cancel_reason, s)
    return s

# ---- (1) _fallback_order: maker-only when clamp on ----
off = ns(clamp=False)
check(off._fallback_order(58) == (58, False), "gate OFF: fallback = taker cross at ask (58, post_only False) [byte-identical]")
on = ns(clamp=True)
check(on._fallback_order(58) == (57, True), "gate ON: fallback = ask-1 MAKER (57, post_only True)")
check(on._fallback_order(1) == (1, True), "gate ON: ask=1 edge -> (1, True) [max(1, ask-1)]")
# INVARIANT: gate ON never returns a taker cross, always one below ask
allmaker = all(on._fallback_order(a)[1] is True for a in range(1, 100))
check(allmaker, "INVARIANT: gate ON post_only==True for every ask (NO taker cross on the fallback path)")
belowask = all(on._fallback_order(a)[0] < a or a <= 1 for a in range(1, 100))
check(belowask, "INVARIANT: gate ON price is below the ask (rests, cannot cross)")

# ---- (2) cancel-on-marketable exemption, FALLBACK-SCOPED ----
def decide(s, target, bid, ask, entry_mode):
    sc, cr = s._resting_cancel_reason(target, bid, ask)
    if sc and cr == "bid_marketable_stale" and entry_mode == "fallback_maker":   # the call-site override
        sc, cr = False, None
    return sc, cr
s = ns(clamp=True)
# ask-1 fallback bid, marketable (target 57 vs ask 58, buffer 1) -> EXEMPT
check(decide(s, 57, 55, 58, "fallback_maker") == (False, None), "exemption: fallback_maker marketable bid -> NOT cancelled (intentional ask-1)")
# a NORMAL drifted-marketable bid -> still cancelled (no blanket disable / no reintroduced pick-off)
sc, cr = decide(s, 57, 55, 58, "resting_maker")
check(sc is True and cr == "bid_marketable_stale", "exemption SCOPED: normal resting bid drifts marketable -> STILL cancelled")
# degenerate book -> still cancelled even for the fallback bid
sc, cr = decide(s, 57, 0, 58, "fallback_maker")
check(sc is True and cr == "degenerate", "exemption SCOPED: degenerate book still cancels the fallback bid")
# fallback bid resting safely below the ask -> no cancel anyway
check(decide(s, 40, 38, 58, "fallback_maker") == (False, None), "fallback bid safely below ask -> rests")

# ---- (3) source guards ----
src = (REPO / "live_v4.py").read_text(errors="replace")
inner = src.split("async def _v4_manage_resting_inner", 1)[1].split("\n    async def ", 1)[0]
fb = inner.split("T-20m taker fallback (STEP 6)", 1)[1]
check("post_only=fb_post_only" in fb, "fallback place uses post_only=fb_post_only (gated, not a literal)")
check("self._fallback_order(book.best_ask)" in fb, "fallback uses _fallback_order helper")
check('entry_mode in ("fallback_maker", "marketable_clamp")' in inner,
      "cancel-on-marketable exemption is scoped to the two intentional ask-1 clamp modes (fallback_maker + marketable_clamp), not blanket")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
