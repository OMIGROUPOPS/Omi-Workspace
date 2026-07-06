# LIVE VALIDATION — rolling status

- cycle 23 @ **2026-07-06 07:09:06 PM ET** | build `7c82778` | session boot 07-06 15:26 ET | log `live_v3_20260706.jsonl` | 22980 session events | monitor READ-ONLY
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

## RESTING BIDS — 22 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 15, 'FLOW_AT_LEVEL': 1} | repriceable now: true 3 / false 19 | **cumulative bid_grade lines: 2536 (repriceable true 240 / false 2296)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06VUKBRO-B | 49 | 223m | 3/51-51/68 | 49-51 | 2 | **FLOW_ABOVE** | 48 | flow above but bound 48c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BORHAR-BOR | 51 | 42m | 0 | 51-58 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BORHAR-HAR | 42 | 54m | 2/49-50/9 | 42-50 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06CHEJIN-JIN | 39 | 54m | 0 | 39-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KIMSHI-KIM | 79 | 1m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KIMSHI-SHI | 19 | 51m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MATKOM-KOM | 6 | 37m | 2/8-8/9 | 6-8 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL06NAKIDO-IDO | 15 | 12m | 0 | 15-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06OCHMUT-MUT | 23 | 54m | 4/26-26/72 | 23-26 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFMATCH-26JUL06OCHMUT-OCH | 74 | 68m | 6/74-77/158 | 74-77 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL06PHATOM-PHA | 21 | 52m | 0 | 21-24 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TAGSUZ-TAG | 77 | 4m | 0 | 80-80 | — | **NO_FLOW** | 77 |  |
| ITFMATCH-26JUL06TANVIS-VIS | 57 | 7m | 0 | 57-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VANBOO-BOO | 62 | 0m | 0 | 62-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CAIOHX-OHX | 61 | 4m | 0 | 61-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CHOPHA-CHO | 79 | 20m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CHOPHA-PHA | 17 | 1m | 0 | 18-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GAONON-GAO | 16 | 69m | 0 | 16-28 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOSOUN-KOS | 39 | 46m | 0 | 39-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOSOUN-OUN | 56 | 41m | 2/60-60/72 | 56-57 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFWMATCH-26JUL06OHWLIU-LIU | 19 | 34m | 1/26-26/0 | 19-25 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06OHWLIU-OHW | 74 | 52m | 0 | 74-81 | — | **NO_FLOW** | 99 |  |

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
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"fill": 53, "age_min": 223, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06KOZJOH-KOZ {"fill": 66, "age_min": 217, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06GARPER-PER {"fill": 27, "age_min": 211, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GLIYUN-GLI {"fill": 16, "age_min": 202, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFWMATCH-26JUL06JULOLI-JUL {"entry_minus_fv_burst": -31.5}
- half_arm_aging: KXITFWMATCH-26JUL06JULOLI-JUL {"fill": 16, "age_min": 198, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GOMRIB-RIB {"fill": 80, "age_min": 194, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPMATCH-26JUL06LEHZVE-LEH {"fill": 24, "age_min": 186, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06RODLIN-LIN {"entry_minus_fv_burst": -15.5}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL06RODLIN {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06ABOALVA-ABO {"fill": 55, "age_min": 119, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VARFER-VAR {"fill": 74, "age_min": 80, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
