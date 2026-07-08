# LIVE VALIDATION — rolling status

- cycle 30 @ **2026-07-08 07:21:58 PM ET** | build `b536ea9` | session boot 07-08 17:25 ET | log `live_v3_20260708.jsonl` | 8974 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 16 graded (session)
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
| 19:17 | ITFMATCH-26JUL08STHBER-BER | ITF_M | ? | 40 | 41 | -1 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 23 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 19, 'NO_FLOW': 4} | repriceable now: true 16 / false 7 | **cumulative bid_grade lines: 5799 (repriceable true 582 / false 5217)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 116m | 100/61-63/13754 | 62-63 | 3 | **FLOW_ABOVE** | 60 | REPRICEABLE→60 |
| ITFMATCH-26JUL08DELKUS-DEL | 89 | 51m | 4/91-91/52 | 89-91 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→91 |
| ITFMATCH-26JUL08DELKUS-KUS | 8 | 45m | 7/11-12/87 | 8-12 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 51m | 4/54-54/14 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL08HONNAK-NAK | 43 | 23m | 2/47-47/14 | 43-47 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 51m | 4/68-69/103 | 67-69 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 51m | 2/31-31/8 | 30-31 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→31 |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 51m | 1/47-47/6 | 46-47 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL08MOCTAN-TAN | 51 | 51m | 0 | 51-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08OCHSAM-OCH | 14 | 116m | 16/15-15/324 | 14-15 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFMATCH-26JUL08OCHSAM-SAM | 85 | 116m | 5/87-87/17 | 85-87 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→87 |
| ITFMATCH-26JUL08TAKJAS-JAS | 51 | 116m | 0 | 51-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-TAK | 44 | 116m | 1/48-48/12 | 44-48 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 116m | 1/21-21/1 | 9-10 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-KAL | 78 | 81m | 1/80-80/0 | 78-80 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 81m | 1/22-22/1 | 21-22 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 81m | 1/21-21/1 | 19-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 80m | 1/80-80/0 | 77-80 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08TIKZHA-TIK | 69 | 26m | 1/74-74/0 | 69-74 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08TIKZHA-ZHA | 26 | 39m | 1/31-31/1 | 26-31 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 81m | 7/13-13/265 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL08WANLEO-WAN | 85 | 76m | 0 | 85-88 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VIDANS-V | 85 | 16m | 0 | 88-89 | — | **NO_FLOW** | 85 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08THUPEC | 21 | 1 | **22** | 97 | -75 |
| ATPCHALLENGERMATCH-26JUL08MILUCH | 63 | 2 | **65** | 97 | -32 |
| ITFMATCH-26JUL08STHBER | 40 | 50 | **90** | 97 | -7 |
| WTACHALLENGERMATCH-26JUL08YAMMIN | 9 | 87 | **96** | 97 | -1 |
| WTACHALLENGERMATCH-26JUL08VIDANS | 12 | 89 | **101** | 97 | +4 |

## FLOW-STATE — 24 tracked game(s) ({'WAKING': 16, 'OPEN': 5, 'QUIET': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 2.167 | 1 | **OPEN** |
| ITFMATCH-26JUL08DELKUS | ITF_M | 0.367 | 2 | **OPEN** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.233 | 1 | **OPEN** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 0.367 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL08VIDANS | WTA_CHALL | 0.333 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08MILUCH | ATP_CHALL | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL08CASBLA | ATP_CHALL | 146.567 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08JOHMAL | ATP_CHALL | 61.467 | — | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.067 | 3 | **WAKING** |
| ITFMATCH-26JUL08LAPKIR | ITF_M | 76.633 | — | **WAKING** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL08STHBER | ITF_M | 11.667 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08PLADIG | ITF_W | 25.633 | — | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 0.1 | 5 | **WAKING** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.1 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL07SAWDOL | WTA_CHALL | 32.533 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL08YAMMIN | WTA_CHALL | 17.133 | — | **WAKING** |

## PATTERNS (sub-B) — 5
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL08MILUCH-MIL {"fill": 63, "age_min": 116, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL08CASBLA-BLA {"entry_minus_fv_burst": -22.5}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL08YAMMIN-YAM {"fill": 9, "age_min": 93, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07SAWDOL-DOL {"fill": 35, "age_min": 88, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08THUPEC-THU {"fill": 21, "age_min": 87, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
