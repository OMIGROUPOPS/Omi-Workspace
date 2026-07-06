# LIVE VALIDATION — rolling status

- cycle 152 @ **2026-07-06 12:49:45 PM ET** | build `ec129a7` | session boot 07-06 12:15 ET | log `live_v3_20260706.jsonl` | 5396 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 12:26:21 | **handler_error** | on_bbo_update_error | [Errno 28] No space left on device |
| 12:26:21 | **handler_error** | error | [Errno 28] No space left on device |

## FILLS — 25 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 12:15 | ITFMATCH-26JUL06IAMBEN-IAM | ITF_M | ? | 66 | 64 | +2 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 12:15 | ATPCHALLENGERMATCH-26JUL06DEHUD-DE | ATP_CHALL | ? | 36 | 33 | +3 (adopted_est) | -48.5 | pre | single |  | EARNED |
| 12:15 | ITFMATCH-26JUL06BROTHU-BRO | ITF_M | ? | 38 | 34 | +4 (adopted_est) | 25.0 | pre | single |  | GIFT_CLASS |
| 12:15 | ITFWMATCH-26JUL06TRATEO-TRA | ITF_W | ? | 18 | 14 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:16 | ITFMATCH-26JUL06IAMBEN-BEN | ITF_M | ? | 31 | 30 | +1 (window_cell) | — | pre | pair | 97 | EARNED |
| 12:17 | ATPCHALLENGERMATCH-26JUL06KASCIN-K | ATP_CHALL | ? | 43 | 40 | +3 (fill_est) | -8.5 | pre | single |  | EARNED |
| 12:18 | WTACHALLENGERMATCH-26JUL06CURDOD-D | WTA_CHALL | ? | 29 | 32 | -3 (window_cell) | — | pre | single |  | EARNED |
| 12:18 | ATPCHALLENGERMATCH-26JUL06SANARN-A | ATP_CHALL | ? | 53 | 51 | +2 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 12:18 | ITFWMATCH-26JUL06POHSTU-POH | ITF_W | ? | 28 | 24 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 12:21 | ITFMATCH-26JUL06SLODIF-SLO | ITF_M | ? | 55 | 52 | +3 (adopted_est) | — | pre | pair | 93 | PENDING |
| 12:22 | ITFMATCH-26JUL06SURMED-MED | ITF_M | ? | 56 | 53 | +3 (adopted_est) | -7.0 | pre | single |  | EARNED |
| 12:22 | ITFMATCH-26JUL06CUNLIM-CUN | ITF_M | ? | 79 | 76 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 12:23 | ATPCHALLENGERMATCH-26JUL06HUETEN-T | ATP_CHALL | ? | 29 | 53 | -24 (window_cell) | — | pre | single |  | EARNED |
| 12:27 | ITFWMATCH-26JUL06MARBED-MAR | ITF_W | ? | 79 | 77 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 12:34 | ITFWMATCH-26JUL06BERMEL-BER | ITF_W | leader | 84 | 75 | +9 (place_cell) | — | pre | single |  | PENDING |
| 12:35 | ITFWMATCH-26JUL06SINUSU-SIN | ITF_W | ? | 35 | 31 | +4 (fill_est) | -1.0 | pre | single |  | MIXED |
| 12:35 | ITFWMATCH-26JUL06POHSTU-STU | ITF_W | ? | 69 | 67 | +2 (fill_est) | — | pre | pair | 97 | PENDING |
| 12:36 | WTACHALLENGERMATCH-26JUL06DENQUE-Q | WTA_CHALL | ? | 92 | 89 | +3 (adopted_est) | -5.5 | pre | single |  | EARNED |
| 12:39 | ATPCHALLENGERMATCH-26JUL06CLAPAP-C | ATP_CHALL | ? | 71 | 86 | -15 (window_cell) | — | pre | single |  | MIXED |
| 12:42 | ITFMATCH-26JUL06LUEVAN-LUE | ITF_M | ? | 75 | 72 | +3 (fill_est) | 15.5 | pre | single |  | GIFT_CLASS |
| 12:42 | ATPCHALLENGERMATCH-26JUL06PALKOL-P | ATP_CHALL | ? | 22 | 23 | -1 (window_cell) | — | pre | single |  | EARNED |
| 12:43 | ITFMATCH-26JUL06SLODIF-DIF | ITF_M | underdog | 38 | 42 | -4 (place_cell) | — | pre | pair | 93 | PENDING |
| 12:46 | ITFMATCH-26JUL06DONDEV-DEV | ITF_M | ? | 24 | 20 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:46 | ATPCHALLENGERMATCH-26JUL06MAGROD-R | ATP_CHALL | ? | 52 | 52 | +0 (window_cell) | — | pre | single |  | MIXED |
| 12:47 | ITFWMATCH-26JUL06LIMDEK-DEK | ITF_W | ? | 23 | 8 | +15 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 6 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 4, 'NO_FLOW': 1, 'FLOW_AT_LEVEL': 1} | repriceable now: true 1 / false 5 | **cumulative bid_grade lines: 2453 (repriceable true 230 / false 2223)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06CLAPAP-P | 15 | 9m | 92/26-36/11225 | 30-28 | 11 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06SANARN-A | 53 | 13m | 103/47-70/6498 | 52-51 | -6 | **FLOW_AT_LEVEL** | 51 |  |
| ATPCHALLENGERMATCH-26JUL06WEIGRA-G | 81 | 0m | 1/98-98/400 | 97-98 | 17 | **FLOW_ABOVE** | 89 | flow above but bound 89c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06ZEBAND-A | 77 | 29m | 2/81-81/9 | 80-81 | 4 | **FLOW_ABOVE** | 78 | REPRICEABLE→78 |
| ITFMATCH-26JUL06CUNLIM-LIM | 18 | 28m | 0 | 22-24 | — | **NO_FLOW** | 18 |  |
| ITFWMATCH-26JUL06BERMEL-MEL | 13 | 8m | 31/31-66/1963 | 64-66 | 18 | **FLOW_ABOVE** | 13 | flow above but bound 13c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06MAGROD | 52 | 40 | **92** | 97 | -5 |
| ATPCHALLENGERMATCH-26JUL06CLAPAP | 71 | 28 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06SANARN | 53 | 47 | **100** | 97 | +3 |
| ITFMATCH-26JUL06CUNLIM | 79 | 24 | **103** | 97 | +6 |
| ATPCHALLENGERMATCH-26JUL06PALKOL | 22 | 87 | **109** | 97 | +12 |
| ATPCHALLENGERMATCH-26JUL06HUETEN | 29 | 88 | **117** | 97 | +20 |
| WTACHALLENGERMATCH-26JUL06CURDOD | 29 | 91 | **120** | 97 | +23 |
| ITFWMATCH-26JUL06BERMEL | 84 | 66 | **150** | 97 | +53 |

## PATTERNS (sub-B) — 8
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06DEHUD-DE {"entry_minus_fv_burst": -48.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06DEHUD-DE {"fill": 36, "age_min": 34, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-06 12:49:45 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL06BROTHU-BRO {"fill": 38, "age_min": 34, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-06 12:49:45 PM ET"}
- half_arm_aging: KXITFWMATCH-26JUL06TRATEO-TRA {"fill": 18, "age_min": 34, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-06 12:49:45 PM ET"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06KASCIN-KAS {"entry_minus_fv_burst": -8.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06KASCIN-KAS {"fill": 43, "age_min": 33, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-06 12:49:45 PM ET"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06CURDOD-DOD {"fill": 29, "age_min": 32, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-06 12:49:45 PM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"fill": 53, "age_min": 32, "mode": "PAIRING(sib never rested)"}

## ERRORS — 2 handler errors this session (SEE ZERO-TOLERANCE)
