# LIVE VALIDATION — rolling status

- cycle 42 @ **2026-07-08 09:24:02 PM ET** | build `e68992b` | session boot 07-08 20:59 ET | log `live_v3_20260708.jsonl` | 2875 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:13 | ITFMATCH-26JUL08DELKUS-DEL | ITF_M | leader | 88 | 85 | +3 (place_cell) | — | pre | single |  | PENDING |
| 21:20 | ITFMATCH-26JUL08OCHSAM-OCH | ITF_M | ? | 12 | 8 | +4 (fill_est) | — | pre | single |  | PENDING |
| 21:22 | ITFMATCH-26JUL08TAKJAS-TAK | ITF_M | ? | 43 | 39 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 29 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 19, 'NO_FLOW': 6, 'FLOW_AT_LEVEL': 4} | repriceable now: true 16 / false 13 | **cumulative bid_grade lines: 5921 (repriceable true 635 / false 5286)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 24m | 7/63-64/560 | 63-64 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08DELKUS-KUS | 8 | 9m | 7/12-13/171 | 12-12 | 4 | **FLOW_ABOVE** | 9 | REPRICEABLE→9 |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 24m | 5/73-75/40 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 24m | 3/54-54/53 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL08HONNAK-NAK | 43 | 24m | 7/46-47/316 | 43-46 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 24m | 0 | 42-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 24m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 24m | 4/69-69/54 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 24m | 3/31-32/301 | 30-31 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→31 |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 24m | 1/46-46/6 | 46-47 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08MOCTAN-TAN | 53 | 24m | 5/55-55/62 | 53-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 24m | 2/16-17/25 | 6-17 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 24m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 24m | 2/69-69/53 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL08NAKMAL-MAL | 23 | 24m | 1/24-24/3 | 23-24 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| ITFWMATCH-26JUL08NAKMAL-NAK | 76 | 24m | 0 | 76-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-KAL | 79 | 24m | 1/80-80/2 | 79-80 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 24m | 3/22-22/32 | 21-22 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL08SHE2WAN2-SHE2 | 41 | 9m | 1/41-41/0 | 41-44 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL08SHE2WAN2-WAN2 | 56 | 22m | 4/56-59/206 | 56-59 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL08SNINON-NON | 25 | 24m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SNINON-SNI | 74 | 24m | 4/78-78/27 | 74-78 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 24m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 24m | 1/80-80/0 | 77-80 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08TIKZHA-TIK | 72 | 21m | 1/74-74/6 | 72-74 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ITFWMATCH-26JUL08TIKZHA-ZHA | 26 | 1m | 1/30-30/1 | 26-30 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→30 |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 24m | 16/13-13/643 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL08WANLEO-WAN | 85 | 24m | 7/85-88/50 | 85-88 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 24m | 1/64-64/4 | 62-64 | 5 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | 88 | 12 | **100** | 97 | +3 |

## FLOW-STATE — 20 tracked game(s) ({'WAKING': 13, 'OPEN': 7}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | ITF_M | 1.433 | 2 | **OPEN** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.4 | 1 | **OPEN** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.367 | 1 | **OPEN** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.233 | 1 | **OPEN** |
| ITFWMATCH-26JUL08SHE2WAN2 | ITF_W | 0.367 | 3 | **OPEN** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.933 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.267 | 1 | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.167 | 2 | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 29.933 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 10.5 | — | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.1 | 11 | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 0.167 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.033 | 2 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
