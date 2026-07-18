#!/bin/bash
# P0 (5) — promote actual-grade milestone starts into official_ts tier,
# then re-cut the range spectrum on the upgraded right edges (both passes).
set -euo pipefail
cd /root/Omi-Workspace/arb-executor
python3 - <<'EOF'
import json, re
from datetime import datetime
def ep(s):
    try: return datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
    except Exception: return None
ms = json.load(open('state/milestone_starts.json'))
promoted = 0
rows = []
for l in open('state/corpus_events_v2.jsonl'):
    r = json.loads(l)
    sd = (ms.get(r['event']) or {}).get('start_date') or ''
    # actual-grade = non-round-minute second precision (probe receipts:
    # round minutes are schedule-grade Sportradar slots)
    if (not r.get('official_ts')) and sd and not re.search(r':[0-5]\d:00Z$', sd) is None:
        pass
    if (not r.get('official_ts')) and sd and re.search(r':00Z$', sd) is None:
        ts = ep(sd)
        if ts:
            r['official_ts'] = ts
            r['right_edge'] = max(ts, r.get('sched_honest') or ts)
            r['right_edge_src'] = 'official_actual_milestone'
            promoted += 1
    rows.append(r)
with open('state/corpus_events_v2.jsonl', 'w') as fh:
    for r in rows:
        fh.write(json.dumps(r) + '\n')
print('promoted to official_actual_milestone tier:', promoted)
EOF
python3 analysis/range_spectrum_build.py > /tmp/range_recut.log 2>&1
python3 analysis/range_spectrum_itf.py >> /tmp/range_recut.log 2>&1
echo RECUT-DONE
tail -12 /tmp/RANGE_SPECTRUM_CENSUS.md
