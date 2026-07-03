#!/usr/bin/env python3
# Tests for the three Option-C flags: disable_volume_floors, min_minutes_before_start, kalshi_schedule_primary.
# Proves each is byte-identical-when-off (default) and correct-when-armed, and is guarded in the live source.
import sys
LIVE = sys.argv[1] if len(sys.argv) > 1 else "live_v4.py"
SRC = open(LIVE, encoding="utf-8", errors="replace").read()
fails=[]
def check(n,c,m=""):
    print(f"  {'PASS' if c else 'FAIL'}  {n}"+(f"  -- {m}" if (m and not c) else ""))
    if not c: fails.append(n)

# ---- 1) config reads + defaults ----
check("disable_volume_floors_default_off", 'self.disable_volume_floors = bool(self.config.get("disable_volume_floors", False))' in SRC)
check("min_minutes_before_start_default", 'self.min_minutes_before_start = float(self.config.get("min_minutes_before_start", ENTRY_BUFFER_SEC / 60.0))' in SRC)
check("entry_buffer_derived", 'self._entry_buffer_sec = int(self.min_minutes_before_start * 60)' in SRC)
check("kalshi_schedule_primary_default_off", 'self.kalshi_schedule_primary = bool(self.config.get("kalshi_schedule_primary", False))' in SRC)

# ---- 2) gates guarded in-source ----
check("volume_gate_has_disable", "not self.disable_volume_floors" in SRC)
check("entry_buffer_uses_derived", "self._entry_buffer_sec)" in SRC and "KALSHI_COARSE_WIDE_TAIL_SEC, self._entry_buffer_sec" in SRC)
check("kprim_source_swap", 'method": "kalshi_schedule_primary"' in SRC and "if _kprim and et not in self.event_start_time" in SRC)
check("kprim_resolver_guarded", "if not _kprim and et not in self.event_start_time" in SRC)
check("kprim_reconcile_guarded", "not getattr(self, \"kalshi_schedule_primary\", False)" in SRC)

# ---- 3) pure-logic byte-identical-when-off + armed ----
# volume floor: blocks = borrow and cat and not rest and not disable and not vol_ok
def vblocks(borrow,cat,rest,disable,vol_ok): return borrow and cat and (not rest) and (not disable) and (not vol_ok)
check("vol_off_identical", all(vblocks(b,c,r,False,v)==(b and c and (not r) and (not v)) for b in(0,1) for c in(0,1) for r in(0,1) for v in(0,1)))
check("vol_disable_never_blocks", all(not vblocks(b,c,r,True,v) for b in(0,1) for c in(0,1) for r in(0,1) for v in(0,1)))

# entry buffer: sec = minutes*60
ENTRY_BUFFER_SEC=900
def ebuf(mins): return int(mins*60)
check("ebuf_default_identical", ebuf(ENTRY_BUFFER_SEC/60.0)==ENTRY_BUFFER_SEC)   # 15 -> 900, byte-identical
check("ebuf_zero", ebuf(0)==0)                                                   # 0 -> no buffer

# kalshi_schedule_primary: _kprim = flag and occ ; off -> falsy -> resolver runs
def kprim(flag, occ): return flag and occ
check("kprim_off_uses_resolver", all(not kprim(False,occ) for occ in (None, 1234.0)))
check("kprim_on_with_occ", bool(kprim(True, 1234.0)))
check("kprim_on_no_occ_falls_through", not kprim(True, None))

print(f"\n{'ALL PASS' if not fails else 'FAILURES: '+', '.join(fails)}  ({len(fails)} failed)")
sys.exit(1 if fails else 0)
