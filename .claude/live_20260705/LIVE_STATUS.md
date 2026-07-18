# LIVE VALIDATION — rolling status

- cycle 351 @ **2026-07-18 02:37:23 PM ET** | build `e8f8e867` | session boot 07-18 13:59 ET | log `live_v3_20260718.jsonl` | 1627 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 144 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL18BASTAI-BAS aim=73 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- placed:path_aim UL18SAIHOS-HOS aim=26 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- placed:path_aim UL18BASTAI-TAI aim=8 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- placed:path_aim UL18LAJYUN-LAJ aim=33 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS

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

## RESTING BIDS — 11 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 8, 'NO_FLOW': 1, 'FLOW_AT_LEVEL': 2} | repriceable now: true 5 / false 6 | **cumulative bid_grade lines: 12882 (repriceable true 1738 / false 11144)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL18LAJYUN-L | 33 | 31m | 1/37-37/2 | 36-38 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ATPCHALLENGERMATCH-26JUL18LAJYUN-Y | 63 | 36m | 4/64-64/450 | 63-64 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ATPCHALLENGERMATCH-26JUL18RODSAN-R | 72 | 19m | 12/79-80/472 | 79-80 | 7 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL18TOMJOH-J | 55 | 37m | 6/58-59/501 | 57-59 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→58 |
| ATPCHALLENGERMATCH-26JUL18TOMJOH-T | 39 | 37m | 6/43-43/129 | 42-43 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFMATCH-26JUL18BASTAI-BAS | 73 | 37m | 4/87-87/89 | 86-87 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL18BASTAI-TAI | 13 | 27m | 14/13-15/421 | 13-14 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL18SAIHOS-HOS | 36 | 37m | 1/37-37/25 | 36-37 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFWMATCH-26JUL18SAIHOS-SAI | 63 | 36m | 13/63-65/310 | 63-65 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL18THOAIA-AIA | 84 | 17m | 14/86-89/433 | 88-89 | 2 | **FLOW_ABOVE** | 84 | flow above but bound 84c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL18TONSPI-T | 31 | 37m | 0 | 31-59 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL18RODSAN | 21 | 80 | **101** | 97 | +4 |
| ITFWMATCH-26JUL18THOAIA | 13 | 89 | **102** | 97 | +5 |

## FLOW-STATE — 7 tracked game(s) ({'WAKING': 2, 'OPEN': 4, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL18RODSAN | ATP_CHALL | 0.8 | 1 | **OPEN** |
| ITFMATCH-26JUL18BASTAI | ITF_M | 0.6 | 1 | **OPEN** |
| ITFWMATCH-26JUL18SAIHOS | ITF_W | 0.467 | 1 | **OPEN** |
| ITFWMATCH-26JUL18THOAIA | ITF_W | 1.333 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL18TONSPI | WTA_CHALL | 0.0 | 28 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL18LAJYUN | ATP_CHALL | 0.133 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL18TOMJOH | ATP_CHALL | 0.267 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
