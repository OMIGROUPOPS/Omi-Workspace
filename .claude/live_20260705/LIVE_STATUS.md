# LIVE VALIDATION — rolling status

- cycle 44 @ **2026-07-08 09:44:39 PM ET** | build `8ef1c44` | session boot 07-08 20:59 ET | log `live_v3_20260708.jsonl` | 3551 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:13 | ITFMATCH-26JUL08DELKUS-DEL | ITF_M | leader | 88 | 85 | +3 (place_cell) | — | pre | single |  | PENDING |
| 21:20 | ITFMATCH-26JUL08OCHSAM-OCH | ITF_M | ? | 12 | 8 | +4 (fill_est) | — | pre | single |  | PENDING |
| 21:22 | ITFMATCH-26JUL08TAKJAS-TAK | ITF_M | ? | 43 | 39 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 37 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 23, 'NO_FLOW': 10, 'FLOW_AT_LEVEL': 4} | repriceable now: true 20 / false 17 | **cumulative bid_grade lines: 5936 (repriceable true 640 / false 5296)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 45m | 10/63-65/2177 | 64-65 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08DELKUS-KUS | 8 | 30m | 28/12-14/2164 | 12-12 | 4 | **FLOW_ABOVE** | 9 | REPRICEABLE→9 |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 45m | 6/73-75/43 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 45m | 6/54-54/115 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL08HONNAK-NAK | 44 | 13m | 2/47-47/92 | 44-46 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 45m | 0 | 42-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 44m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 45m | 10/68-69/198 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 45m | 4/31-32/302 | 31-31 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→31 |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 44m | 2/46-47/26 | 46-47 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08MOCTAN-TAN | 53 | 44m | 8/55-55/144 | 53-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 45m | 3/16-21/27 | 6-17 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 45m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 45m | 3/69-69/54 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL08NAKMAL-MAL | 23 | 44m | 1/24-24/3 | 23-24 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| ITFWMATCH-26JUL08NAKMAL-NAK | 76 | 45m | 0 | 76-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-KAL | 79 | 44m | 4/80-80/14 | 79-80 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 44m | 5/22-22/55 | 21-22 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL08SHE2WAN2-SHE2 | 42 | 11m | 0 | 42-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHE2WAN2-WAN2 | 56 | 42m | 7/56-59/212 | 56-57 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL08SNINON-NON | 25 | 45m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SNINON-SNI | 74 | 45m | 6/78-78/28 | 74-75 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 45m | 8/20-21/492 | 19-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 45m | 1/80-80/0 | 77-80 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08TIKZHA-TIK | 72 | 42m | 3/74-74/7 | 72-74 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ITFWMATCH-26JUL08TIKZHA-ZHA | 26 | 22m | 2/30-30/32 | 26-30 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→30 |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 44m | 36/13-16/1187 | 13-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL08WANLEO-WAN | 85 | 45m | 13/85-88/74 | 85-88 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09AHLMAK-AHL | 31 | 14m | 1/34-34/1 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL09AHLMAK-MAK | 66 | 14m | 1/69-69/0 | 66-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL09MAMJAN-JAN | 41 | 14m | 0 | 41-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SEDKRO-KRO | 90 | 14m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SEDKRO-SED | 8 | 14m | 2/10-10/98 | 8-9 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL09SHONIS-NIS | 11 | 14m | 3/11-12/42 | 11-12 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-SHO | 87 | 14m | 0 | 87-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09TUPNUP-TUP | 92 | 14m | 0 | 92-95 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 45m | 1/64-64/4 | 62-63 | 5 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | 88 | 12 | **100** | 97 | +3 |

## FLOW-STATE — 25 tracked game(s) ({'WAKING': 16, 'OPEN': 9}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | ITF_M | 1.167 | 1 | **OPEN** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.3 | 1 | **OPEN** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.367 | 1 | **OPEN** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.267 | 1 | **OPEN** |
| ITFWMATCH-26JUL08SHE2WAN2 | ITF_W | 0.233 | 1 | **OPEN** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 0.2 | 2 | **OPEN** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 1.167 | 3 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.267 | 1 | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.167 | 2 | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 65.9 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 29.367 | — | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.033 | 11 | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 0.1 | 3 | **WAKING** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 0.0 | 3 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXITFMATCH-26JUL08DELKUS-DEL {"fill": 88, "age_min": 31, "mode": "SET_BELOW_FLOW(prints 4c above)", "emitted_et": "2026-07-08 09:44:39 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
