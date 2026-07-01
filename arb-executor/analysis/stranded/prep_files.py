#!/usr/bin/env python3
import json
from datetime import datetime, timezone
stranded=json.load(open("/tmp/stranded_rolldowns.json"))
hours=set(); tickers=set()
for s in stranded:
    tickers.add(s["ticker"])
    rds=sorted(s["rolldowns"]); cx=s["cancel_ts"]
    for i,(ts,touch,nt) in enumerate(rds):
        end = rds[i+1][0] if i+1<len(rds) else (cx if cx else ts+7200)
        # collect every UTC hour in [ts, end]
        h=int(ts//3600)*3600
        while h<=end:
            d=datetime.fromtimestamp(h,timezone.utc)
            hours.add(d.strftime("ws_%Y%m%d_%H.jsonl.gz")); h+=3600
open("/tmp/need_files.txt","w").write("\n".join(sorted(hours)))
open("/tmp/need_tickers.txt","w").write("\n".join(sorted(tickers)))
print(f"{len(hours)} hour-files, {len(tickers)} tickers")
print("\n".join(sorted(hours)))
