# LIVE VALIDATION — rolling status

- cycle 137 @ **2026-07-07 02:53:34 PM ET** | build `bf23209` | session boot 07-07 14:33 ET | log `live_v3_20260707.jsonl` | 9187 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 23 graded (session)
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
| 14:43 | ITFWMATCH-26JUL07NGUGJI-NGU | ITF_W | ? | 82 | 80 | +2 (fill_est) | — | pre | single |  | PENDING |
| 14:43 | ITFMATCH-26JUL07MESBYN-BYN | ITF_M | ? | 32 | 28 | +4 (adopted_est) | — | pre | pair | 95 | PENDING |
| 14:48 | ITFMATCH-26JUL07MESBYN-MES | ITF_M | ? | 63 | 60 | +3 (adopted_est) | — | pre | pair | 95 | PENDING |
| 14:48 | ATPCHALLENGERMATCH-26JUL07MEJTEN-T | ATP_CHALL | ? | 6 | 7 | -1 (window_cell) | — | pre | single |  | EARNED |
| 14:51 | ATPCHALLENGERMATCH-26JUL07PACMEL-M | ATP_CHALL | underdog | 48 | 45 | +3 (place_cell) | — | pre | single |  | MIXED |
| 14:52 | ITFMATCH-26JUL07ARSWIL-WIL | ITF_M | ? | 52 | 49 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:52 | ITFMATCH-26JUL07TISNAP-NAP | ITF_M | ? | 24 | 20 | +4 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 12 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 5, 'FLOW_AT_LEVEL': 1} | repriceable now: true 0 / false 12 | **cumulative bid_grade lines: 4944 (repriceable true 425 / false 4519)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07MENAVE-A | 36 | 19m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07MENAVE-M | 61 | 19m | 0 | 61-62 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07PACMEL-P | 49 | 2m | 2/52-52/99 | 52-53 | 3 | **FLOW_ABOVE** | 49 | flow above but bound 49c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07DEDBAL-BAL | 51 | 13m | 10/49-65/179 | 47-49 | -2 | **FLOW_AT_LEVEL** | 51 |  |
| ITFMATCH-26JUL07HURBOU-BOU | 68 | 19m | 0 | 68-71 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07HURBOU-HUR | 28 | 19m | 0 | 28-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07MESBYN-BYN | 34 | 1m | 1/35-35/13 | 34-35 | 1 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07STRGUR-GUR | 6 | 20m | 0 | 7-9 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07THOGEO-THO | 40 | 20m | 45/61-74/3252 | 73-74 | 21 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07GOOKHA-GOO | 23 | 1m | 1/31-31/21 | 29-31 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07KAYDUN-KAY | 57 | 20m | 38/67-87/1359 | 66-69 | 10 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL07MIKPAQ-PAQ | 71 | 20m | 1/98-98/6 | 98-99 | 27 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07PACMEL | 48 | 53 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL07MEJTEN | 6 | 97 | **103** | 97 | +6 |
| ITFWMATCH-26JUL07KAYDUN | 40 | 69 | **109** | 97 | +12 |

## PATTERNS (sub-B) — 3
- deep_neg_fv: KXITFMATCH-26JUL07SEGMIT-MIT {"entry_minus_fv_burst": -21.0}
- deep_neg_fv: KXITFMATCH-26JUL07BOBARO-BOB {"entry_minus_fv_burst": -36.0}
- deep_neg_fv: KXITFWMATCH-26JUL07EVAGOW-GOW {"entry_minus_fv_burst": -27.0}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
