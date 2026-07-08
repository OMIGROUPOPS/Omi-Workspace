# LIVE VALIDATION — rolling status

- cycle 20 @ **2026-07-08 05:39:36 PM ET** | build `1dbd078` | session boot 07-08 17:25 ET | log `live_v3_20260708.jsonl` | 1557 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 5 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:26 | ATPCHALLENGERMATCH-26JUL08MILUCH-M | ATP_CHALL | ? | 63 | 61 | +2 (window_cell) | 4.5 | pre | single |  | GIFT_CLASS |
| 17:30 | ITFWMATCH-26JUL08EKSLUX-EKS | ITF_W | underdog | 11 | 8 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 17:33 | ITFWMATCH-26JUL08EKSLUX-LUX | ITF_W | leader | 86 | 87 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 17:34 | ITFWMATCH-26JUL08PLADIG-DIG | ITF_W | leader | 89 | 91 | -2 (place_cell) | — | pre | single |  | PENDING |
| 17:39 | ATPCHALLENGERMATCH-26JUL08CASBLA-B | ATP_CHALL | ? | 59 | 57 | +2 (window_cell) | — | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 16 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 9, 'NO_FLOW': 7} | repriceable now: true 3 / false 13 | **cumulative bid_grade lines: 5743 (repriceable true 565 / false 5178)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08CASBLA-C | 38 | 0m | 0 | 41-42 | — | **NO_FLOW** | 38 |  |
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 14m | 1/63-63/128 | 62-63 | 5 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL08JOHMAL-J | 40 | 14m | 2/41-41/34 | 40-41 | 1 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08LAPKIR-LAP | 9 | 14m | 1/15-15/18 | 12-15 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08OCHSAM-OCH | 14 | 14m | 0 | 14-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08OCHSAM-SAM | 85 | 14m | 0 | 85-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STHBER-BER | 40 | 14m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-JAS | 51 | 14m | 0 | 51-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-TAK | 44 | 14m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08THUPEC-THU | 21 | 14m | 222/39-61/22690 | 51-40 | 18 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 14m | 0 | 12-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MILMIS-MIL | 6 | 13m | 28/15-44/444 | 17-26 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08PLADIG-PLA | 7 | 13m | 26/10-20/5082 | 7-11 | 3 | **FLOW_ABOVE** | 8 | REPRICEABLE→8 |
| WTACHALLENGERMATCH-26JUL07SAWDOL-D | 35 | 14m | 5/38-38/4848 | 37-38 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| WTACHALLENGERMATCH-26JUL08STEZHA-S | 77 | 14m | 1/81-81/60 | 80-81 | 4 | **FLOW_ABOVE** | 78 | REPRICEABLE→78 |
| WTACHALLENGERMATCH-26JUL08YAMMIN-Y | 9 | 14m | 13/10-10/206 | 9-10 | 1 | **FLOW_ABOVE** | 7 | flow above but bound 7c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08MILUCH | 63 | 37 | **100** | 97 | +3 |
| ITFWMATCH-26JUL08PLADIG | 89 | 11 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL08CASBLA | 59 | 42 | **101** | 97 | +4 |

## FLOW-STATE — 16 tracked game(s) ({'OPEN': 5, 'WAKING': 11}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08CASBLA | ATP_CHALL | 2.233 | 1 | **OPEN** |
| ITFMATCH-26JUL08LAPKIR | ITF_M | 0.2 | 3 | **OPEN** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 13.667 | 1 | **OPEN** |
| ITFWMATCH-26JUL08PLADIG | ITF_W | 1.233 | 3 | **OPEN** |
| WTACHALLENGERMATCH-26JUL08YAMMIN | WTA_CHALL | 0.667 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08JOHMAL | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08MILUCH | ATP_CHALL | 5.167 | 3 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL08STHBER | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 67.733 | — | **WAKING** |
| ITFWMATCH-26JUL08MILMIS | ITF_W | 1.967 | 6 | **WAKING** |
| WTACHALLENGERMATCH-26JUL07SAWDOL | WTA_CHALL | 0.267 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08STEZHA | WTA_CHALL | 0.133 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
