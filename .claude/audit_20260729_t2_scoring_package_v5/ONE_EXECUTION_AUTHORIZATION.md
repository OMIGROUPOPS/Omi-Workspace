# ONE-EXECUTION AUTHORIZATION — Window-1 T2 scoring package V5

**PASS. AUTHORIZED FOR EXACTLY ONE EXECUTION.**

Issued (system clock, computed immediately before writing):
- Eastern: `2026-07-29T09:44:12-04:00`
- UTC: `2026-07-29T13:44:12+00:00`

Branch: `audit/window1-independent` · Sole additions-only child of test-scope addendum `2fe3b2e744b897b9e0c8821a3c9f92fb2285d43c` · Author: independent audit lane

This is the separately bound execution grant for the frozen V5 scoring package. It authorizes exactly ONE invocation of the frozen V5 runner and nothing else. **This document does not execute the scorer; no results directory exists or was created in issuing it.**

## 1. Reverified preconditions (all held at issuance)

- Package remote tip `origin/codex/window1-t2-scoring-package-v5-prerun` = exactly `2c5a730ac7fc2f87a2de33fd0ea2aa8f2cfafdae`; parent exactly `9cc8f1cc…` (V4); V5 is 19 additions + the sole corrected V4 test, all V4 runtime/package artifacts byte-identical.
- Audit remote tip = exactly `2fe3b2e744b897b9e0c8821a3c9f92fb2285d43c`, carrying in order: Phase-2 blind receipt `27373923…` → Phase-3 PASS `07297a69…` → test-scope ADDENDUM PASS `2fe3b2e7…` (198/198 under scorer-entry instrumentation, zero frozen-development scorer calls). This authorization is the sole additions-only child of the addendum.
- No earlier V5 authorization exists (the audit directory at `2fe3b2e7…` contains only the audit report, addendum, and blind receipt).
- The V5 results directory and any V5 results branch are absent locally, on every remote ref, and across all registered worktrees (swept at issuance).
- All frozen metric/result fields remain null; the live preflight-no-score run validated private inputs, prepared all 6,432 scorer calls with full raw-V5 boundaries, and recorded zero scorer-call attempts.
- The consumed V2 (`e4e57bac…`) and V3 (`40a6314f…`) authorizations are dynamically **rejected** by the V5 runner; the retired V4 execution ID cannot be reused; the V2/V3 execution IDs are bound as consumed.

## 2. Bound identities (unabridged, all exact)

- **Package commit (only):** `2c5a730ac7fc2f87a2de33fd0ea2aa8f2cfafdae`
- **Audit lineage:** Phase-3 PASS `07297a6937db2d67359d42a5ccf2baee1c5e59d4` · Addendum PASS `2fe3b2e744b897b9e0c8821a3c9f92fb2285d43c` · Phase-2 blind receipt `27373923171de3d02f71bbc3e19fb094fa6649de`
- **Execution ID (single-use):** `w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v5`
- **Input-bundle SHA-256:** `649a63f79a1b5ffb4fb50199df9029a2e78b1df3af6678e611bd011e4fd056dd`
- **Required FRESH results directory (must be absent immediately before invocation; the only permitted output location):** `.claude/window1_t2_results_w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v5`
- **Frozen command-template literal (verbatim, from the frozen runner):**

```
python -B arb-executor/analysis/window1_t2_scoring_runner_v5.py --repo . --package .claude/window1_t2_scoring_package_v5_prerun_20260729/SCORING_INPUT_MANIFEST.json --mode execute --authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> --authorization-report <AUDIT_REPORT_PATH>
```

`<AUDIT_COMMIT_SUPPLIED_SEPARATELY>` is this authorization's commit SHA, supplied separately at runtime — deliberately not embedded self-referentially. `<AUDIT_REPORT_PATH>` is this file's repository-relative path: `.claude/audit_20260729_t2_scoring_package_v5/ONE_EXECUTION_AUTHORIZATION.md`.

## 3. Execution conditions (all binding)

1. **Exactly one process invocation.**
2. **This authorization is consumed the moment that process starts.**
3. **No retry and no resume under this authorization, including after failure.** Any failure routes to operator review; a further attempt requires a new explicit authorization.
4. Execution only from a **clean worktree at exactly the V5 package commit** with the local package HEAD equal to its remote tip, correctly situated for the private development inputs.
5. The results directory named above must be **absent immediately before invocation** and is the **only** permitted output location.
6. **Any changed identity, ref, hash, command, worktree condition, or results-path condition invalidates this authorization in full.**
7. **No** holdout, live, network-runtime, Kalshi, order, position, exit, settlement, DCA, or Window-2 access; **no** tuning, ranking, selection, deployment, or live mutation. The execution produces only the frozen V5 outputs under the audited reporting law (fit July 12–17 and post-fit July 18–20 reported separately; completion–discount frontier at ≤93/≤95/≤97/<100/any-price with per-leg splits; objective = frontier maximization at <100; PC/D ≥ 603/804 floor; no single-scalar headline; authority × omitted-d2 attribution with no fill-inference; crash-honest scorer-attempt accounting).
8. **Phase-3 commit `07297a69…` is the required independent PASS** (with addendum `2fe3b2e7…`). No additional package audit is required while every bound identity, ref, hash, and condition above remains unchanged.

## 4. Statement of non-execution

The scorer was not invoked in this task; no results directory, result row, ranking, or selection exists; the only artifact created is this authorization.
