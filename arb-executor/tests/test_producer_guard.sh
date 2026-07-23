#!/bin/bash
# producer_keepalive_test.sh — recovery-behaviour tests using ISOLATED FAKE
# fixtures. Never touches the five production producers: every fixture uses a
# unique fake cmdline (python3 -u /tmp/fake_producer_probe.py) and fake tmux
# session names, and cleanup pkills ONLY that exact fake cmdline.
set -uo pipefail

LIB="$(dirname "$0")/lib_producer_guard.sh"; [ -f "$LIB" ] || LIB="/root/lib_producer_guard.sh"
# shellcheck source=/dev/null
. "$LIB"

FAKE_CMD="python3 -u /tmp/fake_producer_probe.py"
FAKE_SESS="keepalive_test_fake"
GOOD_MP="/mnt/omi-trading-data-nyc3"

PASS=0; FAIL=0
chk(){ if [ "$1" = "$2" ]; then echo "  PASS: $3"; PASS=$((PASS+1)); else echo "  FAIL: $3 (got [$1] want [$2])"; FAIL=$((FAIL+1)); fi; }

cleanup(){
  tmux kill-session -t "$FAKE_SESS" 2>/dev/null || true
  tmux kill-session -t "${FAKE_SESS}_dup" 2>/dev/null || true
  tmux kill-session -t "${FAKE_SESS}_x" 2>/dev/null || true
  tmux kill-session -t "${FAKE_SESS}_y" 2>/dev/null || true
  pkill -x -f "$FAKE_CMD" 2>/dev/null || true
  rm -f /tmp/fake_producer_probe.py /tmp/fake_not_symlink_db
}
trap cleanup EXIT
cleanup; sleep 1   # kill any leftover fakes from a prior run

# create the fake producer AFTER the initial cleanup (cleanup rm's this file)
cat > /tmp/fake_producer_probe.py <<'PY'
import time
while True:
    time.sleep(5)
PY

echo "T1: genuinely absent -> relaunch"
pg_guard "FAKE" "$FAKE_CMD" "$FAKE_SESS" "$FAKE_CMD" > /tmp/kt1.log 2>&1; cat /tmp/kt1.log | sed 's/^/    /'
sleep 2
chk "$(pgrep -x -f "$FAKE_CMD" | grep -c . || true)" "1" "one fake now running"
grep -q RELAUNCHED /tmp/kt1.log && chk yes yes "logged RELAUNCHED" || chk no yes "logged RELAUNCHED"

echo "T2: healthy child present -> no-op, same pid"
B="$(pgrep -x -f "$FAKE_CMD")"
pg_guard "FAKE" "$FAKE_CMD" "$FAKE_SESS" "$FAKE_CMD" > /tmp/kt2.log 2>&1; cat /tmp/kt2.log | sed 's/^/    /'
A="$(pgrep -x -f "$FAKE_CMD")"
chk "$B" "$A" "pid unchanged (no restart)"
grep -q HEALTHY /tmp/kt2.log && chk yes yes "logged HEALTHY no-op" || chk no yes "logged HEALTHY no-op"

echo "T3: volume not mounted -> refuse, no launch"
pg_guard "FAKE" "$FAKE_CMD" "${FAKE_SESS}_x" "$FAKE_CMD" "/mnt/does_not_exist_mp" > /tmp/kt3.log 2>&1; cat /tmp/kt3.log | sed 's/^/    /'
grep -q "SKIP volume not mounted" /tmp/kt3.log && chk yes yes "refused on unmounted volume" || chk no yes "refused on unmounted volume"
chk "$(tmux has-session -t ${FAKE_SESS}_x 2>/dev/null && echo y || echo n)" "n" "no session created when unmounted"

echo "T4: tennis.db not symlink->volume -> refuse (root-recreate guard)"
echo x > /tmp/fake_not_symlink_db
pg_guard "FAKE" "$FAKE_CMD" "${FAKE_SESS}_y" "$FAKE_CMD" "$GOOD_MP" "/tmp/fake_not_symlink_db" "/some/volume/target" > /tmp/kt4.log 2>&1; cat /tmp/kt4.log | sed 's/^/    /'
grep -q "SKIP tennis.db not symlink" /tmp/kt4.log && chk yes yes "refused on non-symlink db" || chk no yes "refused on non-symlink db"
chk "$(tmux has-session -t ${FAKE_SESS}_y 2>/dev/null && echo y || echo n)" "n" "no session created on bad db path"

echo "T5: duplicate present -> WARN, no new launch"
tmux new-session -d -s "${FAKE_SESS}_dup" "$FAKE_CMD"; sleep 2
N1="$(pgrep -x -f "$FAKE_CMD" | grep -c . || true)"
pg_guard "FAKE" "$FAKE_CMD" "$FAKE_SESS" "$FAKE_CMD" > /tmp/kt5.log 2>&1; cat /tmp/kt5.log | sed 's/^/    /'
N2="$(pgrep -x -f "$FAKE_CMD" | grep -c . || true)"
grep -q "WARN duplicate" /tmp/kt5.log && chk yes yes "logged WARN duplicate" || chk no yes "logged WARN duplicate"
chk "$N1" "$N2" "no new process launched under duplicate"

echo ""
echo "RESULT: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ]
