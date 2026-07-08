# LIVE VALIDATION — rolling status

- cycle 29 @ **2026-07-08 07:11:46 PM ET** | build `0cec5ce` | session boot 07-08 17:25 ET | log `live_v3_20260708.jsonl` | 8582 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 15 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:26 | ATPCHALLENGERMATCH-26JUL08MILUCH-M | ATP_CHALL | ? | 63 | 61 | +2 (window_cell) | 4.5 | pre | single |  | GIFT_CLASS |
| 17:30 | ITFWMATCH-26JUL08EKSLUX-EKS | ITF_W | underdog | 11 | 8 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 17:33 | ITFWMATCH-26JUL08EKSLUX-LUX | ITF_W | leader | 86 | 87 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 17:34 | ITFWMATCH-26JUL08PLADIG-DIG | ITF_W | leader | 89 | 91 | -2 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 17:39 | ATPCHALLENGERMATCH-26JUL08CASBLA-B | ATP_CHALL | ? | 59 | 57 | +2 (window_cell) | -22.5 | pre | pair | 97 | EARNED |
| 17:40 | ITFWMATCH-26JUL08PLADIG-PLA | ITF_W | underdog | 6 | 7 | -1 (place_cell) | — | pre | pair | 95 | EARNED |
| 17:43 | ATPCHALLENGERMATCH-26JUL08CASBLA-C | ATP_CHALL | ? | 38 | 38 | +0 (window_cell) | 19.5 | pre | pair | 97 | EARNED |
| 17:48 | WTACHALLENGERMATCH-26JUL08YAMMIN-Y | WTA_CHALL | ? | 9 | 7 | +2 (window_cell) | -0.5 | pre | single |  | MIXED |
| 17:53 | WTACHALLENGERMATCH-26JUL07SAWDOL-D | WTA_CHALL | ? | 35 | 32 | +3 (fill_est) | 1.0 | pre | single |  | MIXED |
| 17:54 | ITFMATCH-26JUL08THUPEC-THU | ITF_M | ? | 21 | 37 | -16 (window_cell) | — | pre | single |  | EARNED |
| 18:31 | ATPCHALLENGERMATCH-26JUL08JOHMAL-J | ATP_CHALL | ? | 42 | 38 | +4 (window_cell) | 2.0 | pre | pair | 97 | MIXED |
| 18:49 | ATPCHALLENGERMATCH-26JUL08JOHMAL-M | ATP_CHALL | ? | 55 | 58 | -3 (window_cell) | -5.5 | pre | pair | 97 | EARNED |
| 18:56 | ITFMATCH-26JUL08LAPKIR-LAP | ITF_M | ? | 9 | 5 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 19:01 | ITFMATCH-26JUL08DERMIL-MIL | ITF_M | ? | 26 | 22 | +4 (fill_est) | — | pre | single |  | PENDING |
| 19:06 | WTACHALLENGERMATCH-26JUL08VIDANS-A | WTA_CHALL | ? | 12 | 10 | +2 (window_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 24 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 14, 'NO_FLOW': 10} | repriceable now: true 13 / false 11 | **cumulative bid_grade lines: 5793 (repriceable true 578 / false 5215)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 106m | 76/61-63/11413 | 61-63 | 3 | **FLOW_ABOVE** | 60 | REPRICEABLE→60 |
| ITFMATCH-26JUL08DELKUS-DEL | 89 | 41m | 3/91-91/51 | 89-91 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→91 |
| ITFMATCH-26JUL08DELKUS-KUS | 8 | 35m | 6/11-11/85 | 8-11 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 41m | 4/54-54/14 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL08HONNAK-NAK | 43 | 13m | 2/47-47/14 | 43-47 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 41m | 2/68-69/103 | 67-69 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 41m | 1/31-31/7 | 30-31 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→31 |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 41m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MOCTAN-TAN | 51 | 41m | 0 | 51-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08OCHSAM-OCH | 14 | 106m | 15/15-15/322 | 14-15 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFMATCH-26JUL08OCHSAM-SAM | 85 | 106m | 4/87-87/16 | 85-87 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→87 |
| ITFMATCH-26JUL08STHBER-BER | 40 | 8m | 129/42-56/10162 | 44-45 | 2 | **FLOW_ABOVE** | 41 | REPRICEABLE→41 |
| ITFMATCH-26JUL08TAKJAS-JAS | 51 | 106m | 0 | 51-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-TAK | 44 | 106m | 1/48-48/12 | 44-48 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 106m | 1/21-21/1 | 9-10 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-KAL | 78 | 70m | 1/80-80/0 | 78-80 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 70m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 70m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 70m | 0 | 77-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TIKZHA-TIK | 69 | 15m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TIKZHA-ZHA | 26 | 28m | 0 | 26-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 70m | 4/13-13/164 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL08WANLEO-WAN | 85 | 66m | 0 | 85-88 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VIDANS-V | 85 | 5m | 0 | 88-89 | — | **NO_FLOW** | 85 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08THUPEC | 21 | 1 | **22** | 97 | -75 |
| ATPCHALLENGERMATCH-26JUL08MILUCH | 63 | 2 | **65** | 97 | -32 |
| WTACHALLENGERMATCH-26JUL08VIDANS | 12 | 89 | **101** | 97 | +4 |
| WTACHALLENGERMATCH-26JUL08YAMMIN | 9 | 94 | **103** | 97 | +6 |

## FLOW-STATE — 24 tracked game(s) ({'OPEN': 10, 'QUIET': 2, 'WAKING': 12}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08CASBLA | ATP_CHALL | 190.167 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 1.867 | 2 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08JOHMAL | ATP_CHALL | 55.167 | 1 | **OPEN** |
| ITFMATCH-26JUL08DELKUS | ITF_M | 0.3 | 2 | **OPEN** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.233 | 1 | **OPEN** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 0.3 | 1 | **OPEN** |
| ITFMATCH-26JUL08STHBER | ITF_M | 9.133 | 1 | **OPEN** |
| ITFWMATCH-26JUL08PLADIG | ITF_W | 27.367 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL07SAWDOL | WTA_CHALL | 37.367 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL08YAMMIN | WTA_CHALL | 11.1 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08MILUCH | ATP_CHALL | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL08LAPKIR | ITF_M | 93.833 | — | **WAKING** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 27.633 | — | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 0.067 | 5 | **WAKING** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VIDANS | WTA_CHALL | 0.267 | 1 | **WAKING** |

## PATTERNS (sub-B) — 5
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL08MILUCH-MIL {"fill": 63, "age_min": 106, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL08CASBLA-BLA {"entry_minus_fv_burst": -22.5}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL08YAMMIN-YAM {"fill": 9, "age_min": 83, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07SAWDOL-DOL {"fill": 35, "age_min": 78, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08THUPEC-THU {"fill": 21, "age_min": 77, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
