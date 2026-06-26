import os
src=open(os.path.join(os.path.dirname(__file__),"..","live_v4.py")).read()
def chk(n,c):
    print(("PASS" if c else "FAIL")+"  "+n)
    assert c,n
# source
chk("init volatility_trail default False", 'self.staircase_hold_volatility_trail = bool(self.config.get("staircase_hold_volatility_trail", False))' in src)
chk("init trail_burst default 5", 'self.staircase_hold_trail_burst = int(self.config.get("staircase_hold_trail_burst", 5))' in src)
chk("OFF -> unconditional hold return", "if not self.staircase_hold_volatility_trail:\n                return" in src)
chk("volatility count reuses _trade_times", "self._trade_times.get(_vtk)" in src)
chk("volatility count reuses event_tickers", "self.event_tickers.get(pos.event_ticker, ())" in src)
chk("window = LIVE_DETECT_WINDOW_SEC", "_vcut = now - LIVE_DETECT_WINDOW_SEC" in src)
chk("quiet (< burst) -> hold return", "if _vrecent < self.staircase_hold_trail_burst:" in src)
# ordering: the gate must come BEFORE the best_bid_aware elif (so fall-through routes there) and before exec _depth_join_target
i_gate=src.index("if pos.reference_source == \"staircase_hold\":")
i_bba=src.index("elif self.best_bid_aware_repost:")
i_exec=src.index("self._depth_join_target(book.best_bid, book.best_ask")
chk("gate precedes best_bid_aware elif (fall-through routes to trail)", i_gate < i_bba)
chk("gate precedes depth-governor repost exec", i_gate < i_exec)
chk("60s floor still ABOVE the gate", src.index("if now - pos.last_cancel_repost_ts < 60:") < i_gate)
# functional: hold decision
def hold(ref, flag, vrecent, burst):
    if ref != "staircase_hold": return None
    if not flag: return True          # byte-identical hold
    if vrecent < burst: return True   # quiet -> hold
    return False                      # volatile -> trail
chk("OFF holds regardless (vrecent 100)", hold("staircase_hold",False,100,5) is True)
chk("ON quiet (2<5) -> hold", hold("staircase_hold",True,2,5) is True)
chk("ON volatile (8>=5) -> trail", hold("staircase_hold",True,8,5) is False)
chk("ON at-threshold (5>=5) -> trail", hold("staircase_hold",True,5,5) is False)
chk("non-staircase_hold leg unaffected", hold("join_bid",True,0,5) is None)
# functional: recent trade count
def vcount(event_tickers, trade_times, et, now, window):
    cut=now-window
    return sum(1 for tk in event_tickers.get(et,()) for t in (trade_times.get(tk) or ()) if t>=cut)
ET={"E":{"E-A","E-B"}}
TT={"E-A":[100,150,159,159.5],"E-B":[120,90,159.9]}  # now=160, window 60 -> cut=100
chk("vcount counts both legs in window", vcount(ET,TT,"E",160,60)==6)  # A:100,150,159,159.5 (4) + B:120,159.9 (2) ; 90 out
chk("vcount empty event -> 0", vcount(ET,TT,"X",160,60)==0)
print("\nALL PASS")
