#!/usr/bin/env python3
"""Test for [C-SUSTAINED-FLOW OBS]. Observability-only: window-counts at latch fire, zero decision change."""
import time, collections, live_v4
from live_v4 import LiveV3, LIVE_TRADE_BURST
def bot(on=True, K=3):
    b=object.__new__(LiveV3); b.sustained_flow_latch=on; b.sustained_flow_K=K
    b.event_tickers={"E":{"E-A","E-B"}}; b._trade_times=collections.defaultdict(collections.deque)
    return b
def windows(b, counts, leg="E-A"):
    now=time.time()
    for w,n in enumerate(counts):
        ts=now-w*60-30
        for _ in range(n): b._trade_times[leg].append(ts)
ok=True
def chk(label,cond):
    global ok; print(f"  [{'PASS' if cond else 'FAIL'}] {label}"); ok=ok and cond

print("=== _sustained_flow_windows (real, observability) ===")
b=bot(); windows(b,[10,12,11]); c,onset=b._sustained_flow_windows("E")
chk("returns the K per-window counts (w0=most recent) [10,12,11]", c==[10,12,11])
chk("returns oldest-window lo ts (~now-K*60)", abs(onset-(time.time()-180))<2)
b=bot(); windows(b,[10,0,0]); c,_=b._sustained_flow_windows("E"); chk("false-burst profile -> [10,0,0]", c==[10,0,0])
b=bot(K=5); windows(b,[10,10,10,10,10]); c,_=b._sustained_flow_windows("E"); chk("K=5 -> 5 counts", len(c)==5 and c==[10,10,10,10,10])
# split across legs sums per window
b=bot(); windows(b,[5,5,5],"E-A"); windows(b,[5,5,5],"E-B"); c,_=b._sustained_flow_windows("E"); chk("sums across legs -> [10,10,10]", c==[10,10,10])

print("\n=== decision logic UNCHANGED (the detector still returns bool, same verdicts) ===")
b=bot(); windows(b,[10,10,10]); chk("_sustained_flow_live still True on 3 sustained", b._sustained_flow_live("E") is True)
b=bot(); windows(b,[10,10,5]); chk("_sustained_flow_live still False on <K", b._sustained_flow_live("E") is False)
b=bot(); windows(b,[10,0,0]); chk("_sustained_flow_live still False on false-burst", b._sustained_flow_live("E") is False)

print("\n=== gate: window-counts only computed/logged when sustained_flow_latch ON ===")
# replicate the cancel-site _sfw expression
def sfw_expr(b): return (b._sustained_flow_windows("E") if b.sustained_flow_latch else None)
b=bot(on=True); windows(b,[10,10,10]); chk("ON -> _sfw computed (not None)", sfw_expr(b) is not None)
b=bot(on=False); windows(b,[10,10,10]); chk("OFF -> _sfw None (no compute, no log fields = byte-identical)", sfw_expr(b) is None)

print("\n=== source: behavior-bearing lines unchanged (observability is additive) ===")
src=open("live_v4.py").read()
chk("_live source line unchanged", "_live = (self._sustained_flow_live(pos.event_ticker) if self.sustained_flow_latch" in src)
chk("_gk decision call unchanged", "_gk = self._grace_kill_action(pos, _live, now)" in src)
chk("cancel call unchanged", 'await self._cancel_entry_and_resolve(   # _gk == "cancel"' in src)
chk("window_counts added under gate guard (if _sfw is not None)", src.count('_sfw is not None')==2)
chk("_sustained_flow_live decision body untouched (no _sfw / window_counts inside it)",
    "window_counts" not in src[src.index("def _sustained_flow_live"):src.index("def _sustained_flow_windows")])

print("\nALL PASS" if ok else "\nFAILURES"); import sys; sys.exit(0 if ok else 1)
