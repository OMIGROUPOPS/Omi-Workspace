# LIVE VALIDATION — rolling status

- cycle 19 @ **2026-07-10 04:01:17 AM ET** | build `2ed7b091` | session boot 07-10 00:49 ET | log `live_v3_20260710.jsonl` | 30595 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 17 graded (session)
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

## RESTING BIDS — 52 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 27, 'FLOW_AT_LEVEL': 5, 'FLOW_ABOVE': 20} | repriceable now: true 14 / false 38 | **cumulative bid_grade lines: 7576 (repriceable true 1009 / false 6567)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL10MIDPIR-M | 32 | 0m | 0 | 32-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ADDCRA-ADD | 32 | 189m | 2/36-36/13 | 32-38 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFMATCH-26JUL10ADDCRA-CRA | 64 | 191m | 2/69-69/21 | 64-70 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-ARZ | 75 | 191m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ARZBEL-BEL | 20 | 191m | 1/23-23/82 | 20-25 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFMATCH-26JUL10COCPAN-PAN | 76 | 191m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10DOUVIR-VIR | 5 | 191m | 12/8-9/501 | 5-9 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL10JEDRIV-JED | 47 | 177m | 5/50-51/339 | 47-50 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFMATCH-26JUL10JONBAR-BAR | 63 | 191m | 0 | 63-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LAGROS-LAG | 32 | 1m | 0 | 32-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10LOPBAL-LOP | 77 | 151m | 0 | 77-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MAZBRE-BRE | 43 | 1m | 0 | 43-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10MAZBRE-MAZ | 54 | 191m | 4/57-57/54 | 54-58 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFMATCH-26JUL10ORLTSI-ORL | 81 | 150m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ORLTSI-TSI | 16 | 151m | 1/20-20/23 | 16-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL10TYABEA-BEA | 40 | 176m | 6/44-44/18 | 40-44 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ITFMATCH-26JUL10TYABEA-TYA | 56 | 191m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10VELMON-MON | 75 | 191m | 1/80-80/12 | 75-81 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL10VELMON-VEL | 19 | 191m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10WISMAT-MAT | 43 | 0m | 0 | 44-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10WISMAT-WIS | 54 | 0m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-DUR | 79 | 191m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL10ZAPDUR-ZAP | 19 | 191m | 1/21-21/8 | 19-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFMATCH-26JUL10ZGISHI-SHI | 60 | 186m | 1/60-60/7 | 60-61 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL10ZGISHI-ZGI | 37 | 191m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10BOJINI-BOJ | 55 | 191m | 2/56-56/2 | 55-56 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ITFWMATCH-26JUL10BOJINI-INI | 43 | 191m | 0 | 43-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10DYUSAG-DYU | 16 | 170m | 5142/1-60/775520 | 1-1 | -15 | **FLOW_AT_LEVEL** | 4 |  |
| ITFWMATCH-26JUL10FONELS-ELS | 20 | 191m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10FONELS-FON | 74 | 191m | 1/79-79/1 | 74-79 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-GAN | 18 | 191m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10GANSTR-STR | 76 | 191m | 1/81-81/1 | 76-81 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10GAOVAN-GAO | 27 | 151m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-HOS | 53 | 191m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10HOSVAN-VAN | 44 | 191m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KOVJIA-JIA | 46 | 191m | 0 | 46-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10KUBBER-BER | 9 | 191m | 16/9-11/476 | 9-10 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-NAK | 55 | 1m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10NAKYAM-YAM | 41 | 1m | 0 | 41-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PEREZZ-EZZ | 34 | 191m | 0 | 34-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10PEREZZ-PER | 61 | 191m | 1/65-65/1 | 61-65 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFWMATCH-26JUL10SUNKAL-KAL | 65 | 174m | 4/68-68/99 | 65-70 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFWMATCH-26JUL10SUNKAL-SUN | 32 | 176m | 2/34-34/15 | 32-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL10TUPMAK-MAK | 47 | 166m | 2921/18-99/312722 | 99-98 | -29 | **FLOW_AT_LEVEL** | 55 |  |
| ITFWMATCH-26JUL10VLAMIS-VLA | 18 | 189m | 1/22-22/17 | 18-20 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL10WIEFOU-FOU | 61 | 191m | 1/63-63/1 | 61-63 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL10WIEFOU-WIE | 36 | 191m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10BLIZAN-B | 74 | 0m | 0 | 74-76 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10BLIZAN-Z | 24 | 0m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL10CURVAN-C | 33 | 175m | 19/36-38/2402 | 35-36 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL10QUEWAL-Q | 33 | 181m | 27/33-34/1699 | 33-34 | 0 | **FLOW_AT_LEVEL** | 31 |  |
| WTACHALLENGERMATCH-26JUL10QUEWAL-W | 67 | 181m | 39/68-68/10490 | 67-69 | 1 | **FLOW_ABOVE** | 65 | flow above but bound 65c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL10SHOKRO | 43 | 1 | **44** | 97 | -53 |
| ITFWMATCH-26JUL10DYUSAG | 78 | 1 | **79** | 97 | -18 |
| WTACHALLENGERMATCH-26JUL10CURVAN | 64 | 36 | **100** | 97 | +3 |
| ITFWMATCH-26JUL10YODJAN | 66 | 75 | **141** | 97 | +44 |

## FLOW-STATE — 47 tracked game(s) ({'WAKING': 34, 'OPEN': 10, 'QUIET': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10CATSNI | ITF_M | 14.733 | 2 | **OPEN** |
| ITFMATCH-26JUL10FABOBR | ITF_M | 9.833 | 1 | **OPEN** |
| ITFMATCH-26JUL10VIVJAN | ITF_M | 7.367 | 1 | **OPEN** |
| ITFWMATCH-26JUL10DENGOL | ITF_W | 6.233 | 1 | **OPEN** |
| ITFWMATCH-26JUL10DUELEY | ITF_W | 1.8 | 2 | **OPEN** |
| ITFWMATCH-26JUL10FRISOL | ITF_W | 5.633 | 1 | **OPEN** |
| ITFWMATCH-26JUL10NATTOM | ITF_W | 4.133 | 1 | **OPEN** |
| ITFWMATCH-26JUL10PAWHRU | ITF_W | 4.6 | 1 | **OPEN** |
| ITFWMATCH-26JUL10PLOERC | ITF_W | 11.6 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL10CURVAN | WTA_CHALL | 0.367 | 1 | **OPEN** |
| ITFMATCH-26JUL10LAGROS | ITF_M | 0.0 | 18 | **QUIET** |
| ITFMATCH-26JUL10VELMON | ITF_M | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL10KOVJIA | ITF_W | 0.0 | 6 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL10MIDPIR | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL10ADDCRA | ITF_M | 0.033 | 6 | **WAKING** |
| ITFMATCH-26JUL10ARZBEL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL10BAYERE | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10COCPAN | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10DOUVIR | ITF_M | 0.233 | 4 | **WAKING** |
| ITFMATCH-26JUL10JEDRIV | ITF_M | 0.067 | 3 | **WAKING** |
| ITFMATCH-26JUL10JONBAR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10LOPBAL | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL10MAZBRE | ITF_M | 0.067 | 4 | **WAKING** |
| ITFMATCH-26JUL10ORLTSI | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10TYABEA | ITF_M | 0.2 | 4 | **WAKING** |
| ITFMATCH-26JUL10VANKOI | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL10WISMAT | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL10ZAPDUR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL10ZGISHI | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10BOJINI | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 31.933 | — | **WAKING** |
| ITFWMATCH-26JUL10FONELS | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10GANSTR | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL10GAOVAN | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10HOSVAN | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10KRUSMI | ITF_W | 1.233 | — | **WAKING** |
| ITFWMATCH-26JUL10KUBBER | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL10NAKYAM | ITF_W | 0.067 | 4 | **WAKING** |
| ITFWMATCH-26JUL10PEREZZ | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 5.067 | — | **WAKING** |
| ITFWMATCH-26JUL10SUNKAL | ITF_W | 0.133 | 5 | **WAKING** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 25.433 | — | **WAKING** |
| ITFWMATCH-26JUL10VLAMIS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10WIEFOU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 100.433 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL10BLIZAN | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL10QUEWAL | WTA_CHALL | 0.233 | 1 | **WAKING** |

## PATTERNS (sub-B) — 15
- half_arm_aging: KXITFWMATCH-26JUL10DYUSAG-SAG {"fill": 78, "age_min": 191, "mode": "QUEUE(flow at/below our level, unfilled)"}
- pre_conception_buy: KXITFWMATCH-26JUL10YODJAN-JAN {"price": 66, "conception_ts": 1783666818.2513328, "detail": "buy 66c predates the conception stamp by 130min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL10PLOERC-ERC {"fill": 89, "age_min": 190, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL10CURVAN-VAN {"fill": 64, "age_min": 176, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL10YODJAN-JAN {"fill": 66, "age_min": 170, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10VANKOI-KOI {"fill": 55, "age_min": 153, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10SHOKRO-SHO {"fill": 43, "age_min": 145, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL10NATTOM-TOM {"fill": 87, "age_min": 133, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10BAYERE-ERE {"fill": 90, "age_min": 84, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10FRISOL-SOL {"fill": 37, "age_min": 79, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL10CATSNI-CAT {"fill": 14, "age_min": 59, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10PAWHRU-PAW {"fill": 21, "age_min": 52, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10DENGOL-DEN {"fill": 78, "age_min": 52, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL10VIVJAN-VIV {"fill": 72, "age_min": 49, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL10KRUSMI-KRU {"fill": 81, "age_min": 37, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-10 04:01:17 AM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
