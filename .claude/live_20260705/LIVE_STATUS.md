# LIVE VALIDATION — rolling status

- cycle 11 @ **2026-07-08 04:07:20 PM ET** | build `cc4e73a` | session boot 07-08 15:20 ET | log `live_v3_20260708.jsonl` | 15061 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 20 graded (session)
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
| 15:48 | ITFMATCH-26JUL08POLROZ-ROZ | ITF_M | ? | 49 | 37 | +12 (window_cell) | — | pre | single |  | MIXED |
| 15:48 | ITFMATCH-26JUL08SHEGOR-GOR | ITF_M | ? | 62 | 45 | +17 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 15:50 | ITFWMATCH-26JUL08EKSLUX-EKS | ITF_W | ? | 45 | 45 | +0 (window_cell) | — | pre | pair | 96 | EARNED |
| 15:59 | ATPCHALLENGERMATCH-26JUL08FEALAJ-L | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | — | pre | single |  | MIXED |
| 16:00 | ITFWMATCH-26JUL08EKSLUX-LUX | ITF_W | ? | 51 | 53 | -2 (window_cell) | — | pre | pair | 96 | MIXED |
| 16:04 | ATPCHALLENGERMATCH-26JUL08MATMIC-M | ATP_CHALL | ? | 7 | 5 | +2 (window_cell) | — | pre | single |  | MIXED |
| 16:05 | ITFWMATCH-26JUL08BADMEL-MEL | ITF_W | ? | 8 | 4 | +4 (fill_est) | — | pre | single |  | PENDING |
| 16:05 | WTACHALLENGERMATCH-26JUL08STEZHA-Z | WTA_CHALL | ? | 20 | 17 | +3 (window_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 4 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 3, 'FLOW_AT_LEVEL': 1} | repriceable now: true 1 / false 3 | **cumulative bid_grade lines: 5704 (repriceable true 561 / false 5143)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 8m | 1/61-61/10 | 60-61 | 3 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08BRAMAN-MAN | 57 | 46m | 391/57-88/27163 | 73-58 | 0 | **FLOW_AT_LEVEL** | 79 |  |
| ITFMATCH-26JUL08LEGROB-ROB | 6 | 18m | 408/10-28/53416 | 24-23 | 4 | **FLOW_ABOVE** | 19 | REPRICEABLE→10 |
| ITFWMATCH-26JUL08FEIBER-FEI | 58 | 47m | 320/84-99/48323 | 99-97 | 26 | **FLOW_ABOVE** | 82 | flow above but bound 82c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08MCNGAI | 35 | 28 | **63** | 97 | -34 |
| ITFWMATCH-26JUL08GARBOH | 6 | 83 | **89** | 97 | -8 |
| ATPCHALLENGERMATCH-26JUL08MATMIC | 7 | 92 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | 39 | 61 | **100** | 97 | +3 |
| WTACHALLENGERMATCH-26JUL08STEZHA | 20 | 80 | **100** | 97 | +3 |
| ITFMATCH-26JUL08POLROZ | 49 | 54 | **103** | 97 | +6 |
| ITFMATCH-26JUL08SHEGOR | 62 | 50 | **112** | 97 | +15 |

## FLOW-STATE — 21 tracked game(s) ({'WAKING': 20, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL08MILMIS | ITF_W | 1.9 | 3 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL06HOLSCH | ATP_CHALL | 31.3 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08MATMIC | ATP_CHALL | 2.133 | — | **WAKING** |
| ITFMATCH-26JUL08BRAMAN | ITF_M | 11.3 | — | **WAKING** |
| ITFMATCH-26JUL08LEECOO | ITF_M | 1.467 | — | **WAKING** |
| ITFMATCH-26JUL08LEGROB | ITF_M | 15.833 | — | **WAKING** |
| ITFMATCH-26JUL08OCOZAM | ITF_M | 4.267 | — | **WAKING** |
| ITFMATCH-26JUL08POLROZ | ITF_M | 19.6 | — | **WAKING** |
| ITFMATCH-26JUL08SHEGOR | ITF_M | 3.433 | — | **WAKING** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL08BADMEL | ITF_W | 0.3 | 4 | **WAKING** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 7.967 | — | **WAKING** |
| ITFWMATCH-26JUL08FEIBER | ITF_W | 9.867 | — | **WAKING** |
| ITFWMATCH-26JUL08GARBOH | ITF_W | 22.067 | — | **WAKING** |
| ITFWMATCH-26JUL08LAUTOR | ITF_W | 6.133 | — | **WAKING** |
| ITFWMATCH-26JUL08LEEMAL | ITF_W | 3.2 | — | **WAKING** |
| ITFWMATCH-26JUL08MCNGAI | ITF_W | 19.933 | — | **WAKING** |
| ITFWMATCH-26JUL08PERCCU | ITF_W | 96.233 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL08STEZHA | WTA_CHALL | 0.1 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08YAMROG | WTA_CHALL | 0.233 | 1 | **WAKING** |

## PATTERNS (sub-B) — 11
- half_arm_aging: KXITFWMATCH-26JUL08GARBOH-GAR {"fill": 6, "age_min": 47, "mode": "PAIRING(sib never rested)"}
- pre_conception_buy: KXITFMATCH-26JUL08POLROZ-ROZ {"price": 49, "conception_ts": 1783540800.9758818, "detail": "buy 49c predates the conception stamp by 39min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-08 04:07:20 PM ET"}
- half_arm_aging: KXITFWMATCH-26JUL08LAUTOR-LAU {"fill": 6, "age_min": 45, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06HOLSCH-SCH {"fill": 50, "age_min": 45, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFWMATCH-26JUL08PERCCU-PER {"entry_minus_fv_burst": -18.0}
- half_arm_aging: KXITFWMATCH-26JUL08PERCCU-PER {"fill": 19, "age_min": 43, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08MCNGAI-MCN {"fill": 35, "age_min": 38, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 04:07:20 PM ET"}
- half_arm_aging: KXITFWMATCH-26JUL08LEEMAL-MAL {"fill": 63, "age_min": 33, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08OCOZAM-ZAM {"fill": 76, "age_min": 33, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 04:07:20 PM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXWTACHALLENGERMATCH-26JUL08YAMROG {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- deep_neg_fv: KXITFWMATCH-26JUL08MILMIS-MIL {"entry_minus_fv_burst": -13.5}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
