# LIVE VALIDATION — rolling status

- cycle 21 @ **2026-07-08 05:49:49 PM ET** | build `7a333cc` | session boot 07-08 17:25 ET | log `live_v3_20260708.jsonl` | 2090 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 8 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:26 | ATPCHALLENGERMATCH-26JUL08MILUCH-M | ATP_CHALL | ? | 63 | 61 | +2 (window_cell) | 4.5 | pre | single |  | GIFT_CLASS |
| 17:30 | ITFWMATCH-26JUL08EKSLUX-EKS | ITF_W | underdog | 11 | 8 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 17:33 | ITFWMATCH-26JUL08EKSLUX-LUX | ITF_W | leader | 86 | 87 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 17:34 | ITFWMATCH-26JUL08PLADIG-DIG | ITF_W | leader | 89 | 91 | -2 (place_cell) | — | pre | pair | 95 | PENDING |
| 17:39 | ATPCHALLENGERMATCH-26JUL08CASBLA-B | ATP_CHALL | ? | 59 | 57 | +2 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 17:40 | ITFWMATCH-26JUL08PLADIG-PLA | ITF_W | underdog | 6 | 7 | -1 (place_cell) | — | pre | pair | 95 | PENDING |
| 17:43 | ATPCHALLENGERMATCH-26JUL08CASBLA-C | ATP_CHALL | ? | 38 | 38 | +0 (window_cell) | — | pre | pair | 97 | EARNED |
| 17:48 | WTACHALLENGERMATCH-26JUL08YAMMIN-Y | WTA_CHALL | ? | 9 | 7 | +2 (window_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 14 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 7, 'NO_FLOW': 7} | repriceable now: true 3 / false 11 | **cumulative bid_grade lines: 5746 (repriceable true 566 / false 5180)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 24m | 3/63-63/190 | 62-63 | 5 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL08JOHMAL-J | 40 | 24m | 2/41-41/34 | 40-41 | 1 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08LAPKIR-LAP | 9 | 24m | 5/15-15/100 | 12-15 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08OCHSAM-OCH | 14 | 24m | 4/15-15/87 | 14-15 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFMATCH-26JUL08OCHSAM-SAM | 85 | 24m | 0 | 85-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STHBER-BER | 40 | 24m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-JAS | 51 | 24m | 0 | 51-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-TAK | 44 | 24m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08THUPEC-THU | 21 | 24m | 515/39-61/45945 | 45-42 | 18 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 24m | 0 | 12-15 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL07SAWDOL-D | 35 | 24m | 22/38-38/13319 | 37-38 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| WTACHALLENGERMATCH-26JUL08STEZHA-S | 77 | 24m | 6/81-82/604 | 81-82 | 4 | **FLOW_ABOVE** | 78 | REPRICEABLE→78 |
| WTACHALLENGERMATCH-26JUL08VIDANS-V | 88 | 8m | 0 | 88-89 | — | **NO_FLOW** | 85 |  |
| WTACHALLENGERMATCH-26JUL08YAMMIN-M | 88 | 1m | 0 | 90-91 | — | **NO_FLOW** | 88 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08MILUCH | 63 | 17 | **80** | 97 | -17 |
| WTACHALLENGERMATCH-26JUL08YAMMIN | 9 | 91 | **100** | 97 | +3 |

## FLOW-STATE — 16 tracked game(s) ({'WAKING': 12, 'OPEN': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08LAPKIR | ITF_M | 0.233 | 3 | **OPEN** |
| ITFWMATCH-26JUL08PLADIG | ITF_W | 2.667 | 2 | **OPEN** |
| WTACHALLENGERMATCH-26JUL07SAWDOL | WTA_CHALL | 0.767 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL08YAMMIN | WTA_CHALL | 1.533 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08CASBLA | ATP_CHALL | 10.133 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08JOHMAL | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08MILUCH | ATP_CHALL | 7.6 | — | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL08STHBER | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 19.467 | — | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 49.4 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL08STEZHA | WTA_CHALL | 0.233 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VIDANS | WTA_CHALL | 0.167 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
