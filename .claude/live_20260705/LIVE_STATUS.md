# LIVE VALIDATION — rolling status

- cycle 81 @ **2026-07-05 10:46:59 AM ET** | build `353d2f5` | session boot 07-05 10:39 ET | log `live_v3_20260705.jsonl` | 1723 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 10 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10:39 | ITFWMATCH-26JUL05TRAABB-ABB | ITF_W | ? | 64 | 64 | +0 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 10:39 | ATPCHALLENGERMATCH-26JUL05RAMNEU-R | ATP_CHALL | ? | 36 | 2 | +34 (window_cell) | — | pre | single |  | MIXED |
| 10:39 | ATPCHALLENGERMATCH-26JUL05WEHIFI-I | ATP_CHALL | ? | 11 | 8 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 10:39 | WTACHALLENGERMATCH-26JUL05DITLEW-D | WTA_CHALL | ? | 31 | 28 | +3 (adopted_est) | 25.5 | pre | single |  | GIFT_CLASS |
| 10:39 | ATPCHALLENGERMATCH-26JUL05KUZMAT-M | ATP_CHALL | ? | 5 | 2 | +3 (adopted_est) | -2.5 | pre | single |  | MIXED |
| 10:40 | ITFWMATCH-26JUL05AITDAE-AIT | ITF_W | underdog | 8 | 4 | +4 (place_cell) | — | pre | single |  | MIXED |
| 10:41 | ATPCHALLENGERMATCH-26JUL05VALREJ-V | ATP_CHALL | leader | 62 | 71 | -9 (place_cell) | — | pre | single |  | MIXED |
| 10:41 | ATPCHALLENGERMATCH-26JUL05CIZCAZ-C | ATP_CHALL | underdog | 23 | 19 | +4 (place_cell) | — | pre | single |  | MIXED |
| 10:41 | ITFMATCH-26JUL05GELBRE-GEL | ITF_M | ? | 44 | 40 | +4 (window_cell) | — | pre | single |  | MIXED |
| 10:42 | WTAMATCH-26JUL05BENGAU-GAU | WTA_MAIN | ? | 50 | 50 | +0 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 20 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 11, 'NO_FLOW': 9} | repriceable now: true 1 / false 19 | **cumulative bid_grade lines: 648 (repriceable true 58 / false 590)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BANMAR-B | 65 | 6m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BANMAR-M | 33 | 6m | 2/36-36/132 | 33-36 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05DESYEV-D | 29 | 7m | 124/45-73/13462 | 60-46 | 16 | **FLOW_ABOVE** | 70 |  |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-E | 65 | 6m | 0 | 65-67 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-J | 33 | 6m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GANZIN-G | 28 | 6m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GANZIN-Z | 70 | 6m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05POTANG-P | 50 | 7m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05RAMNEU-N | 61 | 7m | 17/98-99/2359 | 99-98 | 37 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05STEDIN-S | 26 | 7m | 60/46-63/3249 | 62-47 | 20 | **FLOW_ABOVE** | 55 |  |
| ATPCHALLENGERMATCH-26JUL05VALREJ-R | 37 | 6m | 14/43-50/1033 | 45-38 | 6 | **FLOW_ABOVE** | 27 | flow above but bound 27c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05VILPUR-V | 16 | 7m | 100/40-65/8450 | 56-42 | 24 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05AUGDAV-DAV | 34 | 7m | 23/39-41/8361 | 39-40 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL05SABMIS-SAB | 1 | 6m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL05SALCON-CON | 8 | 7m | 181/11-33/15448 | 20-13 | 3 | **FLOW_ABOVE** | 29 | REPRICEABLE→11 |
| ITFWMATCH-26JUL05ALVJOH-ALV | 24 | 7m | 750/44-99/66645 | 87-54 | 20 | **FLOW_ABOVE** | 88 |  |
| ITFWMATCH-26JUL05TRAABB-TRA | 31 | 0m | 3/52-53/204 | 53-36 | 21 | **FLOW_ABOVE** | 29 | flow above but bound 29c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05TUBSOB-SOB | 25 | 7m | 13/32-41/155 | 32-41 | 7 | **FLOW_ABOVE** | 30 | flow above but bound 30c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05YAMOVC-O | 28 | 6m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05YAMOVC-Y | 70 | 6m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL05TRAABB | 64 | 36 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05VALREJ | 62 | 38 | **100** | 97 | +3 |
| ITFWMATCH-26JUL05AITDAE | 8 | 94 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05CIZCAZ | 23 | 82 | **105** | 97 | +8 |
| ITFMATCH-26JUL05GELBRE | 44 | 62 | **106** | 97 | +9 |
| ATPCHALLENGERMATCH-26JUL05RAMNEU | 36 | 98 | **134** | 97 | +37 |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
