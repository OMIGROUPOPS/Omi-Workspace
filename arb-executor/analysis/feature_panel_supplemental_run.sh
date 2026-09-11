#!/usr/bin/env bash
# Source availability only; no local odds audit metadata is uploaded.
set -euo pipefail
root=/mnt/omi-trading-data-nyc3/library/feature_panel_v1
exec 9>"$root/FEATURE_SUPPLEMENTAL_RUN.lock"
flock -n 9 || { echo 'DUPLICATE_FEATURE_SUPPLEMENTAL_REFUSED'; exit 73; }
export PYTHONDONTWRITEBYTECODE=1
finish() {
  code=$?
  printf '%s\n' "$code" > "$root/FEATURE_SUPPLEMENTAL_RUN.exit"
  printf 'EXIT code=%s\n' "$code"
}
trap finish EXIT
printf '%s\n' "$$" > "$root/FEATURE_SUPPLEMENTAL_RUN.pid"
python3 "$root/feature_panel_extract_supplemental.py" \
  --db /mnt/omi-trading-data-nyc3/subsecond/subsecond_store.db \
  --cutter /mnt/omi-trading-data-nyc3/library/build_range_overlap_library_ticks.py \
  --library /mnt/omi-trading-data-nyc3/library/RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz \
  --library-receipt /mnt/omi-trading-data-nyc3/library/RANGE_OVERLAP_LIBRARY_TICKS_RECEIPT.json \
  --repo-root /root/Omi-Workspace \
  --store-lock /root/Omi-Workspace/arb-executor/state/subsecond_store.db.lock \
  --output-dir "$root/production_supplemental" --categories ATP_MAIN ATP_CHALL \
  --supplemental-only \
  --foundation /root/Omi-Workspace/arb-executor/data/durable/per_minute_universe/per_minute_features.parquet \
  --foundation-sha256 9fde4b5d30e56d99efa0637fe042cb6ca4505274e85e42769b4cedc25e3e5ff4 \
  --odds-dir /root/Omi-Workspace/arb-executor/data/durable/fv_history/by_month \
  --record-odds-hashes-only
