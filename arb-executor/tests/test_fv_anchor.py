#!/usr/bin/env python3
"""[C-FV-ANCHOR Move-2/3] regression test for the gated FV-anchor placement (no import; AST-extract the REAL
helpers + module consts). DYNAMIC: _fv_anchor_price over a stub tape + _fv_anchor_sane book-sanity band.
STATIC: default-OFF, hook gated & inside the non-engagement block (engagement untouched), ask-1 clamp STRIPPED
(post AT fv), sanity guard wired before the place, legacy staircase/join intact (byte-identical OFF), tape
source, helpers touch no abort/exit/meter. Run from arb-executor."""
import ast, textwrap, os, re, time
from collections import deque
src = open(os.environ.get("LV4", "live_v4.py")).read()
ns = {"time": time}
exec(re.search(r"^(V4_LAST_TRADE_MAX_AGE_SEC\s*=\s*\d+)", src, re.M).group(1), ns)
exec(re.search(r"^(FV_ANCHOR_MAX_GAP_C\s*=\s*\d+)", src, re.M).group(1), ns)
tree = ast.parse(src)
def getfn(name):
    m = next(n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
    exec(textwrap.dedent(ast.get_source_segment(src, m)), ns)
    return ns[name], m
fn, meth = getfn("_fv_anchor_price")
sane, sane_meth = getfn("_fv_anchor_sane")
MAXAGE = ns["V4_LAST_TRADE_MAX_AGE_SEC"]; GAP = ns["FV_ANCHOR_MAX_GAP_C"]
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

print("(DYNAMIC) _fv_anchor_sane  book-sanity band [GAP=%dc]"%GAP)
S = None  # method ignores self
chk("(I) inside book -> sane (50 in 40/60)", sane(S,50,40,60) is True)
chk("(J) at ask+GAP boundary inclusive", sane(S,60+GAP,40,60) is True)
chk("(K) ask+GAP+1 -> off-book reject", sane(S,60+GAP+1,40,60) is False)
chk("(L) stale-high collapse reject (77, book 40/50)", sane(S,77,40,50) is False)
chk("(M) at bid-GAP boundary inclusive", sane(S,45-GAP,45,46) is True)
chk("(N) far below bid -> gapped reject", sane(S,45-GAP-1,45,46) is False)

print("(STATIC) gating + ask-1 STRIPPED + sanity wired + byte-identical-OFF + scope")
chk("(S1) flag default OFF", 'self.fv_anchor_placement = self.config.get("fv_anchor_placement", False)' in src)
chk("(S2) hook gated", '_fv = self._fv_anchor_price(tk) if self.fv_anchor_placement else None' in src)
chk("(S3) post AT fv (no ceiling) + join_bid", 'target_bid = max(1, _fv)' in src and 'reference_source = "join_bid"' in src)
chk("(S3b) ask-1 clamp REMOVED", 'min(_fv, placement_ask - 1)' not in src)
chk("(S3c) sanity guard wired before place",
    'not self._fv_anchor_sane(_fv, placement_bid, placement_ask)' in src
    and '"reason": "off_book_band"' in src)
i_hook=src.index('_fv = self._fv_anchor_price(tk)'); i_eng=src.index('if table_src != "engagement_wave1":')
i_sane=src.index('not self._fv_anchor_sane(_fv, placement_bid, placement_ask)')
i_stair=src.index('target_bid, _ = self._staircase_bid(cat, cell, current_price, time_to_start, placement_bid, placement_ask)')
chk("(S4) hook->sanity->place all inside non-engagement block, before legacy staircase",
    i_eng < i_hook < i_sane < i_stair)
chk("(S5) legacy staircase+join intact", 'elif cat in self._range_final:' in src and 'target_bid, _ = self._join_target(placement_bid, placement_ask)' in src)
mb = meth.body[1:] if (meth.body and isinstance(meth.body[0], ast.Expr) and isinstance(meth.body[0].value, ast.Constant)) else meth.body
code_only = chr(10).join(ast.get_source_segment(src, n) for n in mb)
chk("(S6) price helper CODE reads TRADE TAPE not book", "self._trade_prices.get(ticker)" in code_only and "book." not in code_only)
chk("(S7) price helper no abort/exit/meter/staircase", all(x not in code_only for x in ["staircase_aborted","_is_match_live","_staircase","abort_rearm"]))
sb = sane_meth.body[1:] if (sane_meth.body and isinstance(sane_meth.body[0], ast.Expr) and isinstance(sane_meth.body[0].value, ast.Constant)) else sane_meth.body
sane_code = chr(10).join(ast.get_source_segment(src, n) for n in sb)
chk("(S8) sane helper pure (const+args only, no state/book/abort/exit)",
    "FV_ANCHOR_MAX_GAP_C" in sane_code and all(x not in sane_code for x in ["self.","book.","staircase","abort","exit","_log"]))
print(chr(10)+"RESULT:", "ALL PASS" if not fails else "FAILED: "+", ".join(fails)); raise SystemExit(1 if fails else 0)
