# INDEPENDENT AUDIT — WINDOW-1 T1 SCORING-PACKAGE PRE-RUN @ bbf6f632 — RULING: PASS

**PASS. The decisive independent unique-fill rebuild reproduced all 3,840 rows exactly — 10,221 raw frozen T1 fill facts, 6,381 excluded as post-right/unprovable, 3,840 admitted — with ZERO field-level differences against the committed ledger, zero law violations, zero duplicates, zero conflicts, and per-candidate conservation to D=804 on all eight candidates. The claimed input-bundle SHA (`67a9166a…`) and package-tree SHA (`80ee2dfb…`) reproduce from clean regeneration; a CRLF-configured build is byte-identical; 71/71 adversarial fixtures pass through the real adapter, audited scorer, and real authorization verifier; 160/160 tests; every hash verifies; no forbidden activity.**

Date: 2026-07-27 · Branch: `audit/window1-independent` · Additions-only child of `de2f627e53885bd1a44a42b92f23b5b93a391a47` · Auditor: independent CC session
Under audit: `bbf6f632795d612be4e237d927821bcd01dc1898` ("research: freeze Window-1 T1 scoring package") on `codex/window1-definition`.

## 1. Lineage and containment — PASS

bbf6f632's parent is exactly `88b0eae8` and it is the **sole child** across all refs; remote `codex/window1-definition` = bbf6f632. Diff: **exactly 22 additions, 15,780 insertions, 0 modifications/deletions**; full `ls-tree` comparison proves every inherited T1 instrument, overlay, candidate, receipt, scorer, reference adapter, audit artifact, and test **byte-identical**. No frozen candidate parameter or switch changed (switch-matrix SHA bindings verified against the frozen T1 spec). No results directory, cache, ranking, or selection artifact exists anywhere in the tree; the package holds exactly its 16 declared files. No event-specific hardcoding in any scoring source (zero event IDs).

## 2. Exact candidate set — PASS

Exactly the eight frozen T1 candidates in frozen order, D=804 each, with identity bindings to the passed T1 overlays (every fill row carries its source-overlay canonical SHA and shard SHA — verified per row in my rebuild). The two Range-Attack parents appear only in PARENT_REFERENCE_CANDIDATE_BINDING as audited, not-rerun references.

## 3. Independent unique-fill rebuild — PASS, zero differences (decisive item)

My driver rebuilt the ledger from the frozen T1 overlays, START_LEDGER boundary contracts, the private events ledger, and raw caches normalized through the inherited audited modules — never importing the package code and never using the committed ledger as expected answers. **10,221 raw fill facts → 6,381 excluded (unprovable boundary or post-guarded-cutoff) → 3,840 admitted; all 3,840 rebuilt rows are field-identical to the committed rows** (including evidence receipts, boundary, trigger sets, causal identities, overlay bindings). Every admitted row carries exact integer five contracts, fill price = original exposed X, a real exposure interval, action receipt/timestamp, and evidence receipt/timestamp with evidence ≥ action; per-row law checks found **zero** violations (print at/below X with positive size at the exact evidence timestamp; strict-ask strictly below X; no self-trigger fills; sibling evidence strictly later than the first fill; guarded-Window-1 membership; no fabricated capacity — fills come only from the frozen simulated fill facts, never decisions/HOLDs/targets/placements/NO_CALLs, which carry no `simulated_fill_ts`). Duplicates removed: 0 needed (uniqueness held); conflicts refused: 0 (all causal identities unique).

Per-candidate decomposition (credited rows / print / strict-ask / 2-leg / 1-leg / 0-leg events, all conserving to 804):

| candidate | rows | print | strict-ask | 2-leg | 1-leg | 0-leg | excluded |
|---|--:|--:|--:|--:|--:|--:|--:|
| hold response | 500 | 487 | 13 | 131 | 238 | 435 | 784 |
| hold target | 503 | 490 | 13 | 134 | 235 | 435 | 788 |
| hold persistence | 471 | 459 | 12 | 102 | 267 | 435 | 808 |
| hold full | 463 | 451 | 12 | 94 | 275 | 435 | 815 |
| micro response | 488 | 475 | 13 | 123 | 242 | 439 | 786 |
| micro target | 493 | 480 | 13 | 128 | 237 | 439 | 788 |
| micro persistence | 463 | 451 | 12 | 98 | 267 | 439 | 804 |
| micro full | 459 | 447 | 12 | 94 | 271 | 439 | 808 |

Positive-d2 sibling fills: 0 on all candidates (none of the 82 lawful positive-d2 targets filled inside the guarded window). The committed derivation receipt matches this decomposition exactly.

## 4. Chronology and T1 causality — PASS

Verified per row in the rebuild (and structurally by the controlling T1 PASS): no pre-first-fill T1 action exists in any overlay; first-leg facts are identical to the parent baselines; sibling actions open after the first fill and sibling evidence is strictly later; evidence never precedes its action; preserved same-timestamp ordering is inherited from the passed instrument; no older favorable BBO substitution (evidence books re-resolved by receipt identity through the audited normalizer); persistence HOLDs only preserve already-active orders (zero fills attach to fabricated earlier exposure — every fill binds a real interval that was open at evidence time); guarded-cutoff extensions stay inside Window 1 (admission cap at the guarded cutoff); shorter candidate horizons neither create nor erase evidence (exclusion is purely the guard admission of frozen facts).

## 5. Strict-ask accounting — PASS

All 100 strict-ask rows (13/13/12/12/13/13/12/12) re-verified: positive-size external ask **strictly below** X from the contemporaneous lawful book at the exact evidence timestamp, credited at the original exposed X on the exposed interval, no ask=X credit (adversarial fixture also proves the adapter refuses it), no double print/strict-ask credit (one fill per candidate/event/leg), no post-right observation. Rows reconcile exactly into the 3,840 total. Credit-before-cancel ordering carries from the controlling T1 PASS (1,472 credits, 0 conflicts).

## 6. Exact numeric validation — PASS

Through the **real adapter** with my own adversarial fixtures: quantities 4, 6, 5.9, 5.0001, True, NaN, and infinity all rejected; only exact integer five passes. Fractional/boolean/NaN/out-of-band fill prices and X rejected; fractional reference bids rejected; fractional d1 rejected; missing causal identity rejected; conflicting duplicate causal identities and duplicate leg fills rejected; sealed-date rows rejected; evidence-before-action rejected; wrong b2_max rejected; self-trigger fills rejected. Validation delegates to the audited `exact_integer`/`finite_number` (bool-hostile, float-integral-only) — no silent int()/round()/truncation path exists.

## 7. Reference law — PASS

References are constructed at execution time by the **byte-identical audited V2 reference adapter** (all five audited files verified against `e7e7b907`, matching the claimed hashes including scorer `a110c2eb…`). The bound reference tie census and source-order trace are the independently audited artifacts from the passed scoring-package-v2 lineage (hash-bound inputs). From the audited parent result ledgers I reproduced the per-candidate populations — **1,410 reference-available legs, 198 reference-record-missing legs, 7 completed-reference-missing events per parent** — which are event/leg-level facts identical across all eight T1 candidates. Fixtures through the real scorer path prove: same-price latest-timestamp ties remain reference-available with all receipts retained; differing-price ties without authoritative sequence become `ambiguous_latest_timestamp_multiple_prices_no_authoritative_sequence`; a completed event lacking determinate references stays in D, stays in C, stays S-eligible, has **PC and IC unavailable (None, not false)**, and lands in `completed_reference_missing_or_ambiguous`. No UUID/lexical/price/volume/favorable selection exists (audited law, previously PASSed).

## 8. Metric law — PASS

Scorer byte-identity proven, then exercised with synthetic fixtures through the real adapter + audited scorer: **D=804; C requires both legs at exactly five; PC ⇔ (fill1−ref1)+(fill2−ref2)+fee < 0 with fee frozen at 0; combined −1 qualifies, combined 0 does not; positive sibling d2 qualifies PC; PC without IC qualifies (IC diagnostic only, no both-negative gate); S ⇔ fill1+fill2 < 100 with 99 qualifying and 100 not; S does not gate PC and PC does not require S; the official denominator is D (PC_over_D), target PC ≥ 603 (`PC_shortfall_from_603`); PC/C appears only inside `completion_conditioned_diagnostics` with `official_target_metrics: false`; reference-unavailable completions are not silently counted non-PC** (aggregate census keeps them in their own class). The output contract reports C, PC, IC, S separately; `ranking_or_selection_applied: false`.

## 9. Classification conservation — PASS

The six closed classes are mutually exclusive and conserve to exactly D=804 (fixture aggregate: 1+1+1+1+799+1 = 804, `equals_D804` true; the adapter hard-fails on unknown classes or non-conservation). Diagnostics (PC_but_not_IC, positive_d2_completed_PC, print-vs-strict-ask decomposition, persistence participation, candidate-vs-parent changes) are reported beside the census and cannot alter membership. Boundary cases (naked single, no-fill, censored/unprovable, reference-ambiguous) all exercised through the real scorer path.

## 10. Authorization gate — PASS

Exercised the **real inherited verifier** with a synthetic authorization repository: a report containing PASS + exact package commit + exact execution ID + the complete unabridged input-bundle SHA + the exact command-template literal, at a commit present on the fetched audit ref, **is accepted**; each mutation is rejected (missing PASS, wrong/unknown commit, wrong execution ID, truncated bundle SHA, altered template, commit not on the audit ref). The runner additionally enforces sole-child parentage, local/remote equality, clean worktree, and a fresh one-attempt results path (fail-closed `validate_package`). There is **no self-referential requirement** — the report binds the package commit, never its own SHA. The real package was not executed.

## 11. Hashes, portability, determinism — PASS

Independently recomputed: **input-bundle SHA-256 = `67a9166a…` (exact claim, from the canonical payload and from clean regeneration) and package-tree SHA-256 = `80ee2dfb…` (exact claim)**; scorer/adapter/runner/contract hashes match all four claims; all 14 artifact receipts (canonical-LF identity) verify; all 48 committed-input receipts verify against bbf6f632 blobs; candidate/overlay bindings verify per fill row; the ledger gzip parses with 3,840 clean rows; FROZEN_EVENT_LEG_IDENTITIES conserves 804/1,608. **160/160 tests pass** at bbf6f632 (20 new + 140 across the bound suites; 198 total pass including the census/attribution suites). **Regeneration:** the frozen two-build freezer, run clean at the parent with LF checkout, reproduced both claimed SHAs with two internally byte-identical builds and **all 16 files byte-identical to the committed package**; a third build from a **CRLF-configured checkout** with CRLF source bytes is likewise byte-identical (canonical-LF identity law holds in practice). Committed receipts were never used as expected answers.

## 12. Null metrics and forbidden access — PASS

C/PC/IC/S, rates, and all performance fields null everywhere (recursive scan, 0 violations); zero scorer invocations by the builder (imports verified — the builder never imports the scorer; only the adapter/runner do, for execution-time use); no results directory; no ranking/selection; no holdout (sealed dates enforced as rejections, fixture-proven); no live/exchange/production/network; no order/position access; no Window-2/exit/settlement/DCA; no parent-artifact mutation.

## RULING

**PASS.** The package can lawfully score the eight frozen T1 candidates: fills derive only from frozen causal fill facts (never manufactured from decisions or targets), duplicates cannot double-count, same-receipt and future evidence cannot credit, PC is not tightened into IC, reference ambiguity is handled by the audited law, D is immutable at 804, and construction performed no optimization or ranking. This PASS authorizes **only one separately bound deterministic scoring execution after an explicit authorization addendum**. It does not itself authorize execution.
