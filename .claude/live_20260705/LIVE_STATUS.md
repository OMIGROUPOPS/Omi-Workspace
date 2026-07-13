# LIVE VALIDATION — rolling status

- cycle 29 @ **2026-07-13 01:43:38 AM ET** | build `8ed9e70e` | session boot 07-13 01:29 ET | log `live_v3_20260713.jsonl` | 4893 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 11 violation(s)
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

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_self_fill_bell.md**

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:35 | ATPCHALLENGERMATCH-26JUL13YEVCAM-Y | ATP_CHALL | underdog | 42 | 39 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 50 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 40, 'FLOW_ABOVE': 10} | repriceable now: true 7 / false 43 | **cumulative bid_grade lines: 8850 (repriceable true 1296 / false 7554)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13BINFUE-B | 36 | 13m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13BINFUE-F | 62 | 13m | 0 | 62-64 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13KRASAL-S | 14 | 13m | 0 | 14-15 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13PRICRI-C | 8 | 11m | 0 | 8-9 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 13m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12SONSCH-SON | 65 | 13m | 33/68-70/3249 | 69-70 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPMATCH-26JUL13PASKRU-PAS | 64 | 11m | 12/65-65/1138 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFMATCH-26JUL13BEAMTI-BEA | 90 | 11m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BEAMTI-MTI | 7 | 13m | 2/8-8/23 | 7-8 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFMATCH-26JUL13BERWAL-BER | 68 | 7m | 0 | 69-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERWAL-WAL | 22 | 7m | 0 | 24-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BRIDUB-DUB | 23 | 7m | 0 | 23-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DUHGAT-DUH | 54 | 11m | 0 | 56-73 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DUHGAT-GAT | 27 | 11m | 0 | 27-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GELSEB-SEB | 74 | 7m | 0 | 74-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HASZAG-HAS | 75 | 11m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MAYAER-AER | 39 | 8m | 0 | 39-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MCHAND-AND | 8 | 7m | 0 | 8-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SARANG-SAR | 24 | 11m | 0 | 24-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SARBOV-BOV | 26 | 0m | 0 | 27-52 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13WITHUE-WIT | 83 | 7m | 0 | 83-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13CAKVOZ-VOZ | 25 | 11m | 0 | 25-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13FEHKRO-FEH | 9 | 7m | 0 | 9-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IBRVER-IBR | 21 | 8m | 0 | 31-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IBRVER-VER | 55 | 7m | 0 | 55-68 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LABMAN-LAB | 62 | 13m | 0 | 63-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LABMAN-MAN | 26 | 11m | 0 | 26-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MAL | 79 | 11m | 0 | 79-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MOO | 13 | 11m | 0 | 16-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MICSEB-SEB | 67 | 12m | 0 | 70-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-NDU | 10 | 7m | 0 | 10-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-SCH | 51 | 7m | 0 | 51-90 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SVIART-SVI | 22 | 11m | 1/27-27/3 | 22-27 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13VELKOR-KOR | 64 | 13m | 0 | 64-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13VELKOR-VEL | 25 | 13m | 1/35-35/2 | 25-35 | 10 | **FLOW_ABOVE** | 99 |  |
| WTACHALLENGERMATCH-26JUL13GRABER-B | 20 | 11m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PAPAND-A | 78 | 2m | 0 | 78-79 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PAPAND-P | 22 | 11m | 0 | 22-23 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 83 | 11m | 0 | 84-85 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 15 | 11m | 0 | 15-16 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13AMAHER-AMA | 35 | 11m | 4/36-36/628 | 35-36 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| WTAMATCH-26JUL13AVAFET-FET | 8 | 13m | 1/9-9/10 | 8-9 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 3m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13CRIJEA-CRI | 64 | 13m | 1/65-65/15 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| WTAMATCH-26JUL13KAWWAL-WAL | 67 | 11m | 0 | 67-69 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 88 | 13m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13MONMAS-MAS | 81 | 11m | 0 | 81-84 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13SHEGAL-SHE | 57 | 13m | 1/62-62/11 | 61-62 | 5 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL13TIMANN-ANN | 58 | 13m | 1/60-60/16 | 58-60 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| WTAMATCH-26JUL13VALCOS-VAL | 81 | 11m | 0 | 81-85 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 40 tracked game(s) ({'WAKING': 23, 'OPEN': 2, 'QUIET': 15}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL12SONSCH | ATP_MAIN | 1.967 | 1 | **OPEN** |
| ATPMATCH-26JUL13PASKRU | ATP_MAIN | 0.6 | 1 | **OPEN** |
| ITFMATCH-26JUL13BERWAL | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13BRIDUB | ITF_M | 0.0 | 32 | **QUIET** |
| ITFMATCH-26JUL13DUHGAT | ITF_M | 0.0 | 17 | **QUIET** |
| ITFMATCH-26JUL13GELSEB | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13MAYAER | ITF_M | 0.0 | 7 | **QUIET** |
| ITFMATCH-26JUL13MCHAND | ITF_M | 0.0 | 79 | **QUIET** |
| ITFMATCH-26JUL13SARANG | ITF_M | 0.0 | 33 | **QUIET** |
| ITFMATCH-26JUL13SARBOV | ITF_M | 0.0 | 25 | **QUIET** |
| ITFMATCH-26JUL13WITHUE | ITF_M | 0.0 | 9 | **QUIET** |
| ITFWMATCH-26JUL13CAKVOZ | ITF_W | 0.0 | 12 | **QUIET** |
| ITFWMATCH-26JUL13IBRVER | ITF_W | 0.0 | 13 | **QUIET** |
| ITFWMATCH-26JUL13LABMAN | ITF_W | 0.0 | 10 | **QUIET** |
| ITFWMATCH-26JUL13MICSEB | ITF_W | 0.0 | 10 | **QUIET** |
| ITFWMATCH-26JUL13SCHNDU | ITF_W | 0.0 | 38 | **QUIET** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 4 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL13BINFUE | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13KRASAL | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13PRICRI | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13YEVCAM | ATP_CHALL | 0.267 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL13BEAMTI | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL13HASZAG | ITF_M | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13FEHKRO | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13MALMOO | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SVIART | ITF_W | 0.033 | 5 | **WAKING** |
| ITFWMATCH-26JUL13VELKOR | ITF_W | 0.033 | 10 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13GRABER | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PAPAND | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13RADREN | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13AMAHER | WTA_MAIN | 0.2 | 1 | **WAKING** |
| WTAMATCH-26JUL13AVAFET | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.033 | 2 | **WAKING** |
| WTAMATCH-26JUL13CRIJEA | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13KAWWAL | WTA_MAIN | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13MONMAS | WTA_MAIN | 0.0 | 3 | **WAKING** |
| WTAMATCH-26JUL13SHEGAL | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13TIMANN | WTA_MAIN | 0.033 | 2 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
