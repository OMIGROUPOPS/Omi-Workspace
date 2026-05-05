# Durable Archive — Irreplaceable Data Files

Created: 2026-05-04 (Session 6, Phase 1B)
Purpose: Preserve canonical data files that lived on /tmp (ephemeral per F27/F1) by copying to durable disk under arb-executor/data/. These files are too large for git and are explicitly NOT committed; they are durable by virtue of disk persistence on the VPS.

## Files

### u4_phase3_state_pass1.parquet
- Source: /tmp/u4_phase3_state_pass1.parquet (mtime 2026-05-01 17:43 EDT)
- Size: 28.2 MB
- Provenance: Phase 3 Stage 1 producer (PID 2566750, ran ~7.4hr May 1 EDT, source bbo_log_v4.csv.gz with match_facts_v3.csv match-start filter, 1.2M rows emitted)
- Producer code: arb-executor/data/scripts/build_g9_archive.py is unrelated; Phase 3 Stage 1 producer is in /tmp (need to identify and capture in Phase 1C)
- References: SESSION_HANDOFF.md ("Phase 3 Stage 1 — running in background as of session close")

### u4_phase3_stage1.log
- Source: /tmp/u4_phase3_stage1.log (mtime 2026-05-01 18:05 EDT)
- Size: 21 KB
- Provenance: companion log for the parquet above. Documents producer behavior, eviction events, throughput.

### bbo_log_v4.csv.gz
- Source: /tmp/bbo_log_v4.csv.gz (mtime 2026-04-17 15:15 EDT)
- Size: 839 MB
- Provenance: B-tier source per LESSONS E23. Single-writer append log, timestamp-monotonic. 5-col schema (timestamp, ticker, bid, ask, spread). Mar 20 - Apr 17 ET. 515M rows.
- Producer code: not yet identified in this session; was producing the live BBO stream during the bot's operational period

### kalshi_fills_history.json
- Source: /tmp/kalshi_fills_history.json (mtime 2026-04-29 21:25 EDT)
- Size: 4.5 MB
- Provenance: Server-side fill history pull per LESSONS A30. Producer: /tmp/fills_history_pull.py (will be captured in Phase 1C). 7,489 fills covering 2026-03-01 00:06 UTC to 2026-04-29 13:02 UTC. Re-runnable to extend coverage.
- Canonical for: per-fill operational analysis, closes F8/F9/F10/F17/A26 partially-or-fully per E29.

### match_facts_v3_metadata.csv
- Source: /tmp/match_facts_v3_metadata.csv (mtime 2026-05-01 00:27 EDT)
- Size: 909 KB
- Provenance: companion metadata to match_facts_v3.csv (which is already durable at arb-executor/data/match_facts_v3.csv). Producer: arb-executor/data/scripts/build_match_facts_v3.py.
- Note: match_facts_v3.csv (durable copy) and /tmp/match_facts_v3.csv have identical sha256 confirmed in inventory probe.

### validation4_ticks/*.bin
- Source: /tmp/validation4/step6_real/ticks/*.bin (mtime range Apr 15-23 EDT)
- Size: ~1.5 GB, 1,678 files
- Provenance: Primary tick-level data per LESSONS Section 4. Format: little-endian I-B-B (4-byte ts + 1-byte bid + 1-byte ask). Coverage: Mar 17 - Apr 17 ET (extends 3 days earlier than bbo_log_v4 which starts Mar 20).
- Producer code: /tmp/validation4/step6_real/extract_ticks.py + binary_splitter.py + fast_splitter.py (will be captured in Phase 1C)
- Consumers: replay.py, replay_v3.py, replay_v4.py, replay_v5.py (versioned strategy backtests). /tmp/extract_facts.py also reads from these bins (the producer of broken match_facts_full.csv per SESSION_HANDOFF "Don't trust"; the issue is in extract_facts.py logic, not the bins themselves).
- Status: bins are canonical primary tick data; do NOT re-run extract_facts.py per SESSION_HANDOFF.

## Verification

sha256 sums recorded in this manifest at copy time. Re-verify integrity by running:

  cd /root/Omi-Workspace/arb-executor/data/durable
  sha256sum *.parquet *.gz *.json *.csv *.log
  find validation4_ticks -name "*.bin" -type f | sort | xargs sha256sum | sha256sum

## What this manifest does NOT cover

- Smaller scripts and outputs from /tmp (Phase 1C, copied to /root/Omi-Workspace/tmp/ curated archive)
- Untracked files in /root/Omi-Workspace/tmp/ that already exist on durable disk but are not yet in git (Phase 1A — committed separately)
- The per_cell_verification/ DIFFER cluster fragmentation (Phase 1D — flagged in ROADMAP for separate resolution)


## Verification record (Phase 1B post-copy)

Single-file sha256 verification: all 5 files match between source and destination.

  u4_phase3_state_pass1.parquet  c8ce0f9c...  PASS
  bbo_log_v4.csv.gz              7a085362...  PASS
  kalshi_fills_history.json      bc658945...  PASS
  match_facts_v3_metadata.csv    3c546042...  PASS
  u4_phase3_stage1.log           fc7618eb...  PASS

Tick directory verification (relative-path aggregate sha256, 1,678 .bin files):

  Source aggregate (relative-path):       84dca1a1f0ac3dfea6133d1691e631e1943a736108724e7d76b9fda8bf3c8786
  Destination aggregate (relative-path):  84dca1a1f0ac3dfea6133d1691e631e1943a736108724e7d76b9fda8bf3c8786
  Source file count:                      1678
  Destination file count:                 1678
  Verdict:                                MATCH

Verified at: 2026-05-04T18:19:17Z



## G9 parquets (T17 producer output, T27 verification-passed)

Added 2026-05-04 (Session 6 T17 + T27). Consolidated from 60K source CSVs/JSONs in
arb-executor/data/historical_pull/ via build_g9_parquets.py at commit bd83412.
Verified by T27 verification probe (LESSONS C27 discipline): 9/9 checks passed including
row count parity, schema normalization, reconstruction equivalence on 10-market sample,
taker_side enum integrity, custom_strike round-trip, no all-null era columns.

| File | Size | Rows | sha256 |
|------|------|------|--------|
| g9_candles.parquet | 82M | 9,500,168 | e9756fe0a7075e3a0eae01c6b3f2b6e430cf9c501b9aadba7ae76a7f0ec2a7fc |
| g9_trades.parquet | 1.5G | 33,727,162 | 268f26a0b218e02498ad0ad07a3b5be07ce8aa8648749b7b0f64772867ad8971 |
| g9_metadata.parquet | 3.2M | 20,110 | 04622accb9e3c0b63681076c30175950a9ef20e5a4da05e72aa0ff0ad10bb230 |

Schema normalization: 2025-era bare names + 2026-era _dollars-suffixed names normalized
to bare canonical (per LESSONS F29). Era distribution: ~67% era-2025, ~33% era-2026.

Per LESSONS G19: candle minutes are sparse; yes_bid_close/yes_ask_close are 100%
populated, price_close/volume_fp/open_interest_fp are ~65% null (no-trade minutes).
Layer A consumers should use bid/ask as primary signal.

Producer: arb-executor/data/scripts/build_g9_parquets.py at commit bd83412.
Verification probe: T27 (this commit's parent for foundation-pointer purposes).

## Layer A v1 outputs (T29 producer output, gated on T21 coherence read)

Foundation pointer: T28 commit ea84e74 (G9 parquets).
Producer: arb-executor/data/scripts/build_layer_a_v1.py at commit 1398c39.
Output directory: arb-executor/data/durable/layer_a_v1/
Producer runtime: 60.7 min, clean exit (Session 6, May 4 2026).
Aggregation scope: 19,603 markets, 8,981,594 moments aggregated into 671 cells.

### cell_stats.parquet

- sha256: 20e9fcbb18f6079ef09e01fd959ea4f1647c7aa6603997ea4fba8c7c78dde290
- Size: 233804 bytes
- Content: 671 cells, ~80 metric columns, forward-bounce distribution per cell

### sample_manifest.json

- sha256: 39ab373a68214d997458754ca286516c7080935b1ea8a2e59f05f85866846031
- Size: 621246 bytes
- Content: Per-cell sampled tickers used in visual reproduction

### build_layer_a_v1.log

- sha256: ec73efb501668877a24d9475b41d5070db20bec448a8ede166d4de9eb4cc7050
- Size: 8656 bytes
- Content: Producer log

### Visual PNGs (15 files, 8758898 bytes total)

5 categories (ATP_MAIN, ATP_CHALL, WTA_MAIN, WTA_CHALL, OTHER) x 3 regimes (premarket, in_match, settlement_zone).

  - visual_ATP_CHALL_in_match.png: c836b6df4a1de80f5097d25c91ee7a1868b6dc73ddd7d6d80713d4ba43374769 (817187 bytes)
  - visual_ATP_CHALL_premarket.png: 60f36b3729aa55651e4cd8790ff5485d1f37101d0dcdd95f6db6b2c1de1d1655 (1131437 bytes)
  - visual_ATP_CHALL_settlement_zone.png: 0dd91c8ea359f13c3c6ce0fbdbd4abfacff8462ab9a859fb7a36b724ebc37e74 (717368 bytes)
  - visual_ATP_MAIN_in_match.png: 7e6ed084a07bea2826e65e86aa06b260fc0ffb0acd360cd5ed3fc6faffd12aab (944958 bytes)
  - visual_ATP_MAIN_premarket.png: f7f52e7aacfa5702d18aa571d3535aab4b83e9f9c1d89991535253a418bcf544 (868809 bytes)
  - visual_ATP_MAIN_settlement_zone.png: 7bb407b34db2bf56e68ef2654ae392eb54bdf8b24ac96aa2314ad9fdc83e4508 (279123 bytes)
  - visual_OTHER_in_match.png: ef053352d7ae2230dbcbd857c39e1a2c0018a6a3d918576739b3b3d8b9afdebc (44620 bytes)
  - visual_OTHER_premarket.png: 5c101ffb2a82890af261f1e36d026a2e7340f5540bd17fcb9c9ccb77fc351d00 (45046 bytes)
  - visual_OTHER_settlement_zone.png: 4b31fed2997f34fea4ff2daab23ad8ad73d7bf3cf818d4a7896e1a8837f33900 (45879 bytes)
  - visual_WTA_CHALL_in_match.png: f88268d37a7c15453c080aa138ba9839aea2d84543ebcbb18912753f7252e34a (891444 bytes)
  - visual_WTA_CHALL_premarket.png: 18bdda3e5cfb57aa5a666ea9d492844d0f9dba66397692f670e6dbf479b83252 (985868 bytes)
  - visual_WTA_CHALL_settlement_zone.png: df7b572e8a2350ec720df5ba2c0a33ef70631b2b743b93df53a8ba6d40260bf7 (47362 bytes)
  - visual_WTA_MAIN_in_match.png: b3bf670c54d93eff5f39b1ed4b11cb04c9c6a3a9d5cd16ca05b7126cf8893092 (984028 bytes)
  - visual_WTA_MAIN_premarket.png: 4a263f88304f77a51070f733ea0b47e4eb632331b684f5e8e246b1027f8521aa (892456 bytes)
  - visual_WTA_MAIN_settlement_zone.png: 380e779679846e39316211f8eef150599a6f92fde88e66cca5b10c3b55e8df5b (63313 bytes)

### Validity status

PENDING T21 coherence read. Outputs verified on-disk and sha256-pinned, but methodology validation gate (the five-check sanity scan from ROADMAP T21) has not run. Downstream Layer B / Layer C analyses must not consume these outputs until T21 passes.

