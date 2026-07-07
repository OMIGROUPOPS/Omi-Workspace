# LIVE VALIDATION — rolling status

- cycle 35 @ **2026-07-06 09:10:18 PM ET** | build `b914270` | session boot 07-06 15:26 ET | log `live_v3_20260706.jsonl` | 32037 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 21 graded (session)
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
| 20:44 | ITFMATCH-26JUL06OCHMUT-MUT | ITF_M | underdog | 24 | 22 | +2 (place_cell) | — | pre | single |  | PENDING |
| 20:52 | ITFMATCH-26JUL06KIMSHI-SHI | ITF_M | underdog | 19 | 17 | +2 (place_cell) | — | pre | single |  | PENDING |
| 20:57 | ITFMATCH-26JUL06TAGSUZ-TAG | ITF_M | leader | 65 | 49 | +16 (place_cell) | — | pre | pair | 85 | PENDING |
| 21:02 | ITFWMATCH-26JUL06CHOPHA-CHO | ITF_W | ? | 79 | 77 | +2 (place_cell) | — | pre | single |  | PENDING |
| 21:03 | ITFMATCH-26JUL06BORHAR-HAR | ITF_M | underdog | 42 | 38 | +4 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 49 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 23, 'NO_FLOW': 26} | repriceable now: true 11 / false 38 | **cumulative bid_grade lines: 2643 (repriceable true 259 / false 2384)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06VUKBRO-B | 49 | 344m | 4/50-51/77 | 49-50 | 1 | **FLOW_ABOVE** | 48 | flow above but bound 48c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BORHAR-BOR | 55 | 7m | 2/74-75/13 | 58-58 | 19 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06CHEJIN-JIN | 39 | 175m | 4/50-52/33 | 39-49 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06FUKTAK-FUK | 41 | 26m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06FUKTAK-TAK | 56 | 70m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HANKUN-HAN | 17 | 1m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HANKUN-KUN | 20 | 11m | 0 | 20-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HAZSHI-HAZ | 30 | 49m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HAZSHI-SHI | 67 | 100m | 2/70-70/56 | 67-70 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| ITFMATCH-26JUL06KIMSHI-KIM | 78 | 18m | 8/88-93/99 | 84-81 | 10 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06MATKOM-KOM | 7 | 88m | 26/10-13/1541 | 9-8 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL06MATKOM-MAT | 91 | 110m | 2/94-95/32 | 91-94 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→94 |
| ITFMATCH-26JUL06NAKIDO-IDO | 16 | 116m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06OCHMUT-OCH | 73 | 26m | 9/75-77/273 | 74-75 | 2 | **FLOW_ABOVE** | 73 | flow above but bound 73c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06OKITAN-OKI | 64 | 83m | 10/67-67/217 | 67-65 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFMATCH-26JUL06OKITAN-TAN | 33 | 99m | 3/36-37/6 | 33-36 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFMATCH-26JUL06PHATOM-PHA | 21 | 13m | 1/28-28/0 | 26-24 | 7 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06SAKLIX-SAK | 56 | 19m | 1/67-67/1 | 56-64 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06TAGSUZ-SUZ | 18 | 11m | 54/23-28/2088 | 35-20 | 5 | **FLOW_ABOVE** | 32 |  |
| ITFMATCH-26JUL06TANKAW-TAN | 80 | 83m | 9/84-90/64 | 81-81 | 4 | **FLOW_ABOVE** | 80 | flow above but bound 80c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06TANVIS-VIS | 57 | 128m | 4/67-67/135 | 57-66 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06VANBOO-BOO | 62 | 121m | 0 | 62-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ZHAISH-ISH | 22 | 40m | 0 | 22-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ZHAISH-ZHA | 65 | 9m | 0 | 65-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07BOUMOC-BOU | 67 | 10m | 1/68-68/8 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL07BOUMOC-MOC | 30 | 8m | 4/32-32/550 | 30-31 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→32 |
| ITFMATCH-26JUL07CHOCHE-CHE | 32 | 1m | 0 | 33-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07CHOCHE-CHO | 61 | 2m | 0 | 61-69 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07KOIKAW-KAW | 58 | 25m | 0 | 58-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07KOIKAW-KOI | 40 | 26m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07OGUJAS-JAS | 71 | 10m | 0 | 71-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07OGUJAS-OGU | 25 | 10m | 1/28-28/0 | 25-28 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→28 |
| ITFWMATCH-26JUL06CAIOHX-CAI | 23 | 35m | 1/27-27/0 | 23-26 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ITFWMATCH-26JUL06CAIOHX-OHX | 69 | 35m | 0 | 77-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CHOPHA-PHA | 16 | 1m | 0 | 18-21 | — | **NO_FLOW** | 18 |  |
| ITFWMATCH-26JUL06GAONON-GAO | 19 | 7m | 0 | 19-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GAONON-NON | 73 | 8m | 1/82-82/23 | 73-81 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06KOSOUN-KOS | 39 | 167m | 4/41-44/61 | 39-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ITFWMATCH-26JUL06KOSOUN-OUN | 56 | 163m | 27/60-65/442 | 57-57 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFWMATCH-26JUL06LIXSUN-LIX | 33 | 3m | 0 | 33-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OHWLIU-LIU | 20 | 9m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OHWLIU-OHW | 74 | 173m | 4/80-81/9 | 74-80 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06TIAZHO-ZHO | 45 | 5m | 0 | 45-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07BATBEL-BAT | 8 | 17m | 0 | 8-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07BATBEL-BEL | 8 | 17m | 0 | 8-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07KHRBEL-KHR | 8 | 39m | 0 | 30-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07PANZHO-ZHO | 20 | 32m | 0 | 20-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07SUSKOR-KOR | 13 | 7m | 0 | 34-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07SUSKOR-SUS | 37 | 1m | 0 | 38-47 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06JULOLI | 16 | 33 | **49** | 97 | -48 |
| ATPCHALLENGERMATCH-26JUL06VARFER | 74 | 1 | **75** | 97 | -22 |
| ATPCHALLENGERMATCH-26JUL06GOMRIB | 80 | 1 | **81** | 97 | -16 |
| ATPCHALLENGERMATCH-26JUL06ABOALVA | 55 | 27 | **82** | 97 | -15 |
| ITFMATCH-26JUL06TANKAW | 17 | 81 | **98** | 97 | +1 |
| ITFMATCH-26JUL06PHATOM | 75 | 24 | **99** | 97 | +2 |
| ITFMATCH-26JUL06OCHMUT | 24 | 75 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06GLIYUN | 16 | 84 | **100** | 97 | +3 |
| ITFMATCH-26JUL06KIMSHI | 19 | 81 | **100** | 97 | +3 |
| ITFWMATCH-26JUL06CHOPHA | 79 | 21 | **100** | 97 | +3 |
| ITFMATCH-26JUL06BORHAR | 42 | 58 | **100** | 97 | +3 |

## PATTERNS (sub-B) — 15
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"entry_minus_fv_burst": -33.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"fill": 53, "age_min": 344, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06KOZJOH-KOZ {"fill": 66, "age_min": 339, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06GARPER-PER {"fill": 27, "age_min": 333, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GLIYUN-GLI {"fill": 16, "age_min": 323, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFWMATCH-26JUL06JULOLI-JUL {"entry_minus_fv_burst": -31.5}
- half_arm_aging: KXITFWMATCH-26JUL06JULOLI-JUL {"fill": 16, "age_min": 319, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GOMRIB-RIB {"fill": 80, "age_min": 315, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPMATCH-26JUL06LEHZVE-LEH {"fill": 24, "age_min": 307, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06RODLIN-LIN {"entry_minus_fv_burst": -15.5}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL06RODLIN {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06ABOALVA-ABO {"fill": 55, "age_min": 240, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VARFER-VAR {"fill": 74, "age_min": 202, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06TANKAW-KAW {"fill": 17, "age_min": 62, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFMATCH-26JUL06PHATOM-TOM {"fill": 75, "age_min": 31, "mode": "SET_BELOW_FLOW(prints 7c above)", "emitted_et": "2026-07-06 09:10:18 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
