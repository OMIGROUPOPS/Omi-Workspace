# EXECUTION AUTHORIZATION — Window-1 T1 scoring package (one deterministic execution)

**This is an authorization-binding addendum to the independent audit PASS at `f3927bc72ace655d13a09abaa340d70691423adf` (`.claude/audit_20260727_window1_t1_scoring_package/AUDIT_REPORT.md`). It changes no audit finding. The ruling of that audit remains PASS, unmodified.**

Date: 2026-07-27 · Branch: `audit/window1-independent` · Additions-only sole child of exactly `f3927bc72ace655d13a09abaa340d70691423adf` · Author: independent audit lane

## Authorization

This addendum authorizes **exactly one** deterministic scoring execution, bound as follows and in no other configuration:

1. **Only authorized package commit:** `bbf6f632795d612be4e237d927821bcd01dc1898` (implementation parent `88b0eae8620172f41e2f5d45320408357de24c6f`). No other commit is authorized.
2. **Only authorized execution ID:** `w1-t1-dev-20260712-20260720-grid1-scorepkg-v1`.
3. **Complete input-bundle SHA-256, exactly:**
   `67a9166a229eca4e048c57bb2316a3298de679ea2b6dad215203e31206743cd0`
4. **Frozen command-template literal, byte-for-byte:**
   `python -B arb-executor/analysis/window1_t1_scoring_runner_v1.py --repo . --package .claude/window1_t1_scoring_package_prerun_20260727/SCORING_INPUT_MANIFEST.json --mode execute --authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> --authorization-report <AUDIT_REPORT_PATH>`
5. **Authorization commit:** the commit SHA carrying this report is supplied **separately at runtime** as `--authorization-commit`. It is deliberately **not** embedded self-referentially inside this report; the frozen verifier binds this report's content to the package, execution ID, bundle, and command template, and reads the report from the separately supplied commit on the fetched `audit/window1-independent` ref.

## Execution constraints

The single authorized execution must:

- run from a **clean worktree** checked out at exactly package commit `bbf6f632795d612be4e237d927821bcd01dc1898`;
- verify **local/remote equality** of the package branch before executing;
- use **exactly one attempt** under the execution ID above;
- create **only** the named new results directory:
  `.claude/window1_t1_results_w1-t1-dev-20260712-20260720-grid1-scorepkg-v1`
  (which must not already exist);
- perform **no tuning, no ranking, no candidate mutation, no holdout access, and no live/production access**;
- return the produced results for **independent audit** before any use.

## No rerun

**No rerun is authorized.** Any failure, partial output, interruption, or deviation exhausts this authorization; it requires operator review and a new explicit authorization addendum before any further attempt.
