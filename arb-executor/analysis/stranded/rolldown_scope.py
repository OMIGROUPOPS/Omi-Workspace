#!/usr/bin/env python3
import json
from collections import defaultdict
LOG="/root/Omi-Workspace/arb-executor/logs/live_v3_20260627.jsonl"
def cat(t):
    if t.startswith("KXATPCHALLENGERMATCH"): return "CHALL"
    if t.startswith("KXITFWMATCH"): return "ITF-W"
    if t.startswith("KXITFMATCH"): return "ITF-M"
    return None
def ev(t): return t.rsplit("-",1)[0]

rolldowns=defaultdict(list)   # ticker -> [(ts_epoch, touch, new_target)]
filled=set(); placed=set(); legs_of_event=defaultdict(set); guncancel={}
for line in open(LOG, errors="replace"):
    if '"event"' not in line: continue
    try: e=json.loads(line)
    except: continue
    evt=e.get("event"); t=e.get("ticker",""); D=e.get("details",{}); tse=e.get("ts_epoch")
    if not t: continue
    c=cat(t)
    if evt=="v4_move_repost" and D.get("reference_source")=="join_bid":
        cp=D.get("current_price"); nt=D.get("new_target")
        if cp is not None and nt is not None and nt<cp:
            rolldowns[t].append((tse,cp,nt)); legs_of_event[ev(t)].add(t)
    elif evt=="v4_place": placed.add(t); legs_of_event[ev(t)].add(t)
    elif evt=="order_placed" and D.get("action")=="buy": placed.add(t); legs_of_event[ev(t)].add(t)
    elif evt=="entry_filled": filled.add(t); legs_of_event[ev(t)].add(t)
    elif evt=="match_live_resting_cancel": guncancel[t]=tse

# classify each rolled-down leg
n_roll_legs=defaultdict(int); n_roll_events=defaultdict(int)
stranded=[]  # (ticker, [(ts,touch,nt)], cancel_ts) -- rolled down, never filled, sibling filled (naked)
for tk, rds in rolldowns.items():
    c=cat(tk); n_roll_legs[c]+=1; n_roll_events[c]+=len(rds)
    ekey=ev(tk)
    sibs=[s for s in legs_of_event[ekey] if s!=tk]
    sib_filled=any(s in filled for s in sibs)
    self_filled = tk in filled
    if (not self_filled) and sib_filled:
        stranded.append((tk, rds, guncancel.get(tk)))

print("=== ROLL-DOWN SCOPE (reposts where new_target < touch) ===")
for c in ["CHALL","ITF-M","ITF-W"]:
    print(f"  {c}: {n_roll_legs[c]} distinct legs rolled down, {n_roll_events[c]} roll-down reposts")
print(f"\n=== STRANDED partner-legs (rolled down, never filled, sibling filled = naked pair) ===")
sc=defaultdict(int)
for tk,rds,cx in stranded: sc[cat(tk)]+=1
for c,n in sc.items(): print(f"  {c}: {n}")
print(f"  TOTAL stranded rolled-down partner-legs: {len(stranded)}")
# dump for tape scan
out=[{"ticker":tk,"rolldowns":rds,"cancel_ts":cx} for tk,rds,cx in stranded]
json.dump(out, open("/tmp/stranded_rolldowns.json","w"))
print("\nWROTE /tmp/stranded_rolldowns.json")
print("sample stranded:")
for tk,rds,cx in stranded[:6]:
    print(f"  {tk.rsplit('-',1)[0].split('-',1)[1]:16s} {tk.rsplit('-',1)[1]:4s} rolls={len(rds)} last_touch={rds[-1][1]} last_target={rds[-1][2]}")
