#!/usr/bin/env python3
"""[READ-ONLY] Overnight ledger + participation sweep + fix scorecard + FV_CAPTURE.
Window: bot restarts 2026-07-02 evening ET -> now. Bot untouched.
Writes /tmp/on3_ledger.tsv, /tmp/on3_participation.tsv, /tmp/on3_agg.txt, /tmp/on3_dump.json"""
import json,time,base64,sys
from pathlib import Path
from datetime import datetime,timezone,timedelta
from collections import defaultdict,Counter
import statistics as st
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import requests
pk=serialization.load_pem_private_key(Path('kalshi.pem').read_bytes(),password=None,backend=default_backend())
B='https://api.elections.kalshi.com/trade-api/v2'
def s(m,p):
    ts=str(int(time.time()*1000)); sp='/trade-api/v2'+p.split('?')[0]
    sig=pk.sign((ts+m+sp).encode(),padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.DIGEST_LENGTH),hashes.SHA256())
    return {'KALSHI-ACCESS-KEY':'f3b064d1-a02e-42a4-b2b1-132834694d23','KALSHI-ACCESS-SIGNATURE':base64.b64encode(sig).decode(),'KALSHI-ACCESS-TIMESTAMP':ts}
def g(p):
    for _ in range(4):
        try: return requests.get(B+p,headers=s('GET',p),timeout=30).json()
        except: time.sleep(0.4)
    return {}
ET=timezone(timedelta(hours=-4))
def hm(e): return datetime.fromtimestamp(e,ET).strftime('%m-%d %H:%M')
def C(x): return round(float(x)*100) if x else None
SER=['KXATPCHALLENGERMATCH','KXWTACHALLENGERMATCH','KXATPMATCH','KXWTAMATCH','KXITFMATCH','KXITFWMATCH']
def ser_of(tk): return next((x for x in SER if tk.startswith(x)),None)
CAT={'KXATPMATCH':'ATP_MAIN','KXWTAMATCH':'WTA_MAIN','KXATPCHALLENGERMATCH':'ATP_CHALL','KXWTACHALLENGERMATCH':'WTA_CHALL','KXITFMATCH':'ITF_M','KXITFWMATCH':'ITF_W'}
import sys as _sys
LOG=_sys.argv[1] if len(_sys.argv)>1 else 'logs/live_v3_20260704.jsonl'
# tonight (flags TRUE first night): e422055 boot 18:27:55 ET Jul 4 = epoch 1783204075
BOOT_LIVE = float(_sys.argv[2]) if len(_sys.argv)>2 else 1783204075.0

fills={}; exitp={}; exitfill={}; settled={}
placed_evt=defaultdict(set)      # event -> set(tickers) that got order_placed buy
window_evt={}                    # event -> (price,cell,ttm_min) intended
sched={}                         # event -> {start_time,cat,p1,p2,method}
discovery=[]                     # discovery snapshots
fvburst={}                       # ticker -> entry_minus_fv_burst detail
abandon_defer=Counter()          # event -> count of schedule_abandon_deferred
completion_evt={}                # event -> completion_no_attempt detail
matchlive={}                     # event -> match_live_detected detail
vplace={}                        # ticker -> last v4_place detail
occ_obs=Counter()

fh=open(LOG,encoding='utf-8',errors='replace')
for line in fh:
    if '"event"' not in line: continue
    try: o=json.loads(line)
    except: continue
    e=o.get('event'); tk=o.get('ticker'); d=o.get('details',{}); ts=o.get('ts_epoch',0)
    if e=='schedule_match':
        ev=d.get('event')
        if ev: sched[ev]={'start':d.get('start_time'),'cat':d.get('category'),'p1':d.get('p1'),'p2':d.get('p2'),'method':d.get('method')}
    elif e=='discovery':
        discovery.append((ts,d.get('total_tickers'),d.get('by_category',{})))
    elif e=='window_open_set':
        ev=d.get('event')
        if ev: window_evt[ev]=window_evt.get(ev,{}); window_evt[ev][tk]={'price':d.get('price'),'cell':d.get('cell'),'ttm':d.get('ttm_min')}
    elif e=='v4_place':
        if tk: vplace[tk]=d
    elif e=='order_placed' and d.get('action')=='buy':
        ser=ser_of(tk)
        if ser: placed_evt[tk.rsplit('-',1)[0]].add(tk)
    elif e=='entry_filled':
        if tk and tk not in fills:
            fills[tk]={'fill':d.get('fill_price'),'posted':d.get('posted_price'),'play':d.get('play_type'),'dir':d.get('direction'),'qty':d.get('qty'),'ts':ts}
    elif e=='v4_exit_posted':
        exitp[tk]={'band_x':d.get('band_x'),'exit_price':d.get('exit_price'),'cell':d.get('cell_id'),'entry':d.get('entry_price')}
    elif e=='exit_filled':
        exitfill[tk]={'pnl':d.get('pnl_cents'),'exit':d.get('exit_price'),'entry':d.get('entry_price'),'qty':d.get('qty')}
    elif e=='settled':
        settled[tk]={'settle':d.get('settle'),'pnl':d.get('pnl_cents'),'qty':d.get('settled_qty'),'entry':d.get('entry_price'),'exitq':d.get('exit_filled_qty')}
    elif e=='fv_burst_anchor':
        if tk: fvburst[tk]=d
    elif e=='schedule_abandon_deferred':
        ev=d.get('event')
        if ev: abandon_defer[ev]+=1
    elif e=='completion_no_attempt':
        ev=d.get('event')
        if ev: completion_evt[ev]=d
    elif e=='match_live_detected':
        ev=d.get('event')
        if ev: matchlive[ev]={'sig':d.get('signal'),'trades':d.get('trades_in_window'),'tts_min':d.get('tts_min')}
    elif e=='kalshi_occ_observe':
        occ_obs[o.get('ticker') or d.get('event')]+=1
fh.close()
print(f'fills={len(fills)} placed_evts={len(placed_evt)} sched={len(sched)} fvburst={len(fvburst)}',file=sys.stderr)

namecache={}
def meta(tk):
    if tk in namecache: return namecache[tk]
    m=g(f'/markets/{tk}').get('market',{})
    namecache[tk]=(m.get('yes_sub_title'),m.get('result'),m.get('close_time'))
    return namecache[tk]

def gun_info(tk,fill_ts):
    ser=ser_of(tk); start=int(fill_ts-3600); end=int(fill_ts+6*3600)
    cs=g(f'/series/{ser}/markets/{tk}/candlesticks?start_ts={start}&end_ts={end}&period_interval=1').get('candlesticks',[])
    rows=[]; carry=None
    for c in cs:
        ts=c['end_period_ts']; pr=c.get('price',{})
        lt=C(pr.get('close_dollars')) if pr.get('close_dollars') else (C(pr.get('previous_dollars')) if pr.get('previous_dollars') else carry)
        if lt is not None: carry=lt
        rows.append((ts,lt,float(c.get('volume_fp',0) or 0)))
    if not rows: return None
    n=len(rows); peak10=0; gun=None
    for i in range(n):
        t0=rows[i][0]; fwd=sum(rows[j][2] for j in range(i,n) if rows[j][0]<t0+600)
        peak10=max(peak10,fwd)
        if gun is None and rows[i][2]>=150 and fwd>=3000: gun=i
    ambiguous=(peak10<3000)
    if gun is None:
        gun=max(range(n),key=lambda i:rows[i][2]); ambiguous=True
    gts,glt,gv=rows[gun]
    pre=[r for r in rows if r[0]<gts and r[1] is not None]
    final_tick=pre[-1][1] if pre else None
    return {'gun_ts':gts,'gun_price':glt,'final_tick':final_tick,'ambiguous':ambiguous,'peak10':round(peak10),'settle_price':rows[-1][1]}

def parse_start(sstr):
    if not sstr: return None
    try: return datetime.strptime(sstr,'%Y-%m-%dT%H:%MZ').replace(tzinfo=timezone.utc).timestamp()
    except:
        try: return datetime.strptime(sstr,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp()
        except: return None

rows_out=[]
keys=sorted(fills,key=lambda t:fills[t]['ts'])
for idx,tk in enumerate(keys):
    f=fills[tk]; fill=f['fill']; ser=ser_of(tk); ev=tk.rsplit('-',1)[0]; suf=tk.rsplit('-',1)[-1]
    nm,res,ct=meta(tk); cat=CAT.get(ser,'?')
    gi=gun_info(tk,f['ts'])
    sibs=[x for x in placed_evt.get(ev,()) if x!=tk]
    # also sibs that filled
    fill_sibs=[x for x in fills if x!=tk and x.rsplit('-',1)[0]==ev]
    sib=fill_sibs[0] if fill_sibs else (sibs[0] if sibs else None)
    sib_filled=sib in fills if sib else False
    sib_price=fills[sib]['fill'] if sib_filled else None
    ep=exitp.get(tk,{})
    if tk in exitfill: outc='exit_FILL'; pnl=(exitfill[tk]['pnl'] or 0)/100.0
    elif tk in settled: outc='settle_'+str(settled[tk]['settle']); pnl=(settled[tk]['pnl'] or 0)/100.0
    else: outc='OPEN'; pnl=0.0
    gp=gi['gun_price'] if gi else None; ft=gi['final_tick'] if gi else None
    d_gun=(fill-gp) if (gp is not None and fill is not None) else None
    # FV_CAPTURE = price at true tape onset - fill. onset=gun; fallback=final_tick pre-scheduled
    fv_onset = gp if (gi and not gi['ambiguous']) else ft
    fv_capture=(fv_onset-fill) if (fv_onset is not None and fill is not None) else None
    fvb=fvburst.get(tk,{})
    sched_start=parse_start((sched.get(ev,{}) or {}).get('start'))
    vp=vplace.get(tk,{})
    rows_out.append({'tk':tk,'ev':ev,'suf':suf,'name':nm,'cat':cat,'cell':ep.get('cell') or vp.get('cell'),
        'fill':fill,'fill_ts':f['ts'],'fill_t':hm(f['ts']),'play':f['play'],'dir':f['dir'],'qty':f['qty'],
        'gun_ts':gi['gun_ts'] if gi else None,'gun_t':hm(gi['gun_ts']) if gi else None,'gun_p':gp,'final_tick':ft,
        'ambiguous':gi['ambiguous'] if gi else True,'peak10':gi['peak10'] if gi else None,
        'sched_start':sched_start,'sched_t':hm(sched_start) if sched_start else None,
        'd_gun':d_gun,'fv_capture':fv_capture,'fv_onset_src':('gun' if (gi and not gi['ambiguous']) else 'final_tick'),
        'fvburst_emfb':fvb.get('entry_minus_fv_burst'),'fvburst_mid':fvb.get('fv_mid'),'fvburst_pre':fvb.get('filled_pre_burst'),
        'anchor_src':vp.get('anchor_src'),'ref_src':vp.get('reference_source'),'min_before_start':vp.get('min_before_start'),
        'runway':vp.get('runway_status'),'target_bid':vp.get('target_bid'),'current_ask':vp.get('current_ask'),
        'sib':sib,'sib_filled':sib_filled,'sib_price':sib_price,
        'band_x':ep.get('band_x'),'exit_posted':ep.get('exit_price'),'outc':outc,'pnl':pnl,
        'result':res,'settle_price':gi['settle_price'] if gi else None})
    if idx%15==0: print(f'..{idx}/{len(keys)}',file=sys.stderr)

# ===== PER-EVENT (game) participation table =====
all_events=set(sched)|set(placed_evt)|set(window_evt)|{r['ev'] for r in rows_out}|set(abandon_defer)
evrows=[]
filled_by_ev=defaultdict(list)
for r in rows_out: filled_by_ev[r['ev']].append(r)
for ev in sorted(all_events):
    ser=ser_of(ev+'-X') or ser_of(ev)
    cat=CAT.get(ser_of(ev) or (ser or ''), (sched.get(ev,{}) or {}).get('cat','?'))
    rested=len(placed_evt.get(ev,set()))
    intended=len(window_evt.get(ev,{}))
    fl=filled_by_ev.get(ev,[])
    nf=len(fl)
    combined=sum(x['fill'] for x in fl) if nf>=2 else None
    evrows.append({'ev':ev,'cat':cat,'scheduled':ev in sched,'intended':intended,'rested':rested,
        'n_filled':nf,'combined':combined,'abandon_defer':abandon_defer.get(ev,0),
        'match_live':ev in matchlive,'completion_no_attempt':ev in completion_evt})

# ===== write dumps =====
json.dump({'legs':rows_out,'events':evrows,'discovery':discovery,
    'flags_note':'ba08243 armed: per_cat_depth=T leg2_reshuffle=T premarket_walk_cap=T match_live_grace_kill=T latch_tape_override=T (+ prior: tape_gated_abandon per_side_placement completion_all_cells completion_combined_ceiling)',
    'abandon_defer_total':sum(abandon_defer.values()),'occ_obs_total':sum(occ_obs.values())},
    open('/tmp/on3_dump.json','w'),default=str)

tf=open('/tmp/on3_ledger.tsv','w')
cols=['cat','tk','name','fill','fill_t','sched_t','gun_t','gun_p','final_tick','d_gun','fv_capture','fv_onset_src','fvburst_emfb','ambiguous','dir','play','anchor_src','ref_src','min_before_start','runway','sib_filled','sib_price','band_x','exit_posted','outc','pnl','result']
tf.write('\t'.join(cols)+'\n')
for r in sorted(rows_out,key=lambda x:(x['cat'],x['ev'])): tf.write('\t'.join(str(r.get(c,'')) for c in cols)+'\n')
tf.close()

pf=open('/tmp/on3_participation.tsv','w')
pc=['cat','ev','scheduled','intended','rested','n_filled','combined','abandon_defer','match_live','completion_no_attempt']
pf.write('\t'.join(pc)+'\n')
for r in sorted(evrows,key=lambda x:(x['cat'],x['ev'])): pf.write('\t'.join(str(r.get(c,'')) for c in pc)+'\n')
pf.close()

# ===== aggregates =====
out=open('/tmp/on3_agg.txt','w')
def w(x): out.write(x+'\n')
w("==== WINDOW: overnight log live_v3_20260702 (evening restarts -> now) ====")
w(f"legs filled: {len(rows_out)} | events touched: {len(all_events)} | schedule_abandon_deferred total: {sum(abandon_defer.values())}")

w("\n==== PARTICIPATION SWEEP ====")
by_cat=defaultdict(lambda:[0,0,0,0])  # tracked,rested,>=1fill,pairfill
for r in evrows:
    c=r['cat']; by_cat[c][0]+=1
    if r['rested']>0: by_cat[c][1]+=1
    if r['n_filled']>=1: by_cat[c][2]+=1
    if r['n_filled']>=2: by_cat[c][3]+=1
w(f"{'cat':10s} {'tracked':>7} {'rested':>7} {'>=1fill':>7} {'pairfill':>8}")
tot=[0,0,0,0]
for c in sorted(by_cat):
    v=by_cat[c];
    for i in range(4): tot[i]+=v[i]
    w(f"{c:10s} {v[0]:>7} {v[1]:>7} {v[2]:>7} {v[3]:>8}")
w(f"{'TOTAL':10s} {tot[0]:>7} {tot[1]:>7} {tot[2]:>7} {tot[3]:>8}")
w(f"\nBaseline trajectory: 1.5/8 -> 19 -> [last night] -> tonight tracked={tot[0]} rested={tot[1]} pairfill={tot[3]}")
if discovery:
    w("discovery snapshots (total_tickers):")
    for ts,n,bc in discovery[:3]: w(f"  {hm(ts)} total={n} {bc}")

w("\n==== FV_CAPTURE (price at tape onset - fill; +=bought under FV) ====")
fvv=[r for r in rows_out if r['fv_capture'] is not None]
allfv=[r['fv_capture'] for r in fvv]
if allfv:
    w(f"ALL legs N={len(allfv)} min={min(allfv):.0f} p50={st.median(allfv):.0f} mean={st.mean(allfv):.1f} max={max(allfv):.0f} pos={sum(1 for x in allfv if x>0)}/{len(allfv)}")
w(f"{'cat':10s} {'N':>3} {'min':>5} {'p50':>5} {'mean':>6} {'max':>5} {'%pos':>5}")
for c in sorted(set(r['cat'] for r in fvv)):
    vs=[r['fv_capture'] for r in fvv if r['cat']==c]
    w(f"{c:10s} {len(vs):>3} {min(vs):>5.0f} {st.median(vs):>5.0f} {st.mean(vs):>6.1f} {max(vs):>5.0f} {100*sum(1 for x in vs if x>0)/len(vs):>4.0f}%")

w("\n==== SYNERGY: pairs both-filled, combined<=100 ====")
# group filled legs by event
strong=0; fragile=0; other=0
w(f"{'event':40s} {'cat':10s} {'comb':>5} {'legA_fv':>7} {'legB_fv':>7} {'shape'}")
for ev,fl in sorted(filled_by_ev.items()):
    if len(fl)<2: continue
    a,b=fl[0],fl[1]
    comb=(a['fill'] or 0)+(b['fill'] or 0)
    fa,fb=a['fv_capture'],b['fv_capture']
    if fa is None or fb is None: shape='fv_unk'; other+=1
    elif fa>0 and fb>0 and comb<=100: shape='STRONG(both+FV)'; strong+=1
    elif (fa< -5 or fb< -5): shape='FRAGILE(deep-neg)'; fragile+=1
    else: shape='mixed'; other+=1
    w(f"{ev:40s} {a['cat']:10s} {comb:>5} {str(round(fa) if fa is not None else '?'):>7} {str(round(fb) if fb is not None else '?'):>7} {shape}")
w(f"SYNERGY totals: strong(both+FV,comb<=100)={strong}  fragile(one deep-neg)={fragile}  other={other}")

w("\n==== FIX SCORECARD (flag error-class counts) ====")
# zero-discount fills: filled at/above onset (fv_capture<=0) among per_side-relevant (dog/anchor<50)
dog_fills=[r for r in rows_out if (r['dir'] in('underdog',) or (r['fill'] is not None and r['fill']<50))]
zd=[r for r in dog_fills if r['fv_capture'] is not None and r['fv_capture']<=0]
paid=[r for r in dog_fills if r['fv_capture'] is not None and r['fv_capture']>0]
w(f"[per_side_placement] dog/sub-50 fills={len(dog_fills)} | PAID-by-dip(FV>0)={len(paid)} | zero-discount(FV<=0)={len(zd)}")
# schedule-killed: events abandoned pre-tape. With tape_gated_abandon on, deferred instead.
killed=[r for r in evrows if r['scheduled'] and r['rested']==0 and r['n_filled']==0]
w(f"[tape_gated_abandon] events scheduled+never-rested+never-filled(pre-tape-killed?)={len(killed)} | abandon_deferred fires={sum(abandon_defer.values())}")
# never-rested: tracked but 0 bids
nr=[r for r in evrows if r['scheduled'] and r['rested']==0]
w(f"[participation] scheduled-but-never-rested={len(nr)} / scheduled={sum(1 for r in evrows if r['scheduled'])}")
# half-armed: 1 leg filled, sibling not filled
half=[r for r in rows_out if not r['sib_filled'] and len([x for x in rows_out if x['ev']==r['ev']])==1]
ha_evts=set(r['ev'] for r in rows_out if len(filled_by_ev[r['ev']])==1)
w(f"[completion/pairing] half-armed pairs (1 leg filled only)={len(ha_evts)} events")

w("\n==== OUTCOME ROLLUP ====")
w(f"exit_FILL legs: {sum(1 for r in rows_out if r['outc']=='exit_FILL')}  ${sum(r['pnl'] for r in rows_out if r['outc']=='exit_FILL'):.2f}")
w(f"settled legs:   {sum(1 for r in rows_out if r['outc'].startswith('settle'))}  ${sum(r['pnl'] for r in rows_out if r['outc'].startswith('settle')):.2f}")
w(f"OPEN legs:      {sum(1 for r in rows_out if r['outc']=='OPEN')}")
w(f"TOTAL realized: ${sum(r['pnl'] for r in rows_out):.2f}")
out.close()
print('DONE')
