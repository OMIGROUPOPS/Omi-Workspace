#!/usr/bin/env python3
import json,statistics as st
from collections import defaultdict
D=json.load(open("on2_dump.json"))
legs=D['legs']; events=D['events']
byev=defaultdict(list)
for l in legs: byev[l['ev']].append(l)
evinfo={e['ev']:e for e in events}

def mins(a,b):
    if a is None or b is None: return None
    try: return (float(a)-float(b))/60.0
    except: return None

def grade_event(ev,ls):
    n=len(ls); cat=ls[0]['cat']
    combined=sum((x['fill'] or 0) for x in ls) if n>=2 else None
    fvs=[x['fv_capture'] for x in ls if x['fv_capture'] is not None]
    pnl=sum(x['pnl'] for x in ls)
    outc=[x['outc'] for x in ls]
    settled_loss=sum(x['pnl'] for x in ls if x['outc'].startswith('settle') and x['pnl']<0)
    deepneg=[x for x in ls if x['fv_capture'] is not None and x['fv_capture']<=-8]
    err=[]; forfeit=0.0; grade='B'
    # timing vs both clocks (use min_before_start captured at place, + gun delta)
    tim=[]
    for x in ls:
        mb=x.get('min_before_start')
        g=mins(x.get('gun_ts'),x.get('fill_ts'))  # minutes gun AFTER fill (+ = filled before gun=good)
        tim.append((x['suf'],mb,g))
    half = (n==1)
    over_par = (combined is not None and combined>100)
    # ---- grade ----
    if half:
        # naked single
        if any(x['outc'].startswith('settle') and x['pnl']<0 for x in ls):
            grade='F'; err.append('half-armed naked single -> settled LOSS'); forfeit=abs(settled_loss)
        elif any(x['outc']=='exit_FILL' for x in ls) and pnl>=0:
            grade='D'; err.append('half-armed naked single (exited green, luck-directional)')
        else:
            grade='D'; err.append('half-armed naked single (open/held)')
    elif over_par and combined>105:
        grade='D'; err.append(f'combined {combined}c >>100 (structurally doomed pair)'); forfeit=combined-100
    elif over_par:
        grade='C'; err.append(f'combined {combined}c >100 (over-par)'); forfeit=combined-100
    elif deepneg:
        grade='C'; err.append(f'{len(deepneg)} leg deep-neg FV ({",".join(str(round(x["fv_capture"]))+"c "+x["suf"] for x in deepneg)}) fragile shape'); forfeit=sum(abs(x['fv_capture']) for x in deepneg)
    elif fvs and all(v<=0 for v in fvs):
        grade='C'; err.append('zero-discount pair (both FV<=0, no dip capture)'); forfeit=sum(abs(v) for v in fvs if v<0)
    else:
        # completed pair, combined<=100, no deep-neg
        if fvs and all(v>=0 for v in fvs) and combined is not None and combined<=100:
            # strong shape
            allgreen = all(x['outc']=='exit_FILL' for x in ls)
            grade='A' if (allgreen or pnl>=0) else 'B'
        else:
            grade='B'
    # settled-loss overrides for pairs (directional hold bleed)
    if not half and settled_loss<-1 and grade in('A','B'):
        grade='C'; err.append(f'directional hold settled -${abs(settled_loss):.2f}'); forfeit=max(forfeit,abs(settled_loss))
    return grade,err,forfeit,combined,fvs,pnl,tim,outc

# ---- build graded ledger ----
graded=[]
for ev,ls in byev.items():
    graded.append((ev,)+grade_event(ev,ls)+ (ls,))
# never-rested-but-intended -> potential F (need intended flag)
order={'A':0,'B':1,'C':2,'D':3,'F':4}
graded.sort(key=lambda g:(g[9][0]['cat'], order[g[1]], g[0]))

print("=== A-F LEDGER (per game, 6 categories) ===")
print(f"{'GAME':38s} {'cat':10s} {'gr':2s} {'nlg':3s} {'comb':>4s} {'FVa':>4s} {'FVb':>4s} {'pnl':>6s}  named_error / forfeit")
gc=defaultdict(lambda:defaultdict(int))
for ev,grade,err,forfeit,combined,fvs,pnl,tim,outc,ls in graded:
    cat=ls[0]['cat']; gc[cat][grade]+=1
    fa=round(fvs[0]) if len(fvs)>0 else '?'; fb=round(fvs[1]) if len(fvs)>1 else '-'
    en=('; '.join(err))[:48] if err else 'clean'
    ff=f"{forfeit:.1f}c" if forfeit else ""
    print(f"{ev.replace('KX','').replace('MATCH',''):38s} {cat:10s} {grade:2s} {len(ls):>3} {str(combined or ''):>4s} {str(fa):>4s} {str(fb):>4s} {pnl:>6.2f}  {en} {ff}")

print("\n=== GRADE DISTRIBUTION BY CATEGORY ===")
print(f"{'cat':10s} {'A':>3}{'B':>3}{'C':>3}{'D':>3}{'F':>3}  total")
tt=defaultdict(int)
for cat in sorted(gc):
    r=gc[cat]; n=sum(r.values())
    for k in r: tt[k]+=r[k]
    print(f"{cat:10s} {r['A']:>3}{r['B']:>3}{r['C']:>3}{r['D']:>3}{r['F']:>3}  {n}")
print(f"{'TOTAL':10s} {tt['A']:>3}{tt['B']:>3}{tt['C']:>3}{tt['D']:>3}{tt['F']:>3}  {sum(tt.values())}")

print("\n=== BELOW-B MECHANICAL CHAINS (every C/D/F, one line) ===")
# classify named-error DOMAIN (which flag owns it, or NEW class)
def domain(grade,err,combined,ls,rested):
    e=(err[0] if err else '')
    if 'directional hold' in e: return 'exit-harvest FUCKUP-3 (NOT a participation flag)'
    if 'over-par' in e or 'doomed' in e: return 'combined>100 over-par (per_side/entry-pricing leak)'
    if 'deep-neg' in e: return 'fragile leg (bought above tape onset)'
    if 'zero-discount' in e: return 'zero-discount (per_side domain)'
    if 'half-armed' in e:
        return 'half-armed: STARVATION (sib rested,unfilled)' if rested>=2 else 'half-armed: PAIRING (sib never rested)'
    return 'unclassified'
dom_ct=defaultdict(lambda:[0,0.0])
for ev,grade,err,forfeit,combined,fvs,pnl,tim,outc,ls in graded:
    if grade in('A','B'): continue
    cat=ls[0]['cat']; rested=evinfo.get(ev,{}).get('rested',0)
    dm=domain(grade,err,combined,ls,rested)
    dom_ct[dm][0]+=1; dom_ct[dm][1]+=pnl
    legdesc=[]
    for x in ls:
        g_after_fill = (float(x['gun_ts'])-float(x['fill_ts']))/60.0 if (x.get('gun_ts') and x.get('fill_ts')) else None
        gt = f"gun{'+' if (g_after_fill and g_after_fill>=0) else ''}{g_after_fill:.0f}m" if g_after_fill is not None else "gun?"
        mb=x.get('min_before_start'); mbs=f"T-{mb:.0f}" if isinstance(mb,(int,float)) else "T?"
        legdesc.append(f"{x['suf']}:{x['dir'] or '?'} fill{x['fill']}c FV{round(x['fv_capture']) if x['fv_capture'] is not None else '?'} place@{mbs} {gt} src={x.get('ref_src')} {x['outc']} ${x['pnl']:.2f}")
    print(f"[{grade}] {ev.replace('KX','').replace('MATCH','')} ({cat}) sib_rested={rested} forfeit~{forfeit:.1f}c pnl${pnl:.2f} | DOMAIN: {dm}")
    for ld in legdesc: print(f"      {ld}")

print("\n=== NAMED-ERROR DOMAIN ROLLUP (below-B) ===")
for dm,(n,p) in sorted(dom_ct.items(),key=lambda x:-x[1][0]):
    print(f"  {n:>3} games  ${p:>7.2f}  {dm}")

print("\n=== ENTRY TIMING vs BOTH CLOCKS (filled legs) ===")
before_sched=before_gun=after_gun=n=0
for l in legs:
    mb=l.get('min_before_start')
    if isinstance(mb,(int,float)):
        n+=1
        if mb>0: before_sched+=1
    if l.get('gun_ts') and l.get('fill_ts'):
        d=(float(l['gun_ts'])-float(l['fill_ts']))/60.0
        if d>=0: before_gun+=1
        else: after_gun+=1
print(f"  filled legs with place-clock: {n} | placed BEFORE scheduled start: {before_sched}")
print(f"  fills BEFORE tape gun (disciplined premarket): {before_gun} | AT/AFTER gun (chase): {after_gun}")
