#!/usr/bin/env python3
"""T58 circuit-breaker test — automated hard-stop on a mis-anchor runaway.

Validates _v4_cap_ok():
  (1) disabled (both caps 0/absent) -> always ok, byte-identical to pre-cap.
  (2) max_concurrent_positions: blocks the (cap+1)th OPEN; allows below.
  (3) max_session_capital: blocks when committed + new_cost exceeds the cap;
      resting (unfilled, entry_qty=0) legs count at posted size.
  (4) settled positions are excluded from the counts.
  (5) read-only: never mutates self.positions (existing positions untouched).

Run: cd arb-executor && python3 tests/test_t58_cap.py
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


def bot(maxpos=0, maxcap=0.0, entry_size=5):
    s = types.SimpleNamespace()
    s.positions = {}
    s.entry_size = entry_size
    s.max_concurrent_positions = maxpos
    s.max_session_capital = maxcap
    s._v4_cap_ok = types.MethodType(M.LiveV3._v4_cap_ok, s)
    return s


def pos(price, qty=5, settled=False):
    return types.SimpleNamespace(entry_price=price, entry_qty=qty, settled=settled)


# (1) disabled -> always ok regardless of how many positions are held
s = bot(0, 0.0)
for i in range(500):
    s.positions["T%d" % i] = pos(60)
ok, reason, _ = s._v4_cap_ok(60)
check(ok and reason is None, "both caps disabled -> ok even with 500 open (byte-identical)")

# (2) max_concurrent_positions
s = bot(maxpos=3)
s.positions = {"A": pos(50), "B": pos(50)}        # 2 open
ok, reason, _ = s._v4_cap_ok(50)
check(ok, "2 open, cap 3 -> 3rd entry allowed")
s.positions["C"] = pos(50)                         # now 3 open
ok, reason, det = s._v4_cap_ok(50)
check(not ok and reason == "max_concurrent_positions" and det["open"] == 3,
      "3 open, cap 3 -> 4th entry BLOCKED (v4_cap_hit max_concurrent_positions)")

# (3) max_session_capital — committed + new_cost > cap
# 5 contracts @ 60c = $3.00/leg. cap $10 -> 3 legs ($9) ok, 4th ($12) blocked.
s = bot(maxcap=10.0)
s.positions = {"A": pos(60), "B": pos(60), "C": pos(60)}  # committed $9.00
ok, reason, det = s._v4_cap_ok(60)                          # +$3 -> $12 > $10
check(not ok and reason == "max_session_capital", "committed $9 + $3 > $10 cap -> BLOCKED")
s.positions = {"A": pos(60)}                                # committed $3.00
ok, reason, _ = s._v4_cap_ok(60)                            # +$3 -> $6 <= $10
check(ok, "committed $3 + $3 <= $10 cap -> allowed")

# resting (unfilled) leg counts at posted size (entry_qty=0 -> entry_size)
s = bot(maxcap=10.0, entry_size=5)
s.positions = {"R1": pos(60, qty=0), "R2": pos(60, qty=0)}  # 2 resting legs @ posted 5 = $6.00
ok, reason, det = s._v4_cap_ok(60)                          # +$3 -> $9 <= $10 ok
check(ok, "resting legs counted at posted size: $6 + $3 <= $10 -> allowed")
s.positions["R3"] = pos(60, qty=0)                          # $9.00 committed
ok, reason, _ = s._v4_cap_ok(60)                            # +$3 -> $12 > $10
check(not ok and reason == "max_session_capital", "3 resting legs ($9) + $3 > $10 -> BLOCKED")

# (4) settled positions excluded
s = bot(maxpos=3)
s.positions = {"A": pos(50), "B": pos(50), "C": pos(50, settled=True)}  # 2 active, 1 settled
ok, reason, det = s._v4_cap_ok(50)
check(ok and det == {}, "settled position excluded -> 2 active, cap 3, entry allowed")

# (5) read-only: positions dict unchanged after the check
s = bot(maxpos=1, maxcap=5.0)
s.positions = {"A": pos(99), "B": pos(99)}
before = dict(s.positions)
s._v4_cap_ok(99)
check(s.positions == before and len(s.positions) == 2, "cap check is read-only (positions untouched)")

# realistic tonight config: 90 / $350, 16 adopted -> wave runs
s = bot(maxpos=90, maxcap=350.0)
for i in range(16):
    s.positions["ADOPT%d" % i] = pos(55)  # ~$2.75 each = $44 committed
ok, reason, _ = s._v4_cap_ok(55)
check(ok, "tonight's 90/$350 with 16 adopted -> new wave entry allowed (real headroom)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
