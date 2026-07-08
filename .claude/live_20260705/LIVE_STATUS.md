# LIVE VALIDATION — rolling status

- cycle 184 @ **2026-07-07 11:14:34 PM ET** | build `3ec8cc0` | session boot 07-07 23:12 ET | log `live_v3_20260707.jsonl` | 2967 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:12 | ITFMATCH-26JUL07DELKOY-DEL | ITF_M | ? | 87 | 84 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 23:13 | ITFMATCH-26JUL07LOMTOM-TOM | ITF_M | ? | 62 | 59 | +3 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 10 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 5, 'NO_FLOW': 5} | repriceable now: true 1 / false 9 | **cumulative bid_grade lines: 5277 (repriceable true 502 / false 4775)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07ADAIMA-ADA | 5 | 2m | 12/9-10/750 | 5-10 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFMATCH-26JUL07ICHOCH-OCH | 28 | 2m | 31/50-54/2097 | 50-51 | 22 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL07KUSTAG-KUS | 34 | 2m | 97/95-99/15258 | 98-96 | 61 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL07NASLEE-LEE | 25 | 0m | 17/37-38/947 | 37-28 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08KUNMEN-MEN | 7 | 2m | 0 | 61-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HARMAI-HAR | 3 | 2m | 0 | 3-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HAYGIO-GIO | 31 | 2m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHOSUV-SHO | 52 | 2m | 0 | 67-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TUPPAN-PAN | 12 | 2m | 0 | 13-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TUPPAN-TUP | 72 | 1m | 1/84-84/55 | 73-90 | 12 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
