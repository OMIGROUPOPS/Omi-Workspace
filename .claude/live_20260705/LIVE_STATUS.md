# LIVE VALIDATION — rolling status

- cycle 11 @ **2026-07-14 02:25:40 PM ET** | build `830dc9d7` | session boot 07-14 14:06 ET | log `live_v3_20260714.jsonl` | 3794 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 10 violation(s)
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

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_flatten_leash.md, FORENSIC_taker_capped.md**

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:10 | ITFWMATCH-26JUL14OVCVAG-VAG | ITF_W | ? | 48 | 44 | +4 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 26 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 16, 'FLOW_ABOVE': 10} | repriceable now: true 2 / false 24 | **cumulative bid_grade lines: 9832 (repriceable true 1459 / false 8373)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL14IMAMCC-M | 62 | 18m | 1/63-63/46 | 62-63 | 1 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14JOHBER-B | 48 | 18m | 4/50-50/87 | 49-50 | 2 | **FLOW_ABOVE** | 47 | flow above but bound 47c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14LAJSVA-L | 51 | 18m | 4/53-54/43 | 53-54 | 2 | **FLOW_ABOVE** | 51 | flow above but bound 51c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14LANYIB-L | 13 | 18m | 1/17-17/55 | 15-16 | 4 | **FLOW_ABOVE** | 11 | flow above but bound 11c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14LANYIB-Y | 85 | 17m | 1/87-87/30 | 86-87 | 2 | **FLOW_ABOVE** | 84 | flow above but bound 84c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14MILCHA-C | 47 | 18m | 0 | 47-48 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL14MILCHA-M | 51 | 18m | 0 | 51-53 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL14NEDDAL-D | 51 | 18m | 0 | 52-53 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL14NEDDAL-N | 46 | 17m | 0 | 47-49 | — | **NO_FLOW** | 46 |  |
| ATPCHALLENGERMATCH-26JUL14ROZRIC-R | 56 | 18m | 1/58-58/97 | 57-58 | 2 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14ROZRIC-R | 42 | 18m | 0 | 42-44 | — | **NO_FLOW** | 41 |  |
| ATPCHALLENGERMATCH-26JUL14SUNGEA-G | 75 | 18m | 3/78-80/5 | 79-80 | 3 | **FLOW_ABOVE** | 76 | REPRICEABLE→76 |
| ITFMATCH-26JUL14COXHAM-COX | 66 | 18m | 0 | 66-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14COXHAM-HAM | 7 | 17m | 0 | 11-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14VULBAS-BAS | 76 | 18m | 0 | 76-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14VULBAS-VUL | 21 | 18m | 0 | 21-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14BARREA-BAR | 5 | 18m | 2/9-9/41 | 8-9 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFWMATCH-26JUL14CLAKHA-KHA | 5 | 8m | 1/58-58/3 | 54-57 | 53 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL14GAINGU-GAI | 42 | 15m | 0 | 43-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14GAINGU-NGU | 49 | 17m | 0 | 49-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14JEOMCN-JEO | 46 | 18m | 0 | 47-53 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14LAHIVA-IVA | 26 | 18m | 60/46-67/3666 | 62-63 | 20 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL14MUSBRA-BRA | 83 | 18m | 0 | 83-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14MUSBRA-MUS | 15 | 18m | 0 | 15-16 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14SCHSOU-SCH | 14 | 18m | 0 | 14-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14SCHSOU-SOU | 86 | 18m | 0 | 86-87 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 18 tracked game(s) ({'WAKING': 14, 'QUIET': 2, 'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL14LAHIVA | ITF_W | 2.0 | 1 | **OPEN** |
| ITFWMATCH-26JUL14OVCVAG | ITF_W | 0.933 | 1 | **OPEN** |
| ITFMATCH-26JUL14COXHAM | ITF_M | 0.0 | 18 | **QUIET** |
| ITFWMATCH-26JUL14GAINGU | ITF_W | 0.0 | 6 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL14IMAMCC | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14JOHBER | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14LAJSVA | ATP_CHALL | 0.133 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14LANYIB | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14MILCHA | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14NEDDAL | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14ROZRIC | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14SUNGEA | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL14VULBAS | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL14BARREA | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL14CLAKHA | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL14JEOMCN | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL14MUSBRA | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL14SCHSOU | ITF_W | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 7
- reality_divergence: KXITFWMATCH-26JUL14ALLOXF-ALL {"kind": "position_basis", "ref": 60.0, "market_mid": 2.5, "divergence": 57.5}
- reality_divergence: KXITFWMATCH-26JUL14ELJKON-ELJ {"kind": "position_basis", "ref": 63.0, "market_mid": 13.5, "divergence": 49.5}
- reality_divergence: KXATPMATCH-26JUL14GOMMCD-MCD {"kind": "position_basis", "ref": 44.0, "market_mid": 12.5, "divergence": 31.5, "emitted_et": "2026-07-14 02:25:35 PM ET"}
- reality_divergence: KXATPMATCH-26JUL14NEUPRA-NEU {"kind": "position_basis", "ref": 64.0, "market_mid": 29.5, "divergence": 34.5, "emitted_et": "2026-07-14 02:25:35 PM ET"}
- reality_divergence: KXITFWMATCH-26JUL14CLAKHA-KHA {"kind": "resting_bid", "ref": 5.0, "market_mid": 55.5, "divergence": -50.5, "emitted_et": "2026-07-14 02:25:35 PM ET"}
- reality_divergence: KXITFWMATCH-26JUL14LAHIVA-IVA {"kind": "resting_bid", "ref": 26.0, "market_mid": 59.5, "divergence": -33.5, "emitted_et": "2026-07-14 02:25:35 PM ET"}
- reality_divergence: KXITFWMATCH-26JUL14LAHIVA-LAH {"kind": "position_basis", "ref": 67.0, "market_mid": 40.5, "divergence": 26.5, "emitted_et": "2026-07-14 02:25:35 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
