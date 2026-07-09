# LIVE VALIDATION — rolling status

- cycle 55 @ **2026-07-08 11:38:06 PM ET** | build `6786127` | session boot 07-08 20:59 ET | log `live_v3_20260708.jsonl` | 16532 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 24 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:13 | ITFMATCH-26JUL08DELKUS-DEL | ITF_M | leader | 88 | 85 | +3 (place_cell) | — | pre | pair | 97 | PENDING |
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
| 23:29 | ITFMATCH-26JUL08DELKUS-KUS | ITF_M | underdog | 9 | 7 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:34 | ITFWMATCH-26JUL08CHOYAM-YAM | ITF_W | leader | 67 | 65 | +2 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 48 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 5, 'FLOW_ABOVE': 25, 'NO_FLOW': 18} | repriceable now: true 18 / false 30 | **cumulative bid_grade lines: 6014 (repriceable true 658 / false 5356)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 158m | 33/63-65/11355 | 63-64 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08ARZARC-ARC | 7 | 37m | 6/19-22/57 | 20-22 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08ARZARC-ARZ | 75 | 26m | 6/76-81/45 | 76-80 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→76 |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 158m | 35/71-77/1194 | 71-75 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 158m | 3/42-45/46 | 42-45 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 158m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MILPLA-MIL | 75 | 38m | 6/98-98/39 | 91-99 | 23 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08MUJBEL-BEL | 55 | 21m | 1/58-58/2 | 55-60 | 3 | **FLOW_ABOVE** | 58 | REPRICEABLE→58 |
| ITFMATCH-26JUL08VIVBRA-VIV | 84 | 26m | 3/90-90/11 | 87-91 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL09BORPAP-BOR | 68 | 26m | 0 | 68-72 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BORPAP-PAP | 28 | 38m | 0 | 28-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THIJER-JER | 79 | 37m | 0 | 79-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THIJER-THI | 17 | 37m | 0 | 17-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-CHO | 27 | 1m | 0 | 31-33 | — | **NO_FLOW** | 30 |  |
| ITFWMATCH-26JUL08LUENAT-LUE | 78 | 26m | 3/84-85/6 | 79-85 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08LUENAT-NAT | 14 | 37m | 2/17-20/26 | 15-20 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→17 |
| ITFWMATCH-26JUL08NAKMAL-NAK | 74 | 35m | 6/80-81/37 | 75-80 | 6 | **FLOW_ABOVE** | 74 | flow above but bound 74c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08STEJIA-JIA | 79 | 33m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08STEJIA-STE | 18 | 33m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 158m | 597/13-99/62842 | 99-13 | 1 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09AHLMAK-AHL | 31 | 128m | 8/34-34/562 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL09AHLMAK-MAK | 66 | 128m | 7/69-69/15 | 66-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL09BOSGOL-BOS | 48 | 93m | 2/52-52/325 | 48-52 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ITFWMATCH-26JUL09BOSGOL-GOL | 47 | 98m | 0 | 47-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-BER | 73 | 45m | 5/76-76/31 | 73-76 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→76 |
| ITFWMATCH-26JUL09CEUBER-CEU | 25 | 68m | 0 | 25-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DESYOD-DES | 36 | 37m | 2/38-38/176 | 36-38 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| ITFWMATCH-26JUL09DESYOD-YOD | 62 | 26m | 3/63-63/10 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL09KORSAG-KOR | 27 | 37m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KORSAG-SAG | 70 | 15m | 0 | 70-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KUHGAN-GAN | 51 | 8m | 0 | 51-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KUHGAN-KUH | 43 | 8m | 0 | 43-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09LOVSTR-LOV | 21 | 8m | 0 | 21-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09LOVSTR-STR | 74 | 5m | 0 | 74-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-ALL | 73 | 45m | 2/75-75/7 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| ITFWMATCH-26JUL09MAIALL-MAI | 25 | 68m | 0 | 25-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAMJAN-JAN | 43 | 51m | 1/46-46/52 | 43-46 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL09MAMJAN-MAM | 56 | 30m | 5/58-58/32 | 56-58 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→58 |
| ITFWMATCH-26JUL09MATDYU-DYU | 11 | 35m | 0 | 11-12 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MATDYU-MAT | 88 | 26m | 1/89-89/6 | 88-90 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| ITFWMATCH-26JUL09ROSHRU-HRU | 94 | 56m | 7/95-96/156 | 94-96 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→95 |
| ITFWMATCH-26JUL09ROSHRU-ROS | 5 | 68m | 7/5-7/551 | 5-7 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SEDKRO-KRO | 90 | 128m | 6/92-92/7 | 90-92 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFWMATCH-26JUL09SEDKRO-SED | 8 | 128m | 33/8-10/1922 | 8-9 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-NIS | 11 | 128m | 7/11-12/108 | 11-12 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-SHO | 87 | 128m | 3/89-89/8 | 87-89 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| ITFWMATCH-26JUL09TUPNUP-TUP | 92 | 128m | 9/92-95/188 | 92-93 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 158m | 4/63-64/178 | 62-64 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08OCHSAM | 12 | 1 | **13** | 97 | -84 |
| ITFMATCH-26JUL08TAKJAS | 43 | 53 | **96** | 97 | -1 |
| ITFWMATCH-26JUL08WANLEO | 85 | 13 | **98** | 97 | +1 |
| ITFMATCH-26JUL08MUJBEL | 39 | 60 | **99** | 97 | +2 |
| ITFWMATCH-26JUL08CHOYAM | 67 | 33 | **100** | 97 | +3 |
| ITFWMATCH-26JUL08NAKMAL | 23 | 80 | **103** | 97 | +6 |

## FLOW-STATE — 41 tracked game(s) ({'OPEN': 9, 'WAKING': 30, 'QUIET': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.367 | 1 | **OPEN** |
| ITFMATCH-26JUL08ARZARC | ITF_M | 0.4 | 2 | **OPEN** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 2.767 | 3 | **OPEN** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.7 | 2 | **OPEN** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.567 | 2 | **OPEN** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 0.3 | 2 | **OPEN** |
| ITFWMATCH-26JUL09ROSHRU | ITF_W | 0.367 | 2 | **OPEN** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 0.433 | 1 | **OPEN** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 0.233 | 1 | **OPEN** |
| ITFMATCH-26JUL08MILPLA | ITF_M | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL08DELKUS | ITF_M | 64.7 | — | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.067 | 4 | **WAKING** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.167 | 2 | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 4.8 | — | **WAKING** |
| ITFMATCH-26JUL08MUJBEL | ITF_M | 0.333 | 5 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 173.033 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 55.767 | — | **WAKING** |
| ITFMATCH-26JUL08VIVBRA | ITF_M | 0.133 | 4 | **WAKING** |
| ITFMATCH-26JUL09BORPAP | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09THIJER | ITF_M | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL08LUENAT | ITF_W | 0.167 | 5 | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 43.667 | — | **WAKING** |
| ITFWMATCH-26JUL08SHE2WAN2 | ITF_W | 19.3 | — | **WAKING** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 2.467 | — | **WAKING** |
| ITFWMATCH-26JUL08STEJIA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 87.267 | — | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 42.233 | — | **WAKING** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 0.167 | 3 | **WAKING** |
| ITFWMATCH-26JUL09BOSGOL | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL09CEUBER | ITF_W | 0.167 | 3 | **WAKING** |
| ITFWMATCH-26JUL09DESYOD | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL09KORSAG | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL09KUHGAN | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL09LOVSTR | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL09MAIALL | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL09MATDYU | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 0.067 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.0 | 2 | **WAKING** |

## PATTERNS (sub-B) — 15
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 43, "conception_ts": 1783566007.7132218, "detail": "buy 43c predates the conception stamp by 120min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 42, "conception_ts": 1783566007.7132218, "detail": "buy 42c predates the conception stamp by 120min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 118min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 116min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 111min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 109min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 107min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 106min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 104min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 102min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 43, "conception_ts": 1783566007.7132218, "detail": "buy 43c predates the conception stamp by 100min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFMATCH-26JUL08OCHSAM-OCH {"fill": 12, "age_min": 138, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08TAKJAS-TAK {"fill": 43, "age_min": 136, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08NAKMAL-MAL {"fill": 23, "age_min": 110, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- half_arm_aging: KXITFWMATCH-26JUL08WANLEO-WAN {"fill": 85, "age_min": 108, "mode": "SET_BELOW_FLOW(prints 1c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
