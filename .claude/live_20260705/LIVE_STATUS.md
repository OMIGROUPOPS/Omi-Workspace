# LIVE VALIDATION — rolling status

- cycle 38 @ **2026-07-08 08:43:23 PM ET** | build `f6490ec` | session boot 07-08 19:55 ET | log `live_v3_20260708.jsonl` | 2800 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 20:29 | ITFMATCH-26JUL08OCHSAM-SAM | ITF_M | leader | 85 | 82 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 29 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 17, 'NO_FLOW': 10, 'FLOW_AT_LEVEL': 2} | repriceable now: true 14 / false 15 | **cumulative bid_grade lines: 5868 (repriceable true 611 / false 5257)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 48m | 25/63-65/3117 | 63-64 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08DELKUS-KUS | 11 | 40m | 17/12-13/400 | 11-12 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→12 |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 48m | 4/75-75/107 | 73-75 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 47m | 2/53-54/350 | 53-54 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08HONNAK-NAK | 43 | 47m | 0 | 43-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 48m | 1/45-45/2 | 42-45 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 47m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 47m | 7/69-69/210 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 47m | 0 | 30-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 47m | 4/47-47/47 | 46-47 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL08MOCTAN-TAN | 53 | 6m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08OCHSAM-OCH | 12 | 9m | 99/17-28/5657 | 18-15 | 5 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08TAKJAS-JAS | 53 | 30m | 38/53-58/1298 | 53-56 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-TAK | 45 | 48m | 21/46-48/1111 | 45-47 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 47m | 1/33-33/1 | 31-32 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→33 |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 47m | 2/69-69/14 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL08NAKMAL-MAL | 23 | 47m | 1/24-24/1 | 23-24 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| ITFWMATCH-26JUL08NAKMAL-NAK | 76 | 47m | 0 | 76-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-KAL | 79 | 0m | 0 | 79-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 47m | 4/22-22/124 | 21-22 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL08SNINON-NON | 25 | 47m | 1/26-26/1 | 25-26 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFWMATCH-26JUL08SNINON-SNI | 74 | 47m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 47m | 1/20-20/20 | 19-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 47m | 2/80-80/3 | 77-80 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08TIKZHA-TIK | 72 | 15m | 1/73-73/9 | 72-73 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFWMATCH-26JUL08TIKZHA-ZHA | 26 | 20m | 0 | 26-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 47m | 14/13-13/335 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL08WANLEO-WAN | 85 | 47m | 0 | 85-88 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 48m | 0 | 62-65 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08OCHSAM | 85 | 15 | **100** | 97 | +3 |

## FLOW-STATE — 18 tracked game(s) ({'WAKING': 14, 'OPEN': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | ITF_M | 0.333 | 1 | **OPEN** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.2 | 2 | **OPEN** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 1.933 | 2 | **OPEN** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.2 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.267 | 1 | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.1 | 2 | **WAKING** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 7.6 | — | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 0.167 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.0 | 3 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
