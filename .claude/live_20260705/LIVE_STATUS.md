# LIVE VALIDATION — rolling status

- cycle 40 @ **2026-07-10 11:44:55 PM ET** | build `1ea1a3c4` | session boot 07-10 23:26 ET | log `live_v3_20260710.jsonl` | 769 session events | monitor READ-ONLY

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
- classes now: {'NO_FLOW': 7, 'FLOW_ABOVE': 2} | repriceable now: true 2 / false 7 | **cumulative bid_grade lines: 7920 (repriceable true 1076 / false 6844)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL11SHIROB-SHI | 31 | 11m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11TYAMON-TYA | 17 | 15m | 0 | 17-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11ERCHRU-HRU | 82 | 3m | 0 | 83-84 | — | **NO_FLOW** | 82 |  |
| ITFWMATCH-26JUL11HOSCIR-CIR | 33 | 14m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 14m | 1/66-66/1 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFWMATCH-26JUL11KUBRYS-KUB | 65 | 14m | 1/67-67/1 | 65-67 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KUBRYS-RYS | 33 | 14m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11MAKSHO-SHO | 50 | 7m | 0 | 53-55 | — | **NO_FLOW** | 50 |  |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 14m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL11ERCHRU | 15 | 84 | **99** | 97 | +2 |
| ITFWMATCH-26JUL11MAKSHO | 47 | 55 | **102** | 97 | +5 |

## FLOW-STATE — 7 tracked game(s) ({'WAKING': 5, 'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 0.833 | 1 | **OPEN** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 0.8 | 1 | **OPEN** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- reality_divergence: KXITFMATCH-26JUL10DELJAS-DEL {"kind": "position_basis", "ref": 71.0, "market_mid": 38.0, "divergence": 33.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
