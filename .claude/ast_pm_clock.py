#!/usr/bin/env python3
"""AST sweep for C-PM-CLOCK / C-SCALE-GUN staging: compare worktree live_v4.py vs git HEAD.
Lists every function/method whose AST differs, every added/removed def, and greps the
forbidden zone (liveness/abandon) for any new clock token. Expected differs are declared
below; exit 1 on any surprise."""
import ast, subprocess, sys, io

EXPECTED_CHANGED = {
    "LiveV3.__init__",                     # flags + caches
    "LiveV3._apply_schedule_data",         # _sched_fetched_epoch stamp (attribute set only)
    "LiveV3.discover_markets",             # _pm_resolve_honest hook (flag-gated)
    "LiveV3._route_event",                 # shadow log + windowing rewire + scale-gun hook
}
EXPECTED_ADDED = {
    "_pm_clock_resolve", "_pm_window_closed",          # module-level pure helpers
    "LiveV3._pm_resolve_honest", "LiveV3._scale_gun_shadow_tick",
}
# Tape-supremacy zone: ZERO change tolerated.
FORBIDDEN_UNCHANGED = {
    "LiveV3._is_match_live", "LiveV3._sustained_flow_live", "LiveV3._sustained_flow_windows",
    "LiveV3._fv_burst_ready", "LiveV3._coarse_window_closed", "_coarse_window_closed",
    "LiveV3._maybe_set_window_open", "LiveV3._completion_target", "LiveV3._reconcile_event_start",
    "LiveV3._match_event_pure", "LiveV3._match_event_to_schedule_async",
}

def index_funcs(src):
    tree = ast.parse(src)
    out = {}
    def walk(node, prefix=""):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out[prefix + ch.name] = ast.dump(ch)
                walk(ch, prefix + ch.name + ".")
            elif isinstance(ch, ast.ClassDef):
                walk(ch, ch.name + ".")
            else:
                walk(ch, prefix)
    walk(tree)
    return out

new_src = open("live_v4.py", encoding="utf-8").read()
old_src = subprocess.run(["git", "show", "HEAD:arb-executor/live_v4.py"],
                         capture_output=True, text=True, encoding="utf-8").stdout
old, new = index_funcs(old_src), index_funcs(new_src)

changed = sorted(k for k in old.keys() & new.keys() if old[k] != new[k])
added   = sorted(new.keys() - old.keys())
removed = sorted(old.keys() - new.keys())

print("CHANGED:", changed)
print("ADDED:  ", added)
print("REMOVED:", removed)

ok = True
if set(changed) != EXPECTED_CHANGED:
    print("!! CHANGED set mismatch. unexpected:", sorted(set(changed) - EXPECTED_CHANGED),
          "missing:", sorted(EXPECTED_CHANGED - set(changed))); ok = False
if set(added) != EXPECTED_ADDED:
    print("!! ADDED set mismatch. unexpected:", sorted(set(added) - EXPECTED_ADDED),
          "missing:", sorted(EXPECTED_ADDED - set(added))); ok = False
if removed:
    print("!! REMOVED functions:", removed); ok = False

for f in FORBIDDEN_UNCHANGED:
    if f in old and f in new and old[f] != new[f]:
        print("!! FORBIDDEN ZONE CHANGED:", f); ok = False

# grep-proof: no pm/scale token inside the liveness/abandon bodies
tree = ast.parse(new_src)
BAD_TOKENS = ("_pm_", "per_match_clock", "PM_CLOCK", "scale_gun", "SCALE_GUN")
GUARD_FUNCS = ("_is_match_live", "_sustained_flow_live", "_sustained_flow_windows",
               "_fv_burst_ready", "_max_ref_move")
lines = new_src.splitlines()
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in GUARD_FUNCS:
        body = "\n".join(lines[node.lineno - 1: node.end_lineno])
        for t in BAD_TOKENS:
            if t in body:
                print(f"!! grep-proof FAIL: token {t!r} inside {node.name}"); ok = False

print("AST SWEEP:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
