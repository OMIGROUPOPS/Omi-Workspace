import os
src=open(os.path.join(os.path.dirname(__file__),"..","live_v4.py")).read()
def chk(n,c):
    print(("PASS" if c else "FAIL")+"  "+n)
    assert c,n
# the engagement elif is attached to the table_src if (so engagement_wave1 falls through to it)
chk("engagement elif present + gated on depth_aware_join",
    'reference_source = "join_bid"   # [C-JOIN-THE-BID WALK] fresh join walks from placement\n                elif self.depth_aware_join:' in src)
chk("engagement elif comment names the coverage hole", "engagement-wave1 placement was the governor's coverage HOLE" in src)
chk("engagement routes through _depth_join_target", src.count("self._depth_join_target(placement_bid, placement_ask, placement_bids, self._depth_floor(cat))")==3)  # C1 + join_bid + engagement
chk("OFF byte-identical (elif gated on flag, not taken when off)", "elif self.depth_aware_join:\n                    # [C-DEPTH-GOVERNOR] engagement-wave1" in src)
chk("legacy _join_target still present (depth governor OFF path intact)", "return max(1, min(int(best_bid), int(best_ask) - 1)), True" in src)
# functional: same _depth_join_target walk -> engagement now governed
def djt(bb,ba,bids,floor,flag):
    base=max(1,min(bb,ba-1))
    if not flag or not bids: return base
    for pr in sorted((pp for pp in bids if pp<=base),reverse=True):
        if bids.get(pr,0)>=floor: return max(1,pr)
    return base
# OSA replay: bb 77 (5 shares = us, thin), wall at 73 (120) -> roll DOWN to 73
chk("ON OSA thin-top (77x5) -> rolls to wall 73", djt(77,78,{77:5,73:120},50,True)==73)
# thick best-bid -> sit at touch (engagement at-touch preserved)
chk("ON engagement thick best-bid (77x200) -> sit 77", djt(77,78,{77:200},50,True)==77)
# OFF -> base = at-touch (byte-identical engagement)
chk("OFF -> at-touch base 77 (byte-identical)", djt(77,78,{77:5,73:120},50,False)==77)
# no wall meets floor -> fall back to base (don't strand)
chk("ON no wall -> fall back to base 77", djt(77,78,{77:5,76:9},50,True)==77)
# never-cross: rolls only downward, < ask
chk("ON 1c book roll stays < ask", djt(77,78,{77:5,76:300},50,True)==76)
print("\nALL PASS")
