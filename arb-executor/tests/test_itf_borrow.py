#!/usr/bin/env python3
"""STEP-3 test [C-ITF-BORROW]. Real LiveV3._entry_cat + _itf_recent_volume_ok (live _trade_notional).
Includes attribute-exists-on-LiveV3 checks (the volume_tracker-was-PaperApi-only lesson)."""
import types, inspect
import live_v4
from live_v4 import LiveV3, ITF_EXIT_BORROW, ITF_VISIBILITY_CATS
from collections import deque
NOW=1_000_000.0
def bot(on, floor=500.0, win=90):
    b=object.__new__(LiveV3)
    b.itf_entry_borrow=on; b.itf_min_recent_vol_usd=floor; b.itf_recent_vol_window_min=win
    b._trade_notional={}; b.event_tickers={}
    return b
ET="KXITFMATCH-26JUN27OJALEA"; A=ET+"-OJA"; B=ET+"-LEA"
def setn(b,na,nb):
    b.event_tickers={ET:{A,B}}; b._trade_notional={A:deque(na),B:deque(nb)}
ok=True
def chk(l,c):
    global ok; print(f"  [{'PASS' if c else 'FAIL'}] {l}"); ok=ok and c
print("=== _entry_cat (gated name map) ===")
chk("OFF: ITF_M->ITF_M (skips as today)", bot(False)._entry_cat("ITF_M")=="ITF_M")
chk("ON: ITF_M->ATP_CHALL", bot(True)._entry_cat("ITF_M")=="ATP_CHALL")
chk("ON: ITF_W->WTA_CHALL", bot(True)._entry_cat("ITF_W")=="WTA_CHALL")
chk("ON: ATP_MAIN native", bot(True)._entry_cat("ATP_MAIN")=="ATP_MAIN")
chk("map == ITF_EXIT_BORROW", ITF_EXIT_BORROW=={"ITF_M":"ATP_CHALL","ITF_W":"WTA_CHALL"})
print("=== _itf_recent_volume_ok (live _trade_notional; entries (ts, price*count)) ===")
b1=bot(True); setn(b1,[(NOW-60,60*500)],[(NOW-120,40*600)])
chk("recent $540/90min -> True", b1._itf_recent_volume_ok(ET,NOW) is True)
b2=bot(True); setn(b2,[(NOW-7200,60*500)],[(NOW-7400,40*600)])
chk("high-cumulative-but-0-recent -> False (the trap)", b2._itf_recent_volume_ok(ET,NOW) is False)
b3=bot(True); setn(b3,[(NOW-60,50*100)],[])
chk("thin recent ($50) -> False", b3._itf_recent_volume_ok(ET,NOW) is False)
b4=bot(True); setn(b4,[(NOW-60,60*500)],[(NOW-60,60*500)])
chk("both legs summed -> True", b4._itf_recent_volume_ok(ET,NOW) is True)
print("=== WIRING: attributes exist on the LIVE LiveV3 (the volume_tracker lesson) ===")
chk("_trade_notional in LiveV3.__init__", "_trade_notional" in inspect.getsource(LiveV3.__init__))
at=inspect.getsource(LiveV3.apply_trade)
chk("apply_trade populates _trade_notional gated on itf_entry_borrow", "_trade_notional" in at and "itf_entry_borrow" in at)
chk("helper reads _trade_notional (not volume_tracker)", "_trade_notional" in inspect.getsource(LiveV3._itf_recent_volume_ok) and "volume_tracker" not in inspect.getsource(LiveV3._itf_recent_volume_ok))
chk("ITF_VISIBILITY_CATS == (ITF_M,ITF_W)", set(ITF_VISIBILITY_CATS)=={"ITF_M","ITF_W"})
print("RESULT:", "ALL PASS" if ok else "FAILURES")
import sys; sys.exit(0 if ok else 1)
