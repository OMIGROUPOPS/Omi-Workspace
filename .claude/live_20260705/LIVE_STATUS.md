# LIVE VALIDATION — rolling status

- cycle 28 @ **2026-07-06 07:59:30 PM ET** | build `28847d5` | session boot 07-06 15:26 ET | log `live_v3_20260706.jsonl` | 26027 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 14 graded (session)
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

## RESTING BIDS — 31 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 14, 'NO_FLOW': 16, 'FLOW_AT_LEVEL': 1} | repriceable now: true 8 / false 23 | **cumulative bid_grade lines: 2570 (repriceable true 246 / false 2324)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06VUKBRO-B | 49 | 273m | 4/50-51/77 | 49-50 | 1 | **FLOW_ABOVE** | 48 | flow above but bound 48c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BORHAR-BOR | 57 | 12m | 0 | 58-58 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BORHAR-HAR | 42 | 104m | 2/49-50/9 | 42-45 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06CHEJIN-JIN | 39 | 104m | 2/51-52/9 | 39-51 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06HANKUN-KUN | 12 | 2m | 0 | 13-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HAZSHI-HAZ | 28 | 29m | 0 | 28-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HAZSHI-SHI | 67 | 29m | 0 | 67-72 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KIMSHI-KIM | 79 | 51m | 1/83-83/23 | 79-81 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→83 |
| ITFMATCH-26JUL06KIMSHI-SHI | 19 | 101m | 7/20-20/175 | 19-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL06MATKOM-KOM | 7 | 17m | 4/10-13/109 | 7-8 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL06MATKOM-MAT | 91 | 39m | 0 | 91-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06NAKIDO-IDO | 16 | 46m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06OCHMUT-MUT | 23 | 104m | 7/26-26/445 | 23-26 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFMATCH-26JUL06OCHMUT-OCH | 74 | 118m | 7/74-77/161 | 74-77 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL06OKITAN-OKI | 64 | 12m | 2/67-67/72 | 66-65 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFMATCH-26JUL06OKITAN-TAN | 33 | 29m | 0 | 33-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06PHATOM-PHA | 21 | 102m | 0 | 21-24 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06PHATOM-TOM | 75 | 21m | 0 | 75-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TAGSUZ-TAG | 77 | 54m | 5/80-81/44 | 79-80 | 3 | **FLOW_ABOVE** | 77 | flow above but bound 77c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06TANKAW-KAW | 17 | 16m | 3/18-18/6 | 17-18 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→18 |
| ITFMATCH-26JUL06TANKAW-TAN | 80 | 12m | 0 | 82-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TANVIS-VIS | 57 | 57m | 0 | 57-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VANBOO-BOO | 62 | 51m | 0 | 62-66 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CAIOHX-OHX | 62 | 35m | 0 | 62-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CHOPHA-CHO | 79 | 71m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CHOPHA-PHA | 18 | 49m | 3/21-22/23 | 18-21 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFWMATCH-26JUL06GAONON-GAO | 16 | 119m | 0 | 16-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOSOUN-KOS | 39 | 96m | 1/44-44/10 | 39-44 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06KOSOUN-OUN | 56 | 92m | 3/60-60/104 | 56-57 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFWMATCH-26JUL06OHWLIU-LIU | 19 | 84m | 1/26-26/0 | 19-26 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06OHWLIU-OHW | 74 | 102m | 0 | 74-81 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06JULOLI | 16 | 33 | **49** | 97 | -48 |
| ATPCHALLENGERMATCH-26JUL06VARFER | 74 | 2 | **76** | 97 | -21 |
| ATPCHALLENGERMATCH-26JUL06GOMRIB | 80 | 1 | **81** | 97 | -16 |
| ATPCHALLENGERMATCH-26JUL06ABOALVA | 55 | 27 | **82** | 97 | -15 |
| ATPCHALLENGERMATCH-26JUL06GLIYUN | 16 | 84 | **100** | 97 | +3 |
| ITFMATCH-26JUL06TAGSUZ | 20 | 80 | **100** | 97 | +3 |

## PATTERNS (sub-B) — 14
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"entry_minus_fv_burst": -33.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"fill": 53, "age_min": 273, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06KOZJOH-KOZ {"fill": 66, "age_min": 268, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06GARPER-PER {"fill": 27, "age_min": 262, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GLIYUN-GLI {"fill": 16, "age_min": 253, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFWMATCH-26JUL06JULOLI-JUL {"entry_minus_fv_burst": -31.5}
- half_arm_aging: KXITFWMATCH-26JUL06JULOLI-JUL {"fill": 16, "age_min": 248, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GOMRIB-RIB {"fill": 80, "age_min": 244, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPMATCH-26JUL06LEHZVE-LEH {"fill": 24, "age_min": 236, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06RODLIN-LIN {"entry_minus_fv_burst": -15.5}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL06RODLIN {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06ABOALVA-ABO {"fill": 55, "age_min": 169, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VARFER-VAR {"fill": 74, "age_min": 131, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06TAGSUZ-SUZ {"fill": 20, "age_min": 54, "mode": "SET_BELOW_FLOW(prints 3c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
