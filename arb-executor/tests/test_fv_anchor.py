#!/usr/bin/env python3
"""[C-FV-ANCHOR Move-2] regression test for the gated FV-anchor placement (no import; AST-extract the REAL
helper + module const). DYNAMIC: _fv_anchor_price over a stub tape + the ask-1 clamp. STATIC: default-OFF,
hook gated & inside the non-engagement block (engagement untouched), legacy staircase/join intact
(byte-identical OFF), tape source, helper touches no abort/exit/meter. Run from arb-executor."""
import ast, textwrap, os, re, time
from collections import deque
src = open(os.environ.get("LV4", "live_v4.py")).read()
ns = {"time": time}
exec(re.search(r"^(V4_LAST_TRADE_MAX_AGE_SEC\s*=\s*\d+)", src, re.M).group(1), ns)
tree = ast.parse(src)
meth = next(n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=="_fv_anchor_price")
exec(textwrap.dedent(ast.get_source_segment(src, meth)), ns)
fn = ns["_fv_anchor_price"]; MAXAGE = ns["V4_LAST_TRADE_MAX_AGE_SEC"]
class Stub:
    def __init__(s, tape): s._trade_prices = tape
fails=[]
def chk(n,c): print("  %s: %s"%(n,"PASS" if c else "FAIL")); (None if c else fails.append(n))
now = time.time()
print("(DYNAMIC) _fv_anchor_price  [MAXAGE=%ds]"%MAXAGE)
chk("(A) most-recent fresh print (56)", fn(Stub({"T":deque([(now-100,54),(now-40,55),(now-5,56)])}),"T")==56)
chk("(B) skips zero prints (55 not 0)", fn(Stub({"T":deque([(now-50,55),(now-5,0)])}),"T")==55)
chk("(C) None all stale", fn(Stub({"T":deque([(now-MAXAGE-100,55)])}),"T") is None)
chk("(D) None absent", fn(Stub({}),"T") is None)
chk("(D2) None empty", fn(Stub({"T":deque()}),"T") is None)
chk("(E) rounds int (55)", fn(Stub({"T":deque([(now-5,55.4)])}),"T")==55)
print("(DYNAMIC) ask-1 clamp")
clamp = lambda fv, ask: max(1, min(fv, ask-1))
chk("(F) FV<ask -> FV (55,58->55)", clamp(55,58)==55)
chk("(G) FV>=ask -> ask-1 (60,56->55)", clamp(60,56)==55)
chk("(H) floor 1 (0,1->1)", clamp(0,1)==1)
print("(STATIC) gating + byte-identical-OFF + scope")
chk("(S1) flag default OFF", 'self.fv_anchor_placement = self.config.get("fv_anchor_placement", False)' in src)
chk("(S2) hook gated", '_fv = self._fv_anchor_price(tk) if self.fv_anchor_placement else None' in src)
chk("(S3) clamp ask-1 + join_bid", 'target_bid = max(1, min(_fv, placement_ask - 1))' in src and 'reference_source = "join_bid"' in src)
i_hook=src.index('_fv = self._fv_anchor_price(tk)'); i_eng=src.index('if table_src != "engagement_wave1":')
i_stair=src.index('target_bid, _ = self._staircase_bid(cat, cell, current_price, time_to_start, placement_bid, placement_ask)')
chk("(S4) hook inside non-engagement block, before legacy staircase", i_eng < i_hook < i_stair)
chk("(S5) legacy staircase+join intact", 'elif cat in self._range_final:' in src and 'target_bid, _ = self._join_target(placement_bid, placement_ask)' in src)
mb = meth.body[1:] if (meth.body and isinstance(meth.body[0], ast.Expr) and isinstance(meth.body[0].value, ast.Constant)) else meth.body
code_only = chr(10).join(ast.get_source_segment(src, n) for n in mb)
chk("(S6) helper CODE reads TRADE TAPE not book", "self._trade_prices.get(ticker)" in code_only and "book." not in code_only)
chk("(S7) helper no abort/exit/meter/staircase", all(x not in code_only for x in ["staircase_aborted","_is_match_live","_staircase","abort_rearm"]))
print(chr(10)+"RESULT:", "ALL PASS" if not fails else "FAILED: "+", ".join(fails)); raise SystemExit(1 if fails else 0)
