#!/bin/bash
set -uo pipefail
cd /root/Omi-Workspace/arb-executor
set -a; . ./.env; set +a
export RCLONE_CONFIG_SPACES_TYPE=s3 RCLONE_CONFIG_SPACES_PROVIDER=DigitalOcean
export RCLONE_CONFIG_SPACES_ACCESS_KEY_ID="$SPACES_KEY" RCLONE_CONFIG_SPACES_SECRET_ACCESS_KEY="$SPACES_SECRET"
export RCLONE_CONFIG_SPACES_ENDPOINT=nyc3.digitaloceanspaces.com
B=spaces:omi-tick-archive
rclone lsf "$B/trades" 2>/dev/null | sed 's/\.csv.*$//' > /tmp/sp_trades.txt
rclone lsf "$B/ticks"   2>/dev/null | sed 's/\.csv.*$//' > /tmp/sp_ticks.txt
python3 - <<'PY'
import json
ld=lambda p:[json.loads(l) for l in open(p)]
ev=ld("/srv/omi-research/window1-20260722/normalized/events.jsonl")
fills=ld("/srv/omi-research/window1-20260722/normalized/fills.jsonl")
legs=[L["ticker"] for e in ev for L in e.get("legs") or [] if L.get("ticker")]
trades=set(l.strip() for l in open("/tmp/sp_trades.txt") if l.strip())
ticks=set(l.strip() for l in open("/tmp/sp_ticks.txt") if l.strip())
gap=[t for t in legs if t not in trades]
open("/tmp/gap39.txt","w").write("\n".join(gap))
fill_tk=set(str(f.get("ticker")) for f in fills)
# sibling map
sib={}
for e in ev:
    ls=[L["ticker"] for L in e.get("legs") or [] if L.get("ticker")]
    for t in ls: sib[t]=[x for x in ls if x!=t]
print("gap legs (no trades object): %d"%len(gap))
print("  of gap: have ticks CSV: %d | have private fills: %d"%(
    sum(1 for t in gap if t in ticks), sum(1 for t in gap if t in fill_tk)))
for t in gap:
    s=sib.get(t,[])
    sib_trades=any(x in trades for x in s)
    print("GAP\t%s\tticks=%d\tfills=%d\tsibling_trades=%d"%(t, int(t in ticks), int(t in fill_tk), int(sib_trades)))
PY
echo "=== per-gap-leg ticks last_trade variation (did trades occur?) ==="
while read t; do
  [ -z "$t" ] && continue
  R=$(rclone cat "$B/ticks/$t.csv.gz" 2>/dev/null | zcat 2>/dev/null | awk -F, 'NR==1{for(i=1;i<=NF;i++)if($i=="last_trade")c=i; next} {v=$c+0; if(v>0){seen[v]=1; nz++}} END{print length(seen)" "nz" "NR}')
  echo "  $t : distinct_nonzero_last_trade rows -> [$R] (fmt: distinct nz_rows total_rows)"
done < /tmp/gap39.txt
