# LIVE VALIDATION — rolling status

- cycle 3 @ **2026-07-04 09:34:52 PM ET** | build `aba83af` | session boot 07-04 21:32 ET | log `live_v3_20260704.jsonl` | 383 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:32 | ITFWMATCH-26JUL04MAXSTE-MAX | ITF_W | underdog | 14 | 10 | +4 (place_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 5 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 2, 'FLOW_AT_LEVEL': 3} | repriceable now: true 0 / false 5 | **cumulative bid_grade lines: 7 (repriceable true 0 / false 7)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL04LEGWIN-L | 49 | 2m | 38/83-84/3409 | 83-83 | 34 | **FLOW_ABOVE** | 83 |  |
| ITFWMATCH-26JUL04BROKOI-BRO | 77 | 2m | 22/77-79/3198 | 78-78 | 0 | **FLOW_AT_LEVEL** | 78 |  |
| ITFWMATCH-26JUL04BROKOI-KOI | 22 | 2m | 81/21-24/20598 | 22-22 | -1 | **FLOW_AT_LEVEL** | 19 |  |
| ITFWMATCH-26JUL04BROKOI-KOI | 21 | 0m | 9/21-22/228 | 22-22 | 0 | **FLOW_AT_LEVEL** | 19 |  |
| ITFWMATCH-26JUL04MAXSTE-STE | 83 | 2m | 26/86-87/6700 | 86-86 | 3 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL04MAXSTE | 14 | 86 | **100** | 97 | +3 |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
