#!/usr/bin/env python3
"""Test for [C-SUSTAINED-FLOW]. Real LiveV3._sustained_flow_live + cancel-site gate semantics."""
import time, collections, live_v4
from live_v4 import LiveV3, LIVE_TRADE_BURST
def bot(on=True, K=3):
    b=object.__new__(LiveV3); b.sustained_flow_latch=on; b.sustained_flow_K=K
    b.event_tickers={"E":{"E-A","E-B"}}; b._trade_times=collections.defaultdict(collections.deque)
    return b
def windows(b, counts, leg="E-A"):
    """counts[w] = prints placed in window w (w=0 = most-recent 60s). Places at window midpoint."""
    now=time.time()
    for w,n in enumerate(counts):
        ts = now - w*60 - 30      # middle of window w
        for _ in range(n): b._trade_times[leg].append(ts)
ok=True
def chk(label,cond):
    global ok; print(f"  [{'PASS' if cond else 'FAIL'}] {label}"); ok=ok and cond
print(f"LIVE_TRADE_BURST={LIVE_TRADE_BURST}, K default test=3")

print("=== _sustained_flow_live (real) ===")
b=bot(); windows(b,[10,10,10]); chk("3 consecutive >=10 windows -> latch True", b._sustained_flow_live("E") is True)
b=bot(); windows(b,[10,10,5]); chk("3rd window <10 (not sustained) -> False", b._sustained_flow_live("E") is False)
b=bot(); windows(b,[10,0,0]); chk("isolated recent burst (1 window) -> False (false burst)", b._sustained_flow_live("E") is False)
b=bot(); windows(b,[0,0,10]); chk("burst 2-3min ago, now quiet -> False (counter-evidence inherent)", b._sustained_flow_live("E") is False)
b=bot(); windows(b,[0,0,0]); chk("fully quiet -> False", b._sustained_flow_live("E") is False)
b=bot(); windows(b,[12,12,12]); chk("FLAT real match (continuous prints, no price-move) -> True (volume-only)", b._sustained_flow_live("E") is True)
# split across legs: each window 5+5=10 across the two legs
b=bot(); windows(b,[5,5,5],"E-A"); windows(b,[5,5,5],"E-B"); chk("flow split across both legs sums per-window -> True", b._sustained_flow_live("E") is True)
# no legs
b=bot(); b.event_tickers={}; chk("no legs -> False", b._sustained_flow_live("E") is False)
# K configurable
b=bot(K=5); windows(b,[10,10,10,10,10]); chk("K=5: 5 consecutive -> True", b._sustained_flow_live("E") is True)
b=bot(K=5); windows(b,[10,10,10,10,5]); chk("K=5: 5th window <10 -> False", b._sustained_flow_live("E") is False)

print("\n=== CAZWAL / VEDMIC tape validation ===")
# CAZWAL @08:13: isolated 1-min premarket spike -> [10,0,0] -> no latch (hold); real start sustained -> [10,10,10] -> latch
b=bot(); windows(b,[10,0,0]); chk("CAZWAL 08:13 false burst -> NO latch (bid rests, fills corridor dip)", b._sustained_flow_live("E") is False)
b=bot(); windows(b,[10,10,10]); chk("CAZWAL ~09:21 real start -> latch", b._sustained_flow_live("E") is True)
# VEDMIC @15:56: 2-min burst -> [10,10,0] -> no latch (only 2 consecutive); 15:57 sustained -> latch
b=bot(); windows(b,[10,10,0]); chk("VEDMIC 15:56 2-min burst -> NO latch (<3 consecutive)", b._sustained_flow_live("E") is False)
b=bot(); windows(b,[10,10,10]); chk("VEDMIC 15:57 sustained -> latch (then grace +5min, NOT extended to +24min crash)", b._sustained_flow_live("E") is True)

print("\n=== byte-identical OFF (cancel-site gate) ===")
# replicate the cancel-site expression; OFF must call _is_match_live, never _sustained_flow_live
calls={"sf":0,"im":0}
class Probe(LiveV3):
    def __init__(s,on): s.sustained_flow_latch=on
    def _sustained_flow_live(s,et): calls["sf"]+=1; return "SF"
    def _is_match_live(s,et): calls["im"]+=1; return "IM"
def gate(s,et): return (s._sustained_flow_live(et) if s.sustained_flow_latch else s._is_match_live(et))
p=Probe(False); r=gate(p,"E"); chk("OFF -> gate returns _is_match_live, _sustained_flow_live NOT called", r=="IM" and calls["sf"]==0 and calls["im"]==1)
calls={"sf":0,"im":0}; p=Probe(True); r=gate(p,"E"); chk("ON -> gate returns _sustained_flow_live", r=="SF" and calls["sf"]==1 and calls["im"]==0)

print("\n=== isolation: cancel-latch-only (window-open + other consumers untouched) ===")
src=open("live_v4.py").read()
chk("_is_match_live still defined (unchanged for placement/ride/staircase)", "def _is_match_live(self, et):" in src)
gk=src[src.index("def _sustained_flow_live"):src.index("def _paired_basis_ok")]
# strip the docstring (prose mentions the words); check EXECUTABLE access only
gk_code = gk[gk.index(chr(34)*3, gk.index(chr(34)*3)+3)+3:]   # everything after the closing docstring
chk("_sustained_flow_live code accesses NO self.event_start_time (window-open untouched)", "self.event_start_time" not in gk_code)
chk("_sustained_flow_live code computes NO tts/scheduled clock", "tts" not in gk_code and "event_start_time" not in gk_code)
# [C-SUSTAINED-FLOW OBS] now 2 cancel-site uses: the _live source + the observability _sfw gate -- BOTH at the cancel block
_sf_lines=[i for i,l in enumerate(src.split(chr(10))) if "if self.sustained_flow_latch" in l]
chk("sustained_flow_latch gated ONLY at the cancel site (2 uses: _live source + obs gate, adjacent)", len(_sf_lines)==2 and (_sf_lines[1]-_sf_lines[0])<=15)
# _trade_times live wiring
chk("_trade_times init on LiveV3 (live, not paper)", "self._trade_times: Dict[str, deque] = defaultdict(deque)" in src)

print("\nALL PASS" if ok else "\nFAILURES"); import sys; sys.exit(0 if ok else 1)
