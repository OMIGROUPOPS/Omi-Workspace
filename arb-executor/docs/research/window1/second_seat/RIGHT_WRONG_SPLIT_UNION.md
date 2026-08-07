# Right-side / wrong-side split — the union maker book

Analysis seat only. Read-only. Union maker book `57daf3c1`. Per credited side:
**GAP = union fill price − that side's cheapest traded price in its W1 span**
(0 = we got the true bottom; >0 = cents left; <0 = we beat the bottom via ask-dwell
below any trade). Right = gap ≤ 1¢. Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RIGHT_WRONG_SPLIT_UNION.json`.

## The union book is bottom-optimal — no wrong sides

| side gap | sides | meaning |
|---|--:|---|
| **> 0 (cents left)** | **0** | — |
| = 0 (got the bottom) | 1,441 | filled at the side's cheapest trade |
| < 0 (beat the bottom) | 116 | ask dwelled ≤ our rest *below* any trade (to −18¢) |

**GAP > 0 never occurs.** Because TRADED_AT_LEVEL (the cheapest trade) is a union channel,
the union fill is ≤ the cheapest trade **by construction** — every credited side gets its
true bottom or better.

**Per-game classes (of 785 both-sides / 637 under-par):**

| class | games |
|---|--:|
| **BOTH_RIGHT** | 773 |
| ONE_RIGHT | 11 |
| BOTH_WRONG | 1 |

The 12 non-BOTH_RIGHT games have a side that **never traded** (filled purely on ask-dwell,
so no traded price to compare) — not a side that left cents. Every side with a traded
reference is right. **Recoverable cents if every wrong side had its bottom = 0.** On the
union book there is nothing to recover: it already holds every side's bottom.

## Where the wrong sides live — the quote-only channel (what the union fixes)

The informative right/wrong pattern is in the narrower **QUOTE_TOUCH** channel — the
dwelled-ask book the union's TRADED_AT_LEVEL + PRINT_CROSS channels rescue.

| class (quote-only, /392 under-par, /688 both-sides) | games |
|---|--:|
| BOTH_RIGHT | 593 |
| **ONE_RIGHT** | **95** |
| BOTH_WRONG | 4 |

**90 wrong sides** (quote fill > cheapest trade by >1¢), gap median 2¢, total 256¢.

**The wrong-side pattern:**

| axis | wrong sides |
|---|--:|
| **FALLER / SETTLED** | **60** |
| RISER | 30 |
| **DOG** (close < 50) | **53** |
| FAVORITE (close ≥ 50) | 37 |

The faller/settled side (bid−1 tracking) is wrong **twice as often** as the riser (whose
recurring ask-divot floor sits closer to the bottom), and the **dog** (cheap side) is wrong
more than the favorite: a resting bid tracking a falling book gets left when a trade
punches below the dwelled ask, and cheap sides have the deepest such punches.

**Gap distribution (quote-only, per category, cents):** ATP_MAIN median 1 / p90 2 /
total 146 (worst); ATP_CHALL median 0 / p90 1 / total 171; WTA_MAIN median 1 / total 110;
WTA_CHALL median 0 / total 82.

**Recoverable by the union's extra channels over quote-only = $7.29 (729¢)** — the cents
TRADED_AT_LEVEL + PRINT_CROSS put back that the dwelled-ask book would have left.

## Named rows

| game · side | dir | cheapest traded | union fill | **gap (union)** | quote fill | gap (quote) |
|---|---|--:|--:|--:|--:|--:|
| ARNROM · ARN | — | 50 | **50** | **0** | 55 | +5 |
| ARNROM · ROM | — | 38 | 38 | 0 | 38 | 0 |
| BOSCOP · BOS | — | 28 | 28 | 0 | 28 | 0 |
| **BOSCOP · COP** | — | 47 | **47** | **0** | 63 | **+16** |
| NIKVRB · NIK | FALLING | 18 | 18 | 0 | 18 | 0 |
| **NIKVRB · VRB** | CLIMBING | 70 | **68** | **−2** | 68 | −2 |

The union got every named side's bottom (gap 0), and **VRB beat it by 2¢** (the climber's
ask dwelled at 68, below the cheapest trade 70). The recovery the union performs is visible
in the quote column: **COP would have filled at 63 on the dwelled ask — a trade at 47 (the
union) puts 16¢ back**; **ARN 55 → 50 (+5¢)**. On the quote-only book these are the wrong
sides; on the union they are right.

## Conservation

785 both-sides games = 773 BOTH_RIGHT + 11 ONE_RIGHT + 1 BOTH_WRONG; 637 under-par (all
right on the union). 1,557 credited sides with a traded reference: 1,441 gap=0 + 116 gap<0
+ 0 gap>0. Quote-only: 593/95/4 classes, 90 wrong sides, 256¢ left; recoverable by
union channels 729¢. Prints scanned 373,203.
