#!/usr/bin/env python3
"""[C-KALSHI-OCC] unit test for the coarse Kalshi-occurrence start fallback's two pure helpers.
AST-extracts _kalshi_occ_start + _coarse_window_closed from live source (no import). Run from arb-executor."""
import ast, textwrap, os
src=open(os.environ.get("LV4","live_v4.py")).read()
def grab(n): return next(ast.get_source_segment(src,x) for x in ast.walk(ast.parse(src)) if isinstance(x,ast.FunctionDef) and x.name==n)
ns={}
exec(textwrap.dedent(grab("_kalshi_occ_start")),ns)
exec(textwrap.dedent(grab("_coarse_window_closed")),ns)
OCC=ns["_kalshi_occ_start"]; WIN=ns["_coarse_window_closed"]
# constants pulled from source
def const(name):
    return next(ast.literal_eval(ast.get_source_segment(src,n.value)) for n in ast.walk(ast.parse(src))
               if isinstance(n,ast.Assign) and any(getattr(t,"id",None)==name for t in n.targets))
WIDE=const("KALSHI_COARSE_WIDE_TAIL_SEC"); MAXF=const("KALSHI_COARSE_MAX_FUTURE_SEC"); BUF=const("ENTRY_BUFFER_SEC")
print(f"constants: WIDE_TAIL={WIDE} MAX_FUTURE={MAXF} ENTRY_BUFFER={BUF}")
fails=[]
def chk(n,c): print(f"  {n}: {'PASS' if c else 'FAIL'}"); (None if c else fails.append(n))

NOW=1_000_000.0
print("\n(1) _kalshi_occ_start -- the guard (real future only)")
# 3 target books: occ 09:00Z ~3.25h future -> accept
chk("YUXSHI/JUNXUX/CHOOHX coarse occ (+3.25h) ACCEPTED", OCC(NOW+3.25*3600, NOW, MAXF)==NOW+3.25*3600)
chk("near-future (+10min) accepted", OCC(NOW+600, NOW, MAXF)==NOW+600)
chk("PAST occurrence (SUMTAK-yesterday, -6h) REJECTED -> None", OCC(NOW-6*3600, NOW, MAXF) is None)
chk("exactly now (tts=0) rejected (not strictly future)", OCC(NOW, NOW, MAXF) is None)
chk("14-DAY close placeholder (+14d) REJECTED via bound", OCC(NOW+14*86400, NOW, MAXF) is None)
chk("just past 36h bound REJECTED", OCC(NOW+MAXF+1, NOW, MAXF) is None)
chk("just inside 36h bound accepted", OCC(NOW+MAXF, NOW, MAXF)==NOW+MAXF)
chk("None input -> None", OCC(None, NOW, MAXF) is None)

print("\n(2) _coarse_window_closed -- COARSE wide envelope vs legacy")
# coarse: clock does NOT lock at T-15 / T-0
chk("coarse, +3h before -> OPEN (None)", WIN(3*3600, True, WIDE, BUF) is None)
chk("coarse, INSIDE T-15 (tts=300) -> still OPEN (legacy would inside_buffer)", WIN(300, True, WIDE, BUF) is None)
chk("coarse, 10min PAST coarse start (tts=-600) -> still OPEN (legacy would match_already_started)", WIN(-600, True, WIDE, BUF) is None)
chk("coarse, just inside tail (tts=-(WIDE-1)) -> OPEN", WIN(-(WIDE-1), True, WIDE, BUF) is None)
chk("coarse, tail elapsed (tts=-(WIDE+1)) -> match_already_started", WIN(-(WIDE+1), True, WIDE, BUF)=="match_already_started")

print("\n(3) _coarse_window_closed -- NON-coarse legacy byte-identical")
def legacy(tts):
    if tts<=0: return "match_already_started"
    if tts<=BUF: return "inside_buffer"
    return None
import random
sweep=[-10000,-5400,-900,-1,0,1,300,899,900,901,3600,14400]
allok=all(WIN(t, False, WIDE, BUF)==legacy(t) for t in sweep)
chk("non-coarse == legacy gate across sweep (byte-identical OFF)", allok)
chk("non-coarse tts=-1 -> match_already_started", WIN(-1, False, WIDE, BUF)=="match_already_started")
chk("non-coarse tts=300 (<T-15) -> inside_buffer", WIN(300, False, WIDE, BUF)=="inside_buffer")
chk("non-coarse tts=3600 -> None (open)", WIN(3600, False, WIDE, BUF) is None)

print("\n(4) end-to-end target-book scenario (flag ON)")
# YUXSHI: kts=now+3.25h accepted; then at tts where legacy locks, coarse stays open
kts=OCC(NOW+3.25*3600, NOW, MAXF)
chk("step1 occ accepted (window will open off it)", kts is not None)
chk("step2 at coarse-T-10min coarse OPEN where legacy=match_already_started",
    WIN(-600, True, WIDE, BUF) is None and WIN(-600, False, WIDE, BUF)=="match_already_started")

print("\n(5) 14-day-close-only event -> skipped (never mistaken for a start) under both flag states")
# kts rejected -> caller would NOT set coarse_source -> gate runs non-coarse legacy
chk("close-only occ rejected -> None -> stays schedule_gap path", OCC(NOW+14*86400, NOW, MAXF) is None)

print("\nRESULT:", "ALL PASS" if not fails else f"FAILURES {fails}")
assert not fails
