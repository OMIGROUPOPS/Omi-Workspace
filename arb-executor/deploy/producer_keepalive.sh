#!/bin/bash
# producer_keepalive.sh — crash protection for the three tennis.db producers whose
# original respawn was defective: betexplorer.py & kalshi_price_scraper.py (cron
# guard self-matched its own wrapper text) and fv_monitor_v3.py (no guard at all).
#
# Invoked by cron every 5 minutes:
#   */5 * * * * bash /root/producer_keepalive.sh >> /tmp/producer_keepalive.log 2>&1
# The cron line carries NO producer text, so the self-match defect cannot recur.
#
# `--check-only` : dry-run (report decisions, never launch) — used to prove the
#                  guard no-ops against the live producers before wiring cron.
#
# te_live.py and tennis_odds.py are intentionally NOT handled here — their existing
# keepalives (te_live_keepalive.sh / respawn_tennis_odds.sh) work and are untouched.
set -uo pipefail

LIB="$(dirname "$0")/lib_producer_guard.sh"; [ -f "$LIB" ] || LIB="/root/lib_producer_guard.sh"
# shellcheck source=/dev/null
. "$LIB"

# serialize overlapping cron runs so two invocations can never double-launch
exec 9>/tmp/producer_keepalive.lock
flock -n 9 || { pg_log "ALL" "another keepalive run in progress — exit"; exit 0; }

DRY=0; [ "${1:-}" = "--check-only" ] && DRY=1
ARB="/root/Omi-Workspace/arb-executor"

pg_guard "betexplorer" "python3 -u betexplorer.py" "betexplorer" \
  "cd $ARB && python3 -u betexplorer.py 2>&1 | tee /tmp/betexplorer.log" "" "" "" "$DRY"

pg_guard "kalshi_price" "python3 -u kalshi_price_scraper.py" "kalshi_price" \
  "cd $ARB && python3 -u kalshi_price_scraper.py 2>&1 | tee /tmp/kalshi_price.log" "" "" "" "$DRY"

pg_guard "fv_monitor" "python3 -u /tmp/fv_monitor_v3.py" "fv_monitor" \
  "cd $ARB && python3 -u /tmp/fv_monitor_v3.py 2>&1 | tee /tmp/fv_monitor.log" "" "" "" "$DRY"
