# V35 Living Rest + Evidence Gate Addendum

Package commit: `0799fba887f1d1e84f9c0ef3e73096fd9d76019e`.

V35 is a separately frozen replay variant on the V34-W1 causal package `e56d79a2aee1f392b3bee5a0adad099c7f011976`. It preserves the first-two-sided-book to V3 PRE-MATCH hard edge, strict/census fill laws, pair cap, dual-evidence state telemetry, and close-free grading. It does not modify `live_v4.py` and is not deployed or ratified as an operative baseline by this build.

The living rest now equals `min(best_bid - 1c, pair_cap)` on every own-book receipt, up and down, with no formation anchor, down-only constraint, or spread gate. The invariant holds on 2,004,999 of 2,004,999 strict receipts and 1,603,420 of 1,603,420 census-priced receipts, with a maximum target gap of zero cents. Strict reprices are 428,465 up and 197,025 down; census-priced reprices are 328,663 up and 164,305 down.

Take authority now requires a ten-second, five-lot displayed ask at or below the running seller-hit/qualifying-ask evidence floor and does not depend on the SETTLED label. A newly created qualifying-ask floor cannot self-authorize while downward quote or pressure evidence remains unabsorbed. An established floor is immediately takeable; evidence absorption is observed on later receipts against the inherited 300-second trailing state horizon, never by a timer-triggered action.

STRICT_LAW has D=804, 1,604 acted legs, 1,017 credited legs, 155 proven-maker legs, 862 proven-taker legs, 264 completed pairs, and 264 under-par pairs. Its cumulative frontier is 9 at <=93, 25 at <=95, 82 at <=97, 264 at <100, and 264 at any price. Regret has 1,015 numeric and 593 null legs; median 2c, p75 4c, p90 12c, and total 5,146c.

CENSUS_PRICED has D=804, 1,604 acted legs, 1,337 credited legs, 27 proven-maker legs, 707 proven-taker legs, 603 separately labeled one-cent conversions, 550 completed pairs, and 550 under-par pairs. Its cumulative frontier is 56 at <=93, 91 at <=95, 186 at <=97, 550 at <100, and 550 at any price. Regret has 1,335 numeric and 273 null legs; median 1c, p75 3c, p90 8c, and total 4,902c.

The V34-W1 comparison is 254 strict and 279 census-priced completed/under-par pairs, so V35 changes those columns by +10 and +271. R3 on the same V3 span remains 229 completed and 217 under par; the earlier `68` value remains only the operator's historical joint reference.

The frozen bleed census denominators are REST_STARVED 190, TAKE_PREEMPT 169, STATE_MISLABEL 90, CAP_STRANGLED 92, and NO_OFFER 9. Strict converts 46, 27, 39, and 2 respectively while losing 104 V34 completions. Census-priced converts 128, 80, 70, and 32 respectively while losing 39 V34 completions. Fill-depth-versus-eventual-print-low rows are preserved per category, starting-price region, and bell-confidence cell.

Named checks: BOSCOP|COP carries 42,562 rest reprices in the 45c-66c band, but the strict trace proves no seller-sweep fill at 47c-51c. POLKUH|POL's last rest action before the named seller print is 79c. KRALOR|LOR has zero prohibited 6c takes and fills at 5c. ARNROM|ROM has zero prohibited 41c takes and fills at 38c. BOSCOP|BOS has zero 32c takes while downward evidence is live; its later 32c take occurs only after the evidence is absorbed on a later SETTLED receipt.

The hard-edge receipt records 1,126,455 actions and 3,610,317 decisions, zero post-edge action/fill/cap-arm rows, and zero post-edge state updates. All close-based grade fields remain null. The supplied short identity `84b455c5` remains unresolved; the actual D=804 V3 ledger is bound at `224417da642a9f378a0d83f76edffe9890cb4a6f`, SHA-256 `1d7fe6a56837ceb0c0b8c932a05daecacc0cefbea94384e16c84975f2ed98ce5`.

Two clean builds compared 38 regenerable artifacts byte-for-byte with zero mismatches. The final focused/inherited run passed all 11 existing V35, V34, V32, and honest-fill tests. The initially named `test_window1_v34_dual_side_residency_machine_package.js` path does not exist; the actual inherited package test is `test_window1_v34_dual_side_residency_package.js` and passed. The build made zero holdout, live, network-runtime, order, position, exit, settlement, DCA, or deployment accesses.

Canonical raw artifacts:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/REPORT.md

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/SCORECARD_TWO_COLUMN.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/STRICT_FRONTIER.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/CENSUS_PRICED_FRONTIER.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/STRICT_REGRET_GAUGE.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/CENSUS_PRICED_REGRET_GAUGE.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/BLEED_CENSUS_DELTA.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/REST_SANITY.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/NAMED_REGRESSION_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/HARD_RIGHT_EDGE_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/FULL_DECISION_TRACE_PARTS.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/DETERMINISM_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/FORBIDDEN_ACCESS_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/0799fba887f1d1e84f9c0ef3e73096fd9d76019e/.claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/ARTIFACT_HASH_MANIFEST.json

This addendum records a replay measurement only. It neither deploys V35 nor supersedes an operative baseline without a separate operator ruling.
