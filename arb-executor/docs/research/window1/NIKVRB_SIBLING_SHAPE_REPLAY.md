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

## Every material decision, in order

The complete receipt-by-receipt English ledger is frozen as NIKVRB_DECISION_PROCESS_ENGLISH.jsonl.gz.b64 (base64-wrapped deterministic gzip so repository LF normalization cannot corrupt it). This table is the readable state-changing spine. Every row contains both books, spread, dwell, last-trade provenance, both shape calls, the organ, opened door, signer, action, declined action, and code path.

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

At T−109.050 / T−114.050, NIK's bid first reaches 19 while the ask is 27 and VRB is 73/77. The full cell has arrived. The live bid signs 19. The order rests for 1,703.923 seconds. At T−80.651 / T−85.651, a positive-size public print at 19 fills it. When ask later reaches 18 at T-57.483 / T-62.483, the OS believes both entries are complete; it records the lower book but correctly declines a fourth entry or re-buy.

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
