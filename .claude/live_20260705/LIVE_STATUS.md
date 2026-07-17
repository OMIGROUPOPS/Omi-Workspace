# LIVE VALIDATION — rolling status

- cycle 219 @ **2026-07-17 03:29:34 PM ET** | build `436babc6` | session boot 07-17 15:16 ET | log `live_v3_20260717.jsonl` | 1123 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL17THOYOS-THO aim=12 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17SAIBRA-BRA aim=47 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17SAIBRA-SAI aim=28 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17OCODEL-OCO aim=10 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:18:52 | **self_fill_bell** | KXITFMATCH-26JUL17OCODEL-OCO | own buys rose 6c (10->16) in 1800s -> match-live presumption, entry buys FROZEN |
| 15:25:55 | **self_fill_bell** | KXATPCHALLENGERMATCH-26JUL17LAJNOG-NOG | own buys rose 4c (24->28) in 1800s -> match-live presumption, entry buys FROZEN |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_self_fill_bell.md**

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:16 | ITFMATCH-26JUL17NEFGAI-GAI | ITF_M | ? | 46 | 39 | +7 (window_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 13 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 4, 'NO_FLOW': 9} | repriceable now: true 2 / false 11 | **cumulative bid_grade lines: 12572 (repriceable true 1653 / false 10919)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17FORTOM-T | 64 | 12m | 0 | 64-66 | — | **NO_FLOW** | 63 |  |
| ATPCHALLENGERMATCH-26JUL17HOLBOU-B | 33 | 6m | 9/35-35/200 | 33-35 | 2 | **FLOW_ABOVE** | 31 | flow above but bound 31c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17HOLBOU-H | 66 | 2m | 0 | 66-67 | — | **NO_FLOW** | 64 |  |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-L | 71 | 10m | 0 | 71-72 | — | **NO_FLOW** | 69 |  |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-N | 28 | 4m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL17SMIYUN-S | 37 | 10m | 0 | 37-38 | — | **NO_FLOW** | 35 |  |
| ATPCHALLENGERMATCH-26JUL17SMIYUN-Y | 62 | 2m | 0 | 62-63 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-G | 51 | 13m | 1/52-52/23 | 51-52 | 1 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-V | 45 | 12m | 2/48-49/156 | 48-49 | 3 | **FLOW_ABOVE** | 46 | REPRICEABLE→46 |
| ATPCHALLENGERMATCH-26JUL17WONJOH-J | 36 | 10m | 0 | 36-37 | — | **NO_FLOW** | 34 |  |
| ATPCHALLENGERMATCH-26JUL17WONJOH-W | 64 | 12m | 0 | 64-65 | — | **NO_FLOW** | 61 |  |
| ITFMATCH-26JUL17OCODEL-DEL | 82 | 13m | 1/84-84/70 | 82-83 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→84 |
| ITFMATCH-26JUL17OCODEL-OCO | 16 | 11m | 0 | 16-17 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL17NEFGAI | 46 | 58 | **104** | 97 | +7 |

## FLOW-STATE — 8 tracked game(s) ({'WAKING': 6, 'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17HOLBOU | ATP_CHALL | 0.733 | 1 | **OPEN** |
| ITFMATCH-26JUL17OCODEL | ITF_M | 0.367 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17FORTOM | ATP_CHALL | 0.067 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17LAJNOG | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17SMIYUN | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17VUKGAL | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17WONJOH | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL17NEFGAI | ITF_M | 0.1 | 2 | **WAKING** |

## PATTERNS (sub-B) — 1
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17DELFUE-DEL {"kind": "position_basis", "ref": 86.0, "market_mid": 29.0, "divergence": 57.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
