#!/usr/bin/env python3
"""[C-COMPLETE-ALL + tripwire carve-out] regression. AST-extract the REAL functions; tick BOTH tripwire
paths (the gap that sank 0db51c4). Proves: all-cells-armed positions are tripwire-EXEMPT (fill + manage),
genuine corruption (non-armed, non-table) STILL fires, and the mirror target binds on ask-1. Run from arb-executor."""
import ast, textwrap, os, re, asyncio
src=open(os.environ.get("LV4","live_v4.py")).read()
ns={}
for m in re.finditer(r"^(V4_PAIRED_BASIS_CAP\s*=\s*\d+|V4_COMPLETION_FRESHNESS_SEC\s*=\s*\d+)",src,re.M): exec(m.group(1),ns)
tree=ast.parse(src)
def grab(name):
    n=next(x for x in ast.walk(tree) if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==name)
    exec(textwrap.dedent(ast.get_source_segment(src,n)),ns); return ns[name]
ctgt=grab("_completion_target"); fillg=grab("_completion_fill_guards"); mgmt=grab("_v4_manage_completion")
fails=[]
def chk(n,c): print("  %s: %s"%(n,"PASS" if c else "FAIL")); (None if c else fails.append(n))

class Cap:
    def __init__(s,c): s.paired_cap_enforced=c
print("(DYNAMIC) _completion_target -- X=99 mirror binds on ask-1")
chk("(A) X=99 ask58 -> 57 (ask-1)", ctgt(Cap(False),50,99,58,43)==57)
chk("(B) table X=2 ask58 -> 52 (legacy)", ctgt(Cap(False),50,2,58,43)==52)
chk("(C) X=99 no-ask -> unbounded(99) [gate must require ask]", ctgt(Cap(False),50,99,None,43)==99)

class Pos:
    def __init__(s,cell,arm,cat="WTA_MAIN"):
        s.category=cat; s.completion_lookup_cell=cell; s.completion_all_cells_arm=arm
        s.completion_leg1_basis=40; s.entry_price=57; s.event_ticker="EV"; s.match_start_ts=0; s.completion_reprice_ts=0.0
class FillSelf:
    paired_cap_enforced=False; completion_cells={("ATP_MAIN",35):3}
print("(DYNAMIC) fill-path _completion_fill_guards -- TICK the V4 tripwire")
chk("(F1) armed non-table cell -> NO V4 violation (exempt)", fillg(FillSelf(),Pos(58,True),50,False) is None)
chk("(F2) NON-armed non-table cell -> V4_cell_not_in_table (corruption preserved)",
    (fillg(FillSelf(),Pos(58,False),50,False) or ("",))[0]=="V4_cell_not_in_table")
chk("(F3) in-table cell, non-armed -> None (normal)", fillg(FillSelf(),Pos(35,False,"ATP_MAIN"),50,False) is None)

class Book: best_ask=58; best_bid=56
class MgSelf:
    completion_reprice=True; completion_disabled=False; completion_cells={("ATP_MAIN",35):3}
    def __init__(s): s.trips=0; s.reverts=0
    def _is_match_live(s,et): return True          # short-circuit AFTER the cell check
    async def _completion_revert(s,*a,**k): s.reverts+=1
    async def _completion_tripwire(s,*a,**k): s.trips+=1
def run_mgmt(arm):
    st=MgSelf(); asyncio.run(mgmt(st,"EV",Pos(58,arm),Book(),0.0)); return st
print("(DYNAMIC) manage-path _v4_manage_completion -- TICK the V4 tripwire (async)")
a=run_mgmt(True);  chk("(M1) armed non-table -> tripwire NOT fired (trips=0, revert via match_live)", a.trips==0 and a.reverts==1)
b=run_mgmt(False); chk("(M2) NON-armed non-table -> tripwire FIRED (trips=1)", b.trips==1 and b.reverts==0)

print("(STATIC) gating + persistence + byte-identical-OFF")
chk("(S1) flag default OFF", 'self.completion_all_cells = self.config.get("completion_all_cells", False)' in src)
chk("(S2) sentinel field default False", 'completion_all_cells_arm: bool = False' in src)
chk("(S3) BOTH tripwires carved out", src.count('not in self.completion_cells and not pos.completion_all_cells_arm:')==2)
chk("(S4) sentinel persisted (save+load)",
    '"completion_all_cells_arm": pos.completion_all_cells_arm,' in src and 'completion_all_cells_arm=bool(d.get("completion_all_cells_arm", False)),' in src)
chk("(S5) sentinel reset on revert", 'pos.completion_all_cells_arm = False' in src)
chk("(S6) sentinel set only when all-cells branch defaults X", 'x_cell = 99; _all_cells_arm = True' in src and 'sp.completion_all_cells_arm = _all_cells_arm' in src)
print(chr(10)+"RESULT:", "ALL PASS" if not fails else "FAILED: "+", ".join(fails)); raise SystemExit(1 if fails else 0)
