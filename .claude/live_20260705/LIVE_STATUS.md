# LIVE VALIDATION — rolling status

- cycle 12 @ **2026-07-08 04:17:30 PM ET** | build `549d106` | session boot 07-08 15:20 ET | log `live_v3_20260708.jsonl` | 16868 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 24 graded (session)
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
| 15:50 | ITFWMATCH-26JUL08EKSLUX-EKS | ITF_W | ? | 45 | 45 | +0 (window_cell) | 13.0 | pre | pair | 96 | EARNED |
| 15:59 | ATPCHALLENGERMATCH-26JUL08FEALAJ-L | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | — | pre | single |  | MIXED |
| 16:00 | ITFWMATCH-26JUL08EKSLUX-LUX | ITF_W | ? | 51 | 53 | -2 (window_cell) | -15.5 | pre | pair | 96 | EARNED |
| 16:04 | ATPCHALLENGERMATCH-26JUL08MATMIC-M | ATP_CHALL | ? | 7 | 5 | +2 (window_cell) | — | pre | pair | 98 | MIXED |
| 16:05 | ITFWMATCH-26JUL08BADMEL-MEL | ITF_W | ? | 8 | 4 | +4 (fill_est) | — | pre | single |  | PENDING |
| 16:05 | WTACHALLENGERMATCH-26JUL08STEZHA-Z | WTA_CHALL | ? | 20 | 17 | +3 (window_cell) | — | pre | single |  | MIXED |
| 16:07 | ITFMATCH-26JUL08BRAMAN-MAN | ITF_M | ? | 57 | 79 | -22 (window_cell) | — | pre | single |  | MIXED |
| 16:09 | ITFMATCH-26JUL08BROKUZ-BRO | ITF_M | ? | 21 | 21 | +0 (window_cell) | — | pre | single |  | EARNED |
| 16:11 | ATPCHALLENGERMATCH-26JUL08MATMIC-M | ATP_CHALL | ? | 91 | 90 | +1 (window_cell) | — | pre | pair | 98 | GIFT_CLASS |
| 16:14 | ITFMATCH-26JUL08ANTCHA-CHA | ITF_M | ? | 32 | 28 | +4 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 3 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 3} | repriceable now: true 1 / false 2 | **cumulative bid_grade lines: 5704 (repriceable true 561 / false 5143)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 18m | 3/61-61/266 | 60-61 | 3 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08LEGROB-ROB | 6 | 28m | 793/10-28/138035 | 25-19 | 4 | **FLOW_ABOVE** | 19 | REPRICEABLE→10 |
| ITFWMATCH-26JUL08FEIBER-FEI | 58 | 57m | 414/84-99/55635 | 99-96 | 26 | **FLOW_ABOVE** | 82 | flow above but bound 82c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08MCNGAI | 35 | 16 | **51** | 97 | -46 |
| ITFMATCH-26JUL08SHEGOR | 62 | 29 | **91** | 97 | -6 |
| ITFMATCH-26JUL08BROKUZ | 21 | 76 | **97** | 97 | +0 |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | 39 | 61 | **100** | 97 | +3 |
| WTACHALLENGERMATCH-26JUL08STEZHA | 20 | 80 | **100** | 97 | +3 |
| ITFMATCH-26JUL08BRAMAN | 57 | 43 | **100** | 97 | +3 |
| ITFWMATCH-26JUL08GARBOH | 6 | 96 | **102** | 97 | +5 |
| ITFMATCH-26JUL08POLROZ | 49 | 65 | **114** | 97 | +17 |

## FLOW-STATE — 23 tracked game(s) ({'WAKING': 22, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL08MILMIS | ITF_W | 0.933 | 2 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL06HOLSCH | ATP_CHALL | 12.567 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08MATMIC | ATP_CHALL | 9.533 | — | **WAKING** |
| ITFMATCH-26JUL08ANTCHA | ITF_M | 0.133 | 3 | **WAKING** |
| ITFMATCH-26JUL08BRAMAN | ITF_M | 14.933 | — | **WAKING** |
| ITFMATCH-26JUL08BROKUZ | ITF_M | 5.2 | — | **WAKING** |
| ITFMATCH-26JUL08LEECOO | ITF_M | 2.433 | — | **WAKING** |
| ITFMATCH-26JUL08LEGROB | ITF_M | 26.967 | — | **WAKING** |
| ITFMATCH-26JUL08OCOZAM | ITF_M | 5.433 | — | **WAKING** |
| ITFMATCH-26JUL08POLROZ | ITF_M | 26.933 | — | **WAKING** |
| ITFMATCH-26JUL08SHEGOR | ITF_M | 5.1 | — | **WAKING** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL08BADMEL | ITF_W | 0.467 | 5 | **WAKING** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 14.167 | — | **WAKING** |
| ITFWMATCH-26JUL08FEIBER | ITF_W | 11.933 | — | **WAKING** |
| ITFWMATCH-26JUL08GARBOH | ITF_W | 26.633 | — | **WAKING** |
| ITFWMATCH-26JUL08LAUTOR | ITF_W | 2.233 | — | **WAKING** |
| ITFWMATCH-26JUL08LEEMAL | ITF_W | 5.333 | — | **WAKING** |
| ITFWMATCH-26JUL08MCNGAI | ITF_W | 24.767 | — | **WAKING** |
| ITFWMATCH-26JUL08PERCCU | ITF_W | 135.133 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL08STEZHA | WTA_CHALL | 0.133 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08YAMROG | WTA_CHALL | 0.133 | 1 | **WAKING** |

## PATTERNS (sub-B) — 16
- half_arm_aging: KXITFWMATCH-26JUL08GARBOH-GAR {"fill": 6, "age_min": 57, "mode": "PAIRING(sib never rested)"}
- pre_conception_buy: KXITFMATCH-26JUL08POLROZ-ROZ {"price": 49, "conception_ts": 1783540800.9758818, "detail": "buy 49c predates the conception stamp by 39min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL08LAUTOR-LAU {"fill": 6, "age_min": 55, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06HOLSCH-SCH {"fill": 50, "age_min": 55, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFWMATCH-26JUL08PERCCU-PER {"entry_minus_fv_burst": -18.0}
- half_arm_aging: KXITFWMATCH-26JUL08PERCCU-PER {"fill": 19, "age_min": 53, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08MCNGAI-MCN {"fill": 35, "age_min": 48, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08LEEMAL-MAL {"fill": 63, "age_min": 43, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08OCOZAM-ZAM {"fill": 76, "age_min": 43, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08THUPEC-THU {"fill": 23, "age_min": 37, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 04:17:30 PM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXWTACHALLENGERMATCH-26JUL08YAMROG {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- deep_neg_fv: KXITFWMATCH-26JUL08MILMIS-MIL {"entry_minus_fv_burst": -13.5}
- half_arm_aging: KXITFWMATCH-26JUL08MILMIS-MIL {"fill": 6, "age_min": 34, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 04:17:30 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL08LEECOO-LEE {"fill": 79, "age_min": 30, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 04:17:30 PM ET"}
- deep_neg_fv: KXITFWMATCH-26JUL08EKSLUX-LUX {"entry_minus_fv_burst": -15.5, "emitted_et": "2026-07-08 04:17:30 PM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL08MATMIC {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-08 04:17:30 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
