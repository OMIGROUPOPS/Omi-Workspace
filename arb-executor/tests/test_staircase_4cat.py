#!/usr/bin/env python3
"""[C-STAIRCASE 4CAT] per-cat loading + gate-fires-for-all-4. Extracts _staircase_bid/_frac2/
_staircase_target/_join_target via AST; loads the 4 range_final CSVs as _load_staircase does; confirms
the inner gate (_staircase_bid) fires the STAIRCASE path for ALL 4 cats with per-cat final_target, and
falls back to join for an unknown cat. Run from arb-executor."""
import ast, textwrap, json, os
import pandas as pd
POL="docs/policy"
src=open(os.environ.get("LV4","live_v4.py")).read()
def grab(name): return next(ast.get_source_segment(src,n) for n in ast.walk(ast.parse(src)) if isinstance(n,ast.FunctionDef) and n.name==name)
ns={}
for fn in ("_frac2","_staircase_target","_join_target","_staircase_bid"): exec(textwrap.dedent(grab(fn)),ns)
SCH=json.load(open(f"{POL}/range_final_walk_schedule.json"))
fails=[]
def chk(name,cond): print(f"  {name}: {'PASS' if cond else 'FAIL'}"); (None if cond else fails.append(name))

# (1) all 4 range_final load -> 90 cells each, 5..94
print("(1) per-cat range_final load (mirrors _load_staircase)")
RF={}
for cat in ("ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL"):
    d={int(r.c):int(r.final_target) for r in pd.read_csv(f"{POL}/range_final_{cat}.csv").itertuples()}
    RF[cat]=d
    chk(f"  {cat}: {len(d)} cells [{min(d)}..{max(d)}]", len(d)==90 and min(d)==5 and max(d)==94)

# (2) _staircase_bid gate FIRES the staircase path for ALL 4 cats (not the join fallback), per-cat ft
print("(2) gate fires per-cat (staircase target, not join fallback)")
class Sh: pass
sh=Sh(); sh._walk_knots=SCH["knots_min_before_start"]; sh._walk_fracs=SCH["depth_fraction_at_knot"]; sh._range_final=RF
sh._frac2=ns["_frac2"].__get__(sh); sh._staircase_target=ns["_staircase_target"].__get__(sh); sh._join_target=ns["_join_target"].__get__(sh)
bid=ns["_staircase_bid"].__get__(sh)
# t=240min (time_to_start passed in SECONDS; _staircase_bid divides /60) -> frac2(240)=1.0 -> D=max(1,ft)
for cat in ("ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL"):
    cell=40; anchor=40; ft=RF[cat][cell]
    expD=max(1,int(round(1+(ft-1)*1.0)))               # frac2(240)=1.0 -> D=ft
    tgt,po=bid(cat,cell,anchor,240*60,35,45)            # best_bid=35,best_ask=45 (join would be 35)
    chk(f"  {cat} cell40 ft={ft}: target={tgt}==anchor-D({anchor-expD}) (join would be 35)", tgt==anchor-expD and po is True)

# (3) unknown cat -> join fallback (proves the gate keys on the per-cat dict, not a hardcoded cat)
print("(3) unknown cat -> join fallback")
jt,_=sh._join_target(35,45)
tgt,_=bid("NOT_A_CAT",40,40,240*60,35,45)
chk(f"  unknown cat -> join fallback ({jt})", tgt==jt)

print("\nRESULT:", "ALL PASS" if not fails else f"FAILURES {fails}")
assert not fails
