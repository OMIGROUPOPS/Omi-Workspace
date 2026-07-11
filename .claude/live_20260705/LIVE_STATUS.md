# LIVE VALIDATION — rolling status

- cycle 51 @ **2026-07-11 01:37:46 AM ET** | build `0abfe918` | session boot 07-11 00:38 ET | log `live_v3_20260711.jsonl` | 3810 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 2 item(s)
- **half_arm_aging**: KXITFWMATCH-26JUL11MAKSHO-SHO {"fill": 50, "age_min": 37, "mode": "PAIRING(sib never rested)"}
- **half_arm_aging**: KXITFMATCH-26JUL11LAGRIV-LAG {"fill": 69, "age_min": 36, "mode": "SET_BELOW_FLOW(prints 5c above)", "emitted_et": "2026-07-11 01:37:46 AM ET"}
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 5 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:00 | ITFWMATCH-26JUL11MAKSHO-SHO | ITF_W | ? | 50 | 48 | +2 (fill_est) | — | pre | single |  | PENDING |
| 01:01 | ITFMATCH-26JUL11LAGRIV-LAG | ITF_M | leader | 69 | 67 | +2 (place_cell) | — | pre | single |  | PENDING |
| 01:25 | ITFWMATCH-26JUL11ERCHRU-HRU | ITF_W | ? | 82 | 80 | +2 (fill_est) | — | pre | single |  | PENDING |
| 01:33 | ITFMATCH-26JUL11DOUROB-ROB | ITF_M | underdog | 11 | 6 | +5 (place_cell) | — | pre | single |  | PENDING |
| 01:34 | ITFWMATCH-26JUL11SAGYOD-SAG | ITF_W | underdog | 41 | 38 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 30 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 17, 'NO_FLOW': 11, 'FLOW_AT_LEVEL': 2} | repriceable now: true 14 / false 16 | **cumulative bid_grade lines: 8001 (repriceable true 1105 / false 6896)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL11TABJEB-TAB | 90 | 59m | 9/92-93/69 | 92-93 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFMATCH-26JUL11DOUROB-DOU | 86 | 1m | 0 | 87-91 | — | **NO_FLOW** | 86 |  |
| ITFMATCH-26JUL11DURBAR-BAR | 39 | 46m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11LAGRIV-RIV | 28 | 36m | 1/33-33/2 | 30-33 | 5 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| ITFMATCH-26JUL11MILARS-ARS | 19 | 7m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11ORLLOP-LOP | 41 | 7m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11SHIROB-ROB | 68 | 57m | 2/69-70/21 | 68-69 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFMATCH-26JUL11SHIROB-SHI | 31 | 55m | 1/32-32/0 | 31-33 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→32 |
| ITFMATCH-26JUL11SNIMAZ-MAZ | 23 | 37m | 0 | 23-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11SNIMAZ-SNI | 75 | 2m | 0 | 75-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11TALPAP-TAL | 44 | 37m | 1/45-45/5 | 44-45 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL11TYAMON-MON | 67 | 59m | 15/79-83/101 | 79-79 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL11DENSTR-DEN | 51 | 37m | 0 | 51-53 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11DENSTR-STR | 49 | 55m | 1/50-50/1 | 49-50 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL11FONROJ-FON | 54 | 7m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11FONROJ-ROJ | 44 | 57m | 0 | 44-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11HOSCIR-CIR | 33 | 57m | 2/37-37/42 | 33-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 57m | 4/67-67/63 | 64-66 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KARSUP-KAR | 59 | 34m | 3/59-61/25 | 59-60 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11KARSUP-SUP | 40 | 43m | 1/42-42/13 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ITFWMATCH-26JUL11KUBRYS-KUB | 66 | 57m | 3/67-67/36 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KUBRYS-RYS | 32 | 59m | 2/33-34/273 | 32-34 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→33 |
| ITFWMATCH-26JUL11PERWIE-PER | 81 | 58m | 1/82-82/0 | 81-82 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL11PERWIE-WIE | 18 | 58m | 4/19-20/129 | 18-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ITFWMATCH-26JUL11SAGYOD-YOD | 56 | 4m | 5/60-61/48 | 60-60 | 4 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL11SHEYAM-SHE | 46 | 57m | 0 | 46-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11SHEYAM-YAM | 52 | 29m | 1/54-54/3 | 52-54 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 57m | 9/39-39/501 | 38-39 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFWMATCH-26JUL11STATOM-STA | 62 | 57m | 1/62-62/5 | 62-63 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11STATOM-TOM | 36 | 57m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL11SAGYOD | 41 | 60 | **101** | 97 | +4 |
| ITFMATCH-26JUL11LAGRIV | 69 | 33 | **102** | 97 | +5 |
| ITFMATCH-26JUL11DOUROB | 11 | 91 | **102** | 97 | +5 |

## FLOW-STATE — 22 tracked game(s) ({'WAKING': 20, 'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 0.333 | 1 | **OPEN** |
| ITFWMATCH-26JUL11SAGYOD | ITF_W | 2.867 | 1 | **OPEN** |
| ATPMATCH-26JUL11TABJEB | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL11DOUROB | ITF_M | 0.2 | 4 | **WAKING** |
| ITFMATCH-26JUL11DURBAR | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11LAGRIV | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL11MILARS | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11ORLLOP | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL11SNIMAZ | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL11TALPAP | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.4 | — | **WAKING** |
| ITFWMATCH-26JUL11DENSTR | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11FONROJ | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL11KARSUP | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 8.567 | — | **WAKING** |
| ITFWMATCH-26JUL11PERWIE | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SHEYAM | ITF_W | 0.167 | 2 | **WAKING** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11STATOM | ITF_W | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 2
- half_arm_aging: KXITFWMATCH-26JUL11MAKSHO-SHO {"fill": 50, "age_min": 37, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL11LAGRIV-LAG {"fill": 69, "age_min": 36, "mode": "SET_BELOW_FLOW(prints 5c above)", "emitted_et": "2026-07-11 01:37:46 AM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
