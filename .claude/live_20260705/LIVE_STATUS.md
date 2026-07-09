# LIVE VALIDATION — rolling status

- cycle 39 @ **2026-07-08 08:53:31 PM ET** | build `8000ca6` | session boot 07-08 19:55 ET | log `live_v3_20260708.jsonl` | 2938 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 20:29 | ITFMATCH-26JUL08OCHSAM-SAM | ITF_M | leader | 85 | 82 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 29 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 20, 'NO_FLOW': 6, 'FLOW_AT_LEVEL': 3} | repriceable now: true 17 / false 12 | **cumulative bid_grade lines: 5874 (repriceable true 615 / false 5259)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 58m | 25/63-65/3117 | 63-64 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08DELKUS-KUS | 11 | 50m | 27/12-13/1063 | 11-12 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→12 |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 58m | 8/73-75/191 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 57m | 4/53-54/417 | 53-54 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08HONNAK-NAK | 43 | 57m | 1/46-46/10 | 43-46 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFMATCH-26JUL08JANFUN-FUN | 40 | 58m | 1/45-45/2 | 42-45 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08JUHKLO-KLO | 35 | 57m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 57m | 8/69-69/211 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 57m | 1/32-32/0 | 30-31 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→32 |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 58m | 4/47-47/47 | 46-47 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL08MOCTAN-TAN | 53 | 16m | 1/55-55/1 | 53-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL08OCHSAM-OCH | 12 | 19m | 288/17-28/11820 | 19-15 | 5 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08TAKJAS-JAS | 54 | 6m | 12/54-58/509 | 54-56 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-TAK | 45 | 58m | 32/46-48/1818 | 45-47 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 57m | 1/33-33/1 | 31-32 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→33 |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 57m | 3/69-69/15 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL08NAKMAL-MAL | 23 | 57m | 1/24-24/1 | 23-24 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| ITFWMATCH-26JUL08NAKMAL-NAK | 76 | 57m | 0 | 76-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-KAL | 79 | 11m | 0 | 79-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 58m | 7/22-22/131 | 21-22 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL08SNINON-NON | 25 | 57m | 1/26-26/1 | 25-26 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFWMATCH-26JUL08SNINON-SNI | 74 | 57m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 57m | 3/20-20/24 | 19-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 57m | 2/80-80/3 | 77-80 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08TIKZHA-TIK | 72 | 25m | 2/73-74/10 | 72-73 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFWMATCH-26JUL08TIKZHA-ZHA | 26 | 31m | 0 | 26-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 58m | 18/12-13/401 | 12-13 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-WAN | 85 | 58m | 1/88-88/1 | 85-88 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→88 |
| WTACHALLENGERMATCH-26JUL08VANSEL-S | 59 | 58m | 0 | 62-64 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08OCHSAM | 85 | 15 | **100** | 97 | +3 |

## FLOW-STATE — 18 tracked game(s) ({'WAKING': 14, 'OPEN': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | ITF_M | 0.5 | 1 | **OPEN** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.233 | 2 | **OPEN** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 2.7 | 2 | **OPEN** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.233 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL08JANFUN | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL08JUHKLO | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.167 | 1 | **WAKING** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 13.033 | — | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 0.067 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VANSEL | WTA_CHALL | 0.0 | 2 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
