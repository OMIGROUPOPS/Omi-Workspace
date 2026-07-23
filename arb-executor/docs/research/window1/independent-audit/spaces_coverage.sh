#!/bin/bash
set -uo pipefail
cd /root/Omi-Workspace/arb-executor
set -a; . ./.env; set +a
export RCLONE_CONFIG_SPACES_TYPE=s3 RCLONE_CONFIG_SPACES_PROVIDER=DigitalOcean
export RCLONE_CONFIG_SPACES_ACCESS_KEY_ID="$SPACES_KEY" RCLONE_CONFIG_SPACES_SECRET_ACCESS_KEY="$SPACES_SECRET"
export RCLONE_CONFIG_SPACES_ENDPOINT=nyc3.digitaloceanspaces.com
B=spaces:omi-tick-archive
rclone lsf "$B/ticks" 2>/dev/null | sed 's/\.csv.*$//' > /tmp/spaces_ticks.txt
rclone lsf "$B/trades" 2>/dev/null | sed 's/\.csv.*$//' > /tmp/spaces_trades.txt
rclone lsf "$B/ws_depth" 2>/dev/null > /tmp/spaces_wsdepth.txt
echo "spaces leg-tickers: ticks=$(wc -l </tmp/spaces_ticks.txt) trades=$(wc -l </tmp/spaces_trades.txt) wsdepth_objs=$(wc -l </tmp/spaces_wsdepth.txt)"
python3 - <<'PY'
import json, collections
ld=lambda p:[json.loads(l) for l in open(p)]
ev=ld("/srv/omi-research/window1-20260722/normalized/events.jsonl")
legtk=[]; ev_legs={}
for e in ev:
    ts=[L["ticker"] for L in e.get("legs") or [] if L.get("ticker")]
    ev_legs[e["event_id"]]=ts; legtk+=ts
legset=set(legtk)
ticks=set(l.strip() for l in open("/tmp/spaces_ticks.txt") if l.strip())
trades=set(l.strip() for l in open("/tmp/spaces_trades.txt") if l.strip())
print("D games=%d  total leg-tickers=%d (distinct %d)"%(len(ev),len(legtk),len(legset)))
tk_cov=sum(1 for t in legset if t in ticks); tr_cov=sum(1 for t in legset if t in trades)
print("=== LEG-TICKER COVERAGE vs Spaces ===")
print("  leg-tickers with ticks(depth) CSV : %d/%d (%.1f%%)"%(tk_cov,len(legset),100*tk_cov/len(legset)))
print("  leg-tickers with trades(prints) CSV: %d/%d (%.1f%%)"%(tr_cov,len(legset),100*tr_cov/len(legset)))
# per-GAME coverage: both legs have ticks
full=part=none=0
tbl=[]
for e in ev:
    ls=ev_legs[e["event_id"]]
    got=[1 if t in ticks else 0 for t in ls]
    s=sum(got)
    if len(ls)>=2 and s==2: full+=1; c="BOTH"
    elif s==1: part+=1; c="ONE"
    else: none+=1; c="NONE"
    tbl.append((e["event_id"],c,s,len(ls)))
print("=== PER-GAME DEPTH-TICK COVERAGE (804) ===")
print("  both legs covered: %d  one leg: %d  neither: %d"%(full,part,none))
# sample event-by-event rows
print("=== sample event-by-event (first 8) ===")
for eid,c,s,n in tbl[:8]: print("  %-42s %s (%d/%d legs)"%(eid,c,s,n))
# save games with no coverage for scrutiny
missing=[eid for eid,c,s,n in tbl if c!="BOTH"]
print("  games without full both-leg tick coverage: %d"%len(missing))
PY
