# LIVE VALIDATION — rolling status

- cycle 52 @ **2026-07-08 11:07:12 PM ET** | build `bc3a9a1` | session boot 07-08 20:59 ET | log `live_v3_20260708.jsonl` | 10020 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 20 graded (session)
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
| 22:12 | ITFWMATCH-26JUL08SHE2WAN2-WAN2 | ITF_W | leader | 56 | 57 | -1 (place_cell) | — | pre | single |  | PENDING |
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

## RESTING BIDS — 40 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 5, 'FLOW_ABOVE': 15, 'NO_FLOW': 20} | repriceable now: true 10 / false 30 | **cumulative bid_grade lines: 5987 (repriceable true 647 / false 5340)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 127m | 22/63-65/2286 | 64-64 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08ARZARC-ARC | 7 | 6m | 0 | 19-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08DELKUS-KUS | 9 | 2m | 25/14-16/435 | 15-11 | 5 | **FLOW_ABOVE** | 9 | flow above but bound 9c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 127m | 32/71-77/1184 | 73-75 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 127m | 3/42-45/46 | 42-45 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 127m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MILPLA-MIL | 75 | 7m | 6/98-98/39 | 82-98 | 23 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08MUJBEL-MUJ | 39 | 6m | 1/39-39/9 | 39-41 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL09BORPAP-PAP | 28 | 7m | 0 | 28-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THIJER-JER | 79 | 6m | 0 | 79-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THIJER-THI | 17 | 6m | 0 | 17-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 127m | 2/32-32/299 | 31-32 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→32 |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 127m | 13/69-69/295 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL08LUENAT-NAT | 14 | 6m | 0 | 15-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NAKMAL-NAK | 74 | 4m | 0 | 76-79 | — | **NO_FLOW** | 74 |  |
| ITFWMATCH-26JUL08SHE2WAN2-SHE2 | 41 | 2m | 30/42-48/2747 | 48-42 | 1 | **FLOW_ABOVE** | 41 | flow above but bound 41c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08STEJIA-JIA | 79 | 2m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08STEJIA-STE | 18 | 2m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 127m | 597/13-99/62842 | 99-13 | 1 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09AHLMAK-AHL | 31 | 97m | 8/34-34/562 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL09AHLMAK-MAK | 66 | 97m | 2/69-69/0 | 66-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL09BOSGOL-BOS | 48 | 62m | 1/52-52/279 | 48-52 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ITFWMATCH-26JUL09BOSGOL-GOL | 47 | 67m | 0 | 47-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-BER | 73 | 14m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-CEU | 25 | 37m | 0 | 25-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DESYOD-DES | 36 | 6m | 0 | 36-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KORSAG-KOR | 27 | 6m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KORSAG-SAG | 69 | 6m | 0 | 69-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-ALL | 73 | 14m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-MAI | 25 | 37m | 0 | 25-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAMJAN-JAN | 43 | 20m | 0 | 43-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MATDYU-DYU | 11 | 4m | 0 | 11-12 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09ROSHRU-HRU | 94 | 25m | 0 | 94-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09ROSHRU-ROS | 5 | 37m | 2/5-5/5 | 5-6 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SEDKRO-KRO | 90 | 97m | 2/92-92/1 | 90-92 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFWMATCH-26JUL09SEDKRO-SED | 8 | 97m | 24/9-10/1636 | 8-9 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFWMATCH-26JUL09SHONIS-NIS | 11 | 97m | 7/11-12/108 | 11-12 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-SHO | 87 | 97m | 1/89-89/0 | 87-89 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| ITFWMATCH-26JUL09TUPNUP-TUP | 92 | 97m | 2/92-95/10 | 92-94 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 127m | 4/63-64/178 | 62-63 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08OCHSAM | 12 | 44 | **56** | 97 | -41 |
| ITFMATCH-26JUL08TAKJAS | 43 | 33 | **76** | 97 | -21 |
| ITFWMATCH-26JUL08WANLEO | 85 | 13 | **98** | 97 | +1 |
| ITFWMATCH-26JUL08SHE2WAN2 | 56 | 42 | **98** | 97 | +1 |
| ITFMATCH-26JUL08DELKUS | 88 | 11 | **99** | 97 | +2 |
| ITFWMATCH-26JUL08NAKMAL | 23 | 79 | **102** | 97 | +5 |

## FLOW-STATE — 38 tracked game(s) ({'WAKING': 32, 'OPEN': 6}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.233 | 2 | **OPEN** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 1.867 | 1 | **OPEN** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.233 | 1 | **OPEN** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.233 | 3 | **OPEN** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.867 | 1 | **OPEN** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 0.267 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.033 | — | **WAKING** |
| ITFMATCH-26JUL08ARZARC | ITF_M | 0.067 | 3 | **WAKING** |
| ITFMATCH-26JUL08DELKUS | ITF_M | 12.767 | — | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 1.433 | — | **WAKING** |
| ITFMATCH-26JUL08MILPLA | ITF_M | 0.2 | 15 | **WAKING** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 8.167 | — | **WAKING** |
| ITFMATCH-26JUL08MUJBEL | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 91.633 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 45.4 | — | **WAKING** |
| ITFMATCH-26JUL09BORPAP | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09THIJER | ITF_M | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL08LUENAT | ITF_W | 0.367 | 4 | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 35.6 | — | **WAKING** |
| ITFWMATCH-26JUL08SHE2WAN2 | ITF_W | 4.1 | — | **WAKING** |
| ITFWMATCH-26JUL08STEJIA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 44.733 | — | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 18.667 | — | **WAKING** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.033 | — | **WAKING** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09BOSGOL | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09CEUBER | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL09DESYOD | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09KORSAG | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09MAIALL | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 0.1 | 3 | **WAKING** |
| ITFWMATCH-26JUL09MATDYU | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL09ROSHRU | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.1 | 1 | **WAKING** |

## PATTERNS (sub-B) — 17
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 43, "conception_ts": 1783566007.7132218, "detail": "buy 43c predates the conception stamp by 120min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-08 11:07:12 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 42, "conception_ts": 1783566007.7132218, "detail": "buy 42c predates the conception stamp by 120min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-08 11:07:12 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 118min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-08 11:07:12 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 116min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-08 11:07:12 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 111min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-08 11:07:12 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 109min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-08 11:07:12 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 107min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-08 11:07:12 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL08DELKUS-DEL {"fill": 88, "age_min": 114, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 106min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-08 11:07:12 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 104min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-08 11:07:12 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 41, "conception_ts": 1783566007.7132218, "detail": "buy 41c predates the conception stamp by 102min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-08 11:07:12 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL08TAKJAS-TAK {"price": 43, "conception_ts": 1783566007.7132218, "detail": "buy 43c predates the conception stamp by 100min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-08 11:07:12 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL08OCHSAM-OCH {"fill": 12, "age_min": 107, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08TAKJAS-TAK {"fill": 43, "age_min": 105, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08NAKMAL-MAL {"fill": 23, "age_min": 79, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL08WANLEO-WAN {"fill": 85, "age_min": 77, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL08SHE2WAN2-WAN2 {"fill": 56, "age_min": 55, "mode": "SET_BELOW_FLOW(prints 1c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
