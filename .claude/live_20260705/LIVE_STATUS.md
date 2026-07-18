# LIVE VALIDATION — rolling status

- cycle 261 @ **2026-07-17 10:46:27 PM ET** | build `7d461ee3` | session boot 07-17 21:44 ET | log `live_v3_20260717.jsonl` | 8144 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 154 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor 6JUL18JACDA-DA aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- placed:path_aim UL18SCHPER-SCH aim=17 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,pm_ref:THIN,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- refused:below_leg_floor UL18WALDJE-WAL aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS
- refused:below_leg_floor 6JUL18JACDA-DA aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,orientation_:CONS,fv_gap:NO-R,pm_ref:NO-M,cohort:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 3 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 21:48:16 | **self_fill_bell** | KXITFMATCH-26JUL18PALWIS-WIS | own buys rose 12c (58->70) in 1800s -> match-live presumption, entry buys FROZEN |
| 21:51:48 | **self_fill_bell** | KXITFMATCH-26JUL18PALWIS-WIS | own buys rose 13c (58->71) in 1800s -> match-live presumption, entry buys FROZEN |
| 22:40:06 | **self_fill_bell** | KXITFMATCH-26JUL18PALWIS-PAL | own buys rose 13c (16->29) in 1800s -> match-live presumption, entry buys FROZEN |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_self_fill_bell.md**

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:50 | WTAMATCH-26JUL18HONTHA-THA | WTA_MAIN | ? | 20 | 18 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 11 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 8, 'FLOW_AT_LEVEL': 1, 'FLOW_ABOVE': 2} | repriceable now: true 1 / false 10 | **cumulative bid_grade lines: 12631 (repriceable true 1662 / false 10969)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL18AGIOVC-AGI | 22 | 61m | 7/22-24/684 | 22-23 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL18AGIOVC-OVC | 75 | 38m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL18PALWIS-PAL | 29 | 6m | 0 | 29-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL18PALWIS-WIS | 71 | 55m | 0 | 71-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL18TORKHO-TOR | 46 | 61m | 0 | 46-50 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL18BASKRA-K | 67 | 7m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL18BANGAO-BAN | 38 | 22m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL18BANGAO-GAO | 62 | 22m | 1/63-63/597 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| WTAMATCH-26JUL18HONTHA-HON | 77 | 56m | 5/83-84/793 | 83-83 | 6 | **FLOW_ABOVE** | 77 | flow above but bound 77c < flow -- chasing breaks goal |
| WTAMATCH-26JUL18MICFRU-FRU | 74 | 50m | 0 | 74-75 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL18OKALEE-OKA | 17 | 10m | 0 | 18-20 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTAMATCH-26JUL18HONTHA | 20 | 83 | **103** | 97 | +6 |

## FLOW-STATE — 8 tracked game(s) ({'WAKING': 7, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| WTACHALLENGERMATCH-26JUL18BASKRA | WTA_CHALL | 0.367 | 1 | **OPEN** |
| ITFMATCH-26JUL18AGIOVC | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL18PALWIS | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL18TORKHO | ITF_M | 0.0 | 4 | **WAKING** |
| WTAMATCH-26JUL18BANGAO | WTA_MAIN | 0.167 | 1 | **WAKING** |
| WTAMATCH-26JUL18HONTHA | WTA_MAIN | 0.233 | — | **WAKING** |
| WTAMATCH-26JUL18MICFRU | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL18OKALEE | WTA_MAIN | 0.033 | 2 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXWTAMATCH-26JUL18HONTHA-THA {"fill": 20, "age_min": 56, "mode": "SET_BELOW_FLOW(prints 6c above)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
