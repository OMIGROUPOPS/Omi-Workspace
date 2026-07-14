# LIVE VALIDATION — rolling status

- cycle 6 @ **2026-07-14 03:52:53 PM ET** | build `6c345a0b` | session boot 07-14 15:30 ET | log `live_v3_20260714.jsonl` | 1427 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL14COXHAM-HAM aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,shadow_range:SHAD
- refused:below_leg_floor UL14COXHAM-HAM aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,shadow_range:SHAD
- placed:path_aim UL14COXHAM-HAM aim=8 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,shadow_range:SHAD
- placed:path_aim UL14SCHSOU-SOU aim=75 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,shadow_range:SHAD

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 11 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:31:26 | **flatten_leash** | KXITFMATCH-26JUL14VULBAS-BAS | flatten DEFERRED: ev -2.11 above margin floor -3.0 |
| 15:31:26 | **flatten_leash** | KXITFWMATCH-26JUL14MARKOI-KOI | flatten CAPPED at 8/day (8 today) |
| 15:31:27 | **flatten_leash** | KXITFWMATCH-26JUL14BARREA-REA | flatten CAPPED at 8/day (8 today) |
| 15:35:23 | **bell_missing** | KXATPCHALLENGERMATCH-26JUL14LAJSVA | min_past_start 10.4 |
| 15:41:28 | **taker_capped** | KXITFMATCH-26JUL14VULBAS-BAS | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 15:41:28 | **taker_capped** | KXITFWMATCH-26JUL14MARKOI-KOI | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 15:41:28 | **flatten_leash** | KXITFWMATCH-26JUL14BARREA-REA | flatten CAPPED at 8/day (8 today) |
| 15:41:29 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA | flatten CAPPED at 8/day (8 today) |
| 15:51:29 | **flatten_leash** | KXITFMATCH-26JUL14VULBAS-BAS | flatten DEFERRED: ev -2.11 above margin floor -3.0 |
| 15:51:29 | **flatten_leash** | KXITFWMATCH-26JUL14BARREA-REA | flatten CAPPED at 8/day (8 today) |
| 15:51:30 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA | flatten CAPPED at 8/day (8 today) |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_flatten_leash.md**

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:31 | WTACHALLENGERMATCH-26JUL14PACVED-P | WTA_CHALL | ? | 16 | 13 | +3 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 6 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 3, 'NO_FLOW': 3} | repriceable now: true 2 / false 4 | **cumulative bid_grade lines: 9885 (repriceable true 1464 / false 8421)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL14DRATRO-D | 72 | 18m | 0 | 75-76 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL14DRATRO-T | 22 | 18m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL14IMAMCC-I | 34 | 20m | 2/38-38/175 | 38-38 | 4 | **FLOW_ABOVE** | 35 | REPRICEABLE→35 |
| ATPCHALLENGERMATCH-26JUL14IMAMCC-M | 59 | 20m | 1/62-62/40 | 61-62 | 3 | **FLOW_ABOVE** | 60 | REPRICEABLE→60 |
| ATPCHALLENGERMATCH-26JUL14ROZRIC-R | 27 | 21m | 3/59-59/362 | 58-59 | 32 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL14MUSBRA-MUS | 9 | 19m | 0 | 15-16 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 5 tracked game(s) ({'WAKING': 4, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| WTACHALLENGERMATCH-26JUL14PACVED | WTA_CHALL | 1.033 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL14DRATRO | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14IMAMCC | ATP_CHALL | 0.233 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14ROZRIC | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL14MUSBRA | ITF_W | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 5
- reality_divergence: KXATPCHALLENGERMATCH-26JUL14ROZRIC-RIC {"kind": "resting_bid", "ref": 27.0, "market_mid": 58.5, "divergence": -31.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL14ROZRIC-ROZ {"kind": "position_basis", "ref": 70.0, "market_mid": 42.5, "divergence": 27.5}
- reality_divergence: KXATPMATCH-26JUL14NEUPRA-NEU {"kind": "position_basis", "ref": 64.0, "market_mid": 13.0, "divergence": 51.0}
- reality_divergence: KXITFMATCH-26JUL14BYNSTE-STE {"kind": "position_basis", "ref": 48.0, "market_mid": 7.0, "divergence": 41.0}
- reality_divergence: KXITFWMATCH-26JUL14CLAKHA-CLA {"kind": "position_basis", "ref": 45.0, "market_mid": 19.5, "divergence": 25.5}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
