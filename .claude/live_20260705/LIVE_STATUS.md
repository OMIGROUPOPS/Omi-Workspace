# LIVE VALIDATION — rolling status

- cycle 16 @ **2026-07-10 03:30:43 AM ET** | build `b7338360` | session boot 07-10 00:49 ET | log `live_v3_20260710.jsonl` | 21079 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 16 graded (session)
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
| 03:23 | ITFWMATCH-26JUL10KRUSMI-KRU | ITF_W | ? | 81 | 79 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 51 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 21, 'FLOW_ABOVE': 24, 'FLOW_AT_LEVEL': 6} | repriceable now: true 19 / false 32 | **cumulative bid_grade lines: 7565 (repriceable true 1007 / false 6558)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10ADDCRA-ADD | 32 | 158m | 1/36-36/13 | 32-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFMATCH-26JUL10ADDCRA-CRA | 64 | 161m | 2/69-69/21 | 64-68 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-ARZ | 75 | 161m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-BEL | 20 | 161m | 1/23-23/82 | 20-25 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFMATCH-26JUL10COCPAN-PAN | 76 | 161m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10DOUVIR-VIR | 5 | 161m | 5/8-9/341 | 5-8 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL10JEDRIV-JED | 47 | 146m | 3/50-51/320 | 47-51 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFMATCH-26JUL10JONBAR-BAR | 63 | 161m | 0 | 63-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LAGROS-LAG | 33 | 161m | 1/36-36/5 | 33-36 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFMATCH-26JUL10LOPBAL-LOP | 77 | 120m | 0 | 77-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MAZBRE-BRE | 45 | 161m | 0 | 45-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MAZBRE-MAZ | 54 | 161m | 2/57-57/30 | 54-57 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFMATCH-26JUL10ORLTSI-ORL | 81 | 120m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ORLTSI-TSI | 16 | 120m | 1/20-20/23 | 16-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL10ROBDEC-ROB | 39 | 161m | 1/43-43/10 | 40-48 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFMATCH-26JUL10TYABEA-BEA | 40 | 146m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10TYABEA-TYA | 56 | 161m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VELMON-MON | 75 | 161m | 1/80-80/12 | 75-81 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10VELMON-VEL | 19 | 161m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-DUR | 79 | 161m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-ZAP | 19 | 161m | 1/21-21/8 | 19-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFMATCH-26JUL10ZGISHI-SHI | 60 | 156m | 1/60-60/7 | 60-61 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL10ZGISHI-ZGI | 37 | 161m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10BOJINI-BOJ | 55 | 161m | 2/56-56/2 | 55-56 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ITFWMATCH-26JUL10BOJINI-INI | 43 | 161m | 0 | 43-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10CIRGRA-CIR | 22 | 161m | 4/23-28/142 | 22-28 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFWMATCH-26JUL10DUELEY-LEY | 27 | 161m | 4/30-31/54 | 27-54 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→30 |
| ITFWMATCH-26JUL10DYUSAG-DYU | 16 | 140m | 4528/5-60/631447 | 14-15 | -11 | **FLOW_AT_LEVEL** | 4 |  |
| ITFWMATCH-26JUL10FONELS-ELS | 20 | 161m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FONELS-FON | 74 | 161m | 1/79-79/1 | 74-79 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-GAN | 18 | 161m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-STR | 76 | 161m | 1/81-81/1 | 76-81 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10GAOVAN-GAO | 27 | 120m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10GAOVAN-VAN | 70 | 120m | 1/73-73/1 | 70-73 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFWMATCH-26JUL10HOSVAN-HOS | 53 | 161m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-VAN | 44 | 161m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KOVJIA-JIA | 46 | 161m | 0 | 46-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KUBBER-BER | 9 | 161m | 12/9-11/357 | 9-10 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-NAK | 56 | 161m | 4/56-57/45 | 56-57 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-YAM | 42 | 161m | 1/43-43/11 | 42-43 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFWMATCH-26JUL10PEREZZ-EZZ | 34 | 161m | 0 | 34-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PEREZZ-PER | 61 | 161m | 1/65-65/1 | 61-65 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFWMATCH-26JUL10SUNKAL-KAL | 65 | 144m | 2/68-68/76 | 65-68 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFWMATCH-26JUL10SUNKAL-SUN | 32 | 146m | 0 | 32-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10TUPMAK-MAK | 47 | 135m | 2139/18-91/192404 | 80-84 | -29 | **FLOW_AT_LEVEL** | 55 |  |
| ITFWMATCH-26JUL10VLAMIS-VLA | 18 | 158m | 1/22-22/17 | 18-20 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL10WIEFOU-FOU | 61 | 161m | 1/63-63/1 | 61-63 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL10WIEFOU-WIE | 36 | 161m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10CURVAN-C | 33 | 144m | 16/36-38/2323 | 35-36 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL10QUEWAL-Q | 33 | 150m | 21/33-34/1385 | 33-34 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL10QUEWAL-W | 67 | 150m | 37/68-68/10334 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10SHOKRO | 43 | 3 | **46** | 97 | -51 |
| ITFWMATCH-26JUL10DYUSAG | 78 | 15 | **93** | 97 | -4 |
| WTACHALLENGERMATCH-26JUL10CURVAN | 64 | 36 | **100** | 97 | +3 |
| ITFWMATCH-26JUL10YODJAN | 66 | 66 | **132** | 97 | +35 |

## FLOW-STATE — 46 tracked game(s) ({'WAKING': 33, 'OPEN': 11, 'QUIET': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10CATSNI | ITF_M | 2.567 | 3 | **OPEN** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 3.433 | 1 | **OPEN** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 1.267 | 1 | **OPEN** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 1.533 | 1 | **OPEN** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 43.067 | 1 | **OPEN** |
| ITFWMATCH-26JUL10NATTOM | ITF_W | 1.367 | 3 | **OPEN** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 2.5 | 1 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 2.667 | 1 | **OPEN** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 20.833 | 1 | **OPEN** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 34.967 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL10QUEWAL | WTA_CHALL | 0.4 | 1 | **OPEN** |
| ITFMATCH-26JUL10VELMON | ITF_M | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL10KOVJIA | ITF_W | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL10ADDCRA | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10ARZBEL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10BAYERE | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10COCPAN | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10DOUVIR | ITF_M | 0.1 | 3 | **WAKING** |
| ITFMATCH-26JUL10JEDRIV | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10JONBAR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10LAGROS | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10LOPBAL | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10MAZBRE | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL10ORLTSI | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10ROBDEC | ITF_M | 0.033 | 8 | **WAKING** |
| ITFMATCH-26JUL10TYABEA | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10VANKOI | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10ZAPDUR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10ZGISHI | ITF_M | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL10BOJINI | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL10CIRGRA | ITF_W | 0.067 | 6 | **WAKING** |
| ITFWMATCH-26JUL10DUELEY | ITF_W | 0.067 | 27 | **WAKING** |
| ITFWMATCH-26JUL10FONELS | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10FRISOL | ITF_W | 1.533 | 4 | **WAKING** |
| ITFWMATCH-26JUL10GANSTR | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10GAOVAN | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL10HOSVAN | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 0.067 | 10 | **WAKING** |
| ITFWMATCH-26JUL10KUBBER | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10NAKYAM | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL10PEREZZ | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10SUNKAL | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 20.833 | 4 | **WAKING** |
| ITFWMATCH-26JUL10VLAMIS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10WIEFOU | ITF_W | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL10CURVAN | WTA_CHALL | 0.267 | 1 | **WAKING** |

## PATTERNS (sub-B) — 10
- half_arm_aging: KXITFWMATCH-26JUL10DYUSAG-SAG {"fill": 78, "age_min": 161, "mode": "QUEUE(flow at/below our level, unfilled)"}
- pre_conception_buy: KXITFWMATCH-26JUL10YODJAN-JAN {"price": 66, "conception_ts": 1783666818.2513328, "detail": "buy 66c predates the conception stamp by 130min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL10PLOERC-ERC {"fill": 89, "age_min": 159, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL10CURVAN-VAN {"fill": 64, "age_min": 145, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL10YODJAN-JAN {"fill": 66, "age_min": 139, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10VANKOI-KOI {"fill": 55, "age_min": 123, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10SHOKRO-SHO {"fill": 43, "age_min": 115, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL10NATTOM-TOM {"fill": 87, "age_min": 102, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10BAYERE-ERE {"fill": 90, "age_min": 53, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10FRISOL-SOL {"fill": 37, "age_min": 48, "mode": "PAIRING(sib never rested)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
