# LIVE VALIDATION — rolling status

- cycle 3 @ **2026-07-06 03:46:43 PM ET** | build `e207612` | session boot 07-06 15:26 ET | log `live_v3_20260706.jsonl` | 3456 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 5 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:26 | ATPCHALLENGERMATCH-26JUL06MONCOU-C | ATP_CHALL | ? | 32 | 29 | +3 (adopted_est) | 1.0 | pre | pair | 97 | MIXED |
| 15:26 | ATPCHALLENGERMATCH-26JUL06SANARN-A | ATP_CHALL | ? | 53 | 50 | +3 (adopted_est) | -33.5 | pre | single |  | EARNED |
| 15:26 | ATPCHALLENGERMATCH-26JUL06MONCOU-M | ATP_CHALL | ? | 65 | 62 | +3 (fill_est) | -2.5 | pre | pair | 97 | MIXED |
| 15:31 | ATPCHALLENGERMATCH-26JUL06KOZJOH-K | ATP_CHALL | ? | 66 | 63 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 15:37 | ITFMATCH-26JUL06GARPER-PER | ITF_M | ? | 27 | 23 | +4 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 3 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 2, 'NO_FLOW': 1} | repriceable now: true 1 / false 2 | **cumulative bid_grade lines: 2485 (repriceable true 233 / false 2252)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06ABOALVA- | 55 | 21m | 5/58-59/661 | 55-58 | 3 | **FLOW_ABOVE** | 56 | REPRICEABLE→56 |
| ATPCHALLENGERMATCH-26JUL06VUKBRO-B | 49 | 20m | 0 | 49-51 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06JULOLI-OLI | 5 | 20m | 3/91-91/5 | 5-91 | 86 | **FLOW_ABOVE** | 89 | flow above but bound 89c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## PATTERNS (sub-B) — 1
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06SANARN-ARN {"entry_minus_fv_burst": -33.5}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
