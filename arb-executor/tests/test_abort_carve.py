#!/usr/bin/env python3
"""[C-ABORT-CARVE] regression test for the gated abort-orphan carve (no import; AST-extract the REAL
helpers). DYNAMIC D1-D6: _carve_abort_for_held_sibling decision over stub positions. STATIC S1-S3:
default-OFF flag, carve wired at BOTH abort gates, helper reaches no exit/manage/completion/meter/routing.
Run from arb-executor."""
import ast, textwrap, os
src = open(os.environ.get("LV4", "live_v4.py")).read()
ns = {}
tree = ast.parse(src)
def getfn(name):
    m = next(n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
    exec(textwrap.dedent(ast.get_source_segment(src, m)), ns)
    return ns[name], m
sib_fn, _ = getfn("_sibling_ticker")
carve, carve_m = getfn("_carve_abort_for_held_sibling")

class Pos:
    def __init__(s, phase="entry_resting", settled=False, exit_filled=False, entry_mode="", entry_qty=0):
        s.phase=phase; s.settled=settled; s.exit_filled=exit_filled; s.entry_mode=entry_mode; s.entry_qty=entry_qty
class Stub:
    _sibling_ticker = sib_fn
    _carve_abort_for_held_sibling = carve
    def __init__(s, sibpos, has_sib=True):
        ET="KX-26X-G"; s.A=ET+"-A"; s.B=ET+"-B"; s.et=ET
        s.event_tickers = {ET: (s.A, s.B)} if has_sib else {ET: (s.B,)}
        s.positions = {s.A: sibpos} if sibpos is not None else {}
def carve_for_B(sibpos, has_sib=True):
    st = Stub(sibpos, has_sib); return st._carve_abort_for_held_sibling(st.B, st.et)

fails=[]
def chk(n,c): print("  %s: %s"%(n,"PASS" if c else "FAIL")); (None if c else fails.append(n))

print("(DYNAMIC) _carve_abort_for_held_sibling")
chk("(D1) FIRES: sib entry_resting + entry_qty==0 (Scenario A)",
    carve_for_B(Pos(phase="entry_resting", entry_qty=0)) is True)
chk("(D2) FIRES: sib entry_qty>0 (Scenario B)",
    carve_for_B(Pos(phase="active", entry_qty=5)) is True)
chk("(D3) NO fire: sib settled",
    carve_for_B(Pos(phase="active", entry_qty=5, settled=True)) is False)
chk("(D4) NO fire: sib exiting/flat (phase==exiting OR exit_filled)",
    carve_for_B(Pos(phase="exiting", entry_qty=5)) is False
    and carve_for_B(Pos(phase="active", entry_qty=5, exit_filled=True)) is False)
chk("(D5) NO fire: sib entry_mode==completion_reprice",
    carve_for_B(Pos(phase="active", entry_qty=5, entry_mode="completion_reprice")) is False)
chk("(D6) NO fire: no sibling exists",
    carve_for_B(None, has_sib=False) is False and carve_for_B(None) is False)

print("(STATIC) gating + both-gate wiring + scope")
chk("(S1) flag default OFF (absent -> False)",
    'self.abort_carve_held_sibling = bool(self.config.get("abort_carve_held_sibling", False))' in src)
chk("(S1b) gate guarded by flag (short-circuit when OFF)",
    'if self.abort_carve_held_sibling and self._carve_abort_for_held_sibling(tk, et):' in src)
chk("(S2) carve at BOTH abort gates (count==2)",
    src.count("self._carve_abort_for_held_sibling(tk, et)") == 2
    and src.count('"gate": "join_trial"') == 1 and src.count('"gate": "staircase"') == 1)
# AST: helper body reaches no exit/manage/completion/meter/routing CALLS
cb = carve_m.body[1:] if (carve_m.body and isinstance(carve_m.body[0], ast.Expr) and isinstance(carve_m.body[0].value, ast.Constant)) else carve_m.body
calls = [n.func.attr for n in ast.walk(ast.Module(body=cb, type_ignores=[]))
         if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
chk("(S3) helper calls ONLY _sibling_ticker/.get (no exit/manage/completion/meter/route)",
    set(calls) <= {"_sibling_ticker", "get"})
attrs = set(n.attr for n in ast.walk(ast.Module(body=cb, type_ignores=[])) if isinstance(n, ast.Attribute))
ALLOWED_ATTRS = {"_sibling_ticker","_carve_abort_for_held_sibling","positions","get",
                 "settled","phase","exit_filled","entry_mode","entry_qty"}
chk("(S3b) helper touches ONLY sibling/positions infra + read-only Position fields",
    attrs <= ALLOWED_ATTRS)
chk("(S4) byte-identical-OFF: original skip+continue preserved in else",
    src.count('self._log("skipped", {"reason": "join_trial_aborted"') == 1
    and src.count('self._log("skipped", {"reason": "staircase_aborted"') == 1)
print(chr(10)+"RESULT:", "ALL PASS" if not fails else "FAILED: "+", ".join(fails)); raise SystemExit(1 if fails else 0)
