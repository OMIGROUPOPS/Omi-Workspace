# LIVE VALIDATION — rolling status

- cycle 43 @ **2026-07-13 04:04:58 AM ET** | build `fc689e7f` | session boot 07-13 03:44 ET | log `live_v3_20260713.jsonl` | 10945 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 13 item(s)
- **reality_divergence**: KXITFMATCH-26JUL13BARURA-URA {"kind": "resting_bid", "ref": 14.0, "market_mid": 44.0, "divergence": -30.0}
- **reality_divergence**: KXITFMATCH-26JUL13BATSYC-BAT {"kind": "resting_bid", "ref": 49.0, "market_mid": 75.5, "divergence": -26.5}
- **reality_divergence**: KXITFMATCH-26JUL13HOSSIN-HOS {"kind": "resting_bid", "ref": 51.0, "market_mid": 90.0, "divergence": -39.0}
- **reality_divergence**: KXITFMATCH-26JUL13LEAMEN-MEN {"kind": "resting_bid", "ref": 12.0, "market_mid": 44.5, "divergence": -32.5}
- **reality_divergence**: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 11.0, "market_mid": 48.0, "divergence": -37.0}
- **reality_divergence**: KXITFWMATCH-26JUL13CEUKRE-CEU {"kind": "resting_bid", "ref": 20.0, "market_mid": 53.5, "divergence": -33.5}
- **reality_divergence**: KXITFWMATCH-26JUL13CEUKRE-KRE {"kind": "resting_bid", "ref": 16.0, "market_mid": 46.0, "divergence": -30.0}
- **reality_divergence**: KXITFWMATCH-26JUL13ZHACOR-ZHA {"kind": "resting_bid", "ref": 15.0, "market_mid": 49.0, "divergence": -34.0}
- **reality_divergence**: KXITFMATCH-26JUL13MARVAL-VAL {"kind": "resting_bid", "ref": 35.0, "market_mid": 67.5, "divergence": -32.5, "emitted_et": "2026-07-13 04:04:58 AM ET"}
- **reality_divergence**: KXITFMATCH-26JUL13SEGKAS-KAS {"kind": "resting_bid", "ref": 16.0, "market_mid": 49.5, "divergence": -33.5, "emitted_et": "2026-07-13 04:04:58 AM ET"}
- **reality_divergence**: KXITFMATCH-26JUL13TAZHAR-TAZ {"kind": "resting_bid", "ref": 48.0, "market_mid": 76.5, "divergence": -28.5, "emitted_et": "2026-07-13 04:04:58 AM ET"}
- **reality_divergence**: KXITFMATCH-26JUL13VRTKLA-KLA {"kind": "resting_bid", "ref": 19.0, "market_mid": 47.5, "divergence": -28.5, "emitted_et": "2026-07-13 04:04:58 AM ET"}
- **reality_divergence**: KXITFWMATCH-26JUL13SIMMAR-SIM {"kind": "resting_bid", "ref": 14.0, "market_mid": 48.0, "divergence": -34.0, "emitted_et": "2026-07-13 04:04:58 AM ET"}
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 4 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 03:45:53 | **self_fill_bell** | KXITFWMATCH-26JUL13IVAKOP-IVA | own buys rose 40c (51->91) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:48:31 | **self_fill_bell** | KXITFMATCH-26JUL13BATSYC-BAT | own buys rose 15c (49->64) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:51:44 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 1251.7 |
| 03:53:36 | **self_fill_bell** | KXITFMATCH-26JUL13URRDRA-URR | own buys rose 19c (49->68) in 1800s -> match-live presumption, entry buys FROZEN |

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 03:45 | ATPCHALLENGERMATCH-26JUL13BINFUE-F | ATP_CHALL | ? | 62 | 59 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 03:45 | ATPMATCH-26JUL13PASKRU-PAS | ATP_MAIN | ? | 64 | 63 | +1 (window_cell) | — | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 166 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 148, 'FLOW_AT_LEVEL': 1, 'FLOW_ABOVE': 17} | repriceable now: true 9 / false 157 | **cumulative bid_grade lines: 9129 (repriceable true 1324 / false 7805)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13BINFUE-B | 35 | 14m | 0 | 36-39 | — | **NO_FLOW** | 35 |  |
| ATPCHALLENGERMATCH-26JUL13DONWES-D | 25 | 16m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13DONWES-W | 73 | 19m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13KRASAL-S | 12 | 19m | 0 | 17-18 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13KUZNIJ-K | 65 | 19m | 0 | 65-68 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13KUZNIJ-N | 32 | 19m | 0 | 32-34 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13PRICRI-C | 10 | 19m | 7/11-12/848 | 10-11 | 1 | **FLOW_ABOVE** | 8 | flow above but bound 8c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL13PRICRI-P | 89 | 19m | 0 | 89-91 | — | **NO_FLOW** | 86 |  |
| ATPCHALLENGERMATCH-26JUL13YEVCAM-C | 56 | 19m | 0 | 57-58 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13YEVCAM-Y | 42 | 15m | 0 | 42-45 | — | **NO_FLOW** | 42 |  |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 19m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12SONSCH-SON | 65 | 19m | 26/69-71/7152 | 69-70 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ATPMATCH-26JUL13COLSKA-SKA | 16 | 4m | 0 | 16-17 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL13FAUDAM-FAU | 55 | 6m | 2/56-56/33 | 55-56 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ATPMATCH-26JUL13MARMID-MAR | 37 | 19m | 1/38-38/221 | 37-38 | 1 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ATPMATCH-26JUL13MARMID-MID | 62 | 19m | 1/63-63/7 | 62-63 | 1 | **FLOW_ABOVE** | 63 | REPRICEABLE→63 |
| ATPMATCH-26JUL13PASKRU-KRU | 33 | 19m | 3/36-37/57 | 36-37 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| ATPMATCH-26JUL13SANDAN-DAN | 77 | 19m | 1/78-78/6 | 77-78 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ATPMATCH-26JUL13SANDAN-SAN | 22 | 19m | 0 | 22-23 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL13TABROD-TAB | 59 | 19m | 21/59-60/3908 | 59-60 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL13BARURA-URA | 14 | 19m | 170/52-89/5484 | 85-61 | 38 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13BATSYC-BAT | 64 | 16m | 0 | 64-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BATSYC-SYC | 12 | 19m | 0 | 12-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BENWRI-BEN | 38 | 19m | 0 | 38-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BENWRI-WRI | 55 | 16m | 0 | 55-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERPIA-BER | 83 | 16m | 0 | 83-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERPIA-PIA | 9 | 19m | 0 | 9-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERWAL-BER | 69 | 16m | 0 | 69-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERWAL-WAL | 24 | 16m | 0 | 24-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BRIDUB-DUB | 25 | 19m | 0 | 25-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13CASMOL-CAS | 81 | 14m | 0 | 81-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13CASMOL-MOL | 12 | 19m | 0 | 12-19 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DUTHAI-DUT | 54 | 14m | 0 | 54-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DUTHAI-HAI | 8 | 14m | 0 | 8-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GARCIO-CIO | 21 | 16m | 0 | 21-27 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GARCIO-GAR | 72 | 16m | 0 | 72-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GUNKUZ-GUN | 35 | 2m | 0 | 35-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GUNKUZ-KUZ | 59 | 13m | 0 | 59-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HASZAG-HAS | 86 | 16m | 0 | 86-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HASZAG-ZAG | 12 | 19m | 0 | 12-13 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HOSSIN-HOS | 52 | 10m | 0 | 88-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HOSSIN-SIN | 7 | 19m | 0 | 7-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13KOZHUS-HUS | 21 | 5m | 0 | 21-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13KOZHUS-KOZ | 69 | 5m | 0 | 69-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13LEAMEN-MEN | 13 | 14m | 0 | 13-73 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MARVAL-VAL | 35 | 4m | 0 | 52-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MAYAER-AER | 40 | 19m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MAYAER-MAY | 55 | 16m | 0 | 55-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MCHAND-AND | 11 | 19m | 0 | 11-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MEHJEF-JEF | 80 | 14m | 0 | 80-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MEHJEF-MEH | 15 | 19m | 0 | 15-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13PIELUE-LUE | 64 | 17m | 0 | 64-70 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13PIELUE-PIE | 30 | 19m | 0 | 30-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SARANG-SAR | 26 | 19m | 0 | 26-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SEGKAS-KAS | 16 | 3m | 0 | 16-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13TAZHAR-HAR | 11 | 3m | 0 | 11-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13TAZHAR-TAZ | 48 | 4m | 0 | 64-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13TIMCAR-CAR | 9 | 19m | 0 | 9-13 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13TIMCAR-TIM | 87 | 19m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13URRDRA-DRA | 12 | 13m | 0 | 16-26 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13URRDRA-URR | 68 | 11m | 0 | 74-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13VRTKLA-KLA | 19 | 4m | 0 | 19-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13VULPAO-PAO | 16 | 18m | 0 | 16-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13VULPAO-VUL | 51 | 18m | 0 | 51-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13WITHUE-WIT | 87 | 18m | 0 | 87-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BALHEJ-BAL | 70 | 3m | 0 | 70-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BALHEJ-HEJ | 24 | 3m | 0 | 24-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BOEPOH-BOE | 16 | 16m | 0 | 16-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BOEPOH-POH | 76 | 18m | 0 | 76-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BULEVT-BUL | 75 | 19m | 0 | 75-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BULEVT-EVT | 16 | 19m | 0 | 16-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13CAKVOZ-CAK | 70 | 18m | 0 | 70-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13CAKVOZ-VOZ | 24 | 17m | 0 | 24-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13CEUKRE-KRE | 16 | 19m | 0 | 16-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13DELBRO-BRO | 61 | 19m | 0 | 61-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13DELBRO-DEL | 36 | 17m | 0 | 36-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13FEHKRO-FEH | 10 | 19m | 0 | 10-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13FEHKRO-KRO | 87 | 16m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GADSVA-GAD | 25 | 4m | 0 | 25-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GADSVA-SVA | 65 | 3m | 0 | 65-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GIZVLA-GIZ | 14 | 19m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GIZVLA-VLA | 82 | 18m | 0 | 82-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GRORAS-GRO | 42 | 19m | 0 | 42-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GRORAS-RAS | 52 | 18m | 0 | 52-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IBRVER-IBR | 23 | 16m | 0 | 23-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IBRVER-VER | 63 | 4m | 0 | 63-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IVAKOP-IVA | 91 | 19m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KARFER-FER | 24 | 19m | 0 | 24-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KARFER-KAR | 57 | 17m | 0 | 57-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KMISUC-KMI | 22 | 4m | 0 | 22-71 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUHSEK-KUH | 75 | 14m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUHSEK-SEK | 22 | 16m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUMCHA-CHA | 20 | 16m | 0 | 20-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUMCHA-KUM | 54 | 19m | 0 | 54-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LABMAN-LAB | 64 | 19m | 0 | 64-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LABMAN-MAN | 28 | 19m | 0 | 28-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LAZREV-LAZ | 53 | 17m | 0 | 53-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LAZREV-REV | 17 | 19m | 0 | 24-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LOLBED-LOL | 91 | 19m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MAL | 79 | 16m | 0 | 79-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MOO | 16 | 16m | 0 | 16-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MICSEB-MIC | 21 | 19m | 0 | 21-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MICSEB-SEB | 70 | 19m | 0 | 70-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MITROM-MIT | 28 | 19m | 0 | 29-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MITROM-ROM | 64 | 16m | 0 | 64-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13NAGCHY-NAG | 93 | 4m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PETURB-PET | 57 | 17m | 0 | 57-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PETURB-URB | 36 | 19m | 0 | 36-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PULWIR-PUL | 25 | 19m | 0 | 25-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PULWIR-WIR | 63 | 19m | 0 | 63-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RAJHUT-HUT | 18 | 19m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RAJHUT-RAJ | 74 | 16m | 0 | 74-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-NDU | 15 | 19m | 0 | 15-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-SCH | 51 | 16m | 0 | 51-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SIMMAR-SIM | 14 | 4m | 0 | 14-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SVIART-SVI | 22 | 14m | 0 | 22-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13VELKOR-KOR | 63 | 1m | 0 | 63-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13VELKOR-VEL | 27 | 19m | 2/35-35/14 | 27-33 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13WIEMON-WIE | 94 | 19m | 0 | 94-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZABSEV-SEV | 63 | 19m | 0 | 63-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZABSEV-ZAB | 28 | 19m | 0 | 28-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHACOR-ZHA | 15 | 19m | 0 | 15-83 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13GRABER-B | 20 | 19m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13GRABER-G | 78 | 19m | 0 | 79-80 | — | **NO_FLOW** | 77 |  |
| WTACHALLENGERMATCH-26JUL13KABPER-K | 72 | 19m | 0 | 72-74 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13KABPER-P | 27 | 14m | 0 | 27-28 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13KHOZHA-K | 82 | 19m | 0 | 82-84 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13KHOZHA-Z | 16 | 19m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PANFAL-F | 54 | 19m | 0 | 54-56 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PANFAL-P | 43 | 19m | 0 | 43-45 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PAPAND-A | 77 | 4m | 0 | 77-78 | — | **NO_FLOW** | 76 |  |
| WTACHALLENGERMATCH-26JUL13PAPAND-P | 22 | 16m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 20 | flow above but bound 20c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL13PENTHA-P | 76 | 18m | 0 | 76-77 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PENTHA-T | 23 | 19m | 0 | 23-24 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 83 | 19m | 1/85-85/1 | 84-85 | 2 | **FLOW_ABOVE** | 82 | flow above but bound 82c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 15 | 19m | 1/16-16/26 | 15-16 | 1 | **FLOW_ABOVE** | 13 | flow above but bound 13c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL13RISPOH-P | 53 | 19m | 3/54-55/554 | 53-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| WTACHALLENGERMATCH-26JUL13RISPOH-R | 46 | 17m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13SAINUG-N | 66 | 19m | 0 | 66-67 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13SAINUG-S | 32 | 19m | 0 | 32-34 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13SHIHUA-H | 65 | 19m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13SHIHUA-S | 33 | 19m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13TIKBEN-B | 59 | 4m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13AMAHER-HER | 62 | 19m | 27/64-65/2384 | 64-64 | 2 | **FLOW_ABOVE** | 65 | REPRICEABLE→64 |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 19m | 0 | 48-49 | — | **NO_FLOW** | 46 |  |
| WTAMATCH-26JUL13AVAFET-AVA | 91 | 19m | 1/92-92/1 | 91-92 | 1 | **FLOW_ABOVE** | 92 | REPRICEABLE→92 |
| WTAMATCH-26JUL13AVAFET-FET | 8 | 19m | 0 | 8-9 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 19m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 19m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13CRIJEA-CRI | 65 | 18m | 0 | 65-67 | — | **NO_FLOW** | 66 |  |
| WTAMATCH-26JUL13CRIJEA-JEA | 33 | 2m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KAWWAL-KAW | 31 | 19m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KAWWAL-WAL | 67 | 19m | 0 | 67-69 | — | **NO_FLOW** | 69 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 88 | 19m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13LIUIPE-IPE | 19 | 19m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13LIUIPE-LIU | 80 | 19m | 0 | 80-81 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13MONMAS-MAS | 81 | 19m | 0 | 81-84 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13QUERUS-QUE | 28 | 19m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13QUERUS-RUS | 69 | 19m | 0 | 69-72 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13ROMKUL-KUL | 23 | 19m | 0 | 23-24 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13ROMKUL-ROM | 76 | 19m | 5/77-77/43 | 76-77 | 1 | **FLOW_ABOVE** | 77 | REPRICEABLE→77 |
| WTAMATCH-26JUL13SHEGAL-GAL | 37 | 19m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13SHEGAL-SHE | 61 | 16m | 0 | 61-62 | — | **NO_FLOW** | 62 |  |
| WTAMATCH-26JUL13TIMANN-ANN | 58 | 19m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13VALCOS-COS | 16 | 15m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13VALCOS-VAL | 81 | 19m | 1/85-85/1 | 81-85 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13BINFUE | 62 | 39 | **101** | 97 | +4 |
| ATPMATCH-26JUL13PASKRU | 64 | 37 | **101** | 97 | +4 |

## FLOW-STATE — 99 tracked game(s) ({'WAKING': 59, 'OPEN': 4, 'QUIET': 36}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13PRICRI | ATP_CHALL | 0.4 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL13YEVCAM | ATP_CHALL | 0.6 | 1 | **OPEN** |
| ATPMATCH-26JUL12SONSCH | ATP_MAIN | 1.533 | 1 | **OPEN** |
| ATPMATCH-26JUL13TABROD | ATP_MAIN | 0.967 | 1 | **OPEN** |
| ITFMATCH-26JUL13BATSYC | ITF_M | 0.0 | 23 | **QUIET** |
| ITFMATCH-26JUL13BENWRI | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13BERPIA | ITF_M | 0.0 | 8 | **QUIET** |
| ITFMATCH-26JUL13BERWAL | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13BRIDUB | ITF_M | 0.0 | 26 | **QUIET** |
| ITFMATCH-26JUL13CASMOL | ITF_M | 0.0 | 7 | **QUIET** |
| ITFMATCH-26JUL13DUTHAI | ITF_M | 0.0 | 38 | **QUIET** |
| ITFMATCH-26JUL13GARCIO | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13KOZHUS | ITF_M | 0.0 | 9 | **QUIET** |
| ITFMATCH-26JUL13LEAMEN | ITF_M | 0.0 | 60 | **QUIET** |
| ITFMATCH-26JUL13MARVAL | ITF_M | 0.0 | 31 | **QUIET** |
| ITFMATCH-26JUL13MCHAND | ITF_M | 0.0 | 74 | **QUIET** |
| ITFMATCH-26JUL13SARANG | ITF_M | 0.0 | 29 | **QUIET** |
| ITFMATCH-26JUL13SEGKAS | ITF_M | 0.0 | 67 | **QUIET** |
| ITFMATCH-26JUL13TAZHAR | ITF_M | 0.0 | 25 | **QUIET** |
| ITFMATCH-26JUL13URRDRA | ITF_M | 0.0 | 10 | **QUIET** |
| ITFMATCH-26JUL13VRTKLA | ITF_M | 0.0 | 57 | **QUIET** |
| ITFMATCH-26JUL13VULPAO | ITF_M | 0.0 | 32 | **QUIET** |
| ITFWMATCH-26JUL13BOEPOH | ITF_W | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL13BULEVT | ITF_W | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL13GADSVA | ITF_W | 0.0 | 9 | **QUIET** |
| ITFWMATCH-26JUL13IBRVER | ITF_W | 0.0 | 13 | **QUIET** |
| ITFWMATCH-26JUL13KARFER | ITF_W | 0.0 | 18 | **QUIET** |
| ITFWMATCH-26JUL13KMISUC | ITF_W | 0.0 | 49 | **QUIET** |
| ITFWMATCH-26JUL13KUMCHA | ITF_W | 0.0 | 25 | **QUIET** |
| ITFWMATCH-26JUL13LABMAN | ITF_W | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL13LAZREV | ITF_W | 0.0 | 22 | **QUIET** |
| ITFWMATCH-26JUL13MICSEB | ITF_W | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL13MITROM | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL13PETURB | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL13PULWIR | ITF_W | 0.0 | 11 | **QUIET** |
| ITFWMATCH-26JUL13RAJHUT | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL13SCHNDU | ITF_W | 0.0 | 33 | **QUIET** |
| ITFWMATCH-26JUL13SIMMAR | ITF_W | 0.0 | 68 | **QUIET** |
| ITFWMATCH-26JUL13ZABSEV | ITF_W | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL13ZHACOR | ITF_W | 0.0 | 68 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL13BINFUE | ATP_CHALL | 0.133 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13DONWES | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13KRASAL | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13KUZNIJ | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 2 | **WAKING** |
| ATPMATCH-26JUL13COLSKA | ATP_MAIN | 0.133 | 1 | **WAKING** |
| ATPMATCH-26JUL13FAUDAM | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ATPMATCH-26JUL13MARMID | ATP_MAIN | 0.233 | 1 | **WAKING** |
| ATPMATCH-26JUL13PASKRU | ATP_MAIN | 0.267 | 1 | **WAKING** |
| ATPMATCH-26JUL13SANDAN | ATP_MAIN | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL13BARURA | ITF_M | 5.833 | — | **WAKING** |
| ITFMATCH-26JUL13GUNKUZ | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL13HASZAG | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL13HOSSIN | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL13MAYAER | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL13MEHJEF | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL13PIELUE | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL13TIMCAR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL13WITHUE | ITF_M | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13BALHEJ | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13CAKVOZ | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13CEUKRE | ITF_W | 0.033 | 63 | **WAKING** |
| ITFWMATCH-26JUL13DELBRO | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL13FEHKRO | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL13GIZVLA | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13GRORAS | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13IVAKOP | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13KUHSEK | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL13LOLBED | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13MALMOO | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13NAGCHY | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL13SVIART | ITF_W | 0.067 | 7 | **WAKING** |
| ITFWMATCH-26JUL13VELKOR | ITF_W | 0.067 | 6 | **WAKING** |
| ITFWMATCH-26JUL13WIEMON | ITF_W | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13GRABER | WTA_CHALL | 0.1 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13KABPER | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13KHOZHA | WTA_CHALL | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PANFAL | WTA_CHALL | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PAPAND | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PENTHA | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13RADREN | WTA_CHALL | 0.067 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13RISPOH | WTA_CHALL | 0.1 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13SAINUG | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13SHIHUA | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13TIKBEN | WTA_CHALL | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13AMAHER | WTA_MAIN | 1.267 | — | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13AVAFET | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13CRIJEA | WTA_MAIN | 0.033 | 2 | **WAKING** |
| WTAMATCH-26JUL13KAWWAL | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13LIUIPE | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13MONMAS | WTA_MAIN | 0.0 | 3 | **WAKING** |
| WTAMATCH-26JUL13QUERUS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13ROMKUL | WTA_MAIN | 0.233 | 1 | **WAKING** |
| WTAMATCH-26JUL13SHEGAL | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13TIMANN | WTA_MAIN | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.067 | 2 | **WAKING** |

## PATTERNS (sub-B) — 13
- reality_divergence: KXITFMATCH-26JUL13BARURA-URA {"kind": "resting_bid", "ref": 14.0, "market_mid": 44.0, "divergence": -30.0}
- reality_divergence: KXITFMATCH-26JUL13BATSYC-BAT {"kind": "resting_bid", "ref": 49.0, "market_mid": 75.5, "divergence": -26.5}
- reality_divergence: KXITFMATCH-26JUL13HOSSIN-HOS {"kind": "resting_bid", "ref": 51.0, "market_mid": 90.0, "divergence": -39.0}
- reality_divergence: KXITFMATCH-26JUL13LEAMEN-MEN {"kind": "resting_bid", "ref": 12.0, "market_mid": 44.5, "divergence": -32.5}
- reality_divergence: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 11.0, "market_mid": 48.0, "divergence": -37.0}
- reality_divergence: KXITFWMATCH-26JUL13CEUKRE-CEU {"kind": "resting_bid", "ref": 20.0, "market_mid": 53.5, "divergence": -33.5}
- reality_divergence: KXITFWMATCH-26JUL13CEUKRE-KRE {"kind": "resting_bid", "ref": 16.0, "market_mid": 46.0, "divergence": -30.0}
- reality_divergence: KXITFWMATCH-26JUL13ZHACOR-ZHA {"kind": "resting_bid", "ref": 15.0, "market_mid": 49.0, "divergence": -34.0}
- reality_divergence: KXITFMATCH-26JUL13MARVAL-VAL {"kind": "resting_bid", "ref": 35.0, "market_mid": 67.5, "divergence": -32.5, "emitted_et": "2026-07-13 04:04:58 AM ET"}
- reality_divergence: KXITFMATCH-26JUL13SEGKAS-KAS {"kind": "resting_bid", "ref": 16.0, "market_mid": 49.5, "divergence": -33.5, "emitted_et": "2026-07-13 04:04:58 AM ET"}
- reality_divergence: KXITFMATCH-26JUL13TAZHAR-TAZ {"kind": "resting_bid", "ref": 48.0, "market_mid": 76.5, "divergence": -28.5, "emitted_et": "2026-07-13 04:04:58 AM ET"}
- reality_divergence: KXITFMATCH-26JUL13VRTKLA-KLA {"kind": "resting_bid", "ref": 19.0, "market_mid": 47.5, "divergence": -28.5, "emitted_et": "2026-07-13 04:04:58 AM ET"}
- reality_divergence: KXITFWMATCH-26JUL13SIMMAR-SIM {"kind": "resting_bid", "ref": 14.0, "market_mid": 48.0, "divergence": -34.0, "emitted_et": "2026-07-13 04:04:58 AM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
