# LIVE VALIDATION — rolling status

- cycle 21 @ **2026-07-10 04:21:36 AM ET** | build `64c9ed7a` | session boot 07-10 00:49 ET | log `live_v3_20260710.jsonl` | 39031 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 26 graded (session)
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
| 04:02 | ITFWMATCH-26JUL10NAKYAM-NAK | ITF_W | ? | 56 | 54 | +2 (fill_est) | — | pre | pair | 97 | PENDING |
| 04:07 | ITFMATCH-26JUL10MAZBRE-BRE | ITF_M | ? | 45 | 41 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 04:07 | ITFMATCH-26JUL10LAGROS-LAG | ITF_M | ? | 33 | 29 | +4 (fill_est) | — | pre | pair | 96 | PENDING |
| 04:09 | ITFWMATCH-26JUL10SUNKAL-KAL | ITF_W | ? | 65 | 63 | +2 (fill_est) | — | pre | single |  | PENDING |
| 04:10 | ITFMATCH-26JUL10ADDCRA-CRA | ITF_M | ? | 65 | 62 | +3 (fill_est) | — | pre | single |  | PENDING |
| 04:12 | ITFMATCH-26JUL10LAGROS-ROS | ITF_M | leader | 63 | 64 | -1 (place_cell) | — | pre | pair | 96 | PENDING |
| 04:13 | ITFMATCH-26JUL10JEDRIV-JED | ITF_M | ? | 49 | 45 | +4 (fill_est) | — | pre | pair | 97 | PENDING |
| 04:15 | ITFWMATCH-26JUL10NAKYAM-YAM | ITF_W | ? | 41 | 37 | +4 (fill_est) | — | pre | pair | 97 | PENDING |
| 04:18 | ITFMATCH-26JUL10JEDRIV-RIV | ITF_M | ? | 48 | 44 | +4 (fill_est) | — | pre | pair | 97 | PENDING |

## RESTING BIDS — 48 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 28, 'FLOW_ABOVE': 16, 'FLOW_AT_LEVEL': 4} | repriceable now: true 10 / false 38 | **cumulative bid_grade lines: 7591 (repriceable true 1009 / false 6582)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL10DIAMCD-D | 80 | 1m | 0 | 80-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL10MIDPIR-M | 32 | 21m | 0 | 32-33 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL10NEUSQU-N | 67 | 14m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL10NEUSQU-S | 31 | 10m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ADDCRA-ADD | 27 | 0m | 0 | 30-34 | — | **NO_FLOW** | 32 |  |
| ITFMATCH-26JUL10ARZBEL-ARZ | 75 | 212m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-BEL | 20 | 212m | 1/23-23/82 | 20-25 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFMATCH-26JUL10COCPAN-PAN | 76 | 212m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10DOUVIR-VIR | 5 | 212m | 15/8-9/843 | 5-9 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL10JONBAR-BAR | 63 | 212m | 0 | 63-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LOPBAL-LOP | 77 | 171m | 0 | 77-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ORLTSI-ORL | 81 | 171m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ORLTSI-TSI | 16 | 171m | 1/20-20/23 | 16-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL10TYABEA-BEA | 40 | 196m | 6/44-44/18 | 40-44 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ITFMATCH-26JUL10TYABEA-TYA | 56 | 212m | 1/60-60/59 | 56-60 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFMATCH-26JUL10VELMON-MON | 75 | 212m | 1/80-80/12 | 75-80 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10VELMON-VEL | 19 | 212m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10WISMAT-MAT | 44 | 20m | 0 | 44-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10WISMAT-WIS | 54 | 21m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-DUR | 79 | 212m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-ZAP | 19 | 212m | 1/21-21/8 | 19-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFMATCH-26JUL10ZGISHI-SHI | 60 | 206m | 1/60-60/7 | 60-61 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL10ZGISHI-ZGI | 37 | 212m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10BOJINI-BOJ | 55 | 212m | 2/56-56/2 | 55-56 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ITFWMATCH-26JUL10BOJINI-INI | 43 | 212m | 0 | 43-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DYUSAG-DYU | 16 | 191m | 5142/1-60/775520 | 1-1 | -15 | **FLOW_AT_LEVEL** | 4 |  |
| ITFWMATCH-26JUL10FONELS-ELS | 20 | 212m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FONELS-FON | 74 | 212m | 1/79-79/1 | 74-79 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-GAN | 20 | 3m | 0 | 20-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-STR | 76 | 212m | 1/81-81/1 | 76-81 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10GAOVAN-GAO | 27 | 171m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-HOS | 53 | 212m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-VAN | 44 | 212m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KOVJIA-JIA | 49 | 4m | 0 | 49-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KUBBER-BER | 10 | 5m | 0 | 10-12 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-NAK | 56 | 1m | 0 | 72-75 | — | **NO_FLOW** | 56 |  |
| ITFWMATCH-26JUL10PEREZZ-EZZ | 34 | 212m | 0 | 34-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PEREZZ-PER | 61 | 212m | 1/65-65/1 | 61-65 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFWMATCH-26JUL10SUNKAL-SUN | 32 | 12m | 9/41-54/217 | 42-47 | 9 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL10TUPMAK-MAK | 47 | 186m | 2921/18-99/312722 | 99-98 | -29 | **FLOW_AT_LEVEL** | 55 |  |
| ITFWMATCH-26JUL10VLAMIS-VLA | 18 | 209m | 1/22-22/17 | 18-20 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL10WIEFOU-FOU | 61 | 212m | 1/63-63/1 | 61-63 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL10WIEFOU-WIE | 36 | 212m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10BLIZAN-B | 74 | 21m | 0 | 74-76 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10BLIZAN-Z | 24 | 21m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10CURVAN-C | 33 | 195m | 30/36-38/6492 | 36-37 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL10QUEWAL-Q | 33 | 201m | 33/33-34/2297 | 33-34 | 0 | **FLOW_AT_LEVEL** | 31 |  |
| WTACHALLENGERMATCH-26JUL10QUEWAL-W | 67 | 201m | 40/68-69/10525 | 67-69 | 1 | **FLOW_ABOVE** | 65 | flow above but bound 65c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10SHOKRO | 43 | 1 | **44** | 97 | -53 |
| ITFWMATCH-26JUL10DYUSAG | 78 | 1 | **79** | 97 | -18 |
| ITFMATCH-26JUL10ADDCRA | 65 | 34 | **99** | 97 | +2 |
| WTACHALLENGERMATCH-26JUL10CURVAN | 64 | 37 | **101** | 97 | +4 |
| ITFWMATCH-26JUL10SUNKAL | 65 | 47 | **112** | 97 | +15 |
| ITFWMATCH-26JUL10YODJAN | 66 | 75 | **141** | 97 | +44 |

## FLOW-STATE — 49 tracked game(s) ({'WAKING': 34, 'OPEN': 14, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10ADDCRA | ITF_M | 1.133 | 3 | **OPEN** |
| ITFMATCH-26JUL10BAYERE | ITF_M | 1.0 | 1 | **OPEN** |
| ITFMATCH-26JUL10CATSNI | ITF_M | 22.5 | 2 | **OPEN** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 22.8 | 1 | **OPEN** |
| ITFMATCH-26JUL10LAGROS | ITF_M | 0.967 | 2 | **OPEN** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 11.667 | 2 | **OPEN** |
| ITFWMATCH-26JUL10DUELEY | ITF_W | 2.467 | 1 | **OPEN** |
| ITFWMATCH-26JUL10FRISOL | ITF_W | 9.1 | 1 | **OPEN** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 3.633 | 3 | **OPEN** |
| ITFWMATCH-26JUL10NAKYAM | ITF_W | 2.567 | 2 | **OPEN** |
| ITFWMATCH-26JUL10NATTOM | ITF_W | 6.067 | 1 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 23.5 | 3 | **OPEN** |
| WTACHALLENGERMATCH-26JUL10CURVAN | WTA_CHALL | 0.6 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL10QUEWAL | WTA_CHALL | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL10DIAMCD | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL10MIDPIR | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL10NEUSQU | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL10ARZBEL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10COCPAN | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10DOUVIR | ITF_M | 0.167 | 4 | **WAKING** |
| ITFMATCH-26JUL10JEDRIV | ITF_M | 1.333 | 4 | **WAKING** |
| ITFMATCH-26JUL10JONBAR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10LOPBAL | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10MAZBRE | ITF_M | 0.233 | 5 | **WAKING** |
| ITFMATCH-26JUL10ORLTSI | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10TYABEA | ITF_M | 0.167 | 4 | **WAKING** |
| ITFMATCH-26JUL10VANKOI | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10VELMON | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10WISMAT | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL10ZAPDUR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10ZGISHI | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10BOJINI | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 11.0 | — | **WAKING** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 0.033 | — | **WAKING** |
| ITFWMATCH-26JUL10FONELS | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10GANSTR | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL10GAOVAN | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10HOSVAN | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10KOVJIA | ITF_W | 0.067 | 3 | **WAKING** |
| ITFWMATCH-26JUL10KUBBER | ITF_W | 0.133 | 2 | **WAKING** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 9.267 | — | **WAKING** |
| ITFWMATCH-26JUL10PEREZZ | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10SUNKAL | ITF_W | 0.733 | 5 | **WAKING** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 0.2 | — | **WAKING** |
| ITFWMATCH-26JUL10VLAMIS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10WIEFOU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 30.3 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL10BLIZAN | WTA_CHALL | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 16
- half_arm_aging: KXITFWMATCH-26JUL10DYUSAG-SAG {"fill": 78, "age_min": 212, "mode": "QUEUE(flow at/below our level, unfilled)"}
- pre_conception_buy: KXITFWMATCH-26JUL10YODJAN-JAN {"price": 66, "conception_ts": 1783666818.2513328, "detail": "buy 66c predates the conception stamp by 130min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL10PLOERC-ERC {"fill": 89, "age_min": 210, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL10CURVAN-VAN {"fill": 64, "age_min": 196, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL10YODJAN-JAN {"fill": 66, "age_min": 190, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10VANKOI-KOI {"fill": 55, "age_min": 173, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10SHOKRO-SHO {"fill": 43, "age_min": 165, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL10NATTOM-TOM {"fill": 87, "age_min": 153, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10BAYERE-ERE {"fill": 90, "age_min": 104, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10FRISOL-SOL {"fill": 37, "age_min": 99, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL10CATSNI-CAT {"fill": 14, "age_min": 80, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10PAWHRU-PAW {"fill": 21, "age_min": 72, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10DENGOL-DEN {"fill": 78, "age_min": 72, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10VIVJAN-VIV {"fill": 72, "age_min": 69, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10KRUSMI-KRU {"fill": 81, "age_min": 58, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10DUELEY-LEY {"fill": 27, "age_min": 50, "mode": "NO_BID(sib rested earlier, none now)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
