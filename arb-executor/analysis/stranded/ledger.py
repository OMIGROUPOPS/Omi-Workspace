#!/usr/bin/env python3
# ERROR LEDGER (current deploy box, Jun30 15:46 -> now). ENTRY-SIDE ONLY. Read-only.
# 6 categories; per-game dual-anchor timing (scheduled start + true tape onset), letter grade,
# named mechanical error, forfeited $. Rollups: grade dist + error freq x dollar, per cat + total.
# Writes OMQS_ERROR_LEDGER_CURRENT.md.  NB: exits are OUT OF SCOPE (Vault 0A standing order).
import os, csv, glob, gzip, json, statistics as st
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
BASE="/root/Omi-Workspace/arb-executor"; TICK=BASE+"/analysis/premarket_ticks"; TR=BASE+"/analysis/trades"; LOGDIR=BASE+"/logs"
EDT=timezone(timedelta(hours=-4)); UTC=timezone.utc
def ep(y,mo,d,h,mi): return datetime(y,mo,d,h,mi,tzinfo=EDT).timestamp()
START=ep(2026,6,30,15,46)
LOGS=[LOGDIR+"/live_v3_20260630.jsonl",LOGDIR+"/live_v3_20260701.jsonl"]
CAT_ORDER=["ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL","ITF_M","ITF_W"]
BORROW={"ITF_M":"ATP_CHALL","ITF_W":"WTA_CHALL"}
QTY=5
def opent(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
def findf(d,tk):
    for e in (".csv",".csv.gz"):
        if os.path.exists(d+"/"+tk+e): return d+"/"+tk+e
    return None
def cat(t):
    for p,c in (("KXATPCHALLENGERMATCH","ATP_CHALL"),("KXWTACHALLENGERMATCH","WTA_CHALL"),("KXATPMATCH","ATP_MAIN"),("KXWTAMATCH","WTA_MAIN"),("KXITFWMATCH","ITF_W"),("KXITFMATCH","ITF_M")):
        if t.startswith(p): return c
    return "?"
def evkey(t): return t.rsplit("-",1)[0]
def leg(t): return t.rsplit("-",1)[1] if "-" in t else t
def piso(s):
    if not s: return None
    for f in ("%Y-%m-%dT%H:%M:%SZ","%Y-%m-%dT%H:%MZ","%Y-%m-%dT%H:%M:%S%z","%Y-%m-%dT%H:%M%z"):
        try:
            d=datetime.strptime(s,f)
            if d.tzinfo is None: d=d.replace(tzinfo=UTC)
            return d.timestamp()
        except: pass
    return None
def ptape(s):
    try:
        d,t,ap=s.split(" "); Y,Mo,D=d.split("-"); h,mi,se=t.split(":"); h=int(h)
        if ap=="PM" and h!=12: h+=12
        if ap=="AM" and h==12: h=0
        return datetime(int(Y),int(Mo),int(D),h,int(mi),int(se),tzinfo=EDT).timestamp()
    except: return None
def tm(anchor,ts):
    if anchor is None or ts is None: return "n/a"
    d=anchor-ts; sign="-" if d>=0 else "+"; d=abs(int(d))
    h=d//3600; m=(d%3600)//60
    return f"{sign}{h}h{m:02d}m" if h else f"{sign}{m}m"
def hhmm(ts): return datetime.fromtimestamp(ts,EDT).strftime("%H:%M") if ts else "--:--"

# ---------- ingest ----------
L=defaultdict(lambda: dict(place=[],placed=[],cancel=[],fill=None,walk=[],settle=None,skip=Counter()))
SCHED={}   # event -> best scheduled start epoch (latest correction wins)
SGAP_EVENTS=Counter()   # schedule_gap-skipped events (keyed by details.event) -> skip count
for f in LOGS:
    if not os.path.exists(f): continue
    for line in open(f,errors="replace"):
        if '"event"' not in line: continue
        try: e=json.loads(line)
        except: continue
        ts=e.get("ts_epoch"); ev=e.get("event"); D=e.get("details",{}) or {}
        if ev in ("schedule_match","schedule_corrected"):
            evk=D.get("event"); s=piso(D.get("start_time") or D.get("new_start"))
            if evk and s: SCHED[evk]=s   # last write wins (corrections come later in the stream)
            continue
        if ts is None or ts<START: continue
        if ev=="skipped" and D.get("reason")=="schedule_gap" and D.get("event"):
            SGAP_EVENTS[D["event"]]+=1   # schedule_gap logs the event in details.event (ticker often empty)
        tk=e.get("ticker","")
        if not tk: continue
        d=L[tk]
        if ev=="v4_place" and D.get("target_bid") is not None: d["place"].append((ts,int(D["target_bid"])))
        elif ev=="order_placed" and D.get("action")=="buy": d["placed"].append((ts,D.get("price")))
        elif ev=="order_cancelled": d["cancel"].append((ts,D.get("label")))
        elif ev in ("entry_filled","completion_fill") and d["fill"] is None: d["fill"]=(ts,D.get("fill_price"))
        elif ev=="v4_move_repost": d["walk"].append((ts,D.get("new_target")))
        elif ev=="settled": d["settle"]=(D.get("settle"),D.get("pnl_dollars"))
        elif ev=="skipped": d["skip"][D.get("reason","")]+=1

# ---------- tape: ONE pass per tape computes onset + best_fillable + has_book + touch_after ----------
def analyze_tape(tk, target=None, after_ts=None):
    f=findf(TICK,tk)
    if not f: return dict(onset=None,bf=None,book=False,touch=None,found=False)
    op=opent(f); rdr=csv.reader(op); hdr=next(rdr,None)
    if not hdr: return dict(onset=None,bf=None,book=False,touch=None,found=True)
    ix={h:i for i,h in enumerate(hdr)}
    ci=[ix.get(c,-1) for c in ("ts_et","bid_1","ask_1","bid_1_sz","last_trade")]
    def gi(r,j):
        if j<0: return 0
        try: return int(float(r[j] or 0))
        except: return 0
    bf=None; book=False; touch=None
    # streaming per-minute churn for onset (first minute w/ >=6 last_trade transitions followed by >=4)
    onset=None; cur_m=None; cur_first=None; cur_churn=0; prev_first=None; prev_churn=None; prevlt=None
    for r in rdr:
        try: e=ptape(r[ci[0]])
        except: continue
        if e is None: continue
        b=gi(r,ci[1]); a=gi(r,ci[2]); bs=gi(r,ci[3]); lt=gi(r,ci[4])
        if b>0 and a>0: book=True
        if lt>0 and bs>=5 and (bf is None or lt<bf): bf=lt
        if target is not None and after_ts is not None and touch is None and e>=after_ts and ((0<lt<=target) or (0<a<=target)): touch=e
        m=int(e//60)
        if cur_m is None: cur_m=m; cur_first=e; cur_churn=0
        elif m!=cur_m:
            if onset is None and prev_churn is not None and prev_churn>=6 and cur_churn>=4: onset=prev_first
            prev_first,prev_churn=cur_first,cur_churn
            cur_m=m; cur_first=e; cur_churn=0; prevlt=None
        if prevlt is not None and lt!=prevlt and lt>0: cur_churn+=1
        prevlt=lt
    return dict(onset=onset,bf=bf,book=book,touch=touch,found=True)

# ---------- assemble events ----------
# Scope: a REAL POSITION (posted/filled) OR a schedule_gap-skip that actually had a book (tape file exists).
# Excludes the schedule_gap phantom-listing tail (no book, never postable) that inflates to ~548 events.
events_raw=defaultdict(list)
for tk,d in L.items():
    if d["place"] or d["placed"] or d["fill"] or d["skip"]: events_raw[evkey(tk)].append(tk)
def tape_kb(tk):
    f=findf(TICK,tk)
    try: return os.path.getsize(f)/1024.0 if f else 0.0
    except: return 0.0
BOOK_KB=200.0   # a real book-bearing tape
# GRADED rows = actual POSITIONS (posted/filled). schedule_gap skip-census (never posted, book-bearing)
# tallied by category (cheap) and detailed in ITEM 3. SGAP events are keyed by details.event.
events=defaultdict(list)
for ek,legs in events_raw.items():
    if any(L[tk]["place"] or L[tk]["placed"] or L[tk]["fill"] for tk in legs): events[ek]=legs
skip_by_cat=Counter(); skip_events=[]
_evkb=defaultdict(float)   # scan tape dir ONCE: event-prefix -> max leg tape KB
for fn in os.listdir(TICK):
    base=fn.replace(".csv.gz","").replace(".csv","")
    if "-" not in base: continue
    ekp=base.rsplit("-",1)[0]
    try: kb=os.path.getsize(TICK+"/"+fn)/1024.0
    except: kb=0.0
    if kb>_evkb[ekp]: _evkb[ekp]=kb
for ek in SGAP_EVENTS:
    if ek in events: continue   # it became a real position
    if _evkb.get(ek,0.0)>=BOOK_KB:
        skip_by_cat[cat(ek+"-X")]+=1; skip_events.append(ek)
print(f"[scope] {len(events_raw)} raw ticker-events -> {len(events)} GRADED positions; {len(SGAP_EVENTS)} schedule_gap events, {sum(skip_by_cat.values())} of them book-bearing (census -> ITEM 3)")

def errclass(name):   # normalize a per-game primary error to its CLASS (strip cents/timestamps) for the freq table
    n=name
    for pre in ("posted-late/over-fillable","posted +","posted-late","pulled-by-t20m","pulled-by-match-live",
                "blocked-by-volume-floor","target-vs-tape misaligned","schedule_gap-skipped","maker-only-no-late-entry",
                "never-laid","combined","clean","—"):
        if n.startswith(pre):
            if pre=="posted +": return "posted-over-fillable"
            if pre=="combined": return "combined>=100 (locked loss)"
            return pre
    return n.split(" ")[0]

def posts(tk): return sorted([t for (t,_) in L[tk]["placed"]]+[t for (t,_) in L[tk]["place"]])
def first_post(tk):
    p=posts(tk); return p[0] if p else None
def targets(tk): return [pr for (_,pr) in L[tk]["placed"] if pr is not None]+[tg for (_,tg) in L[tk]["place"] if tg is not None]
def fill_ts(tk): return L[tk]["fill"][0] if L[tk]["fill"] else None
def fill_px(tk): return L[tk]["fill"][1] if L[tk]["fill"] else None
def filled(tk): return L[tk]["fill"] is not None

rows_all=[]  # per-event record
import sys as _sys
_EVL=list(events.items())
for _i,(ek,legs) in enumerate(_EVL):
    if _i%20==0: print(f"[progress] event {_i}/{len(_EVL)} {ek[-22:]}",file=_sys.stderr,flush=True)
    c=cat(ek+"-X"); sched=SCHED.get(ek)
    legs=sorted(legs)
    fc=[tk for tk in legs if filled(tk)]
    # ONE tape pass per leg: onset + best_fillable + has_book + touch-after-first-cancel (for pulled-by errors)
    an={}
    for tk in legs:
        tgt=max(targets(tk)+[0]) if targets(tk) else None
        cancel_ts=None
        if not filled(tk):
            for (cts,lb) in sorted(L[tk]["cancel"]):
                if lb in ("v4_t20m_fallback","match_live_cancel","match_live_resting_cancel"): cancel_ts=cts; break
        an[tk]=analyze_tape(tk, tgt, cancel_ts)
    onsets=[an[tk]["onset"] for tk in legs if an[tk]["onset"]]
    onset=min(onsets) if onsets else None
    bf={tk:an[tk]["bf"] for tk in legs}
    postable={tk:an[tk]["book"] for tk in legs}
    rec=dict(event=ek,cat=c,sched=sched,onset=onset,legs=legs,nfill=len(fc))
    # combined + grade
    if len(fc)==2:
        a,b=fc; comb=fill_px(a)+fill_px(b)
        rec["combined"]=comb
        overpay_legs=sum(max(0,(fill_px(tk)-(bf[tk] if bf[tk] is not None else fill_px(tk)))) for tk in fc)
        if comb>=100: grade="C"; dmg=(comb-100)/100.0*QTY; forfeit=f"locked LOSS +{comb-100}c (combined {comb})"
        elif comb<=97: grade="A" if overpay_legs<=2 else "B"; dmg=overpay_legs/100.0*QTY; forfeit=(f"clean lock {comb}" if grade=="A" else f"overpaid {overpay_legs}c vs fillable (comb {comb})")
        else: grade="B"; dmg=overpay_legs/100.0*QTY; forfeit=f"combined {comb} (>97), overpay {overpay_legs}c"
        rec.update(grade=grade,damage=dmg,forfeit=forfeit)
    elif len(fc)==1:
        kept=fc[0]; missed=[tk for tk in legs if tk!=kept][0] if len(legs)>1 else None
        rec["combined"]=None; grade="D"
        ach=None
        if missed is not None and bf.get(missed) is not None:
            ach=fill_px(kept)+bf[missed]
        dmg=max(0.0,(100-ach))/100.0*QTY if (ach is not None and ach<100) else 0.0
        rec.update(grade=grade,kept=leg(kept),missed=(leg(missed) if missed else None),
                   damage=dmg,forfeit=(f"forfeited combined {ach} (missed lock)" if ach is not None else "one-sided; missed leg unfillable/no book"))
    else:
        grade="F"; rec["combined"]=None
        ach=None
        if len(legs)==2 and all(bf.get(tk) is not None for tk in legs): ach=sum(bf[tk] for tk in legs)
        dmg=max(0.0,(100-ach))/100.0*QTY if (ach is not None and ach<100) else 0.0
        rec.update(grade=grade,damage=dmg,forfeit=(f"achievable combined {ach} never captured" if ach is not None else "missed-both / skipped; no book"))
    # ---- named mechanical error (entry-side) ----
    errs=[]
    # schedule_gap skip
    sg=sum(L[tk]["skip"].get("schedule_gap",0) for tk in legs)
    vf=sum(L[tk]["skip"].get("itf_recent_volume_floor",0) for tk in legs)
    ml_block=sum(L[tk]["skip"].get("maker_only_no_late_entry",0) for tk in legs)
    if rec["nfill"]<2:
        # examine the unfilled leg(s)
        for tk in legs:
            if filled(tk): continue
            fp=first_post(tk); tgt=max(targets(tk)+[0]) if targets(tk) else None
            # pulled-by-t20m / match-live: first such cancel + tape touched our level after (single-pass 'touch')
            cancel_first=None
            for (cts,lb) in sorted(L[tk]["cancel"]):
                if lb in ("v4_t20m_fallback","match_live_cancel","match_live_resting_cancel"): cancel_first=(cts,lb); break
            if cancel_first and an[tk]["touch"] is not None:
                cts,lb=cancel_first
                errs.append(f"pulled-by-{'t20m' if 't20m' in lb else 'match-live'} {hhmm(cts)} (tape touched {tgt} at {hhmm(an[tk]['touch'])}) [{leg(tk)}]")
            if not L[tk]["placed"] and not L[tk]["place"]:
                if L[tk]["skip"].get("schedule_gap",0)>0: errs.append(f"schedule_gap-skipped [{leg(tk)}]")
                elif L[tk]["skip"].get("itf_recent_volume_floor",0)>0: errs.append(f"blocked-by-volume-floor x{L[tk]['skip']['itf_recent_volume_floor']} (never posted) [{leg(tk)}]")
                elif L[tk]["skip"].get("maker_only_no_late_entry",0)>0: errs.append(f"maker-only-no-late-entry (re-lay blocked) [{leg(tk)}]")
                else: errs.append(f"never-laid [{leg(tk)}]")
            elif tgt is not None and bf.get(tk) is not None and tgt<bf[tk]:
                errs.append(f"target-vs-tape misaligned {bf[tk]-tgt}c too deep [{leg(tk)}]")
            elif tgt is not None and bf.get(tk) is not None and fp is not None and tgt>bf[tk]+2:
                errs.append(f"posted-late/over-fillable +{tgt-bf[tk]}c [{leg(tk)}]")
    else:
        # both filled but overpaid or >=100
        for tk in fc:
            if bf.get(tk) is not None and fill_px(tk)>bf[tk]+2:
                errs.append(f"posted +{fill_px(tk)-bf[tk]}c over fillable [{leg(tk)}]")
        if rec.get("combined",0) and rec["combined"]>=100:
            errs.append(f"combined {rec['combined']} >=100 (locked loss)")
    # ITF liquidity note
    itf_note=""
    if c in ("ITF_M","ITF_W"):
        nobook=[leg(tk) for tk in legs if not postable.get(tk)]
        if nobook: itf_note=f"ITF no-book: {','.join(nobook)}"
    rec["errors"]=errs; rec["primary"]=(errs[0].split(" [")[0] if errs else ("clean" if grade=="A" else "—"))
    rec["itf_note"]=itf_note; rec["vf"]=vf; rec["sg"]=sg
    # timing strings per leg
    tstr=[]
    for tk in sorted(legs, key=lambda x:-(st.median(targets(x)) if targets(x) else 0)):
        fp=first_post(tk); ft=fill_ts(tk)
        role="fav" if (targets(tk) and st.median(targets(tk))>=50) else "dog"
        s=f"{role}:{leg(tk)} post {tm(sched,fp)}s"
        if ft is not None: s+=f"/fill {tm(sched,ft)}s·{tm(onset,ft)}t @{fill_px(tk)}"
        else: s+="/NO-FILL"
        tstr.append(s)
    rec["timing"]="  ".join(tstr)
    rows_all.append(rec)
    an=None  # release

# ---------- render markdown ----------
GR=["A","B","C","D","F"]
out=[]
out.append("# OMQS — ERROR LEDGER, CURRENT DEPLOY BOX (entry-side only) — 2026-07-02")
out.append("")
out.append(f"**Box:** Jun 30 15:46 ET bisect (`2b23b5d`) → now, full slate. **{len(rows_all)} graded positions** (posted/filled). Read-only. **Exits are OUT OF SCOPE (Vault §0A standing order)** — this ledger grades ENTRIES only.")
out.append("")
out.append(f"**Scope:** {len(events_raw)} raw Kalshi tennis ticker-events in the box → **{len(rows_all)} were actual POSITIONS** (we posted/filled ≥1 leg, graded below). Separately, **{len(SGAP_EVENTS)} events were schedule_gap-skipped** (never resolved by ESPN/Odds), of which **{sum(skip_by_cat.values())} were book-bearing** (substantial tape) — the never-touched slate. Book-bearing schedule_gap-skips by category: "+(", ".join(f"**{k}** {v}" for k,v in sorted(skip_by_cat.items(),key=lambda kv:-kv[1])) or "none")+f". Their achievable-combined census is **ITEM 3's remit** (C-KALSHI-OCC).")
out.append("")
out.append("**Grade rubric:** A = both filled + combined ≤97 + at/near fillable · B = both + <100 · C = both but ≥100 (locked loss) · D = one-sided · F = missed-both/skipped. **Timing:** each leg `post`/`fill` as T-minus vs **sched**uled start (`s`) and **t**rue tape onset (`t`). **best-fillable** = lowest last_trade that printed with size≥5.")
out.append("")
# global rollup first
gd_all=Counter(r["grade"] for r in rows_all)
out.append("## Global grade distribution")
out.append("| A | B | C | D | F | total |")
out.append("|--:|--:|--:|--:|--:|--:|")
out.append("| "+" | ".join(str(gd_all.get(g,0)) for g in GR)+f" | {len(rows_all)} |")
out.append("")
# error freq x dollar (global) — aggregated by error CLASS (cents/timestamps stripped)
def err_rollup(recs):
    agg=defaultdict(lambda:[0,0.0])
    for r in recs:
        k=errclass(r["primary"]); agg[k][0]+=1; agg[k][1]+=r.get("damage",0.0)
    return sorted(agg.items(),key=lambda kv:-kv[1][1])
out.append("## Global error × dollar (primary error CLASS per game, dollar = forfeited lock / overpay / locked-loss)")
out.append("| primary error | count | $ damage |")
out.append("|---|--:|--:|")
for name,(n,d) in err_rollup(rows_all):
    out.append(f"| {name} | {n} | ${d:.2f} |")
out.append(f"| **TOTAL** | **{len(rows_all)}** | **${sum(r.get('damage',0.0) for r in rows_all):.2f}** |")
out.append("")
# per category
for c in CAT_ORDER:
    recs=[r for r in rows_all if r["cat"]==c]
    hdr=f"## {c}"
    if c in BORROW: hdr+=f"  (exits borrow → **{BORROW[c]}**)"
    out.append(hdr)
    if not recs:
        out.append("_no events in box._"); out.append(""); continue
    gd=Counter(r["grade"] for r in recs)
    out.append(f"**{len(recs)} events** — grades: "+" · ".join(f"{g}:{gd.get(g,0)}" for g in GR)+f" · **$ damage ${sum(r.get('damage',0.0) for r in recs):.2f}**")
    out.append("")
    out.append("| grade | event | timing (T-minus: s=sched, t=tape onset) | combined | named error | forfeited / overpay | $ |")
    out.append("|:--:|---|---|:--:|---|---|--:|")
    for r in sorted(recs,key=lambda x:-x.get("damage",0.0)):
        cb=r.get("combined"); cbs=(f"**{cb}**"+("✓≤97" if cb is not None and cb<=97 else ("⚠≥100" if cb is not None and cb>=100 else "")) if cb is not None else "—")
        er="; ".join(r["errors"]) if r["errors"] else ("clean" if r["grade"]=="A" else "—")
        if r["itf_note"]: er+=f"  ·_{r['itf_note']}_"
        out.append(f"| {r['grade']} | {r['event'].split('-',1)[1] if '-' in r['event'] else r['event']} | {r['timing']} | {cbs} | {er} | {r['forfeit']} | ${r.get('damage',0.0):.2f} |")
    out.append("")
    # per-cat error rollup
    out.append(f"**{c} error × dollar:**")
    out.append("| primary error | count | $ |")
    out.append("|---|--:|--:|")
    for name,(n,d) in err_rollup(recs):
        out.append(f"| {name} | {n} | ${d:.2f} |")
    out.append("")

md="\n".join(out)
open("/root/shadow_p4/OMQS_ERROR_LEDGER_CURRENT.md","w").write(md)
json.dump({"rows":rows_all,"sgap":dict(SGAP_EVENTS),"skip_by_cat":dict(skip_by_cat)},
          open("/root/shadow_p4/OMQS_ERROR_LEDGER.json","w"), default=str)
# console summary
print(f"=== ERROR LEDGER built: {len(rows_all)} events ===")
print("grades:",dict(gd_all))
print("by cat:",{c:len([r for r in rows_all if r['cat']==c]) for c in CAT_ORDER})
print(f"total $ damage: ${sum(r.get('damage',0.0) for r in rows_all):.2f}")
print("top errors:")
for name,(n,d) in err_rollup(rows_all)[:8]: print(f"  {name:42s} n={n:3d} ${d:.2f}")
print("wrote /root/shadow_p4/OMQS_ERROR_LEDGER_CURRENT.md")
