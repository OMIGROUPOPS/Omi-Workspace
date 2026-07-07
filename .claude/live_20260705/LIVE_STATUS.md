# LIVE VALIDATION — rolling status

- cycle 40 @ **2026-07-06 10:01:35 PM ET** | build `4fb15c6` | session boot 07-06 15:26 ET | log `live_v3_20260706.jsonl` | 36656 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 27 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:26 | ATPCHALLENGERMATCH-26JUL06MONCOU-C | ATP_CHALL | ? | 32 | 29 | +3 (adopted_est) | 1.0 | pre | pair | 97 | MIXED |
| 15:26 | ATPCHALLENGERMATCH-26JUL06SANARN-A | ATP_CHALL | ? | 53 | 50 | +3 (adopted_est) | -33.5 | pre | single |  | EARNED |
| 15:26 | ATPCHALLENGERMATCH-26JUL06MONCOU-M | ATP_CHALL | ? | 65 | 62 | +3 (fill_est) | -2.5 | pre | pair | 97 | MIXED |
| 15:31 | ATPCHALLENGERMATCH-26JUL06KOZJOH-K | ATP_CHALL | ? | 66 | 63 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 15:37 | ITFMATCH-26JUL06GARPER-PER | ITF_M | ? | 27 | 23 | +4 (adopted_est) | 10.5 | pre | single |  | GIFT_CLASS |
| 15:46 | ATPCHALLENGERMATCH-26JUL06GLIYUN-G | ATP_CHALL | ? | 16 | 13 | +3 (window_cell) | — | pre | single |  | MIXED |
| 15:51 | ITFWMATCH-26JUL06JULOLI-JUL | ITF_W | underdog | 16 | 8 | +8 (place_cell) | -31.5 | pre | single |  | EARNED |
| 15:55 | ATPCHALLENGERMATCH-26JUL06GOMRIB-R | ATP_CHALL | ? | 80 | 90 | -10 (window_cell) | -7.0 | pre | single |  | EARNED |
| 16:03 | ATPMATCH-26JUL06LEHZVE-LEH | ATP_MAIN | ? | 24 | 22 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 16:32 | ATPCHALLENGERMATCH-26JUL06RODLIN-R | ATP_CHALL | ? | 87 | 85 | +2 (window_cell) | 15.5 | pre | pair | 99 | GIFT_CLASS |
| 16:34 | ATPCHALLENGERMATCH-26JUL06RODLIN-L | ATP_CHALL | ? | 12 | 10 | +2 (window_cell) | -15.5 | pre | pair | 99 | EARNED |
| 17:10 | ATPCHALLENGERMATCH-26JUL06ABOALVA- | ATP_CHALL | ? | 55 | 56 | -1 (window_cell) | -2.0 | pre | single |  | MIXED |
| 17:48 | ATPCHALLENGERMATCH-26JUL06VARFER-V | ATP_CHALL | ? | 74 | 73 | +1 (window_cell) | 0.0 | pre | single |  | GIFT_CLASS |
| 19:05 | ITFMATCH-26JUL06TAGSUZ-SUZ | ITF_M | underdog | 20 | 17 | +3 (place_cell) | — | pre | pair | 85 | PENDING |
| 20:07 | ITFMATCH-26JUL06TANKAW-KAW | ITF_M | underdog | 17 | 5 | +12 (place_cell) | — | pre | single |  | PENDING |
| 20:39 | ITFMATCH-26JUL06PHATOM-TOM | ITF_M | leader | 75 | 77 | -2 (place_cell) | — | pre | single |  | PENDING |
| 20:44 | ITFMATCH-26JUL06OCHMUT-MUT | ITF_M | underdog | 24 | 22 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 20:52 | ITFMATCH-26JUL06KIMSHI-SHI | ITF_M | underdog | 19 | 17 | +2 (place_cell) | — | pre | single |  | PENDING |
| 20:57 | ITFMATCH-26JUL06TAGSUZ-TAG | ITF_M | leader | 65 | 49 | +16 (place_cell) | — | pre | pair | 85 | PENDING |
| 21:02 | ITFWMATCH-26JUL06CHOPHA-CHO | ITF_W | ? | 79 | 77 | +2 (place_cell) | — | pre | single |  | PENDING |
| 21:03 | ITFMATCH-26JUL06BORHAR-HAR | ITF_M | underdog | 42 | 38 | +4 (place_cell) | — | pre | single |  | PENDING |
| 21:15 | ITFMATCH-26JUL06OCHMUT-OCH | ITF_M | leader | 73 | 71 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 21:31 | ITFMATCH-26JUL06MATKOM-KOM | ITF_M | underdog | 7 | 2 | +5 (place_cell) | — | pre | single |  | PENDING |
| 21:49 | ATPCHALLENGERMATCH-26JUL06HOLSCH-H | ATP_CHALL | ? | 47 | 44 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 21:53 | ITFWMATCH-26JUL06OHWLIU-OHW | ITF_W | leader | 74 | 70 | +4 (place_cell) | — | pre | single |  | PENDING |
| 21:56 | ITFWMATCH-26JUL06LIXSUN-LIX | ITF_W | underdog | 34 | 40 | -6 (place_cell) | — | pre | single |  | PENDING |
| 22:00 | ITFWMATCH-26JUL06KOSOUN-KOS | ITF_W | underdog | 40 | 32 | +8 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 70 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 24, 'NO_FLOW': 44, 'FLOW_AT_LEVEL': 2} | repriceable now: true 11 / false 59 | **cumulative bid_grade lines: 2727 (repriceable true 263 / false 2464)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06HOLSCH-S | 50 | 1m | 0 | 54-56 | — | **NO_FLOW** | 50 |  |
| ATPCHALLENGERMATCH-26JUL06VUKBRO-B | 49 | 395m | 4/50-51/77 | 49-50 | 1 | **FLOW_ABOVE** | 48 | flow above but bound 48c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BORHAR-BOR | 55 | 58m | 10/61-75/87 | 57-58 | 6 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06CHEJIN-JIN | 43 | 17m | 0 | 43-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06FUKTAK-FUK | 41 | 77m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06FUKTAK-TAK | 56 | 121m | 1/60-60/1 | 56-59 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFMATCH-26JUL06HANKUN-HAN | 19 | 24m | 0 | 19-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HANKUN-KUN | 21 | 24m | 0 | 21-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HAZSHI-HAZ | 32 | 29m | 0 | 32-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HAZSHI-SHI | 67 | 151m | 4/70-70/58 | 67-70 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| ITFMATCH-26JUL06KIMSHI-KIM | 78 | 69m | 20/82-94/172 | 87-81 | 4 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06MATKOM-MAT | 90 | 30m | 1/95-95/1 | 91-94 | 5 | **FLOW_ABOVE** | 90 | flow above but bound 90c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06NAKIDO-IDO | 16 | 168m | 1/22-22/4 | 16-18 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06OCHMUT-MUT | 22 | 39m | 38/20-34/605 | 27-26 | -2 | **FLOW_AT_LEVEL** | 24 |  |
| ITFMATCH-26JUL06OKITAN-OKI | 64 | 134m | 12/67-68/221 | 67-65 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFMATCH-26JUL06OKITAN-TAN | 33 | 151m | 5/36-37/20 | 33-36 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFMATCH-26JUL06PHATOM-PHA | 21 | 64m | 3/28-29/3 | 26-24 | 7 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06SAKLIX-SAK | 56 | 71m | 2/66-67/3 | 56-64 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06TAGSUZ-SUZ | 19 | 23m | 76/20-27/5405 | 35-20 | 1 | **FLOW_ABOVE** | 32 | REPRICEABLE→20 |
| ITFMATCH-26JUL06TANKAW-TAN | 80 | 134m | 11/84-90/66 | 81-81 | 4 | **FLOW_ABOVE** | 80 | flow above but bound 80c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06TANVIS-TAN | 32 | 4m | 0 | 32-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TANVIS-VIS | 61 | 25m | 2/68-68/7 | 61-66 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06VANBOO-BOO | 62 | 173m | 4/66-66/11 | 62-66 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFMATCH-26JUL06VANBOO-VAN | 38 | 20m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ZHAISH-ISH | 22 | 92m | 0 | 22-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ZHAISH-ZHA | 65 | 60m | 1/77-77/1 | 65-78 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL07BOUMOC-BOU | 67 | 61m | 4/67-68/11 | 67-68 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL07BOUMOC-MOC | 30 | 59m | 4/32-32/550 | 30-31 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→32 |
| ITFMATCH-26JUL07CHOCHE-CHE | 34 | 41m | 0 | 34-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07CHOCHE-CHO | 64 | 48m | 0 | 64-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07KOIKAW-KAW | 58 | 76m | 0 | 58-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07KOIKAW-KOI | 40 | 77m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07OGUJAS-JAS | 72 | 26m | 0 | 72-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07OGUJAS-OGU | 25 | 61m | 1/28-28/0 | 25-27 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→28 |
| ITFWMATCH-26JUL06CAIOHX-CAI | 23 | 86m | 2/26-27/3 | 23-26 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFWMATCH-26JUL06CAIOHX-OHX | 69 | 86m | 2/76-77/3 | 76-70 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06CHOLIX-CHO | 43 | 0m | 0 | 47-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CHOLIX-LIX | 30 | 0m | 0 | 30-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CHOPHA-PHA | 16 | 0m | 0 | 20-21 | — | **NO_FLOW** | 18 |  |
| ITFWMATCH-26JUL06GAONON-GAO | 19 | 58m | 2/27-28/3 | 19-27 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06GAONON-NON | 73 | 59m | 1/82-82/23 | 73-81 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06KOSOUN-OUN | 56 | 214m | 37/60-67/515 | 61-57 | 4 | **FLOW_ABOVE** | 57 | REPRICEABLE→57 |
| ITFWMATCH-26JUL06LIXSUN-SUN | 59 | 2m | 0 | 61-67 | — | **NO_FLOW** | 63 |  |
| ITFWMATCH-26JUL06OHWLIU-LIU | 23 | 2m | 0 | 24-26 | — | **NO_FLOW** | 23 |  |
| ITFWMATCH-26JUL06TIAZHO-ZHO | 45 | 57m | 0 | 45-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07BATBEL-BAT | 8 | 69m | 0 | 8-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07BATBEL-BEL | 8 | 68m | 0 | 8-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07BEHBAR-BAR | 20 | 2m | 0 | 21-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07BEHBAR-BEH | 16 | 3m | 0 | 16-77 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07GOLALH-ALH | 51 | 1m | 0 | 52-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07GOLALH-GOL | 44 | 1m | 0 | 44-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07HERBAL-BAL | 17 | 1m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07HERBAL-HER | 78 | 1m | 0 | 78-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07KHOSAM-SAM | 8 | 8m | 0 | 8-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07KHRBEL-BEL | 10 | 13m | 0 | 49-67 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07KHRBEL-KHR | 19 | 1m | 0 | 20-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07LANDEN-DEN | 60 | 1m | 0 | 60-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07LANDEN-LAN | 35 | 1m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07MCKGUD-GUD | 2 | 1m | 0 | 6-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07MCKGUD-MCK | 6 | 1m | 0 | 64-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07PANZHO-PAN | 69 | 17m | 0 | 69-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07PANZHO-ZHO | 25 | 11m | 0 | 25-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07PUSMAY-PUS | 2 | 1m | 0 | 7-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07SENKEN-KEN | 27 | 2m | 0 | 58-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07SENKEN-SEN | 17 | 17m | 3/21-22/20 | 17-18 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFWMATCH-26JUL07SUSKOR-KOR | 14 | 13m | 0 | 44-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07SUSKOR-SUS | 44 | 13m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07YARHAY-YAR | 11 | 1m | 0 | 12-23 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06COLSMI-C | 35 | 1m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06LINMAR-M | 90 | 1m | 0 | 93-96 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06JULOLI | 16 | 33 | **49** | 97 | -48 |
| ATPCHALLENGERMATCH-26JUL06VARFER | 74 | 1 | **75** | 97 | -22 |
| ATPCHALLENGERMATCH-26JUL06GOMRIB | 80 | 1 | **81** | 97 | -16 |
| ATPCHALLENGERMATCH-26JUL06ABOALVA | 55 | 27 | **82** | 97 | -15 |
| ITFWMATCH-26JUL06KOSOUN | 40 | 57 | **97** | 97 | +0 |
| ITFMATCH-26JUL06TANKAW | 17 | 81 | **98** | 97 | +1 |
| ITFMATCH-26JUL06PHATOM | 75 | 24 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06GLIYUN | 16 | 84 | **100** | 97 | +3 |
| ITFMATCH-26JUL06KIMSHI | 19 | 81 | **100** | 97 | +3 |
| ITFWMATCH-26JUL06CHOPHA | 79 | 21 | **100** | 97 | +3 |
| ITFMATCH-26JUL06BORHAR | 42 | 58 | **100** | 97 | +3 |
| ITFWMATCH-26JUL06OHWLIU | 74 | 26 | **100** | 97 | +3 |
| ITFMATCH-26JUL06MATKOM | 7 | 94 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06LIXSUN | 34 | 67 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL06HOLSCH | 47 | 56 | **103** | 97 | +6 |

## PATTERNS (sub-B) — 18
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"entry_minus_fv_burst": -33.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"fill": 53, "age_min": 395, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06KOZJOH-KOZ {"fill": 66, "age_min": 390, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06GARPER-PER {"fill": 27, "age_min": 384, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GLIYUN-GLI {"fill": 16, "age_min": 375, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFWMATCH-26JUL06JULOLI-JUL {"entry_minus_fv_burst": -31.5}
- half_arm_aging: KXITFWMATCH-26JUL06JULOLI-JUL {"fill": 16, "age_min": 370, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GOMRIB-RIB {"fill": 80, "age_min": 366, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPMATCH-26JUL06LEHZVE-LEH {"fill": 24, "age_min": 358, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06RODLIN-LIN {"entry_minus_fv_burst": -15.5}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL06RODLIN {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06ABOALVA-ABO {"fill": 55, "age_min": 291, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VARFER-VAR {"fill": 74, "age_min": 253, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06TANKAW-KAW {"fill": 17, "age_min": 114, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFMATCH-26JUL06PHATOM-TOM {"fill": 75, "age_min": 82, "mode": "SET_BELOW_FLOW(prints 7c above)"}
- half_arm_aging: KXITFMATCH-26JUL06KIMSHI-SHI {"fill": 19, "age_min": 69, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06CHOPHA-CHO {"fill": 79, "age_min": 59, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFMATCH-26JUL06BORHAR-HAR {"fill": 42, "age_min": 58, "mode": "SET_BELOW_FLOW(prints 6c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
