# LIVE VALIDATION — rolling status

- cycle 49 @ **2026-07-08 10:35:45 PM ET** | build `6efffff` | session boot 07-08 20:59 ET | log `live_v3_20260708.jsonl` | 7514 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 12 graded (session)
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

## RESTING BIDS — 35 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 6, 'FLOW_ABOVE': 21, 'NO_FLOW': 8} | repriceable now: true 15 / false 20 | **cumulative bid_grade lines: 5963 (repriceable true 646 / false 5317)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 96m | 21/63-65/2271 | 64-64 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08DELKUS-KUS | 8 | 81m | 126/10-18/4027 | 12-12 | 2 | **FLOW_ABOVE** | 9 | REPRICEABLE→9 |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 96m | 25/71-77/1024 | 71-75 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 96m | 35/54-59/2272 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL08HONNAK-NAK | 45 | 46m | 13/45-51/157 | 46-46 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 96m | 2/45-45/36 | 42-45 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 96m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 96m | 27/68-79/373 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 96m | 20/31-36/680 | 30-31 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→31 |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 96m | 11/46-49/442 | 47-47 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08MOCTAN-TAN | 53 | 96m | 19/55-57/557 | 53-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 96m | 1/32-32/1 | 31-32 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→32 |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 96m | 5/69-69/82 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL08NAKMAL-NAK | 72 | 47m | 1/79-79/0 | 76-79 | 7 | **FLOW_ABOVE** | 74 | flow above but bound 74c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08SHE2WAN2-SHE2 | 40 | 21m | 3/45-46/110 | 45-44 | 5 | **FLOW_ABOVE** | 41 | flow above but bound 41c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08SNINON-NON | 25 | 96m | 12/26-36/2867 | 25-26 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFWMATCH-26JUL08SNINON-SNI | 74 | 96m | 12/75-78/115 | 74-75 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 96m | 583/13-99/60092 | 99-13 | 1 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09AHLMAK-AHL | 31 | 65m | 8/34-34/562 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL09AHLMAK-MAK | 66 | 65m | 1/69-69/0 | 66-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL09BOSGOL-BOS | 48 | 30m | 1/52-52/279 | 48-52 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ITFWMATCH-26JUL09BOSGOL-GOL | 47 | 35m | 0 | 47-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-BER | 69 | 5m | 0 | 69-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-CEU | 25 | 5m | 0 | 25-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-ALL | 72 | 0m | 0 | 72-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-MAI | 25 | 5m | 0 | 25-28 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAMJAN-JAN | 42 | 30m | 1/46-46/41 | 42-46 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL09ROSHRU-HRU | 93 | 5m | 1/93-93/12 | 93-95 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09ROSHRU-ROS | 5 | 5m | 0 | 5-6 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SEDKRO-KRO | 90 | 65m | 2/92-92/1 | 90-92 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFWMATCH-26JUL09SEDKRO-SED | 8 | 65m | 15/9-10/943 | 8-9 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFWMATCH-26JUL09SHONIS-NIS | 11 | 65m | 5/11-12/64 | 11-12 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-SHO | 87 | 65m | 0 | 87-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09TUPNUP-TUP | 92 | 65m | 2/92-95/10 | 92-95 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 96m | 1/64-64/4 | 62-63 | 5 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08WANLEO | 85 | 13 | **98** | 97 | +1 |
| ITFMATCH-26JUL08DELKUS | 88 | 12 | **100** | 97 | +3 |
| ITFWMATCH-26JUL08SHE2WAN2 | 56 | 44 | **100** | 97 | +3 |
| ITFWMATCH-26JUL08NAKMAL | 23 | 79 | **102** | 97 | +5 |

## FLOW-STATE — 28 tracked game(s) ({'WAKING': 21, 'OPEN': 7}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | ITF_M | 2.567 | 1 | **OPEN** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.8 | 1 | **OPEN** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.967 | 1 | **OPEN** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.633 | 2 | **OPEN** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.6 | 1 | **OPEN** |
| ITFWMATCH-26JUL09ROSHRU | ITF_W | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 0.433 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.2 | — | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.167 | 4 | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.067 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 106.467 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 31.1 | — | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.1 | 3 | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 7.167 | — | **WAKING** |
| ITFWMATCH-26JUL08SHE2WAN2 | ITF_W | 0.667 | — | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 12.2 | — | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 7.967 | — | **WAKING** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 21.133 | — | **WAKING** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09BOSGOL | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL09CEUBER | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL09MAIALL | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 0.067 | 3 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 5
- half_arm_aging: KXITFMATCH-26JUL08DELKUS-DEL {"fill": 88, "age_min": 82, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFMATCH-26JUL08OCHSAM-OCH {"fill": 12, "age_min": 75, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08TAKJAS-TAK {"fill": 43, "age_min": 73, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08NAKMAL-MAL {"fill": 23, "age_min": 47, "mode": "SET_BELOW_FLOW(prints 7c above)"}
- half_arm_aging: KXITFWMATCH-26JUL08WANLEO-WAN {"fill": 85, "age_min": 46, "mode": "SET_BELOW_FLOW(prints 1c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
