#!/usr/bin/env python3
"""READ-ONLY 4-day progress artifact (Jun 19-22 2026 ET) from live logs only. Writes 3 CSVs:
per-fill bucketed table, today's complete_cross events, per-day P&L + both-fill summary."""
import json,datetime,csv,collections,hashlib,re
from pathlib import Path
HERE=Path("/root/Omi-Workspace/arb-executor"); DOCS=HERE/"docs/analysis/premarket_dynamics_v1"
DAYS=["20260619","20260620","20260621","20260622"]
MAN=["BARYEV","TURRUB","JOVWAN","TAUSHN","BALMAK","PAPSPE","POTUES","ROCGIM"]
ismanual=lambda tk: any(m in tk for m in MAN)
def iso2ep(s):
    try: return datetime.datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()
    except: return None
def logts2ep(ts):
    m=re.match(r'(\d{4})-(\d\d)-(\d\d) (\d+):(\d\d):(\d\d) (AM|PM)',ts)
    if not m: return None
    y,mo,d,h,mi,s=int(m[1]),int(m[2]),int(m[3]),int(m[4]),int(m[5]),int(m[6])
    if m[7]=="PM" and h!=12:h+=12
    if m[7]=="AM" and h==12:h=0
    return datetime.datetime(y,mo,d,h,mi,s,tzinfo=datetime.timezone.utc).timestamp()+4*3600
def etstr(ep): return datetime.datetime.fromtimestamp(ep-4*3600,tz=datetime.timezone.utc).strftime("%H:%M:%S") if ep else ""
def cat_of(tk):
    if tk.startswith("KXATPCHALLENGERMATCH"): return "ATP_CHALL"
    if tk.startswith("KXWTACHALLENGERMATCH"): return "WTA_CHALL"
    if tk.startswith("KXATPMATCH"): return "ATP_MAIN"
    if tk.startswith("KXWTAMATCH"): return "WTA_MAIN"
# global maps across all 4 days
sched={}; real={}; names={}; refsrc={}
fills=[]; placed=collections.defaultdict(set); filledsides=collections.defaultdict(set)
exits=collections.defaultdict(list); settles=collections.defaultdict(list)
cross=[]
for day in DAYS:
    lf=HERE/f"logs/live_v3_{day}.jsonl"
    if not lf.exists(): continue
    for line in open(lf):
        if not any(s in line for s in ('schedule_match','match_live_detected','v4_place','entry_filled','exit_filled','"settled"','complete_cross')): continue
        try: d=json.loads(line)
        except: continue
        e=d.get("event"); det=d.get("details",{}); tk=d.get("ticker","")
        if e=="schedule_match":
            ev=det.get("event")
            if ev and det.get("start_time"): sched.setdefault(ev,iso2ep(det["start_time"])); names.setdefault(ev,{"p1":det.get("p1"),"p2":det.get("p2")})
        elif e=="match_live_detected":
            ev=det.get("event") or (tk.rsplit("-",1)[0] if tk else None)
            if ev: real.setdefault(ev,logts2ep(d["ts"]))
        elif e=="v4_place" and "-" in tk:
            refsrc.setdefault(tk,det.get("reference_source") or det.get("anchor_src") or "")
            placed[day].add(tk.rsplit("-",1)[0]+"|"+tk.rsplit("-",1)[1])
        elif e=="entry_filled" and "-" in tk:
            fills.append((day,logts2ep(d["ts"]),tk,det.get("fill_price"),det.get("play_type")))
            filledsides[(day,tk.rsplit("-",1)[0])].add(tk.rsplit("-",1)[1])
        elif e=="exit_filled" and "-" in tk:
            exits[day].append((tk,det.get("pnl_cents",0)))
        elif e=="settled" and "-" in tk:
            settles[day].append((tk,det.get("pnl_cents",0)))
        elif e in ("complete_cross","complete_cross_skip","complete_cross_nofill") and day=="20260622":
            cross.append((logts2ep(d["ts"]),e,tk,det))
ANCHOR={"KXATPMATCH-26JUN22CRAROD-ROD":"Jurij Rodionov","KXATPMATCH-26JUN22CRAROD-CRA":"Oliver Crawford"}
def nm(tk):
    if tk in ANCHOR: return ANCHOR[tk]
    ev=tk.rsplit("-",1)[0]; sd=tk.rsplit("-",1)[1]; dn=names.get(ev,{})
    for p in (dn.get("p1"),dn.get("p2")):
        if p and any(tok[:3].upper()==sd.upper() for tok in p.split() if tok):
            return p
    return sd+"?"
def src_label(tk,play):
    rs=refsrc.get(tk,"")
    if rs=="staircase": return "staircase"
    if rs=="join_bid": return "join_bid"
    pl=play or ""
    if "engagement" in pl: return "engagement"
    if "fallback" in pl: return "fallback"
    if "resting_maker" in pl: return "resting_maker"
    if "cross" in pl: return "complete_cross"
    if "reconcil" in pl: return "reconcile"
    return rs or pl or "other"
def bucket(fts,ev):
    sc=sched.get(ev); rs=real.get(ev)
    if sc is None: return "NO_SCHEDULE","scheduled_fallback"
    w1=sc-14400.0; rsrc="latch" if rs else "scheduled_fallback"
    if fts is None: return "NA",rsrc
    if fts<w1: return "PRE_WINDOW1",rsrc
    if fts<sc: return "PREMARKET",rsrc
    if rs: return ("CORRIDOR" if fts<rs else "POST_REAL"),rsrc
    return "POST_SCHEDULED",rsrc
# ---- (1) per-fill table ----
frows=[]
for day,fts,tk,fc,play in fills:
    ev=tk.rsplit("-",1)[0]; bk,rsrc=bucket(fts,ev)
    frows.append(dict(day=day,fill_ts_ET=etstr(fts),player=nm(tk),category=cat_of(tk),fill_cent=fc,
        source=src_label(tk,play),real_start_source=rsrc,bucket=bk,event=ev))
frows.sort(key=lambda r:(r["day"],r["fill_ts_ET"]))
f1=DOCS/"progress_4day_fills_2026-0619_22.csv"
with open(f1,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["day","fill_ts_ET","player","category","fill_cent","source","real_start_source","bucket","event"]); w.writeheader(); [w.writerow(r) for r in frows]
# ---- (2) complete_cross today ----
crows=[]
for fts,e,tk,det in sorted(cross):
    ev=det.get("event") or tk.rsplit("-",1)[0]
    p1=names.get(ev,{}).get("p1"); p2=names.get(ev,{}).get("p2")
    crows.append(dict(ts_ET=etstr(fts),event_kind=e,crossed_leg=nm(tk),match=f"{p1} vs {p2}",
        sib_fill=det.get("sib_fill"),ask=det.get("ask") or det.get("cross_ask"),ask_sz=det.get("ask_sz"),
        basis=det.get("basis"),cap=det.get("cap"),qty=det.get("qty"),fill_price=det.get("fill_price"),event=ev))
f2=DOCS/"complete_cross_2026-06-22.csv"
with open(f2,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["ts_ET","event_kind","crossed_leg","match","sib_fill","ask","ask_sz","basis","cap","qty","fill_price","event"]); w.writeheader(); [w.writerow(r) for r in crows]
# ---- (3) per-day summary ----
srows=[]
lastsummary={}
for day in DAYS:
    lf=HERE/f"logs/live_v3_{day}.jsonl"
    if lf.exists():
        for line in open(lf):
            if '"event": "summary"' in line:
                try: lastsummary[day]=json.loads(line)["details"].get("total_pnl_cents")
                except: pass
for day in DAYS:
    ex=sum(p for tk,p in exits[day] if not ismanual(tk)); se=sum(p for tk,p in settles[day] if not ismanual(tk))
    dayfills=[r for r in frows if r["day"]==day]
    prem=sum(1 for r in dayfills if r["bucket"]=="PREMARKET"); post=sum(1 for r in dayfills if r["bucket"] in ("POST_SCHEDULED","CORRIDOR","POST_REAL"))
    # both-fill rate this day
    evs=set(b.split("|")[0] for b in placed[day])
    both=single=0
    for ev in evs:
        n=len(filledsides.get((day,ev),set()))
        if n>=2: both+=1
        elif n==1: single+=1
    bfr = (100*both/(both+single)) if (both+single) else 0
    srows.append(dict(day=day,fills=len(dayfills),premarket=prem,post_scheduled=post,
        both_filled=both,single_legged=single,both_fill_rate_pct=round(bfr,1),
        exit_sells_pnl_usd=round(ex/100,2),settlement_pnl_usd=round(se/100,2),
        net_realized_logderived_usd=round((ex+se)/100,2),bot_session_counter_usd=round((lastsummary.get(day) or 0)/100,2)))
f3=DOCS/"progress_4day_summary_2026-0619_22.csv"
with open(f3,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(srows[0].keys())); w.writeheader(); [w.writerow(r) for r in srows]
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
# ---- summary stdout ----
C=collections.Counter
print("================ 4-DAY PROGRESS (Jun 19-22 2026 ET) ================")
print(f"per-fill rows: {len(frows)} | complete_cross rows: {len(crows)} | summary rows: {len(srows)}")
print("\n--- PER-DAY ---")
print(f"{'day':<10}{'fills':>6}{'prem':>6}{'post':>6}{'bfr%':>7}{'exit$':>9}{'settle$':>9}{'netReal$':>10}{'botCtr$':>9}")
for r in srows:
    print(f"{r['day']:<10}{r['fills']:>6}{r['premarket']:>6}{r['post_scheduled']:>6}{r['both_fill_rate_pct']:>7}{r['exit_sells_pnl_usd']:>9}{r['settlement_pnl_usd']:>9}{r['net_realized_logderived_usd']:>10}{r['bot_session_counter_usd']:>9}")
print("  NOTE: P&L = log-derived realized (exit_filled+settled pnl_cents, manual excluded) AND the bot session")
print("  counter; NEITHER is account-equity-reconciled per-day (no daily equity snapshots) -- per E161 the")
print("  binding standard is account equity, which overstated vs the counter intraday Jun 22. Treat as directional.")
print("\n--- complete_cross today (Jun 22): kinds ---")
print(dict(C(r['event_kind'] for r in crows)))
print("  FIRES:")
for r in crows:
    if r['event_kind']=='complete_cross': print(f"    {r['ts_ET']} {r['crossed_leg']} ({r['match']}) sib_fill={r['sib_fill']} ask={r['ask']} basis={r['basis']} qty={r['qty']} fill={r['fill_price']}")
# Basel surfacing
bas=[r for r in crows if 'Basel' in (r['match'] or '') or 'Basilashvili' in (r['match'] or '')]
print(f"  BASEL/BASILASHVILI cross events: {len(bas)}")
for r in bas: print(f"    {r['ts_ET']} {r['event_kind']} {r['crossed_leg']} ({r['match']}) sib_fill={r['sib_fill']} ask={r['ask']} basis={r['basis']} cap={r['cap']}")
print("\n--- CROSS-CHECKS ---")
cr=[r for r in frows if r['player']=='Oliver Crawford']
for r in cr: print(f"  Oliver Crawford fill {r['day']} {r['fill_ts_ET']} -> bucket {r['bucket']}  {'PASS' if r['bucket']=='CORRIDOR' else 'FAIL'}")
j22=[r for r in frows if r['day']=='20260622']; j22_2226=[r for r in j22 if '26JUN22' in r['event']]
print(f"  Jun22 entry_filled total={len(j22)} | 26JUN22-only={len(j22_2226)} | carryover={len(j22)-len(j22_2226)} (today_bands_FIXED filled=167; 26JUN22 depth-covered subset)")
print(f"\nCSV1 {f1}\n  sha256 {sha(f1)}")
print(f"CSV2 {f2}\n  sha256 {sha(f2)}")
print(f"CSV3 {f3}\n  sha256 {sha(f3)}")
