#!/usr/bin/env python3
"""[C-STAIRCASE-ABORT-FIX 2026-06-20] unit test for the corrected _staircase_resolve abort gate.

Extends the C-STAIRCASE 4CAT per-cat AND-gate test with the two false-trigger fixes diagnosed in the
2026-06-20 entry autopsy (the walking staircase filled 15/18 legs = 83% but auto-aborted at 0% on a
premarket walk-step sample):
  Defect A -- walk-step reposts (label v4_move_repost) are NOT counted -> per-LEG, not per-walk-step.
  Defect B -- a resolution counts only if the leg reached its match (fill / _is_match_live / <=ENTRY_BUFFER_SEC).
  once-per-leg -- staircase_counted makes one leg -> at most ONE resolution.
Preserves the original AND-gate + per-cat isolation guarantees, now driven with LIVE terminal cancels
(post-fix a cancel counts only when the leg was live). Extracts the method via AST; shims self/pos (no
import; matches the C-STAIRCASE 4CAT harness). Run from arb-executor."""
import ast, textwrap, os, time
src=open(os.environ.get("LV4","live_v4.py")).read()
tree=ast.parse(src)
def const(name):
    for n in ast.walk(tree):
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets):
            return ast.literal_eval(n.value)
    raise KeyError(name)
MINR=const("STAIRCASE_MIN_RESOLVED"); FR=const("STAIRCASE_ABORT_FILLRATE"); DB=const("STAIRCASE_ABORT_DEPTH")
EBS=const("ENTRY_BUFFER_SEC"); NONTERM=const("_STAIRCASE_NONTERMINAL_LABELS")
print("constants: MIN_RESOLVED=%s  ENTRY_BUFFER_SEC=%s  NONTERMINAL=%s" % (MINR, EBS, sorted(NONTERM)))
print("  FILLRATE bars: %s" % (FR,))
print("  DEPTH bars:    %s" % (DB,))
fsrc=next(ast.get_source_segment(src,n) for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=="_staircase_resolve")
ns={"STAIRCASE_MIN_RESOLVED":MINR,"STAIRCASE_ABORT_FILLRATE":FR,"STAIRCASE_ABORT_DEPTH":DB,
    "ENTRY_BUFFER_SEC":EBS,"_STAIRCASE_NONTERMINAL_LABELS":NONTERM,"time":time}
exec(textwrap.dedent(fsrc),ns); resolve=ns["_staircase_resolve"]
WALK=next(iter(NONTERM))   # "v4_move_repost"

class Pos:
    def __init__(s,cat="ATP_MAIN",anchor=60,ref=58,cell=60,mst=0.0,et="EV"):
        s.reference_source="staircase"; s.category=cat
        s.staircase_anchor=anchor; s.staircase_ref=ref; s.staircase_cell=cell
        s.staircase_counted=False; s.match_start_ts=mst; s.event_ticker=et
class Self:
    def __init__(s,live=True): s.staircase_aborted={}; s.staircase_resolved={}; s.staircase_fills={}; s.staircase_depth_sum={}; s.logs=[]; s._live=live
    def _log(s,e,d,ticker=None): s.logs.append((e,d))
    def _is_match_live(s,et): return s._live
def run(seq,cat="ATP_MAIN",anchor=60,S=None,live=True,mst=0.0,reuse=False):
    # seq item: (outcome,fill_price) -> terminal default-label; or (outcome,fill_price,label)
    S=S if S is not None else Self(live=live)
    p=None
    for item in seq:
        outcome,fp = item[0],item[1]; label = item[2] if len(item)>2 else None
        if reuse:
            if p is None: p=Pos(cat=cat,anchor=anchor,mst=mst)
            resolve(S,p,outcome,fp,label)
        else:
            resolve(S,Pos(cat=cat,anchor=anchor,mst=mst),outcome,fp,label)
    return S
fails=[]
def chk(name,cond): print("  %s: %s" % (name, 'PASS' if cond else 'FAIL')); (None if cond else fails.append(name))

# (0) per-cat constant bars present + equal the derived values
print("(0) per-cat constant bars")
EXP_FR={"ATP_MAIN":0.623,"WTA_MAIN":0.602,"ATP_CHALL":0.621,"WTA_CHALL":0.685}
EXP_DB={"ATP_MAIN":1.44,"WTA_MAIN":1.89,"ATP_CHALL":1.88,"WTA_CHALL":1.71}
for cat in EXP_FR:
    chk("  %s FILLRATE=%s & DEPTH=%s" % (cat,EXP_FR[cat],EXP_DB[cat]), FR.get(cat)==EXP_FR[cat] and DB.get(cat)==EXP_DB[cat])
chk("  v4_move_repost is the non-terminal label", "v4_move_repost" in NONTERM)

# (a-g) ORIGINAL AND-gate + per-cat isolation -- now driven with LIVE terminal cancels (live=True default)
print("(a-g) AND-gate + per-cat isolation (LIVE terminal cancels)")
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
print("(f) per-cat bars applied (mean_depth 1.6 splits WTA_MAIN 1.89 vs ATP_MAIN 1.44)")
SEQ=[("fill",58)]*3+[("fill",59)]*2+[("cancel",0)]*5   # depths 2,2,2,1,1 -> mean 1.6; fr 5/10=0.5
chk("(f) WTA_MAIN mean1.6<1.89 & fr0.5<0.602 -> ABORT", run(SEQ,cat="WTA_MAIN").staircase_aborted.get("WTA_MAIN") is True)
chk("(f) ATP_MAIN same seq mean1.6>=1.44 -> NOT aborted (own bar)", run(SEQ,cat="ATP_MAIN").staircase_aborted.get("ATP_MAIN",False) is False)
print("(g) per-cat isolation")
S=Self()
run([("fill",59)]*5+[("cancel",0)]*5, cat="WTA_CHALL", S=S)
chk("(g1) WTA_CHALL aborted on its own bars", S.staircase_aborted.get("WTA_CHALL") is True)
chk("(g2) ATP_MAIN NOT aborted by WTA_CHALL", S.staircase_aborted.get("ATP_MAIN") in (None,False))
chk("(g3) ATP_MAIN tally untouched", S.staircase_resolved.get("ATP_MAIN",0)==0)
run([("fill",59)]*5+[("cancel",0)]*5, cat="ATP_MAIN", S=S)
chk("(g4) ATP_MAIN aborts on ITS bars (same Self)", S.staircase_aborted.get("ATP_MAIN") is True)
chk("(g5) both tallies independent (10 each)", S.staircase_resolved["WTA_CHALL"]==10 and S.staircase_resolved["ATP_MAIN"]==10)
chk("(g6) healthy ATP_CHALL (depth5/fr1.0) NOT aborted", run([("fill",55)]*10,cat="ATP_CHALL").staircase_aborted.get("ATP_CHALL",False) is False)

# ===== C-STAIRCASE-ABORT-FIX new cases =====
print("(A) Defect A -- walk-step reposts excluded")
S=run([("cancel",0,WALK)]*10, live=False, mst=0.0)   # 10 premarket bid-climbs (the 04:01 false-abort sample)
chk("(A1) 10 walk-steps -> resolved=0, NOT aborted", S.staircase_resolved.get("ATP_MAIN",0)==0 and S.staircase_aborted.get("ATP_MAIN",False) is False)
chk("(A1) walk-steps still log telemetry (walk_step=True)", sum(1 for e,d in S.logs if e=="staircase_walk" and d.get("walk_step"))==10)
S=run([("cancel",0,WALK)]*5+[("fill",59)], reuse=True, live=True)   # 1 leg: 5 climbs + fill
chk("(A2) 5 walk-steps + 1 fill -> resolved=1, fills=1 (counted once)", S.staircase_resolved.get("ATP_MAIN")==1 and S.staircase_fills.get("ATP_MAIN")==1)
S=run([("cancel",0,WALK)]*5+[("fill",59),("cancel",0,"match_live_cancel")], reuse=True, live=True)  # fill THEN a live terminal on same leg
chk("(A2b) once-per-leg flag -> terminal after fill does NOT double-count", S.staircase_resolved.get("ATP_MAIN")==1)

print("(B) Defect B -- only legs that reached their match count")
S=run([("cancel",0,"match_live_cancel")]*10, live=True)   # 10 DISTINCT live legs, 0 fills
chk("(B1/SAFETY) 10 live no-fills -> abort STILL fires", S.staircase_aborted.get("ATP_MAIN") is True and S.staircase_resolved["ATP_MAIN"]==10)
S=run([("cancel",0,"schedule_corrected_window_deferred")]*10, live=False, mst=time.time()+4*3600)  # tts +4h, not live
chk("(B2) premarket terminal cancel (tts +4h) -> NOT counted", S.staircase_resolved.get("ATP_MAIN",0)==0 and S.staircase_aborted.get("ATP_MAIN",False) is False)
S=run([("cancel",0,"match_start_buffer")]*10, live=False, mst=time.time()+(EBS-60))  # within T-15 buffer of known start
chk("(B3) near-start terminal (tts<=ENTRY_BUFFER) -> COUNTS even when not volume-live", S.staircase_resolved.get("ATP_MAIN")==10 and S.staircase_aborted.get("ATP_MAIN") is True)
S=run([("fill",59)]*10, live=False, mst=0.0)   # fills count regardless of liveness
chk("(B4) a FILL always counts (proof-of-chance) even when not live", S.staircase_resolved.get("ATP_MAIN")==10)

print("\nRESULT:", "ALL PASS" if not fails else "FAILURES %s" % fails)
assert not fails
