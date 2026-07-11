# LIVE VALIDATION — rolling status

- cycle 55 @ **2026-07-11 02:18:10 AM ET** | build `c9d02ecb` | session boot 07-11 00:38 ET | log `live_v3_20260711.jsonl` | 5943 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 5 item(s)
- **half_arm_aging**: KXITFWMATCH-26JUL11MAKSHO-SHO {"fill": 50, "age_min": 78, "mode": "PAIRING(sib never rested)"}
- **half_arm_aging**: KXITFMATCH-26JUL11LAGRIV-LAG {"fill": 69, "age_min": 76, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- **half_arm_aging**: KXITFWMATCH-26JUL11ERCHRU-HRU {"fill": 82, "age_min": 53, "mode": "PAIRING(sib never rested)"}
- **half_arm_aging**: KXITFMATCH-26JUL11DOUROB-ROB {"fill": 11, "age_min": 45, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- **half_arm_aging**: KXITFMATCH-26JUL11SNIMAZ-SNI {"fill": 75, "age_min": 31, "mode": "SET_BELOW_FLOW(prints 5c above)", "emitted_et": "2026-07-11 02:18:10 AM ET"}
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 9 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:00 | ITFWMATCH-26JUL11MAKSHO-SHO | ITF_W | ? | 50 | 48 | +2 (fill_est) | — | pre | single |  | PENDING |
| 01:01 | ITFMATCH-26JUL11LAGRIV-LAG | ITF_M | leader | 69 | 67 | +2 (place_cell) | — | pre | single |  | PENDING |
| 01:25 | ITFWMATCH-26JUL11ERCHRU-HRU | ITF_W | ? | 82 | 80 | +2 (fill_est) | — | pre | single |  | PENDING |
| 01:33 | ITFMATCH-26JUL11DOUROB-ROB | ITF_M | underdog | 11 | 6 | +5 (place_cell) | — | pre | single |  | PENDING |
| 01:34 | ITFWMATCH-26JUL11SAGYOD-SAG | ITF_W | underdog | 41 | 38 | +3 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:46 | ITFMATCH-26JUL11SNIMAZ-SNI | ITF_M | leader | 75 | 71 | +4 (place_cell) | — | pre | single |  | PENDING |
| 01:49 | ITFMATCH-26JUL11SHIROB-ROB | ITF_M | leader | 68 | 67 | +1 (place_cell) | — | pre | single |  | PENDING |
| 02:04 | ITFWMATCH-26JUL11SAGYOD-YOD | ITF_W | ? | 56 | 54 | +2 (fill_est) | — | pre | pair | 97 | PENDING |
| 02:08 | ATPMATCH-26JUL11HUEBUT-BUT | ATP_MAIN | leader | 51 | 52 | -1 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 39 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 27, 'FLOW_AT_LEVEL': 3, 'NO_FLOW': 9} | repriceable now: true 21 / false 18 | **cumulative bid_grade lines: 8031 (repriceable true 1116 / false 6915)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL11HUEBUT-HUE | 46 | 10m | 3/49-50/331 | 49-49 | 3 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| ATPMATCH-26JUL11TABJEB-TAB | 90 | 99m | 26/92-93/1414 | 92-93 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFMATCH-26JUL11DOUROB-DOU | 86 | 42m | 3/91-91/3 | 89-91 | 5 | **FLOW_ABOVE** | 86 | flow above but bound 86c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11DURBAR-BAR | 39 | 87m | 1/40-40/2 | 39-40 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |
| ITFMATCH-26JUL11DURBAR-DUR | 60 | 8m | 0 | 60-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11FABARZ-ARZ | 71 | 35m | 2/73-73/14 | 71-73 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL11FABARZ-FAB | 28 | 40m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11LAGRIV-RIV | 28 | 76m | 1/33-33/2 | 30-33 | 5 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11MILARS-ARS | 19 | 47m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11NORKOI-KOI | 36 | 17m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11NORKOI-NOR | 61 | 17m | 0 | 61-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11ORLLOP-LOP | 41 | 47m | 1/45-45/2 | 41-45 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL11ORLLOP-ORL | 56 | 27m | 0 | 56-58 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11ROHBOR-BOR | 44 | 10m | 1/46-46/31 | 44-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFMATCH-26JUL11SHIROB-SHI | 29 | 28m | 2/33-33/12 | 32-33 | 4 | **FLOW_ABOVE** | 29 | flow above but bound 29c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11SNIMAZ-MAZ | 20 | 29m | 1/25-25/3 | 24-25 | 5 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11TALPAP-PAP | 53 | 22m | 4/53-56/64 | 53-55 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL11TALPAP-TAL | 44 | 77m | 1/45-45/5 | 44-45 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL11TYAMON-MON | 67 | 99m | 28/79-83/189 | 79-79 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL11BOSKAR-BOS | 59 | 17m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11BOSKAR-KAR | 38 | 17m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11DENSTR-DEN | 51 | 77m | 2/52-53/19 | 51-52 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ITFWMATCH-26JUL11DENSTR-STR | 49 | 95m | 2/50-50/20 | 49-50 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL11FONROJ-FON | 54 | 47m | 1/55-55/1 | 54-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFWMATCH-26JUL11FONROJ-ROJ | 44 | 97m | 1/46-46/1 | 44-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL11HOSCIR-CIR | 33 | 97m | 7/36-37/62 | 33-36 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 97m | 7/66-67/261 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFWMATCH-26JUL11KALTIK-TIK | 62 | 4m | 0 | 62-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11KARSUP-KAR | 59 | 75m | 5/59-61/37 | 59-60 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11KARSUP-SUP | 40 | 84m | 4/42-42/78 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ITFWMATCH-26JUL11KUBRYS-KUB | 66 | 97m | 7/67-67/283 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KUBRYS-RYS | 32 | 99m | 6/33-34/296 | 32-34 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→33 |
| ITFWMATCH-26JUL11PERWIE-PER | 81 | 98m | 2/82-82/1 | 81-82 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL11PERWIE-WIE | 18 | 98m | 5/19-20/133 | 18-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ITFWMATCH-26JUL11SHEYAM-SHE | 46 | 97m | 2/48-48/35 | 46-48 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFWMATCH-26JUL11SHEYAM-YAM | 52 | 69m | 4/54-54/30 | 52-54 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 97m | 18/39-39/625 | 38-39 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFWMATCH-26JUL11STATOM-STA | 62 | 97m | 2/62-63/6 | 62-63 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11STATOM-TOM | 36 | 97m | 1/40-40/4 | 36-40 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL11SNIMAZ | 75 | 25 | **100** | 97 | +3 |
| ATPMATCH-26JUL11HUEBUT | 51 | 49 | **100** | 97 | +3 |
| ITFMATCH-26JUL11SHIROB | 68 | 33 | **101** | 97 | +4 |
| ITFMATCH-26JUL11LAGRIV | 69 | 33 | **102** | 97 | +5 |
| ITFMATCH-26JUL11DOUROB | 11 | 91 | **102** | 97 | +5 |

## FLOW-STATE — 28 tracked game(s) ({'WAKING': 20, 'OPEN': 8}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL11TABJEB | ATP_MAIN | 0.567 | 1 | **OPEN** |
| ITFMATCH-26JUL11DOUROB | ITF_M | 0.467 | 2 | **OPEN** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.533 | 1 | **OPEN** |
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 0.6 | 1 | **OPEN** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.2 | 2 | **OPEN** |
| ITFWMATCH-26JUL11KALTIK | ITF_W | 0.333 | 2 | **OPEN** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.233 | 1 | **OPEN** |
| ATPMATCH-26JUL11HUEBUT | ATP_MAIN | 2.567 | — | **WAKING** |
| ITFMATCH-26JUL11DURBAR | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL11FABARZ | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL11LAGRIV | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL11MILARS | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11NORKOI | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL11ORLLOP | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL11ROHBOR | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL11SNIMAZ | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL11TALPAP | ITF_M | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.433 | — | **WAKING** |
| ITFWMATCH-26JUL11BOSKAR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL11DENSTR | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL11FONROJ | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11KARSUP | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 24.6 | — | **WAKING** |
| ITFWMATCH-26JUL11PERWIE | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SAGYOD | ITF_W | 10.2 | — | **WAKING** |
| ITFWMATCH-26JUL11SHEYAM | ITF_W | 0.167 | 2 | **WAKING** |
| ITFWMATCH-26JUL11STATOM | ITF_W | 0.067 | 1 | **WAKING** |

## PATTERNS (sub-B) — 5
- half_arm_aging: KXITFWMATCH-26JUL11MAKSHO-SHO {"fill": 50, "age_min": 78, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL11LAGRIV-LAG {"fill": 69, "age_min": 76, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFWMATCH-26JUL11ERCHRU-HRU {"fill": 82, "age_min": 53, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL11DOUROB-ROB {"fill": 11, "age_min": 45, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFMATCH-26JUL11SNIMAZ-SNI {"fill": 75, "age_min": 31, "mode": "SET_BELOW_FLOW(prints 5c above)", "emitted_et": "2026-07-11 02:18:10 AM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
