#!/usr/bin/env python3
"""Test for [C-LIQUID-REPOST]. Real LiveV3 helper + real Book + real join/depth helpers."""
import types, live_v4
from live_v4 import LiveV3, Book

def bot(on=False, maxgap=15, depth=True, floor=50):
    b=object.__new__(LiveV3)
    b.liquid_repost_at_touch=on
    b.bestbid_follow_at_touch=False     # isolate: FIX-1 off so we exercise the new elif branch
    b.best_bid_aware_repost=True
    b.bestbid_follow_max_gap=maxgap
    b.depth_aware_join=depth
    b.depth_aware_floor=floor
    b.depth_aware_floor_by_cat={}
    return b
def pos(tp,cat="ATP_CHALL"): return types.SimpleNamespace(target_price=tp, category=cat)
ok=True
def chk(label,cond):
    global ok; print(f"  [{'PASS' if cond else 'FAIL'}] {label}"); ok=ok and cond

# KUMLAG-LAG-style: touch 34 thin (<floor), depth rolls to 32 (>=floor). our resting bid 33 (gap=34-33=1).
B=Book(bids={34:20,33:30,32:80}, best_bid=34, best_ask=36)
dj,_=bot(on=True)._depth_join_target(34,36,B.bids,50); touch,_=bot(on=True)._join_target(34,36)
print(f"depth_target={dj} (rolls below touch) touch={touch}")
chk("setup: depth rolls 34->32, touch=34", dj==32 and touch==34)

print("\n=== helper _liquid_repost_at_touch_applies ===")
chk("OFF -> False (byte-identical)", bot(on=False)._liquid_repost_at_touch_applies(B,pos(33),dj,touch) is False)
chk("ON, roll-down + small gap(1) -> True (sit at touch)", bot(on=True)._liquid_repost_at_touch_applies(B,pos(33),dj,touch) is True)
chk("ON, gap<=0 phantom (our bid 40 above touch) -> True", bot(on=True)._liquid_repost_at_touch_applies(B,pos(40),dj,touch) is True)
# depth already at touch (no roll) -> nothing to suppress
chk("ON, depth_target==touch (no roll) -> False", bot(on=True)._liquid_repost_at_touch_applies(B,pos(33),touch,touch) is False)
# run-away: our resting bid 18, touch 34 -> gap 16 > 15 -> don't chase
chk("ON, run-away gap16>15 -> False (don't chase)", bot(on=True)._liquid_repost_at_touch_applies(B,pos(18),dj,touch) is False)
chk("ON, boundary gap==15 -> True", bot(on=True)._liquid_repost_at_touch_applies(B,pos(19),dj,touch) is True)
chk("ON, boundary gap==16 -> False", bot(on=True)._liquid_repost_at_touch_applies(B,pos(18),dj,touch) is False)

print("\n=== effective repost target (mirrors the patched branch) ===")
def eff(b,book,p):
    # FIX-1 off in this bot, so exercise the elif depth_aware_join branch
    if b.depth_aware_join:
        _dj,_=b._depth_join_target(book.best_bid,book.best_ask,book.bids,b._depth_floor(p.category))
        _t,_=b._join_target(book.best_bid,book.best_ask)
        if b._liquid_repost_at_touch_applies(book,p,_dj,_t): return _t
        return _dj
    return b._join_target(book.best_bid,book.best_ask)[0]
on_t=eff(bot(on=True),B,pos(33)); off_t=eff(bot(on=False),B,pos(33))
print(f"  KUMLAG-LAG-style: OFF target={off_t} (depth-roll, strands) ON target={on_t} (sits at touch)")
chk("ON sits at touch=34 (fix), OFF rolls to 32 (byte-identical)", on_t==34 and off_t==32)
# run-away: OFF and ON identical (both keep depth path, don't chase)
on_r=eff(bot(on=True),B,pos(18)); off_r=eff(bot(on=False),B,pos(18))
chk("run-away: ON==OFF (no chase, depth path stands)", on_r==off_r==32)

print("\n=== initial placement preserved (depth helper still rolls down) ===")
chk("INITIAL depth_join still rolls 34->32 (lone-top job intact)", bot()._depth_join_target(34,36,B.bids,50)[0]==32)

print("\nALL PASS" if ok else "\nFAILURES"); 
import sys; sys.exit(0 if ok else 1)
