# INDEPENDENT AUDIT — CASUKA DEPLOYMENT PRE-RUN @ ccf95e46 — RULING: PASS

**PASS. The candidate is proven byte-exact: reverse-applying the frozen D1–D3 patch to candidate blob `ebd29103` reproduces the running blob `f1857199` byte-for-byte — simultaneously proving the patch is complete, the transplant contains exactly the audited repair delta (added/removed line multisets identical to the audited 94be4113 diff, +340/−19), and ZERO P0 REAL-START GUARD bytes (v1, v2, or v3) exist anywhere in the candidate. Provenance is resolved from tree objects, not prose. All 21 auditor probes, 38 focused tests, 7 inherited suites, the offline smoke replay, and exact 38-failure parity reproduce in clean checkouts; every hash verifies; rollback and deployment templates are fail-closed and single-file; no live surface was touched.**

Date: 2026-07-27 · Branch: `audit/window1-independent` · Additions-only child of `66136e6240f2adda990ea8fddc7e00cc643cfb4c` · Auditor: independent CC session
Under audit: package `ccf95e464ead48ca99cef0be62bc65c6ae8ba832` (receipts) on code commit `d256c491c851999047779827bca73de808b5f650`, parent `bb085ce06db5932049af85f927a7f9316ad76816`, on `codex/casuka-live-safety-deployment-prerun`.

## 1. Lineage and containment — PASS

ccf95e46's parent is d256c491; d256c491's parent is exactly bb085ce0; remote tip equals ccf95e46; clean checkout. Total containment bb085ce0→ccf95e46: **1 modified `arb-executor/live_v4.py` + 20 additive test/receipt files, 0 deletions.** The deployment file set is **exactly one file** (`live_v4.py`, blob `ebd29103`, SHA-256 `85fdd653…`, 1,011,785 bytes); tests/receipts are declared non-deployment; zero configuration/service/data/state changes.

## 2. Provenance ruling — resolved from tree objects

**What the receipt proves:** only that a checkout event at `eca101c6` occurred — nothing about the running bytes. **What the blob proves:** the running file hashes to `f1857199` (re-verified live during this audit). Git-tree facts, independently reproduced: `eca101c6:live_v4.py = 035135ea` (**not** the running blob — the P0 v1 checkout never governed the running file); `bb085ce0` changed the file **from `2aa371a2` to `f1857199`** — it is the commit that produced the running bytes. One precision the package's prose elides: **bb085ce0 itself is not on the VPS branch's ancestry** (the VPS lineage carries the identical blob via `19ec3633`); the lawful basis for the parent choice is **byte identity of the tree blob with the running file**, which holds exactly. bb085ce0 is therefore a lawful source parent in the only sense that matters for a single-file deploy. (This also corrects my prior audit's shorthand that the running engine was "guard v1" — the running engine predates all P0 guard commits.)

## 3. Pre-mutation hash gate — PASS

The ceremony template's **first command** hashes the actual remote `live_v4.py` and requires equality with `f1857199` under `set -euo pipefail` — any mismatch aborts before backup, copy, restart, or any other mutation. Required env bindings (`AUTHORIZED_PACKAGE_COMMIT`, `AUTHORIZED_INTEGRATION_COMMIT`, `OUTCOME_PROOF`) make the template non-executable from the PRE-RUN alone.

## 4. P0 exclusion — PASS (byte-level, stronger than AST)

`git apply -R` of the frozen `CASUKA_D1_D3.patch` (byte-identical to `git diff bb085ce0 d256c491 -- live_v4.py`) onto the candidate yields **exactly** the running blob `f1857199`. Therefore every byte of the candidate outside the audited D1–D3 delta is identical to the running parent — no P0 helper, import, constant, call-site, configuration, or behavior can exist in the candidate, and candidate P0 behavior is **byte-identical** (not merely AST-identical) to the running engine. Marker scan of the delta: 0 hits (`_entry_start_gate`, `_start_conflict`, `_strong_live_evidence`, `occurrence_datetime`, `post_start_entry_refused`). The package's AST-based P0-exclusion and semantic-equivalence receipts are consistent with, and subsumed by, this proof.

## 5. D1–D3 completeness — PASS

The candidate delta's added and removed line multisets are **identical** to the independently audited repair delta at 94be4113 (+340/−19 content lines each) — the transplant is exactly the audited behavior: per-ticker same-cycle exit-intent serialization, authoritative paginated sell-side exchange-truth clamp (final pre-POST operation, fail-closed on missing truth and repeated cursors, refuse-in-full with receipt+alert), and booked-positive + unsettled pair-classifier truth. Behavior confirmed on the candidate itself by my probes (below), not just by patch identity.

## 6. Fixtures, probes, tests — PASS

In a clean checkout of d256c491: **12/12 repair fixtures + 26/26 deployment-candidate tests = 38 focused tests; all 21 auditor-authored adversarial probes** (both organ orderings → exactly one 5-lot exit; two-cycle idempotence; oversell/covered/zero/negative/fractional/api-loss all refused pre-POST; buys ungated; FARRIU zero-booked-entry-resting and VEGKAW stale-booked classifier regressions; genuine fills intact); **7/7 relevant inherited suites**; `py_compile` and deployment AST lint PASS; the **offline CASUKA smoke replay** reproduces the exact causal shape (partial 2-lot → full 5, same-cycle top-up no-op, final one 5-lot, resting ≤ held, classifier regressions `settled`, zero network access).

## 7. Failure parity — PASS (independently reproduced)

Script census in my environment: parent bb085ce0 **45/83 with 38 failures**; candidate d256c491 **47/85 with the same 38 failures** — identical identities, identical terminal-cause signatures, zero formerly-passing tests failing, and only the two intended new suites added (both passing).

## 8. Hashes — PASS

Candidate SHA-256 matches the claim; frozen patch byte-identical to the git diff; all 16 artifact-manifest rows verify (an initial "16 bad" reading was my own path-join error, corrected); all 4 source-manifest rows verify; rollback blob SHA-256 `834b9e04…` and 997,352 bytes verify against the immutable git object; control-binding blob OIDs verify against the controlling repair/PASS/reproduction commits.

## 9. Rollback manifest — PASS

Restores exactly the current running bytes (`f1857199` from `bb085ce0`, hash- and size-verified), exact single target path, materialization from the immutable git object with a hash-verification template, fail-closed on separate rollback authorization + file-only integration commit + ancestor checks; touches no unrelated configuration or state.

## 10. Deployment templates — PASS

Exact candidate/target hashes embedded; single-file scope enforced (`git diff --name-only HEAD $INTEGRATION == exactly live_v4.py`); pre-mutation remote hash verification first; deployment only through the gated `deploy/deploy_live_v4.sh` (fetch+ff-only → lint + smoke-replay gate → one graceful tmux restart with drain → post-boot health check), with `OUTCOME_PROOF` required; the outcome-proof plan covers resting-exits ≤ held and classifier truth; stop/rollback path symmetric and fail-closed; no broad copy/reset/clean/checkout/deletion anywhere.

## 11. Non-action — PASS

Throughout construction and this audit: running engine unchanged (blob `f1857199`, PID 2241929, boot Jul 25 00:12:01), no deployment, no restart, no live-order/position/halt action, no live-state mutation.

## RULING

**PASS.** This authorizes **only a separately bound one-time deployment ceremony** using exactly candidate blob `ebd29103ff2153f3d6ced83995c3eb8c159fe38d` (SHA-256 `85fdd653…`) against running blob `f1857199…`, through the frozen templates and the gated deploy script, with a file-only integration commit and separate operator authorization. **This audit does not itself authorize deployment.**
