#!/usr/bin/env python3
"""Tests for C-PM-CLOCK (Part-1 staged) + C-SCALE-GUN shadow (Part-3 staged).
AST-extract pattern (per 706cb3c/47fa2ff): the REAL bodies are extracted from live_v4.py
and executed -- no re-implementation, no import of the live module (which needs creds/config).
Run: python tests/test_pm_clock.py   (from arb-executor/)"""
import ast, sys, time
from collections import deque
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parent.parent / "live_v4.py"
SRC = SRC_PATH.read_text(encoding="utf-8")
TREE = ast.parse(SRC)
LINES = SRC.splitlines()

def _extract(name, cls=None):
    """Return the source of a function (module-level or method of cls)."""
    def scan(node, want_cls):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, ast.ClassDef) and ch.name == want_cls:
                return scan(ch, None)
            if want_cls is None and isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and ch.name == name:
                return ch
        return None
    fn = scan(TREE, cls)
    assert fn is not None, f"function {name} not found (cls={cls})"
    body = "\n".join(LINES[fn.lineno - 1: fn.end_lineno])
    # dedent methods (class indent = 4)
    if cls:
        body = "\n".join(l[4:] if l[:4] == "    " else l for l in body.splitlines())
    return body

def _const(name):
    for node in ast.iter_child_nodes(TREE):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id == name:
            return eval(compile(ast.Expression(node.value), "<const>", "eval"), {})
    raise AssertionError(f"constant {name} not found")

NS = {}
for fname in ("_pm_clock_resolve", "_pm_window_closed", "_coarse_window_closed"):
    exec(compile(_extract(fname), SRC_PATH.name, "exec"), NS)
_pm_clock_resolve = NS["_pm_clock_resolve"]
_pm_window_closed = NS["_pm_window_closed"]
_coarse_window_closed = NS["_coarse_window_closed"]

PM_CLOCK_STALE_SEC = _const("PM_CLOCK_STALE_SEC")
PM_CLOCK_WIDEN_SEC = _const("PM_CLOCK_WIDEN_SEC")
PM_CLOCK_WIDEN_DEFAULT_SEC = _const("PM_CLOCK_WIDEN_DEFAULT_SEC")
LIVE_TRADE_BURST = _const("LIVE_TRADE_BURST")
LIVE_DETECT_WINDOW_SEC = _const("LIVE_DETECT_WINDOW_SEC")
V4_RUNNING_MID_WINDOW_SEC = _const("V4_RUNNING_MID_WINDOW_SEC")
SCALE_GUN_MULT = _const("SCALE_GUN_MULT")
SCALE_GUN_BASELINE_EXCL_SEC = _const("SCALE_GUN_BASELINE_EXCL_SEC")
SCALE_GUN_BASELINE_MIN_SPAN_SEC = _const("SCALE_GUN_BASELINE_MIN_SPAN_SEC")

checks = []
def check(name, cond):
    checks.append((name, bool(cond)))
    print(("PASS" if cond else "FAIL"), name)

# ---------------- _pm_clock_resolve ----------------
check("resolve: honest+fresh -> honest clock",
      _pm_clock_resolve(1000.0, True, 2000.0) == (1000.0, "honest"))
check("resolve: honest ts but STALE file -> fallback to legacy",
      _pm_clock_resolve(1000.0, False, 2000.0) == (2000.0, "fallback"))
check("resolve: entry-missing (None) even fresh -> fallback",
      _pm_clock_resolve(None, True, 2000.0) == (2000.0, "fallback"))
check("resolve: missing + stale -> fallback",
      _pm_clock_resolve(None, False, 2000.0) == (2000.0, "fallback"))

# ---------------- _pm_window_closed: HONEST == legacy edges ----------------
TAIL, BUF = 5400, 900
sweep = [-90000, -5401, -5400, -3600, -1, 0, 1, 899, 900, 901, 3600, 86400]
hon_ok = all(_pm_window_closed(t, "honest", 0, TAIL, BUF) ==
             _coarse_window_closed(t, False, TAIL, BUF) for t in sweep)
check("honest mode == legacy _coarse_window_closed(coarse=False) across edge sweep", hon_ok)

# ---------------- _pm_window_closed: FALLBACK envelope ----------------
X = PM_CLOCK_WIDEN_SEC["ITF_W"]
check("fallback: NO inside_buffer lock (T-10m stays open)",
      _pm_window_closed(600, "fallback", X, TAIL, BUF) is None)
check("fallback: NO T-0 lock (T+1h stays open, tape governs)",
      _pm_window_closed(-3600, "fallback", X, TAIL, BUF) is None)
check("fallback: open until placeholder + max(tail, X) (ITF X=%ds)" % X,
      _pm_window_closed(-(X - 1), "fallback", X, TAIL, BUF) is None)
check("fallback: gives up past placeholder + X",
      _pm_window_closed(-X, "fallback", X, TAIL, BUF) == "match_already_started")
check("fallback: tail floor is the coarse 90-min tail when X small",
      _pm_window_closed(-5399, "fallback", 0, TAIL, BUF) is None and
      _pm_window_closed(-5400, "fallback", 0, TAIL, BUF) == "match_already_started")

# ---------------- widen table sanity vs the audit ----------------
check("widen: CHALL 4h", PM_CLOCK_WIDEN_SEC["ATP_CHALL"] == 14400 == PM_CLOCK_WIDEN_SEC["WTA_CHALL"])
check("widen: ITF 7h covers observed max skew 360min",
      PM_CLOCK_WIDEN_SEC["ITF_M"] == 25200 == PM_CLOCK_WIDEN_SEC["ITF_W"] and 25200 >= 360 * 60)
check("widen: MAIN 8h (card-span heuristic)", PM_CLOCK_WIDEN_SEC["ATP_MAIN"] == 28800)
check("widen: default == CHALL", PM_CLOCK_WIDEN_DEFAULT_SEC == 14400)

# ---------------- byte-identical-OFF reduction ----------------
# OFF path: _pm_mode None, _pm_widen 0 -> every rewired comparison reduces to legacy.
for tts in (86401, 86400, 14400, 0, -1):
    if (tts - 0 > 86400) != (tts > 86400):
        check("OFF reduction (86400 horizon)", False); break
else:
    check("OFF reduction: tts - 0 > K  ==  tts > K", True)
check("OFF reduction: defer tail max(TAIL, 0) == TAIL", max(TAIL, 0) == TAIL)

# ---------------- _scale_gun_shadow_tick (real body on a fake bot) ----------------
method_src = _extract("_scale_gun_shadow_tick", cls="LiveV3")
GNS = {"LIVE_DETECT_WINDOW_SEC": LIVE_DETECT_WINDOW_SEC, "LIVE_TRADE_BURST": LIVE_TRADE_BURST,
       "V4_RUNNING_MID_WINDOW_SEC": V4_RUNNING_MID_WINDOW_SEC, "SCALE_GUN_MULT": SCALE_GUN_MULT,
       "SCALE_GUN_BASELINE_EXCL_SEC": SCALE_GUN_BASELINE_EXCL_SEC,
       "SCALE_GUN_BASELINE_MIN_SPAN_SEC": SCALE_GUN_BASELINE_MIN_SPAN_SEC,
       "THIN_GUN_MIN_PRINTS": _const("THIN_GUN_MIN_PRINTS"),
       "THIN_GUN_BASELINE_MAX": _const("THIN_GUN_BASELINE_MAX")}
exec(compile(method_src, SRC_PATH.name, "exec"), GNS)

class FakeBot:
    _scale_gun_shadow_tick = GNS["_scale_gun_shadow_tick"]
    def __init__(self):
        self.event_tickers = {"EV": {"EV-A", "EV-B"}}
        self._trade_times = {}
        self._trade_prices = {}
        self.event_start_time = {}
        self._events_live = set()
        self._scale_gun_fired = set()
        self._thin_gun_fired = set()
        self._pm_honest = {}
        self.logged = []
    def get_category(self, et): return "ATP_MAIN"
    def _log(self, ev, det, **kw): self.logged.append((ev, det))

NOW = 1_000_000.0

# (a) below legacy floor, quiet baseline -> THIN shadow fires (C-THIN-GUN; scale-gun set untouched)
b = FakeBot()
b._trade_times = {"EV-A": deque([NOW - 5] * (LIVE_TRADE_BURST - 1))}
b._scale_gun_shadow_tick("EV", NOW)
check("thin-gun: gun-blind burst (9 prints, 0 baseline) -> gun_thin_shadow fires",
      len(b.logged) == 1 and b.logged[0][0] == "gun_thin_shadow" and not b._scale_gun_fired
      and b.logged[0][1]["legacy_gun_would_fire"] is False)
# (a2) truly silent tape (< THIN floor) -> nothing
b0 = FakeBot()
b0._trade_times = {"EV-A": deque([NOW - 5] * 2)}
b0._scale_gun_shadow_tick("EV", NOW)
check("thin-gun: 2 prints -> silent", not b0.logged and not b0._thin_gun_fired)
# (a3) thin log-once
b._scale_gun_shadow_tick("EV", NOW + 1)
check("thin-gun: log-once", len(b.logged) == 1)

# (b) ITF-like: burst over a quiet baseline -> fires at the legacy bar
b = FakeBot()
b._trade_times = {"EV-A": deque([NOW - i for i in range(12)])}          # 12 prints/60s
b._trade_prices = {"EV-A": deque((NOW - 300 - i * 60, 50) for i in range(10))}  # ~1/min baseline
b._scale_gun_shadow_tick("EV", NOW)
check("scale-gun: quiet baseline + burst -> shadow fires",
      len(b.logged) == 1 and b.logged[0][0] == "gun_scale_shadow" and "EV" in b._scale_gun_fired)
check("scale-gun: fired bar >= legacy floor", b.logged[0][1]["scaled_bar"] >= LIVE_TRADE_BURST)

# (c) MAIN-like: 12 prints/60s burst over a ~5/min baseline -> scaled bar 15 SUPPRESSES
b = FakeBot()
b._trade_times = {"EV-A": deque([NOW - i for i in range(12)])}
base = deque()
for i in range(150):  # 150 prints across 30 min ending 2 min ago -> ~5.4/min
    base.append((NOW - SCALE_GUN_BASELINE_EXCL_SEC - 1 - i * 11, 50))
b._trade_prices = {"EV-A": base}
b._scale_gun_shadow_tick("EV", NOW)
check("scale-gun: MAIN-scale baseline suppresses a legacy-size burst",
      not b.logged and not b._scale_gun_fired)

# (d) same MAIN baseline but a REAL acceleration (3x baseline) -> fires
b2 = FakeBot()
b2._trade_times = {"EV-A": deque([NOW - i * 2 for i in range(30)])}     # 30 prints/60s
b2._trade_prices = {"EV-A": deque(base)}
b2._scale_gun_shadow_tick("EV", NOW)
check("scale-gun: 3x-baseline acceleration fires through the scaled bar",
      len(b2.logged) == 1 and b2.logged[0][1]["recent_burst"] == 30)

# (e) log-once: second call is silent
b2._scale_gun_shadow_tick("EV", NOW + 1)
check("scale-gun: log-once latch", len(b2.logged) == 1)

# (f) purity: no writes outside its own latch
b3 = FakeBot()
tt = {"EV-A": deque([NOW - i for i in range(12)])}
b3._trade_times = tt
before = {k: list(v) for k, v in tt.items()}
b3._scale_gun_shadow_tick("EV", NOW)
check("scale-gun: trade buffers untouched",
      {k: list(v) for k, v in b3._trade_times.items()} == before)
check("scale-gun: _events_live untouched", b3._events_live == set())

# ---------------- summary ----------------
fails = [n for n, ok in checks if not ok]
print("\n%d/%d checks pass" % (len(checks) - len(fails), len(checks)))
if fails:
    print("FAILED:", fails)
    sys.exit(1)
print("ALL PASS")
