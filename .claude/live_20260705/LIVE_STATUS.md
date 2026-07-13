# LIVE VALIDATION — rolling status

- cycle 34 @ **2026-07-13 02:34:11 AM ET** | build `4c6a4832` | session boot 07-13 01:29 ET | log `live_v3_20260713.jsonl` | 14028 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 4 item(s)
- **half_arm_aging**: KXATPCHALLENGERMATCH-26JUL13YEVCAM-YEV {"fill": 42, "age_min": 59, "mode": "NO_BID(sib rested earlier, none now)"}
- **reality_divergence**: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 8.0, "market_mid": 47.5, "divergence": -39.5}
- **half_arm_aging**: KXWTAMATCH-26JUL13AMAHER-AMA {"fill": 35, "age_min": 35, "mode": "SET_BELOW_FLOW(prints 3c above)", "emitted_et": "2026-07-13 02:34:11 AM ET"}
- **reality_divergence**: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 9.0, "market_mid": 48.0, "divergence": -39.0}
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

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:35 | ATPCHALLENGERMATCH-26JUL13YEVCAM-Y | ATP_CHALL | underdog | 42 | 39 | +3 (place_cell) | — | pre | single |  | PENDING |
| 01:59 | WTAMATCH-26JUL13AMAHER-AMA | WTA_MAIN | underdog | 35 | 34 | +1 (place_cell) | — | pre | single |  | MIXED |
| 02:26 | ATPCHALLENGERMATCH-26JUL13KRASAL-K | ATP_CHALL | leader | 85 | 82 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 95 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 68, 'FLOW_ABOVE': 26, 'FLOW_AT_LEVEL': 1} | repriceable now: true 19 / false 76 | **cumulative bid_grade lines: 8925 (repriceable true 1313 / false 7612)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13BINFUE-B | 36 | 63m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13BINFUE-F | 62 | 63m | 0 | 62-64 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13DONWES-D | 25 | 2m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13DONWES-W | 73 | 4m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13KRASAL-S | 12 | 8m | 0 | 15-16 | — | **NO_FLOW** | 12 |  |
| ATPCHALLENGERMATCH-26JUL13KUZNIJ-K | 65 | 4m | 0 | 65-68 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13PRICRI-C | 8 | 61m | 4/9-10/415 | 9-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ATPCHALLENGERMATCH-26JUL13PRICRI-P | 90 | 34m | 0 | 90-91 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 64m | 1/59-59/32 | 57-59 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ATPMATCH-26JUL12FELKEC-FEL | 26 | 34m | 5/27-27/127 | 26-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ATPMATCH-26JUL12FELKEC-KEC | 73 | 32m | 34/73-75/9066 | 73-74 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPMATCH-26JUL12SONSCH-SON | 65 | 64m | 112/68-71/16710 | 69-70 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPMATCH-26JUL13MARMID-MAR | 37 | 29m | 8/38-38/183 | 37-38 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| ATPMATCH-26JUL13MARMID-MID | 62 | 34m | 9/63-63/575 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ATPMATCH-26JUL13PASKRU-PAS | 64 | 61m | 21/65-65/1359 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFMATCH-26JUL13BERWAL-BER | 68 | 57m | 0 | 69-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERWAL-WAL | 22 | 57m | 0 | 24-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BRIDUB-DUB | 24 | 43m | 0 | 24-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DUHGAT-DUH | 54 | 61m | 6/70-73/553 | 58-66 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13DUHGAT-GAT | 27 | 61m | 0 | 33-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GARCIO-CIO | 19 | 24m | 0 | 19-28 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GARCIO-GAR | 71 | 23m | 0 | 71-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HASZAG-HAS | 75 | 61m | 0 | 86-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MAYAER-AER | 39 | 58m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MAYAER-MAY | 56 | 37m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MCHAND-AND | 9 | 43m | 0 | 9-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MEHJEF-JEF | 77 | 2m | 0 | 77-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MEHJEF-MEH | 14 | 1m | 0 | 14-23 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SARANG-SAR | 24 | 61m | 0 | 25-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SARBOV-BOV | 28 | 43m | 1/40-40/11 | 31-40 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13TIMCAR-CAR | 8 | 23m | 0 | 8-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13TIMCAR-TIM | 79 | 23m | 0 | 79-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13WITHUE-WIT | 85 | 32m | 0 | 85-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BOEPOH-BOE | 13 | 4m | 0 | 13-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BOEPOH-POH | 52 | 4m | 0 | 68-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BULEVT-BUL | 59 | 32m | 0 | 59-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BULEVT-EVT | 15 | 33m | 0 | 15-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13CAKVOZ-VOZ | 25 | 61m | 0 | 25-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13DELBRO-BRO | 59 | 32m | 1/64-64/15 | 59-64 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13DELBRO-DEL | 36 | 28m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13FEHKRO-FEH | 9 | 57m | 1/13-13/21 | 9-13 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL13FEHKRO-KRO | 87 | 17m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IBRVER-IBR | 21 | 58m | 0 | 23-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IBRVER-VER | 55 | 57m | 0 | 60-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUHSEK-KUH | 72 | 32m | 0 | 72-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUHSEK-SEK | 14 | 33m | 0 | 22-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LABMAN-LAB | 62 | 64m | 0 | 63-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LABMAN-MAN | 26 | 61m | 0 | 26-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LOLBED-LOL | 91 | 33m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MAL | 79 | 61m | 0 | 79-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MOO | 13 | 61m | 0 | 16-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MICSEB-SEB | 67 | 63m | 0 | 70-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MITROM-MIT | 28 | 33m | 0 | 29-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MITROM-ROM | 64 | 32m | 0 | 64-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PETURB-PET | 53 | 33m | 0 | 53-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PETURB-URB | 36 | 32m | 0 | 36-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RAJHUT-HUT | 18 | 33m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RAJHUT-RAJ | 74 | 32m | 0 | 74-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-NDU | 10 | 57m | 0 | 10-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-SCH | 51 | 57m | 0 | 51-90 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SVIART-SVI | 22 | 61m | 5/26-27/76 | 22-27 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFWMATCH-26JUL13VELKOR-KOR | 64 | 63m | 0 | 64-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13VELKOR-VEL | 25 | 63m | 2/35-35/3 | 25-35 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13ZABSEV-SEV | 63 | 33m | 0 | 63-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZABSEV-ZAB | 25 | 32m | 0 | 25-36 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13GRABER-B | 20 | 61m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13GRABER-G | 78 | 3m | 1/80-80/6 | 79-80 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| WTACHALLENGERMATCH-26JUL13KABPER-K | 72 | 4m | 0 | 72-74 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13KABPER-P | 26 | 4m | 0 | 26-28 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13KHOZHA-K | 82 | 3m | 0 | 82-84 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13KHOZHA-Z | 16 | 33m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PANFAL-F | 54 | 29m | 0 | 54-56 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PANFAL-P | 43 | 29m | 0 | 43-45 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PAPAND-A | 78 | 53m | 1/79-79/1 | 78-79 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→79 |
| WTACHALLENGERMATCH-26JUL13PAPAND-P | 22 | 61m | 5/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 83 | 61m | 3/85-85/5 | 84-85 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 15 | 61m | 1/16-16/15 | 15-16 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→16 |
| WTACHALLENGERMATCH-26JUL13RISPOH-P | 53 | 4m | 0 | 53-54 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13RISPOH-R | 45 | 4m | 0 | 45-47 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13SHIHUA-H | 65 | 33m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13SHIHUA-S | 33 | 33m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13AMAHER-HER | 62 | 35m | 38/65-66/1160 | 65-66 | 3 | **FLOW_ABOVE** | 62 | flow above but bound 62c < flow -- chasing breaks goal |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 50m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13AVAFET-FET | 8 | 63m | 9/9-9/314 | 8-9 | 1 | **FLOW_ABOVE** | 7 | flow above but bound 7c < flow -- chasing breaks goal |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 54m | 1/61-61/15 | 59-61 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| WTAMATCH-26JUL13CRIJEA-CRI | 64 | 63m | 3/65-65/30 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| WTAMATCH-26JUL13KAWWAL-WAL | 67 | 61m | 1/69-69/14 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| WTAMATCH-26JUL13KRETOM-KRE | 88 | 63m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13MONMAS-MAS | 81 | 61m | 0 | 81-84 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13QUERUS-RUS | 69 | 49m | 1/72-72/13 | 70-72 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→72 |
| WTAMATCH-26JUL13ROMKUL-KUL | 23 | 15m | 0 | 23-24 | — | **NO_FLOW** | 22 |  |
| WTAMATCH-26JUL13ROMKUL-ROM | 76 | 4m | 0 | 76-77 | — | **NO_FLOW** | 77 |  |
| WTAMATCH-26JUL13SHEGAL-SHE | 57 | 63m | 1/62-62/11 | 61-62 | 5 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL13TIMANN-ANN | 58 | 63m | 1/60-60/16 | 58-60 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| WTAMATCH-26JUL13VALCOS-VAL | 81 | 61m | 0 | 81-85 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTAMATCH-26JUL13AMAHER | 35 | 66 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL13KRASAL | 85 | 16 | **101** | 97 | +4 |

## FLOW-STATE — 62 tracked game(s) ({'WAKING': 38, 'OPEN': 3, 'QUIET': 21}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL12FELKEC | ATP_MAIN | 1.2 | 1 | **OPEN** |
| ATPMATCH-26JUL12SONSCH | ATP_MAIN | 1.6 | 1 | **OPEN** |
| WTAMATCH-26JUL13AMAHER | WTA_MAIN | 1.467 | 1 | **OPEN** |
| ITFMATCH-26JUL13BERWAL | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13BRIDUB | ITF_M | 0.0 | 29 | **QUIET** |
| ITFMATCH-26JUL13GARCIO | ITF_M | 0.0 | 9 | **QUIET** |
| ITFMATCH-26JUL13MCHAND | ITF_M | 0.0 | 78 | **QUIET** |
| ITFMATCH-26JUL13MEHJEF | ITF_M | 0.0 | 9 | **QUIET** |
| ITFMATCH-26JUL13SARANG | ITF_M | 0.0 | 30 | **QUIET** |
| ITFMATCH-26JUL13TIMCAR | ITF_M | 0.0 | 13 | **QUIET** |
| ITFMATCH-26JUL13WITHUE | ITF_M | 0.0 | 7 | **QUIET** |
| ITFWMATCH-26JUL13BOEPOH | ITF_W | 0.0 | 18 | **QUIET** |
| ITFWMATCH-26JUL13BULEVT | ITF_W | 0.0 | 25 | **QUIET** |
| ITFWMATCH-26JUL13CAKVOZ | ITF_W | 0.0 | 12 | **QUIET** |
| ITFWMATCH-26JUL13IBRVER | ITF_W | 0.0 | 15 | **QUIET** |
| ITFWMATCH-26JUL13LABMAN | ITF_W | 0.0 | 10 | **QUIET** |
| ITFWMATCH-26JUL13MICSEB | ITF_W | 0.0 | 10 | **QUIET** |
| ITFWMATCH-26JUL13MITROM | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL13PETURB | ITF_W | 0.0 | 10 | **QUIET** |
| ITFWMATCH-26JUL13RAJHUT | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL13SCHNDU | ITF_W | 0.0 | 38 | **QUIET** |
| ITFWMATCH-26JUL13VELKOR | ITF_W | 0.0 | 10 | **QUIET** |
| ITFWMATCH-26JUL13ZABSEV | ITF_W | 0.0 | 11 | **QUIET** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 4 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL13BINFUE | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13DONWES | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13KRASAL | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13KUZNIJ | ATP_CHALL | 0.0 | 3 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13PRICRI | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13YEVCAM | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 2 | **WAKING** |
| ATPMATCH-26JUL13MARMID | ATP_MAIN | 0.433 | 1 | **WAKING** |
| ATPMATCH-26JUL13PASKRU | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL13DUHGAT | ITF_M | 0.167 | 8 | **WAKING** |
| ITFMATCH-26JUL13HASZAG | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL13MAYAER | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL13SARBOV | ITF_M | 0.033 | 9 | **WAKING** |
| ITFWMATCH-26JUL13DELBRO | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL13FEHKRO | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13KUHSEK | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13LOLBED | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13MALMOO | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SVIART | ITF_W | 0.133 | 5 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13GRABER | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13KABPER | WTA_CHALL | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13KHOZHA | WTA_CHALL | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PANFAL | WTA_CHALL | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PAPAND | WTA_CHALL | 0.167 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13RADREN | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13RISPOH | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13SHIHUA | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13AVAFET | WTA_MAIN | 0.2 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13CRIJEA | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KAWWAL | WTA_MAIN | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13MONMAS | WTA_MAIN | 0.0 | 3 | **WAKING** |
| WTAMATCH-26JUL13QUERUS | WTA_MAIN | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13ROMKUL | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13SHEGAL | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13TIMANN | WTA_MAIN | 0.0 | 2 | **WAKING** |

## PATTERNS (sub-B) — 4
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL13YEVCAM-YEV {"fill": 42, "age_min": 59, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 8.0, "market_mid": 47.5, "divergence": -39.5}
- half_arm_aging: KXWTAMATCH-26JUL13AMAHER-AMA {"fill": 35, "age_min": 35, "mode": "SET_BELOW_FLOW(prints 3c above)", "emitted_et": "2026-07-13 02:34:11 AM ET"}
- reality_divergence: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 9.0, "market_mid": 48.0, "divergence": -39.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
