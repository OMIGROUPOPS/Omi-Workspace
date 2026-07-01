#!/usr/bin/env python3
# READ-ONLY: re-frame the 40% one-leg-only -> recoverable vs genuinely-unfillable.
# Recoverable = a resting AT-TOUCH maker on the missed leg would have filled (a trade
# printed <= prevailing best_bid at some point in the distortion window) but the bot's
# actual (dumb/static/lone-top/stranded) bid did not. Categorize the intelligence needed.
import csv,os,datetime,collections,glob,functools
TICK="/root/Omi-Workspace/arb-executor/analysis/premarket_ticks"
TRADE="/root/Omi-Workspace/arb-executor/analysis/trades"
def cat(t):
    if t.startswith("KXATPCHALLENGERMATCH"):return "ATP_CHALL"
    if t.startswith("KXWTACHALLENGERMATCH"):return "WTA_CHALL"
    if t.startswith("KXATPMATCH"):return "ATP_MAIN"
    if t.startswith("KXWTAMATCH"):return "WTA_MAIN"
    if t.startswith("KXITF"):return "ITF"
    return "OTHER"
@functools.lru_cache(maxsize=8192)
def dayb(ds):
    return datetime.date(int(ds[0:4]),int(ds[5:7]),int(ds[8:10])).toordinal()*86400
def ep(s):
    try:
        h=int(s[11:13])%12+(12 if s[20]=='P' else 0)
        return dayb(s[0:10])+h*3600+int(s[14:16])*60+int(s[17:19])
    except: return None
SPREAD_MAX=12; BID_MIN=2
def load_tick(tk):
    out=[]
    for r in csv.DictReader(open(os.path.join(TICK,tk+".csv"))):
        t=ep(r["ts_et"])
        if t is None: continue
        try: out.append((t,int(r["bid_1"] or 0),int(r["ask_1"] or 100),int(r["last_trade"] or 0),int(r["bid_1_sz"] or 0)))
        except: continue
    return out
def load_trades(tk):
    p=os.path.join(TRADE,tk+".csv"); out=[]
    if not os.path.exists(p): return out
    for r in csv.DictReader(open(p)):
        t=ep(r["ts_et"])
        if t is None: continue
        try: out.append((t,int(r["price"])))
        except: continue
    out.sort(); return out
def prevailing_bid(series,t):
    b=0
    for (tt,bid,*_ ) in series:
        if tt<=t: b=bid
        else: break
    return b

legs=collections.defaultdict(list)
for f in glob.glob(TICK+"/*26JUN2[456]*.csv"):
    b=os.path.basename(f)[:-4]; legs[b.rsplit("-",1)[0]].append(b)
events={e:ls for e,ls in legs.items() if len(ls)==2}

both=one=neither=0
recoverable=0; unfillable=0
intel=collections.Counter()
rec_by_cat=collections.Counter(); one_by_cat=collections.Counter()
samples=[]
for e,(la,lb) in events.items():
    A=load_tick(la); B=load_tick(lb)
    if len(A)<20 or len(B)<20: continue
    allt=sorted(set(x[0] for x in A)|set(x[0] for x in B))
    pa=pb=0; ba=bb=0; aa=ab=100; lta=ltb=0; series=[]
    for t in allt:
        while pa<len(A) and A[pa][0]<=t: ba,aa,lta=A[pa][1],A[pa][2],A[pa][3]; pa+=1
        while pb<len(B) and B[pb][0]<=t: bb,ab,ltb=B[pb][1],B[pb][2],B[pb][3]; pb+=1
        if ba>=BID_MIN and bb>=BID_MIN and aa<=99 and ab<=99 and (aa-ba)<=SPREAD_MAX and (ab-bb)<=SPREAD_MAX and lta>0 and ltb>0:
            series.append((t,ba+bb,ba,bb))
    if len(series)<20: continue
    mn=min(s[1] for s in series)
    if mn>95: continue
    di=min(range(len(series)),key=lambda i:series[i][1])
    t0,comb,cba,cbb=series[di]
    TA=load_trades(la); TB=load_trades(lb)
    lo,hi=t0-150,t0+600
    ra=any(p<=cba for (t,p) in TA if lo<=t<=hi)
    rb=any(p<=cbb for (t,p) in TB if lo<=t<=hi)
    c=cat(la)
    if ra and rb: both+=1; continue
    if not (ra or rb): neither+=1; continue
    # ONE-leg-only
    one+=1; one_by_cat[c]+=1
    missed, ms, mt, our_bid = (lb,B,TB,cbb) if ra else (la,A,TA,cba)
    # wider distortion window +-45min, clipped to formed span
    w0,w1=max(series[0][0],t0-2700),min(series[-1][0],t0+2700)
    # fillable_maker: any trade <= prevailing best_bid on missed leg in window
    fill_t=None; fill_bid=None
    for (tt,p) in mt:
        if tt<w0 or tt>w1: continue
        pb_=prevailing_bid(ms,tt)
        if pb_>0 and p<=pb_:
            fill_t=tt; fill_bid=pb_; break
    if fill_t is None:
        unfillable+=1
        continue
    recoverable+=1; rec_by_cat[c]+=1
    # categorize intelligence needed (book state on missed leg)
    bids_in=[bid for (tt,bid,*_ ) in ms if w0<=tt<=w1 and bid>0]
    szs=[(tt,sz) for (tt,bid,a,lt,sz) in ms if w0<=tt<=w1 and bid>0]
    maxbid=max(bids_in) if bids_in else our_bid
    # support trend at the time of fill (lone-top + building?)
    sz_at_fill=0
    for (tt,bid,a,lt,sz) in ms:
        if tt<=fill_t: sz_at_fill=sz
        else: break
    sz_start=szs[0][1] if szs else 0
    if fill_bid> our_bid+1 or maxbid> our_bid+1:
        intel["RE-JOIN (best-bid moved up; we stranded below)"]+=1; lab="re-join"
    elif fill_bid< our_bid-1:
        intel["SCOOT (leg faded; follow down)"]+=1; lab="scoot"
    elif sz_at_fill<=50 and sz_at_fill>=sz_start:
        intel["PULL-RATE (lone-top, support building, hold)"]+=1; lab="pull-rate"
    else:
        intel["POSITIONING (at-touch maker would catch; bot not resting there)"]+=1; lab="positioning"
    if len(samples)<12: samples.append((e[-16:],c,f"comb{comb}",f"missed {missed[-3:]}@{our_bid}",f"filled@{fill_bid}",lab))

tested=both+one+neither
print(f"matches reaching formed combined<=95: {tested}   (both={both} one={one} neither={neither})")
print(f"\n=== (1) THE 40% ONE-LEG-ONLY split ===")
print(f"  one-leg-only total: {one}")
print(f"  RECOVERABLE (flow existed on missed leg; at-touch maker would fill): {recoverable} ({100*recoverable/max(1,one):.0f}% of one-leg)")
print(f"  GENUINELY-UNFILLABLE (no seller ever hit the touch): {unfillable} ({100*unfillable/max(1,one):.0f}% of one-leg)")
print(f"\n=== (2) INTELLIGENCE NEEDED per recoverable leg ===")
for k,v in intel.most_common(): print(f"  {v:3d}  {k}")
print(f"\n=== one-leg & recoverable by category ===")
for c in sorted(one_by_cat,key=lambda c:-one_by_cat[c]):
    print(f"  {c:10s} one-leg={one_by_cat[c]:3d}  recoverable={rec_by_cat[c]:3d}")
print(f"\n=== (3) TRUE ADDRESSABLE EDGE (of {tested} matches reaching <=95) ===")
print(f"  current capture (both legs, broken exec):   {both:3d}  ({100*both/max(1,tested):.0f}%)")
print(f"  + recoverable one-leg (intelligent exec):   {recoverable:3d}")
print(f"  = TRUE ADDRESSABLE:                          {both+recoverable:3d}  ({100*(both+recoverable)/max(1,tested):.0f}%)")
print(f"  genuinely out of reach (unfillable+neither): {unfillable+neither:3d}  ({100*(unfillable+neither)/max(1,tested):.0f}%)")
print(f"\nsamples (event,cat,combined,missed-leg@ourbid,filled@bid,intel):")
for s in samples: print("   ",s)
