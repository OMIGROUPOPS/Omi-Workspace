# CASUKA deployment and rollback templates

Status: **TEMPLATE ONLY — NOT AUTHORIZED OR EXECUTED**

These templates intentionally cannot deploy from this PRE-RUN alone. A future
operator authorization must supply an audited, file-only integration commit on
top of the actual VPS checkout. This prevents the historical checkout/file
divergence from silently bundling any P0 rider.

## Candidate materialization preflight

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

## Future deployment command

Only after the preceding checks, the independent package audit, the outcome
proof, and a separate operator authorization all pass:

```bash
OUTCOME_PROOF="$OUTCOME_PROOF" \
  /root/Omi-Workspace/arb-executor/deploy/deploy_live_v4.sh \
  "$AUTHORIZED_INTEGRATION_COMMIT"
```

## Rollback materialization and verification

Rollback is also separately authorized and file-only:

```bash
set -euo pipefail
: "${AUTHORIZED_ROLLBACK_COMMIT:?separate rollback authorization required}"
REPO=/root/Omi-Workspace
ROLLBACK_BLOB=f1857199164664037fef41b024e60f27fa373548
test "$(git -C "$REPO" ls-tree "$AUTHORIZED_ROLLBACK_COMMIT" arb-executor/live_v4.py | awk '{print $3}')" = "$ROLLBACK_BLOB"
test "$(git -C "$REPO" diff --name-only HEAD "$AUTHORIZED_ROLLBACK_COMMIT")" = "arb-executor/live_v4.py"
git -C "$REPO" merge-base --is-ancestor HEAD "$AUTHORIZED_ROLLBACK_COMMIT"
OUTCOME_PROOF="$ROLLBACK_OUTCOME_PROOF" \
  "$REPO/arb-executor/deploy/deploy_live_v4.sh" \
  "$AUTHORIZED_ROLLBACK_COMMIT"
```

No command in this file was invoked while building the PRE-RUN.
