# LIVE VALIDATION — rolling status

- cycle 154 @ **2026-07-06 01:09:57 PM ET** | build `56cd3f5` | session boot 07-06 12:15 ET | log `live_v3_20260706.jsonl` | 7379 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 12:26:21 | **handler_error** | on_bbo_update_error | [Errno 28] No space left on device |
| 12:26:21 | **handler_error** | error | [Errno 28] No space left on device |

## FILLS — 27 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 12:15 | ITFMATCH-26JUL06IAMBEN-IAM | ITF_M | ? | 66 | 64 | +2 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 12:15 | ATPCHALLENGERMATCH-26JUL06DEHUD-DE | ATP_CHALL | ? | 36 | 33 | +3 (adopted_est) | -48.5 | pre | single |  | EARNED |
| 12:15 | ITFMATCH-26JUL06BROTHU-BRO | ITF_M | ? | 38 | 34 | +4 (adopted_est) | 25.0 | pre | single |  | GIFT_CLASS |
| 12:15 | ITFWMATCH-26JUL06TRATEO-TRA | ITF_W | ? | 18 | 14 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:16 | ITFMATCH-26JUL06IAMBEN-BEN | ITF_M | ? | 31 | 30 | +1 (window_cell) | — | pre | pair | 97 | EARNED |
| 12:17 | ATPCHALLENGERMATCH-26JUL06KASCIN-K | ATP_CHALL | ? | 43 | 40 | +3 (fill_est) | -8.5 | pre | single |  | EARNED |
| 12:18 | WTACHALLENGERMATCH-26JUL06CURDOD-D | WTA_CHALL | ? | 29 | 32 | -3 (window_cell) | 21.0 | pre | single |  | EARNED |
| 12:18 | ATPCHALLENGERMATCH-26JUL06SANARN-A | ATP_CHALL | ? | 53 | 51 | +2 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 12:18 | ITFWMATCH-26JUL06POHSTU-POH | ITF_W | ? | 28 | 24 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 12:21 | ITFMATCH-26JUL06SLODIF-SLO | ITF_M | ? | 55 | 40 | +15 (window_cell) | — | pre | pair | 93 | GIFT_CLASS |
| 12:22 | ITFMATCH-26JUL06SURMED-MED | ITF_M | ? | 56 | 53 | +3 (adopted_est) | -7.0 | pre | single |  | EARNED |
| 12:22 | ITFMATCH-26JUL06CUNLIM-CUN | ITF_M | ? | 79 | 76 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 12:23 | ATPCHALLENGERMATCH-26JUL06HUETEN-T | ATP_CHALL | ? | 29 | 53 | -24 (window_cell) | — | pre | single |  | EARNED |
| 12:27 | ITFWMATCH-26JUL06MARBED-MAR | ITF_W | ? | 79 | 77 | +2 (adopted_est) | -9.5 | pre | single |  | EARNED |
| 12:34 | ITFWMATCH-26JUL06BERMEL-BER | ITF_W | leader | 84 | 75 | +9 (place_cell) | — | pre | single |  | PENDING |
| 12:35 | ITFWMATCH-26JUL06SINUSU-SIN | ITF_W | ? | 35 | 31 | +4 (fill_est) | -1.0 | pre | single |  | MIXED |
| 12:35 | ITFWMATCH-26JUL06POHSTU-STU | ITF_W | ? | 69 | 67 | +2 (fill_est) | — | pre | pair | 97 | PENDING |
| 12:36 | WTACHALLENGERMATCH-26JUL06DENQUE-Q | WTA_CHALL | ? | 92 | 89 | +3 (adopted_est) | -5.5 | pre | single |  | EARNED |
| 12:39 | ATPCHALLENGERMATCH-26JUL06CLAPAP-C | ATP_CHALL | ? | 71 | 86 | -15 (window_cell) | — | pre | single |  | MIXED |
| 12:42 | ITFMATCH-26JUL06LUEVAN-LUE | ITF_M | ? | 75 | 72 | +3 (fill_est) | 15.5 | pre | single |  | GIFT_CLASS |
| 12:42 | ATPCHALLENGERMATCH-26JUL06PALKOL-P | ATP_CHALL | ? | 22 | 23 | -1 (window_cell) | — | pre | single |  | EARNED |
| 12:43 | ITFMATCH-26JUL06SLODIF-DIF | ITF_M | underdog | 38 | 42 | -4 (place_cell) | — | pre | pair | 93 | EARNED |
| 12:46 | ITFMATCH-26JUL06DONDEV-DEV | ITF_M | ? | 24 | 58 | -34 (window_cell) | 4.0 | pre | single |  | EARNED |
| 12:46 | ATPCHALLENGERMATCH-26JUL06MAGROD-R | ATP_CHALL | ? | 52 | 52 | +0 (window_cell) | — | pre | single |  | MIXED |
| 12:47 | ITFWMATCH-26JUL06LIMDEK-DEK | ITF_W | ? | 23 | 8 | +15 (place_cell) | — | pre | single |  | MIXED |
| 12:52 | WTACHALLENGERMATCH-26JUL06COLSMI-S | WTA_CHALL | ? | 60 | 57 | +3 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 12:57 | ITFMATCH-26JUL06XUXBER-BER | ITF_M | ? | 32 | 53 | -21 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 12 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 5, 'NO_FLOW': 2, 'FLOW_AT_LEVEL': 5} | repriceable now: true 2 / false 10 | **cumulative bid_grade lines: 2462 (repriceable true 230 / false 2232)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06ABOALVA- | 56 | 9m | 1/56-56/1 | 56-57 | 0 | **FLOW_AT_LEVEL** | 53 |  |
| ATPCHALLENGERMATCH-26JUL06ABOALVA- | 42 | 9m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06CLAPAP-P | 15 | 29m | 282/3-36/50321 | 3-4 | -12 | **FLOW_AT_LEVEL** | 15 |  |
| ATPCHALLENGERMATCH-26JUL06MAGROD-R | 53 | 15m | 133/51-62/7705 | 54-55 | -2 | **FLOW_AT_LEVEL** | 52 |  |
| ATPCHALLENGERMATCH-26JUL06PALKOL-P | 22 | 10m | 96/25-45/12269 | 41-39 | 3 | **FLOW_ABOVE** | 23 | REPRICEABLE→23 |
| ATPCHALLENGERMATCH-26JUL06PERMEL-P | 2 | 4m | 1/8-8/1 | 4-8 | 6 | **FLOW_ABOVE** | 3 | flow above but bound 3c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06SANARN-A | 53 | 33m | 306/47-72/31374 | 51-50 | -6 | **FLOW_AT_LEVEL** | 51 |  |
| ATPCHALLENGERMATCH-26JUL06WEIGRA-G | 81 | 21m | 59/98-99/30174 | 98-99 | 17 | **FLOW_ABOVE** | 89 | flow above but bound 89c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06ZEBAND-A | 77 | 49m | 2/81-81/9 | 80-81 | 4 | **FLOW_ABOVE** | 78 | REPRICEABLE→78 |
| ITFMATCH-26JUL06CUNLIM-LIM | 18 | 48m | 0 | 22-24 | — | **NO_FLOW** | 18 |  |
| ITFMATCH-26JUL06DONDEV-DEV | 24 | 14m | 496/1-74/43949 | 32-1 | -23 | **FLOW_AT_LEVEL** | 58 |  |
| ITFWMATCH-26JUL06BERMEL-MEL | 13 | 28m | 71/31-71/4554 | 38-40 | 18 | **FLOW_ABOVE** | 13 | flow above but bound 13c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL06XUXBER | 32 | 25 | **57** | 97 | -40 |
| ATPCHALLENGERMATCH-26JUL06CLAPAP | 71 | 4 | **75** | 97 | -22 |
| ATPCHALLENGERMATCH-26JUL06PALKOL | 22 | 59 | **81** | 97 | -16 |
| ATPCHALLENGERMATCH-26JUL06MAGROD | 52 | 41 | **93** | 97 | -4 |
| ATPCHALLENGERMATCH-26JUL06SANARN | 53 | 49 | **102** | 97 | +5 |
| ITFMATCH-26JUL06CUNLIM | 79 | 24 | **103** | 97 | +6 |
| ITFMATCH-26JUL06DONDEV | 24 | 80 | **104** | 97 | +7 |
| ATPCHALLENGERMATCH-26JUL06HUETEN | 29 | 79 | **108** | 97 | +11 |
| ITFWMATCH-26JUL06LIMDEK | 23 | 94 | **117** | 97 | +20 |
| ITFWMATCH-26JUL06BERMEL | 84 | 40 | **124** | 97 | +27 |
| WTACHALLENGERMATCH-26JUL06CURDOD | 29 | 99 | **128** | 97 | +31 |

## PATTERNS (sub-B) — 19
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06DEHUD-DE {"entry_minus_fv_burst": -48.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06DEHUD-DE {"fill": 36, "age_min": 54, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06BROTHU-BRO {"fill": 38, "age_min": 54, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL06TRATEO-TRA {"fill": 18, "age_min": 54, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06KASCIN-KAS {"entry_minus_fv_burst": -8.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06KASCIN-KAS {"fill": 43, "age_min": 53, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06CURDOD-DOD {"fill": 29, "age_min": 52, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"fill": 53, "age_min": 52, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06SURMED-MED {"fill": 56, "age_min": 48, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06CUNLIM-CUN {"fill": 79, "age_min": 48, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06HUETEN-TEN {"fill": 29, "age_min": 46, "mode": "PAIRING(sib never rested)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LIMDEK-DEK {"price": 21, "ceiling": 19, "emitted_et": "2026-07-06 01:09:57 PM ET"}
- deep_neg_fv: KXITFWMATCH-26JUL06MARBED-MAR {"entry_minus_fv_burst": -9.5}
- half_arm_aging: KXITFWMATCH-26JUL06MARBED-MAR {"fill": 79, "age_min": 42, "mode": "PAIRING(sib never rested)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LIMDEK-DEK {"price": 24, "ceiling": 19, "emitted_et": "2026-07-06 01:09:57 PM ET"}
- half_arm_aging: KXITFWMATCH-26JUL06BERMEL-BER {"fill": 84, "age_min": 36, "mode": "SET_BELOW_FLOW(prints 18c above)", "emitted_et": "2026-07-06 01:09:57 PM ET"}
- half_arm_aging: KXITFWMATCH-26JUL06SINUSU-SIN {"fill": 35, "age_min": 34, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-06 01:09:57 PM ET"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06DENQUE-QUE {"fill": 92, "age_min": 33, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-06 01:09:57 PM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06CLAPAP-CLA {"fill": 71, "age_min": 31, "mode": "QUEUE(flow at/below our level, unfilled)"}

## ERRORS — 2 handler errors this session (SEE ZERO-TOLERANCE)
