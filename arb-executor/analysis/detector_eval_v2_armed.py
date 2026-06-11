"""[C-ARMED-WINDOW] Detector re-eval under armed-window semantics. READ-ONLY.
Lineage: detector_eval_v1 (f3d5ee7e) ground truth + machinery; entry_minute_ev
engine (R1-gated) for the rest-cancellation cost.

Envelope: detector counts prints only from (arm_ts = start - W min) onward,
W in {60,120,240}; full (W,K,T) surface, K in {5,10,15,20}, T in {30,60,120}.
DISCLOSED: the corpus preserves no feed predictions, so the surface arms at
TRUE_start - W (feed-assumed-correct). The never-armed class (item 4) is therefore
measured on the JUNE cohort, where feed predictions survive in the jsonls
(schedule_match start_time) against June tape onsets, with status-quo disposition
from the committed bucket-A date-mismatch population (91f6e1bc).

Item 3 (rest-cancellation cost): fraction of v3-engine maker_resting FILLS whose
fill moment (start - emin*60) lies AFTER a pre-start false latch -- i.e. rests the
false fire would have cancelled before they filled.
"""
import pyarrow.parquet as pq, pyarrow as pa
import glob, csv, json, collections, math, statistics, hashlib, os
from datetime import datetime, timezone
ROOT="/root/Omi-Workspace/arb-executor"
SPIKE=ROOT+"/data/durable/spike_volatility_map"
TAPE=ROOT+"/data/durable/per_minute_universe/premarket_tape_v1.parquet"
PBV1=ROOT+"/data/durable/per_minute_universe/path_b_per_regime_fill_summary_v1.parquet"
HIST=ROOT+"/data/historical_pull/trades"
TRADES=ROOT+"/analysis/trades"
WS=[60,120,240]; KS=[5,10,15,20]; TS=[30,60,120]
TIER12={"both_sides_trade_density","both_sides_price_discovery"}
BANDS=[(5,14,"r05_14"),(15,24,"r15_24"),(25,34,"r25_34"),(35,44,"r35_44"),(45,54,"r45_54"),
       (55,64,"r55_64"),(65,74,"r65_74"),(75,84,"r75_84"),(85,94,"r85_94")]
def band(c):
    for lo,hi,l in BANDS:
        if lo<=c<=hi: return l
    return "r_oob"

# ---- engine (verbatim lineage) for maker fills ----
leg={}
for f in glob.glob(SPIKE+"/*_spike_perN.parquet"):
    cat=f.split("/")[-1].replace("_spike_perN.parquet","").upper()
    t=pq.read_table(f,columns=["ticker","anchor_price"]).to_pandas()
    for r in t.itertuples():
        if r.anchor_price is None: continue
        ac=int(round(r.anchor_price*100)); leg[r.ticker]=dict(cat=cat,anchor=min(94,max(5,ac)))
lut={}
_pb=pq.read_table(PBV1).to_pandas()
for r in _pb.loc[_pb.groupby(["category","anchor_regime"]).expected_improvement_cents.idxmax()].itertuples():
    lut[(r.category,r.anchor_regime)]=(int(r.placement_minute),int(r.bid_offset_cents))

cols=["ticker","time_to_match_start_min","yes_ask_close","price_close","minute_has_trade",
      "match_start_method","match_start_ts","category"]
def f100(x): return None if x is None else x*100.0
series=collections.defaultdict(list); start={}; meth={}; cat_of={}
sc=pq.ParquetFile(TAPE)
for i in range(sc.metadata.num_row_groups):
    rg=sc.read_row_group(i,columns=cols)
    tk=rg.column("ticker").to_pylist(); tt=rg.column("time_to_match_start_min").to_pylist()
    ak=rg.column("yes_ask_close").to_pylist(); pcl=rg.column("price_close").to_pylist()
    mh=rg.column("minute_has_trade").to_pylist(); ms=rg.column("match_start_method").to_pylist()
    mst=rg.column("match_start_ts").to_pylist(); cc=rg.column("category").to_pylist()
    for j in range(len(tk)):
        t=tk[j]
        if t not in leg or ms[j]=="unknown": continue
        a=tt[j]
        if a is None or not (0.0<a<=240.0): continue
        series[t].append((a,f100(ak[j]),f100(pcl[j])))
        if t not in start and mst[j] is not None:
            try:
                start[t]=mst[j].timestamp() if hasattr(mst[j],"timestamp") else float(mst[j])
                meth[t]=ms[j]; cat_of[t]=(cc[j] or "?").upper()
            except Exception: pass
INF=1e18
maker_fill={}   # ticker -> fill ttm (maker_resting only)
for tk,rows in series.items():
    rows.sort(key=lambda r:-r[0])
    L=leg[tk]; anchor=L["anchor"]; cat=L["cat"]
    reg=band(anchor); pl,off=lut.get((cat,reg),(20,1)); bid=max(anchor-off,1)
    a_at=None
    for (a,ak,pc_) in rows:
        if a==pl and ak is not None: a_at=ak; break
    if a_at is not None and a_at<=bid: continue   # marketable taker, not a rest
    for (a,ak,pc_) in rows:
        if 20<=a<=pl:
            trig=min(ak if ak is not None else INF, pc_ if pc_ is not None else INF)
            if trig<=bid: maker_fill[tk]=a; break
del series
print("maker_resting fills:", len(maker_fill))

# ---- tier-1/2 events ----
events={}
for t,s in start.items():
    if meth.get(t) not in TIER12: continue
    et=t.rsplit("-",1)[0]
    cur=events.get(et)
    if cur is None or s<cur[0]: events[et]=(s,cat_of.get(t,"?"))
print("tier12 events:", len(events))

def multi_latch(prints, arm):
    """prints sorted; counting only prints >= arm; -> {(K,T): first latch ts}"""
    pts=[p for p in prints if p>=arm]
    out={}
    for T in TS:
        j=0; first={K:None for K in KS}; need=set(KS)
        for i,ts in enumerate(pts):
            while pts[j]<ts-T: j+=1
            n=i-j+1
            for K in list(need):
                if n>=K: first[K]=ts; need.discard(K)
            if not need: break
        for K in KS: out[(K,T)]=first[K]
    return out

agg=collections.defaultdict(lambda:collections.Counter())
lat=collections.defaultdict(list)
rest_lost=collections.defaultdict(lambda:[0,0])  # (W,K,T)->[lost, total maker fills]
n_cov=0
for et,(st,cat) in sorted(events.items()):
    files=list(glob.glob(os.path.join(HIST,et+"-*")))
    prints=[]
    for p in files:
        try:
            for row in csv.DictReader(open(p)):
                try: prints.append(datetime.fromisoformat(row["created_time"].replace("Z","+00:00")).timestamp())
                except Exception: continue
        except Exception: continue
    if not prints: continue
    n_cov+=1
    prints.sort()
    legs_mf=[(t,m) for (t,m) in maker_fill.items() if t.rsplit("-",1)[0]==et]
    for W in WS:
        arm=st-W*60
        lt=multi_latch(prints,arm)
        for (K,T),l in lt.items():
            key=(W,K,T)
            if l is None: v="never"
            else:
                d=l-st
                if d< -1800: v="ff_ge30m"
                elif d< -60: v="ff_1_30m"
                elif d<=0: v="early_le60s"
                else: v="post"; lat[key].append(d)
            agg[key][v]+=1
            # item 3: rest-cancellation
            for (t,emin) in legs_mf:
                fill_ts=st-emin*60.0
                rest_lost[key][1]+=1
                if l is not None and l<fill_ts and l<st:
                    rest_lost[key][0]+=1
print("events covered:", n_cov)

# ---- item 4: June feed-error / never-armed (feed predictions survive in jsonls) ----
feed={}
for lf in sorted(glob.glob(ROOT+"/logs/live_v3_2026*.jsonl")):
    for l in open(lf,errors="replace"):
        if '"schedule_match"' not in l: continue
        try: e=json.loads(l)
        except Exception: continue
        if e.get("event")!="schedule_match": continue
        d=e["details"]; ev=d.get("event")
        if ev and ev not in feed and d.get("start_time") not in (None,"?",""):
            try:
                feed[ev]=datetime.fromisoformat(d["start_time"].replace("Z","+00:00")).timestamp()
            except Exception: pass
import gzip
def june_onset(et):
    prints=[]
    from zoneinfo import ZoneInfo
    ET=ZoneInfo("America/New_York")
    for p in glob.glob(os.path.join(TRADES,et+"-*")):
        opener=gzip.open(p,"rt") if p.endswith(".gz") else open(p)
        try:
            for row in csv.DictReader(opener):
                try: prints.append(datetime.strptime(row["ts_et"],"%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp())
                except Exception: continue
        finally: opener.close()
    prints.sort()
    j=0
    for i,ts in enumerate(prints):
        while prints[j]<ts-60: j+=1
        if i-j+1>=10: return ts
    return None
mismatch=set()
ba=json.load(open("/tmp/bucket_a_rows.json")) if os.path.exists("/tmp/bucket_a_rows.json") else []
for r in ba: mismatch.add(r["event"])
na=collections.defaultdict(lambda:[0,0,0])  # W -> [never_armed, of which status-quo-skipped, n]
err=[]
for ev,fs in feed.items():
    on=june_onset(ev)
    if on is None: continue
    err.append(fs-on)
    for W in WS:
        na[W][2]+=1
        if on < fs-W*60:
            na[W][0]+=1
            if ev in mismatch: na[W][1]+=1
err.sort()

# ---- emit ----
rows_out=[]
for (W,K,T),c in sorted(agg.items()):
    tot=sum(c.values()); ds=sorted(lat[(W,K,T)])
    def q(p): return ds[min(len(ds)-1,int(len(ds)*p))] if ds else None
    lost,totr=rest_lost[(W,K,T)]
    rows_out.append(dict(W=W,K=K,T=T,n_events=tot,
        post_pct=round(100*c["post"]/tot,2), early60_pct=round(100*c["early_le60s"]/tot,2),
        ff_1_30m_pct=round(100*c["ff_1_30m"]/tot,2), ff_ge30m_pct=round(100*c["ff_ge30m"]/tot,2),
        never_pct=round(100*c["never"]/tot,2),
        lat_p50=q(.5), lat_p90=q(.9), lat_p99=q(.99),
        rest_fills=totr, rest_lost=lost,
        rest_lost_pct=round(100*lost/totr,2) if totr else None))
tbl=pa.Table.from_pylist(rows_out)
OUTP="/tmp/detector_eval_v2_armed.parquet"
pq.write_table(tbl,OUTP)
sha=hashlib.sha256(open(OUTP,"rb").read()).hexdigest()

S=[];A=S.append
A("[C-ARMED-WINDOW] detector under armed-window semantics (arm = true_start - W; feed-assumed-correct, disclosed)")
A("cohort: %d tier-1/2 events; maker_resting fills tracked: %d legs"%(n_cov,len(maker_fill)))
A("")
A("W/K/T surface -- post-start%% / early<=60s / ff1-30m / ff>=30m / never ; lat p50/p90 ; rest-fills lost%%")
for W in WS:
    for K in KS:
        for T in TS:
            r=[x for x in rows_out if x["W"]==W and x["K"]==K and x["T"]==T][0]
            mark=" <== deployed K/T" if (K,T)==(10,60) else ""
            A("W=%3d K=%2d T=%3d | %5.1f / %4.1f / %4.1f / %4.1f / %4.1f | p50=%-4s p90=%-5s | lost %5.2f%%%s"%(
                W,K,T,r["post_pct"],r["early60_pct"],r["ff_1_30m_pct"],r["ff_ge30m_pct"],r["never_pct"],
                r["lat_p50"],r["lat_p90"],r["rest_lost_pct"],mark))
A("")
A("ITEM 4 -- never-armed (JUNE cohort: feed predictions from jsonl schedule_match vs June tape onsets):")
A("  feed-error distribution (feed_start - onset, sec): n=%d p10=%+.0f p50=%+.0f p90=%+.0f"%(
    len(err),err[int(len(err)*.1)] if err else 0,err[len(err)//2] if err else 0,
    err[int(len(err)*.9)] if err else 0))
for W in WS:
    nv,sk,n=na[W]
    A("  W=%3d: never-armed %d/%d (%.1f%%) ; of those, status-quo date-gate already skipped %d (delta-vs-status-quo = %d events)"%(
        W,nv,n,100*nv/max(n,1),sk,nv-sk))
A("")
A("parquet %s"%OUTP)
A("sha256 %s"%sha)
open("/tmp/detector_eval_v2_summary.txt","w").write("\n".join(S)+"\n")
print("\n".join(S))
