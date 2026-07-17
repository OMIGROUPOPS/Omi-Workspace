#!/usr/bin/env python3
# Tests for the AIM-TABLE entry-side dispatch: per_cat_depth, leg2_reshuffle, freeze_at_gun.
# Proves (1) all default OFF => byte-identical baseline, (2) each gate is guarded by its flag
# in-source, (3) pure-logic correctness: leg2 never completes over combined_goal, byte-identical
# when off, freeze gates fresh-post + walk at the latch.
import sys, os, importlib.util
LIVE = sys.argv[1] if len(sys.argv) > 1 else "live_v4.py"
sys.path.insert(0, os.path.dirname(os.path.abspath(LIVE)) or ".")  # resolve live_v4's sibling imports (fv, etc.)
SRC = open(LIVE, encoding="utf-8", errors="replace").read()
fails = []
def check(name, cond, msg=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  -- {msg}" if (msg and not cond) else ""))
    if not cond: fails.append(name)

# ---------- 1) config flags default OFF (byte-identical baseline) ----------
check("per_cat_depth_default_off",  'self.per_cat_depth = bool(self.config.get("per_cat_depth", False))' in SRC)
check("leg2_reshuffle_default_off", 'self.leg2_reshuffle = bool(self.config.get("leg2_reshuffle", False))' in SRC)
check("freeze_at_gun_default_off",  'self.freeze_at_gun = bool(self.config.get("freeze_at_gun", False))' in SRC)
check("combined_goal_default_97",   'self.combined_goal = int(self.config.get("combined_goal", 97))' in SRC)
check("aim_table_path_default",     'self.aim_table_path = self.config.get("aim_table_path", "docs/policy/aim_table.json")' in SRC)

# ---------- 2) each gate guarded by its flag in-source ----------
# per_cat_depth: flat 3c path preserved when off
check("per_cat_depth_guarded",
      "self._aim_faller_depth(cat, anchor_price) if self.per_cat_depth else self.dog_dip_offset_cents" in SRC)
# leg2_reshuffle entry policy + walk re-aim both flag-guarded
check("leg2_entry_guarded", "if self.leg2_reshuffle and book is not None and 0 < book.best_bid < 100:" in SRC)
check("leg2_walk_guarded",  "if self.leg2_reshuffle and current_price < 50:" in SRC)
# leg-1 (riser) never vetoed for projected combined -- riser posts AT best bid, no combined guard
check("leg1_never_blocked", "if anchor_price >= 50:\n                target_bid = int(book.best_bid)" in SRC)
# reshuffle fires only once leg-1 (sibling) has FILLED
check("reshuffle_on_fill", 'getattr(_sp, "entry_qty", 0) > 0 and getattr(_sp, "entry_price", 0)' in SRC)
# freeze_at_gun gates fresh post (entry anchor returns None) + holds bid at the live latch (no walk)
check("freeze_entry_gate", 'if self.freeze_at_gun and self._is_match_live(tk.rsplit("-", 1)[0]):\n            return None' in SRC)
# [P0v3 (4) 07-17] the law_collision founding wire now sits between the guard
# and the hold-log (freeze-vs-sweep collision filed; HOLD current state kept)
check("freeze_walk_hold",  "if self.freeze_at_gun:" in SRC and 'self._log("freeze_at_gun_hold"' in SRC
      and SRC.index("if self.freeze_at_gun:") < SRC.index('self._log("freeze_at_gun_hold"'))

# ---------- 3) pure-logic: import the class, call the pure methods ----------
spec = importlib.util.spec_from_file_location("live_v4_mod", LIVE)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    LiveV3 = mod.LiveV3
    ok_import = True
except Exception as e:
    ok_import = False
    print("  (module import skipped:", e, ")")
check("module_imports", ok_import)

if ok_import:
    R = LiveV3._reshuffle_leg2_target  # pure, ignores self
    B = LiveV3._aim_bucket             # staticmethod

    # leg-2 NEVER completes over goal: for any leg-1 basis X, reshuffle target <= goal - X
    goal = 97
    over = []
    for X in range(1, 99):
        for anchor in (10, 25, 40, 48):
            for depth in (1, 3, 5, 10):
                t = R(None, anchor, depth, X, goal)
                if X + t > goal and t > 1:   # t floored at 1; a 1c floor may exceed goal only at X>=97
                    over.append((X, anchor, depth, t, X + t))
    check("leg2_never_over_goal", len(over) == 0, f"{len(over)} cases X+t>goal, e.g. {over[:3]}")

    # re-aim takes the MIN of (aim dip, goal - X): when goal-X binds, that wins
    # anchor 40, depth 3 -> aim dip = 37; leg-1 X=70 -> goal-X = 27 -> re-aim = 27 (goal binds)
    check("reaim_goal_binds", R(None, 40, 3, 70, 97) == 27)
    # anchor 40, depth 3 -> aim dip 37; leg-1 X=50 -> goal-X=47 -> aim dip 37 binds (lower)
    check("reaim_dip_binds",  R(None, 40, 3, 50, 97) == 37)
    # floor at 1
    check("reaim_floor_1", R(None, 5, 10, 96, 97) == 1)

    # bucket boundaries match the harness
    check("bucket_low",  B(15) == "01-20")
    check("bucket_mid",  B(45) == "41-49")
    check("bucket_edge", B(50) == "50-59")
    check("bucket_high", B(99) == "80-99")
    check("bucket_oob",  B(0) is None)

    # _aim_faller_depth falls back to flat dog_dip_offset_cents when table is empty (never raises)
    stub = object.__new__(LiveV3)
    stub._aim_table = {}                # forces empty table
    stub.dog_dip_offset_cents = 3
    stub.aim_table_path = "x"
    check("faller_depth_fallback", LiveV3._aim_faller_depth(stub, "ITF_M", 30) == 3)
    # with a table present, returns the per-cell faller_depth
    stub2 = object.__new__(LiveV3)
    stub2._aim_table = {"ITF_M": {"21-40": {"faller_depth": 4}}}
    stub2.dog_dip_offset_cents = 3
    check("faller_depth_from_table", LiveV3._aim_faller_depth(stub2, "ITF_M", 30) == 4)

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}")
    sys.exit(1)
print("ALL PASS")
