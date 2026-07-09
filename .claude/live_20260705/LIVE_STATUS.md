# LIVE VALIDATION — rolling status

- cycle 56 @ **2026-07-08 11:48:20 PM ET** | build `81c8eb5` | session boot 07-08 20:59 ET | log `live_v3_20260708.jsonl` | 17538 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 25 graded (session)
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
| 23:38 | ITFWMATCH-26JUL08LUENAT-NAT | ITF_W | underdog | 14 | 15 | -1 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 46 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 7, 'FLOW_ABOVE': 24, 'NO_FLOW': 15} | repriceable now: true 18 / false 28 | **cumulative bid_grade lines: 6019 (repriceable true 660 / false 5359)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL08ARZARC-ARC | 7 | 47m | 6/19-22/57 | 20-22 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08ARZARC-ARZ | 75 | 36m | 6/76-81/45 | 76-82 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→76 |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 168m | 36/71-77/1203 | 73-75 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 168m | 5/42-45/88 | 42-45 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 168m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MILPLA-MIL | 75 | 48m | 6/98-98/39 | 91-99 | 23 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08MUJBEL-BEL | 55 | 31m | 5/58-60/99 | 59-60 | 3 | **FLOW_ABOVE** | 58 | REPRICEABLE→58 |
| ITFMATCH-26JUL08VIVBRA-VIV | 84 | 36m | 4/90-91/13 | 90-92 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL09BORPAP-BOR | 68 | 36m | 1/72-72/2 | 68-72 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→72 |
| ITFMATCH-26JUL09BORPAP-PAP | 28 | 48m | 0 | 28-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THIJER-JER | 79 | 47m | 2/79-83/4 | 79-82 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL09THIJER-THI | 17 | 47m | 0 | 17-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-CHO | 28 | 1m | 0 | 32-33 | — | **NO_FLOW** | 30 |  |
| ITFWMATCH-26JUL08LUENAT-LUE | 78 | 36m | 7/84-85/43 | 81-85 | 6 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08NAKMAL-NAK | 74 | 45m | 10/76-81/153 | 75-79 | 2 | **FLOW_ABOVE** | 74 | flow above but bound 74c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08STEJIA-JIA | 79 | 43m | 1/81-81/2 | 79-81 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→81 |
| ITFWMATCH-26JUL08STEJIA-STE | 18 | 43m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 168m | 597/13-99/62842 | 99-13 | 1 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09AHLMAK-AHL | 31 | 138m | 8/34-34/562 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL09AHLMAK-MAK | 66 | 138m | 7/69-69/15 | 66-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL09BOSGOL-BOS | 48 | 103m | 3/52-52/328 | 48-52 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ITFWMATCH-26JUL09BOSGOL-GOL | 47 | 108m | 0 | 47-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-BER | 73 | 55m | 5/76-76/31 | 73-76 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→76 |
| ITFWMATCH-26JUL09CEUBER-CEU | 25 | 78m | 0 | 25-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DESYOD-DES | 36 | 47m | 2/38-38/176 | 36-38 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| ITFWMATCH-26JUL09DESYOD-YOD | 62 | 36m | 3/63-63/10 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL09KORSAG-KOR | 27 | 47m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KORSAG-SAG | 70 | 25m | 0 | 70-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KUHGAN-GAN | 51 | 18m | 0 | 51-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KUHGAN-KUH | 43 | 18m | 0 | 43-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09LOVSTR-LOV | 21 | 18m | 0 | 21-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09LOVSTR-STR | 74 | 15m | 0 | 74-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-ALL | 73 | 55m | 3/75-75/9 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| ITFWMATCH-26JUL09MAIALL-MAI | 25 | 78m | 0 | 25-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAMJAN-JAN | 43 | 61m | 4/46-46/113 | 43-46 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL09MAMJAN-MAM | 56 | 40m | 7/58-58/48 | 56-58 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→58 |
| ITFWMATCH-26JUL09MATDYU-DYU | 11 | 45m | 0 | 11-12 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MATDYU-MAT | 88 | 36m | 1/89-89/6 | 88-89 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| ITFWMATCH-26JUL09ROSHRU-HRU | 94 | 66m | 8/94-96/161 | 94-95 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09ROSHRU-ROS | 5 | 78m | 10/5-7/603 | 5-7 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SEDKRO-KRO | 90 | 138m | 6/92-92/7 | 90-92 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFWMATCH-26JUL09SEDKRO-SED | 8 | 138m | 40/8-10/2200 | 8-9 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-NIS | 11 | 138m | 12/11-12/302 | 11-12 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-SHO | 87 | 138m | 3/89-89/8 | 87-89 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| ITFWMATCH-26JUL09TUPNUP-TUP | 92 | 138m | 14/92-95/206 | 92-93 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 168m | 6/62-64/227 | 62-63 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→62 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08OCHSAM | 12 | 1 | **13** | 97 | -84 |
| ITFMATCH-26JUL08TAKJAS | 43 | 53 | **96** | 97 | -1 |
| ITFWMATCH-26JUL08WANLEO | 85 | 13 | **98** | 97 | +1 |
| ITFMATCH-26JUL08MUJBEL | 39 | 60 | **99** | 97 | +2 |
| ITFWMATCH-26JUL08LUENAT | 14 | 85 | **99** | 97 | +2 |
| ITFWMATCH-26JUL08CHOYAM | 67 | 33 | **100** | 97 | +3 |
| ITFWMATCH-26JUL08NAKMAL | 23 | 79 | **102** | 97 | +5 |

## FLOW-STATE — 40 tracked game(s) ({'OPEN': 11, 'WAKING': 27, 'QUIET': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08ARZARC | ITF_M | 0.4 | 2 | **OPEN** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 1.033 | 1 | **OPEN** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 3.467 | 1 | **OPEN** |
| ITFMATCH-26JUL08MUJBEL | ITF_M | 0.367 | 1 | **OPEN** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.8 | 1 | **OPEN** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 1.0 | 3 | **OPEN** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 0.333 | 2 | **OPEN** |
| ITFWMATCH-26JUL09ROSHRU | ITF_W | 0.267 | 1 | **OPEN** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 0.467 | 1 | **OPEN** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 0.233 | 1 | **OPEN** |
| ITFMATCH-26JUL08MILPLA | ITF_M | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL08DELKUS | ITF_M | 91.7 | — | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.067 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 10.033 | — | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 157.4 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 60.433 | — | **WAKING** |
| ITFMATCH-26JUL08VIVBRA | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL09BORPAP | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL09THIJER | ITF_M | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL08LUENAT | ITF_W | 0.267 | 4 | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 50.033 | — | **WAKING** |
| ITFWMATCH-26JUL08SHE2WAN2 | ITF_W | 29.333 | — | **WAKING** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.9 | — | **WAKING** |
| ITFWMATCH-26JUL08STEJIA | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 127.7 | — | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 70.133 | — | **WAKING** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 0.1 | 3 | **WAKING** |
| ITFWMATCH-26JUL09BOSGOL | ITF_W | 0.067 | 4 | **WAKING** |
| ITFWMATCH-26JUL09CEUBER | ITF_W | 0.133 | 3 | **WAKING** |
| ITFWMATCH-26JUL09DESYOD | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL09KORSAG | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL09KUHGAN | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL09LOVSTR | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL09MAIALL | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL09MATDYU | ITF_W | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.067 | 1 | **WAKING** |

## PATTERNS (sub-B) — 16
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
- half_arm_aging: KXITFMATCH-26JUL08OCHSAM-OCH {"fill": 12, "age_min": 148, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08TAKJAS-TAK {"fill": 43, "age_min": 146, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08NAKMAL-MAL {"fill": 23, "age_min": 120, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFWMATCH-26JUL08WANLEO-WAN {"fill": 85, "age_min": 118, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFMATCH-26JUL08MUJBEL-MUJ {"fill": 39, "age_min": 31, "mode": "SET_BELOW_FLOW(prints 3c above)", "emitted_et": "2026-07-08 11:48:20 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
