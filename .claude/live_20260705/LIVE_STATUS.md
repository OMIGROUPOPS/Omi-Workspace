# LIVE VALIDATION — rolling status

- cycle 258 @ **2026-07-17 10:15:21 PM ET** | build `8f497d1c` | session boot 07-17 21:44 ET | log `live_v3_20260717.jsonl` | 4732 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 122 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL17LIMABD-LIM aim=82 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- placed:path_aim UL18GAUTSE-TSE aim=34 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,orientation_:CONS,fv_gap:NO-R,pm_ref:THIN,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- refused:below_leg_floor UL18WALDJE-WAL aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- refused:below_leg_floor 6JUL18JACDA-DA aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 21:48:16 | **self_fill_bell** | KXITFMATCH-26JUL18PALWIS-WIS | own buys rose 12c (58->70) in 1800s -> match-live presumption, entry buys FROZEN |
| 21:51:48 | **self_fill_bell** | KXITFMATCH-26JUL18PALWIS-WIS | own buys rose 13c (58->71) in 1800s -> match-live presumption, entry buys FROZEN |

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:50 | WTAMATCH-26JUL18HONTHA-THA | WTA_MAIN | ? | 20 | 18 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 9 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 5, 'FLOW_ABOVE': 4} | repriceable now: true 3 / false 6 | **cumulative bid_grade lines: 12624 (repriceable true 1661 / false 10963)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL18AGIOVC-AGI | 22 | 30m | 6/23-24/682 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFMATCH-26JUL18AGIOVC-OVC | 75 | 7m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL18PALWIS-WIS | 71 | 23m | 0 | 71-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL18TORKHO-TOR | 46 | 30m | 0 | 46-50 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL18BASKRA-K | 66 | 27m | 1/67-67/43 | 66-67 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| WTAMATCH-26JUL18BANGAO-BAN | 37 | 12m | 1/39-39/7 | 37-39 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| WTAMATCH-26JUL18BANGAO-GAO | 57 | 30m | 0 | 61-63 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL18HONTHA-HON | 77 | 25m | 2/83-83/708 | 83-83 | 6 | **FLOW_ABOVE** | 77 | flow above but bound 77c < flow -- chasing breaks goal |
| WTAMATCH-26JUL18MICFRU-FRU | 74 | 18m | 0 | 74-75 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTAMATCH-26JUL18HONTHA | 20 | 83 | **103** | 97 | +6 |

## FLOW-STATE — 7 tracked game(s) ({'OPEN': 1, 'WAKING': 6}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL18AGIOVC | ITF_M | 0.2 | 1 | **OPEN** |
| ITFMATCH-26JUL18PALWIS | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL18TORKHO | ITF_M | 0.0 | 4 | **WAKING** |
| WTACHALLENGERMATCH-26JUL18BASKRA | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL18BANGAO | WTA_MAIN | 0.067 | 2 | **WAKING** |
| WTAMATCH-26JUL18HONTHA | WTA_MAIN | 0.267 | — | **WAKING** |
| WTAMATCH-26JUL18MICFRU | WTA_MAIN | 0.033 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
