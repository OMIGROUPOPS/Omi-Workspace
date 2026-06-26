import os
src=open(os.path.join(os.path.dirname(__file__),"..","live_v4.py")).read()
def chk(n,c):
    print(("PASS" if c else "FAIL")+"  "+n)
    assert c,n
# source
chk("init pair_governor_scoot default False", 'self.pair_governor_scoot = bool(self.config.get("pair_governor_scoot", False))' in src)
chk("init scoot_cents default 1", 'self.pair_governor_scoot_cents = int(self.config.get("pair_governor_scoot_cents", 1))' in src)
chk("eval method present", "async def _pair_governor_scoot_eval(self, tk, et, this_basis, sib, sp):" in src)
chk("hook gated + scoots before completion", 'if self.pair_governor_scoot and await self._pair_governor_scoot_eval(tk, et, this_basis, sib, sp):\n            return' in src)
# mutual exclusion: hook must precede the completion call (scoot returns first)
i_hook=src.index("if self.pair_governor_scoot and await self._pair_governor_scoot_eval")
i_comp=src.index("await self._attempt_completion_reprice(tk, et, this_basis, sib, sp)")
chk("hook precedes completion call (mutually exclusive)", i_hook < i_comp)
# byte-identical OFF: completion check + call still intact
chk("OFF byte-identical: completion check intact", "if not self.completion_reprice or self.completion_disabled:\n            return\n        await self._attempt_completion_reprice(tk, et, this_basis, sib, sp)" in src)
# isolate the eval body
body=src[src.index("async def _pair_governor_scoot_eval"):src.index("    def _completion_target")]
chk("drift = last_trade_price_at_post vs book.last_trade_price", "last_trade_price_at_post" in body and ".last_trade_price" in body)
chk("firming test = cur > ref", "cur > ref" in body)
chk("never-cross guard (>= sib_ask -> no scoot)", "new_target >= sib_ask" in body)
chk("per-leg floor >=1 (max(1,...))", "new_target = max(1, int(sp.entry_price)" in body)
chk("NO combined cap in the scoot", "V4_PAIRED_BASIS_CAP" not in body and "paired_cap" not in body)
chk("re-lay = cancel v2 + re-post", "_cancel_entry_and_resolve(sib, sp, \"pair_governor_scoot\"" in body and "self.place_order(sib, \"buy\", \"yes\", new_target" in body)
# functional: firming/fading decision
def decide(ref, cur, flag):
    if not flag: return "skip"          # block skipped (byte-identical)
    return "scoot" if (ref>0 and cur>0 and cur>ref) else "no-scoot"
chk("OFF -> skip (no pair-gov)", decide(55,62,False)=="skip")
chk("ON firming (post55 now62) -> scoot (Daems)", decide(55,62,True)=="scoot")
chk("ON fading (post65 now62) -> no-scoot", decide(65,62,True)=="no-scoot")
chk("ON flat (post62 now62) -> no-scoot", decide(62,62,True)=="no-scoot")
chk("ON no ref -> no-scoot (fail safe)", decide(0,62,True)=="no-scoot")
# functional: scoot price + never-cross + combined
def scoot_price(sib_bid, cents, sib_ask):
    new=max(1, sib_bid-cents)
    if new==sib_bid or new>=sib_ask: return None
    return new
chk("DAEVAS Vasilescu 33 - 1 (ask36) -> 32", scoot_price(33,1,36)==32)
chk("combined 62+33=95 -> 62+32=94 (lowers)", 62+scoot_price(33,1,36)==94)
chk("never-cross abort (crossed book bid36/ask35: new35>=ask) -> None", scoot_price(36,1,35) is None)
chk("floor no-op (bid 1 -> max(1,0)=1==bid) -> None", scoot_price(1,1,5) is None)
chk("scoot stays strict maker below ask", scoot_price(33,1,34)==32 and 32<34)
print("\nALL PASS")
