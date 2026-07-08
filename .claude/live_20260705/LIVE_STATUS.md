# LIVE VALIDATION — rolling status

- cycle 10 @ **2026-07-08 03:57:09 PM ET** | build `140623d` | session boot 07-08 15:20 ET | log `live_v3_20260708.jsonl` | 11909 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 15 graded (session)
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
| 15:47 | ITFMATCH-26JUL08LEECOO-LEE | ITF_M | ? | 79 | 76 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 15:48 | ITFMATCH-26JUL08POLROZ-ROZ | ITF_M | ? | 49 | 45 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 15:48 | ITFMATCH-26JUL08SHEGOR-GOR | ITF_M | ? | 62 | 59 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 15:50 | ITFWMATCH-26JUL08EKSLUX-EKS | ITF_W | ? | 45 | 45 | +0 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 6 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 5, 'NO_FLOW': 1} | repriceable now: true 3 / false 3 | **cumulative bid_grade lines: 5702 (repriceable true 561 / false 5141)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 59 | 32m | 2/60-60/77 | 60-61 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ATPCHALLENGERMATCH-26JUL08FEALAJ-L | 39 | 32m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BRAMAN-MAN | 57 | 36m | 153/65-84/6943 | 77-76 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08LEGROB-ROB | 6 | 8m | 117/10-20/12643 | 18-15 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL08BADMEL-MEL | 8 | 36m | 9/11-13/208 | 8-12 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFWMATCH-26JUL08FEIBER-FEI | 58 | 36m | 137/84-95/18740 | 94-95 | 26 | **FLOW_ABOVE** | 82 | flow above but bound 82c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08MCNGAI | 35 | 35 | **70** | 97 | -27 |
| ITFWMATCH-26JUL08GARBOH | 6 | 87 | **93** | 97 | -4 |
| ITFWMATCH-26JUL08EKSLUX | 45 | 62 | **107** | 97 | +10 |

## FLOW-STATE — 19 tracked game(s) ({'WAKING': 14, 'OPEN': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08LEECOO | ITF_M | 0.2 | 3 | **OPEN** |
| ITFMATCH-26JUL08POLROZ | ITF_M | 11.367 | 1 | **OPEN** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 0.767 | 1 | **OPEN** |
| ITFWMATCH-26JUL08FEIBER | ITF_W | 4.367 | 1 | **OPEN** |
| ITFWMATCH-26JUL08LEEMAL | ITF_W | 2.5 | 3 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL06HOLSCH | ATP_CHALL | 43.833 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL08BRAMAN | ITF_M | 5.033 | — | **WAKING** |
| ITFMATCH-26JUL08LEGROB | ITF_M | 6.467 | — | **WAKING** |
| ITFMATCH-26JUL08OCOZAM | ITF_M | 1.9 | 5 | **WAKING** |
| ITFMATCH-26JUL08SHEGOR | ITF_M | 1.7 | — | **WAKING** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL08BADMEL | ITF_W | 0.3 | 4 | **WAKING** |
| ITFWMATCH-26JUL08GARBOH | ITF_W | 10.933 | — | **WAKING** |
| ITFWMATCH-26JUL08LAUTOR | ITF_W | 11.2 | — | **WAKING** |
| ITFWMATCH-26JUL08MCNGAI | ITF_W | 14.5 | — | **WAKING** |
| ITFWMATCH-26JUL08MILMIS | ITF_W | 1.667 | 5 | **WAKING** |
| ITFWMATCH-26JUL08PERCCU | ITF_W | 66.8 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL08YAMROG | WTA_CHALL | 0.167 | 1 | **WAKING** |

## PATTERNS (sub-B) — 7
- half_arm_aging: KXITFWMATCH-26JUL08GARBOH-GAR {"fill": 6, "age_min": 36, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 03:57:09 PM ET"}
- half_arm_aging: KXITFWMATCH-26JUL08LAUTOR-LAU {"fill": 6, "age_min": 35, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 03:57:09 PM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06HOLSCH-SCH {"fill": 50, "age_min": 35, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFWMATCH-26JUL08PERCCU-PER {"entry_minus_fv_burst": -18.0}
- half_arm_aging: KXITFWMATCH-26JUL08PERCCU-PER {"fill": 19, "age_min": 33, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 03:57:09 PM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXWTACHALLENGERMATCH-26JUL08YAMROG {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- deep_neg_fv: KXITFWMATCH-26JUL08MILMIS-MIL {"entry_minus_fv_burst": -13.5}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
