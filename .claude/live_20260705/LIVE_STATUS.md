# LIVE VALIDATION — rolling status

- cycle 166 @ **2026-07-07 08:07:50 PM ET** | build `869e87d` | session boot 07-07 19:38 ET | log `live_v3_20260707.jsonl` | 4835 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 4 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:39 | ITFMATCH-26JUL07OGUJAS-OGU | ITF_M | ? | 25 | 21 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 19:39 | ITFMATCH-26JUL07DELKOY-DEL | ITF_M | ? | 90 | 87 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 19:42 | ATPCHALLENGERMATCH-26JUL07VANMIL-V | ATP_CHALL | ? | 47 | 44 | +3 (fill_est) | -4.0 | 1.4 | single |  | EARNED |
| 19:58 | ITFMATCH-26JUL07ISOTOM-ISO | ITF_M | ? | 80 | 77 | +3 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 11 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 7, 'FLOW_ABOVE': 3, 'FLOW_AT_LEVEL': 1} | repriceable now: true 1 / false 10 | **cumulative bid_grade lines: 5111 (repriceable true 469 / false 4642)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07DELKOY-KOY | 8 | 29m | 38/10-11/5208 | 8-10 | 2 | **FLOW_ABOVE** | 7 | flow above but bound 7c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07ISOTOM-TOM | 16 | 8m | 13/22-22/188 | 20-21 | 6 | **FLOW_ABOVE** | 17 | flow above but bound 17c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07NAKSHI-NAK | 39 | 7m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07NAKSHI-SHI | 57 | 7m | 0 | 57-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07TAKSAM-TAK | 9 | 9m | 5/11-11/144 | 9-10 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFMATCH-26JUL07TANCHE-TAN | 47 | 27m | 4/47-50/69 | 47-49 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL07YAMNAK-NAK | 6 | 6m | 0 | 6-10 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07YAMNAK-YAM | 89 | 4m | 0 | 89-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07YAMTAN-TAN | 81 | 7m | 0 | 81-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07YAMTAN-YAM | 15 | 7m | 0 | 15-18 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07CHOCAO-CHO | 49 | 29m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07DELKOY | 90 | 10 | **100** | 97 | +3 |
| ITFMATCH-26JUL07ISOTOM | 80 | 21 | **101** | 97 | +4 |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
