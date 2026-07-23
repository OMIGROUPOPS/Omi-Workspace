#!/bin/bash
# lib_producer_guard.sh — robust singleton keepalive guard for tennis.db producers.
#
# Why this exists: the original */5 cron guards used `pgrep -f "python3.*NAME"`.
# Cron runs the guard as `/bin/sh -c '... || tmux ... python3 -u NAME ...'`, and
# that wrapper's OWN command line contains "python3 -u NAME", so pgrep -f matched
# the wrapper itself -> the guard always believed the producer was alive and never
# restarted it after a crash. fv_monitor_v3.py had no guard at all.
#
# Fix: liveness is tested with `pgrep -x -f "<exact child cmdline>"` (whole-cmdline
# exact match). That matches ONLY the real python child — never the bash -c wrapper,
# never this script's shell, never the pgrep invocation. Guards are invoked from a
# script FILE, so the cron line itself carries no producer text to self-match.
#
# Fail-closed: refuse to launch unless the DO volume is mounted AND the app
# tennis.db path is a symlink to the volume copy (prevents recreating tennis.db on
# the root disk). Never launches a duplicate; no-ops when the child is healthy.
#
# Sourced by producer_keepalive.sh (production) and producer_keepalive_test.sh (tests).

PG_VOL="/mnt/omi-trading-data-nyc3"
PG_DB="/root/Omi-Workspace/arb-executor/tennis.db"
PG_DB_TARGET="/mnt/omi-trading-data-nyc3/active/tennis.db"

pg_log() {  # pg_log <name> <decision-text>
  printf '%s keepalive %-13s : %s\n' "$(date -u +%FT%TZ)" "$1" "$2"
}

pg_volume_ok() {  # [mountpoint-override]
  mountpoint -q "${1:-$PG_VOL}"
}

pg_db_symlink_ok() {  # [db-override] [target-override]
  local db="${1:-$PG_DB}" tgt="${2:-$PG_DB_TARGET}"
  [ -L "$db" ] && [ "$(readlink -f "$db" 2>/dev/null)" = "$tgt" ]
}

pg_alive_pids() {  # <exact-full-cmdline> ; prints matching pids (child only)
  pgrep -x -f "$1" 2>/dev/null || true
}

# pg_guard <name> <exact_cmdline> <tmux_session> <launch_cmd> \
#          [mp_override] [db_override] [tgt_override] [dry(0|1)]
# Decisions: SKIP (fail-closed), HEALTHY (no-op), WARN (duplicate -> no launch),
#            ABSENT (dry-run), RELAUNCHED (genuinely absent -> started).
pg_guard() {
  local name="$1" cmd="$2" session="$3" launch="$4"
  local mp="${5:-$PG_VOL}" db="${6:-$PG_DB}" tgt="${7:-$PG_DB_TARGET}" dry="${8:-0}"

  if ! pg_volume_ok "$mp"; then
    pg_log "$name" "SKIP volume not mounted ($mp) — fail-closed"; return 0
  fi
  if ! pg_db_symlink_ok "$db" "$tgt"; then
    pg_log "$name" "SKIP tennis.db not symlink->volume (refuse root recreate): now=$(readlink -f "$db" 2>/dev/null || echo MISSING)"; return 0
  fi

  local pids n; pids="$(pg_alive_pids "$cmd")"; n="$(printf '%s' "$pids" | grep -c . || true)"
  if [ "$n" -ge 2 ]; then
    pg_log "$name" "WARN duplicate pids=[$(echo $pids)] — NOT launching (manual review)"; return 0
  fi
  if [ "$n" -eq 1 ]; then
    pg_log "$name" "HEALTHY pid=$(echo $pids) — no-op"; return 0
  fi

  # genuinely absent
  if [ "$dry" = "1" ]; then
    pg_log "$name" "ABSENT — dry-run, would relaunch tmux session=$session"; return 0
  fi
  tmux kill-session -t "$session" 2>/dev/null || true   # clear a dead/leftover session shell
  tmux new-session -d -s "$session" "$launch"
  sleep 2
  local np; np="$(pg_alive_pids "$cmd")"
  if [ -n "$np" ]; then
    pg_log "$name" "RELAUNCHED tmux session=$session newpid=$(echo $np)"
  else
    pg_log "$name" "RELAUNCH-ATTEMPTED session=$session but child not yet visible (will recheck next cycle)"
  fi
  return 0
}
