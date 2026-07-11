# LIVE VALIDATION — rolling status

- cycle 61 @ **2026-07-11 03:19:10 AM ET** | build `772ac5e8` | session boot 07-11 00:38 ET | log `live_v3_20260711.jsonl` | 7865 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 8 item(s)
- **half_arm_aging**: KXITFWMATCH-26JUL11MAKSHO-SHO {"fill": 50, "age_min": 139, "mode": "PAIRING(sib never rested)"}
- **half_arm_aging**: KXITFMATCH-26JUL11LAGRIV-LAG {"fill": 69, "age_min": 137, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- **half_arm_aging**: KXITFWMATCH-26JUL11ERCHRU-HRU {"fill": 82, "age_min": 114, "mode": "PAIRING(sib never rested)"}
- **half_arm_aging**: KXITFMATCH-26JUL11DOUROB-ROB {"fill": 11, "age_min": 106, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- **half_arm_aging**: KXITFMATCH-26JUL11SNIMAZ-SNI {"fill": 75, "age_min": 92, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- **half_arm_aging**: KXITFMATCH-26JUL11SHIROB-ROB {"fill": 68, "age_min": 89, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- **half_arm_aging**: KXATPMATCH-26JUL11HUEBUT-BUT {"fill": 51, "age_min": 71, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- **half_arm_aging**: KXATPMATCH-26JUL11MONHER-MON {"fill": 59, "age_min": 32, "mode": "SET_BELOW_FLOW(prints 4c above)", "emitted_et": "2026-07-11 03:19:10 AM ET"}
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 11 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:00 | ITFWMATCH-26JUL11MAKSHO-SHO | ITF_W | ? | 50 | 42 | +8 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 01:01 | ITFMATCH-26JUL11LAGRIV-LAG | ITF_M | leader | 69 | 67 | +2 (place_cell) | — | pre | single |  | PENDING |
| 01:25 | ITFWMATCH-26JUL11ERCHRU-HRU | ITF_W | ? | 82 | 80 | +2 (fill_est) | — | pre | single |  | PENDING |
| 01:33 | ITFMATCH-26JUL11DOUROB-ROB | ITF_M | underdog | 11 | 6 | +5 (place_cell) | — | pre | single |  | PENDING |
| 01:34 | ITFWMATCH-26JUL11SAGYOD-SAG | ITF_W | underdog | 41 | 38 | +3 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:46 | ITFMATCH-26JUL11SNIMAZ-SNI | ITF_M | leader | 75 | 71 | +4 (place_cell) | — | pre | single |  | PENDING |
| 01:49 | ITFMATCH-26JUL11SHIROB-ROB | ITF_M | leader | 68 | 67 | +1 (place_cell) | — | pre | single |  | PENDING |
| 02:04 | ITFWMATCH-26JUL11SAGYOD-YOD | ITF_W | ? | 56 | 54 | +2 (fill_est) | — | pre | pair | 97 | PENDING |
| 02:08 | ATPMATCH-26JUL11HUEBUT-BUT | ATP_MAIN | leader | 51 | 52 | -1 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 02:46 | ATPMATCH-26JUL11MONHER-MON | ATP_MAIN | leader | 59 | 60 | -1 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 03:18 | ITFWMATCH-26JUL11STATOM-STA | ITF_W | leader | 62 | 60 | +2 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 49 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 34, 'FLOW_AT_LEVEL': 6, 'NO_FLOW': 9} | repriceable now: true 27 / false 22 | **cumulative bid_grade lines: 8068 (repriceable true 1132 / false 6936)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL11HUEBUT-HUE | 46 | 71m | 56/49-53/10912 | 49-49 | 3 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| ATPMATCH-26JUL11MONHER-HER | 38 | 32m | 4/42-42/339 | 41-42 | 4 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |
| ATPMATCH-26JUL11TABJEB-TAB | 90 | 160m | 62/92-93/7139 | 93-93 | 2 | **FLOW_ABOVE** | 93 | REPRICEABLE→92 |
| ATPMATCH-26JUL11VIRDIE-DIE | 33 | 19m | 1/35-35/3 | 34-34 | 2 | **FLOW_ABOVE** | 34 | REPRICEABLE→34 |
| ATPMATCH-26JUL11VIRDIE-VIR | 65 | 19m | 17/65-67/3877 | 66-66 | 0 | **FLOW_AT_LEVEL** | 67 |  |
| ITFMATCH-26JUL11DOUROB-DOU | 86 | 103m | 3/91-91/3 | 87-89 | 5 | **FLOW_ABOVE** | 86 | flow above but bound 86c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11DURBAR-BAR | 39 | 148m | 2/40-40/25 | 39-40 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |
| ITFMATCH-26JUL11DURBAR-DUR | 60 | 69m | 3/61-61/19 | 60-61 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ITFMATCH-26JUL11FABARZ-ARZ | 71 | 96m | 2/73-73/14 | 71-73 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL11FABARZ-FAB | 28 | 101m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11LAGRIV-RIV | 28 | 137m | 5/33-33/92 | 30-33 | 5 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11MILARS-ARS | 19 | 108m | 3/20-21/84 | 19-21 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL11MILARS-MIL | 78 | 31m | 0 | 78-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11NICJUA-JUA | 25 | 6m | 1/26-26/3 | 25-26 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFMATCH-26JUL11NORKOI-KOI | 36 | 78m | 1/39-39/2 | 36-39 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFMATCH-26JUL11NORKOI-NOR | 61 | 78m | 1/63-63/1 | 61-63 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFMATCH-26JUL11ORLLOP-LOP | 41 | 108m | 1/45-45/2 | 41-44 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL11ORLLOP-ORL | 56 | 88m | 2/58-58/37 | 56-58 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→58 |
| ITFMATCH-26JUL11RECWIS-REC | 31 | 34m | 0 | 31-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11RECWIS-WIS | 67 | 48m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11ROHBOR-BOR | 45 | 11m | 0 | 45-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11ROHBOR-ROH | 53 | 50m | 3/55-55/47 | 53-54 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL11SHIROB-SHI | 29 | 89m | 15/33-39/930 | 34-33 | 4 | **FLOW_ABOVE** | 29 | flow above but bound 29c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11SNIMAZ-MAZ | 20 | 90m | 2/25-25/6 | 23-25 | 5 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11TALPAP-PAP | 54 | 24m | 1/55-55/4 | 54-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL11TALPAP-TAL | 44 | 138m | 3/45-45/10 | 44-45 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL11TYAMON-MON | 67 | 160m | 72/79-84/1067 | 79-79 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL11BOSKAR-BOS | 60 | 39m | 0 | 60-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11BOSKAR-KAR | 38 | 78m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11DENSTR-DEN | 51 | 138m | 3/52-53/20 | 51-52 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ITFWMATCH-26JUL11DENSTR-STR | 49 | 156m | 6/50-50/624 | 49-50 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL11FONROJ-FON | 54 | 108m | 4/55-55/11 | 54-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFWMATCH-26JUL11FONROJ-ROJ | 44 | 158m | 4/46-47/11 | 44-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL11HOSCIR-CIR | 35 | 47m | 5/35-38/50 | 35-36 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 158m | 22/64-67/648 | 64-66 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11KALTIK-TIK | 63 | 48m | 6/67-68/160 | 64-64 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KARSUP-KAR | 59 | 136m | 12/59-61/139 | 59-60 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11KARSUP-SUP | 40 | 145m | 5/42-42/87 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ITFWMATCH-26JUL11KUBRYS-KUB | 66 | 158m | 18/67-68/1049 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KUBRYS-RYS | 33 | 48m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11LEEJOR-JOR | 43 | 48m | 2/43-46/2 | 43-45 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11LEEJOR-LEE | 55 | 48m | 2/57-57/2 | 55-57 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFWMATCH-26JUL11PERWIE-PER | 81 | 159m | 2/82-82/1 | 81-82 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL11PERWIE-WIE | 18 | 159m | 8/19-20/341 | 18-19 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ITFWMATCH-26JUL11SHEYAM-SHE | 46 | 158m | 2/48-48/35 | 46-48 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFWMATCH-26JUL11SHEYAM-YAM | 53 | 10m | 1/54-54/8 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFWMATCH-26JUL11SMILEY-LEY | 61 | 49m | 15/63-64/1054 | 61-62 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 158m | 23/38-40/979 | 38-39 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11STATOM-TOM | 35 | 0m | 0 | 36-38 | — | **NO_FLOW** | 35 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL11MAKSHO | 50 | 31 | **81** | 97 | -16 |
| ITFMATCH-26JUL11DOUROB | 11 | 89 | **100** | 97 | +3 |
| ITFMATCH-26JUL11SNIMAZ | 75 | 25 | **100** | 97 | +3 |
| ATPMATCH-26JUL11HUEBUT | 51 | 49 | **100** | 97 | +3 |
| ITFWMATCH-26JUL11STATOM | 62 | 38 | **100** | 97 | +3 |
| ITFMATCH-26JUL11SHIROB | 68 | 33 | **101** | 97 | +4 |
| ATPMATCH-26JUL11MONHER | 59 | 42 | **101** | 97 | +4 |
| ITFMATCH-26JUL11LAGRIV | 69 | 33 | **102** | 97 | +5 |

## FLOW-STATE — 33 tracked game(s) ({'WAKING': 24, 'OPEN': 9}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL11MONHER | ATP_MAIN | 0.7 | 1 | **OPEN** |
| ITFMATCH-26JUL11DOUROB | ITF_M | 0.2 | 2 | **OPEN** |
| ITFMATCH-26JUL11LAGRIV | ITF_M | 0.233 | 1 | **OPEN** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.6 | 1 | **OPEN** |
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 0.533 | 1 | **OPEN** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.333 | 1 | **OPEN** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.333 | 1 | **OPEN** |
| ITFWMATCH-26JUL11STATOM | ITF_W | 0.3 | 2 | **OPEN** |
| ATPMATCH-26JUL11HUEBUT | ATP_MAIN | 1.533 | — | **WAKING** |
| ATPMATCH-26JUL11TABJEB | ATP_MAIN | 0.233 | — | **WAKING** |
| ATPMATCH-26JUL11VIRDIE | ATP_MAIN | 0.733 | — | **WAKING** |
| ITFMATCH-26JUL11DURBAR | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL11FABARZ | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11MILARS | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL11NICJUA | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL11NORKOI | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL11ORLLOP | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL11RECWIS | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11ROHBOR | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL11SNIMAZ | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL11TALPAP | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.9 | — | **WAKING** |
| ITFWMATCH-26JUL11BOSKAR | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL11DENSTR | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL11FONROJ | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL11KALTIK | ITF_W | 0.2 | — | **WAKING** |
| ITFWMATCH-26JUL11KARSUP | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL11LEEJOR | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 135.1 | — | **WAKING** |
| ITFWMATCH-26JUL11PERWIE | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SAGYOD | ITF_W | 11.833 | — | **WAKING** |
| ITFWMATCH-26JUL11SHEYAM | ITF_W | 0.167 | 1 | **WAKING** |

## PATTERNS (sub-B) — 8
- half_arm_aging: KXITFWMATCH-26JUL11MAKSHO-SHO {"fill": 50, "age_min": 139, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL11LAGRIV-LAG {"fill": 69, "age_min": 137, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFWMATCH-26JUL11ERCHRU-HRU {"fill": 82, "age_min": 114, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL11DOUROB-ROB {"fill": 11, "age_min": 106, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFMATCH-26JUL11SNIMAZ-SNI {"fill": 75, "age_min": 92, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFMATCH-26JUL11SHIROB-ROB {"fill": 68, "age_min": 89, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPMATCH-26JUL11HUEBUT-BUT {"fill": 51, "age_min": 71, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPMATCH-26JUL11MONHER-MON {"fill": 59, "age_min": 32, "mode": "SET_BELOW_FLOW(prints 4c above)", "emitted_et": "2026-07-11 03:19:10 AM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
