# LIVE VALIDATION — rolling status

- cycle 1 @ **2026-07-06 03:26:29 PM ET** | build `7def47e` | session boot 07-06 15:26 ET | log `live_v3_20260706.jsonl` | 485 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:26 | ATPCHALLENGERMATCH-26JUL06MONCOU-C | ATP_CHALL | ? | 32 | 29 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 15:26 | ATPCHALLENGERMATCH-26JUL06SANARN-A | ATP_CHALL | ? | 53 | 50 | +3 (adopted_est) | -33.5 | pre | single |  | EARNED |

## RESTING BIDS — 4 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 1, 'NO_FLOW': 3} | repriceable now: true 0 / false 4 | **cumulative bid_grade lines: 2483 (repriceable true 232 / false 2251)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06ABOALVA- | 55 | 0m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MONCOU-M | 65 | 0m | 2/75-76/278 | 70-71 | 10 | **FLOW_ABOVE** | 65 | flow above but bound 65c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06VUKBRO-B | 49 | 0m | 0 | 49-51 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06JULOLI-OLI | 5 | 0m | 0 | 5-91 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06MONCOU | 32 | 71 | **103** | 97 | +6 |

## PATTERNS (sub-B) — 1
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"entry_minus_fv_burst": -33.5, "emitted_et": "2026-07-06 03:26:29 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
