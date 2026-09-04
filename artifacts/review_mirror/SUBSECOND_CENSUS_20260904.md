# SUBSECOND CONSOLIDATION — CENSUS PASS (2026-09-04)

Read-only. Machines: desktop, droplet A (104.131.191.95), DO Spaces omi-tick-archive, git history. Droplet B unreachable. Companion JSON: SUBSECOND_CENSUS_20260904.json (all counts, paths, raw dumps).

## File sets

| source | cadence class | median gap s | columns | files | tickers | events | first | last | bytes | timestamps |
|---|---|---|---|---|---|---|---|---|---|---|
| local:fit-local/ticks | 1-second | 1.0 | ts_et,ticker,bid_1,bid_1_sz,bid_2,bid_2_sz,bid_3,bid_3_sz,bid_4,bid_4_sz,bid_5,bid_5_sz,as | 1608 | 1608 | 804 | 2026-07-11T13:48:53 | 2026-07-21T14:40:28 | 973834436 | absolute (ET 12-hour string, 1 s resolution) |
| local:fit-local/prints.jsonl | subsecond (event-driven) | None | exchange_ts,is_block_trade,price_cents,receipt_id,size,source,taker_book_side,taker_outcom | 1 | 1606 | 804 | 2026-07-11T10:48:48.641494Z | 2026-07-21T19:33:45.512718Z | 1766090446 | absolute (exchange_ts ISO microseconds) |
| local:fit-local/depth_recorder | poll (per-ticker median 21.4 s) | 21.40750002861023 | ts, ts_epoch, ticker, cat, player, opp, mins_to_start, bid, ask, spread, bids[[px,sz]], as | 175 | None | None | 20260713 | 20260720 | 400532818 | absolute (ts_epoch) |
| local:ws-depth-source/ws_depth | subsecond | None | t, m{type, sid, seq, msg{market_ticker, market_id, price_dollars, delta_fp, side, ts, ts_m | 215 | None | None | 2026-07-12 | 2026-07-20 | 5393753162 | absolute (t epoch ms, msg.ts ISO) |
| local:holdout-exam-20260807/tapes | 1-second | 2.0 | ts_et,ticker,bid_1,bid_1_sz,bid_2,bid_2_sz,bid_3,bid_3_sz,bid_4,bid_4_sz,bid_5,bid_5_sz,as | 342 | 342 | 171 | 2026-07-26T14:12:24 | 2026-07-28T12:40:44 | 559715685 | absolute (ET 12-hour string) |
| local:calibration-v1/ws_public_trade_reconcile.sqlite | subsecond (event-driven) | None | public_print(trade_id,ticker,ts_ms,price_cents,size_text); ws_raw(+source_file); ws_unique | 1 | None | None | 2026-07-11T10:48:48Z | 2026-07-21T19:33:45Z | 1511034880 | absolute (ts_ms) |
| local:fit-local/guarded-cache-v3 | derived | None | cache_key, cache_version, earliest_utc, latest_utc, event_id, legs[{leg,ticker,prints,snap | 804 | None | 804 | 2026-07-12 | 2026-07-20 | 197461623 | absolute |
| dropletA:data/durable/depth_recorder | poll (same recorder as local depth_recorder) | None | ts, ts_epoch, ticker, cat, player, opp, mins_to_start, bid, ask, spread, bids, asks | 171 | None | None | 20260828 | 20260904 | 516298005 | absolute (ts_epoch) |
| dropletA:data/durable/ws_depth_recorder | subsecond | None | t, received_at_utc, source_epoch, staleness_ms, staleness_status, raw_ws_sha256, bbo{marke | 26 | None | None | 20260903 | 20260904 | 3062095038 | absolute |
| dropletA:data/durable/validation4_ticks | 1-second (median gap 1.0 s) | 1.0 | ts(uint32 LE), bid(uint8), ask(uint8) | 1678 | 1678 | 1150 | 2026-03-20T04:49:51 | 2026-04-17T15:15:49 | 1537053480 | absolute (epoch seconds) |
| dropletA:data/durable/bbo_log_v4.csv.gz | 1-second (single-writer append; MANIFEST) | None | timestamp, ticker, bid, ask, spread | 1 | None | None | 2026-03-20 04:49:51 ET | 2026-04-17 15:15:49 ET | 879047205 | absolute (ET string, 1 s) |
| dropletA:state/daysheet_tape | subsecond (event-driven; median gap 15.1 s) | 15.108958959579468 | {v, fetched_at, final, covered_from, prints[{ts, price_c, ct}]} | 476 | 476 | 303 | 2026-07-13T02:00:31Z | 2026-07-18T02:17:10Z | 48019556 | absolute (ts epoch) |
| dropletA:logs/live_v3_*.jsonl.gz | event-driven | None | ts, ts_epoch, event, ticker, details{} | 46 | None | None | 2026-06-01 | 2026-07-28 | 344130790 | absolute (ts_epoch) |
| dropletA:analysis/premarket_ticks | n/a | None |  | 0 | 0 | 0 | None | None | 0 | n/a |
| dropletA:tennis.db kalshi_price_snapshots | poll-5min (302 s median from range_spectrum tick arrays) | 302 | polled_at,ticker,event_ticker,series_ticker,bid_cents,ask_cents,last_cents,volume_24h,comm | 1 | 32742 | 16371 | 2026-04-21 11:45:12 | 2026-09-04 13:50:33 | 27388317696 | absolute (polled_at UTC string) |
| dropletA:/srv/omi-research | subsecond (public prints) | None | exchange_ts, is_block_trade, price_cents, receipt_id, size, source, taker_book_side, taker | 474 | 342 | 171 | 2026-07-12 | 2026-07-28 | 713357949 | absolute |
| spaces:omi-tick-archive/ticks | 1-second | 1.0 | ts_et,ticker,bid_1..ask_5(+sz),mid,bid_depth_5,ask_depth_5,depth_ratio,last_trade | 31767 | 31767 | 15884 | 2026-04-19 | 2026-07-28 | 9375338339 | absolute (ET 12-hour string) |
| spaces:omi-tick-archive/trades | subsecond (event-driven; 2-5 s median between prints) | 2.0 | ts_et,ticker,price,count,taker_side | 30813 | 30813 | 15554 | 2026-04-18 | 2026-07-28 | 214580025 | absolute (ET 12-hour string) |
| spaces:omi-tick-archive/ws_depth | subsecond | None | as ws_depth_recorder | 1740 | None | None | 20260623 | 20260904 | 128487896571 | absolute |
| git:c8119431 arb-executor/analysis/match_ticks | 1-second | 1.0 | ts_offset_sec, bid, ask, mid | 473 | 473 | 327 | 26MAR17 (name) | 26APR14 (name) | None | OFFSETS from first row (no absolute clock) |
| git:26f8e853 arb-executor/analysis/match_ticks_full | 1-second | 1.0 | ts_offset_sec, bid, ask, mid | 808 | 808 | 404 | 26MAR17 (name) | 26APR14 (name) | None | OFFSETS from first row |

Notes per set are in the JSON (`file_sets[].notes`).

## Stores

- **subsecond_store.db** — {"path": "/root/Omi-Workspace/arb-executor/state/subsecond_store.db", "bytes": 6376095744, "mtime": "2026-08-02 04:35", "sha256": "fecc8d8766cc6572bf84dd46fce49b1e59b80ac77b05db20bf44b223ca62ea93"}
- **tennis.db** — {"path": "/mnt/omi-trading-data-nyc3/active/tennis.db (symlink /root/Omi-Workspace/arb-executor/tennis.db)", "bytes": 27388317696, "wal_bytes": 146173512, "sha256": null, "sha256_note": "live database with WAL, not hashed"}
- **tennis_small_tables_backup_20260708.db** — {"path": "/root/tennis_small_tables_backup_20260708.db", "bytes": 16617472, "sha256": "ea3a3187dfb0bf7c7e59b090133278b91d75ad9fab68f4d25c73de69791274ad"}
- **fv_history (book_prices archive)** — {"path": "/root/Omi-Workspace/arb-executor/data/durable/fv_history/by_month/*.parquet", "kind": "bookmaker odds fair-values archived nightly from tennis.db book_prices (NOT Kalshi ticks)", "total_rows_archived": 62594288, "last_archived_ts": "2026-09-04 02:29:35", "files": {"2026-04": 3088738, "2026-05": 20388795, "2026-06": 12910761, "2026-07": 4484812, "2026-08": 18061180, "2026-09": 3660002}, "columns": ["event_ticker", "book_key", "player1_name", "player2_name", "book_p1_fv_cents", "book_p2_fv_cents", "raw_odds_p1", "raw_odds_p2", "vig_pct", "sport_key", "commence_time", "polled_at"]}
- **local prints.jsonl** — {"path": "C:/Users/omigr/OMI-Window1-private\\fit-local\\prints.jsonl", "sha256": "e9b5a765b51ddbf0d65364c4f38744ad949ca3c675e5b3a0e472392fbcfabb55", "bytes": 1766090446}
- **consolidator** — {"droplet_path": "/root/Omi-Workspace/arb-executor/analysis/subsecond_consolidate.py", "droplet_sha256": "e954dcd0122f2bbb35d7dae93be8817e6ab38af8dcc1287b3925ff1ef9e587a1", "droplet_mtime": "2026-07-18 12:40", "print_backfill_sha256": "bc29c1c72541d1343ebfa9c1361dc25b31ba6dcd4c9be6df526a737ea3307c5f", "cron": "no crontab entry for subsecond_consolidate.py or print_backfill.py on droplet A; only archive_sync.sh (09:10 daily), premarket_ticks gzip (06:17), ws_depth rclone copy (every 6 h), archive_book_prices_v1.py (02:30)"}

subsecond_store.db prints by src: [{"src": "backfill", "rows": 21061384, "first": "2026-05-14T00:00:00Z", "last": "2026-07-18T17:50:50Z", "tickers": 9405, "events": 4708}, {"src": "book_transition", "rows": 3629957, "first": "2026-07-11T13:27:21Z", "last": "2026-07-28T12:40:45Z", "tickers": 8962, "events": 4517}, {"src": "public_tape", "rows": 883557, "first": "2026-07-13T02:00:31Z", "last": "2026-07-18T02:17:10Z", "tickers": 463, "events": 301}]

subsecond_store.db prints by src×month: [{"src": "backfill", "month": "2026-05", "rows": 4906302, "events": 1147}, {"src": "backfill", "month": "2026-06", "rows": 8635562, "events": 2209}, {"src": "backfill", "month": "2026-07", "rows": 7519520, "events": 1468}, {"src": "book_transition", "month": "2026-07", "rows": 3629957, "events": 4517}, {"src": "public_tape", "month": "2026-07", "rows": 883557, "events": 301}]

tennis.db kalshi_price_snapshots: cols ['polled_at', 'ticker', 'event_ticker', 'series_ticker', 'bid_cents', 'ask_cents', 'last_cents', 'volume_24h', 'commence_time']; span [['2026-04-21 11:45:12'], ['2026-09-04 13:50:33']]; by month {"2026-04": {"rows": 296807, "tickers": 1448, "events": 724, "events_both_legs": 724}, "2026-05": {"rows": 1319932, "tickers": 4382, "events": 2191, "events_both_legs": 2191}, "2026-06": {"rows": 1297011, "tickers": 4738, "events": 2369, "events_both_legs": 2369}, "2026-07": {"rows": 834266, "tickers": 5356, "events": 2678, "events_both_legs": 2678}, "2026-08": {"rows": 2611254, "tickers": 14098, "events": 7049, "events_both_legs": 7049}, "2026-09": {"rows": 451830, "tickers": 2720, "events": 1360, "events_both_legs": 1360}}

tennis.db tables (name: max_rowid): active_positions: None, betexplorer_staging: 214972, book_prices: 66062674, bookmaker_odds: 173649, dca_truth: 655, edge_scores: 2538691, historical_events: 5889, kalshi_price_snapshots: 6814124, kalshi_schedule_revisions: 16990, live_scores: 46219907, matches: 3627, name_cache: 39331062, observed_start_events: None, observed_starts: 69, players: 612, sqlite_sequence: 5

## T1 — month × source → events with BOTH legs at ≤ 1-second cadence

| source | 2026-03 | 2026-03/04 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-09 |
|---|---|---|---|---|---|---|---|---|
| validation4_ticks (dropletA) | 188 |  | 340 |  |  |  |  |  |
| match_ticks (git c8119431) |  | 146 of 327 events have 2 files |  |  |  |  |  |  |
| match_ticks_full (git 26f8e853) |  | 404 |  |  |  |  |  |  |
| bbo_log_v4.csv.gz (dropletA) |  | NOT_ENUMERATED (515M rows; scan not completed) |  |  |  |  |  |  |
| spaces ticks |  |  | 865 | 617 | 7070 | 7331 |  |  |
| spaces trades (prints) |  |  | 865 | 559 | 6881 | 6954 |  |  |
| local fit-local/ticks |  |  |  |  |  | 804 |  |  |
| local fit-local/prints.jsonl |  |  |  |  |  | 804 |  |  |
| local holdout-exam tapes |  |  |  |  |  | 171 |  |  |
| local ws-depth-source |  |  |  |  |  | hourly frames 07-12..07-20 (per-event both-legs not enumerated) |  |  |
| dropletA daysheet_tape (public_tape) |  |  |  |  |  | 303 events, 476 tickers |  |  |
| subsecond_store prints src=backfill |  |  |  | 1147 | 2209 | 1468 |  |  |
| subsecond_store prints src=book_transition |  |  |  |  |  | 4517 |  |  |
| subsecond_store prints src=public_tape |  |  |  |  |  | 301 |  |  |
| spaces ws_depth (subsecond frames) |  |  |  |  | 8 days | 31 days | 31 days | 4 days |

## T2 — month × source → events with both legs at any cadence

| source | 2026-03 | 2026-03/04 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-08/09 | 2026-09 |
|---|---|---|---|---|---|---|---|---|---|
| validation4_ticks (dropletA) | 188 |  | 340 |  |  |  |  |  |  |
| match_ticks (git c8119431) |  | 327 |  |  |  |  |  |  |  |
| match_ticks_full (git 26f8e853) |  | 404 |  |  |  |  |  |  |  |
| bbo_log_v4.csv.gz (dropletA) |  | NOT_ENUMERATED |  |  |  |  |  |  |  |
| spaces ticks |  |  | 865 | 617 | 7070 | 7331 |  |  |  |
| spaces trades (prints) |  |  | 865 | 559 | 6881 | 6954 |  |  |  |
| local fit-local/ticks |  |  |  |  |  | 804 |  |  |  |
| local fit-local/prints.jsonl |  |  |  |  |  | 804 |  |  |  |
| local holdout-exam tapes |  |  |  |  |  | 171 |  |  |  |
| local ws-depth-source |  |  |  |  |  | same |  |  |  |
| dropletA daysheet_tape (public_tape) |  |  |  |  |  | 303 |  |  |  |
| subsecond_store prints src=backfill |  |  |  | 1147 | 2209 | 1468 |  |  |  |
| subsecond_store prints src=book_transition |  |  |  |  |  | 4517 |  |  |  |
| subsecond_store prints src=public_tape |  |  |  |  |  | 301 |  |  |  |
| local depth_recorder (poll) |  |  |  |  |  | hourly files 07-13..07-20; not per-event |  |  |  |
| dropletA depth_recorder (poll) |  |  |  |  |  |  |  | hourly files 08-28..09-04 |  |
| tennis.db kalshi_price_snapshots (poll-5min) |  |  | 724 | 2191 | 2369 | 2678 | 7049 |  | 1360 |
| spaces ws_depth (subsecond frames) |  |  |  |  | 8 days | 31 days | 31 days |  | 4 days |

## T3 — subsecond_store.db ingest_log

Ingested (src|month → files): {"public_tape|2026-07": 476, "ws_log|2026-06": 24, "ws_log|2026-07": 30, "book_transition|2026-07": 15210, "backfill|2026-04": 1268, "backfill|2026-07": 2911, "backfill|2026-06": 4274, "backfill|2026-05": 3908}

On disk but not ingested:
- daysheet_tape 2026-07 → ingested (476/476)
- premarket_ticks (book_transition) → ingested 15,210 files in 2026-07; directory now empty on disk; the same tickers persist only as spaces:omi-tick-archive/ticks objects (not in ingest_log by that path)
- spaces ticks 2026-04..2026-07 (31,767 objects) → NOT ingested by path (ingest_log has no spaces: paths)
- spaces trades 2026-04..2026-07 (30,813 objects) → NOT ingested; overlaps backfill (Kalshi /markets/trades) by ticker for 9405 tickers
- spaces ws_depth 2026-06-23..2026-09-04 (1,740 objects) → NOT ingested (book-grade; consolidator inventories only)
- validation4_ticks 2026-03-17..04-17 (1,678 .bin) → NOT ingested (no consolidator source for I-B-B binaries)
- bbo_log_v4.csv.gz 2026-03-20..04-17 → NOT ingested
- local fit-local/ticks 2026-07-11..07-21 (1,608 csv.gz) → NOT ingested (desktop only)
- local fit-local/prints.jsonl 2026-07-11..07-21 (4,836,462 prints) → NOT ingested (desktop only); same rows as calibration-v1 public_print
- local ws-depth-source 2026-07-12..07-20 (215 files) → NOT ingested (desktop only)
- local holdout-exam-20260807 2026-07-26..07-28 → NOT ingested (desktop only); droplet copy at /srv/omi-research/window1-exam-20260807
- /srv/omi-research PRINTS_804 + exam prints → NOT ingested
- live_v3 logs 2026-06-01..07-28 (46 files) → ingested as ws_log, 54 entries, 0 rows
- match_ticks / match_ticks_full (git only) → NOT ingested (offset clocks; not on any disk)
- kalshi_price_snapshots 2026-04-21..2026-09-04 → NOT ingested (poll grade; consumed by range_spectrum_build.py only)

## T4 — calendar days with zero tick-grain capture (all sources)

First capture day 2026-03-20; evaluated through 2026-09-04. Sources counted: ['validation4_ticks (measured per-file first-tick days; bbo_log_v4 is the same data, first/last lines identical, not separately day-enumerated)', 'spaces ticks', 'spaces trades', 'spaces ws_depth', 'local ticks/prints', 'holdout tapes', 'daysheet_tape', 'droplet depth_recorder']. Poll-grade stores excluded: ['kalshi_price_snapshots (2026-04-21..2026-09-04, no day gaps by month)', 'depth_recorder local 07-13..07-20'].

Zero-capture ranges:
- 2026-03-21 → 2026-03-22
- 2026-05-05 → 2026-05-23
- 2026-05-30 → 2026-05-30

## Unreachable / partial

- droplet B 159.65.234.55: UNREACHABLE — ssh connect timed out (port 22)
- tennis.db full table row counts: PARTIAL — count(*) on the 27 GB live DB did not complete within the SSH session (connection reset after ~50 min); max(rowid) proxies used where the file-backed pass finished
- bbo_log_v4 per-ticker enumeration: PARTIAL — 515M-row gz; per-line Python scan stopped; head/tail/row-count from C tools only
- match_ticks / match_ticks_full: GIT ONLY — not on any disk; read from commits c8119431 / 26f8e853
