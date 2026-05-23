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

PASSED T21 coherence read 2026-05-04 (commit faf51d9). 4 PASS / 2 INCONCLUSIVE / 0 FAIL. Cleanly passing checks: Check 2 premarket-vs-in_match, Check 3 settlement asymmetry, Check 4 category sanity, Check 6 YES/NO fold symmetry. Informatively inconclusive: Check 1 (hypothesis-shape mismatch -> LESSONS B20), Check 5 (volume_intensity in_match collapse -> LESSONS F30). Downstream Layer B (T31b) cleared to consume.

## Layer B v1 outputs (T31b-gamma producer output, gated on T31c coherence read)

[#layer-b-v1-outputs-t31b-gamma-producer-output-gated-on-t31c-coherence-read](#layer-b-v1-outputs-t31b-gamma-producer-output-gated-on-t31c-coherence-read)

Foundation pointer: T28 commit ea84e74 (G9 parquets) + T29 commit 1398c39 (Layer A v1 cell_stats + sample_manifest).
Producer: arb-executor/data/scripts/build_layer_b_v1.py at commit 28e8ab7.
Output directory: arb-executor/data/durable/layer_b_v1/
Producer runtime: 79.5 min, clean exit (Session 7, 2026-05-05 ET).
Aggregation scope: 355 cells processed (of 356 in-scope substantial); 1 cells excluded by 50-trajectory threshold per spec Decision 2 patch 3. 278208 total entry moments evaluated across the 54-policy grid.

### exit_policy_per_cell.parquet

[#exit_policy_per_cellparquet](#exit_policy_per_cellparquet)

- sha256: d94bc56c7909738a8f8ad8ae388102b34fe81909d493015cb90d3f8390262f92
- Size: 646464 bytes
- Row count: 19170 rows (one per (cell, policy) tuple)
- Schema: 21 columns per spec Decision 4 (channel, category, entry_band_lo, entry_band_hi, spread_band, volume_intensity, policy_type, policy_params, n_simulated, n_fired, n_horizon_expired, n_settled_unfired, fire_rate, capture_mean, capture_p10/p25/p50/p75/p90, median_time_to_fire, capital_utilization)
- Compression: snappy

### Validity status

[#validity-status](#validity-status)

PASSED T31c coherence read 2026-05-05 ET (commit 5cf45e0). 4/4 gating-checks PASS:
- Check 1 (capture bounded by physical limits): 217 fired trajectories spot-checked across 10 (cell, limit_policy) pairs, 0 violations. Floor min capture_p10 across all = -0.98 >= -1.00.
- Check 2 (fire rate monotonic): 355/355 cells (100%) exhibit monotone non-increasing fire rate across the limit-policy grid.
- Check 3a (limit-policy capture_p90 trend in positive-bounce cells): 266/318 cells (83.6%) positive-rho with median Spearman +0.992. Layer B inherits Layer A MFE structure faithfully via limit policies.
- Check 4 (premarket vs in_match): 6,048 matched (category, entry_band, spread, volume, policy) tuples, median delta in_match - premarket = +0.0087, Wilcoxon signed-rank p = 9.7e-232.

Plus 1 informative-only Check 3b (time-stop horizon trend): 137/354 cells (38.7%) positive-rho, median Spearman -0.321. This is the empirical signature of mean reversion per LESSONS B21 (MFE vs endpoint-capture metric distinction); time-stop endpoint trend is structurally different from Layer A bounce MFE and is reported for completeness, not as a gating check.

Downstream Layer C (G11) cleared to consume.

### coherence_report.md

[#coherence-report-md](#coherence-report-md)

- sha256: 72f1747b5502932f0099b3cbb7e62cabc906dfd89835bc2f9f6138c0e9aab121
- File: data/durable/layer_b_v1/coherence_report.md
- Producer: data/scripts/check_layer_b_v1_coherence.py at commit 5cf45e0
- Spec: layer_b_spec.md Validation Gate section (post-T31a patches 5, 7, 8)

## Rung 0 outputs (T39 recomputation ladder Rung 0; ROADMAP T39, recomputation_ladder.json problem=P1)

[#rung-0-outputs-t39-recomputation-ladder-rung-0](#rung-0-outputs-t39-recomputation-ladder-rung-0)

Foundation pointer: T37 per_minute_features.parquet sha256 9fde4b5d30e56d99efa0637fe042cb6ca4505274e85e42769b4cedc25e3e5ff4 (checkpoint 3) + g9_trades.parquet (trade-tape entry/peak) + g9_metadata.parquet (binary-outcome filter + settlement value).
Spec: docs/rung0_cell_economics_spec.md at commit 87103d0d (v1.1, 36-column schema).
Producer: arb-executor/data/scripts/build_rung0_cell_economics.py at commit 10322a8f (base 356f25f4; pandas3/pyarrow24 compat 52edf132; find_t20m_anchor float-precision anchor fix 10322a8f).
Output directory: arb-executor/data/durable/rung0_cell_economics/
Producer runtime: 4h 45m 03s Phase 3 re-run, clean exit (2026-05-15 ET; attempt #1 halted at C37 gate on 21 int()-truncation boundary violations, fixed and re-run strictly).
Coverage: 14,033 emitted / 19,614 binary-outcome tickers (71.5%); 5,581 dropouts (dominant no_trade_near_t20m=3,390, the strict trade-tape entry cost per LESSONS A37). 72/72 cells populated; 54 cells n>=100, 62 n>=50.

### cell_economics.parquet

[#cell_economicsparquet](#cell_economicsparquet)

- sha256: 6fdd019d08722d0afb5688181fb60394d73dc2b05765af74d6c5675edd17c992
- File: data/durable/rung0_cell_economics/cell_economics.parquet
- Size: 1721074 bytes
- Row count: 14033 rows (one per qualifying N — trade-tape T-20m anchor within +/-2min, band 5-95c, binary outcome)
- Schema: 36 columns per spec rung0_cell_economics_spec.md commit 87103d0d (ticker/event/category, t20m trade anchor, 5c price_band, cell_key, band_n_count, phase_state_at_t20m, dual peak bid+trade [full vs pre_resolution], bounce columns, first_extreme_touch_ts, realized_at_settlement, premarket volume/OI/context, n_minutes_premarket/first_trade_ts/n_trades_pre_t20m); all timestamps tz-aware ET per G21
- Compression: snappy
- Date: 2026-05-15 ET

### Validity status

[#validity-status-rung0](#validity-status-rung0)

PASSED C37 pre-replace gate 2026-05-15 ET (producer commit 10322a8f). 5/5 hard gates PASS, run in-loop AND independently re-validated against the on-disk .new bytes before os.replace:
- Gate 1 anchor_consistency: 0 violations (t20m_trade_ts within +/-2min of match_start_ts - 20min; float-precision after 10322a8f fix).
- Gate 2 band_exclusion: 0 violations (no extreme 0.00-0.05 / 0.95-1.00 bands).
- Gate 3 peak_monotonicity: 0 violations across all 6 sub-checks (peak_bid/trade full >= pre_resolution >= entry).
- Gate 4 settlement_consistency: 0 violations (realized_at_settlement = settlement_value_dollars - t20m_trade_price exact).
- Gate 5 tz_correctness: all timestamp columns tz-aware ET.

Headline (top cell by mean peak_bid_bounce_pre_resolution): WTA_CHALL__0.30-0.35 n=55 mean +0.3398. Diagnostic peak_bid_bounce_full and A39 ROI complement in validation_report.md.

### validation_report.md

[#validation_report-md-rung0](#validation_report-md-rung0)

- sha256: 8f1ec4ffe931bf0bb304852b3735c2d4b209baf4dc620ee10ee02bc561fffadf
- File: data/durable/rung0_cell_economics/validation_report.md
- Producer: gen_rung0_report.py (deterministic report generator over cell_economics.parquet)
- Spec: docs/rung0_cell_economics_spec.md Section 6 hard gates (commit 87103d0d)
- Lessons earned this arc: LESSONS A37 (strict-entry coverage cost), A38 (dual-peak vs settlement saturation), A39 (cents vs ROI ranking)

## n_profile_v1 (Phase-3 full-corpus, gate-validated foundation)

Foundation pointer: per_minute_features T37 ckpt-3 (inputs sha256 9fde4b5d). Producer commit: a28840e (Pass-1 del + gc-every-200 OOM remediation, validated at full-corpus heavy-tail scale). ANALYSIS_LIBRARY lineage commit: c76eee5. Run: 2026-05-17 20:56 → 2026-05-18 02:37 ET (~5h41m, detached). Spec: docs/n_profile_v1_spec.md (commit chain to ef3add7; both_sides_active_minutes corpus-scoped per LESSONS G23). Lessons this arc: F35, G23, C38.

### n_profile.parquet

- sha256: a7ed11550e8226f18c22069cc5937d35b184e7f0d2a9264435604a0270c1837e
- Size: 3423678 bytes
- Rows: 19614 (45 cols, one row per binary N, 0 dropouts, unique tickers == rows — gate-1 parity exact)
- File: data/durable/n_profile_v1/n_profile.parquet
- Producer: data/scripts/build_n_profile_v1.py at commit a28840e
- Source: per_minute_features.parquet (T37 ckpt-3, sha256 9fde4b5d) + g9_trades + g9_candles + g9_metadata, per-ticker pushdown I/O
- Validity status: PASSED — all 7 gates at full corpus 2026-05-18 (gate1 row-parity 0-dropout, gate2 0 orphans, gate3 phase-partition-exhaustiveness a/b/c all 0, gate4-7 0 violations), re-validated vs on-disk .new bytes pre-replace (C37). OOM remediation validated at full-corpus heavy-tail scale (~5.7h continuous watch, bounded ~700-720MB plateau, zero OOM).
- Companions: n_profile.meta.json (producer_commit a28840e, inputs pinned), validation_report.md (7-gate PASS table + F35 match_start_method section)

## inmatch_bounce_surface_v1 (Phase-2 full-cohort, gate-validated — first analytical deliverable)

Foundation pointers: n_profile.parquet sha256 a7ed1155 (lineage c76eee5 / MANIFEST c9a0f3e) + per_minute_features.parquet sha256 9fde4b5d (T37 ckpt-3). Spec: docs/inmatch_bounce_surface_v1_spec.md (11dce1c; v0.2 G2-corrected 85118d4; v0.3 classifier-fixed 0e94959). ANALYSIS_LIBRARY lineage: this commit. Run: Phase-2 full cohort 2026-05-18 (~40min). Layer-A-equivalent per B16 (descriptive; exit-optimization is the defined Phase-2 interface). Lessons: G1/G2 gate-spec defects probe-corrected (v0.2); brittle-classifier false-negative fixed (v0.3).

### surface.parquet

- sha256: 14241db05183ff214aec80b0cbf72d3d194c931d6e8548ec493941bdf8a5f655
- Size: 65903 bytes
- Rows: 800 (per price_level_bin × horizon × category; pooled ALL + 4 strata)
- File: data/durable/inmatch_bounce_surface_v1/surface.parquet
- Producer: data/scripts/build_inmatch_bounce_surface_v1.py — surface built at 85118d4 (v0.2 validated Phase-2); validation_report.md regenerated at 0e94959 (v0.3 Spearman-classifier fix; surface byte-identical, sha unchanged)
- Source: n_profile.parquet (sha256 a7ed1155, cohort screen) + per_minute_features.parquet (sha256 9fde4b5d, T37 ckpt-3, bounce source), per-ticker pushdown
- Validity status: PASSED — all 7 gates at full cohort 2026-05-18 (G1 phase-aware 7369+14==7383, G2 regime-purity non_in_match=0, G3 A38 ratio 1.866, G4-G7), C37 triple-consistent (on-disk == meta == DONE-log). Memory bounded (producer VmHWM peak 1184 MB < 1700). Science reproduces probe-1/2 (Spearman cents −0.995, roi +0.722, cents↔ROI inversion present).
- Companions: surface.meta.json (producer_commit 85118d4, both inputs_sha256, gates_passed:true), validation_report.md (regenerated by v0.3 0e94959 — corrected Spearman shape classifier; pooled-30min cents+ROI curves, A38 saturation, per-category covariate, SCALP sensitivity)

## spike_volatility_map_v1 (T42 four-category descriptive atlas, gate-validated, strategy-anchored)

Foundation pointers: n_profile.parquet sha256 a7ed1155 (lineage c76eee5 / MANIFEST c9a0f3e) + per_minute_features.parquet sha256 9fde4b5d (T37 ckpt-3) + g9_trades.parquet (T28 ea84e74, spike measurement source). ANALYSIS_LIBRARY lineage: Section 2 entry at commit 64a8ab1 + Section 4 finding entry same commit. Canonical reproducible producer: data/scripts/build_spike_perN.py at commit c5e377f (reproduces ATP_MAIN + WTA_MAIN spike per-N parquets byte-identical to commit 9912660 artifacts). Atlas arc: six commits 481de7f → 75603f4 → c5e377f → ec1f593 → d038cb3 → d99c6e9 (2026-05-19 → 2026-05-20 ET). Layer-A-equivalent per B16 (descriptive market measurement; NO predictive claim, NO Layer C economics). Operationally distinct from inmatch_bounce_surface_v1 (sibling, not nested): atlas is per-cell × exit-or-hold ROI from T-20m taker anchors; surface is band-free in-match bounce as continuous market property.

Atlas files are git-tracked (small enough): all 16 parquets + 4 LOCKED_DOWN.md + PAIRING_DIAGNOSTIC.md + CROSS_CATEGORY_MAP.md (pre-Challenger, deprecation header pending Stage 0 Commit 7). Three-axis caveat (load-bearing for every headline number) documented verbatim in each LOCKED_DOWN.md and SESSION_HANDOFF.md.

### atp_main_spike_perN.parquet

- sha256: 621c86340b90653e384720b1f10c4617f9fbd64d5f177cbfab0d2153c9ea960f
- Size: 343312 bytes
- Rows: 4137 (per-N rows, one per qualifying ATP Main binary market; 16 cols)
- File: data/durable/spike_volatility_map/atp_main_spike_perN.parquet
- Producer: data/scripts/build_spike_perN.py at commit c5e377f, --category ATP_MAIN
- Source: n_profile.parquet (cohort screen) + per_minute_features.parquet (entry-anchor context) + g9_trades.parquet (spike measurement walk over [t20m_trade_ts, settlement_ts])
- Validity status: LOCKED — landed at commit 481de7f (first ATP_MAIN descriptive lock); canonical producer at c5e377f reproduces this byte-identical.
- Schema: ticker, event_ticker, partner_ticker, anchor_price, anchor_ts, settlement_ts, settlement_value, old_metric_cents, raw_max, raw_max_ts, size_qual_max_250, spike_cents, spike_pct, truncation_delta_cents, time_to_max_min, drop_reason

### wta_main_spike_perN.parquet

- sha256: 299b52df87841dff0a065aba264b7b4311c834f80bd8bfee9f90f38ccbca7f98
- Size: 306241 bytes
- Rows: 3683 (per-N rows, 16 cols)
- File: data/durable/spike_volatility_map/wta_main_spike_perN.parquet
- Producer: data/scripts/build_spike_perN.py at commit c5e377f, --category WTA_MAIN
- Validity status: LOCKED — landed at commit 75603f4 (WTA_MAIN descriptive lock); canonical producer at c5e377f reproduces this byte-identical.

### atp_chall_spike_perN.parquet

- sha256: e28faed5c8d19e9c09ab99a54c724b03bf38bc9c983fdf1956111a86bffa68db
- Size: 438587 bytes
- Rows: 5326 (per-N rows, 16 cols; highest-density category at 48.86 N/day across 109 trading days)
- File: data/durable/spike_volatility_map/atp_chall_spike_perN.parquet
- Producer: data/scripts/build_spike_perN.py at commit c5e377f, --category ATP_CHALL
- Validity status: LOCKED — landed at commit ec1f593.

### wta_chall_spike_perN.parquet

- sha256: ba2e5ef2b9e3a7df681d9e62e259bb583bab6b008326228c215069efc495640f
- Size: 86196 bytes
- Rows: 887 (per-N rows, 16 cols; smallest cohort, shortest season)
- File: data/durable/spike_volatility_map/wta_chall_spike_perN.parquet
- Producer: data/scripts/build_spike_perN.py at commit c5e377f, --category WTA_CHALL
- Validity status: LOCKED — landed at commit d038cb3 (closes the four-category lock).

### Descriptive per-cell parquets (12 files: 4 categories × 3 resolutions)

Per-cell hindsight-optimal exit-or-hold tables. Three cell resolutions reported side-by-side per Plex round-2 methodology recommendation (1c / 2c / 3c) — neither "more correct," they describe corpus pay-outs at three cell-granularity levels (90/45/30 cells per category respectively). 16 columns uniform schema: cell_label, cell_id, N, anchor_min, anchor_max, reachable_X_max, best_exit_X, hit_rate_at_best, best_exit_sum, hold_to_settle_sum, best_sum, rule, median_anchor_cents, capital_deployed_$, roi_pct, cts_deployed, best_sum_per_ct_c. (Two files — atp_main_descriptive_1c and atp_main_descriptive_3c — carry 17 cols due to producer drift on the ATP_MAIN run; non-load-bearing extra column, schema otherwise uniform.)

- atp_main_descriptive_1c.parquet: sha256 2d836bf8504d7c77bd50cc152c7057bfbe49b25c08baf3b99864b95bffcd6427, 18755 bytes, 90 rows (17 cols), commit 481de7f
- atp_main_descriptive_2c.parquet: sha256 d0e0292ffca40535721a864e6c2a4ec245a0e14cf10880d369f0d8dd9b288895, 14287 bytes, 45 rows, commit 481de7f
- atp_main_descriptive_3c.parquet: sha256 acd6b6ecc8c250ff863578d7bd5ea24aed3456078f2c13c9ff854ac8c583f552, 13700 bytes, 30 rows (17 cols), commit 481de7f
- wta_main_descriptive_1c.parquet: sha256 e275ea3f6be1bb17fcd9e9b791040ce4bde19c67711c47833b5e4cc570bfd672, 17778 bytes, 90 rows, commit 75603f4
- wta_main_descriptive_2c.parquet: sha256 6ff0a4c76f8861447ceede8fbf965473a006a4a3cfd82320d1065cbe73734c4b, 14308 bytes, 45 rows, commit 75603f4
- wta_main_descriptive_3c.parquet: sha256 dddfa7444f0d20d756fce5bea1a2ed4269ee78a039b2c3ec8dcb8903589778f4, 12917 bytes, 30 rows, commit 75603f4
- atp_chall_descriptive_1c.parquet: sha256 00d94357cc197328b44bc483c1e18d65d70d4212ab7c4a00328ff978fcb100dd, 17985 bytes, 90 rows, commit ec1f593
- atp_chall_descriptive_2c.parquet: sha256 3dffdcb3483ef1b3b116347e52627fd0eaba5b68edacb17f0363e331cd7ef364, 14292 bytes, 45 rows, commit ec1f593
- atp_chall_descriptive_3c.parquet: sha256 783ffeca47a902c65cbcbf56037c6557f9f63bf35af57ca6432ce4f900cb9c18, 12926 bytes, 30 rows, commit ec1f593
- wta_chall_descriptive_1c.parquet: sha256 758afdd2b3f134cbd5005b3294582f4bc83b9f34f0f8c70637742c698da560e3, 16830 bytes, 90 rows, commit d038cb3
- wta_chall_descriptive_2c.parquet: sha256 ac38032df6c89949048cba119daf64af1528f68157bfb66e793e60055b4d3345, 14024 bytes, 45 rows, commit d038cb3
- wta_chall_descriptive_3c.parquet: sha256 91f26b786731495ad1e899e458dcaccd5111e91a01acfc605f7ba8e0fe2f8e6c, 12821 bytes, 30 rows, commit d038cb3

### Atlas documentation (6 markdown files)

Methodology and findings documentation — the canonical reference for what each per-N parquet contains and how to read it.

- ATP_MAIN_LOCKED_DOWN.md (6759 bytes, commit 481de7f) — ATP_MAIN methodology lock + headline numbers + three-axis caveat verbatim
- WTA_MAIN_LOCKED_DOWN.md (4353 bytes, commit 75603f4) — WTA_MAIN equivalent
- ATP_CHALL_LOCKED_DOWN.md (3586 bytes, commit ec1f593) — ATP_CHALL equivalent
- WTA_CHALL_LOCKED_DOWN.md (3659 bytes, commit d038cb3) — WTA_CHALL equivalent
- PAIRING_DIAGNOSTIC.md (6812 bytes, commit d99c6e9) — event-level pairing analysis, 79.3% paired (6,208 of 7,825 events), per-category breakdown
- CROSS_CATEGORY_MAP.md (6111 bytes, pre-Challenger; flagged stale; deprecation header pending Stage 0 Commit 7)


## premarket_tape_v1 (Track 1 microstructure-only premarket substrate)

Foundation pointer: per_minute_features T37 ckpt-3 (sha256 9fde4b5d30e56d99efa0637fe042cb6ca4505274e85e42769b4cedc25e3e5ff4). Producer: data/scripts/build_premarket_tape_v1.py at commit a6734c3. Run: 2026-05-22 04:04 UTC (~51s wall; arrow-native row-group streaming over 94 row-groups, incremental ParquetWriter; peak RSS 493 MB, 35% of 1.4 GiB gate). Filter: regime == premarket AND time_to_match_start_min in [20, 240] (T-4h to T-20m window). Scope: foundation universe (17,979 tickers with a qualifying premarket window of 19,207 total foundation tickers; 1,228 skipped for no qualifying window) — a strict SUPERSET of the atlas 14,033-ticker universe (atlas 100% covered; 3,946 foundation-only tickers retained for upstream microstructure edge-case dynamics). Descriptive Track 1 substrate (microstructure-only); NO FV anchor join (Track 2 is a separate workstream). Lineage note: App stopped at validation per overnight protocol when Gate 3 surfaced a prompt scope ambiguity (Step 2 producer logic = foundation universe vs Gate 3 = atlas universe); operator resolved to foundation scope (A). Gate 5 size band (500MB-2GB) was a prompt order-of-magnitude error.

### premarket_tape_v1.parquet

- sha256: ff2a63d9951d1a3d6b80044106c96ca9fdfd8d3951590e73eec1b46209c5a214
- Size: 86344070 bytes
- Rows: 2064211 (one per (ticker, minute) in T-4h to T-20m window; 92 cols = 88 source + 4 convenience)
- File: data/durable/per_minute_universe/premarket_tape_v1.parquet (NOT git-tracked — size; sha256 here per durable-corpus discipline, mirrors per_minute_features.parquet)
- Producer: data/scripts/build_premarket_tape_v1.py at commit a6734c3
- Source: per_minute_features.parquet (T37 ckpt-3, sha256 9fde4b5d), arrow-native row-group streaming filter
- Coverage: 17,979 distinct tickers / 8,993 distinct event_tickers; atlas 14,033/14,033 (100.0%) + 3,946 foundation-only
- Convenience cols: premarket_minute_index (backward minute count from T-20m, 0 at T-20m up to 220 at T-4h), time_to_t20m_min (float, ttm-20), in_t4h_t2h_subwindow (ttm in [120,240]), in_t2h_t20m_subwindow (ttm in [20,120])
- Validity status: PASSED — 5 gates: gate1 regime_pure (premarket only), gate2 window_in_range ([20,240]), gate4 paired_arb_gap_present (16.34% null), gate3 ticker_coverage resolved to foundation scope by operator, gate5 size resolved as prompt mis-estimate (41.8 bytes/row == foundation 43.6 bytes/row density). 493 MB peak RSS bounded.
- Companions: premarket_tape_v1_run_summary.json


## fv_history/ (book_prices archive — Tennis cross-book FV poll history)

- Source: tennis.db book_prices table (live rolling ~32-day store with composite PK (event_ticker, book_key, polled_at) preventing INSERT-OR-REPLACE collapse). Schema: 12 cols (event_ticker, book_key, player1_name, player2_name, book_p1_fv_cents, book_p2_fv_cents, raw_odds_p1, raw_odds_p2, vig_pct, sport_key, commence_time, polled_at). polled_at is ISO text "YYYY-MM-DD HH:MM:SS".
- Layout: data/durable/fv_history/by_month/YYYY-MM.parquet (monthly partitioned, append-only). Companion data/durable/fv_history/state.json tracks high-water-mark polled_at for incremental runs. Parquets + state.json are NOT git-tracked (size/volatility; mirrors per_minute_features durable discipline — only producer + this MANIFEST entry + run_summary in git).
- Initial snapshot: 2026-05-23 via archive_book_prices_v1.py --mode initial. 13,155,461 rows, polled_at range 2026-04-19 18:33:45 → 2026-05-23 13:01:31, 914 distinct event_tickers, 35 distinct book_keys. Partitions: 2026-04.parquet (3,088,738 rows), 2026-05.parquet (10,066,723 rows at snapshot). 571s wall, peak RSS 314 MB.
- Validation: archive_total == DB COUNT(*) WHERE polled_at <= archive_max (13,155,461; the DB is live so this snapshot-bounded check is the correct invariant). Per-event spot-check PASS. A validation --mode incremental run (stream-merge append path, the cron's exact code) appended 88,593 rows to 2026-05 (peak RSS 253 MB, 193s); current archive total 13,244,054, last_archived_ts 2026-05-23 13:49:24.
- Cron: 02:30 UTC daily (systemd cron active), incremental mode appends rows where polled_at > last_archived_ts to >> /var/log/archive_book_prices.log.
- Purpose: preserves cross-book FV anchor history before the live tennis.db rolling ~32-day window deletes it. Enables FV-overlap subset analysis for Track 2 (FV-conditional premarket dynamics) on the ~12-day overlap with the atlas corpus (book_prices start 2026-04-19 vs atlas end ~2026-05-01) plus forward accumulation. Every day without archive shrinks this overlap as the trailing edge of the rolling window deletes the oldest 24h.
- Producer: data/scripts/archive_book_prices_v1.py at commit 85aee72. Memory-safe streaming (per-month ParquetWriter; stream-merge for incremental appends) — deviation from the drafted whole-month-buffer producer, which would have OOM'd on the 10M-row month; output contract unchanged. High-water-mark is the max polled_at actually written (not a racing SELECT MAX()). See run_summary_initial.json "deviations_from_drafted_producer" for detail.
- Companion: data/durable/fv_history/run_summary_initial.json (run_summary_incremental_<date>.json may follow for daily runs).


## fv_overlap_join_v1 (Track 2 substrate — premarket_tape_v1 ⨯ fv_history FV anchor)

Producer: data/scripts/build_fv_overlap_join_v1.py at commit a0700b8. Run 2026-05-23 (~319s wall, peak RSS 603 MB). Joins premarket_tape_v1.parquet with the fv_history archive (book_prices) to attach a per-leg per-minute cross-book consensus fair value AS OF each minute, plus fv_delta, partner FV and paired_fv_sum. Analytical foundation for Track 2 (FV-conditional premarket dynamics).

### fv_overlap_join_v1.parquet

- sha256: 58cb0d894d83d782f6a793a060b964565e5484c72da4d01b9a35e43f5cf14e1a
- Size: 7432699 bytes
- Rows: 154367 (premarket_tape_v1 rows with minute_ts within FV-archive coverage, i.e. >= 2026-04-19 22:33:45 UTC)
- File: data/durable/per_minute_universe/fv_overlap_join_v1.parquet (NOT git-tracked — size; sha256 here per durable-corpus discipline, mirrors premarket_tape_v1)
- Sources: premarket_tape_v1.parquet (sha256 ff2a63d9), fv_history/by_month/{2026-04,2026-05}.parquet
- New columns (9): fv_consensus_own, fv_source {pinnacle|aggregate|betexplorer|unavailable}, num_books_in_window, confidence_weight {0.95|0.80|0.50|null per fv.py}, fv_consensus_partner, fv_delta_at_last_traded (price_close−FV, trade-print minutes only), fv_delta_at_mid (diagnostic only — NOT a primary signal), paired_fv_sum, fv_join_minute_ts
- Join: as-of carry-forward per tier within fv.py freshness (pinnacle/aggregate 1800s, betexplorer 3600s); polled_at parsed America/New_York → UTC epoch (verified via match_start gap test, median +78min ET vs −162min UTC). Tiers = fv.py pinnacle→aggregate(≥3 books)→betexplorer; tier-5 paired-sum intentionally EXCLUDED (runtime fallback, circular w.r.t. Kalshi price). Leg→side via last-name[:3] bijection on book_prices player1/2_name + name_cache fallback.
- Validation: gate1 rowcount PASS; gate2 null<50% PASS under intended denominator (bp-events 0.267; per-category ATP_MAIN 0.198 / WTA_MAIN 0.282 / ATP_CHALL 0.322 [betexplorer tier-3]); gate3 pinnacle 67% of populated PASS; gate4 paired_fv_sum mean 100.000 PASS; gate5 fv_delta median +1.0c, p5/p95 [−2.5,+4.4] PASS.
- Coverage gaps (NOT substrate defects): (a) 463/836 FV-window events absent from book_prices (no odds-API coverage); (b) WTA Challenger has ZERO FV — betexplorer.py CHALLENGER_URLS lists only 7 men's tournaments, no women's URLs (scraper-coverage F-gap; operator decision); (c) ATP Challenger limited to those 7 tournaments; (d) aggregate tier dormant (pinnacle always present when ≥3 Main books poll).
- Confidence semantics: downstream Track 2 should weight FV-conditional signals by confidence_weight so betexplorer (Challenger, 0.50) is not treated as equal to Pinnacle (Main, 0.95).
- Companions: data/durable/per_minute_universe/fv_overlap_join_v1_run_summary.json; example chart docs/analysis/premarket_dynamics_v1/example_premarket_chain_v3_KXATPMATCH-26APR26FONJOD.{png,md}


## scope_a corpus premarket map (per_minute_distributions_v1 + per_event_fingerprint_v1)

Producer: data/scripts/build_premarket_scope_a_v1.py at commit f33e25e. Run 2026-05-23 (~221s wall, peak RSS 1424 MB — see note). Corpus-wide descriptive map over the atlas universe (14,033 N / 7,825 events), T-4h to T-20m, stratified by category x anchor_regime (9 x 10c bands). Base = premarket_tape_v1 (full atlas); FV layered from fv_overlap_join_v1 (~3.5% of events). Foundation for Scope B regime classification, Plex Round 5, and the bid-laying policy spec.

### per_minute_distributions_v1.parquet

- sha256: dd0cb3dd4fd374d418538c6c49c978e50e75541c714c54335b9f9b929996b2e6
- Size: 1378285 bytes ; Rows: 7956 (221 min x 4 category x 9 anchor_regime, all cells populated)
- File: data/durable/per_minute_universe/per_minute_distributions_v1.parquet (NOT git-tracked — durable, sha256 here)
- One row per (time_to_match_start_min x category x anchor_regime): n_observations + mean/median/p10/p25/p75/p90/std for yes_bid/ask/spread/mid (cents), price_close availability + mean/median, volume + taker_flow + paired_arb_gap_maker + bid/ask consumption velocity stats, open_interest, and FV stats (fv_consensus_own, fv_delta_at_last_traded) where covered.

### per_event_fingerprint_v1.parquet

- sha256: b5dbf391d11778fe5c93ae469bb144f2cb0f1cdcb0aaba8108163d75c7ac2c95
- Size: 890801 bytes ; Rows: 7825 (6208 paired + 1617 singleton; 2*paired+singleton = 14,033 atlas N)
- File: data/durable/per_minute_universe/per_event_fingerprint_v1.parquet (NOT git-tracked)
- One row per atlas event: per-leg trajectory features (minute/trade counts, total volume, spread summary, wide-spread minutes, max abs consumption velocities, mid_t4h/mid_t20m/mid_drift, FV coverage + fv_delta, volume_burst_concentration), paired distortion extremes, has_fv_coverage.

- Source: premarket_tape_v1.parquet (sha256 ff2a63d9) + fv_overlap_join_v1.parquet (sha256 58cb0d89) FV layer; atlas membership/anchor from the 4 spike_perN parquets (anchor_price in dollars, x100 for cent banding).
- Headline patterns (see scope_a_corpus_map_findings.md): mid-drift is a clean monotonic ~symmetric function of anchor regime (~+/-11c at the extremes, ~0 at coin-flip), near-identical across categories; spread tails widen into T-20m; large paired distortions ~2x more frequent on Challenger than ATP_MAIN.
- Memory note: in-memory build peaked 1.42 GB RSS (exceeded the 1.2 GB run-gate; completed cleanly with headroom on 1.9 GB + 2 GB swap; conservative gate, not load-bearing). Future expanded-atlas re-runs may need a streaming rewrite. See scope_a_v1_run_summary.json deviations + future_rebuild_note.
- Companions: data/durable/per_minute_universe/scope_a_v1_run_summary.json; docs/analysis/premarket_dynamics_v1/scope_a_corpus_map_findings.md


## Path B premarket fill mechanics (path_b_per_n_fill_results_v1 + path_b_per_regime_fill_summary_v1)

Producer: data/scripts/build_path_b_fill_mechanics_v1.py at commit 884e951. Run 2026-05-23 (~15s wall, peak RSS 762 MB). Measures, for each atlas N x (placement_minute, bid_offset) cell, whether a maker bid at anchor_price - offset would have filled by natural premarket trajectory (price_close <= bid OR yes_ask_close <= bid) between placement and T-20m. Pure fill mechanics: no PnL, no exit logic. Downstream of locked atlas T42 (d99c6e9); Axis 2 (entry-side improvement) per G22. Doctrine A39/B16/B25/G22.

### path_b_per_n_fill_results_v1.parquet
- sha256: 603ac54a4410837cec8891719ceaf447c6987ee667cb05e7d36758cb2bb23e62 ; Size: 835964 bytes ; Rows: 589386 (14033 N x 42 cells)
- File: data/durable/per_minute_universe/path_b_per_n_fill_results_v1.parquet (NOT git-tracked)
- Cols: ticker, event_ticker, category, anchor_price_cents, anchor_regime, placement_minute, bid_offset_cents, bid_price_cents, fill_outcome, fill_minute.

### path_b_per_regime_fill_summary_v1.parquet
- sha256: d9e2c3c55c6d7fb5d93beeddfde8a40f1298b841a0547d3743e14cd21e64e37e ; Size: 45355 bytes ; Rows: 1512 (4 cat x 9 regime x 6 placement x 7 offset)
- File: data/durable/per_minute_universe/path_b_per_regime_fill_summary_v1.parquet (NOT git-tracked)
- Cols: category, anchor_regime, placement_minute, bid_offset_cents, n_tickers_in_stratum, fill_rate, mean_fill_minute, median_fill_minute, expected_improvement_cents (= fill_rate x bid_offset).

- Source: premarket_tape_v1.parquet (sha256 ff2a63d9) + atlas membership/anchor from 4 spike_perN parquets.
- Gates: 1 rowcount PASS (589386); 2 coverage PASS (exact per-cat N, 9 regimes); 3/4 fill-rate sanity PASS (majority; exceedances are the prompt-anticipated favorite/underdog drift asymmetry); 5 monotonicity 216/216=100% PASS.
- Headline: expected entry-improvement rises monotonically with anchor regime -- heavy favorites (r85_94) ~6.3-7.0c/N via 15c offsets (books drift up ~11c), deep underdogs (r05_14) ~1.0-1.2c via 2-3c offsets only (books drift down to anchor). Corpus hindsight ceiling 2.46c/N; best single uniform cell (T-240, 15c) 2.25c/N. Earlier placement weakly dominates.
- Caveats: hindsight-optimal (live loses to per-event placement uncertainty); minute-cadence fill (no sub-minute/queue); fill realism downstream (Axis 1/B25) separate; entry-side ONLY (atlas T42 owns exit).
- Companions: data/durable/per_minute_universe/path_b_v1_run_summary.json ; docs/analysis/premarket_dynamics_v1/path_b_fill_mechanics_findings.md
