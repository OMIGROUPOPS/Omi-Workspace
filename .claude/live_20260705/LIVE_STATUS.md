# LIVE VALIDATION — rolling status

- cycle 1 @ **2026-07-10 12:58:52 AM ET** | build `a850665` | session boot 07-10 00:49 ET | log `live_v3_20260710.jsonl` | 1557 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:49 | ITFWMATCH-26JUL10DYUSAG-SAG | ITF_W | ? | 78 | 76 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 00:51 | ITFWMATCH-26JUL10PLOERC-ERC | ITF_W | ? | 89 | 87 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 90 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 73, 'FLOW_ABOVE': 16, 'FLOW_AT_LEVEL': 1} | repriceable now: true 14 / false 76 | **cumulative bid_grade lines: 7469 (repriceable true 966 / false 6503)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK-NAK | 43 | 9m | 565/45-58/95643 | 55-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL10ADDCRA-ADD | 32 | 6m | 0 | 32-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ADDCRA-CRA | 64 | 9m | 0 | 64-69 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARSJUH-ARS | 22 | 9m | 0 | 22-26 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARSJUH-JUH | 73 | 9m | 0 | 73-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-ARZ | 75 | 9m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-BEL | 20 | 9m | 0 | 20-24 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10BAYERE-BAY | 8 | 9m | 0 | 8-10 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10BAYERE-ERE | 90 | 7m | 0 | 90-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATDEL-CAT | 16 | 7m | 0 | 16-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATDEL-DEL | 80 | 9m | 0 | 80-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10CATSNI-CAT | 14 | 9m | 2/16-16/29 | 14-16 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→16 |
| ITFMATCH-26JUL10CATSNI-SNI | 87 | 9m | 2/87-88/18 | 87-88 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL10COCPAN-COC | 18 | 9m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10COCPAN-PAN | 76 | 9m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10DOUVIR-DOU | 92 | 9m | 0 | 92-95 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10DOUVIR-VIR | 5 | 9m | 0 | 5-9 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10FABOBR-FAB | 18 | 9m | 1/19-19/24 | 18-19 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ITFMATCH-26JUL10FABOBR-OBR | 81 | 9m | 0 | 81-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10JEDRIV-JED | 46 | 9m | 0 | 46-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10JONBAR-BAR | 63 | 9m | 0 | 63-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10JONBAR-JON | 33 | 9m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LAGROS-LAG | 33 | 9m | 0 | 33-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LAGROS-ROS | 62 | 9m | 0 | 62-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MAZBRE-BRE | 45 | 9m | 0 | 45-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MAZBRE-MAZ | 54 | 9m | 0 | 54-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MILMIK-MIK | 12 | 9m | 2/13-13/37 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFMATCH-26JUL10MILMIK-MIL | 86 | 9m | 0 | 86-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MIRTAL-MIR | 37 | 9m | 3/39-39/123 | 37-39 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFMATCH-26JUL10MIRTAL-TAL | 59 | 9m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10PAPJER-JER | 44 | 9m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10PAPJER-PAP | 53 | 9m | 0 | 53-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ROBDEC-DEC | 57 | 9m | 0 | 57-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ROBDEC-ROB | 39 | 9m | 0 | 39-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10TYABEA-TYA | 56 | 9m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VELMON-MON | 75 | 9m | 0 | 75-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VELMON-VEL | 19 | 9m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VIVJAN-JAN | 25 | 9m | 0 | 25-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VIVJAN-VIV | 72 | 6m | 1/74-74/5 | 72-74 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ITFMATCH-26JUL10ZAPDUR-DUR | 79 | 9m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-ZAP | 19 | 9m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZGISHI-SHI | 60 | 4m | 0 | 60-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZGISHI-ZGI | 37 | 9m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10BOJINI-BOJ | 55 | 9m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10BOJINI-INI | 43 | 9m | 0 | 43-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10CIRGRA-CIR | 22 | 9m | 0 | 22-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10CIRGRA-GRA | 75 | 9m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-DEN | 78 | 9m | 0 | 78-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DENGOL-GOL | 20 | 7m | 0 | 20-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-DUE | 69 | 9m | 0 | 69-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DUELEY-LEY | 27 | 9m | 0 | 27-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FONELS-ELS | 20 | 9m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FONELS-FON | 74 | 9m | 0 | 74-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FRISOL-SOL | 37 | 9m | 0 | 37-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-GAN | 18 | 9m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-STR | 76 | 9m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-HOS | 53 | 9m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-VAN | 44 | 9m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KOVJIA-JIA | 46 | 9m | 0 | 46-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KRUSMI-KRU | 81 | 7m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KRUSMI-SMI | 19 | 9m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KUBBER-BER | 9 | 9m | 1/10-10/5 | 9-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL10KUBBER-KUB | 88 | 9m | 0 | 88-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-NAK | 56 | 9m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-YAM | 42 | 9m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NATTOM-NAT | 12 | 9m | 2/13-13/37 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL10NATTOM-TOM | 87 | 7m | 0 | 87-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAVKAR-KAR | 57 | 9m | 1/60-60/55 | 57-60 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFWMATCH-26JUL10PAVKAR-PAV | 41 | 9m | 0 | 41-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAWHRU-HRU | 76 | 9m | 0 | 76-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PAWHRU-PAW | 22 | 9m | 2/23-23/25 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFWMATCH-26JUL10PEREZZ-EZZ | 34 | 9m | 0 | 34-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PEREZZ-PER | 61 | 9m | 0 | 61-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PLOERC-PLO | 7 | 1m | 0 | 10-11 | — | **NO_FLOW** | 8 |  |
| ITFWMATCH-26JUL10RYSALL-ALL | 23 | 9m | 1/25-25/0 | 23-25 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→25 |
| ITFWMATCH-26JUL10RYSALL-RYS | 75 | 9m | 0 | 75-77 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SHENON-NON | 26 | 9m | 1/32-32/121 | 28-32 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10SHOKRO-SHO | 43 | 9m | 18/47-50/440 | 47-50 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFWMATCH-26JUL10STAPOZ-POZ | 7 | 9m | 1/32-32/10 | 31-45 | 25 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10STAPOZ-STA | 9 | 9m | 0 | 50-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUNKAL-KAL | 64 | 9m | 0 | 64-68 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUNKAL-SUN | 33 | 9m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUPPOP-POP | 45 | 9m | 0 | 45-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SUPPOP-SUP | 54 | 7m | 0 | 54-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10VLAMIS-MIS | 78 | 9m | 0 | 78-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10VLAMIS-VLA | 18 | 7m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10WIEFOU-FOU | 61 | 9m | 0 | 61-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10WIEFOU-WIE | 36 | 9m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10YODJAN-JAN | 66 | 9m | 12/68-68/637 | 66-68 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFWMATCH-26JUL10YODJAN-YOD | 34 | 9m | 4/35-35/219 | 34-35 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10PLOERC | 89 | 11 | **100** | 97 | +3 |

## FLOW-STATE — 50 tracked game(s) ({'WAKING': 42, 'OPEN': 7, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10CATSNI | ITF_M | 0.267 | 1 | **OPEN** |
| ITFMATCH-26JUL10PAPJER | ITF_M | 0.333 | 3 | **OPEN** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 1.067 | 3 | **OPEN** |
| ITFWMATCH-26JUL10NATTOM | ITF_W | 0.333 | 1 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 1.1 | 1 | **OPEN** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 1.567 | 3 | **OPEN** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 1.533 | 1 | **OPEN** |
| ITFWMATCH-26JUL10KOVJIA | ITF_W | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL09IMANAK | ITF_M | 74.567 | — | **WAKING** |
| ITFMATCH-26JUL10ADDCRA | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10ARSJUH | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10ARZBEL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10BAYERE | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL10CATDEL | ITF_M | 0.067 | 4 | **WAKING** |
| ITFMATCH-26JUL10COCPAN | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10DOUVIR | ITF_M | 0.133 | 3 | **WAKING** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL10JEDRIV | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10JONBAR | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL10LAGROS | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10MAZBRE | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL10MILMIK | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL10MIRTAL | ITF_M | 0.167 | 2 | **WAKING** |
| ITFMATCH-26JUL10ROBDEC | ITF_M | 0.067 | 4 | **WAKING** |
| ITFMATCH-26JUL10TYABEA | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10VELMON | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL10ZAPDUR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10ZGISHI | ITF_M | 0.133 | 2 | **WAKING** |
| ITFWMATCH-26JUL10BOJINI | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10CIRGRA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 0.167 | 2 | **WAKING** |
| ITFWMATCH-26JUL10DUELEY | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL10FONELS | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10FRISOL | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL10GANSTR | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10HOSVAN | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL10KUBBER | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL10NAKYAM | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10PAVKAR | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL10PEREZZ | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL10RYSALL | ITF_W | 0.133 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SHENON | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL10STAPOZ | ITF_W | 0.067 | 14 | **WAKING** |
| ITFWMATCH-26JUL10SUNKAL | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SUPPOP | ITF_W | 0.067 | 3 | **WAKING** |
| ITFWMATCH-26JUL10VLAMIS | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10WIEFOU | ITF_W | 0.0 | 2 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
