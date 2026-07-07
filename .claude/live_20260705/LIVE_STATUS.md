# LIVE VALIDATION — rolling status

- cycle 136 @ **2026-07-07 02:42:48 PM ET** | build `6b2edf7` | session boot 07-07 14:33 ET | log `live_v3_20260707.jsonl` | 5265 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 16 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:33 | ITFMATCH-26JUL07AGUPES-PES | ITF_M | ? | 26 | 22 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:33 | ITFWMATCH-26JUL07KAYDUN-DUN | ITF_W | ? | 40 | 36 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:33 | ITFMATCH-26JUL07SEGMIT-MIT | ITF_M | ? | 32 | 28 | +4 (adopted_est) | -21.0 | pre | single |  | EARNED |
| 14:33 | ITFMATCH-26JUL07BOBARO-BOB | ITF_M | ? | 56 | 53 | +3 (adopted_est) | -36.0 | pre | single |  | EARNED |
| 14:33 | ATPCHALLENGERMATCH-26JUL07HERHAR-H | ATP_CHALL | ? | 17 | 14 | +3 (adopted_est) | -6.0 | pre | single |  | EARNED |
| 14:33 | ATPCHALLENGERMATCH-26JUL07ONCCAM-C | ATP_CHALL | ? | 20 | 17 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:33 | ITFWMATCH-26JUL07EVAGOW-GOW | ITF_W | ? | 14 | 10 | +4 (adopted_est) | -27.0 | pre | single |  | EARNED |
| 14:33 | ITFWMATCH-26JUL07MAROLU-OLU | ITF_W | ? | 30 | 26 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:36 | ATPCHALLENGERMATCH-26JUL07POPPDA-P | ATP_CHALL | leader | 69 | 69 | +0 (place_cell) | -4.5 | pre | pair | 93 | EARNED |
| 14:36 | ITFMATCH-26JUL07DEDBAL-BAL | ITF_M | ? | 48 | 44 | +4 (place_cell) | — | pre | pair | 94 | PENDING |
| 14:37 | ATPCHALLENGERMATCH-26JUL07POPPDA-P | ATP_CHALL | underdog | 24 | 30 | -6 (place_cell) | -1.5 | pre | pair | 93 | EARNED |
| 14:37 | ATPCHALLENGERMATCH-26JUL07FERPAV-P | ATP_CHALL | ? | 57 | 54 | +3 (adopted_est) | 0.0 | pre | single |  | MIXED |
| 14:38 | ITFMATCH-26JUL07ZHUKEN-ZHU | ITF_M | ? | 23 | 19 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:39 | ITFWMATCH-26JUL07SCHCAN-SCH | ITF_W | ? | 13 | 9 | +4 (fill_est) | -4.5 | 2.8 | single |  | EARNED |
| 14:39 | ITFMATCH-26JUL07DEDBAL-DED | ITF_M | leader | 46 | 50 | -4 (place_cell) | — | pre | pair | 94 | PENDING |
| 14:40 | ITFWMATCH-26JUL07GOOKHA-GOO | ITF_W | ? | 17 | 13 | +4 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 15 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 1, 'FLOW_ABOVE': 8, 'NO_FLOW': 6} | repriceable now: true 2 / false 13 | **cumulative bid_grade lines: 4940 (repriceable true 425 / false 4515)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06ILARYB-R | 45 | 9m | 11/74-78/350 | 73-74 | 29 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07HERHAR-H | 17 | 6m | 115/20-39/14371 | 39-39 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ATPCHALLENGERMATCH-26JUL07JANGIL-J | 18 | 7m | 137/21-44/15404 | 37-38 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ATPCHALLENGERMATCH-26JUL07MENAVE-A | 36 | 8m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07MENAVE-M | 61 | 8m | 0 | 61-62 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07PACMEL-M | 48 | 8m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07PACMEL-P | 51 | 8m | 1/52-52/2 | 51-52 | 1 | **FLOW_ABOVE** | 49 | flow above but bound 49c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07DEDBAL-BAL | 51 | 2m | 1/56-56/5 | 56-60 | 5 | **FLOW_ABOVE** | 51 | flow above but bound 51c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07HURBOU-BOU | 68 | 8m | 0 | 68-71 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07HURBOU-HUR | 28 | 8m | 0 | 28-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07STRGUR-GUR | 6 | 9m | 0 | 6-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07THOGEO-THO | 40 | 9m | 7/64-66/22 | 65-66 | 24 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07KAYDUN-KAY | 57 | 9m | 15/80-87/409 | 78-82 | 23 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL07MIKPAQ-PAQ | 71 | 9m | 1/98-98/6 | 98-99 | 27 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07NGUGJI-NGU | 82 | 9m | 6/81-91/73 | 79-81 | -1 | **FLOW_AT_LEVEL** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL07KAYDUN | 40 | 82 | **122** | 97 | +25 |

## PATTERNS (sub-B) — 3
- deep_neg_fv: KXITFMATCH-26JUL07SEGMIT-MIT {"entry_minus_fv_burst": -21.0, "emitted_et": "2026-07-07 02:42:48 PM ET"}
- deep_neg_fv: KXITFMATCH-26JUL07BOBARO-BOB {"entry_minus_fv_burst": -36.0, "emitted_et": "2026-07-07 02:42:48 PM ET"}
- deep_neg_fv: KXITFWMATCH-26JUL07EVAGOW-GOW {"entry_minus_fv_burst": -27.0}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
