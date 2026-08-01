# Five-game maker/taker and insufficiency diagnosis

This is a cold-input, score-free diagnostic. It changes no placement or fill.

## Maker versus taker

| category | region | event | leg | action BBO/last | dwell | replay X | replay relation | role | live maker clamp X/relation | maker fee / 5 | taker fee / 5 |
|---|---|---|---|---|---:|---:|---|---|---|---:|---:|
| ATP_CHALL | 51_75 | KXATPCHALLENGERMATCH-26JUL19HURBIG | BIG | 54/55/55 (spread 1) | 13459s | 55 | SITTING_AT_ASK_MARKETABLE_BUY | TAKER | 54/JOINING_BID | 3c | 9c |
| ATP_CHALL | 26_50 | KXATPCHALLENGERMATCH-26JUL19HURBIG | HUR | 37/38/38 (spread 1) | 489s | 38 | SITTING_AT_ASK_MARKETABLE_BUY | TAKER | 37/JOINING_BID | 3c | 9c |
| ATP_CHALL | 26_50 | KXATPCHALLENGERMATCH-26JUL19NIKVRB | NIK | 17/18/18 (spread 1) | 12s | 18 | SITTING_AT_ASK_MARKETABLE_BUY | TAKER | 17/JOINING_BID | 2c | 6c |
| ATP_CHALL | 51_75 | KXATPCHALLENGERMATCH-26JUL19NIKVRB | VRB | 67/68/70 (spread 1) | 32s | 68 | SITTING_AT_ASK_MARKETABLE_BUY | TAKER | 67/JOINING_BID | 2c | 8c |

All four credited prices equal the contemporaneous external ask. They are marketable taker actions. The live post-only chokepoint would clamp each one-cent-spread action to ask-1, which equals the bid, before submission. The later external ask receipt reaches none of those clamped prices. It proves the replay's delayed capacity rule; it does not retroactively turn the ask-priced action into maker liquidity.

| event | price-only delta/contract | maker fees/pair | taker fees/pair | maker-adjusted delta/contract | taker-adjusted delta/contract | maker-only valid |
|---|---:|---:|---:|---:|---:|---|
| KXATPCHALLENGERMATCH-26JUL19HURBIG | -9 | 6c | 18c | -7.8 | -5.4 | NO |
| KXATPCHALLENGERMATCH-26JUL19NIKVRB | -16 | 4c | 14c | -15.2 | -13.2 | NO |

The -9 and -16 remain price-only arithmetic, and remain negative after counterfactual taker fees. They are not maker-only completed-pair results because none of the four actions could lawfully rest post-only at its action BBO.

## Insufficient legs

| category | region | partition n | event | leg | first terminal-predicate tick (sched/bell) | BBO/last, spread, dwell | recomputed terminal predicate | own surviving shapes | pair-constrained shapes | blocker class | low | dwell | capacity | low-close |
|---|---|---:|---|---|---|---|---|---|---|---|---:|---:|---:|---:|
| ATP_MAIN | 26_50 | 96 | KXATPMATCH-26JUL12LAJVAN | LAJ | #2 (T-471:40 / T-1791:40) | 49/50/49, 1c, 151s | SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP | ATP_MAIN_26_50_FLAT_UNMOVED | EMPTY | LIBRARY_FITTING_PAIR_TUPLE_COVERAGE_DEFECT | 45 | 114s | 883 | +0 |
| ATP_MAIN | 26_50 | 96 | KXATPMATCH-26JUL12LAJVAN | VAN | #3 (T-470:35 / T-1790:35) | 49/50/51, 1c, 0s | SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP | ATP_MAIN_26_50_FLAT_UNMOVED | EMPTY | LIBRARY_FITTING_PAIR_TUPLE_COVERAGE_DEFECT | 50 | 25s | 351 | -7 |
| WTA_CHALL | 26_50 | 64 | KXWTACHALLENGERMATCH-26JUL16BRAVED | BRA | #1559 (T-123:35 / T-173:35) | 40/41/41, 1c, 1738s | FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED | WTA_CHALL_26_50_DOWN_CONTINUATION | WTA_CHALL_26_50_DOWN_CONTINUATION:FLOOR | PAIR_EVIDENCE_PREDICATE_UNPROVEN | 40 | 10s | 2180 | -4 |
| WTA_CHALL | 51_75 | 65 | KXWTACHALLENGERMATCH-26JUL16BRAVED | VED | #38 (T-474:40 / T-524:40) | 59/60/60, 1c, 311s | FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED | WTA_CHALL_51_75_UP_CONTINUATION | WTA_CHALL_51_75_UP_CONTINUATION:FLOOR | PAIR_EVIDENCE_PREDICATE_UNPROVEN | 57 | 13s | 4886 | +0 |
| WTA_MAIN | 26_50 | 73 | KXWTAMATCH-26JUL20KORJIM | JIM | #329 (T+117:29 / T-1462:31) | 30/32/39, 2c, 1856s | FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED | WTA_MAIN_26_50_FLAT_UNMOVED | WTA_MAIN_26_50_FLAT_UNMOVED:FLOOR | PAIR_EVIDENCE_PREDICATE_UNPROVEN | 30 | 10s | 380 | -2 |
| WTA_MAIN | 51_75 | 73 | KXWTAMATCH-26JUL20KORJIM | KOR | #2 (T-83:37 / T-1663:37) | 59/60/60, 1c, 18s | FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED | WTA_MAIN_51_75_FLAT_UNMOVED | WTA_MAIN_51_75_FLAT_UNMOVED:FLOOR | PAIR_EVIDENCE_PREDICATE_UNPROVEN | 60 | 13s | 394 | -10 |

The 226-leg ATP_CHALL 51_75 partition belongs to BIG and resolved successfully. None of the six insufficient legs is in that partition. LAJ/VAN are ATP_MAIN 26_50 (n=96); their pair-constrained tuple set is exhausted. That is a pair-library coverage/fitting defect, not missing market evidence. The other four failures retain their exact named evidence predicates above.

| event | capacity-proven ask-floor pair | own-close pair | signed floor-close | discount left unharvested |
|---|---:|---:|---:|---:|
| KXATPMATCH-26JUL12LAJVAN | 95 | 102 | -7 | 7c |
| KXWTACHALLENGERMATCH-26JUL16BRAVED | 97 | 101 | -4 | 4c |
| KXWTAMATCH-26JUL20KORJIM | 90 | 102 | -12 | 12c |
