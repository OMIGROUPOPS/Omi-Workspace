# LIVE VALIDATION — rolling status

- cycle 44 @ **2026-07-11 12:26:47 AM ET** | build `0fa9f4c8` | session boot 07-10 23:26 ET | log `live_v3_20260710.jsonl` | 2622 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:38 | ITFWMATCH-26JUL11MAKSHO-MAK | ITF_W | underdog | 47 | 45 | +2 (place_cell) | — | pre | single |  | PENDING |
| 23:38 | ITFWMATCH-26JUL11ERCHRU-ERC | ITF_W | underdog | 15 | 13 | +2 (place_cell) | — | pre | single |  | PENDING |
| 00:10 | ITFMATCH-26JUL11TYAMON-TYA | ITF_M | underdog | 17 | 15 | +2 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 17 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 9, 'NO_FLOW': 7, 'FLOW_AT_LEVEL': 1} | repriceable now: true 8 / false 9 | **cumulative bid_grade lines: 7940 (repriceable true 1084 / false 6856)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL11TABJEB-JEB | 7 | 26m | 11/8-8/681 | 7-8 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL11SHIROB-ROB | 68 | 8m | 2/70-70/3 | 68-70 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| ITFMATCH-26JUL11SHIROB-SHI | 31 | 53m | 1/32-32/29 | 31-32 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→32 |
| ITFMATCH-26JUL11TYAMON-MON | 80 | 16m | 0 | 81-83 | — | **NO_FLOW** | 80 |  |
| ITFWMATCH-26JUL11DENSTR-DEN | 49 | 26m | 1/53-53/3 | 49-53 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→53 |
| ITFWMATCH-26JUL11ERCHRU-HRU | 82 | 45m | 12/82-85/552 | 83-84 | 0 | **FLOW_AT_LEVEL** | 82 |  |
| ITFWMATCH-26JUL11HOSCIR-CIR | 33 | 56m | 6/34-34/471 | 34-34 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 56m | 3/66-66/37 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFWMATCH-26JUL11KARSUP-KAR | 59 | 23m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11KUBRYS-KUB | 66 | 1m | 0 | 66-67 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11KUBRYS-RYS | 33 | 56m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11MAKSHO-SHO | 50 | 49m | 52/53-55/4065 | 54-54 | 3 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL11SHEYAM-SHE | 46 | 26m | 1/48-48/4 | 46-48 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFWMATCH-26JUL11SHEYAM-YAM | 51 | 26m | 0 | 51-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 56m | 3/39-39/5 | 38-39 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFWMATCH-26JUL11STATOM-STA | 62 | 8m | 0 | 62-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11STATOM-TOM | 36 | 26m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL11ERCHRU | 15 | 84 | **99** | 97 | +2 |
| ITFMATCH-26JUL11TYAMON | 17 | 83 | **100** | 97 | +3 |
| ITFWMATCH-26JUL11MAKSHO | 47 | 54 | **101** | 97 | +4 |

## FLOW-STATE — 12 tracked game(s) ({'WAKING': 9, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 1.167 | 1 | **OPEN** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.233 | 2 | **OPEN** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 2.367 | 1 | **OPEN** |
| ATPMATCH-26JUL11TABJEB | ATP_MAIN | 0.4 | 1 | **WAKING** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.133 | 2 | **WAKING** |
| ITFWMATCH-26JUL11DENSTR | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL11KARSUP | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SHEYAM | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11STATOM | ITF_W | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 4
- reality_divergence: KXITFMATCH-26JUL10DELJAS-DEL {"kind": "position_basis", "ref": 71.0, "market_mid": 38.0, "divergence": 33.0}
- half_arm_aging: KXITFWMATCH-26JUL11MAKSHO-MAK {"fill": 47, "age_min": 49, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL11ERCHRU-ERC {"fill": 15, "age_min": 49, "mode": "QUEUE(flow at/below our level, unfilled)"}
- reality_divergence: KXITFMATCH-26JUL10DELJAS-DEL {"kind": "position_basis", "ref": 71.0, "market_mid": 31.0, "divergence": 40.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
