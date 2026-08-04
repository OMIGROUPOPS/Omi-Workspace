# ARNROM — one game, told at the tick

Analysis seat only. Descriptive. Read-only, from the raw tapes
`KXATPCHALLENGERMATCH-26JUL12ARNROM-{ARN,ROM}.csv.gz`. Full dual timeline (every
BBO change + every true print, both legs on one clock, both clock columns) in
`ARNROM_DUAL_TIMELINE.csv`; anchors and travel summaries in
`ARNROM_TICK_STORY_SUMMARY.json`. Inline below: the key hour; the CSV holds the
rest.

## The game

ARN is the climb side (favorite), ROM the decay side (dog). Scheduled start
`1783854000`, but the schedule lied by ~11.7h — the **actual bell is
`1783946100` (V5_EXACT_START)**, so every row carries both clocks. ARN's floor
formed at **56** and was refused; ROM was credited at **42**; at the bell ARN
closed **62** and ROM **39** (sum 101 — over par, which is why it was never a clean
joint capture). Had ARN been armed at its 56 floor and ROM at 42, the pair sums to
98 < 100 — a capture. ARN refused.

## Marks on the timeline

| epoch | t−bell | event |
|---|---|---|
| 1783896043 | +13:54:17 | ARN qualifying floor **56** forms (tape row 35592) |
| 1783896044 | +13:54:16 | ARN **refusal** receipt — `SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED` (row 35593) |
| 1783896551 | +13:45:49 | **ROM fill 42** |
| 1783946022 | +0:01:18 | ARN audited close **62** (BUY-lifted) |
| 1783946040 | +0:01:00 | ROM audited close **39** (BUY-lifted) |

## Key hour — the floor, the refusal, and ROM walking to 42 (18:40-18:49 ET)

Six numbers per side (bid/sz · ask/sz · last · spread); both clocks. ARN is quoted
56/40 and never moves off it here; ROM descends 45→44→43→42 in nine minutes.

| ts ET | t−sched | t−bell | chg | ARN bid/sz ask/sz L sp | ROM bid/sz ask/sz L sp | mark |
|---|---|---|---|---|---|---|
| 18:40:32 | −11:40:32 | +13:54:28 | ROM | 55/27 56/57 56 1 | 44/8 **45**/29 49 1 | NEW_LOW ROM→45 |
| 18:40:38 | −11:40:38 | +13:54:22 | ROM | 55/27 56/40 56 1 | 42/99 **44**/30 45 2 | NEW_LOW ROM→44 |
| **18:40:43** | −11:40:43 | **+13:54:17** | ROM | **55/27 56/40 56 1** | 41/28 44/30 45 3 | **ARN QUALIFYING FLOOR 56** (row 35592) |
| **18:40:44** | −11:40:44 | **+13:54:16** | ROM | **55/27 56/40 56 1** | 40/61 44/30 45 4 | **ARN REFUSAL** (row 35593) |
| 18:40:48 | −11:40:48 | +13:54:12 | ROM | 55/27 56/12 56 1 | 40/137 **43**/33 45 3 | NEW_LOW ROM→43 |
| 18:42:37 | −11:42:37 | +13:52:23 | ROM | 57/823 56/2 56 −1 | 40/37 43/898 44 3 | (ARN bid crosses to 57) |
| 18:48:08 | −11:48:08 | +13:46:52 | ROM | 57/1323 56/2 56 −1 | 40/37 **42**/800 44 2 | NEW_LOW ROM→42 |
| **18:49:11** | −11:49:11 | **+13:45:49** | ARN | 57/823 56/2 56 −1 | 40/37 **42**/851 44 2 | **ROM FILL 42** |

The two marks sit one second apart: ARN's floor prints at 56 and is refused, and in
the very same book ROM is already showing **44 bid-side pressure and a walking ask**
— the "independent sibling observation" the refusal gate demanded was on ROM's own
tape, live, at that second. Nine minutes later ROM's ask reaches 42 and fills.

## How ROM travelled to 42 — the walk-down

Distinct traded-price steps (taker side):

| ts ET | t−bell | price | aggressor | size |
|---|---|---|---|---|
| 18:40:32 | +13:54 | 45 | BUY (lift ask) | 1.0 |
| 18:42:22 | +13:52 | 44 | BUY (lift ask) | 21.9 |
| 19:09:53 | +13:25 | **42** | BUY (lift ask) | 22.9 |
| 19:44:59 | +12:50 | 39 | SELL (hit bid) | 21.9 |
| 20:32:14 | +12:02 | 42 | BUY (lift ask) | 0.5 |
| 07-13 07:13 | +1:21 | 38 | BUY (lift ask) | 5.0 |
| 07-13 08:30 | +0:04 | **39** | BUY (lift ask) | 29.5 |

ROM walked **45→44→42** on buyers lifting the *declining* offer (the dog's price
falling, takers still buying it down), touched **39 on a seller hitting the bid**
(the true low), bounced to 42, drifted to a late **38**, and closed **39** four
minutes before the bell on a 29.5-lot buy. A descent, buyer-paid the whole way down
except the one seller-driven bottom at 39.

## How ARN travelled 56 → 62 — the climb into the bell

Distinct traded-price steps ≥ 54 (taker side):

| ts ET | t−bell | price | aggressor | size |
|---|---|---|---|---|
| 07-12 12:56 | +19:38 | 56 | BUY (lift ask) | 15.6 |
| 07-12 20:23 | +12:11 | 61 | BUY (lift ask) | 19.1 |
| 07-12 22:56 | +9:38 | 58 | SELL (hit bid) | 59.0 |
| 07-12 23:20 | +9:14 | 61 | BUY (lift ask) | 31.0 |
| 07-13 01:34 | +7:00 | 58 | SELL (hit bid) | 8.0 |
| 07-13 04:13 | +4:21 | 61 | BUY (lift ask) | 7.0 |
| 07-13 06:14 | +2:20 | **62** | BUY (lift ask) | 9.0 |
| 07-13 08:31 | +0:03 | 61 | BUY (lift ask) | 100.0 |
| 07-13 08:31 | +0:03 | **62** | BUY (lift ask) | 7.9 |

ARN **climbed on buyers lifting the ask** — 56→61 early, twice knocked back to 58
by a seller hitting the bid (−9:38 and −7:00 to the bell), each time re-lifted to
61, reaching **62 at −2:20** and closing **62 three minutes before the bell** on a
100-lot lift then a 7.9-lot lift. A buyer-driven ascent into the bell, the
climb-side signature: the price is made by takers paying up, late, right at the
close.

## Reading

The seesaw is textbook: ROM down 45→39, ARN up 56→62, summing to ~101 at the bell.
The one decision that mattered landed at 18:40:44 — ARN's 56 floor refused for lack
of an independent sibling reading, with ROM's descent printing on its own tape in
the same second. The floor was real, the sibling's direction was observable, and
the pair (56 + 42 = 98) was completable; the gate could not see across the two
tapes it already had. One game, at the tick.

## Conservation

ARN tape 148,870 rows → 24,294 change-events; ROM tape 117,768 rows → 784
change-events (the dog barely re-quoted). Merged dual timeline: **25,078 rows**,
one per BBO-change-or-print across both legs, on one clock. Full file:
`ARNROM_DUAL_TIMELINE.csv`.

## Artifacts

`ARNROM_DUAL_TIMELINE.csv` (25,078 rows: epoch, ts ET, t−scheduled, t−bell,
changed side, change type, ARN six numbers, ROM six numbers, mark) and
`ARNROM_TICK_STORY_SUMMARY.json`.
