# LIVE VALIDATION — rolling status

- cycle 65 @ **2026-07-11 03:59:47 AM ET** | build `cd0e6b94` | session boot 07-11 00:38 ET | log `live_v3_20260711.jsonl` | 9333 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 10 item(s)
- **half_arm_aging**: KXITFWMATCH-26JUL11MAKSHO-SHO {"fill": 50, "age_min": 179, "mode": "PAIRING(sib never rested)"}
- **half_arm_aging**: KXITFMATCH-26JUL11LAGRIV-LAG {"fill": 69, "age_min": 178, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- **half_arm_aging**: KXITFWMATCH-26JUL11ERCHRU-HRU {"fill": 82, "age_min": 155, "mode": "PAIRING(sib never rested)"}
- **half_arm_aging**: KXITFMATCH-26JUL11DOUROB-ROB {"fill": 11, "age_min": 147, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- **half_arm_aging**: KXITFMATCH-26JUL11SNIMAZ-SNI {"fill": 75, "age_min": 133, "mode": "STARVATION(no prints since post)"}
- **half_arm_aging**: KXITFMATCH-26JUL11SHIROB-ROB {"fill": 68, "age_min": 130, "mode": "NO_BID(sib rested earlier, none now)"}
- **half_arm_aging**: KXATPMATCH-26JUL11HUEBUT-BUT {"fill": 51, "age_min": 111, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- **half_arm_aging**: KXATPMATCH-26JUL11MONHER-MON {"fill": 59, "age_min": 73, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- **half_arm_aging**: KXITFWMATCH-26JUL11STATOM-STA {"fill": 62, "age_min": 41, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- **half_arm_aging**: KXITFWMATCH-26JUL11SHEYAM-YAM {"fill": 53, "age_min": 36, "mode": "SET_BELOW_FLOW(prints 3c above)", "emitted_et": "2026-07-11 03:59:47 AM ET"}
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 16 graded (session)
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
| 03:32 | ITFWMATCH-26JUL11HOSCIR-HOS | ITF_W | leader | 64 | 64 | +0 (place_cell) | — | pre | single |  | PENDING |
| 03:35 | ITFWMATCH-26JUL11SMILEY-LEY | ITF_W | leader | 61 | 60 | +1 (place_cell) | — | pre | single |  | PENDING |
| 03:42 | ITFWMATCH-26JUL11KUBRYS-RYS | ITF_W | ? | 33 | 29 | +4 (fill_est) | — | pre | single |  | PENDING |
| 03:53 | ITFWMATCH-26JUL11PERWIE-WIE | ITF_W | underdog | 18 | 15 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 45 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 32, 'FLOW_AT_LEVEL': 3, 'NO_FLOW': 10} | repriceable now: true 26 / false 19 | **cumulative bid_grade lines: 8085 (repriceable true 1138 / false 6947)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL11GIUDAM-D | 39 | 29m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL11RINCHO-R | 32 | 29m | 0 | 32-33 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL11CINZAH-CIN | 87 | 8m | 0 | 87-88 | — | **NO_FLOW** | 88 |  |
| ATPMATCH-26JUL11CINZAH-ZAH | 12 | 29m | 2/13-13/72 | 12-13 | 1 | **FLOW_ABOVE** | 11 | flow above but bound 11c < flow -- chasing breaks goal |
| ATPMATCH-26JUL11HUEBUT-HUE | 46 | 111m | 129/49-53/19774 | 50-49 | 3 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| ATPMATCH-26JUL11MONHER-HER | 38 | 73m | 21/42-43/3114 | 42-42 | 4 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |
| ATPMATCH-26JUL11TABJEB-TAB | 90 | 201m | 98/92-95/34759 | 93-93 | 2 | **FLOW_ABOVE** | 93 | REPRICEABLE→92 |
| ATPMATCH-26JUL11VIRDIE-DIE | 33 | 59m | 1/35-35/3 | 34-34 | 2 | **FLOW_ABOVE** | 34 | REPRICEABLE→34 |
| ATPMATCH-26JUL11VIRDIE-VIR | 65 | 59m | 31/65-67/4977 | 66-66 | 0 | **FLOW_AT_LEVEL** | 67 |  |
| ITFMATCH-26JUL11DOUROB-DOU | 86 | 143m | 11/89-91/295 | 87-91 | 3 | **FLOW_ABOVE** | 86 | flow above but bound 86c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11DURBAR-BAR | 39 | 188m | 2/40-40/25 | 39-40 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |
| ITFMATCH-26JUL11DURBAR-DUR | 60 | 109m | 5/61-61/47 | 60-61 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ITFMATCH-26JUL11FABARZ-ARZ | 71 | 136m | 10/73-73/271 | 71-73 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL11FABARZ-FAB | 28 | 142m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11LAGRIV-RIV | 28 | 178m | 10/33-34/766 | 30-33 | 5 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11MILARS-ARS | 19 | 149m | 3/20-21/84 | 19-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL11MILARS-MIL | 78 | 72m | 0 | 78-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11NICJUA-JUA | 25 | 47m | 1/26-26/3 | 25-26 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFMATCH-26JUL11NORKOI-KOI | 36 | 119m | 1/39-39/2 | 36-39 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFMATCH-26JUL11NORKOI-NOR | 61 | 119m | 2/63-63/5 | 61-63 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFMATCH-26JUL11ORLLOP-LOP | 41 | 149m | 1/45-45/2 | 41-44 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL11ORLLOP-ORL | 56 | 128m | 9/58-58/274 | 56-58 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→58 |
| ITFMATCH-26JUL11RECWIS-REC | 31 | 75m | 0 | 31-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11RECWIS-WIS | 67 | 89m | 1/68-68/3 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL11ROHBOR-BOR | 45 | 52m | 2/46-46/220 | 48-46 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFMATCH-26JUL11ROHBOR-ROH | 53 | 91m | 5/54-55/51 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL11SNIMAZ-MAZ | 20 | 22m | 0 | 24-25 | — | **NO_FLOW** | 22 |  |
| ITFMATCH-26JUL11TALPAP-PAP | 54 | 64m | 3/55-55/277 | 56-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL11TALPAP-TAL | 44 | 179m | 3/45-45/10 | 44-45 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFWMATCH-26JUL11BOSKAR-BOS | 60 | 80m | 2/61-61/7 | 60-61 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ITFWMATCH-26JUL11BOSKAR-KAR | 38 | 119m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11DENSTR-DEN | 51 | 179m | 3/52-53/20 | 51-52 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ITFWMATCH-26JUL11DENSTR-STR | 49 | 197m | 13/50-51/841 | 49-50 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL11FONROJ-FON | 54 | 149m | 4/55-55/11 | 54-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFWMATCH-26JUL11FONROJ-ROJ | 44 | 199m | 4/46-47/11 | 44-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL11KALTIK-TIK | 63 | 89m | 9/66-68/162 | 64-64 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFWMATCH-26JUL11KARSUP-KAR | 59 | 176m | 14/59-61/244 | 59-60 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11KARSUP-SUP | 40 | 185m | 8/42-42/592 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ITFWMATCH-26JUL11KOVVED-KOV | 42 | 24m | 0 | 42-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11KOVVED-VED | 56 | 29m | 1/59-59/4 | 56-59 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFWMATCH-26JUL11LEEJOR-JOR | 43 | 89m | 2/43-46/2 | 43-45 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11LEEJOR-LEE | 55 | 89m | 3/57-57/6 | 55-57 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFWMATCH-26JUL11PERWIE-PER | 79 | 7m | 0 | 81-82 | — | **NO_FLOW** | 79 |  |
| ITFWMATCH-26JUL11SHEYAM-SHE | 43 | 36m | 4/46-48/855 | 46-48 | 3 | **FLOW_ABOVE** | 44 | REPRICEABLE→44 |
| ITFWMATCH-26JUL11STATOM-TOM | 35 | 41m | 2/38-38/500 | 36-39 | 3 | **FLOW_ABOVE** | 35 | flow above but bound 35c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL11MAKSHO | 50 | 31 | **81** | 97 | -16 |
| ITFMATCH-26JUL11SNIMAZ | 75 | 25 | **100** | 97 | +3 |
| ATPMATCH-26JUL11HUEBUT | 51 | 49 | **100** | 97 | +3 |
| ITFWMATCH-26JUL11PERWIE | 18 | 82 | **100** | 97 | +3 |
| ATPMATCH-26JUL11MONHER | 59 | 42 | **101** | 97 | +4 |
| ITFWMATCH-26JUL11STATOM | 62 | 39 | **101** | 97 | +4 |
| ITFWMATCH-26JUL11SHEYAM | 53 | 48 | **101** | 97 | +4 |
| ITFMATCH-26JUL11LAGRIV | 69 | 33 | **102** | 97 | +5 |
| ITFMATCH-26JUL11DOUROB | 11 | 91 | **102** | 97 | +5 |

## FLOW-STATE — 36 tracked game(s) ({'WAKING': 31, 'OPEN': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL11LAGRIV | ITF_M | 0.2 | 1 | **OPEN** |
| ITFMATCH-26JUL11ORLLOP | ITF_M | 0.2 | 2 | **OPEN** |
| ITFMATCH-26JUL11SNIMAZ | ITF_M | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL11DENSTR | ITF_W | 0.233 | 1 | **OPEN** |
| ITFWMATCH-26JUL11SHEYAM | ITF_W | 1.0 | 2 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL11GIUDAM | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL11RINCHO | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL11CINZAH | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ATPMATCH-26JUL11HUEBUT | ATP_MAIN | 3.6 | — | **WAKING** |
| ATPMATCH-26JUL11MONHER | ATP_MAIN | 0.933 | — | **WAKING** |
| ATPMATCH-26JUL11TABJEB | ATP_MAIN | 1.167 | — | **WAKING** |
| ATPMATCH-26JUL11VIRDIE | ATP_MAIN | 0.4 | — | **WAKING** |
| ITFMATCH-26JUL11DOUROB | ITF_M | 0.4 | 4 | **WAKING** |
| ITFMATCH-26JUL11DURBAR | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL11FABARZ | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL11MILARS | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11NICJUA | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11NORKOI | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL11RECWIS | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL11ROHBOR | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 5.467 | — | **WAKING** |
| ITFMATCH-26JUL11TALPAP | ITF_M | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11BOSKAR | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 6.933 | — | **WAKING** |
| ITFWMATCH-26JUL11FONROJ | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 5.233 | — | **WAKING** |
| ITFWMATCH-26JUL11KALTIK | ITF_W | 0.1 | — | **WAKING** |
| ITFWMATCH-26JUL11KARSUP | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL11KOVVED | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 3.733 | — | **WAKING** |
| ITFWMATCH-26JUL11LEEJOR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 110.533 | — | **WAKING** |
| ITFWMATCH-26JUL11PERWIE | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SAGYOD | ITF_W | 5.367 | — | **WAKING** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 6.767 | — | **WAKING** |
| ITFWMATCH-26JUL11STATOM | ITF_W | 0.1 | 1 | **WAKING** |

## PATTERNS (sub-B) — 10
- half_arm_aging: KXITFWMATCH-26JUL11MAKSHO-SHO {"fill": 50, "age_min": 179, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL11LAGRIV-LAG {"fill": 69, "age_min": 178, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFWMATCH-26JUL11ERCHRU-HRU {"fill": 82, "age_min": 155, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL11DOUROB-ROB {"fill": 11, "age_min": 147, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFMATCH-26JUL11SNIMAZ-SNI {"fill": 75, "age_min": 133, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFMATCH-26JUL11SHIROB-ROB {"fill": 68, "age_min": 130, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPMATCH-26JUL11HUEBUT-BUT {"fill": 51, "age_min": 111, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPMATCH-26JUL11MONHER-MON {"fill": 59, "age_min": 73, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFWMATCH-26JUL11STATOM-STA {"fill": 62, "age_min": 41, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL11SHEYAM-YAM {"fill": 53, "age_min": 36, "mode": "SET_BELOW_FLOW(prints 3c above)", "emitted_et": "2026-07-11 03:59:47 AM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
