#!/usr/bin/env python3
"""STEP-3 test for [C-BESTBID-FOLLOW] FIX 1. Real LiveV3 predicate + real Book + real join helpers."""
import types
import live_v4
from live_v4 import LiveV3, Book

def bot(on=True, bbaware=True, maxgap=15, depth=True, floor=50):
    b=object.__new__(LiveV3)
    b.bestbid_follow_at_touch=on
    b.best_bid_aware_repost=bbaware
    b.bestbid_follow_max_gap=maxgap
    b.depth_aware_join=depth
    b.depth_aware_floor=floor
    b.depth_aware_floor_by_cat={}
    return b
def pos(tp, cat="ATP_CHALL"):
    return types.SimpleNamespace(target_price=tp, category=cat)

ok=True
def chk(label,cond):
    global ok; print(f"  [{'PASS' if cond else 'FAIL'}] {label}"); ok=ok and cond

# CREMCD-CRE book: 60-touch thin (25sh<floor), 55 thick (80), 54 (100). ask 62.
CRE=Book(bids={60:25,55:80,54:100}, best_bid=60, best_ask=62)

print("=== helpers (real) on the CREMCD-CRE book ===")
dj,_=bot()._depth_join_target(60,62,CRE.bids,50)
jt,_=bot()._join_target(60,62)
print(f"  _depth_join_target -> {dj} (rolls down off thin 60-touch)   _join_target -> {jt} (AT touch)")
chk("depth-roll lands 55 (below touch), join lands 60 (AT touch)", dj==55 and jt==60)

print("\n=== predicate _bestbid_follow_at_touch_applies ===")
# (2) ON small-gap thin (our bid 54, touch 60, gap 6)
chk("ON small-gap upward (gap6<=15) -> applies True", bot(on=True)._bestbid_follow_at_touch_applies(CRE,pos(54)) is True)
# (1) OFF -> never applies (even small-gap)
chk("OFF -> applies False (byte-identical path)", bot(on=False)._bestbid_follow_at_touch_applies(CRE,pos(54)) is False)
# best_bid_aware off -> never applies
chk("best_bid_aware OFF -> applies False", bot(on=True,bbaware=False)._bestbid_follow_at_touch_applies(CRE,pos(54)) is False)
# (3) large-gap directional run-away (our 80, touch ->99): gap 19 > 15
RUN=Book(bids={99:5},best_bid=99,best_ask=100)
chk("ON large-gap (gap19>15, directional) -> applies False (no chase)", bot(on=True)._bestbid_follow_at_touch_applies(RUN,pos(80)) is False)
# (4) down-move (touch 50 below our 55): gap -5
DN=Book(bids={50:30},best_bid=50,best_ask=53)
chk("ON down-move (gap<=0) -> applies False", bot(on=True)._bestbid_follow_at_touch_applies(DN,pos(55)) is False)
# boundary gap==maxgap and gap==maxgap+1
B15=Book(bids={69:5},best_bid=69,best_ask=71)
chk("boundary gap==15 -> applies True", bot(on=True)._bestbid_follow_at_touch_applies(B15,pos(54)) is True)
B16=Book(bids={70:5},best_bid=70,best_ask=72)
chk("boundary gap==16 -> applies False", bot(on=True)._bestbid_follow_at_touch_applies(B16,pos(54)) is False)

print("\n=== effective target the repost would use (predicate -> join vs depth-roll) ===")
def eff(b,book,p):
    if b._bestbid_follow_at_touch_applies(book,p): return b._join_target(book.best_bid,book.best_ask)[0]
    return (b._depth_join_target(book.best_bid,book.best_ask,book.bids,b._depth_floor(p.category))[0] if b.depth_aware_join else b._join_target(book.best_bid,book.best_ask)[0])
on_t=eff(bot(on=True),CRE,pos(54)); off_t=eff(bot(on=False),CRE,pos(54))
print(f"  CREMCD-CRE: OFF target={off_t} (depth-roll, the bug)   ON target={on_t} (joins touch, the fix)")
chk("ON joins touch=60 (fixes 55), OFF stays 55 (byte-identical)", on_t==60 and off_t==55)
# (6) initial placement (depth helper) still rolls down -- unchanged
chk("INITIAL placement (depth_join helper) still rolls 60->55 (preserved)", bot()._depth_join_target(60,62,CRE.bids,50)[0]==55)

print("\nRESULT:", "ALL PASS" if ok else "FAILURES")
import sys; sys.exit(0 if ok else 1)
