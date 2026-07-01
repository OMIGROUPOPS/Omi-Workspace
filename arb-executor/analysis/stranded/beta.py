import json, os, csv, math
from datetime import datetime, timezone, timedelta
from collections import defaultdict

BASE="/root/Omi-Workspace/arb-executor"
TICK=BASE+"/analysis/premarket_ticks"
EDT=timezone(timedelta(hours=-4))
def ptape(s):
    try:
        d,t,ap=s.split(" "); Y,Mo,D=d.split("-"); h,mi,se=t.split(":"); h=int(h)
        if ap=="PM" and h!=12: h+=12
        if ap=="AM" and h==12: h=0
        return datetime(int(Y),int(Mo),int(D),h,int(mi),int(se),tzinfo=EDT).timestamp()
    except: return None
def piso(s):
    for f in ("%Y-%m-%dT%H:%M:%SZ","%Y-%m-%dT%H:%MZ"):
        try: return datetime.strptime(s,f).replace(tzinfo=timezone.utc).timestamp()
        except: pass
    return None

# scheduled starts
sched={}
for line in open("/tmp/sched_all.jsonl",errors="replace"):
    try: dd=json.loads(line)["details"]
    except: continue
    ev=dd.get("event"); st=dd.get("start_time")
    if ev and st:
        se=piso(st)
        if se: sched[ev]=se

def taker_fee(a_cents, qty):
    p=a_cents/100.0
    return math.ceil(0.07*qty*p*(1-p)*100)/100.0

def load_tape(tk):
    p=os.path.join(TICK,tk+".csv")
    if not os.path.exists(p): return None
    rows=[]
    for r in csv.DictReader(open(p)):
        e=ptape(r["ts_et"])
        if e is None: continue
        try: a=int(float(r["ask_1"] or 0))
        except: a=0
        try: asz=int(float(r["ask_1_sz"] or 0))
        except: asz=0
        rows.append((e,a,asz))
    rows.sort()
    return rows

def ask_at(rows, t):
    # latest row with ts<=t and ask>0
    lo=None
    for (e,a,asz) in rows:
        if e<=t:
            if a>0: lo=(a,asz)
        else: break
    return lo

d=json.load(open("/tmp/stranded_91.json"))
OFF=[("gun-30s",30),("gun-15s",15),("gun-5s",5),("gun-time",0)]
baseline=sum(r["kept_naked_pnl_usd"] for r in d)

per=defaultdict(lambda: dict(n=0,cross=0,lock100=0,lock97=0,betaNET_all=0.0,
                             base_cov=0.0,beta_cov=0.0,asks=[],combs=[],thin=0))
covered=0
for r in d:
    rows=load_tape(r["missed"])
    ke=r["kept_entry_cents"]; qty=r["kept_qty"] or 5
    naked=r["kept_naked_pnl_usd"]
    if rows is None or ke is None:
        # not evaluable -> beta keeps naked for all offsets
        for lbl,_ in OFF: per[lbl]["betaNET_all"]+=naked
        continue
    covered+=1
    gun = r["gun_cancel_ts"] or sched.get(r["event"]) or rows[-1][0]
    if gun>rows[-1][0]: gun=rows[-1][0]
    for lbl,X in OFF:
        P=per[lbl]; P["n"]+=1; P["base_cov"]+=naked
        hit=ask_at(rows, gun-X)
        if not hit:
            P["betaNET_all"]+=naked; P["beta_cov"]+=naked; continue
        a,asz=hit
        comb=ke+a
        pair_pnl=(100-comb)/100.0*qty - taker_fee(a,qty)
        P["cross"]+=1; P["asks"].append(a); P["combs"].append(comb)
        if comb<=100: P["lock100"]+=1
        if comb<=97:  P["lock97"]+=1
        if asz<qty: P["thin"]+=1
        P["betaNET_all"]+=pair_pnl; P["beta_cov"]+=pair_pnl

print(f"stranded events: {len(d)} | tape-covered: {covered} | baseline (all 91): ${baseline:.2f}")
print(f"good price = combined <=97 (100=par); lock97 is the one that matters\n")
print(f"{'offset':9s} {'compl':>6s} {'lock<=100':>10s} {'lock<=97':>9s} {'askMed':>7s} {'combMed':>8s} {'thin':>5s} {'betaNET_all91':>14s} {'recov_vs_base':>13s} {'covBase->covBeta':>18s}")
for lbl,_ in OFF:
    P=per[lbl]
    import statistics as st
    aM=st.median(P["asks"]) if P["asks"] else 0
    cM=st.median(P["combs"]) if P["combs"] else 0
    l100=f"{P['lock100']}/{P['cross']}"; l97=f"{P['lock97']}/{P['cross']}"
    recov=P["betaNET_all"]-baseline
    print(f"{lbl:9s} {P['cross']:>3d}/{P['n']:<2d} {l100:>10s} {l97:>9s} {aM:>7.0f} {cM:>8.0f} {P['thin']:>5d} "
          f"${P['betaNET_all']:>11.2f} ${recov:>+10.2f}   ${P['base_cov']:>6.2f}->${P['beta_cov']:>7.2f}")
print("\nNotes: betaNET_all91 = cross covered+crossable events, rest keep naked baseline (conservative, coverage-capped).")
print("covBase->covBeta = baseline vs beta on the tape-covered subset only (what beta does WHERE visible).")
print("thin = # cross events where ask_1_sz < kept_qty (partial-fill risk).")
