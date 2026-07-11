# LIVE VALIDATION — rolling status

- cycle 41 @ **2026-07-10 11:55:26 PM ET** | build `9240473a` | session boot 07-10 23:26 ET | log `live_v3_20260710.jsonl` | 930 session events | monitor READ-ONLY

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

## RESTING BIDS — 9 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 5, 'NO_FLOW': 3, 'FLOW_AT_LEVEL': 1} | repriceable now: true 4 / false 5 | **cumulative bid_grade lines: 7924 (repriceable true 1078 / false 6846)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL11SHIROB-SHI | 31 | 22m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11TYAMON-TYA | 17 | 25m | 3/19-19/30 | 17-19 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ITFWMATCH-26JUL11ERCHRU-HRU | 82 | 14m | 3/82-84/370 | 83-84 | 0 | **FLOW_AT_LEVEL** | 82 |  |
| ITFWMATCH-26JUL11HOSCIR-CIR | 33 | 25m | 1/34-34/28 | 33-34 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 25m | 1/66-66/1 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFWMATCH-26JUL11KUBRYS-KUB | 65 | 25m | 3/67-67/21 | 65-67 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KUBRYS-RYS | 33 | 25m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11MAKSHO-SHO | 50 | 17m | 10/53-54/469 | 53-54 | 3 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 25m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL11ERCHRU | 15 | 84 | **99** | 97 | +2 |
| ITFWMATCH-26JUL11MAKSHO | 47 | 54 | **101** | 97 | +4 |

## FLOW-STATE — 7 tracked game(s) ({'WAKING': 5, 'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 0.667 | 1 | **OPEN** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 1.067 | 1 | **OPEN** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- reality_divergence: KXITFMATCH-26JUL10DELJAS-DEL {"kind": "position_basis", "ref": 71.0, "market_mid": 38.0, "divergence": 33.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
