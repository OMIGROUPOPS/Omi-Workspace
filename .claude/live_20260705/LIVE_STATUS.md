# LIVE VALIDATION — rolling status

- cycle 30 @ **2026-07-13 01:53:46 AM ET** | build `6c117f9e` | session boot 07-13 01:29 ET | log `live_v3_20260713.jsonl` | 6753 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 1 item(s)
- **reality_divergence**: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 8.0, "market_mid": 47.5, "divergence": -39.5, "emitted_et": "2026-07-13 01:53:46 AM ET"}
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 12 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 01:30:53 | **self_fill_bell** | KXITFWMATCH-26JUL13VELKOR-KOR | own buys rose 14c (50->64) in 1800s -> match-live presumption, entry buys FROZEN |
| 01:31:06 | **self_fill_bell** | KXITFWMATCH-26JUL13MICSEB-SEB | own buys rose 16c (51->67) in 1800s -> match-live presumption, entry buys FROZEN |
| 01:32:49 | **self_fill_bell** | KXITFMATCH-26JUL13HASZAG-HAS | own buys rose 7c (68->75) in 1800s -> match-live presumption, entry buys FROZEN |
| 01:32:50 | **self_fill_bell** | KXITFMATCH-26JUL13SARANG-SAR | own buys rose 8c (16->24) in 1800s -> match-live presumption, entry buys FROZEN |
| 01:32:52 | **self_fill_bell** | KXITFMATCH-26JUL13DUHGAT-GAT | own buys rose 4c (23->27) in 1800s -> match-live presumption, entry buys FROZEN |
| 01:32:58 | **self_fill_bell** | KXITFWMATCH-26JUL13CAKVOZ-CAK | own buys rose 13c (50->63) in 1800s -> match-live presumption, entry buys FROZEN |
| 01:32:59 | **self_fill_bell** | KXITFWMATCH-26JUL13MALMOO-MAL | own buys rose 14c (65->79) in 1800s -> match-live presumption, entry buys FROZEN |
| 01:32:59 | **self_fill_bell** | KXITFWMATCH-26JUL13SVIART-SVI | own buys rose 6c (16->22) in 1800s -> match-live presumption, entry buys FROZEN |
| 01:36:06 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 1116.1 |
| 01:37:02 | **self_fill_bell** | KXITFWMATCH-26JUL13IBRVER-VER | own buys rose 9c (46->55) in 1800s -> match-live presumption, entry buys FROZEN |
| 01:37:05 | **self_fill_bell** | KXITFMATCH-26JUL13BERWAL-BER | own buys rose 14c (54->68) in 1800s -> match-live presumption, entry buys FROZEN |
| 01:51:04 | **self_fill_bell** | KXITFMATCH-26JUL13SARBOV-BOV | own buys rose 4c (24->28) in 1800s -> match-live presumption, entry buys FROZEN |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_self_fill_bell.md**

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:35 | ATPCHALLENGERMATCH-26JUL13YEVCAM-Y | ATP_CHALL | underdog | 42 | 39 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 53 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 35, 'FLOW_ABOVE': 18} | repriceable now: true 15 / false 38 | **cumulative bid_grade lines: 8862 (repriceable true 1304 / false 7558)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13BINFUE-B | 36 | 23m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13BINFUE-F | 62 | 23m | 0 | 62-64 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13KRASAL-K | 85 | 2m | 1/86-86/2 | 85-86 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→86 |
| ATPCHALLENGERMATCH-26JUL13KRASAL-S | 14 | 23m | 0 | 14-15 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13PRICRI-C | 8 | 21m | 3/9-10/410 | 8-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 23m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12SONSCH-SON | 65 | 23m | 45/68-70/4229 | 69-70 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPMATCH-26JUL13PASKRU-PAS | 64 | 21m | 15/65-65/1161 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFMATCH-26JUL13BEAMTI-BEA | 90 | 21m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BEAMTI-MTI | 7 | 23m | 2/8-8/23 | 7-8 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL13BERWAL-BER | 68 | 17m | 0 | 69-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERWAL-WAL | 22 | 17m | 0 | 24-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BRIDUB-DUB | 24 | 3m | 0 | 24-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DUHGAT-DUH | 54 | 21m | 0 | 56-72 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DUHGAT-GAT | 27 | 21m | 0 | 28-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GELSEB-SEB | 74 | 17m | 0 | 74-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HASZAG-HAS | 75 | 21m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MAYAER-AER | 39 | 18m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MCHAND-AND | 9 | 3m | 0 | 9-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SARANG-SAR | 24 | 21m | 0 | 25-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SARBOV-BOV | 28 | 3m | 0 | 29-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13WITHUE-WIT | 83 | 17m | 0 | 83-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13CAKVOZ-VOZ | 25 | 21m | 0 | 25-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13FEHKRO-FEH | 9 | 17m | 1/13-13/21 | 9-13 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL13IBRVER-IBR | 21 | 18m | 0 | 31-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IBRVER-VER | 55 | 17m | 0 | 55-68 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LABMAN-LAB | 62 | 23m | 0 | 63-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LABMAN-MAN | 26 | 21m | 0 | 26-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MAL | 79 | 21m | 0 | 79-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MOO | 13 | 21m | 0 | 16-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MICSEB-SEB | 67 | 23m | 0 | 70-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-NDU | 10 | 17m | 0 | 10-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-SCH | 51 | 17m | 0 | 51-90 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SVIART-SVI | 22 | 21m | 1/27-27/3 | 22-27 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13VELKOR-KOR | 64 | 23m | 0 | 64-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13VELKOR-VEL | 25 | 23m | 1/35-35/2 | 25-35 | 10 | **FLOW_ABOVE** | 99 |  |
| WTACHALLENGERMATCH-26JUL13GRABER-B | 20 | 21m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PAPAND-A | 78 | 13m | 1/79-79/1 | 78-79 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→79 |
| WTACHALLENGERMATCH-26JUL13PAPAND-P | 22 | 21m | 0 | 22-23 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 83 | 21m | 2/85-85/3 | 84-85 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 15 | 21m | 0 | 15-16 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13AMAHER-AMA | 35 | 21m | 6/36-36/633 | 35-36 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 9m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13AVAFET-FET | 8 | 23m | 1/9-9/10 | 8-9 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 14m | 1/61-61/15 | 59-61 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| WTAMATCH-26JUL13CRIJEA-CRI | 64 | 23m | 2/65-65/29 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| WTAMATCH-26JUL13KAWWAL-WAL | 67 | 21m | 1/69-69/14 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| WTAMATCH-26JUL13KRETOM-KRE | 88 | 23m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13MONMAS-MAS | 81 | 21m | 0 | 81-84 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13QUERUS-RUS | 69 | 9m | 1/72-72/13 | 70-72 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→72 |
| WTAMATCH-26JUL13SHEGAL-SHE | 57 | 23m | 1/62-62/11 | 61-62 | 5 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL13TIMANN-ANN | 58 | 23m | 1/60-60/16 | 58-60 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| WTAMATCH-26JUL13VALCOS-VAL | 81 | 21m | 0 | 81-85 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 42 tracked game(s) ({'WAKING': 26, 'OPEN': 2, 'QUIET': 14}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL12SONSCH | ATP_MAIN | 1.8 | 1 | **OPEN** |
| ATPMATCH-26JUL13PASKRU | ATP_MAIN | 0.533 | 1 | **OPEN** |
| ITFMATCH-26JUL13BERWAL | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13BRIDUB | ITF_M | 0.0 | 29 | **QUIET** |
| ITFMATCH-26JUL13DUHGAT | ITF_M | 0.0 | 16 | **QUIET** |
| ITFMATCH-26JUL13GELSEB | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13MCHAND | ITF_M | 0.0 | 78 | **QUIET** |
| ITFMATCH-26JUL13SARANG | ITF_M | 0.0 | 30 | **QUIET** |
| ITFMATCH-26JUL13SARBOV | ITF_M | 0.0 | 21 | **QUIET** |
| ITFMATCH-26JUL13WITHUE | ITF_M | 0.0 | 9 | **QUIET** |
| ITFWMATCH-26JUL13CAKVOZ | ITF_W | 0.0 | 12 | **QUIET** |
| ITFWMATCH-26JUL13IBRVER | ITF_W | 0.0 | 13 | **QUIET** |
| ITFWMATCH-26JUL13LABMAN | ITF_W | 0.0 | 10 | **QUIET** |
| ITFWMATCH-26JUL13MICSEB | ITF_W | 0.0 | 10 | **QUIET** |
| ITFWMATCH-26JUL13SCHNDU | ITF_W | 0.0 | 38 | **QUIET** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 4 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL13BINFUE | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13KRASAL | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13PRICRI | ATP_CHALL | 0.167 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13YEVCAM | ATP_CHALL | 0.267 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL13BEAMTI | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL13HASZAG | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL13MAYAER | ITF_M | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13FEHKRO | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL13MALMOO | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SVIART | ITF_W | 0.033 | 5 | **WAKING** |
| ITFWMATCH-26JUL13VELKOR | ITF_W | 0.033 | 10 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13GRABER | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PAPAND | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13RADREN | WTA_CHALL | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13AMAHER | WTA_MAIN | 0.2 | 1 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13AVAFET | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.067 | 2 | **WAKING** |
| WTAMATCH-26JUL13CRIJEA | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13KAWWAL | WTA_MAIN | 0.033 | 2 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13MONMAS | WTA_MAIN | 0.0 | 3 | **WAKING** |
| WTAMATCH-26JUL13QUERUS | WTA_MAIN | 0.067 | 2 | **WAKING** |
| WTAMATCH-26JUL13SHEGAL | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13TIMANN | WTA_MAIN | 0.033 | 2 | **WAKING** |

## PATTERNS (sub-B) — 1
- reality_divergence: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 8.0, "market_mid": 47.5, "divergence": -39.5, "emitted_et": "2026-07-13 01:53:46 AM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
