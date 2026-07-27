# INDEPENDENT AUDIT — WINDOW-1 DECISION-LAYER ATTRIBUTION PRE-RUN @ 7fe299e5 — RULING: PASS

**PASS. A fully independent reconstruction — a fresh driver built only from the immutable passed-V2 census, the frozen strict-package policy receipts, and the frozen mechanism table, never importing the attribution module — reproduced every artifact with ZERO row-level and ZERO aggregate differences: all 47 decision rows, 28 never-exposed rows, 17 moved-away rows, 2 capacity rows, 372 no-fill geometry rows, the full crosswalk, the complete 216k-line episode feature breakdown, the mechanism matrix, and the conservation receipt. 38/38 tests; two fresh clean regenerations byte-identical to the committed package; every hash verifies; zero semantic violations; no forbidden activity.**

Date: 2026-07-27 · Branch: `audit/window1-independent` · Additions-only sole child of `26dd6e5e19a7890f02b538cc8b14a900f36e5b2f` · Auditor: independent CC session
Under audit: `7fe299e50a9fc018378873e1277c7c891ce313c0` ("Freeze Window-1 decision-layer attribution") on `codex/window1-definition`.

## 1. Lineage and containment — PASS

Parent exactly `e60f6af4`; sole child of e60f6af4 across all refs; remote `codex/window1-definition` = 7fe299e5. Diff: **17 additions, 0 modifications, 0 deletions**; full `ls-tree` comparison proves every inherited blob — the passed V2 census package, candidates, instruments, scorers, results, tests, artifacts — **byte-identical**. The package contains only the score-free attribution implementation, spec, tests, and 14 receipts/artifacts.

## 2. Immutable-input discipline — PASS

The builder gates on the passed V2 package (every artifact hash + determinism inventory + source hash re-verified at load, hard-failing on any drift — a gate I confirmed live when a CRLF-smudged checkout was correctly rejected during regeneration), pins the controlling PASS `26dd6e5e` blobs, and consumes V2 rows as immutable facts: no opportunity rescan/redefinition, no BBO or first-leg or boundary or headroom arithmetic changes, no policy fabrication, no scorer import, no C/PC/IC/S. Raw-cache access is limited to resolving the exact already-frozen no-fill witness episode IDs (68 targeted cache receipts, all hashes verified); the resolver matches a pre-frozen (episode-ID, timestamp, X, bid) tuple and fails on anything else — no enumeration or selection. All 23 immutable-input hashes + 2 audit blobs verify and point only at the passed V2, strict-ask, and mechanism-table lineage.

## 3. Independent reconstruction — PASS, zero differences

| artifact | rows | differences |
|---|--:|--:|
| DECISION_LAYER_EVENT_LEDGER | 47 | 0 |
| NEVER_EXPOSED_ATTRIBUTION | 28 | 0 |
| MOVED_AWAY_ATTRIBUTION | 17 | 0 |
| CAPACITY_UNPROVED_RECEIPT | 2 | 0 |
| NOFILL_COUNTERFACTUAL_GEOMETRY (orientations + unions) | 372 | 0 |
| SHARED_UNIQUE_EVENT_CROSSWALK | full | 0 |
| EPISODE_FEATURE_BREAKDOWN (all cross-tabs + 6,501-row receipt index) | full | 0 |
| MECHANISM_STATUS_DECISION_MATRIX | full | 0 |
| CONSERVATION_RECEIPT | full | 0 |

## 4. Crosswalk — PASS

**22 shared recovered games, 0 macro-hold-only, 3 macro-micro-only; 47 candidate rows = 22×2 + 3 across 25 distinct games.** All 22 shared games have identical credited first legs (leg, X1, timestamp, receipt), identical earliest lawful sibling episodes, and identical terminal attribution across candidates — verified per event with receipt pointers. Candidate rows carry `candidate_rows_are_not_distinct_games: true` and are never presented as games.

## 5. Never-exposed — PASS

All 28 rows reproduce: **24 × first-fill sibling response produced no episode-keyed decision** (headroom arm receipted at the causal first-fill timestamp; zero sibling decisions keyed to the earliest lawful opportunity receipt — verified empty per row; no order/action receipt contradicts the absence; attribution is to the missing episode-keyed decision output, not generalized "no strategy") and **4 × same-receipt target selection omitted the lawful X** (sibling decision exists at the exact controlling trigger receipt and timestamp; every selected `complete_raw_target_cents` differs from the lawful X; no receipt substitution — trigger receipt equality enforced). The classifier's fall-through class (`policy_evidence_insufficient_to_distinguish`) exists and is unused — no row was forced.

## 6. Moved-away — PASS

All 17 rows reproduce: **8 headroom reprices (CAUSAL_PAIR_HEADROOM), 8 corridor/policy-horizon terminations (POLICY_HORIZON), 1 LIVE-AIM reprice**. Each row carries the original exposure interval and X, the same-timestamp frozen cancel/reprice action receipt and exact reason, the replacement X (with contemporaneous-headroom check) or terminal state, the earliest lawful opportunity, elapsed move-to-opportunity time, and whether the old X equals the later opportunity X. Maker-safety / LIVE-AIM / headroom / horizon / supersession / cancel-without-replacement are distinct enum layers, not conflated; every row carries `counterfactual_only: true` and `certain_fill_claim: false`; the causal action is identified only from the interval-close receipt, never future evidence.

## 7. Capacity-unproved — PASS

**2 candidate rows, 1 distinct game.** Price reach is lawful and preserved (`price_reach_is_not_erased: true`); five-contract capacity remains unproved with the exact per-episode shortfall (`missing_capacity_contracts`), full BBO/depth context, no capacity invention; `policy_absence_class: false` — not counted as never-exposed or moved-away.

## 8. Conservation — PASS

**47 = 28 + 17 + 2; macro-hold 22 = 14 + 7 + 1; macro-micro 25 = 14 + 10 + 1** — recomputed independently, classes mutually exclusive and exhaustive over all recovered rows (per-row ID lists conserve).

## 9. Episode features — PASS

**3,226 / 3,275 = 6,501 episodes; 6,310 positive-d2 inside strict combined headroom.** Every cross-tab (candidate, event, category, date, orientation, d1, b2_max, d2 sign/exact, combined delta, elapsed band, evidence type, multiplicity, capacity/volume/cadence, spread, depth, macro regime, historical cell) conserves to exactly 6,501 candidate-episode rows and matches my recomputation bucket-for-bucket. Every bucket reports `candidate_episode_rows` beside `distinct_games` and the file carries `episode_rows_are_not_event_counts: true`. Positive d2 is a positive sibling delta inside a strictly negative combined pair delta — nowhere reinterpreted as individual-negative capture.

## 10. No-fill geometry — PASS

**Unions 65/336 and 68/340; shared 65, hold-only 0, micro-only 3; both 52/54; one 13/14; neither 271/272; orientation path rows 117/122.** Every witness verified: first leg/X/time, sibling X/time, strict ordering (elapsed gap > 0), d1/d2/combined, guarded corridors, and BBO/evidence receipts independently re-resolved from the raw cache against the frozen episode IDs. All 372 rows carry `counterfactual: true` and `realized_policy_miss_claim: false`; no counterfactual geometry enters the recovered realized-policy attribution (disjoint artifacts, verified).

## 11. Mechanism matrix — PASS

Every mapping verified against the frozen MECHANISM_RECOVERY_TABLE (BOUND 9 / PROXIED 10 / RETRACTED 5 / ABSENT 4): per-layer candidate rows, distinct games, qualifying episodes, candidate overlap, mechanism statuses copied verbatim, exact evidence sources, proven findings, and unresolved limitations all reproduce. **Zero promotions** (no PROXIED→BOUND, ABSENT→anything, RETRACTED→active). Only existing OS layers appear (discovery/recognition, target selection, initial exposure, exposure persistence/cancel-reprice, first-fill sibling response, capacity evidence, unavailable/indeterminate); no new strategy mechanism or parameter anywhere.

## 12–13. Semantics and recurring-X — PASS

Prose, field names, tables, and receipts reviewed: zero conflations of candidate rows/games, episodes/events, reach/capacity, policy absence/market absence, moved-away/guaranteed fill, counterfactual/realized miss, macro context/micro authority, positive d2/positive combined. Recurring-X context preserved verbatim from the passed V2 — **27/34** ledger-rejected and **16/16** ledger-absent — as separate classes, context only, never redefined.

## 14. Metrics and forbidden activity — PASS

All metrics/performance fields null, `scored: false`, zero C/PC/IC/S fields in any row (scanned all artifacts); no scorer/benchmark/tuning/ranking/selection/parameter proposal; no holdout (sealed dates enforced as rejections), live, network, production; no order/position mutation; no Window-2/exit/settlement/DCA. Builder git usage is read-only.

## 15. Integrity, tests, determinism — PASS

All 12 artifact-manifest rows, 13 determinism-inventory rows, 23 + 2 + 68 source-manifest rows, and all 4 gzip payloads verify; artifact self-exclusion correct; audit-PASS binding verified against `26dd6e5e` blobs. **38/38 tests pass** (13 attribution + 25 census; inherited tests byte-identical). **Two fresh clean regenerations** from immutable inputs — in a scratch clone pinned to the freeze-time refs (`origin/codex/window1-definition` = e60f6af4), `core.autocrlf=false`, and the three frozen source files placed untracked (the builder hashes them from the working tree) — were byte-identical to each other and **all 14 committed package files byte-identical**. Conservation was recomputed independently, not trusted.

## RULING

**PASS.** The decision-layer attribution is a faithful, deterministic, score-free diagnosis of the passed V2 census with zero reconstruction differences. This PASS authorizes **only** operator use of the attribution map to formulate a later Window-1 tuning instruction. It does **not** authorize tuning, scoring, ranking, deployment, or another benchmark.
