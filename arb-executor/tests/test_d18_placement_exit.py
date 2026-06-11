#!/usr/bin/env python3
"""D18 regression: placement-path instant-fill is booked + an exit is posted at source
(TRASQU NO_EXIT, placement-side). A post_only=False cross that fills ON PLACEMENT must NOT
be left phase=entry_resting (which the match_start_buffer cleanup would strand naked).
Also asserts the helper is idempotent and the fallback path's own handler is unchanged.
Run: cd arb-executor && python3 tests/test_d18_placement_exit.py"""
import sys, types, asyncio
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)


def make_self():
    s = types.SimpleNamespace(n_entries=0, exit_calls=[], sib_calls=[], saved=0)
    async def apply_exit(tk, pos, price, filled):
        s.exit_calls.append((tk, price, filled))
    async def cancel_sib(tk, et, price):
        s.sib_calls.append((tk, et, price))
    s._v4_apply_exit = apply_exit
    s._cancel_sibling_if_paired_over_cap = cancel_sib
    s._save_v4_resting = lambda: setattr(s, "saved", s.saved + 1)
    s._log = lambda *a, **k: None
    s._book_placement_cross_fill = types.MethodType(M.LiveV3._book_placement_cross_fill, s)
    return s


def make_pos(is_v4=True, exit_order_id=""):
    return types.SimpleNamespace(entry_qty=0, phase="entry_resting", entry_filled_ts=0,
        cell_name="", direction="leader", play_type="v4_miss_fallback", is_v4=is_v4,
        event_ticker="KXATPCHALLENGERMATCH-26JUN03SHEBRA", exit_order_id=exit_order_id)


def run(coro):
    # [C-P0-RACE fixture hygiene] close the loop -- leaked loops GC at exit and
    # py3.12 raises "Invalid file descriptor: -1" on the double-closed self-pipe
    # (surfaced on the VPS once live_v4 grew; harness bug, not product code).
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# 1. instant fill on placement -> booked + exit posted at source (the SHEBRA-SHE case)
s = make_self(); pos = make_pos()
resp = {"order": {"fill_count_fp": "5.00", "status": "executed"}}
r = run(s._book_placement_cross_fill("TK", pos, resp, 73))
check(r is True, "instant-fill: returns True (booked)")
check(pos.phase == "active", "instant-fill: phase flipped entry_resting -> active (not stranded)")
check(pos.entry_qty == 5, "instant-fill: entry_qty = 5 (booked the fill)")
check(s.exit_calls == [("TK", 73, 5)], "instant-fill: _v4_apply_exit called with anchor 73, qty 5")
check(s.sib_calls == [("TK", "KXATPCHALLENGERMATCH-26JUN03SHEBRA", 73)], "instant-fill: sibling over-cap backstop called")
check(s.n_entries == 1, "instant-fill: n_entries incremented")

# 2. no fill on placement (rested) -> no booking, no exit (phase stays entry_resting for the poll)
s = make_self(); pos = make_pos()
r = run(s._book_placement_cross_fill("TK", pos, {"order": {"fill_count_fp": "0"}}, 73))
check(r is False, "no-fill: returns False")
check(pos.phase == "entry_resting" and not s.exit_calls, "no-fill: not booked, no exit posted")

# 3. idempotent: an exit already exists -> do not double-post
s = make_self(); pos = make_pos(exit_order_id="abc")
r = run(s._book_placement_cross_fill("TK", pos, {"order": {"fill_count_fp": "5.00"}}, 73))
check(r is False and not s.exit_calls, "idempotent: exit_order_id set -> no second exit")

# 4. defensive: missing/None response -> no crash, no booking
s = make_self(); pos = make_pos()
check(run(s._book_placement_cross_fill("TK", pos, None, 73)) is False, "None resp -> False, no crash")
check(run(s._book_placement_cross_fill("TK", pos, {}, 73)) is False, "empty resp -> False, no crash")

# 5. non-v4 position: books the fill but does NOT post a v4 exit (guarded)
s = make_self(); pos = make_pos(is_v4=False)
r = run(s._book_placement_cross_fill("TK", pos, {"order": {"fill_count_fp": "5.00"}}, 73))
check(r is True and pos.entry_qty == 5 and not s.exit_calls, "non-v4: booked, no v4 exit (is_v4 guard)")

# 6. fallback path untouched: its own instant-fill handler still reads fill_count_fp inline
src = (REPO / "live_v4.py").read_text(errors="replace")
check(src.count("INSTANT TAKER FILL (TRASQU NO_EXIT fix)") == 1, "fallback path's TRASQU handler still present (unchanged)")
check("source\": \"t20m_instant_fill" in src, "fallback path still logs t20m_instant_fill (byte-intact)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
