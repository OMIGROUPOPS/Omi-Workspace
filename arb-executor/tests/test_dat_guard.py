#!/usr/bin/env python3
"""[C-STAIRCASE SHIP-2] GATE 4 -- load-bearing guard: no D@T column references in any *.py outside
analysis/exit_charts/build_range_final.py (the sole generator). Path A forbids live callers reading
the CSV D@T columns; this fails the suite on any hit. The search token is built by concatenation so
THIS file contains no literal match. Run: cd arb-executor && python3 tests/test_dat_guard.py
(SCANCWD/SCANROOT override the scan target; default repo root / arb-executor)."""
import subprocess, os
TOK = "D@" + "T"                                  # never appears literally in this file
ALLOW = "build_range_final.py"
cwd  = os.environ.get("SCANCWD", "/root/Omi-Workspace")
root = os.environ.get("SCANROOT", "arb-executor")
r = subprocess.run(["grep", "-rn", f'"{TOK}\\|{TOK}-', root, "--include=*.py"],
                   cwd=cwd, capture_output=True, text=True)
hits = [ln for ln in r.stdout.splitlines() if ALLOW not in ln]
print(f"(GATE4) {TOK} refs outside {ALLOW}: {len(hits)}")
for h in hits: print("   ", h)
assert not hits, f"{TOK} references must be confined to {ALLOW}; found {len(hits)}"
print("RESULT: ALL PASS (only build_range_final.py may reference the column)")
