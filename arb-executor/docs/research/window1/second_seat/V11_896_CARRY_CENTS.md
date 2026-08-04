# Carry priced in cents — the 359 disjoint ceiling events

Analysis seat only. Descriptive. Read-only. A tape walk of the held (earlier-
reachable) leg across the carry, for the 359 DISJOINT events in
`EXECUTABLE_CEILING_EVENTS.csv` (commit b0e89437). Per-event rows in
`CARRY_CENTS_EVENTS.csv`; all numbers in `CARRY_CENTS_SUMMARY.json`.

## Band source (cited, not invented)

Exit bands scored against the deployed, git-tracked table
**`arb-executor/data/durable/spike_volatility_map/{category}_adaptive_exit_bands.parquet`**,
loaded by `arb-executor/live_v4.py::_load_exit_table` (line 5122) and applied by
`exit_rule_for` (line 5464). Schema `price_low, price_high, band_exit_X`;
`band_exit_X` is **"+X cents for exit cells"** (`live_v4.py:660`) — a fill-relative
offset, so the exit band absolute = `fill_cents + X`. `HOLD` cells carry no band
(hold to resolution). One definition for all legs; all four categories here are
native (no ITF borrow). This is the live system's own exit surface, not a
constructed one.

## Method, mark convention, conservation

Held leg = the earlier-reachable leg (fills at its `maker_floor`). Carry window =
`[held first-reachable, other first-reachable]` (fill → completion). Mark = **mid**.
`net_drift = mid(completion) − fill`; MAE/MFE = min/max(`mid − fill`) over the
carry; **band touched = best_bid reaches `fill + X`** during the carry (the
residency-exit mirror of the entry: a buyer stepping to your resting sell).
Budget buckets use the committed `carry_gap_seconds`.

**Acceptance: PASS.** 359 scored, 0 unscored; **31 (OVERLAP) + 359 (DISJOINT) =
390**; each event in exactly one bucket (`≤1h 106 · ≤2h 55 · ≤4h 86 · ≤8h 60 ·
>8h 52`). MTM present on 340/359 (19 have a zero-length carry — fill and
completion coincide, e.g. a seller-aggressed-instant fill — so no mid samples).

## Does the mirror's recovery subsidize the carry? — yes, both sides

Net drift sign, fill→completion:

| you carry the… | n | favorable (drift up) | adverse | flat | median drift |
|---|---:|---:|---:|---:|---:|
| DEARER leg (favorite) | 211 | **203** | 1 | 7 | +2.0¢ |
| CHEAPER leg | 128 | **123** | 0 | 5 | +2.0¢ |

**~96% of carries drift favorably, regardless of which side you hold.** The held
leg fills at its dip (the maker floor is the low), and it recovers while you wait
for the sibling — the recovery phase subsidizes the carry. Only **1 of 340** carries
ends net-negative (−0.5¢). This is largely the entry-at-floor selection working as
designed, not free alpha, but it means sequential legging is far less punishing in
cents than in hours.

## Per carry-budget bucket × side (medians, cents)

| bucket | side | n | med net | med MAE | med MFE | band-touched | HOLD cells |
|---|---|---:|---:|---:|---:|---:|---:|
| ≤1h | DEARER | 62 | +1.2 | −0.5 | +1.5 | 11 | 3 |
| ≤1h | CHEAPER | 44 | +1.0 | −0.5 | +1.0 | 3 | 3 |
| ≤2h | DEARER | 36 | +1.5 | −0.5 | +1.5 | 7 | 7 |
| ≤2h | CHEAPER | 18 | +1.5 | −0.5 | +1.5 | 0 | 3 |
| ≤4h | DEARER | 48 | +1.5 | −0.2 | +2.0 | 9 | 4 |
| ≤4h | CHEAPER | 38 | +1.5 | +0.5 | +1.8 | 1 | 7 |
| ≤8h | DEARER | 39 | +2.5 | 0.0 | +3.5 | 8 | 3 |
| ≤8h | CHEAPER | 21 | +2.5 | +0.2 | +2.8 | 1 | 1 |
| >8h | DEARER | 34 | +5.5 | +0.5 | +5.5 | 12 | 1 |
| >8h | CHEAPER | 18 | +4.0 | +0.2 | +4.2 | 3 | 1 |

Median MAE hovers at −0.5 to +0.5¢ across every bucket — the typical carry barely
goes against you. Favorable drift and MFE grow with the wait (the longer you hold,
the more the leg recovers), and the >8h bucket carries the most anomalous windows.

## Harvested winner vs true exposure

A carry whose mark reaches the exit band is a harvested winner, not an exposure:

| bucket | banded carries | band touched | true exposure | touch % |
|---|---:|---:|---:|---:|
| ≤1h | 100 | 14 | 86 | 14% |
| ≤2h | 45 | 7 | 38 | 16% |
| ≤4h | 75 | 10 | 65 | 13% |
| ≤8h | 56 | 9 | 47 | 16% |
| >8h | 51 | 15 | 36 | 29% |

Overall **55 of 327 banded carries (17%) touch the exit band**; 32 events sit in
HOLD cells (no band defined). So most carries drift up a couple of cents but do
**not** reach the full harvest (band offsets X run a median 12-29¢ by category);
the favorable drift is real but small relative to the exit target. Per category:
ATP_CHALL 19/152 touched, ATP_MAIN 20/82, WTA_MAIN 7/63, WTA_CHALL 9/30.

## The adverse tail (not buried)

The medians are benign, but the distribution has a left tail: MAE min −31¢, p10
−1.5¢, and **8 carries dipped ≥5¢ against you mid-carry (5 ≥10¢, 3 ≥20¢** —
BARVIS −31, VALCAS −25, BOOONC −22.5). Almost all mean-reverted by completion:
those same legs finished net 0 to +29¢ (BOOONC MAE −22.5 → net +29). Net drift is
negative on exactly one event. So the risk is a transient intra-carry drawdown on
a handful of held favorites, not a realized loss at completion in this window.

## Reading

Priced in cents, the single-leg carry is cheap and favorable-biased: you fill at
the floor, the leg recovers a median +2¢ (~96% favorable, both sides), the typical
worst mark is −0.5¢, and 17% of the time the mark reaches the deployed exit band
outright (a harvest, not an exposure). The executable ceiling's "92% sequential-
only" is a statement about *timing lockability*, not about *dollar risk* — the
carry the sequencing forces is, in this window, a mild positive-drift hold with a
small mean-reverting adverse tail. What it is not is a simultaneous arb: the cents
are favorable in expectation, but they are directional exposure, not a locked pair.

## Artifacts

`CARRY_CENTS_EVENTS.csv` (per event: held leg, fill, exit-band X and absolute,
net drift, MAE, MFE, band-touched) and `CARRY_CENTS_SUMMARY.json` under
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/`.
