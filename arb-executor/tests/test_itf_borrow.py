#!/usr/bin/env python3
"""STEP-3 test [C-ITF-BORROW]. Real LiveV3._entry_cat + _itf_recent_volume_ok + ITF_EXIT_BORROW map."""
import types
import live_v4
from live_v4 import LiveV3, ITF_EXIT_BORROW, ITF_VISIBILITY_CATS
from collections import deque

NOW=1_000_000.0
def bot(on, floor=500.0, win=90):
    b=object.__new__(LiveV3)
    b.itf_entry_borrow=on; b.itf_min_recent_vol_usd=floor; b.itf_recent_vol_window_min=win
    b.volume_tracker=types.SimpleNamespace(trades={})
    b.event_tickers={}
    return b
ok=True
def chk(l,c):
    global ok; print(f"  [{'PASS' if c else 'FAIL'}] {l}"); ok=ok and c

print("=== _entry_cat (gated name map) ===")
boff=bot(False); bon=bot(True)
chk("OFF: ITF_M -> ITF_M (native, skips as today)", boff._entry_cat("ITF_M")=="ITF_M")
chk("OFF: ATP_CHALL -> ATP_CHALL", boff._entry_cat("ATP_CHALL")=="ATP_CHALL")
chk("ON: ITF_M -> ATP_CHALL", bon._entry_cat("ITF_M")=="ATP_CHALL")
chk("ON: ITF_W -> WTA_CHALL", bon._entry_cat("ITF_W")=="WTA_CHALL")
chk("ON: ATP_MAIN unchanged (native)", bon._entry_cat("ATP_MAIN")=="ATP_MAIN")
chk("map matches ITF_EXIT_BORROW (same name map both sides)", ITF_EXIT_BORROW=={"ITF_M":"ATP_CHALL","ITF_W":"WTA_CHALL"})

print("\n=== _itf_recent_volume_ok (RECENT in-window, not cumulative) ===")
ET="KXITFMATCH-26JUN27OJALEA"; A=ET+"-OJA"; B=ET+"-LEA"
def setvol(b,trades_a,trades_b):
    b.event_tickers={ET:{A,B}}
    b.volume_tracker.trades={A:deque(trades_a),B:deque(trades_b)}
# recent: A $300 (60,500) 1min ago + B $240 (40,600) 2min ago = $540 within 90min
b1=bot(True)
setvol(b1,[(NOW-60,60,500,"sell")],[(NOW-120,40,600,"buy")])
chk("recent >=$500/90min -> True (allow)", b1._itf_recent_volume_ok(ET,NOW) is True)
# DEAD-IN-WINDOW trap: same $ but 2h ago (outside 90min window)
b2=bot(True)
setvol(b2,[(NOW-7200,60,500,"sell")],[(NOW-7400,40,600,"buy")])
chk("high cumulative but 0 in last 90min -> False (the trap)", b2._itf_recent_volume_ok(ET,NOW) is False)
# thin: only $50 recent
b3=bot(True)
setvol(b3,[(NOW-60,50,100,"sell")],[])
chk("thin recent ($50) -> False (skip thin game)", b3._itf_recent_volume_ok(ET,NOW) is False)
# both legs counted: A $300 + B $300 = $600
b4=bot(True)
setvol(b4,[(NOW-60,60,500,"sell")],[(NOW-60,60,500,"buy")])
chk("both legs summed (300+300=600) -> True", b4._itf_recent_volume_ok(ET,NOW) is True)
# window edge: trade exactly at boundary (90min) excluded if < since
b5=bot(True,win=90)
setvol(b5,[(NOW-90*60-1,99,1000,"sell")],[])  # just-too-old big trade
chk("trade just outside window -> not counted -> False", b5._itf_recent_volume_ok(ET,NOW) is False)

print("\n=== categories_enabled gate semantics (config-load: ON adds ITF) ===")
chk("ITF_VISIBILITY_CATS == (ITF_M, ITF_W)", set(ITF_VISIBILITY_CATS)=={"ITF_M","ITF_W"})

print("\nRESULT:", "ALL PASS" if ok else "FAILURES")
import sys; sys.exit(0 if ok else 1)
