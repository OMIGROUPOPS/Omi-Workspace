# LIVE VALIDATION — rolling status

- cycle 49 @ **2026-07-09 11:46:22 PM ET** | build `cae345e` | session boot 07-09 23:15 ET | log `live_v3_20260709.jsonl` | 2278 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:24 | ITFWMATCH-26JUL10TUPMAK-MAK | ITF_W | ? | 47 | 50 | -3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 30 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 17, 'NO_FLOW': 12, 'FLOW_AT_LEVEL': 1} | repriceable now: true 15 / false 15 | **cumulative bid_grade lines: 7295 (repriceable true 926 / false 6369)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10CATDEL-CAT | 15 | 31m | 1/20-20/23 | 15-20 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10CATDEL-DEL | 80 | 31m | 0 | 80-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATSNI-CAT | 13 | 31m | 1/14-14/33 | 13-14 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→14 |
| ITFMATCH-26JUL10FABOBR-FAB | 15 | 31m | 3/19-19/109 | 15-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ITFMATCH-26JUL10MILMIK-MIK | 11 | 31m | 2/13-13/10 | 11-13 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFMATCH-26JUL10MIRTAL-TAL | 59 | 30m | 1/63-63/1 | 59-63 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFMATCH-26JUL10PAPJER-JER | 44 | 30m | 1/47-47/2 | 44-47 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL10ROBDEC-DEC | 58 | 16m | 1/61-61/1 | 58-61 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ITFMATCH-26JUL10VIVJAN-JAN | 25 | 2m | 0 | 25-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10CIRGRA-CIR | 20 | 16m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-GOL | 19 | 30m | 0 | 19-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-DUE | 69 | 16m | 0 | 69-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-LEY | 27 | 16m | 0 | 27-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DYUSAG-SAG | 78 | 31m | 3/82-82/31 | 80-82 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL10FRISOL-SOL | 37 | 31m | 0 | 37-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KRUSMI-SMI | 19 | 16m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-NAT | 12 | 30m | 8/12-14/184 | 12-14 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-TOM | 85 | 30m | 0 | 85-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAVKAR-KAR | 57 | 30m | 1/60-60/1 | 57-60 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFWMATCH-26JUL10PAVKAR-PAV | 41 | 30m | 0 | 41-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAWHRU-PAW | 21 | 30m | 3/24-24/11 | 21-24 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| ITFWMATCH-26JUL10PLOERC-ERC | 89 | 26m | 2/90-90/22 | 89-90 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| ITFWMATCH-26JUL10PLOERC-PLO | 10 | 30m | 13/11-12/1854 | 10-11 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFWMATCH-26JUL10RYSALL-ALL | 23 | 30m | 0 | 23-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SHOKRO-SHO | 44 | 31m | 8/48-48/120 | 44-48 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFWMATCH-26JUL10SUPPOP-POP | 45 | 30m | 0 | 45-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUPPOP-SUP | 54 | 30m | 1/57-57/1 | 54-57 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFWMATCH-26JUL10TUPMAK-TUP | 50 | 22m | 10/53-54/225 | 52-53 | 3 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL10YODJAN-JAN | 66 | 16m | 2/67-67/7 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL10YODJAN-YOD | 34 | 30m | 5/35-35/18 | 34-35 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10TUPMAK | 47 | 53 | **100** | 97 | +3 |

## FLOW-STATE — 23 tracked game(s) ({'WAKING': 18, 'QUIET': 1, 'OPEN': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL10NATTOM | ITF_W | 0.267 | 2 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 0.5 | 1 | **OPEN** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 0.867 | 1 | **OPEN** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 0.367 | 1 | **OPEN** |
| ITFWMATCH-26JUL10CIRGRA | ITF_W | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL10CATDEL | ITF_M | 0.033 | 5 | **WAKING** |
| ITFMATCH-26JUL10CATSNI | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 0.1 | 4 | **WAKING** |
| ITFMATCH-26JUL10MILMIK | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL10MIRTAL | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10PAPJER | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL10ROBDEC | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10DUELEY | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL10FRISOL | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10PAVKAR | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 0.1 | 3 | **WAKING** |
| ITFWMATCH-26JUL10RYSALL | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 0.267 | 4 | **WAKING** |
| ITFWMATCH-26JUL10SUPPOP | ITF_W | 0.033 | 3 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
