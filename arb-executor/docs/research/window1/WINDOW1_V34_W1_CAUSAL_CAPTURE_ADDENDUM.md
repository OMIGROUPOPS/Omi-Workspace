# V34-W1 Causal Capture Measurement Addendum

Package commit: `e56d79a2aee1f392b3bee5a0adad099c7f011976`.

This measurement replays the frozen V34 dual-side residency machine without changing its policy. Each event begins at its first two-sided book and ends at the PRE-MATCH edge selected from `REAL_START_LEDGER_V3` by `exact_start_utc`, else `known_live_by_utc`, else `schedule_bound_utc`. The hard edge admitted zero later state updates, rest walks, takes, fills, or cap arms.

The operator-supplied short identity `84b455c5` does not resolve as a Git object after fetch and object census. It is not used as an operative binding. Git path history binds the actual 804-row ledger to commit `224417da642a9f378a0d83f76edffe9890cb4a6f`, SHA-256 `1d7fe6a56837ceb0c0b8c932a05daecacc0cefbea94384e16c84975f2ed98ce5`. Edge sources conserve as 234 exact, 507 known-live-by, and 63 schedule-bound.

STRICT_LAW: 1,604 acted legs; 1,015 credited legs; 31 proven-maker and 984 proven-taker legs; 254 completed pairs; 254 under-par pairs. Frontier counts are 23 at <=93, 34 at <=95, 68 at <=97, 254 at <100, and 254 at any price. Regret has 1,012 numeric and 596 null legs; median 2c, p75 4c, p90 8c, total 4,427c.

CENSUS_PRICED: 1,604 acted legs; 1,041 credited legs; 6 proven-maker, 958 proven-taker, and 77 one-cent census-priced conversion legs; 279 completed pairs; 279 under-par pairs. Frontier counts are 30 at <=93, 39 at <=95, 80 at <=97, 279 at <100, and 279 at any price. Regret has 1,038 numeric and 570 null legs; median 2c, p75 4c, p90 8c, total 4,284c.

R3 on the same V3 pre-match spans has 886 credited legs, 229 completed pairs, and 217 under-par pairs. The former `68` value is retained only as the operator's original joint reference, not substituted for this close-free score.

The operator-named census-adjusted under-par OFFER is 680. Its historical source calls 680 any-price tape completability and 451 strict-sequential `<100`; the package preserves that semantic distinction instead of relabeling the historical 680 as under-par.

Close values are telemetry only. Deleting all close-named fields leaves strict and census grade digests unchanged. Close-based grade fields are null.

The full trace contains 4,508,577 decision rows and 7,704 action/fill/cap rows. Its original gzip is SHA-256 `687a8fdaee6a47210cf925dc18301574135468a44e47ad95f3efacb526221187`, 123,653,566 bytes, preserved as two deterministic Git-safe parts. The two clean builds compared 34 canonical artifacts with zero mismatches.

Relative to V34 full-life, the hard W1 edge leaves 1,286 strict leg streams byte/semantically identical and classifies 318 as waited-and-lost; census-priced has 1,293 identical and 311 waited-and-lost. The complete partitions remain category x price-region x bell-confidence and conserve to 1,608 legs per column.

The build made zero holdout, live, network-runtime, order, position, exit, settlement, DCA, or deployment accesses.

Canonical raw artifacts:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/REPORT.md

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/SCORECARD_TWO_COLUMN.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/STRICT_FRONTIER.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/CENSUS_PRICED_FRONTIER.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/STRICT_REGRET_GAUGE.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/CENSUS_PRICED_REGRET_GAUGE.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/R3_SAME_WINDOW_COMPARISON.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/UNDER_PAR_OFFER_BINDING.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/WINDOW1_SPAN_804.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/FULL_DECISION_TRACE_PARTS.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/ENTRY_PATH_DISPOSITION.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/DIFFERENTIAL_VS_V34_FULL_LIFE.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/ARNROM_NAMED_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/HARD_RIGHT_EDGE_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/START_LEDGER_V3_IDENTITY_AND_EDGE_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/DETERMINISM_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/FORBIDDEN_ACCESS_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/e56d79a2aee1f392b3bee5a0adad099c7f011976/.claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/ARTIFACT_HASH_MANIFEST.json

This addendum supersedes the earlier V34 full-life construction block only for this separately ruled V3 PRE-MATCH Window-1 measurement. It does not rewrite that block's historical finding and does not make this measurement a deployment artifact.
