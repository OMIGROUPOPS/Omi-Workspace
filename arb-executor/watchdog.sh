#!/bin/bash
# Run via cron every 5 min. Restarts dead sidecars.
# Install: */5 * * * * /root/Omi-Workspace/arb-executor/watchdog.sh >> /var/log/watchdog.log 2>&1

cd /root/Omi-Workspace/arb-executor

check_and_restart() {
    local name=$1
    local tmux_session=$2
    local start_cmd=$3

    if ! pgrep -f "$name" > /dev/null; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $name is dead, restarting in tmux session $tmux_session"
        tmux kill-session -t "$tmux_session" 2>/dev/null
        tmux new-session -d -s "$tmux_session" "$start_cmd"
    fi
}

check_and_restart "tennis_odds.py" "odds" "cd /root/Omi-Workspace/arb-executor && PYTHONUNBUFFERED=1 python3 tennis_odds.py 2>&1 | tee -a logs/tennis_odds.log"
check_and_restart "betexplorer.py" "betexplorer" "cd /root/Omi-Workspace/arb-executor && PYTHONUNBUFFERED=1 python3 betexplorer.py 2>&1 | tee -a logs/betexplorer_console.log"
check_and_restart "fv_monitor" "fv_monitor" "cd /root/Omi-Workspace/arb-executor && PYTHONUNBUFFERED=1 python3 /tmp/fv_monitor_v3.py 2>&1 | tee -a /tmp/fv_monitor_console.log"
check_and_restart "live_v3.py" "live_v3" "cd /root/Omi-Workspace/arb-executor && PYTHONUNBUFFERED=1 python3 live_v3.py 2>&1 | tee -a logs/live_v3_console.log"
