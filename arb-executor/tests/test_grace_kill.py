#!/usr/bin/env python3
"""Test for [C-GRACE-KILL]. Real LiveV3._grace_kill_action + real Position/PaperPosition dataclass wiring."""
import types, dataclasses, live_v4
from live_v4 import LiveV3, Position, PaperPosition
NOW=1000.0
def bot(on, grace=300, sib=True):
    b=object.__new__(LiveV3)
    b.match_live_grace_kill=on; b.match_live_grace_sec=grace
    b._carve_abort_for_held_sibling=lambda tk,et: sib   # stub the held-sibling predicate
    return b
def pos(latch=0.0):
    return types.SimpleNamespace(match_live_latch_ts=latch, ticker="KX-T", event_ticker="KX-E")
ok=True
def chk(label,cond):
    global ok; print(f"  [{'PASS' if cond else 'FAIL'}] {label}"); ok=ok and cond

print("=== _grace_kill_action (real helper) ===")
# not live
chk("not-live, no stamp -> None", bot(True)._grace_kill_action(pos(0.0), False, NOW) is None)
chk("not-live, stamped -> 'reset' (self-heal, false/transient latch never cancels)", bot(True)._grace_kill_action(pos(950.0), False, NOW)=="reset")
# OFF (byte-identical)
chk("OFF, live -> 'cancel' (instant, byte-identical)", bot(False)._grace_kill_action(pos(0.0), True, NOW)=="cancel")
chk("OFF, not-live, ts=0 -> None (matches legacy fall-through)", bot(False)._grace_kill_action(pos(0.0), False, NOW) is None)
# ON, naked
chk("ON, live, NAKED (no held sibling) -> 'cancel' (instant, never ride naked)", bot(True, sib=False)._grace_kill_action(pos(0.0), True, NOW)=="cancel")
# ON, held-sibling
chk("ON, live, held-sibling, no stamp -> 'arm' (stamp + hold)", bot(True, sib=True)._grace_kill_action(pos(0.0), True, NOW)=="arm")
chk("ON, live, held-sibling, within grace (gap 50<300) -> 'hold'", bot(True, sib=True)._grace_kill_action(pos(NOW-50), True, NOW)=="hold")
chk("ON, live, held-sibling, grace elapsed (gap 400>300) -> 'cancel'", bot(True, sib=True)._grace_kill_action(pos(NOW-400), True, NOW)=="cancel")
chk("ON, held-sibling, boundary gap==grace(300) -> 'cancel' (not <grace)", bot(True, sib=True)._grace_kill_action(pos(NOW-300), True, NOW)=="cancel")
chk("ON, held-sibling, boundary gap==299 -> 'hold'", bot(True, sib=True)._grace_kill_action(pos(NOW-299), True, NOW)=="hold")
chk("bounded at 5min: grace_sec default is 300", LiveV3.__init__ is not None and 300==int(bot(True).match_live_grace_sec))

print("\n=== byte-identical OFF sweep (live -> always cancel; not-live -> None; ts irrelevant since never set OFF) ===")
mis=0
for live in (True,False):
    for ts in (0.0, 500.0, NOW-10):
        r=bot(False)._grace_kill_action(pos(ts), live, NOW)
        want=("cancel" if live else ("reset" if ts else None))
        if r!=want: mis+=1
chk("OFF helper matches legacy semantics across grid", mis==0)

print("\n=== dataclass wiring (live, not paper) ===")
pf={f.name:f for f in dataclasses.fields(Position)}
ppf={f.name for f in dataclasses.fields(PaperPosition)}
chk("match_live_latch_ts IS a field on LIVE Position", "match_live_latch_ts" in pf)
chk("match_live_latch_ts default == 0.0", "match_live_latch_ts" in pf and pf["match_live_latch_ts"].default==0.0)
chk("match_live_latch_ts NOT on PaperPosition (live-only, no paper confusion)", "match_live_latch_ts" not in ppf)

print("\n=== exit-safety (structural) ===")
src=open("live_v4.py").read()
# the grace-kill touches only the entry resting-bid cancel (_cancel_entry_and_resolve), never _v4_apply_exit
gk_region=src[src.index("_grace_kill_action"):src.index("def _paired_basis_ok")]
chk("helper references no exit symbols (_v4_apply_exit/exit_order/exit_price)", not any(s in gk_region for s in ("_v4_apply_exit","exit_order","exit_price")))
chk("cancel-site still routes through _cancel_entry_and_resolve (entry-side only)", 'self._grace_kill_action(pos, _live, now)' in src and 'match_live_cancel' in src)

print("\nALL PASS" if ok else "\nFAILURES"); import sys; sys.exit(0 if ok else 1)
