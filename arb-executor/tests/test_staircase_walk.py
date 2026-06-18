#!/usr/bin/env python3
"""[C-STAIRCASE SHIP-2 full-walk] NEW tests: walk-trajectory (monotone + held-step), recast-
immutability (target moves only on knot cross, never on mid), restart round-trip.
Extracts _frac2 + _staircase_target from the live source via AST (no module import).
Run: cd arb-executor && LV4=/tmp/live_v4_ship2full.py python3 tests/test_staircase_walk.py"""
import ast, textwrap, json, os
import pandas as pd
POL="docs/policy"
src=open(os.environ.get("LV4","live_v4.py")).read()
def grab(name):
    return next(ast.get_source_segment(src,n) for n in ast.walk(ast.parse(src))
               if isinstance(n,ast.FunctionDef) and n.name==name)
ns={}; exec(textwrap.dedent(grab("_frac2")),ns); exec(textwrap.dedent(grab("_staircase_target")),ns)
SCH=json.load(open(f"{POL}/range_final_walk_schedule.json"))
class Sh: pass
sh=Sh(); sh._walk_knots=SCH["knots_min_before_start"]; sh._walk_fracs=SCH["depth_fraction_at_knot"]
frac2=lambda t: ns["_frac2"](sh,t)
sct=lambda a,D,ask: ns["_staircase_target"](sh,a,D,ask)
deep={int(r.c):int(r.final_target) for r in pd.read_csv(f"{POL}/range_final_ATP_MAIN.csv").itertuples()}
def D(ft,t): return max(1,int(round(1+(ft-1)*frac2(t))))
KN=SCH["knots_min_before_start"]
fails=[]

# ---- (1) WALK TRAJECTORY: D monotone non-increasing as t->0 ----
print("(1) walk trajectory monotone + held-step")
ts_desc=[240,225,210,195,180,165,150,135,120,105,90,75,60,45,30,20,10,5,1,0]
mono_ok=True; varied=0
for c,ft in deep.items():
    seq=[D(ft,t) for t in ts_desc]
    if any(seq[i+1]>seq[i] for i in range(len(seq)-1)): mono_ok=False; fails.append(("mono",c,seq))
    if len(set(seq))>1: varied+=1
print(f"    monotone non-increasing (t 240->0) for ALL {len(deep)} cells: {'PASS' if mono_ok else 'FAIL'}; cells with varying D: {varied}")

# ---- (1b) HELD-STEP: D CONSTANT within each knot interval (catch linear-interp) ----
# intervals defined by frac2 = frac at smallest knot >= t. pick two interior t per interval.
intervals=[(210,240),(180,210),(150,180),(120,150),(90,120),(60,90),(30,60),(10,30)]  # (lo,hi]: t in (lo,hi]
held_ok=True; ft7=max(deep,key=lambda c:deep[c]); FT=deep[ft7]
for lo,hi in intervals:
    t1=lo+0.5*(hi-lo); t2=lo+0.9*(hi-lo)   # two distinct interior points (NOT knot-aligned)
    if frac2(t1)!=frac2(t2) or D(FT,t1)!=D(FT,t2):
        held_ok=False; fails.append(("held",lo,hi,frac2(t1),frac2(t2),D(FT,t1),D(FT,t2)))
print(f"    held-step D constant within each knot interval (cell {ft7}, ft={FT}): {'PASS' if held_ok else 'FAIL'}")
# explicit linear-interp catch: a linear interp would give D(195)!=D(205) in (180,210]; held-step gives equal
li1,li2=D(FT,195),D(FT,205)
print(f"    linear-interp catch: D(195)={li1} D(205)={li2} (same interval) {'PASS (held)' if li1==li2 else 'FAIL (interp!)'}")
if li1!=li2: fails.append(("interp",li1,li2))

# ---- (2) RECAST IMMUTABILITY: target moves ONLY on knot cross, NEVER on mid ----
print("(2) recast immutability")
anchor=60; ft=deep.get(60,7)
# fixed t, vary mid (best_ask high so never-cross non-binding) -> target constant
t_fixed=120.0; Dt=D(ft,t_fixed)
targets_vs_mid={sct(anchor,Dt,ask)[0] for ask in range(anchor+2, anchor+40)}
mid_ok = len(targets_vs_mid)==1 and targets_vs_mid=={anchor-Dt}
print(f"    fixed t=120, mid (ask) varied {anchor+2}..{anchor+39}: target set={targets_vs_mid} {'PASS (immutable to mid)' if mid_ok else 'FAIL'}")
if not mid_ok: fails.append(("mid_immut",targets_vs_mid))
# crossing a knot DOES move the target (180->210 boundary): D differs -> target differs
tgt_a=sct(anchor,D(ft,179),100)[0]; tgt_b=sct(anchor,D(ft,181),100)[0]   # 179 in(150,180], 181 in(180,210]
cross_ok = tgt_a != tgt_b
print(f"    knot cross t=179 vs 181: target {tgt_a} -> {tgt_b} {'PASS (moves on cross)' if cross_ok else 'FAIL'}")
if not cross_ok: fails.append(("cross",tgt_a,tgt_b))

# ---- (3) RESTART ROUND-TRIP: save->load preserves anchor/cell/ref; restored leg recomputes same target ----
print("(3) restart round-trip")
# simulate save (sparse) + load (int(d.get(...))) of the 3 fields, per the scratch's serialization
pos_like={"reference_source":"staircase","staircase_anchor":60,"staircase_cell":60,"staircase_ref":56}
saved={k:pos_like[k] for k in ("staircase_anchor","staircase_cell","staircase_ref")} if pos_like["reference_source"]=="staircase" else {}
loaded={k:int(saved.get(k,0)) for k in ("staircase_anchor","staircase_cell","staircase_ref")}
rt_ok = loaded=={"staircase_anchor":60,"staircase_cell":60,"staircase_ref":56}
print(f"    save->load fields: {loaded} {'PASS' if rt_ok else 'FAIL'}")
if not rt_ok: fails.append(("rt",loaded))
# restored leg recomputes SAME target as pre-save (same anchor/cell/t)
t=120.0
pre = sct(60, D(deep[60],t), 100)[0]
post= sct(loaded["staircase_anchor"], D(deep[loaded["staircase_cell"]],t), 100)[0]
print(f"    recompute pre={pre} post-restore={post} {'PASS (identical)' if pre==post else 'FAIL'}")
if pre!=post: fails.append(("rt_recompute",pre,post))
# structural: scratch actually wires save + load for the 3 fields
for needle in ['out[tk]["staircase_anchor"]','staircase_anchor=int(d.get("staircase_anchor"']:
    ok = needle in src
    print(f"    scratch wires: {needle[:40]}... {'PASS' if ok else 'FAIL'}")
    if not ok: fails.append(("wire",needle))

print("\nRESULT:", "ALL PASS" if not fails else f"FAILURES {len(fails)}: {fails[:8]}")
assert not fails
