# INDEPENDENT FAILURE FORENSIC — w1r2-dev-20260712-20260720-0a7fd1c6-grid1

**Status: READ-ONLY FORENSIC. NO RETRY. NO SCORING. NO REPAIR APPLIED.**
Date: 2026-07-25 · Branch: `audit/window1-independent` · Auditor: independent CC session (no Codex artifacts modified)

## 0. Prior art (C45 gate)

Searched the audit branch and workspace for prior treatment of this failure
(`git log --oneline audit/window1-independent`, grep for `OSError`, `Errno 22`,
`EXECUTION_FAILURE` in `.claude/` and `arb-executor/analysis/`). Prior art:

- `9868bf48` — packaging audit of Round-2 execution package @ `4b243bab` — EXECUTION AUTHORIZED (the authorization this run executed under).
- `dd6fc308` — delta audit of final Round-2 PRE-RUN @ `0a7fd1c6` — AUTHORIZED (pinned as `authorization_audit` in the runner and start receipt).
- `7851204a`, `fb17a98f`, `024f03bb` — earlier Round-2 / OS-family audits.

No prior forensic of this failed execution exists anywhere. Delta of this
document: first and only forensic of execution
`w1r2-dev-20260712-20260720-0a7fd1c6-grid1`, which failed at
2026-07-25T05:52:29Z. Nothing here re-derives the packaging audit; it is
consumed as pinned identities only.

## 1. Identities under audit

| Item | Value |
|---|---|
| PRE-RUN HEAD at execution | `4b243babee97fe251bde21fa6a1197dfbba5387d` |
| Authorized parent (`HEAD^`) | `0a7fd1c62d5cf662929c29f2298ed80aeecee1df` |
| Authorization audit commit | `dd6fc30812f5199e048ecee1c80f5649c826bb4d` |
| Prior CC packaging authorization | `9868bf482b752ce14ab39a050c6cbe229e182202` |
| Execution ID | `w1r2-dev-20260712-20260720-0a7fd1c6-grid1` |
| Worktree | `C:\Users\omigr\OMI-Workspace-codex-window1` (verified at `4b243bab`, `git status` clean except the untracked partial results directory) |
| Partial dir | `.claude/window1_round2_results_w1r2-dev-20260712-20260720-0a7fd1c6-grid1/` |
| Runner | `arb-executor/analysis/window1_round2_grid_runner.py` (disk SHA-256 `f7f9f8a6…f055049` == package `runner_source_sha256`) |
| Started / ended (UTC) | 2026-07-25T05:26:52.141696 → 05:52:29.260545 (25 min 37 s) |

## 2. Hash and receipt-chain verification — ALL PASS

Recomputed SHA-256 of every file in the partial directory:

| File | Recorded | Recomputed | Verdict |
|---|---|---|---|
| `01_r2_async_pair__park_join__hold_EVENT_LEDGER.jsonl` (1,168,434 B) | `3619e26d…aa0399f1` | identical | PASS |
| `EXECUTION_FAILURE.json` (728 B) | `0d46c3d8…ecfdc0c3` | identical | PASS |
| `EXECUTION_START_RECEIPT.json` (1,658 B) | `c9fe3442…befb4cb5` | identical | PASS |
| `STDOUT.log` (205 B) | `ae29e02f…42745d5e` | identical | PASS |
| `STDERR.log` (454 B) | `83513883…d24bd02c833c`* | identical | PASS |
| `OUTPUT_HASH_MANIFEST.json` (896 B) | self-consistent over the 5 files above | recomputed identical | PASS |

*full value `8351388348624387a88f50697f4be29825062049a906292b651bd24bd02c833c`.

Receipt chain: the start receipt pins `git_sha=4b243bab`,
`authorized_parent=0a7fd1c6`, `authorization_audit=dd6fc308`,
`input_bundle_sha256=b8424ce7…faaa617e`, scorer source `b41e6915…`, scorer
contract `6684ee34…`, dispatch order = the 8 frozen candidates, and
`candidate_scorer_invocations_completed: 1`. All values match (a) the
constants baked into the runner at lines 37–47, (b) the frozen package on
disk, and (c) git ancestry (`4b243bab^ == 0a7fd1c6`, verified). The
failure receipt repeats the same execution ID / SHA / command, records
`exit_code: 1`, `error: "OSError: [Errno 22] Invalid argument"`,
`retry_permitted: false`, `holdout_opened: false`, `holdout_queried: false`,
`live_or_production_access: false`. Chain verdict: **intact and internally
consistent**.

## 3. Failure localization — proven output-only

Runner facts (all line references at frozen SHA `4b243bab`):

- `emit()` (lines 1075–1077) appends the message to an in-memory
  `stdout_lines` list **before** calling `print(message, flush=True)`.
- Candidate-1 sequence executed in this order: frozen scorer invocation
  (line 1220) → ledger `write_text` (1222–1225) → summary append (1226) →
  start-receipt update to `invocations_completed=1` (1227–1231) →
  `emit("candidate_complete=1:…")` (1232) → **`print` raised
  `OSError: [Errno 22]`** at line 1077.
- STDERR.log's traceback names exactly lines 1232 → 1077, matching the
  frozen source byte-for-byte.
- STDOUT.log contains all four tee'd lines including `candidate_complete=1`
  — proof the failure was in the console write, not in producing the message.
- The traceback shows the **first** failing print was the candidate-complete
  emit. The three earlier emits at ~05:26:52 printed successfully, so the
  stdout handle was valid at start and became invalid during the ~25-minute
  candidate-1 computation.

Microsecond write timeline (NTFS mtimes, UTC, all 2026-07-25T05:52:29):

| .212126 | ledger written and closed |
| .259563 | start receipt updated (`invocations_completed: 1`) |
| .260545 | `ended_at_utc` stamped in the except-handler |
| .321796 | STDOUT.log + STDERR.log (failure-path preservation) |
| .325359 | EXECUTION_FAILURE.json |
| .330366 | OUTPUT_HASH_MANIFEST.json — **last write; nothing after** |

The failure therefore occurred strictly **after** candidate 1's ledger and
receipt were durably closed, and strictly **before** any candidate-2 work
(no candidate-2 artifacts exist). All scorer state, ledger writes, and
receipts completed normally. **Proven: the failure occurred solely during
stdout progress emission.**

## 4. Candidate-1 ledger — structurally complete, hash-valid, INADMISSIBLE

- SHA-256 matches the recorded and manifest value.
- 804 rows, 804 distinct `event_id`s, zero JSON parse failures, terminal
  newline present, uniform `candidate_id = r2_async_pair__park_join__hold`.
- The 804 event IDs are **set-identical** to the frozen event ledger
  (`roles.event_ledger`, SHA `1f150cf0…e48b46`) — exact D=804 identity.
- Every row carries the contract fields (C/PC/IC/S, classification,
  censor structures); rows partition into the expected censored /
  non-censored schema variants; classification census conserves to 804.
- Event dates span 2026-07-12 → 2026-07-20 (9 development dates), zero
  holdout dates present.

**Verdict: structurally complete and hash-valid — and INADMISSIBLE as a
strategy or performance result.** It is a partial artifact of a failed
8-candidate execution: no `EIGHT_CANDIDATE_RESULTS.json`, no conservation
report, no comparison, no completed execution manifest exists. Per the
frozen no-partial-use law it must be preserved as failed-attempt evidence
and excluded from every metric. No per-class integers or PC values are
reproduced in this report for that reason.

## 5. File inventory of the attempt

Exactly six files exist; the attempt wrote nothing else anywhere
(worktree `git status` shows no tracked modification and no other
untracked path; all role/external inputs carry pre-run mtimes,
newest 2026-07-24T16:42Z).

| File | mtime (UTC 07-25) | State | Written after failure? |
|---|---|---|---|
| `01_…_EVENT_LEDGER.jsonl` | 05:52:29.212 | finalized, hash-valid | No (pre-failure) |
| `EXECUTION_START_RECEIPT.json` | 05:52:29.259 | finalized (`invocations_completed: 1`) | No (pre-failure) |
| `STDOUT.log` | 05:52:29.321 | finalized | Yes — designed failure-path preservation |
| `STDERR.log` | 05:52:29.321 | finalized | Yes — designed failure-path preservation |
| `EXECUTION_FAILURE.json` | 05:52:29.325 | finalized | Yes — designed failure-path preservation |
| `OUTPUT_HASH_MANIFEST.json` | 05:52:29.330 | finalized, self-consistent | Yes — designed failure-path preservation |

The four post-failure writes are exactly the runner's except-handler
sequence (lines 1354–1384) — evidence preservation, not result mutation.
No write of any kind occurred after 05:52:29.330366.

## 6. Frozen-surface verification — UNTOUCHED

- Worktree at `4b243bab`, `git diff HEAD` empty → runner, scorer,
  candidates file, metric contract, scorer contract, package directory all
  byte-identical to the authorized freeze.
- Package `input_bundle_sha256` recomputed over the canonicalized package
  minus that field: `b8424ce7…faaa617e` — exact match (self-verifying bundle).
- All 22 pinned `git_inputs` verify against `HEAD:` blobs; all 3 pinned
  `external_inputs` (`events.jsonl`, `prints.jsonl`, sanitized tape
  manifest, in `../OMI-Window1-private/`) verify byte-exact on disk.
- Three git inputs (`cohort.json`, `recut_cells.json`, `ORIENT_V1.json`)
  show different *working-tree* SHA-256 solely because git checked them out
  with CRLF (`git ls-files --eol`: `i/lf w/crlf`); CRLF→LF normalization
  reproduces the pinned hashes exactly, and validation reads `HEAD:` blobs.
  **Benign checkout artifact, not tampering.** (JSON parsing is
  line-ending-insensitive, so runtime content was identical too.)
- D=804 / target_PC=603 / dev dates 07-12…07-20 / sealed holdout
  07-24…07-26 all pinned in both package and runner constants; the runner
  hard-refuses holdout dates (lines 337–342) and validates the market cache
  census (804 files, `holdout_dates_present == 0`). No holdout path appears
  in any role. Failure receipt: `holdout_opened/queried: false`. Market
  cache (804 files) newest mtime 2026-07-24T16:42Z — pre-run.

**Verdict: candidates, scorer, input bundle, D=804 contract, and holdout
all remained byte-identical and untouched.**

## 7. Output-write inventory and fixture reproduction

The runner has exactly **three** console-write sites:

1. line 1077 — `print(message, flush=True)` inside `emit()` — **the failure site**;
2. line 1384 — failure-echo to stderr, executed only *after* all failure artifacts are on disk (harmless even if it raises);
3. line 1413 — validate-only mode JSON dump (not on the execute path).

All authoritative artifacts are written with `Path.write_text`/`write_json`
to files — none route through stdout.

Fixture harness `fixture_emit_handles.py` (this directory; **synthetic
only** — no package, candidate, market, or holdout data) replicates the
exact emit pattern and except-handler under seven output-handle classes,
in both `runner` (current) and `repaired` (proposed) modes. Results in
`FIXTURE_RESULTS.json` (Windows, CPython 3.11 — same platform family as
the failed run):

| Handle class | runner-mode outcome | repaired-mode outcome |
|---|---|---|
| console_inherit | OK | OK |
| redirect_file | OK | OK |
| redirect_devnull | OK | OK |
| pipe_open (live reader) | OK | OK |
| **pipe_closed_early (reader dies mid-run)** | **`OSError: [Errno 22] Invalid argument` on the post-work emit; earlier emits succeed; ledger + failure files preserved — exact signature match** | all emits survive; ledger + PROGRESS.log complete |
| detached_no_console (DETACHED_PROCESS) | OK on this interpreter (handle invalid from start would fail the *first* emit — inconsistent with the record) | OK |
| closed_in_process | `ValueError` (wrong exception type — inconsistent with the record) | survives |

The `pipe_closed_early` fixture is a **unique-signature match** on all four
observables: exception type/errno/message, first-failure position (the
post-work emit, earlier emits succeeding), pre-failure ledger survival, and
post-failure preservation writes succeeding. Windows maps a
written-to-but-abandoned pipe/console handle (`ERROR_NO_DATA`/broken pipe)
to `EINVAL` (errno 22). The stdout consumer that launched the run (console
window / relay pipe) went away during the ~25-minute candidate-1
computation; the next flushed write hit the dead handle.

Fixture side-finding: even with suppressed emit exceptions, the interpreter's
**exit-time flush** of a dead `sys.stdout` yields a nonzero process exit
(observed 120). The repair below therefore must neutralize `sys.stdout`
after the first console failure, not merely swallow the exception.

## 8. Verdicts

**Root cause — Category A: output-only infrastructure failure.**
A cosmetic progress `print` to a stdout handle whose consumer disappeared
mid-run raised `OSError: [Errno 22]` and, because `emit()` has no handler,
aborted the grid loop between candidate 1 and candidate 2. No runner-state,
scorer, data, or contract defect exists. Not category B; not unresolved.

**Partial-artifact integrity — INTACT.** All six files hash-verified;
receipt chain consistent; ledger structurally complete and hash-valid;
the only post-failure writes are the designed evidence-preservation
sequence. The partial directory must remain preserved, unmodified, as
failed-attempt evidence, excluded from every metric; candidate 1 is not
usable as a performance result.

**Exact smallest lawful repair** (runner-only; nothing else may change):

1. **stdout-safe, nonfatal emission**: wrap the console `print` in `emit()`
   in `try/except (OSError, ValueError)`; on first failure set a
   module-level flag that permanently disables further console echo and
   re-bind `sys.stdout` to `open(os.devnull, "w")` (prevents both repeat
   raises and the exit-time-flush nonzero exit). Same guard on the line-1384
   stderr echo.
2. **Authoritative progress to files, atomically**: append each emitted
   line to `<result_dir>/PROGRESS.log` (open-append-write-flush-close per
   line) at the moment of emission, so progress truth never depends on any
   console. STDOUT.log/STDERR.log snapshot behavior stays as-is.
3. **Fixture coverage**: adopt `fixture_emit_handles.py` (or equivalent)
   with the `pipe_closed_early`, `detached_no_console`, and
   `closed_in_process` cases as a mandatory pre-run smoke for the runner's
   emit path.
4. **Frozen surfaces unchanged**: candidates, scorer source + contract,
   input bundle content, data bindings, D=804 / target_PC=603 contract,
   dev dates, and sealed holdout must remain byte-identical. Only the
   runner's emission code changes, which changes `runner_source_sha256` —
   therefore:
5. **New identity, mandatory**: a new PRE-RUN commit (new SHA superseding
   `4b243bab`), a new execution ID (the string
   `w1r2-dev-20260712-20260720-0a7fd1c6-grid1` is permanently retired —
   the runner's own `validate_result_directory_absent` refuses reuse while
   the preserved partial directory exists, and reuse is forbidden
   regardless), a regenerated package pinning the new
   `runner_source_sha256`/`input_bundle_sha256`, and a new results
   directory.
6. **Independent audit before any new execution** of the repaired runner
   diff + new PRE-RUN, on this audit branch, before `--mode execute` is
   ever run again.

**May a new PRE-RUN be constructed?** Yes — construction of a repaired
runner and a superseding PRE-RUN freeze is permitted under the repair spec
above, subject to independent audit before execution.

**NO RETRY AUTHORIZATION YET.** This report authorizes nothing to run.
The failed attempt may not be retried or resumed; its execution ID may
never be reused; its partial artifacts stay frozen as evidence and out of
every metric.
