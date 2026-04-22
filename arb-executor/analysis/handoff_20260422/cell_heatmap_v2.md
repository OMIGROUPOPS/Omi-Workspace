# Cell Heat Map v2 — Pregame-Close Counting
Generated: 2026-04-22 04:01:46 PM ET

## Summary

- Total cells: 80 (4 categories x 20 buckets)
- Active: 34 | Disabled: 4 | Missing: 42

### Data Coverage
- Source 1: match_facts_full.csv (Mar 17 - Apr 14, pregame-close via volatility-jump detector)
  - Rows processed: 1431 | Excluded (bad entry_mid): 1
  - Dates covered: 29
- Source 2: premarket_ticks CSVs (Apr 19 - Apr 23, pregame-close via volatility-jump detector)
  - Tickers processed: 724 | Excluded: 0
  - Dates covered: 5
- Combined date range: 2026-03-17 to 2026-04-22
- Gap days: 3 (2026-04-15, 2026-04-16, 2026-04-17)

### Counting Integrity
- Total cell-match entries: 1921
- Expected (2 x included matches): method uses per-ticker counting, not per-match pairing

### Symmetry Check

| Category | N (0-49) | N (50-99) | Ratio | Flag |
|---|---|---|---|---|
| ATP_MAIN | 211 | 195 | 1.08 | OK |
| ATP_CHALL | 536 | 500 | 1.07 | OK |
| WTA_MAIN | 205 | 190 | 1.08 | OK |
| WTA_CHALL | 44 | 40 | 1.10 | OK |

## ATP_MAIN

| Bucket | Status | Exit | N_total | N_mar17+ | N_apr | N_days |
|--------|--------|------|---------|----------|-------|--------|
| 0-4 | MISSING | - | 0 | 0 | 0 | 0 |
| 5-9 | MISSING | - | 0 | 0 | 0 | 0 |
| 10-14 | MISSING | - | 3 | 3 | 1 | 0 |
| 15-19 | MISSING | - | 10 | 10 | 6 | 0 |
| 20-24 | ACTIVE | 25c | 25 | 25 | 14 | 0 |
| 25-29 | ACTIVE | 23c | 12 | 12 | 7 | 0 |
| 30-34 | ACTIVE | 15c | 38 | 38 | 27 | 1 |
| 35-39 | ACTIVE | 12c | 33 | 33 | 23 | 2 |
| 40-44 | ACTIVE | 7c | 50 | 50 | 37 | 3 |
| 45-49 | MISSING | - | 40 | 40 | 37 | 4 |
| 50-54 | MISSING | - | 29 | 29 | 28 | 3 |
| 55-59 | DISABLED | - | 15 | 15 | 10 | 1 |
| 60-64 | ACTIVE | 13c | 58 | 58 | 36 | 1 |
| 65-69 | ACTIVE | 5c | 31 | 31 | 23 | 2 |
| 70-74 | ACTIVE | 10c | 31 | 31 | 18 | 1 |
| 75-79 | ACTIVE | 17c | 21 | 21 | 16 | 1 |
| 80-84 | MISSING | - | 9 | 9 | 5 | 0 |
| 85-89 | MISSING | - | 1 | 1 | 1 | 0 |
| 90-94 | MISSING | - | 0 | 0 | 0 | 0 |
| 95-99 | MISSING | - | 0 | 0 | 0 | 0 |

## ATP_CHALL

| Bucket | Status | Exit | N_total | N_mar17+ | N_apr | N_days |
|--------|--------|------|---------|----------|-------|--------|
| 0-4 | MISSING | - | 1 | 1 | 1 | 1 |
| 5-9 | MISSING | - | 3 | 3 | 3 | 0 |
| 10-14 | MISSING | - | 20 | 20 | 13 | 3 |
| 15-19 | ACTIVE | 31c | 40 | 40 | 25 | 3 |
| 20-24 | ACTIVE | 25c | 75 | 75 | 44 | 2 |
| 25-29 | ACTIVE | 21c | 57 | 57 | 29 | 2 |
| 30-34 | ACTIVE | 16c | 79 | 79 | 44 | 3 |
| 35-39 | ACTIVE | 12c | 64 | 64 | 35 | 3 |
| 40-44 | ACTIVE | 10c | 92 | 92 | 55 | 3 |
| 45-49 | ACTIVE | 6c | 105 | 105 | 88 | 5 |
| 50-54 | MISSING | - | 90 | 90 | 83 | 5 |
| 55-59 | ACTIVE | 6c | 41 | 41 | 25 | 3 |
| 60-64 | ACTIVE | 10c | 101 | 101 | 51 | 4 |
| 65-69 | ACTIVE | 10c | 39 | 39 | 28 | 3 |
| 70-74 | ACTIVE | 11c | 87 | 87 | 49 | 4 |
| 75-79 | ACTIVE | 19c | 58 | 58 | 32 | 3 |
| 80-84 | ACTIVE | 15c | 63 | 63 | 41 | 1 |
| 85-89 | ACTIVE | 11c | 18 | 18 | 10 | 2 |
| 90-94 | MISSING | - | 2 | 2 | 1 | 0 |
| 95-99 | MISSING | - | 1 | 1 | 1 | 1 |

## WTA_MAIN

| Bucket | Status | Exit | N_total | N_mar17+ | N_apr | N_days |
|--------|--------|------|---------|----------|-------|--------|
| 0-4 | MISSING | - | 0 | 0 | 0 | 0 |
| 5-9 | MISSING | - | 2 | 2 | 2 | 1 |
| 10-14 | MISSING | - | 7 | 7 | 6 | 1 |
| 15-19 | ACTIVE | 31c | 12 | 12 | 7 | 0 |
| 20-24 | ACTIVE | 25c | 16 | 16 | 10 | 0 |
| 25-29 | ACTIVE | 21c | 26 | 26 | 18 | 1 |
| 30-34 | ACTIVE | 16c | 23 | 23 | 14 | 2 |
| 35-39 | ACTIVE | 12c | 23 | 23 | 10 | 3 |
| 40-44 | ACTIVE | 5c | 39 | 39 | 24 | 3 |
| 45-49 | ACTIVE | 14c | 57 | 57 | 53 | 4 |
| 50-54 | ACTIVE | 26c | 54 | 54 | 50 | 4 |
| 55-59 | DISABLED | - | 12 | 12 | 5 | 1 |
| 60-64 | ACTIVE | 8c | 21 | 21 | 11 | 0 |
| 65-69 | DISABLED | - | 27 | 27 | 13 | 2 |
| 70-74 | ACTIVE | 15c | 29 | 29 | 19 | 0 |
| 75-79 | MISSING | - | 10 | 10 | 7 | 1 |
| 80-84 | ACTIVE | 15c | 18 | 18 | 10 | 0 |
| 85-89 | DISABLED | - | 17 | 17 | 11 | 1 |
| 90-94 | MISSING | - | 2 | 2 | 2 | 0 |
| 95-99 | MISSING | - | 0 | 0 | 0 | 0 |

## WTA_CHALL

| Bucket | Status | Exit | N_total | N_mar17+ | N_apr | N_days |
|--------|--------|------|---------|----------|-------|--------|
| 0-4 | MISSING | - | 0 | 0 | 0 | 0 |
| 5-9 | MISSING | - | 0 | 0 | 0 | 0 |
| 10-14 | MISSING | - | 0 | 0 | 0 | 0 |
| 15-19 | MISSING | - | 0 | 0 | 0 | 0 |
| 20-24 | MISSING | - | 0 | 0 | 0 | 0 |
| 25-29 | MISSING | - | 0 | 0 | 0 | 0 |
| 30-34 | MISSING | - | 1 | 1 | 0 | 0 |
| 35-39 | MISSING | - | 6 | 6 | 3 | 1 |
| 40-44 | MISSING | - | 23 | 23 | 19 | 2 |
| 45-49 | MISSING | - | 14 | 14 | 14 | 4 |
| 50-54 | MISSING | - | 25 | 25 | 24 | 3 |
| 55-59 | MISSING | - | 0 | 0 | 0 | 0 |
| 60-64 | MISSING | - | 6 | 6 | 5 | 1 |
| 65-69 | MISSING | - | 3 | 3 | 2 | 1 |
| 70-74 | MISSING | - | 1 | 1 | 1 | 1 |
| 75-79 | MISSING | - | 0 | 0 | 0 | 0 |
| 80-84 | MISSING | - | 0 | 0 | 0 | 0 |
| 85-89 | MISSING | - | 1 | 1 | 0 | 0 |
| 90-94 | MISSING | - | 4 | 4 | 4 | 1 |
| 95-99 | MISSING | - | 0 | 0 | 0 | 0 |

## Validation Trace (5 samples)

| match_id | ticker | ts | pregame_mid | bucket | ticks | pc_idx |
|---|---|---|---|---|---|---|
| KXATPCHALLENGERMATCH-26APR19ADESAN | ADESAN-ADE | 2026-04-18 10:24:06 PM | 49.5c | 45-49 | 33067 | 538 |
| KXATPCHALLENGERMATCH-26APR19ADESAN | ADESAN-SAN | 2026-04-18 10:24:06 PM | 49.5c | 45-49 | 35077 | 442 |
| KXATPCHALLENGERMATCH-26APR19BALROM | BALROM-BAL | 2026-04-18 06:43:20 PM | 50.0c | 50-54 | 5583 | 867 |
| KXATPCHALLENGERMATCH-26APR19BALROM | BALROM-ROM | 2026-04-18 06:28:27 PM | 49.5c | 45-49 | 2879 | 292 |
| KXATPCHALLENGERMATCH-26APR19BIGCID | BIGCID-BIG | 2026-04-19 01:00:51 AM | 49.5c | 45-49 | 16405 | 95 |

### Pair coherence check
- KXATPCHALLENGERMATCH-26APR19ADESAN: 49.5 + 49.5 = 99.0c (expect ~100)
- KXATPCHALLENGERMATCH-26APR19BALROM: 50.0 + 49.5 = 99.5c (expect ~100)
