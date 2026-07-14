# LIVE VALIDATION — rolling status

- cycle 13 @ **2026-07-14 02:46:33 PM ET** | build `92472906` | session boot 07-14 14:06 ET | log `live_v3_20260714.jsonl` | 7094 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 30 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 14:08:16 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL14ZHOKOZ-ZHO | flatten DEFERRED: ev -1.12 above margin floor -3.0 |
| 14:08:37 | **bell_missing** | KXATPCHALLENGERMATCH-26JUL14CASSCH | min_past_start 13.6 |
| 14:10:08 | **bell_missing** | KXITFWMATCH-26JUL14CLAKHA | min_past_start 10.1 |
| 14:18:15 | **flatten_leash** | KXWTACHALLENGERMATCH-26JUL14MAZBRO-BRO | flatten DEFERRED: ev -2.44 above margin floor -3.0 |
| 14:18:15 | **flatten_leash** | KXITFWMATCH-26JUL14MARKOI-KOI | flatten CAPPED at 8/day (8 today) |
| 14:18:16 | **taker_capped** | KXITFMATCH-26JUL14UTACAZ-UTA | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 14:18:16 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL14SUNGEA-SUN | flatten DEFERRED: ev -2.3 above margin floor -3.0 |
| 14:18:18 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA | flatten CAPPED at 8/day (8 today) |
| 14:18:18 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL14CASSCH-CAS | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 14:18:18 | **flatten_leash** | KXWTAMATCH-26JUL13BLISAS-BLI | flatten DEFERRED: ev -0.44 above margin floor -3.0 |
| 14:27:20 | **flatten_leash** | KXITFWMATCH-26JUL14SCHSOU-SCH | flatten DEFERRED: ev -2.0 above margin floor -3.0 |
| 14:28:16 | **flatten_leash** | KXWTACHALLENGERMATCH-26JUL14MAZBRO-BRO | flatten DEFERRED: ev -2.44 above margin floor -3.0 |
| 14:28:16 | **flatten_leash** | KXITFWMATCH-26JUL14CLAKHA-CLA | flatten CAPPED at 8/day (8 today) |
| 14:28:17 | **flatten_leash** | KXITFMATCH-26JUL14UTACAZ-UTA | flatten CAPPED at 8/day (8 today) |
| 14:28:17 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL14SUNGEA-SUN | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 14:28:17 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL14DELXIL-XIL | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 14:28:18 | **taker_capped** | KXITFMATCH-26JUL14PINLIM-PIN | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 14:28:18 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA | flatten CAPPED at 8/day (8 today) |
| 14:28:18 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL14CASSCH-CAS | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 14:38:36 | **flatten_leash** | KXWTACHALLENGERMATCH-26JUL14MAZBRO-BRO | flatten DEFERRED: ev -2.44 above margin floor -3.0 |
| 14:38:36 | **taker_capped** | KXITFWMATCH-26JUL14MARKOI-KOI | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 14:38:38 | **flatten_leash** | KXITFWMATCH-26JUL14BARREA-REA | flatten CAPPED at 8/day (8 today) |
| 14:38:39 | **flatten_leash** | KXITFWMATCH-26JUL14CLAKHA-CLA | flatten DEFERRED: ev -1.8 above margin floor -3.0 |
| 14:38:39 | **flatten_leash** | KXITFMATCH-26JUL14UTACAZ-UTA | flatten CAPPED at 8/day (8 today) |
| 14:38:39 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL14SUNGEA-SUN | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 14:38:39 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL14DELXIL-XIL | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 14:38:39 | **taker_capped** | KXITFMATCH-26JUL14PINLIM-PIN | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 14:38:40 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL14LAJSVA-SVA | flatten CAPPED at 8/day (8 today) |
| 14:38:40 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL14CASSCH-CAS | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 14:46:18 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL14ROZRIC-ROZ | flatten CAPPED at 8/day (8 today) |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_flatten_leash.md, FORENSIC_taker_capped.md**

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:10 | ITFWMATCH-26JUL14OVCVAG-VAG | ITF_W | ? | 48 | 44 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:27 | ITFWMATCH-26JUL14SCHSOU-SCH | ITF_W | ? | 14 | 10 | +4 (fill_est) | — | pre | single |  | PENDING |
| 14:45 | ATPCHALLENGERMATCH-26JUL14ROZRIC-R | ATP_CHALL | ? | 42 | 41 | +1 (window_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 22 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 1, 'FLOW_ABOVE': 15, 'NO_FLOW': 6} | repriceable now: true 5 / false 17 | **cumulative bid_grade lines: 9843 (repriceable true 1462 / false 8381)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL14IMAMCC-M | 62 | 39m | 1/63-63/46 | 62-63 | 1 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14JOHBER-B | 47 | 12m | 1/50-50/11 | 49-50 | 3 | **FLOW_ABOVE** | 47 | flow above but bound 47c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14LAJSVA-L | 51 | 39m | 6/53-54/90 | 53-54 | 2 | **FLOW_ABOVE** | 51 | flow above but bound 51c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14LANYIB-L | 13 | 39m | 6/16-17/144 | 14-16 | 3 | **FLOW_ABOVE** | 11 | flow above but bound 11c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14LANYIB-Y | 81 | 6m | 1/86-86/1 | 85-86 | 5 | **FLOW_ABOVE** | 84 | flow above but bound 84c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14MILCHA-C | 47 | 39m | 0 | 47-48 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL14MILCHA-M | 51 | 39m | 0 | 51-53 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL14NEDDAL-D | 51 | 39m | 5/53-54/811 | 53-54 | 2 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14NEDDAL-N | 46 | 38m | 0 | 47-48 | — | **NO_FLOW** | 46 |  |
| ATPCHALLENGERMATCH-26JUL14ROZRIC-R | 55 | 1m | 0 | 57-58 | — | **NO_FLOW** | 55 |  |
| ATPCHALLENGERMATCH-26JUL14SUNGEA-G | 75 | 39m | 6/78-80/43 | 78-80 | 3 | **FLOW_ABOVE** | 76 | REPRICEABLE→76 |
| ITFMATCH-26JUL14COXHAM-COX | 66 | 39m | 0 | 66-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14COXHAM-HAM | 7 | 38m | 1/29-29/3 | 11-29 | 22 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL14VULBAS-BAS | 76 | 39m | 1/77-77/1 | 76-77 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→77 |
| ITFMATCH-26JUL14VULBAS-VUL | 21 | 39m | 1/23-23/8 | 21-23 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFWMATCH-26JUL14BARREA-BAR | 5 | 39m | 6/9-9/159 | 8-9 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFWMATCH-26JUL14GAINGU-GAI | 42 | 36m | 0 | 43-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14GAINGU-NGU | 49 | 38m | 1/56-56/17 | 52-57 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL14LAHIVA-IVA | 26 | 39m | 234/46-88/32499 | 78-76 | 20 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL14MUSBRA-BRA | 83 | 39m | 2/86-86/13 | 84-86 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→86 |
| ITFWMATCH-26JUL14MUSBRA-MUS | 15 | 39m | 3/15-16/44 | 15-16 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL14SCHSOU-SOU | 83 | 19m | 1/89-89/10 | 87-90 | 6 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL14ROZRIC | 42 | 58 | **100** | 97 | +3 |
| ITFWMATCH-26JUL14SCHSOU | 14 | 90 | **104** | 97 | +7 |

## FLOW-STATE — 16 tracked game(s) ({'WAKING': 13, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL14LANYIB | ATP_CHALL | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL14BARREA | ITF_W | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL14SCHSOU | ITF_W | 0.233 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL14IMAMCC | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14JOHBER | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14LAJSVA | ATP_CHALL | 0.133 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14MILCHA | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14NEDDAL | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14ROZRIC | ATP_CHALL | 0.133 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14SUNGEA | ATP_CHALL | 0.2 | 2 | **WAKING** |
| ITFMATCH-26JUL14COXHAM | ITF_M | 0.033 | 18 | **WAKING** |
| ITFMATCH-26JUL14VULBAS | ITF_M | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL14GAINGU | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL14LAHIVA | ITF_W | 6.767 | — | **WAKING** |
| ITFWMATCH-26JUL14MUSBRA | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL14OVCVAG | ITF_W | 2.4 | — | **WAKING** |

## PATTERNS (sub-B) — 9
- reality_divergence: KXITFWMATCH-26JUL14ALLOXF-ALL {"kind": "position_basis", "ref": 60.0, "market_mid": 2.5, "divergence": 57.5}
- reality_divergence: KXITFWMATCH-26JUL14ELJKON-ELJ {"kind": "position_basis", "ref": 63.0, "market_mid": 13.5, "divergence": 49.5}
- half_arm_aging: KXITFWMATCH-26JUL14OVCVAG-VAG {"fill": 48, "age_min": 36, "mode": "PAIRING(sib never rested)"}
- reality_divergence: KXATPMATCH-26JUL14GOMMCD-MCD {"kind": "position_basis", "ref": 44.0, "market_mid": 12.5, "divergence": 31.5}
- reality_divergence: KXATPMATCH-26JUL14NEUPRA-NEU {"kind": "position_basis", "ref": 64.0, "market_mid": 29.5, "divergence": 34.5}
- reality_divergence: KXITFWMATCH-26JUL14CLAKHA-KHA {"kind": "resting_bid", "ref": 5.0, "market_mid": 55.5, "divergence": -50.5}
- reality_divergence: KXITFWMATCH-26JUL14LAHIVA-IVA {"kind": "resting_bid", "ref": 26.0, "market_mid": 59.5, "divergence": -33.5}
- reality_divergence: KXITFWMATCH-26JUL14LAHIVA-LAH {"kind": "position_basis", "ref": 67.0, "market_mid": 40.5, "divergence": 26.5}
- reality_divergence: KXITFMATCH-26JUL14BYNSTE-STE {"kind": "position_basis", "ref": 48.0, "market_mid": 21.5, "divergence": 26.5, "emitted_et": "2026-07-14 02:46:30 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
