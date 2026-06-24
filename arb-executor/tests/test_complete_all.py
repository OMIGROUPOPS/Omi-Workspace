#!/usr/bin/env python3
"""[C-COMPLETE-ALL] regression test for gated all-cells completion. AST-extract _completion_target;
verify the default X=99 (set in the gate for non-table cells) makes the mirror target bind on ask-1.
STATIC: default-OFF, gate branch gated + ask-guarded, legacy no-attempt intact (byte-identical OFF),
touches only the eligibility gate. Run from arb-executor."""
import ast, textwrap, os, re
src=open(os.environ.get("LV4","live_v4.py")).read()
ns={}
for m in re.finditer(r"^(V4_PAIRED_BASIS_CAP\s*=\s*\d+)",src,re.M): exec(m.group(1),ns)
tree=ast.parse(src)
meth=next(n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=="_completion_target")
exec(textwrap.dedent(ast.get_source_segment(src,meth)),ns); fn=ns["_completion_target"]
class S:
    def __init__(s,cap): s.paired_cap_enforced=cap
fails=[]
def chk(n,c): print("  %s: %s"%(n,"PASS" if c else "FAIL")); (None if c else fails.append(n))
print("(DYNAMIC) _completion_target with default X=99 (the all-cells mirror) [cap-off, live]")
chk("(A) X=99, ask=58 -> ask-1 (57): mirror at ask-1", fn(S(False),50,99,58,43)==57)
chk("(B) X=99, ask=72 -> 71 (ask-1)", fn(S(False),40,99,72,30)==71)
chk("(C) table X=2, ask=58 -> 52 (s0+X, legacy unchanged)", fn(S(False),50,2,58,43)==52)
chk("(D) X=99, ask=None -> NOT ask-bounded (=99) -> proves gate must require an ask", fn(S(False),50,99,None,43)==99)
chk("(E) cap-ENFORCED never exceeds ask-1 (cap term may bind tighter)", fn(S(True),50,99,58,43) <= 57)
print("(STATIC) gating + byte-identical-OFF + scope")
chk("(S1) flag default OFF", 'self.completion_all_cells = self.config.get("completion_all_cells", False)' in src)
chk("(S2) all-cells branch gated", 'if x_cell is None and self.completion_all_cells:' in src)
chk("(S3) ask-guarded x=99 (never unbounded)", '_sb is not None and 0 < _sb.best_ask < 100' in src and 'x_cell = 99' in src)
i_branch=src.index('if x_cell is None and self.completion_all_cells:')
i_legacy=src.index('"reason": "cell_not_eligible"')
chk("(S4) all-cells branch precedes legacy no-attempt (OFF -> falls through)", i_branch < i_legacy)
chk("(S5) legacy no-attempt return INTACT (byte-identical OFF)",
    '"reason": "cell_not_eligible", "category": pos.category,' in src)
# the patched region must not touch exit/abort/meter/routing
reg=src[i_branch-50:i_legacy+300]
chk("(S6) gate touches only completion (no exit/abort/meter/routing)",
    all(x not in reg for x in ["exit","staircase_abort","_is_match_live","reference_source","_staircase"]))
print(chr(10)+"RESULT:", "ALL PASS" if not fails else "FAILED: "+", ".join(fails)); raise SystemExit(1 if fails else 0)
