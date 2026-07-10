# LIVE VALIDATION — rolling status

- cycle 4 @ **2026-07-10 12:34:57 AM ET** | build `204be91` | session boot 07-09 23:56 ET | log `live_v3_20260709.jsonl` | 5084 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:19 | ITFWMATCH-26JUL10SHENON-SHE | ITF_W | leader | 68 | 65 | +3 (place_cell) | — | pre | single |  | PENDING |
| 00:27 | ITFWMATCH-26JUL10TUPMAK-TUP | ITF_W | ? | 50 | 48 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 81 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 23, 'NO_FLOW': 55, 'FLOW_AT_LEVEL': 3} | repriceable now: true 22 / false 59 | **cumulative bid_grade lines: 7416 (repriceable true 954 / false 6462)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10ADDCRA-ADD | 32 | 34m | 0 | 32-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ADDCRA-CRA | 64 | 34m | 0 | 64-70 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARSJUH-ARS | 22 | 4m | 0 | 22-26 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARSJUH-JUH | 73 | 4m | 0 | 73-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-ARZ | 75 | 4m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-BEL | 20 | 4m | 0 | 20-24 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10BAYERE-BAY | 8 | 34m | 6/10-11/1014 | 8-11 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL10BAYERE-ERE | 90 | 31m | 0 | 90-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATDEL-CAT | 15 | 37m | 1/20-20/14 | 15-20 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10CATSNI-CAT | 13 | 37m | 4/14-14/58 | 13-14 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→14 |
| ITFMATCH-26JUL10CATSNI-SNI | 87 | 14m | 2/88-88/7 | 87-88 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→88 |
| ITFMATCH-26JUL10COCPAN-COC | 18 | 4m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10COCPAN-PAN | 76 | 4m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10DOUVIR-DOU | 92 | 4m | 0 | 92-96 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10FABOBR-FAB | 18 | 1m | 0 | 18-19 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10FABOBR-OBR | 81 | 14m | 1/85-85/2 | 81-85 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFMATCH-26JUL10JEDRIV-JED | 46 | 34m | 0 | 46-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10JONBAR-BAR | 64 | 4m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10JONBAR-JON | 33 | 0m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LAGROS-LAG | 33 | 34m | 0 | 33-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LAGROS-ROS | 62 | 27m | 1/66-66/10 | 62-66 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFMATCH-26JUL10MAZBRE-BRE | 45 | 4m | 0 | 45-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MAZBRE-MAZ | 54 | 4m | 1/57-57/8 | 54-57 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFMATCH-26JUL10MILMIK-MIK | 12 | 17m | 1/13-13/8 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFMATCH-26JUL10MILMIK-MIL | 86 | 37m | 2/86-90/8 | 86-89 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL10MIRTAL-MIR | 37 | 37m | 1/39-39/1 | 37-39 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFMATCH-26JUL10PAPJER-JER | 44 | 34m | 1/47-47/4 | 44-47 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL10ROBDEC-ROB | 39 | 37m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10TYABEA-TYA | 56 | 4m | 1/60-60/11 | 56-60 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFMATCH-26JUL10VELMON-MON | 75 | 4m | 0 | 75-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VELMON-VEL | 19 | 4m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VIVJAN-JAN | 25 | 37m | 0 | 25-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VIVJAN-VIV | 72 | 33m | 1/74-74/5 | 72-74 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ITFMATCH-26JUL10ZAPDUR-DUR | 79 | 4m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-ZAP | 19 | 4m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZGISHI-SHI | 56 | 4m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZGISHI-ZGI | 42 | 4m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10BOJINI-BOJ | 55 | 4m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10BOJINI-INI | 43 | 4m | 0 | 43-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10CIRGRA-CIR | 22 | 1m | 0 | 22-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10CIRGRA-GRA | 75 | 1m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-DEN | 75 | 13m | 0 | 75-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-GOL | 19 | 37m | 0 | 19-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-DUE | 69 | 37m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-LEY | 27 | 37m | 0 | 27-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DYUSAG-SAG | 78 | 37m | 18/82-83/150 | 80-82 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL10FONELS-ELS | 20 | 4m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FONELS-FON | 74 | 4m | 0 | 74-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-GAN | 18 | 4m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-STR | 76 | 4m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-HOS | 52 | 4m | 0 | 52-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-VAN | 44 | 4m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KOVJIA-JIA | 46 | 4m | 0 | 46-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KRUSMI-KRU | 81 | 28m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KRUSMI-SMI | 19 | 37m | 1/21-21/8 | 19-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFWMATCH-26JUL10KUBBER-BER | 9 | 4m | 0 | 9-10 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KUBBER-KUB | 88 | 4m | 0 | 88-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-NAK | 56 | 26m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-YAM | 42 | 26m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-NAT | 12 | 37m | 13/12-14/267 | 12-13 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10PAWHRU-HRU | 76 | 15m | 2/78-78/3 | 76-78 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL10PAWHRU-PAW | 21 | 37m | 1/24-24/11 | 21-23 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| ITFWMATCH-26JUL10PEREZZ-EZZ | 34 | 4m | 0 | 34-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PEREZZ-PER | 61 | 4m | 0 | 61-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PLOERC-PLO | 10 | 37m | 29/11-12/1565 | 10-11 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFWMATCH-26JUL10RYSALL-ALL | 23 | 37m | 0 | 23-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10RYSALL-RYS | 75 | 37m | 1/77-77/16 | 75-77 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→77 |
| ITFWMATCH-26JUL10SHENON-NON | 28 | 34m | 5/32-32/89 | 28-32 | 4 | **FLOW_ABOVE** | 29 | REPRICEABLE→29 |
| ITFWMATCH-26JUL10SHOKRO-KRO | 54 | 0m | 0 | 55-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SHOKRO-SHO | 47 | 6m | 8/47-49/106 | 47-48 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10STAPOZ-POZ | 29 | 2m | 0 | 30-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUNKAL-KAL | 64 | 34m | 0 | 64-68 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUNKAL-SUN | 33 | 19m | 1/35-35/3 | 33-35 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ITFWMATCH-26JUL10SUPPOP-POP | 45 | 37m | 0 | 45-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUPPOP-SUP | 54 | 25m | 1/57-57/0 | 54-57 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFWMATCH-26JUL10VLAMIS-MIS | 78 | 4m | 0 | 78-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10VLAMIS-VLA | 21 | 4m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10WIEFOU-FOU | 61 | 4m | 0 | 61-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10WIEFOU-WIE | 36 | 4m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10YODJAN-JAN | 66 | 37m | 22/67-67/915 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL10YODJAN-YOD | 34 | 37m | 10/35-35/647 | 34-35 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10SHENON | 68 | 32 | **100** | 97 | +3 |

## FLOW-STATE — 48 tracked game(s) ({'WAKING': 34, 'OPEN': 9, 'QUIET': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10BAYERE | ITF_M | 0.2 | 3 | **OPEN** |
| ITFMATCH-26JUL10CATSNI | ITF_M | 0.2 | 1 | **OPEN** |
| ITFMATCH-26JUL10MILMIK | ITF_M | 0.233 | 1 | **OPEN** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 0.533 | 2 | **OPEN** |
| ITFWMATCH-26JUL10NATTOM | ITF_W | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 0.967 | 1 | **OPEN** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 2.0 | 1 | **OPEN** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 1.6 | 3 | **OPEN** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 0.9 | 1 | **OPEN** |
| ITFMATCH-26JUL10ROBDEC | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL10VELMON | ITF_M | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL10FONELS | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL10KOVJIA | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL10STAPOZ | ITF_W | 0.0 | 16 | **QUIET** |
| ITFMATCH-26JUL10ADDCRA | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10ARSJUH | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10ARZBEL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10CATDEL | ITF_M | 0.033 | 5 | **WAKING** |
| ITFMATCH-26JUL10COCPAN | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10DOUVIR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL10JEDRIV | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10JONBAR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10LAGROS | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10MAZBRE | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL10MIRTAL | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL10PAPJER | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL10TYABEA | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL10ZAPDUR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10ZGISHI | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10BOJINI | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10CIRGRA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10DUELEY | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL10GANSTR | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10HOSVAN | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL10KUBBER | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10NAKYAM | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 0.167 | 2 | **WAKING** |
| ITFWMATCH-26JUL10PEREZZ | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL10RYSALL | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SHENON | ITF_W | 0.2 | 4 | **WAKING** |
| ITFWMATCH-26JUL10SUNKAL | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SUPPOP | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL10VLAMIS | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10WIEFOU | ITF_W | 0.0 | 3 | **WAKING** |

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
