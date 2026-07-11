#!/bin/bash
# THE deploy procedure for live_v4. The restart REQUIRES the gate.
#   ./deploy/deploy_live_v4.sh [git-ref]     (default: origin/<current-branch>)
# Steps: fetch+ff-only to the ref -> DEPLOY GATE (lint + smoke replay) ->
# graceful restart in tmux (SIGINT drain honored) -> post-boot health check.
set -euo pipefail

REPO_ROOT="/root/Omi-Workspace"
ARB="$REPO_ROOT/arb-executor"
BRANCH="$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD)"
REF="${1:-origin/$BRANCH}"
TMUX_SESSION="live_v4"
BOOT_CMD="cd $ARB && ulimit -n 262144 && python3 -u live_v4.py >> /tmp/live_v4.log 2>&1"

echo "=== DEPLOY live_v4 -> $REF ==="
git -C "$REPO_ROOT" fetch origin
git -C "$REPO_ROOT" merge --ff-only "$REF"
SHA=$(git -C "$REPO_ROOT" rev-parse --short HEAD)
echo "checked out $SHA"

# ---- THE GATE (law 2026-07-04): refuse to restart unless it passes ----
bash "$ARB/deploy/deploy_gate.sh" "$ARB"

# [C-SYSTEM-PAGE] regenerate the build-time knob census artifact per deploy
# (classification computed from knob_citations.json; uncited knobs land NAKED)
python3 "$ARB/analysis/knob_census_check.py" --emit || echo "WARN: census emit failed (viewer will show stale census stamp)"

# ---- graceful restart ----
echo "--- stopping current bot (SIGINT -> graceful drain)"
if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
  tmux send-keys -t "$TMUX_SESSION" C-c || true
  for i in $(seq 1 20); do
    pgrep -f "python3 -u live_v4.py" >/dev/null || break
    sleep 1
  done
  if pgrep -f "python3 -u live_v4.py" >/dev/null; then
    echo "DEPLOY FAIL: bot did not stop within 20s; NOT killing hard. Investigate."
    exit 1
  fi
  tmux kill-session -t "$TMUX_SESSION" 2>/dev/null || true
fi

echo "--- booting $SHA"
tmux new-session -d -s "$TMUX_SESSION" "$BOOT_CMD"
sleep 15

PID=$(pgrep -f "python3 -u live_v4.py" | head -1 || true)
if [ -z "$PID" ]; then
  echo "DEPLOY FAIL: bot not running 15s after boot. tail /tmp/live_v4.log:"
  tail -20 /tmp/live_v4.log
  exit 1
fi

# 30s error-free window on the fresh jsonl log
sleep 30
TODAY_LOG="$ARB/logs/live_v3_$(date +%Y%m%d).jsonl"
ERRS=$(grep -c '"event": "error"\|"event": "on_bbo_update_error"' "$TODAY_LOG" 2>/dev/null || echo 0)
BOOT_ERRS=$(tail -200 /tmp/live_v4.log | grep -c 'Traceback' || true)
echo "post-boot: PID=$PID error-events-today=$ERRS console-tracebacks(recent)=$BOOT_ERRS"
if [ "$BOOT_ERRS" -gt 0 ]; then
  echo "DEPLOY WARN: tracebacks in console tail -- inspect /tmp/live_v4.log"
fi

# [C47-ENFORCE] the post-boot book audit MUST run within 5 min; verify on the
# JSONL (C47: key-presence on the jsonl, never the truncated console log).
echo "--- waiting for post_boot_audit on the jsonl (max 300s)"
AUDIT_LINE=""
for i in $(seq 1 60); do
  AUDIT_LINE=$(grep '"event": "post_boot_audit"' "$TODAY_LOG" 2>/dev/null | tail -1 || true)
  [ -n "$AUDIT_LINE" ] && break
  sleep 5
done
if [ -z "$AUDIT_LINE" ]; then
  echo "DEPLOY FAIL: post_boot_audit never appeared on the jsonl within 300s (C47-ENFORCE)."
  exit 1
fi
VERDICT=$(printf '%s' "$AUDIT_LINE" | grep -o '"verdict": "[A-Z]*"' | head -1)
echo "post_boot_audit: $VERDICT"
if printf '%s' "$VERDICT" | grep -q FAIL; then
  echo "AUDIT FAIL: conceptions HALTED (exits keep working). Halt clears on a passing re-audit."
  echo "Alert artifact under .claude/audit_halt/ (committed+pushed by the bot)."
fi
# [C50] record the deployed SHA -- the next gate's two-file close-out window starts here
git -C "$REPO_ROOT" rev-parse HEAD > "$ARB/state/last_deploy_sha"
echo "=== DEPLOYED $SHA (PID $PID, tmux $TMUX_SESSION) ==="
