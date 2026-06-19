#!/usr/bin/env python3
"""[C-STAIRCASE 4CAT abort-spec] unit test for the PER-CAT _staircase_resolve AND-gate. Extracts the
method + per-cat constant DICTS from the live source via AST; shims self/pos (no import). The key new
guarantee is per-cat ISOLATION: one cat's abort must not touch another's tally or halt it. Run from arb-executor."""
import ast, textwrap, os
src=open(os.environ.get("LV4","live_v4.py")).read()
tree=ast.parse(src)
def const(name):
    for n in ast.walk(tree):
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets):
            return ast.literal_eval(n.value)
    raise KeyError(name)
MINR=const("STAIRCASE_MIN_RESOLVED"); FR=const("STAIRCASE_ABORT_FILLRATE"); DB=const("STAIRCASE_ABORT_DEPTH")
print(f"constants: MIN_RESOLVED={MINR}")
print(f"  FILLRATE bars: {FR}")
print(f"  DEPTH bars:    {DB}")
fsrc=next(ast.get_source_segment(src,n) for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=="_staircase_resolve")
ns={"STAIRCASE_MIN_RESOLVED":MINR,"STAIRCASE_ABORT_FILLRATE":FR,"STAIRCASE_ABORT_DEPTH":DB}
exec(textwrap.dedent(fsrc),ns); resolve=ns["_staircase_resolve"]
class Pos:
    def __init__(s,cat="ATP_MAIN",anchor=60,ref=58,cell=60):
        s.reference_source="staircase"; s.category=cat; s.staircase_anchor=anchor; s.staircase_ref=ref; s.staircase_cell=cell
class Self:
    def __init__(s): s.staircase_aborted={}; s.staircase_resolved={}; s.staircase_fills={}; s.staircase_depth_sum={}; s.logs=[]
    def _log(s,e,d,ticker=None): s.logs.append((e,d))
def run(seq,cat="ATP_MAIN",anchor=60,S=None):
    S=S or Self()
    for outcome,fp in seq: resolve(S,Pos(cat=cat,anchor=anchor),outcome,fp)
    return S
fails=[]
def chk(name,cond): print(f"  {name}: {'PASS' if cond else 'FAIL'}"); (None if cond else fails.append(name))

# (0) per-cat constant bars present + equal the derived values
print("(0) per-cat constant bars")
EXP_FR={"ATP_MAIN":0.623,"WTA_MAIN":0.602,"ATP_CHALL":0.621,"WTA_CHALL":0.685}
EXP_DB={"ATP_MAIN":1.44,"WTA_MAIN":1.89,"ATP_CHALL":1.88,"WTA_CHALL":1.71}
for cat in EXP_FR:
    chk(f"  {cat} FILLRATE={EXP_FR[cat]} & DEPTH={EXP_DB[cat]}", FR.get(cat)==EXP_FR[cat] and DB.get(cat)==EXP_DB[cat])

# (a-e) AND-gate behavior (ATP_MAIN bars 1.44/0.623), Ship-2 cases under the new per-cat structure
print("(a-e) AND-gate (ATP_MAIN)")
S=run([("cancel",0)]*9)
chk("(a) 9 resolved (<MIN) -> not aborted", S.staircase_aborted.get("ATP_MAIN",False) is False and S.staircase_resolved["ATP_MAIN"]==9)
S=run([("fill",59)]*5+[("cancel",0)]*5)   # depth1 (<1.44), fr0.5 (<0.623) -> BOTH bars
chk("(b) both bars -> ABORTED", S.staircase_aborted.get("ATP_MAIN") is True)
chk("(b) trial_abort logged w/ cat tag", any(e=="staircase_trial_abort" and d.get("cat")=="ATP_MAIN" for e,d in S.logs))
S=run([("fill",57)]*5+[("cancel",0)]*5)   # depth3 (>=1.44) -> one bar only
chk("(c) depth ok -> NOT aborted", S.staircase_aborted.get("ATP_MAIN",False) is False)
S=run([("fill",59)]*9+[("cancel",0)])     # fr0.9 (>=0.623) -> one bar only
chk("(c2) fill ok -> NOT aborted", S.staircase_aborted.get("ATP_MAIN",False) is False)
S=Self(); p=Pos(); p.reference_source="join_bid"; resolve(S,p,"fill",59)
chk("(d) non-staircase -> ignored", S.staircase_resolved.get("ATP_MAIN",0)==0)
S=run([("fill",59),("cancel",0)])
chk("(e) staircase_walk per resolve", sum(1 for e,_ in S.logs if e=="staircase_walk")==2)

# (f) per-cat DEPTH bar is actually USED: mean_depth 1.6 (3x depth2 + 2x depth1) trips WTA_MAIN's 1.89
#     bar but NOT ATP_MAIN's 1.44 bar -- SAME sequence, opposite outcome by cat (proves per-cat lookup).
print("(f) per-cat bars applied (mean_depth 1.6 splits WTA_MAIN 1.89 vs ATP_MAIN 1.44)")
SEQ=[("fill",58)]*3+[("fill",59)]*2+[("cancel",0)]*5   # depths 2,2,2,1,1 -> mean 1.6; fr 5/10=0.5
S=run(SEQ, cat="WTA_MAIN")
chk("(f) WTA_MAIN mean1.6<1.89 & fr0.5<0.602 -> ABORT", S.staircase_aborted.get("WTA_MAIN") is True)
S=run(SEQ, cat="ATP_MAIN")
chk("(f) ATP_MAIN same seq mean1.6>=1.44 -> NOT aborted (own bar)", S.staircase_aborted.get("ATP_MAIN",False) is False)

# (g) PER-CAT ISOLATION (the new guarantee)
print("(g) per-cat isolation")
S=Self()
run([("fill",59)]*5+[("cancel",0)]*5, cat="WTA_CHALL", S=S)   # depth1<1.71, fr0.5<0.685 -> abort
chk("(g1) WTA_CHALL aborted on its own bars", S.staircase_aborted.get("WTA_CHALL") is True)
chk("(g2) ATP_MAIN NOT aborted by WTA_CHALL", S.staircase_aborted.get("ATP_MAIN") in (None,False))
chk("(g3) ATP_MAIN tally untouched", S.staircase_resolved.get("ATP_MAIN",0)==0)
run([("fill",59)]*5+[("cancel",0)]*5, cat="ATP_MAIN", S=S)    # now drive ATP_MAIN in the SAME Self
chk("(g4) ATP_MAIN aborts on ITS bars (same Self)", S.staircase_aborted.get("ATP_MAIN") is True)
chk("(g5) both tallies independent (10 each)", S.staircase_resolved["WTA_CHALL"]==10 and S.staircase_resolved["ATP_MAIN"]==10)
S=Self()
run([("fill",55)]*10, cat="ATP_CHALL", S=S)   # depth5 >> 1.88, fr1.0 -> NO abort
chk("(g6) healthy ATP_CHALL (depth5/fr1.0) NOT aborted", S.staircase_aborted.get("ATP_CHALL",False) is False)

print("\nRESULT:", "ALL PASS" if not fails else f"FAILURES {fails}")
assert not fails
