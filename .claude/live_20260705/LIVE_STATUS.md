# LIVE VALIDATION — rolling status

- cycle 225 @ **2026-07-17 04:32:08 PM ET** | build `614d43fb` | session boot 07-17 15:16 ET | log `live_v3_20260717.jsonl` | 4460 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL17SAIBRA-SAI aim=28 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17OCODEL-OCO aim=10 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17AIAYAN-YAN aim=18 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17FORTOM-FOR aim=31 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 3 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:18:52 | **self_fill_bell** | KXITFMATCH-26JUL17OCODEL-OCO | own buys rose 6c (10->16) in 1800s -> match-live presumption, entry buys FROZEN |
| 15:25:55 | **self_fill_bell** | KXATPCHALLENGERMATCH-26JUL17LAJNOG-NOG | own buys rose 4c (24->28) in 1800s -> match-live presumption, entry buys FROZEN |
| 15:31:17 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17HOLBOU-BOU | flatten DEFERRED: ev -1.29 above margin floor -3.0 |

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:16 | ITFMATCH-26JUL17NEFGAI-GAI | ITF_M | ? | 46 | 39 | +7 (window_cell) | — | pre | single |  | MIXED |
| 15:31 | ATPCHALLENGERMATCH-26JUL17HOLBOU-B | ATP_CHALL | ? | 33 | 31 | +2 (window_cell) | — | pre | single |  | MIXED |
| 16:07 | ATPCHALLENGERMATCH-26JUL17WONJOH-W | ATP_CHALL | ? | 64 | 61 | +3 (window_cell) | — | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 11 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 9, 'FLOW_AT_LEVEL': 1, 'NO_FLOW': 1} | repriceable now: true 4 / false 7 | **cumulative bid_grade lines: 12585 (repriceable true 1655 / false 10930)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17FORTOM-F | 31 | 32m | 1/35-35/5 | 34-35 | 4 | **FLOW_ABOVE** | 32 | REPRICEABLE→32 |
| ATPCHALLENGERMATCH-26JUL17FORTOM-T | 65 | 31m | 5/66-66/81 | 65-66 | 1 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-L | 71 | 73m | 8/72-72/220 | 71-72 | 1 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-N | 28 | 66m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL17SMIYUN-S | 37 | 73m | 2/38-38/30 | 37-38 | 1 | **FLOW_ABOVE** | 35 | flow above but bound 35c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17SMIYUN-Y | 63 | 52m | 9/64-64/1415 | 63-64 | 1 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-G | 51 | 75m | 20/51-53/1245 | 51-53 | 0 | **FLOW_AT_LEVEL** | 50 |  |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-V | 45 | 75m | 22/48-49/1601 | 48-49 | 3 | **FLOW_ABOVE** | 46 | REPRICEABLE→46 |
| ATPCHALLENGERMATCH-26JUL17WONJOH-J | 33 | 25m | 1/37-37/5 | 36-37 | 4 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| ITFMATCH-26JUL17OCODEL-DEL | 82 | 75m | 5/83-84/94 | 82-83 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→83 |
| ITFMATCH-26JUL17OCODEL-OCO | 16 | 73m | 8/17-18/909 | 16-17 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→17 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL17NEFGAI | 46 | 18 | **64** | 97 | -33 |
| ATPCHALLENGERMATCH-26JUL17WONJOH | 64 | 37 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | 33 | 97 | **130** | 97 | +33 |

## FLOW-STATE — 8 tracked game(s) ({'WAKING': 5, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17SMIYUN | ATP_CHALL | 0.367 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17VUKGAL | ATP_CHALL | 1.067 | 1 | **OPEN** |
| ITFMATCH-26JUL17OCODEL | ITF_M | 0.333 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17FORTOM | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | ATP_CHALL | 10.8 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17LAJNOG | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17WONJOH | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ITFMATCH-26JUL17NEFGAI | ITF_M | 25.333 | — | **WAKING** |

## PATTERNS (sub-B) — 7
- half_arm_aging: KXITFMATCH-26JUL17NEFGAI-GAI {"fill": 46, "age_min": 75, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17DELFUE-DEL {"kind": "position_basis", "ref": 86.0, "market_mid": 29.0, "divergence": 57.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL17HOLBOU-BOU {"fill": 33, "age_min": 61, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17RODCRA-ROD {"kind": "position_basis", "ref": 71.0, "market_mid": 26.5, "divergence": 44.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17SANALM-ALM {"kind": "position_basis", "ref": 68.0, "market_mid": 34.5, "divergence": 33.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17HOLBOU-BOU {"kind": "position_basis", "ref": 33.0, "market_mid": 1.5, "divergence": 31.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17RODCRA-ROD {"kind": "position_basis", "ref": 71.0, "market_mid": 36.0, "divergence": 35.0, "emitted_et": "2026-07-17 04:32:08 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
