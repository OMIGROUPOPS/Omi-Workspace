# LIVE VALIDATION — rolling status

- cycle 132 @ **2026-07-07 01:59:17 PM ET** | build `dd4e5b3` | session boot 07-07 13:13 ET | log `live_v3_20260707.jsonl` | 19070 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 27 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 13:13 | ITFWMATCH-26JUL07MIKPAQ-PAQ | ITF_W | ? | 70 | 68 | +2 (adopted_est) | — | pre | pair | 96 | PENDING |
| 13:13 | ITFMATCH-26JUL07RICMAR-RIC | ITF_M | ? | 53 | 50 | +3 (adopted_est) | — | pre | pair | 98 | PENDING |
| 13:13 | ITFMATCH-26JUL07RICMAR-MAR | ITF_M | ? | 45 | 41 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
| 13:13 | ITFWMATCH-26JUL07EVAGOW-GOW | ITF_W | ? | 14 | 30 | -16 (window_cell) | -8.5 | pre | single |  | EARNED |
| 13:13 | ITFWMATCH-26JUL07GIADIA-GIA | ITF_W | ? | 34 | 30 | +4 (adopted_est) | -60.0 | pre | single |  | EARNED |
| 13:13 | ITFWMATCH-26JUL07MAROLU-OLU | ITF_W | ? | 30 | 26 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 13:13 | ATPCHALLENGERMATCH-26JUL07CLAHER-C | ATP_CHALL | ? | 44 | 41 | +3 (adopted_est) | -18.5 | pre | single |  | EARNED |
| 13:14 | ITFWMATCH-26JUL07SCHZID-SCH | ITF_W | ? | 27 | 7 | +20 (window_cell) | — | pre | single |  | MIXED |
| 13:16 | ITFWMATCH-26JUL07MIKPAQ-MIK | ITF_W | ? | 26 | 22 | +4 (fill_est) | — | pre | pair | 96 | PENDING |
| 13:16 | ITFWMATCH-26JUL07MOROLM-OLM | ITF_W | ? | 54 | 52 | +2 (fill_est) | — | pre | single |  | PENDING |
| 13:18 | ATPCHALLENGERMATCH-26JUL07MOESAN-S | ATP_CHALL | ? | 26 | 23 | +3 (fill_est) | -15.5 | 0.9 | single |  | EARNED |
| 13:18 | ATPCHALLENGERMATCH-26JUL07ONCCAM-C | ATP_CHALL | ? | 20 | 35 | -15 (window_cell) | -37.0 | pre | single |  | EARNED |
| 13:18 | ITFWMATCH-26JUL07FERMED-MED | ITF_W | ? | 86 | 84 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 13:18 | ITFWMATCH-26JUL07SCHCAN-CAN | ITF_W | ? | 84 | 82 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 13:22 | ATPCHALLENGERMATCH-26JUL07SKAPET-P | ATP_CHALL | ? | 36 | 33 | +3 (fill_est) | -12.0 | 3.9 | single |  | EARNED |
| 13:22 | ATPCHALLENGERMATCH-26JUL06MCDWAL-M | ATP_CHALL | ? | 47 | 44 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 13:24 | ATPCHALLENGERMATCH-26JUL07JANGIL-J | ATP_CHALL | ? | 18 | 15 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 13:25 | ITFMATCH-26JUL07KAMMIY-KAM | ITF_M | ? | 5 | 1 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 13:26 | ITFWMATCH-26JUL07AKLRAP-RAP | ITF_W | ? | 44 | 40 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 13:29 | ITFWMATCH-26JUL07ELJRAB-ELJ | ITF_W | ? | 57 | 78 | -21 (window_cell) | — | pre | single |  | MIXED |
| 13:35 | ITFMATCH-26JUL07PUTVAS-VAS | ITF_M | ? | 93 | 90 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 13:40 | ATPCHALLENGERMATCH-26JUL07POPPDA-P | ATP_CHALL | ? | 39 | 36 | +3 (window_cell) | — | pre | single |  | MIXED |
| 13:46 | ITFWMATCH-26JUL07KAYDUN-KAY | ITF_W | underdog | 60 | 22 | +38 (place_cell) | — | pre | pair | 102 | PENDING |
| 13:47 | ITFWMATCH-26JUL07KAYDUN-DUN | ITF_W | ? | 42 | 38 | +4 (adopted_est) | — | pre | pair | 102 | PENDING |
| 13:53 | ITFWMATCH-26JUL07NGUGJI-NGU | ITF_W | ? | 75 | 73 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 13:56 | ITFMATCH-26JUL07BOBARO-ARO | ITF_M | ? | 34 | 30 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 13:58 | ATPCHALLENGERMATCH-26JUL06ILARYB-I | ATP_CHALL | ? | 52 | 49 | +3 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 14 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 6, 'FLOW_AT_LEVEL': 2} | repriceable now: true 2 / false 12 | **cumulative bid_grade lines: 4910 (repriceable true 423 / false 4487)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07DROERH-E | 23 | 26m | 177/7-32/18261 | 13-14 | -16 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07HERHAR-H | 15 | 35m | 331/11-40/34098 | 11-12 | -4 | **FLOW_AT_LEVEL** | 15 |  |
| ATPCHALLENGERMATCH-26JUL07JANGIL-J | 18 | 2m | 13/20-24/406 | 24-25 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ATPCHALLENGERMATCH-26JUL07MENAVE-A | 35 | 9m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07MENAVE-M | 61 | 30m | 2/62-62/36 | 61-62 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→62 |
| ATPCHALLENGERMATCH-26JUL07PACMEL-M | 48 | 45m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07PACMEL-P | 51 | 45m | 1/52-52/37 | 51-52 | 1 | **FLOW_ABOVE** | 49 | flow above but bound 49c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07ROYNEU-R | 89 | 34m | 78/96-99/20669 | 95-96 | 7 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07BOBARO-BOB | 63 | 3m | 5/73-77/110 | 75-76 | 10 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07DAYDEA-DAY | 56 | 31m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07KAYDUN-DUN | 37 | 2m | 0 | 56-58 | — | **NO_FLOW** | 37 |  |
| ITFWMATCH-26JUL07KELXUX-KEL | 33 | 33m | 0 | 33-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07KELXUX-XUX | 62 | 5m | 0 | 62-66 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07SCHCAN-SCH | 13 | 38m | 3/16-26/22 | 13-16 | 3 | **FLOW_ABOVE** | 13 | flow above but bound 13c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07ONCCAM | 20 | 75 | **95** | 97 | -2 |
| ITFWMATCH-26JUL07SCHCAN | 84 | 16 | **100** | 97 | +3 |
| ITFWMATCH-26JUL07EVAGOW | 14 | 91 | **105** | 97 | +8 |
| ATPCHALLENGERMATCH-26JUL07POPPDA | 39 | 71 | **110** | 97 | +13 |
| ITFMATCH-26JUL07BOBARO | 34 | 76 | **110** | 97 | +13 |
| ITFWMATCH-26JUL07SCHZID | 27 | 98 | **125** | 97 | +28 |
| ITFWMATCH-26JUL07ELJRAB | 57 | 91 | **148** | 97 | +51 |

## PATTERNS (sub-B) — 24
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07RICMAR {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- deep_neg_fv: KXITFWMATCH-26JUL07EVAGOW-GOW {"entry_minus_fv_burst": -8.5}
- half_arm_aging: KXITFWMATCH-26JUL07EVAGOW-GOW {"fill": 14, "age_min": 46, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFWMATCH-26JUL07GIADIA-GIA {"entry_minus_fv_burst": -60.0}
- half_arm_aging: KXITFWMATCH-26JUL07GIADIA-GIA {"fill": 34, "age_min": 46, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07MAROLU-OLU {"fill": 30, "age_min": 46, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07CLAHER-CLA {"entry_minus_fv_burst": -18.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07CLAHER-CLA {"fill": 44, "age_min": 46, "mode": "PAIRING(sib never rested)"}
- pre_conception_buy: KXITFWMATCH-26JUL07SCHZID-SCH {"price": 27, "conception_ts": 1783445411.2336688, "detail": "buy 27c predates the conception stamp by 17min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL07SCHZID-SCH {"fill": 27, "age_min": 44, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07MOROLM-OLM {"fill": 54, "age_min": 42, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07MOESAN-SAN {"entry_minus_fv_burst": -15.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07MOESAN-SAN {"fill": 26, "age_min": 41, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07ONCCAM-CAM {"entry_minus_fv_burst": -37.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07ONCCAM-CAM {"fill": 20, "age_min": 41, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07FERMED-MED {"fill": 86, "age_min": 41, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL07SCHCAN-CAN {"fill": 84, "age_min": 41, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07SKAPET-PET {"entry_minus_fv_burst": -12.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07SKAPET-PET {"fill": 36, "age_min": 37, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06MCDWAL-MCD {"fill": 47, "age_min": 37, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-07 01:59:17 PM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07JANGIL-JAN {"fill": 18, "age_min": 35, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07KAMMIY-KAM {"fill": 5, "age_min": 34, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-07 01:59:17 PM ET"}
- half_arm_aging: KXITFWMATCH-26JUL07AKLRAP-RAP {"fill": 44, "age_min": 33, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-07 01:59:17 PM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFWMATCH-26JUL07KAYDUN {"combined": 102, "detail": "pair combined 102c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
