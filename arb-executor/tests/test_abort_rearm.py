#!/usr/bin/env python3
"""[C-ABORT-REARM Fix A] regression test for the gated, re-armable sliding-window staircase abort.
No import (AST-extract the REAL method + module constants, matching the staircase-test harness).
  DYNAMIC -- exec the real _staircase_abort_rearm_eval on a stub and assert: trips on a broad breach,
             does NOT trip on a thin <K-event sample, and RE-ARMS after recent fills recover.
  STATIC  -- assert default-OFF, the gate precedes (and short-circuits to) the legacy cumulative latch
             which is left INTACT (byte-identical when OFF), and the dbf1809 reached-its-match guard
             is untouched. Run from arb-executor."""
import ast, textwrap, os, re
from collections import deque
src = open(os.environ.get("LV4", "live_v4.py")).read()
ns = {"deque": deque}
for m in re.finditer(r"^(STAIRCASE_[A-Z_]+\s*=\s*.+)$", src, re.M):
    exec(m.group(1), ns)
tree = ast.parse(src)
meth = next(n for n in ast.walk(tree)
           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "_staircase_abort_rearm_eval")
exec(textwrap.dedent(ast.get_source_segment(src, meth)), ns)
fn = ns["_staircase_abort_rearm_eval"]

class Stub:
    def __init__(s): s.staircase_window = {}; s.staircase_aborted = {}; s.logs = []
    def _log(s, e, p): s.logs.append((e, p))
def feed(st, outcome, depth, ev, cat="WTA_MAIN"): fn(st, cat, outcome, depth, ev)

fails = []
def chk(n, c): print("  %s: %s" % (n, "PASS" if c else "FAIL")); (None if c else fails.append(n))

print("(DYNAMIC) real extracted _staircase_abort_rearm_eval  [WINDOW=%d MIN_RESOLVED=%d MIN_EVENTS=%d WTA bar fr=%.3f d=%.2f]"
      % (ns["STAIRCASE_ABORT_WINDOW"], ns["STAIRCASE_MIN_RESOLVED"], ns["STAIRCASE_ABORT_MIN_EVENTS"],
         ns["STAIRCASE_ABORT_FILLRATE"]["WTA_MAIN"], ns["STAIRCASE_ABORT_DEPTH"]["WTA_MAIN"]))

# (A) broad breach: 10 cancels across 6 distinct events -> trips
st = Stub()
for i in range(10): feed(st, "cancel", 0, "EV%d" % (i % 6))
chk("(A) trips: n>=10, >=5 events, fill_rate 0 + depth 0 below bars", st.staircase_aborted["WTA_MAIN"] is True)

# (B) <K events: 10 cancels from only 2 events -> does NOT trip (the Yuan thin-morning guard)
st = Stub()
for i in range(10): feed(st, "cancel", 0, "EV%d" % (i % 2))
chk("(B) NO trip with <5 distinct events (>=K-events guard)", st.staircase_aborted["WTA_MAIN"] is False)

# (C) RE-ARM: trip, then recent fills recover -> flips back to False (latch is NOT permanent)
st = Stub()
for i in range(10): feed(st, "cancel", 0, "EV%d" % (i % 6))
tripped = st.staircase_aborted["WTA_MAIN"]
for i in range(20): feed(st, "fill", 5, "FV%d" % (i % 6))
chk("(C) RE-ARMS after window recovers (tripped first=%s, then cleared)" % tripped,
    tripped is True and st.staircase_aborted["WTA_MAIN"] is False)

# (D) below MIN_RESOLVED never trips
st = Stub()
for i in range(9): feed(st, "cancel", 0, "EV%d" % i)
chk("(D) no trip below STAIRCASE_MIN_RESOLVED", st.staircase_aborted.get("WTA_MAIN", False) is False)

# (E) re-arm event logged on state change
st = Stub()
for i in range(10): feed(st, "cancel", 0, "EV%d" % (i % 6))
for i in range(20): feed(st, "fill", 5, "FV%d" % (i % 6))
states = [p["state"] for e, p in st.logs if e == "staircase_abort_rearm"]
chk("(E) logs ABORT then REARM on transitions", states[:1] == ["ABORT"] and "REARM" in states)

print("(STATIC) gating + byte-identical-when-OFF")
chk("(S1) config flag default OFF",
    'self.staircase_abort_rearm = self.config.get("staircase_abort_rearm", False)' in src)
chk("(S2) gated branch + helper call present",
    'if self.staircase_abort_rearm:' in src and
    'self._staircase_abort_rearm_eval(_cat, outcome, depth, pos.event_ticker)' in src)
i_gate = src.index('if self.staircase_abort_rearm:')
i_cum  = src.index('if self.staircase_aborted.get(_cat, False) or _res < STAIRCASE_MIN_RESOLVED:')
chk("(S3) gate PRECEDES legacy cumulative latch (OFF -> falls through unchanged)", i_gate < i_cum)
chk("(S4) legacy cumulative latch INTACT (byte-identical when OFF)",
    'self.staircase_aborted[_cat] = True' in src and 'if mean_depth < _dbar and fill_rate < _frbar:' in src and
    '"action": "ABORT -- staircase depth+fill below bars; halting new entries (THIS cat only)"' in src)
chk("(S5) dbf1809 reached-its-match guard UNTOUCHED",
    '_counts = (not _walk_step) and _live and (not pos.staircase_counted)' in src)
chk("(S6) bid/routing/exit/meter not referenced by the new helper (latch-only)",
    all(x not in textwrap.dedent(ast.get_source_segment(src, meth))
        for x in ["staircase_anchor", "_is_match_live", "ORDER", "reference_source", "regime_lookup"]))

print("\nRESULT:", "ALL PASS" if not fails else "FAILED: " + ", ".join(fails))
raise SystemExit(1 if fails else 0)
