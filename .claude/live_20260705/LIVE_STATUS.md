# LIVE VALIDATION — rolling status

- cycle 45 @ **2026-07-11 12:37:11 AM ET** | build `dce5ef7c` | session boot 07-10 23:26 ET | log `live_v3_20260710.jsonl` | 3013 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 4 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:38 | ITFWMATCH-26JUL11MAKSHO-MAK | ITF_W | underdog | 47 | 45 | +2 (place_cell) | — | pre | single |  | PENDING |
| 23:38 | ITFWMATCH-26JUL11ERCHRU-ERC | ITF_W | underdog | 15 | 13 | +2 (place_cell) | — | pre | single |  | PENDING |
| 00:10 | ITFMATCH-26JUL11TYAMON-TYA | ITF_M | underdog | 17 | 15 | +2 (place_cell) | — | pre | single |  | PENDING |
| 00:34 | ATPMATCH-26JUL11TABJEB-JEB | ATP_MAIN | underdog | 7 | 6 | +1 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 22 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 12, 'NO_FLOW': 9, 'FLOW_AT_LEVEL': 1} | repriceable now: true 10 / false 12 | **cumulative bid_grade lines: 7951 (repriceable true 1088 / false 6863)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL11TABJEB-TAB | 90 | 3m | 0 | 92-93 | — | **NO_FLOW** | 90 |  |
| ITFMATCH-26JUL11DOUROB-DOU | 88 | 6m | 0 | 88-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11DOUROB-ROB | 10 | 6m | 0 | 10-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11SHIROB-ROB | 68 | 19m | 2/70-70/3 | 68-70 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| ITFMATCH-26JUL11SHIROB-SHI | 31 | 64m | 1/32-32/29 | 31-32 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→32 |
| ITFMATCH-26JUL11TYAMON-MON | 80 | 26m | 2/81-81/17 | 81-83 | 1 | **FLOW_ABOVE** | 80 | flow above but bound 80c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL11DENSTR-DEN | 50 | 7m | 1/52-52/0 | 50-52 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ITFWMATCH-26JUL11DENSTR-STR | 49 | 5m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11ERCHRU-HRU | 82 | 55m | 14/82-85/587 | 83-84 | 0 | **FLOW_AT_LEVEL** | 82 |  |
| ITFWMATCH-26JUL11FONROJ-ROJ | 44 | 7m | 0 | 44-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11HOSCIR-CIR | 33 | 67m | 6/34-34/471 | 33-34 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 67m | 4/66-66/181 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFWMATCH-26JUL11KARSUP-KAR | 59 | 33m | 1/61-61/3 | 59-61 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ITFWMATCH-26JUL11KUBRYS-KUB | 66 | 11m | 3/67-67/160 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KUBRYS-RYS | 33 | 67m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11MAKSHO-SHO | 50 | 59m | 70/53-55/5372 | 53-54 | 3 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL11PERWIE-WIE | 18 | 4m | 0 | 18-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11SHEYAM-SHE | 46 | 36m | 1/48-48/4 | 46-48 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFWMATCH-26JUL11SHEYAM-YAM | 52 | 5m | 1/54-54/0 | 52-54 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 67m | 3/39-39/5 | 38-39 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFWMATCH-26JUL11STATOM-STA | 62 | 19m | 0 | 62-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11STATOM-TOM | 36 | 36m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL11ERCHRU | 15 | 84 | **99** | 97 | +2 |
| ITFMATCH-26JUL11TYAMON | 17 | 83 | **100** | 97 | +3 |
| ATPMATCH-26JUL11TABJEB | 7 | 93 | **100** | 97 | +3 |
| ITFWMATCH-26JUL11MAKSHO | 47 | 54 | **101** | 97 | +4 |

## FLOW-STATE — 15 tracked game(s) ({'OPEN': 6, 'WAKING': 9}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL11TABJEB | ATP_MAIN | 1.467 | 1 | **OPEN** |
| ITFMATCH-26JUL11DOUROB | ITF_M | 0.533 | 2 | **OPEN** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.2 | 2 | **OPEN** |
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 1.0 | 1 | **OPEN** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.233 | 1 | **OPEN** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 3.267 | 1 | **OPEN** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL11DENSTR | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11FONROJ | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL11KARSUP | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL11PERWIE | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SHEYAM | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL11STATOM | ITF_W | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 4
- reality_divergence: KXITFMATCH-26JUL10DELJAS-DEL {"kind": "position_basis", "ref": 71.0, "market_mid": 38.0, "divergence": 33.0}
- half_arm_aging: KXITFWMATCH-26JUL11MAKSHO-MAK {"fill": 47, "age_min": 59, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL11ERCHRU-ERC {"fill": 15, "age_min": 59, "mode": "QUEUE(flow at/below our level, unfilled)"}
- reality_divergence: KXITFMATCH-26JUL10DELJAS-DEL {"kind": "position_basis", "ref": 71.0, "market_mid": 31.0, "divergence": 40.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
