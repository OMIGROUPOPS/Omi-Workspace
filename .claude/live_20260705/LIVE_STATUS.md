# LIVE VALIDATION — rolling status

- cycle 33 @ **2026-07-06 08:49:56 PM ET** | build `3ae82cb` | session boot 07-06 15:26 ET | log `live_v3_20260706.jsonl` | 29595 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 17 graded (session)
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
| 19:05 | ITFMATCH-26JUL06TAGSUZ-SUZ | ITF_M | underdog | 20 | 17 | +3 (place_cell) | — | pre | single |  | PENDING |
| 20:07 | ITFMATCH-26JUL06TANKAW-KAW | ITF_M | underdog | 17 | 5 | +12 (place_cell) | — | pre | single |  | PENDING |
| 20:39 | ITFMATCH-26JUL06PHATOM-TOM | ITF_M | leader | 75 | 77 | -2 (place_cell) | — | pre | single |  | PENDING |
| 20:44 | ITFMATCH-26JUL06OCHMUT-MUT | ITF_M | underdog | 24 | 22 | +2 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 41 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 23, 'NO_FLOW': 18} | repriceable now: true 13 / false 28 | **cumulative bid_grade lines: 2612 (repriceable true 256 / false 2356)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06VUKBRO-B | 49 | 324m | 4/50-51/77 | 49-50 | 1 | **FLOW_ABOVE** | 48 | flow above but bound 48c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BORHAR-BOR | 57 | 62m | 1/59-59/4 | 58-58 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFMATCH-26JUL06BORHAR-HAR | 42 | 155m | 2/49-50/9 | 42-44 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06CHEJIN-JIN | 39 | 155m | 4/50-52/33 | 39-49 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06FUKTAK-FUK | 41 | 6m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06FUKTAK-TAK | 56 | 50m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HANKUN-HAN | 7 | 1m | 0 | 8-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HANKUN-KUN | 18 | 44m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HAZSHI-HAZ | 30 | 29m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HAZSHI-SHI | 67 | 80m | 1/70-70/50 | 67-70 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| ITFMATCH-26JUL06KIMSHI-KIM | 80 | 12m | 3/83-83/5 | 80-81 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→83 |
| ITFMATCH-26JUL06KIMSHI-SHI | 19 | 151m | 18/20-20/423 | 19-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL06MATKOM-KOM | 7 | 67m | 13/10-13/748 | 9-8 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL06MATKOM-MAT | 91 | 89m | 1/95-95/31 | 91-94 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→95 |
| ITFMATCH-26JUL06NAKIDO-IDO | 16 | 96m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06OCHMUT-OCH | 73 | 6m | 2/76-77/17 | 74-76 | 3 | **FLOW_ABOVE** | 73 | flow above but bound 73c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06OKITAN-OKI | 64 | 63m | 6/67-67/129 | 66-65 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFMATCH-26JUL06OKITAN-TAN | 33 | 79m | 2/36-37/5 | 33-36 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFMATCH-26JUL06PHATOM-PHA | 17 | 1m | 7/26-28/40 | 26-24 | 9 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06TAGSUZ-TAG | 77 | 104m | 57/80-90/2210 | 79-80 | 3 | **FLOW_ABOVE** | 77 | flow above but bound 77c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06TANKAW-TAN | 80 | 63m | 6/84-90/36 | 81-81 | 4 | **FLOW_ABOVE** | 80 | flow above but bound 80c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06TANVIS-VIS | 57 | 108m | 4/67-67/135 | 57-66 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06VANBOO-BOO | 62 | 101m | 0 | 62-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ZHAISH-ISH | 22 | 20m | 0 | 22-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07CHOCHE-CHE | 17 | 3m | 0 | 17-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07KOIKAW-KAW | 58 | 5m | 0 | 58-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07KOIKAW-KOI | 40 | 6m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CAIOHX-CAI | 23 | 15m | 1/27-27/0 | 23-26 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ITFWMATCH-26JUL06CAIOHX-OHX | 69 | 15m | 0 | 77-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CHOPHA-CHO | 79 | 121m | 3/81-81/6 | 79-81 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→81 |
| ITFWMATCH-26JUL06CHOPHA-PHA | 19 | 50m | 4/22-23/232 | 19-21 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL06GAONON-GAO | 17 | 2m | 0 | 17-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOSOUN-KOS | 39 | 146m | 4/41-44/61 | 39-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ITFWMATCH-26JUL06KOSOUN-OUN | 56 | 142m | 21/60-65/387 | 57-57 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFWMATCH-26JUL06OHWLIU-LIU | 19 | 134m | 2/26-28/0 | 19-26 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06OHWLIU-OHW | 74 | 152m | 2/81-81/8 | 74-81 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07BATBEL-BAT | 7 | 1m | 0 | 7-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07BATBEL-BEL | 7 | 18m | 0 | 7-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07KHRBEL-KHR | 8 | 19m | 0 | 26-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07PANZHO-ZHO | 20 | 11m | 0 | 20-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07SUSKOR-SUS | 24 | 1m | 0 | 25-47 | — | **NO_FLOW** | 99 |  |

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
| ITFMATCH-26JUL06TAGSUZ | 20 | 80 | **100** | 97 | +3 |
| ITFMATCH-26JUL06OCHMUT | 24 | 76 | **100** | 97 | +3 |

## PATTERNS (sub-B) — 15
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"entry_minus_fv_burst": -33.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"fill": 53, "age_min": 324, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06KOZJOH-KOZ {"fill": 66, "age_min": 318, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06GARPER-PER {"fill": 27, "age_min": 312, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GLIYUN-GLI {"fill": 16, "age_min": 303, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFWMATCH-26JUL06JULOLI-JUL {"entry_minus_fv_burst": -31.5}
- half_arm_aging: KXITFWMATCH-26JUL06JULOLI-JUL {"fill": 16, "age_min": 298, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GOMRIB-RIB {"fill": 80, "age_min": 294, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPMATCH-26JUL06LEHZVE-LEH {"fill": 24, "age_min": 287, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06RODLIN-LIN {"entry_minus_fv_burst": -15.5}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL06RODLIN {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06ABOALVA-ABO {"fill": 55, "age_min": 219, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VARFER-VAR {"fill": 74, "age_min": 181, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06TAGSUZ-SUZ {"fill": 20, "age_min": 104, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFMATCH-26JUL06TANKAW-KAW {"fill": 17, "age_min": 42, "mode": "SET_BELOW_FLOW(prints 4c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
