#!/bin/bash
# Install the nightly shape-accumulator cron (PLEX_REGRESSION_RULING §1, 2026-07-06).
# Idempotent. MUST be run as a file ON the VPS (never inline over ssh — the 06-2x
# crontab-wipe law: state-changing ops via scp'd files only).
set -euo pipefail
LINE='45 4 * * * cd /root/Omi-Workspace/arb-executor && python3 analysis/shape_accumulator.py >> /tmp/shape_accum.log 2>&1'
( crontab -l 2>/dev/null | grep -v shape_accumulator || true ; echo "$LINE" ) | crontab -
echo "--- crontab now:"
crontab -l | grep shape_accumulator
echo "CRON INSTALLED"
