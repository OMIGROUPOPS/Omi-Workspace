# LIVE VALIDATION — rolling status

- cycle 15 @ **2026-07-10 03:20:35 AM ET** | build `63d2f253` | session boot 07-10 00:49 ET | log `live_v3_20260710.jsonl` | 17650 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 15 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:49 | ITFWMATCH-26JUL10DYUSAG-SAG | ITF_W | ? | 78 | 92 | -14 (window_cell) | — | pre | single |  | MIXED |
| 00:51 | ITFWMATCH-26JUL10PLOERC-ERC | ITF_W | ? | 89 | 87 | +2 (fill_est) | — | pre | single |  | PENDING |
| 01:05 | WTACHALLENGERMATCH-26JUL10CURVAN-V | WTA_CHALL | leader | 64 | 62 | +2 (place_cell) | — | pre | single |  | PENDING |
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

## RESTING BIDS — 54 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 25, 'FLOW_ABOVE': 22, 'FLOW_AT_LEVEL': 7} | repriceable now: true 17 / false 37 | **cumulative bid_grade lines: 7561 (repriceable true 1003 / false 6558)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10ADDCRA-ADD | 32 | 148m | 0 | 32-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ADDCRA-CRA | 64 | 151m | 2/69-69/21 | 64-68 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-ARZ | 75 | 151m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-BEL | 20 | 151m | 1/23-23/82 | 20-25 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFMATCH-26JUL10COCPAN-PAN | 76 | 151m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10DOUVIR-VIR | 5 | 151m | 2/8-9/324 | 5-8 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL10JEDRIV-JED | 47 | 136m | 3/50-51/320 | 47-51 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFMATCH-26JUL10JONBAR-BAR | 63 | 151m | 0 | 63-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LAGROS-LAG | 33 | 151m | 1/36-36/5 | 33-36 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFMATCH-26JUL10LOPBAL-LOP | 77 | 110m | 0 | 77-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MAZBRE-BRE | 45 | 151m | 0 | 45-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MAZBRE-MAZ | 54 | 151m | 2/57-57/30 | 54-57 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFMATCH-26JUL10ORLTSI-ORL | 81 | 110m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ORLTSI-TSI | 16 | 110m | 1/20-20/23 | 16-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL10ROBDEC-ROB | 39 | 151m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10TYABEA-BEA | 40 | 135m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10TYABEA-TYA | 56 | 151m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VELMON-MON | 75 | 151m | 1/80-80/12 | 75-80 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10VELMON-VEL | 19 | 151m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-DUR | 79 | 151m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-ZAP | 19 | 151m | 1/21-21/8 | 19-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFMATCH-26JUL10ZGISHI-SHI | 60 | 145m | 1/60-60/7 | 60-61 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL10ZGISHI-ZGI | 37 | 151m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10BOJINI-BOJ | 55 | 151m | 2/56-56/2 | 55-56 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ITFWMATCH-26JUL10BOJINI-INI | 43 | 151m | 0 | 43-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10CIRGRA-CIR | 22 | 151m | 2/23-23/106 | 22-24 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFWMATCH-26JUL10DUELEY-DUE | 69 | 151m | 2/73-73/18 | 69-74 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFWMATCH-26JUL10DUELEY-LEY | 27 | 151m | 2/30-31/24 | 27-30 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→30 |
| ITFWMATCH-26JUL10DYUSAG-DYU | 16 | 129m | 4167/5-60/583645 | 22-23 | -11 | **FLOW_AT_LEVEL** | 4 |  |
| ITFWMATCH-26JUL10FONELS-ELS | 20 | 151m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FONELS-FON | 74 | 151m | 1/79-79/1 | 74-79 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-GAN | 18 | 151m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-STR | 76 | 151m | 1/81-81/1 | 76-81 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10GAOVAN-GAO | 27 | 110m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10GAOVAN-VAN | 70 | 110m | 0 | 70-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-HOS | 53 | 151m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-VAN | 44 | 151m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KOVJIA-JIA | 46 | 151m | 0 | 46-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KRUSMI-KRU | 81 | 148m | 7/81-83/126 | 81-83 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10KRUSMI-SMI | 19 | 151m | 4/20-21/39 | 19-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFWMATCH-26JUL10KUBBER-BER | 9 | 151m | 12/9-11/357 | 9-10 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-NAK | 56 | 151m | 3/56-57/11 | 56-57 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-YAM | 42 | 151m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PEREZZ-EZZ | 34 | 151m | 0 | 34-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PEREZZ-PER | 61 | 151m | 1/65-65/1 | 61-65 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFWMATCH-26JUL10SUNKAL-KAL | 65 | 133m | 2/68-68/76 | 65-68 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFWMATCH-26JUL10SUNKAL-SUN | 32 | 135m | 0 | 32-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10TUPMAK-MAK | 47 | 125m | 1906/18-84/165907 | 80-83 | -29 | **FLOW_AT_LEVEL** | 55 |  |
| ITFWMATCH-26JUL10VLAMIS-VLA | 18 | 148m | 1/22-22/17 | 18-20 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL10WIEFOU-FOU | 61 | 151m | 1/63-63/1 | 61-63 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL10WIEFOU-WIE | 36 | 151m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10CURVAN-C | 33 | 134m | 15/36-38/2322 | 35-36 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL10QUEWAL-Q | 33 | 140m | 17/33-34/973 | 33-34 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL10QUEWAL-W | 67 | 140m | 36/68-68/10306 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10SHOKRO | 43 | 1 | **44** | 97 | -53 |
| WTACHALLENGERMATCH-26JUL10CURVAN | 64 | 36 | **100** | 97 | +3 |
| ITFWMATCH-26JUL10DYUSAG | 78 | 23 | **101** | 97 | +4 |
| ITFWMATCH-26JUL10YODJAN | 66 | 59 | **125** | 97 | +28 |

## FLOW-STATE — 46 tracked game(s) ({'WAKING': 33, 'OPEN': 12, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10CATSNI | ITF_M | 1.0 | 3 | **OPEN** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 0.667 | 1 | **OPEN** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 0.433 | 2 | **OPEN** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 0.467 | 3 | **OPEN** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 47.6 | 1 | **OPEN** |
| ITFWMATCH-26JUL10FRISOL | ITF_W | 0.533 | 3 | **OPEN** |
| ITFWMATCH-26JUL10NATTOM | ITF_W | 0.867 | 2 | **OPEN** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 1.267 | 2 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 1.0 | 1 | **OPEN** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 24.6 | 3 | **OPEN** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 21.033 | 2 | **OPEN** |
| WTACHALLENGERMATCH-26JUL10QUEWAL | WTA_CHALL | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL10KOVJIA | ITF_W | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL10ADDCRA | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10ARZBEL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10BAYERE | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10COCPAN | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10DOUVIR | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10JEDRIV | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10JONBAR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10LAGROS | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10LOPBAL | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10MAZBRE | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL10ORLTSI | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10ROBDEC | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10TYABEA | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10VANKOI | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10VELMON | ITF_M | 0.033 | 5 | **WAKING** |
| ITFMATCH-26JUL10ZAPDUR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10ZGISHI | ITF_M | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL10BOJINI | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL10CIRGRA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10DUELEY | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10FONELS | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10GANSTR | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10GAOVAN | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10HOSVAN | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL10KUBBER | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10NAKYAM | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL10PEREZZ | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 17.567 | — | **WAKING** |
| ITFWMATCH-26JUL10SUNKAL | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10VLAMIS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10WIEFOU | ITF_W | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL10CURVAN | WTA_CHALL | 0.233 | 1 | **WAKING** |

## PATTERNS (sub-B) — 10
- half_arm_aging: KXITFWMATCH-26JUL10DYUSAG-SAG {"fill": 78, "age_min": 151, "mode": "QUEUE(flow at/below our level, unfilled)"}
- pre_conception_buy: KXITFWMATCH-26JUL10YODJAN-JAN {"price": 66, "conception_ts": 1783666818.2513328, "detail": "buy 66c predates the conception stamp by 130min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL10PLOERC-ERC {"fill": 89, "age_min": 149, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL10CURVAN-VAN {"fill": 64, "age_min": 135, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL10YODJAN-JAN {"fill": 66, "age_min": 129, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10VANKOI-KOI {"fill": 55, "age_min": 112, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10SHOKRO-SHO {"fill": 43, "age_min": 104, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL10NATTOM-TOM {"fill": 87, "age_min": 92, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10BAYERE-ERE {"fill": 90, "age_min": 43, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10FRISOL-SOL {"fill": 37, "age_min": 38, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-10 03:20:35 AM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
