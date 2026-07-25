# Packaging audit — Round-2 deterministic execution package @ 4b243bab

- Object: `origin/codex/window1-definition` @ `4b243babee97fe251bde21fa6a1197dfbba5387d` ("Freeze Round-2 deterministic execution package"), sole child of authorized PRE-RUN `0a7fd1c6` and the branch tip. Prior authorization receipt `dd6fc308` bound in the manifest and runner constants.
- Method: detached read-only worktree; static verification of every receipt against committed git bytes; full read of `window1_round2_grid_runner.py` (1,419 lines); full verification of the 36.5 MB materialized stream bundle; the 24 committed tests (pass); and an auditor-authored refusal-fixture campaign (`refusal_fixtures.py`, receipt committed). Execute mode was **not** run; nothing was scored; the holdout was untouched.

## 1. Ancestry and scope — verified

- 4b243bab is the **sole** commit after 0a7fd1c6 and equals the branch tip.
- The commit is **additions only** (9 files, 9 A, 0 M/D): package artifacts, packager, grid runner, tests. Every inherited candidate, stream, scorer, contract, guard, ledger, and evidence artifact is therefore byte-identical by construction; the bundle additionally re-pins them by blob OID (verified).
- No live, production, configuration, order, position, Window-2, exit, settlement, DCA, or holdout surface changed (all paths are research-lane; committed test verifies the runner has no network/live interface).

## 2. Package identity — verified

- Execution ID `w1r2-dev-20260712-20260720-0a7fd1c6-grid1` is declared once, hard-coded as a runner constant, and **unused**: the frozen result directory does not exist anywhere in the tree.
- Input-bundle SHA-256 `b8424ce7…` is **exact** under the declared law (canonical JSON of the bundle minus its own `input_bundle_sha256` field) — recomputed independently and matched.
- All **22 git inputs** verify (blob OID + bytes + SHA-256 at 4b243bab); all **3 external inputs** carry exactly the Round-1-frozen private hashes (events `1f150cf0…`, prints `e9b5a765…`, tape manifest `d2a3bd4b…`); **804** market-cache receipts (unique event IDs, development dates only, aggregate 197,461,623 bytes = the frozen v3 cache); **6,432** candidate-event stream inputs; **1,608** leg identities; **8 candidates** in the frozen order — every collection recomputed, and the stream receipts and leg identities are byte-equal to the authorized PRE-RUN's `SCORER_FREEZE_CONTRACT.json` with matching canonical SHAs.
- The full materialized stream bundle was decompressed and verified row by row: 6,432 rows in the exact frozen (event × candidate) order, each row's `order_stream` canonical hash equal to its frozen receipt, all score-free flags intact (`scored: false`, `metrics: null`, no evaluation truth). Zero violations.
- Runner source, scorer source, and scorer-contract hashes in the bundle match their committed blobs.

## 3. Exact command — verified

`python -B arb-executor/analysis/window1_round2_grid_runner.py --repo . --package .claude/window1_round2_execution_package_20260724/SCORING_INPUT_BUNDLE.json --mode execute`

is complete and runnable from the repository root: no discovery, wildcards, discretionary arguments, or post-freeze choices (the command string itself is frozen inside the bundle and enforced by the runner). One invocation dispatches the whole eight-candidate grid internally; the `FrozenScorerDispatcher` enforces exactly one frozen-scorer call per candidate in the frozen order (out-of-order, duplicate, and incomplete dispatch all refuse — fixture-proved). The runner defines no policy, thresholds, ranking, tuning, selection, or ablation; `selection_law` forbids ranking and the output is explicitly `UNRANKED_FROZEN_SELECTION_RULE_ABSENT` with no winner receipt.

## 4. Refusal and safety contract — verified (committed tests + independent fixtures)

My fixture campaign (tampered scratch copies only) confirmed, each with the exact typed reason: bundle-hash mismatch; missing / additional / duplicated / reordered candidates; changed execution ID; changed command; holdout date smuggled into the development dates; changed denominator; `validate_dates` hard-refusals for July 24–26 and non-development dates; dispatcher out-of-order and double invocation. The untampered package passes hash/identity/grid/denominator checks and then refuses on my detached worktree at the git-state guard — execute mode additionally requires the frozen branch, HEAD whose parent is `0a7fd1c6`, and a clean worktree. Result-directory existence refuses overwrite and resume (`retry_permitted: false` on failure); the committed 24-test suite covers the same ground plus git-input, external-input, cache, stream-receipt, and leg-identity tampering. The committed `VALIDATION_ONLY_RECEIPT.json` records zero candidate-instrument invocations, zero scorer calls, no results produced, and a validate-only re-run must replay byte-identically or refuse.

## 5. Output contract — verified from code

One execution deterministically emits, inside the single frozen result directory: per-candidate event ledgers and summaries with raw-integer D/C/PC/S/IC before percentages, target distance, full classification conservation mechanically gated to exactly 804 per candidate (`METRIC_CONSERVATION_REPORT.json`; failure aborts), day/category/start-source breakdowns, `BASE_REAIM_COMPARISON.json` for the four frozen pairs, the development report, a non-access proof, `EXECUTION_START_RECEIPT.json` and `EXECUTION_MANIFEST.json` recording the exact command, execution ID, git SHA, timestamps, exit status, runtime versions, input/code hashes, stdout/stderr hashes, and an output-hash manifest. No post-result candidate selection is possible (no selection rule exists in the frozen package) and failure preserves partial logs without retry.

## Final answer

**EXECUTION AUTHORIZED: YES**

- SHA: `4b243babee97fe251bde21fa6a1197dfbba5387d`
- Execution ID: `w1r2-dev-20260712-20260720-0a7fd1c6-grid1`
- Input-bundle SHA-256: `b8424ce782299254891e4c616ea7fd9f67fd476462c740e97fa2421ffaaa617e`
- Exact command: `python -B arb-executor/analysis/window1_round2_grid_runner.py --repo . --package .claude/window1_round2_execution_package_20260724/SCORING_INPUT_BUNDLE.json --mode execute`

authorized for **ONE** deterministic July 12–20 development-only execution, results returned for independent audit. No execution, scoring, tuning, holdout access, production access, or Codex-branch edits were performed in this audit.
