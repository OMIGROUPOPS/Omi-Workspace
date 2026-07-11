# LIVE VALIDATION — rolling status

- cycle 39 @ **2026-07-10 11:34:34 PM ET** | build `3f80deb5` | session boot 07-10 23:26 ET | log `live_v3_20260710.jsonl` | 576 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 0 graded (session)
none yet this session

## RESTING BIDS — 11 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 1, 'FLOW_ABOVE': 3, 'NO_FLOW': 7} | repriceable now: true 3 / false 8 | **cumulative bid_grade lines: 7918 (repriceable true 1076 / false 6842)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10NAKMAT-MAT | 40 | 5m | 20/44-45/382 | 44-45 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ITFMATCH-26JUL11SHIROB-SHI | 31 | 1m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL11TYAMON-TYA | 17 | 5m | 0 | 17-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11ERCHRU-ERC | 15 | 4m | 0 | 15-16 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11HOSCIR-CIR | 33 | 4m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11HOSCIR-HOS | 64 | 4m | 1/66-66/1 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFWMATCH-26JUL11KUBRYS-KUB | 65 | 4m | 1/67-67/1 | 65-67 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFWMATCH-26JUL11KUBRYS-RYS | 33 | 4m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11MAKSHO-MAK | 47 | 5m | 3/47-49/24 | 47-49 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL11MAKSHO-SHO | 53 | 3m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL11SMILEY-SMI | 38 | 4m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 8 tracked game(s) ({'OPEN': 3, 'WAKING': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10NAKMAT | ITF_M | 3.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 0.467 | 1 | **OPEN** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 0.667 | 2 | **OPEN** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11TYAMON | ITF_M | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- reality_divergence: KXITFMATCH-26JUL10DELJAS-DEL {"kind": "position_basis", "ref": 71.0, "market_mid": 38.0, "divergence": 33.0, "emitted_et": "2026-07-10 11:34:34 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
