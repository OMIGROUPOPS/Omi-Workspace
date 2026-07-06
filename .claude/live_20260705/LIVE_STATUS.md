# LIVE VALIDATION — rolling status

- cycle 24 @ **2026-07-06 07:19:12 PM ET** | build `e6d8e58` | session boot 07-06 15:26 ET | log `live_v3_20260706.jsonl` | 23541 session events | monitor READ-ONLY
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

## RESTING BIDS — 26 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 8, 'NO_FLOW': 17, 'FLOW_AT_LEVEL': 1} | repriceable now: true 4 / false 22 | **cumulative bid_grade lines: 2543 (repriceable true 241 / false 2302)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06VUKBRO-B | 49 | 233m | 4/50-51/77 | 49-50 | 1 | **FLOW_ABOVE** | 48 | flow above but bound 48c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BORHAR-BOR | 51 | 52m | 0 | 51-58 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BORHAR-HAR | 42 | 64m | 2/49-50/9 | 42-50 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06CHEJIN-JIN | 39 | 64m | 0 | 39-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KIMSHI-KIM | 79 | 11m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KIMSHI-SHI | 19 | 61m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MATKOM-KOM | 6 | 47m | 2/8-8/9 | 6-8 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL06NAKIDO-IDO | 16 | 5m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06OCHMUT-MUT | 23 | 64m | 5/26-26/437 | 23-26 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFMATCH-26JUL06OCHMUT-OCH | 74 | 78m | 7/74-77/161 | 74-77 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL06OKITAN-OKI | 54 | 0m | 0 | 55-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06OKITAN-TAN | 27 | 0m | 0 | 28-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06PHATOM-PHA | 21 | 62m | 0 | 21-24 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TAGSUZ-TAG | 77 | 14m | 1/81-81/18 | 80-80 | 4 | **FLOW_ABOVE** | 77 | flow above but bound 77c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06TANKAW-KAW | 10 | 0m | 0 | 11-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TANKAW-TAN | 54 | 0m | 0 | 55-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TANVIS-VIS | 57 | 17m | 0 | 57-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VANBOO-BOO | 62 | 10m | 0 | 62-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CAIOHX-OHX | 61 | 14m | 0 | 61-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CHOPHA-CHO | 79 | 30m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CHOPHA-PHA | 18 | 9m | 1/22-22/19 | 18-21 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL06GAONON-GAO | 16 | 79m | 0 | 16-28 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOSOUN-KOS | 39 | 56m | 0 | 39-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOSOUN-OUN | 56 | 52m | 2/60-60/72 | 56-57 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFWMATCH-26JUL06OHWLIU-LIU | 19 | 44m | 1/26-26/0 | 19-26 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06OHWLIU-OHW | 74 | 62m | 0 | 74-81 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06JULOLI | 16 | 33 | **49** | 97 | -48 |
| ATPCHALLENGERMATCH-26JUL06GOMRIB | 80 | 1 | **81** | 97 | -16 |
| ATPCHALLENGERMATCH-26JUL06ABOALVA | 55 | 27 | **82** | 97 | -15 |
| ATPCHALLENGERMATCH-26JUL06VARFER | 74 | 20 | **94** | 97 | -3 |
| ATPCHALLENGERMATCH-26JUL06GLIYUN | 16 | 84 | **100** | 97 | +3 |
| ITFMATCH-26JUL06TAGSUZ | 20 | 80 | **100** | 97 | +3 |

## PATTERNS (sub-B) — 13
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"entry_minus_fv_burst": -33.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"fill": 53, "age_min": 233, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06KOZJOH-KOZ {"fill": 66, "age_min": 228, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06GARPER-PER {"fill": 27, "age_min": 221, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GLIYUN-GLI {"fill": 16, "age_min": 212, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFWMATCH-26JUL06JULOLI-JUL {"entry_minus_fv_burst": -31.5}
- half_arm_aging: KXITFWMATCH-26JUL06JULOLI-JUL {"fill": 16, "age_min": 208, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GOMRIB-RIB {"fill": 80, "age_min": 204, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPMATCH-26JUL06LEHZVE-LEH {"fill": 24, "age_min": 196, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06RODLIN-LIN {"entry_minus_fv_burst": -15.5}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL06RODLIN {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06ABOALVA-ABO {"fill": 55, "age_min": 129, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VARFER-VAR {"fill": 74, "age_min": 90, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
