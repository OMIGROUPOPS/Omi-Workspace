# ONE-EXECUTION AUTHORIZATION — Window-1 T2 scoring package V3

**PASS. AUTHORIZED FOR EXACTLY ONE EXECUTION.**

Issued (system clock, computed immediately before writing — not converted, not rounded, not the defective V2 label):
- Eastern: `2026-07-29T00:47:22-04:00`
- UTC: `2026-07-29T04:47:22+00:00`

Branch: `audit/window1-independent` · Additions-only exact child of `4a3a206e4966e85df181bd43c4ded854655f75aa` · Author: independent audit lane

This is the separately bound execution grant for the frozen V3 scoring package. It authorizes exactly ONE invocation of the frozen V3 runner and nothing else. **This document does not execute the scorer; no results directory exists or was created in issuing it.**

## 1. Reverified preconditions (all held at issuance)

- Package remote tip `origin/codex/window1-t2-scoring-package-v3-prerun` = exactly `a758279184ab0f367a3ce74a69da851608645e19`; its exact parent = `b73679edc9186eb72236cd1bee5f886ac141cac4`; V3 is additions-only (22 A / 0 M / 0 D) with all inherited V1/V2 bytes unchanged.
- Audit remote tip = exactly `4a3a206e4966e85df181bd43c4ded854655f75aa`, carrying in order: Phase-2 blind receipt `c5f3a3a2…` → Phase-3 PASS `9c5fe904…` → test-scope ADDENDUM PASS `4a3a206e…`. This authorization is the sole additions-only child of the addendum.
- No earlier V3 authorization exists (the audit directory at `4a3a206e…` contains only the audit report, the addendum, and the blind receipt).
- The V3 results directory and any V3 results branch are absent locally, on every remote ref, and across all registered worktrees (swept at issuance).
- All frozen metric and result fields remain null (C/PC/IC/S, frontier, regret, attribution, ranking, selection, performance — verified in the Phase-3 audit and unchanged since; refs unmoved).
- The frozen `SCORING_INPUT_MANIFEST.json` binds the input-bundle SHA-256 `92c8992b…`, the V3 execution ID, and the command template; source hashes (30 rows), artifact hashes (14 rows), and the 805 private-input hashes validated in the Phase-3 audit, and `validate_package(verify_private_inputs=True)` revalidates all of them fail-closed at invocation time.
- The consumed V2 authorization `e4e57bac…` remains consumed and is **explicitly rejected by the V3 runner** ("consumed V2 authorization is rejected by V3"); the V2 execution ID is bound as consumed and cannot be reused.

## 2. Bound identities (unabridged, all exact)

- **Package commit (only):** `a758279184ab0f367a3ce74a69da851608645e19`
- **Package-audit PASS (only):** `9c5fe90416b7b7bb1895d914cdba3139114cf500`
- **Addendum PASS:** `4a3a206e4966e85df181bd43c4ded854655f75aa`
- **Phase-2 blind receipt:** `c5f3a3a2e7180ea23b6dd6517ae6a8d2568e0afd`
- **Execution ID (single-use):** `w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v3`
- **Input-bundle SHA-256:** `92c8992bfe72529ed9b1229d1e67fd762aee6ba67463020f88e3ac44b4952996`
- **Required FRESH results directory (must be absent immediately before invocation; the only permitted output location):** `.claude/window1_t2_results_w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v3`
- **Frozen command-template literal (verbatim):**

```
python -B arb-executor/analysis/window1_t2_scoring_runner_v3.py --repo . --package .claude/window1_t2_scoring_package_v3_prerun_20260728/SCORING_INPUT_MANIFEST.json --mode execute --authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> --authorization-report <AUDIT_REPORT_PATH>
```

`<AUDIT_COMMIT_SUPPLIED_SEPARATELY>` is this authorization's commit SHA, supplied separately at runtime — deliberately not embedded self-referentially. `<AUDIT_REPORT_PATH>` is this file's repository-relative path: `.claude/audit_20260729_t2_scoring_package_v3/ONE_EXECUTION_AUTHORIZATION.md`.

## 3. Execution conditions (all binding)

1. **Exactly one process invocation.**
2. **This authorization is consumed the moment that process starts.**
3. **No retry and no resume under this authorization, including after failure.** Any failure routes to operator review; a further attempt requires a new explicit authorization.
4. Execution only from a **clean worktree at exactly the V3 package commit** (`git status --porcelain` empty) with the local package HEAD equal to its remote tip.
5. The results directory named above must be **absent immediately before invocation** and is the **only** permitted output location.
6. **Any changed identity, ref, hash, command, worktree condition, or results-path condition invalidates this authorization in full.**
7. **No** holdout, live, network-runtime, Kalshi, order, position, exit, settlement, DCA, or Window-2 access; **no** tuning, ranking, selection, deployment, or live mutation. The execution produces only the frozen V3 outputs under the audited reporting law (fit July 12–17 and post-fit July 18–20 reported separately; completion–discount frontier at ≤93/≤95/≤97/<100/any-price with per-leg splits; objective = frontier maximization at <100; PC/D ≥ 603/804 floor; no single-scalar headline; authority × omitted-d2 attribution with no fill-inference).
8. **Phase-3 commit `9c5fe904…` is the required independent PASS.** No additional package audit is required while every bound identity, ref, hash, and condition above remains unchanged.

## 4. Statement of non-execution

The scorer was not invoked in this task; no results directory, result row, ranking, or selection exists; the only artifact created is this authorization.
