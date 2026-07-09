# LIVE VALIDATION — rolling status

- cycle 47 @ **2026-07-08 10:15:21 PM ET** | build `2f17d59` | session boot 07-08 20:59 ET | log `live_v3_20260708.jsonl` | 5909 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 9 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:13 | ITFMATCH-26JUL08DELKUS-DEL | ITF_M | leader | 88 | 85 | +3 (place_cell) | — | pre | single |  | PENDING |
| 21:20 | ITFMATCH-26JUL08OCHSAM-OCH | ITF_M | ? | 12 | 8 | +4 (fill_est) | — | pre | single |  | PENDING |
| 21:22 | ITFMATCH-26JUL08TAKJAS-TAK | ITF_M | ? | 43 | 39 | +4 (fill_est) | — | pre | single |  | PENDING |
| 21:48 | ITFWMATCH-26JUL08NAKMAL-MAL | ITF_W | underdog | 23 | 19 | +4 (place_cell) | — | pre | single |  | PENDING |
| 21:50 | ITFWMATCH-26JUL08WANLEO-WAN | ITF_W | leader | 85 | 83 | +2 (place_cell) | — | pre | single |  | PENDING |
| 21:56 | ITFWMATCH-26JUL08TIKZHA-TIK | ITF_W | leader | 72 | 72 | +0 (place_cell) | — | pre | single |  | PENDING |
| 22:09 | ITFWMATCH-26JUL08RUOKAL-KAL | ITF_W | leader | 79 | 77 | +2 (place_cell) | — | pre | single |  | PENDING |
| 22:11 | ITFWMATCH-26JUL08SUNCHO-SUN | ITF_W | leader | 79 | 75 | +4 (place_cell) | — | pre | single |  | PENDING |
| 22:12 | ITFWMATCH-26JUL08SHE2WAN2-WAN2 | ITF_W | leader | 56 | 57 | -1 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 33 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 4, 'FLOW_ABOVE': 19, 'NO_FLOW': 10} | repriceable now: true 12 / false 21 | **cumulative bid_grade lines: 5950 (repriceable true 643 / false 5307)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 75m | 16/63-65/2225 | 64-65 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08DELKUS-KUS | 8 | 61m | 75/11-17/3436 | 12-12 | 3 | **FLOW_ABOVE** | 9 | REPRICEABLE→9 |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 75m | 22/71-77/1004 | 71-75 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 75m | 25/54-58/2004 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL08HONNAK-NAK | 45 | 25m | 7/45-51/87 | 46-46 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 75m | 0 | 42-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 75m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 75m | 12/68-69/199 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 75m | 8/31-32/370 | 30-31 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→31 |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 75m | 4/46-47/57 | 46-47 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08MOCTAN-TAN | 53 | 75m | 9/55-55/179 | 53-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 75m | 19/10-21/397 | 18-17 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 75m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 75m | 3/69-69/54 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL08NAKMAL-NAK | 72 | 27m | 0 | 76-79 | — | **NO_FLOW** | 74 |  |
| ITFWMATCH-26JUL08RUOKAL-RUO | 18 | 2m | 7/23-26/219 | 21-22 | 5 | **FLOW_ABOVE** | 18 | flow above but bound 18c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08SHE2WAN2-SHE2 | 40 | 1m | 0 | 45-44 | — | **NO_FLOW** | 41 |  |
| ITFWMATCH-26JUL08SNINON-NON | 25 | 75m | 12/26-36/2867 | 25-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFWMATCH-26JUL08SNINON-SNI | 74 | 75m | 7/75-78/41 | 74-75 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| ITFWMATCH-26JUL08SUNCHO-CHO | 18 | 2m | 28/20-27/867 | 24-20 | 2 | **FLOW_ABOVE** | 18 | flow above but bound 18c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08TIKZHA-ZHA | 25 | 2m | 10/30-33/154 | 29-29 | 5 | **FLOW_ABOVE** | 25 | flow above but bound 25c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 75m | 72/13-24/2053 | 22-13 | 1 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09AHLMAK-AHL | 31 | 45m | 8/34-34/562 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL09AHLMAK-MAK | 66 | 45m | 1/69-69/0 | 66-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL09BOSGOL-BOS | 48 | 10m | 0 | 48-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09BOSGOL-GOL | 47 | 15m | 0 | 47-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAMJAN-JAN | 42 | 10m | 0 | 42-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SEDKRO-KRO | 90 | 45m | 1/92-92/1 | 90-92 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFWMATCH-26JUL09SEDKRO-SED | 8 | 45m | 9/9-10/739 | 8-9 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFWMATCH-26JUL09SHONIS-NIS | 11 | 45m | 3/11-12/42 | 11-12 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-SHO | 87 | 45m | 0 | 87-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09TUPNUP-TUP | 92 | 45m | 0 | 92-95 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 75m | 1/64-64/4 | 62-63 | 5 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08WANLEO | 85 | 13 | **98** | 97 | +1 |
| ITFWMATCH-26JUL08SUNCHO | 79 | 20 | **99** | 97 | +2 |
| ITFMATCH-26JUL08DELKUS | 88 | 12 | **100** | 97 | +3 |
| ITFWMATCH-26JUL08SHE2WAN2 | 56 | 44 | **100** | 97 | +3 |
| ITFWMATCH-26JUL08TIKZHA | 72 | 29 | **101** | 97 | +4 |
| ITFWMATCH-26JUL08RUOKAL | 79 | 22 | **101** | 97 | +4 |
| ITFWMATCH-26JUL08NAKMAL | 23 | 79 | **102** | 97 | +5 |

## FLOW-STATE — 26 tracked game(s) ({'WAKING': 18, 'OPEN': 8}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | ITF_M | 1.767 | 1 | **OPEN** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 1.2 | 1 | **OPEN** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 1.067 | 1 | **OPEN** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.433 | 1 | **OPEN** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 1.767 | 1 | **OPEN** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 0.233 | 3 | **OPEN** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 0.267 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.533 | 4 | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 72.5 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 52.0 | — | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.533 | — | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.133 | 3 | **WAKING** |
| ITFWMATCH-26JUL08SHE2WAN2 | ITF_W | 0.667 | — | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 3.0 | — | **WAKING** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 1.6 | — | **WAKING** |
| ITFWMATCH-26JUL09BOSGOL | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 0.0 | 3 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 3
- half_arm_aging: KXITFMATCH-26JUL08DELKUS-DEL {"fill": 88, "age_min": 62, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFMATCH-26JUL08OCHSAM-OCH {"fill": 12, "age_min": 55, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08TAKJAS-TAK {"fill": 43, "age_min": 53, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
