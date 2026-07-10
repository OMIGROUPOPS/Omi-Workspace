# LIVE VALIDATION — rolling status

- cycle 45 @ **2026-07-09 11:05:21 PM ET** | build `da27128` | session boot 07-09 22:51 ET | log `live_v3_20260709.jsonl` | 1736 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 22:59 | ITFMATCH-26JUL09MOCJAS-MOC | ITF_M | ? | 23 | 19 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 32 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 9, 'NO_FLOW': 23} | repriceable now: true 7 / false 25 | **cumulative bid_grade lines: 7250 (repriceable true 908 / false 6342)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK-NAK | 42 | 13m | 80/46-50/1454 | 45-46 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFMATCH-26JUL10CATDEL-CAT | 15 | 5m | 2/20-20/94 | 15-20 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10CATDEL-DEL | 80 | 5m | 0 | 80-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATSNI-CAT | 13 | 2m | 0 | 13-14 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATSNI-SNI | 84 | 4m | 1/88-88/0 | 84-88 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→88 |
| ITFMATCH-26JUL10FABOBR-FAB | 15 | 5m | 0 | 15-19 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MILMIK-MIK | 11 | 5m | 0 | 11-13 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MIRTAL-TAL | 59 | 5m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10PAPJER-JER | 44 | 5m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10PAPJER-PAP | 53 | 5m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VIVJAN-JAN | 25 | 5m | 0 | 25-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VIVJAN-VIV | 72 | 0m | 0 | 72-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-DEN | 75 | 4m | 1/80-80/0 | 75-80 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-GOL | 19 | 4m | 0 | 19-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DYUSAG-DYU | 19 | 13m | 2/21-21/9 | 19-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFWMATCH-26JUL10FRISOL-FRI | 60 | 4m | 0 | 60-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FRISOL-SOL | 37 | 4m | 0 | 37-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-NAT | 12 | 4m | 0 | 12-14 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-TOM | 85 | 4m | 0 | 85-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAVKAR-KAR | 57 | 4m | 0 | 57-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAVKAR-PAV | 41 | 4m | 0 | 41-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAWHRU-HRU | 75 | 4m | 1/79-79/0 | 75-79 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→79 |
| ITFWMATCH-26JUL10PAWHRU-PAW | 21 | 4m | 1/24-24/39 | 21-24 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| ITFWMATCH-26JUL10PLOERC-PLO | 10 | 4m | 1/11-11/12 | 10-11 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFWMATCH-26JUL10RYSALL-ALL | 23 | 4m | 0 | 23-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10RYSALL-RYS | 75 | 4m | 1/78-78/0 | 75-78 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL10SHOKRO-SHO | 44 | 4m | 0 | 44-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUPPOP-POP | 45 | 4m | 0 | 45-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUPPOP-SUP | 54 | 2m | 0 | 54-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10TUPMAK-MAK | 47 | 2m | 0 | 47-51 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10TUPMAK-TUP | 52 | 4m | 0 | 52-53 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10YODJAN-YOD | 34 | 13m | 0 | 34-35 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 21 tracked game(s) ({'OPEN': 4, 'WAKING': 17}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK | ITF_M | 3.567 | 1 | **OPEN** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 0.2 | 2 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 0.467 | 1 | **OPEN** |
| ITFMATCH-26JUL09MOCJAS | ITF_M | 83.367 | — | **WAKING** |
| ITFMATCH-26JUL10CATDEL | ITF_M | 0.067 | 5 | **WAKING** |
| ITFMATCH-26JUL10CATSNI | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10MILMIK | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL10MIRTAL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10PAPJER | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 0.033 | 5 | **WAKING** |
| ITFWMATCH-26JUL10FRISOL | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10NATTOM | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL10PAVKAR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 0.133 | 3 | **WAKING** |
| ITFWMATCH-26JUL10RYSALL | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL10SUPPOP | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
