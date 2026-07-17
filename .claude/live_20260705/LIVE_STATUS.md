# LIVE VALIDATION — rolling status

- cycle 231 @ **2026-07-17 05:34:02 PM ET** | build `af420c48` | session boot 07-17 15:16 ET | log `live_v3_20260717.jsonl` | 7598 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL18TIKSAT-TIK aim=47 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL18TUPSHO-SHO aim=38 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL18JANYOD-JAN aim=45 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL18JANYOD-YOD aim=30 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 7 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:18:52 | **self_fill_bell** | KXITFMATCH-26JUL17OCODEL-OCO | own buys rose 6c (10->16) in 1800s -> match-live presumption, entry buys FROZEN |
| 15:25:55 | **self_fill_bell** | KXATPCHALLENGERMATCH-26JUL17LAJNOG-NOG | own buys rose 4c (24->28) in 1800s -> match-live presumption, entry buys FROZEN |
| 15:31:17 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17HOLBOU-BOU | flatten DEFERRED: ev -1.29 above margin floor -3.0 |
| 16:54:35 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17VUKGAL-GAL | flatten DEFERRED: ev -0.77 above margin floor -3.0 |
| 17:04:40 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17VUKGAL-GAL | flatten DEFERRED: ev -0.77 above margin floor -3.0 |
| 17:16:05 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17VUKGAL-GAL | flatten DEFERRED: ev -0.77 above margin floor -3.0 |
| 17:26:15 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17VUKGAL-GAL | flatten DEFERRED: ev -0.77 above margin floor -3.0 |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_flatten_leash.md**

## FILLS — 7 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:16 | ITFMATCH-26JUL17NEFGAI-GAI | ITF_M | ? | 46 | 39 | +7 (window_cell) | — | pre | single |  | MIXED |
| 15:31 | ATPCHALLENGERMATCH-26JUL17HOLBOU-B | ATP_CHALL | ? | 33 | 31 | +2 (window_cell) | — | pre | single |  | MIXED |
| 16:07 | ATPCHALLENGERMATCH-26JUL17WONJOH-W | ATP_CHALL | ? | 64 | 61 | +3 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 16:32 | ATPCHALLENGERMATCH-26JUL17SMIYUN-Y | ATP_CHALL | ? | 63 | 61 | +2 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 16:47 | ITFMATCH-26JUL17OCODEL-OCO | ITF_M | ? | 17 | 12 | +5 (place_cell) | — | pre | pair | 99 | PENDING |
| 16:47 | ITFMATCH-26JUL17OCODEL-DEL | ITF_M | ? | 82 | 79 | +3 (fill_est) | — | pre | pair | 99 | PENDING |
| 16:54 | ATPCHALLENGERMATCH-26JUL17VUKGAL-G | ATP_CHALL | ? | 53 | 50 | +3 (window_cell) | — | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 7 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 7} | repriceable now: true 1 / false 6 | **cumulative bid_grade lines: 12593 (repriceable true 1655 / false 10938)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17FORTOM-F | 31 | 94m | 3/35-35/129 | 34-35 | 4 | **FLOW_ABOVE** | 32 | REPRICEABLE→32 |
| ATPCHALLENGERMATCH-26JUL17FORTOM-T | 66 | 32m | 6/67-67/337 | 66-67 | 1 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-L | 71 | 135m | 27/72-72/7526 | 71-72 | 1 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-N | 28 | 128m | 5/29-29/34 | 28-29 | 1 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17SMIYUN-S | 32 | 60m | 8/37-37/150 | 36-37 | 5 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-V | 44 | 39m | 26/48-49/5411 | 48-49 | 4 | **FLOW_ABOVE** | 44 | flow above but bound 44c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17WONJOH-J | 33 | 86m | 15/36-37/4221 | 36-37 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL17NEFGAI | 46 | 2 | **48** | 97 | -49 |
| ATPCHALLENGERMATCH-26JUL17SMIYUN | 63 | 37 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL17WONJOH | 64 | 37 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL17VUKGAL | 53 | 49 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | 33 | 97 | **130** | 97 | +33 |

## FLOW-STATE — 8 tracked game(s) ({'WAKING': 2, 'QUIET': 1, 'OPEN': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17LAJNOG | ATP_CHALL | 0.333 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17SMIYUN | ATP_CHALL | 0.767 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17VUKGAL | ATP_CHALL | 0.933 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17WONJOH | ATP_CHALL | 0.733 | 1 | **OPEN** |
| ITFMATCH-26JUL17OCODEL | ITF_M | 0.733 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL17FORTOM | ATP_CHALL | 0.267 | 1 | **WAKING** |
| ITFMATCH-26JUL17NEFGAI | ITF_M | 0.433 | — | **WAKING** |

## PATTERNS (sub-B) — 12
- half_arm_aging: KXITFMATCH-26JUL17NEFGAI-GAI {"fill": 46, "age_min": 137, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17DELFUE-DEL {"kind": "position_basis", "ref": 86.0, "market_mid": 29.0, "divergence": 57.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL17HOLBOU-BOU {"fill": 33, "age_min": 123, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17RODCRA-ROD {"kind": "position_basis", "ref": 71.0, "market_mid": 26.5, "divergence": 44.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17SANALM-ALM {"kind": "position_basis", "ref": 68.0, "market_mid": 34.5, "divergence": 33.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL17WONJOH-WON {"fill": 64, "age_min": 87, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17HOLBOU-BOU {"kind": "position_basis", "ref": 33.0, "market_mid": 1.5, "divergence": 31.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17RODCRA-ROD {"kind": "position_basis", "ref": 71.0, "market_mid": 36.0, "divergence": 35.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL17SMIYUN-YUN {"fill": 63, "age_min": 61, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL17OCODEL {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17SANALM-ALM {"kind": "position_basis", "ref": 68.0, "market_mid": 26.0, "divergence": 42.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL17VUKGAL-GAL {"fill": 53, "age_min": 39, "mode": "SET_BELOW_FLOW(prints 4c above)", "emitted_et": "2026-07-17 05:34:01 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
