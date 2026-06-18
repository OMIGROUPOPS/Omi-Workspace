#!/usr/bin/env python3
"""[C-STAIRCASE SHIP-2] GATE 3 -- held-between-knots parity. Asserts the live caller's depth D
equals the sim's D at NON-knot-aligned t (catches held-step bugs that knot-aligned tests miss),
explicitly incl. Plex's 5 boundary t: 150.0, 149.999, 150.001, 30.0, 9.999. Extracts _frac2 from
the live source via AST (no module import). Run: cd arb-executor && python3 tests/test_staircase_ship2.py
(set LV4=/tmp/live_v4_ship2.py to test the scratch; default 'live_v4.py')."""
import ast, textwrap, json, os
import pandas as pd
POL = "docs/policy"
SRCFILE = os.environ.get("LV4", "live_v4.py")
src = open(SRCFILE).read()
fsrc = next(ast.get_source_segment(src, n) for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.FunctionDef) and n.name == "_frac2")
ns = {}; exec(textwrap.dedent(fsrc), ns)
SCH = json.load(open(f"{POL}/range_final_walk_schedule.json"))
class _Shim: pass
sh = _Shim(); sh._walk_knots = SCH["knots_min_before_start"]; sh._walk_fracs = SCH["depth_fraction_at_knot"]
caller_frac2 = lambda t: ns["_frac2"](sh, t)

# sim frac2 -- independent, byte-for-byte abort_validation.py:20-22
KN, FR = SCH["knots_min_before_start"], SCH["depth_fraction_at_knot"]
def sim_frac2(t):
    c=[(k,f) for k,f in zip(KN,FR) if k>=t]; return min(c,key=lambda x:x[0])[1] if c else 0.0
deep = {int(r.c): int(r.final_target) for r in pd.read_csv(f"{POL}/range_final_ATP_MAIN.csv").itertuples()}
caller_D = lambda ft,t: max(1, int(round(1 + (ft-1)*caller_frac2(t))))
sim_D    = lambda ft,t: max(1, int(round(1 + (ft-1)*sim_frac2(t))))

fails = []
# (i) held-step frac2 VALUES at the 5 Plex boundaries (direct held-step assertion)
EXP = {150.0:0.625, 149.999:0.625, 150.001:0.750, 30.0:0.125, 9.999:0.0}
print("(i) held-step frac2 at boundaries:")
for t, e in EXP.items():
    got = caller_frac2(t); ok = abs(got-e) < 1e-12
    print(f"    frac2({t:>8}) = {got:<5} expect {e:<5} {'PASS' if ok else 'FAIL'}")
    if not ok: fails.append(("frac2", t, got, e))

# (ii) caller_D == sim_D across 90 cells x {5 boundaries + 9 knots + non-aligned}
TS = [150.0,149.999,150.001,30.0,9.999] + KN + \
     [239.5,200.0,175.0,124.9,90.001,59.999,45.0,29.999,10.001,5.0,1.0,0.0]
n = 0; mism = 0
for c, ft in deep.items():
    for t in TS:
        n += 1
        if caller_D(ft,t) != sim_D(ft,t): mism += 1; fails.append((c,ft,t,caller_D(ft,t),sim_D(ft,t)))
print(f"(ii) held-between-knots parity: {len(deep)} cells x {len(TS)} t = {n} cases, mismatches={mism}")

# (iii) the existing 810 knot-aligned cases still pass
k = sum(1 for c,ft in deep.items() for t in KN if caller_D(ft,t)==sim_D(ft,t))
print(f"(iii) 810 knot-aligned: {k}/{len(deep)*len(KN)} pass")

print("\nRESULT:", "ALL PASS" if not fails else f"FAILURES {len(fails)}: {fails[:8]}")
assert not fails, "GATE 3 FAILED"
