# NIK–VRB sibling-shape cold replay

## Result

The tune changes the faller at the joint-tree level, not by choosing a deeper table row. The current orientation-conditioned branch buys VRB at **69** and NIK at **21**: NIK is two cents above its own 19 close and three cents above its own 18 fillable low, so the pair's combined success depends on VRB carrying it. In the corrected branch VRB still rests **69** at T−316.033 scheduled / T−321.033 bell and is credited by strict ask 68 at T−314.633 / T−319.633. NIK rests 21 early, but at the first lawful receipt inside the existing T2 timing bucket the realized VRB pulse path cancels that exposure. NIK then waits unexposed until its own live bid falls one complete existing five-cent cell, from 24 to 19. The current bid signs 19 at T−109.050 / T−114.050; a strictly later public print at 19 credits it at T−80.651 / T−85.651.

The frozen close references are VRB 83 and NIK 19. Individual deltas are **−14** and **0**; combined delta is **−14**. Against each leg's own frozen fillable low, VRB 69 is one cent better than the print floor via strict ask and NIK 19 is one cent above its 18 low. The result no longer depends on one leg paying for a bad sibling entry. Any letter grade still depends on the separately declared N-cent tolerance; this replay does not invent it.

## The tune

1. Orientation still opens VRB's riser-near-now door and NIK's faller door.
2. At the first receipt inside the already-existing T2 bucket (60–120 minutes before schedule), the joint reader asks whether the riser is still above its fill and has completed a causal raw-quote recurrence. If yes, the riser shape is *realized*, and the inverse faller order is cancelled into patience.
3. Patience releases only when the faller's own live bid has moved one existing five-cent price cell below the arm bid while the sibling remains above its fill. The current external bid signs the price. No ATLAS depth and no future low participates.
4. The release receipt cannot fill its new order. Only a strictly later print or strict ask can credit it.

Implementation path: buildConsultations → ColdReplay.process:siblingShapePatienceArm → ColdReplay.process:fallerPatienceRelease → ColdReplay._fillEvidence → ColdReplay._fill in arb-executor/analysis/nikvrb_sibling_shape_cold_replay.js. Production live_v4.py is byte-identical to the parent and is not armed by this one-event tune.

## Read this before the trace

Three labels in the first report were too compressed:

- **ATLAS depth is not live book depth.** It is a historical price-dip distribution attached to page `ATP_CHALL|underdog|26_50`. On all three NIK calls the frozen row is `[p25=2, p50=4, p75=7]`, population 1,470. The replay's faller branch chooses p75 and computes `anchor - 7`. No displayed size or queue field produces 26, 23, or 21.
- **The 97 recurrences are observations, not a threshold.** They decompose into **31 bid recurrences + 66 ask recurrences** under the replay's local-trough counter. The code gate is merely `recurrences > 0`. The first receipt inside T2, not the 97th recurrence, fires the branch.
- **The five-cent cell is mechanical.** It is copied from production `V4_REPRICE_MOVE_CENTS=5`, where it is a resting-repost deadband. The tune repurposes that number as a faller-patience release. It is not a learned NIK cell lattice and it does not prove that five cents is economically optimal.

There is also a source distinction the compact table hid. The clock has a normalized `last` column and separately preserved true-print receipts. At T−119 the normalized NIK last says 28 while the newest proven print is 27; at T−109 it still says 28 while the newest proven print is 24. The tuned release does not use last trade, so the target is unaffected, but the trace reports the receipt-backed print as the authoritative last-trade fact and keeps the lagging normalized field visible.

## VRB alone, from appearance to bell

### T−375.450 / T−380.450: visible, but not priceable

Both books first coexist at 5/92. Neither leg has a receipt-identified print. `DISCOVERY_GATE` returns `NO_ORDER__NO_VERIFIED_LAST_TRADE`; BBO-only conception is unreachable. At NIK's first lawful consultation (T−361.917), orientation already names VRB the riser with conviction 1.0, but VRB still lacks its own anchor, so that call opens a *role* and not a VRB order.

### T−316.033 / T−321.033: VRB 69

Leading quote states (raw normalized last and the newest proven print are deliberately separate):

| Scheduled / bell | VRB bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
| T-317.883 / T-322.883 | 67/74 | ask | 1s | — | none |
| T-317.867 / T-322.867 | 67/76 | ask | 0s | — | none |
| T-317.867 / T-322.867 | 67/75 | ask | 0s | — | none |
| T-317.867 / T-322.867 | 67/73 | ask | 1s | — | none |
| T-317.850 / T-322.850 | 67/72 | ask | 0s | — | none |
| T-317.850 / T-322.850 | 67/71 | ask | 1s | — | none |
| T-317.833 / T-322.833 | 67/70 | ask | 0s | — | none |
| T-317.833 / T-322.833 | 67/69 | ask | 1s | — | none |
| T-317.817 / T-322.817 | 67/68 | ask | 12s | — | none |
| T-317.617 / T-322.617 | 67/75 | ask | 45s | — | none |
| T-316.867 / T-321.867 | 67/74 | ask | 27s | — | none |
| T-316.417 / T-321.417 | 67/73 | ask | 2s | — | none |
| T-316.383 / T-321.383 | 69/73 | bid | 0s | — | none |
| T-316.383 / T-321.383 | 69/72 | ask | 0s | — | none |
| T-316.383 / T-321.383 | 69/71 | ask | 0s | — | none |
| T-316.383 / T-321.383 | 69/70 | ask | 21s | — | 70 @ 07:13:56 |

The useful local sequence is: 67/75; ask compresses 74, 76, 75, 73, 72, 71, 70, 69, then 68 while bid stays 67; ask snaps back to 75; later bid lifts 67→69 while ask compresses 73→72→71→70. That 69/70 state holds 21 seconds before the consultation. A true print at 70 arrives 1.821 seconds before the call.

**Every organ at the call:** anchor last_traded=70; orientation VRB riser, conviction 1, voices cohort+anchor_role; cohort ATP_CHALL|fav|51_75, n=2008, dip-p50=4, reach-3c=0.587, rose=37.3%; ATLAS ATP_CHALL|leader|51_75, n=1614, depth=1/3/6, p50 aim=67; contention DROP -6.5%; pair PAIR-COMPOSED, composed=93, synthetic sibling=30; flow quiet, prints30m=1, p-fill-1h=0.037; FV NO-READ/stale_sources; Polymarket NO-FEED; library NO-OPINION.

The OS reads **VRB riser / climb with pulses expected before T2**. In this branch, the fresh 70 print plus the 69/70 book means the shallow retouch is actionable now. `ORIENTATION_RISER_NEAR_NOW` signs the live bid: `X=69`. ATLAS separately says `70 - p50(3) = 67`; the branch declines 67. Nothing in this call predicts an unseen future low.

### T−314.633 / T−319.633: ask 68 credits the resting 69

| Scheduled / bell | VRB bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
| T-317.867 / T-322.867 | 67/76 | ask | 0s | — | none |
| T-317.867 / T-322.867 | 67/75 | ask | 0s | — | none |
| T-317.867 / T-322.867 | 67/73 | ask | 1s | — | none |
| T-317.850 / T-322.850 | 67/72 | ask | 0s | — | none |
| T-317.850 / T-322.850 | 67/71 | ask | 1s | — | none |
| T-317.833 / T-322.833 | 67/70 | ask | 0s | — | none |
| T-317.833 / T-322.833 | 67/69 | ask | 1s | — | none |
| T-317.817 / T-322.817 | 67/68 | ask | 12s | — | none |
| T-317.617 / T-322.617 | 67/75 | ask | 45s | — | none |
| T-316.867 / T-321.867 | 67/74 | ask | 27s | — | none |
| T-316.417 / T-321.417 | 67/73 | ask | 2s | — | none |
| T-316.383 / T-321.383 | 69/73 | bid | 0s | — | none |
| T-316.383 / T-321.383 | 69/72 | ask | 0s | — | none |
| T-316.383 / T-321.383 | 69/71 | ask | 0s | — | none |
| T-316.383 / T-321.383 | 69/70 | ask | 105s | — | none |
| T-314.633 / T-319.633 | 67/68 | bid+ask | 0s | 70 | 70 @ 07:13:56 |

The immediate pre-fill book is 69/70. It has held **105 seconds from first appearance and 84 seconds since our order**. At 07:15:22 both sides step down together to 67/68: ask falls from 70 to 68 and bid falls from 69 to 67. Because 68 is strictly below the already exposed 69, `_fillEvidence` returns `STRICT_ASK_CERTAIN_FILL` and credits five at the original 69 before any maker-safety action can lower or cancel it.

After that, VRB's entry path is locked. The later frozen 07:15:43 consultation would have proposed current-bid 67 in this orientation branch (and ATLAS 65), but that exact consultation timestamp is absent from the 13,123-row dual clock, so the cold replay does not invent a row for it. Every receipt that is present takes `legFilledLock`, and after NIK fills it takes `pairCompleteLock`. Visits 3–9 to ask 68 therefore update pulse memory but cannot create a second VRB entry.

## NIK alone, from appearance to bell

### T−361.917 / T−366.917: NIK 26

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
| T-375.450 / T-380.450 | 5/92 | bid+ask | 808s | — | none |
| T-361.983 / T-366.983 | 23/33 | bid+ask | 4s | — | 33 @ 06:28:01 |

The book jumps from 5/92 to 23/33 after 13 minutes 28 seconds. A one-contract true print at 33 follows 0.766 seconds later; the consultation is 3.234 seconds after that print. Orientation calls VRB the riser, making NIK the faller. The replay's faller child does not use displayed depth: it selects the ATLAS historical p75 dip of seven cents. Exact arithmetic is `33 - 7 = 26`. ATLAS p50 would be 29 and is explicitly declined. Thus 26 is a candidate-imposed p75 output, not a number inferred from the 23/33 queue.

**Every organ at the call:** anchor last_traded=33; orientation VRB riser, conviction 1, voices cohort+anchor_role; cohort ATP_CHALL|dog|26_50, n=2053, dip-p50=4, reach-3c=0.61, rose=34%; ATLAS ATP_CHALL|underdog|26_50, n=1470, depth=2/4/7, p50 aim=29; contention TRADE-AT-PATH 26.1%; pair PAIR-COMPOSED, composed=93, synthetic sibling=67; flow quiet, prints30m=1, p-fill-1h=0.02; FV NO-READ/stale_sources; Polymarket NO-FEED; library NO-OPINION. Orientation opens the faller child; the replay p75 child signs. Cohort, contention, pair, flow, FV, Polymarket and library remain context and do not overwrite 26.

### T−322.450 / T−327.450: NIK 23

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
| T-375.450 / T-380.450 | 5/92 | bid+ask | 808s | — | none |
| T-361.983 / T-366.983 | 23/33 | bid+ask | 23s | — | none |
| T-361.600 / T-366.600 | 29/33 | bid | 135s | 33 | 33 @ 06:28:01 |
| T-359.350 / T-364.350 | 29/32 | ask | 2197s | 33 | 33 @ 06:28:01 |
| T-322.733 / T-327.733 | 29/31 | ask | 17s | 32 | 32 @ 06:55:10 |
| T-322.450 / T-327.450 | 29/30 | ask | 0s | 32 | 32 @ 06:55:10 |

From the first call, bid rises 23→29 and ask falls 33→32. The 29/32 book then persists for roughly 36 minutes 37 seconds. At T−322.733 ask falls to 31 and holds 17 seconds; at the call it falls again to 30 while bid remains 29. The newest true print is 32, now outside the 29/30 book, so the anchor gate replaces the print with tight-mid 30. The ATLAS row does not change: p75 remains seven. Exact arithmetic is `30 - 7 = 23`. That is the whole three-cent order move: anchor 33→30, fixed depth seven. A later same-timestamp row shows bid 23, but its preserved sequence is after the decision and did not sign the target.

**Every organ at the call:** anchor tight_mid=30; orientation VRB riser, conviction 1, voices cohort+anchor_role; cohort ATP_CHALL|dog|26_50, n=2053, dip-p50=4, reach-3c=0.61, rose=34%; ATLAS ATP_CHALL|underdog|26_50, n=1470, depth=2/4/7, p50 aim=26; contention TRADE-AT-PATH 39.4%; pair PAIR-COMPOSED, composed=93, synthetic sibling=70; flow quiet, prints30m=1, p-fill-1h=0.01; FV NO-READ/stale_sources; Polymarket NO-FEED; library NO-OPINION. The only controlling numeric change is the anchor. Orientation keeps the same child open; the same p75 child overwrites 26 with 23. The p50 result 26 and all contextual voices are declined.

### T−278.650 / T−283.650: NIK 21

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
| T-322.733 / T-327.733 | 29/31 | ask | 17s | 32 | 32 @ 06:55:10 |
| T-322.450 / T-327.450 | 29/30 | ask | 0s | 32 | 32 @ 06:55:10 |
| T-322.450 / T-327.450 | 23/30 | bid | 2s | 32 | 32 @ 06:55:10 |
| T-322.417 / T-327.417 | 28/30 | bid | 12s | 32 | 32 @ 06:55:10 |
| T-322.217 / T-327.217 | 28/29 | ask | 0s | 32 | 32 @ 06:55:10 |
| T-322.217 / T-327.217 | 23/29 | bid | 1s | 32 | 32 @ 06:55:10 |
| T-322.200 / T-327.200 | 28/29 | bid | 2612s | 32 | 32 @ 06:55:10 |
| T-278.667 / T-283.667 | 24/29 | bid | 0s | 32 | 32 @ 06:55:10 |
| T-278.667 / T-283.667 | 24/28 | ask | 0s | 32 | 32 @ 06:55:10 |
| T-278.667 / T-283.667 | 23/28 | bid | 0s | 28 | 32 @ 06:55:10 |
| T-278.667 / T-283.667 | 23/27 | ask | 0s | 28 | 32 @ 06:55:10 |
| T-278.667 / T-283.667 | 24/27 | bid | 1s | 28 | 28 @ 07:51:20 |

The book spends most of the next 43 minutes near 28/29. At T−278.667 it breaks rapidly through 24/29, 24/28, 23/28, 23/27 and 24/27 while a true print establishes 28. At the next preserved call the causal book is 24/27 and the verified anchor is 28. The same historical p75 seven signs `28 - 7 = 21`. It is 21 rather than 22 or 20 because the row exposes 2/4/7, and this branch chooses exactly the third number. P50 would sign 24. “Depth call” means this macro dip lookup; it does not mean the 24/27 book displayed seven contracts.

**Every organ at the call:** anchor last_traded=28; orientation VRB riser, conviction 1, voices cohort+anchor_role; cohort ATP_CHALL|dog|26_50, n=2053, dip-p50=4, reach-3c=0.61, rose=34%; ATLAS ATP_CHALL|underdog|26_50, n=1470, depth=2/4/7, p50 aim=24; contention TRADE-AT-PATH 50.5%; pair PAIR-COMPOSED, composed=93, synthetic sibling=72; flow quiet, prints30m=2, p-fill-1h=0.02; FV NO-READ/stale_sources; Polymarket NO-FEED; library NO-OPINION. The branch again gives the p75 child the pen. ATLAS p50 says 24; contention says trade-at-path; the pair organ says composed 93 using a synthetic sibling 72; none of those numbers displaces 21 in this replay.

### T−119.350 / T−124.350: cancel 21

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
| T-155.067 / T-160.067 | 19/29 | bid | 0s | 28 | 28 @ 08:34:48 |
| T-155.067 / T-160.067 | 20/29 | bid | 86s | 28 | 28 @ 08:34:48 |
| T-153.633 / T-158.633 | 23/28 | bid+ask | 4s | 28 | 28 @ 08:34:48 |
| T-153.567 / T-158.567 | 24/28 | bid | 3s | 28 | 28 @ 08:34:48 |
| T-153.517 / T-158.517 | 23/28 | bid | 18s | 28 | 28 @ 08:34:48 |
| T-153.217 / T-158.217 | 23/27 | ask | 442s | 28 | 28 @ 08:34:48 |
| T-145.850 / T-150.850 | 24/27 | bid | 375s | 28 | 28 @ 08:34:48 |
| T-139.600 / T-144.600 | 24/28 | ask | 547s | 28 | 27 @ 10:09:49 |
| T-130.483 / T-135.483 | 25/27 | bid+ask | 160s | 28 | 27 @ 10:09:49 |
| T-127.817 / T-132.817 | 25/29 | ask | 398s | 28 | 27 @ 10:09:49 |
| T-121.183 / T-126.183 | 24/28 | bid+ask | 60s | 28 | 27 @ 10:09:49 |
| T-120.183 / T-125.183 | 24/29 | ask | 50s | 28 | 27 @ 10:09:49 |

NIK 21 has rested for 9,558 seconds. The first receipt inside the existing T2 bucket sees NIK 24/29 and VRB 73/74. VRB's bid is four cents above its 69 fill. The raw quote tracker has completed 97 local-trough recoveries since observation began (31 bid, 66 ask).

What *resolved* is the replay state flag, not a calibrated recurrence score: `T2_OPEN && VRB_bid>69 && recurrence_count>0 && valid_NIK_book`. The threshold is one recurrence; 97 is merely the accumulated value by the first T2 receipt. `siblingShapePatienceArm` then calls `_closeOrder("NIK")` unconditionally. It does **not** score continued support for 21, compare HOLD with WALK, or compute an improved target. That is why it cancels rather than holds or improves: this one-game tune made cancel/wait the only reachable child. The evidence supports “reconsider NIK”; it does not independently prove that cancellation is the uniquely correct response.

### T−109.050 / T−114.050: NIK 19

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
| T-155.067 / T-160.067 | 20/29 | bid | 86s | 28 | 28 @ 08:34:48 |
| T-153.633 / T-158.633 | 23/28 | bid+ask | 4s | 28 | 28 @ 08:34:48 |
| T-153.567 / T-158.567 | 24/28 | bid | 3s | 28 | 28 @ 08:34:48 |
| T-153.517 / T-158.517 | 23/28 | bid | 18s | 28 | 28 @ 08:34:48 |
| T-153.217 / T-158.217 | 23/27 | ask | 442s | 28 | 28 @ 08:34:48 |
| T-145.850 / T-150.850 | 24/27 | bid | 375s | 28 | 28 @ 08:34:48 |
| T-139.600 / T-144.600 | 24/28 | ask | 547s | 28 | 27 @ 10:09:49 |
| T-130.483 / T-135.483 | 25/27 | bid+ask | 160s | 28 | 27 @ 10:09:49 |
| T-127.817 / T-132.817 | 25/29 | ask | 398s | 28 | 27 @ 10:09:49 |
| T-121.183 / T-126.183 | 24/28 | bid+ask | 60s | 28 | 27 @ 10:09:49 |
| T-120.183 / T-125.183 | 24/29 | ask | 183s | 28 | 27 @ 10:09:49 |
| T-117.133 / T-122.133 | 24/28 | ask | 440s | 28 | 27 @ 10:09:49 |
| T-109.800 / T-114.800 | 23/27 | bid+ask | 45s | 28 | 24 @ 10:40:05 |
| T-109.050 / T-114.050 | 19/27 | bid | 0s | 28 | 24 @ 10:40:05 |

After cancellation, 40 receipts repeat `HOLD_NO_ORDER__WAIT_FOR_FULL_CELL`. NIK is 24/28 at T−117.133 (zero-cent bid drop), then 23/27 at T−109.800 (one cent). A burst of receipt-identified prints at 24 arrives around T−110. The newest proven last at release is 24 even though the normalized clock column still carries 28.

At the first 19/27 BBO, the release calculation is `arm_bid 24 - live_bid 19 = 5`, while VRB remains 73/77 above its fill. The price is 19 because the current bid signs after the first full mechanical threshold crossing. A bid of 20 would be only four cents down; 18 had not been observed. Later preserved rows in the same second bounce 19→20→19, then 21/20/21 and 22/23. They are strictly later than the action and do not rewrite it.

This “cell” does not have a multi-cell market taxonomy behind it. The code imports production's five-cent reprice deadband and treats one such move as release authority. That is the exact rule; it is also the unproven economic assumption in this tune.

### T−80.651 / T−85.651: print 19 fills NIK

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
| T-95.267 / T-100.267 | 24/28 | bid | 0s | 28 | 30 @ 10:45:21 |
| T-95.267 / T-100.267 | 26/28 | bid | 0s | 28 | 30 @ 10:45:21 |
| T-95.267 / T-100.267 | 24/28 | bid | 124s | 28 | 30 @ 10:45:21 |
| T-93.200 / T-98.200 | 24/29 | ask | 480s | 28 | 30 @ 10:45:21 |
| T-85.200 / T-90.200 | 25/29 | bid | 265s | 28 | 30 @ 10:45:21 |
| T-80.783 / T-85.783 | 23/24 | bid+ask | 5s | 28 | 23 @ 11:09:09 |
| T-80.700 / T-85.700 | 22/24 | bid | 0s | 28 | 23 @ 11:09:15 |
| T-80.700 / T-85.700 | 20/24 | bid | 2s | 23 | 23 @ 11:09:15 |
| T-80.667 / T-85.667 | 19/24 | bid | 0s | 23 | 23 @ 11:09:15 |
| T-80.667 / T-85.667 | 19/23 | ask | 0.922s | 23 | 19 @ 11:09:20 |

The 19 order rests 1,703.923 seconds. The book compresses from 25/29 through 23/24, 22/24, 20/24, 19/24 and 19/23. A strictly later positive-size public print at 19 then returns `PRICE_REACHED`; fill accounting credits the exposed 19. The trigger that created the order never fills it.

### T−57.483 / T−62.483: ask 18 is observed and declined

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
| T-80.700 / T-85.700 | 22/24 | bid | 0s | 28 | 23 @ 11:09:15 |
| T-80.700 / T-85.700 | 20/24 | bid | 2s | 23 | 23 @ 11:09:15 |
| T-80.667 / T-85.667 | 19/24 | bid | 0s | 23 | 23 @ 11:09:15 |
| T-80.667 / T-85.667 | 19/23 | ask | 2s | 23 | 23 @ 11:09:15 |
| T-80.633 / T-85.633 | 18/23 | bid | 0s | 23 | 19 @ 11:09:20 |
| T-80.633 / T-85.633 | 18/19 | ask | 33s | 23 | 19 @ 11:09:20 |
| T-80.083 / T-85.083 | 17/19 | bid | 48s | 19 | 19 @ 11:09:50 |
| T-79.283 / T-84.283 | 18/19 | bid | 442s | 19 | 19 @ 11:10:41 |
| T-71.917 / T-76.917 | 17/19 | bid | 866s | 19 | 19 @ 11:16:08 |
| T-57.483 / T-62.483 | 17/18 | ask | 0s | 19 | 19 @ 11:16:08 |

The book has already shown 18/19 shortly after the fill; the first ask 18 arrives later when 17/19 becomes 17/18. The deciding rule is `ColdReplay.process:pairCompleteLock`: both exact-five entry fills exist, so every later Window-1 entry organ is unreachable. The OS does **not** believe that 18 is too expensive and does **not** compare it with 19. It calculates no alternative cost at all. Ex post, 69+18 would be 87 instead of the achieved 88, but that counterfactual was not decision-time evidence. From the 19 fill through the observed bell, 9,762 receipts repeat the same pair-complete refusal.

## Both legs on the same clock

## Every material decision, in order

The complete receipt-by-receipt English ledger is frozen as NIKVRB_DECISION_PROCESS_ENGLISH.jsonl.gz.b64. The exact requested T−375-through-bell slice is NIKVRB_T375_TO_BELL_DECISION_TRACE.jsonl.gz.b64: **13,122 rows, sequences 2–13,123**, including the two same-time appearance rows and the bell. Both are base64-wrapped deterministic gzip so repository LF normalization cannot corrupt them. Every row contains both books, spread, dwell, last-trade provenance, both shape calls, the organ, opened door, signer, action, declined action, and code path. The prose below summarizes state changes; the ledger is the exhaustive event-by-event record.

| # | Scheduled / bell | Joint observation (bid/ask/last) | Shape call: VRB / NIK | Organ and door | Organ returns | Price signer | Action and overwritten/declined action |
|---:|---|---|---|---|---|---|---|
| 1 | T-480.000 / T-485.000 | NIK —/—/—; spread —; dwell 0s; last UNAVAILABLE; VRB —/—/—; spread —; dwell 0s; last UNAVAILABLE | UNRESOLVED / UNRESOLVED | WINDOW_GATE → OBSERVATION_ONLY | none | NO_CALL | NO_ORDER__BOOKS_UNAVAILABLE; overwritten/declined all entry pricing |
| 2 | T-375.450 / T-380.450 | NIK 5/92/—; spread 87; dwell 0s; last UNAVAILABLE; VRB 5/92/—; spread 87; dwell 0s; last UNAVAILABLE | UNRESOLVED / UNRESOLVED | DISCOVERY_GATE → WAIT_FOR_TRUE_PRINT_ANCHOR | none | NO_CALL | NO_ORDER__NO_VERIFIED_LAST_TRADE; overwritten/declined BBO-only conception |
| 3 | T-361.917 / T-366.917 | NIK 23/33/33; spread 10; dwell 4s; last CARRIED_VERIFIED_EXECUTION; VRB 67/77/—; spread 10; dwell 0s; last UNAVAILABLE | RISER__CLIMB_WITH_PULSES_EXPECTED_BEFORE_T2 / FALLER__INVERSE_SLIDE_EXPECTED_IN_T2 | INITIAL_ENTRY_TREE → FALLER_DEEP_CAST | fresh_print_anchor=last_traded:33; orientation=VRB_RISER conviction=1; atlas=29 (p50); p75=7; cohort=dip_p50=4; contention=TRADE-AT-PATH:26.1%; pair=PAIR-COMPOSED:93; flow=quiet; prints30m=1 | ORIENTATION_FALLER_DEEP | PLACE_NIK_26; overwritten/declined ATLAS p50 29 |
| 4 | T-322.450 / T-327.450 | NIK 29/30/32; spread 1; dwell 0s; last CARRIED_VERIFIED_EXECUTION; VRB 67/76/—; spread 9; dwell 2349s; last UNAVAILABLE | RISER__CLIMB_WITH_PULSES_EXPECTED_BEFORE_T2 / FALLER__INVERSE_SLIDE_EXPECTED_IN_T2 | INITIAL_ENTRY_TREE → FALLER_DEEP_CAST | fresh_print_anchor=tight_mid:30; orientation=VRB_RISER conviction=1; atlas=26 (p50); p75=7; cohort=dip_p50=4; contention=TRADE-AT-PATH:39.4%; pair=PAIR-COMPOSED:93; flow=quiet; prints30m=1 | ORIENTATION_FALLER_DEEP | REPRICE_NIK_23; overwritten/declined ATLAS p50 26 |
| 5 | T-316.033 / T-321.033 | NIK 28/29/32; spread 1; dwell 370s; last CARRIED_VERIFIED_EXECUTION; VRB 69/70/70; spread 1; dwell 21s; last CARRIED_VERIFIED_EXECUTION | RISER__CLIMB_WITH_PULSES_EXPECTED_BEFORE_T2 / FALLER__INVERSE_SLIDE_EXPECTED_IN_T2 | INITIAL_ENTRY_TREE → RISER_NEAR_NOW | fresh_print_anchor=last_traded:70; orientation=VRB_RISER conviction=1; atlas=67 (p50); p75=6; cohort=dip_p50=4; contention=DROP:-6.5%; pair=PAIR-COMPOSED:93; flow=quiet; prints30m=1 | ORIENTATION_RISER_NEAR_NOW | PLACE_VRB_69; overwritten/declined ATLAS 67 |
| 6 | T-314.633 / T-319.633 | NIK 28/29/32; spread 1; dwell 454s; last CARRIED_VERIFIED_EXECUTION; VRB 67/68/70; spread 1; dwell 0s; last CARRIED_VERIFIED_EXECUTION | RISER__CLIMB_WITH_PULSES_EXPECTED_BEFORE_T2 / FALLER__INVERSE_SLIDE_EXPECTED_IN_T2 | FILL_ACCOUNTING → SIBLING_REMAINS_OPEN | none | STRICT_ASK_CERTAIN_FILL | CREDIT_VRB_FILL_69; overwritten/declined no cancel/reprice before fill credit |
| 7 | T-278.650 / T-283.650 | NIK 24/27/28; spread 3; dwell 1s; last CARRIED_VERIFIED_EXECUTION; VRB 72/73/73; spread 1; dwell 159s; last CARRIED_VERIFIED_EXECUTION | RISER__CLIMB_WITH_PULSES_EXPECTED_BEFORE_T2 / FALLER__INVERSE_SLIDE_EXPECTED_IN_T2 | INITIAL_ENTRY_TREE → FALLER_DEEP_CAST | fresh_print_anchor=last_traded:28; orientation=VRB_RISER conviction=1; atlas=24 (p50); p75=7; cohort=dip_p50=4; contention=TRADE-AT-PATH:50.5%; pair=PAIR-COMPOSED:93; flow=quiet; prints30m=2 | ORIENTATION_FALLER_DEEP | REPRICE_NIK_21; overwritten/declined ATLAS p50 24 |
| 8 | T-119.350 / T-124.350 | NIK 24/29/28; spread 5; dwell 50s; last CARRIED_VERIFIED_EXECUTION; VRB 73/74/74; spread 1; dwell 2993s; last CARRIED_VERIFIED_EXECUTION | RISER__CLIMB_WITH_PULSES_RESOLVED / FALLER__WAIT_FOR_ONE_LIVE_PRICE_CELL | SIBLING_REALIZED_SHAPE → FALLER_PATIENCE_WAIT_FOR_ONE_LIVE_PRICE_CELL | orientation=VRB_RISER/NIK_FALLER; timing_axis=T2_OPEN; sibling_live_book=73/74; sibling_completed_quote_recurrences=97; sibling_above_fill=4 | JOINT_SHAPE_AUTHORITY | CANCEL_NIK_21__WAIT; overwritten/declined accepting the still-lawful 21 before the late inverse slide |
| 9 | T-109.050 / T-114.050 | NIK 19/27/28; spread 8; dwell 0s; last CARRIED_VERIFIED_EXECUTION; VRB 73/77/74; spread 4; dwell 43s; last CARRIED_VERIFIED_EXECUTION | RISER__RESOLVED_NO_CONTRADICTION / FALLER__LATE_IMPULSE_CONFIRMED | FALLER_PATIENCE_RELEASE → CURRENT_BID_MAKER_EXPOSURE | arm_bid=24; current_bid=19; bid_drop=5; mechanical_cell_width=5; sibling_book=73/77 | LIVE_NIK_BID | PLACE_NIK_19; overwritten/declined ATLAS 21 and any future lower price not yet observed |
| 10 | T-80.651 / T-85.651 | NIK 19/23/19; spread 4; dwell 0.922s; last VERIFIED_NEW_EXECUTION; VRB 77/78/77; spread 1; dwell 0.922s; last CARRIED_VERIFIED_EXECUTION | ENTRY_COMPLETE / ENTRY_COMPLETE | FILL_ACCOUNTING → PAIR_ENTRY_COMPLETE | none | PRICE_REACHED | CREDIT_NIK_FILL_19; overwritten/declined no cancel/reprice before fill credit |

## What the shapes mean

- **VRB riser, climbing with pulses:** expect the useful VRB entry early, before T2. A divot is a recurrence opportunity, not evidence that the path has reversed.
- **NIK inverse faller:** while VRB keeps resolving upward, NIK's early depth is not terminal. The useful NIK move is expected after the T2 door opens, so an early table-generated bid loses authority when the sibling shape becomes realized.
- **Late faller impulse:** one full live price-cell move on NIK, with VRB still above its fill, changes “wait” into “rest at the current bid.” It predicts a retouch/print at the new live level; it does not predict an unseen 18.

## VRB's nine ask-68 visits

| Visit | Scheduled / bell | VRB book | Tuned decision in English |
|---:|---|---|---|
| 1 | T-317.817 / T-322.817 | 67/68 | The ask reached 68 before VRB had a verified discovery call, so the OS had no lawful order to hold or move. |
| 2 | T-314.633 / T-319.633 | 67/68 | The 69 riser bid was already resting. Ask 68 was strictly through it, so fill accounting signed 69 before the resting manager could cancel. |
| 3 | T-308.800 / T-313.800 | 67/68 | VRB was already filled at 69. The repeated ask-68 pulse updated shape memory but could not trigger another entry. |
| 4 | T-307.800 / T-312.800 | 67/68 | VRB was already filled at 69. The repeated ask-68 pulse updated shape memory but could not trigger another entry. |
| 5 | T-306.750 / T-311.750 | 67/68 | VRB was already filled at 69. The repeated ask-68 pulse updated shape memory but could not trigger another entry. |
| 6 | T-305.783 / T-310.783 | 67/68 | VRB was already filled at 69. The repeated ask-68 pulse updated shape memory but could not trigger another entry. |
| 7 | T-301.833 / T-306.833 | 67/68 | VRB was already filled at 69. The repeated ask-68 pulse updated shape memory but could not trigger another entry. |
| 8 | T-300.817 / T-305.817 | 67/68 | VRB was already filled at 69. The repeated ask-68 pulse updated shape memory but could not trigger another entry. |
| 9 | T-299.717 / T-304.717 | 67/68 | VRB was already filled at 69. The repeated ask-68 pulse updated shape memory but could not trigger another entry. |

The pre-orientation OS cancelled 67 on visit 2, reconceived 65, then repeated quiet-staircase HOLD. Both the current orientation branch and this tuned branch instead let fill accounting consume ask 68 against the already-resting 69 before the resting manager runs. Visits 3–9 are therefore shape observations, not entry decisions.

## NIK's late slide and the non-decisions

At T−119.350 / T−124.350, the joint-shape organ cancels 21 and deliberately has no NIK order. From there, every receipt asks the same causal question: has NIK's **live bid** moved a full five-cent cell from 24 while VRB remains above 69? Until the answer is yes, the result is a named patience HOLD with no order.

At T−109.050 / T−114.050, NIK's bid first reaches 19 while the ask is 27 and VRB is 73/77. The full cell has arrived. The live bid signs 19. The order rests for 1,703.923 seconds. At T−80.651 / T−85.651, a positive-size public print at 19 fills it. When ask later reaches 18 at T-57.483 / T-62.483, the OS sees both entries as complete; it records the lower book but declines a fourth entry or re-buy without calculating an alternative entry cost.

| Repeated decision | Receipts | English reason |
|---|---:|---|
| NO_CALL__PAIR_ENTRY_COMPLETE | 9,762 | The credited fill locked entry while books and tape remained readable. |
| HOLD_NIK_21 | 1,600 | The existing resting order remained lawful and no named transition fired. |
| NO_CALL__VRB_ENTRY_COMPLETE | 1,132 | The credited fill locked entry while books and tape remained readable. |
| NO_CALL__NO_ENTRY_TRIGGER | 211 | No causal entry door was open. |
| HOLD_NIK_19 | 171 | The existing resting order remained lawful and no named transition fired. |
| HOLD_NIK_23 | 117 | The existing resting order remained lawful and no named transition fired. |
| HOLD_NIK_26 | 59 | The existing resting order remained lawful and no named transition fired. |
| HOLD_NO_ORDER__WAIT_FOR_FULL_CELL | 40 | The existing resting order remained lawful and no named transition fired. |
| HOLD_VRB_69 | 21 | The existing resting order remained lawful and no named transition fired. |

## How fluid the process is

The cold clock contains **13,123** ordered rows, of which **13,121** are BBO or true-print receipts. Each receipt refreshes the joint observation and reaches a named gate, but only **10** state-changing decisions occur. Reconsideration is therefore frequent; authority changes are sparse.

The chain unlocks only on: a lawful discovery consultation, strict fill evidence, entry into the existing T2 timing bucket with a resolved sibling shape, a full live price-cell move on the faller, or the Window-1 boundary. It locks at three places: missing discovery evidence, a resting-order HOLD without a named trigger, and the filled-phase gate. The important repair is that the T2 sibling-shape transition now sits *before* the filled-phase lock on NIK; 21 is cancelled while entry is still reachable.

## Scope fence

This is a cold, one-event, score-free replay against frozen July 19 chronology. It reads no future row at a decision, runs no 804-event population, changes no production candidate, and does not modify or execute live_v4.py. The full ledger makes the silences explicit rather than treating absence of an action as absence of a decision.
