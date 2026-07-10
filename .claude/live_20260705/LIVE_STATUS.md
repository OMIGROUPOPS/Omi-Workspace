# LIVE VALIDATION — rolling status

- cycle 48 @ **2026-07-09 11:35:53 PM ET** | build `0d645a3` | session boot 07-09 23:15 ET | log `live_v3_20260709.jsonl` | 1833 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:24 | ITFWMATCH-26JUL10TUPMAK-MAK | ITF_W | ? | 47 | 50 | -3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 29 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 9, 'NO_FLOW': 19, 'FLOW_AT_LEVEL': 1} | repriceable now: true 9 / false 20 | **cumulative bid_grade lines: 7286 (repriceable true 920 / false 6366)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10CATDEL-CAT | 15 | 20m | 0 | 15-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATDEL-DEL | 80 | 20m | 0 | 80-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATSNI-CAT | 13 | 20m | 0 | 13-14 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10FABOBR-FAB | 15 | 20m | 0 | 15-19 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MILMIK-MIK | 11 | 20m | 2/13-13/10 | 11-13 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFMATCH-26JUL10MIRTAL-TAL | 59 | 20m | 1/63-63/1 | 59-63 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFMATCH-26JUL10PAPJER-JER | 44 | 20m | 1/47-47/2 | 44-47 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL10ROBDEC-DEC | 58 | 5m | 0 | 58-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10CIRGRA-CIR | 20 | 5m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-GOL | 19 | 20m | 0 | 19-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-DUE | 69 | 5m | 0 | 69-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-LEY | 27 | 5m | 0 | 27-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DYUSAG-SAG | 78 | 20m | 1/82-82/2 | 80-82 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL10FRISOL-SOL | 37 | 20m | 0 | 37-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KRUSMI-SMI | 19 | 6m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-NAT | 12 | 20m | 4/12-14/88 | 12-14 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-TOM | 85 | 20m | 0 | 85-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAVKAR-KAR | 57 | 20m | 0 | 57-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAVKAR-PAV | 41 | 20m | 0 | 41-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAWHRU-PAW | 21 | 20m | 2/24-24/4 | 21-24 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| ITFWMATCH-26JUL10PLOERC-ERC | 89 | 16m | 2/90-90/22 | 89-90 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| ITFWMATCH-26JUL10PLOERC-PLO | 10 | 20m | 7/11-11/133 | 10-11 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFWMATCH-26JUL10RYSALL-ALL | 23 | 20m | 0 | 23-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SHOKRO-SHO | 44 | 20m | 4/48-48/33 | 44-48 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFWMATCH-26JUL10SUPPOP-POP | 45 | 20m | 0 | 45-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUPPOP-SUP | 54 | 20m | 0 | 54-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10TUPMAK-TUP | 50 | 12m | 0 | 52-53 | — | **NO_FLOW** | 50 |  |
| ITFWMATCH-26JUL10YODJAN-JAN | 66 | 5m | 0 | 66-67 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10YODJAN-YOD | 34 | 20m | 5/35-35/18 | 34-35 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10TUPMAK | 47 | 53 | **100** | 97 | +3 |

## FLOW-STATE — 22 tracked game(s) ({'WAKING': 17, 'QUIET': 1, 'OPEN': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL10NATTOM | ITF_W | 0.2 | 2 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 0.4 | 1 | **OPEN** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 0.633 | 1 | **OPEN** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 0.367 | 1 | **OPEN** |
| ITFWMATCH-26JUL10CIRGRA | ITF_W | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL10CATDEL | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10CATSNI | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10MILMIK | ITF_M | 0.167 | 2 | **WAKING** |
| ITFMATCH-26JUL10MIRTAL | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10PAPJER | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL10ROBDEC | ITF_M | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10DUELEY | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL10FRISOL | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10PAVKAR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 0.067 | 3 | **WAKING** |
| ITFWMATCH-26JUL10RYSALL | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 0.167 | 4 | **WAKING** |
| ITFWMATCH-26JUL10SUPPOP | ITF_W | 0.0 | 3 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
