import json, os, csv, glob, gzip, statistics as stx
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter

BASE="/root/Omi-Workspace/arb-executor"; TR=BASE+"/analysis/trades"; TICK=BASE+"/analysis/premarket_ticks"
EDT=timezone(timedelta(hours=-4))
START=datetime(2026,6,30,15,46,tzinfo=EDT).timestamp()
LOGS=[BASE+"/logs/live_v3_20260630.jsonl",BASE+"/logs/live_v3_20260701.jsonl"]
def et(ts): return datetime.fromtimestamp(ts,EDT).strftime("%m-%d %H:%M:%S") if ts else "?"
def hm(ts): return datetime.fromtimestamp(ts,EDT).strftime("%H:%M") if ts else "?"
def cat(t):
    for p,c in (("KXATPCHALLENGERMATCH","ATP_CHALL"),("KXWTACHALLENGERMATCH","WTA_CHALL"),("KXATPMATCH","ATP_MAIN"),("KXWTAMATCH","WTA_MAIN"),("KXITFWMATCH","ITF_W"),("KXITFMATCH","ITF_M")):
        if t.startswith(p): return c
    return "OTHER"
def evkey(t): return t.rsplit("-",1)[0]
def leg(t): return t.rsplit("-",1)[1] if "-" in t else t
def opent(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
def findf(dir_,tk):
    for e in (".csv",".csv.gz"):
        if os.path.exists(dir_+"/"+tk+e): return dir_+"/"+tk+e
    return None
def ptape(s):
    try:
        d,t,ap=s.split(" "); Y,Mo,D=d.split("-"); h,mi,se=t.split(":"); h=int(h)
        if ap=="PM" and h!=12: h+=12
        if ap=="AM" and h==12: h=0
        return datetime(int(Y),int(Mo),int(D),h,int(mi),int(se),tzinfo=EDT).timestamp()
    except: return None

# ---- collect per-leg events in window ----
L=defaultdict(lambda: dict(place=[],placed=[],cancel=[],fill=[],exitp=[],exitf=[],settle=None,ws=None,mlive=None,gates=[],skip=Counter()))
for f in LOGS:
    for line in open(f,errors="replace"):
        if '"event"' not in line: continue
        try: e=json.loads(line)
        except: continue
        ts=e.get("ts_epoch")
        if ts is None or ts<START: continue
        tk=e.get("ticker",""); ev=e.get("event"); D=e.get("details",{}) or {}
        if not tk: continue
        d=L[tk]
        if ev=="v4_place": d["place"].append((ts,D.get("target_bid"),D.get("cell"),D.get("entry_mode"),D.get("current_ask"),D.get("runway_status")))
        elif ev=="order_placed" and D.get("action")=="buy": d["placed"].append((ts,D.get("price"),D.get("count"),D.get("response_status")))
        elif ev=="order_cancelled": d["cancel"].append((ts,D.get("label")))
        elif ev in ("entry_filled","completion_fill"): d["fill"].append((ts,D.get("fill_price"),D.get("qty") or D.get("new_fills"),D.get("play_type"),ev))
        elif ev=="v4_exit_posted": d["exitp"].append((ts,D.get("exit_price")))
        elif ev=="exit_filled": d["exitf"].append((ts,D.get("exit_price"),D.get("pnl_dollars")))
        elif ev=="settled": d["settle"]=(D.get("settle"),D.get("pnl_dollars"))
        elif ev=="ws_settled_pre_finalized" and D.get("market_status")=="determined": d["ws"]="determined"
        elif ev in ("match_live_resting_cancel","v4_resting_cancel"): d["mlive"]=ts if d["mlive"] is None else min(d["mlive"],ts)
        elif ev in ("v4_t20m_fallback",): pass
        elif ev=="would_skip_walled_post": d["gates"].append((ts,"would_skip_walled_post"))
        elif ev=="skipped": d["skip"][D.get("reason","")]+=1
        # cancel labels captured in d["cancel"]

# only legs the bot TOUCHED (posted at least once)
legs=[tk for tk,d in L.items() if d["placed"] or d["place"]]

def tape_stats(tk, onset):
    f=findf(TICK,tk)
    if not f: return None
    lts=[]; ticks=[]
    for r in csv.DictReader(opent(f)):
        e=ptape(r["ts_et"])
        if e is None: continue
        def gi(k):
            try: return int(float(r.get(k) or 0))
            except: return 0
        pre = (onset is None) or (e<onset)
        if pre and gi("last_trade")>0: lts.append(gi("last_trade"))
        ticks.append((e,gi("bid_1"),gi("ask_1"),gi("last_trade")))
    ticks.sort()
    return dict(lts=lts,ticks=ticks)
def bidask_at(ticks,t):
    lo=None
    for row in ticks:
        if row[0]<=t: lo=row
        else: break
    return (lo[1],lo[2]) if lo else (None,None)
def dedup_no(tk,ref,onset):
    f=findf(TR,tk)
    if not f: return []
    fil=[]
    for r in csv.reader(opent(f)):
        if not r or r[0]=="ts_et": continue
        e=ptape(r[0])
        if e is None: continue
        try: p=int(float(r[2])); c=int(float(r[3]))
        except: continue
        s=r[4] if len(r)>4 else ""
        if s=="no" and p<=ref+2 and (onset is None or e<onset): fil.append((e,p,c))
    opps=[]; cur=None
    for (e,p,c) in fil:
        if cur and p<=cur["lvl"]+2 and e-cur["t2"]<120: cur["lots"]+=c; cur["t2"]=e; cur["lvl"]=max(cur["lvl"],p); cur["pmin"]=min(cur["pmin"],p)
        else:
            if cur: opps.append(cur)
            cur=dict(t=e,t2=e,lvl=p,pmin=p,lots=c)
    if cur: opps.append(cur)
    return opps

def tercile(fill,lts):
    if not lts or fill is None: return "n/a"
    lo,hi=min(lts),max(lts); rng=hi-lo
    if rng<=0: return "flat"
    if fill< lo+rng/3: return "CHEAP-3rd"
    if fill< lo+2*rng/3: return "mid-3rd"
    return "EXPENSIVE-3rd"

# ---- build output ----
out=[]
def W(s): out.append(s)
W("# OMQS — CURRENT DEPLOY-BOX TRADE REVIEW (player-by-player)\n")
W("**Deploy box:** Jun 30 15:46 ET bisect-flip → Jul 1 18:40 ET (config unchanged across the disk-crash gap + restart — one box). Read-only, assumptions vs tape.\n")
W(f"**Scope:** {len(legs)} legs the bot touched (posted ≥1), across {len(set(evkey(t) for t in legs))} events.\n")

# summary accumulators
summ=dict(filled=0,onesided=0,missedboth=0,terc=Counter(),comb=Counter(),cls=Counter(),gate_players=Counter())
events=defaultdict(list)
for tk in legs: events[evkey(tk)].append(tk)

for ek in sorted(events, key=lambda e:(cat(e+"-X"),e)):
    ls=sorted(events[ek])
    c=cat(ek+"-X")
    W(f"\n## {ek}  [{c}]")
    # onset per event = min mlive across legs, else last tick
    onset=None
    for tk in ls:
        if L[tk]["mlive"]: onset = L[tk]["mlive"] if onset is None else min(onset,L[tk]["mlive"])
    fills_in_event={}
    for tk in ls:
        d=L[tk]; pl=leg(tk)
        ts_stats=tape_stats(tk,onset)
        # timeline
        tlrows=[]
        for (ts,pr,ct,rs) in d["placed"]: tlrows.append((ts,f"post {pr}c x{ct} ({rs})"))
        for (ts,lb) in d["cancel"]: tlrows.append((ts,f"cancel [{lb}]"))
        for (ts,fp,q,pt,ev) in d["fill"]: tlrows.append((ts,f"**FILL {fp}c x{q} {pt}**")); fills_in_event[tk]=fp
        for (ts,xp) in d["exitp"]: tlrows.append((ts,f"exit_post {xp}c"))
        for (ts,xp,pn) in d["exitf"]: tlrows.append((ts,f"exit_fill {xp}c pnl${pn}"))
        tlrows.sort()
        W(f"\n### {pl}  ({tk})")
        W("- **timeline:** "+" | ".join(f"{hm(ts)} {txt}" for ts,txt in tlrows[:24]) if tlrows else "- timeline: (posts only)")
        # entry grade
        asum = d["place"][-1] if d["place"] else None
        tgt = asum[1] if asum else None; cell=asum[2] if asum else None
        fillpx = d["fill"][0][1] if d["fill"] else None
        if ts_stats and ts_stats["lts"]:
            lts=ts_stats["lts"]; tp=f"tape premkt last_trade min/med/max = {min(lts)}/{int(stx.median(lts))}/{max(lts)}c (n={len(lts)})"
            terc=tercile(fillpx,lts) if fillpx is not None else "n/a"
            # bid/ask at first & last post
            ba=[]
            for (ts,pr,ct,rs) in d["placed"][:1]+d["placed"][-1:]:
                b,a=bidask_at(ts_stats["ticks"],ts); ba.append(f"@{hm(ts)} bid{b}/ask{a}")
            baS="; ".join(ba)
        else:
            tp="tape: NO premarket_ticks file"; terc="n/a"; baS="n/a"
        W(f"- **entry grade:** assumption cell={cell} target_bid={tgt}c | {tp} | book-at-post {baS}")
        if fillpx is not None:
            W(f"  → **FILL {fillpx}c**: vs target {tgt} ({'+' if (tgt is not None and fillpx>tgt) else ''}{fillpx-tgt if tgt is not None else '?'}c), tape-position **{terc}**")
            summ["terc"][terc]+=1
        # mechanical
        mech=[]
        for (ts,lb) in d["cancel"]:
            if lb in ("v4_t20m_fallback","no_fallback_fat_spread"):
                lead = (onset-ts)/60.0 if onset else None
                mech.append(f"{lb}@{hm(ts)}"+(f" ({lead:.0f}min before onset)" if lead is not None else ""))
        if d["skip"].get("itf_recent_volume_floor"): mech.append(f"itf_recent_volume_floor x{d['skip']['itf_recent_volume_floor']}")
        if d["skip"].get("maker_only_no_late_entry"): mech.append(f"maker_only_no_late_entry x{d['skip']['maker_only_no_late_entry']}")
        if d["gates"]: mech.append(f"would_skip_walled x{len(d['gates'])}")
        if mech:
            W(f"- **mechanical:** "+" ; ".join(mech))
            for g in ("v4_t20m_fallback","no_fallback_fat_spread","itf_recent_volume_floor","maker_only_no_late_entry"):
                if any(g in m for m in mech): summ["gate_players"][g]+=1
        # outcome
        st=d["settle"]; ws=d["ws"]
        pnl = st[1] if st else (d["exitf"][0][2] if d["exitf"] else None)
        oc = f"settled {st[0]} pnl=${st[1]}" if st else (f"determined (ws), exit_fill pnl=${d['exitf'][0][2]}" if d["exitf"] else (f"determined (ws)" if ws else "OPEN"))
        W(f"- **outcome:** {oc}")
    # pair status
    both=[tk for tk in ls if tk in fills_in_event]
    W(f"\n**PAIR:** posted {len(ls)} legs; filled {len(both)}.")
    if len(both)==2:
        comb=fills_in_event[both[0]]+fills_in_event[both[1]]
        bkt = "<=97" if comb<=97 else ("98-100" if comb<=100 else ">100")
        W(f"  → BOTH FILLED, combined = {fills_in_event[both[0]]}+{fills_in_event[both[1]]} = **{comb}c [{bkt}]**")
        summ["filled"]+=1; summ["comb"][bkt]+=1
    elif len(both)==1:
        kept=both[0]; missed=[tk for tk in ls if tk!=kept]
        summ["onesided"]+=1
        mt = missed[0] if missed else None
        if mt:
            # class of missed: was a bid resting when its catchable dip printed?
            ref=max([p for (ts,p,ct,rs) in L[mt]["placed"]]+[a[1] for a in L[mt]["place"] if a[1] is not None]+[0])
            opps=dedup_no(mt,ref,onset)
            # simple class: any resting bid interval covering first opp?
            iv=[]
            canc={i:None for i in range(len(L[mt]["placed"]))}
            # crude: if no placed -> NEVER_LAID; if placed but all cancelled before first opp -> PULLED; if placed price<opp -> TOO_DEEP
            cls="NEVER_LAID"
            if L[mt]["placed"]:
                maxbid=max(p for (ts,p,ct,rs) in L[mt]["placed"])
                if opps:
                    fp=opps[0]["pmin"]
                    cls = "TOO_DEEP" if maxbid<fp else "PULLED"
                else: cls="NO_OPP"
            summ["cls"][cls]+=1
            oppstr="; ".join(f"{hm(o['t'])} ~{o['pmin']}c x{o['lots']}" for o in opps[:5]) or "none"
            W(f"  → ONE-SIDED. kept={leg(kept)}, missed={leg(mt)} class=**{cls}** | catchable sibling dedup opps: {oppstr}")
    else:
        summ["missedboth"]+=1
        W(f"  → MISSED BOTH (posted, no fill)")

# ---- summary ----
W("\n\n## DEPLOY-BOX SUMMARY")
W(f"- players (legs touched): {len(legs)} | events: {len(events)}")
W(f"- pair outcome: BOTH-filled {summ['filled']} | ONE-sided {summ['onesided']} | MISSED-both {summ['missedboth']}")
W(f"- entry-grade tape position of FILLS: {dict(summ['terc'])}")
W(f"- combined distribution (both-filled pairs): {dict(summ['comb'])}")
W(f"- one-sided miss class: {dict(summ['cls'])}")
W(f"- mechanical gate — players hit: {dict(summ['gate_players'])}")
open("/tmp/OMQS_DEPLOYBOX_CURRENT.md","w").write("\n".join(out))
print("wrote /tmp/OMQS_DEPLOYBOX_CURRENT.md  (%d lines, %d legs)"%(len(out),len(legs)))
print("SUMMARY:", dict(summ["terc"]), dict(summ["comb"]), dict(summ["cls"]), dict(summ["gate_players"]))
print("pair:",summ["filled"],summ["onesided"],summ["missedboth"])
