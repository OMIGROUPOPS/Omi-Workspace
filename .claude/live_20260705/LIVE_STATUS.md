# LIVE VALIDATION — rolling status

- cycle 18 @ **2026-07-10 03:51:01 AM ET** | build `48f25fff` | session boot 07-10 00:49 ET | log `live_v3_20260710.jsonl` | 26908 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 17 graded (session)
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
| 03:31 | ITFWMATCH-26JUL10DUELEY-LEY | ITF_W | ? | 27 | 23 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 47 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 19, 'FLOW_AT_LEVEL': 6, 'FLOW_ABOVE': 22} | repriceable now: true 17 / false 30 | **cumulative bid_grade lines: 7567 (repriceable true 1009 / false 6558)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10ADDCRA-ADD | 32 | 179m | 1/36-36/13 | 32-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFMATCH-26JUL10ADDCRA-CRA | 64 | 181m | 2/69-69/21 | 64-68 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-ARZ | 75 | 181m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-BEL | 20 | 181m | 1/23-23/82 | 20-25 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFMATCH-26JUL10COCPAN-PAN | 76 | 181m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10DOUVIR-VIR | 5 | 181m | 10/8-9/444 | 5-8 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL10JEDRIV-JED | 47 | 167m | 3/50-51/320 | 47-51 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFMATCH-26JUL10JONBAR-BAR | 63 | 181m | 0 | 63-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LAGROS-LAG | 33 | 181m | 1/36-36/5 | 33-36 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFMATCH-26JUL10LOPBAL-LOP | 77 | 141m | 0 | 77-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MAZBRE-BRE | 45 | 181m | 0 | 45-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MAZBRE-MAZ | 54 | 181m | 2/57-57/30 | 54-57 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFMATCH-26JUL10ORLTSI-ORL | 81 | 140m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ORLTSI-TSI | 16 | 141m | 1/20-20/23 | 16-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL10TYABEA-BEA | 40 | 166m | 2/44-44/6 | 40-44 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ITFMATCH-26JUL10TYABEA-TYA | 56 | 181m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VELMON-MON | 75 | 181m | 1/80-80/12 | 75-80 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10VELMON-VEL | 19 | 181m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-DUR | 79 | 181m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-ZAP | 19 | 181m | 1/21-21/8 | 19-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFMATCH-26JUL10ZGISHI-SHI | 60 | 176m | 1/60-60/7 | 60-61 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL10ZGISHI-ZGI | 37 | 181m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10BOJINI-BOJ | 55 | 181m | 2/56-56/2 | 55-56 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ITFWMATCH-26JUL10BOJINI-INI | 43 | 181m | 0 | 43-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DYUSAG-DYU | 16 | 160m | 5141/1-60/775427 | 1-1 | -15 | **FLOW_AT_LEVEL** | 4 |  |
| ITFWMATCH-26JUL10FONELS-ELS | 20 | 181m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FONELS-FON | 74 | 181m | 1/79-79/1 | 74-79 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-GAN | 18 | 181m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-STR | 76 | 181m | 1/81-81/1 | 76-81 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10GAOVAN-GAO | 27 | 141m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-HOS | 53 | 181m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-VAN | 44 | 181m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KOVJIA-JIA | 46 | 181m | 0 | 46-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KUBBER-BER | 9 | 181m | 14/9-11/432 | 9-10 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-NAK | 56 | 181m | 4/56-57/45 | 56-57 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-YAM | 42 | 181m | 1/43-43/11 | 42-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFWMATCH-26JUL10PEREZZ-EZZ | 34 | 181m | 0 | 34-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PEREZZ-PER | 61 | 181m | 1/65-65/1 | 61-65 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFWMATCH-26JUL10SUNKAL-KAL | 65 | 164m | 2/68-68/76 | 65-68 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFWMATCH-26JUL10SUNKAL-SUN | 32 | 166m | 1/34-34/14 | 32-34 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL10TUPMAK-MAK | 47 | 155m | 2912/18-99/310157 | 99-98 | -29 | **FLOW_AT_LEVEL** | 55 |  |
| ITFWMATCH-26JUL10VLAMIS-VLA | 18 | 179m | 1/22-22/17 | 18-20 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL10WIEFOU-FOU | 61 | 181m | 1/63-63/1 | 61-63 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL10WIEFOU-WIE | 36 | 181m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10CURVAN-C | 33 | 164m | 19/36-38/2402 | 35-36 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL10QUEWAL-Q | 33 | 170m | 25/33-34/1505 | 33-34 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL10QUEWAL-W | 67 | 171m | 38/68-68/10348 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10SHOKRO | 43 | 1 | **44** | 97 | -53 |
| ITFWMATCH-26JUL10DYUSAG | 78 | 1 | **79** | 97 | -18 |
| WTACHALLENGERMATCH-26JUL10CURVAN | 64 | 36 | **100** | 97 | +3 |
| ITFWMATCH-26JUL10YODJAN | 66 | 75 | **141** | 97 | +44 |

## FLOW-STATE — 44 tracked game(s) ({'WAKING': 32, 'OPEN': 11, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10CATSNI | ITF_M | 9.867 | 1 | **OPEN** |
| ITFMATCH-26JUL10DOUVIR | ITF_M | 0.267 | 3 | **OPEN** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 7.167 | 3 | **OPEN** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 4.5 | 1 | **OPEN** |
| ITFWMATCH-26JUL10DUELEY | ITF_W | 0.833 | 3 | **OPEN** |
| ITFWMATCH-26JUL10FRISOL | ITF_W | 3.867 | 1 | **OPEN** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 0.233 | 2 | **OPEN** |
| ITFWMATCH-26JUL10NATTOM | ITF_W | 1.967 | 1 | **OPEN** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 3.133 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL10CURVAN | WTA_CHALL | 0.367 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL10QUEWAL | WTA_CHALL | 0.333 | 1 | **OPEN** |
| ITFWMATCH-26JUL10KOVJIA | ITF_W | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL10ADDCRA | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL10ARZBEL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10BAYERE | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10COCPAN | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10JEDRIV | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10JONBAR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10LAGROS | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10LOPBAL | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10MAZBRE | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL10ORLTSI | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10TYABEA | ITF_M | 0.067 | 4 | **WAKING** |
| ITFMATCH-26JUL10VANKOI | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10VELMON | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10ZAPDUR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10ZGISHI | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10BOJINI | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 3.3 | — | **WAKING** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 50.433 | — | **WAKING** |
| ITFWMATCH-26JUL10FONELS | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10GANSTR | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10GAOVAN | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10HOSVAN | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10KUBBER | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL10NAKYAM | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL10PEREZZ | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 6.1 | — | **WAKING** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 12.5 | — | **WAKING** |
| ITFWMATCH-26JUL10SUNKAL | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 33.333 | — | **WAKING** |
| ITFWMATCH-26JUL10VLAMIS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10WIEFOU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 86.967 | — | **WAKING** |

## PATTERNS (sub-B) — 14
- half_arm_aging: KXITFWMATCH-26JUL10DYUSAG-SAG {"fill": 78, "age_min": 181, "mode": "QUEUE(flow at/below our level, unfilled)"}
- pre_conception_buy: KXITFWMATCH-26JUL10YODJAN-JAN {"price": 66, "conception_ts": 1783666818.2513328, "detail": "buy 66c predates the conception stamp by 130min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL10PLOERC-ERC {"fill": 89, "age_min": 179, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL10CURVAN-VAN {"fill": 64, "age_min": 165, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL10YODJAN-JAN {"fill": 66, "age_min": 159, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10VANKOI-KOI {"fill": 55, "age_min": 143, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10SHOKRO-SHO {"fill": 43, "age_min": 135, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL10NATTOM-TOM {"fill": 87, "age_min": 123, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10BAYERE-ERE {"fill": 90, "age_min": 74, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10FRISOL-SOL {"fill": 37, "age_min": 69, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL10CATSNI-CAT {"fill": 14, "age_min": 49, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10PAWHRU-PAW {"fill": 21, "age_min": 42, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10DENGOL-DEN {"fill": 78, "age_min": 41, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10VIVJAN-VIV {"fill": 72, "age_min": 38, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-10 03:51:01 AM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
