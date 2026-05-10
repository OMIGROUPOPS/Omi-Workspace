# forensic_replay_v1 — on-disk catalog (NOTE)

This directory holds forensic replay v1 outputs from Session 9 work. Not all
artifacts are committed to git. This NOTE records what's where and why.

## In-repo (committed)

- `phase3/run_summary.json` — corrected Phase 3 validation gate verdicts.
- `phase3/candidate_summary.parquet` — per-candidate metrics, the canonical
  truth source for cell ranking under corrected convention. 80 rows, 35 KB.
- `phase3/scenario_comparison.parquet` — per-candidate Scenario A vs B
  comparison. 80 rows, 8.4 KB.
- `phase3/cell_drift_per_minute.parquet` — per-candidate per-5min cell-drift
  trajectory. 3,920 rows, 30 KB.

## On-disk only (not committed)

- `phase3/replay_tape.parquet` (552 KB) — per-moment merged tape across all
  candidates. Useful for forensic re-investigation; reproducible from
  per-candidate intermediates if lost. Excluded from repo for size.
- `phase3/replay_tape_cand_*.parquet` (80 files, ~25 KB each, ~2 MB total) —
  per-candidate moment-level tapes. Resilience artifacts from incremental
  writes. Reproducible by re-running Phase 3.
- `phase3/_progress_summary.jsonl` (112 KB) — per-candidate progress log
  used during run for kill-resilience. Information-equivalent to
  candidate_summary.parquet.
- `phase3/build_log.txt` — runtime log, not strategic data.
- `phase3_pre_convention_fix/` (2.9 MB) — archive of the convention-bug
  Phase 3 run (commit db1d249-era). Preserved for audit / comparison.
  Not committed because the data is known-corrupted; the LESSONS amendment
  cites it by directory existence + empirical anchors (5,878-pair
  cross-tab + OSO/KAL forensic) without needing the parquets in repo.

## Reproducibility

The corrected Phase 3 producer is at
`data/scripts/build_forensic_replay_v1.py` (commit a058212). Re-running
`python3 data/scripts/build_forensic_replay_v1.py --phase=3` reproduces
all on-disk-only artifacts deterministically given the same input
parquets (g9_trades, g9_candles, g9_metadata, sample_manifest.json,
exit_policy_per_cell.parquet).
