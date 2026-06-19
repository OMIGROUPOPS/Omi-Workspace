#!/usr/bin/env python3
"""[C-STAIRCASE SHIP-2 abort-spec] unit test for _staircase_resolve AND-gate. Extracts the method +
constants from the live source via AST; shims self/pos (no module import). Run from arb-executor.
(LV4 env overrides the source path; default live_v4.py)."""
import ast, textwrap, os, re
src = open(os.environ.get("LV4", "live_v4.py")).read()
def C(name): return float(re.search(rf'^{name}\s*=\s*([0-9.]+)', src, re.M).group(1))
MINR=int(C("STAIRCASE_MIN_RESOLVED")); FRBAR=C("STAIRCASE_ABORT_FILLRATE"); DBAR=C("STAIRCASE_ABORT_DEPTH")
print(f"constants: MIN_RESOLVED={MINR} FILLRATE={FRBAR} DEPTH={DBAR}")
fsrc=next(ast.get_source_segment(src,n) for n in ast.walk(ast.parse(src)) if isinstance(n,ast.FunctionDef) and n.name=="_staircase_resolve")
ns={"STAIRCASE_MIN_RESOLVED":MINR,"STAIRCASE_ABORT_FILLRATE":FRBAR,"STAIRCASE_ABORT_DEPTH":DBAR}
exec(textwrap.dedent(fsrc), ns); resolve=ns["_staircase_resolve"]
class Pos:
    def __init__(s,anchor=60,ref=58,cell=60): s.reference_source="staircase"; s.staircase_anchor=anchor; s.staircase_ref=ref; s.staircase_cell=cell
class Self:
    def __init__(s): s.staircase_aborted=False; s.staircase_resolved=0; s.staircase_fills=0; s.staircase_depth_sum=0.0; s.logs=[]
    def _log(s,e,d,ticker=None): s.logs.append((e,d))
def run(seq):
    """seq: list of (outcome, fill_price). anchor=60."""
    S=Self()
    for outcome,fp in seq: resolve(S,Pos(anchor=60),outcome,fp)
    return S
fails=[]
def chk(name,cond): print(f"  {name}: {'PASS' if cond else 'FAIL'}"); (None if cond else fails.append(name))

# (a) below MIN_RESOLVED -> never abort (9 all-cancel = worst case)
S=run([("cancel",0)]*9)
chk("(a) 9 resolved (<MIN) -> not aborted", S.staircase_aborted is False and S.staircase_resolved==9)

# (b) BOTH bars trip -> abort. 10 legs, 5 fills @ depth 1 (mean_depth 1.0<1.44), fill_rate 0.5<0.623
S=run([("fill",59)]*5 + [("cancel",0)]*5)   # depth=60-59=1
chk("(b) both bars (depth1, fr0.5) -> ABORTED", S.staircase_aborted is True)
chk("(b) staircase_trial_abort logged", any(e=="staircase_trial_abort" for e,_ in S.logs))

# (c) AND-gate: depth OK (>=1.44) but fill low -> NO abort. 5 fills @ depth 3 (mean 3), fr 0.5
S=run([("fill",57)]*5 + [("cancel",0)]*5)   # depth=3
chk("(c) depth3>=1.44 (one bar) -> NOT aborted", S.staircase_aborted is False)
# (c2) AND-gate: fill OK (>=0.623) but depth low -> NO abort. 9 fills @ depth1 + 1 cancel, fr 0.9
S=run([("fill",59)]*9 + [("cancel",0)])
chk("(c2) fr0.9>=0.623 (one bar) -> NOT aborted", S.staircase_aborted is False)

# (d) non-staircase pos -> no-op
S=Self(); p=Pos(); p.reference_source="join_bid"; resolve(S,p,"fill",59)
chk("(d) non-staircase leg -> ignored", S.staircase_resolved==0 and S.staircase_aborted is False)

# (e) telemetry: staircase_walk on every resolve
S=run([("fill",59),("cancel",0)])
chk("(e) staircase_walk logged per resolve", sum(1 for e,_ in S.logs if e=="staircase_walk")==2)

# (f) depth uses realized offset anchor-fill; abort only AFTER >=MIN even if bars met early
S=Self()
for _ in range(9): resolve(S,Pos(anchor=60),"cancel",0)   # 9 -> bars met but <MIN
chk("(f) bars met at 9 but <MIN -> still not aborted", S.staircase_aborted is False)
resolve(S,Pos(anchor=60),"cancel",0)   # 10th -> abort
chk("(f) 10th resolve -> abort fires", S.staircase_aborted is True)

print("\nRESULT:", "ALL PASS" if not fails else f"FAILURES {fails}")
assert not fails
