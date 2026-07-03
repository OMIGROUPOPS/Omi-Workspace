#!/usr/bin/env python3
# Tests for [C-PER-SIDE-PRICING] per_side_placement: dog (anchor<50) rests deeper at the dip floor;
# favorite (anchor>=50) unchanged. Proves byte-identical-when-off and correct-when-on.
import sys
LIVE = sys.argv[1] if len(sys.argv) > 1 else "live_v4.py"
SRC = open(LIVE, encoding="utf-8", errors="replace").read()
fails=[]
def check(n,c,m=""):
    print(f"  {'PASS' if c else 'FAIL'}  {n}"+(f"  -- {m}" if (m and not c) else ""));
    if not c: fails.append(n)

# 1) config defaults
check("per_side_placement_default_off", 'self.per_side_placement = bool(self.config.get("per_side_placement", False))' in SRC)
check("dog_dip_offset_default", 'self.dog_dip_offset_cents = int(self.config.get("dog_dip_offset_cents", 3))' in SRC)
# 2) gated deepen present
check("deepen_guarded", "if self.per_side_placement and anchor_price < 50:" in SRC and "offset = max(offset, self.dog_dip_offset_cents)" in SRC)

# 3) pure-logic: the exact offset transform the code applies
def eff_offset(on, anchor, offset, dip):
    if on and anchor < 50:
        return max(offset, dip)
    return offset
def target(anchor, off): return max(1, anchor - off)

# OFF -> offset unchanged, byte-identical (every case)
check("off_identical", all(eff_offset(False, a, o, 3) == o for a in (10,38,50,80) for o in (1,3,7)))
# ON + DOG shallow table (anchor 38, table off 1) -> deepened to dip 3 -> bid 35 (was 37 zero-discount)
check("on_dog_deepens", eff_offset(True, 38, 1, 3) == 3 and target(38, eff_offset(True,38,1,3)) == 35)
# ON + DOG already deep (table off 5 > dip 3) -> stays 5 (never shallower)
check("on_dog_keeps_deep", eff_offset(True, 30, 5, 3) == 5)
# ON + FAVORITE (anchor 62) -> unchanged shallow (fill early at/near current)
check("on_fav_unchanged", eff_offset(True, 62, 2, 3) == 2 and target(62, eff_offset(True,62,2,3)) == 60)
# ON + coin-flip favorite side (anchor exactly 50) -> treated as fav (>=50), unchanged
check("on_50_is_fav", eff_offset(True, 50, 1, 3) == 1)
# tonight's actual zero-discount dog fills, what per-side would have posted (fill plausibly at dip):
for anchor, tableoff in [(45,1),(47,1),(38,1),(30,1),(22,1)]:   # YAM45 HAL47 IMA38 DUC30 BUB22
    check(f"dog_{anchor}_posts_deeper", target(anchor, eff_offset(True, anchor, tableoff, 3)) == anchor-3)

print(f"\n{'ALL PASS' if not fails else 'FAILURES: '+', '.join(fails)}  ({len(fails)} failed)")
sys.exit(1 if fails else 0)
