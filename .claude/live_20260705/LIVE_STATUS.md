# LIVE VALIDATION — rolling status

- cycle 217 @ **2026-07-17 03:08:44 PM ET** | build `4e32f6fb` | session boot 07-17 14:58 ET | log `live_v3_20260717.jsonl` | 1203 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 51 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL17SAIBRA-BRA aim=47 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17SAIBRA-SAI aim=32 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17LAJNOG-NOG aim=24 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17SMIYUN-YUN aim=59 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 3 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 14:59:47 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17DRAGEA-GEA | flatten DEFERRED: ev -0.76 above margin floor -3.0 |
| 15:00:48 | **self_fill_bell** | KXITFMATCH-26JUL17NEFGAI-NEF | own buys rose 15c (38->53) in 1800s -> match-live presumption, entry buys FROZEN |
| 15:04:47 | **self_fill_bell** | KXITFMATCH-26JUL17NEFGAI-NEF | own buys rose 16c (38->54) in 1800s -> match-live presumption, entry buys FROZEN |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_self_fill_bell.md**

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:07 | ITFMATCH-26JUL17NEFGAI-GAI | ITF_M | ? | 46 | 44 | +2 (place_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 12 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 10, 'FLOW_ABOVE': 2} | repriceable now: true 0 / false 12 | **cumulative bid_grade lines: 12557 (repriceable true 1651 / false 10906)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17HOLBOU-B | 33 | 10m | 1/34-34/1 | 33-34 | 1 | **FLOW_ABOVE** | 31 | flow above but bound 31c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17HOLBOU-H | 66 | 10m | 0 | 66-67 | — | **NO_FLOW** | 64 |  |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-L | 69 | 10m | 0 | 71-72 | — | **NO_FLOW** | 69 |  |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-N | 24 | 8m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL17SMIYUN-S | 35 | 10m | 0 | 37-38 | — | **NO_FLOW** | 36 |  |
| ATPCHALLENGERMATCH-26JUL17SMIYUN-Y | 59 | 7m | 0 | 62-63 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-G | 51 | 8m | 0 | 51-53 | — | **NO_FLOW** | 50 |  |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-V | 47 | 8m | 0 | 47-49 | — | **NO_FLOW** | 46 |  |
| ATPCHALLENGERMATCH-26JUL17WONJOH-J | 33 | 9m | 0 | 36-37 | — | **NO_FLOW** | 34 |  |
| ATPCHALLENGERMATCH-26JUL17WONJOH-W | 61 | 10m | 2/64-64/14 | 63-64 | 3 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFMATCH-26JUL17OCODEL-DEL | 82 | 7m | 0 | 82-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17OCODEL-OCO | 16 | 7m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL17NEFGAI | 46 | 58 | **104** | 97 | +7 |

## FLOW-STATE — 7 tracked game(s) ({'WAKING': 7}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17HOLBOU | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17LAJNOG | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17SMIYUN | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17VUKGAL | ATP_CHALL | 0.033 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17WONJOH | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ITFMATCH-26JUL17NEFGAI | ITF_M | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL17OCODEL | ITF_M | 0.067 | 2 | **WAKING** |

## PATTERNS (sub-B) — 1
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17DELFUE-DEL {"kind": "position_basis", "ref": 86.0, "market_mid": 47.5, "divergence": 38.5, "emitted_et": "2026-07-17 03:08:43 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
