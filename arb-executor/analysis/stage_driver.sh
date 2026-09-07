#!/bin/bash
# SUBSECOND CONSOLIDATION — staged-ingest driver (2026-09-05, operator-approved method change).
# Runs once under nohup; installs no cron. Log: /tmp/stage_driver.log
set -u
cd /root/Omi-Workspace/arb-executor || exit 1
MNT=/mnt/omi-trading-data-nyc3/subsecond
STAGE=/root/tick_stage
mkdir -p $MNT/tmp $STAGE/tmp $STAGE/ticks
export SQLITE_TMPDIR=$MNT/tmp
say(){ echo "$(date -u +%FT%TZ) $*"; }
set -a; . ./.env; set +a
export RCLONE_CONFIG_SPACES_TYPE=s3 RCLONE_CONFIG_SPACES_PROVIDER=DigitalOcean RCLONE_CONFIG_SPACES_ACCESS_KEY_ID="$SPACES_KEY" RCLONE_CONFIG_SPACES_SECRET_ACCESS_KEY="$SPACES_SECRET" RCLONE_CONFIG_SPACES_ENDPOINT=nyc3.digitaloceanspaces.com
say "driver start; disk:"; df -h / /mnt/omi-trading-data-nyc3 | tail -2

# ---- A. compact the store off the 95%-full root disk (VACUUM INTO the data volume; path kept via symlink)
if [ ! -L state/subsecond_store.db ]; then
  if [ -f /tmp/stage_move_counts.json ] && [ -f $MNT/subsecond_store.db ] && [ $MNT/subsecond_store.db -nt state/subsecond_store.db ] && python3 -c "
import json,sys; r=json.load(open('/tmp/stage_move_counts.json'))
ok = r.get('quick_check')=='ok' and all(v[0]==v[1] for k,v in r.items() if isinstance(v,list))
print('prior verification:', r); sys.exit(0 if ok else 1)"; then
    say "A: compacted copy already verified (counts equal, quick_check ok) and newer than the root store; skipping re-verify"
  else
    say "A: VACUUM INTO $MNT/subsecond_store.db"
    rm -f $MNT/subsecond_store.db
    python3 - <<PY
import sqlite3, time
t = time.time(); con = sqlite3.connect("state/subsecond_store.db", timeout=600)
con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
con.execute("VACUUM INTO '$MNT/subsecond_store.db'")
print("vacuum into", round(time.time() - t), "s")
PY
    ls -la $MNT/subsecond_store.db; df -h / /mnt/omi-trading-data-nyc3 | tail -2
    say "A: verify counts old vs new + quick_check"
    python3 - <<PY
import sqlite3, json, sys, time
t = time.time()
o = sqlite3.connect("file:state/subsecond_store.db?mode=ro", uri=True); n = sqlite3.connect("file:$MNT/subsecond_store.db?mode=ro", uri=True)
res = {}
for tb in ("ingest_log", "cadence", "dupes", "ticks", "prints"):
    res[tb] = [o.execute("select count(*) from " + tb).fetchone()[0], n.execute("select count(*) from " + tb).fetchone()[0]]
qc = n.execute("pragma quick_check").fetchone()[0]
res["quick_check"] = qc; res["seconds"] = round(time.time() - t)
print(json.dumps(res)); json.dump(res, open("/tmp/stage_move_counts.json", "w"))
ok = all(v[0] == v[1] for k, v in res.items() if isinstance(v, list)) and qc == "ok"
print("MOVE_OK" if ok else "MOVE_MISMATCH"); sys.exit(0 if ok else 2)
PY
    [ $? -eq 0 ] || { say "ABORT: move verification failed (root store untouched)"; exit 2; }
  fi
  say "A: replace root store with symlink"
  rm -f state/subsecond_store.db state/subsecond_store.db-wal state/subsecond_store.db-shm
  ln -s $MNT/subsecond_store.db state/subsecond_store.db
  ls -la state/subsecond_store.db; df -h / /mnt/omi-trading-data-nyc3 | tail -2
  say "A: drop p_key on the moved store (its pages are reused by the ticks load)"
  python3 -c "
import sqlite3, time; t = time.time(); con = sqlite3.connect('state/subsecond_store.db', timeout=600)
con.execute('DROP INDEX IF EXISTS p_key'); con.commit(); con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
print('dropped p_key', round(time.time() - t), 's; freelist pages', con.execute('pragma freelist_count').fetchone()[0])"
fi

# ---- B. unique index (idempotent)
say "B: prep"
python3 analysis/subsecond_stage_ingest.py --prep || { say "ABORT: prep failed"; exit 3; }

# ---- C. month batches: stage → verify against listing → ingest → receipt check → delete batch
for M in 2026-04 2026-05 2026-06 2026-07; do
  if [ -f /tmp/stage_driver.STOP ]; then say "STOP file present; halting at batch boundary before $M"; exit 0; fi
  case $M in
    2026-04) INC=(--include "*-26APR*"); MM=APR;;
    2026-05) INC=(--include "*-26MAY*"); MM=MAY;;
    2026-06) INC=(--include "*-26JUN*"); MM=JUN;;
    2026-07) INC=(--include "*-26JUL0*" --include "*-26JUL1*" --include "*-26JUL2[0-5]*"); MM=JUL;;
  esac
  say "C[$M]: stage"; t0=$(date +%s)
  rclone copy "${INC[@]}" --transfers 16 --checkers 32 --buffer-size 1M --use-mmap --stats 10m --stats-one-line spaces:omi-tick-archive/ticks $STAGE/ticks 2>&1 | tail -3
  say "C[$M]: staged in $(( $(date +%s) - t0 )) s"; df -h / | tail -1
  python3 - <<PY
import json, re, sys, os, glob
MON = {"APR": 4, "MAY": 5, "JUN": 6, "JUL": 7}
L = json.load(open("/tmp/spaces_ticks_lsjson.json")); m = int("$M"[5:7])
def want(o):
    mm = re.search(r"-(\d\d)([A-Z]{3})(\d\d)", o["Path"])
    return bool(mm) and MON.get(mm.group(2)) == m and (m != 7 or int(mm.group(3)) <= 25)
exp = [o for o in L if want(o)]
got = {os.path.relpath(p, "$STAGE/ticks").replace(os.sep, "/"): os.path.getsize(p) for p in glob.glob("$STAGE/ticks/**/*.csv.gz", recursive=True)}
missing = [o["Path"] for o in exp if o["Path"] not in got]; sizebad = [o["Path"] for o in exp if o["Path"] in got and got[o["Path"]] != o["Size"]]
r = {"month": "$M", "expected_objects": len(exp), "expected_bytes": sum(o["Size"] for o in exp), "staged_objects": len(got), "staged_bytes": sum(got.values()), "missing": len(missing), "size_mismatch": len(sizebad), "seconds_stage": $(( $(date +%s) - t0 ))}
print(json.dumps(r)); json.dump(r, open("/tmp/stage_verify_$M.json", "w"))
sys.exit(0 if not missing and not sizebad else 4)
PY
  [ $? -eq 0 ] || { say "ABORT: staging verification failed for $M"; exit 4; }
  say "C[$M]: ingest"; t0=$(date +%s)
  python3 -u analysis/subsecond_stage_ingest.py --ingest --month $M --listing /tmp/spaces_ticks_lsjson.json --progress /tmp/stage_ingest_progress.json > /tmp/stage_ingest_$M.log 2>&1
  rc=$?; say "C[$M]: ingest rc=$rc in $(( $(date +%s) - t0 )) s"; tail -c 1500 /tmp/stage_ingest_$M.log; echo
  [ $rc -eq 0 ] || { say "ABORT: ingest failed for $M (batch kept on disk)"; exit 5; }
  python3 - <<PY
import json, sqlite3, sys
v = json.load(open("/tmp/stage_verify_$M.json"))
con = sqlite3.connect("file:state/subsecond_store.db?mode=ro", uri=True)
n = con.execute("select count(*) from ingest_log where src='spaces_ticks' and path like 'spaces:ticks/%-26$MM%'").fetchone()[0]
print("ingest_log spaces_ticks objects named $MM:", n, "expected >=", v["expected_objects"])
sys.exit(0 if n >= v["expected_objects"] else 6)
PY
  [ $? -eq 0 ] || { say "ABORT: month receipt check failed for $M (batch kept on disk)"; exit 6; }
  say "C[$M]: receipted; deleting staged batch"
  rm -rf $STAGE/ticks; mkdir -p $STAGE/ticks
  df -h / /mnt/omi-trading-data-nyc3 | tail -2
done

# ---- D. receipt (sqlite temp on root, free again after the batches)
export SQLITE_TMPDIR=$STAGE/tmp
say "D: receipt"; t0=$(date +%s)
python3 -u analysis/subsecond_stage_ingest.py --receipt /tmp/CONSOLIDATION_RECEIPT_20260904.json > /tmp/stage_receipt.log 2>&1
say "D: receipt rc=$? in $(( $(date +%s) - t0 )) s"; tail -c 500 /tmp/stage_receipt.log; echo
say "DONE"
