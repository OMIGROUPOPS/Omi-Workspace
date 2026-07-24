# Delta audit — final Round-2 PRE-RUN @ 0a7fd1c6

- Object: `origin/codex/window1-definition` @ `0a7fd1c62d5cf662929c29f2298ed80aeecee1df` ("Finalize Round-2 Window-1 PRE-RUN freeze"); scope limited to the two prior blockers (R1 reaim, R2 scorer) plus freeze integrity, per mandate. Detached read-only worktree; no scoring, no D=804 execution, no holdout access, no edits to Codex's branch.
- Controlling audit `7851204a2f1ffac1d6af61670b67bc0bf6794f9e` (the SHA in the operator brief contained a stray digit; the commit bound by Codex is the real one) — bound in the manifest by exact hash **and** git blob OID `6085e449…`, re-derived on the audit branch and confirmed.

## Final answer

| Gate | Verdict |
|---|---|
| FREEZE/ANCESTRY | **PASS** |
| REAIM CANDIDATE RESTORATION | **PASS** |
| EIGHT-CANDIDATE DISTINCTNESS | **PASS** |
| SCORER COMPLETENESS | **PASS** |
| GUARDED-CUTOFF/METRIC CONTRACT | **PASS** |
| NO PREMATURE SCORING/HOLDOUT ACCESS | **PASS** |
| **ROUND-2 DEVELOPMENT EXECUTION AUTHORIZED** | **YES** |

**Authorized: exactly SHA `0a7fd1c62d5cf662929c29f2298ed80aeecee1df` for one deterministic July 12–20 development-only execution** of the frozen eight-candidate grid under the frozen scorer contract, with results returned for independent audit before any further step.

## A. Freeze and ancestry — verified

1. 0a7fd1c6 is the sole commit after 7667157f and equals the branch tip (ancestry chain 0a7fd1c6 → 7667157f → 6eecbd1d → f7cd4209 as declared).
2. Controlling audit bound by hash + blob OID (verified against the audit branch).
3. All **16** generated artifact receipts and all **38** manifest source/code/data/metric receipts verify against committed git blob bytes (bytes + SHA-256 + OID where declared).
4. Exactly the declared surface changed: 23 added + 9 modified files, every one scoped to the Round-2 research lane (final-freeze artifacts, instrument v3, scorer + contract + tests, reaim/campaign scripts, candidate/adapter/allowlist/spec contracts, one supersession note). No live/production/config path touched.
5. No candidate results, performance tables, rankings, winners, or holdout-derived artifacts exist anywhere in the committed freeze (searched); the only holdout-date strings are the sealed-dates declarations; every artifact carries `candidate_scoring_performed/tuning/performance_ablation/holdout_queried = false`, and `metrics: null` in the capability receipt.
6. Prior gates preserved: the four hold candidates' full event streams are byte-identical to the audited 7667157f lineage — **3,216 = 4 hold candidates × 804 events**, independently cross-checked hash-by-hash between the v2 and v3 committed receipts (3,216/3,216 identical). My full prior-gate adversarial fixture campaign re-run against the v3 instrument regresses clean on all ten checks (forbidden clock fields, corridor declarations, stream/evaluator separation, schedule-only, admission gate, zero-size walk, NO_CALL continuation, own volume, date fence, schedule-anchored eligibility).

## B. Reaim restoration — verified

- Eight frozen candidates (4 hold + 4 reaim); every one reproduces **694 eligible + 110 censored = 804** from its 804 per-event receipts, and all **28 pairs are pairwise distinct** on real frozen development events.
- Base/reaim changed-event counts reproduced **exactly from committed decision hashes**: 91 (async park_join), 85 (async touch_park), 87 (causal_steer), 64 (full_os) — with the full changed-event ID lists equal, pair by pair, to the exact-+1-applied ID lists (no order difference from any abstained call).
- Witness chronology verified per pair: first-leg fill < sibling eligibility ≤ sibling's own later lawful trigger (e.g. HERALM: fill 1783880950.27 → eligibility 1783882500 → trigger 1783883421.50; base 84 → reaim 85); every applied change is exactly +1¢; earlier order decisions are hash-identical between base and reaim; price/par/band/maximum-combined-cost guards all pass on every witness.
- The v3 mechanism is the demanded design: first fill only **arms** (`sibling_reaim_armed`, `immediate_order_change: false`); application happens solely inside the sibling's own trigger paths, gated on eligibility, armed-ts ordering, and the guard set; no lawful later trigger → `sibling_reaim_no_call` with the underlying policy continuing. `sibling_hold` bookkeeping is explicitly not counted as a witness (`sibling_hold_bookkeeping_counted_as_order_witness: false`); every witness is an actual changed sibling order.
- 3,216 inherited-hold streams: grain explained and verified above (4 hold candidates × 804 full event streams, zero differences).

## C. Deterministic scorer — verified

1. Scorer source, both contract files, fixture-test manifest, and tests are all hash-bound in the manifest (verified as git blobs); the runtime requires `--expected-contract-sha256` and refuses a changed contract file.
2. Complete: full implementation, no stub/TODO/callback/code-generation path; the adapter now declares `scoring_implemented: true`.
3. All 1,608 leg identities frozen in the contract with a verified canonical SHA; enforced at runtime.
4–5. Exactly **6,432 = 804 × 8** candidate-event stream hashes in the contract, 804 per candidate, all 64-hex, keys exactly the frozen event set, **zero mismatches** against the committed capability receipts; the scorer refuses any stream whose hash is outside the frozen receipt set.
6. Consumes only the bound sections (event ledger, streams, fill evidence, start boundaries, references, feature classifications, data-binding manifest), each double-hashed (canonical + frozen source receipt) against the contract, with the data-binding bundle SHA pinned to the audited `4a56deea…`.
7. Holdout and non-development dates hard-refused at both event and population level (tested).
8–9. Raw realized-start fields are forbidden by name; the cutoff is always anchor − frozen guard with pinned guard IDs and values — official/interval −60 s, proxy −900 s (negative 600 s pinned as well), and proxy directionality is cross-checked against the committed `strict_window1_completion_lte_utc`; any deviation raises.
10. Schedule-only (and live-by-only) rows must carry `positive_window1_provable: false` and can only classify censored; a positive is structurally impossible.
11–12. Metric definitions exact and frozen (D=804; C dual exact-five inside the guarded window; PC strictly < 0; S strictly < 100¢; IC both strictly < 0). Committed tests cover every mandated edge by name: delta 0 not PC, cost 100 not S, one delta 0 not IC, fills after the guarded cutoff not C, partial/other-quantity, naked singles kept separate, NO_CALL continues (never nonfill/censor), missing features censored with named reasons, contradictory rows, exact-five with a missing close reference censored (never success).
13. Duplicate receipts cannot inflate fills: fill actions must bind one-to-one to unique public evidence receipts (ticker + trade identity), with size ceilings and timestamp equality enforced; duplicates raise.
14. Census conservation to exactly D=804 is mechanically enforced (raises otherwise); metric totals conservation covered by test.
15. Determinism: pure function of bundle + contract with a canonical `result_sha256`; byte-identical repetition covered by the committed test and by my double test-suite run (20/20 twice, plus 50/50 across both suites).

One disclosure note for the results reader (not a blocker): the scorer's `naked_single_leg` class includes single-leg **partial** fills (one leg 0<q<5, other 0), a slight widening of Round-1's exactly-five-single definition; census still conserves and no success class is affected.

## D. No premature scoring — verified

No C/PC/S/IC results by Round-2 candidate, no rankings, no selected winner, no performance-derived removal, and no holdout rows exist in any committed or generated artifact; fixture-level expected values live only in the test suite and fixture manifest.

Artifacts committed alongside this report: `regression_v3` prior-gate fixture receipt. No changes to Codex's branch; nothing scored; holdout untouched.
