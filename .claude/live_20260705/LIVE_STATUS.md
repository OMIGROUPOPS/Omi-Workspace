# LIVE VALIDATION — rolling status

- cycle 353 @ **2026-07-18 02:57:36 PM ET** | build `dbf7e009` | session boot 07-18 13:59 ET | log `live_v3_20260718.jsonl` | 2162 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 164 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL18SAIHOS-HOS aim=26 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- placed:path_aim UL18BASTAI-TAI aim=8 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- placed:path_aim UL18LAJYUN-LAJ aim=33 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- placed:path_aim UL18TIKWAN-WAN aim=38 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 4 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 14:00:30 | **self_fill_bell** | KXITFWMATCH-26JUL18SAIHOS-HOS | own buys rose 10c (26->36) in 1800s -> match-live presumption, entry buys FROZEN |
| 14:00:31 | **self_fill_bell** | KXITFMATCH-26JUL18BASTAI-TAI | own buys rose 4c (8->12) in 1800s -> match-live presumption, entry buys FROZEN |
| 14:00:53 | **self_fill_bell** | KXITFWMATCH-26JUL18SAIHOS-SAI | own buys rose 11c (52->63) in 1800s -> match-live presumption, entry buys FROZEN |
| 14:09:56 | **self_fill_bell** | KXITFMATCH-26JUL18BASTAI-TAI | own buys rose 5c (8->13) in 1800s -> match-live presumption, entry buys FROZEN |

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:17 | ATPCHALLENGERMATCH-26JUL18RODSAN-S | ATP_CHALL | ? | 21 | 18 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:20 | ITFWMATCH-26JUL18THOAIA-THO | ITF_W | ? | 13 | 9 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 10 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 7, 'NO_FLOW': 1, 'FLOW_AT_LEVEL': 2} | repriceable now: true 5 / false 5 | **cumulative bid_grade lines: 12882 (repriceable true 1738 / false 11144)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL18LAJYUN-L | 33 | 51m | 1/37-37/2 | 36-37 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ATPCHALLENGERMATCH-26JUL18LAJYUN-Y | 63 | 56m | 6/64-64/517 | 63-64 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ATPCHALLENGERMATCH-26JUL18TOMJOH-J | 55 | 57m | 7/58-59/566 | 57-59 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→58 |
| ATPCHALLENGERMATCH-26JUL18TOMJOH-T | 39 | 57m | 10/43-43/357 | 42-43 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFMATCH-26JUL18BASTAI-BAS | 73 | 57m | 10/86-87/204 | 84-86 | 13 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL18BASTAI-TAI | 13 | 48m | 30/13-16/1315 | 14-14 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL18SAIHOS-HOS | 36 | 57m | 5/37-37/66 | 36-37 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFWMATCH-26JUL18SAIHOS-SAI | 63 | 57m | 23/63-65/375 | 63-65 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL18THOAIA-AIA | 84 | 37m | 15/86-89/437 | 88-89 | 2 | **FLOW_ABOVE** | 84 | flow above but bound 84c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL18TONSPI-T | 31 | 57m | 0 | 31-59 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL18THOAIA | 13 | 89 | **102** | 97 | +5 |

## FLOW-STATE — 7 tracked game(s) ({'WAKING': 2, 'OPEN': 4, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL18RODSAN | ATP_CHALL | 0.4 | 1 | **OPEN** |
| ITFMATCH-26JUL18BASTAI | ITF_M | 0.967 | 2 | **OPEN** |
| ITFWMATCH-26JUL18SAIHOS | ITF_W | 0.667 | 1 | **OPEN** |
| ITFWMATCH-26JUL18THOAIA | ITF_W | 1.4 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL18TONSPI | WTA_CHALL | 0.0 | 28 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL18LAJYUN | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL18TOMJOH | ATP_CHALL | 0.167 | 1 | **WAKING** |

## PATTERNS (sub-B) — 2
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL18RODSAN-SAN {"fill": 21, "age_min": 40, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-18 02:57:36 PM ET"}
- half_arm_aging: KXITFWMATCH-26JUL18THOAIA-THO {"fill": 13, "age_min": 37, "mode": "SET_BELOW_FLOW(prints 2c above)", "emitted_et": "2026-07-18 02:57:36 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
