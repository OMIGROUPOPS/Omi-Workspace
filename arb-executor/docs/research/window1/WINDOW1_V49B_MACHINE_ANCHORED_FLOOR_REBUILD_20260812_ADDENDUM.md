# V49b machine-anchored floor rebuild

Date: 2026-08-12

Status: PASS. Measurement only; no replay-policy change and no deployment authorization.

The rebuild executes the staged `f36798fc` correction. The old `d3db740f`
table anchored placement-family triggers analytically and excluded evidence at
the trigger timestamp. On frozen V47 it reproduces the full impossible set:
213 credited legs had entry below the table's alleged causal floor. The new
table is anchored to the executable action trace's actual rest intervals. Its
floor is the minimum true trade or qualifying ask at-or-below a real rest
while that rest stood. V47 and V49b each contain zero credited legs below the
rebuilt floor.

V49b completed 405 pairs, exactly 810 credited legs. Across those legs:

- sum(entry minus rebuilt machine floor) = 100 cents; distribution
  min/p25/median/p75/p90/max = 0/0/0/0/0/8;
- sum(entry minus market-offered true-trade floor) = 3,544 cents;
- presence premium, their arithmetic difference, = 3,444 cents; distribution
  min/p25/median/p75/p90/max = 0/0/1/3/10/88.

Per category, machine-floor gap / market-offer gap / presence premium totals:

- ATP_CHALL: 42 / 1,483 / 1,441 cents across 312 legs;
- ATP_MAIN: 33 / 927 / 894 cents across 186 legs;
- WTA_CHALL: 7 / 502 / 495 cents across 118 legs;
- WTA_MAIN: 18 / 632 / 614 cents across 194 legs.

The identity conserves on all 810 rows:

`entry - market offered floor = entry - machine floor + machine floor - market offered floor`.

The result measures counterfactual replay presence: the price flow intersecting
rests the machine actually carried versus all true traded prices the recorded
market offered. It does not establish queue position, causal market impact, or
the premium a real displayed order would create. No separately SHA-pinned
V49b CC par sheet existed in fetched refs; its true-trade basis was reproduced
locally and bound beside CC's prior `096241ae` overpay census.

Two clean builds compared ten pre-determinism artifacts byte-for-byte with
zero mismatch. The unit and conservation tests pass. Forbidden access is zero.

Controlling package:

`.claude/window1_live_v4_replay/v49b_machine_anchored_floor_rebuild_20260812/`
