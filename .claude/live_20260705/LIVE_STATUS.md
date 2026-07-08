# LIVE VALIDATION — rolling status

- cycle 9 @ **2026-07-08 03:46:53 PM ET** | build `49786fb` | session boot 07-08 15:20 ET | log `live_v3_20260708.jsonl` | 8526 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 11 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:20 | ITFWMATCH-26JUL08GARBOH-GAR | ITF_W | ? | 6 | 2 | +4 (window_cell) | — | pre | single |  | MIXED |
| 15:22 | ITFWMATCH-26JUL08LAUTOR-LAU | ITF_W | ? | 6 | 2 | +4 (fill_est) | -0.5 | pre | single |  | MIXED |
| 15:22 | ATPCHALLENGERMATCH-26JUL06HOLSCH-S | ATP_CHALL | ? | 50 | 47 | +3 (fill_est) | -0.5 | pre | single |  | MIXED |
| 15:24 | ITFWMATCH-26JUL08PERCCU-PER | ITF_W | ? | 19 | 15 | +4 (fill_est) | -18.0 | 0.8 | single |  | EARNED |
| 15:26 | WTACHALLENGERMATCH-26JUL08YAMROG-Y | WTA_CHALL | ? | 57 | 55 | +2 (window_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 15:29 | ITFWMATCH-26JUL08MCNGAI-MCN | ITF_W | ? | 35 | 48 | -13 (window_cell) | 0.0 | pre | single |  | EARNED |
| 15:34 | ITFWMATCH-26JUL08LEEMAL-MAL | ITF_W | ? | 63 | 61 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 15:34 | ITFMATCH-26JUL08OCOZAM-ZAM | ITF_M | ? | 76 | 73 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 15:40 | ITFMATCH-26JUL08THUPEC-THU | ITF_M | ? | 23 | 19 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 15:40 | WTACHALLENGERMATCH-26JUL08YAMROG-R | WTA_CHALL | ? | 42 | 40 | +2 (window_cell) | — | pre | pair | 99 | MIXED |
| 15:43 | ITFWMATCH-26JUL08MILMIS-MIL | ITF_W | ? | 6 | 2 | +4 (fill_est) | -13.5 | 0.7 | single |  | EARNED |

## RESTING BIDS — 8 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 7, 'NO_FLOW': 1} | repriceable now: true 4 / false 4 | **cumulative bid_grade lines: 5701 (repriceable true 560 / false 5141)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 59 | 21m | 2/60-60/77 | 60-61 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ATPCHALLENGERMATCH-26JUL08FEALAJ-L | 39 | 21m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BRAMAN-MAN | 57 | 25m | 82/65-82/2660 | 79-80 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08LEGROB-ROB | 5 | 26m | 57/7-12/4767 | 6-9 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→7 |
| ITFMATCH-26JUL08POLROZ-ROZ | 49 | 26m | 215/53-85/9700 | 52-53 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→53 |
| ITFWMATCH-26JUL08BADMEL-MEL | 8 | 26m | 9/11-13/208 | 8-12 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFWMATCH-26JUL08FEIBER-FEI | 58 | 26m | 53/84-91/5132 | 91-92 | 26 | **FLOW_ABOVE** | 82 | flow above but bound 82c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08REARAB-REA | 57 | 25m | 210/73-99/21542 | 97-98 | 16 | **FLOW_ABOVE** | 82 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08MCNGAI | 35 | 57 | **92** | 97 | -5 |
| ITFWMATCH-26JUL08GARBOH | 6 | 92 | **98** | 97 | +1 |

## FLOW-STATE — 17 tracked game(s) ({'OPEN': 11, 'WAKING': 6}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06HOLSCH | ATP_CHALL | 35.9 | 1 | **OPEN** |
| ITFMATCH-26JUL08BRAMAN | ITF_M | 2.767 | 1 | **OPEN** |
| ITFMATCH-26JUL08LEGROB | ITF_M | 1.9 | 3 | **OPEN** |
| ITFMATCH-26JUL08OCOZAM | ITF_M | 0.833 | 1 | **OPEN** |
| ITFMATCH-26JUL08POLROZ | ITF_M | 7.233 | 1 | **OPEN** |
| ITFWMATCH-26JUL08FEIBER | ITF_W | 1.933 | 1 | **OPEN** |
| ITFWMATCH-26JUL08GARBOH | ITF_W | 6.633 | 3 | **OPEN** |
| ITFWMATCH-26JUL08LEEMAL | ITF_W | 1.0 | 1 | **OPEN** |
| ITFWMATCH-26JUL08MCNGAI | ITF_W | 8.833 | 3 | **OPEN** |
| ITFWMATCH-26JUL08MILMIS | ITF_W | 1.267 | 2 | **OPEN** |
| ITFWMATCH-26JUL08REARAB | ITF_W | 7.033 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL08BADMEL | ITF_W | 0.3 | 4 | **WAKING** |
| ITFWMATCH-26JUL08LAUTOR | ITF_W | 12.233 | — | **WAKING** |
| ITFWMATCH-26JUL08PERCCU | ITF_W | 46.533 | 6 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08YAMROG | WTA_CHALL | 0.167 | 1 | **WAKING** |

## PATTERNS (sub-B) — 3
- deep_neg_fv: KXITFWMATCH-26JUL08PERCCU-PER {"entry_minus_fv_burst": -18.0}
- combined_over_goal_UNVERIFIED_BASIS: KXWTACHALLENGERMATCH-26JUL08YAMROG {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-08 03:46:53 PM ET"}
- deep_neg_fv: KXITFWMATCH-26JUL08MILMIS-MIL {"entry_minus_fv_burst": -13.5, "emitted_et": "2026-07-08 03:46:53 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
