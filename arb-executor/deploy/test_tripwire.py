#!/usr/bin/env python3
"""Micro-test: drive LiveV3._log unbound with a stub -> tripwire must fire at the
threshold, emit CRITICAL_error_rate_tripwire once, honor re-arm, and call
_request_shutdown only when error_tripwire_halt."""
import io, sys, types, importlib.util
from collections import deque
from pathlib import Path

spec = importlib.util.spec_from_file_location("lv4", Path(__file__).resolve().parent.parent / "live_v4.py")
lv4 = importlib.util.module_from_spec(spec)
# do NOT exec the module (needs pem etc.) -- just compile and pull the class def out
src = (Path(__file__).resolve().parent.parent / "live_v4.py").read_text(encoding="utf-8")
import ast
tree = ast.parse(src)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "LiveV3")
fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_log")
mod = ast.Module(body=[fn], type_ignores=[])
ns = {}
import json, time
from datetime import datetime, timezone, timedelta
ns.update({"json": json, "time": time, "datetime": datetime,
           "ET": timezone(timedelta(hours=-4))})
exec(compile(mod, "lv4_log", "exec"), ns)
_log = ns["_log"]

class Stub:
    def __init__(self, halt):
        self.log_file = io.StringIO()
        self._err_tripwire_ts = deque()
        self._err_tripwire_last = 0.0
        self.error_tripwire_threshold = 20
        self.error_tripwire_window_sec = 600
        self.error_tripwire_halt = halt
        self.halted = []
        self.critical = 0
    def _request_shutdown(self, name): self.halted.append(name)
    def _log(self, event, details=None, ticker=""):
        if event == "CRITICAL_error_rate_tripwire": self.critical += 1
        return _log(self, event, details, ticker)

for halt in (False, True):
    s = Stub(halt)
    for i in range(25):
        s._log("error", {"error": "TypeError: boom %d" % i})
    assert s.critical == 1, f"CRITICAL fired {s.critical}x (want 1, halt={halt})"
    assert len(s._err_tripwire_ts) >= 20
    if halt:
        assert s.halted == ["ERROR_TRIPWIRE"], s.halted
    else:
        assert s.halted == [], s.halted
    # benign events never touch the deque
    n = len(s._err_tripwire_ts)
    s._log("order_placed", {"x": 1})
    assert len(s._err_tripwire_ts) == n
print("TRIPWIRE MICRO-TEST: PASS (alert-only + halt modes, single-fire, re-arm window)")
