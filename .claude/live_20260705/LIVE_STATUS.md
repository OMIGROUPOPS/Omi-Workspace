# LIVE VALIDATION — rolling status

- cycle 151 @ **2026-07-06 12:39:40 PM ET** | build `026c6fe` | session boot 07-06 12:15 ET | log `live_v3_20260706.jsonl` | 4512 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 12:26:21 | **handler_error** | on_bbo_update_error | [Errno 28] No space left on device |
| 12:26:21 | **handler_error** | error | [Errno 28] No space left on device |

## FILLS — 19 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 12:15 | ITFMATCH-26JUL06IAMBEN-IAM | ITF_M | ? | 66 | 64 | +2 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 12:15 | ATPCHALLENGERMATCH-26JUL06DEHUD-DE | ATP_CHALL | ? | 36 | 33 | +3 (adopted_est) | -48.5 | pre | single |  | EARNED |
| 12:15 | ITFMATCH-26JUL06BROTHU-BRO | ITF_M | ? | 38 | 34 | +4 (adopted_est) | 25.0 | pre | single |  | GIFT_CLASS |
| 12:15 | ITFWMATCH-26JUL06TRATEO-TRA | ITF_W | ? | 18 | 14 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:16 | ITFMATCH-26JUL06IAMBEN-BEN | ITF_M | ? | 31 | 30 | +1 (window_cell) | — | pre | pair | 97 | EARNED |
| 12:17 | ATPCHALLENGERMATCH-26JUL06KASCIN-K | ATP_CHALL | ? | 43 | 40 | +3 (fill_est) | -8.5 | pre | single |  | EARNED |
| 12:18 | WTACHALLENGERMATCH-26JUL06CURDOD-D | WTA_CHALL | ? | 29 | 32 | -3 (window_cell) | — | pre | single |  | EARNED |
| 12:18 | ATPCHALLENGERMATCH-26JUL06SANARN-A | ATP_CHALL | ? | 53 | 51 | +2 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 12:18 | ITFWMATCH-26JUL06POHSTU-POH | ITF_W | ? | 28 | 24 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 12:21 | ITFMATCH-26JUL06SLODIF-SLO | ITF_M | ? | 55 | 52 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 12:22 | ITFMATCH-26JUL06SURMED-MED | ITF_M | ? | 56 | 53 | +3 (adopted_est) | -7.0 | pre | single |  | EARNED |
| 12:22 | ITFMATCH-26JUL06CUNLIM-CUN | ITF_M | ? | 79 | 76 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 12:23 | ATPCHALLENGERMATCH-26JUL06HUETEN-T | ATP_CHALL | ? | 29 | 53 | -24 (window_cell) | — | pre | single |  | EARNED |
| 12:27 | ITFWMATCH-26JUL06MARBED-MAR | ITF_W | ? | 79 | 77 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 12:34 | ITFWMATCH-26JUL06BERMEL-BER | ITF_W | leader | 84 | 75 | +9 (place_cell) | — | pre | single |  | PENDING |
| 12:35 | ITFWMATCH-26JUL06SINUSU-SIN | ITF_W | ? | 35 | 31 | +4 (fill_est) | -1.0 | pre | single |  | MIXED |
| 12:35 | ITFWMATCH-26JUL06POHSTU-STU | ITF_W | ? | 69 | 67 | +2 (fill_est) | — | pre | pair | 97 | PENDING |
| 12:36 | WTACHALLENGERMATCH-26JUL06DENQUE-Q | WTA_CHALL | ? | 92 | 89 | +3 (adopted_est) | -5.5 | pre | single |  | EARNED |
| 12:39 | ATPCHALLENGERMATCH-26JUL06CLAPAP-C | ATP_CHALL | ? | 71 | 86 | -15 (window_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 9 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 8, 'NO_FLOW': 1} | repriceable now: true 2 / false 7 | **cumulative bid_grade lines: 2449 (repriceable true 230 / false 2219)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06SANARN-A | 53 | 3m | 22/57-70/589 | 64-63 | 4 | **FLOW_ABOVE** | 51 | flow above but bound 51c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06ZEBAND-A | 77 | 19m | 2/81-81/9 | 80-81 | 4 | **FLOW_ABOVE** | 78 | REPRICEABLE→78 |
| ITFMATCH-26JUL06BROTHU-THU | 59 | 24m | 118/88-99/5336 | 99-99 | 29 | **FLOW_ABOVE** | 59 | flow above but bound 59c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06CUNLIM-LIM | 18 | 18m | 0 | 22-24 | — | **NO_FLOW** | 18 |  |
| ITFMATCH-26JUL06LUEVAN-LUE | 75 | 3m | 7/79-83/167 | 76-77 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→79 |
| ITFMATCH-26JUL06SLODIF-DIF | 42 | 19m | 12/46-50/2700 | 51-52 | 4 | **FLOW_ABOVE** | 42 | flow above but bound 42c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06BERMEL-MEL | 12 | 1m | 1/24-24/14 | 24-15 | 12 | **FLOW_ABOVE** | 13 | flow above but bound 13c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06COHXAV-COH | 50 | 24m | 161/79-99/12816 | 98-99 | 29 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06LIMDEK-DEK | 24 | 11m | 125/30-54/12279 | 50-44 | 6 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06SANARN | 53 | 36 | **89** | 97 | -8 |
| ATPCHALLENGERMATCH-26JUL06CLAPAP | 71 | 19 | **90** | 97 | -7 |
| ITFWMATCH-26JUL06BERMEL | 84 | 15 | **99** | 97 | +2 |
| ITFMATCH-26JUL06CUNLIM | 79 | 24 | **103** | 97 | +6 |
| ITFMATCH-26JUL06SLODIF | 55 | 52 | **107** | 97 | +10 |
| WTACHALLENGERMATCH-26JUL06CURDOD | 29 | 83 | **112** | 97 | +15 |
| ATPCHALLENGERMATCH-26JUL06HUETEN | 29 | 84 | **113** | 97 | +16 |
| ITFMATCH-26JUL06BROTHU | 38 | 99 | **137** | 97 | +40 |

## PATTERNS (sub-B) — 2
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06DEHUD-DE {"entry_minus_fv_burst": -48.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06KASCIN-KAS {"entry_minus_fv_burst": -8.5}

## ERRORS — 2 handler errors this session (SEE ZERO-TOLERANCE)
