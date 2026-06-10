#!/bin/bash
# Respawn the tennis_odds collector if dead (C-SIDECAR, 2026-06-10). Cron */5.
#
# Why a script and not a crontab one-liner: a crontab `pgrep -f ... || tmux ...`
# line ALWAYS self-matches -- cron's own `sh -c` cmdline contains both the pgrep
# pattern and the tmux command text (the plain "python3 -u tennis_odds.py"), so
# the || branch is unreachable. That dead respawn is how the Jun 5 collector
# death went unrevived for 5 days. From this script, the running process cmdline
# is just "bash <script-path>" -- nothing for the pattern to match.
#
# Liveness = a REAL python3 process (comm-filtered, watchdog.sh discipline): the
# tmux wrapper bash also matches the pattern text and must not count as alive.
for p in $(pgrep -f "python3 -u [t]ennis_odds.py"); do
    [ "$(cat /proc/$p/comm 2>/dev/null)" = python3 ] && exit 0
done
tmux kill-session -t tennis_odds 2>/dev/null  # clear a dead-named session if any
tmux new-session -d -s tennis_odds \
    "cd /root/Omi-Workspace/arb-executor && python3 -u tennis_odds.py 2>&1 | tee -a /tmp/tennis_odds.log"
echo "$(date -u +%FT%TZ) respawned tennis_odds (session created)"
