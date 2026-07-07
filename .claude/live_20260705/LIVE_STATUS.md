# LIVE VALIDATION — rolling status

- cycle 164 @ **2026-07-07 07:47:18 PM ET** | build `a170336` | session boot 07-07 19:38 ET | log `live_v3_20260707.jsonl` | 2681 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:39 | ITFMATCH-26JUL07OGUJAS-OGU | ITF_M | ? | 25 | 21 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 19:39 | ITFMATCH-26JUL07DELKOY-DEL | ITF_M | ? | 90 | 87 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 19:42 | ATPCHALLENGERMATCH-26JUL07VANMIL-V | ATP_CHALL | ? | 47 | 44 | +3 (fill_est) | -4.0 | 1.4 | single |  | EARNED |

## RESTING BIDS — 5 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 1, 'FLOW_ABOVE': 3, 'FLOW_AT_LEVEL': 1} | repriceable now: true 2 / false 3 | **cumulative bid_grade lines: 5103 (repriceable true 468 / false 4635)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07DELKOY-KOY | 8 | 8m | 1/10-10/28 | 8-10 | 2 | **FLOW_ABOVE** | 7 | flow above but bound 7c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07ISOTOM-TOM | 20 | 8m | 3/21-21/31 | 20-21 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFMATCH-26JUL07TAKSAM-TAK | 8 | 8m | 1/12-12/0 | 8-10 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→12 |
| ITFMATCH-26JUL07TANCHE-TAN | 47 | 6m | 2/47-50/0 | 47-50 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL07CHOCAO-CHO | 49 | 8m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07DELKOY | 90 | 10 | **100** | 97 | +3 |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
