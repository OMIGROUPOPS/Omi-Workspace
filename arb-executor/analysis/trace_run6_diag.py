#!/usr/bin/env python3
"""READ-ONLY RUN-6 diagnostics: (1) status counts, (2) entry_cancelled timing (is match_buffer
premature?), (3) paired_basis_skip values vs the two legs' maker targets (maker-path over-block?)."""
import json, glob, time
from collections import defaultdict, Counter

LOGS = sorted(glob.glob("logs/live_v3_2026060*.jsonl"))
boundary = 0.0
for lf in LOGS:
    for line in open(lf, errors="replace"):
        if '"system_start"' in line:
            try: boundary = max(boundary, json.loads(line).get("ts_epoch", 0))
            except Exception: pass
now = time.time()
print("RUN-6 boundary=%.0f  now=%.0f  (session age %.0f min)\n" % (boundary, now, (now-boundary)/60))

place={}; cancels=[]; pbskips=[]; fatskips=[]; fills_log={}; placed=set()
ev_counts=Counter()
for lf in LOGS:
    for line in open(lf, errors="replace"):
        if '"event"' not in line: continue
        try: r=json.loads(line)
        except Exception: continue
        if r.get("ts_epoch",0) < boundary: continue
        e=r.get("event"); tk=r.get("ticker",""); d=r.get("details",{}); ev=d.get("event","")
        if "26JUN03" not in (tk or ev): continue
        ev_counts[e]+=1
        if e=="v4_place": place[tk]=d; placed.add(tk)
        elif e=="entry_cancelled": cancels.append((tk, d, r.get("ts_epoch",0)))
        elif e=="paired_basis_skip": pbskips.append((tk,d))
        elif e=="skip_fat_spread_taker": fatskips.append((tk,d))
        elif e=="entry_filled": fills_log[tk]=d

print("=== RUN-6 26JUN03 event counts ===")
for k,v in sorted(ev_counts.items(), key=lambda x:-x[1]): print("  %-26s %d" % (k,v))

print("\n=== entry_cancelled timing (DEDUP latest/ticker; min_to_start@cancel: <15=legit buffer, >>15=PREMATURE) ===")
canc_last = {}
for tk,d,ts in cancels: canc_last[tk] = (d,ts)
from collections import Counter as _C
reason_ct = _C(d.get("reason") for d,ts in canc_last.values())
print("  reasons:", dict(reason_ct))
for tk,(d,ts) in sorted(canc_last.items()):
    ms = d.get("match_start",0); mins = (ms - ts)/60 if ms else None
    print("  %-30s reason=%-18s min_to_start@cancel=%s" % (
        tk.rsplit("-",1)[1] if "-" in tk else tk, d.get("reason"),
        ("%.0f"%mins) if mins is not None else "n/a (match_start=%s)"%ms))

print("\n=== paired_basis_skip DEDUP (unique leg): cap combined vs MAKER-TARGET-SUM (over-block check) ===")
pb_last = {}
for tk,d in pbskips: pb_last[tk] = d
overblock = 0
for tk,d in sorted(pb_last.items()):
    ev = d.get("event","")
    this_tgt = place.get(tk,{}).get("target_bid")
    sib_tk = next((t for t in place if t.rsplit("-",1)[0]==ev and t!=tk), None)
    sib_tgt = place.get(sib_tk,{}).get("target_bid") if sib_tk else None
    tgt_sum = (this_tgt+sib_tgt) if (this_tgt is not None and sib_tgt is not None) else None
    ob = (tgt_sum is not None and tgt_sum<=99)
    if ob: overblock += 1
    print("  %-28s this=%s(tgt %s)+sib %s(cost %s)=comb %s>%s | maker-tgt-sum=%s%s" % (
        ev.replace("KX","")[:28], tk.rsplit("-",1)[1], this_tgt, d.get("sibling"), d.get("sibling_cost"),
        d.get("combined"), d.get("cap"), tgt_sum, "  <-- OVER-BLOCK (safe as maker pair)" if ob else ""))
print("  -> unique pbskip legs: %d ; OVER-BLOCK (maker-tgt-sum<=99): %d" % (len(pb_last), overblock))

print("\n=== status counts ===")
print("  legs placed (v4_place):    %d" % len(placed))
print("  entry_filled (log):        %d" % len(fills_log))
print("  paired_basis_skip legs:    %d" % len(pbskips))
print("  fat_spread skip legs:      %d" % len(fatskips))
print("  entry_cancelled legs:      %d" % len(set(c[0] for c in cancels)))
