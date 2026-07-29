# TEST-SCOPE RECONCILIATION ADDENDUM — V5 @ 2c5a730a — RULING: ADDENDUM PASS

**ADDENDUM PASS. The full V5 scope collects exactly 198 tests and runs 198/198 passed — zero failed, skipped, xfailed, deselected, filtered, or omitted — under the same scorer-entry instrumentation as the Phase-3 audit, with ZERO frozen-development event IDs reaching the scorer across the entire run. 105 + 93 = 198, reconciled exactly. No prior finding changes; the blind receipt and PASS report are not amended.**

Branch: `audit/window1-independent` · Sole additions-only child of Phase-3 PASS `07297a6937db2d67359d42a5ccf2baee1c5e59d4` · Environment: clean detached worktree at exactly V5 `2c5a730ac7fc2f87a2de33fd0ea2aa8f2cfafdae`, correctly situated for the private development inputs.

## 1. Collection (recorded before comparison)

`--collect-only` over the ten files printed **`198 tests collected`** before the run and before any comparison with the required total.

| test file | collected |
|---|---|
| tests/test_window1_t2_scoring_package_v1.py | 35 |
| tests/test_window1_t2_scoring_package_v2.py | 24 |
| tests/test_window1_t2_scoring_package_v3.py | 17 |
| tests/test_window1_t2_scoring_package_v4.py | 15 |
| tests/test_window1_t2_scoring_package_v5.py | 14 |
| tests/test_window1_t2_causal_divot_prerun.py | 22 |
| tests/test_window1_range_attack_prerun.py | 18 |
| tests/test_window1_range_attack_scoring_package_v1.py | 22 |
| tests/test_window1_range_attack_scoring_package_v2.py | 21 |
| tests/test_window1_range_attack_strict_ask_v2.py | 10 |
| **total** | **198** |

## 2. Reconciliation

- Scoring-package suites V1–V5: 35+24+17+15+14 = **105** (the set already instrumented and passed in the Phase-3 audit).
- Inherited-lineage suites: causal-divot 22 + Range-Attack pre-run 18 + Range-Attack V1 scoring 22 + Range-Attack V2 scoring 21 + strict-ask V2 10 = **93** (the same 93-test inherited set reconciled for V3 at `4a3a206e…`).
- **105 + 93 = 198.** Exact; no mismatch; no BLOCK condition.

## 3. Full instrumented run

One invocation, `-q -rA`, with the identical auditor scorer-entry plugin from the Phase-3 audit (wrapping both `window1_t2_frontier_regret_scorer_v1.score_t2_event` and the runner_v4/v5 aliases): **`198 passed in 786.51s`** — 198 PASSED lines, zero failed/skipped/xfailed/deselected/filtered/omitted. Scorer-entry call log across the complete 198-test run: **8 calls, all synthetic, ZERO frozen-development event IDs** — 3 × `SYNTHETIC-W1-T2-V5-BOUNDARY-SEAM` (the corrected V4 seam tests) and 5 × the synthetic unit-fixture id `"E"`; every call checked against the full 804-event frozen development population.

## 4. Non-action statement

No authorization was created, no execute mode was invoked, and no results directory was created. The Phase-2 blind receipt (`27373923`) and the Phase-3 PASS report (`07297a69`) are unchanged. The only artifact created is this addendum.
