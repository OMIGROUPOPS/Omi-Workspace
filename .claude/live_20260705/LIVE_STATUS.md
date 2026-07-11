# LIVE VALIDATION — rolling status

- cycle 59 @ **2026-07-11 02:58:49 AM ET** | build `08422194` | session boot 07-11 00:38 ET | log `live_v3_20260711.jsonl` | 7207 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 7 item(s)
- **half_arm_aging**: KXITFWMATCH-26JUL11MAKSHO-SHO {"fill": 50, "age_min": 118, "mode": "PAIRING(sib never rested)"}
- **half_arm_aging**: KXITFMATCH-26JUL11LAGRIV-LAG {"fill": 69, "age_min": 117, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- **half_arm_aging**: KXITFWMATCH-26JUL11ERCHRU-HRU {"fill": 82, "age_min": 94, "mode": "PAIRING(sib never rested)"}
- **half_arm_aging**: KXITFMATCH-26JUL11DOUROB-ROB {"fill": 11, "age_min": 86, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- **half_arm_aging**: KXITFMATCH-26JUL11SNIMAZ-SNI {"fill": 75, "age_min": 72, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- **half_arm_aging**: KXITFMATCH-26JUL11SHIROB-ROB {"fill": 68, "age_min": 69, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- **half_arm_aging**: KXATPMATCH-26JUL11HUEBUT-BUT {"fill": 51, "age_min": 50, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 10 graded (session)
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
| 02:46 | ATPMATCH-26JUL11MONHER-MON | ATP_MAIN | leader | 59 | 60 | -1 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 47 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 34, 'FLOW_AT_LEVEL': 5, 'NO_FLOW': 8} | repriceable now: true 27 / false 20 | **cumulative bid_grade lines: 8057 (repriceable true 1127 / false 6930)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL11HUEBUT-HUE | 46 | 50m | 46/49-53/9220 | 49-49 | 3 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| ATPMATCH-26JUL11MONHER-HER | 38 | 11m | 1/42-42/9 | 41-42 | 4 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |
| ATPMATCH-26JUL11TABJEB-TAB | 90 | 140m | 57/92-93/3959 | 92-93 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFMATCH-26JUL11DOUROB-DOU | 86 | 82m | 3/91-91/3 | 87-91 | 5 | **FLOW_ABOVE** | 86 | flow above but bound 86c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11DURBAR-BAR | 39 | 127m | 2/40-40/25 | 39-40 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |
| ITFMATCH-26JUL11DURBAR-DUR | 60 | 48m | 2/61-61/16 | 60-61 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ITFMATCH-26JUL11FABARZ-ARZ | 71 | 75m | 2/73-73/14 | 71-73 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL11FABARZ-FAB | 28 | 81m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11LAGRIV-RIV | 28 | 117m | 3/33-33/90 | 30-33 | 5 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11MILARS-ARS | 19 | 88m | 3/20-21/84 | 19-21 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL11MILARS-MIL | 78 | 10m | 0 | 78-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11NORKOI-KOI | 36 | 58m | 1/39-39/2 | 36-39 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFMATCH-26JUL11NORKOI-NOR | 61 | 58m | 1/63-63/1 | 61-63 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFMATCH-26JUL11ORLLOP-LOP | 41 | 88m | 1/45-45/2 | 41-45 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL11ORLLOP-ORL | 56 | 67m | 2/58-58/37 | 56-58 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→58 |
| ITFMATCH-26JUL11RECWIS-REC | 31 | 14m | 0 | 31-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11RECWIS-WIS | 67 | 28m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11ROHBOR-BOR | 44 | 50m | 3/46-46/35 | 44-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFMATCH-26JUL11ROHBOR-ROH | 53 | 30m | 3/55-55/47 | 53-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL11SHIROB-SHI | 29 | 69m | 8/33-35/181 | 34-33 | 4 | **FLOW_ABOVE** | 29 | flow above but bound 29c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11SNIMAZ-MAZ | 20 | 70m | 1/25-25/3 | 23-25 | 5 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11TALPAP-PAP | 54 | 3m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11TALPAP-TAL | 44 | 118m | 3/45-45/10 | 44-45 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL11TYAMON-MON | 67 | 140m | 56/79-84/828 | 79-79 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL11BOSKAR-BOS | 60 | 19m | 0 | 60-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11BOSKAR-KAR | 38 | 58m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11DENSTR-DEN | 51 | 118m | 3/52-53/20 | 51-52 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ITFWMATCH-26JUL11DENSTR-STR | 49 | 136m | 2/50-50/20 | 49-50 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL11FONROJ-FON | 54 | 88m | 3/55-55/3 | 54-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFWMATCH-26JUL11FONROJ-ROJ | 44 | 138m | 3/46-47/6 | 44-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL11HOSCIR-CIR | 35 | 27m | 2/37-37/31 | 35-36 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 137m | 18/64-67/531 | 64-66 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11KALTIK-TIK | 63 | 28m | 2/67-68/58 | 64-64 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KARSUP-KAR | 59 | 115m | 11/59-61/135 | 59-60 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11KARSUP-SUP | 40 | 124m | 4/42-42/78 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ITFWMATCH-26JUL11KUBRYS-KUB | 66 | 137m | 13/67-68/919 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KUBRYS-RYS | 33 | 27m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11LEEJOR-JOR | 43 | 27m | 2/43-46/2 | 43-45 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11LEEJOR-LEE | 55 | 28m | 1/57-57/1 | 55-57 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFWMATCH-26JUL11PERWIE-PER | 81 | 139m | 2/82-82/1 | 81-82 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL11PERWIE-WIE | 18 | 138m | 7/19-20/242 | 18-19 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ITFWMATCH-26JUL11SHEYAM-SHE | 46 | 138m | 2/48-48/35 | 46-48 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFWMATCH-26JUL11SHEYAM-YAM | 52 | 110m | 14/54-54/217 | 52-54 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFWMATCH-26JUL11SMILEY-LEY | 61 | 28m | 12/63-64/875 | 61-62 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 137m | 21/39-39/963 | 38-39 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFWMATCH-26JUL11STATOM-STA | 62 | 138m | 6/62-63/143 | 62-63 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11STATOM-TOM | 36 | 137m | 4/36-40/20 | 36-38 | 0 | **FLOW_AT_LEVEL** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL11SNIMAZ | 75 | 25 | **100** | 97 | +3 |
| ATPMATCH-26JUL11HUEBUT | 51 | 49 | **100** | 97 | +3 |
| ITFMATCH-26JUL11SHIROB | 68 | 33 | **101** | 97 | +4 |
| ATPMATCH-26JUL11MONHER | 59 | 42 | **101** | 97 | +4 |
| ITFMATCH-26JUL11LAGRIV | 69 | 33 | **102** | 97 | +5 |
| ITFMATCH-26JUL11DOUROB | 11 | 91 | **102** | 97 | +5 |

## FLOW-STATE — 31 tracked game(s) ({'WAKING': 23, 'OPEN': 8}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL11MONHER | ATP_MAIN | 1.467 | 1 | **OPEN** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 0.333 | 1 | **OPEN** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.333 | 1 | **OPEN** |
| ITFWMATCH-26JUL11KARSUP | ITF_W | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL11SHEYAM | ITF_W | 0.3 | 2 | **OPEN** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.5 | 1 | **OPEN** |
| ITFWMATCH-26JUL11STATOM | ITF_W | 0.2 | 1 | **OPEN** |
| ATPMATCH-26JUL11HUEBUT | ATP_MAIN | 2.733 | — | **WAKING** |
| ATPMATCH-26JUL11TABJEB | ATP_MAIN | 0.467 | 1 | **WAKING** |
| ITFMATCH-26JUL11DOUROB | ITF_M | 0.6 | 4 | **WAKING** |
| ITFMATCH-26JUL11DURBAR | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL11FABARZ | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11LAGRIV | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL11MILARS | ITF_M | 0.1 | 2 | **WAKING** |
| ITFMATCH-26JUL11NORKOI | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL11ORLLOP | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL11RECWIS | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11ROHBOR | ITF_M | 0.133 | 2 | **WAKING** |
| ITFMATCH-26JUL11SNIMAZ | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL11TALPAP | ITF_M | 0.167 | 1 | **WAKING** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.6 | — | **WAKING** |
| ITFWMATCH-26JUL11BOSKAR | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11DENSTR | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11FONROJ | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL11KALTIK | ITF_W | 0.067 | — | **WAKING** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL11LEEJOR | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 119.767 | — | **WAKING** |
| ITFWMATCH-26JUL11PERWIE | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SAGYOD | ITF_W | 11.4 | — | **WAKING** |

## PATTERNS (sub-B) — 7
- half_arm_aging: KXITFWMATCH-26JUL11MAKSHO-SHO {"fill": 50, "age_min": 118, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL11LAGRIV-LAG {"fill": 69, "age_min": 117, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFWMATCH-26JUL11ERCHRU-HRU {"fill": 82, "age_min": 94, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL11DOUROB-ROB {"fill": 11, "age_min": 86, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFMATCH-26JUL11SNIMAZ-SNI {"fill": 75, "age_min": 72, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFMATCH-26JUL11SHIROB-ROB {"fill": 68, "age_min": 69, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPMATCH-26JUL11HUEBUT-BUT {"fill": 51, "age_min": 50, "mode": "SET_BELOW_FLOW(prints 3c above)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
