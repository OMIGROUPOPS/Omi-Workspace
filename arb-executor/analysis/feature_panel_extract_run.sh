#!/usr/bin/env bash
# Approved feature-only source extraction. No model fit and no source writes.
set -euo pipefail
root=/mnt/omi-trading-data-nyc3/library/feature_panel_v1
exec 9>"$root/FEATURE_POPULATION_RUN.lock"
flock -n 9 || { echo 'DUPLICATE_FEATURE_POPULATION_REFUSED'; exit 73; }
export PYTHONDONTWRITEBYTECODE=1
finish() {
  code=$?
  printf '%s\n' "$code" > "$root/FEATURE_POPULATION_RUN.exit"
  printf 'EXIT code=%s\n' "$code"
}
trap finish EXIT
printf '%s\n' "$$" > "$root/FEATURE_POPULATION_RUN.pid"
script="$root/feature_panel_extract.py"
common=(--db /mnt/omi-trading-data-nyc3/subsecond/subsecond_store.db
  --cutter /mnt/omi-trading-data-nyc3/library/build_range_overlap_library_ticks.py
  --library /mnt/omi-trading-data-nyc3/library/RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz
  --library-receipt /mnt/omi-trading-data-nyc3/library/RANGE_OVERLAP_LIBRARY_TICKS_RECEIPT.json
  --repo-root /root/Omi-Workspace
  --store-lock /root/Omi-Workspace/arb-executor/state/subsecond_store.db.lock
  --categories ATP_MAIN ATP_CHALL)
printf 'PHASE SOURCE_SPOOL\n'
if [[ ! -f "$root/production_spool/SOURCE_SPOOL_RECEIPT.json" ]]; then
  python3 "$script" "${common[@]}" --output-dir "$root/production_spool" --prepare-only
else
  printf 'SPOOL_PRESENT (phase two verifies sealed hash and source binding)\n'
fi
printf 'PHASE ORIGINAL_OBJECT_FEATURES\n'
python3 "$script" "${common[@]}" --output-dir "$root/production_sources" \
  --source-spool "$root/production_spool/PREPARED_SOURCES.sqlite" --resume
printf 'CORE_COMPLETE; supplemental odds binding deferred (local audit export not authorized)\n'
