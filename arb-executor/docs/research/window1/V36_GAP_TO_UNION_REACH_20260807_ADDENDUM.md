# V36 gap to union reach — 2026-08-07 addendum

## Binding

- V36 actual output: `bfde0d8d1135f5c5f48a5f3d619ab30050efab83`, STRICT column only.
- Union maker-reach ruler: `57daf3c15ad618098a810566d24127df8f17f3f9`.
- Reconstructed union law: per-leg minimum of the sealed 10-second quote-touch level and the lowest lawful true trade in the ruler's whole-second-inclusive interval.
- Exact ruler reproduction: 373,203 prints; trade availability 773/11/20; union availability 785/0/19; 1,570 reach legs; price sum 73,300¢; 637 under-par games; frontier 120/183/345/637; 5,253¢ locked.

## Grade

| class | games | V36 completed | missing sides | shallow sides | shallow cents |
|---|---:|---:|---:|---:|---:|
| MATCHED | 52 | 52 | 0 | 0 | 0 |
| SHALLOW | 212 | 212 | 0 | 269 | 1,406 |
| ONE_MISSING | 486 | 0 | 486 | 384 | 2,267 |
| BOTH_MISSING | 35 | 0 | 70 | 0 | 0 |
| NO_REACH | 19 | 6 | 0 | 0 | 0 |

SHALLOW per-leg gap: n=269, median 2¢, p75 4¢, p90 9¢, max 60¢, total 1,406¢. The credited side of ONE_MISSING was itself shallow in 384 cases: median 3¢, p75 5¢, p90 11¢, max 68¢, total 2,267¢.

Six NO_REACH games are V36-complete because the two frozen packages bind different window edges. They remain NO_REACH/ungradeable; no later V36 price is backfilled into the 57daf3c1 ruler.

## Layer bind

| owner | games | issue sides | measured cents | unpriced sides |
|---|---:|---:|---:|---:|
| TAKE_FIRED_ABOVE_REACH | 539 | 569 | 3,046 | 0 |
| REST_PLACED_OFF_REACH_LEVEL | 185 | 214 | 1,078 | 0 |
| PAIR_CAP_ARITHMETIC | 270 | 270 | 866 | 0 |
| DIVOT_CLASS_NOT_IMPLEMENTED | 64 | 66 | 152 | 0 |
| FILL_MODEL_SEAM_NOT_V36_ORGAN | 83 | 86 | 0 | 0 |
| ADMISSION_NO_TWO_SIDED_BOOK | 2 | 4 | 0 | 4 |

Games overlap across organ rows. Measured cents are entry-minus-reach for shallow credits and the contemporaneous rest/cap shortfall to reach for missing sides. Missing prices are never assigned an invented fill or penalty. The fill-model seam is not a V36 policy organ: in 86 missing sides, V36 already had a rest at or above the union-reach level, but its strict print-crossing build-verification ruler did not credit the market-measurement reach.

The full 804-game, 1,608-leg, category × bell-confidence, reach-moment, terminal-state, and organ ledgers are frozen under `.claude/window1_live_v4_replay/v36_gap_to_union_reach_20260807/`.

Two clean builds produced 14 regenerable files / 752,304 bytes byte-identically. Focused tests passed 12/12. No policy or replay was invoked; no holdout, network, live, order, position, or exit surface was accessed or mutated.
