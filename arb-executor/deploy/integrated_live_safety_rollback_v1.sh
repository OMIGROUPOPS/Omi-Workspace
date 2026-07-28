#!/bin/bash
# Exact integrated live-safety deployment-control V1 rollback.
# Executed only by the one-shot controller after MUTATION_STARTED.
set -euo pipefail

TARGET="${1:?target required}"
BACKUP="${2:?backup required}"
TMUX_SESSION="${3:?tmux session required}"
EXPECTED_SHA256="${4:?preimage sha256 required}"
EXPECTED_BYTES="${5:?preimage bytes required}"
INSTALLED_CRON_PATH="${6:?installed crontab path required}"
INHIBITED_CRON_SHA256="${7:?inhibited crontab sha256 required}"
ORIGINAL_CRON_BACKUP="${8:?original crontab backup required}"
ORIGINAL_CRON_SHA256="${9:?original crontab backup sha256 required}"

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

if pgrep -af '^python3 -u live_v4.py$' >/dev/null; then
  echo "ROLLBACK FAIL: candidate process still present"
  exit 1
fi

test "$(sha256sum "$INSTALLED_CRON_PATH" | awk '{print $1}')" = "$INHIBITED_CRON_SHA256"
test -f "$ORIGINAL_CRON_BACKUP"
test "$(sha256sum "$ORIGINAL_CRON_BACKUP" | awk '{print $1}')" = "$ORIGINAL_CRON_SHA256"

echo "ROLLBACK PASS: exact preimage restored; engine parked; cron inhibited"
