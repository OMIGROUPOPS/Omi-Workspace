# LIVE VALIDATION — rolling status

- cycle 149 @ **2026-07-06 12:19:27 PM ET** | build `a46a354` | session boot 07-06 12:15 ET | log `live_v3_20260706.jsonl` | 1391 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 9 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 12:15 | ITFMATCH-26JUL06IAMBEN-IAM | ITF_M | ? | 66 | 64 | +2 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 12:15 | ATPCHALLENGERMATCH-26JUL06DEHUD-DE | ATP_CHALL | ? | 36 | 33 | +3 (adopted_est) | -48.5 | pre | single |  | EARNED |
| 12:15 | ITFMATCH-26JUL06BROTHU-BRO | ITF_M | ? | 38 | 34 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:15 | ITFWMATCH-26JUL06TRATEO-TRA | ITF_W | ? | 18 | 14 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:16 | ITFMATCH-26JUL06IAMBEN-BEN | ITF_M | ? | 31 | 30 | +1 (window_cell) | — | pre | pair | 97 | EARNED |
| 12:17 | ATPCHALLENGERMATCH-26JUL06KASCIN-K | ATP_CHALL | ? | 43 | 40 | +3 (fill_est) | -8.5 | pre | single |  | EARNED |
| 12:18 | WTACHALLENGERMATCH-26JUL06CURDOD-D | WTA_CHALL | ? | 29 | 32 | -3 (window_cell) | — | pre | single |  | EARNED |
| 12:18 | ATPCHALLENGERMATCH-26JUL06SANARN-A | ATP_CHALL | ? | 53 | 51 | +2 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 12:18 | ITFWMATCH-26JUL06POHSTU-POH | ITF_W | ? | 28 | 24 | +4 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 14 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 8, 'NO_FLOW': 6} | repriceable now: true 0 / false 14 | **cumulative bid_grade lines: 2438 (repriceable true 228 / false 2210)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06HUETEN-T | 33 | 4m | 0 | 44-59 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MAXGHI-M | 43 | 4m | 7/96-96/1171 | 95-96 | 53 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL06DIMFER-FER | 33 | 4m | 46/47-49/8488 | 46-47 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06BROTHU-THU | 59 | 4m | 0 | 88-91 | — | **NO_FLOW** | 59 |  |
| ITFMATCH-26JUL06LUEVAN-LUE | 74 | 0m | 0 | 74-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SLODIF-DIF | 46 | 0m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BERMEL-MEL | 14 | 0m | 0 | 17-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06COHXAV-COH | 50 | 4m | 3/79-82/9 | 82-83 | 29 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06KULVOG-VOG | 41 | 4m | 21/67-77/1440 | 77-78 | 26 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06LIMDEK-DEK | 8 | 0m | 0 | 10-11 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06POHSTU-STU | 69 | 1m | 1/81-81/5 | 83-85 | 12 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SINUSU-SIN | 35 | 4m | 3/54-64/3 | 62-65 | 19 | **FLOW_ABOVE** | 99 |  |
| WTACHALLENGERMATCH-26JUL06WERSAL-W | 32 | 4m | 62/77-90/21842 | 83-84 | 45 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL06KEYNOS-NOS | 43 | 4m | 82/67-79/40211 | 78-79 | 24 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTACHALLENGERMATCH-26JUL06CURDOD | 29 | 82 | **111** | 97 | +14 |
| ITFWMATCH-26JUL06POHSTU | 28 | 85 | **113** | 97 | +16 |
| ITFMATCH-26JUL06BROTHU | 38 | 91 | **129** | 97 | +32 |

## PATTERNS (sub-B) — 2
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06DEHUD-DE {"entry_minus_fv_burst": -48.5, "emitted_et": "2026-07-06 12:19:27 PM ET"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06KASCIN-KAS {"entry_minus_fv_burst": -8.5}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
