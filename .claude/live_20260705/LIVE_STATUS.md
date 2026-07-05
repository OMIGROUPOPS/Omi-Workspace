# LIVE VALIDATION — rolling status

- cycle 82 @ **2026-07-05 10:57:09 AM ET** | build `bf3a9c2` | session boot 07-05 10:39 ET | log `live_v3_20260705.jsonl` | 3091 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 10:48:45 | **grace_breach** | KXITFMATCH-26JUL05SALCON-CON | fill 13c 5.2min past latch (grace 300s) |

## FILLS — 14 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10:39 | ITFWMATCH-26JUL05TRAABB-ABB | ITF_W | ? | 64 | 64 | +0 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 10:39 | ATPCHALLENGERMATCH-26JUL05RAMNEU-R | ATP_CHALL | ? | 36 | 2 | +34 (window_cell) | — | pre | single |  | MIXED |
| 10:39 | ATPCHALLENGERMATCH-26JUL05WEHIFI-I | ATP_CHALL | ? | 11 | 8 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 10:39 | WTACHALLENGERMATCH-26JUL05DITLEW-D | WTA_CHALL | ? | 31 | 28 | +3 (adopted_est) | 25.5 | pre | single |  | GIFT_CLASS |
| 10:39 | ATPCHALLENGERMATCH-26JUL05KUZMAT-M | ATP_CHALL | ? | 5 | 2 | +3 (adopted_est) | -2.5 | pre | single |  | MIXED |
| 10:40 | ITFWMATCH-26JUL05AITDAE-AIT | ITF_W | underdog | 8 | 4 | +4 (place_cell) | — | pre | single |  | MIXED |
| 10:41 | ATPCHALLENGERMATCH-26JUL05VALREJ-V | ATP_CHALL | leader | 62 | 71 | -9 (place_cell) | 11.5 | pre | single |  | GIFT_CLASS |
| 10:41 | ATPCHALLENGERMATCH-26JUL05CIZCAZ-C | ATP_CHALL | underdog | 23 | 19 | +4 (place_cell) | — | pre | single |  | MIXED |
| 10:41 | ITFMATCH-26JUL05GELBRE-GEL | ITF_M | ? | 44 | 40 | +4 (window_cell) | — | pre | pair | 92 | MIXED |
| 10:42 | WTAMATCH-26JUL05BENGAU-GAU | WTA_MAIN | ? | 50 | 50 | +0 (adopted_est) | — | pre | single |  | PENDING |
| 10:48 | ITFMATCH-26JUL05SALCON-CON | ITF_M | ? | 13 | 29 | -16 (window_cell) | -10.0 | 5.2 | single |  | EARNED |
| 10:53 | ITFMATCH-26JUL05GELBRE-BRE | ITF_M | ? | 48 | 56 | -8 (window_cell) | — | pre | pair | 92 | EARNED |
| 10:53 | ATPCHALLENGERMATCH-26JUL05PEROPI-O | ATP_CHALL | ? | 25 | 22 | +3 (window_cell) | — | pre | single |  | MIXED |
| 10:55 | ATPCHALLENGERMATCH-26JUL05INGFEL-F | ATP_CHALL | ? | 72 | 72 | +0 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 15 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 7, 'NO_FLOW': 8} | repriceable now: true 1 / false 14 | **cumulative bid_grade lines: 651 (repriceable true 58 / false 593)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BANMAR-B | 65 | 17m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BANMAR-M | 33 | 17m | 2/36-36/132 | 33-36 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-E | 65 | 17m | 0 | 65-67 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-J | 33 | 17m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GANZIN-G | 28 | 17m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GANZIN-Z | 70 | 17m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05POTANG-P | 50 | 17m | 2/55-55/4 | 53-56 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05RAMNEU-N | 61 | 17m | 17/98-99/2359 | 99-98 | 37 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05STEDIN-S | 26 | 17m | 87/43-63/5140 | 62-44 | 17 | **FLOW_ABOVE** | 55 |  |
| ITFMATCH-26JUL05GELBRE-GEL | 46 | 4m | 4/52-62/116 | 46-47 | 6 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05SABMIS-SAB | 1 | 17m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL05TRAABB-TRA | 33 | 4m | 109/44-49/9976 | 53-36 | 11 | **FLOW_ABOVE** | 29 | flow above but bound 29c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05TUBSOB-SOB | 25 | 17m | 66/29-41/1475 | 36-31 | 4 | **FLOW_ABOVE** | 30 | REPRICEABLE→29 |
| WTACHALLENGERMATCH-26JUL05YAMOVC-O | 28 | 17m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05YAMOVC-Y | 70 | 17m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL05SALCON | 13 | 78 | **91** | 97 | -6 |
| ITFWMATCH-26JUL05TRAABB | 64 | 36 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05VALREJ | 62 | 38 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05PEROPI | 25 | 75 | **100** | 97 | +3 |
| ITFWMATCH-26JUL05AITDAE | 8 | 93 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05CIZCAZ | 23 | 82 | **105** | 97 | +8 |
| ATPCHALLENGERMATCH-26JUL05RAMNEU | 36 | 98 | **134** | 97 | +37 |

## PATTERNS (sub-B) — 1
- deep_neg_fv: KXITFMATCH-26JUL05SALCON-CON {"entry_minus_fv_burst": -10.0, "emitted_et": "2026-07-05 10:57:08 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
