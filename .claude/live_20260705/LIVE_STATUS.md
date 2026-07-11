# LIVE VALIDATION — rolling status

- cycle 43 @ **2026-07-11 12:16:24 AM ET** | build `66af379f` | session boot 07-10 23:26 ET | log `live_v3_20260710.jsonl` | 2270 session events | monitor READ-ONLY

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

## RESTING BIDS — 15 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 8, 'NO_FLOW': 6, 'FLOW_AT_LEVEL': 1} | repriceable now: true 7 / false 8 | **cumulative bid_grade lines: 7936 (repriceable true 1082 / false 6854)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL11TABJEB-JEB | 7 | 15m | 2/8-8/347 | 7-8 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL11SHIROB-SHI | 31 | 43m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11TYAMON-MON | 80 | 6m | 0 | 81-83 | — | **NO_FLOW** | 80 |  |
| ITFWMATCH-26JUL11DENSTR-DEN | 49 | 15m | 1/53-53/3 | 49-53 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→53 |
| ITFWMATCH-26JUL11ERCHRU-HRU | 82 | 35m | 7/82-85/379 | 83-84 | 0 | **FLOW_AT_LEVEL** | 82 |  |
| ITFWMATCH-26JUL11HOSCIR-CIR | 33 | 46m | 2/34-34/247 | 33-34 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 46m | 2/66-66/1 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFWMATCH-26JUL11KARSUP-KAR | 59 | 13m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11KUBRYS-KUB | 65 | 46m | 3/67-67/21 | 65-67 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KUBRYS-RYS | 33 | 46m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11MAKSHO-SHO | 50 | 38m | 33/53-55/3245 | 54-54 | 3 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL11SHEYAM-SHE | 46 | 15m | 1/48-48/4 | 46-48 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFWMATCH-26JUL11SHEYAM-YAM | 51 | 15m | 0 | 51-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 46m | 3/39-39/5 | 38-39 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFWMATCH-26JUL11STATOM-TOM | 36 | 15m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL11ERCHRU | 15 | 84 | **99** | 97 | +2 |
| ITFMATCH-26JUL11TYAMON | 17 | 83 | **100** | 97 | +3 |
| ITFWMATCH-26JUL11MAKSHO | 47 | 54 | **101** | 97 | +4 |

## FLOW-STATE — 12 tracked game(s) ({'WAKING': 10, 'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 0.833 | 1 | **OPEN** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 1.633 | 1 | **OPEN** |
| ATPMATCH-26JUL11TABJEB | ATP_MAIN | 0.167 | 1 | **WAKING** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.167 | 2 | **WAKING** |
| ITFWMATCH-26JUL11DENSTR | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL11KARSUP | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SHEYAM | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL11STATOM | ITF_W | 0.0 | 3 | **WAKING** |

## PATTERNS (sub-B) — 4
- reality_divergence: KXITFMATCH-26JUL10DELJAS-DEL {"kind": "position_basis", "ref": 71.0, "market_mid": 38.0, "divergence": 33.0}
- half_arm_aging: KXITFWMATCH-26JUL11MAKSHO-MAK {"fill": 47, "age_min": 38, "mode": "SET_BELOW_FLOW(prints 3c above)", "emitted_et": "2026-07-11 12:16:24 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL11ERCHRU-ERC {"fill": 15, "age_min": 38, "mode": "QUEUE(flow at/below our level, unfilled)", "emitted_et": "2026-07-11 12:16:24 AM ET"}
- reality_divergence: KXITFMATCH-26JUL10DELJAS-DEL {"kind": "position_basis", "ref": 71.0, "market_mid": 31.0, "divergence": 40.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
