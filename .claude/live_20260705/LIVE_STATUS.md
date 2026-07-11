# LIVE VALIDATION — rolling status

- cycle 62 @ **2026-07-11 03:29:18 AM ET** | build `d4bf1094` | session boot 07-11 00:38 ET | log `live_v3_20260711.jsonl` | 8174 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 8 item(s)
- **half_arm_aging**: KXITFWMATCH-26JUL11MAKSHO-SHO {"fill": 50, "age_min": 149, "mode": "PAIRING(sib never rested)"}
- **half_arm_aging**: KXITFMATCH-26JUL11LAGRIV-LAG {"fill": 69, "age_min": 148, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- **half_arm_aging**: KXITFWMATCH-26JUL11ERCHRU-HRU {"fill": 82, "age_min": 124, "mode": "PAIRING(sib never rested)"}
- **half_arm_aging**: KXITFMATCH-26JUL11DOUROB-ROB {"fill": 11, "age_min": 116, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- **half_arm_aging**: KXITFMATCH-26JUL11SNIMAZ-SNI {"fill": 75, "age_min": 102, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- **half_arm_aging**: KXITFMATCH-26JUL11SHIROB-ROB {"fill": 68, "age_min": 99, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- **half_arm_aging**: KXATPMATCH-26JUL11HUEBUT-BUT {"fill": 51, "age_min": 81, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- **half_arm_aging**: KXATPMATCH-26JUL11MONHER-MON {"fill": 59, "age_min": 43, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 12 graded (session)
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
| 03:23 | ITFWMATCH-26JUL11SHEYAM-YAM | ITF_W | leader | 53 | 50 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 48 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 33, 'FLOW_AT_LEVEL': 6, 'NO_FLOW': 9} | repriceable now: true 26 / false 22 | **cumulative bid_grade lines: 8070 (repriceable true 1133 / false 6937)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL11HUEBUT-HUE | 46 | 81m | 66/49-53/11462 | 49-49 | 3 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| ATPMATCH-26JUL11MONHER-HER | 38 | 42m | 7/42-42/551 | 41-42 | 4 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |
| ATPMATCH-26JUL11TABJEB-TAB | 90 | 170m | 63/92-94/7148 | 93-93 | 2 | **FLOW_ABOVE** | 93 | REPRICEABLE→92 |
| ATPMATCH-26JUL11VIRDIE-DIE | 33 | 29m | 1/35-35/3 | 34-34 | 2 | **FLOW_ABOVE** | 34 | REPRICEABLE→34 |
| ATPMATCH-26JUL11VIRDIE-VIR | 65 | 29m | 19/65-67/3963 | 66-66 | 0 | **FLOW_AT_LEVEL** | 67 |  |
| ITFMATCH-26JUL11DOUROB-DOU | 86 | 113m | 11/89-91/295 | 88-91 | 3 | **FLOW_ABOVE** | 86 | flow above but bound 86c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11DURBAR-BAR | 39 | 158m | 2/40-40/25 | 39-40 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |
| ITFMATCH-26JUL11DURBAR-DUR | 60 | 79m | 3/61-61/19 | 60-61 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ITFMATCH-26JUL11FABARZ-ARZ | 71 | 106m | 7/73-73/183 | 71-73 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL11FABARZ-FAB | 28 | 111m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11LAGRIV-RIV | 28 | 148m | 5/33-33/92 | 30-33 | 5 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11MILARS-ARS | 19 | 118m | 3/20-21/84 | 19-21 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL11MILARS-MIL | 78 | 41m | 0 | 78-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11NICJUA-JUA | 25 | 16m | 1/26-26/3 | 25-26 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFMATCH-26JUL11NORKOI-KOI | 36 | 88m | 1/39-39/2 | 36-39 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFMATCH-26JUL11NORKOI-NOR | 61 | 88m | 2/63-63/5 | 61-63 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFMATCH-26JUL11ORLLOP-LOP | 41 | 118m | 1/45-45/2 | 41-44 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL11ORLLOP-ORL | 56 | 98m | 3/58-58/43 | 56-58 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→58 |
| ITFMATCH-26JUL11RECWIS-REC | 31 | 44m | 0 | 31-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11RECWIS-WIS | 67 | 58m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11ROHBOR-BOR | 45 | 21m | 0 | 45-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11ROHBOR-ROH | 53 | 60m | 5/54-55/51 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL11SHIROB-SHI | 29 | 99m | 23/33-39/1375 | 35-33 | 4 | **FLOW_ABOVE** | 29 | flow above but bound 29c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11SNIMAZ-MAZ | 20 | 100m | 2/25-25/6 | 23-25 | 5 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11TALPAP-PAP | 54 | 34m | 1/55-55/4 | 54-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL11TALPAP-TAL | 44 | 148m | 3/45-45/10 | 44-45 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL11TYAMON-MON | 67 | 170m | 76/79-84/1237 | 79-79 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL11BOSKAR-BOS | 60 | 50m | 0 | 60-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11BOSKAR-KAR | 38 | 88m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11DENSTR-DEN | 51 | 148m | 3/52-53/20 | 51-52 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ITFWMATCH-26JUL11DENSTR-STR | 49 | 166m | 6/50-50/624 | 49-50 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL11FONROJ-FON | 54 | 118m | 4/55-55/11 | 54-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFWMATCH-26JUL11FONROJ-ROJ | 44 | 168m | 4/46-47/11 | 44-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL11HOSCIR-CIR | 35 | 57m | 9/35-38/55 | 35-36 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 168m | 26/64-67/751 | 64-66 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11KALTIK-TIK | 63 | 58m | 6/67-68/160 | 66-64 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KARSUP-KAR | 59 | 146m | 12/59-61/139 | 59-60 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11KARSUP-SUP | 40 | 155m | 5/42-42/87 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ITFWMATCH-26JUL11KUBRYS-KUB | 66 | 168m | 19/67-69/1056 | 67-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KUBRYS-RYS | 33 | 58m | 1/34-34/195 | 33-34 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL11LEEJOR-JOR | 43 | 58m | 2/43-46/2 | 43-45 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11LEEJOR-LEE | 55 | 58m | 3/57-57/6 | 55-57 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFWMATCH-26JUL11PERWIE-PER | 81 | 169m | 9/82-85/263 | 81-82 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL11PERWIE-WIE | 18 | 169m | 9/19-20/374 | 18-19 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ITFWMATCH-26JUL11SHEYAM-SHE | 43 | 6m | 0 | 46-48 | — | **NO_FLOW** | 44 |  |
| ITFWMATCH-26JUL11SMILEY-LEY | 61 | 59m | 20/63-64/1288 | 62-62 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 168m | 26/38-40/1040 | 38-39 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11STATOM-TOM | 35 | 10m | 0 | 36-38 | — | **NO_FLOW** | 35 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL11MAKSHO | 50 | 31 | **81** | 97 | -16 |
| ITFMATCH-26JUL11SNIMAZ | 75 | 25 | **100** | 97 | +3 |
| ATPMATCH-26JUL11HUEBUT | 51 | 49 | **100** | 97 | +3 |
| ITFWMATCH-26JUL11STATOM | 62 | 38 | **100** | 97 | +3 |
| ITFMATCH-26JUL11SHIROB | 68 | 33 | **101** | 97 | +4 |
| ATPMATCH-26JUL11MONHER | 59 | 42 | **101** | 97 | +4 |
| ITFWMATCH-26JUL11SHEYAM | 53 | 48 | **101** | 97 | +4 |
| ITFMATCH-26JUL11LAGRIV | 69 | 33 | **102** | 97 | +5 |
| ITFMATCH-26JUL11DOUROB | 11 | 91 | **102** | 97 | +5 |

## FLOW-STATE — 33 tracked game(s) ({'WAKING': 25, 'OPEN': 8}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL11MONHER | ATP_MAIN | 0.867 | 1 | **OPEN** |
| ITFMATCH-26JUL11DOUROB | ITF_M | 0.367 | 3 | **OPEN** |
| ITFMATCH-26JUL11LAGRIV | ITF_M | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.5 | 1 | **OPEN** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.233 | 1 | **OPEN** |
| ITFWMATCH-26JUL11PERWIE | ITF_W | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.433 | 1 | **OPEN** |
| ITFWMATCH-26JUL11STATOM | ITF_W | 0.233 | 1 | **OPEN** |
| ATPMATCH-26JUL11HUEBUT | ATP_MAIN | 1.567 | — | **WAKING** |
| ATPMATCH-26JUL11TABJEB | ATP_MAIN | 0.2 | — | **WAKING** |
| ATPMATCH-26JUL11VIRDIE | ATP_MAIN | 0.7 | — | **WAKING** |
| ITFMATCH-26JUL11DURBAR | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL11FABARZ | ITF_M | 0.167 | 1 | **WAKING** |
| ITFMATCH-26JUL11MILARS | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL11NICJUA | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL11NORKOI | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL11ORLLOP | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL11RECWIS | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11ROHBOR | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.6 | — | **WAKING** |
| ITFMATCH-26JUL11SNIMAZ | ITF_M | 0.1 | 2 | **WAKING** |
| ITFMATCH-26JUL11TALPAP | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.667 | — | **WAKING** |
| ITFWMATCH-26JUL11BOSKAR | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL11DENSTR | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 0.567 | — | **WAKING** |
| ITFWMATCH-26JUL11FONROJ | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11KALTIK | ITF_W | 0.1 | — | **WAKING** |
| ITFWMATCH-26JUL11KARSUP | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11LEEJOR | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 134.833 | — | **WAKING** |
| ITFWMATCH-26JUL11SAGYOD | ITF_W | 12.233 | — | **WAKING** |
| ITFWMATCH-26JUL11SHEYAM | ITF_W | 0.133 | 1 | **WAKING** |

## PATTERNS (sub-B) — 8
- half_arm_aging: KXITFWMATCH-26JUL11MAKSHO-SHO {"fill": 50, "age_min": 149, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL11LAGRIV-LAG {"fill": 69, "age_min": 148, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFWMATCH-26JUL11ERCHRU-HRU {"fill": 82, "age_min": 124, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL11DOUROB-ROB {"fill": 11, "age_min": 116, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFMATCH-26JUL11SNIMAZ-SNI {"fill": 75, "age_min": 102, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFMATCH-26JUL11SHIROB-ROB {"fill": 68, "age_min": 99, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPMATCH-26JUL11HUEBUT-BUT {"fill": 51, "age_min": 81, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPMATCH-26JUL11MONHER-MON {"fill": 59, "age_min": 43, "mode": "SET_BELOW_FLOW(prints 4c above)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
