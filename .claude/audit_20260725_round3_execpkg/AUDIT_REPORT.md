# INDEPENDENT ROUND-3 EXECUTION-PACKAGE AUDIT @ 6daab089 — NOT EXECUTED, NOT SCORED

**Status: ALL GATES PASS. PACKAGE ADMISSIBLE FOR EXACTLY ONE EXECUTION — AUTHORIZED (scope at end).**
Date: 2026-07-25 · Branch: `audit/window1-independent` · Auditor: independent CC session
Method: both branches fetched and remote identities verified; detached read-only worktree at the package SHA; every hash reproduced from git blobs; only package-integrity tests, refusal fixtures, and synthetic stdout/dead-pipe fixtures were run; the real execution command was never invoked; zero scorer invocations on real data; the real results directory does not exist.

## 0. Prior art (C45 gate)

`b415a98e` (Round-3 PRE-RUN audit — all gates pass, execution package named as the required next step), `807e2c86` (Round-2 results audit), `c94d4e50` (Round-2 stdout-safe package audit — the template this package instantiates), `2ac4a2f4` (grid1 forensic). Delta: first audit of the Round-3 execution package; verifies it is the additions-only instantiation demanded by `b415a98e`.

## Gate 1 — Ancestry and scope: PASS

`6daab089` ("research: freeze Round-3 execution package") has parent exactly `14e0e846`; the all-refs children scan shows it is the **sole child**; it is the remote tip of `codex/window1-definition` (ls-remote verified; my audit branch tip `b415a98e` also verified). The diff is **exactly 14 additions, zero modifications/deletions** (10 package files, packager, runner, 2 test suites) — every frozen Round-3 candidate, stream, scorer, metric, guard, receipt, source, and governance artifact is byte-identical by construction; the frozen stream bundle's blob OID is unchanged from the parent. All claimed hashes independently reproduce: bundle canonical `7dec1673…`, runner `f9dfab1e…`, scorer `b41e6915…` (unchanged Round-2 scorer), scorer contract `c0918343…`, metric contract `19795e4d…` (unchanged). All manifest receipts verify (input bundle, runner, all 14 bound package receipts with blob OIDs, embedded test/refusal/validation receipts identical to their committed files). The runner and manifest pin the full controlling chain — Round-2 results `10ac6dbc`, results audit `807e2c86` + report blob `9bb51a3d…`, Round-3 PRE-RUN `14e0e846`, PRE-RUN audit `b415a98e` + report blob `e4b32d21…` — every blob OID verified against my audit branch.

## Gate 2 — Frozen population: PASS

D=804; 8 candidates in the frozen r3 order; **6,432 stream receipts in the bundle are exactly identical** to the receipts I verified three-ways at the audited PRE-RUN (and the streams file itself is the same content-addressed blob); 1,608 leg identities; 804 cache receipts; external inputs unchanged (events ledger `1f150cf0…`, cache aggregate `aad8d055…`). The 694-eligible/110-named-censored sets per candidate and the 28-pair behavioral distinctness carry over by content-address — the streams are bit-for-bit the ones in which I independently recomputed those properties at `b415a98e`. The validation receipt re-verified 6,432 stream receipts, 21 git inputs, 3 external inputs, 804 cache files with **zero scorer invocations**.

## Gate 3 — Strategy fidelity: PASS

The package **consumes** the audited Round-3 mechanics rather than re-deriving them: the runner scores the frozen streams (dispatcher enforces exactly one scorer call per candidate against hash-pinned per-event streams) and cannot re-simulate, drop, simplify, or proxy any mechanic — first-lawful-BBO presence, advisory t_deep, real touch/join/park, positive-size receipt-identified print recuts, queue preservation, single armed sibling +1 response, content-bound deduplicated receipts, and named NO_CALL/censor handling are all properties *of the frozen streams*, whose 6,432 hashes the runner checks at dispatch. The unavailable sealed dual-divot object remains explicitly unavailable and unproxied (nothing in the package binds or substitutes for it). The instrument test suite (part of the 72) re-verifies the mechanics at this SHA.

## Gate 4 — Metric contract: PASS

D=804 and target_PC=603 pinned in bundle and runner; the metric contract file is byte-identical to Round 2's (`19795e4d…`): C = dual exact-five Window-1 completion, **PC = C with strictly negative combined close delta**, S = C with combined entry cost strictly below 100¢, IC = C with both individual-leg deltas strictly negative; combined cost, combined delta, and both individual deltas are retained in the ledger schema. Selection law: `report_all_candidates_unranked`, selection/ranking not permitted, no selection rule frozen; the candidate-receipt set is closed (missing/additional/duplicated/reordered candidates hard-refuse — refusal fixtures prove each); no ranking, tuning, winner selection, post-result policy change, or candidate mutation is possible.

## Gate 5 — Runner safety: PASS

`ConsoleEchoGuard`, `ProgressEmitter`, and `FrozenScorerDispatcher` are **byte-identical** to the classes proven in the Round-2 grid2 run. PROGRESS.log is authoritative: single-line records enforced, append/flush/close **before** any console echo; stdout/stderr echoes guarded against OSError and ValueError; first failure permanently disables echo and rebinds the stream to a retained devnull handle; the runner contains exactly two `print` sites, both inside the guard — **zero unguarded console writes**. New in this runner (an enforcement gain): the expected 20-line progress sequence and 19-file output inventory are frozen in the bundle (hashes verified), checked at validate time, and the final output inventory is re-checked against the contract at completion. My independent dead-pipe campaign against this runner's classes (7 handle classes: live pipe, dead pipe after successful write, detached non-console, file/devnull redirects, closed stdout ValueError, dead stderr) passes every case with exit 0 and complete, duplicate-free progress; the committed refusal-fixture receipt additionally proves the full synthetic 8-candidate publication with **all 19 expected artifacts written exactly once after console loss**, and exit-time flush after pipe failure returning zero.

## Gate 6 — One-attempt/refusal law: PASS

Execution ID `w1r3-dev-…-grid1-stdoutsafe` is new and appears nowhere as a results directory — the real results directory is **absent** in the package tree, the Codex worktree, and the main workspace, before and after this audit. `validate_result_directory_absent` refuses any pre-existing directory ("overwrite/resume refused"); write law: overwrite/resume/retry false, partial-artifact reuse forbidden; the 19 refusal fixtures each PASS (existing directory, changed bundle hash, changed blob/sha, changed stream receipt, changed leg identity, changed external input, holdout date, non-development date, candidate add/remove/duplicate/reorder — all refused; console-loss cases all nonfatal; validation-only dispatch proves zero scorer invocations). **No real candidate scorer invocation has occurred anywhere** (packaging receipt: 72/72 tests, 0 real-bundle scorer calls — independently reproduced: 72/72 in 2.65s); no result files exist.

## Gate 7 — Isolation: PASS

No network, Kalshi, VPS, live, production, configuration, order, position, Window-2, exit, settlement, or DCA interface exists in the runner or packager (grep-verified; the only "live_v4" string is the empty non-access-proof field). July 24–26 is hard-refused in date validation, absent from every input census (`holdout_dates_present: 0`), and inaccessible through any role path. Every execute-time import (runner → instrument/data-binding/capability/scorer modules, streams, contracts, caches) is a hash-pinned frozen blob at `6daab089`.

## Discrepancies — every one, however small

1. **Operational condition (not a package defect):** this runner requires an **exactly clean** worktree (the Round-2 grid1-exception was deliberately removed). The Codex worktree at `6daab089` still carries the preserved untracked grid1 evidence directory, so `--mode execute` there **will be refused**. Execution must run from a fresh, clean checkout/worktree of `6daab089`. The preserved grid1 directory must not be deleted or moved to satisfy the cleanliness law.
2. `expected_progress_sequence` line 2 is the literal placeholder `git_sha={RESULT_COMMIT_SHA}` (by design — the SHA is the package commit at run time; the runner emits the real value; the contract check compares the frozen template). Noted so the literal string in the receipts is not mistaken for an error.
3. Cosmetic only: the EXPECTED_OUTPUT_INVENTORY.json wraps its list under `successful_output_files` (bundle and file lists are identical; hashes bind both).

Nothing else. No gate fails.

## Final answers

- **Every package gate passes:** 1–7 PASS.
- **The package is admissible for exactly one execution.**
- **Zero execution/scoring confirmed:** the real command was never run by this audit or before it (validation receipt and packaging receipts record zero real scorer invocations); the results directory `.claude/window1_round3_results_w1r3-dev-20260712-20260720-14e0e846-grid1-stdoutsafe/` is **absent**.

**EXECUTION AUTHORIZED — exactly and only:**

- Package PRE-RUN SHA `6daab089d1e6c11bd75a684b4e8609e815fec8f4`
- Execution ID `w1r3-dev-20260712-20260720-14e0e846-grid1-stdoutsafe`
- Input-bundle SHA-256 `7dec1673c79dd548899f2e003ce753d90af01b182c929aa04be5f20714b24cb5`
- The exact frozen command, run once, from the repository root of a **fresh clean checkout** of the package SHA:
  `python -B arb-executor/analysis/window1_round3_grid_runner.py --repo . --package .claude/window1_round3_execution_package_20260725/SCORING_INPUT_BUNDLE.json --mode execute`
- One deterministic July 12–20 development-only execution; no retry, no resume, no overwrite; holdout (July 24–26) untouched; the preserved grid1 evidence directory untouched; results committed additively and **returned for independent audit before anything else is done with them**.
