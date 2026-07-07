# LIVE VALIDATION — rolling status

- cycle 112 @ **2026-07-07 10:27:08 AM ET** | build `54ad392` | session boot 07-07 10:21 ET | log `live_v3_20260707.jsonl` | 5502 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 20 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10:21 | WTACHALLENGERMATCH-26JUL07ZANJAC-Z | WTA_CHALL | ? | 28 | 25 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | WTACHALLENGERMATCH-26JUL07ZANJAC-J | WTA_CHALL | ? | 69 | 66 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | ITFMATCH-26JUL07MOUMON-MOU | ITF_M | ? | 34 | 30 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 10:21 | ATPCHALLENGERMATCH-26JUL07HAMWAL-H | ATP_CHALL | ? | 13 | 10 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 10:21 | ITFWMATCH-26JUL07BUEXAV-XAV | ITF_W | ? | 68 | 66 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 10:21 | ATPCHALLENGERMATCH-26JUL07GASCHE-C | ATP_CHALL | ? | 24 | 21 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 10:21 | ITFWMATCH-26JUL07SIMROU-SIM | ITF_W | ? | 33 | 66 | -33 (window_cell) | — | pre | single |  | EARNED |
| 10:21 | ITFWMATCH-26JUL07KHRYOU-KHR | ITF_W | ? | 44 | 40 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | ITFWMATCH-26JUL07KHRYOU-YOU | ITF_W | ? | 53 | 51 | +2 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | ATPCHALLENGERMATCH-26JUL07WALVAL-W | ATP_CHALL | ? | 32 | 2 | +30 (window_cell) | — | pre | single |  | MIXED |
| 10:21 | ITFWMATCH-26JUL07GUESAN-SAN | ITF_W | ? | 8 | 4 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 10:21 | ITFMATCH-26JUL07URSPOU-POU | ITF_M | ? | 50 | 33 | +17 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 10:21 | ITFWMATCH-26JUL07MALKOM-KOM | ITF_W | ? | 10 | 6 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 10:21 | ITFWMATCH-26JUL07VRARUG-RUG | ITF_W | ? | 61 | 59 | +2 (adopted_est) | 30.5 | pre | single |  | GIFT_CLASS |
| 10:23 | ATPCHALLENGERMATCH-26JUL07ZAHSEA-S | ATP_CHALL | ? | 82 | 79 | +3 (fill_est) | -2.5 | pre | single |  | MIXED |
| 10:23 | ITFWMATCH-26JUL07MELDIG-MEL | ITF_W | underdog | 4 | 2 | +2 (place_cell) | — | pre | single |  | PENDING |
| 10:23 | ATPCHALLENGERMATCH-26JUL07GUEDON-D | ATP_CHALL | ? | 29 | 29 | +0 (window_cell) | — | pre | single |  | EARNED |
| 10:25 | WTACHALLENGERMATCH-26JUL07GALRIN-G | WTA_CHALL | ? | 63 | 60 | +3 (fill_est) | -7.5 | 0.8 | single |  | EARNED |
| 10:25 | ITFMATCH-26JUL07GAGMED-MED | ITF_M | ? | 10 | 6 | +4 (fill_est) | -5.5 | 1.1 | single |  | EARNED |
| 10:25 | ITFMATCH-26JUL07TSIHER-TSI | ITF_M | ? | 50 | 47 | +3 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 18 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 11, 'NO_FLOW': 6, 'FLOW_AT_LEVEL': 1} | repriceable now: true 2 / false 16 | **cumulative bid_grade lines: 4774 (repriceable true 413 / false 4361)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07BOSMIC-M | 54 | 5m | 19/72-81/747 | 75-75 | 18 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07MRVVIL-V | 32 | 5m | 58/47-65/6726 | 64-65 | 15 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL07AUGDJO-AUG | 39 | 5m | 10/40-40/2279 | 39-40 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |
| ATPMATCH-26JUL07AUGDJO-DJO | 60 | 5m | 16/60-61/470 | 60-61 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL07COXBRA-BRA | 3 | 5m | 0 | 20-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07DELFER-FER | 6 | 4m | 0 | 6-28 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07IAMGAL-GAL | 57 | 5m | 6/80-84/374 | 81-82 | 23 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL07SICTAB-SIC | 13 | 5m | 40/18-21/3550 | 18-19 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL07SULFRI-FRI | 16 | 5m | 54/20-31/5546 | 29-30 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL07URSPOU-URS | 47 | 5m | 22/57-64/1095 | 52-54 | 10 | **FLOW_ABOVE** | 47 | flow above but bound 47c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL07BADMIK-BAD | 61 | 5m | 8/84-90/376 | 82-84 | 23 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07GUESAN-GUE | 89 | 5m | 0 | 97-98 | — | **NO_FLOW** | 89 |  |
| ITFWMATCH-26JUL07JAUMAT-JAU | 47 | 5m | 5/70-73/108 | 63-66 | 23 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07MCNREE-REE | 54 | 5m | 4/70-71/425 | 63-65 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07VRARUG-VRA | 36 | 5m | 103/53-78/6664 | 56-53 | 17 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL07SCOSTO-S | 18 | 4m | 0 | 18-19 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL07SCOSTO-S | 82 | 5m | 0 | 82-83 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL07SEBBRA-B | 51 | 5m | 0 | 51-52 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL07SIMROU | 33 | 36 | **69** | 97 | -28 |
| ATPCHALLENGERMATCH-26JUL07GUEDON | 29 | 58 | **87** | 97 | -10 |
| ITFMATCH-26JUL07URSPOU | 50 | 54 | **104** | 97 | +7 |
| ITFWMATCH-26JUL07GUESAN | 8 | 98 | **106** | 97 | +9 |
| ITFWMATCH-26JUL07VRARUG | 61 | 53 | **114** | 97 | +17 |
| ATPCHALLENGERMATCH-26JUL07WALVAL | 32 | 99 | **131** | 97 | +34 |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
