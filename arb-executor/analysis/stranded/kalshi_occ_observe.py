#!/usr/bin/env python3
# C-KALSHI-OCC OBSERVE (read-only). Measures what the gated occ-fallback WOULD resolve, WITHOUT arming the
# live flag (its only arm is a live-entry arm; bot holds live positions -> not flipped this session).
# (a) schedule_gap events that become occ-resolvable, by category; (b) loop-lag + removable skip load;
# (c) byte-identical proof (code gate); + CENSUS: book-bearing hard-skipped events, by tier, achievable combined.
import os, csv, gzip, json, statistics as st
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
BASE="/root/Omi-Workspace/arb-executor"; TICK=BASE+"/analysis/premarket_ticks"; LOGDIR=BASE+"/logs"
EDT=timezone(timedelta(hours=-4)); UTC=timezone.utc
def ep(y,mo,d,h,mi): return datetime(y,mo,d,h,mi,tzinfo=EDT).timestamp()
START=ep(2026,6,30,15,46)
LOGS=[LOGDIR+"/live_v3_20260630.jsonl",LOGDIR+"/live_v3_20260701.jsonl"]
BOOK_KB=200.0
def opent(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
def cat(t):
    for p,c in (("KXATPCHALLENGERMATCH","ATP_CHALL"),("KXWTACHALLENGERMATCH","WTA_CHALL"),("KXATPMATCH","ATP_MAIN"),("KXWTAMATCH","WTA_MAIN"),("KXITFWMATCH","ITF_W"),("KXITFMATCH","ITF_M")):
        if t.startswith(p): return c
    return "?"
def leg(t): return t.rsplit("-",1)[1] if "-" in t else t
def ptape(s):
    try:
        d,t,ap=s.split(" "); Y,Mo,D=d.split("-"); h,mi,se=t.split(":"); h=int(h)
        if ap=="PM" and h!=12: h+=12
        if ap=="AM" and h==12: h=0
        return datetime(int(Y),int(Mo),int(D),h,int(mi),int(se),tzinfo=EDT).timestamp()
    except: return None

# ---------- ingest ----------
SGAP=Counter()             # schedule_gap event -> skip count (keyed by details.event)
RESOLVED=set()             # events that DID resolve via a real source (schedule_match)
COARSE=set()               # events resolved via kalshi_occurrence_coarse (flag was ON historically? default OFF => empty)
LAGS=[]                    # lag_sec samples
posted_events=set()        # events where we actually posted/filled (real positions)
for f in LOGS:
    if not os.path.exists(f): continue
    for line in open(f,errors="replace"):
        if '"event"' not in line: continue
        try: e=json.loads(line)
        except: continue
        ev=e.get("event"); D=e.get("details",{}) or {}; ts=e.get("ts_epoch")
        if ev=="schedule_match":
            evk=D.get("event")
            if evk:
                if D.get("method")=="kalshi_occurrence_coarse" or D.get("coarse_source"): COARSE.add(evk)
                else: RESOLVED.add(evk)
            continue
        if ev=="loop_lag" and isinstance(D.get("lag_sec"),(int,float)): LAGS.append(D["lag_sec"]); continue
        if ts is None or ts<START: continue
        if ev=="skipped" and D.get("reason")=="schedule_gap" and D.get("event"): SGAP[D["event"]]+=1
        tk=e.get("ticker","")
        if tk and ev in ("v4_place","order_placed","entry_filled","completion_fill"):
            posted_events.add(tk.rsplit("-",1)[0])

# ---------- tape dir index (event-prefix -> [leg files], max kb) ----------
evfiles=defaultdict(list); evkb=defaultdict(float)
for fn in os.listdir(TICK):
    base=fn.replace(".csv.gz","").replace(".csv","")
    if "-" not in base: continue
    ekp=base.rsplit("-",1)[0]; evfiles[ekp].append(fn)
    try: kb=os.path.getsize(TICK+"/"+fn)/1024.0
    except: kb=0.0
    if kb>evkb[ekp]: evkb[ekp]=kb

def best_fillable(path):
    # single pass: lowest last_trade printed with bid_1_sz>=5
    try: op=opent(path); rdr=csv.reader(op); hdr=next(rdr,None)
    except: return None
    if not hdr: return None
    ix={h:i for i,h in enumerate(hdr)}
    ci_lt=ix.get("last_trade",-1); ci_bs=ix.get("bid_1_sz",-1)
    bf=None
    for r in rdr:
        try:
            lt=int(float(r[ci_lt] or 0)) if ci_lt>=0 else 0
            bs=int(float(r[ci_bs] or 0)) if ci_bs>=0 else 0
        except: continue
        if lt>0 and bs>=5 and (bf is None or lt<bf): bf=lt
    return bf

# ---------- (a) resolvability ----------
gap_events=[ek for ek in SGAP if ek not in posted_events]         # schedule_gap, never became a real position
book_gap=[ek for ek in gap_events if evkb.get(ek,0.0)>=BOOK_KB]   # book-bearing (occ-resolvable proxy: Kalshi listed w/ tape)
by_cat=Counter(cat(ek+"-X") for ek in book_gap)
thin_gap=[ek for ek in gap_events if evkb.get(ek,0.0)<BOOK_KB]

print("="*72)
print(f"C-KALSHI-OCC OBSERVE (read-only; live flag NOT armed) — box Jun30 15:46 -> now")
print("="*72)
print(f"\n(a) RESOLVABILITY — schedule_gap events that the occ-fallback would resolve")
print(f"  schedule_gap events (never posted): {len(gap_events)}")
print(f"  -> BOOK-BEARING (Kalshi listed + real tape => occ-resolvable): {len(book_gap)}")
print(f"     by category: {dict(by_cat)}")
print(f"  -> thin/phantom (no real book; excused): {len(thin_gap)}")
print(f"  historically occ-resolved live (flag was on?): {len(COARSE)} (expect 0 — default-OFF all box)")

# ---------- (b) loop-lag + removable load ----------
removable_skips=sum(SGAP[ek] for ek in book_gap)
tot_gap_skips=sum(SGAP.values())
print(f"\n(b) LOOP-LAG + removable schedule_gap load")
if LAGS:
    ls=sorted(LAGS)
    print(f"  loop_lag samples: {len(ls)} | mean {sum(ls)/len(ls):.2f}s | p50 {ls[len(ls)//2]:.2f}s | p95 {ls[int(len(ls)*.95)]:.2f}s | max {ls[-1]:.2f}s")
    print(f"  lags >5s: {sum(1 for x in ls if x>5)} | >2s: {sum(1 for x in ls if x>2)}")
print(f"  total schedule_gap skip-events logged: {tot_gap_skips}")
print(f"  skips attributable to the {len(book_gap)} occ-resolvable events (removed once resolved): {removable_skips} ({100*removable_skips/tot_gap_skips if tot_gap_skips else 0:.0f}% of gap-spam)")
print(f"  -> BEFORE: {len(gap_events)} unmatched events re-evaluated every ~1s loop, {tot_gap_skips} skip-logs.")
print(f"     AFTER (est): {len(book_gap)} resolve off the coarse clock -> their re-eval + {removable_skips} skip-logs drop out;")
print(f"     the loop stops re-scanning them each cycle -> lag tail shrinks. (Exact after-lag needs the armed observe run, deferred.)")

# ---------- (c) byte-identical proof ----------
print(f"\n(c) BYTE-IDENTICAL on already-resolved events — code-gate proof")
print(f"  {len(RESOLVED)} events resolved via a real source (ESPN/TE / odds_api_commence_time) this box.")
print( "  live_v4.py: the occ-fallback is 'Fallback 2' INSIDE the `else` reached ONLY when the primary")
print( "  sources miss; resolved events take the odds_api_commence_time `schedule_match` branch ABOVE it")
print( "  and never enter the else. Within the else: kts = _kalshi_occ_start(...) if <flag> else None —")
print( "  the flag is consulted ONLY on a primary-miss. => for every resolved event the flag on/off path")
print( "  is byte-identical (branch never taken). Overlap of RESOLVED with book_gap (should be 0): "
       f"{len(RESOLVED & set(book_gap))}")

# ---------- CENSUS: book-bearing hard-skipped, by tier, achievable combined ----------
print(f"\nCENSUS — book-bearing schedule_gap-skipped events (what their tapes offered)")
rows=[]
for ek in book_gap:
    files=sorted(evfiles.get(ek,[]))
    if len(files)<2:
        rows.append((ek,cat(ek+"-X"),None,None,None,"single-leg tape")); continue
    bfs=[]
    for fn in files[:2]:
        bfs.append(best_fillable(TICK+"/"+fn))
    if all(b is not None for b in bfs):
        ach=sum(bfs); rows.append((ek,cat(ek+"-X"),bfs[0],bfs[1],ach,("<=97" if ach<=97 else ("<100" if ach<100 else ">=100"))))
    else:
        rows.append((ek,cat(ek+"-X"),bfs[0],bfs[1],None,"thin/one-sided book"))
# tier rollup
print(f"  {'tier':10s} {'n':>3s} {'w/combined':>10s} {'<=97':>5s} {'<100':>5s} {'med_ach':>8s}")
for tier in ("ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL","ITF_M","ITF_W"):
    tr=[r for r in rows if r[1]==tier]
    if not tr: continue
    achs=[r[4] for r in tr if r[4] is not None]
    le97=sum(1 for a in achs if a<=97); le100=sum(1 for a in achs if a<100)
    med=int(st.median(achs)) if achs else 0
    print(f"  {tier:10s} {len(tr):>3d} {len(achs):>10d} {le97:>5d} {le100:>5d} {med:>8d}")
allach=[r[4] for r in rows if r[4] is not None]
print(f"  TOTAL book-bearing {len(rows)} | with combined {len(allach)} | <=97 {sum(1 for a in allach if a<=97)} | <100 {sum(1 for a in allach if a<100)} | median achievable {int(st.median(allach)) if allach else 0}")
# top missed (lowest achievable combined = best forfeited locks)
print(f"\n  Top-20 forfeited (lowest achievable combined we never touched):")
for ek,c,b1,b2,ach,tag in sorted([r for r in rows if r[4] is not None],key=lambda x:x[4])[:20]:
    print(f"   {ek.split('-',1)[1] if '-' in ek else ek:24s} {c:9s} legs {b1}+{b2}={ach} {tag}")

json.dump({"a_resolvable_by_cat":dict(by_cat),"a_book_gap":len(book_gap),"a_thin":len(thin_gap),
           "b_total_gap_skips":tot_gap_skips,"b_removable":removable_skips,"b_lag_mean":(sum(LAGS)/len(LAGS) if LAGS else 0),
           "c_resolved":len(RESOLVED),"census":[dict(event=r[0],tier=r[1],leg1=r[2],leg2=r[3],achievable=r[4],tag=r[5]) for r in rows]},
          open("/root/shadow_p4/OMQS_KALSHI_OCC_OBSERVE.json","w"), default=str)
print("\nwrote /root/shadow_p4/OMQS_KALSHI_OCC_OBSERVE.json")
