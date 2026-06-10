#!/bin/bash
# OMI tick archive -- nightly compress + off-box sync (operator-ratified C-ARCHIVE,
# 2026-06-10). Runs from cron in quiet hours; everything nice/ionice'd -- the running
# bot and any in-flight card are untouchable.
#
# STANDING RULE: NOTHING local is ever deleted unless its checksum-verified twin
# exists in the bucket -- and THIS job deletes nothing regardless; local retention is
# a separate operator decision, taken later on the inventory table.
#
# (a) gzip tick/trade CSVs with mtime >3 days (recurring compression policy, standing)
# (b) rclone copy new .gz to DO Spaces  spaces:omi-tick-archive/{ticks,trades}
# (c) rclone check (checksum) -- one retry pass on mismatch; MISMATCH in the summary
#     line means a file is STILL unverified after retry and needs operator eyes
# (d) one-line summary appended to logs/archive_sync.log
#
# Credentials: SPACES_KEY / SPACES_SECRET in arb-executor/.env (chmod 600, never
# echoed). Absent creds -> compression still runs, sync logs SKIPPED and exits 0.
set -u
BASE=/root/Omi-Workspace/arb-executor
LOG="$BASE/logs/archive_sync.log"
RLOG="$BASE/logs/archive_sync_rclone.log"
BUCKET=omi-tick-archive
TS() { date -u +%FT%TZ; }
cd "$BASE" || exit 1

# (a) recurring compression: >3-day-old raw CSVs, lossless, low priority
NG=$(nice -n 19 ionice -c3 bash -c \
  'find analysis/premarket_ticks analysis/trades -name "*.csv" -mtime +3 -print -exec gzip -f {} \;' \
  | wc -l)

# creds from .env only; never printed
set -a; . ./.env 2>/dev/null; set +a
if [ -z "${SPACES_KEY:-}" ] || [ -z "${SPACES_SECRET:-}" ]; then
    echo "$(TS) gzipped=$NG uploaded=- verified=- bucket=- result=SKIPPED_NO_CREDS" >> "$LOG"
    exit 0
fi
export RCLONE_CONFIG_SPACES_TYPE=s3
export RCLONE_CONFIG_SPACES_PROVIDER=DigitalOcean
export RCLONE_CONFIG_SPACES_ACCESS_KEY_ID="$SPACES_KEY"
export RCLONE_CONFIG_SPACES_SECRET_ACCESS_KEY="$SPACES_SECRET"
export RCLONE_CONFIG_SPACES_ENDPOINT=nyc3.digitaloceanspaces.com
export RCLONE_CONFIG_SPACES_ACL=private
# no global --log-level: the copy call needs -v (INFO) so its "Copied" lines are
# countable for the summary; other calls use rclone's default NOTICE.
RC() { nice -n 19 ionice -c3 rclone --transfers 4 --checkers 8 --bwlimit 30M "$@"; }

RC mkdir "spaces:$BUCKET" >> "$RLOG" 2>&1

RESULT=OK
UPLOADED=0
sync_one() {  # $1 = local dir, $2 = remote prefix
    local dir=$1 pfx=$2 n
    n=$(RC copy --include "*.csv.gz" -v "$dir" "spaces:$BUCKET/$pfx" 2>&1 \
        | tee -a "$RLOG" | grep -c ": Copied")
    UPLOADED=$((UPLOADED + n))
    if ! RC check --one-way --include "*.csv.gz" "$dir" "spaces:$BUCKET/$pfx" >> "$RLOG" 2>&1; then
        # one retry pass: re-copy (rclone re-transfers differing files), re-check
        RC copy --include "*.csv.gz" "$dir" "spaces:$BUCKET/$pfx" >> "$RLOG" 2>&1
        if ! RC check --one-way --include "*.csv.gz" "$dir" "spaces:$BUCKET/$pfx" >> "$RLOG" 2>&1; then
            RESULT=MISMATCH
        fi
    fi
}
sync_one analysis/premarket_ticks ticks
sync_one analysis/trades trades

BUCKET_SIZE=$(RC size "spaces:$BUCKET" 2>/dev/null | tr "\n" " ")
NV=$(find analysis/premarket_ticks analysis/trades -name "*.csv.gz" | wc -l)
echo "$(TS) gzipped=$NG uploaded=$UPLOADED verified_pool=$NV result=$RESULT bucket: $BUCKET_SIZE" >> "$LOG"
[ "$RESULT" = OK ]
