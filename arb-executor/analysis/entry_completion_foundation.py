"""Stage-1 foundation for entry-completion derivation: cohort -> T-20 anchors ->
pairing -> leg labeling. Validates against atp_main_paired_primitive probes
(C38/G23 equivalence discipline) BEFORE the full derivation is built on top.
Read-only. sha256-gated PMF already verified (9fde4b5d)."""
import pyarrow.parquet as pq, pyarrow as pa, pyarrow.compute as pc
import glob, collections, statistics, json

PMF="data/durable/per_minute_universe/per_minute_features.parquet"
ATLAS="data/durable/spike_volatility_map"

# --- cohort: union of 4 category atlas spike_perN ticker lists ---
cat_of={}
cohort=set()
for f in sorted(glob.glob(ATLAS+"/*_spike_perN.parquet")):
    cat=f.split("/")[-1].replace("_spike_perN.parquet","")
    tk=pq.read_table(f,columns=["ticker"]).column("ticker").to_pylist()
    for t in tk:
        cohort.add(t); cat_of[t]=cat
print("cohort N (tickers):",len(cohort),"by cat:",dict(collections.Counter(cat_of.values())))

# --- stream PMF, keep only cohort rows in T-20 window [18,22], not unknown ---
cols=["ticker","event_ticker","time_to_match_start_min","match_start_method",
      "yes_ask_close","yes_bid_close","mid_close","settlement_value","result"]
pf=pq.ParquetFile(PMF)
# per ticker: pick minute closest to ttms=20
best={}  # ticker -> (abs(ttms-20), dict)
for i in range(pf.metadata.num_row_groups):
    rg=pf.read_row_group(i,columns=cols)
    d={c:rg.column(c).to_pylist() for c in cols}
    n=len(d["ticker"])
    for j in range(n):
        tk=d["ticker"][j]
        if tk not in cohort: continue
        if d["match_start_method"][j]=="unknown": continue
        ttms=d["time_to_match_start_min"][j]
        if ttms is None or not (18.0<=ttms<=22.0): continue
        ak=d["yes_ask_close"][j]
        if ak is None: continue
        key=abs(ttms-20.0)
        if tk not in best or key<best[tk][0]:
            best[tk]=(key,{"event":d["event_ticker"][j],"ttms":ttms,
                "ask":ak,"bid":d["yes_bid_close"][j],"mid":d["mid_close"][j],
                "settle":d["settlement_value"][j],"result":d["result"][j],"cat":cat_of[tk]})
print("tickers with T-20 anchor:",len(best))

# --- pair legs by event_ticker ---
ev_legs=collections.defaultdict(list)
for tk,(_,r) in best.items():
    ev_legs[r["event"]].append((tk,r))
paired=[]; singleton=0
for ev,legs in ev_legs.items():
    if len(legs)!=2: 
        singleton=singleton if len(legs)!=1 else None
        continue
    (tA,rA),(tB,rB)=legs
    # anchor = T-20 ask (A49 suckers baseline); cents
    aA=round(rA["ask"]*100) if rA["ask"]<1.5 else round(rA["ask"])
    aB=round(rB["ask"]*100) if rB["ask"]<1.5 else round(rB["ask"])
    # fav = higher anchor = legA
    if aA>=aB: fav=(tA,rA,aA); dog=(tB,rB,aB)
    else: fav=(tB,rB,aB); dog=(tA,rA,aA)
    paired.append({"event":ev,"cat":fav[1]["cat"],
        "fav_tk":fav[0],"fav_anchor":fav[2],"fav_settle":fav[1]["settle"],
        "dog_tk":dog[0],"dog_anchor":dog[2],"dog_settle":dog[1]["settle"],
        "combined":fav[2]+dog[2]})

# --- equivalence checks vs handoff (ATP_MAIN) ---
def med(xs): return statistics.median(xs) if xs else None
for cat in ["atp_main","atp_chall","wta_main","wta_chall"]:
    P=[p for p in paired if p["cat"]==cat]
    if not P: continue
    favA=[p["fav_anchor"] for p in P]; dogB=[p["dog_anchor"] for p in P]; comb=[p["combined"] for p in P]
    favwin=sum(1 for p in P if p["fav_settle"]==1.0)/len(P)
    print("%-10s paired=%4d favA_med=%4s dogB_med=%4s comb_mean=%.1f favwin=%.3f"%(
        cat,len(P),med(favA),med(dogB),sum(comb)/len(comb),favwin))
print("TOTAL paired events:",len(paired))
# dump for stage 2
import pickle
with open("/tmp/ec_paired.pkl","wb") as f: pickle.dump(paired,f)
print("wrote /tmp/ec_paired.pkl")
