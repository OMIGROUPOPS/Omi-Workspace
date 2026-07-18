# LIVE VALIDATION — rolling status

- cycle 264 @ **2026-07-17 11:17:33 PM ET** | build `fe2601c9` | session boot 07-17 21:44 ET | log `live_v3_20260717.jsonl` | 11992 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL18BASKRA-BAS aim=31 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- refused:no_path_page UL18DOTROJ-ROJ aim=None | atlas_page:CONS,contention_s:CONS,pair_state:NOT-,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:THIN,cohort:THIN,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- refused:no_path_page UL18DOTROJ-ROJ aim=None | atlas_page:CONS,contention_s:CONS,pair_state:NOT-,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:THIN,cohort:THIN,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- refused:no_path_page UL18DOTROJ-ROJ aim=None | atlas_page:CONS,contention_s:CONS,pair_state:NOT-,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:THIN,cohort:THIN,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 3 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 21:48:16 | **self_fill_bell** | KXITFMATCH-26JUL18PALWIS-WIS | own buys rose 12c (58->70) in 1800s -> match-live presumption, entry buys FROZEN |
| 21:51:48 | **self_fill_bell** | KXITFMATCH-26JUL18PALWIS-WIS | own buys rose 13c (58->71) in 1800s -> match-live presumption, entry buys FROZEN |
| 22:40:06 | **self_fill_bell** | KXITFMATCH-26JUL18PALWIS-PAL | own buys rose 13c (16->29) in 1800s -> match-live presumption, entry buys FROZEN |

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:50 | WTAMATCH-26JUL18HONTHA-THA | WTA_MAIN | ? | 20 | 18 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 16 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'FLOW_AT_LEVEL': 2, 'NO_FLOW': 8} | repriceable now: true 4 / false 12 | **cumulative bid_grade lines: 12642 (repriceable true 1666 / false 10976)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL18VALDAR-DAR | 62 | 17m | 8/68-68/309 | 67-67 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL18VALDAR-VAL | 30 | 17m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL18AGIOVC-AGI | 22 | 92m | 8/22-24/687 | 22-23 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL18AGIOVC-OVC | 75 | 69m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL18PALWIS-PAL | 29 | 37m | 2/29-30/5 | 29-30 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL18PALWIS-WIS | 72 | 10m | 0 | 72-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL18TORKHO-TOR | 46 | 92m | 1/50-50/19 | 46-50 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| WTACHALLENGERMATCH-26JUL18BASKRA-B | 31 | 3m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL18BASKRA-K | 67 | 38m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL18ERJGRA-E | 54 | 17m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL18BANGAO-BAN | 38 | 53m | 2/39-39/34 | 38-39 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| WTAMATCH-26JUL18BANGAO-GAO | 62 | 53m | 2/63-63/599 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| WTAMATCH-26JUL18HONTHA-HON | 77 | 87m | 5/83-84/793 | 83-83 | 6 | **FLOW_ABOVE** | 77 | flow above but bound 77c < flow -- chasing breaks goal |
| WTAMATCH-26JUL18ITOKNU-KNU | 49 | 17m | 0 | 52-54 | — | **NO_FLOW** | 54 |  |
| WTAMATCH-26JUL18MICFRU-FRU | 74 | 81m | 1/75-75/1 | 74-75 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| WTAMATCH-26JUL18OKALEE-OKA | 17 | 42m | 0 | 18-20 | — | **NO_FLOW** | 18 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTAMATCH-26JUL18HONTHA | 20 | 83 | **103** | 97 | +6 |

## FLOW-STATE — 11 tracked game(s) ({'WAKING': 11}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL18VALDAR | ATP_MAIN | 0.4 | 1 | **WAKING** |
| ITFMATCH-26JUL18AGIOVC | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL18PALWIS | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL18TORKHO | ITF_M | 0.033 | 4 | **WAKING** |
| WTACHALLENGERMATCH-26JUL18BASKRA | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL18ERJGRA | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL18BANGAO | WTA_MAIN | 0.1 | 1 | **WAKING** |
| WTAMATCH-26JUL18HONTHA | WTA_MAIN | 0.067 | — | **WAKING** |
| WTAMATCH-26JUL18ITOKNU | WTA_MAIN | 0.033 | 2 | **WAKING** |
| WTAMATCH-26JUL18MICFRU | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL18OKALEE | WTA_MAIN | 0.0 | 2 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXWTAMATCH-26JUL18HONTHA-THA {"fill": 20, "age_min": 87, "mode": "SET_BELOW_FLOW(prints 6c above)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
