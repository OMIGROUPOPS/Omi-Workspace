"""Tick spot-check for the entry-completion derivation (pre-registered selection rule:
2 highest touch-rate cells, 2 at eligibility margin, 1 thin cell at the N floor; chosen
MECHANICALLY from the output parquet, no hand-picking). Compares minute-bar down-touch
(price_low<=open-k) vs TICK down-touch (any g9 trade yes_price<=open-k) over the same
pre-onset premarket window; reports which way bar-aggregation cuts (B25). Read-only."""
import pyarrow.parquet as pq, pyarrow as pa
import glob, collections, datetime
ROOT="/root/Omi-Workspace/arb-executor"
PMF=ROOT+"/data/durable/per_minute_universe/per_minute_features.parquet"
OUTP=ROOT+"/data/durable/entry_completion/entry_completion_part1_v1.parquet"
G9=ROOT+"/data/durable/g9_trades.parquet"
SPIKE=ROOT+"/data/durable/spike_volatility_map"
LIVE_BURST=10; LIVE_NEAR_START=60; KTEST=1   # test the shallow k=1 fill

# ---- mechanical cell selection from the parquet ----
t=pq.read_table(OUTP)
rows=t.to_pylist()
# collapse to per-cell (use k=KTEST,j=1 representative row)
percell={}
for r in rows:
    if r["k"]==KTEST and r["j"]==1:
        percell[(r["category"],r["cell"])]=r
cells=list(percell.values())
elig=[r for r in cells if r["wave"] in("WAVE1","WAVE2") and r["n_down_touch"]>=25]
hi=sorted([r for r in cells if r["n_down_touch"]>=25],key=lambda r:-r["down_reach"])[:2]
margin=sorted(elig,key=lambda r:abs(r["ev_dom_0p4x"]))[:2]
thin=sorted([r for r in cells if r["n_down_touch"]>=25],key=lambda r:abs(r["n_down_touch"]-25))[:1]
sel=[]
for tag,rs in [("highest_touch",hi),("eligibility_margin",margin),("thin_Nfloor",thin)]:
    for r in rs: sel.append((tag,r["category"],r["cell"]))
print("SELECTED CELLS (mechanical):")
for tag,cat,c in sel: print("  %-18s %-10s cell=%d"%(tag,cat,c))
sel_keys=set((cat,c) for _,cat,c in sel)

# ---- cohort + cat ----
cat_of={}
for f in glob.glob(SPIKE+"/*_spike_perN.parquet"):
    cat=f.split("/")[-1].replace("_spike_perN.parquet","")
    for tk in pq.read_table(f,columns=["ticker"]).column("ticker").to_pylist(): cat_of[tk]=cat
cohort=set(cat_of)

# ---- rebuild per-leg open_c/onset/cell/match_start from PMF (cohort only) ----
cols=["ticker","time_to_match_start_min","minute_has_trade","price_close","price_low",
      "trade_count_in_minute","match_start_ts","match_start_method"]
series=collections.defaultdict(list); mstart={}
pf=pq.ParquetFile(PMF)
def c100(x): return int(round(x*100)) if x is not None else None
for i in range(pf.metadata.num_row_groups):
    rg=pf.read_row_group(i,columns=cols)
    tk=rg.column("ticker").to_pylist(); tt=rg.column("time_to_match_start_min").to_pylist()
    mh=rg.column("minute_has_trade").to_pylist(); pc=rg.column("price_close").to_pylist()
    pl=rg.column("price_low").to_pylist(); tcn=rg.column("trade_count_in_minute").to_pylist()
    mst=rg.column("match_start_ts").to_pylist(); ms=rg.column("match_start_method").to_pylist()
    for j in range(len(tk)):
        t=tk[j]
        if t not in cohort or ms[j]=="unknown": continue
        a=tt[j]
        if a is None or not (0.0<a<=240.0): continue
        if not (mh[j] and pc[j] is not None): continue
        series[t].append((a,c100(pl[j]),c100(pc[j]),tcn[j] or 0)); mstart[t]=mst[j]

# per-leg: window-open cell (pre-onset), open_c, onset_ttms, match_start_ts; minute-bar touch@k
legmeta={}   # ticker -> (cat,cell,open_c,onset_ttms,match_start_ts, minutebar_touch_bool)
sel_tickers=set()
for tk,r in series.items():
    r.sort(key=lambda x:-x[0])
    onset=-1e9
    for (a,plo,pcl,tc) in r:
        if tc>=LIVE_BURST and a<=LIVE_NEAR_START and a>onset: onset=a
    pre=[x for x in r if x[0]>onset]
    if not pre: continue
    open_c=pre[0][2]; cell=min(94,max(5,open_c)); cat=cat_of[tk]
    if (cat,cell) not in sel_keys: continue
    thr=open_c-KTEST
    mb=any(x[1] is not None and x[1]<=thr for x in pre)   # minute-bar price_low touch
    legmeta[tk]=(cat,cell,open_c,onset,mstart.get(tk),mb)
    sel_tickers.add(tk)
print("tickers in selected cells:",len(sel_tickers))

# ---- TICK touch from g9_trades (stream, filter to sel_tickers) ----
tick_min=collections.defaultdict(lambda:9999)   # ticker -> min yes_price cents (pre-onset premarket)
def parse_iso(s):
    try: return datetime.datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()
    except: return None
g9=pq.ParquetFile(G9)
gcols=["ticker","created_time","yes_price_dollars"]
for i in range(g9.metadata.num_row_groups):
    rg=g9.read_row_group(i,columns=gcols)
    tks=rg.column("ticker").to_pylist()
    # quick skip row-group if no selected ticker present
    if not sel_tickers.intersection(tks): continue
    cts=rg.column("created_time").to_pylist(); yp=rg.column("yes_price_dollars").to_pylist()
    for j in range(len(tks)):
        tk=tks[j]
        if tk not in legmeta: continue
        ms=legmeta[tk][4]; onset=legmeta[tk][3]
        if ms is None: continue
        ts=parse_iso(cts[j])
        if ts is None: continue
        # pre-onset premarket: created before (match_start - onset_ttms*60)
        if ts >= ms - onset*60: continue
        if yp[j] is None: continue
        c=int(round(yp[j]*100))
        if c<tick_min[tk]: tick_min[tk]=c

# ---- compare per selected cell: minute-bar touch-rate vs tick touch-rate ----
print("\n-- TICK vs MINUTE-BAR down-touch @ k=%d (pre-onset premarket) --"%KTEST)
print("  %-18s %-10s cell  N   minbar  tick   delta(tick-minbar)"%("selection","category"))
agg=collections.defaultdict(lambda:[0,0,0])  # (cat,cell)->[n, minbar_touch, tick_touch]
for tk,(cat,cell,open_c,onset,ms,mb) in legmeta.items():
    a=agg[(cat,cell)]; a[0]+=1; a[1]+=1 if mb else 0
    tmin=tick_min.get(tk,9999)
    tt=1 if tmin<=open_c-KTEST else 0
    a[2]+=tt
for tag,cat,c in sel:
    n,mbt,tct=agg[(cat,c)]
    if n==0: print("  %-18s %-10s %3d   0    -      -"%(tag,cat,c)); continue
    print("  %-18s %-10s %3d  %3d  %.3f  %.3f  %+.3f"%(tag,cat,c,n,mbt/n,tct/n,(tct-mbt)/n))
print("\nNOTE: minute-bar uses price_low (intra-minute trade low) which already captures the")
print("intra-minute tick low; positive delta => ticks find touches the minute bar missed")
print("(B25 undercount); ~0 => price_low aggregation does NOT cut against touch detection.")
