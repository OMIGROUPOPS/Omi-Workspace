# LIVE VALIDATION — rolling status

- cycle 159 @ **2026-07-06 02:00:41 PM ET** | build `815b372` | session boot 07-06 12:15 ET | log `live_v3_20260706.jsonl` | 10849 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 4 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 12:26:21 | **handler_error** | on_bbo_update_error | [Errno 28] No space left on device |
| 12:26:21 | **handler_error** | error | [Errno 28] No space left on device |
| 13:18:15 | **grace_breach** | KXATPMATCH-26JUL06FRIBUB-FRI | fill 64c 49.7min past latch (grace 300s) |
| 13:49:18 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL06MONCOU | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 38 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 12:15 | ITFMATCH-26JUL06IAMBEN-IAM | ITF_M | ? | 66 | 64 | +2 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 12:15 | ATPCHALLENGERMATCH-26JUL06DEHUD-DE | ATP_CHALL | ? | 36 | 33 | +3 (adopted_est) | -48.5 | pre | single |  | EARNED |
| 12:15 | ITFMATCH-26JUL06BROTHU-BRO | ITF_M | ? | 38 | 34 | +4 (adopted_est) | 25.0 | pre | single |  | GIFT_CLASS |
| 12:15 | ITFWMATCH-26JUL06TRATEO-TRA | ITF_W | ? | 18 | 14 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:16 | ITFMATCH-26JUL06IAMBEN-BEN | ITF_M | ? | 31 | 30 | +1 (window_cell) | — | pre | pair | 97 | EARNED |
| 12:17 | ATPCHALLENGERMATCH-26JUL06KASCIN-K | ATP_CHALL | ? | 43 | 40 | +3 (fill_est) | -8.5 | pre | single |  | EARNED |
| 12:18 | WTACHALLENGERMATCH-26JUL06CURDOD-D | WTA_CHALL | ? | 29 | 32 | -3 (window_cell) | 21.0 | pre | single |  | EARNED |
| 12:18 | ATPCHALLENGERMATCH-26JUL06SANARN-A | ATP_CHALL | ? | 53 | 51 | +2 (window_cell) | 23.5 | pre | single |  | GIFT_CLASS |
| 12:18 | ITFWMATCH-26JUL06POHSTU-POH | ITF_W | ? | 28 | 75 | -47 (window_cell) | — | pre | pair | 97 | EARNED |
| 12:21 | ITFMATCH-26JUL06SLODIF-SLO | ITF_M | ? | 55 | 40 | +15 (window_cell) | 30.5 | pre | pair | 93 | GIFT_CLASS |
| 12:22 | ITFMATCH-26JUL06SURMED-MED | ITF_M | ? | 56 | 53 | +3 (adopted_est) | -7.0 | pre | single |  | EARNED |
| 12:22 | ITFMATCH-26JUL06CUNLIM-CUN | ITF_M | ? | 79 | 76 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 12:23 | ATPCHALLENGERMATCH-26JUL06HUETEN-T | ATP_CHALL | ? | 29 | 53 | -24 (window_cell) | — | pre | single |  | EARNED |
| 12:27 | ITFWMATCH-26JUL06MARBED-MAR | ITF_W | ? | 79 | 77 | +2 (adopted_est) | -9.5 | pre | single |  | EARNED |
| 12:34 | ITFWMATCH-26JUL06BERMEL-BER | ITF_W | leader | 84 | 75 | +9 (place_cell) | — | pre | pair | 97 | PENDING |
| 12:35 | ITFWMATCH-26JUL06SINUSU-SIN | ITF_W | ? | 35 | 31 | +4 (fill_est) | -1.0 | pre | single |  | MIXED |
| 12:35 | ITFWMATCH-26JUL06POHSTU-STU | ITF_W | ? | 69 | 21 | +48 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 12:36 | WTACHALLENGERMATCH-26JUL06DENQUE-Q | WTA_CHALL | ? | 92 | 89 | +3 (adopted_est) | -5.5 | pre | single |  | EARNED |
| 12:39 | ATPCHALLENGERMATCH-26JUL06CLAPAP-C | ATP_CHALL | ? | 71 | 86 | -15 (window_cell) | — | pre | single |  | MIXED |
| 12:42 | ITFMATCH-26JUL06LUEVAN-LUE | ITF_M | ? | 75 | 72 | +3 (fill_est) | 15.5 | pre | single |  | GIFT_CLASS |
| 12:42 | ATPCHALLENGERMATCH-26JUL06PALKOL-P | ATP_CHALL | ? | 22 | 23 | -1 (window_cell) | -18.0 | pre | single |  | EARNED |
| 12:43 | ITFMATCH-26JUL06SLODIF-DIF | ITF_M | underdog | 38 | 42 | -4 (place_cell) | -36.0 | pre | pair | 93 | EARNED |
| 12:46 | ITFMATCH-26JUL06DONDEV-DEV | ITF_M | ? | 24 | 58 | -34 (window_cell) | 4.0 | pre | single |  | EARNED |
| 12:46 | ATPCHALLENGERMATCH-26JUL06MAGROD-R | ATP_CHALL | ? | 52 | 52 | +0 (window_cell) | 16.5 | pre | single |  | GIFT_CLASS |
| 12:47 | ITFWMATCH-26JUL06LIMDEK-DEK | ITF_W | ? | 23 | 8 | +15 (place_cell) | — | pre | single |  | MIXED |
| 12:52 | WTACHALLENGERMATCH-26JUL06COLSMI-S | WTA_CHALL | ? | 60 | 57 | +3 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 12:57 | ITFMATCH-26JUL06XUXBER-BER | ITF_M | ? | 32 | 53 | -21 (window_cell) | -45.0 | pre | single |  | EARNED |
| 13:10 | ATPCHALLENGERMATCH-26JUL06OLIDAN-D | ATP_CHALL | ? | 61 | 59 | +2 (window_cell) | 6.0 | pre | single |  | GIFT_CLASS |
| 13:18 | ATPMATCH-26JUL06FRIBUB-FRI | ATP_MAIN | ? | 64 | 64 | +0 (adopted_est) | — | 49.7 | single |  | PENDING |
| 13:34 | ITFWMATCH-26JUL06BERMEL-MEL | ITF_W | underdog | 13 | 12 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 13:36 | ITFMATCH-26JUL06MOUCAR-CAR | ITF_M | ? | 30 | 26 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 13:36 | ITFWMATCH-26JUL06LABTSY-LAB | ITF_W | ? | 1 | 1 | +0 (adopted_est) | — | pre | single |  | PENDING |
| 13:37 | ITFMATCH-26JUL06MOUCAR-MOU | ITF_M | ? | 67 | 64 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 13:42 | ATPCHALLENGERMATCH-26JUL06MONCOU-C | ATP_CHALL | ? | 32 | 30 | +2 (window_cell) | — | pre | pair | 98 | MIXED |
| 13:49 | ATPCHALLENGERMATCH-26JUL06KOZJOH-J | ATP_CHALL | ? | 33 | 32 | +1 (window_cell) | — | pre | single |  | MIXED |
| 13:49 | ATPCHALLENGERMATCH-26JUL06MONCOU-M | ATP_CHALL | ? | 66 | 66 | +0 (window_cell) | — | pre | pair | 98 | MIXED |
| 13:49 | ITFWMATCH-26JUL06VARMUN-MUN | ITF_W | ? | 12 | 8 | +4 (adopted_est) | 0.5 | pre | single |  | MIXED |
| 13:55 | ATPCHALLENGERMATCH-26JUL06PERMEL-P | ATP_CHALL | underdog | 1 | 5 | -4 (place_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 12 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 5, 'NO_FLOW': 1, 'FLOW_AT_LEVEL': 6} | repriceable now: true 2 / false 10 | **cumulative bid_grade lines: 2468 (repriceable true 232 / false 2236)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06ABOALVA- | 56 | 60m | 7/56-59/44 | 57-58 | 0 | **FLOW_AT_LEVEL** | 53 |  |
| ATPCHALLENGERMATCH-26JUL06ABOALVA- | 42 | 60m | 1/43-43/13 | 42-44 | 1 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06CLAPAP-P | 15 | 79m | 391/1-36/68794 | 1-1 | -14 | **FLOW_AT_LEVEL** | 15 |  |
| ATPCHALLENGERMATCH-26JUL06MAGROD-R | 53 | 66m | 807/30-82/54583 | 34-35 | -23 | **FLOW_AT_LEVEL** | 52 |  |
| ATPCHALLENGERMATCH-26JUL06OLIDAN-O | 36 | 48m | 252/3-46/34076 | 6-7 | -33 | **FLOW_AT_LEVEL** | 36 |  |
| ATPCHALLENGERMATCH-26JUL06SANARN-A | 53 | 84m | 1815/2-72/236614 | 5-6 | -51 | **FLOW_AT_LEVEL** | 51 |  |
| ATPCHALLENGERMATCH-26JUL06WEIGRA-G | 81 | 71m | 59/98-99/30174 | 98-99 | 17 | **FLOW_ABOVE** | 89 | flow above but bound 89c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06ZEBAND-A | 77 | 100m | 3/81-81/10 | 80-81 | 4 | **FLOW_ABOVE** | 78 | REPRICEABLE→78 |
| ITFMATCH-26JUL06CUNLIM-LIM | 18 | 99m | 0 | 22-25 | — | **NO_FLOW** | 18 |  |
| ITFMATCH-26JUL06DONDEV-DEV | 24 | 64m | 496/1-74/43949 | 32-1 | -23 | **FLOW_AT_LEVEL** | 58 |  |
| ITFWMATCH-26JUL06LABTSY-TSY | 95 | 24m | 4/99-99/31 | 99-98 | 4 | **FLOW_ABOVE** | 96 | REPRICEABLE→96 |
| ITFWMATCH-26JUL06MARBED-MAR | 79 | 10m | 28/98-99/4380 | 97-98 | 19 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06HUETEN | 29 | 1 | **30** | 97 | -67 |
| ITFMATCH-26JUL06XUXBER | 32 | 15 | **47** | 97 | -50 |
| ATPCHALLENGERMATCH-26JUL06OLIDAN | 61 | 7 | **68** | 97 | -29 |
| ATPCHALLENGERMATCH-26JUL06CLAPAP | 71 | 1 | **72** | 97 | -25 |
| ITFWMATCH-26JUL06LABTSY | 1 | 98 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06PERMEL | 1 | 99 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL06KOZJOH | 33 | 68 | **101** | 97 | +4 |
| ITFMATCH-26JUL06CUNLIM | 79 | 25 | **104** | 97 | +7 |
| ITFMATCH-26JUL06DONDEV | 24 | 80 | **104** | 97 | +7 |
| ITFWMATCH-26JUL06LIMDEK | 23 | 93 | **116** | 97 | +19 |
| ATPCHALLENGERMATCH-26JUL06MAGROD | 52 | 66 | **118** | 97 | +21 |
| ATPCHALLENGERMATCH-26JUL06PALKOL | 22 | 98 | **120** | 97 | +23 |
| WTACHALLENGERMATCH-26JUL06CURDOD | 29 | 99 | **128** | 97 | +31 |
| ATPCHALLENGERMATCH-26JUL06SANARN | 53 | 95 | **148** | 97 | +51 |

## PATTERNS (sub-B) — 30
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06DEHUD-DE {"entry_minus_fv_burst": -48.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06DEHUD-DE {"fill": 36, "age_min": 105, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06BROTHU-BRO {"fill": 38, "age_min": 105, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL06TRATEO-TRA {"fill": 18, "age_min": 105, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06KASCIN-KAS {"entry_minus_fv_burst": -8.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06KASCIN-KAS {"fill": 43, "age_min": 103, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06CURDOD-DOD {"fill": 29, "age_min": 103, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"fill": 53, "age_min": 102, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06SURMED-MED {"fill": 56, "age_min": 99, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06CUNLIM-CUN {"fill": 79, "age_min": 99, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06HUETEN-TEN {"fill": 29, "age_min": 97, "mode": "PAIRING(sib never rested)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LIMDEK-DEK {"price": 21, "ceiling": 19}
- deep_neg_fv: KXITFWMATCH-26JUL06MARBED-MAR {"entry_minus_fv_burst": -9.5}
- half_arm_aging: KXITFWMATCH-26JUL06MARBED-MAR {"fill": 79, "age_min": 93, "mode": "PAIRING(sib never rested)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LIMDEK-DEK {"price": 24, "ceiling": 19}
- half_arm_aging: KXITFWMATCH-26JUL06SINUSU-SIN {"fill": 35, "age_min": 85, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06DENQUE-QUE {"fill": 92, "age_min": 84, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06CLAPAP-CLA {"fill": 71, "age_min": 82, "mode": "QUEUE(flow at/below our level, unfilled)"}
- half_arm_aging: KXITFMATCH-26JUL06LUEVAN-LUE {"fill": 75, "age_min": 78, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06PALKOL-PAL {"entry_minus_fv_burst": -18.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06PALKOL-PAL {"fill": 22, "age_min": 78, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFMATCH-26JUL06SLODIF-DIF {"entry_minus_fv_burst": -36.0}
- half_arm_aging: KXITFMATCH-26JUL06DONDEV-DEV {"fill": 24, "age_min": 75, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06MAGROD-ROD {"fill": 52, "age_min": 74, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL06LIMDEK-DEK {"fill": 23, "age_min": 74, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06COLSMI-SMI {"fill": 60, "age_min": 68, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFMATCH-26JUL06XUXBER-BER {"entry_minus_fv_burst": -45.0}
- half_arm_aging: KXITFMATCH-26JUL06XUXBER-BER {"fill": 32, "age_min": 63, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06OLIDAN-DAN {"fill": 61, "age_min": 50, "mode": "QUEUE(flow at/below our level, unfilled)"}
- half_arm_aging: KXATPMATCH-26JUL06FRIBUB-FRI {"fill": 64, "age_min": 42, "mode": "PAIRING(sib never rested)"}

## ERRORS — 2 handler errors this session (SEE ZERO-TOLERANCE)
