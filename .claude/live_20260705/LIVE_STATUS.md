# LIVE VALIDATION — rolling status

- cycle 19 @ **2026-07-08 05:29:22 PM ET** | build `ac89dd4` | session boot 07-08 17:25 ET | log `live_v3_20260708.jsonl` | 925 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:26 | ATPCHALLENGERMATCH-26JUL08MILUCH-M | ATP_CHALL | ? | 63 | 61 | +2 (window_cell) | 4.5 | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 25 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 9, 'NO_FLOW': 15, 'FLOW_AT_LEVEL': 1} | repriceable now: true 3 / false 22 | **cumulative bid_grade lines: 5737 (repriceable true 564 / false 5173)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06GLIYUN-Y | 81 | 4m | 46/93-97/9046 | 96-93 | 12 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL08CASBLA-B | 59 | 4m | 2/60-60/1452 | 59-60 | 1 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 4m | 0 | 62-63 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL08GALFIC-F | 21 | 4m | 85/38-43/14456 | 41-39 | 17 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL08JOHMAL-J | 40 | 4m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL08MCCJUN-J | 25 | 4m | 47/28-33/11869 | 31-28 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→28 |
| ITFMATCH-26JUL08ISOIMA-IMA | 62 | 4m | 0 | 62-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08ISOIMA-ISO | 34 | 4m | 0 | 34-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAPKIR-LAP | 9 | 3m | 0 | 12-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08OCHSAM-OCH | 14 | 3m | 0 | 14-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08OCHSAM-SAM | 85 | 3m | 0 | 85-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STHBER-BER | 40 | 3m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-JAS | 51 | 4m | 0 | 51-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-TAK | 44 | 4m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08THUPEC-THU | 21 | 4m | 31/40-43/2254 | 42-40 | 19 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08YAMSHI-SHI | 71 | 4m | 0 | 71-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08YAMSHI-YAM | 26 | 3m | 0 | 26-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 4m | 0 | 12-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08EKSLUX-EKS | 11 | 3m | 80/11-20/6692 | 19-12 | 0 | **FLOW_AT_LEVEL** | 8 |  |
| ITFWMATCH-26JUL08FOSKAY-FOS | 29 | 4m | 22/53-57/650 | 53-55 | 24 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08MILMIS-MIL | 6 | 3m | 5/15-16/68 | 12-20 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08PLADIG-PLA | 7 | 3m | 3/10-11/136 | 7-11 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| WTACHALLENGERMATCH-26JUL07SAWDOL-D | 35 | 3m | 1/38-38/26 | 37-38 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| WTACHALLENGERMATCH-26JUL08STEZHA-S | 77 | 4m | 0 | 80-81 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08YAMMIN-Y | 9 | 3m | 0 | 9-10 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08MILUCH | 63 | 38 | **101** | 97 | +4 |

## FLOW-STATE — 22 tracked game(s) ({'WAKING': 17, 'OPEN': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08CASBLA | ATP_CHALL | 0.5 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08MILUCH | ATP_CHALL | 2.7 | 1 | **OPEN** |
| ITFMATCH-26JUL08LAPKIR | ITF_M | 0.433 | 3 | **OPEN** |
| ITFWMATCH-26JUL08FOSKAY | ITF_W | 8.5 | 2 | **OPEN** |
| WTACHALLENGERMATCH-26JUL08YAMMIN | WTA_CHALL | 0.467 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL06GLIYUN | ATP_CHALL | 11.467 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08GALFIC | ATP_CHALL | 56.933 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08JOHMAL | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08MCCJUN | ATP_CHALL | 8.967 | — | **WAKING** |
| ITFMATCH-26JUL08ISOIMA | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL08STHBER | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 13.0 | — | **WAKING** |
| ITFMATCH-26JUL08YAMSHI | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 26.167 | — | **WAKING** |
| ITFWMATCH-26JUL08MILMIS | ITF_W | 1.533 | 12 | **WAKING** |
| ITFWMATCH-26JUL08PLADIG | ITF_W | 0.5 | 4 | **WAKING** |
| WTACHALLENGERMATCH-26JUL07SAWDOL | WTA_CHALL | 0.2 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08STEZHA | WTA_CHALL | 0.1 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
