# LIVE VALIDATION — rolling status

- cycle 20 @ **2026-07-10 04:11:28 AM ET** | build `e4becd5c` | session boot 07-10 00:49 ET | log `live_v3_20260710.jsonl` | 35210 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 22 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:49 | ITFWMATCH-26JUL10DYUSAG-SAG | ITF_W | ? | 78 | 92 | -14 (window_cell) | — | pre | single |  | MIXED |
| 00:51 | ITFWMATCH-26JUL10PLOERC-ERC | ITF_W | ? | 89 | 87 | +2 (fill_est) | — | pre | single |  | PENDING |
| 01:05 | WTACHALLENGERMATCH-26JUL10CURVAN-V | WTA_CHALL | leader | 64 | 62 | +2 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 01:11 | ITFWMATCH-26JUL10YODJAN-JAN | ITF_W | ? | 66 | 39 | +27 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 01:27 | ITFMATCH-26JUL10FABOBR-FAB | ITF_M | ? | 18 | 14 | +4 (fill_est) | — | pre | pair | 97 | PENDING |
| 01:28 | ITFMATCH-26JUL10VANKOI-KOI | ITF_M | leader | 55 | 52 | +3 (place_cell) | — | pre | single |  | PENDING |
| 01:36 | ITFWMATCH-26JUL10SHOKRO-SHO | ITF_W | ? | 43 | 79 | -36 (window_cell) | — | pre | single |  | EARNED |
| 01:48 | ITFWMATCH-26JUL10NATTOM-TOM | ITF_W | ? | 87 | 85 | +2 (fill_est) | — | pre | single |  | PENDING |
| 02:37 | ITFMATCH-26JUL10BAYERE-ERE | ITF_M | ? | 90 | 87 | +3 (fill_est) | — | pre | single |  | PENDING |
| 02:42 | ITFWMATCH-26JUL10FRISOL-SOL | ITF_W | ? | 37 | 33 | +4 (fill_est) | — | pre | single |  | PENDING |
| 03:01 | ITFMATCH-26JUL10CATSNI-CAT | ITF_M | ? | 14 | 10 | +4 (fill_est) | — | pre | single |  | PENDING |
| 03:09 | ITFWMATCH-26JUL10PAWHRU-PAW | ITF_W | ? | 21 | 17 | +4 (fill_est) | — | pre | single |  | PENDING |
| 03:09 | ITFWMATCH-26JUL10DENGOL-DEN | ITF_W | ? | 78 | 76 | +2 (fill_est) | — | pre | single |  | PENDING |
| 03:12 | ITFMATCH-26JUL10VIVJAN-VIV | ITF_M | ? | 72 | 69 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 03:12 | ITFMATCH-26JUL10FABOBR-OBR | ITF_M | ? | 79 | 76 | +3 (fill_est) | — | pre | pair | 97 | PENDING |
| 03:23 | ITFWMATCH-26JUL10KRUSMI-KRU | ITF_W | ? | 81 | 79 | +2 (fill_est) | — | pre | single |  | PENDING |
| 03:31 | ITFWMATCH-26JUL10DUELEY-LEY | ITF_W | ? | 27 | 23 | +4 (fill_est) | — | pre | single |  | PENDING |
| 04:02 | ITFWMATCH-26JUL10NAKYAM-NAK | ITF_W | ? | 56 | 54 | +2 (fill_est) | — | pre | single |  | PENDING |
| 04:07 | ITFMATCH-26JUL10MAZBRE-BRE | ITF_M | ? | 45 | 41 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 04:07 | ITFMATCH-26JUL10LAGROS-LAG | ITF_M | ? | 33 | 29 | +4 (fill_est) | — | pre | single |  | PENDING |
| 04:09 | ITFWMATCH-26JUL10SUNKAL-KAL | ITF_W | ? | 65 | 63 | +2 (fill_est) | — | pre | single |  | PENDING |
| 04:10 | ITFMATCH-26JUL10ADDCRA-CRA | ITF_M | ? | 65 | 62 | +3 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 48 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 25, 'FLOW_AT_LEVEL': 5, 'FLOW_ABOVE': 18} | repriceable now: true 10 / false 38 | **cumulative bid_grade lines: 7584 (repriceable true 1009 / false 6575)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL10MIDPIR-M | 32 | 11m | 0 | 32-33 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL10NEUSQU-N | 67 | 4m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ADDCRA-ADD | 32 | 1m | 0 | 35-39 | — | **NO_FLOW** | 32 |  |
| ITFMATCH-26JUL10ARZBEL-ARZ | 75 | 202m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-BEL | 20 | 202m | 1/23-23/82 | 20-25 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFMATCH-26JUL10COCPAN-PAN | 76 | 202m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10DOUVIR-VIR | 5 | 202m | 12/8-9/501 | 5-9 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL10JEDRIV-JED | 47 | 187m | 6/50-51/340 | 47-49 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFMATCH-26JUL10JONBAR-BAR | 63 | 201m | 0 | 63-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LAGROS-ROS | 63 | 0m | 0 | 63-68 | — | **NO_FLOW** | 64 |  |
| ITFMATCH-26JUL10LOPBAL-LOP | 77 | 161m | 0 | 77-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ORLTSI-ORL | 81 | 161m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ORLTSI-TSI | 16 | 161m | 1/20-20/23 | 16-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL10TYABEA-BEA | 40 | 186m | 6/44-44/18 | 40-44 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ITFMATCH-26JUL10TYABEA-TYA | 56 | 202m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VELMON-MON | 75 | 202m | 1/80-80/12 | 75-81 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10VELMON-VEL | 19 | 202m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10WISMAT-MAT | 44 | 10m | 0 | 44-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10WISMAT-WIS | 54 | 11m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-DUR | 79 | 202m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-ZAP | 19 | 202m | 1/21-21/8 | 19-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFMATCH-26JUL10ZGISHI-SHI | 60 | 196m | 1/60-60/7 | 60-61 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL10ZGISHI-ZGI | 37 | 201m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10BOJINI-BOJ | 55 | 202m | 2/56-56/2 | 55-56 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ITFWMATCH-26JUL10BOJINI-INI | 43 | 202m | 0 | 43-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DYUSAG-DYU | 16 | 180m | 5142/1-60/775520 | 1-1 | -15 | **FLOW_AT_LEVEL** | 4 |  |
| ITFWMATCH-26JUL10FONELS-ELS | 20 | 202m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FONELS-FON | 74 | 202m | 1/79-79/1 | 74-80 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-GAN | 18 | 202m | 1/24-24/19 | 18-24 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-STR | 76 | 202m | 1/81-81/1 | 76-81 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10GAOVAN-GAO | 27 | 161m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-HOS | 53 | 202m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-VAN | 44 | 202m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KOVJIA-JIA | 46 | 202m | 2/52-52/118 | 46-52 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10KUBBER-BER | 9 | 202m | 17/9-11/485 | 9-10 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-YAM | 39 | 2m | 0 | 41-45 | — | **NO_FLOW** | 41 |  |
| ITFWMATCH-26JUL10PEREZZ-EZZ | 34 | 202m | 0 | 34-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PEREZZ-PER | 61 | 202m | 1/65-65/1 | 61-65 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFWMATCH-26JUL10SUNKAL-SUN | 32 | 2m | 2/41-43/12 | 42-43 | 9 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL10TUPMAK-MAK | 47 | 176m | 2921/18-99/312722 | 99-98 | -29 | **FLOW_AT_LEVEL** | 55 |  |
| ITFWMATCH-26JUL10VLAMIS-VLA | 18 | 199m | 1/22-22/17 | 18-20 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL10WIEFOU-FOU | 61 | 202m | 1/63-63/1 | 61-63 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL10WIEFOU-WIE | 36 | 202m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10BLIZAN-B | 74 | 11m | 0 | 74-76 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10BLIZAN-Z | 24 | 11m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10CURVAN-C | 33 | 185m | 28/36-38/6392 | 35-36 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL10QUEWAL-Q | 33 | 191m | 32/33-34/2163 | 33-34 | 0 | **FLOW_AT_LEVEL** | 31 |  |
| WTACHALLENGERMATCH-26JUL10QUEWAL-W | 67 | 191m | 39/68-68/10490 | 67-69 | 1 | **FLOW_ABOVE** | 65 | flow above but bound 65c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10SHOKRO | 43 | 1 | **44** | 97 | -53 |
| ITFWMATCH-26JUL10DYUSAG | 78 | 1 | **79** | 97 | -18 |
| WTACHALLENGERMATCH-26JUL10CURVAN | 64 | 36 | **100** | 97 | +3 |
| ITFWMATCH-26JUL10NAKYAM | 56 | 45 | **101** | 97 | +4 |
| ITFMATCH-26JUL10LAGROS | 33 | 68 | **101** | 97 | +4 |
| ITFMATCH-26JUL10ADDCRA | 65 | 39 | **104** | 97 | +7 |
| ITFWMATCH-26JUL10SUNKAL | 65 | 43 | **108** | 97 | +11 |
| ITFWMATCH-26JUL10YODJAN | 66 | 75 | **141** | 97 | +44 |

## FLOW-STATE — 48 tracked game(s) ({'WAKING': 41, 'OPEN': 5, 'QUIET': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10ADDCRA | ITF_M | 0.333 | 3 | **OPEN** |
| ITFMATCH-26JUL10BAYERE | ITF_M | 0.267 | 1 | **OPEN** |
| ITFWMATCH-26JUL10SUNKAL | ITF_W | 0.367 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL10CURVAN | WTA_CHALL | 0.7 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL10QUEWAL | WTA_CHALL | 0.367 | 1 | **OPEN** |
| ITFMATCH-26JUL10VELMON | ITF_M | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL10FONELS | ITF_W | 0.0 | 6 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL10MIDPIR | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL10NEUSQU | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL10ARZBEL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10CATSNI | ITF_M | 20.3 | — | **WAKING** |
| ITFMATCH-26JUL10COCPAN | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10DOUVIR | ITF_M | 0.167 | 4 | **WAKING** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 17.667 | — | **WAKING** |
| ITFMATCH-26JUL10JEDRIV | ITF_M | 0.1 | 2 | **WAKING** |
| ITFMATCH-26JUL10JONBAR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10LAGROS | ITF_M | 0.3 | 4 | **WAKING** |
| ITFMATCH-26JUL10LOPBAL | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10MAZBRE | ITF_M | 0.2 | 5 | **WAKING** |
| ITFMATCH-26JUL10ORLTSI | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10TYABEA | ITF_M | 0.2 | 4 | **WAKING** |
| ITFMATCH-26JUL10VANKOI | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 9.167 | — | **WAKING** |
| ITFMATCH-26JUL10WISMAT | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL10ZAPDUR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10ZGISHI | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10BOJINI | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 10.233 | — | **WAKING** |
| ITFWMATCH-26JUL10DUELEY | ITF_W | 2.9 | — | **WAKING** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 12.367 | — | **WAKING** |
| ITFWMATCH-26JUL10FRISOL | ITF_W | 7.967 | — | **WAKING** |
| ITFWMATCH-26JUL10GANSTR | ITF_W | 0.033 | 5 | **WAKING** |
| ITFWMATCH-26JUL10GAOVAN | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10HOSVAN | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10KOVJIA | ITF_W | 0.067 | 6 | **WAKING** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 2.2 | — | **WAKING** |
| ITFWMATCH-26JUL10KUBBER | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL10NAKYAM | ITF_W | 0.633 | 4 | **WAKING** |
| ITFWMATCH-26JUL10NATTOM | ITF_W | 6.067 | — | **WAKING** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 7.867 | — | **WAKING** |
| ITFWMATCH-26JUL10PEREZZ | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 18.533 | — | **WAKING** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 0.767 | — | **WAKING** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 11.633 | — | **WAKING** |
| ITFWMATCH-26JUL10VLAMIS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10WIEFOU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 67.533 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL10BLIZAN | WTA_CHALL | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 16
- half_arm_aging: KXITFWMATCH-26JUL10DYUSAG-SAG {"fill": 78, "age_min": 202, "mode": "QUEUE(flow at/below our level, unfilled)"}
- pre_conception_buy: KXITFWMATCH-26JUL10YODJAN-JAN {"price": 66, "conception_ts": 1783666818.2513328, "detail": "buy 66c predates the conception stamp by 130min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL10PLOERC-ERC {"fill": 89, "age_min": 200, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL10CURVAN-VAN {"fill": 64, "age_min": 186, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL10YODJAN-JAN {"fill": 66, "age_min": 180, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10VANKOI-KOI {"fill": 55, "age_min": 163, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10SHOKRO-SHO {"fill": 43, "age_min": 155, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL10NATTOM-TOM {"fill": 87, "age_min": 143, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10BAYERE-ERE {"fill": 90, "age_min": 94, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10FRISOL-SOL {"fill": 37, "age_min": 89, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL10CATSNI-CAT {"fill": 14, "age_min": 69, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10PAWHRU-PAW {"fill": 21, "age_min": 62, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10DENGOL-DEN {"fill": 78, "age_min": 62, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10VIVJAN-VIV {"fill": 72, "age_min": 59, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10KRUSMI-KRU {"fill": 81, "age_min": 47, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10DUELEY-LEY {"fill": 27, "age_min": 40, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-10 04:11:28 AM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
