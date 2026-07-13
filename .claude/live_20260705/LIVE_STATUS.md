# LIVE VALIDATION — rolling status

- cycle 40 @ **2026-07-13 03:34:45 AM ET** | build `e0bea174` | session boot 07-13 01:29 ET | log `live_v3_20260713.jsonl` | 24797 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 11 item(s)
- **half_arm_aging**: KXATPCHALLENGERMATCH-26JUL13YEVCAM-YEV {"fill": 42, "age_min": 119, "mode": "NO_BID(sib rested earlier, none now)"}
- **reality_divergence**: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 8.0, "market_mid": 47.5, "divergence": -39.5}
- **half_arm_aging**: KXWTAMATCH-26JUL13AMAHER-AMA {"fill": 35, "age_min": 95, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- **reality_divergence**: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 9.0, "market_mid": 48.0, "divergence": -39.0}
- **half_arm_aging**: KXATPCHALLENGERMATCH-26JUL13KRASAL-KRA {"fill": 85, "age_min": 69, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- **combined_over_goal_UNVERIFIED_BASIS**: KXATPMATCH-26JUL12FELKEC {"combined": 100, "detail": "pair combined 100c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- **reality_divergence**: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 9.0, "market_mid": 48.0, "divergence": -39.0}
- **reality_divergence**: KXITFMATCH-26JUL13BARURA-BAR {"kind": "resting_bid", "ref": 5.0, "market_mid": 65.5, "divergence": -60.5}
- **reality_divergence**: KXITFMATCH-26JUL13HOSSIN-HOS {"kind": "resting_bid", "ref": 50.0, "market_mid": 90.0, "divergence": -40.0}
- **reality_divergence**: KXITFMATCH-26JUL13LEAMEN-MEN {"kind": "resting_bid", "ref": 12.0, "market_mid": 48.5, "divergence": -36.5}
- **reality_divergence**: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 11.0, "market_mid": 48.0, "divergence": -37.0}
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 29 violation(s)
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
| 02:48:02 | **self_fill_bell** | KXITFWMATCH-26JUL13BOEPOH-POH | own buys rose 17c (52->69) in 1800s -> match-live presumption, entry buys FROZEN |
| 02:53:31 | **self_fill_bell** | KXITFMATCH-26JUL13TIMCAR-TIM | own buys rose 4c (80->84) in 1800s -> match-live presumption, entry buys FROZEN |
| 02:56:44 | **self_fill_bell** | KXITFWMATCH-26JUL13LABMAN-LAB | own buys rose 13c (50->63) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:05:07 | **self_fill_bell** | KXITFMATCH-26JUL13DUTHAI-DUT | own buys rose 4c (49->53) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:05:08 | **self_fill_bell** | KXITFMATCH-26JUL13BATSYC-BAT | own buys rose 12c (49->61) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:05:09 | **self_fill_bell** | KXITFMATCH-26JUL13BENWRI-WRI | own buys rose 4c (51->55) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:05:10 | **self_fill_bell** | KXITFMATCH-26JUL13BARURA-URA | own buys rose 5c (9->14) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:07:18 | **self_fill_bell** | KXITFWMATCH-26JUL13KUMCHA-CHA | own buys rose 4c (14->18) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:09:24 | **self_fill_bell** | KXITFMATCH-26JUL13BERCON-CON | own buys rose 4c (9->13) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:26:15 | **self_fill_bell** | KXITFMATCH-26JUL13URRDRA-URR | own buys rose 4c (57->61) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:27:53 | **self_fill_bell** | KXITFWMATCH-26JUL13IVAKOP-IVA | own buys rose 20c (51->71) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:32:21 | **self_fill_bell** | KXITFWMATCH-26JUL13KARFER-KAR | own buys rose 15c (42->57) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:32:22 | **self_fill_bell** | KXITFWMATCH-26JUL13LAZREV-LAZ | own buys rose 4c (49->53) in 1800s -> match-live presumption, entry buys FROZEN |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_self_fill_bell.md**

## FILLS — 5 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:35 | ATPCHALLENGERMATCH-26JUL13YEVCAM-Y | ATP_CHALL | underdog | 42 | 39 | +3 (place_cell) | — | pre | single |  | PENDING |
| 01:59 | WTAMATCH-26JUL13AMAHER-AMA | WTA_MAIN | underdog | 35 | 34 | +1 (place_cell) | — | pre | single |  | MIXED |
| 02:26 | ATPCHALLENGERMATCH-26JUL13KRASAL-K | ATP_CHALL | leader | 85 | 82 | +3 (place_cell) | — | pre | single |  | PENDING |
| 02:45 | ATPMATCH-26JUL12FELKEC-KEC | ATP_MAIN | leader | 73 | 74 | -1 (place_cell) | — | pre | pair | 100 | PENDING |
| 02:46 | ATPMATCH-26JUL12FELKEC-FEL | ATP_MAIN | ? | 27 | 25 | +2 (place_cell) | — | pre | pair | 100 | PENDING |

## RESTING BIDS — 137 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 37, 'NO_FLOW': 98, 'FLOW_AT_LEVEL': 2} | repriceable now: true 23 / false 114 | **cumulative bid_grade lines: 9017 (repriceable true 1321 / false 7696)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13BINFUE-B | 36 | 124m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13BINFUE-F | 62 | 124m | 0 | 62-64 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13DONWES-D | 25 | 62m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13DONWES-W | 73 | 64m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13KRASAL-S | 12 | 69m | 2/16-19/619 | 17-19 | 4 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL13KUZNIJ-K | 65 | 64m | 0 | 65-68 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13KUZNIJ-N | 32 | 42m | 0 | 32-34 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13PRICRI-C | 8 | 122m | 4/9-10/415 | 9-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ATPCHALLENGERMATCH-26JUL13PRICRI-P | 90 | 94m | 1/91-91/6 | 90-91 | 1 | **FLOW_ABOVE** | 88 | flow above but bound 88c < flow -- chasing breaks goal |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 124m | 1/59-59/32 | 57-59 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ATPMATCH-26JUL12SONSCH-SON | 65 | 124m | 161/68-71/26954 | 69-70 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPMATCH-26JUL13MARMID-MAR | 37 | 89m | 9/38-38/183 | 37-38 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| ATPMATCH-26JUL13MARMID-MID | 62 | 94m | 12/63-63/633 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ATPMATCH-26JUL13PASKRU-KRU | 35 | 34m | 0 | 36-36 | — | **NO_FLOW** | 34 |  |
| ATPMATCH-26JUL13PASKRU-PAS | 64 | 122m | 25/65-65/1463 | 64-65 | 1 | **FLOW_ABOVE** | 65 | REPRICEABLE→65 |
| ATPMATCH-26JUL13SANDAN-DAN | 77 | 4m | 0 | 77-78 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL13SANDAN-SAN | 22 | 4m | 0 | 22-23 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL13TABROD-TAB | 59 | 4m | 2/61-61/80 | 59-60 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ITFMATCH-26JUL13BARURA-URA | 14 | 30m | 10/37-63/58 | 19-40 | 23 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13BATSYC-BAT | 61 | 30m | 0 | 64-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BATSYC-SYC | 12 | 31m | 0 | 12-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BENWRI-BEN | 38 | 31m | 2/44-44/20 | 39-44 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13BENWRI-WRI | 55 | 30m | 0 | 55-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERPIA-BER | 83 | 27m | 0 | 83-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERPIA-PIA | 9 | 27m | 0 | 9-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERWAL-BER | 68 | 118m | 0 | 69-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BERWAL-WAL | 22 | 118m | 0 | 24-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13BRIDUB-DUB | 24 | 104m | 1/53-53/7 | 24-51 | 29 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13CASMOL-CAS | 81 | 27m | 0 | 81-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DUHGAT-DUH | 54 | 122m | 12/60-73/580 | 59-62 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13DUHGAT-GAT | 27 | 122m | 4/40-49/357 | 35-40 | 13 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13DUTHAI-DUT | 53 | 30m | 0 | 53-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DUTHAI-HAI | 5 | 31m | 0 | 8-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GARCIO-CIO | 21 | 38m | 0 | 21-27 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GARCIO-GAR | 72 | 41m | 0 | 72-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GUNKUZ-GUN | 33 | 31m | 0 | 33-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13GUNKUZ-KUZ | 59 | 17m | 0 | 59-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HASZAG-HAS | 75 | 122m | 0 | 86-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HOSSIN-HOS | 51 | 5m | 0 | 88-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13HOSSIN-SIN | 7 | 29m | 0 | 7-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13LEAMEN-MEN | 12 | 31m | 0 | 12-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MAYAER-AER | 40 | 45m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MAYAER-MAY | 56 | 97m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MCHAND-AND | 11 | 42m | 0 | 11-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MEHJEF-JEF | 80 | 38m | 0 | 80-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13MEHJEF-MEH | 15 | 41m | 0 | 15-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13PIELUE-LUE | 61 | 17m | 0 | 61-70 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13PIELUE-PIE | 30 | 31m | 0 | 30-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SARANG-SAR | 24 | 122m | 0 | 26-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SARBOV-BOV | 28 | 104m | 11/40-50/328 | 40-40 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13TIMCAR-CAR | 9 | 56m | 0 | 9-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13TIMCAR-TIM | 84 | 41m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13URRDRA-DRA | 15 | 31m | 0 | 15-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13URRDRA-URR | 61 | 9m | 0 | 62-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13VULPAO-VUL | 52 | 41m | 0 | 52-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13WITHUE-WIT | 87 | 11m | 0 | 87-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BOEPOH-BOE | 13 | 64m | 0 | 16-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BOEPOH-POH | 69 | 47m | 0 | 76-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BULEVT-BUL | 59 | 92m | 0 | 75-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BULEVT-EVT | 15 | 94m | 0 | 16-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13CAKVOZ-VOZ | 25 | 122m | 0 | 25-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13DELBRO-BRO | 61 | 6m | 0 | 61-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13DELBRO-DEL | 36 | 89m | 0 | 36-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13FEHKRO-FEH | 10 | 6m | 0 | 10-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13FEHKRO-KRO | 87 | 78m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IBRVER-IBR | 21 | 119m | 0 | 23-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IBRVER-VER | 55 | 118m | 0 | 62-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13IVAKOP-IVA | 71 | 7m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KARFER-FER | 24 | 4m | 0 | 25-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KARFER-KAR | 57 | 2m | 0 | 57-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUHSEK-KUH | 72 | 92m | 0 | 72-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUHSEK-SEK | 14 | 94m | 0 | 22-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUMCHA-CHA | 18 | 27m | 0 | 20-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13KUMCHA-KUM | 52 | 29m | 0 | 54-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LABMAN-MAN | 26 | 122m | 0 | 28-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LAZREV-LAZ | 53 | 2m | 0 | 53-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LAZREV-REV | 17 | 4m | 0 | 24-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LOLBED-LOL | 91 | 94m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MAL | 79 | 122m | 0 | 79-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MALMOO-MOO | 13 | 122m | 0 | 16-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MICSEB-SEB | 67 | 124m | 0 | 70-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MITROM-MIT | 28 | 94m | 0 | 29-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13MITROM-ROM | 64 | 92m | 0 | 64-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PETURB-PET | 57 | 25m | 0 | 57-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13PETURB-URB | 36 | 92m | 0 | 36-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RAJHUT-HUT | 18 | 94m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RAJHUT-RAJ | 74 | 92m | 0 | 74-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-NDU | 14 | 1m | 0 | 15-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SCHNDU-SCH | 51 | 118m | 0 | 51-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SVIART-SVI | 22 | 122m | 8/26-29/92 | 22-27 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFWMATCH-26JUL13VELKOR-KOR | 64 | 124m | 0 | 64-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13VELKOR-VEL | 25 | 124m | 5/35-35/57 | 27-35 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13WIEMON-WIE | 94 | 31m | 0 | 94-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZABSEV-SEV | 63 | 94m | 0 | 63-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZABSEV-ZAB | 27 | 32m | 0 | 27-36 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13GRABER-B | 20 | 122m | 1/21-21/8 | 20-21 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| WTACHALLENGERMATCH-26JUL13GRABER-G | 78 | 63m | 2/80-80/7 | 79-80 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| WTACHALLENGERMATCH-26JUL13KABPER-K | 72 | 64m | 0 | 72-74 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13KABPER-P | 26 | 64m | 0 | 26-28 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13KHOZHA-K | 82 | 63m | 0 | 82-84 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13KHOZHA-Z | 16 | 94m | 0 | 16-17 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PANFAL-F | 54 | 89m | 0 | 54-56 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PANFAL-P | 43 | 89m | 2/45-45/45 | 43-45 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| WTACHALLENGERMATCH-26JUL13PAPAND-A | 78 | 114m | 5/78-79/137 | 78-79 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PAPAND-P | 22 | 122m | 5/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| WTACHALLENGERMATCH-26JUL13PENTHA-P | 76 | 4m | 0 | 76-77 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13PENTHA-T | 23 | 4m | 0 | 23-24 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 83 | 122m | 3/85-85/5 | 84-85 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| WTACHALLENGERMATCH-26JUL13RADREN-R | 15 | 122m | 1/16-16/15 | 15-16 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→16 |
| WTACHALLENGERMATCH-26JUL13RISPOH-P | 53 | 64m | 0 | 53-54 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13RISPOH-R | 46 | 7m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13SAINUG-N | 66 | 4m | 0 | 66-67 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13SAINUG-S | 32 | 4m | 0 | 32-34 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL13SHIHUA-H | 65 | 94m | 1/66-66/20 | 65-66 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| WTACHALLENGERMATCH-26JUL13SHIHUA-S | 33 | 94m | 4/33-33/272 | 33-34 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTAMATCH-26JUL13AMAHER-HER | 62 | 95m | 72/64-66/3139 | 65-65 | 2 | **FLOW_ABOVE** | 62 | flow above but bound 62c < flow -- chasing breaks goal |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 110m | 1/49-49/5 | 48-49 | 1 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| WTAMATCH-26JUL13AVAFET-AVA | 91 | 60m | 2/93-93/294 | 91-92 | 2 | **FLOW_ABOVE** | 92 | REPRICEABLE→92 |
| WTAMATCH-26JUL13AVAFET-FET | 8 | 124m | 10/9-9/366 | 8-9 | 1 | **FLOW_ABOVE** | 7 | flow above but bound 7c < flow -- chasing breaks goal |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 115m | 1/61-61/15 | 59-61 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 34m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13CRIJEA-CRI | 64 | 124m | 5/65-65/412 | 64-65 | 1 | **FLOW_ABOVE** | 65 | REPRICEABLE→65 |
| WTAMATCH-26JUL13CRIJEA-JEA | 34 | 34m | 0 | 34-35 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KAWWAL-KAW | 31 | 34m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KAWWAL-WAL | 67 | 122m | 2/69-69/15 | 67-69 | 2 | **FLOW_ABOVE** | 69 | REPRICEABLE→69 |
| WTAMATCH-26JUL13KRETOM-KRE | 88 | 124m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13LIUIPE-IPE | 19 | 43m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13LIUIPE-LIU | 80 | 4m | 0 | 80-81 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13MONMAS-MAS | 81 | 122m | 0 | 81-84 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13QUERUS-QUE | 28 | 34m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13QUERUS-RUS | 69 | 110m | 2/72-72/14 | 69-72 | 3 | **FLOW_ABOVE** | 72 | REPRICEABLE→72 |
| WTAMATCH-26JUL13ROMKUL-KUL | 23 | 76m | 1/24-24/0 | 23-24 | 1 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| WTAMATCH-26JUL13ROMKUL-ROM | 76 | 64m | 5/77-77/97 | 76-77 | 1 | **FLOW_ABOVE** | 77 | REPRICEABLE→77 |
| WTAMATCH-26JUL13SHEGAL-GAL | 37 | 34m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13SHEGAL-SHE | 57 | 124m | 3/62-62/31 | 61-62 | 5 | **FLOW_ABOVE** | 62 |  |
| WTAMATCH-26JUL13TIMANN-ANN | 58 | 124m | 2/60-60/18 | 58-60 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| WTAMATCH-26JUL13VALCOS-VAL | 81 | 122m | 2/85-85/20 | 81-85 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTAMATCH-26JUL13AMAHER | 35 | 65 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL13KRASAL | 85 | 19 | **104** | 97 | +7 |

## FLOW-STATE — 84 tracked game(s) ({'WAKING': 54, 'OPEN': 3, 'QUIET': 27}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL12SONSCH | ATP_MAIN | 0.833 | 1 | **OPEN** |
| ATPMATCH-26JUL13TABROD | ATP_MAIN | 0.733 | 1 | **OPEN** |
| ITFMATCH-26JUL13DUHGAT | ITF_M | 0.2 | 3 | **OPEN** |
| ITFMATCH-26JUL13BATSYC | ITF_M | 0.0 | 23 | **QUIET** |
| ITFMATCH-26JUL13BERPIA | ITF_M | 0.0 | 8 | **QUIET** |
| ITFMATCH-26JUL13BERWAL | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13BRIDUB | ITF_M | 0.0 | 27 | **QUIET** |
| ITFMATCH-26JUL13CASMOL | ITF_M | 0.0 | 7 | **QUIET** |
| ITFMATCH-26JUL13DUTHAI | ITF_M | 0.0 | 38 | **QUIET** |
| ITFMATCH-26JUL13GARCIO | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL13GUNKUZ | ITF_M | 0.0 | 7 | **QUIET** |
| ITFMATCH-26JUL13LEAMEN | ITF_M | 0.0 | 69 | **QUIET** |
| ITFMATCH-26JUL13MCHAND | ITF_M | 0.0 | 74 | **QUIET** |
| ITFMATCH-26JUL13PIELUE | ITF_M | 0.0 | 8 | **QUIET** |
| ITFMATCH-26JUL13SARANG | ITF_M | 0.0 | 29 | **QUIET** |
| ITFMATCH-26JUL13URRDRA | ITF_M | 0.0 | 22 | **QUIET** |
| ITFMATCH-26JUL13VULPAO | ITF_M | 0.0 | 31 | **QUIET** |
| ITFWMATCH-26JUL13BOEPOH | ITF_W | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL13BULEVT | ITF_W | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL13IBRVER | ITF_W | 0.0 | 14 | **QUIET** |
| ITFWMATCH-26JUL13KARFER | ITF_W | 0.0 | 17 | **QUIET** |
| ITFWMATCH-26JUL13KUMCHA | ITF_W | 0.0 | 25 | **QUIET** |
| ITFWMATCH-26JUL13LABMAN | ITF_W | 0.0 | 8 | **QUIET** |
| ITFWMATCH-26JUL13LAZREV | ITF_W | 0.0 | 22 | **QUIET** |
| ITFWMATCH-26JUL13MICSEB | ITF_W | 0.0 | 9 | **QUIET** |
| ITFWMATCH-26JUL13MITROM | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL13PETURB | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL13RAJHUT | ITF_W | 0.0 | 6 | **QUIET** |
| ITFWMATCH-26JUL13SCHNDU | ITF_W | 0.0 | 33 | **QUIET** |
| ITFWMATCH-26JUL13ZABSEV | ITF_W | 0.0 | 9 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL13BINFUE | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13DONWES | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13KRASAL | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13KUZNIJ | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13PRICRI | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL13YEVCAM | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 2 | **WAKING** |
| ATPMATCH-26JUL12FELKEC | ATP_MAIN | 0.467 | 1 | **WAKING** |
| ATPMATCH-26JUL13MARMID | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ATPMATCH-26JUL13PASKRU | ATP_MAIN | 0.033 | 1 | **WAKING** |
| ATPMATCH-26JUL13SANDAN | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL13BARURA | ITF_M | 0.4 | 21 | **WAKING** |
| ITFMATCH-26JUL13BENWRI | ITF_M | 0.067 | 5 | **WAKING** |
| ITFMATCH-26JUL13HASZAG | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL13HOSSIN | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL13MAYAER | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL13MEHJEF | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL13SARBOV | ITF_M | 0.033 | — | **WAKING** |
| ITFMATCH-26JUL13TIMCAR | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL13WITHUE | ITF_M | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13CAKVOZ | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13DELBRO | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL13FEHKRO | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL13IVAKOP | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13KUHSEK | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13LOLBED | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13MALMOO | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SVIART | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13VELKOR | ITF_W | 0.067 | 8 | **WAKING** |
| ITFWMATCH-26JUL13WIEMON | ITF_W | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13GRABER | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13KABPER | WTA_CHALL | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13KHOZHA | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PANFAL | WTA_CHALL | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PAPAND | WTA_CHALL | 0.133 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13PENTHA | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13RADREN | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13RISPOH | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13SAINUG | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL13SHIHUA | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13AMAHER | WTA_MAIN | 1.033 | — | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13AVAFET | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13CRIJEA | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13KAWWAL | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13LIUIPE | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13MONMAS | WTA_MAIN | 0.0 | 3 | **WAKING** |
| WTAMATCH-26JUL13QUERUS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13ROMKUL | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13SHEGAL | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13TIMANN | WTA_MAIN | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.067 | 4 | **WAKING** |

## PATTERNS (sub-B) — 11
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL13YEVCAM-YEV {"fill": 42, "age_min": 119, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 8.0, "market_mid": 47.5, "divergence": -39.5}
- half_arm_aging: KXWTAMATCH-26JUL13AMAHER-AMA {"fill": 35, "age_min": 95, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- reality_divergence: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 9.0, "market_mid": 48.0, "divergence": -39.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL13KRASAL-KRA {"fill": 85, "age_min": 69, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPMATCH-26JUL12FELKEC {"combined": 100, "detail": "pair combined 100c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- reality_divergence: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 9.0, "market_mid": 48.0, "divergence": -39.0}
- reality_divergence: KXITFMATCH-26JUL13BARURA-BAR {"kind": "resting_bid", "ref": 5.0, "market_mid": 65.5, "divergence": -60.5}
- reality_divergence: KXITFMATCH-26JUL13HOSSIN-HOS {"kind": "resting_bid", "ref": 50.0, "market_mid": 90.0, "divergence": -40.0}
- reality_divergence: KXITFMATCH-26JUL13LEAMEN-MEN {"kind": "resting_bid", "ref": 12.0, "market_mid": 48.5, "divergence": -36.5}
- reality_divergence: KXITFMATCH-26JUL13MCHAND-AND {"kind": "resting_bid", "ref": 11.0, "market_mid": 48.0, "divergence": -37.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
