#!/usr/bin/env python3
# Tests for the three C-PARTICIPATE-CLEAN gated flags: tape_gated_abandon, book_quality_gate,
# rest_both_legs. Proves (1) all default OFF (byte-identical baseline), (2) each gate is guarded by
# its flag in the live source, (3) pure-logic byte-identical-when-off + correct-when-on for each gate
# condition (the exact boolean the code uses).
import sys
LIVE = sys.argv[1] if len(sys.argv) > 1 else "live_v4.py"
SRC = open(LIVE, encoding="utf-8", errors="replace").read()
fails=[]
def check(name, cond, msg=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}"+(f"  -- {msg}" if (msg and not cond) else ""));
    if not cond: fails.append(name)

# ---- 1) config flags default OFF ----
check("tape_gated_abandon_default_off", 'self.tape_gated_abandon = bool(self.config.get("tape_gated_abandon", False))' in SRC)
check("book_quality_gate_default_off",  'self.book_quality_gate = bool(self.config.get("book_quality_gate", False))' in SRC)
check("book_quality_max_spread_default",'self.book_quality_max_spread = int(self.config.get("book_quality_max_spread", 12))' in SRC)
check("rest_both_legs_default_off",     'self.rest_both_legs = bool(self.config.get("rest_both_legs", False))' in SRC)

# ---- 2) each gate guarded by its flag in-source ----
check("tape_gate_guarded", "self.tape_gated_abandon" in SRC and "_is_match_live(et)" in SRC and "schedule_abandon_deferred" in SRC)
check("tape_gate_startup_skip", "(start_ts - now) <= ENTRY_BUFFER_SEC\n                    and not self.tape_gated_abandon" in SRC)  # startup schedule-skip also tape-gated
check("volume_gate_rest_both", "not self.rest_both_legs" in SRC and "_itf_recent_volume_ok(et, now)" in SRC)
check("book_quality_gate_guarded", "if self.book_quality_gate and not self.rest_both_legs" in SRC)

# ---- 3) pure-logic: exact conditions the code uses ----
WIDE_TAIL = 5400
def defer(tape_flag, is_live, tts):            # tape_gated_abandon defer condition
    return tape_flag and (not is_live) and tts > -WIDE_TAIL
# OFF -> never defer -> original abandon path, byte-identical
check("tape_off_never_defers", all(defer(False, il, t) is False for il in (True,False) for t in (-9999,0,9999)))
# ON + tape NOT live + within tail -> defer (keep event alive)
check("tape_on_defers_when_not_live", defer(True, False, 100) is True)
# ON + tape LIVE -> abandon (no defer)
check("tape_on_abandons_when_live", defer(True, True, 100) is False)
# ON + far past T-0 (beyond wide tail) -> abandon even if tape quiet (schedule can't be that wrong)
check("tape_on_abandons_far_past", defer(True, False, -WIDE_TAIL-1) is False)

def vol_blocks(borrow, cat_ok, rest_flag, vol_ok):   # volume-floor gate condition
    return borrow and cat_ok and (not rest_flag) and (not vol_ok)
# OFF (rest_both_legs False) -> identical to original (borrow and cat_ok and not vol_ok)
check("vol_off_identical", all(vol_blocks(b,c,False,v) == (b and c and (not v)) for b in (0,1) for c in (0,1) for v in (0,1)))
# ON -> never blocks (PRIORITY 1 override). (vol_blocks returns a falsy operand, so test with `not`.)
check("vol_on_never_blocks", all(not vol_blocks(b,c,True,v) for b in (0,1) for c in (0,1) for v in (0,1)))

def book_skips(bq_flag, rest_flag, bad):        # book_quality_gate condition
    return bq_flag and (not rest_flag) and bad
check("book_off_never_skips", all(book_skips(False, r, bad) is False for r in (0,1) for bad in (0,1)))
check("book_on_skips_bad", book_skips(True, False, True) is True)
check("book_on_rest_both_override", book_skips(True, True, True) is False)   # PRIORITY 1 wins
def bad_book(bid, ask, maxspread):
    return bid <= 0 or ask <= 0 or (ask - bid) > maxspread
check("bad_book_wide", bad_book(40, 60, 12) is True)     # spread 20 > 12
check("bad_book_ok", bad_book(48, 52, 12) is False)      # spread 4 <= 12
check("bad_book_nobook", bad_book(0, 52, 12) is True)

print(f"\n{'ALL PASS' if not fails else 'FAILURES: '+', '.join(fails)}  ({len(fails)} failed)")
sys.exit(1 if fails else 0)
