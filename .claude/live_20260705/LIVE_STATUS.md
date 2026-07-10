# LIVE VALIDATION — rolling status

- cycle 3 @ **2026-07-10 12:24:33 AM ET** | build `ed32e2c` | session boot 07-09 23:56 ET | log `live_v3_20260709.jsonl` | 3927 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:19 | ITFWMATCH-26JUL10SHENON-SHE | ITF_W | leader | 68 | 65 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 46 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 16, 'NO_FLOW': 26, 'FLOW_AT_LEVEL': 4} | repriceable now: true 15 / false 31 | **cumulative bid_grade lines: 7369 (repriceable true 946 / false 6423)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10ADDCRA-ADD | 32 | 24m | 0 | 32-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ADDCRA-CRA | 64 | 24m | 0 | 64-70 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10BAYERE-BAY | 8 | 24m | 4/10-11/999 | 8-11 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL10BAYERE-ERE | 90 | 21m | 0 | 90-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATDEL-CAT | 15 | 27m | 1/20-20/14 | 15-20 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10CATSNI-CAT | 13 | 27m | 2/14-14/21 | 13-14 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→14 |
| ITFMATCH-26JUL10CATSNI-SNI | 87 | 3m | 1/88-88/2 | 87-88 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→88 |
| ITFMATCH-26JUL10FABOBR-FAB | 16 | 3m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10FABOBR-OBR | 81 | 3m | 1/85-85/2 | 81-85 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFMATCH-26JUL10JEDRIV-JED | 46 | 24m | 0 | 46-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LAGROS-LAG | 33 | 24m | 0 | 33-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LAGROS-ROS | 62 | 16m | 0 | 62-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MILMIK-MIK | 12 | 7m | 0 | 12-13 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MILMIK-MIL | 86 | 27m | 2/86-90/8 | 86-89 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL10MIRTAL-MIR | 37 | 27m | 1/39-39/1 | 37-39 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFMATCH-26JUL10PAPJER-JER | 44 | 24m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ROBDEC-ROB | 39 | 27m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VIVJAN-JAN | 25 | 27m | 0 | 25-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VIVJAN-VIV | 72 | 23m | 1/74-74/5 | 72-74 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ITFWMATCH-26JUL10CIRGRA-CIR | 20 | 27m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10CIRGRA-GRA | 74 | 27m | 0 | 74-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-DEN | 75 | 2m | 0 | 75-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-GOL | 19 | 27m | 0 | 19-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-DUE | 69 | 27m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-LEY | 27 | 27m | 0 | 27-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DYUSAG-SAG | 78 | 27m | 13/82-82/129 | 80-82 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL10KRUSMI-KRU | 81 | 17m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KRUSMI-SMI | 19 | 27m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-NAK | 56 | 16m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-YAM | 42 | 16m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-NAT | 12 | 27m | 8/12-14/188 | 12-13 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10PAWHRU-HRU | 76 | 5m | 1/78-78/2 | 76-78 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL10PAWHRU-PAW | 21 | 27m | 1/24-24/11 | 21-23 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| ITFWMATCH-26JUL10PLOERC-PLO | 10 | 27m | 23/11-12/1310 | 10-11 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFWMATCH-26JUL10RYSALL-ALL | 23 | 27m | 0 | 23-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10RYSALL-RYS | 75 | 27m | 1/77-77/16 | 75-77 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→77 |
| ITFWMATCH-26JUL10SHENON-NON | 28 | 24m | 5/32-32/89 | 28-32 | 4 | **FLOW_ABOVE** | 29 | REPRICEABLE→29 |
| ITFWMATCH-26JUL10SHOKRO-KRO | 52 | 22m | 14/52-56/883 | 52-55 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10SHOKRO-SHO | 44 | 27m | 13/44-49/1136 | 44-48 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10SUNKAL-KAL | 64 | 24m | 0 | 64-68 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUNKAL-SUN | 33 | 9m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUPPOP-POP | 45 | 27m | 0 | 45-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUPPOP-SUP | 54 | 14m | 0 | 54-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10TUPMAK-TUP | 50 | 27m | 28/53-56/3216 | 52-53 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→53 |
| ITFWMATCH-26JUL10YODJAN-JAN | 66 | 27m | 10/67-67/539 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL10YODJAN-YOD | 34 | 27m | 8/35-35/517 | 34-35 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10SHENON | 68 | 32 | **100** | 97 | +3 |

## FLOW-STATE — 28 tracked game(s) ({'WAKING': 20, 'OPEN': 7, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10MILMIK | ITF_M | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 0.433 | 2 | **OPEN** |
| ITFWMATCH-26JUL10NATTOM | ITF_W | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 0.767 | 1 | **OPEN** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 1.167 | 3 | **OPEN** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 0.933 | 1 | **OPEN** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 0.633 | 1 | **OPEN** |
| ITFMATCH-26JUL10ROBDEC | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL10ADDCRA | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10BAYERE | ITF_M | 0.133 | 3 | **WAKING** |
| ITFMATCH-26JUL10CATDEL | ITF_M | 0.033 | 5 | **WAKING** |
| ITFMATCH-26JUL10CATSNI | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL10JEDRIV | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10LAGROS | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10MIRTAL | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL10PAPJER | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL10CIRGRA | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10DUELEY | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL10NAKYAM | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 0.167 | 2 | **WAKING** |
| ITFWMATCH-26JUL10RYSALL | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SHENON | ITF_W | 0.3 | 4 | **WAKING** |
| ITFWMATCH-26JUL10SUNKAL | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SUPPOP | ITF_W | 0.0 | 3 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — **9 VIOLATIONS**
- **VIOLATION**: `KXITFMATCH-26JUL10CATDEL-DEL` drained 2026-07-09 11:56:41 PM ET — neither filled, re-placed, nor refusal-named within 10 min post-boot
- **VIOLATION**: `KXITFMATCH-26JUL10MIRTAL-TAL` drained 2026-07-09 11:56:42 PM ET — neither filled, re-placed, nor refusal-named within 10 min post-boot
- **VIOLATION**: `KXITFMATCH-26JUL10ROBDEC-DEC` drained 2026-07-09 11:56:44 PM ET — neither filled, re-placed, nor refusal-named within 10 min post-boot
- **VIOLATION**: `KXITFWMATCH-26JUL10FRISOL-SOL` drained 2026-07-09 11:56:41 PM ET — neither filled, re-placed, nor refusal-named within 10 min post-boot
- **VIOLATION**: `KXITFWMATCH-26JUL10NATTOM-TOM` drained 2026-07-09 11:56:42 PM ET — neither filled, re-placed, nor refusal-named within 10 min post-boot
- **VIOLATION**: `KXITFWMATCH-26JUL10PAVKAR-KAR` drained 2026-07-09 11:56:42 PM ET — neither filled, re-placed, nor refusal-named within 10 min post-boot
- **VIOLATION**: `KXITFWMATCH-26JUL10PAVKAR-PAV` drained 2026-07-09 11:56:43 PM ET — neither filled, re-placed, nor refusal-named within 10 min post-boot
- **VIOLATION**: `KXITFWMATCH-26JUL10PLOERC-ERC` drained 2026-07-09 11:56:43 PM ET — neither filled, re-placed, nor refusal-named within 10 min post-boot
- **VIOLATION**: `KXITFWMATCH-26JUL10SUPPOP-SUP` drained 2026-07-09 11:56:43 PM ET — neither filled, re-placed, nor refusal-named within 10 min post-boot

## ERRORS — 0 handler errors this session (ZERO — clean loop)
