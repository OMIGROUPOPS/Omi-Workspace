# TEST-SCOPE RECONCILIATION ADDENDUM — V3 @ a7582791 — RULING: ADDENDUM PASS

**ADDENDUM PASS. The broader V3 construction selection of 169 collected tests is exactly reproduced, fully enumerated, and fully run: 169 collected, 169 passed, 0 failed, 0 skipped, 0 xfailed, 0 deselected, 0 filtered, 0 unexplained omissions. The previously audited 76 is confirmed as the recursively manifested subset — precisely the three test files enumerated by the frozen V1/V2/V3 `SOURCE_HASH_MANIFEST.json` files. No prior finding changes.**

Branch: `audit/window1-independent` · Additions-only child of exactly `9c5fe90416b7b7bb1895d914cdba3139114cf500` · Environment: clean detached worktree at exactly V3 `a758279184ab0f367a3ce74a69da851608645e19`, sited so the `../OMI-Window1-private` sibling inputs resolve.

## 1. Exact reconstruction of the 169-test selection

The frozen V3 package contains no literal "169" claim; the number came from the construction lane's broader run. Reconstruction from per-file collection counts at V3 identifies exactly one sensible selection summing to 169: the three scoring-package suites **plus the inherited instrument-lineage suites of the modules the scoring stack imports** (the T2 causal-divot instrument suite and the four Range-Attack suites covering the `passed` substrate, the guarded-fill adapter, and the strict-ask law). The only other arithmetic solution would exclude the V3 suite itself, which is not a sensible construction selection and is rejected.

**Exact command (from `arb-executor/`, worktree at a7582791):**

```
python -B -m pytest tests/test_window1_t2_scoring_package_v1.py tests/test_window1_t2_scoring_package_v2.py tests/test_window1_t2_scoring_package_v3.py tests/test_window1_t2_causal_divot_prerun.py tests/test_window1_range_attack_prerun.py tests/test_window1_range_attack_scoring_package_v1.py tests/test_window1_range_attack_scoring_package_v2.py tests/test_window1_range_attack_strict_ask_v2.py -q -rA
```

`--collect-only` on this exact command prints: **`169 tests collected`**.

## 2. Per-file collection counts

| test file | collected |
|---|---|
| tests/test_window1_t2_scoring_package_v1.py | 35 |
| tests/test_window1_t2_scoring_package_v2.py | 24 |
| tests/test_window1_t2_scoring_package_v3.py | 17 |
| tests/test_window1_t2_causal_divot_prerun.py | 22 |
| tests/test_window1_range_attack_prerun.py | 18 |
| tests/test_window1_range_attack_scoring_package_v1.py | 22 |
| tests/test_window1_range_attack_scoring_package_v2.py | 21 |
| tests/test_window1_range_attack_strict_ask_v2.py | 10 |
| **total** | **169** |

## 3. Set difference from the audited 76

- **Audited 76** = the recursively manifested subset: exactly the test files enumerated (with hashes) by the frozen source manifests of the three scoring packages — `test_window1_t2_scoring_package_v1.py` (35, named by the V1 manifest), `…_v2.py` (24, named by the V2 manifest), `…_v3.py` (17, named by the V3 manifest). 35+24+17 = 76.
- **169 − 76 = 93**, consisting of the five inherited-lineage suites NOT named by any scoring-package source manifest: `test_window1_t2_causal_divot_prerun.py` (22), `test_window1_range_attack_prerun.py` (18), `test_window1_range_attack_scoring_package_v1.py` (22), `test_window1_range_attack_scoring_package_v2.py` (21), `test_window1_range_attack_strict_ask_v2.py` (10).
- The 76 is a strict subset of the 169; there is no test in the 76 absent from the 169.

## 4. Complete run result

The complete 169-test set ran in one invocation with `-rA` (all outcomes reported): **`169 passed in 783.64s`** — 169 PASSED lines, **zero** failed, skipped, xfailed, xpassed, deselected, filtered, or errored tests, and no unexplained omission. The run included the real-input V3 preflight tests (full 804-event population to the scorer boundary) and the original failing event's coverage.

## 5. Standing of the Phase-3 ruling

Phase-3 commit `9c5fe90416b7b7bb1895d914cdba3139114cf500` **is already the required independent PASS** for the V3 scoring package. Nothing in this addendum modifies it. The only remaining step before V3 execution is a **separately bound one-execution authorization**, which this addendum does not create.

## 6. Non-action statement

No V3 execute-mode invocation, real scoring, results directory, authorization, holdout, live, network-runtime, exchange, or Kalshi access occurred in this reconciliation. The only artifact created is this addendum.
