# LIVE VALIDATION — rolling status

- cycle 5 @ **2026-07-10 12:45:23 AM ET** | build `781246c` | session boot 07-09 23:56 ET | log `live_v3_20260709.jsonl` | 5748 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:19 | ITFWMATCH-26JUL10SHENON-SHE | ITF_W | leader | 68 | 65 | +3 (place_cell) | — | pre | single |  | PENDING |
| 00:27 | ITFWMATCH-26JUL10TUPMAK-TUP | ITF_W | ? | 50 | 48 | +2 (fill_est) | — | pre | single |  | PENDING |
| 00:35 | ITFWMATCH-26JUL10SHOKRO-KRO | ITF_W | leader | 54 | 50 | +4 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 89 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 29, 'NO_FLOW': 57, 'FLOW_AT_LEVEL': 3} | repriceable now: true 25 / false 64 | **cumulative bid_grade lines: 7433 (repriceable true 958 / false 6475)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10ADDCRA-ADD | 32 | 45m | 0 | 32-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ADDCRA-CRA | 64 | 44m | 0 | 64-69 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARSJUH-ARS | 22 | 14m | 0 | 22-26 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARSJUH-JUH | 73 | 14m | 0 | 73-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-ARZ | 75 | 14m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-BEL | 20 | 14m | 0 | 20-24 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10BAYERE-BAY | 8 | 44m | 6/10-11/1014 | 8-11 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL10BAYERE-ERE | 90 | 41m | 0 | 90-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATDEL-CAT | 15 | 48m | 1/20-20/14 | 15-20 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10CATDEL-DEL | 80 | 3m | 0 | 80-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATSNI-CAT | 13 | 48m | 7/14-14/88 | 14-14 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→14 |
| ITFMATCH-26JUL10CATSNI-SNI | 87 | 24m | 2/88-88/7 | 87-88 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→88 |
| ITFMATCH-26JUL10COCPAN-COC | 18 | 14m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10COCPAN-PAN | 76 | 14m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10DOUVIR-DOU | 92 | 15m | 0 | 92-95 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10FABOBR-FAB | 18 | 12m | 0 | 18-19 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10FABOBR-OBR | 81 | 24m | 1/85-85/2 | 81-85 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFMATCH-26JUL10JEDRIV-JED | 46 | 45m | 0 | 46-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10JONBAR-BAR | 64 | 14m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10JONBAR-JON | 33 | 11m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LAGROS-LAG | 33 | 45m | 0 | 33-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LAGROS-ROS | 62 | 37m | 1/66-66/10 | 62-66 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFMATCH-26JUL10MAZBRE-BRE | 45 | 14m | 0 | 45-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MAZBRE-MAZ | 54 | 14m | 1/57-57/8 | 54-57 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFMATCH-26JUL10MILMIK-MIK | 12 | 27m | 1/13-13/8 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFMATCH-26JUL10MILMIK-MIL | 86 | 48m | 2/86-90/8 | 86-89 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL10MIRTAL-MIR | 37 | 48m | 1/39-39/1 | 37-39 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFMATCH-26JUL10MIRTAL-TAL | 59 | 3m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10PAPJER-JER | 44 | 44m | 1/47-47/4 | 44-47 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL10PAPJER-PAP | 53 | 3m | 1/55-55/253 | 53-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL10ROBDEC-ROB | 39 | 48m | 0 | 39-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10TYABEA-TYA | 56 | 14m | 1/60-60/11 | 56-60 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFMATCH-26JUL10VELMON-MON | 75 | 14m | 0 | 75-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VELMON-VEL | 19 | 14m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VIVJAN-JAN | 25 | 48m | 0 | 25-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VIVJAN-VIV | 72 | 43m | 1/74-74/5 | 72-74 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ITFMATCH-26JUL10ZAPDUR-DUR | 79 | 14m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-ZAP | 19 | 14m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZGISHI-SHI | 56 | 15m | 4/57-57/624 | 57-57 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFMATCH-26JUL10ZGISHI-ZGI | 42 | 15m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10BOJINI-BOJ | 55 | 14m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10BOJINI-INI | 43 | 14m | 0 | 43-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10CIRGRA-CIR | 22 | 12m | 0 | 22-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10CIRGRA-GRA | 75 | 11m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-DEN | 75 | 23m | 4/80-80/361 | 75-81 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-GOL | 19 | 48m | 0 | 19-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-DUE | 69 | 48m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-LEY | 27 | 48m | 0 | 27-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DYUSAG-SAG | 78 | 48m | 33/80-83/739 | 80-82 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL10FONELS-ELS | 20 | 14m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FONELS-FON | 74 | 14m | 0 | 74-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FRISOL-SOL | 37 | 3m | 0 | 37-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-GAN | 18 | 14m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-STR | 76 | 14m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-HOS | 53 | 1m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-VAN | 44 | 14m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KOVJIA-JIA | 46 | 14m | 0 | 46-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KRUSMI-KRU | 81 | 38m | 1/81-81/4 | 81-83 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10KRUSMI-SMI | 19 | 48m | 1/21-21/8 | 19-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFWMATCH-26JUL10KUBBER-BER | 9 | 14m | 0 | 9-10 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KUBBER-KUB | 88 | 14m | 0 | 88-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-NAK | 56 | 37m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-YAM | 42 | 37m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-NAT | 12 | 48m | 17/12-14/319 | 12-13 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-TOM | 85 | 3m | 0 | 87-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAVKAR-KAR | 57 | 3m | 0 | 57-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAVKAR-PAV | 41 | 3m | 0 | 41-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAWHRU-HRU | 76 | 26m | 2/78-78/3 | 76-78 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL10PAWHRU-PAW | 22 | 3m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFWMATCH-26JUL10PEREZZ-EZZ | 34 | 14m | 0 | 34-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PEREZZ-PER | 61 | 14m | 0 | 61-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PLOERC-ERC | 89 | 3m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PLOERC-PLO | 10 | 48m | 34/11-14/1598 | 12-11 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFWMATCH-26JUL10RYSALL-ALL | 23 | 48m | 0 | 23-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10RYSALL-RYS | 75 | 48m | 4/77-77/390 | 75-77 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→77 |
| ITFWMATCH-26JUL10SHENON-NON | 28 | 44m | 5/32-32/89 | 28-32 | 4 | **FLOW_ABOVE** | 29 | REPRICEABLE→29 |
| ITFWMATCH-26JUL10SHOKRO-SHO | 43 | 10m | 9/47-50/224 | 47-48 | 4 | **FLOW_ABOVE** | 43 | flow above but bound 43c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL10STAPOZ-POZ | 31 | 8m | 0 | 31-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10STAPOZ-STA | 9 | 7m | 1/68-68/3 | 62-69 | 59 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10SUNKAL-KAL | 64 | 44m | 0 | 64-68 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUNKAL-SUN | 33 | 29m | 1/35-35/3 | 33-35 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ITFWMATCH-26JUL10SUPPOP-POP | 45 | 48m | 1/48-48/0 | 45-48 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFWMATCH-26JUL10SUPPOP-SUP | 54 | 35m | 1/57-57/0 | 54-57 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFWMATCH-26JUL10VLAMIS-MIS | 78 | 14m | 0 | 78-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10VLAMIS-VLA | 21 | 14m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10WIEFOU-FOU | 61 | 14m | 0 | 61-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10WIEFOU-WIE | 36 | 14m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10YODJAN-JAN | 66 | 48m | 36/67-68/1497 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL10YODJAN-YOD | 34 | 48m | 15/35-35/750 | 34-35 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10SHENON | 68 | 32 | **100** | 97 | +3 |
| ITFWMATCH-26JUL10SHOKRO | 54 | 48 | **102** | 97 | +5 |

## FLOW-STATE — 50 tracked game(s) ({'WAKING': 38, 'OPEN': 9, 'QUIET': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10CATSNI | ITF_M | 0.267 | 1 | **OPEN** |
| ITFMATCH-26JUL10MILMIK | ITF_M | 0.233 | 1 | **OPEN** |
| ITFMATCH-26JUL10PAPJER | ITF_M | 0.367 | 2 | **OPEN** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 0.9 | 2 | **OPEN** |
| ITFWMATCH-26JUL10NATTOM | ITF_W | 0.467 | 1 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 0.933 | 1 | **OPEN** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 2.767 | 1 | **OPEN** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 2.033 | 1 | **OPEN** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 1.433 | 1 | **OPEN** |
| ITFMATCH-26JUL10VELMON | ITF_M | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL10FONELS | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL10KOVJIA | ITF_W | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL10ADDCRA | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10ARSJUH | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10ARZBEL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10BAYERE | ITF_M | 0.067 | 3 | **WAKING** |
| ITFMATCH-26JUL10CATDEL | ITF_M | 0.1 | 5 | **WAKING** |
| ITFMATCH-26JUL10COCPAN | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10DOUVIR | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL10JEDRIV | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10JONBAR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10LAGROS | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10MAZBRE | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL10MIRTAL | ITF_M | 0.1 | 2 | **WAKING** |
| ITFMATCH-26JUL10ROBDEC | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10TYABEA | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL10ZAPDUR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10ZGISHI | ITF_M | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL10BOJINI | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10CIRGRA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 0.133 | 5 | **WAKING** |
| ITFWMATCH-26JUL10DUELEY | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL10FRISOL | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL10GANSTR | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10HOSVAN | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL10KUBBER | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10NAKYAM | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10PAVKAR | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL10PEREZZ | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL10RYSALL | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SHENON | ITF_W | 0.133 | 4 | **WAKING** |
| ITFWMATCH-26JUL10STAPOZ | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SUNKAL | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SUPPOP | ITF_W | 0.067 | 3 | **WAKING** |
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
