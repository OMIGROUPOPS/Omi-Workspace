# LIVE VALIDATION — rolling status

- cycle 31 @ **2026-07-13 02:03:53 AM ET** | build `9ad57d7f` | session boot 07-13 01:29 ET | log `live_v3_20260713.jsonl` | 9275 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 1 item(s)
- **reality_divergence**: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 8.0, "market_mid": 47.5, "divergence": -39.5}
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 16 violation(s)
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
| 02:02:20 | **self_fill_bell** | KXITFWMATCH-26JUL13BULEVT-BUL | own buys rose 10c (49->59) in 1800s -> match-live presumption, entry buys FROZEN |
| 02:02:21 | **self_fill_bell** | KXITFWMATCH-26JUL13KUHSEK-KUH | own buys rose 15c (57->72) in 1800s -> match-live presumption, entry buys FROZEN |
| 02:02:23 | **self_fill_bell** | KXITFWMATCH-26JUL13MITROM-ROM | own buys rose 4c (60->64) in 1800s -> match-live presumption, entry buys FROZEN |
| 02:02:24 | **self_fill_bell** | KXITFWMATCH-26JUL13RAJHUT-RAJ | own buys rose 15c (59->74) in 1800s -> match-live presumption, entry buys FROZEN |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_self_fill_bell.md**

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:35 | ATPCHALLENGERMATCH-26JUL13YEVCAM-Y | ATP_CHALL | underdog | 42 | 39 | +3 (place_cell) | — | pre | single |  | PENDING |
| 01:59 | WTAMATCH-26JUL13AMAHER-AMA | WTA_MAIN | underdog | 35 | 34 | +1 (place_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 77 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 52, 'FLOW_ABOVE': 25} | repriceable now: true 19 / false 58 | **cumulative bid_grade lines: 8893 (repriceable true 1310 / false 7583)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13BINFUE-B | 36 | 33m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13BINFUE-F | 62 | 33m | 0 | 62-64 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13KRASAL-K | 85 | 12m | 2/86-86/3 | 85-86 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→86 |
| ATPCHALLENGERMATCH-26JUL13KRASAL-S | 14 | 33m | 3/15-15/320 | 15-16 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ATPCHALLENGERMATCH-26JUL13PRICRI-C | 8 | 31m | 4/9-10/415 | 9-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ATPCHALLENGERMATCH-26JUL13PRICRI-P | 90 | 3m | 0 | 90-91 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 34m | 1/59-59/32 | 57-59 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ATPMATCH-26JUL12FELKEC-FEL | 26 | 3m | 1/27-27/31 | 26-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ATPMATCH-26JUL12FELKEC-KEC | 73 | 1m | 2/74-74/704 | 73-74 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ATPMATCH-26JUL12SONSCH-SON | 65 | 34m | 63/68-71/5455 | 69-70 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPMATCH-26JUL13MARMID-MID | 62 | 3m | 3/63-63/153 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ATPMATCH-26JUL13PASKRU-PAS | 64 | 31m | 19/65-65/1217 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFMATCH-26JUL13BEAMTI-BEA | 90 | 31m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BEAMTI-MTI | 7 | 33m | 4/8-8/81 | 7-8 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL13BERWAL-BER | 68 | 27m | 0 | 69-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERWAL-WAL | 22 | 27m | 0 | 24-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BRIDUB-DUB | 24 | 13m | 0 | 24-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DUHGAT-DUH | 54 | 31m | 1/70-70/1 | 56-70 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13DUHGAT-GAT | 27 | 31m | 0 | 30-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HASZAG-HAS | 75 | 31m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MAYAER-AER | 39 | 28m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MAYAER-MAY | 56 | 6m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MCHAND-AND | 9 | 13m | 0 | 9-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MEHJEF-JEF | 74 | 3m | 0 | 74-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MEHJEF-MEH | 12 | 4m | 0 | 12-26 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SARANG-SAR | 24 | 31m | 0 | 25-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SARBOV-BOV | 28 | 13m | 0 | 31-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13WITHUE-WIT | 85 | 2m | 0 | 85-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BULEVT-BUL | 59 | 2m | 0 | 59-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BULEVT-EVT | 15 | 3m | 0 | 15-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13CAKVOZ-VOZ | 25 | 31m | 0 | 25-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13DELBRO-BRO | 59 | 1m | 0 | 59-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13DELBRO-DEL | 35 | 3m | 0 | 35-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13FEHKRO-FEH | 9 | 27m | 1/13-13/21 | 9-13 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL13IBRVER-IBR | 21 | 28m | 0 | 24-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IBRVER-VER | 55 | 27m | 0 | 58-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUHSEK-KUH | 72 | 2m | 0 | 72-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUHSEK-SEK | 14 | 3m | 0 | 22-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LABMAN-LAB | 62 | 34m | 0 | 63-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LABMAN-MAN | 26 | 31m | 0 | 26-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LOLBED-LOL | 91 | 3m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MAL | 79 | 31m | 0 | 79-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MOO | 13 | 31m | 0 | 16-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MICSEB-SEB | 67 | 33m | 0 | 70-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MITROM-MIT | 28 | 3m | 0 | 29-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MITROM-ROM | 64 | 1m | 0 | 64-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PETURB-PET | 53 | 3m | 0 | 53-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PETURB-URB | 36 | 2m | 0 | 36-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RAJHUT-HUT | 18 | 3m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RAJHUT-RAJ | 74 | 1m | 0 | 74-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-NDU | 10 | 27m | 0 | 10-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-SCH | 51 | 27m | 0 | 51-90 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SVIART-SVI | 22 | 31m | 1/27-27/3 | 22-27 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13VELKOR-KOR | 64 | 33m | 0 | 64-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13VELKOR-VEL | 25 | 33m | 2/35-35/3 | 25-35 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13ZABSEV-SEV | 63 | 3m | 0 | 63-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZABSEV-ZAB | 25 | 1m | 0 | 25-36 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13GRABER-B | 20 | 31m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13KHOZHA-Z | 16 | 3m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PAPAND-A | 78 | 23m | 1/79-79/1 | 78-79 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→79 |
| WTACHALLENGERMATCH-26JUL13PAPAND-P | 22 | 31m | 0 | 22-23 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 83 | 31m | 2/85-85/3 | 84-85 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 15 | 31m | 1/16-16/15 | 15-16 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→16 |
| WTACHALLENGERMATCH-26JUL13SHIHUA-H | 65 | 3m | 0 | 65-67 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13SHIHUA-S | 33 | 3m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13AMAHER-HER | 62 | 4m | 5/66-66/95 | 64-66 | 4 | **FLOW_ABOVE** | 62 | flow above but bound 62c < flow -- chasing breaks goal |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 19m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13AVAFET-FET | 8 | 33m | 3/9-9/114 | 8-9 | 1 | **FLOW_ABOVE** | 7 | flow above but bound 7c < flow -- chasing breaks goal |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 24m | 1/61-61/15 | 59-61 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| WTAMATCH-26JUL13CRIJEA-CRI | 64 | 33m | 3/65-65/30 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| WTAMATCH-26JUL13KAWWAL-WAL | 67 | 31m | 1/69-69/14 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| WTAMATCH-26JUL13KRETOM-KRE | 88 | 33m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13MONMAS-MAS | 81 | 31m | 0 | 81-84 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13QUERUS-RUS | 69 | 19m | 1/72-72/13 | 70-72 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→72 |
| WTAMATCH-26JUL13SHEGAL-SHE | 57 | 33m | 1/62-62/11 | 61-62 | 5 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL13TIMANN-ANN | 58 | 33m | 1/60-60/16 | 58-60 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| WTAMATCH-26JUL13VALCOS-VAL | 81 | 31m | 0 | 81-85 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTAMATCH-26JUL13AMAHER | 35 | 66 | **101** | 97 | +4 |

## FLOW-STATE — 54 tracked game(s) ({'WAKING': 31, 'OPEN': 5, 'QUIET': 18}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13YEVCAM | ATP_CHALL | 0.3 | 1 | **OPEN** |
| ATPMATCH-26JUL12FELKEC | ATP_MAIN | 1.3 | 1 | **OPEN** |
| ATPMATCH-26JUL12SONSCH | ATP_MAIN | 2.0 | 1 | **OPEN** |
| ATPMATCH-26JUL13PASKRU | ATP_MAIN | 0.633 | 1 | **OPEN** |
| WTAMATCH-26JUL13AMAHER | WTA_MAIN | 0.933 | 1 | **OPEN** |
| ITFMATCH-26JUL13BERWAL | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13BRIDUB | ITF_M | 0.0 | 29 | **QUIET** |
| ITFMATCH-26JUL13MCHAND | ITF_M | 0.0 | 78 | **QUIET** |
| ITFMATCH-26JUL13MEHJEF | ITF_M | 0.0 | 14 | **QUIET** |
| ITFMATCH-26JUL13SARANG | ITF_M | 0.0 | 30 | **QUIET** |
| ITFMATCH-26JUL13SARBOV | ITF_M | 0.0 | 9 | **QUIET** |
| ITFMATCH-26JUL13WITHUE | ITF_M | 0.0 | 7 | **QUIET** |
| ITFWMATCH-26JUL13BULEVT | ITF_W | 0.0 | 25 | **QUIET** |
| ITFWMATCH-26JUL13CAKVOZ | ITF_W | 0.0 | 12 | **QUIET** |
| ITFWMATCH-26JUL13IBRVER | ITF_W | 0.0 | 17 | **QUIET** |
| ITFWMATCH-26JUL13LABMAN | ITF_W | 0.0 | 10 | **QUIET** |
| ITFWMATCH-26JUL13MICSEB | ITF_W | 0.0 | 10 | **QUIET** |
| ITFWMATCH-26JUL13MITROM | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL13PETURB | ITF_W | 0.0 | 10 | **QUIET** |
| ITFWMATCH-26JUL13RAJHUT | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL13SCHNDU | ITF_W | 0.0 | 38 | **QUIET** |
| ITFWMATCH-26JUL13ZABSEV | ITF_W | 0.0 | 11 | **QUIET** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 4 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL13BINFUE | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13KRASAL | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13PRICRI | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.033 | 2 | **WAKING** |
| ATPMATCH-26JUL13MARMID | ATP_MAIN | 0.367 | 1 | **WAKING** |
| ITFMATCH-26JUL13BEAMTI | ITF_M | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL13DUHGAT | ITF_M | 0.033 | 14 | **WAKING** |
| ITFMATCH-26JUL13HASZAG | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL13MAYAER | ITF_M | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13DELBRO | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13FEHKRO | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL13KUHSEK | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13LOLBED | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13MALMOO | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SVIART | ITF_W | 0.033 | 5 | **WAKING** |
| ITFWMATCH-26JUL13VELKOR | ITF_W | 0.033 | 10 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13GRABER | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13KHOZHA | WTA_CHALL | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PAPAND | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13RADREN | WTA_CHALL | 0.1 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13SHIHUA | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13AVAFET | WTA_MAIN | 0.1 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.067 | 2 | **WAKING** |
| WTAMATCH-26JUL13CRIJEA | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13KAWWAL | WTA_MAIN | 0.033 | 2 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13MONMAS | WTA_MAIN | 0.0 | 3 | **WAKING** |
| WTAMATCH-26JUL13QUERUS | WTA_MAIN | 0.067 | 2 | **WAKING** |
| WTAMATCH-26JUL13SHEGAL | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13TIMANN | WTA_MAIN | 0.033 | 2 | **WAKING** |

## PATTERNS (sub-B) — 1
- reality_divergence: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 8.0, "market_mid": 47.5, "divergence": -39.5}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
