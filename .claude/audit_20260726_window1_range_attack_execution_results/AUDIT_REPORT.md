# INDEPENDENT WINDOW-1 RANGE-ATTACK SCORING EXECUTION AUDIT @ 53eaf2b5 — RULING: PASS

**PASS.** The execution is the single authorized attempt under the corrected V2 package, and my full independent reproduction — 991 fills re-adapted, 1,608 references re-derived, both candidates re-scored from the frozen inputs and metric law — matches both committed 804-row event ledgers with **ZERO row-level differences**. Every claimed aggregate reproduces exactly. **This PASS validates only these two frozen candidate results. PC = 116 and 111 are NOT a market ceiling, NOT a full-OS verdict, and NOT proof that Window-1 opportunity is absent** — they are the measured outcomes of two frozen candidates under guarded evidence, with the censor/ambiguity partition below.

Date: 2026-07-26 · Branch: `audit/window1-independent` (child of `582c062e`) · Auditor: independent CC session
Method: detached worktree at `53eaf2b5b10b82b86b71b651bb720028a6ee7979`; read-only; execute mode never invoked, no second results directory, no ranking/tuning/selection; reproduction via an in-process driver over the frozen adapter/reference/scorer modules and pinned inputs; sealed dates untouched.

## 1. Lineage and execution scope — PASS

`53eaf2b5` ("Record Range-Attack scoring execution") has parent exactly `e7e7b907`; all-refs children scan: **sole child**; local/remote `codex/window1-definition` equality verified. **Exactly nine result files added; no inherited file changed** (additions-only diff confined to the declared results directory). Receipts bind exactly: authorization commit `582c062e` and authorization report `.claude/audit_20260726_window1_range_attack_scoring_package_v2/EXECUTION_AUTHORIZATION.md`; package commit `e7e7b907`; execution ID `w1-range-attack-v2-dev-20260712-20260720-grid2-scorepkg-v2`; input-bundle `21b4db24…c732`; and the exact frozen command (with the real authorization SHA and report path). **Exit 0; one attempt; retry_count 0; exactly two scorer invocations**; `ranking_or_selection_applied: false`, `selected_candidate: null`; coherent start/end receipts (17:58:18 → 18:01:09 UTC) and a complete 13-line PROGRESS.log (references_derived ticks, candidate start/complete pairs).

## 2. Artifact integrity — PASS

All **8/8 OUTPUT_HASH_MANIFEST entries recompute exactly** (bytes and sha256), with lawful self-exclusion of the manifest — nine files total, none missing, extra, edited, or post-run. Both event ledgers contain **exactly 804 unique event rows** whose identity sets match the immutable D ledger (verified in reproduction: the frozen event ledger drives both).

## 3. Independent event-level reproduction — PASS (zero differences)

Reconstructed every candidate/event row from the frozen unique guarded-fill ledger (991 fills through the exact-integer adapter), the frozen V5 boundaries, and references derived from guarded-cache-v3 true prints, applying the frozen metric law: C only on both legs' exactly-five guarded fills; PC only on C with combined delta strictly below zero at fee 0; IC only on both leg deltas strictly negative; S only on combined cost strictly below 100¢; PC independent of IC; S separate from PC; missing/ambiguous reference preserves C/S but never PC/IC. No raw causal stream, post-right strict-ask observation, UUID ordering, or forbidden runtime source enters scoring (role firewall verified at the package audit; my driver consumed only the frozen runtime roles).
**Result: `macro_hold` 804/804 rows identical; `macro_micro` 804/804 rows identical — zero row-level differences from the committed ledgers** (canonical-JSON comparison; full receipt in AUDIT_RECEIPTS.json).

## 4. Aggregate results — PASS (every number exact)

Recomputed from the event ledgers (not TWO_CANDIDATE_RESULTS.json), matching the claimed values with **zero mismatches**:

| | macro_hold | macro_micro |
|---|--:|--:|
| D | 804 | 804 |
| C | **132** | **125** |
| PC | **116** | **111** |
| IC | 38 | 36 |
| S | 101 | 96 |
| completed_PC | 116 | 111 |
| completed_non_PC | 9 | 7 |
| completed_reference_missing | 7 | 7 |
| naked_single | 237 | 240 |
| no_fill | 336 | 340 |
| censored_boundary | 99 | 99 |
| **total** | **804** | **804** |
| PC-but-not-IC | 78 | 75 |

Official rates recomputed and matching the committed summary: C/D 0.16418 / 0.15547; PC/D 0.14428 / 0.13806; PC/C 0.87879 / 0.88800; IC/C 0.28788 / 0.28800; S/C 0.76515 / 0.76800. Conservation exact in both candidates (classification census sums to 804; completed decomposition IC + PC-not-IC + non-PC consistent). Date/category/boundary-source breakdowns recomputed from ledger rows and internally consistent with the census.

## 5. Reference ambiguity — PASS

Reproduced exactly: **64 ambiguous legs across 58 events per candidate** (per-leg tie fields: tie_count > 1 with >1 distinct price). **Exactly seven completed reference-missing pairs per candidate**, the same events in both: `…26JUL16MRVRON`, `…26JUL17GALCOP`, `…26JUL19IMATRA`, `…26JUL15COBBUR`, `…26JUL18PELSIL`, `…26JUL20GORMIN`, `…26JUL20PRIBRA`. **None counted as PC or IC**; **C preserved on all seven**, and **S preserved where lawful** (5 of 7 S=true; MRVRON and COBBUR S=false on cost ≥ 100¢ — the cost law, not the ambiguity). The rows remain separately identifiable (`completed_reference_missing` class plus per-leg tie receipts) and are **not blended into completed_non_PC**.

## 6. Diagnostic arithmetic (diagnostics only — PC/D is not redefined)

| diagnostic | macro_hold | macro_micro |
|---|--:|--:|
| official PC/C | 116/132 = **0.8788** | 111/125 = **0.8880** |
| PC / reference-determinate completed | 116/125 = **0.9280** | 111/118 = **0.9407** |
| max attainable PC/D at observed C | 132/804 = **0.1642** | 125/804 = **0.1555** |

Exact partition of D (censor table — measurement/evidence limitation vs candidate-policy outcome):

| class | macro_hold | macro_micro | nature |
|---|--:|--:|---|
| censored_boundary | 99 | 99 | evidence limitation (no positive provable boundary) |
| completed, reference-ambiguous/missing | 7 | 7 | evidence limitation (measurement, not policy) |
| instrument no_fill | 336 | 340 | candidate-policy outcome (no leg filled) |
| naked_single | 237 | 240 | candidate-policy outcome (one leg stranded) |
| completed_non_PC | 9 | 7 | candidate-policy outcome (adverse close) |
| completed_PC | 116 | 111 | candidate-policy outcome (objective met) |
| **Σ** | **804** | **804** | |

## 7. Access and one-attempt proof — PASS

`holdout_opened: false`, `holdout_queried: false`, `live_or_production_access: false`, `network_calls: 0`, `retry_count: 0`, `scorer_invocations: 2`, only the declared results directory written; no failure artifact, no second execution ID, no retry/resume/mutation anywhere in the tree; this audit touched no sealed dates or external systems and created no results directory.

## RULING

**PASS.** The execution is lawful, singular, correctly authorized through the finite gate, and its results are independently reproduced to the row. The scope of this PASS is strictly the two frozen candidate results above: macro_hold C=132/PC=116 and macro_micro C=125/PC=111 on D=804, under guarded fill evidence and sequence-honest references. It makes no claim of a market ceiling, no full-OS verdict, and no statement that Window-1 opportunity is absent; 99 boundary-censored events and 7 reference-ambiguous completions per candidate are measurement limits, not strategy misses, and are reported separately above. Awaiting operator review.
