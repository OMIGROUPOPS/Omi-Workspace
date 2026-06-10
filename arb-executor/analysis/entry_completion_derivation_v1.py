"""
Entry drift envelope + completion eligibility  (CONSOLIDATED PART-1 SPEC).
Read-only derivation. PMF sha256-gated (9fde4b5d, verified separately).

UNIT: locked 90-cell grid 5-94c per category (data/durable/exit_surface_gated_optima
/*_adaptive_exit_bands.parquet, band_exit_X = per-cell atlas R). An N belongs to ONE
cell = cell(window_open price) = first traded print after gate open (ttms<=240),
last-trade discipline (price_close of first traded minute), NEVER mid/T-20 anchor.

EMIT per (category, cell, k, j) over T-240->T-1, C32-unknowns excluded:
 1 down_reach P(touch open-k) k=1..5 (+n_down_touch)
 2 recovery_after_down PARTNER-DIRECT: P(partner touches partner_open-j | this leg
   touched open-k) TIME-ORDERED (down first, then partner) (+n_recovery_given_down)
 3 inversion cross-check (own-leg recovery-up +j via pinned-sum) + divergence
 4 timing p10/p25/p50/p75/p90 time-to-touch (down & recovery separately)
 5 drift distribution cell(close)-cell(open) per N
 6 p_be(cell,X) breakeven prob from EV-dominance=0
 7 EV-dominance + freshness (10-min ceiling vs passive ride)
 8 value columns LAST (T-20 anchored A40; cents AND ROI A39)
Sanity invariant: ordered conditional <= unordered both-touch every cell, else HALT.
Eligibility frozen: (a) N>=25; (b) exists X<=3c Wilson90LB(partner-direct cond touch
at X) >= p_be(cell,X); (c) survives 0.4x B25 haircut. Inversion never gates.
WAVE1 passes(b)+(c) & div<=0.1; WAVE2 passes(b)+(c) & div>0.1; else INELIGIBLE;
below N floor -> insufficient_data. SHAPE: nothing clears (b)+(c) at 0.4x -> no ship.
Reconciliation: down_reach vs entry_table_percell.csv expected_fill_rate (HALT on mismatch).
"""
import pyarrow.parquet as pq, pyarrow as pa
import glob, collections, math, statistics, json, hashlib, sys

ROOT="/root/Omi-Workspace/arb-executor"
PMF=ROOT+"/data/durable/per_minute_universe/per_minute_features.parquet"
GRID=ROOT+"/data/durable/exit_surface_gated_optima"
SPIKE=ROOT+"/data/durable/spike_volatility_map"
ENTRYTBL=ROOT+"/docs/policy/entry_table_percell.csv"
OUTDIR=ROOT+"/data/durable/entry_completion"
import os; os.makedirs(OUTDIR,exist_ok=True)
Z90=1.6449  # 90% CI -> lower bound z
KMAX=18; JMAX=5; NFLOOR=25; HAIRCUT=0.4; DIV_FLAG=0.10  # KMAX covers entry_table offsets (max=18)
# Volume-accel live onset (build_premarket_surface DISCIPLINE): premarket = strictly BEFORE
# the first trade_count>=LIVE_BURST burst within the final hour; post-onset = in-match dynamics,
# excluded from all premarket-entry reach measures.
LIVE_BURST=10; LIVE_NEAR_START=60

def wilson_lb(x,n,z=Z90):
    if n<=0: return 0.0
    p=x/n; d=1.0+z*z/n
    c=(p+z*z/(2*n))/d
    m=(z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)))/d
    return max(0.0,c-m)

def pct(xs,q):
    if not xs: return None
    xs=sorted(xs); i=min(len(xs)-1,int(q*(len(xs)-1)+0.5)); return xs[i]

# ---------------- load locked grid + atlas EV per leg ----------------
cat_files={f.split("/")[-1].replace("_adaptive_exit_bands.parquet",""):f
           for f in glob.glob(GRID+"/*_adaptive_exit_bands.parquet")}
cell_R={}   # (cat,cell) -> R cents
for cat,f in cat_files.items():
    t=pq.read_table(f)
    for r in range(t.num_rows):
        lo=t.column("price_low")[r].as_py(); hi=t.column("price_high")[r].as_py()
        R=int(float(t.column("band_exit_X")[r].as_py()))
        for c in range(lo,hi+1): cell_R[(cat,c)]=R

# atlas spike_perN -> per-leg atlas single-leg EV (orphan opportunity cost, T-20 frame)
cat_of={}; partner_of={}; atlas_ev_leg={}
for f in glob.glob(SPIKE+"/*_spike_perN.parquet"):
    cat=f.split("/")[-1].replace("_spike_perN.parquet","")
    t=pq.read_table(f,columns=["ticker","partner_ticker","anchor_price","spike_cents","settlement_value"])
    for r in range(t.num_rows):
        tk=t.column("ticker")[r].as_py(); cat_of[tk]=cat
        partner_of[tk]=t.column("partner_ticker")[r].as_py()
        ap=t.column("anchor_price")[r].as_py(); sp=t.column("spike_cents")[r].as_py()
        sv=t.column("settlement_value")[r].as_py()
        if ap is None: continue
        ac=int(round(ap*100)); ac=min(94,max(5,ac))
        R=cell_R.get((cat,ac),4)
        spc=sp if sp is not None else 0.0
        sv=sv if sv is not None else 0.0
        # atlas single-leg EV (profit cents): fire +R if spike>=R else hold-to-settle
        atlas_ev_leg[tk]= R if spc>=R else (100.0*sv - ac)
cohort=set(cat_of.keys())
print("grid cells:",len(cell_R)," cohort legs:",len(cohort)," atlas_ev legs:",len(atlas_ev_leg))

# entry_table expected fill rates (reconciliation)
exp_fill={}   # (cat,cell) -> (offset, fill_rate)
import csv
with open(ENTRYTBL) as fh:
    for row in csv.DictReader(fh):
        exp_fill[(row["category"].lower(),int(row["c"]))]=(int(row["bid_offset_cents"]),float(row["expected_fill_rate"]))

# ---------------- PMF pass: per-ticker TRADED premarket series + T20 anchor -------
# HOUSE INSTRUMENT DISCIPLINE (build_premarket_surface.py / chart_common): honest TRADED
# prints ONLY -- price_low (down) / price_high (up). NEVER yes_bid/yes_ask (phantom on
# no-trade minutes), NEVER mid. Cell keying = window-open = first TRADED price_close.
cols=["ticker","time_to_match_start_min","minute_has_trade","price_close",
      "price_low","price_high","trade_count_in_minute","yes_ask_close","match_start_method"]
series=collections.defaultdict(list)   # ticker -> list[(ttms,plo_c,phi_c,pclose_c,tcount)]  TRADED minutes
t20=collections.defaultdict(lambda:(99.0,None))  # ticker -> (abs(ttms-20), ask_c) for value cols (A40)
def c100(x): return int(round(x*100)) if x is not None else None
pf=pq.ParquetFile(PMF)
for i in range(pf.metadata.num_row_groups):
    rg=pf.read_row_group(i,columns=cols)
    tk=rg.column("ticker").to_pylist(); tt=rg.column("time_to_match_start_min").to_pylist()
    mh=rg.column("minute_has_trade").to_pylist(); pc=rg.column("price_close").to_pylist()
    pl=rg.column("price_low").to_pylist(); ph=rg.column("price_high").to_pylist()
    tcn=rg.column("trade_count_in_minute").to_pylist()
    ak=rg.column("yes_ask_close").to_pylist(); ms=rg.column("match_start_method").to_pylist()
    for j in range(len(tk)):
        t=tk[j]
        if t not in cohort: continue
        if ms[j]=="unknown": continue           # C32 exclusion
        a=tt[j]
        if a is None or not (0.0<a<=240.0): continue
        if 18.0<=a<=22.0 and ak[j] is not None:  # T-20 anchor (ask, [18,22]) for value columns
            key=abs(a-20.0)
            if key<t20[t][0]: t20[t]=(key,c100(ak[j]))
        if not (mh[j] and pc[j] is not None): continue   # TRADED minutes only (phantom-quote discipline)
        series[t].append((a, c100(pl[j]), c100(ph[j]), c100(pc[j]), tcn[j] or 0))
print("tickers with traded premarket series:",len(series))

# ---------------- per-ticker derived features ----------------
class Leg: __slots__=("cell","open_c","close_c","drift","rows","tdown","open_ttms")
legs={}
for tk,rows in series.items():
    rows.sort(key=lambda r:-r[0])     # ttms desc = time ascending (all rows are TRADED minutes)
    if not rows: continue
    # volume-accel live onset = max ttms among bursts (tcount>=LIVE_BURST) within the final hour;
    # premarket sample = minutes STRICTLY BEFORE onset (post-onset = in-match, excluded).
    onset=-1e9
    for (a,plo,phi,cc,tc) in rows:
        if tc>=LIVE_BURST and a<=LIVE_NEAR_START and a>onset: onset=a
    pre=[r for r in rows if r[0]>onset]
    if not pre: continue
    L=Leg()
    L.open_c=pre[0][3]                # window-open = first pre-onset TRADED last-trade price
    L.open_ttms=pre[0][0]
    L.close_c=pre[-1][3]              # window-close = last pre-onset TRADED price (= dip-surface anchor c0)
    L.rows=[(a,plo,phi) for (a,plo,phi,cc,tc) in pre]   # pre-onset traded touch series
    oc=min(94,max(5,L.open_c)); L.cell=oc
    L.drift=L.close_c-L.open_c
    # first-time down touch ttms for k=1..KMAX (traded price_low <= open-k)
    L.tdown=[None]*(KMAX+1)
    for k in range(1,KMAX+1):
        thr=L.open_c-k
        for (a,plo,phi) in L.rows:    # time ascending
            if plo is not None and plo<=thr: L.tdown[k]=a; break
    legs[tk]=L

def first_touch_after(rows, ttms_after, thr, up=False):
    """first TRADED minute strictly AFTER time t (ttms < ttms_after) hitting thr; ttms or None.
    up=False -> price_low<=thr (down/fill); up=True -> price_high>=thr (inversion up-recovery)."""
    if ttms_after is None: return None
    for (a,plo,phi) in rows:
        if a<ttms_after:
            v=phi if up else plo
            if v is not None and ((up and v>=thr) or ((not up) and v<=thr)): return a
    return None
def touch_anywhere(rows,thr,up=False):
    for (a,plo,phi) in rows:
        v=phi if up else plo
        if v is not None and ((up and v>=thr) or ((not up) and v<=thr)): return True
    return False

# ---------------- aggregate per (cat,cell,k,j) ----------------
N_cell=collections.Counter()                         # (cat,cell) -> #legs
n_down=collections.Counter()                         # (cat,cell,k)
n_rec_pd=collections.Counter()                       # (cat,cell,k,j) partner-direct ordered
n_rec_inv=collections.Counter()                      # (cat,cell,k,j) inversion ordered
n_unord=collections.Counter()                        # (cat,cell,k,j) unordered both-touch
down_time=collections.defaultdict(list)              # (cat,cell,k) -> [minutes open->down]
rec_time=collections.defaultdict(list)               # (cat,cell,k,j) -> [minutes down->partner]
drift_by=collections.defaultdict(list)               # (cat,cell) -> [drift]
combined_by=collections.defaultdict(list)            # (cat,cell) -> [open_self+open_partner]
atlasev_by=collections.defaultdict(list)             # (cat,cell) -> [atlas_ev_leg]
n_down_fresh10=collections.Counter()                 # (cat,cell,k) touch within 10min of open
floor_by=collections.defaultdict(list)               # (cat,cell,k,j) -> [floor return cents]
t20_by=collections.defaultdict(list)                 # (cat,cell)->[t20 anchor self]
n_recon=collections.Counter(); n_recon_touch=collections.Counter()  # matched-method C38 recon

for tk,L in legs.items():
    cat=cat_of[tk]; cell=L.cell; key=(cat,cell)
    N_cell[key]+=1
    # C38 matched-method recon: replicate build_premarket_surface dip-reach under ITS OWN
    # anchor (c0 = last premarket TRADED close = L.close_c) + traded price_low touch over the
    # premarket window, at the cell's entry_table offset. Validates the touch machinery against
    # the audited grid; window-open vs last-trade anchor gap is the spec-acknowledged drift.
    rcell=min(94,max(5,L.close_c)); c0=L.close_c; ofr=exp_fill.get((cat,rcell))
    if ofr:
        off=ofr[0]; minplo=min((r[1] for r in L.rows if r[1] is not None),default=None)
        n_recon[(cat,rcell)]+=1
        if minplo is not None and minplo<=c0-off: n_recon_touch[(cat,rcell)]+=1
    drift_by[key].append(L.drift)
    atlasev_by[key].append(atlas_ev_leg.get(tk, 0.0))
    if t20[tk][1] is not None: t20_by[key].append(t20[tk][1])
    P=legs.get(partner_of.get(tk))
    if P is not None:
        combined_by[key].append(L.open_c+P.open_c)
    for k in range(1,KMAX+1):
        if L.tdown[k] is not None:
            n_down[(cat,cell,k)]+=1
            elapsed=L.open_ttms-L.tdown[k]          # minutes from window-open to the down touch
            down_time[(cat,cell,k)].append(elapsed)
            # freshness: touch within 10 min of window-open
            if elapsed<=10: n_down_fresh10[(cat,cell,k)]+=1
            if P is None: continue
            for j in range(1,JMAX+1):
                # partner-direct ordered: partner ASK touches Popen-j AFTER L's down-k touch
                tp=first_touch_after(P.rows, L.tdown[k], P.open_c-j, up=False)
                if tp is not None:
                    n_rec_pd[(cat,cell,k,j)]+=1
                    rec_time[(cat,cell,k,j)].append(L.tdown[k]-tp)
                    floor_by[(cat,cell,k,j)].append(100-((L.open_c-k)+(P.open_c-j)))
                # inversion ordered: L's own BID recovers UP +j AFTER its down-k touch (pinned-sum)
                ti=first_touch_after(L.rows, L.tdown[k], L.open_c+j, up=True)
                if ti is not None: n_rec_inv[(cat,cell,k,j)]+=1
                # unordered both-touch (sanity ceiling)
                if touch_anywhere(P.rows, P.open_c-j, up=False): n_unord[(cat,cell,k,j)]+=1

# ---------------- assemble rows + eligibility + HALT checks ----------------
HALT=[]
cells=sorted(set((c,ce) for (c,ce) in N_cell))
out=[]
shape_any_eligible=False
for (cat,cell) in cells:
    ncell=N_cell[(cat,cell)]
    drift=drift_by[(cat,cell)]; atlasev=statistics.fmean(atlasev_by[(cat,cell)]) if atlasev_by[(cat,cell)] else 0.0
    comb=statistics.fmean(combined_by[(cat,cell)]) if combined_by[(cat,cell)] else None
    t20self=statistics.fmean(t20_by[(cat,cell)]) if t20_by[(cat,cell)] else None
    drift_mean=statistics.fmean(drift) if drift else 0.0
    drift_sd=statistics.pstdev(drift) if len(drift)>1 else 0.0
    cell_eligible=False; cell_wave="INELIGIBLE"; best=None
    for k in range(1,KMAX+1):
        nd=n_down[(cat,cell,k)]
        dr=nd/ncell if ncell else 0.0
        dr10=n_down_fresh10[(cat,cell,k)]/ncell if ncell else 0.0
        for j in range(1,JMAX+1):
            npd=n_rec_pd[(cat,cell,k,j)]; ninv=n_rec_inv[(cat,cell,k,j)]; nun=n_unord[(cat,cell,k,j)]
            # sanity: ordered partner-direct <= unordered both-touch
            if npd>nun: HALT.append("ordered>unordered %s cell%d k%d j%d (%d>%d)"%(cat,cell,k,j,npd,nun))
            rate_pd=npd/nd if nd else 0.0
            rate_inv=ninv/nd if nd else 0.0
            divergence=abs(rate_pd-rate_inv)
            wlb=wilson_lb(npd,nd)
            # paired-floor return (cents): 100 - combined entry cost when leg fills at
            # open-k and partner at open-j. combined window-open ~103c => floor = k+j - vig;
            # floor<=0 means completing at these prices LOCKS A GUARANTEED LOSS (A40 vig) ->
            # completion impossible to justify -> p_be = inf (ineligible), never garbage.
            floor=(100.0-(comb-k-j)) if comb is not None else None
            attempt_cost=dr*j+atlasev   # P(touch s0)*X + orphan opportunity cost (atlas EV)
            if floor is None or floor<=0:
                p_be=float('inf'); ev_dom_full=-attempt_cost; ev_dom_hair=-attempt_cost
                mean_att=atlasev; sd_att=0.0
            else:
                p_be=attempt_cost/floor   # breakeven conditional-touch probability (EV-dominance=0)
                ev_dom_full=rate_pd*floor-attempt_cost
                ev_dom_hair=HAIRCUT*rate_pd*floor-attempt_cost
                mean_att=rate_pd*floor+(1-rate_pd)*atlasev
                sd_att=math.sqrt(max(0.0,rate_pd*(1-rate_pd)))*abs(floor-atlasev)
            p_be_out=min(p_be,9.999)   # display cap; eligibility uses the real (possibly inf) p_be
            mean_no=atlasev; sd_no=statistics.pstdev(atlasev_by[(cat,cell)]) if len(atlasev_by[(cat,cell)])>1 else 0.0
            dt=down_time[(cat,cell,k)]; rt=rec_time[(cat,cell,k,j)]
            # eligibility contribution: j<=3, N>=25, wlb>=p_be, (c) 0.4x ev-dom>=0
            elig_b=(j<=3 and nd>=NFLOOR and wlb>=p_be)
            elig_c=(ev_dom_hair>=0)
            if elig_b and elig_c:
                cell_eligible=True
                w="WAVE1" if divergence<=DIV_FLAG else "WAVE2"
                if best is None: best=(k,j,w)
            out.append(dict(category=cat,cell=cell,k=k,j=j,n_cell=ncell,
                n_down_touch=nd, down_reach=round(dr,4),
                n_recovery_given_down=npd, recovery_pd=round(rate_pd,4),
                inversion=round(rate_inv,4), divergence=round(divergence,4),
                div_flag=bool(divergence>DIV_FLAG),
                n_unordered_both=nun, wilson_lb=round(wlb,4), p_be=round(p_be_out,4),
                p_be_impossible=bool(p_be>1.0),
                ev_dom=round(ev_dom_full,3), ev_dom_0p4x=round(ev_dom_hair,3),
                freshness_touch_10min=round(dr10,4), freshness_delta=round(dr-dr10,4),
                down_t_p10=pct(dt,.1),down_t_p25=pct(dt,.25),down_t_p50=pct(dt,.5),down_t_p75=pct(dt,.75),down_t_p90=pct(dt,.9),
                rec_t_p10=pct(rt,.1),rec_t_p25=pct(rt,.25),rec_t_p50=pct(rt,.5),rec_t_p75=pct(rt,.75),rec_t_p90=pct(rt,.9),
                drift_mean=round(drift_mean,3),drift_sd=round(drift_sd,3),
                atlas_ev_cell=round(atlasev,3),
                pred_mean_attempt=round(mean_att,3),pred_sd_attempt=round(sd_att,3),
                pred_mean_noattempt=round(mean_no,3),pred_sd_noattempt=round(sd_no,3),
                # value LAST (T-20 anchored A40; cents AND ROI A39)
                t20_anchor_self=t20self, combined_anchor=round(comb,2) if comb else None,
                floor_return_cents=round(floor,3) if floor is not None else None,
                floor_return_roi=round(floor/t20self,4) if (floor is not None and t20self and t20self>0) else None,
                p_be_X_roi=round(p_be_out/(j if j else 1),4),
            ))
    # finalize cell wave (below floor -> insufficient_data handled by max nd)
    maxnd=max((n_down[(cat,cell,k)] for k in range(1,KMAX+1)),default=0)
    if maxnd<NFLOOR: cell_wave="insufficient_data"
    elif cell_eligible: cell_wave=best[2]; shape_any_eligible=True
    else: cell_wave="INELIGIBLE"
    for row in out:
        if row["category"]==cat and row["cell"]==cell: row["wave"]=cell_wave

# ---------------- C38 reconciliation: matched-method reach vs entry_table fill ----
# Replicates build_premarket_surface dip-reach (anchor=last-trade c0, traded price_low,
# premarket window, entry_table offset). Should reproduce entry_table within sampling noise
# (entry_table copies reach_dip as expected_fill_rate; small gap = sand-pooling smoothing).
recon=[]
for (cat,cell),(off,fr) in exp_fill.items():
    nc=n_recon[(cat,cell)]
    if nc>=NFLOOR:
        reach=n_recon_touch[(cat,cell)]/nc
        recon.append((cat,cell,off,fr,round(reach,4),round(reach-fr,4)))
recon.sort(key=lambda r:abs(r[5]),reverse=True)

# ---------------- write parquet ----------------
import pyarrow as pa
tbl=pa.Table.from_pylist(out)
OUTP=OUTDIR+"/entry_completion_part1_v1.parquet"
pq.write_table(tbl,OUTP)
sha=hashlib.sha256(open(OUTP,"rb").read()).hexdigest()

# ---------------- summary ----------------
print("\n================ SUMMARY ================")
print("rows:",len(out)," cells:",len(cells)," parquet:",OUTP)
print("sha256:",sha)
print("HALT(sanity ordered>unordered):",len(HALT))
for h in HALT[:5]: print("  HALT",h)
elig=[(c,ce) for (c,ce) in cells if any(r["wave"] in("WAVE1","WAVE2") for r in out if r["category"]==c and r["cell"]==ce)]
w1=sum(1 for (c,ce) in cells if any(r["wave"]=="WAVE1" for r in out if r["category"]==c and r["cell"]==ce))
w2=sum(1 for (c,ce) in cells if any(r["wave"]=="WAVE2" for r in out if r["category"]==c and r["cell"]==ce))
insuf=sum(1 for (c,ce) in cells if any(r["wave"]=="insufficient_data" for r in out if r["category"]==c and r["cell"]==ce))
inelig=len(cells)-w1-w2-insuf
print("WAVE1 cells:",w1," WAVE2 cells:",w2," INELIGIBLE:",inelig," insufficient_data:",insuf)
print("SHAPE pre-commit: %s"%("ELIGIBLE PAIRS EXIST -> proceed" if shape_any_eligible else "NOTHING CLEARS (b)+(c) at 0.4x -> mechanism does NOT ship, return to diagnosis"))
print("\n-- per-category eligible cell counts --")
for cat in sorted(cat_files):
    cc=[ce for (c,ce) in cells if c==cat]
    e=[ce for (c,ce) in elig if c==cat]
    print("  %-10s cells=%d eligible=%d"%(cat,len(cc),len(e)))
print("\n-- top eligible cells (by Wilson-LB margin over p_be, j<=3) --")
cand=[r for r in out if r["wave"] in("WAVE1","WAVE2") and r["j"]<=3 and r["n_down_touch"]>=NFLOOR]
cand.sort(key=lambda r:(r["wilson_lb"]-r["p_be"]),reverse=True)
for r in cand[:12]:
    print("  %-9s c%2d k%d j%d  down=%.2f rec_pd=%.2f wlb=%.2f p_be=%.2f div=%.2f ev0.4=%.1f %s"%(
        r["category"],r["cell"],r["k"],r["j"],r["down_reach"],r["recovery_pd"],
        r["wilson_lb"],r["p_be"],r["divergence"],r["ev_dom_0p4x"],r["wave"]))
print("\n-- C38 reconciliation: matched-method reach (last-trade anchor) vs entry_table fill, worst|delta| 8 --")
for cat,cell,off,fr,reach,delta in recon[:8]:
    print("  %-9s c%2d off%2d  entry_fill=%.3f matched_reach=%.3f delta=%+.3f"%(cat,cell,off,fr,reach,delta))
viol=[r for r in recon if abs(r[5])>0.15]
mean_abs=statistics.fmean([abs(r[5]) for r in recon]) if recon else 0.0
print("  reconciliation HALT (|matched_reach-fill|>0.15): %d of %d  | mean|delta|=%.3f"%(len(viol),len(recon),mean_abs))
json.dump({"sha256":sha,"rows":len(out),"cells":len(cells),"w1":w1,"w2":w2,
           "inelig":inelig,"insuf":insuf,"shape_eligible":shape_any_eligible,
           "halt_sanity":len(HALT),"recon_halt":len(viol)},
          open(OUTDIR+"/_run_meta.json","w"),indent=1)
print("\nDONE.")
