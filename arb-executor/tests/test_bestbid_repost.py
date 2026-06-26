import os,re
src=open(os.path.join(os.path.dirname(__file__),"..","live_v4.py")).read()
def chk(n,c): print(("PASS" if c else "FAIL")+"  "+n); assert c,n
# source-level
chk("init flag default False", 'self.best_bid_aware_repost = bool(self.config.get("best_bid_aware_repost", False))' in src)
chk("trigger: best_bid_aware elif present", 'elif self.best_bid_aware_repost:' in src)
chk("trigger: best-bid mismatch compares pos.target_price",
    'if max(1, min(book.best_bid, book.best_ask - 1)) == pos.target_price:' in src)
chk("legacy mid-deadband elif STILL present (byte-identical OFF path)",
    'elif abs(current_price - price_basis) <= V4_REPRICE_MOVE_CENTS:' in src)
chk("exec: engagement re-joins under flag", 'if pos.play_type != "v4_engagement_join" or self.best_bid_aware_repost:' in src)
chk("60s floor preserved", 'if now - pos.last_cancel_repost_ts < 60:' in src)
chk("never-cross _reprice_target preserved", 'new_target, po = self._reprice_target(new_target, current_ask)' in src)
# ordering: best_bid_aware elif must come BEFORE the legacy deadband elif
i1=src.index('elif self.best_bid_aware_repost:'); i2=src.index('elif abs(current_price - price_basis)')
chk("best_bid_aware elif precedes legacy deadband elif", i1<i2)
# functional replication of the trigger HOLD decision (offset/engagement catch-all branch)
def hold(best_bid,best_ask,target_price,mid_delta,flag):
    # True = HOLD (no repost). staircase/join_bid branches handled separately.
    if flag:
        return max(1,min(best_bid,best_ask-1))==target_price
    return mid_delta<=5   # V4_REPRICE_MOVE_CENTS legacy
# flag OFF = byte-identical legacy (mid deadband)
chk("OFF small mid-move (2c) -> HOLD (legacy)", hold(32,34,21,2,False)==True)
chk("OFF big mid-move (7c) -> REPOST (legacy)", hold(32,34,21,7,False)==False)
# flag ON
chk("ON stranded-LOW (bid32/ask34, ours21) -> REPOST", hold(32,34,21,2,True)==False)
chk("ON stranded lone-TOP (bid25/ask27, ours32 after support pulled) -> REPOST", hold(25,27,32,1,True)==False)
chk("ON at-touch (bid32/ask34, ours32) -> HOLD (FIFO)", hold(32,34,32,0,True)==True)
chk("ON at-touch capped ask-1 (locked 50/50, ours49) -> HOLD", hold(50,50,49,0,True)==True)
chk("ON DAEVAS-DAE replay (bid67/ask71, ours58) -> REPOST", hold(67,71,58,4,True)==False)
print("\nALL PASS")
