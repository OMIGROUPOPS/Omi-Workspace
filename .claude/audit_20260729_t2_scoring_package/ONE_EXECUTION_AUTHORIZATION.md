# ONE-EXECUTION AUTHORIZATION — Window-1 T2 scoring package V2

**PASS. AUTHORIZED FOR EXACTLY ONE EXECUTION.**

Issued: 10:43 PM ET, Tuesday, July 28, 2026 · Branch: `audit/window1-independent` · Additions-only child of exactly `3f415f3697b0983925923444f5688ef35865c1bd` · Author: independent audit lane

This authorization is the separately bound execution grant contemplated by the three-phase blind audit. It authorizes exactly ONE invocation of the frozen V2 scoring runner and nothing else. **This document does not execute the scorer. No scorer was run and no results directory was created in issuing it.**

## 1. Reverified preconditions (all held at issuance)

- Package remote tip `origin/codex/window1-t2-scoring-package-v2-prerun` = exactly `b73679edc9186eb72236cd1bee5f886ac141cac4`; its exact parent = `3800416669e75e2ed2a7f1a075f360aec92c2ea6`; both commits are pure additions and V1 is preserved byte-for-byte inside V2 (28/28 files).
- Audit branch remote tip = exactly `3f415f3697b0983925923444f5688ef35865c1bd`, containing, in order: Phase-2 blind receipt `8f645d7dbcd498804b887a03a7a8d97098b6391d` (sole child of `87439397…`), then Phase-3 PASS `3f415f36…` (sole child of the blind receipt). Both preserved byte-for-byte in this commit's tree (report `ceeead0e…`, blind receipt `4307ccf4…`).
- Neither the package ref nor the audit ref has moved since the Phase-3 ruling.
- No earlier execution authorization exists on the audit branch; the tree at `3f415f36…` contains only the audit report and blind receipt in this directory.
- The required results directory does not exist in any repository tree, worktree, or the package commit.
- Every C/PC/IC/S, frontier, regret, attribution-result, ranking, selection, and performance field in the frozen package remains null (independently verified in the Phase-3 audit; `NULL_METRIC_NO_EXECUTION_RECEIPT` and manifests binding).
- No holdout, live, exchange, or trading-system access occurred during issuance.

## 2. Bound identities (unabridged, all exact)

- **Package commit (only):** `b73679edc9186eb72236cd1bee5f886ac141cac4`
- **Package-audit PASS (only):** `3f415f3697b0983925923444f5688ef35865c1bd`
- **Phase-2 blind receipt:** `8f645d7dbcd498804b887a03a7a8d97098b6391d`
- **Execution ID (single-use):** `w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v2`
- **Input-bundle SHA-256:** `67508764d4560c2229f30b9a73d1211e8820fdc95e7bd2ffe2e5c6842ed6e34a` (bound inside the frozen `SCORING_INPUT_MANIFEST.json` at the package commit)
- **Frozen command-template literal (verbatim):**

```
python -B arb-executor/analysis/window1_t2_scoring_runner_v2.py --repo . --package .claude/window1_t2_scoring_package_v2_prerun_20260728/SCORING_INPUT_MANIFEST.json --mode execute --authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> --authorization-report <AUDIT_REPORT_PATH>
```

- **Required NEW results directory (must be absent before invocation):** `.claude/window1_t2_results_w1-t2-dev-20260712-20260720-frontier-regret-grid1-scorepkg-v2`
- **Authorization commit:** supplied separately at runtime as `<AUDIT_COMMIT_SUPPLIED_SEPARATELY>` — deliberately not embedded self-referentially in this report. `<AUDIT_REPORT_PATH>` is this file's repository-relative path: `.claude/audit_20260729_t2_scoring_package/ONE_EXECUTION_AUTHORIZATION.md`.

## 3. Execution conditions (all binding)

1. **Exactly one process invocation.** Once the runner process starts, this authorization is consumed.
2. **No retry under this authorization, including after failure.** Any failure routes to operator review; a further attempt requires a new explicit authorization.
3. Execution only from a **clean worktree at exactly package commit `b73679ed…`** (`git status --porcelain` empty), with local package HEAD equal to the remote package branch tip.
4. All frozen source, artifact, private-input, and bundle hashes must validate before scoring (the runner's own validation law; any mismatch aborts with zero output).
5. The required results directory must be **absent** immediately before invocation and is the only permitted output location.
6. **No** holdout, live, network, Kalshi, order, position, exit, settlement, DCA, or Window-2 access.
7. **No** candidate selection, ranking, tuning, deployment, or live mutation. The execution produces the frozen frontier/regret/attribution outputs for all eight candidates under the audited reporting law (fit July 12–17 and post-fit July 18–20 reported separately; completion–discount frontier at ≤93/≤95/≤97/<100/any-price with per-leg splits; objective = frontier maximization at <100; PC/D ≥ 603/804 floor; no single-scalar headline) and nothing else.
8. **This authorization becomes invalid immediately** if any bound identity, input hash, ref position, worktree condition, command template, or results-directory condition above changes in any way.

## 4. Statement of non-execution

The scorer was not invoked in this task; no results directory, result row, ranking, or selection exists; the only artifact created is this report.
