import os
src=open(os.path.join(os.path.dirname(__file__),"..","live_v4.py")).read()
def chk(n,c):
    print(("PASS" if c else "FAIL")+"  "+n)
    assert c,n
chk("init depth_aware_join default False", 'self.depth_aware_join = bool(self.config.get("depth_aware_join", False))' in src)
chk("init depth_aware_floor default 50", 'self.depth_aware_floor = int(self.config.get("depth_aware_floor", 50))' in src)
chk("per-cat floor dict", 'self.depth_aware_floor_by_cat = dict(self.config.get("depth_aware_floor_by_cat", {}))' in src)
chk("method _depth_join_target present", "def _depth_join_target(self, best_bid, best_ask, bids, floor):" in src)
chk("_depth_floor helper present", "def _depth_floor(self, cat):" in src)
chk("legacy _join_target UNCHANGED 1-liner", "return max(1, min(int(best_bid), int(best_ask) - 1)), True" in src)
chk("snapshot conditional on flag", "placement_bids = dict(book.bids) if self.depth_aware_join else None" in src)
chk("placement gated x2", src.count("if self.depth_aware_join else self._join_target(placement_bid, placement_ask)")==2)
chk("repost gated", "if self.depth_aware_join else self._join_target(book.best_bid, book.best_ask)" in src)
chk("walks DOWN only (pp <= base)", "for pr in sorted((pp for pp in bids if pp <= base), reverse=True):" in src)
# functional replication
def djt(bb,ba,bids,floor,flag):
    base=max(1,min(bb,ba-1))
    if not flag or not bids: return base
    for pr in sorted((pp for pp in bids if pp<=base),reverse=True):
        if bids.get(pr,0)>=floor: return max(1,pr)
    return base
chk("OFF -> base regardless of depth", djt(55,58,{55:3,54:9000},50,False)==55)
chk("OFF 1c book -> ask-1", djt(55,56,{55:3},50,False)==55)
chk("ON best-bid thick (>=floor) -> best_bid", djt(55,58,{55:200,54:9},50,True)==55)
chk("ON thin top -> roll to lower wall", djt(60,62,{60:8,59:12,58:120},50,True)==58)
chk("ON no depth -> fall back base", djt(55,58,{55:5,54:10},50,True)==55)
chk("ON 1c book roll -> 54 (<ask56 never-cross)", djt(55,56,{55:5,54:300},50,True)==54)
chk("Nedic 287@43 vs floor 50 -> sit 43 (wall)", djt(43,45,{43:287,42:1472,41:2662},50,True)==43)
chk("Nedic vs floor 300 -> roll to 42", djt(43,45,{43:287,42:1472,41:2662},300,True)==42)
chk("Nedic vs floor 2000 -> roll to 41", djt(43,45,{43:287,42:1472,41:2662},2000,True)==41)
print("\nALL PASS")
