# INDEPENDENT FINAL AUDIT — STDOUT-SAFE ROUND-2 PRE-RUN @ 47bfbd43

**Status: AUDIT COMPLETE. BENCHMARK NOT EXECUTED. EXECUTION AUTHORIZED (scope at end).**
Date: 2026-07-25 · Branch: `audit/window1-independent` · Auditor: independent CC session
Method: read-only detached worktree pinned to `47bfbd43`; synthetic/temp fixtures only; zero scorer or instrument invocations; the real grid2 results directory was never created; the preserved grid1 directory was never touched.

## 0. Prior art (C45 gate)

`git log audit/window1-independent`; grep of `.claude/forensic_20260725_w1r2_stdout_failure/` and prior audit dirs. Prior art: `2ac4a2f4` (controlling forensic of the grid1 failure — Category A output-only, defines the smallest-repair spec), `9868bf48` (packaging audit @ `4b243bab`), `dd6fc308`, `7851204a`, `fb17a98f`. Delta: first audit of the superseding stdout-safe PRE-RUN `47bfbd43`; verifies the repair implements the forensic spec exactly and nothing else changed.

## 1. Ancestry and forensic binding — PASS

- `47bfbd43` = "Freeze stdout-safe Round-2 execution package", parent exactly `4b243bab`. `git rev-list --all --children` shows `4b243bab` has **exactly one child** — `47bfbd43` — across every ref; it is the remote tip of `codex/window1-definition` (`git ls-remote` confirmed).
- The forensic commit `2ac4a2f4…` and exact report blob `b587b241…` are bound in the runner constants (`CONTROLLING_FORENSIC`, `FORENSIC_REPORT_BLOB_OID`), in the bundle (`controlling_forensic` object, enforced at validate time — mismatch raises), in PRE_RUN_MANIFEST, and in the packager (`verify_forensic_binding` checks `AUDIT:FORENSIC_REPORT` blob). Independently verified: `git ls-tree 2ac4a2f4 <report path>` = `b587b241…`.
- Retired execution: `w1r2-dev-…-grid1` is bound as retired in runner constants, bundle (`retired_execution_id`, `retired_attempt_consumed_as_input: false`), and manifest (`permanently_inadmissible: true`). The new `RESULT_DIRECTORY` is the grid2-stdoutsafe path; `validate_result_directory_absent` (unchanged) refuses any pre-existing directory; the worktree law admits the preserved grid1 directory **only** as the single allowed untracked entry. The failed ID cannot be reused.

## 2. Freeze integrity — PASS

- **Input bundle**: canonical SHA-256 recomputed over the package minus `input_bundle_sha256` = `e0e088e355589f77e3b3a9cf1a9da51b3045f70c551721fe41e3da5df4ffee2b` — exact match. Git-blob SHA-256 of the bundle file = `47e1afff…` matching the manifest receipt (working-tree CRLF checkout explains any disk-byte difference; canonical and blob hashes are authoritative).
- **All 35 manifest blob receipts verified** (21 preserved inherited blobs + 14 package/source receipts): every `git_blob_oid` and SHA-256 matches git content at `47bfbd43`, and every inherited blob has the **same OID at `4b243bab`** — byte-identical.
- **Field-level bundle diff old→new**: IDENTICAL — candidates (8, exact order), `candidate_event_stream_receipts` (6,432), `candidate_event_stream_inputs`, `frozen_event_leg_identities` (1,608), `market_cache_files` (804 receipts) + aggregate, `external_inputs` (3), `metric_law`, `guarded_cutoff_law`, `reconstruction_law`, `selection_law`, `roles`, `D=804`, `target_PC=603`, dev dates, sealed holdout dates, scorer source + contract hashes. CHANGED — only identity/authorization fields (execution ID, result dir, commands, parent, audit), `runner_source_sha256`, schema version, `write_law` (adds progress-authority clauses). ADDED — forensic + retirement bindings and `frozen_surface_parity`. `git_inputs` differs in **exactly one row**: the runner (`f7f9f8a6…` → `b8c02d16…`).
- **Runner blob**: `git ls-tree` OID `23ec4690…`, content SHA-256 `b8c02d16…` — both exact.
- **Change classification**: runner (emission safety only — see §3/§4), packager (builds new package, reuses the prior frozen stream bundle by reference, adds forensic verification + parity computation), tests (new stdout-safe suite + identity updates). **No candidate membership, policy, ranking, scoring, metric, date, guard, or holdout rule changed.** The 6,432 streams live in the parent package's `FROZEN_CANDIDATE_EVENT_STREAMS.jsonl.gz` (blob `f9623954…`, unchanged, referenced not copied).

## 3. Progress authority — PASS

`ProgressEmitter.__call__` (frozen runner): (1) rejects any multi-line message (one complete record per event, enforced); (2) opens `PROGRESS.log` in append mode, writes `message + "\n"`, **flushes, and closes** — all before (3) tee to the in-memory `stdout_lines` and (4) cosmetic console echo. Console failure cannot suppress, truncate, duplicate, or corrupt the file record — proven by the order-checking unit test in the frozen suite and by my independent campaign (§5). All results, receipts, and manifests are written via file APIs; stdout/stderr are never load-bearing. `PROGRESS.log` is included in `OUTPUT_FILENAMES` and the output-hash manifest.

## 4. Failure handling — PASS

`ConsoleEchoGuard`: catches `(OSError, ValueError)` on both stdout and stderr echo paths; first failure permanently disables that stream's echo (`stdout_enabled=False`, short-circuit on all later calls), records the failure string in receipts, and rebinds `sys.stdout`/`sys.stderr` to a **devnull handle retained in `self._devnull_handles`** — so interpreter exit-time flush targets devnull, cannot re-raise, and the handle cannot be garbage-collected early. No descriptor-lifetime defect found: the progress file is opened/closed per event; the devnull handle persists for process lifetime by design. The failure-path stderr echo (`console.echo_stderr`) and the validate-only dump are equally guarded — the runner now contains **zero unguarded console writes** (verified by grep: the only two `print` calls sit inside the guard's `try` blocks).

## 5. Fixture campaign — PASS (frozen suite + independent reproduction)

- **Frozen suites**: `test_window1_round2_stdout_safe.py` + `test_window1_round2_grid_runner.py` — **32/32 pass** in 2.09s (no scorer work). The stdout-safe suite covers all seven required cases, including an exit-code-0 subprocess proof for exit-time flush after pipe failure.
- **Independent campaign** (`fixture_stdout_safe_campaign.py`, this directory; results in `FIXTURE_RESULTS.json`): drives the frozen `ConsoleEchoGuard`/`ProgressEmitter` imported from `47bfbd43` through a synthetic 8-candidate emission sequence (18 events) in child processes under: live pipe; **pipe reader vanishing after a successful write** (the grid1 killer); `DETACHED_PROCESS` non-console stdout; file redirect; devnull redirect; explicitly closed stdout (`ValueError` path); dead stderr. **All 7 cases: exit code 0, PROGRESS.log exactly the 18 expected events in order, zero duplicates, zero gaps, final receipt written, zero scorer invocations.** The `pipe_closed_early` console receipt records `stdout_failure: "OSError: [Errno 22] Invalid argument"` with `stdout_rebound_to_devnull: true` — the exact grid1 failure signature, now nonfatal end-to-end including interpreter shutdown.

## 6. Refusal and isolation — PASS, one flagged discrepancy

- `validate_result_directory_absent` is unchanged: existing results directory → hard refusal ("overwrite/resume refused").
- The real grid2 results directory does **not** exist in the Codex worktree, the audit worktree, or the main workspace — before or after this audit (all fixtures ran in OS temp directories).
- The preserved grid1 directory still contains **exactly six files, each byte-identical** (SHA-256 re-verified this session) to the forensic-recorded hashes: ledger `3619e26d…`, failure `0d46c3d8…`, start `c9fe3442…`, manifest `cac6af9d…`, stderr `83513883…`, stdout `ae29e02f…`.
- ⚠ **Flag — unverifiable claimed value**: the tasking's "failed-grid1 preserved manifest hash `030f8bf96506f9906a0bb08953385a3fec33fc6b9a1e454ad1dfd6868d06829d`" does **not** reproduce from the preserved directory under ~40 tested derivations (per-file, concatenations in every order, sha256sum-style, canonical JSON maps, manifest-content, CRLF/BOM variants, digest concatenation), and the value appears **nowhere** in the frozen tree, the forensic commit, the package, any manifest, or either worktree. It is a claim in the audit request with no counterpart artifact. Preservation is nonetheless **proven by the stronger per-file byte-identity above**, so this does not indict the freeze. For future reference the canonical combined hash is hereby defined as SHA-256 over sha256sum-style lines (`<sha256>  <name>\n`, names sorted): **`42eb84b38914a70fcc17380ee7e3ecac47a6a9f68807cea64408ecf09e12be37`** (equivalently, canonical-JSON `{name: sha256}` map: `2429c69c4d092e6e0499b6af5afdfb4f937913248f2ad15eb850c5484e2fc483`).
- Candidate 1's failed-attempt ledger is not referenced anywhere in the new package (`retired_attempt_consumed_as_input: false`; roles identical to the parent bundle; no path into the grid1 directory).
- This audit made **zero** real scorer/instrument invocations; the frozen `VALIDATION_ONLY_RECEIPT` records `scorer_invocations: 0`, `candidate_instrument_invocations: 0`, `result_directory_created: false`, and is byte-consistent with `PRE_RUN_MANIFEST.validation_only` (exact object equality). At execute time the runner replays validation and hard-fails if the receipt differs from the frozen replay.

## 7. Package completeness — PASS

Execution ID, bundle hash, runner hash/blob, exact command, result directory, and one-attempt law (`overwrite/resume/retry: false`, `partial_failure_log_preserved: true`) are mutually consistent across runner constants, bundle, manifest, validation receipt, and PRE_RUN_REPORT. The execute path consumes only hash-pinned frozen inputs (22 git inputs verified against HEAD blobs, 3 external inputs, 804 cache files with holdout-dates-present=0, 6,432 stream hashes re-checked per candidate at dispatch) and writes only into the new results directory; all eight candidate results, conservation report, comparison, development report, non-access proof, manifests, and output hashes are produced by file writes alone — stdout/stderr are never required (§3, §5). No post-freeze code generation is required: every module imported at execute time (`data_binding`, `real_capability`, `scorer`, runner) is a frozen, hash-bound blob at `47bfbd43`.

## Verdict

All seven audit items **PASS**. The single flag (§6) is a discrepancy in the audit request's claimed combined hash, not in any frozen artifact, and is fully superseded by per-file byte-identity proof. No blocker exists.

**EXECUTION AUTHORIZED — exactly and only:**

- PRE-RUN SHA `47bfbd4335a435a30054be9007c5029331252eee`
- execution ID `w1r2-dev-20260712-20260720-0a7fd1c6-grid2-stdoutsafe`
- input-bundle SHA-256 `e0e088e355589f77e3b3a9cf1a9da51b3045f70c551721fe41e3da5df4ffee2b`
- the exact frozen command:
  `python -B arb-executor/analysis/window1_round2_grid_runner.py --repo . --package .claude/window1_round2_stdout_safe_execution_package_20260725/SCORING_INPUT_BUNDLE.json --mode execute`
- one deterministic July 12–20 development-only execution
- no retry, no resume, holdout (July 24–26) untouched
- results returned for independent audit before anything else is done with them

The retired grid1 execution ID remains permanently inadmissible; its preserved directory remains frozen evidence, excluded from every metric.
