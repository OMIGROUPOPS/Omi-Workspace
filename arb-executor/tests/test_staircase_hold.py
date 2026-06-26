# [C1-STAIRCASE-HOLD] build-contract verification (source-level, mirrors test_abort_carve discipline).
import os, re
src = open(os.path.join(os.path.dirname(__file__), "..", "live_v4.py")).read()
def chk(name, cond):
    print(("PASS" if cond else "FAIL") + "  " + name); assert cond, name
# T1: flag exists, default OFF
chk("T1 flag default OFF", 'self.staircase_hold_at_bid = self.config.get("staircase_hold_at_bid", False)' in src)
# T2: ON -> posts _join_target (at bid, not deep) + ref staircase_hold
chk("T2 ON -> _join_target + ref=staircase_hold",
    re.search(r'if self\.staircase_hold_at_bid:.*?self\._join_target\(placement_bid, placement_ask\).*?reference_source = "staircase_hold"', src, re.S) is not None)
# T3: walk early-return (HOLD, no re-quote, FIFO)
chk("T3 walk hold early-return (no re-quote)", 'if pos.reference_source == "staircase_hold":\n            return' in src)
# T4: completion excludes staircase_hold (no pay-up cancel)
chk("T4 completion excludes staircase_hold", 'if sp.reference_source == "staircase_hold":\n            return' in src)
# T5: STEP-6 excludes staircase_hold (owns its window)
chk("T5 STEP-6 excludes staircase_hold", 'not in ("staircase", "staircase_hold")' in src)
# T6: OFF byte-identical -> else branch keeps the deep-cast + ref staircase
chk("T6 OFF legacy staircase intact",
    re.search(r'else:\s*\n\s*target_bid, _ = self\._staircase_bid\(cat, cell, current_price, time_to_start, placement_bid, placement_ask\)\s*\n\s*reference_source = "staircase"', src) is not None)
# T7: abort-resolve UNCHANGED -> staircase_hold NOT in the staircase abort tally
chk("T7 abort-resolve still != staircase (hold excluded from abort)", 'if pos.reference_source != "staircase":\n            return' in src)
# T8: greppable measurement log
chk("T8 staircase_hold_place log present", '"staircase_hold_place"' in src)
# T9: hold posts at bid, NOT deep (_staircase_bid not called under the flag branch)
m = re.search(r'if self\.staircase_hold_at_bid:(.*?)else:', src, re.S)
chk("T9 hold branch does NOT deep-cast", m is not None and "_staircase_bid" not in m.group(1))
# T10: hold does NOT use the join_bid re-join walk path (it early-returns before any walk)
chk("T10 hold != join_bid re-join (distinct ref)", 'reference_source = "staircase_hold"' in src and 'reference_source = "join_bid"' in src)
print("\nALL PASS (10/10)")
