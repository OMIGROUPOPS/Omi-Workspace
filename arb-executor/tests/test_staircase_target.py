#!/usr/bin/env python3
"""[C-STAIRCASE SHIP-1] Parity + boundary test for _staircase_target.
Run: cd arb-executor && python3 tests/test_staircase_target.py
Extracts the EXACT _staircase_target source from the committed live_v4.py via AST and
execs it standalone (no module import -> no fv.py/IO side effects). Live tree untouched."""
import ast, textwrap, json
import numpy as np, pandas as pd
POL = "docs/policy"

# ---- extract the exact proposed function, exec standalone ----
src = open("live_v4.py").read()
fsrc = None
for node in ast.walk(ast.parse(src)):
    if isinstance(node, ast.FunctionDef) and node.name == "_staircase_target":
        fsrc = ast.get_source_segment(src, node); break
assert fsrc, "could not locate _staircase_target in scratch"
ns = {}; exec(textwrap.dedent(fsrc), ns)
_impl = ns["_staircase_target"]
def st(anchor, offset, ask): return _impl(None, anchor, offset, ask)  # method ignores self

# ---- sim parity inputs (identical to abort_validation.py) ----
SCH = json.load(open(f"{POL}/range_final_walk_schedule.json"))
KN, FR = SCH["knots_min_before_start"], SCH["depth_fraction_at_knot"]
def frac2(t):
    c = [(k,f) for k,f in zip(KN,FR) if k>=t]
    return min(c, key=lambda x:x[0])[1] if c else 0.0
deep = {int(r.c): int(r.final_target) for r in pd.read_csv(f"{POL}/range_final_ATP_MAIN.csv").itertuples()}
def D_validation(cell, t):                       # == abort_validation.py:58
    return max(1, int(round(1 + (deep[cell]-1)*frac2(t))))

fails = []; passed = 0
# ---- (a) 810-case sim parity: 90 cells x 9 knots ----
cells = sorted(deep); assert len(cells)==90, f"expected 90 cells, got {len(cells)}"
for c in cells:
    for t in KN:
        Dv = D_validation(c, t)                   # pre-rounded python int
        got, want = st(c, Dv, 100), (c - Dv, True)   # ask=100 -> never-cross slack
        if got == want: passed += 1
        else: fails.append((c,t,Dv,got,want))
n_parity = len(cells)*len(KN)
print(f"(a) SIM-PARITY 90 cells x 9 knots = {n_parity}: passed {passed}/{n_parity}")

# ---- file-identity cross-check: CSV D@T vs sim D (FLAG knot mismatch) ----
csv = pd.read_csv(f"{POL}/range_final_ATP_MAIN.csv")
csv_knots = [int(col.split("-")[1]) for col in csv.columns if col.startswith("D@T-")]
overlap = sorted(set(csv_knots) & set(KN), reverse=True)
mism = sum(1 for _,r in csv.iterrows() for t in overlap if int(r[f"D@T-{t}"]) != D_validation(int(r.c), t))
print(f"    CSV-vs-sim file-identity @ overlap {overlap}: mismatches={mism}/{90*len(overlap)}")
print(f"    *** FLAG (Ship-2): CSV D@T knots {sorted(csv_knots,reverse=True)} != schedule {sorted(KN,reverse=True)}")
print(f"        schedule-only {sorted(set(KN)-set(csv_knots),reverse=True)} | CSV-only {sorted(set(csv_knots)-set(KN),reverse=True)}")

# ---- (b) boundary cases ----
B=[]
def chk(name,got,want): B.append((name,got,want,got==want));
chk("offset=0 -> anchor-1       ", st(50,0,100), (49,True))
chk("ncross n/b: a50 o3 ask50   ", st(50,3,50), (47,True))
chk("ncross @eq: a50 o3 ask48   ", st(50,3,48), (47,True))
chk("ncross BIND: a50 o1 ask49  ", st(50,1,49), (48,True))
chk("anchor=1 degenerate -> 1   ", st(1,1,100), (1,True))
chk("negative offset -> >=1     ", st(50,-5,100), (49,True))
chk("overflow offset -> >=1     ", st(50,10**9,100), (1,True))
for name,got,want,ok in B:
    print(f"(b) {name} got={got} want={want} {'PASS' if ok else 'FAIL'}")
    if not ok: fails.append((name,got,want))
def raises(off):
    try: st(50,off,100); return False
    except AssertionError: return True
for label,off in [("float 3.5", 3.5), ("numpy.int64(3)", np.int64(3))]:
    r=raises(off); print(f"(b) clean-raise on {label}: {'PASS (AssertionError)' if r else 'FAIL'}")
    if not r: fails.append(("raise",label))

print("\n==== RESULT ====")
print(f"ALL PASS: {n_parity} parity + {len(B)+2} boundary/raise" if (not fails and passed==n_parity)
      else f"FAILURES: {len(fails)} -> " + str(fails[:20]))
