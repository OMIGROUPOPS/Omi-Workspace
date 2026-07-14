# LIVE VALIDATION — rolling status

- cycle 10 @ **2026-07-14 02:15:11 PM ET** | build `f8a82f4b` | session boot 07-14 14:06 ET | log `live_v3_20260714.jsonl` | 2009 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 3 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 14:08:16 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL14ZHOKOZ-ZHO | flatten DEFERRED: ev -1.12 above margin floor -3.0 |
| 14:08:37 | **bell_missing** | KXATPCHALLENGERMATCH-26JUL14CASSCH | min_past_start 13.6 |
| 14:10:08 | **bell_missing** | KXITFWMATCH-26JUL14CLAKHA | min_past_start 10.1 |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_bell_missing.md**

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:10 | ITFWMATCH-26JUL14OVCVAG-VAG | ITF_W | ? | 48 | 44 | +4 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 29 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 24, 'FLOW_ABOVE': 5} | repriceable now: true 0 / false 29 | **cumulative bid_grade lines: 9828 (repriceable true 1457 / false 8371)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL14IMAMCC-M | 62 | 7m | 0 | 62-63 | — | **NO_FLOW** | 60 |  |
| ATPCHALLENGERMATCH-26JUL14JOHBER-B | 48 | 7m | 3/50-50/78 | 49-50 | 2 | **FLOW_ABOVE** | 47 | flow above but bound 47c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14JOHBER-J | 50 | 7m | 1/52-52/5 | 50-52 | 2 | **FLOW_ABOVE** | 49 | flow above but bound 49c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14LAJSVA-L | 51 | 7m | 2/53-54/8 | 53-54 | 2 | **FLOW_ABOVE** | 51 | flow above but bound 51c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL14LANYIB-L | 13 | 7m | 0 | 14-16 | — | **NO_FLOW** | 11 |  |
| ATPCHALLENGERMATCH-26JUL14LANYIB-Y | 85 | 7m | 0 | 86-87 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL14MILCHA-C | 47 | 7m | 0 | 47-48 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL14MILCHA-M | 51 | 7m | 0 | 51-53 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL14NEDDAL-D | 51 | 7m | 0 | 52-53 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL14NEDDAL-N | 46 | 7m | 0 | 47-49 | — | **NO_FLOW** | 46 |  |
| ATPCHALLENGERMATCH-26JUL14ROZRIC-R | 56 | 7m | 0 | 57-58 | — | **NO_FLOW** | 55 |  |
| ATPCHALLENGERMATCH-26JUL14ROZRIC-R | 42 | 7m | 0 | 42-44 | — | **NO_FLOW** | 41 |  |
| ATPCHALLENGERMATCH-26JUL14SUNGEA-G | 75 | 7m | 0 | 78-79 | — | **NO_FLOW** | 76 |  |
| ITFMATCH-26JUL14COXHAM-COX | 66 | 7m | 0 | 66-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14COXHAM-HAM | 7 | 7m | 0 | 11-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14PINLIM-LIM | 70 | 7m | 0 | 73-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14UTACAZ-CAZ | 58 | 7m | 1/68-68/14 | 63-68 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL14VULBAS-BAS | 76 | 7m | 0 | 76-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14VULBAS-VUL | 21 | 7m | 0 | 21-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14BARREA-BAR | 5 | 7m | 0 | 8-9 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14CLAKHA-KHA | 52 | 7m | 0 | 53-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14GAINGU-GAI | 42 | 5m | 0 | 43-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14GAINGU-NGU | 49 | 7m | 0 | 49-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14JEOMCN-JEO | 46 | 7m | 0 | 46-51 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14LAHIVA-IVA | 26 | 7m | 27/46-58/740 | 57-53 | 20 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL14MUSBRA-BRA | 83 | 7m | 0 | 83-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14MUSBRA-MUS | 15 | 7m | 0 | 15-16 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14SCHSOU-SCH | 14 | 7m | 0 | 14-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14SCHSOU-SOU | 86 | 7m | 0 | 86-87 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 20 tracked game(s) ({'WAKING': 18, 'QUIET': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL14COXHAM | ITF_M | 0.0 | 18 | **QUIET** |
| ITFWMATCH-26JUL14GAINGU | ITF_W | 0.0 | 6 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL14IMAMCC | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14JOHBER | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14LAJSVA | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14LANYIB | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14MILCHA | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14NEDDAL | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14ROZRIC | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL14SUNGEA | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL14PINLIM | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL14UTACAZ | ITF_M | 0.067 | 5 | **WAKING** |
| ITFMATCH-26JUL14VULBAS | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL14BARREA | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL14CLAKHA | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL14JEOMCN | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL14LAHIVA | ITF_W | 0.933 | — | **WAKING** |
| ITFWMATCH-26JUL14MUSBRA | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL14OVCVAG | ITF_W | 0.333 | 5 | **WAKING** |
| ITFWMATCH-26JUL14SCHSOU | ITF_W | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 2
- reality_divergence: KXITFWMATCH-26JUL14ALLOXF-ALL {"kind": "position_basis", "ref": 60.0, "market_mid": 2.5, "divergence": 57.5, "emitted_et": "2026-07-14 02:15:08 PM ET"}
- reality_divergence: KXITFWMATCH-26JUL14ELJKON-ELJ {"kind": "position_basis", "ref": 63.0, "market_mid": 13.5, "divergence": 49.5, "emitted_et": "2026-07-14 02:15:08 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
