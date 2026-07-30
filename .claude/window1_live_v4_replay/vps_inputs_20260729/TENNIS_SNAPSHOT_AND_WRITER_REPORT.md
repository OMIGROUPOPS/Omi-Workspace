# tennis.db online snapshot — writer and space report

The process writing `tennis.db` was **not the live order engine**. No `live_v4` or `tennis_v4` process had the database open. The openers were the tennis-data collectors below; the first, second, and fourth contain SQLite commit paths, while the monitor is read-only.

| PID | Process | Role | Can write `tennis.db` | Places exchange orders |
|---:|---|---|---|---|
| 1214162 | `python3 te_live.py` | Tennis Explorer collector | Yes | No order/API-post path found |
| 1214181 | `python3 -u tennis_odds.py` | Odds collector | Yes | No order/API-post path found |
| 1270860 | `python3 -u /tmp/fv_monitor_v3.py` | Fair-value monitor | No; reader | No |
| 1298320 | `python3 -u betexplorer.py` | BetExplorer collector | Yes | No order/API-post path found |

The four processes were left running. There was no pause, checkpoint, service change, or order-engine intervention.

## Snapshot

- Source symlink: `/root/Omi-Workspace/arb-executor/tennis.db`
- Resolved source: `/mnt/omi-trading-data-nyc3/active/tennis.db`
- Source open mode: read-only
- Method: one SQLite online-backup call into one temporary VPS snapshot
- Snapshot bytes: `17,434,673,152`
- SHA-256: `ade09fdc101267ac282c8194700ba188cd60aac4c554e4f38da02d14b5e8602c`
- SQLite `quick_check`: `ok`
- Source mtime recorded: `2026-07-30T00:34:14.118538540Z`
- Snapshot mtime preserved locally: `2026-07-30T00:00:47Z`
- Elapsed: `3,194.324` seconds
- Remote temporary snapshot: deleted only after local size, hash, and read-only SQLite-open verification
- Local replay path: `.claude/window1_live_v4_replay/vps_inputs_20260729/db/tennis.snapshot.db`
- Git status: ignored; the database is not committed

## Free-space guard

The abort threshold was 5,000,000,000 bytes.

| Point | Free bytes |
|---|---:|
| Before backup | 25,856,798,720 |
| Minimum sampled during backup | 8,378,953,728 |
| Snapshot present on VPS | 8,394,113,024 |
| After verified download and remote cleanup | 25,825,349,632 |

The threshold was never crossed.

## WAL

| Point | WAL bytes |
|---|---:|
| Before | 66,451,512 |
| During (641 samples; observed value) | 66,451,512 |
| Immediately after backup | 66,451,512 |
| After snapshot verification | 66,451,512 |
| After remote cleanup | 66,451,512 |

The WAL size was unchanged throughout the recorded operation.

Machine-readable evidence:

- `TENNIS_SNAPSHOT_RECEIPT.json`
- `TENNIS_SNAPSHOT_WAL_SAMPLES.jsonl`
- `VPS_INPUT_MANIFEST.json`
