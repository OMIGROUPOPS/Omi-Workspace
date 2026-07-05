# NIGHTLY PASS — the week's standing analysis (run every morning, push everything)

From `/root/Omi-Workspace/arb-executor` on the VPS. Log = the current session's
`logs/live_v3_YYYYMMDD.jsonl` (+ previous night's file for the full window).

```bash
# 1. Standing ledger pass: chains + exchange truth (edit EVENTS list to the night's slate,
#    or extend causal_audit.py to auto-discover from entry_filled/window_open events)
python3 ../.claude/live_20260705/audit/causal_audit.py          # -> /tmp/causal_audit.json

# 2. Grades + stamps: the monitor's live_validation.jsonl already carries per-fill
#    stamp/chain/Δaim rows (EARNED/GIFT_CLASS/MIXED); A-F letter grades via
#    ../.claude/overnight_20260705/on3_ledger.py + grade2.py when a full window closes.

# 3. THE LEAK DECOMPOSITION (appends to week_leak.jsonl, deduped by date+event)
python3 ../.claude/live_20260705/audit/leak_decomposition.py \
    logs/live_v3_<prev>.jsonl logs/live_v3_<today>.jsonl

# 4. Evidence-stream counters
grep -c 'bid_grade' ../.claude/live_20260705/live_validation.jsonl   # repriceable stream
python3 - <<'EOF'
# fv_observe riser accumulation vs the ~100 target
import json,glob
n=0
for lp in sorted(glob.glob('logs/live_v3_*.jsonl'))[-7:]:
    for l in open(lp,encoding='utf-8',errors='replace'):
        if 'fv_burst_anchor' in l and '"event"' in l:
            o=json.loads(l)
            if (o['details'].get('entry_price') or 0)>=50 and o['details'].get('fv_mid') is not None: n+=1
print('fv-graded riser legs to date:',n,'/ ~100 target')
EOF

# 5. Commit + push (the monitor auto-commits .claude/live_20260705/; for the rest:)
cd /root/Omi-Workspace && git add .claude/live_20260705/ && git commit -m "nightly pass <date>" && git push origin blend/kalshi-occ-fallback
```

Pass bars each night: zero-tolerance board clean (or same-day patch through the gate —
defects are exempt from the config hold); leak table updated; counters reported.
