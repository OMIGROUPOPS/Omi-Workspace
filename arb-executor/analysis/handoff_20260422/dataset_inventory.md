# Dataset Inventory — 2026-04-22 02:11:43 PM ET

## /tmp/validation4/step6_real/ticks/

1432 files, total 1.3GB, earliest=04/15 03:55 PM ET, latest=04/15 05:15 PM ET, formats=.bin

ticker_meta.json: 1628 entries, settle_bid for 1624

## /root/Omi-Workspace/arb-executor/analysis/premarket_ticks/

716 files, total 2.2GB, earliest=04/19 06:33 AM ET, latest=04/22 02:11 PM ET, formats=.csv

## tennis.db (SQLite)

Size: 599.9MB

| Table | Rows | Min TS | Max TS |
|---|---|---|---|
| active_positions | 0 |  |  |
| betexplorer_staging | 18856 |  |  |
| book_prices | 1457716 | 2026-04-19 18:33:45 | 2026-04-22 14:11:38 |
| bookmaker_odds | 32471 |  |  |
| dca_truth | 655 |  |  |
| edge_scores | 137 |  |  |
| historical_events | 5889 |  |  |
| kalshi_price_snapshots | 47556 | 2026-04-21 11:45:12 | 2026-04-22 14:11:04 |
| live_scores | 3364 |  |  |
| matches | 3627 | 2026-02-05 | 2026-04-17 |
| name_cache | 206 |  |  |
| players | 612 |  |  |
| sqlite_sequence | 4 |  |  |

## Files >1GB

- /tmp/bbo_log_v4.csv (32.9GB)

## Git grep for 218M / BBO rows / tick replay

- **218M**: c97ccde step 6 REAL: tick-replay heat map (65min, 218M ticks, 41 cells)
- **BBO rows**: no commits found
- **tick replay**: 5f1f3a4 v3 analysis: per-cell exit sweep + paired match analysis (tick replay)
