# Quote-shape library coverage gaps

Source for every count and identity below:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/823a739daed7af6073e48ec037cff05db8f3d494/.claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/QUOTE_SHAPE_LIBRARY_DYNAMIC_RENARROW_V6.json

Definitions:

- `no ordinal`: `signing_ordinal_after_a_descent_is_observed` is null because
  positive qualified-descent support is zero.
- `thin`: class membership `n < 20`; no aggregation across category or price
  region.
- `definition conflict`: no qualified-descent ordinal, but the class medoid has
  one or more progress bins with a negative raw-ask `medoid_future`. This means
  the raw future-low path and the ten-second/exact-five qualified future-low
  path disagree inside the same named class.

Population: 681 fit events, 1,343 fit legs, 16 category × starting-price
regions, 94 classes. There are 32 no-ordinal classes, 72 thin classes, 49
classes with heterogeneous observed ordinal counts, and 16 definition-conflict
classes.

| Category | Price region | No fitted ordinal | Classes with n<20 | No-ordinal definition conflict |
|---|---|---|---|---|
| ATP_CHALL | 26–50 | FLAT_UNMOVED (33); UP_CONTINUATION (77) | UP_AFTER_DIP (19) | UP_CONTINUATION (33 lower bins) |
| ATP_CHALL | 51–75 | FLAT_UNMOVED (29); UP_CONTINUATION (104) | DOWN_REBOUND (18); FLAT_RECOVERED (16) | FLAT_UNMOVED (17); UP_CONTINUATION (16) |
| ATP_CHALL | ≥76 | FLAT_UNMOVED (15); UP_CONTINUATION (42) | DOWN_CONTINUATION (12); DOWN_REBOUND (6); FLAT_RECOVERED (7); FLAT_UNMOVED (15); UP_AFTER_DIP (11) | UP_CONTINUATION (8) |
| ATP_CHALL | ≤25 | FLAT_UNMOVED (15); UP_CONTINUATION (26) | DOWN_REBOUND (13); FLAT_RECOVERED (16); FLAT_UNMOVED (15); UP_AFTER_DIP (8) | FLAT_UNMOVED (15); UP_CONTINUATION (9) |
| ATP_MAIN | 26–50 | FLAT_UNMOVED (11); UP_CONTINUATION (22) | FLAT_RECOVERED (10); FLAT_UNMOVED (11); UP_AFTER_DIP (10) | FLAT_UNMOVED (55); UP_CONTINUATION (36) |
| ATP_MAIN | 51–75 | FLAT_UNMOVED (17); UP_CONTINUATION (27) | DOWN_CONTINUATION (12); DOWN_REBOUND (17); FLAT_RECOVERED (9); FLAT_UNMOVED (17); UP_AFTER_DIP (16) | UP_CONTINUATION (40) |
| ATP_MAIN | ≥76 | FLAT_UNMOVED (4); UP_CONTINUATION (6) | all six: DOWN_CONTINUATION (3); DOWN_REBOUND (4); FLAT_RECOVERED (4); FLAT_UNMOVED (4); UP_AFTER_DIP (3); UP_CONTINUATION (6) | none |
| ATP_MAIN | ≤25 | FLAT_UNMOVED (4); UP_CONTINUATION (9) | all six: DOWN_CONTINUATION (9); DOWN_REBOUND (5); FLAT_RECOVERED (2); FLAT_UNMOVED (4); UP_AFTER_DIP (1); UP_CONTINUATION (9) | UP_CONTINUATION (30) |
| WTA_CHALL | 26–50 | FLAT_UNMOVED (28); UP_CONTINUATION (14) | DOWN_CONTINUATION (14); DOWN_REBOUND (3); FLAT_RECOVERED (3); UP_AFTER_DIP (2); UP_CONTINUATION (14) | UP_CONTINUATION (30) |
| WTA_CHALL | 51–75 | FLAT_UNMOVED (20); UP_CONTINUATION (27) | DOWN_CONTINUATION (7); DOWN_REBOUND (1); FLAT_RECOVERED (6); UP_AFTER_DIP (4) | FLAT_UNMOVED (10); UP_CONTINUATION (25) |
| WTA_CHALL | ≥76 | FLAT_UNMOVED (6); UP_CONTINUATION (10) | DOWN_CONTINUATION (6); FLAT_RECOVERED (3); FLAT_UNMOVED (6); UP_AFTER_DIP (1); UP_CONTINUATION (10) | none |
| WTA_CHALL | ≤25 | FLAT_UNMOVED (8); UP_CONTINUATION (9) | DOWN_CONTINUATION (8); DOWN_REBOUND (1); FLAT_RECOVERED (2); FLAT_UNMOVED (8); UP_CONTINUATION (9) | none |
| WTA_MAIN | 26–50 | FLAT_UNMOVED (15); UP_CONTINUATION (12) | DOWN_REBOUND (7); FLAT_RECOVERED (5); FLAT_UNMOVED (15); UP_AFTER_DIP (2); UP_CONTINUATION (12) | FLAT_UNMOVED (28); UP_CONTINUATION (16) |
| WTA_MAIN | 51–75 | FLAT_UNMOVED (17); UP_CONTINUATION (36) | DOWN_CONTINUATION (9); DOWN_REBOUND (3); FLAT_RECOVERED (4); FLAT_UNMOVED (17); UP_AFTER_DIP (4) | UP_CONTINUATION (8) |
| WTA_MAIN | ≥76 | FLAT_UNMOVED (16); UP_CONTINUATION (21) | DOWN_CONTINUATION (5); DOWN_REBOUND (3); FLAT_RECOVERED (3); FLAT_UNMOVED (16); UP_AFTER_DIP (1) | none |
| WTA_MAIN | ≤25 | FLAT_UNMOVED (15); UP_CONTINUATION (10) | DOWN_CONTINUATION (19); DOWN_REBOUND (7); FLAT_RECOVERED (5); FLAT_UNMOVED (15); UP_AFTER_DIP (2); UP_CONTINUATION (10) | none |

## Classes whose single ordinal cannot express all fitted members

The values in parentheses are the distinct qualified-descent ordinals observed
among members. These 49 class identities are the complete heterogeneous set.

| Category | Price region | Heterogeneous classes and member ordinals |
|---|---|---|
| ATP_CHALL | 26–50 | DOWN_CONTINUATION (1/2/3/4/6/7/11); DOWN_REBOUND (1/2/3/4/7/8); FLAT_RECOVERED (0/1/2); UP_AFTER_DIP (1/2/3) |
| ATP_CHALL | 51–75 | DOWN_CONTINUATION (1/2/3/4/6/8); DOWN_REBOUND (2/3/4/5/6/7); FLAT_RECOVERED (0/1/2/3); UP_AFTER_DIP (0/1/2/3) |
| ATP_CHALL | ≥76 | DOWN_CONTINUATION (1/2/3/4/5/7/8); DOWN_REBOUND (2/3/5/10); FLAT_RECOVERED (1/2); UP_AFTER_DIP (0/1/2) |
| ATP_CHALL | ≤25 | DOWN_CONTINUATION (0/1/2/3/4/5); DOWN_REBOUND (2/3/4); FLAT_RECOVERED (0/1/2); UP_AFTER_DIP (0/1/2/3) |
| ATP_MAIN | 26–50 | DOWN_CONTINUATION (0/1/2/3/4/5); DOWN_REBOUND (2/3/4/5/6/7/8/9); FLAT_RECOVERED (1/2/3); UP_AFTER_DIP (0/1/3) |
| ATP_MAIN | 51–75 | DOWN_CONTINUATION (1/2/3/4/5); DOWN_REBOUND (1/2/3/4/6/10/18); FLAT_RECOVERED (1/2/3/4/6); UP_AFTER_DIP (1/2/3/5) |
| ATP_MAIN | ≥76 | DOWN_CONTINUATION (1/2); DOWN_REBOUND (2/4/5); FLAT_RECOVERED (1/2) |
| ATP_MAIN | ≤25 | DOWN_CONTINUATION (1/2/5/9); DOWN_REBOUND (1/2/3/5) |
| WTA_CHALL | 26–50 | DOWN_CONTINUATION (0/1/2/3/6); DOWN_REBOUND (2/3); UP_AFTER_DIP (1/2) |
| WTA_CHALL | 51–75 | DOWN_CONTINUATION (1/2); UP_AFTER_DIP (0/1) |
| WTA_CHALL | ≥76 | DOWN_CONTINUATION (1/2); FLAT_RECOVERED (1/2) |
| WTA_CHALL | ≤25 | DOWN_CONTINUATION (1/2) |
| WTA_MAIN | 26–50 | DOWN_CONTINUATION (1/2/3/4/5/6); DOWN_REBOUND (2/3/4/6); FLAT_RECOVERED (1/2) |
| WTA_MAIN | 51–75 | DOWN_CONTINUATION (1/2/3); DOWN_REBOUND (1/5); FLAT_RECOVERED (1/2); UP_AFTER_DIP (1/2) |
| WTA_MAIN | ≥76 | DOWN_CONTINUATION (1/2/4/9); DOWN_REBOUND (2/3/4) |
| WTA_MAIN | ≤25 | DOWN_CONTINUATION (1/2/3/4); DOWN_REBOUND (2/3/4/10); FLAT_RECOVERED (1/2) |

## What “cannot express” means here

1. Every category × price region contains a `FLAT_UNMOVED` and an
   `UP_CONTINUATION` class with zero positive qualified descents. Once a live
   leg assigned to one of these classes descends, its behavior lies outside the
   class’s fitted ordinal support. The descent verdict must return UNKNOWN or
   reopen the macro set; the class itself cannot interpret the new behavior.
2. Forty-nine classes contain more than one realized descent ordinal. Their
   single upper-median signing ordinal is a lossy summary: it cannot express
   every member’s path even where it is available.
3. Sixteen no-ordinal classes have negative raw-ask medoid-future bins. Their
   own medoid can say LOWER while their qualified-ask ordinal says that no
   qualified descent occurred. This is not thinness. It is two target
   definitions living under one class name.

No class was pooled to make these cells appear thicker.
