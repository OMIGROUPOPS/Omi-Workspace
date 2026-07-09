# LIVE VALIDATION — rolling status

- cycle 53 @ **2026-07-08 11:17:36 PM ET** | build `32b46fc` | session boot 07-08 20:59 ET | log `live_v3_20260708.jsonl` | 11205 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 22 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:13 | ITFMATCH-26JUL08DELKUS-DEL | ITF_M | leader | 88 | 85 | +3 (place_cell) | — | pre | single |  | PENDING |
| 21:20 | ITFMATCH-26JUL08OCHSAM-OCH | ITF_M | ? | 12 | 43 | -31 (window_cell) | — | pre | single |  | EARNED |
| 21:22 | ITFMATCH-26JUL08TAKJAS-TAK | ITF_M | ? | 43 | 22 | +21 (window_cell) | — | pre | single |  | MIXED |
| 21:48 | ITFWMATCH-26JUL08NAKMAL-MAL | ITF_W | underdog | 23 | 19 | +4 (place_cell) | — | pre | single |  | PENDING |
| 21:50 | ITFWMATCH-26JUL08WANLEO-WAN | ITF_W | leader | 85 | 83 | +2 (place_cell) | — | pre | single |  | PENDING |
| 21:56 | ITFWMATCH-26JUL08TIKZHA-TIK | ITF_W | leader | 72 | 72 | +0 (place_cell) | — | pre | pair | 94 | PENDING |
| 22:09 | ITFWMATCH-26JUL08RUOKAL-KAL | ITF_W | leader | 79 | 77 | +2 (place_cell) | — | pre | pair | 96 | PENDING |
| 22:11 | ITFWMATCH-26JUL08SUNCHO-SUN | ITF_W | leader | 79 | 75 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 22:12 | ITFWMATCH-26JUL08SHE2WAN2-WAN2 | ITF_W | leader | 56 | 57 | -1 (place_cell) | — | pre | pair | 97 | PENDING |
| 22:16 | ITFWMATCH-26JUL08RUOKAL-RUO | ITF_W | ? | 17 | 17 | +0 (place_cell) | — | pre | pair | 96 | PENDING |
| 22:17 | ITFWMATCH-26JUL08TIKZHA-ZHA | ITF_W | underdog | 22 | 26 | -4 (place_cell) | — | pre | pair | 94 | PENDING |
| 22:21 | ITFWMATCH-26JUL08SUNCHO-CHO | ITF_W | underdog | 18 | 15 | +3 (place_cell) | — | pre | pair | 97 | PENDING |
| 22:38 | ITFWMATCH-26JUL08SNINON-SNI | ITF_W | leader | 74 | 72 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 22:38 | ITFWMATCH-26JUL08SNINON-NON | ITF_W | underdog | 23 | 21 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 22:40 | ITFMATCH-26JUL08MOCTAN-MOC | ITF_M | underdog | 46 | 42 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 22:41 | ITFMATCH-26JUL08MATMAT2-MAT2 | ITF_M | underdog | 30 | 27 | +3 (place_cell) | — | pre | pair | 97 | PENDING |
| 22:43 | ITFMATCH-26JUL08HONNAK-NAK | ITF_M | underdog | 45 | 39 | +6 (place_cell) | — | pre | pair | 97 | PENDING |
| 22:44 | ITFMATCH-26JUL08HONNAK-HON | ITF_M | leader | 52 | 50 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 22:46 | ITFMATCH-26JUL08MOCTAN-TAN | ITF_M | ? | 51 | 50 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 22:46 | ITFMATCH-26JUL08MATMAT2-MAT | ITF_M | leader | 67 | 64 | +3 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:08 | ITFWMATCH-26JUL08SHE2WAN2-SHE2 | ITF_W | underdog | 41 | 40 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:16 | ITFMATCH-26JUL08MUJBEL-MUJ | ITF_M | underdog | 39 | 35 | +4 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 46 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 5, 'FLOW_ABOVE': 22, 'NO_FLOW': 19} | repriceable now: true 15 / false 31 | **cumulative bid_grade lines: 6001 (repriceable true 653 / false 5348)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 138m | 23/63-65/2290 | 63-64 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08ARZARC-ARC | 7 | 16m | 0 | 19-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08ARZARC-ARZ | 75 | 5m | 0 | 77-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08DELKUS-KUS | 9 | 7m | 292/14-29/37340 | 27-17 | 5 | **FLOW_ABOVE** | 9 | flow above but bound 9c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 138m | 34/71-77/1192 | 73-76 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 138m | 3/42-45/46 | 42-45 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 137m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MILPLA-MIL | 75 | 17m | 6/98-98/39 | 84-99 | 23 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08MUJBEL-BEL | 55 | 0m | 0 | 59-60 | — | **NO_FLOW** | 58 |  |
| ITFMATCH-26JUL08VIVBRA-VIV | 84 | 5m | 3/90-90/11 | 87-91 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL09BORPAP-BOR | 68 | 5m | 0 | 68-72 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BORPAP-PAP | 28 | 17m | 0 | 28-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THIJER-JER | 79 | 16m | 0 | 79-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THIJER-THI | 17 | 16m | 0 | 17-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 137m | 3/32-33/299 | 31-35 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→32 |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 137m | 17/67-69/421 | 67-70 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL08LUENAT-LUE | 78 | 5m | 3/84-85/6 | 79-85 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08LUENAT-NAT | 14 | 16m | 1/17-17/6 | 15-20 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→17 |
| ITFWMATCH-26JUL08NAKMAL-NAK | 74 | 14m | 5/80-81/33 | 77-80 | 6 | **FLOW_ABOVE** | 74 | flow above but bound 74c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08STEJIA-JIA | 79 | 12m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08STEJIA-STE | 18 | 12m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 137m | 597/13-99/62842 | 99-13 | 1 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09AHLMAK-AHL | 31 | 107m | 8/34-34/562 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL09AHLMAK-MAK | 66 | 107m | 4/69-69/5 | 66-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL09BOSGOL-BOS | 48 | 72m | 1/52-52/279 | 48-52 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ITFWMATCH-26JUL09BOSGOL-GOL | 47 | 77m | 0 | 47-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-BER | 73 | 25m | 0 | 73-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-CEU | 25 | 47m | 0 | 25-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DESYOD-DES | 36 | 16m | 0 | 36-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DESYOD-YOD | 62 | 5m | 1/63-63/0 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL09KORSAG-KOR | 27 | 16m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KORSAG-SAG | 69 | 16m | 0 | 69-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-ALL | 73 | 25m | 1/75-75/7 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| ITFWMATCH-26JUL09MAIALL-MAI | 25 | 47m | 0 | 25-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAMJAN-JAN | 43 | 30m | 0 | 43-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAMJAN-MAM | 56 | 10m | 1/58-58/8 | 56-58 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→58 |
| ITFWMATCH-26JUL09MATDYU-DYU | 11 | 14m | 0 | 11-12 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MATDYU-MAT | 88 | 5m | 1/89-89/6 | 88-90 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| ITFWMATCH-26JUL09ROSHRU-HRU | 94 | 36m | 7/95-96/156 | 94-96 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→95 |
| ITFWMATCH-26JUL09ROSHRU-ROS | 5 | 47m | 3/5-6/395 | 5-7 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SEDKRO-KRO | 90 | 107m | 4/92-92/4 | 90-92 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFWMATCH-26JUL09SEDKRO-SED | 8 | 107m | 28/9-10/1755 | 8-9 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFWMATCH-26JUL09SHONIS-NIS | 11 | 107m | 7/11-12/108 | 11-12 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-SHO | 87 | 107m | 2/89-89/6 | 87-89 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| ITFWMATCH-26JUL09TUPNUP-TUP | 92 | 107m | 7/92-95/185 | 92-94 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 138m | 4/63-64/178 | 62-64 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08OCHSAM | 12 | 42 | **54** | 97 | -43 |
| ITFWMATCH-26JUL08WANLEO | 85 | 13 | **98** | 97 | +1 |
| ITFMATCH-26JUL08TAKJAS | 43 | 56 | **99** | 97 | +2 |
| ITFMATCH-26JUL08MUJBEL | 39 | 60 | **99** | 97 | +2 |
| ITFWMATCH-26JUL08NAKMAL | 23 | 80 | **103** | 97 | +6 |
| ITFMATCH-26JUL08DELKUS | 88 | 17 | **105** | 97 | +8 |

## FLOW-STATE — 39 tracked game(s) ({'WAKING': 30, 'OPEN': 8, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.967 | 3 | **OPEN** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.5 | 3 | **OPEN** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 5.967 | 3 | **OPEN** |
| ITFMATCH-26JUL08MUJBEL | ITF_M | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.367 | 3 | **OPEN** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.267 | 3 | **OPEN** |
| ITFWMATCH-26JUL09ROSHRU | ITF_W | 0.267 | 2 | **OPEN** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 0.433 | 1 | **OPEN** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL08ARZARC | ITF_M | 0.167 | 3 | **WAKING** |
| ITFMATCH-26JUL08DELKUS | ITF_M | 30.1 | — | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.133 | 3 | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08MILPLA | ITF_M | 0.2 | 15 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 91.267 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 44.8 | — | **WAKING** |
| ITFMATCH-26JUL08VIVBRA | ITF_M | 0.167 | 4 | **WAKING** |
| ITFMATCH-26JUL09BORPAP | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09THIJER | ITF_M | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL08LUENAT | ITF_W | 0.3 | 5 | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 44.7 | — | **WAKING** |
| ITFWMATCH-26JUL08SHE2WAN2 | ITF_W | 6.967 | — | **WAKING** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 1.933 | 19 | **WAKING** |
| ITFWMATCH-26JUL08STEJIA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 70.433 | — | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 23.633 | — | **WAKING** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 0.067 | 3 | **WAKING** |
| ITFWMATCH-26JUL09BOSGOL | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09CEUBER | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09DESYOD | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL09KORSAG | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09MAIALL | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL09MATDYU | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 0.167 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.033 | 2 | **WAKING** |

## PATTERNS (sub-B) — 16
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 43, "conception_ts": 1783566007.7132218, "detail": "buy 43c predates the conception stamp by 120min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 42, "conception_ts": 1783566007.7132218, "detail": "buy 42c predates the conception stamp by 120min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 118min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 116min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 111min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 109min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 107min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFMATCH-26JUL08DELKUS-DEL {"fill": 88, "age_min": 124, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 106min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 104min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 102min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 43, "conception_ts": 1783566007.7132218, "detail": "buy 43c predates the conception stamp by 100min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFMATCH-26JUL08OCHSAM-OCH {"fill": 12, "age_min": 117, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08TAKJAS-TAK {"fill": 43, "age_min": 115, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08NAKMAL-MAL {"fill": 23, "age_min": 89, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- half_arm_aging: KXITFWMATCH-26JUL08WANLEO-WAN {"fill": 85, "age_min": 87, "mode": "SET_BELOW_FLOW(prints 1c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
