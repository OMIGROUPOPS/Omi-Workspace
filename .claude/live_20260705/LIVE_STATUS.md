# LIVE VALIDATION — rolling status

- cycle 126 @ **2026-07-07 12:56:16 PM ET** | build `0589447` | session boot 07-07 12:54 ET | log `live_v3_20260707.jsonl` | 1491 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 7 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 12:54 | ITFMATCH-26JUL07MARBAS-MAR | ITF_M | ? | 36 | 18 | +18 (window_cell) | — | pre | single |  | MIXED |
| 12:54 | ITFWMATCH-26JUL07EVAGOW-GOW | ITF_W | ? | 14 | 10 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:54 | ITFWMATCH-26JUL07GIADIA-GIA | ITF_W | ? | 34 | 30 | +4 (adopted_est) | -37.0 | pre | single |  | EARNED |
| 12:54 | ITFWMATCH-26JUL07MAROLU-OLU | ITF_W | ? | 30 | 26 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:54 | ATPCHALLENGERMATCH-26JUL07CLAHER-C | ATP_CHALL | ? | 44 | 41 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 12:54 | ATPCHALLENGERMATCH-26JUL07AZKBON-A | ATP_CHALL | ? | 32 | 29 | +3 (adopted_est) | -63.5 | pre | single |  | EARNED |
| 12:55 | ITFWMATCH-26JUL07MOROLM-MOR | ITF_W | ? | 43 | 39 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 9 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 7, 'NO_FLOW': 2} | repriceable now: true 0 / false 9 | **cumulative bid_grade lines: 4872 (repriceable true 420 / false 4452)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07DROERH-E | 23 | 1m | 3/31-31/107 | 31-30 | 8 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07OSOSOT-O | 20 | 1m | 36/31-39/2740 | 37-37 | 11 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL07AUGDJO-AUG | 36 | 1m | 41/44-49/16082 | 47-48 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL07MARBAS-BAS | 61 | 2m | 3/69-71/601 | 78-79 | 8 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL07EVAGOW-GOW | 18 | 2m | 0 | 18-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07SCHZID-ZID | 70 | 1m | 0 | 87-88 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL07FITPIG-F | 30 | 1m | 4/35-41/100 | 34-35 | 5 | **FLOW_ABOVE** | 99 |  |
| WTACHALLENGERMATCH-26JUL07GALRIN-R | 34 | 1m | 47/68-75/5687 | 70-73 | 34 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL07OSAMUC-MUC | 44 | 1m | 6/99-99/437 | 97-98 | 55 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07MARBAS | 36 | 79 | **115** | 97 | +18 |

## PATTERNS (sub-B) — 2
- deep_neg_fv: KXITFWMATCH-26JUL07GIADIA-GIA {"entry_minus_fv_burst": -37.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07AZKBON-AZK {"entry_minus_fv_burst": -63.5}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
