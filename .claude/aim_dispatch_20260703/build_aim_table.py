#!/usr/bin/env python3
"""[READ-ONLY] Item 0 — per-category AIM TABLE.
Aim = the fillable DIP below current (discount a correctly-placed resting bid is paid to the gun),
NOT FV. Supersedes the flat 3c constant. Tour cats from PMU (9.3M rows, bid/ask/forward-dip/spread);
ITF from raw gzipped trade CSVs. Output: /tmp/aim_table.json (machine, consumed by patches 1+2),
/tmp/aim_table.tsv (human), /tmp/aim_summary.txt."""
import glob,gzip,csv,io,json,os,sys
import pandas as pd, numpy as np
PMU="data/durable/per_minute_universe/per_minute_features_batch_*.parquet"
TOUR=["ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL"]
# price buckets (cents), on the leg's OWN price
BUCKETS=[(1,20,"01-20"),(21,40,"21-40"),(41,49,"41-49"),(50,59,"50-59"),(60,79,"60-79"),(80,99,"80-99")]
def bkt(p):
    for lo,hi,nm in BUCKETS:
        if lo<=p<=hi: return nm
    return None
def med(a): a=np.asarray(a,float); a=a[np.isfinite(a)]; return float(np.median(a)) if len(a) else float('nan')
def pct(a,q): a=np.asarray(a,float); a=a[np.isfinite(a)]; return float(np.percentile(a,q)) if len(a) else float('nan')

COLS=["category","price_close","yes_bid_close","yes_ask_close","spread_close","spread_band",
      "min_yes_ask_forward_to_match_start","max_yes_bid_forward_to_match_start","bounce_to_match_start",
      "time_to_match_start_min","regime","minute_has_trade","paired_yes_bid_sum"]

def load_tour():
    fr=[]
    for f in sorted(glob.glob(PMU)):
        try: d=pd.read_parquet(f,columns=COLS)
        except Exception as e:
            print("skip",f,e,file=sys.stderr); continue
        d=d[(d.category.isin(TOUR))&(d.regime=="premarket")
            &(d.time_to_match_start_min>=15)&(d.time_to_match_start_min<=300)]
        if len(d): fr.append(d)
    return pd.concat(fr,ignore_index=True) if fr else pd.DataFrame(columns=COLS)

def tour_rows(df):
    out=[]
    C=lambda s: (s.astype(float)*100)
    df=df.copy()
    df["p"]=(df.price_close.astype(float)*100).round()
    df["bidc"]=(df.yes_bid_close.astype(float)*100)
    df["askc"]=(df.yes_ask_close.astype(float)*100)
    df["spc"]=(df.spread_close.astype(float)*100)
    df["minask"]=(df.min_yes_ask_forward_to_match_start.astype(float)*100)
    df["maxbid"]=(df.max_yes_bid_forward_to_match_start.astype(float)*100)
    df["bounce"]=(df.bounce_to_match_start.astype(float)*100)
    df["dip"]=df.p-df.minask   # how deep ask dips below current price before gun (the AIM)
    df["bkt"]=df.p.apply(lambda x: bkt(x) if np.isfinite(x) else None)
    for cat in TOUR:
        for lo,hi,nm in BUCKETS:
            s=df[(df.category==cat)&(df.bkt==nm)]
            if len(s)<200: continue
            dip=s.dip.to_numpy(float); dip=dip[np.isfinite(dip)]
            fillrate=float(np.mean(dip>0)) if len(dip) else 0.0   # A49 analog: % where ask dips below current
            drift=med(s.bounce)                                   # + = riser (rises to gun), - = faller
            spread=med(s.spc)
            wide=float(np.mean(s.spread_band=="wide")); tight=float(np.mean(s.spread_band=="tight"))
            dip_med=med(dip); dip_p75=pct(dip,75)
            comb=med(s.paired_yes_bid_sum.astype(float)*100)
            out.append(dict(cat=cat,bucket=nm,N=len(s),drift_med=round(drift,2),
                side=("RISER" if drift>=0 else "FALLER"),
                dip_med=round(dip_med,2),dip_p75=round(dip_p75,2),fill_rate=round(fillrate,3),
                spread_med=round(spread,2),pct_wide=round(wide,2),pct_tight=round(tight,2),
                paired_bid_sum_med=round(comb,1) if np.isfinite(comb) else None))
    return out

# ---- ITF from raw gzipped trade CSVs ----
def itf_rows():
    out=[]
    for cat,ser in [("ITF_M","KXITFMATCH"),("ITF_W","KXITFWMATCH")]:
        files=sorted(glob.glob(f"analysis/trades/{ser}-*.csv.gz"))+sorted(glob.glob(f"analysis/trades/{ser}-*.csv"))
        # per-ticker: build premarket anchor + dip; approximate spread from prints
        # collect per-bucket dip samples
        samp={nm:[] for _,_,nm in BUCKETS}; sprd={nm:[] for _,_,nm in BUCKETS}; drift={nm:[] for _,_,nm in BUCKETS}
        cnt=0
        for f in files:
            try:
                op=gzip.open(f,'rt') if f.endswith('.gz') else open(f)
                rd=list(csv.DictReader(op)); op.close()
            except Exception: continue
            if len(rd)<5: continue
            cols=rd[0].keys()
            # find price + ts columns robustly
            pcol=next((c for c in cols if c.lower() in('yes_price','price','trade_price','last_price')),None)
            tcol=next((c for c in cols if 'time_to' in c.lower() or c.lower() in('ttms','minutes_to_start')),None)
            tscol=next((c for c in cols if c.lower() in('ts','timestamp','created_time','trade_ts')),None)
            bcol=next((c for c in cols if 'bid' in c.lower()),None); acol=next((c for c in cols if 'ask' in c.lower()),None)
            if pcol is None: continue
            def num(x):
                try: v=float(x); return v*100 if v<=1.0 else v
                except: return None
            prices=[num(r.get(pcol)) for r in rd]; prices=[p for p in prices if p is not None]
            if len(prices)<5: continue
            # anchor = median of first third (premarket), dip = anchor - min(prices before last third)
            k=max(1,len(prices)//3)
            anchor=float(np.median(prices[:k]))
            if anchor<3 or anchor>97: continue
            pre_min=float(np.min(prices[:2*k]))       # dip within premarket-ish span
            dipv=anchor-pre_min
            last=float(np.median(prices[-k:]))
            nm=bkt(round(anchor))
            if not nm: continue
            samp[nm].append(dipv); drift[nm].append(last-anchor)
            if bcol and acol:
                for r in rd[:2*k]:
                    b=num(r.get(bcol)); a=num(r.get(acol))
                    if b and a and a>b: sprd[nm].append(a-b)
            cnt+=1
        for lo,hi,nm in BUCKETS:
            d=np.asarray(samp[nm],float); d=d[np.isfinite(d)]
            if len(d)<15: continue
            dr=med(drift[nm]); sp=med(sprd[nm]) if sprd[nm] else float('nan')
            out.append(dict(cat=cat,bucket=nm,N=int(len(d)),drift_med=round(dr,2),
                side=("RISER" if dr>=0 else "FALLER"),
                dip_med=round(med(d),2),dip_p75=round(pct(d,75),2),fill_rate=round(float(np.mean(d>0)),3),
                spread_med=round(sp,2) if np.isfinite(sp) else None,pct_wide=None,pct_tight=None,
                paired_bid_sum_med=None))
    return out

print("loading PMU...",file=sys.stderr)
tdf=load_tour()
print("PMU premarket rows:",len(tdf),file=sys.stderr)
rows=tour_rows(tdf)
print("tour buckets:",len(rows),"| ITF...",file=sys.stderr)
rows+=itf_rows()

# ---- derive deployable per-cat table: faller_depth + riser_post + combined_goal ----
# faller_depth = aim = clamp(round(dip_med), 1, fillable_max). fillable_max wider when spread wide.
# riser_post = 0 (post at bid; risers dip shallow). combined_goal = 97 (operator default).
COMBINED_GOAL=97
deploy={}
for r in rows:
    cat=r['cat']; deploy.setdefault(cat,{})
    dip=r['dip_med'] if r['dip_med']==r['dip_med'] else 0
    spread=r.get('spread_med') or 3
    # fillable_max: how deep a resting bid still gets paid ~ min(spread-derived reach, dip_p75)
    fmax=max(2, round((spread or 3)*1.0 + 1))   # wide spreads (ITF/CHALL) -> deeper allowed
    faller_depth=int(max(1,min(round(dip) if dip==dip else 1, fmax, r.get('dip_p75') or 99)))
    riser_post=0 if r['side']=="RISER" else max(0,faller_depth-1)
    deploy[cat][r['bucket']]=dict(side=r['side'],faller_depth=faller_depth,riser_post=riser_post,
        dip_med=r['dip_med'],dip_p75=r['dip_p75'],fill_rate=r['fill_rate'],spread_med=r.get('spread_med'),
        N=r['N'],combined_goal=COMBINED_GOAL)

json.dump({'meta':{'source':'PMU 9.3M rows (tour) + raw trade CSVs (ITF); aim=dip below current, not FV; supersedes flat 3c',
    'combined_goal_default':COMBINED_GOAL,'buckets':[b[2] for b in BUCKETS]},'aim':deploy},
    open('/tmp/aim_table.json','w'),indent=1)

tf=open('/tmp/aim_table.tsv','w')
cols=['cat','bucket','N','side','drift_med','dip_med','dip_p75','fill_rate','spread_med','pct_wide','paired_bid_sum_med']
tf.write('\t'.join(cols)+'\n')
for r in sorted(rows,key=lambda x:(x['cat'],x['bucket'])):
    tf.write('\t'.join(str(r.get(c,'')) for c in cols)+'\n')
tf.close()

sm=open('/tmp/aim_summary.txt','w')
def w(x): sm.write(x+'\n');
w("==== AIM TABLE (aim = fillable DIP below current; supersedes flat 3c) ====")
w(f"{'cat':10s} {'bucket':7s} {'N':>6} {'side':6s} {'drift':>6} {'dipMed':>6} {'dip75':>6} {'fill%':>6} {'sprd':>5} {'->faller_depth':>14} {'riser':>5}")
for r in sorted(rows,key=lambda x:(x['cat'],x['bucket'])):
    dpl=deploy[r['cat']][r['bucket']]
    w(f"{r['cat']:10s} {r['bucket']:7s} {r['N']:>6} {r['side']:6s} {str(r['drift_med']):>6} {str(r['dip_med']):>6} {str(r['dip_p75']):>6} {str(r['fill_rate']):>6} {str(r.get('spread_med')):>5} {dpl['faller_depth']:>14} {dpl['riser_post']:>5}")
w("\nDeployable per-cat faller_depth (the aim, replaces flat 3c):")
for cat in sorted(deploy):
    fds={b:deploy[cat][b]['faller_depth'] for b in deploy[cat]}
    w(f"  {cat:10s} {fds}")
sm.close()
print("DONE")
