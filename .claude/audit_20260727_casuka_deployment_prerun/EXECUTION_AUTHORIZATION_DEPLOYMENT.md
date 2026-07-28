# EXECUTION AUTHORIZATION — CASUKA D1–D3 one-time deployment ceremony

**This is an authorization-binding addendum to the independent deployment-package audit PASS at `1e62d7e4a2aa4d38e6e71b5e0271725f7e3a6f0e` (`.claude/audit_20260727_casuka_deployment_prerun/AUDIT_REPORT.md`), the repair PASS at `66136e6240f2adda990ea8fddc7e00cc643cfb4c`, and the controlling independent reproduction at `b442908f3b253d1e13d5b2a5e93c3dbf0491320d`. It changes no audit finding. It authorizes exactly ONE deployment ceremony and nothing else. This document does not deploy.**

Date: 2026-07-27 · Branch: `audit/window1-independent` · Additions-only child of exactly `1e62d7e4a2aa4d38e6e71b5e0271725f7e3a6f0e` · Author: independent audit lane

## 1. Frozen bindings (unabridged)

- **Deployment package commit (only):** `ccf95e464ead48ca99cef0be62bc65c6ae8ba832`
- **Deployment code commit (only):** `d256c491c851999047779827bca73de808b5f650`
- **Candidate file:** `arb-executor/live_v4.py`
  - Git blob: `ebd29103ff2153f3d6ced83995c3eb8c159fe38d`
  - SHA-256: `85fdd653ee85dd598388d3cf6f537999decf0f0bdece6b8b3495a19041ee05d4`
  - Bytes: `1011785`
  - Source-hash receipt: `.claude/casuka_live_safety_deployment_prerun_20260727/SOURCE_HASH_MANIFEST.json` at `ccf95e464ead48ca99cef0be62bc65c6ae8ba832` (DEPLOYMENT_FILE_SET.json binds the identical values)
- **Required running preimage (must hold immediately before mutation):**
  - Git blob: `f1857199164664037fef41b024e60f27fa373548`
  - SHA-256: `834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54`
  - Bytes: `997352`
  - Immutable rollback source: exactly `bb085ce06db5932049af85f927a7f9316ad76816:arb-executor/live_v4.py` per `ROLLBACK_MANIFEST.json` (materialization `git show bb085ce06db5932049af85f927a7f9316ad76816:arb-executor/live_v4.py`).
- **Remote host:** `root@104.131.191.95` · repo `/root/Omi-Workspace`
- **Service identity:** tmux session `live_v4`, process `python3 -u live_v4.py`, boot command `cd /root/Omi-Workspace/arb-executor && ulimit -n 262144 && python3 -u live_v4.py >> /tmp/live_v4.log 2>&1`
- **Target file path (only):** `/root/Omi-Workspace/arb-executor/live_v4.py`
- **Backup path convention (must not pre-exist):** `/root/Omi-Workspace/arb-executor/live_v4.py.pre-casuka-d1d3.casuka-d1d3-deploy-20260727-attempt1.bak`
- **Deployment script:** `/root/Omi-Workspace/arb-executor/deploy/deploy_live_v4.sh` (fetch + ff-only → gate → graceful restart → post-boot health check)
- **Smoke/lint gate:** `/root/Omi-Workspace/arb-executor/deploy/deploy_gate.sh` (lint + smoke replay; restart refused unless it passes)
- **Health check:** the deploy script's built-in post-boot check (single process of `python3 -u live_v4.py`, tmux session `live_v4` alive) plus the engine's post-boot book audit
- **Outcome-proof artifact paths:** per `OUTCOME_PROOF_PLAN.json` and `PRE_POST_INVARIANTS.json` in the frozen package; ceremony receipts must be written under the unique results directory below.

## 2. Exact deployment command template (unabridged, from the frozen package)

Preflight (must run first, verbatim semantics):

```bash
set -euo pipefail
: "${AUTHORIZED_PACKAGE_COMMIT:?separate authorization required}"
: "${AUTHORIZED_INTEGRATION_COMMIT:?file-only integration commit required}"
: "${OUTCOME_PROOF:?audited outcome proof required}"

REPO=/root/Omi-Workspace
RUNNING_BLOB=f1857199164664037fef41b024e60f27fa373548
CANDIDATE_BLOB=ebd29103ff2153f3d6ced83995c3eb8c159fe38d
CANDIDATE_COMMIT=d256c491c851999047779827bca73de808b5f650

test "$(git -C "$REPO" hash-object arb-executor/live_v4.py)" = "$RUNNING_BLOB"
git -C "$REPO" fetch origin
test "$(git -C "$REPO" rev-parse "$AUTHORIZED_PACKAGE_COMMIT")" = "$AUTHORIZED_PACKAGE_COMMIT"
test "$(git -C "$REPO" rev-parse "$AUTHORIZED_INTEGRATION_COMMIT")" = "$AUTHORIZED_INTEGRATION_COMMIT"
test "$(git -C "$REPO" ls-tree "$AUTHORIZED_INTEGRATION_COMMIT" arb-executor/live_v4.py | awk '{print $3}')" = "$CANDIDATE_BLOB"
test "$(git -C "$REPO" diff --name-only HEAD "$AUTHORIZED_INTEGRATION_COMMIT")" = "arb-executor/live_v4.py"
git -C "$REPO" merge-base --is-ancestor HEAD "$AUTHORIZED_INTEGRATION_COMMIT"
```

Deployment command literal (the verifier-bound template):

`OUTCOME_PROOF="$OUTCOME_PROOF" /root/Omi-Workspace/arb-executor/deploy/deploy_live_v4.sh "$AUTHORIZED_INTEGRATION_COMMIT"`

## 3. Unique deployment identity

- **Deployment ID (only, single-use):** `casuka-d1d3-deploy-20260727-attempt1`
- **Results/receipt directory (must not pre-exist, verified absent at authoring on both repo trees and the VPS):** `.claude/casuka_deployment_results_casuka-d1d3-deploy-20260727-attempt1/`
- **Authorization commit:** supplied **separately at runtime** as the ceremony's authorization reference. It is deliberately **not** embedded self-referentially in this report; the frozen verifier binds this report's content to the package commit, deployment ID, candidate hash, preimage hash, and command literal, reading the report from the separately supplied commit on the fetched `audit/window1-independent` ref.
- **Exactly one attempt.** Once any remote mutation begins (backup creation onward), **no retry of the candidate deployment is authorized under any circumstances** — a failure routes to mandatory rollback and operator review; any further attempt requires a new explicit authorization.

## 4. Fail-closed preconditions (all must hold immediately before mutation)

1. This authorization report passes the real frozen verifier with the bindings above.
2. Package commit `ccf95e46…` and audit PASS `1e62d7e4…` are present and hash-consistent on the fetched refs.
3. The local deployment worktree is clean and at exactly the frozen code commit (or its file-only integration descendant per the preflight).
4. Target host is `root@104.131.191.95` and the service identity matches (tmux `live_v4`, single `python3 -u live_v4.py`).
5. The **actual remote** `/root/Omi-Workspace/arb-executor/live_v4.py` hashes byte-for-byte to git blob `f1857199164664037fef41b024e60f27fa373548` (SHA-256 `834b9e04…`, 997352 bytes).
6. The backup destination named above is absent.
7. The candidate materialization hashes exactly to blob `ebd29103…` / SHA-256 `85fdd653…` / 1011785 bytes.
8. Deployment scope is exactly one file (`arb-executor/live_v4.py`); `git diff --name-only` between the running checkout and the integration commit lists exactly that path; no unrelated staged, copied, or deployable file exists.
9. Pre-deploy compile (`py_compile`), lint gate, and offline CASUKA smoke replay pass on the candidate.
10. No pre-existing ticker shows resting sell quantity greater than authoritative held quantity.

If ANY precondition fails: **stop; mutate nothing; report to operator.**

## 5. Authorized remote mutations (these five, in order, and nothing else)

1. Create ONE immutable backup of the exact preimage at the named backup path and verify its hash equals `834b9e04…` before proceeding.
2. Atomically replace ONLY the target `live_v4.py` with the frozen candidate (via the file-only integration commit + ff-only), and verify the on-disk file hashes to `ebd29103…` before restart.
3. Run the gated deployment script (`deploy_live_v4.sh` → `deploy_gate.sh` lint + smoke).
4. Perform exactly ONE graceful service restart (SIGINT drain, 200s stop window; if the old process survives the window the script exits with the OLD code still trading — that is the required fail-safe, not a retry license).
5. Record post-boot receipts under the unique results directory: process identity, on-disk and in-process source hash (= candidate), health-check result, post-boot audit verdict, and the outcome-proof observations of `OUTCOME_PROOF_PLAN.json`.

## 6. Explicitly forbidden

Order cancellation or placement; position mutation; halt creation/clearing; configuration changes; branch reset/clean/checkout-overwrite; deployment of any P0 REAL-START GUARD revision (v1 `eca101c6`, v2 `3f5d85d4`, v3 `a4996dd0`) or any file other than the single candidate; broad directory copies; a second restart; any retry after mutation begins; any mutation of the T2/research worktrees.

## 7. Post-deployment PASS invariants

- Remote `live_v4.py` equals the frozen candidate byte-for-byte (`ebd29103…` / `85fdd653…`).
- Service healthy after exactly one restart: one process, one tmux session, post-boot audit completes without a new conception halt attributable to this change.
- For every unsettled ticker: authoritative resting exit quantity ≤ authoritative held quantity, always.
- Same-cycle heal/top-up suppression active and receipted (`reconcile_exit_topup_noop` after a full heal; CASUKA-class replay posts zero).
- Zero-booked or settled entries produce zero `filled` classifications and zero false `pair_incomplete` flags (FARRIU/VEGKAW classes).
- No negative exchange quantity outside the named quarantine path.
- No unrelated source or configuration hash changed.

## 8. Mandatory rollback

If source verification, compile, gate, boot health, or the immediate outcome proof fails: rollback is **mandatory**, restoring exactly the preimage from the immutable object `bb085ce06db5932049af85f927a7f9316ad76816:arb-executor/live_v4.py`, verifying blob `f1857199164664037fef41b024e60f27fa373548` and SHA-256 `834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54` on the restored file before the **separately specified rollback restart** (one, via the same gated script), and recording the complete result under the results directory. **No retry of the candidate deployment is authorized after rollback.**

## Verifier acceptance line

RULING CONTEXT: the controlling audits are PASS. This addendum binds package `ccf95e464ead48ca99cef0be62bc65c6ae8ba832`, deployment ID `casuka-d1d3-deploy-20260727-attempt1`, candidate SHA-256 `85fdd653ee85dd598388d3cf6f537999decf0f0bdece6b8b3495a19041ee05d4`, preimage SHA-256 `834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54`, host `root@104.131.191.95`, target `/root/Omi-Workspace/arb-executor/live_v4.py`, results directory `.claude/casuka_deployment_results_casuka-d1d3-deploy-20260727-attempt1/`, and the exact command literal above.
