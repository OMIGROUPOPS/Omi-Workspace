# EXECUTION AUTHORIZATION — BRANCH-ATTACHMENT RECOVERY (Window-1 T1 scoring, still-first execution)

**This is a narrow recovery addendum to the execution authorization at `143e3f1b4fa04e9e677994617c9967088d19155f`, itself an addendum to the independent audit PASS at `f3927bc72ace655d13a09abaa340d70691423adf`. It changes no audit finding and grants no new scoring authority beyond re-enabling the single still-unconsumed execution.**

Date: 2026-07-27 · Branch: `audit/window1-independent` · Additions-only sole child of exactly `143e3f1b4fa04e9e677994617c9967088d19155f` · Author: independent audit lane

## 1. Pre-flight failure facts (verified)

The earlier failure occurred **before execute mode was ever entered** and consumed **zero attempts**: execution attempts 0, retries 0, scorer never invoked, results directory `.claude/window1_t1_results_w1-t1-dev-20260712-20260720-grid1-scorepkg-v1` absent, no commit created or pushed. **The prior authorization's scoring authority was never exercised.** The only failed pre-flight condition was branch attachment: the package worktree `C:\Users\omigr\OMI-Workspace-codex-w1-range-attack-v2-execution` is clean and detached at the correct package HEAD `bbf6f632795d612be4e237d927821bcd01dc1898` (remote `codex/window1-definition` equal), but the local branch `codex/window1-definition` is owned by the stale worktree `C:\Users\omigr\OMI-Workspace-codex-window1` at ancestor `6daab089d1e6c11bd75a684b4e8609e815fec8f4`.

## 2. Authorized recovery — Git branch metadata repair ONLY

The only authorized recovery is the following branch-metadata repair, in this order:

1. **Detach** the stale worktree `C:\Users\omigr\OMI-Workspace-codex-window1` from `codex/window1-definition` (e.g. `git switch --detach` at its current commit `6daab089…`) **without altering any of its files**.
2. **Preserve byte-for-byte** that worktree's untracked historical directory `.claude/window1_round2_results_w1r2-dev-20260712-20260720-0a7fd1c6-grid1/` — it must not be deleted, moved, staged, committed, or overwritten.
3. **Atomically advance** the local branch ref `codex/window1-definition` from `6daab089d1e6c11bd75a684b4e8609e815fec8f4` to `bbf6f632795d612be4e237d927821bcd01dc1898`, only after verifying that `6daab089…` is an ancestor of `bbf6f632…` and that the remote `codex/window1-definition` equals `bbf6f632…` (e.g. `git update-ref` with the old value as compare-and-swap).
4. **Attach** `codex/window1-definition` to the already-clean package worktree at `bbf6f632…` (e.g. `git switch codex/window1-definition` there) without file changes.

**No reset, no clean, no checkout-overwrite, no deletion, no move, and no stash is authorized.** No other worktree, ref, file, or configuration may be touched.

## 3. Re-authorized still-first execution

After successful branch repair, this addendum authorizes **exactly one still-first deterministic scoring execution** — the same single attempt authorized at `143e3f1b…`, never consumed — under the unchanged bindings. The independent audit ruling for this package remains PASS, unmodified:

- **Package commit (only):** `bbf6f632795d612be4e237d927821bcd01dc1898` (implementation parent `88b0eae8620172f41e2f5d45320408357de24c6f`)
- **Execution ID (only):** `w1-t1-dev-20260712-20260720-grid1-scorepkg-v1`
- **Complete input-bundle SHA-256:** `67a9166a229eca4e048c57bb2316a3298de679ea2b6dad215203e31206743cd0`
- **Frozen command-template literal, byte-for-byte:**
  `python -B arb-executor/analysis/window1_t1_scoring_runner_v1.py --repo . --package .claude/window1_t1_scoring_package_prerun_20260727/SCORING_INPUT_MANIFEST.json --mode execute --authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> --authorization-report <AUDIT_REPORT_PATH>`
- **Results directory (only, must not pre-exist):** `.claude/window1_t1_results_w1-t1-dev-20260712-20260720-grid1-scorepkg-v1`
- The authorization commit carrying this report is supplied **separately at runtime** and is not embedded self-referentially.
- All constraints of `143e3f1b…` remain in force: clean worktree at the exact package commit, local/remote equality, exactly one attempt, no tuning/ranking/candidate mutation/holdout/live access.

## 4. Fail-closed conditions

- **If the branch repair or any new pre-flight check fails, execution remains forbidden** and requires operator review and a new explicit authorization.
- **No retry after an actual scorer invocation is authorized.** Once execute mode is entered, any failure, partial output, or interruption exhausts this authority permanently.
- **Results must be returned for independent audit** before any use.
