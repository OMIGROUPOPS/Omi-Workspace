#!/bin/bash
# Exact CASUKA deployment-control V2 rollback.
# Executed only by the one-shot controller after MUTATION_STARTED.
set -euo pipefail

TARGET="${1:?target required}"
BACKUP="${2:?backup required}"
TMUX_SESSION="${3:?tmux session required}"
BOOT_CMD="${4:?boot command required}"
EXPECTED_SHA256="${5:?preimage sha256 required}"
EXPECTED_BYTES="${6:?preimage bytes required}"
ARB="${7:?arb root required}"

test -f "$BACKUP"
test "$(sha256sum "$BACKUP" | awk '{print $1}')" = "$EXPECTED_SHA256"
test "$(stat -c %s "$BACKUP")" = "$EXPECTED_BYTES"

TMP="$TARGET.rollback.$$"
trap 'rm -f "$TMP"' EXIT
install -m 0644 "$BACKUP" "$TMP"
test "$(sha256sum "$TMP" | awk '{print $1}')" = "$EXPECTED_SHA256"
test "$(stat -c %s "$TMP")" = "$EXPECTED_BYTES"
mv "$TMP" "$TARGET"
trap - EXIT
test "$(sha256sum "$TARGET" | awk '{print $1}')" = "$EXPECTED_SHA256"
test "$(stat -c %s "$TARGET")" = "$EXPECTED_BYTES"

python3 -m py_compile "$TARGET"
python3 "$ARB/deploy/lint_gate.py" "$TARGET"

STOP_WINDOW_SEC=200
if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
  tmux send-keys -t "$TMUX_SESSION" C-c
  STOPPED=0
  for _ in $(seq 1 "$STOP_WINDOW_SEC"); do
    if ! pgrep -af '^python3 -u live_v4.py$' >/dev/null; then
      STOPPED=1
      break
    fi
    sleep 1
  done
  if [ "$STOPPED" -ne 1 ]; then
    echo "ROLLBACK FAIL: candidate process survived graceful stop window"
    exit 1
  fi
  tmux kill-session -t "$TMUX_SESSION" 2>/dev/null || true
fi

tmux new-session -d -s "$TMUX_SESSION" "$BOOT_CMD"
sleep 15
if ! pgrep -af '^python3 -u live_v4.py$' >/dev/null; then
  echo "ROLLBACK FAIL: restored process did not boot"
  exit 1
fi
sleep 30

TODAY_LOG="$ARB/logs/live_v3_$(date +%Y%m%d).jsonl"
AUDIT_LINE=""
for _ in $(seq 1 60); do
  AUDIT_LINE=$(grep '"event": "post_boot_audit"' "$TODAY_LOG" 2>/dev/null | tail -1 || true)
  [ -n "$AUDIT_LINE" ] && break
  sleep 5
done
if [ -z "$AUDIT_LINE" ]; then
  echo "ROLLBACK FAIL: post_boot_audit absent"
  exit 1
fi
printf '%s' "$AUDIT_LINE" | grep -q '"verdict": "PASS"'
echo "ROLLBACK PASS: exact preimage restored and healthy"
