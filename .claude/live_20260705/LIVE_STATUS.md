# LIVE VALIDATION — rolling status

- cycle 51 @ **2026-07-08 10:56:47 PM ET** | build `99531bc` | session boot 07-08 20:59 ET | log `live_v3_20260708.jsonl` | 9131 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 20 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:13 | ITFMATCH-26JUL08DELKUS-DEL | ITF_M | leader | 88 | 85 | +3 (place_cell) | — | pre | single |  | PENDING |
| 21:20 | ITFMATCH-26JUL08OCHSAM-OCH | ITF_M | ? | 12 | 8 | +4 (fill_est) | — | pre | single |  | PENDING |
| 21:22 | ITFMATCH-26JUL08TAKJAS-TAK | ITF_M | ? | 43 | 39 | +4 (fill_est) | — | pre | single |  | PENDING |
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

## RESTING BIDS — 27 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 4, 'FLOW_ABOVE': 15, 'NO_FLOW': 8} | repriceable now: true 10 / false 17 | **cumulative bid_grade lines: 5971 (repriceable true 647 / false 5324)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 117m | 21/63-65/2271 | 64-64 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08DELKUS-KUS | 8 | 102m | 211/10-18/9918 | 12-12 | 2 | **FLOW_ABOVE** | 9 | REPRICEABLE→9 |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 117m | 32/71-77/1184 | 73-75 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 117m | 2/45-45/36 | 42-45 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 116m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 117m | 2/32-32/299 | 31-32 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→32 |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 117m | 10/69-69/263 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL08NAKMAL-NAK | 72 | 68m | 3/79-80/41 | 76-79 | 7 | **FLOW_ABOVE** | 74 | flow above but bound 74c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08SHE2WAN2-SHE2 | 40 | 42m | 21/45-46/621 | 45-44 | 5 | **FLOW_ABOVE** | 41 | flow above but bound 41c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 116m | 597/13-99/62842 | 99-13 | 1 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09AHLMAK-AHL | 31 | 86m | 8/34-34/562 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL09AHLMAK-MAK | 66 | 86m | 2/69-69/0 | 66-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL09BOSGOL-BOS | 48 | 51m | 1/52-52/279 | 48-52 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ITFWMATCH-26JUL09BOSGOL-GOL | 47 | 56m | 0 | 47-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-BER | 73 | 4m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-CEU | 25 | 26m | 0 | 25-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-ALL | 73 | 4m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-MAI | 25 | 26m | 0 | 25-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAMJAN-JAN | 43 | 9m | 0 | 43-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09ROSHRU-HRU | 94 | 15m | 0 | 94-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09ROSHRU-ROS | 5 | 26m | 2/5-5/5 | 5-6 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SEDKRO-KRO | 90 | 86m | 2/92-92/1 | 90-92 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFWMATCH-26JUL09SEDKRO-SED | 8 | 86m | 17/9-10/979 | 8-9 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFWMATCH-26JUL09SHONIS-NIS | 11 | 86m | 7/11-12/108 | 11-12 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-SHO | 87 | 86m | 1/89-89/0 | 87-89 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| ITFWMATCH-26JUL09TUPNUP-TUP | 92 | 86m | 2/92-95/10 | 92-94 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 117m | 3/63-64/130 | 62-63 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08WANLEO | 85 | 13 | **98** | 97 | +1 |
| ITFMATCH-26JUL08DELKUS | 88 | 12 | **100** | 97 | +3 |
| ITFWMATCH-26JUL08SHE2WAN2 | 56 | 44 | **100** | 97 | +3 |
| ITFWMATCH-26JUL08NAKMAL | 23 | 79 | **102** | 97 | +5 |

## FLOW-STATE — 28 tracked game(s) ({'WAKING': 20, 'OPEN': 8}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | ITF_M | 4.567 | 1 | **OPEN** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.267 | 2 | **OPEN** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 1.933 | 1 | **OPEN** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 1.967 | 1 | **OPEN** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.267 | 1 | **OPEN** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.267 | 3 | **OPEN** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.933 | 1 | **OPEN** |
| ITFWMATCH-26JUL09ROSHRU | ITF_W | 0.267 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.033 | — | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.067 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 5.233 | — | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 111.733 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 37.967 | — | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 23.933 | — | **WAKING** |
| ITFWMATCH-26JUL08SHE2WAN2 | ITF_W | 1.6 | — | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 20.933 | — | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 15.3 | — | **WAKING** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 17.3 | — | **WAKING** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL09BOSGOL | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09CEUBER | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL09MAIALL | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 0.133 | 3 | **WAKING** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 0.067 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.067 | 1 | **WAKING** |

## PATTERNS (sub-B) — 6
- half_arm_aging: KXITFMATCH-26JUL08DELKUS-DEL {"fill": 88, "age_min": 103, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFMATCH-26JUL08OCHSAM-OCH {"fill": 12, "age_min": 96, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08TAKJAS-TAK {"fill": 43, "age_min": 94, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08NAKMAL-MAL {"fill": 23, "age_min": 68, "mode": "SET_BELOW_FLOW(prints 7c above)"}
- half_arm_aging: KXITFWMATCH-26JUL08WANLEO-WAN {"fill": 85, "age_min": 67, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL08SHE2WAN2-WAN2 {"fill": 56, "age_min": 44, "mode": "SET_BELOW_FLOW(prints 5c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
