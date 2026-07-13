# FULL SLATE REVIEW 20260712 (grade the logic; read-only; §0A held)

## Part 1 — per-step grades (3 trades x L1-L9 = 27 rows)

| id | step | rule (cite) | class | anchor | composer verdict | $ |
|---|---|---|---|---|---|---|
| T-20260712-0235 | L1 | kalshi schedule clock (kalshi_schedule_primary) (discover_markets/schedule resolver) | DECREED | census 07-10: Kalshi = card markers; ITF live-era only |  |  |
| T-20260712-0235 | L2 | universal T-240 window (V4_MAX_PLACEMENT_SEC) | DECREED | constraint #4 named constant (universal window) |  |  |
| T-20260712-0235 | L3 | fallback bell rate+rise (_gun_poll src5) | DECREED | M10/M13 constants, scorecard-graded |  |  |
| T-20260712-0235 | L4 | no v4_place recorded (adopted/booked path) (-) | NAKED | lineage-only aim |  |  |
| T-20260712-0235 | L5 | maker placement @40 (place_order chokepoint battery) | FITTED | chokepoint guards (law) | edge -0.2 vs posterior |  |
| T-20260712-0235 | L6 | reposts=0 holds=0 walk-caps=0 (_v4_manage_resting) | FITTED | churn-fix hold (law) |  |  |
| T-20260712-0235 | L7 | band exit filled @48 (band from cell table) (exit_rule_for (FV-blind by design)) | DECREED | M6 + pending -0g ruling | posterior 0.48 at exit tick -> gap -0.1 |  |
| T-20260712-0235 | L8 | fill booked via check_fills (cycle 1) (_book_v4_entry_fill / C-BOOK-THE-FILL) | FITTED | booking law + cycle stamps |  |  |
| T-20260712-0235 | L9 | settled open (settlement vocabulary + bot-only basis) | FITTED | rulings 07-09/07-10 |  |  |
| T-20260712-0234 | L1 | kalshi schedule clock (kalshi_schedule_primary) (discover_markets/schedule resolver) | DECREED | census 07-10: Kalshi = card markers; ITF live-era only |  |  |
| T-20260712-0234 | L2 | universal T-240 window (V4_MAX_PLACEMENT_SEC) | DECREED | constraint #4 named constant (universal window) |  |  |
| T-20260712-0234 | L3 | fallback bell rate+rise (_gun_poll src5) | DECREED | M10/M13 constants, scorecard-graded |  |  |
| T-20260712-0234 | L4 | entry table per-cell offset (anchor last_traded, cell 83) (v4 entry tables) | DECREED | M5 era-mixed, refit queued | posterior 0.82 at aim tick |  |
| T-20260712-0234 | L5 | maker placement @82 (place_order chokepoint battery) | FITTED | chokepoint guards (law) | edge +0.2 vs posterior |  |
| T-20260712-0234 | L6 | reposts=0 holds=0 walk-caps=0 (_v4_manage_resting) | FITTED | churn-fix hold (law) |  |  |
| T-20260712-0234 | L7 | band exit filled @98 (band from cell table) (exit_rule_for (FV-blind by design)) | DECREED | M6 + pending -0g ruling | posterior 0.98 at exit tick -> gap -0.1 |  |
| T-20260712-0234 | L8 | fill booked via check_fills (cycle 1) (_book_v4_entry_fill / C-BOOK-THE-FILL) | FITTED | booking law + cycle stamps |  |  |
| T-20260712-0234 | L9 | settled open (settlement vocabulary + bot-only basis) | FITTED | rulings 07-09/07-10 |  |  |
| T-20260712-0249 | L1 | kalshi schedule clock (kalshi_schedule_primary) (discover_markets/schedule resolver) | DECREED | census 07-10: Kalshi = card markers; ITF live-era only |  |  |
| T-20260712-0249 | L2 | universal T-240 window (V4_MAX_PLACEMENT_SEC) | DECREED | constraint #4 named constant (universal window) |  |  |
| T-20260712-0249 | L3 | gun: percat_fitted (_gun_poll) | DECREED | M10 |  |  |
| T-20260712-0249 | L4 | engagement_wave1 (anchor engagement_join, cell 55) (v4 place) | DECREED | unmapped table source | posterior 0.66 at aim tick |  |
| T-20260712-0249 | L5 | maker placement @55 (place_order chokepoint battery) | FITTED | chokepoint guards (law) | edge +10.5 vs posterior |  |
| T-20260712-0249 | L6 | reposts=0 holds=0 walk-caps=0 (_v4_manage_resting) | FITTED | churn-fix hold (law) |  |  |
| T-20260712-0249 | L7 | band exit resting @67 (exit_rule_for (FV-blind by design)) | DECREED | M6 + pending -0g ruling |  |  |
| T-20260712-0249 | L8 | fill booked via check_fills (cycle 1) (_book_v4_entry_fill / C-BOOK-THE-FILL) | FITTED | booking law + cycle stamps |  |  |
| T-20260712-0249 | L9 | settled open (settlement vocabulary + bot-only basis) | FITTED | rulings 07-09/07-10 |  |  |

**STEP-LEVEL MIGRATION METER: FITTED 12 (44%) | DECREED 14 (52%) | NAKED 1 (3.7%)**

## Part 2 — the no-fill cohort (17 legs placed, never filled)

| ticker | cat | bid | buys | taxonomy | forgone edge_p50 ¢ | strand? | unfilled side won? |
|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL12DEJGAU-GAU | ATP_MAIN | 32 | 1 | aim_below_achievable (tape low 33 > bid 32) | 0 | False | None |
| ATPMATCH-26JUL12ALTGAS-ALT | ATP_MAIN | 55 | 3 | aim_below_achievable (tape low 59 > bid 55) | 2 | False | None |
| ITFWMATCH-26JUL12SUNYUN-YU | ITF_W | 5 | 3 | aim_below_achievable (tape low 8 > bid 5) | 0 | False | None |
| WTAMATCH-26JUL13QUERUS-QUE | WTA_MAIN | 28 | 1 | aim_below_achievable (tape low 999 > bid 28) | 0 | False | None |
| ATPMATCH-26JUL12OFNTIR-OFN | ATP_MAIN | 42 | 1 | late_vs_dip (the dip printed before our placement) | 1 | False | None |
| ATPMATCH-26JUL12OFNTIR-TIR | ATP_MAIN | 56 | 1 | late_vs_dip (the dip printed before our placement) | 2 | False | None |
| ATPMATCH-26JUL12JACTRU-TRU | ATP_MAIN | 47 | 1 | late_vs_dip (the dip printed before our placement) | 3 | False | None |
| WTAMATCH-26JUL13KAWWAL-WAL | WTA_MAIN | 67 | 1 | late_vs_dip (the dip printed before our placement) | 2 | False | None |
| ATPMATCH-26JUL12SONSCH-SON | ATP_MAIN | 65 | 1 | late_vs_dip (the dip printed before our placement) | 2 | False | None |
| ATPCHALLENGERMATCH-26JUL12 | ATP_CHALL | 54 | 1 | queue_starved (tape printed at/below our level, no fill -- adverse-sel | 2 | False | None |
| ATPCHALLENGERMATCH-26JUL12 | ATP_CHALL | 36 | 2 | queue_starved (tape printed at/below our level, no fill -- adverse-sel | 1 | False | None |
| ATPCHALLENGERMATCH-26JUL12 | ATP_CHALL | 32 | 2 | queue_starved (tape printed at/below our level, no fill -- adverse-sel | 2 | False | None |
| ATPCHALLENGERMATCH-26JUL12 | ATP_CHALL | 51 | 1 | queue_starved (tape printed at/below our level, no fill -- adverse-sel | 0 | False | None |
| ATPCHALLENGERMATCH-26JUL12 | ATP_CHALL | 16 | 9 | queue_starved (tape printed at/below our level, no fill -- adverse-sel | 0 | True | None |
| ATPCHALLENGERMATCH-26JUL12 | ATP_CHALL | 57 | 2 | queue_starved (tape printed at/below our level, no fill -- adverse-sel | 1 | True | None |
| ITFWMATCH-26JUL12PANOUN-PA | ITF_W | 5 | 2 | queue_starved (tape printed at/below our level, no fill -- adverse-sel | 0 | True | None |
| ITFWMATCH-26JUL12SUNYUN-SU | ITF_W | 50 | 3 | queue_starved (tape printed at/below our level, no fill -- adverse-sel | 1 | False | None |

**Strand test (June mechanism):** 3 strands; unfilled-side-won verified on 0 (settlement rows where determinable).

## Part 3 — exchange truth (three-way, audited REST path)

exchange day buy-fills: 610 across 118 tickers | **violations: 114**
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXATPCHALLENGERMATCH-26JUL12RAIZHU-RAI", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXATPCHALLENGERMATCH-26JUL12HOHSUR-SUR", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXATPCHALLENGERMATCH-26JUL12YOUDLI-YOU", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXATPCHALLENGERMATCH-26JUL12MIYKUZ-MIY", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXATPCHALLENGERMATCH-26JUL12TOKROZ-TOK", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXATPCHALLENGERMATCH-26JUL12ECHMUN-MUN", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXITFWMATCH-26JUL12LERXUX-LER", "kind": "exchange_fill_missing_from_log", "exchange_qty": 10.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXWTACHALLENGERMATCH-26JUL12MALTUR-MAL", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXITFWMATCH-26JUL12DONDOB-DON", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXITFWMATCH-26JUL12LERXUX-XUX", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXATPCHALLENGERMATCH-26JUL12AVEFOR-FOR", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXITFWMATCH-26JUL12SAATAB-SAA", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXITFMATCH-26JUL12RICMIY-MIY", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXATPCHALLENGERMATCH-26JUL12MEJSOT-SOT", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXITFMATCH-26JUL12RICMIY-RIC", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXWTACHALLENGERMATCH-26JUL12BASABB-ABB", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXWTAMATCH-26JUL12MICKUL-MIC", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXWTAMATCH-26JUL12MORNEP-NEP", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXWTACHALLENGERMATCH-26JUL12MALTUR-TUR", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}
- **VIOLATION** exchange_fill_missing_from_log: {"tk": "KXATPCHALLENGERMATCH-26JUL12MORPET-PET", "kind": "exchange_fill_missing_from_log", "exchange_qty": 5.0}

## Part 4 — class filings + fix queue (ranked by measured cost)

| filing | instances | $ weight |
|---|---|---|
| AIM/TIMING MISS (no-fill) | 9 | 0.60 |
| ADVERSE-SELECTION STRAND (live population) | 8 | 0.35 |
| NAKED-STEP L4 | 1 | 0.00 |
| EXCHANGE-TRUTH DAYLIGHT | 114 | 0.00 |