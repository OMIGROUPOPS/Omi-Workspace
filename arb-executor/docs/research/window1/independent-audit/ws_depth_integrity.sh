#!/bin/bash
set -uo pipefail
cd /root/Omi-Workspace/arb-executor
set -a; . ./.env; set +a
export RCLONE_CONFIG_SPACES_TYPE=s3 RCLONE_CONFIG_SPACES_PROVIDER=DigitalOcean RCLONE_CONFIG_SPACES_ACCESS_KEY_ID="$SPACES_KEY" RCLONE_CONFIG_SPACES_SECRET_ACCESS_KEY="$SPACES_SECRET" RCLONE_CONFIG_SPACES_ENDPOINT=nyc3.digitaloceanspaces.com
B=spaces:omi-tick-archive
F=$(rclone lsf "$B/ws_depth" 2>/dev/null | grep -E "2026072[0]" | head -1)
echo "=== ws_depth integrity sample: $F ==="
rclone cat "$B/ws_depth/$F" 2>/dev/null | zcat 2>/dev/null | python3 - <<'PY'
import sys,json,collections
types=collections.Counter(); seqfields=collections.Counter(); n=0; sample=None
per_mkt_seq=collections.defaultdict(list); msgkeys=collections.Counter()
for line in sys.stdin:
    try: r=json.loads(line)
    except: continue
    n+=1
    m=r.get("m") or {}
    if not isinstance(m,dict):
        continue
    t=m.get("type") or r.get("ev") or "?"
    types[t]+=1
    for k in m: msgkeys[k]+=1
    if sample is None and t in ("orderbook_snapshot","orderbook_delta"): sample=m
    # sequence tracking
    msg=m.get("msg") if isinstance(m.get("msg"),dict) else m
    sid=msg.get("market_ticker") or msg.get("market_id")
    sq=msg.get("seq")
    if sid is not None and sq is not None:
        try: per_mkt_seq[sid].append(int(sq))
        except: pass
print("  total lines=%d"%n)
print("  message types:", dict(types.most_common(10)))
print("  msg keys:", dict(msgkeys.most_common(12)))
# snapshot ancestry: are there snapshots to anchor deltas?
snap=types.get("orderbook_snapshot",0); delta=types.get("orderbook_delta",0)
print("  SNAPSHOT count=%d  DELTA count=%d  (delta-only w/o snapshot => cannot prove full depth)"%(snap,delta))
# sequence gap analysis
gaps=0; resets=0; mkts=0
for sid,seqs in per_mkt_seq.items():
    mkts+=1
    s=sorted(seqs)
    for a,b in zip(s,s[1:]):
        if b==a: continue
        if b<a: resets+=1
        elif b-a>1: gaps+=1
print("  markets with seq=%d  intra-market seq gaps(>1)=%d  seq resets/reconnect=%d"%(mkts,gaps,resets))
if sample: print("  sample depth msg keys:", sorted(sample.keys())[:15])
PY
