# LIVE VALIDATION — rolling status

- cycle 43 @ **2026-07-08 09:34:21 PM ET** | build `a13b1ad` | session boot 07-08 20:59 ET | log `live_v3_20260708.jsonl` | 3289 session events | monitor READ-ONLY
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
- classes now: {'FLOW_ABOVE': 20, 'NO_FLOW': 14, 'FLOW_AT_LEVEL': 3} | repriceable now: true 17 / false 20 | **cumulative bid_grade lines: 5932 (repriceable true 637 / false 5295)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 34m | 7/63-64/560 | 63-64 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08DELKUS-KUS | 8 | 20m | 12/12-13/1135 | 12-12 | 4 | **FLOW_ABOVE** | 9 | REPRICEABLE→9 |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 34m | 5/73-75/40 | 71-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 34m | 3/54-54/53 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL08HONNAK-NAK | 44 | 3m | 0 | 44-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 34m | 0 | 42-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 34m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 34m | 10/68-69/198 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 34m | 4/31-32/302 | 31-31 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→31 |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 34m | 1/46-46/6 | 46-47 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08MOCTAN-TAN | 53 | 34m | 5/55-55/62 | 53-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 34m | 2/16-17/25 | 6-17 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 34m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 34m | 3/69-69/54 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL08NAKMAL-MAL | 23 | 34m | 1/24-24/3 | 23-24 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| ITFWMATCH-26JUL08NAKMAL-NAK | 76 | 34m | 0 | 76-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-KAL | 79 | 34m | 3/80-80/12 | 79-80 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 34m | 4/22-22/53 | 21-22 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL08SHE2WAN2-SHE2 | 42 | 1m | 0 | 42-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHE2WAN2-WAN2 | 56 | 32m | 6/56-59/207 | 56-57 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL08SNINON-NON | 25 | 34m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SNINON-SNI | 74 | 34m | 6/78-78/28 | 74-75 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 34m | 5/20-21/444 | 19-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 34m | 1/80-80/0 | 77-80 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08TIKZHA-TIK | 72 | 32m | 3/74-74/7 | 72-74 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ITFWMATCH-26JUL08TIKZHA-ZHA | 26 | 11m | 2/30-30/32 | 26-30 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→30 |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 34m | 23/13-14/843 | 13-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL08WANLEO-WAN | 85 | 34m | 11/85-88/64 | 85-88 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09AHLMAK-AHL | 31 | 4m | 1/34-34/1 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL09AHLMAK-MAK | 66 | 4m | 0 | 66-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAMJAN-JAN | 41 | 4m | 0 | 41-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SEDKRO-KRO | 90 | 4m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SEDKRO-SED | 8 | 4m | 0 | 8-9 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-NIS | 11 | 4m | 0 | 11-12 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-SHO | 87 | 4m | 0 | 87-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09TUPNUP-TUP | 92 | 4m | 0 | 92-95 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 34m | 1/64-64/4 | 62-64 | 5 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | 88 | 12 | **100** | 97 | +3 |

## FLOW-STATE — 25 tracked game(s) ({'WAKING': 14, 'OPEN': 10, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | ITF_M | 1.267 | 1 | **OPEN** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.233 | 1 | **OPEN** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.367 | 1 | **OPEN** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.233 | 1 | **OPEN** |
| ITFWMATCH-26JUL08SHE2WAN2 | ITF_W | 0.367 | 1 | **OPEN** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 0.2 | 2 | **OPEN** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 1.067 | 3 | **OPEN** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 0.267 | 1 | **OPEN** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.0 | 11 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.133 | 4 | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 44.233 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 19.933 | — | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 0.1 | 3 | **WAKING** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 0.0 | 3 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.033 | 2 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
