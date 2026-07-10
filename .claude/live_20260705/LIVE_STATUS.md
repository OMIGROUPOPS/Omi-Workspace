# LIVE VALIDATION — rolling status

- cycle 50 @ **2026-07-09 11:56:39 PM ET** | build `14d1a5b` | session boot 07-09 23:15 ET | log `live_v3_20260709.jsonl` | 2556 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:24 | ITFWMATCH-26JUL10TUPMAK-MAK | ITF_W | ? | 47 | 50 | -3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 32 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 17, 'FLOW_AT_LEVEL': 5, 'NO_FLOW': 10} | repriceable now: true 14 / false 18 | **cumulative bid_grade lines: 7304 (repriceable true 928 / false 6376)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10CATDEL-CAT | 15 | 41m | 1/20-20/23 | 15-20 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10CATDEL-DEL | 80 | 41m | 1/85-85/0 | 80-85 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10CATSNI-CAT | 13 | 41m | 1/14-14/33 | 13-14 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→14 |
| ITFMATCH-26JUL10FABOBR-FAB | 15 | 41m | 4/19-19/159 | 15-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ITFMATCH-26JUL10MILMIK-MIK | 11 | 41m | 6/11-13/73 | 11-13 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL10MIRTAL-TAL | 59 | 41m | 3/59-63/3 | 59-63 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL10PAPJER-JER | 44 | 41m | 1/47-47/2 | 44-47 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL10ROBDEC-DEC | 58 | 26m | 1/61-61/1 | 58-61 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ITFMATCH-26JUL10VIVJAN-JAN | 25 | 13m | 0 | 25-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VIVJAN-VIV | 72 | 4m | 0 | 72-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10CIRGRA-CIR | 20 | 26m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-GOL | 19 | 41m | 0 | 19-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-DUE | 69 | 26m | 0 | 69-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-LEY | 27 | 26m | 0 | 27-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DYUSAG-SAG | 78 | 41m | 4/82-82/34 | 80-82 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL10FRISOL-SOL | 37 | 41m | 2/37-40/2 | 37-40 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10KRUSMI-SMI | 19 | 26m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-NAT | 12 | 41m | 11/12-14/317 | 12-14 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-TOM | 85 | 41m | 1/89-89/0 | 85-89 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| ITFWMATCH-26JUL10PAVKAR-KAR | 57 | 41m | 2/60-60/1 | 57-60 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFWMATCH-26JUL10PAVKAR-PAV | 41 | 41m | 1/43-43/1 | 41-43 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFWMATCH-26JUL10PAWHRU-HRU | 75 | 6m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAWHRU-PAW | 21 | 41m | 6/21-24/28 | 21-24 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10PLOERC-ERC | 89 | 36m | 3/90-90/22 | 89-90 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| ITFWMATCH-26JUL10PLOERC-PLO | 10 | 41m | 17/11-12/2252 | 10-11 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFWMATCH-26JUL10RYSALL-ALL | 23 | 41m | 0 | 23-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SHOKRO-SHO | 44 | 41m | 8/48-48/120 | 44-48 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFWMATCH-26JUL10SUPPOP-POP | 45 | 41m | 0 | 45-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUPPOP-SUP | 54 | 41m | 1/57-57/1 | 54-57 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFWMATCH-26JUL10TUPMAK-TUP | 50 | 32m | 12/53-54/232 | 52-53 | 3 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL10YODJAN-JAN | 66 | 26m | 3/67-67/8 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL10YODJAN-YOD | 34 | 41m | 5/35-35/18 | 34-35 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10TUPMAK | 47 | 53 | **100** | 97 | +3 |

## FLOW-STATE — 23 tracked game(s) ({'WAKING': 18, 'QUIET': 1, 'OPEN': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL10NATTOM | ITF_W | 0.367 | 2 | **OPEN** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 0.2 | 3 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 0.467 | 1 | **OPEN** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 0.6 | 1 | **OPEN** |
| ITFWMATCH-26JUL10CIRGRA | ITF_W | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL10CATDEL | ITF_M | 0.067 | 5 | **WAKING** |
| ITFMATCH-26JUL10CATSNI | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 0.133 | 4 | **WAKING** |
| ITFMATCH-26JUL10MILMIK | ITF_M | 0.167 | 2 | **WAKING** |
| ITFMATCH-26JUL10MIRTAL | ITF_M | 0.067 | 4 | **WAKING** |
| ITFMATCH-26JUL10PAPJER | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL10ROBDEC | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10DUELEY | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 0.133 | 2 | **WAKING** |
| ITFWMATCH-26JUL10FRISOL | ITF_W | 0.067 | 3 | **WAKING** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10PAVKAR | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL10RYSALL | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 0.233 | 4 | **WAKING** |
| ITFWMATCH-26JUL10SUPPOP | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 0.167 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXITFWMATCH-26JUL10TUPMAK-MAK {"fill": 47, "age_min": 32, "mode": "SET_BELOW_FLOW(prints 3c above)", "emitted_et": "2026-07-09 11:56:39 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
