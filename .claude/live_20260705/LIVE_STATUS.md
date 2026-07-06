# LIVE VALIDATION — rolling status

- cycle 150 @ **2026-07-06 12:29:35 PM ET** | build `4106a52` | session boot 07-06 12:15 ET | log `live_v3_20260706.jsonl` | 3558 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 12:26:21 | **handler_error** | on_bbo_update_error | [Errno 28] No space left on device |
| 12:26:21 | **handler_error** | error | [Errno 28] No space left on device |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_handler_error.md**

## FILLS — 14 graded (session)
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
| 12:18 | ITFWMATCH-26JUL06POHSTU-POH | ITF_W | ? | 28 | 24 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:21 | ITFMATCH-26JUL06SLODIF-SLO | ITF_M | ? | 55 | 52 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 12:22 | ITFMATCH-26JUL06SURMED-MED | ITF_M | ? | 56 | 53 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 12:22 | ITFMATCH-26JUL06CUNLIM-CUN | ITF_M | ? | 79 | 76 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 12:23 | ATPCHALLENGERMATCH-26JUL06HUETEN-T | ATP_CHALL | ? | 29 | 53 | -24 (window_cell) | — | pre | single |  | EARNED |
| 12:27 | ITFWMATCH-26JUL06MARBED-MAR | ITF_W | ? | 79 | 77 | +2 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 10 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 7, 'NO_FLOW': 3} | repriceable now: true 0 / false 10 | **cumulative bid_grade lines: 2445 (repriceable true 228 / false 2217)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06ZEBAND-A | 77 | 8m | 0 | 80-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BROTHU-THU | 59 | 14m | 29/88-96/365 | 92-91 | 29 | **FLOW_ABOVE** | 59 | flow above but bound 59c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06CUNLIM-LIM | 18 | 7m | 0 | 22-24 | — | **NO_FLOW** | 18 |  |
| ITFMATCH-26JUL06LUEVAN-LUE | 74 | 10m | 1/79-79/124 | 75-80 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SLODIF-DIF | 42 | 8m | 1/46-46/50 | 46-51 | 4 | **FLOW_ABOVE** | 42 | flow above but bound 42c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06BERMEL-BER | 76 | 1m | 0 | 78-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06COHXAV-COH | 50 | 14m | 50/79-91/3421 | 89-88 | 29 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06LIMDEK-DEK | 24 | 1m | 2/32-32/60 | 31-28 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06POHSTU-STU | 69 | 11m | 7/81-84/131 | 79-81 | 12 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SINUSU-SIN | 35 | 14m | 11/54-64/122 | 56-58 | 19 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06SANARN | 53 | 45 | **98** | 97 | +1 |
| ATPCHALLENGERMATCH-26JUL06HUETEN | 29 | 72 | **101** | 97 | +4 |
| ITFMATCH-26JUL06CUNLIM | 79 | 24 | **103** | 97 | +6 |
| ITFMATCH-26JUL06SLODIF | 55 | 51 | **106** | 97 | +9 |
| ITFWMATCH-26JUL06POHSTU | 28 | 81 | **109** | 97 | +12 |
| WTACHALLENGERMATCH-26JUL06CURDOD | 29 | 86 | **115** | 97 | +18 |
| ITFMATCH-26JUL06BROTHU | 38 | 91 | **129** | 97 | +32 |

## PATTERNS (sub-B) — 2
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06DEHUD-DE {"entry_minus_fv_burst": -48.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06KASCIN-KAS {"entry_minus_fv_burst": -8.5}

## ERRORS — 2 handler errors this session (SEE ZERO-TOLERANCE)
