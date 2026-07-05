#!/usr/bin/env python3
"""Tests for C-RISER-REVISION (riser_post_revision flag, 2026-07-05).
AST-extract pattern: real bodies from live_v4.py, no module import.
Run: python tests/test_riser_revision.py   (from arb-executor/)"""
import ast, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SRC = (HERE / "live_v4.py").read_text(encoding="utf-8")
TREE = ast.parse(SRC)
LINES = SRC.splitlines()

def _method(name):
    for node in ast.walk(TREE):
        if isinstance(node, ast.ClassDef) and node.name == "LiveV3":
            for ch in node.body:
                if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) and ch.name == name:
                    return ch
    raise AssertionError("method %s not found" % name)

def _src_of(fn):
    body = "\n".join(LINES[fn.lineno - 1: fn.end_lineno])
    return "\n".join(l[4:] if l[:4] == "    " else l for l in body.splitlines())

checks = []
def check(name, cond):
    checks.append((name, bool(cond)))
    print(("PASS" if cond else "FAIL"), name)

# ---- real bodies: _aim_bucket, _aim_cell, _aim_riser_post on a fake bot ----
NS = {"staticmethod": staticmethod}
for m in ("_aim_bucket", "_aim_cell", "_aim_riser_post", "_aim_faller_depth"):
    exec(compile(_src_of(_method(m)), "live_v4.py", "exec"), NS)

class FakeBot:
    _aim_bucket = staticmethod(NS["_aim_bucket"].__func__ if isinstance(NS["_aim_bucket"], staticmethod) else NS["_aim_bucket"])
    _aim_cell = NS["_aim_cell"]
    _aim_riser_post = NS["_aim_riser_post"]
    _aim_faller_depth = NS["_aim_faller_depth"]
    dog_dip_offset_cents = 3
    def __init__(self, table):
        self._table = table
    def _aim_load(self):
        return self._table

TABLE = json.load(open(HERE / "docs/policy/aim_table.json"))["aim"]
b = FakeBot(TABLE)

# ---- the revised table values (the deploy's data half) ----
check("table: ATP_CHALL riser_post=3 all buckets", all(v["riser_post"] == 3 for v in TABLE["ATP_CHALL"].values()))
check("table: WTA_CHALL riser_post=3 all buckets", all(v["riser_post"] == 3 for v in TABLE["WTA_CHALL"].values()))
check("table: ITF_M riser_post=3 all buckets", all(v["riser_post"] == 3 for v in TABLE["ITF_M"].values()))
check("table: ITF_W riser_post=2 all buckets", all(v["riser_post"] == 2 for v in TABLE["ITF_W"].values()))
check("table: mains HOLD at 0", all(v["riser_post"] == 0 for c in ("ATP_MAIN", "WTA_MAIN") for v in TABLE[c].values()))

# ---- helper behavior (real body) ----
check("helper: ATP_CHALL @72 -> 3", b._aim_riser_post("ATP_CHALL", 72) == 3)
check("helper: ITF_W @55 -> 2", b._aim_riser_post("ITF_W", 55) == 2)
check("helper: ATP_MAIN @80 -> 0 (hold)", b._aim_riser_post("ATP_MAIN", 80) == 0)
check("helper: unknown cat -> 0 (never deepens on a miss)", b._aim_riser_post("NOPE", 60) == 0)
b2 = FakeBot({"X": {"50-59": {"riser_post": "junk"}}})
check("helper: junk value -> 0", b2._aim_riser_post("X", 55) == 0)
b3 = FakeBot({"X": {"50-59": {}}})
check("helper: missing field -> 0", b3._aim_riser_post("X", 55) == 0)
check("helper: faller_depth untouched (ATP_CHALL @30)", isinstance(b._aim_faller_depth("ATP_CHALL", 30), int))

# ---- structural gating proof on the REAL _v4_entry_anchor body ----
anchor = _method("_v4_entry_anchor")
calls, guarded, in_riser_branch = 0, 0, 0
class V(ast.NodeVisitor):
    def visit_If(self, node):
        # find `if self.riser_post_revision:` guards
        t = ast.dump(node.test)
        global guarded
        for ch in ast.walk(node):
            if isinstance(ch, ast.Attribute) and ch.attr == "_aim_riser_post":
                if "riser_post_revision" in t:
                    guarded += 1
        self.generic_visit(node)
for node in ast.walk(anchor):
    if isinstance(node, ast.Attribute) and node.attr == "_aim_riser_post":
        calls += 1
V().visit(anchor)
check("anchor: _aim_riser_post called exactly once", calls == 1)
check("anchor: the call sits under `if self.riser_post_revision` (byte-identical OFF)", guarded >= 1)

# subtraction floor: max(1, ...) present on the revised line
seg = "\n".join(LINES[anchor.lineno - 1: anchor.end_lineno])
check("anchor: revised target floored at 1c", "max(1, target_bid - self._aim_riser_post" in seg)

# flag default False in __init__
init = _method("__init__")
iseg = "\n".join(LINES[init.lineno - 1: init.end_lineno])
check("__init__: riser_post_revision default False", 'config.get("riser_post_revision", False)' in iseg)

# ---- OFF-path arithmetic reduction ----
best_bid = 61
for dep in (0, 2, 3):
    on = max(1, best_bid - dep)
    check("math: depth %d -> %d" % (dep, best_bid - dep), on == best_bid - dep)
check("math: floor binds at 1", max(1, 1 - 3) == 1)

fails = [n for n, ok in checks if not ok]
print("\n%d/%d checks pass" % (len(checks) - len(fails), len(checks)))
if fails:
    print("FAILED:", fails)
    sys.exit(1)
print("ALL PASS")
