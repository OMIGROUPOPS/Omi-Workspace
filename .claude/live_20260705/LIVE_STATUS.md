# LIVE VALIDATION — rolling status

- cycle 22 @ **2026-07-06 06:58:59 PM ET** | build `ad68ea4` | session boot 07-06 15:26 ET | log `live_v3_20260706.jsonl` | 21910 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 13 graded (session)
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

## RESTING BIDS — 20 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 9, 'NO_FLOW': 10, 'FLOW_AT_LEVEL': 1} | repriceable now: true 5 / false 15 | **cumulative bid_grade lines: 2530 (repriceable true 240 / false 2290)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06VUKBRO-B | 49 | 213m | 3/51-51/68 | 49-51 | 2 | **FLOW_ABOVE** | 48 | flow above but bound 48c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BORHAR-BOR | 51 | 32m | 0 | 51-58 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BORHAR-HAR | 42 | 44m | 2/49-50/9 | 42-50 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06CHEJIN-JIN | 39 | 44m | 0 | 39-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KIMSHI-SHI | 19 | 41m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MATKOM-KOM | 6 | 27m | 2/8-8/9 | 6-8 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL06NAKIDO-IDO | 15 | 2m | 0 | 15-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06OCHMUT-MUT | 23 | 44m | 3/26-26/54 | 23-26 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFMATCH-26JUL06OCHMUT-OCH | 74 | 58m | 6/74-77/158 | 74-77 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL06PHATOM-PHA | 21 | 42m | 0 | 21-24 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TAGSUZ-SUZ | 20 | 42m | 4/21-22/21 | 20-21 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFMATCH-26JUL06TAGSUZ-TAG | 79 | 40m | 2/80-80/47 | 80-80 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL06CAIOHX-OHX | 59 | 16m | 1/70-70/9 | 59-69 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06CHOPHA-CHO | 79 | 10m | 0 | 79-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CHOPHA-PHA | 12 | 39m | 0 | 12-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GAONON-GAO | 16 | 59m | 0 | 16-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOSOUN-KOS | 39 | 35m | 0 | 39-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOSOUN-OUN | 56 | 31m | 2/60-60/72 | 56-57 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFWMATCH-26JUL06OHWLIU-LIU | 19 | 24m | 1/26-26/0 | 19-26 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06OHWLIU-OHW | 74 | 42m | 0 | 74-81 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06JULOLI | 16 | 33 | **49** | 97 | -48 |
| ATPCHALLENGERMATCH-26JUL06GOMRIB | 80 | 1 | **81** | 97 | -16 |
| ATPCHALLENGERMATCH-26JUL06ABOALVA | 55 | 27 | **82** | 97 | -15 |
| ATPCHALLENGERMATCH-26JUL06VARFER | 74 | 20 | **94** | 97 | -3 |
| ATPCHALLENGERMATCH-26JUL06GLIYUN | 16 | 84 | **100** | 97 | +3 |

## PATTERNS (sub-B) — 13
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"entry_minus_fv_burst": -33.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"fill": 53, "age_min": 213, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06KOZJOH-KOZ {"fill": 66, "age_min": 207, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL06GARPER-PER {"fill": 27, "age_min": 201, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GLIYUN-GLI {"fill": 16, "age_min": 192, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFWMATCH-26JUL06JULOLI-JUL {"entry_minus_fv_burst": -31.5}
- half_arm_aging: KXITFWMATCH-26JUL06JULOLI-JUL {"fill": 16, "age_min": 188, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06GOMRIB-RIB {"fill": 80, "age_min": 183, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPMATCH-26JUL06LEHZVE-LEH {"fill": 24, "age_min": 176, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06RODLIN-LIN {"entry_minus_fv_burst": -15.5}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL06RODLIN {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06ABOALVA-ABO {"fill": 55, "age_min": 108, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VARFER-VAR {"fill": 74, "age_min": 70, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
