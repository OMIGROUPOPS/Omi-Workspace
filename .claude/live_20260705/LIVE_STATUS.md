# LIVE VALIDATION — rolling status

- cycle 42 @ **2026-07-11 12:05:47 AM ET** | build `5895039d` | session boot 07-10 23:26 ET | log `live_v3_20260710.jsonl` | 1941 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:38 | ITFWMATCH-26JUL11MAKSHO-MAK | ITF_W | underdog | 47 | 45 | +2 (place_cell) | — | pre | single |  | PENDING |
| 23:38 | ITFWMATCH-26JUL11ERCHRU-ERC | ITF_W | underdog | 15 | 13 | +2 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 16 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 9, 'FLOW_AT_LEVEL': 1} | repriceable now: true 5 / false 11 | **cumulative bid_grade lines: 7932 (repriceable true 1079 / false 6853)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL11TABJEB-JEB | 7 | 5m | 0 | 7-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11SHIROB-SHI | 31 | 32m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11TYAMON-MON | 81 | 1m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11TYAMON-TYA | 17 | 36m | 4/19-19/125 | 17-19 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ITFWMATCH-26JUL11DENSTR-DEN | 49 | 5m | 0 | 49-53 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11ERCHRU-HRU | 82 | 24m | 5/82-85/373 | 83-84 | 0 | **FLOW_AT_LEVEL** | 82 |  |
| ITFWMATCH-26JUL11HOSCIR-CIR | 33 | 35m | 1/34-34/28 | 33-34 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 35m | 2/66-66/1 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFWMATCH-26JUL11KARSUP-KAR | 59 | 2m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11KUBRYS-KUB | 65 | 35m | 3/67-67/21 | 65-67 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KUBRYS-RYS | 33 | 35m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11MAKSHO-SHO | 50 | 28m | 14/53-55/727 | 53-54 | 3 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL11SHEYAM-SHE | 46 | 5m | 0 | 46-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11SHEYAM-YAM | 51 | 5m | 0 | 51-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 35m | 3/39-39/5 | 38-39 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFWMATCH-26JUL11STATOM-TOM | 36 | 5m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL11ERCHRU | 15 | 84 | **99** | 97 | +2 |
| ITFWMATCH-26JUL11MAKSHO | 47 | 54 | **101** | 97 | +4 |

## FLOW-STATE — 12 tracked game(s) ({'WAKING': 10, 'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 0.8 | 1 | **OPEN** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 1.167 | 1 | **OPEN** |
| ATPMATCH-26JUL11TABJEB | ATP_MAIN | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.133 | 2 | **WAKING** |
| ITFWMATCH-26JUL11DENSTR | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11KARSUP | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SHEYAM | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL11STATOM | ITF_W | 0.0 | 3 | **WAKING** |

## PATTERNS (sub-B) — 2
- reality_divergence: KXITFMATCH-26JUL10DELJAS-DEL {"kind": "position_basis", "ref": 71.0, "market_mid": 38.0, "divergence": 33.0}
- reality_divergence: KXITFMATCH-26JUL10DELJAS-DEL {"kind": "position_basis", "ref": 71.0, "market_mid": 31.0, "divergence": 40.0, "emitted_et": "2026-07-11 12:05:47 AM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
