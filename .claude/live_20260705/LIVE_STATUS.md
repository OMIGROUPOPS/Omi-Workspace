# LIVE VALIDATION — rolling status

- cycle 355 @ **2026-07-18 03:17:53 PM ET** | build `10bead48` | session boot 07-18 13:59 ET | log `live_v3_20260718.jsonl` | 2858 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 185 min ago (>30 tripwire; source observed_starts.db)

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

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:17 | ATPCHALLENGERMATCH-26JUL18RODSAN-S | ATP_CHALL | ? | 21 | 18 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:20 | ITFWMATCH-26JUL18THOAIA-THO | ITF_W | ? | 13 | 9 | +4 (fill_est) | — | pre | single |  | PENDING |
| 15:03 | ITFWMATCH-26JUL18SAIHOS-HOS | ITF_W | underdog | 36 | 33 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 7 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 1} | repriceable now: true 4 / false 3 | **cumulative bid_grade lines: 12884 (repriceable true 1738 / false 11146)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL18LAJYUN-L | 33 | 71m | 1/37-37/2 | 36-37 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ATPCHALLENGERMATCH-26JUL18LAJYUN-Y | 63 | 76m | 9/64-64/667 | 63-64 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ATPCHALLENGERMATCH-26JUL18TOMJOH-J | 55 | 78m | 11/58-59/1455 | 58-59 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→58 |
| ATPCHALLENGERMATCH-26JUL18TOMJOH-T | 39 | 78m | 13/43-43/489 | 42-43 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFWMATCH-26JUL18SAIHOS-SAI | 52 | 14m | 2/65-65/400 | 63-65 | 13 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL18THOAIA-AIA | 84 | 57m | 15/86-89/437 | 84-89 | 2 | **FLOW_ABOVE** | 84 | flow above but bound 84c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL18TONSPI-T | 31 | 78m | 0 | 31-59 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL18SAIHOS | 36 | 65 | **101** | 97 | +4 |
| ITFWMATCH-26JUL18THOAIA | 13 | 89 | **102** | 97 | +5 |

## FLOW-STATE — 6 tracked game(s) ({'WAKING': 1, 'OPEN': 4, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL18RODSAN | ATP_CHALL | 0.433 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL18TOMJOH | ATP_CHALL | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL18SAIHOS | ITF_W | 0.667 | 2 | **OPEN** |
| ITFWMATCH-26JUL18THOAIA | ITF_W | 0.5 | 2 | **OPEN** |
| WTACHALLENGERMATCH-26JUL18TONSPI | WTA_CHALL | 0.0 | 28 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL18LAJYUN | ATP_CHALL | 0.133 | 1 | **WAKING** |

## PATTERNS (sub-B) — 2
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL18RODSAN-SAN {"fill": 21, "age_min": 60, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL18THOAIA-THO {"fill": 13, "age_min": 57, "mode": "SET_BELOW_FLOW(prints 2c above)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
