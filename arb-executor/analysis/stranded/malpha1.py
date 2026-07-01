import json, os, csv, glob, math, statistics as stx
from datetime import datetime, timezone, timedelta
from collections import defaultdict

BASE="/root/Omi-Workspace/arb-executor"
TICK=BASE+"/analysis/premarket_ticks"; TR=BASE+"/analysis/trades"; LOGDIR=BASE+"/logs"
EDT=timezone(timedelta(hours=-4))
def ptape(s):
    try:
        d,t,ap=s.split(" "); Y,Mo,D=d.split("-"); h,mi,se=t.split(":"); h=int(h)
        if ap=="PM" and h!=12: h+=12
        if ap=="AM" and h==12: h=0
        return datetime(int(Y),int(Mo),int(D),h,int(mi),int(se),tzinfo=EDT).timestamp()
    except: return None
def opent(p):
    import gzip
    return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
def find(dir_,tk):
    for e in (".csv",".csv.gz"):
        if os.path.exists(dir_+"/"+tk+e): return dir_+"/"+tk+e
    return None
def taker_fee(a,q):
    p=a/100.0; return math.ceil(0.07*q*p*(1-p)*100)/100.0

d=json.load(open("/tmp/stranded_91.json"))
evs=[r for r in d if find(TR,r["missed"]) and find(TICK,r["missed"])]
missed_tk={r["missed"] for r in evs}

# our bid timeline (from logs) for error-class + ref level
placed=defaultdict(list); cancelled={}; legcancel=defaultdict(list); target=defaultdict(list)
for f in sorted(glob.glob(LOGDIR+"/live_v3_2026062*.jsonl")+glob.glob(LOGDIR+"/live_v3_20260630.jsonl")):
    for line in open(f,errors="replace"):
        if '"event"' not in line: continue
        try: e=json.loads(line)
        except: continue
        tk=e.get("ticker",""); ev=e.get("event"); D=e.get("details",{}) or {}; ts=e.get("ts_epoch")
        if tk not in missed_tk: continue
        if ev=="order_placed" and D.get("action")=="buy" and D.get("side")=="yes":
            placed[tk].append((ts,D.get("order_id"),D.get("price")))
        elif ev=="v4_place" and D.get("target_bid") is not None: target[tk].append(D["target_bid"])
        elif ev=="order_cancelled" and D.get("order_id"): cancelled[D["order_id"]]=ts
        elif ev in ("match_live_resting_cancel","v4_resting_cancel","orphan_buy_cancelled"): legcancel[tk].append(ts)
def intervals(tk):
    iv=[]; lc=sorted(legcancel[tk])
    for (ts,oid,pr) in placed[tk]:
        if ts is None or pr is None: continue
        end=cancelled.get(oid) or (next((c for c in lc if c>=ts),None)) or ts+7200
        iv.append((ts,end,pr))
    return iv
def active(iv,t): return max([p for (s,e,p) in iv if s<=t<=e],default=None)
def pulled(iv,t,p): return any(e<=t and pr>=p for (s,e,pr) in iv)

def loadticks(tk):
    rows=[]
    for r in csv.DictReader(opent(find(TICK,tk))):
        e=ptape(r["ts_et"]);
        if e is None: continue
        def gi(k):
            try: return int(float(r.get(k) or 0))
            except: return 0
        rows.append((e,gi("bid_1"),gi("last_trade"),r.get("mid")))
    rows.sort(); return rows
def loadtr(tk):
    rows=[]
    for r in csv.reader(opent(find(TR,tk))):
        if not r or r[0]=="ts_et": continue
        e=ptape(r[0])
        if e is None: continue
        try: p=int(float(r[2])); c=int(float(r[3]))
        except: continue
        rows.append((e,p,c,r[4] if len(r)>4 else ""))
    rows.sort(); return rows

def dedup_opps(prints, ref, gun):
    # taker_side=no, p<=ref, premarket -> group consecutive same-ish level (<=2c rise) & gap<120s
    fil=[(t,p,c) for (t,p,c,s) in prints if s=="no" and p<=ref and (gun is None or t<gun)]
    opps=[]; cur=None
    for (t,p,c) in fil:
        if cur and p<=cur["lvl"]+2 and t-cur["t_last"]<120:
            cur["lots"]+=c; cur["t_last"]=t; cur["pmin"]=min(cur["pmin"],p)
        else:
            if cur: opps.append(cur)
            cur=dict(t=t,t_last=t,lvl=p,pmin=p,lots=c)
        cur["lvl"]=max(cur["lvl"],p)
    if cur: opps.append(cur)
    return opps

def price_after(ticks, tau):
    return [lt for (e,b,lt,m) in ticks if e>tau and lt>0]

QTY=5
rows=[]
for r in evs:
    tk=r["missed"]; iv=intervals(tk); ticks=loadticks(tk); trades=loadtr(tk)
    gun=r["gun_cancel_ts"] or (ticks[-1][0] if ticks else None)
    ref=max([p for (_,_,p) in iv]+target[tk]+[0])
    opps=dedup_opps(trades,ref,gun)
    # accumulate up to QTY lots across opportunities (time order)
    need=QTY; fills=[]  # (price, lots, tau)
    for o in opps:
        if need<=0: break
        take=min(o["lots"],need); need-=take
        fills.append((o["pmin"],take,o["t"]))
    filled_lots=sum(l for (_,l,_) in fills)
    ke=r["kept_entry_cents"]
    # error class of first opportunity
    if fills:
        tau0=fills[0][2]; p0=fills[0][0]; q=active(iv,tau0)
        if q is None: ecls="PULLED" if pulled(iv,tau0,p0) else "NEVER_LAID"
        elif q>=p0: ecls="BEHIND_WALL"
        else: ecls="TOO_DEEP"
    else: ecls="NO_OPP"
    # peak class per fill: PRE if price later exceeded fill price; else POST(collapse)
    pre_lots=post_lots=0; wsum=0.0
    for (p,l,tau) in fills:
        aft=price_after(ticks,tau)
        pre = (max(aft) > p) if aft else False
        if pre: pre_lots+=l
        else: post_lots+=l
        wsum+=p*l
    fillpx = (wsum/filled_lots) if filled_lots else None
    rows.append(dict(event=r["event"],cat=r["cat"],mode=r["mode"],missed=tk,kept_entry=ke,
        kept_naked=r["kept_naked_pnl_usd"],ecls=ecls,n_opps=len(opps),filled_lots=filled_lots,
        fill_px=fillpx,pre_lots=pre_lots,post_lots=post_lots,ref=ref,
        combined=(ke+fillpx) if (ke is not None and fillpx is not None) else None))

def pair_net(row, contamination_filter):
    # complete pair: pay fill on missed leg, hold both -> pays 100 (winner-independent)
    if row["fill_px"] is None or row["kept_entry"] is None: return row["kept_naked"]
    lots = row["pre_lots"] if contamination_filter else row["filled_lots"]
    if lots<=0: return row["kept_naked"]
    # weighted fill for the lots used (approx use fill_px)
    px=row["fill_px"]; comb=row["kept_entry"]+px
    return (100-comb)/100.0*lots - taker_fee(px,lots)

baseline=sum(r["kept_naked_pnl_usd"] for r in d)   # -43.97 over all 91
print(f"M-alpha1 PAIR-ECONOMICS REPLAY | covered legs w/ trades+L1: {len(evs)} | baseline(all 91) ${baseline:.2f}")
print(f"good price = combined <=97 (100=par)\n")

for filt in (False, True):
    tag = "WITH contamination filter (PRE-PEAK only)" if filt else "WITHOUT filter (all fills)"
    net_all=0.0; le97=le100=gt100=0; ncomp=0
    by=defaultdict(lambda:[0,0.0])  # ecls -> [n, recovery]
    for row in rows:
        pn=pair_net(row,filt); net_all+=pn
        comb=row["combined"]
        if comb is not None and (not filt or row["pre_lots"]>0):
            ncomp+=1
            if comb<=97: le97+=1
            elif comb<=100: le100+=1
            else: gt100+=1
        by[row["ecls"]][0]+=1; by[row["ecls"]][1]+=(pn-row["kept_naked"])
    # events not covered keep naked -> add their naked to net_all
    covered_events={r["event"] for r in rows}
    net_full = net_all + sum(r["kept_naked_pnl_usd"] for r in d if r["event"] not in covered_events)
    print(f"--- {tag} ---")
    print(f"  completions: {ncomp}  buckets: <=97:{le97}  98-100:{le100}  >100:{gt100}")
    print(f"  NET over all 91 (covered replayed, rest naked): ${net_full:.2f}   recovery vs baseline: ${net_full-baseline:+.2f}")
    for cl in ("PULLED","NEVER_LAID","BEHIND_WALL","TOO_DEEP","NO_OPP"):
        if by[cl][0]: print(f"    {cl:11s} n={by[cl][0]:2d}  recovery ${by[cl][1]:+.2f}")
    print()

print("=== SIEBON + DALTRA FORENSIC WALK ===")
for key in ("SIEBON","DALTRA"):
    row=next((x for x in rows if key in x["missed"]),None)
    if not row: print(f"  {key}: not in covered set"); continue
    tk=row["missed"]; ticks=loadticks(tk); trades=loadtr(tk)
    r0=next(x for x in d if x["missed"]==tk)
    lt=[l for (e,b,l,m) in ticks if l>0]
    nno=sum(1 for (e,p,c,s) in trades if s=="no"); nyes=sum(1 for (e,p,c,s) in trades if s=="yes")
    opps=dedup_opps(trades,row["ref"],r0["gun_cancel_ts"] or (ticks[-1][0] if ticks else None))
    print(f"\n  {tk}  ({r0['cat']}, mode={r0['mode']}, kept_settle={r0['kept_settle']}, missed_settle={r0['missed_settle']}, winner={r0['winner']})")
    print(f"    raw prints: total={len(trades)} taker_no={nno} taker_yes={nyes} | our ref bid={row['ref']} kept_entry={row['kept_entry']}")
    if lt: print(f"    last_trade trajectory: first={lt[0]} min={min(lt)} max={max(lt)} last={lt[-1]}  ticks={len(ticks)}")
    print(f"    DEDUPPED opportunities: {len(opps)}  (raw taker_no prints collapse to this many fill windows)")
    for o in opps[:8]:
        dt=datetime.fromtimestamp(o['t'],EDT).strftime('%m-%d %H:%M:%S')
        print(f"      opp @ {dt} ET  level~{o['pmin']}c  lots={o['lots']}  dur={o['t_last']-o['t']:.0f}s")
    print(f"    -> first-opp fill {row['fill_px']}c, {row['filled_lots']} lots, class={row['ecls']}, combined={row['combined']}c, pre/post lots {row['pre_lots']}/{row['post_lots']}")
