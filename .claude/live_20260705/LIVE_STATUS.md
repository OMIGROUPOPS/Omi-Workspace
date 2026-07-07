# LIVE VALIDATION — rolling status

- cycle 125 @ **2026-07-07 12:45:41 PM ET** | build `4a76356` | session boot 07-07 12:35 ET | log `live_v3_20260707.jsonl` | 4985 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 17 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 12:35 | ITFMATCH-26JUL07ROLLAR-ROL | ITF_M | ? | 92 | 89 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 12:35 | WTACHALLENGERMATCH-26JUL07MARBUR-M | WTA_CHALL | ? | 67 | 67 | +0 (window_cell) | — | pre | single |  | MIXED |
| 12:35 | ATPCHALLENGERMATCH-26JUL07HERAMB-H | ATP_CHALL | ? | 4 | 2 | +2 (window_cell) | — | pre | pair | 94 | MIXED |
| 12:35 | ATPCHALLENGERMATCH-26JUL07HERAMB-A | ATP_CHALL | ? | 90 | 91 | -1 (window_cell) | — | pre | pair | 94 | MIXED |
| 12:35 | ATPCHALLENGERMATCH-26JUL07KRUPIE-K | ATP_CHALL | ? | 60 | 57 | +3 (adopted_est) | -23.0 | pre | single |  | EARNED |
| 12:35 | ITFWMATCH-26JUL07GIADIA-GIA | ITF_W | ? | 34 | 30 | +4 (adopted_est) | -21.5 | pre | pair | 79 | EARNED |
| 12:35 | ITFWMATCH-26JUL07MAROLU-OLU | ITF_W | ? | 30 | 26 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:35 | ITFWMATCH-26JUL07EVAGOW-GOW | ITF_W | ? | 14 | 10 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:35 | ATPCHALLENGERMATCH-26JUL07CLAHER-C | ATP_CHALL | ? | 44 | 70 | -26 (window_cell) | — | pre | single |  | EARNED |
| 12:35 | ATPCHALLENGERMATCH-26JUL07MONSUM-S | ATP_CHALL | ? | 9 | 6 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 12:35 | ATPCHALLENGERMATCH-26JUL07AZKBON-A | ATP_CHALL | ? | 32 | 29 | +3 (adopted_est) | -51.0 | pre | single |  | EARNED |
| 12:36 | ITFWMATCH-26JUL07PASLEE-LEE | ITF_W | ? | 36 | 32 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:40 | ITFWMATCH-26JUL07GIADIA-DIA | ITF_W | ? | 45 | 41 | +4 (adopted_est) | — | pre | pair | 79 | PENDING |
| 12:41 | ATPCHALLENGERMATCH-26JUL07HAMWAL-H | ATP_CHALL | ? | 11 | 8 | +3 (fill_est) | — | pre | single |  | PENDING |
| 12:44 | ATPCHALLENGERMATCH-26JUL07OSOSOT-O | ATP_CHALL | ? | 20 | 25 | -5 (window_cell) | — | pre | single |  | EARNED |
| 12:44 | ITFMATCH-26JUL07DJAGUA-DJA | ITF_M | ? | 69 | 66 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 12:44 | ITFWMATCH-26JUL07MOROLM-OLM | ITF_W | ? | 54 | 52 | +2 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 1 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 1} | repriceable now: true 0 / false 1 | **cumulative bid_grade lines: 4863 (repriceable true 420 / false 4443)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07BARCOT-COT | 41 | 10m | 26/66-90/1264 | 89-90 | 25 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07CLAHER | 44 | 24 | **68** | 97 | -29 |
| WTACHALLENGERMATCH-26JUL07MARBUR | 67 | 14 | **81** | 97 | -16 |
| ATPCHALLENGERMATCH-26JUL07OSOSOT | 20 | 74 | **94** | 97 | -3 |

## PATTERNS (sub-B) — 3
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07KRUPIE-KRU {"entry_minus_fv_burst": -23.0, "emitted_et": "2026-07-07 12:45:41 PM ET"}
- deep_neg_fv: KXITFWMATCH-26JUL07GIADIA-GIA {"entry_minus_fv_burst": -21.5, "emitted_et": "2026-07-07 12:45:41 PM ET"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07AZKBON-AZK {"entry_minus_fv_burst": -51.0, "emitted_et": "2026-07-07 12:45:41 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
