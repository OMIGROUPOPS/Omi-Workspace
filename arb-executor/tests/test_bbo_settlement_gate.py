#!/usr/bin/env python3
"""Regression: the BBO-threshold settlement heuristic (check_settlements) must NOT be a settlement
source / must NOT cancel a resting exit when `disable_bbo_threshold_settlement` is ON. A price
touching best_bid>=98 or best_ask<=2 mid-match round-trips and is NOT settlement -- settling on it
calls process_settlement which cancels the resting exit (settlement_cleanup) early. Real settlement
(ws_lifecycle / rest_poll -> process_settlement) is unchanged.

Drives the REAL check_settlements (bound via MethodType) with a stub process_settlement that records
calls, so we assert the actual gate behavior -- not a mirror.
Run: cd arb-executor && python3 tests/test_bbo_settlement_gate.py"""
import sys, types
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

M._PAPER_API = None   # force the LIVE branch (the one that cancels real exits)

def book(bid, ask): return types.SimpleNamespace(best_bid=bid, best_ask=ask)
def pos():           return types.SimpleNamespace(settled=False, phase="active")

def run(disable, bid, ask):
    """Run the real check_settlements with one active position; return list of process_settlement calls."""
    calls = []
    s = types.SimpleNamespace(
        disable_bbo_threshold_settlement=disable,
        books={"TK": book(bid, ask)},
        positions={"TK": pos()},
        process_settlement=lambda tk, val, ts, source: calls.append((tk, val, source)),
    )
    types.MethodType(M.LiveV3.check_settlements, s)()
    return calls

# ---- gate OFF (default) = byte-identical: BBO heuristic still settles ----
c = run(False, 1, 1)   # best_ask<=2 -> bbo_threshold_no
check(c == [("TK", 0, "bbo_threshold_no")], "OFF: best_ask<=2 -> process_settlement(bbo_threshold_no) [byte-identical]")
c = run(False, 99, 99) # best_bid>=98 -> bbo_threshold_yes
check(c == [("TK", 100, "bbo_threshold_yes")], "OFF: best_bid>=98 -> process_settlement(bbo_threshold_yes) [byte-identical]")
c = run(False, 50, 52) # normal book -> no settlement
check(c == [], "OFF: normal book -> no settlement (unchanged)")

# ---- gate ON = the FIX: BBO heuristic NEVER settles / never cancels the exit ----
c = run(True, 1, 1)
check(c == [], "ON: mid-match price spike to ask<=2 -> NO process_settlement (resting exit untouched)")
c = run(True, 99, 99)
check(c == [], "ON: mid-match price spike to bid>=98 -> NO process_settlement (resting exit untouched)")
c = run(True, 2, 0)
check(c == [], "ON: extreme book (ask=0) -> still NO settlement (heuristic is dead)")
c = run(True, 50, 52)
check(c == [], "ON: normal book -> no settlement")

# INVARIANT: with the gate ON, NO book state produces a settlement call (the heuristic touches nothing)
inv = all(run(True, b, a) == [] for b in range(0, 101) for a in range(0, 101))
check(inv, "INVARIANT ON: no (bid, ask) state triggers process_settlement -> BBO can never cancel an exit")

# ---- real settlement path is UNTOUCHED (process_settlement still cancels the exit on a real fill/settle) ----
src = (REPO / "live_v4.py").read_text(encoding="utf-8", errors="ignore")
check('source="ws_lifecycle"' in src and 'source="rest_poll"' in src,
      "ws_lifecycle + rest_poll still call process_settlement (real settlement unchanged)")
check('cancel_order(ticker, pos.exit_order_id, "settlement_cleanup")' in src,
      "process_settlement still cleans up the exit on REAL settlement (cancel path intact)")
# the gate lives ONLY in check_settlements, not in the real-settlement callers
check('if self.disable_bbo_threshold_settlement:\n            return' in src,
      "gate is an early-return in check_settlements only (ws/rest callers do not reference the flag)")

print(f"\n{'ALL PASS' if fails == 0 else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
