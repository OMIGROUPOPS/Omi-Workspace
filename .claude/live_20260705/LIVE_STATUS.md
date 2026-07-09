# LIVE VALIDATION — rolling status

- cycle 41 @ **2026-07-08 09:13:52 PM ET** | build `7da4949` | session boot 07-08 20:59 ET | log `live_v3_20260708.jsonl` | 2428 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:13 | ITFMATCH-26JUL08DELKUS-DEL | ITF_M | leader | 88 | 85 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 29 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 15, 'NO_FLOW': 12, 'FLOW_AT_LEVEL': 2} | repriceable now: true 10 / false 19 | **cumulative bid_grade lines: 5912 (repriceable true 628 / false 5284)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 14m | 2/63-64/16 | 63-64 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08DELKUS-KUS | 9 | 0m | 0 | 11-12 | — | **NO_FLOW** | 9 |  |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 14m | 1/75-75/5 | 73-75 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 14m | 3/54-54/53 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL08HONNAK-NAK | 43 | 14m | 3/46-46/112 | 43-46 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 14m | 0 | 42-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 14m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 14m | 3/69-69/53 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 14m | 0 | 30-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 14m | 1/46-46/6 | 46-47 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08MOCTAN-TAN | 53 | 14m | 3/55-55/62 | 53-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL08OCHSAM-OCH | 12 | 14m | 386/17-51/14690 | 31-18 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-TAK | 41 | 1m | 5/47-51/83 | 47-46 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 14m | 2/16-17/25 | 6-17 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 14m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 14m | 2/69-69/53 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL08NAKMAL-MAL | 23 | 14m | 0 | 23-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NAKMAL-NAK | 76 | 14m | 0 | 76-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-KAL | 79 | 14m | 1/80-80/2 | 79-80 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 14m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHE2WAN2-WAN2 | 56 | 12m | 1/59-59/16 | 56-59 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFWMATCH-26JUL08SNINON-NON | 25 | 14m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SNINON-SNI | 74 | 14m | 3/78-78/25 | 74-78 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 14m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 14m | 0 | 77-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TIKZHA-TIK | 72 | 11m | 0 | 72-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 14m | 7/13-13/451 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL08WANLEO-WAN | 85 | 14m | 5/85-88/38 | 85-88 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 14m | 1/64-64/4 | 62-64 | 5 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | 88 | 12 | **100** | 97 | +3 |

## FLOW-STATE — 20 tracked game(s) ({'WAKING': 15, 'OPEN': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | ITF_M | 1.433 | 1 | **OPEN** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.367 | 1 | **OPEN** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.3 | 1 | **OPEN** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.867 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.167 | 2 | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 22.0 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 2.267 | — | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.1 | 11 | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SHE2WAN2 | ITF_W | 0.1 | 3 | **WAKING** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 0.067 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.033 | 2 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
