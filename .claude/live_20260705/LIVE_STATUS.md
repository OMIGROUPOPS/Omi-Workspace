# LIVE VALIDATION — rolling status

- cycle 36 @ **2026-07-06 09:20:24 PM ET** | build `dc461ec` | session boot 07-06 15:26 ET | log `live_v3_20260706.jsonl` | 32867 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 22 graded (session)
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

## RESTING BIDS — 49 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 22, 'NO_FLOW': 26, 'FLOW_AT_LEVEL': 1} | repriceable now: true 10 / false 39 | **cumulative bid_grade lines: 2650 (repriceable true 259 / false 2391)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06VUKBRO-B | 49 | 354m | 4/50-51/77 | 49-50 | 1 | **FLOW_ABOVE** | 48 | flow above but bound 48c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BORHAR-BOR | 55 | 17m | 3/73-75/15 | 58-58 | 18 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06CHEJIN-JIN | 39 | 185m | 6/49-52/35 | 39-51 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06FUKTAK-FUK | 41 | 36m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06FUKTAK-TAK | 56 | 80m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HANKUN-HAN | 18 | 9m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HANKUN-KUN | 20 | 21m | 0 | 20-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HAZSHI-HAZ | 30 | 59m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HAZSHI-SHI | 67 | 110m | 2/70-70/56 | 67-70 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| ITFMATCH-26JUL06KIMSHI-KIM | 78 | 28m | 11/87-93/128 | 87-81 | 9 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06MATKOM-KOM | 7 | 98m | 33/10-13/1739 | 10-8 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL06MATKOM-MAT | 91 | 120m | 2/94-95/32 | 91-94 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→94 |
| ITFMATCH-26JUL06NAKIDO-IDO | 16 | 127m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06OCHMUT-MUT | 23 | 1m | 1/34-34/14 | 27-26 | 11 | **FLOW_ABOVE** | 24 | flow above but bound 24c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06OKITAN-OKI | 64 | 93m | 11/67-68/220 | 67-65 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFMATCH-26JUL06OKITAN-TAN | 33 | 109m | 3/36-37/6 | 33-36 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFMATCH-26JUL06PHATOM-PHA | 21 | 23m | 2/28-28/0 | 26-24 | 7 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06SAKLIX-SAK | 56 | 29m | 1/67-67/1 | 56-64 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06TAGSUZ-SUZ | 18 | 21m | 135/23-33/5891 | 35-20 | 5 | **FLOW_ABOVE** | 32 |  |
| ITFMATCH-26JUL06TANKAW-TAN | 80 | 93m | 11/84-90/66 | 81-81 | 4 | **FLOW_ABOVE** | 80 | flow above but bound 80c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06TANVIS-VIS | 57 | 138m | 4/67-67/135 | 57-66 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06VANBOO-BOO | 62 | 131m | 0 | 62-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ZHAISH-ISH | 22 | 50m | 0 | 22-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ZHAISH-ZHA | 65 | 19m | 0 | 65-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07BOUMOC-BOU | 67 | 20m | 2/67-68/9 | 67-68 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL07BOUMOC-MOC | 30 | 18m | 4/32-32/550 | 30-31 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→32 |
| ITFMATCH-26JUL07CHOCHE-CHE | 34 | 0m | 0 | 34-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07CHOCHE-CHO | 64 | 7m | 0 | 64-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07KOIKAW-KAW | 58 | 35m | 0 | 58-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07KOIKAW-KOI | 40 | 36m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07OGUJAS-JAS | 71 | 20m | 0 | 71-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07OGUJAS-OGU | 25 | 20m | 1/28-28/0 | 25-28 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→28 |
| ITFWMATCH-26JUL06CAIOHX-CAI | 23 | 45m | 1/27-27/0 | 23-26 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ITFWMATCH-26JUL06CAIOHX-OHX | 69 | 45m | 0 | 77-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CHOPHA-PHA | 16 | 2m | 0 | 19-21 | — | **NO_FLOW** | 18 |  |
| ITFWMATCH-26JUL06GAONON-GAO | 19 | 17m | 0 | 19-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GAONON-NON | 73 | 18m | 1/82-82/23 | 73-81 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06KOSOUN-KOS | 39 | 177m | 5/41-44/71 | 39-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ITFWMATCH-26JUL06KOSOUN-OUN | 56 | 173m | 27/60-65/442 | 57-57 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFWMATCH-26JUL06LIXSUN-LIX | 33 | 13m | 0 | 33-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OHWLIU-LIU | 20 | 20m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OHWLIU-OHW | 74 | 183m | 4/80-81/9 | 74-81 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06TIAZHO-ZHO | 45 | 15m | 0 | 45-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07BATBEL-BAT | 8 | 27m | 0 | 8-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07BATBEL-BEL | 8 | 27m | 0 | 8-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07KHRBEL-KHR | 8 | 49m | 0 | 29-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07PANZHO-ZHO | 20 | 42m | 0 | 20-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07SUSKOR-KOR | 13 | 17m | 0 | 36-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07SUSKOR-SUS | 41 | 3m | 0 | 41-47 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06JULOLI | 16 | 33 | **49** | 97 | -48 |
| ATPCHALLENGERMATCH-26JUL06VARFER | 74 | 1 | **75** | 97 | -22 |
| ATPCHALLENGERMATCH-26JUL06GOMRIB | 80 | 1 | **81** | 97 | -16 |
| ATPCHALLENGERMATCH-26JUL06ABOALVA | 55 | 27 | **82** | 97 | -15 |
| ITFMATCH-26JUL06TANKAW | 17 | 81 | **98** | 97 | +1 |
| ITFMATCH-26JUL06PHATOM | 75 | 24 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06GLIYUN | 16 | 84 | **100** | 97 | +3 |
| ITFMATCH-26JUL06KIMSHI | 19 | 81 | **100** | 97 | +3 |
| ITFWMATCH-26JUL06CHOPHA | 79 | 21 | **100** | 97 | +3 |
| ITFMATCH-26JUL06BORHAR | 42 | 58 | **100** | 97 | +3 |

## PATTERNS (sub-B) — 15
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"entry_minus_fv_burst": -33.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"fill": 53, "age_min": 354, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06KOZJOH-KOZ {"fill": 66, "age_min": 349, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06GARPER-PER {"fill": 27, "age_min": 343, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GLIYUN-GLI {"fill": 16, "age_min": 333, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFWMATCH-26JUL06JULOLI-JUL {"entry_minus_fv_burst": -31.5}
- half_arm_aging: KXITFWMATCH-26JUL06JULOLI-JUL {"fill": 16, "age_min": 329, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GOMRIB-RIB {"fill": 80, "age_min": 325, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPMATCH-26JUL06LEHZVE-LEH {"fill": 24, "age_min": 317, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06RODLIN-LIN {"entry_minus_fv_burst": -15.5}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL06RODLIN {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06ABOALVA-ABO {"fill": 55, "age_min": 250, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VARFER-VAR {"fill": 74, "age_min": 212, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06TANKAW-KAW {"fill": 17, "age_min": 73, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFMATCH-26JUL06PHATOM-TOM {"fill": 75, "age_min": 41, "mode": "SET_BELOW_FLOW(prints 7c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
