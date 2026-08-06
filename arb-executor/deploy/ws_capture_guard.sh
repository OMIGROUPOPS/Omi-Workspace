#!/bin/bash
# Recorder-only supervisor. Exact process identity prevents capture-only helper
# arguments from being mistaken for the recorder itself.
pgrep -f '^python3 -u ws_depth_recorder.py$' >/dev/null 2>&1 || \
  tmux new-session -d -s ws_depthrec \
    'cd /root/Omi-Workspace/arb-executor && python3 -u ws_depth_recorder.py >> /tmp/ws_depthrec.out 2>&1'
