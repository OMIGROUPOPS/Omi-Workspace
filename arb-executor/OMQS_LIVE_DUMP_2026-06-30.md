# OMQS LIVE GROUND-TRUTH DUMP — 2026-06-30

Source: authoritative Kalshi REST (/portfolio/balance,positions,fills,orders,settlements; /markets book) + live_v3_20260630.jsonl order-event log. Generated 2026-06-30 19:01:57 UTC. All times ET. Prices in cents (yes terms).

## (1) ACCOUNT
| metric | value |
|---|---|
| balance (cash) | $2475.72 |
| portfolio mark (open) | $30.03 |
| **total equity now** | **$2505.75** |
| this-morning baseline (first snapshot ~11:00 ET) | $2524.61 |
| **delta today** | **$-18.86** |
| realized from settlements settled today (payout-basis-fee), n=230 | $99.49 |
| exit-fill proceeds today (gross, n=198 sell fills) | $514.57 |
| unrealized on open (mark-basis), n=14 | $3.95 |

## (2) OPEN POSITIONS (14)
| ticker | player | side | entry | entry_ts ET | tts@entry | cur_bid | cur_ask | book_status | exit_order | unrl$ |
|---|---|---|---|---|---|---|---|---|---|---|
| KXATPCHALLENGERMATCH-26JUN29MBISOT-SOT | Matias Soto | YES | n/a | n/a | ? | None | None | active | None | +4.35 |
| KXATPCHALLENGERMATCH-26JUN30DEHER-HER | Samuel Heredia | YES | 28 | 13:18:08 | T-432m | None | None | active | None | -0.00 |
| KXATPCHALLENGERMATCH-26JUN30LAHER-HER | Alex Hernandez | YES | 28 | 13:41:27 | T-259m | None | None | active | None | +0.00 |
| KXATPCHALLENGERMATCH-26JUN30LEGBIC-BIC | Blaise Bicknell | YES | 51 | 13:18:01 | T-462m | None | None | active | None | -0.00 |
| KXATPCHALLENGERMATCH-26JUN30NOGMAR-MAR | Alex Martinez | YES | 35 | 14:49:23 | T-161m | None | None | active | None | +0.00 |
| KXATPCHALLENGERMATCH-26JUN30SAKLER-LER | Jules Leroux | YES | 7 | 14:41:30 | T-378m | None | None | active | None | -0.00 |
| KXATPMATCH-26JUN29MOLALT-ALT | Daniel Altmaier | YES | 54 | 08:37:08 | T-203m | None | None | active | None | +0.00 |
| KXATPMATCH-26JUN29NAVCOB-COB | Flavio Cobolli | YES | 78 | 10:31:54 | T+32m | None | None | active | None | +0.00 |
| KXATPMATCH-26JUN29TIAATM-TIA | Frances Tiafoe | YES | 80 | 08:29:41 | T-90m | None | None | active | None | +0.00 |
| KXATPMATCH-26JUN29WAWBER-BER | Matteo Berrettini | YES | 80 | 12:34:07 | T+34m | None | None | active | None | +0.00 |
| KXATPMATCH-26JUN29WAWBER-WAW | Stan Wawrinka | YES | 20 | 11:08:10 | T-52m | None | None | active | exit-filled | -0.40 |
| KXITFMATCH-26JUN30HASREN-REN | Henry Ren | YES | 35 | 13:50:40 | T-309m | None | None | active | None | +0.00 |
| KXWTAMATCH-26JUN29OSOWAL-WAL | Simona Waltert | YES | 36 | 14:13:06 | ? | None | None | active | None | +0.00 |
| KXWTAMATCH-26JUN29WILJOI-JOI | Maya Joint | YES | 53 | 10:40:29 | T-110m | None | None | active | None | +0.00 |

## (4) SETTLED LOSERS TODAY
| ticker | player | entry | tts@fill | is_taker | exit_filled | settled_pnl_c |
|---|---|---|---|---|---|---|
| KXWTAMATCH-26JUN30TOMBOL-TOM | Ajla Tomljanovic | 86 | T-181m | False | N | -431 |
| KXATPMATCH-26JUN29VIRSHE-SHE | Ben Shelton | 82 | T-131m | False | N | -411 |
| KXATPMATCH-26JUN29MUNCER-CER | Francisco Cerundolo | 77 | T-62m | False | N | -387 |
| KXATPCHALLENGERMATCH-26JUN30CREWAL-CRE | CRE | 75 | T-46m | False | N | -375 |
| KXWTAMATCH-26JUN30SVISNI-SVI | Elina Svitolina | 74 | T-360m | False | N | -372 |
| KXATPCHALLENGERMATCH-26JUN30RIBRAP-RIB | Michele Ribecai | 74 | T-188m | False | N | -370 |
| KXWTAMATCH-26JUN29BOUGRA-BOU | Katie Boulter | 72 | T-92m | False | N | -362 |
| KXATPMATCH-26JUN29KYPMCD-MCD | Mackenzie McDonald | 71 | T+60m | False | N | -357 |
| KXATPCHALLENGERMATCH-26JUN30ERHROD-ROD | Jurij Rodionov | 70 | T-217m | False | N | -350 |
| KXATPCHALLENGERMATCH-26JUN30MAEMIL-MAE | Francesco Maestrelli | 69 | T-377m | False | N | -345 |
| KXITFMATCH-26JUN30VETRET-VET | Miha Vetrih | 68 | T-264m | False | N | -340 |
| KXATPMATCH-26JUN29GRIDUC-GRI | Tallon Griekspoor | 67 | T-74m | False | N | -337 |
| KXWTAMATCH-26JUN29SAKTAU-TAU | Clara Tauson | 65 | T-215m | False | N | -327 |
| KXATPCHALLENGERMATCH-26JUN30BRABAS-BAS | Nikoloz Basilashvili | 64 | T-206m | False | N | -320 |
| KXATPCHALLENGERMATCH-26JUN30MENABO-MEN | Facundo Mena | 62 | T-221m | False | N | -310 |
| KXATPCHALLENGERMATCH-26JUN30MCDMAR-MCD | Niels McDonald | 61 | T-220m | False | N | -305 |
| KXATPMATCH-26JUN29KOPCHO-KOP | Vit Kopriva | 59 | T+124m | False | N | -297 |
| KXATPCHALLENGERMATCH-26JUN30JORPRA-PRA | Juan Carlos Prado Angelo | 55 | T-191m | False | N | -275 |
| KXWTAMATCH-26JUN29SELKRA-KRA | Sinja Kraus | 53 | T-17m | False | N | -267 |
| KXATPCHALLENGERMATCH-26JUN30WINFEN-FEN | Andrew Fenty | 53 | T-158m | False | N | -265 |
| KXWTAMATCH-26JUN29BEGSWA-BEG | Irina-Camelia Begu | 50 | T+4m | False | N | -252 |
| KXATPCHALLENGERMATCH-26JUN30OSOBER-BER | Peter Bertran | 50 | T-100m | False | N | -250 |
| KXATPMATCH-26JUN29SONETC-ETC | Tomas Martin Etcheverry | 47 | T-60m | False | N | -237 |
| KXATPCHALLENGERMATCH-26JUN30GOMMON-GOM | Juan Sebastian Gomez | 47 | T-221m | False | N | -235 |
| KXATPCHALLENGERMATCH-26JUN30MATHEM-MAT | Anton Matusevich | 39 | T-170m | False | N | -195 |
| KXATPMATCH-26JUN29MANDRO-DRO | Titouan Droguet | 36 | T-193m | False | N | -182 |
| KXATPMATCH-26JUN29MAJTAB-TAB | Alejandro Tabilo | 33 | T-162m | False | N | -167 |
| KXATPMATCH-26JUN29JACGAU-GAU | Vilius Gaubas | 30 | T+108m | False | N | -152 |
| KXWTAMATCH-26JUN29HADTIM-HAD | Beatriz Haddad Maia | 30 | T-16m | False | N | -152 |
| KXATPMATCH-26JUN30LLASVA-LLA | Pablo Llamas Ruiz | 29 | T-287m | False | N | -147 |
| KXATPCHALLENGERMATCH-26JUN30CANALM-ALM | Izan Almazan Valiente | 28 | T-147m | False | N | -140 |
| KXITFMATCH-26JUN30MABPAL-PAL | Arin Pallegar | 27 | T-274m | False | N | -135 |
| KXATPCHALLENGERMATCH-26JUN30ALBPIR-ALB | Radu Albot | 26 | T-200m | False | N | -130 |
| KXWTAMATCH-26JUN29MERSIE-SIE | Laura Siegemund | 24 | T+84m | False | N | -122 |
| KXATPCHALLENGERMATCH-26JUN30FELPIE-PIE | Samuele Pieri | 22 | T-184m | False | N | -110 |
| KXATPCHALLENGERMATCH-26JUN30COMDON-DON | Matthew William Donald | 18 | T-201m | False | N | -90 |
| KXITFWMATCH-26JUN30POLTVE-POL | Adela Polakovicova | 18 | T-256m | False | N | -90 |
| KXATPCHALLENGERMATCH-26JUN30DIATOB-TOB | Miguel Tobon | 16 | T-190m | False | N | -80 |
| KXWTAMATCH-26JUN29EALZAR-ZAR | Renata Zarazua | 14 | T+6m | False | N | -71 |
| KXWTAMATCH-26JUN29SEINOS-SEI | Ella Seidel | 10 | T-37m | False | N | -51 |
| KXATPMATCH-26JUN30FRILAJ-LAJ | Dusan Lajovic | 6 | T-419m | False | N | -30 |
| KXWTAMATCH-26JUN29ANIGJO-GJO | Lina Gjorcheska | 6 | T+9m | False | N | -30 |
| KXITFWMATCH-26JUN30BOYMIT-MIT | Nora Mitrea Gerocz | 6 | T-255m | False | N | -30 |
| KXITFWMATCH-26JUN30ERCPAN-ERC | Melisa Ercan | 98 | T-266m | False | Y | +0 |

**losers: n=44, sum=-9881c ($-98.81). taker=True count: 0. exit_filled=Y count: 1.**

## (5) GUN-CANCEL EVIDENCE
### match_live_resting_cancel + match_live_detected events today
| ts ET | ticker | event | detail |
|---|---|---|---|
| 04:49:27 |  | match_live_detected | {"event": "KXITFWMATCH-26JUN30ERCPAN", "trades_in_window": 10, "window_sec": 60, "signal": "volume_burst", "stage1_age_sec": 165.9, "tts_min": 25.5} |
| 14:20:28 | KXATPMATCH-26JUN29KOPCHO-CHO | match_live_resting_cancel | {"event": "KXATPMATCH-26JUN29KOPCHO", "graced": true, "window_counts": [51, 21, 26], "sustained_window_start_ts": 1782843447.3647993} |

### order cancels today with match/buffer/live reasons
| ts ET | ticker | reason | ok |
|---|---|---|---|
| 03:40:16 | KXITFWMATCH-26JUN30BOYMIT-BOY | v4_t20m_fallback | True |
| 03:42:12 | KXATPCHALLENGERMATCH-26JUN30MOELEC-MOE | v4_t20m_fallback | True |
| 03:42:12 | KXATPCHALLENGERMATCH-26JUN30TOPRAQ-RAQ | v4_t20m_fallback | True |
| 03:42:14 | KXATPCHALLENGERMATCH-26JUN30ERHROD-ERH | v4_t20m_fallback | True |
| 03:42:14 | KXITFWMATCH-26JUN30POLTVE-POL | v4_t20m_fallback | True |
| 03:42:15 | KXITFWMATCH-26JUN30BOYMIT-MIT | v4_t20m_fallback | True |
| 03:46:35 | KXITFWMATCH-26JUN30BOYMIT-BOY | v4_t20m_fallback | True |
| 03:51:37 | KXATPCHALLENGERMATCH-26JUN30MOELEC-LEC | v4_t20m_fallback | True |
| 04:10:09 | KXITFMATCH-26JUN30CASBLA-BLA | v4_t20m_fallback | True |
| 04:10:24 | KXITFWMATCH-26JUN29BOEVAS-VAS | v4_t20m_fallback | True |
| 04:40:13 | KXATPCHALLENGERMATCH-26JUN30ALBPIR-ALB | v4_t20m_fallback | True |
| 04:55:55 | KXITFMATCH-26JUN30SOOKUR-SOO | v4_t20m_fallback | True |
| 04:56:00 | KXITFMATCH-26JUN30SOOKUR-KUR | v4_t20m_fallback | True |
| 04:56:05 | KXITFMATCH-26JUN30SOOKUR-SOO | v4_t20m_fallback | True |
| 04:56:07 | KXITFMATCH-26JUN30SOOKUR-KUR | v4_t20m_fallback | True |
| 04:57:15 | KXITFMATCH-26JUN30SOOKUR-SOO | v4_t20m_fallback | True |
| 04:58:31 | KXITFMATCH-26JUN30SOOKUR-SOO | v4_t20m_fallback | True |
| 04:59:51 | KXITFMATCH-26JUN30SOOKUR-SOO | v4_t20m_fallback | True |
| 05:10:36 | KXATPCHALLENGERMATCH-26JUN30FELPIE-PIE | v4_t20m_fallback | True |
| 05:11:26 | KXATPCHALLENGERMATCH-26JUN30FELPIE-FEL | v4_t20m_fallback | True |
| 05:11:27 | KXATPCHALLENGERMATCH-26JUN30COMDON-DON | v4_t20m_fallback | True |
| 05:11:27 | KXATPCHALLENGERMATCH-26JUN30DIATOB-DIA | v4_t20m_fallback | True |
| 05:11:27 | KXATPCHALLENGERMATCH-26JUN30DIATOB-TOB | v4_t20m_fallback | True |
| 05:11:28 | KXATPCHALLENGERMATCH-26JUN30COMDON-COM | v4_t20m_fallback | True |
| 05:41:08 | KXATPMATCH-26JUN29MAJTAB-MAJ | v4_t20m_fallback | True |
| 05:41:09 | KXWTAMATCH-26JUN29KALRAK-RAK | v4_t20m_fallback | True |
| 05:41:09 | KXWTAMATCH-26JUN29ANIGJO-ANI | v4_t20m_fallback | True |
| 05:41:10 | KXWTAMATCH-26JUN29BEGSWA-SWA | v4_t20m_fallback | True |
| 05:41:10 | KXWTAMATCH-26JUN29DAYKEY-KEY | v4_t20m_fallback | True |
| 05:41:11 | KXWTAMATCH-26JUN29BOUGRA-GRA | v4_t20m_fallback | True |
| 05:41:11 | KXWTAMATCH-26JUN29GIBBOU-BOU | v4_t20m_fallback | True |
| 05:41:12 | KXWTAMATCH-26JUN29PAOMON-PAO | v4_t20m_fallback | True |
| 05:41:12 | KXWTAMATCH-26JUN29MARKEN-KEN | v4_t20m_fallback | True |
| 05:41:13 | KXATPMATCH-26JUN29SHIFAR-SHI | v4_t20m_fallback | True |
| 05:41:13 | KXATPMATCH-26JUN29ROYWEN-WEN | v4_t20m_fallback | True |
| 05:41:14 | KXWTAMATCH-26JUN29BEGSWA-BEG | v4_t20m_fallback | True |
| 05:46:08 | KXWTAMATCH-26JUN29GIBBOU-BOU | v4_t20m_fallback | True |
| 05:57:41 | KXWTAMATCH-26JUN29VALPLI-PLI | v4_t20m_fallback | True |
| 06:11:51 | KXATPCHALLENGERMATCH-26JUN30PAVSAN-SAN | v4_t20m_fallback | True |
| 06:11:52 | KXATPCHALLENGERMATCH-26JUN30PAVSAN-SAN | v4_t20m_fallback | True |
| 06:17:56 | KXATPCHALLENGERMATCH-26JUN30PAVSAN-SAN | v4_t20m_fallback | True |
| 06:28:31 | KXATPCHALLENGERMATCH-26JUN30PAVSAN-SAN | v4_t20m_fallback | True |
| 06:41:06 | KXATPCHALLENGERMATCH-26JUN30BONMON-BON | v4_t20m_fallback | True |
| 06:42:09 | KXATPCHALLENGERMATCH-26JUN30RIBRAP-RIB | v4_t20m_fallback | True |
| 06:42:09 | KXATPCHALLENGERMATCH-26JUN30RIBRAP-RAP | v4_t20m_fallback | True |
| 06:42:10 | KXATPCHALLENGERMATCH-26JUN30BRABAS-BRA | v4_t20m_fallback | True |
| 06:42:10 | KXATPCHALLENGERMATCH-26JUN30CREWAL-CRE | v4_t20m_fallback | True |
| 06:42:11 | KXATPCHALLENGERMATCH-26JUN30CREWAL-WAL | v4_t20m_fallback | True |
| 07:11:29 | KXATPMATCH-26JUN29MICFEA-MIC | v4_t20m_fallback | True |
| 07:11:30 | KXATPMATCH-26JUN29JACGAU-GAU | v4_t20m_fallback | True |
| 07:11:31 | KXATPMATCH-26JUN29DZUFER-FER | v4_t20m_fallback | True |
| 07:21:26 | KXATPMATCH-26JUN29MICFEA-MIC | v4_t20m_fallback | True |
| 07:21:31 | KXWTAMATCH-26JUN29HADTIM-TIM | v4_t20m_fallback | True |
| 07:21:36 | KXWTAMATCH-26JUN29HADTIM-HAD | v4_t20m_fallback | True |
| 07:42:13 | KXATPMATCH-26JUN29MUNCER-MUN | v4_t20m_fallback | True |
| 07:42:13 | KXWTAMATCH-26JUN29SHYGOL-GOL | v4_t20m_fallback | True |
| 07:42:14 | KXWTAMATCH-26JUN29BIRKOR-BIR | v4_t20m_fallback | True |
| 07:42:15 | KXWTAMATCH-26JUN29BIRKOR-BIR | v4_t20m_fallback | True |
| 07:47:17 | KXWTAMATCH-26JUN29BIRKOR-BIR | v4_t20m_fallback | True |
| 08:10:20 | KXATPCHALLENGERMATCH-26JUN30CANALM-ALM | v4_t20m_fallback | True |
| 08:10:22 | KXWTAMATCH-26JUN29TOWSWI-SWI | v4_t20m_fallback | True |
| 08:12:36 | KXATPCHALLENGERMATCH-26JUN30CANALM-ALM | v4_t20m_fallback | True |
| 09:10:43 | KXWTAMATCH-26JUN29STABLI-BLI | v4_t20m_fallback | True |
| 09:10:44 | KXWTAMATCH-26JUN30ERJJEA-ERJ | v4_t20m_fallback | True |
| 09:10:48 | KXWTAMATCH-26JUN29SELKRA-KRA | v4_t20m_fallback | True |
| 09:10:50 | KXATPMATCH-26JUN29SONETC-SON | v4_t20m_fallback | True |
| 09:10:51 | KXATPMATCH-26JUN29KYPMCD-KYP | v4_t20m_fallback | True |
| 09:10:52 | KXWTAMATCH-26JUN29SELKRA-SEL | v4_t20m_fallback | True |
| 09:10:54 | KXATPMATCH-26JUN29KHAHAR-HAR | v4_t20m_fallback | True |
| 09:10:57 | KXATPMATCH-26JUN29COLFIL-FIL | v4_t20m_fallback | True |
| 09:10:58 | KXATPMATCH-26JUN29COLFIL-COL | v4_t20m_fallback | True |
| 09:10:59 | KXWTAMATCH-26JUN30SVISNI-SNI | v4_t20m_fallback | True |
| 09:11:00 | KXATPMATCH-26JUN29MOUGIR-GIR | v4_t20m_fallback | True |
| 09:11:51 | KXWTAMATCH-26JUN29STABLI-BLI | v4_t20m_fallback | True |
| 09:11:53 | KXATPMATCH-26JUN29MOUGIR-GIR | v4_t20m_fallback | True |
| 09:29:45 | KXATPMATCH-26JUN29KHAHAR-HAR | v4_t20m_fallback | True |
| 09:41:31 | KXWTAMATCH-26JUN29CIRBEJ-CIR | v4_t20m_fallback | True |
| 09:41:32 | KXWTAMATCH-26JUN29RUSMCC-MCC | v4_t20m_fallback | True |
| 09:41:34 | KXATPMATCH-26JUN29BLOZVE-ZVE | v4_t20m_fallback | True |
| 09:41:35 | KXWTAMATCH-26JUN29MERSIE-MER | v4_t20m_fallback | True |
| 09:41:36 | KXWTAMATCH-26JUN29BOIRYB-RYB | v4_t20m_fallback | True |
| 10:00:05 | KXATPCHALLENGERMATCH-26JUN30MOLGOM-GOM | v4_t20m_fallback | True |
| 10:01:51 | KXATPCHALLENGERMATCH-26JUN30MOLGOM-GOM | v4_t20m_fallback | True |
| 10:08:25 | KXATPCHALLENGERMATCH-26JUN30MOLGOM-GOM | v4_t20m_fallback | True |
| 10:10:20 | KXATPCHALLENGERMATCH-26JUN30ROCBAS-BAS | v4_t20m_fallback | True |
| 10:40:31 | KXATPMATCH-26JUN29GRIDUC-DUC | v4_t20m_fallback | True |
| 10:40:31 | KXATPMATCH-26JUN29NAVCOB-NAV | v4_t20m_fallback | True |
| 10:40:32 | KXATPMATCH-26JUN29TIAATM-ATM | v4_t20m_fallback | True |
| 10:40:32 | KXATPMATCH-26JUN29KOPCHO-KOP | v4_t20m_fallback | True |
| 10:40:33 | KXATPCHALLENGERMATCH-26JUN30MENABO-ABO | v4_t20m_fallback | True |
| 11:10:47 | KXWTAMATCH-26JUN29KUDSAM-KUD | v4_t20m_fallback | True |
| 11:10:48 | KXATPMATCH-26JUN29WAWBER-BER | v4_t20m_fallback | True |
| 11:10:49 | KXWTAMATCH-26JUN29OSOWAL-WAL | v4_t20m_fallback | True |
| 11:10:49 | KXWTAMATCH-26JUN29SHNLYS-LYS | v4_t20m_fallback | True |
| 11:10:50 | KXATPMATCH-26JUN29LEHPOP-POP | v4_t20m_fallback | True |
| 11:10:51 | KXWTAMATCH-26JUN30TOMBOL-TOM | v4_t20m_fallback | True |
| 11:10:51 | KXATPMATCH-26JUN29SWEDIM-SWE | v4_t20m_fallback | True |
| 11:13:13 | KXATPMATCH-26JUN29SWEDIM-SWE | v4_t20m_fallback | True |
| 11:40:09 | KXWTAMATCH-26JUN30KRUVEK-KRU | v4_t20m_fallback | True |
| 12:10:14 | KXATPCHALLENGERMATCH-26JUN30CASGAL-CAS | v4_t20m_fallback | True |
| 12:12:30 | KXATPCHALLENGERMATCH-26JUN30CASGAL-CAS | v4_t20m_fallback | True |
| 12:18:16 | KXATPCHALLENGERMATCH-26JUN30CASGAL-CAS | v4_t20m_fallback | False |
| 13:11:51 | KXWTAMATCH-26JUN29SEINOS-NOS | v4_t20m_fallback | True |
| 13:40:17 | KXATPCHALLENGERMATCH-26JUN30LAHER-HER | v4_t20m_fallback | True |
| 13:41:27 | KXATPCHALLENGERMATCH-26JUN30LAHER-HER | v4_t20m_fallback | True |
| 13:43:16 | KXATPCHALLENGERMATCH-26JUN30LAHER-LA | v4_t20m_fallback | True |
| 13:44:14 | KXATPCHALLENGERMATCH-26JUN30LAHER-LA | v4_t20m_fallback | True |
| 14:20:27 | KXATPMATCH-26JUN29KOPCHO-CHO | match_live_cancel | True |
| 14:41:38 | KXITFMATCH-26JUN30HASREN-HAS | v4_t20m_fallback | True |
| 14:41:41 | KXATPCHALLENGERMATCH-26JUN30SAKMAG-MAG | v4_t20m_fallback | True |
| 14:41:56 | KXITFMATCH-26JUN30HASREN-HAS | v4_t20m_fallback | True |
| 14:41:57 | KXATPCHALLENGERMATCH-26JUN30SAKMAG-MAG | v4_t20m_fallback | True |
| 14:45:38 | KXITFMATCH-26JUN30HASREN-HAS | v4_t20m_fallback | True |
| 14:45:39 | KXATPCHALLENGERMATCH-26JUN30SAKMAG-MAG | v4_t20m_fallback | True |
| 14:45:43 | KXITFMATCH-26JUN30HASREN-HAS | v4_t20m_fallback | True |
| 14:47:43 | KXITFMATCH-26JUN30HASREN-HAS | v4_t20m_fallback | True |

### unfilled bids that filled AFTER scheduled start (rode open into live play)
| ticker | player | sched_start ET | fill_ts ET | minutes_after_start | fill_price | is_taker |
|---|---|---|---|---|---|---|
| KXWTAMATCH-26JUN29DAYKEY-DAY | Kayla Day | 06:00:00 | 06:02:04 | +2 | 8 | False |
| KXATPMATCH-26JUN29MAJTAB-MAJ | Kamil Majchrzak | 06:00:00 | 06:02:32 | +3 | 68 | False |
| KXWTAMATCH-26JUN29BEGSWA-BEG | Irina-Camelia Begu | 06:00:00 | 06:04:25 | +4 | 50 | False |
| KXWTAMATCH-26JUN29KALRAK-KAL | Anhelina Kalinina | 06:00:00 | 06:04:58 | +5 | 57 | False |
| KXWTAMATCH-26JUN29ANIGJO-ANI | Amanda Anisimova | 06:00:00 | 06:06:22 | +6 | 94 | False |
| KXWTAMATCH-26JUN29PAOMON-PAO | Jasmine Paolini | 06:00:00 | 06:07:07 | +7 | 42 | False |
| KXWTAMATCH-26JUN29BEGSWA-SWA | Katie Swan | 06:00:00 | 06:07:14 | +7 | 50 | False |
| KXWTAMATCH-26JUN29BEGSWA-SWA | Katie Swan | 06:00:00 | 06:07:28 | +7 | 50 | False |
| KXATPMATCH-26JUN29ROYWEN-WEN | Harry Wendelken | 06:00:00 | 06:08:38 | +9 | 46 | False |
| KXWTAMATCH-26JUN29ANIGJO-GJO | Lina Gjorcheska | 06:00:00 | 06:08:39 | +9 | 6 | False |
| KXWTAMATCH-26JUN29MARKEN-MAR | Petra Marcinko | 06:00:00 | 06:09:33 | +10 | 56 | False |
| KXWTAMATCH-26JUN29GIBBOU-BOU | Marie Bouzkova | 06:00:00 | 06:12:23 | +12 | 72 | False |
| KXWTAMATCH-26JUN29MARKEN-KEN | Sofia Kenin | 06:00:00 | 06:17:15 | +17 | 43 | False |
| KXATPMATCH-26JUN29SHIFAR-SHI | Sho Shimabukuro | 06:00:00 | 06:17:46 | +18 | 53 | False |
| KXWTAMATCH-26JUN29DAYKEY-KEY | Madison Keys | 06:00:00 | 06:24:20 | +24 | 91 | False |
| KXWTAMATCH-26JUN29KALRAK-RAK | Kamilla Rakhimova | 06:00:00 | 06:29:39 | +30 | 42 | False |
| KXATPMATCH-26JUN29MICFEA-MIC | Alex Michelsen | 07:10:00 | 07:21:44 | +12 | 60 | False |
| KXATPMATCH-26JUN29DZUFER-DZU | Damir Dzumhur | 07:10:00 | 07:24:17 | +14 | 21 | False |
| KXATPMATCH-26JUN29DEBUR-BUR | Roman Andres Burruchaga | 07:10:00 | 07:24:50 | +15 | 5 | False |
| KXATPMATCH-26JUN29MICFEA-FEA | Jacob Fearnley | 07:10:00 | 07:24:58 | +15 | 41 | False |
| KXATPMATCH-26JUN29ARNHAL-ARN | Matteo Arnaldi | 07:10:00 | 07:37:45 | +28 | 42 | False |
| KXATPMATCH-26JUN29JACGAU-JAC | Kyrian Jacquet | 07:10:00 | 07:41:30 | +32 | 70 | False |
| KXWTAMATCH-26JUN29HADTIM-TIM | Maria Timofeeva | 08:00:00 | 08:07:10 | +7 | 70 | False |
| KXATPMATCH-26JUN29DZUFER-FER | Arthur Fery | 07:10:00 | 08:07:10 | +57 | 78 | False |
| KXWTAMATCH-26JUN29SHYGOL-SHY | Iryna Shymanovich | 08:00:00 | 08:22:43 | +23 | 23 | False |
| KXWTAMATCH-26JUN29SHYGOL-GOL | Viktorija Golubic | 08:00:00 | 08:27:19 | +27 | 77 | False |
| KXATPMATCH-26JUN29KHAHAR-KHA | Karen Khachanov | 07:10:00 | 08:46:03 | +96 | 75 | False |
| KXWTAMATCH-26JUN29TOWSWI-TOW | Taylor Townsend | 08:30:00 | 08:50:36 | +21 | 13 | False |
| KXATPMATCH-26JUN29MUNCER-MUN | Jaume Munar | 07:40:00 | 08:54:12 | +74 | 23 | False |
| KXATPMATCH-26JUN29JACGAU-GAU | Vilius Gaubas | 07:10:00 | 08:58:22 | +108 | 30 | False |
| KXWTAMATCH-26JUN29BIRKOR-BIR | Kimberly Birrell | 08:00:00 | 09:07:35 | +68 | 49 | False |
| KXWTAMATCH-26JUN29HADTIM-HAD | Beatriz Haddad Maia | 08:00:00 | 09:09:30 | +70 | 30 | False |
| KXATPMATCH-26JUN29MUNCER-MUN | Jaume Munar | 07:40:00 | 09:19:52 | +100 | 23 | False |
| KXATPMATCH-26JUN29SWEDIM-DIM | Grigor Dimitrov | 08:50:00 | 09:20:45 | +31 | 77 | False |
| KXATPMATCH-26JUN29KHAHAR-KHA | Karen Khachanov | 07:10:00 | 09:32:20 | +142 | 75 | False |
| KXATPMATCH-26JUN29MENSAM-SAM | Toby Samuel | 08:50:00 | 09:40:44 | +51 | 31 | False |
| KXATPMATCH-26JUN29KHAHAR-HAR | Billy Harris | 07:10:00 | 09:41:39 | +152 | 25 | False |
| KXATPMATCH-26JUN29KYPMCD-KYP | Patrick Kypson | 08:50:00 | 09:48:01 | +58 | 28 | False |
| KXATPMATCH-26JUN29KYPMCD-MCD | Mackenzie McDonald | 08:50:00 | 09:49:52 | +60 | 71 | False |
| KXWTAMATCH-26JUN29EALZAR-ZAR | Renata Zarazua | 10:00:00 | 10:06:12 | +6 | 14 | False |
| KXWTAMATCH-26JUN29BOIRYB-RYB | Elena Rybakina | 10:00:00 | 10:08:30 | +8 | 97 | False |
| KXATPMATCH-26JUN29MOUGIR-GIR | Marcos Giron | 08:50:00 | 10:16:04 | +86 | 56 | False |
| KXWTAMATCH-26JUN29RUSMCC-MCC | Caty McNally | 10:00:00 | 10:20:07 | +20 | 42 | False |
| KXWTAMATCH-26JUN29STABLI-STA | Yuliia Starodubtseva | 10:00:00 | 10:23:57 | +24 | 55 | False |
| KXATPMATCH-26JUN29NAVCOB-COB | Flavio Cobolli | 10:00:00 | 10:31:54 | +32 | 78 | False |
| KXATPMATCH-26JUN29SONETC-SON | Lorenzo Sonego | 08:50:00 | 10:40:53 | +111 | 53 | False |
| KXWTAMATCH-26JUN29MERSIE-MER | Elise Mertens | 10:00:00 | 11:00:30 | +60 | 75 | False |
| KXATPMATCH-26JUN29BLOZVE-ZVE | Alexander Zverev | 10:30:00 | 11:11:01 | +41 | 88 | False |
| KXWTAMATCH-26JUN29SELKRA-SEL | Oksana Selekhmeteva | 10:00:00 | 11:11:19 | +71 | 47 | False |
| KXATPMATCH-26JUN29COLFIL-COL | Raphael Collignon | 10:00:00 | 11:18:30 | +78 | 42 | False |
| KXWTAMATCH-26JUN29MERSIE-SIE | Laura Siegemund | 10:00:00 | 11:24:03 | +84 | 24 | False |
| KXATPMATCH-26JUN29SWEDIM-SWE | Dane Sweeny | 08:50:00 | 11:35:09 | +165 | 24 | False |
| KXATPMATCH-26JUN29KOPCHO-KOP | Vit Kopriva | 10:00:00 | 12:04:15 | +124 | 59 | False |
| KXATPMATCH-26JUN29WAWBER-BER | Matteo Berrettini | 12:00:00 | 12:34:07 | +34 | 80 | False |
| KXATPMATCH-26JUN29WAWBER-BER | Matteo Berrettini | 12:00:00 | 12:34:37 | +35 | 80 | False |
| KXATPMATCH-26JUN29WAWBER-WAW | Stan Wawrinka | 12:00:00 | 12:39:01 | +39 | 20 | False |
| KXWTAMATCH-26JUN29SHNLYS-LYS | Eva Lys | 12:00:00 | 12:39:47 | +40 | 35 | False |
| KXWTAMATCH-26JUN29CIRBEJ-CIR | Sorana Cirstea | 11:00:00 | 12:55:07 | +115 | 74 | False |
| KXWTAMATCH-26JUN29SHNLYS-SHN | Diana Shnaider | 12:00:00 | 13:13:44 | +74 | 64 | False |
| KXWTAMATCH-26JUN29SEINOS-NOS | Linda Noskova | 12:00:00 | 13:14:23 | +74 | 91 | False |
| KXWTAMATCH-26JUN29KUDSAM-KUD | Polina Kudermetova | 12:00:00 | 13:15:58 | +76 | 38 | False |
| KXATPMATCH-26JUN29LEHPOP-POP | Alexei Popyrin | 10:50:00 | 13:17:54 | +148 | 22 | False |
| KXATPMATCH-26JUN29GRIDUC-DUC | James Duckworth | 10:00:00 | 13:18:50 | +199 | 34 | False |
| KXATPMATCH-26JUN29NAVCOB-NAV | Mariano Navone | 10:00:00 | 13:25:42 | +206 | 22 | False |
| KXATPMATCH-26JUN29TIAATM-ATM | Terence Atmane | 10:00:00 | 14:01:28 | +241 | 19 | False |

## (3) ALL FILLS TODAY (chronological)
Note: best_bid/best_ask = CURRENT live book (Kalshi REST does not store at-fill book; settled markets show null). is_taker is authoritative maker/taker truth.
| ts ET | ticker | player | action | side | price | qty | is_taker | play_type | cur_bid | cur_ask |
|---|---|---|---|---|---|---|---|---|---|---|
| 00:00:54 | KXITFMATCH-26JUN29ZHAKOA-KOA | Hao Sheng Koay | sell | no | 52 | 1.26 | False | exit | None | None |
| 00:03:31 | KXATPCHALLENGERMATCH-26JUN30MAEMIL-MIL | Ognjen Milic | buy | yes | 32 | 5.00 | False |  | None | None |
| 00:07:44 | KXITFWMATCH-26JUN30YAMREN-YAM | Ikumi Yamazaki | buy | yes | 91 | 5.00 | False |  | None | None |
| 00:18:16 | KXITFWMATCH-26JUN30YAMREN-REN | Ke Ren | buy | yes | 11 | 5.00 | False |  | None | None |
| 00:31:58 | KXITFWMATCH-26JUN30YAMREN-REN | Ke Ren | sell | no | 14 | 5.00 | False | exit | None | None |
| 00:32:45 | KXITFWMATCH-26JUN30ZHASNI-SNI | Anna Snigireva | buy | yes | 49 | 5.00 | False |  | None | None |
| 00:45:37 | KXITFWMATCH-26JUN30ZHASNI-ZHA | Junhan Zhang | buy | yes | 52 | 4.00 | False |  | None | None |
| 00:45:37 | KXITFWMATCH-26JUN30ZHASNI-ZHA | Junhan Zhang | buy | yes | 52 | 1.00 | False |  | None | None |
| 00:45:37 | KXITFWMATCH-26JUN30ZHASNI-ZHA | Junhan Zhang | buy | yes | 52 | 5.00 | False |  | None | None |
| 00:45:37 | KXITFWMATCH-26JUN30ZHASNI-SNI | Anna Snigireva | sell | no | 59 | 5.00 | False | exit | None | None |
| 00:58:38 | KXITFMATCH-26JUN29SUMTAK-SUM | Daisuke Sumizawa | sell | no | 74 | 5.00 | False | exit | None | None |
| 01:01:23 | KXITFMATCH-26JUN30NASMEN-NAS | Amirkhamza Nasridinov | buy | yes | 57 | 5.00 | False | v4_fallback_maker | None | None |
| 01:11:54 | KXATPCHALLENGERMATCH-26JUN30MIDHAI-MID | Lautaro Midon | buy | yes | 77 | 1.26 | False | v4_engagement_join | None | None |
| 01:12:58 | KXATPCHALLENGERMATCH-26JUN30MAEMIL-MAE | Francesco Maestrelli | buy | yes | 69 | 5.00 | False | v4_resting_maker | None | None |
| 01:15:59 | KXITFMATCH-26JUN29TANNAK-TAN | Ryota Tanuma | sell | no | 98 | 5.00 | False | exit | None | None |
| 01:50:10 | KXITFWMATCH-26JUN30ZHASNI-ZHA | Junhan Zhang | sell | no | 64 | 7.62 | False | exit | None | None |
| 01:50:11 | KXITFWMATCH-26JUN30ZHASNI-ZHA | Junhan Zhang | sell | no | 64 | 2.38 | False | exit | None | None |
| 01:53:34 | KXATPCHALLENGERMATCH-26JUN30JUSGIM-GIM | Sebastian Gima | buy | yes | 25 | 5.00 | False | v4_engagement_join | None | None |
| 02:25:29 | KXWTAMATCH-26JUN29SAKTAU-TAU | Clara Tauson | buy | yes | 65 | 5.00 | False | v4_engagement_join | None | None |
| 02:46:51 | KXATPMATCH-26JUN29MANDRO-DRO | Titouan Droguet | buy | yes | 36 | 5.00 | False | v4_resting_maker | None | None |
| 03:02:57 | KXWTAMATCH-26JUN29VALPLI-VAL | Tereza Valentova | buy | yes | 41 | 5.00 | False | v4_engagement_join | None | None |
| 03:18:01 | KXATPMATCH-26JUN29MAJTAB-TAB | Alejandro Tabilo | buy | yes | 33 | 5.00 | False | v4_engagement_join | None | None |
| 03:23:39 | KXITFMATCH-26JUN30NOVBAR-NOV | Michal Novansky | buy | yes | 39 | 5.00 | False | v4_resting_maker | None | None |
| 03:24:10 | KXATPCHALLENGERMATCH-26JUN30MICPAS-MIC | Daniel Michalski | buy | yes | 33 | 5.00 | False | v4_engagement_join | None | None |
| 03:26:20 | KXATPMATCH-26JUN29SHIFAR-FAR | Jaime Faria | buy | yes | 47 | 5.00 | False | v4_engagement_join | None | None |
| 03:26:52 | KXITFWMATCH-26JUN30POLTVE-TVE | Emilija Tverijonaite | buy | yes | 80 | 5.00 | False | v4_resting_maker | None | None |
| 03:29:14 | KXITFMATCH-26JUN30VETRET-RET | Marko Retelj | buy | yes | 43 | 5.00 | False | v4_resting_maker | None | None |
| 03:32:30 | KXATPMATCH-26JUN29HANMPE-MPE | Giovanni Mpetshi Perricard | buy | yes | 60 | 5.00 | False | v4_engagement_join | None | None |
| 03:36:01 | KXITFMATCH-26JUN30VETRET-VET | Miha Vetrih | buy | yes | 68 | 5.00 | False | v4_resting_maker | None | None |
| 03:37:29 | KXATPCHALLENGERMATCH-26JUN30JUSGIM-JUS | Guido Ivan Justo | buy | yes | 74 | 5.00 | False | v4_resting_maker | None | None |
| 03:39:30 | KXATPMATCH-26JUN29VIRSHE-VIR | Otto Virtanen | buy | yes | 18 | 5.00 | False | v4_resting_maker | None | None |
| 03:40:14 | KXATPCHALLENGERMATCH-26JUN30JUSGIM-GIM | Sebastian Gima | sell | no | 32 | 4.00 | False | exit | None | None |
| 03:40:31 | KXATPCHALLENGERMATCH-26JUN30JUSGIM-GIM | Sebastian Gima | sell | no | 32 | 1.00 | False | exit | None | None |
| 03:40:32 | KXATPCHALLENGERMATCH-26JUN30MIDHAI-MID | Lautaro Midon | buy | yes | 77 | 3.74 | False | v4_engagement_join | None | None |
| 03:44:24 | KXITFWMATCH-26JUN30POLTVE-POL | Adela Polakovicova | buy | yes | 18 | 5.00 | False | v4_reconciled | None | None |
| 03:44:51 | KXITFWMATCH-26JUN30BOYMIT-MIT | Nora Mitrea Gerocz | buy | yes | 6 | 5.00 | False | v4_fallback_maker | None | None |
| 03:45:03 | KXITFWMATCH-26JUN30YAMREN-YAM | Ikumi Yamazaki | sell | no | 98 | 5.00 | False | exit | None | None |
| 03:45:39 | KXWTAMATCH-26JUN29PAOMON-MON | Robin Montgomery | buy | yes | 59 | 5.00 | False | v4_reconciled | None | None |
| 03:48:04 | KXITFWMATCH-26JUN29BOEVAS-BOE | Laura Boehner | buy | yes | 24 | 5.00 | False | v4_resting_maker | None | None |
| 03:49:39 | KXATPCHALLENGERMATCH-26JUN30MIDHAI-HAI | Stefan Horia Haita | buy | yes | 22 | 5.00 | False | v4_engagement_join | None | None |
| 03:55:23 | KXATPCHALLENGERMATCH-26JUN30SMIGHE-SMI | Keegan Smith | buy | yes | 47 | 5.00 | False | v4_resting_maker | None | None |
| 03:55:53 | KXATPCHALLENGERMATCH-26JUN30MOELEC-MOE | Marvin Moeller | buy | yes | 77 | 5.00 | False | v4_reconciled | None | None |
| 03:58:57 | KXATPCHALLENGERMATCH-26JUN30MIDHAI-HAI | Stefan Horia Haita | sell | no | 28 | 5.00 | False | exit | None | None |
| 04:02:11 | KXATPCHALLENGERMATCH-26JUN30MAEMIL-MIL | Ognjen Milic | sell | no | 40 | 2.99 | False | exit | None | None |
| 04:02:15 | KXATPCHALLENGERMATCH-26JUN30MAEMIL-MIL | Ognjen Milic | sell | no | 40 | 2.01 | False | exit | None | None |
| 04:02:38 | KXATPCHALLENGERMATCH-26JUN30GIUGUL-GUL | Svyatoslav Gulin | buy | yes | 48 | 5.00 | False | v4_resting_maker | None | None |
| 04:03:07 | KXITFWMATCH-26JUN30BOYMIT-BOY | Melissa Boyden | buy | yes | 96 | 5.00 | False | v4_fallback_maker | None | None |
| 04:04:43 | KXITFMATCH-26JUN30CASBLA-CAS | Yannick Castelnuovo | buy | yes | 20 | 5.00 | False | v4_resting_maker | None | None |
| 04:06:18 | KXATPCHALLENGERMATCH-26JUN30MOELEC-LEC | Fryderyk Lechno-Wasiutynski | buy | yes | 24 | 5.00 | False | v4_reconciled | None | None |
| 04:07:09 | KXATPCHALLENGERMATCH-26JUN30ERHROD-ERH | Mathys Erhard | buy | yes | 28 | 5.00 | False | v4_reconciled | None | None |
| 04:07:29 | KXATPCHALLENGERMATCH-26JUN30TOPRAQ-RAQ | Leo Raquillet | buy | yes | 29 | 5.00 | False | v4_reconciled | None | None |
| 04:09:21 | KXATPCHALLENGERMATCH-26JUN30TOPRAQ-TOP | Marko ToPo | buy | yes | 68 | 5.00 | False | v4_resting_maker | None | None |
| 04:12:48 | KXATPCHALLENGERMATCH-26JUN30MICPAS-PAS | Francesco Passaro | buy | yes | 66 | 5.00 | False | v4_reconciled | None | None |
| 04:13:19 | KXITFMATCH-26JUN30VETRET-RET | Marko Retelj | sell | no | 52 | 5.00 | False | exit | None | None |
| 04:13:34 | KXATPMATCH-26JUN29DEBUR-DE | Alex de Minaur | buy | yes | 95 | 1.00 | False | v4_reconciled | None | None |
| 04:13:58 | KXATPCHALLENGERMATCH-26JUN30GIUGUL-GIU | Lorenzo Giustino | buy | yes | 48 | 5.00 | False | v4_resting_maker | None | None |
| 04:15:11 | KXATPCHALLENGERMATCH-26JUN30TOPRAQ-RAQ | Leo Raquillet | sell | no | 36 | 5.00 | False | exit | None | None |
| 04:16:48 | KXATPCHALLENGERMATCH-26JUN30GIUGUL-GUL | Svyatoslav Gulin | sell | no | 59 | 5.00 | False | exit | None | None |
| 04:18:47 | KXATPCHALLENGERMATCH-26JUN30DALTRA-DAL | Enrico Dalla Valle | buy | yes | 46 | 5.00 | False | v4_reconciled | None | None |
| 04:22:23 | KXITFWMATCH-26JUN30POLTVE-TVE | Emilija Tverijonaite | sell | no | 98 | 4.53 | False | exit | None | None |
| 04:22:32 | KXATPCHALLENGERMATCH-26JUN30ERHROD-ROD | Jurij Rodionov | buy | yes | 70 | 5.00 | False | v4_reconciled | None | None |
| 04:23:00 | KXITFWMATCH-26JUN30POLTVE-TVE | Emilija Tverijonaite | sell | no | 98 | 0.47 | False | exit | None | None |
| 04:23:14 | KXITFWMATCH-26JUN30BOYMIT-BOY | Melissa Boyden | sell | no | 98 | 5.00 | False | exit | None | None |
| 04:23:53 | KXITFMATCH-26JUN30NOVBAR-NOV | Michal Novansky | sell | no | 47 | 5.00 | False | exit | None | None |
| 04:23:55 | KXATPCHALLENGERMATCH-26JUN30ERHROD-ERH | Mathys Erhard | sell | no | 35 | 5.00 | False | exit | None | None |
| 04:24:23 | KXATPCHALLENGERMATCH-26JUN30MICPAS-MIC | Daniel Michalski | sell | no | 41 | 5.00 | False | exit | None | None |
| 04:26:42 | KXITFMATCH-26JUN30CASBLA-CAS | Yannick Castelnuovo | sell | no | 26 | 5.00 | False | exit | None | None |
| 04:27:34 | KXWTAMATCH-26JUN29BOUGRA-BOU | Katie Boulter | buy | yes | 72 | 5.00 | False | v4_engagement_join | None | None |
| 04:29:21 | KXATPCHALLENGERMATCH-26JUN30JUSGIM-JUS | Guido Ivan Justo | sell | no | 93 | 5.00 | False | exit | None | None |
| 04:30:12 | KXATPCHALLENGERMATCH-26JUN30TOPRAQ-TOP | Marko ToPo | sell | no | 88 | 5.00 | False | exit | None | None |
| 04:32:30 | KXATPCHALLENGERMATCH-26JUN30GIUGUL-GIU | Lorenzo Giustino | sell | no | 59 | 5.00 | False | exit | None | None |
| 04:35:46 | KXATPCHALLENGERMATCH-26JUN30MOELEC-LEC | Fryderyk Lechno-Wasiutynski | sell | no | 31 | 5.00 | False | exit | None | None |
| 04:42:57 | KXATPMATCH-26JUN29HANMPE-HAN | Yannick Hanfmann | buy | yes | 41 | 5.00 | False | v4_resting_maker | None | None |
| 04:43:54 | KXITFWMATCH-26JUN29BOEVAS-VAS | Arina Gabriela Vasilescu | buy | yes | 73 | 5.00 | False | v4_fallback_maker | None | None |
| 04:44:06 | KXITFWMATCH-26JUN29BOEVAS-BOE | Laura Boehner | sell | no | 30 | 5.00 | False | exit | None | None |
| 04:44:38 | KXATPMATCH-26JUN29KOKBUB-KOK | Thanasi Kokkinakis | buy | yes | 29 | 5.00 | False | v4_reconciled | None | None |
| 04:48:33 | KXITFWMATCH-26JUN30ERCPAN-ERC | Melisa Ercan | buy | yes | 98 | 5.00 | False | v4_resting_maker | None | None |
| 04:53:07 | KXITFWMATCH-26JUN29BOEVAS-VAS | Arina Gabriela Vasilescu | sell | no | 91 | 5.00 | False | exit | None | None |
| 04:53:54 | KXATPCHALLENGERMATCH-26JUN30MICPAS-PAS | Francesco Passaro | sell | no | 85 | 4.00 | False | exit | None | None |
| 04:54:26 | KXATPCHALLENGERMATCH-26JUN30MICPAS-PAS | Francesco Passaro | sell | no | 85 | 1.00 | False | exit | None | None |
| 04:54:26 | KXITFWMATCH-26JUN30ERCPAN-PAN | Eva Panova | buy | yes | 1 | 5.00 | False | v4_resting_maker | None | None |
| 04:56:19 | KXITFWMATCH-26JUN30ERCPAN-ERC | Melisa Ercan | sell | no | 98 | 5.00 | False | exit | None | None |
| 04:56:20 | KXITFMATCH-26JUN30MABPAL-PAL | Arin Pallegar | buy | yes | 27 | 1.31 | False | v4_resting_maker | None | None |
| 04:56:27 | KXATPMATCH-26JUN29ROYWEN-ROY | Valentin Royer | buy | yes | 55 | 1.00 | False | v4_reconciled | None | None |
| 04:56:39 | KXITFMATCH-26JUN30SOOKUR-KUR | Renato Kurmanaev | buy | yes | 61 | 5.00 | False | v4_fallback_maker | None | None |
| 04:58:03 | KXATPMATCH-26JUN30FRILAJ-FRI | Taylor Fritz | buy | yes | 94 | 5.00 | False | v4_engagement_join | None | None |
| 04:58:49 | KXATPMATCH-26JUN29VIRSHE-SHE | Ben Shelton | buy | yes | 82 | 2.38 | False | v4_engagement_join | None | None |
| 04:59:56 | KXITFMATCH-26JUN30MABPAL-PAL | Arin Pallegar | buy | yes | 27 | 3.69 | False | v4_resting_maker | None | None |
| 05:00:12 | KXITFMATCH-26JUN30SOOKUR-SOO | Lakshit Sood | buy | yes | 38 | 5.00 | False | v4_fallback_maker | None | None |
| 05:01:05 | KXATPMATCH-26JUN30FRILAJ-LAJ | Dusan Lajovic | buy | yes | 6 | 5.00 | False | v4_resting_maker | None | None |
| 05:03:43 | KXITFWMATCH-26JUN30ERCPAN-PAN | Eva Panova | sell | no | 4 | 5.00 | False | exit | None | None |
| 05:04:31 | KXATPCHALLENGERMATCH-26JUN30DALTRA-DAL | Enrico Dalla Valle | sell | no | 54 | 5.00 | False | exit | None | None |
| 05:12:05 | KXATPCHALLENGERMATCH-26JUN30MOELEC-MOE | Marvin Moeller | sell | no | 96 | 5.00 | False | exit | None | None |
| 05:13:51 | KXITFMATCH-26JUN30SOOKUR-KUR | Renato Kurmanaev | sell | no | 79 | 5.00 | False | exit | None | None |
| 05:15:08 | KXWTAMATCH-26JUN29GIBBOU-GIB | Talia Gibson | buy | yes | 29 | 5.00 | False | v4_engagement_join | None | None |
| 05:18:20 | KXATPMATCH-26JUN29HUMBER-BER | Zizou Bergs | buy | yes | 36 | 5.00 | False | v4_resting_maker | None | None |
| 05:30:58 | KXWTAMATCH-26JUN29SAKTAU-SAK | Maria Sakkari | buy | yes | 36 | 5.00 | False | v4_engagement_join | None | None |
| 05:31:48 | KXATPMATCH-26JUN29MANDRO-MAN | Adrian Mannarino | buy | yes | 63 | 5.00 | False | v4_resting_maker | None | None |
| 05:40:20 | KXATPCHALLENGERMATCH-26JUN30ALBPIR-ALB | Radu Albot | buy | yes | 26 | 5.00 | False | v4_fallback_maker | None | None |
| 05:40:54 | KXATPCHALLENGERMATCH-26JUN30DHAXIL-XIL | Ioannis Xilas | buy | yes | 42 | 5.00 | False | v4_reconciled | None | None |
| 05:41:52 | KXATPMATCH-26JUN29DEBUR-DE | Alex de Minaur | buy | yes | 95 | 4.00 | False | v4_reconciled | None | None |
| 05:43:48 | KXITFMATCH-26JUN30SOOKUR-SOO | Lakshit Sood | sell | no | 46 | 5.00 | False | exit | None | None |
| 05:46:31 | KXATPCHALLENGERMATCH-26JUN30DHAXIL-DHA | Manas Dhamne | buy | yes | 58 | 5.00 | False | v4_resting_maker | None | None |
| 05:50:11 | KXWTAMATCH-26JUN29BOUGRA-GRA | Tyra Caterina Grant | buy | yes | 28 | 5.00 | False | v4_reconciled | None | None |
| 05:50:18 | KXATPCHALLENGERMATCH-26JUN30MCDMAR-MCD | Niels McDonald | buy | yes | 61 | 5.00 | False | v4_reconciled | None | None |
| 05:51:44 | KXATPCHALLENGERMATCH-26JUN30MCDMAR-MAR | Juan Cruz Martin Manzano | buy | yes | 37 | 5.00 | False | v4_resting_maker | None | None |
| 05:53:00 | KXATPCHALLENGERMATCH-26JUN30MIDHAI-MID | Lautaro Midon | sell | no | 96 | 5.00 | False | exit | None | None |
| 05:56:57 | KXATPCHALLENGERMATCH-26JUN30DIATOB-DIA | Facundo Diaz Acosta | buy | yes | 84 | 5.00 | False | v4_reconciled | None | None |
| 05:57:11 | KXATPMATCH-26JUN29VIRSHE-SHE | Ben Shelton | buy | yes | 82 | 0.14 | False | v4_engagement_join | None | None |
| 05:57:46 | KXWTAMATCH-26JUN29VALPLI-PLI | Karolina Pliskova | buy | yes | 60 | 5.00 | False | v4_fallback_maker | None | None |
| 05:58:43 | KXATPCHALLENGERMATCH-26JUN30PALYEV-YEV | Denis Yevseyev | buy | yes | 48 | 5.00 | False | v4_reconciled | None | None |
| 05:58:51 | KXATPMATCH-26JUN29ROYWEN-ROY | Valentin Royer | buy | yes | 55 | 4.00 | False | v4_reconciled | None | None |
| 06:02:04 | KXWTAMATCH-26JUN29DAYKEY-DAY | Kayla Day | buy | yes | 8 | 5.00 | False | v4_reconciled | None | None |
| 06:02:32 | KXATPMATCH-26JUN29MAJTAB-MAJ | Kamil Majchrzak | buy | yes | 68 | 5.00 | False | v4_reconciled | None | None |
| 06:04:25 | KXWTAMATCH-26JUN29BEGSWA-BEG | Irina-Camelia Begu | buy | yes | 50 | 5.00 | False | v4_fallback_maker | None | None |
| 06:04:58 | KXWTAMATCH-26JUN29KALRAK-KAL | Anhelina Kalinina | buy | yes | 57 | 5.00 | False | v4_reconciled | None | None |
| 06:05:09 | KXATPMATCH-26JUN29VIRSHE-SHE | Ben Shelton | buy | yes | 82 | 2.48 | False | v4_engagement_join | None | None |
| 06:06:22 | KXWTAMATCH-26JUN29ANIGJO-ANI | Amanda Anisimova | buy | yes | 94 | 5.00 | False | v4_reconciled | None | None |
| 06:06:31 | KXATPCHALLENGERMATCH-26JUN30DHAXIL-DHA | Manas Dhamne | sell | no | 74 | 5.00 | False | exit | None | None |
| 06:07:07 | KXWTAMATCH-26JUN29PAOMON-PAO | Jasmine Paolini | buy | yes | 42 | 5.00 | False | v4_fallback_maker | None | None |
| 06:07:14 | KXWTAMATCH-26JUN29BEGSWA-SWA | Katie Swan | buy | yes | 50 | 4.00 | False | v4_fallback_maker | None | None |
| 06:07:28 | KXWTAMATCH-26JUN29BEGSWA-SWA | Katie Swan | buy | yes | 50 | 1.00 | False | v4_fallback_maker | None | None |
| 06:07:54 | KXATPCHALLENGERMATCH-26JUN30BLASTA-BLA | Geoffrey Blancaneaux | buy | yes | 59 | 5.00 | False | v4_reconciled | None | None |
| 06:08:38 | KXATPMATCH-26JUN29ROYWEN-WEN | Harry Wendelken | buy | yes | 46 | 5.00 | False | v4_fallback_maker | None | None |
| 06:08:39 | KXWTAMATCH-26JUN29ANIGJO-GJO | Lina Gjorcheska | buy | yes | 6 | 5.00 | False | v4_reconciled | None | None |
| 06:08:55 | KXATPCHALLENGERMATCH-26JUN30COMDON-DON | Matthew William Donald | buy | yes | 18 | 5.00 | False | v4_reconciled | None | None |
| 06:09:33 | KXWTAMATCH-26JUN29MARKEN-MAR | Petra Marcinko | buy | yes | 56 | 5.00 | False | v4_resting_maker | None | None |
| 06:12:23 | KXWTAMATCH-26JUN29GIBBOU-BOU | Marie Bouzkova | buy | yes | 72 | 5.00 | False | v4_reconciled | None | None |
| 06:14:06 | KXATPMATCH-26JUN29ARNHAL-HAL | Quentin Halys | buy | yes | 58 | 5.00 | False | v4_engagement_join | None | None |
| 06:14:30 | KXWTAMATCH-26JUN29PAOMON-MON | Robin Montgomery | sell | no | 75 | 5.00 | False | exit | None | None |
| 06:15:01 | KXWTAMATCH-26JUN29BOUGRA-GRA | Tyra Caterina Grant | sell | no | 35 | 5.00 | False | exit | None | None |
| 06:17:15 | KXWTAMATCH-26JUN29MARKEN-KEN | Sofia Kenin | buy | yes | 43 | 5.00 | False | v4_reconciled | None | None |
| 06:17:46 | KXATPMATCH-26JUN29SHIFAR-SHI | Sho Shimabukuro | buy | yes | 53 | 5.00 | False | v4_fallback_maker | None | None |
| 06:17:56 | KXWTAMATCH-26JUN29SAKTAU-SAK | Maria Sakkari | sell | no | 44 | 3.74 | False | exit | None | None |
| 06:18:23 | KXWTAMATCH-26JUN29SAKTAU-SAK | Maria Sakkari | sell | no | 44 | 1.26 | False | exit | None | None |
| 06:18:59 | KXATPMATCH-26JUN29ROYWEN-WEN | Harry Wendelken | sell | no | 56 | 4.98 | False | exit | None | None |
| 06:19:00 | KXATPMATCH-26JUN29ROYWEN-WEN | Harry Wendelken | sell | no | 56 | 0.02 | False | exit | None | None |
| 06:19:40 | KXATPCHALLENGERMATCH-26JUN30DIATOB-TOB | Miguel Tobon | buy | yes | 16 | 5.00 | False | v4_fallback_maker | None | None |
| 06:21:58 | KXATPCHALLENGERMATCH-26JUN30MCDMAR-MAR | Juan Cruz Martin Manzano | sell | no | 45 | 5.00 | False | exit | None | None |
| 06:23:02 | KXATPMATCH-26JUN29SHIFAR-SHI | Sho Shimabukuro | sell | no | 66 | 0.22 | False | exit | None | None |
| 06:23:10 | KXATPMATCH-26JUN29SHIFAR-SHI | Sho Shimabukuro | sell | no | 66 | 4.78 | False | exit | None | None |
| 06:23:26 | KXATPCHALLENGERMATCH-26JUN30SMIGHE-GHE | Gabriel Ghetu | buy | yes | 54 | 5.00 | False | v4_resting_maker | None | None |
| 06:23:30 | KXWTAMATCH-26JUN29MARKEN-KEN | Sofia Kenin | sell | no | 52 | 5.00 | False | exit | None | None |
| 06:24:20 | KXWTAMATCH-26JUN29DAYKEY-KEY | Madison Keys | buy | yes | 91 | 5.00 | False | v4_reconciled | None | None |
| 06:24:35 | KXWTAMATCH-26JUN29DAYKEY-DAY | Kayla Day | sell | no | 12 | 5.00 | False | exit | None | None |
| 06:26:09 | KXATPCHALLENGERMATCH-26JUN30FELPIE-PIE | Samuele Pieri | buy | yes | 22 | 5.00 | False | v4_reconciled | None | None |
| 06:26:31 | KXATPMATCH-26JUN29BONDIA-BON | Benjamin Bonzi | buy | yes | 51 | 5.00 | False | v4_reconciled | None | None |
| 06:26:55 | KXATPCHALLENGERMATCH-26JUN30BLASTA-STA | Luca Staeheli | buy | yes | 39 | 5.00 | False | v4_resting_maker | None | None |
| 06:27:45 | KXATPCHALLENGERMATCH-26JUN30SMIGHE-SMI | Keegan Smith | sell | no | 57 | 5.00 | False | exit | None | None |
| 06:29:39 | KXWTAMATCH-26JUN29KALRAK-RAK | Kamilla Rakhimova | buy | yes | 42 | 5.00 | False | v4_reconciled | None | None |
| 06:29:58 | KXATPMATCH-26JUN29HANMPE-HAN | Yannick Hanfmann | sell | no | 49 | 5.00 | False | exit | None | None |
| 06:30:32 | KXATPMATCH-26JUN29KOKBUB-BUB | Alexander Bublik | buy | yes | 71 | 5.00 | False | v4_reconciled | None | None |
| 06:32:36 | KXWTAMATCH-26JUN29ANIGJO-ANI | Amanda Anisimova | sell | no | 98 | 5.00 | False | exit | None | None |
| 06:33:03 | KXWTAMATCH-26JUN29VALPLI-VAL | Tereza Valentova | sell | no | 49 | 5.00 | False | exit | None | None |
| 06:34:18 | KXWTAMATCH-26JUN29GIBBOU-BOU | Marie Bouzkova | sell | no | 91 | 5.00 | False | exit | None | None |
| 06:34:20 | KXATPMATCH-26JUN29MAJTAB-MAJ | Kamil Majchrzak | sell | no | 86 | 5.00 | False | exit | None | None |
| 06:34:37 | KXATPMATCH-26JUN29MENSAM-MEN | Jakub Mensik | buy | yes | 69 | 5.00 | False | v4_resting_maker | None | None |
| 06:35:42 | KXATPMATCH-26JUN29MANDRO-MAN | Adrian Mannarino | sell | no | 80 | 5.00 | False | exit | None | None |
| 06:35:46 | KXWTAMATCH-26JUN29MARKEN-MAR | Petra Marcinko | sell | no | 71 | 5.00 | False | exit | None | None |
| 06:37:22 | KXWTAMATCH-26JUN29BEGSWA-SWA | Katie Swan | sell | no | 63 | 3.09 | False | exit | None | None |
| 06:38:10 | KXATPMATCH-26JUN29MUNCER-CER | Francisco Cerundolo | buy | yes | 77 | 5.00 | False | v4_reconciled | None | None |
| 06:39:10 | KXWTAMATCH-26JUN29KALRAK-KAL | Anhelina Kalinina | sell | no | 73 | 5.00 | False | exit | None | None |
| 06:39:25 | KXWTAMATCH-26JUN29BEGSWA-SWA | Katie Swan | sell | no | 63 | 0.91 | False | exit | None | None |
| 06:39:48 | KXWTAMATCH-26JUN29VALPLI-PLI | Karolina Pliskova | sell | no | 76 | 5.00 | False | exit | None | None |
| 06:40:17 | KXWTAMATCH-26JUN29BEGSWA-SWA | Katie Swan | sell | no | 63 | 1.00 | False | exit | None | None |
| 06:42:41 | KXATPCHALLENGERMATCH-26JUN30DHAXIL-XIL | Ioannis Xilas | sell | no | 51 | 5.00 | False | exit | None | None |
| 06:42:50 | KXWTAMATCH-26JUN29DAYKEY-KEY | Madison Keys | sell | no | 98 | 5.00 | False | exit | None | None |
| 06:42:58 | KXATPMATCH-26JUN30LLASVA-LLA | Pablo Llamas Ruiz | buy | yes | 29 | 5.00 | False | v4_engagement_join | None | None |
| 06:43:45 | KXATPCHALLENGERMATCH-26JUN30SMIGHE-GHE | Gabriel Ghetu | sell | no | 69 | 5.00 | False | exit | None | None |
| 06:52:46 | KXATPCHALLENGERMATCH-26JUN30SIMKUZ-KUZ | Dimitar Kuzmanov | buy | yes | 59 | 5.00 | False | v4_reconciled | None | None |
| 06:53:43 | KXATPMATCH-26JUN29SHIFAR-FAR | Jaime Faria | sell | no | 58 | 5.00 | False | exit | None | None |
| 06:55:03 | KXATPCHALLENGERMATCH-26JUN30BLASTA-STA | Luca Staeheli | sell | no | 47 | 5.00 | False | exit | None | None |
| 06:55:32 | KXATPCHALLENGERMATCH-26JUN30LAGCOU-COU | Eliakim Coulibaly | buy | yes | 52 | 5.00 | False | v4_reconciled | None | None |
| 06:56:05 | KXATPCHALLENGERMATCH-26JUN30DIATOB-DIA | Facundo Diaz Acosta | sell | no | 98 | 5.00 | False | exit | None | None |
| 06:58:00 | KXATPCHALLENGERMATCH-26JUN30SIMKUZ-SIM | Ilia Simakin | buy | yes | 39 | 5.00 | False | v4_reconciled | None | None |
| 07:03:21 | KXATPCHALLENGERMATCH-26JUN30SIMKUZ-SIM | Ilia Simakin | sell | no | 47 | 5.00 | False | exit | None | None |
| 07:08:09 | KXATPMATCH-26JUN29HANMPE-MPE | Giovanni Mpetshi Perricard | sell | no | 76 | 5.00 | False | exit | None | None |
| 07:21:04 | KXATPMATCH-26JUN29BLOZVE-BLO | Alexander Blockx | buy | yes | 11 | 5.00 | False | v4_reconciled | None | None |
| 07:21:44 | KXATPMATCH-26JUN29MICFEA-MIC | Alex Michelsen | buy | yes | 60 | 5.00 | False | v4_fallback_maker | None | None |
| 07:24:17 | KXATPMATCH-26JUN29DZUFER-DZU | Damir Dzumhur | buy | yes | 21 | 5.00 | False | v4_resting_maker | None | None |
| 07:24:50 | KXATPMATCH-26JUN29DEBUR-BUR | Roman Andres Burruchaga | buy | yes | 5 | 5.00 | False | v4_reconciled | None | None |
| 07:24:58 | KXATPMATCH-26JUN29MICFEA-FEA | Jacob Fearnley | buy | yes | 41 | 5.00 | False | v4_resting_maker | None | None |
| 07:29:16 | KXATPMATCH-26JUN29VIRSHE-VIR | Otto Virtanen | sell | no | 23 | 5.00 | False | exit | None | None |
| 07:29:48 | KXWTAMATCH-26JUN30SVISNI-SVI | Elina Svitolina | buy | yes | 74 | 5.00 | False | v4_engagement_join | None | None |
| 07:31:29 | KXWTAMATCH-26JUN29BIRKOR-KOR | Alina Korneeva | buy | yes | 50 | 5.00 | False | v4_reconciled | None | None |
| 07:32:45 | KXATPCHALLENGERMATCH-26JUN30BRABAS-BRA | Raul Brancaccio | buy | yes | 34 | 5.00 | False | v4_reconciled | None | None |
| 07:33:03 | KXATPCHALLENGERMATCH-26JUN30BLASTA-BLA | Geoffrey Blancaneaux | sell | no | 76 | 5.00 | False | exit | None | None |
| 07:33:30 | KXATPCHALLENGERMATCH-26JUN30BRABAS-BAS | Nikoloz Basilashvili | buy | yes | 64 | 5.00 | False | v4_reconciled | None | None |
| 07:34:47 | KXATPCHALLENGERMATCH-26JUN30BRABAS-BRA | Raul Brancaccio | sell | no | 42 | 5.00 | False | exit | None | None |
| 07:35:27 | KXWTAMATCH-26JUN29PAOMON-PAO | Jasmine Paolini | sell | no | 51 | 1.23 | False | exit | None | None |
| 07:35:30 | KXWTAMATCH-26JUN29PAOMON-PAO | Jasmine Paolini | sell | no | 51 | 3.77 | False | exit | None | None |
| 07:37:45 | KXATPMATCH-26JUN29ARNHAL-ARN | Matteo Arnaldi | buy | yes | 42 | 5.00 | False | v4_reconciled | None | None |
| 07:38:33 | KXATPMATCH-26JUN29DEBUR-BUR | Roman Andres Burruchaga | sell | no | 9 | 5.00 | False | exit | None | None |
| 07:41:30 | KXATPMATCH-26JUN29JACGAU-JAC | Kyrian Jacquet | buy | yes | 70 | 5.00 | False | v4_reconciled | None | None |
| 07:44:17 | KXWTAMATCH-26JUN29HADTIM-HAD | Beatriz Haddad Maia | buy | yes | 30 | 1.00 | False | v4_fallback_maker | None | None |
| 07:47:37 | KXWTAMATCH-26JUN29SHYGOL-GOL | Viktorija Golubic | buy | yes | 77 | 1.00 | False | v4_fallback_maker | None | None |
| 07:48:34 | KXATPCHALLENGERMATCH-26JUN30JORPRA-PRA | Juan Carlos Prado Angelo | buy | yes | 55 | 5.00 | False | v4_resting_maker | None | None |
| 07:49:30 | KXATPMATCH-26JUN29SONETC-ETC | Tomas Martin Etcheverry | buy | yes | 47 | 5.00 | False | v4_reconciled | None | None |
| 07:50:27 | KXATPCHALLENGERMATCH-26JUN30JORPRA-JOR | David Jorda Sanchis | buy | yes | 43 | 5.00 | False | v4_resting_maker | None | None |
| 07:51:39 | KXATPCHALLENGERMATCH-26JUN30RIBRAP-RIB | Michele Ribecai | buy | yes | 74 | 5.00 | False | v4_fallback_maker | None | None |
| 07:52:49 | KXATPCHALLENGERMATCH-26JUN30RIBRAP-RAP | Daniele Rapagnetta | buy | yes | 25 | 5.00 | False | v4_reconciled | None | None |
| 07:54:20 | KXATPMATCH-26JUN29ARNHAL-ARN | Matteo Arnaldi | sell | no | 51 | 5.00 | False | exit | None | None |
| 07:55:38 | KXWTAMATCH-26JUN29GIBBOU-GIB | Talia Gibson | sell | no | 37 | 5.00 | False | exit | None | None |
| 07:56:32 | KXWTAMATCH-26JUN29KALRAK-RAK | Kamilla Rakhimova | sell | no | 51 | 5.00 | False | exit | None | None |
| 07:56:52 | KXATPCHALLENGERMATCH-26JUN30PAVSAN-PAV | Luka Pavlovic | buy | yes | 70 | 5.00 | False | v4_resting_maker | None | None |
| 07:57:57 | KXATPCHALLENGERMATCH-26JUN30JORPRA-JOR | David Jorda Sanchis | sell | no | 52 | 5.00 | False | exit | None | None |
| 07:58:01 | KXATPMATCH-26JUN29MICFEA-MIC | Alex Michelsen | sell | no | 76 | 1.29 | False | exit | None | None |
| 07:58:07 | KXATPMATCH-26JUN29MICFEA-MIC | Alex Michelsen | sell | no | 76 | 3.71 | False | exit | None | None |
| 07:58:31 | KXATPCHALLENGERMATCH-26JUN30PAVSAN-SAN | Akira Santillan | buy | yes | 28 | 5.00 | False | v4_fallback_maker | None | None |
| 07:59:59 | KXITFMATCH-26JUN30NASMEN-MEN | Fanming Meng | sell | no | 55 | 5.00 | False | exit | None | None |
| 08:01:19 | KXATPMATCH-26JUN29BONDIA-BON | Benjamin Bonzi | sell | no | 62 | 5.00 | False | exit | None | None |
| 08:03:02 | KXATPCHALLENGERMATCH-26JUN30CHAZAH-ZAH | Patrick Zahraj | buy | yes | 36 | 5.00 | False | v4_resting_maker | None | None |
| 08:04:16 | KXATPMATCH-26JUN29ROYWEN-ROY | Valentin Royer | sell | no | 69 | 1.00 | False | exit | None | None |
| 08:07:10 | KXWTAMATCH-26JUN29HADTIM-TIM | Maria Timofeeva | buy | yes | 70 | 5.00 | False | v4_reconciled | None | None |
| 08:07:10 | KXATPMATCH-26JUN29DZUFER-FER | Arthur Fery | buy | yes | 78 | 5.00 | False | v4_reconciled | None | None |
| 08:07:29 | KXATPCHALLENGERMATCH-26JUN30CHAZAH-CHA | Maxime Chazal | buy | yes | 61 | 5.00 | False | v4_resting_maker | None | None |
| 08:07:43 | KXATPMATCH-26JUN29DZUFER-DZU | Damir Dzumhur | sell | no | 27 | 3.26 | False | exit | None | None |
| 08:07:58 | KXATPCHALLENGERMATCH-26JUN30CHAZAH-ZAH | Patrick Zahraj | sell | no | 44 | 5.00 | False | exit | None | None |
| 08:08:04 | KXATPMATCH-26JUN29DZUFER-DZU | Damir Dzumhur | sell | no | 27 | 1.74 | False | exit | None | None |
| 08:08:06 | KXITFMATCH-26JUN30NASMEN-NAS | Amirkhamza Nasridinov | sell | no | 73 | 5.00 | False | exit | None | None |
| 08:12:06 | KXATPCHALLENGERMATCH-26JUN30RIBRAP-RAP | Daniele Rapagnetta | sell | no | 32 | 5.00 | False | exit | None | None |
| 08:14:46 | KXWTAMATCH-26JUN29NAVBAD-NAV | Emma Navarro | buy | yes | 62 | 5.00 | False | v4_resting_maker | None | None |
| 08:18:36 | KXWTAMATCH-26JUN29TOWSWI-SWI | Iga Swiatek | buy | yes | 86 | 5.00 | False | v4_fallback_maker | None | None |
| 08:21:53 | KXWTAMATCH-26JUN29NAVBAD-BAD | Paula Badosa | buy | yes | 38 | 5.00 | False | v4_reconciled | None | None |
| 08:22:43 | KXWTAMATCH-26JUN29SHYGOL-SHY | Iryna Shymanovich | buy | yes | 23 | 5.00 | False | v4_reconciled | None | None |
| 08:25:01 | KXATPCHALLENGERMATCH-26JUN30PAVSAN-SAN | Akira Santillan | sell | no | 35 | 5.00 | False | exit | None | None |
| 08:27:19 | KXWTAMATCH-26JUN29SHYGOL-GOL | Viktorija Golubic | buy | yes | 77 | 4.00 | False | v4_fallback_maker | None | None |
| 08:29:41 | KXATPMATCH-26JUN29TIAATM-TIA | Frances Tiafoe | buy | yes | 80 | 5.00 | False | v4_engagement_join | None | None |
| 08:34:47 | KXATPCHALLENGERMATCH-26JUN30SIMKUZ-KUZ | Dimitar Kuzmanov | sell | no | 76 | 5.00 | False | exit | None | None |
| 08:36:07 | KXWTAMATCH-26JUN29CIRBEJ-BEJ | Sara Bejlek | buy | yes | 27 | 5.00 | False | v4_engagement_join | None | None |
| 08:36:11 | KXATPCHALLENGERMATCH-26JUN29MBISOT-MBI | Mwendwa Mbithi | buy | yes | 54 | 5.00 | False | v4_resting_maker | None | None |
| 08:36:20 | KXATPMATCH-26JUN29MOUGIR-MOU | Corentin Moutet | buy | yes | 44 | 5.00 | False | v4_resting_maker | None | None |
| 08:37:08 | KXATPMATCH-26JUN29MOLALT-ALT | Daniel Altmaier | buy | yes | 54 | 5.00 | False | v4_engagement_join | None | None |
| 08:41:04 | KXATPCHALLENGERMATCH-26JUN30CHAZAH-CHA | Maxime Chazal | sell | no | 79 | 5.00 | False | exit | None | None |
| 08:42:00 | KXWTAMATCH-26JUN29KUDSAM-SAM | Liudmila Samsonova | buy | yes | 63 | 5.00 | False | v4_resting_maker | None | None |
| 08:42:23 | KXATPMATCH-26JUN29ARNHAL-HAL | Quentin Halys | sell | no | 73 | 5.00 | False | exit | None | None |
| 08:44:11 | KXATPCHALLENGERMATCH-26JUN30BONMON-BON | Federico Bondioli | buy | yes | 31 | 5.00 | False | v4_reconciled | None | None |
| 08:46:03 | KXATPMATCH-26JUN29KHAHAR-KHA | Karen Khachanov | buy | yes | 75 | 1.00 | False | v4_engagement_join | None | None |
| 08:46:18 | KXATPMATCH-26JUN29GRIDUC-GRI | Tallon Griekspoor | buy | yes | 67 | 1.00 | False | v4_resting_maker | None | None |
| 08:46:24 | KXATPCHALLENGERMATCH-26JUN30BONMON-MON | Inaki Montes-de la Torre | buy | yes | 69 | 5.00 | False | v4_reconciled | None | None |
| 08:49:06 | KXATPCHALLENGERMATCH-26JUN30BONMON-BON | Federico Bondioli | sell | no | 38 | 5.00 | False | exit | None | None |
| 08:49:30 | KXWTAMATCH-26JUN29EALZAR-EAL | Alexandra Eala | buy | yes | 86 | 5.00 | False | v4_engagement_join | None | None |
| 08:50:36 | KXWTAMATCH-26JUN29TOWSWI-TOW | Taylor Townsend | buy | yes | 13 | 5.00 | False | v4_resting_maker | None | None |
| 08:52:25 | KXATPMATCH-26JUN29DEBUR-DE | Alex de Minaur | sell | no | 98 | 1.00 | False | exit | None | None |
| 08:53:51 | KXWTAMATCH-26JUN29WILJOI-WIL | Serena Williams | buy | yes | 46 | 5.00 | False | v4_engagement_join | None | None |
| 08:54:12 | KXATPMATCH-26JUN29MUNCER-MUN | Jaume Munar | buy | yes | 23 | 3.00 | False | v4_fallback_maker | None | None |
| 08:54:49 | KXATPMATCH-26JUN29KOKBUB-KOK | Thanasi Kokkinakis | sell | no | 36 | 5.00 | False | exit | None | None |
| 08:55:54 | KXWTAMATCH-26JUN29RUSMCC-RUS | Elena-Gabriela Ruse | buy | yes | 57 | 5.00 | False | v4_resting_maker | None | None |
| 08:56:29 | KXATPMATCH-26JUN30FRILAJ-FRI | Taylor Fritz | sell | no | 98 | 5.00 | False | exit | None | None |
| 08:57:29 | KXATPMATCH-26JUN29DEBUR-DE | Alex de Minaur | sell | no | 98 | 4.00 | False | exit | None | None |
| 08:58:22 | KXATPMATCH-26JUN29JACGAU-GAU | Vilius Gaubas | buy | yes | 30 | 5.00 | False | v4_fallback_maker | None | None |
| 08:59:40 | KXATPMATCH-26JUN29NAKPIN-NAK | Brandon Nakashima | sell | no | 98 | 5.00 | False | exit | None | None |
| 09:02:44 | KXATPMATCH-26JUN29MOLALT-MOL | Alex Molcan | buy | yes | 47 | 5.00 | False | v4_engagement_join | None | None |
| 09:03:26 | KXATPMATCH-26JUN29HUMBER-BER | Zizou Bergs | sell | no | 44 | 5.00 | False | exit | None | None |
| 09:07:35 | KXWTAMATCH-26JUN29BIRKOR-BIR | Kimberly Birrell | buy | yes | 49 | 5.00 | False | v4_reconciled | None | None |
| 09:07:39 | KXWTAMATCH-26JUN29SHYGOL-GOL | Viktorija Golubic | sell | no | 96 | 5.00 | False | exit | None | None |
| 09:09:30 | KXWTAMATCH-26JUN29HADTIM-HAD | Beatriz Haddad Maia | buy | yes | 30 | 4.00 | False | v4_fallback_maker | None | None |
| 09:10:39 | KXWTAMATCH-26JUN29BIRKOR-BIR | Kimberly Birrell | sell | no | 61 | 1.47 | False | exit | None | None |
| 09:10:41 | KXWTAMATCH-26JUN29BIRKOR-BIR | Kimberly Birrell | sell | no | 61 | 3.53 | False | exit | None | None |
| 09:11:18 | KXATPCHALLENGERMATCH-26JUN30SHIMMO-MMO | Michael Mmoh | buy | yes | 63 | 5.00 | False | v4_resting_maker | None | None |
| 09:11:31 | KXATPCHALLENGERMATCH-26JUN30SHIMMO-SHI | Yuta Shimizu | buy | yes | 35 | 5.00 | False | v4_resting_maker | None | None |
| 09:13:22 | KXATPCHALLENGERMATCH-26JUN30PAVSAN-PAV | Luka Pavlovic | sell | no | 89 | 5.00 | False | exit | None | None |
| 09:15:15 | KXATPCHALLENGERMATCH-26JUN30SHIMMO-SHI | Yuta Shimizu | sell | no | 43 | 5.00 | False | exit | None | None |
| 09:19:35 | KXATPMATCH-26JUN29JACGAU-JAC | Kyrian Jacquet | sell | no | 88 | 5.00 | False | exit | None | None |
| 09:19:46 | KXATPCHALLENGERMATCH-26JUN30CASGAL-GAL | Mario Andre Galarraga | buy | yes | 5 | 5.00 | False | v4_resting_maker | None | None |
| 09:19:52 | KXATPMATCH-26JUN29MUNCER-MUN | Jaume Munar | buy | yes | 23 | 2.00 | False | v4_fallback_maker | None | None |
| 09:20:45 | KXATPMATCH-26JUN29SWEDIM-DIM | Grigor Dimitrov | buy | yes | 77 | 5.00 | False | v4_reconciled | None | None |
| 09:20:47 | KXWTAMATCH-26JUN29HADTIM-TIM | Maria Timofeeva | sell | no | 89 | 2.00 | False | exit | None | None |
| 09:25:14 | KXWTAMATCH-26JUN29TOWSWI-TOW | Taylor Townsend | sell | no | 18 | 5.00 | False | exit | None | None |
| 09:26:19 | KXATPCHALLENGERMATCH-26JUN30BONMON-MON | Inaki Montes-de la Torre | sell | no | 88 | 5.00 | False | exit | None | None |
| 09:31:03 | KXATPMATCH-26JUN29MUNCER-MUN | Jaume Munar | sell | no | 30 | 0.74 | False | exit | None | None |
| 09:31:03 | KXATPMATCH-26JUN29MUNCER-MUN | Jaume Munar | sell | no | 30 | 2.26 | False | exit | None | None |
| 09:32:20 | KXATPMATCH-26JUN29KHAHAR-KHA | Karen Khachanov | buy | yes | 75 | 4.00 | False | v4_engagement_join | None | None |
| 09:32:45 | KXATPCHALLENGERMATCH-26JUN30PALYEV-YEV | Denis Yevseyev | sell | no | 59 | 5.00 | False | exit | None | None |
| 09:35:26 | KXWTAMATCH-26JUN29SHYGOL-SHY | Iryna Shymanovich | sell | no | 28 | 5.00 | False | exit | None | None |
| 09:39:15 | KXATPMATCH-26JUN29COLFIL-FIL | Arthur Fils | buy | yes | 58 | 5.00 | False | v4_fallback_maker | None | None |
| 09:40:44 | KXATPMATCH-26JUN29MENSAM-SAM | Toby Samuel | buy | yes | 31 | 5.00 | False | v4_resting_maker | None | None |
| 09:41:39 | KXATPMATCH-26JUN29KHAHAR-HAR | Billy Harris | buy | yes | 25 | 5.00 | False | v4_reconciled | None | None |
| 09:42:34 | KXWTAMATCH-26JUN29SELKRA-KRA | Sinja Kraus | buy | yes | 53 | 5.00 | False | v4_fallback_maker | None | None |
| 09:44:04 | KXWTAMATCH-26JUN29HADTIM-TIM | Maria Timofeeva | sell | no | 89 | 3.00 | False | exit | None | None |
| 09:44:30 | KXATPCHALLENGERMATCH-26JUN30WINFEN-WIN | Edward Winter | buy | yes | 44 | 5.00 | False | v4_reconciled | None | None |
| 09:44:54 | KXWTAMATCH-26JUN29PODKOS-POD | Nadia Podoroska | buy | yes | 3 | 5.00 | False | v4_engagement_join | None | None |
| 09:45:24 | KXATPCHALLENGERMATCH-26JUN30LAGCOU-LAG | Pavel Lagutin | buy | yes | 38 | 5.00 | False | v4_resting_maker | None | None |
| 09:46:06 | KXATPCHALLENGERMATCH-26JUN30LAGCOU-COU | Eliakim Coulibaly | sell | no | 66 | 5.00 | False | exit | None | None |
| 09:47:39 | KXATPCHALLENGERMATCH-26JUN30MOLGOM-MOL | Elmer Moller | buy | yes | 64 | 5.00 | False | v4_resting_maker | None | None |
| 09:48:01 | KXATPMATCH-26JUN29KYPMCD-KYP | Patrick Kypson | buy | yes | 28 | 5.00 | False | v4_reconciled | None | None |
| 09:48:21 | KXWTAMATCH-26JUN29STABLI-BLI | Anna Blinkova | buy | yes | 43 | 5.00 | False | v4_fallback_maker | None | None |
| 09:49:52 | KXATPMATCH-26JUN29KYPMCD-MCD | Mackenzie McDonald | buy | yes | 71 | 5.00 | False | v4_reconciled | None | None |
| 09:51:28 | KXATPCHALLENGERMATCH-26JUN30LAGCOU-LAG | Pavel Lagutin | sell | no | 46 | 5.00 | False | exit | None | None |
| 09:51:45 | KXWTAMATCH-26JUN30KRUVEK-VEK | Donna Vekic | buy | yes | 60 | 5.00 | False | v4_resting_maker | None | None |
| 09:52:34 | KXATPMATCH-26JUN29MENSAM-SAM | Toby Samuel | sell | no | 38 | 5.00 | False | exit | None | None |
| 09:54:25 | KXWTAMATCH-26JUN30SVISNI-SNI | Daria Snigur | buy | yes | 27 | 5.00 | False | v4_fallback_maker | None | None |
| 09:55:42 | KXATPMATCH-26JUN29GRIDUC-GRI | Tallon Griekspoor | buy | yes | 67 | 4.00 | False | v4_resting_maker | None | None |
| 10:02:54 | KXATPMATCH-26JUN29KHAHAR-HAR | Billy Harris | sell | no | 32 | 5.00 | False | exit | None | None |
| 10:03:20 | KXATPCHALLENGERMATCH-26JUN30CANALM-ALM | Izan Almazan Valiente | buy | yes | 28 | 5.00 | False | v4_reconciled | None | None |
| 10:06:12 | KXWTAMATCH-26JUN29EALZAR-ZAR | Renata Zarazua | buy | yes | 14 | 5.00 | False | v4_reconciled | None | None |
| 10:07:34 | KXATPMATCH-26JUN29LEHPOP-LEH | Jiri Lehecka | buy | yes | 78 | 5.00 | False | v4_engagement_join | None | None |
| 10:07:37 | KXATPMATCH-26JUN29DZUFER-FER | Arthur Fery | sell | no | 98 | 5.00 | False | exit | None | None |
| 10:08:30 | KXWTAMATCH-26JUN29BOIRYB-RYB | Elena Rybakina | buy | yes | 97 | 5.00 | False | v4_fallback_maker | None | None |
| 10:09:03 | KXATPCHALLENGERMATCH-26JUN30ROMCEC-ROM | Filippo Romano | buy | yes | 34 | 5.00 | False | v4_reconciled | None | None |
| 10:11:58 | KXATPMATCH-26JUN29MICFEA-FEA | Jacob Fearnley | sell | no | 49 | 5.00 | False | exit | None | None |
| 10:12:41 | KXWTAMATCH-26JUN30ERJJEA-JEA | Leolia Jeanjean | buy | yes | 62 | 5.00 | False | v4_resting_maker | None | None |
| 10:12:56 | KXWTAMATCH-26JUN30ERJJEA-ERJ | Veronika Erjavec | buy | yes | 38 | 5.00 | False | v4_fallback_maker | None | None |
| 10:13:26 | KXATPCHALLENGERMATCH-26JUN30SHIMMO-MMO | Michael Mmoh | sell | no | 82 | 5.00 | False | exit | None | None |
| 10:13:26 | KXATPCHALLENGERMATCH-26JUN30ROCBAS-BAS | Pierluigi Basile | buy | yes | 34 | 5.00 | False | v4_fallback_maker | None | None |
| 10:16:04 | KXATPMATCH-26JUN29MOUGIR-GIR | Marcos Giron | buy | yes | 56 | 5.00 | False | v4_reconciled | None | None |
| 10:17:00 | KXWTAMATCH-26JUN29BIRKOR-KOR | Alina Korneeva | sell | no | 63 | 5.00 | False | exit | None | None |
| 10:19:24 | KXWTAMATCH-26JUN30ERJJEA-JEA | Leolia Jeanjean | sell | no | 79 | 5.00 | False | exit | None | None |
| 10:19:58 | KXWTAMATCH-26JUN29BOIRYB-RYB | Elena Rybakina | sell | no | 98 | 5.00 | False | exit | None | None |
| 10:20:07 | KXWTAMATCH-26JUN29RUSMCC-MCC | Caty McNally | buy | yes | 42 | 5.00 | False | v4_fallback_maker | None | None |
| 10:23:57 | KXWTAMATCH-26JUN29STABLI-STA | Yuliia Starodubtseva | buy | yes | 55 | 5.00 | False | v4_resting_maker | None | None |
| 10:25:27 | KXWTAMATCH-26JUN29STABLI-BLI | Anna Blinkova | sell | no | 52 | 5.00 | False | exit | None | None |
| 10:27:10 | KXATPCHALLENGERMATCH-26JUN30MOLGOM-GOM | Norbert Gombos | buy | yes | 37 | 5.00 | False | v4_fallback_maker | None | None |
| 10:27:17 | KXATPCHALLENGERMATCH-26JUN30ROMCEC-CEC | Marco Cecchinato | buy | yes | 65 | 5.00 | False | v4_resting_maker | None | None |
| 10:30:27 | KXATPCHALLENGERMATCH-26JUN30ROMCEC-ROM | Filippo Romano | sell | no | 42 | 5.00 | False | exit | None | None |
| 10:31:08 | KXWTAMATCH-26JUN29STABLI-STA | Yuliia Starodubtseva | sell | no | 70 | 5.00 | False | exit | None | None |
| 10:31:54 | KXATPMATCH-26JUN29NAVCOB-COB | Flavio Cobolli | buy | yes | 78 | 5.00 | False | v4_reconciled | None | None |
| 10:31:55 | KXATPCHALLENGERMATCH-26JUN30VASWEH-WEH | Kai Wehnelt | buy | yes | 35 | 3.00 | False | v4_reconciled | None | None |
| 10:38:27 | KXATPMATCH-26JUN29KYPMCD-KYP | Patrick Kypson | sell | no | 35 | 5.00 | False | exit | None | None |
| 10:38:40 | KXWTAMATCH-26JUN29TOWSWI-SWI | Iga Swiatek | sell | no | 98 | 5.00 | False | exit | None | None |
| 10:40:29 | KXWTAMATCH-26JUN29WILJOI-JOI | Maya Joint | buy | yes | 53 | 5.00 | False | v4_reconciled | None | None |
| 10:40:53 | KXATPMATCH-26JUN29SONETC-SON | Lorenzo Sonego | buy | yes | 53 | 5.00 | False | v4_fallback_maker | None | None |
| 10:41:14 | KXATPCHALLENGERMATCH-26JUN30CREWAL-WAL | Olle Wallin | buy | yes | 24 | 1.28 | False | v4_fallback_maker | None | None |
| 10:44:06 | KXATPCHALLENGERMATCH-26JUN30MOLGOM-GOM | Norbert Gombos | sell | no | 45 | 5.00 | False | exit | None | None |
| 10:50:50 | KXATPCHALLENGERMATCH-26JUN30ROCBAS-ROC | Oriol Roca Batalla | buy | yes | 65 | 5.00 | False | v4_reconciled | None | None |
| 10:52:16 | KXATPCHALLENGERMATCH-26JUN30ROCBAS-BAS | Pierluigi Basile | sell | no | 42 | 5.00 | False | exit | None | None |
| 11:00:07 | KXWTAMATCH-26JUN29NAVBAD-BAD | Paula Badosa | sell | no | 46 | 3.11 | False | exit | None | None |
| 11:00:11 | KXWTAMATCH-26JUN29NAVBAD-BAD | Paula Badosa | sell | no | 46 | 1.89 | False | exit | None | None |
| 11:00:30 | KXWTAMATCH-26JUN29MERSIE-MER | Elise Mertens | buy | yes | 75 | 5.00 | False | v4_reconciled | None | None |
| 11:08:10 | KXATPMATCH-26JUN29WAWBER-WAW | Stan Wawrinka | buy | yes | 20 | 1.00 | False | v4_reconciled | None | None |
| 11:09:12 | KXATPCHALLENGERMATCH-26JUN30MENABO-ABO | Valerio Aboian | buy | yes | 35 | 5.00 | False | v4_fallback_maker | None | None |
| 11:09:15 | KXATPCHALLENGERMATCH-26JUN30ROCBAS-ROC | Oriol Roca Batalla | sell | no | 84 | 5.00 | False | exit | None | None |
| 11:11:01 | KXATPMATCH-26JUN29BLOZVE-ZVE | Alexander Zverev | buy | yes | 88 | 5.00 | False | v4_reconciled | None | None |
| 11:11:19 | KXWTAMATCH-26JUN29SELKRA-SEL | Oksana Selekhmeteva | buy | yes | 47 | 5.00 | False | v4_reconciled | None | None |
| 11:11:27 | KXATPCHALLENGERMATCH-26JUN30GOMMON-MON | Ignacio Monzon | buy | yes | 51 | 5.00 | False | v4_resting_maker | None | None |
| 11:13:42 | KXATPCHALLENGERMATCH-26JUN30CREWAL-CRE | CRE | buy | yes | 75 | 5.00 | False | v4_fallback_maker | None | None |
| 11:14:21 | KXATPMATCH-26JUN29SONETC-SON | Lorenzo Sonego | sell | no | 66 | 5.00 | False | exit | None | None |
| 11:14:43 | KXATPCHALLENGERMATCH-26JUN30CREWAL-WAL | Olle Wallin | buy | yes | 24 | 3.72 | False | v4_fallback_maker | None | None |
| 11:15:58 | KXATPMATCH-26JUN29WAWBER-WAW | Stan Wawrinka | buy | yes | 20 | 1.33 | False | v4_reconciled | None | None |
| 11:16:23 | KXATPCHALLENGERMATCH-26JUN30CREWAL-WAL | Olle Wallin | sell | no | 31 | 5.00 | False | exit | None | None |
| 11:16:30 | KXATPMATCH-26JUN29MOUGIR-MOU | Corentin Moutet | sell | no | 53 | 5.00 | False | exit | None | None |
| 11:17:21 | KXATPCHALLENGERMATCH-26JUN30OSOBER-OSO | Juan Sebastian Osorio | buy | yes | 47 | 5.00 | False | v4_reconciled | None | None |
| 11:18:30 | KXATPMATCH-26JUN29COLFIL-COL | Raphael Collignon | buy | yes | 42 | 5.00 | False | v4_fallback_maker | None | None |
| 11:18:38 | KXATPCHALLENGERMATCH-26JUN30MENABO-MEN | Facundo Mena | buy | yes | 62 | 5.00 | False | v4_resting_maker | None | None |
| 11:18:53 | KXATPCHALLENGERMATCH-26JUN30GOMMON-GOM | Juan Sebastian Gomez | buy | yes | 47 | 5.00 | False | v4_resting_maker | None | None |
| 11:20:33 | KXATPCHALLENGERMATCH-26JUN30GOMMON-MON | Ignacio Monzon | sell | no | 64 | 5.00 | False | exit | None | None |
| 11:23:22 | KXWTAMATCH-26JUN29SEINOS-SEI | Ella Seidel | buy | yes | 10 | 5.00 | False | v4_resting_maker | None | None |
| 11:24:03 | KXWTAMATCH-26JUN29MERSIE-SIE | Laura Siegemund | buy | yes | 24 | 5.00 | False | v4_reconciled | None | None |
| 11:26:54 | KXATPMATCH-26JUN29BLOZVE-BLO | Alexander Blockx | sell | no | 16 | 5.00 | False | exit | None | None |
| 11:27:01 | KXATPCHALLENGERMATCH-26JUN30MENABO-ABO | Valerio Aboian | sell | no | 43 | 5.00 | False | exit | None | None |
| 11:28:00 | KXWTAMATCH-26JUN29SELKRA-SEL | Oksana Selekhmeteva | sell | no | 57 | 5.00 | False | exit | None | None |
| 11:30:09 | KXATPMATCH-26JUN29MENSAM-MEN | Jakub Mensik | sell | no | 87 | 5.00 | False | exit | None | None |
| 11:30:22 | KXWTAMATCH-26JUN29PODKOS-KOS | Marta Kostyuk | buy | yes | 97 | 5.00 | False | v4_engagement_join | None | None |
| 11:35:09 | KXATPMATCH-26JUN29SWEDIM-SWE | Dane Sweeny | buy | yes | 24 | 5.00 | False | v4_fallback_maker | None | None |
| 11:38:40 | KXATPCHALLENGERMATCH-26JUN30VASWEH-WEH | Kai Wehnelt | buy | yes | 35 | 2.00 | False | v4_reconciled | None | None |
| 11:40:05 | KXATPCHALLENGERMATCH-26JUN30VASWEH-VAS | Alexander Vasilev | buy | yes | 62 | 5.00 | False | v4_reconciled | None | None |
| 11:41:13 | KXWTAMATCH-26JUN29RUSMCC-RUS | Elena-Gabriela Ruse | sell | no | 73 | 5.00 | False | exit | None | None |
| 11:42:03 | KXATPCHALLENGERMATCH-26JUN30MOLGOM-MOL | Elmer Moller | sell | no | 83 | 5.00 | False | exit | None | None |
| 11:44:13 | KXWTAMATCH-26JUN30ERJJEA-ERJ | Veronika Erjavec | sell | no | 46 | 5.00 | False | exit | None | None |
| 11:48:26 | KXATPCHALLENGERMATCH-26JUN30VASWEH-WEH | Kai Wehnelt | sell | no | 43 | 3.00 | False | exit | None | None |
| 11:50:21 | KXATPCHALLENGERMATCH-26JUN30VASWEH-WEH | Kai Wehnelt | sell | no | 43 | 2.00 | False | exit | None | None |
| 11:51:39 | KXATPCHALLENGERMATCH-26JUN30WINFEN-FEN | Andrew Fenty | buy | yes | 53 | 5.00 | False | v4_resting_maker | None | None |
| 11:52:15 | KXATPMATCH-26JUN29COLFIL-COL | Raphael Collignon | sell | no | 51 | 5.00 | False | exit | None | None |
| 11:57:04 | KXATPMATCH-26JUN29COLFIL-FIL | Arthur Fils | sell | no | 73 | 5.00 | False | exit | None | None |
| 11:57:31 | KXATPCHALLENGERMATCH-26JUN30WINFEN-WIN | Edward Winter | sell | no | 53 | 5.00 | False | exit | None | None |
| 12:02:07 | KXATPCHALLENGERMATCH-26JUN30ROMCEC-CEC | Marco Cecchinato | sell | no | 84 | 5.00 | False | exit | None | None |
| 12:04:15 | KXATPMATCH-26JUN29KOPCHO-KOP | Vit Kopriva | buy | yes | 59 | 5.00 | False | v4_reconciled | None | None |
| 12:08:12 | KXWTAMATCH-26JUN29MERSIE-MER | Elise Mertens | sell | no | 94 | 5.00 | False | exit | None | None |
| 12:09:09 | KXATPMATCH-26JUN29KOKBUB-BUB | Alexander Bublik | sell | no | 89 | 5.00 | False | exit | None | None |
| 12:09:25 | KXWTAMATCH-26JUN29RUSMCC-MCC | Caty McNally | sell | no | 51 | 5.00 | False | exit | None | None |
| 12:09:56 | KXATPCHALLENGERMATCH-26JUN30CASGAL-GAL | Mario Andre Galarraga | sell | no | 9 | 3.76 | False | exit | None | None |
| 12:13:55 | KXATPMATCH-26JUN29KHAHAR-KHA | Karen Khachanov | sell | no | 94 | 1.00 | False | exit | None | None |
| 12:16:48 | KXATPCHALLENGERMATCH-26JUN30CASGAL-GAL | Mario Andre Galarraga | sell | no | 9 | 1.24 | False | exit | None | None |
| 12:16:53 | KXATPMATCH-26JUN29KHAHAR-KHA | Karen Khachanov | sell | no | 94 | 4.00 | False | exit | None | None |
| 12:18:16 | KXATPCHALLENGERMATCH-26JUN30CASGAL-CAS | Hernan Casanova | buy | yes | 97 | 5.00 | False | v4_resting_maker | None | None |
| 12:25:43 | KXWTAMATCH-26JUN30TOMBOL-BOL | Mariam Bolkvadze | buy | yes | 14 | 5.00 | False | v4_resting_maker | None | None |
| 12:29:00 | KXWTAMATCH-26JUN30TOMBOL-TOM | Ajla Tomljanovic | buy | yes | 86 | 5.00 | False | v4_fallback_maker | None | None |
| 12:30:26 | KXWTAMATCH-26JUN30TOMBOL-BOL | Mariam Bolkvadze | sell | no | 19 | 4.00 | False | exit | None | None |
| 12:30:27 | KXWTAMATCH-26JUN30TOMBOL-BOL | Mariam Bolkvadze | sell | no | 19 | 1.00 | False | exit | None | None |
| 12:34:07 | KXATPMATCH-26JUN29WAWBER-BER | Matteo Berrettini | buy | yes | 80 | 0.38 | False | v4_fallback_maker | None | None |
| 12:34:37 | KXATPMATCH-26JUN29WAWBER-BER | Matteo Berrettini | buy | yes | 80 | 4.62 | False | v4_fallback_maker | None | None |
| 12:34:40 | KXATPMATCH-26JUN29WAWBER-WAW | Stan Wawrinka | sell | no | 26 | 1.00 | False | exit | None | None |
| 12:34:52 | KXWTAMATCH-26JUN30SVISNI-SNI | Daria Snigur | sell | no | 34 | 5.00 | False | exit | None | None |
| 12:36:42 | KXWTAMATCH-26JUN29OSOWAL-OSO | Camila Osorio | buy | yes | 64 | 5.00 | False | v4_resting_maker | None | None |
| 12:36:48 | KXATPMATCH-26JUN29WAWBER-WAW | Stan Wawrinka | sell | no | 26 | 1.00 | False | exit | None | None |
| 12:39:01 | KXATPMATCH-26JUN29WAWBER-WAW | Stan Wawrinka | buy | yes | 20 | 2.67 | False | v4_reconciled | None | None |
| 12:39:47 | KXWTAMATCH-26JUN29SHNLYS-LYS | Eva Lys | buy | yes | 35 | 5.00 | False | v4_reconciled | None | None |
| 12:40:06 | KXATPCHALLENGERMATCH-26JUN30MATHEM-MAT | Anton Matusevich | buy | yes | 39 | 5.00 | False | v4_resting_maker | None | None |
| 12:48:33 | KXWTAMATCH-26JUN29NAVBAD-NAV | Emma Navarro | sell | no | 79 | 5.00 | False | exit | None | None |
| 12:52:11 | KXITFMATCH-26JUN30DEMLOG-LOG | Jack Loge | buy | yes | 48 | 5.00 | False | v4_resting_maker | None | None |
| 12:55:07 | KXWTAMATCH-26JUN29CIRBEJ-CIR | Sorana Cirstea | buy | yes | 74 | 5.00 | False | v4_fallback_maker | None | None |
| 12:56:00 | KXWTAMATCH-26JUN29CIRBEJ-BEJ | Sara Bejlek | sell | no | 34 | 1.24 | False | exit | None | None |
| 12:56:01 | KXWTAMATCH-26JUN29CIRBEJ-BEJ | Sara Bejlek | sell | no | 34 | 3.76 | False | exit | None | None |
| 12:58:51 | KXATPMATCH-26JUN29MOUGIR-GIR | Marcos Giron | sell | no | 70 | 3.79 | False | exit | None | None |
| 12:59:00 | KXATPMATCH-26JUN29MOUGIR-GIR | Marcos Giron | sell | no | 70 | 1.21 | False | exit | None | None |
| 13:03:47 | KXATPCHALLENGERMATCH-26JUN30VASWEH-VAS | Alexander Vasilev | sell | no | 80 | 5.00 | False | exit | None | None |
| 13:13:44 | KXWTAMATCH-26JUN29SHNLYS-SHN | Diana Shnaider | buy | yes | 64 | 5.00 | False | v4_resting_maker | None | None |
| 13:14:23 | KXWTAMATCH-26JUN29SEINOS-NOS | Linda Noskova | buy | yes | 91 | 5.00 | False | v4_fallback_maker | None | None |
| 13:15:03 | KXWTAMATCH-26JUN29SHNLYS-LYS | Eva Lys | sell | no | 43 | 5.00 | False | exit | None | None |
| 13:15:58 | KXWTAMATCH-26JUN29KUDSAM-KUD | Polina Kudermetova | buy | yes | 38 | 5.00 | False | v4_reconciled | None | None |
| 13:17:54 | KXATPMATCH-26JUN29LEHPOP-POP | Alexei Popyrin | buy | yes | 22 | 5.00 | False | v4_reconciled | None | None |
| 13:18:01 | KXATPCHALLENGERMATCH-26JUN30LEGBIC-BIC | Blaise Bicknell | buy | yes | 51 | 5.00 | False | v4_resting_maker | None | None |
| 13:18:08 | KXATPCHALLENGERMATCH-26JUN30DEHER-HER | Samuel Heredia | buy | yes | 28 | 5.00 | False | v4_engagement_join | None | None |
| 13:18:50 | KXATPMATCH-26JUN29GRIDUC-DUC | James Duckworth | buy | yes | 34 | 5.00 | False | v4_fallback_maker | None | None |
| 13:19:40 | KXATPCHALLENGERMATCH-26JUN30OSOBER-BER | Peter Bertran | buy | yes | 50 | 5.00 | False | v4_resting_maker | None | None |
| 13:19:42 | KXATPCHALLENGERMATCH-26JUN30OSOBER-OSO | Juan Sebastian Osorio | sell | no | 57 | 5.00 | False | exit | None | None |
| 13:21:23 | KXATPMATCH-26JUN29LEHPOP-POP | Alexei Popyrin | sell | no | 28 | 5.00 | False | exit | None | None |
| 13:21:39 | KXWTAMATCH-26JUN30KRUVEK-KRU | Ashlyn Krueger | buy | yes | 40 | 5.00 | False | v4_reconciled | None | None |
| 13:25:28 | KXATPMATCH-26JUN29GRIDUC-DUC | James Duckworth | sell | no | 41 | 5.00 | False | exit | None | None |
| 13:25:42 | KXATPMATCH-26JUN29NAVCOB-NAV | Mariano Navone | buy | yes | 22 | 5.00 | False | v4_fallback_maker | None | None |
| 13:26:48 | KXWTAMATCH-26JUN29KUDSAM-KUD | Polina Kudermetova | sell | no | 46 | 4.00 | False | exit | None | None |
| 13:28:05 | KXATPMATCH-26JUN29MOLALT-MOL | Alex Molcan | sell | no | 58 | 5.00 | False | exit | None | None |
| 13:28:32 | KXWTAMATCH-26JUN29KUDSAM-KUD | Polina Kudermetova | sell | no | 46 | 1.00 | False | exit | None | None |
| 13:30:21 | KXWTAMATCH-26JUN29PODKOS-KOS | Marta Kostyuk | sell | no | 98 | 5.00 | False | exit | None | None |
| 13:34:21 | KXWTAMATCH-26JUN30KRUVEK-VEK | Donna Vekic | sell | no | 76 | 5.00 | False | exit | None | None |
| 13:34:54 | KXWTAMATCH-26JUN29EALZAR-EAL | Alexandra Eala | sell | no | 98 | 5.00 | False | exit | None | None |
| 13:35:53 | KXITFMATCH-26JUN30DEMLOG-LOG | Jack Loge | sell | no | 59 | 5.00 | False | exit | None | None |
| 13:36:37 | KXWTAMATCH-26JUN29PODKOS-POD | Nadia Podoroska | sell | no | 6 | 5.00 | False | exit | None | None |
| 13:40:45 | KXATPMATCH-26JUN29BLOZVE-ZVE | Alexander Zverev | sell | no | 98 | 5.00 | False | exit | None | None |
| 13:41:27 | KXATPCHALLENGERMATCH-26JUN30LAHER-HER | Alex Hernandez | buy | yes | 29 | 5.00 | False | v4_reconciled | None | None |
| 13:42:51 | KXATPCHALLENGERMATCH-26JUN30LAHER-HER | Alex Hernandez | buy | yes | 26 | 5.00 | False | v4_reconciled | None | None |
| 13:43:06 | KXATPMATCH-26JUN29NAVCOB-NAV | Mariano Navone | sell | no | 28 | 5.00 | False | exit | None | None |
| 13:43:44 | KXWTAMATCH-26JUN29KUDSAM-SAM | Liudmila Samsonova | sell | no | 80 | 5.00 | False | exit | None | None |
| 13:49:17 | KXWTAMATCH-26JUN29CIRBEJ-CIR | Sorana Cirstea | sell | no | 93 | 5.00 | False | exit | None | None |
| 13:50:40 | KXITFMATCH-26JUN30HASREN-REN | Henry Ren | buy | yes | 35 | 3.00 | False | v4_resting_maker | None | None |
| 13:54:42 | KXWTAMATCH-26JUN29SHNLYS-SHN | Diana Shnaider | sell | no | 81 | 5.00 | False | exit | None | None |
| 14:00:07 | KXATPMATCH-26JUN29SWEDIM-SWE | Dane Sweeny | sell | no | 31 | 5.00 | False | exit | None | None |
| 14:01:28 | KXATPMATCH-26JUN29TIAATM-ATM | Terence Atmane | buy | yes | 19 | 5.00 | False | v4_fallback_maker | None | None |
| 14:13:06 | KXWTAMATCH-26JUN29OSOWAL-WAL | Simona Waltert | buy | yes | 36 | 5.00 | False | v4_reconciled | None | None |
| 14:16:24 | KXWTAMATCH-26JUN29SEINOS-NOS | Linda Noskova | sell | no | 98 | 5.00 | False | exit | None | None |
| 14:17:41 | KXATPCHALLENGERMATCH-26JUN29MBISOT-MBI | Mwendwa Mbithi | sell | no | 69 | 5.00 | False | exit | None | None |
| 14:20:53 | KXATPMATCH-26JUN29TIAATM-ATM | Terence Atmane | sell | no | 24 | 5.00 | False | exit | None | None |
| 14:26:53 | KXITFMATCH-26JUN30HASREN-REN | Henry Ren | buy | yes | 35 | 2.00 | False | v4_resting_maker | None | None |
| 14:32:53 | KXATPMATCH-26JUN29LEHPOP-LEH | Jiri Lehecka | sell | no | 98 | 5.00 | False | exit | None | None |
| 14:35:36 | KXWTAMATCH-26JUN29WILJOI-WIL | Serena Williams | sell | no | 55 | 1.00 | False | exit | None | None |
| 14:35:46 | KXWTAMATCH-26JUN29WILJOI-WIL | Serena Williams | sell | no | 55 | 4.00 | False | exit | None | None |
| 14:41:30 | KXATPCHALLENGERMATCH-26JUN30SAKLER-LER | Jules Leroux | buy | yes | 7 | 5.00 | False | v4_engagement_join | None | None |
| 14:49:23 | KXATPCHALLENGERMATCH-26JUN30NOGMAR-MAR | Alex Martinez | buy | yes | 35 | 5.00 | False | v4_resting_maker | None | None |
| 14:49:33 | KXATPMATCH-26JUN29SWEDIM-DIM | Grigor Dimitrov | sell | no | 97 | 5.00 | False | exit | None | None |
| 14:50:38 | KXWTAMATCH-26JUN30KRUVEK-KRU | Ashlyn Krueger | sell | no | 48 | 5.00 | False | exit | None | None |
| 14:56:49 | KXWTAMATCH-26JUN29OSOWAL-OSO | Camila Osorio | sell | no | 81 | 5.00 | False | exit | None | None |

## (6) FLAG STATE (config/deploy_v5_live.json, loaded by running PID)
| flag | value |
|---|---|
| liquid_repost_at_touch | True |
| match_live_grace_kill | True |
| match_live_grace_sec | <absent → code default False> |
| sustained_flow_latch | True |
| pair_governor_scoot | False |
| fv_anchor_enabled | <absent → code default False> |
| completion_combined_ceiling | True |
| completion_all_cells | True |
| premarket_bids_ride_live | True |
