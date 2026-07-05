#!/usr/bin/env python3
"""[C-BOUND-RULING 2026-07-05] The operator-adjudicated bound unification, tested to
its three bars (exhaustive sweeps, no mocks of the functions under test):

  BAR 1  no path can produce a >97 resting completion
         (_completion_target, _reshuffle_leg2_target, reaim/fallback bound arithmetic)
  BAR 2  no cross completion >100 combined  (cross_bounds_ok)
  BAR 3  no cross fill outside 5-95c        (cross_bounds_ok leg range)

Run from arb-executor root:  python3 tests/test_bound_ruling.py
Exit 0 = all bars hold. Non-zero = the ruling is violated; do not deploy.

Coverage notes (choreography, not arithmetic -- asserted against config here):
- the <=2c noise band is owned by cancels/skips, not pricing: reaim_on_sibling_arrival
  CANCELS the sibling at leg-1 booking when goal - basis <= 2 (live_v4 ~3631);
  _repost_missing_siblings SKIPS level <= 2; the T-20m fallback stays FLAT at
  bound <= 2. The walk-site max(1,.) clamp is unreachable for over-goal combos while
  reaim_on_sibling_arrival is armed -- asserted below from the live config.
- V3 tripwire now fires on completion fills with combined > combined_goal
  (boot-grace: first V4_COMPLETION_FRESHNESS_SEC+120s after start_ts log-only,
  so pre-ruling recovered bids cannot kill the mechanism on stale law)."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import live_v4 as lv

FAILS = []
def bar(name, cond, detail=""):
    if not cond:
        FAILS.append((name, detail))
        print("FAIL  %s  %s" % (name, detail))
    else:
        print("pass  %s" % name)

class Stub:
    combined_goal = 97

GOAL = 97

# ---- BAR 1a: _completion_target -- every branch, exhaustive ----
worst = None
for basis in range(1, 100):
    for s0 in range(1, 96):
        for x in (0, 1, 2, 3, 5, 8, 15, 30):
            for ask in (None, 1, 2, 6, 40, 94, 96, 99):
                s1 = lv.LiveV3._completion_target(Stub(), s0, x, ask, basis)
                # callers drop s1 < 1 (no_headroom) and never-cross clamps handle ask
                if s1 >= 1 and s1 + basis > GOAL:
                    worst = (basis, s0, x, ask, s1)
bar("BAR1a completion_target <= 97-basis on all branches", worst is None, str(worst))

# flags must NOT alter the bound (ruling: unified on EVERY branch)
class StubFlags(Stub):
    paired_cap_enforced = True
    completion_combined_ceiling = False
worst = None
for basis in range(1, 100):
    for s0 in (1, 20, 50, 90):
        s1 = lv.LiveV3._completion_target(StubFlags(), s0, 30, None, basis)
        if s1 >= 1 and s1 + basis > GOAL:
            worst = (basis, s0, s1)
bar("BAR1b completion_target flag-independent (99 ceiling dead)", worst is None, str(worst))

# ---- BAR 1c: _reshuffle_leg2_target bounded wherever a bid may legally rest ----
# (bound <= 2 is owned by the reaim-on-arrival CANCEL, asserted from config below)
worst = None
for basis in range(1, 95):           # goal_level >= 3 <=> basis <= 94
    if GOAL - basis <= 2:
        continue
    for anchor in range(1, 100):
        for depth in (0, 1, 2, 3, 5, 8):
            t = lv.LiveV3._reshuffle_leg2_target(Stub(), anchor, depth, basis, GOAL)
            if t + basis > GOAL:
                worst = (basis, anchor, depth, t)
bar("BAR1c reshuffle_leg2_target <= 97-basis (bound>=3 domain)", worst is None, str(worst))

# ---- BAR 2 + 3: the emergency cross ----
viol2 = viol3 = None
allowed = []
for sib in range(1, 100):
    for ask in range(1, 100):
        ok = lv.cross_bounds_ok(sib, ask)
        if ok:
            allowed.append((sib, ask))
            if sib + ask > 100:
                viol2 = (sib, ask)
            if not (5 <= ask <= 95):
                viol3 = (sib, ask)
bar("BAR2 cross combined <= 100", viol2 is None, str(viol2))
bar("BAR3 cross leg inside 5-95c", viol3 is None, str(viol3))

# the named dead classes
bar("IEMBER class dead (4+98=102)", not lv.cross_bounds_ok(4, 98))
bar("DELNIC class dead (23+78=101)", not lv.cross_bounds_ok(23, 78))
bar("MUCKRE fallback class dead at cross too (38+72=110)", not lv.cross_bounds_ok(38, 72))
# boundary case DISCLOSED (verbatim ruling: <=100 AND 5-95 leaves 6+94=100 alive)
print("note  DALARI boundary (6+94=100, leg 94 in-range): %s under verbatim ruling"
      % ("ALIVE" if lv.cross_bounds_ok(6, 94) else "dead"))

# constants pinned to the ruling
bar("cap constant == 100", lv.ENTRY_COMPLETE_BASIS_CAP == 100)
bar("leg range constants == (5, 95)", (lv.CROSS_LEG_MIN, lv.CROSS_LEG_MAX) == (5, 95))

# ---- config choreography assertions (the <=2 band owner must be armed) ----
cfg = json.load(open(ROOT / "config" / "deploy_v5_live.json"))
bar("config: reaim_on_sibling_arrival armed (owns bound<=2 cancels)",
    cfg.get("reaim_on_sibling_arrival") is True)
bar("config: fallback_pair_bound armed", cfg.get("fallback_pair_bound") is True)
bar("config: combined_goal == 97", int(cfg.get("combined_goal", 97)) == 97)

# ---- V3 tripwire: fires on >goal after boot grace, log-only inside it ----
class TripStub:
    combined_goal = 97
    paired_cap_enforced = False
    completion_cells = {}
    logged = None
    def _log(self, ev, det, ticker=""):
        self.logged = (ev, det)
class PosStub:
    completion_leg1_basis = 60
    completion_lookup_cell = 1
    completion_all_cells_arm = True
    entry_price = 39
    category = "ATP_CHALL"
ts = TripStub(); ps = PosStub()
ts.start_ts = time.time() - (lv.V4_COMPLETION_FRESHNESS_SEC + 121)
v = lv.LiveV3._completion_fill_guards(ts, ps, 39, False)
bar("V3 clean fill (60+39=99? no: bound test)", v is not None and v[0] == "V3_goal_breach",
    "60+39=99>97 must breach post-grace, got %s" % (v,))
v = lv.LiveV3._completion_fill_guards(ts, ps, 37, False)
bar("V3 at-goal fill passes (60+37=97)", v is None, str(v))
ts2 = TripStub(); ts2.start_ts = time.time()
v = lv.LiveV3._completion_fill_guards(ts2, ps, 39, False)
bar("V3 boot-grace: stale-law fill is log-only", v is None and ts2.logged is not None
    and ts2.logged[0] == "completion_goal_breach_boot_grace", str(v))

print()
if FAILS:
    print("BOUND RULING: %d BAR FAILURES -- DO NOT DEPLOY" % len(FAILS))
    sys.exit(1)
print("BOUND RULING: ALL BARS HOLD")
