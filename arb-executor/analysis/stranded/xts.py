import json,datetime,calendar,os,subprocess
inp=json.load(open('/tmp/stranded_ext.json'))
TD=datetime.timedelta(hours=4)
HDR="ts_et,ticker,bid_1,bid_1_sz,bid_2,bid_2_sz,bid_3,bid_3_sz,bid_4,bid_4_sz,bid_5,bid_5_sz,ask_1,ask_1_sz,ask_2,ask_2_sz,ask_3,ask_3_sz,ask_4,ask_4_sz,ask_5,ask_5_sz,mid,bid_depth_5,ask_depth_5,depth_ratio,last_trade".split(',')
def etp(s):
    try: return calendar.timegm((datetime.datetime.strptime(s.strip(),"%Y-%m-%d %I:%M:%S %p")+TD).timetuple())
    except: return None
def gnum(v):
    try: return float(v) if v not in (None,'') else None
    except: return None
out={}
for c in inp:
    tk=c['tk']; ft=c['ft']; path="analysis/premarket_ticks/%s.csv"%tk
    if ft is None or not os.path.exists(path): out[tk]={'cov':False}; continue
    det=datetime.datetime.utcfromtimestamp(ft)-TD; cand=[]
    for dm in (0,-1,1,-2,2,-3,3):
        pat=(det+datetime.timedelta(minutes=dm)).strftime("%Y-%m-%d %I:%M")
        try: r=subprocess.run(['grep','-F',pat,path],capture_output=True,text=True,timeout=20)
        except: continue
        for line in r.stdout.splitlines():
            row=dict(zip(HDR,line.split(','))); ep=etp(row.get('ts_et',''))
            if ep is not None: cand.append((ep,row))
        if cand: break
    if not cand: out[tk]={'cov':False}; continue
    ep,row=min(cand,key=lambda x:abs(x[0]-ft))
    b,a=gnum(row['bid_1']),gnum(row['ask_1'])
    out[tk]={'cov':True,'bid':b,'ask':a,'mid':((b+a)/2 if (b is not None and a is not None and a>b) else None),'delta':ep-ft}
json.dump(out,open('/tmp/stranded_ticks.json','w'))
print('extracted',len(out),'| covered:',sum(1 for v in out.values() if v.get('cov')),'| two-sided-mid:',sum(1 for v in out.values() if v.get('mid') is not None))
