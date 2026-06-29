#!/usr/bin/env python3
"""[C-PAIR-GOVERNOR rev] tests: pure scoot-target decision + dead-input-fix wiring + byte-identical OFF."""
import os, dataclasses, types
import live_v4
from live_v4 import LiveV3, Position
src=open(os.path.join(os.path.dirname(__file__),"..","live_v4.py")).read()
ok=True
def chk(n,c):
    global ok; print(("  [PASS] " if c else "  [FAIL] ")+n); ok=ok and c

def bot(cents=1):
    b=object.__new__(LiveV3); b.pair_governor_scoot_cents=cents; return b
T=bot()._pair_governor_scoot_target   # bound pure helper (reads pair_governor_scoot_cents=1)

print("=== pure _pair_governor_scoot_target (the decision) ===")
# over par -> scoot to under_par (combined<=99)
chk("over-par (basis70+bid35=105) -> 29 (combined 99)", T(70,35,40,False)==29)
# firming (DAEVAS): basis62 bid33 ask36 -> 33-1=32 (combined 94)
chk("firming DAEVAS (basis62 bid33) -> 32", T(62,33,36,True)==32)
# under par + not firming -> None (hold -> completion)
chk("under-par + not firming (95) -> None (hold)", T(62,33,36,False) is None)
# never-cross: over par, ask caps below under_par -> ask-1 (strict maker)
chk("never-cross: basis40 bid61(101) ask55 -> 54 (<ask, combined 94)", T(40,61,55,True)==54)
# floor: bid 1 firming -> None (nothing lower)
chk("floor bid1 firming -> None", T(50,1,10,True) is None)
# marginal complete (cannot reach under par): basis99 bid5(104) ask10 -> 1 (never refuse)
chk("marginal: basis99 bid5(104) -> 1 (complete at best, never refuse)", T(99,5,10,True)==1)
# never refuse: returns a lowered target whenever it fires + room (not None when scoot possible)
chk("over-par always returns a (lowered) target, never None when room", T(80,30,40,False)==19 and 19<30)

print("\n=== DEAD-INPUT FIX: ref field live on Position + tape-sourced cur ===")
pf={f.name for f in dataclasses.fields(Position)}
chk("last_trade_price_at_post IS a Position field", "last_trade_price_at_post" in pf)
chk("3 placement constructs STAMP it live (gated)", src.count("last_trade_price_at_post=((self._fv_anchor_price(tk) or 0) if self.pair_governor_scoot else 0)")==3)
chk("_save persists it (gated + sparse)", 'if self.pair_governor_scoot and pos.last_trade_price_at_post:' in src and 'out[tk]["last_trade_price_at_post"] = pos.last_trade_price_at_post' in src)
chk("_load restores it", 'last_trade_price_at_post=int(d.get("last_trade_price_at_post", 0))' in src)
body=src[src.index("async def _pair_governor_scoot_eval"):src.index("    def _pair_governor_scoot_target")]
# code-level: book1 var fully removed (no book.last_trade_price access); cur from the tape. (Docstring prose mentions the recorder field -> check code, not prose.)
code=body[body.index(chr(34)*3, body.index(chr(34)*3)+3)+3:]   # after the closing docstring
chk("eval cur from TAPE (_fv_anchor_price), book1/recorder access removed", "cur = self._fv_anchor_price(tk)" in body and "book1" not in code)
chk("eval ref from live-stamped last_trade_price_at_post", 'ref = int(getattr(leg1, "last_trade_price_at_post", 0) or 0)' in body)

print("\n=== firing model: EVERY leg-1 fill (not firming-only) ===")
chk("no firming-only early-return gate (old 'not (ref>0 and cur>0 and cur>ref)' removed)", "not (ref > 0 and cur > 0 and cur > ref)" not in body)
chk("fires via combined-OR-firming in the pure helper", "over_par = (int(this_basis) + int(cur_bid)) >= 100" in src and "if not (over_par or firming):" in src)

print("\n=== byte-identical OFF + completion mutual-exclusion ===")
chk("placement stamp gated (=0 when OFF, no _fv call)", "if self.pair_governor_scoot else 0)" in src)
chk("save key gated under flag (OFF -> legacy save shape)", "if self.pair_governor_scoot and pos.last_trade_price_at_post:" in src)
chk("hook gated + scoots BEFORE completion (returns -> mutually exclusive)",
    'if self.pair_governor_scoot and await self._pair_governor_scoot_eval(tk, et, this_basis, sib, sp):\n            return' in src)
i_hook=src.index("if self.pair_governor_scoot and await self._pair_governor_scoot_eval")
i_comp=src.index("await self._attempt_completion_reprice(tk, et, this_basis, sib, sp)")
chk("hook precedes completion (scoot DOWN vs completion UP)", i_hook < i_comp)
chk("OFF byte-identical: completion path intact", "if not self.completion_reprice or self.completion_disabled:\n            return\n        await self._attempt_completion_reprice(tk, et, this_basis, sib, sp)" in src)
chk("re-lay = cancel v2 + re-post (never refuse: always re-lays lower)",
    '_cancel_entry_and_resolve(sib, sp, "pair_governor_scoot"' in body and 'self.place_order(sib, "buy", "yes", new_target' in body)

print("\nALL PASS" if ok else "\nFAILURES"); import sys; sys.exit(0 if ok else 1)
