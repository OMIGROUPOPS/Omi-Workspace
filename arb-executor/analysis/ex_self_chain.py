#!/usr/bin/env python3
"""THE ONE CHAIN — [C-EX-SELF fork-killer, rider 2026-07-07].
`book_ex_self` is the ONLY non-self chain math any component may consume:
live_v4._book_ex_self (runtime object wrapper — equivalence-asserted in
tests/test_ex_self.py), the spread census/recount engines, the validation
harnesses, and any future monitor posture grading ALL call or mirror THIS
function. The self-inclusive book survives only as the raw feed beneath it.
Grep symbol: book_ex_self / _book_ex_self — the prior-art gate catches any
future divergence on this name."""


def book_ex_self(levels, own_px=None, own_qty=0.0):
    """Best bid NET of our own resting order.
    levels: iterable of (px:int, size:float) bid levels, any order.
    own_px/own_qty: our resting bid (one entry order per ticker by construction).
    A level emptied by our size (residual <= 0.01) falls through to the next
    real level. Asks are never touched (we rest bids only). Returns int px or None."""
    try:
        lv = sorted(((int(p), float(s)) for p, s in levels if s and int(p) > 0),
                    reverse=True)
    except Exception:
        return None
    for px, sz in lv:
        adj = sz - (float(own_qty) if (own_px is not None and int(own_px) == px) else 0.0)
        if adj > 0.01:
            return px
    return None


def express_target(target, bid_ex_self):
    """[PLEX expression invariant] expressed = target if target <= bid_ex+1
    else bid_ex+1 (join-or-improve the MARKET's chain, never our reflection)."""
    if target is None or bid_ex_self is None or target <= bid_ex_self + 1:
        return target
    return bid_ex_self + 1
