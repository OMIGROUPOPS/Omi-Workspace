#!/usr/bin/env python3
# Tests for the 2026-07-03 latch/walk dispatch: latch_tape_override (item 2), premarket_walk_cap
# (item 4), freeze_at_gun SHELVED marker (item 3). Proves default-OFF byte-identical + correct-when-on.
import sys, os, types, importlib.util
LIVE = sys.argv[1] if len(sys.argv) > 1 else "live_v4.py"
sys.path.insert(0, os.path.dirname(os.path.abspath(LIVE)) or ".")
SRC = open(LIVE, encoding="utf-8", errors="replace").read()
fails = []
def check(name, cond, msg=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  -- {msg}" if (msg and not cond) else ""))
    if not cond: fails.append(name)

# ---- 1) flags default OFF ----
check("premarket_walk_cap_off", 'self.premarket_walk_cap = bool(self.config.get("premarket_walk_cap", False))' in SRC)
check("latch_tape_override_off", 'self.latch_tape_override = bool(self.config.get("latch_tape_override", False))' in SRC)
check("freeze_at_gun_shelved_marked", "SHELVED per doctrine audit" in SRC and "grace_kill owns the hold+cut" in SRC)

# ---- 2) guarded in-source ----
check("walkcap_guarded", 'if getattr(self, "premarket_walk_cap", False):' in SRC and 'self._walk_cap_cents(pos.category)' in SRC)
check("walkcap_after_reach", SRC.index("reach_repost_capped") < SRC.index("premarket_walk_capped"))
check("latch_override_guarded", 'getattr(self, "latch_tape_override", False)' in SRC
      and "recent >= LATCH_TAPE_OVERRIDE_BURST" in SRC and "self._max_ref_move(et) >= LATCH_TAPE_OVERRIDE_MOVE_CENTS" in SRC)
check("latch_constants", "LATCH_TAPE_OVERRIDE_BURST = 30" in SRC and "LATCH_TAPE_OVERRIDE_MOVE_CENTS = 15" in SRC)

# ---- 3) import + pure/integration ----
spec = importlib.util.spec_from_file_location("live_v4_mod", LIVE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
LiveV3 = mod.LiveV3

# _walk_cap_cents per-cat
stub = object.__new__(LiveV3); stub.premarket_walk_cap_by_cat = {}
caps = {c: LiveV3._walk_cap_cents(stub, c) for c in ("ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL","ITF_M","ITF_W")}
check("walkcap_main2", caps["ATP_MAIN"] == 2 and caps["WTA_MAIN"] == 2)
check("walkcap_chall3", caps["ATP_CHALL"] == 3 and caps["WTA_CHALL"] == 3)
check("walkcap_itf4", caps["ITF_M"] == 4 and caps["ITF_W"] == 4)
stub2 = object.__new__(LiveV3); stub2.premarket_walk_cap_by_cat = {"ITF_M": 6}
check("walkcap_config_override", LiveV3._walk_cap_cents(stub2, "ITF_M") == 6)

# ---- integration: _is_match_live latch override (controlled clock) ----
Book = mod.Book
T = [1_000_000.0]
orig_time = mod.time.time
mod.time.time = lambda: T[0]
try:
    def make_stub(override, recent_n):
        s = object.__new__(LiveV3)
        et = "KXITFWMATCH-26JUL03LOPCLA"
        legs = [et + "-LOP", et + "-CLA"]
        s.event_start_time = {et: T[0] + 4000.0}       # tts = +4000s > 1800 floor
        s.event_tickers = {et: legs}
        # recent_n trades in the last 60s on leg-0
        s._trade_times = {legs[0]: [T[0] - i for i in range(recent_n)], legs[1]: []}
        s._window_open = {legs[0]: {"price": 65}, legs[1]: {"price": 36}}
        b = Book.__new__(Book) if hasattr(Book, "__new__") else Book()
        # mid = 45 -> |45-65| = 20 >= 15 override move bar
        b.best_bid, b.best_ask = 44, 46
        s.books = {legs[0]: b}
        s._events_live = set(); s._live_stage1 = {}; s._live_suppress_logged = set()
        s._live_skip_logged = set()
        s.latch_tape_override = override
        s._log = lambda *a, **k: None
        s._fv_burst_snapshot = lambda *a, **k: None
        return s, et
    # OFF: floor hard-blocks even with a 40-print gun
    s, et = make_stub(False, 40)
    check("latch_off_floor_blocks", LiveV3._is_match_live(s, et) is False)
    # ON but weak burst (20 < 30): override bar unmet -> still blocked
    s, et = make_stub(True, 20)
    check("latch_on_weak_blocked", LiveV3._is_match_live(s, et) is False)
    # ON strong burst (40 >= 30) + move 20 >= 15: stage-1 arms (False), then confirm -> True
    s, et = make_stub(True, 40)
    first = LiveV3._is_match_live(s, et)      # arms stage1
    T[0] += 70.0                              # >60 gap, <300 ttl
    s._trade_times[et + "-LOP"] = [T[0] - i for i in range(40)]  # keep the burst live
    second = LiveV3._is_match_live(s, et)     # confirm
    check("latch_on_stage1_false", first is False)
    check("latch_on_confirm_true", second is True and et in s._events_live)
finally:
    mod.time.time = orig_time

print()
if fails:
    print(f"FAILED {len(fails)}: {fails}"); sys.exit(1)
print("ALL PASS")
