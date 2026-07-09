# LIVE VALIDATION — rolling status

- cycle 45 @ **2026-07-08 09:54:49 PM ET** | build `0e6ec45` | session boot 07-08 20:59 ET | log `live_v3_20260708.jsonl` | 3745 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 5 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:13 | ITFMATCH-26JUL08DELKUS-DEL | ITF_M | leader | 88 | 85 | +3 (place_cell) | — | pre | single |  | PENDING |
| 21:20 | ITFMATCH-26JUL08OCHSAM-OCH | ITF_M | ? | 12 | 8 | +4 (fill_est) | — | pre | single |  | PENDING |
| 21:22 | ITFMATCH-26JUL08TAKJAS-TAK | ITF_M | ? | 43 | 39 | +4 (fill_est) | — | pre | single |  | PENDING |
| 21:48 | ITFWMATCH-26JUL08NAKMAL-MAL | ITF_W | underdog | 23 | 19 | +4 (place_cell) | — | pre | single |  | PENDING |
| 21:50 | ITFWMATCH-26JUL08WANLEO-WAN | ITF_W | leader | 85 | 83 | +2 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 35 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 4, 'FLOW_ABOVE': 21, 'NO_FLOW': 10} | repriceable now: true 17 / false 18 | **cumulative bid_grade lines: 5940 (repriceable true 641 / false 5299)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 55m | 15/63-65/2215 | 64-65 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08DELKUS-KUS | 8 | 40m | 40/11-14/2749 | 12-12 | 3 | **FLOW_ABOVE** | 9 | REPRICEABLE→9 |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 55m | 20/71-77/990 | 71-75 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 55m | 23/54-58/1973 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL08HONNAK-NAK | 45 | 5m | 0 | 45-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 55m | 0 | 42-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 55m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 55m | 12/68-69/199 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 55m | 4/31-32/302 | 31-31 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→31 |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 55m | 2/46-47/26 | 46-47 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08MOCTAN-TAN | 53 | 55m | 8/55-55/144 | 53-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 55m | 3/16-21/27 | 6-17 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 55m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 55m | 3/69-69/54 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL08NAKMAL-NAK | 72 | 6m | 0 | 76-80 | — | **NO_FLOW** | 74 |  |
| ITFWMATCH-26JUL08RUOKAL-KAL | 79 | 55m | 4/80-80/14 | 79-80 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 55m | 15/22-22/329 | 21-22 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL08SHE2WAN2-SHE2 | 42 | 22m | 0 | 42-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHE2WAN2-WAN2 | 56 | 53m | 12/56-59/714 | 56-57 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL08SNINON-NON | 25 | 55m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SNINON-SNI | 74 | 55m | 6/78-78/28 | 74-75 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 55m | 9/20-21/492 | 19-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 55m | 4/80-80/245 | 77-80 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08TIKZHA-TIK | 72 | 52m | 3/74-74/7 | 72-74 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ITFWMATCH-26JUL08TIKZHA-ZHA | 26 | 32m | 4/29-30/38 | 26-29 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 55m | 57/13-23/1811 | 14-13 | 1 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09AHLMAK-AHL | 31 | 24m | 1/34-34/1 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL09AHLMAK-MAK | 66 | 24m | 1/69-69/0 | 66-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL09MAMJAN-JAN | 41 | 24m | 0 | 41-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SEDKRO-KRO | 90 | 24m | 1/92-92/1 | 90-92 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFWMATCH-26JUL09SEDKRO-SED | 8 | 24m | 3/9-10/150 | 8-9 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFWMATCH-26JUL09SHONIS-NIS | 11 | 24m | 3/11-12/42 | 11-12 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-SHO | 87 | 24m | 0 | 87-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09TUPNUP-TUP | 92 | 24m | 0 | 92-95 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 55m | 1/64-64/4 | 62-63 | 5 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08WANLEO | 85 | 13 | **98** | 97 | +1 |
| ITFMATCH-26JUL08DELKUS | 88 | 12 | **100** | 97 | +3 |
| ITFWMATCH-26JUL08NAKMAL | 23 | 80 | **103** | 97 | +6 |

## FLOW-STATE — 25 tracked game(s) ({'WAKING': 19, 'OPEN': 6}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | ITF_M | 1.433 | 1 | **OPEN** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 1.067 | 1 | **OPEN** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.467 | 1 | **OPEN** |
| ITFWMATCH-26JUL08SHE2WAN2 | ITF_W | 0.267 | 1 | **OPEN** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.4 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.267 | 1 | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.5 | 4 | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 74.767 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 41.067 | — | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.033 | 11 | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.1 | 3 | **WAKING** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 0.167 | 2 | **WAKING** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 1.6 | — | **WAKING** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 0.067 | 3 | **WAKING** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 0.0 | 3 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 3
- half_arm_aging: KXITFMATCH-26JUL08DELKUS-DEL {"fill": 88, "age_min": 41, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFMATCH-26JUL08OCHSAM-OCH {"fill": 12, "age_min": 34, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 09:54:49 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL08TAKJAS-TAK {"fill": 43, "age_min": 33, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 09:54:49 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
