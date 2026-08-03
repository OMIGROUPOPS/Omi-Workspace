#!/usr/bin/env python3
"""Deterministically rebuild the V11 non-action 896-leg mechanism audit.

Analysis seat only (see docs/research/window1/WINDOW1_TWO_SEAT_BOUNDARY.md).
Read-only on every input.  Writes only under the analysis namespace
`.claude/window1_second_seat/` and this file's own tree.

Inputs (frozen, not owned by this seat):
  - V11 non-action decision trace (gz JSONL, 896 legs), from the live/replay seat.
  - Per-leg Window-1 quote tapes (`*.csv.gz`) from the private evidence bundle.

Outputs (under .claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/):
  - V11_NON_ACTION_MECHANISM_LEDGER_896.csv   one enriched row per leg
  - MECHANISM_SUMMARY.json                     every table, machine-readable
  - AUDIT_RECEIPT.json                         provenance + method + conservation

Method summary
  * Decision instant = the first receipt at which an actionable floor existed
    (first_qualifying_floor_receipt, else the shape-floor-consensus / observed-low
    fallbacks).  The book, both clocks, and the failed-predicate set are read there.
  * Mechanism grouping is by the *binding predicate set at that first actionable
    floor*, mapped to a structural mechanism -- NOT by the pricer's terminal gate
    name.  A leg is "covered" only when every binding predicate maps to one of the
    five already-hand-fixed defects.
  * Ask-return behaviour is measured by scanning each leg's tape from the decision
    epoch to the scheduled-start epoch: a return episode is a contiguous run whose
    top ask is <= the refused floor; episodes >=10s are executable-dwell returns.
  * Frontier = sum of both sides' frozen qualifying_ask_floor_cents, over events
    whose two legs are both in the 896.

Clock convention: t_minus_scheduled_s counts back from the scheduled start;
t_minus_bell_s from the observed bell (valid only where |value| < 1e6 -- challenger
bells are largely unobserved).  ET = UTC-4 (EDT) for the Jul-2026 window.
"""
import argparse, calendar, collections, csv, glob, gzip, hashlib, json, os, statistics as st, time

FIXMAP = {"stable-ask-refused-for-no-transition":1, "floor-on-first-descent":2,
          "stale-action-book":3, "class-cannot-express-member-behaviour":4,
          "verdict-lagging-tape":5}
CATS = ["ATP_CHALL","ATP_MAIN","WTA_MAIN","WTA_CHALL"]
REGS = ["le25","26_50","51_75","ge76"]

# ---------------------------------------------------------------- trace parse
def pick_receipt(dr):
    for k in ("first_qualifying_floor_receipt","first_shape_floor_consensus",
              "first_qualifying_terminal_observed_low_receipt","first_terminal_observed_low_arrival"):
        if dr.get(k): return dr[k]
    return None

def load_legs(trace_gz):
    rows=[]
    with gzip.open(trace_gz,"rt",encoding="utf-8") as f:
        for line in f:
            r=json.loads(line); b=r["baseline_v11"]; dr=b.get("decision_receipt") or {}
            rc=pick_receipt(dr) or {}
            bk=rc.get("book") or {}; pf=rc.get("prefix") or {}; sv=rc.get("shape_verdicts") or []
            qa=dr.get("qualifying_observed_low_receipts_by_price") or {}
            rows.append(dict(
                ticker=r["ticker"], event=r["event_id"], leg=r["leg_identity"].split("|")[-1],
                cat=r["category"], region=r["price_region"], split=r["starting_price_split"],
                terminal=b.get("terminal_reason"), has_receipt=bool(rc),
                floor=b.get("qualifying_ask_floor_cents"), obj_low=b.get("objective_traded_low_cents"),
                close=b.get("own_window1_close_cents"), term_obs_low=dr.get("terminal_observed_low_cents"),
                dec_ep=rc.get("timestamp_epoch"),
                t_sched=rc.get("t_minus_scheduled_seconds"), t_bell=rc.get("t_minus_actual_bell_seconds"),
                bid=bk.get("bid"), ask=bk.get("ask"), last=bk.get("carried_last"), spread=bk.get("spread"),
                dwell=bk.get("ask_dwell_seconds"), top_ask_sz=bk.get("top_ask_size"), top5=bk.get("top5_ask_depth"),
                new_low_desc=pf.get("new_low_descent_count"), distinct_ask=pf.get("distinct_ask_count"),
                n_shapes=len(sv), n_floor=sum(1 for s in sv if s.get("verdict")=="FLOOR"),
                n_lower=sum(1 for s in sv if s.get("verdict")=="LOWER"),
                failed=rc.get("failed_predicates") or [],
                floor_requalified=(b.get("qualifying_ask_floor_cents") is not None
                                   and str(b.get("qualifying_ask_floor_cents")) in qa)))
    return rows

# ---------------------------------------------------------------- mechanisms
def leg_mechanisms(r):
    if not r["has_receipt"]:
        return {("no-formed-book-source-gap", False)}
    out=set(); ns,nf,nl=r["n_shapes"],r["n_floor"],r["n_lower"]
    for p in r["failed"]:
        if   p=="STABLE_SIGNING_SUPPORT_UNPROVEN":                 out.add(("stable-ask-refused-for-no-transition",True))
        elif p=="CURRENT_ASK_ABOVE_OBSERVED_LOW":                  out.add(("verdict-lagging-tape",True))
        elif p in ("NO_FRESH_OWN_BOOK_RECEIPT","OWN_MICRO_POSITION_UNOBSERVED"): out.add(("stale-action-book",True))
        elif p=="SHAPE_VERDICT_STILL_LOWER":                       out.add(("floor-on-first-descent",True))
        elif p=="INVERSE_SIBLING_UNRESOLVED":                      out.add(("synthetic-sibling-veto",False))
        elif p in ("ASK_DWELL_BELOW_10_SECONDS","TOP_ASK_CAPACITY_BELOW_FIVE"): out.add(("microstructure-nonexecutable",False))
        elif p=="SHAPE_VERDICT_NOT_UNANIMOUS_FLOOR":
            if ns==0 or (nf==0 and nl==0): out.add(("class-cannot-express-member-behaviour",True))
            elif nf>=1 and nl>=1:          out.add(("class-splits-floor-vs-lower",False))
            elif nl>=1 and nf==0:          out.add(("floor-on-first-descent",True))
            else:                          out.add(("class-cannot-express-member-behaviour",True))
    return out or {("unclassified-no-predicate",False)}

NEW_PRIO=["synthetic-sibling-veto","class-splits-floor-vs-lower","no-formed-book-source-gap",
          "microstructure-nonexecutable","unclassified-no-predicate"]
COV_PRIO=["verdict-lagging-tape","stable-ask-refused-for-no-transition","floor-on-first-descent",
          "class-cannot-express-member-behaviour","stale-action-book"]
def primary(mechs):
    names={m for m,_ in mechs}
    for m in NEW_PRIO:
        if m in names: return m,False
    for m in COV_PRIO:
        if m in names: return m,True
    return "unclassified",False

# ---------------------------------------------------------------- tape scan
def make_et():
    cache={}
    def et_to_epoch(s):
        e=cache.get(s)
        if e is None:
            e=calendar.timegm(time.strptime(s,"%Y-%m-%d %I:%M:%S %p"))+4*3600
            cache[s]=e
        return e
    return et_to_epoch

def scan_returns(path, dec_ep, sched_ep, floor, et_to_epoch):
    below_start=None; below_last=None; episodes=[]; min_after=None
    with gzip.open(path,"rt") as f:
        f.readline()
        for line in f:
            c=line.split(",")
            try: ep=et_to_epoch(c[0])
            except Exception: continue
            if ep>sched_ep: break
            if ep<=dec_ep: continue
            try: ask=int(c[12])
            except Exception: continue
            if min_after is None or ask<min_after: min_after=ask
            if ask<=floor:
                if below_start is None: below_start=ep
                below_last=ep
            elif below_start is not None:
                episodes.append((below_start,below_last)); below_start=None
    if below_start is not None: episodes.append((below_start,below_last))
    durs=[b-a for a,b in episodes]
    return dict(n_ret_episodes=len(episodes), n_ret_ge10s=sum(1 for d in durs if d>=10),
                total_sec_at_or_below=int(sum(durs)), max_episode_sec=int(max(durs)) if durs else 0,
                min_ask_after=min_after, went_below_floor=(min_after is not None and min_after<floor))

# ---------------------------------------------------------------- summaries
def med(x): return st.median(x) if x else None
def regret(rs):
    fb=[r for r in rs if r["floor"] is not None]
    edges=[r["close"]-r["floor"] for r in fb if r["close"] is not None]
    sc=[r for r in rs if r.get("ret")]
    back=[r for r in sc if r["ret"]["n_ret_ge10s"]>=1]
    lo=[r for r in sc if r["ret"]["went_below_floor"]]
    return dict(n=len(rs), floor_backed=len(fb), floor_median=med([r["floor"] for r in fb]),
        n_floor_le_close=sum(1 for r in fb if r["close"] is not None and r["floor"]<=r["close"]),
        n_floor_le_97=sum(1 for r in fb if r["floor"]<=97),
        edge_vs_close_sum=sum(edges), edge_vs_close_median=med(edges),
        scanned=len(sc), n_refused_floor_returned_ge10s=len(back),
        pct_returned=(round(100*len(back)/len(sc),1) if sc else None),
        return_episodes_median=med([r["ret"]["n_ret_ge10s"] for r in back]),
        total_sec_at_or_below_floor_median=med([r["ret"]["total_sec_at_or_below"] for r in back]),
        max_episode_sec_median=med([r["ret"]["max_episode_sec"] for r in back]),
        n_ask_went_below_floor=len(lo))
def clocks(rs):
    ts=[r["t_sched"] for r in rs if r["t_sched"] is not None]
    tb=[r["t_bell"] for r in rs if r["t_bell"] is not None and abs(r["t_bell"])<1e6]
    return dict(median_t_scheduled_min=(round(med(ts)/60,1) if ts else None),
                bell_observed_n=len(tb), median_t_bell_min=(round(med(tb)/60,1) if tb else None))
def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--trace", required=True, help="V11_NON_ACTION_DECISION_TRACE_896.jsonl.gz")
    ap.add_argument("--ticks", required=True, help="dir of per-leg *.csv.gz quote tapes")
    ap.add_argument("--out",   required=True, help="output dir under .claude/window1_second_seat/")
    a=ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows=load_legs(a.trace)
    ev_sched={}
    for r in rows:
        if r["dec_ep"] and r["t_sched"] is not None:
            ev_sched.setdefault(r["event"], r["dec_ep"]+int(r["t_sched"]))
    et=make_et(); t0=time.time()
    for i,r in enumerate(rows,1):
        for m,c in [(x,y) for x,y in leg_mechanisms(r)]: pass
        mset=leg_mechanisms(r)
        r["new_mechs"]=sorted({x for x,c in mset if not c})
        r["cov_mechs"]=sorted({x for x,c in mset if c})
        r["fully_covered"]=(len(r["new_mechs"])==0)
        r["primary"],r["primary_covered"]=primary(mset)
        r["mset"]=mset
        sched=ev_sched.get(r["event"])
        r["ret"]=None
        if sched and r["dec_ep"] and r["floor"] is not None:
            r["ret"]=scan_returns(os.path.join(a.ticks, r["ticker"]+".csv.gz"),
                                  r["dec_ep"], sched, r["floor"], et)
        if i%100==0: print(f"  {i}/{len(rows)} legs  {time.time()-t0:.0f}s", flush=True)

    # ledger csv
    cols=["ticker","event","leg","cat","region","split","terminal","primary_mechanism","primary_covered",
          "all_mechanisms","new_mechanisms","fully_covered_by_5fixes","floor_cents","own_w1_close_cents",
          "objective_low_cents","term_observed_low_cents","edge_vs_close","dec_book_bid","dec_book_ask",
          "dec_book_last","dec_spread","dec_ask_dwell_s","dec_top_ask_size","dec_top5_ask_depth",
          "new_low_descents","distinct_asks","n_shapes","n_floor_verdicts","n_lower_verdicts",
          "failed_predicates","t_minus_scheduled_s","t_minus_bell_s","bell_observed",
          "ret_episodes_ge10s","ret_total_sec_at_or_below_floor","ret_max_episode_sec",
          "min_ask_after_decision","ask_went_below_floor"]
    with open(os.path.join(a.out,"V11_NON_ACTION_MECHANISM_LEDGER_896.csv"),"w",newline="") as f:
        w=csv.writer(f); w.writerow(cols)
        for r in rows:
            ret=r["ret"] or {}; bell=(r["t_bell"] is not None and abs(r["t_bell"])<1e6)
            edge=(r["close"]-r["floor"]) if (r["close"] is not None and r["floor"] is not None) else ""
            w.writerow([r["ticker"],r["event"],r["leg"],r["cat"],r["region"],r["split"],r["terminal"],
                r["primary"],r["primary_covered"],"|".join(r["cov_mechs"]+r["new_mechs"]),
                "|".join(r["new_mechs"]),r["fully_covered"],r["floor"],r["close"],r["obj_low"],
                r["term_obs_low"],edge,r["bid"],r["ask"],r["last"],r["spread"],r["dwell"],
                r["top_ask_sz"],r["top5"],r["new_low_desc"],r["distinct_ask"],r["n_shapes"],
                r["n_floor"],r["n_lower"],";".join(r["failed"]),r["t_sched"],
                (r["t_bell"] if bell else ""),bell,ret.get("n_ret_ge10s",""),
                ret.get("total_sec_at_or_below",""),ret.get("max_episode_sec",""),
                ret.get("min_ask_after",""),ret.get("went_below_floor","")])

    # summary json
    bym=collections.defaultdict(list); incidence=collections.Counter(); covof={}
    for r in rows:
        bym[r["primary"]].append(r)
        for m,c in r["mset"]: incidence[m]+=1; covof[m]=c
    mechs=[]
    for m in sorted(bym,key=lambda k:-len(bym[k])):
        rs=bym[m]
        mechs.append(dict(mechanism=m, covered_by_hand_fix=covof.get(m,False), hand_fix_id=FIXMAP.get(m),
            incidence_as_binding_constraint=incidence[m], primary_binding_count=len(rs),
            by_category={c:sum(1 for r in rs if r["cat"]==c) for c in CATS},
            by_price_region={rg:sum(1 for r in rs if r["region"]==rg) for rg in REGS},
            regret=regret(rs), clocks=clocks(rs)))
    term=collections.Counter(r["terminal"] for r in rows)
    ct=collections.defaultdict(collections.Counter)
    for r in rows: ct[r["terminal"]][r["primary"]]+=1
    byev=collections.defaultdict(list)
    for r in rows: byev[r["event"]].append(r)
    both=[(ev,v) for ev,v in byev.items() if len(v)==2 and all(x["floor"] is not None for x in v)]
    frontier={"both_legs_known_events":len(both),
              "single_leg_in_896_events":sum(1 for ev,v in byev.items() if len(v)==1),"levels":[]}
    for T,op in [(93,"<="),(95,"<="),(97,"<="),(100,"<")]:
        lim=T-1 if op=="<" else T
        evok=[(ev,v) for ev,v in both if v[0]["floor"]+v[1]["floor"]<=lim]
        legs=[x for ev,v in evok for x in v]
        frontier["levels"].append(dict(threshold=f"{op}{T}",events=len(evok),legs=len(legs),
            by_region={rg:sum(1 for x in legs if x["region"]==rg) for rg in REGS},
            by_category={c:sum(1 for x in legs if x["cat"]==c) for c in CATS}))
    summary=dict(artifact="V11 non-action 896-leg mechanism audit",
        seat="claude-code analysis (codex/window1-analysis-seat)",
        coverage_by_five_hand_fixes=dict(fully_covered=sum(1 for r in rows if r["fully_covered"]),
            residual=sum(1 for r in rows if not r["fully_covered"])),
        mechanisms=mechs, terminal_reason_distribution=dict(term.most_common()),
        terminal_reason_x_primary_mechanism={t:dict(ct[t]) for t in term}, frontier=frontier,
        per_price_region={rg:dict(regret=regret([r for r in rows if r["region"]==rg]),
                                  clocks=clocks([r for r in rows if r["region"]==rg])) for rg in REGS},
        per_category={c:dict(regret=regret([r for r in rows if r["cat"]==c]),
                             clocks=clocks([r for r in rows if r["cat"]==c])) for c in CATS},
        post_refusal_return_overall=regret(rows))
    json.dump(summary, open(os.path.join(a.out,"MECHANISM_SUMMARY.json"),"w"), indent=2)

    ticks=glob.glob(os.path.join(a.ticks,"*.csv.gz"))
    receipt=dict(generated_by=os.path.relpath(__file__).replace("\\","/"),
        source_trace=dict(path=a.trace, sha256=sha256(a.trace), bytes=os.path.getsize(a.trace),
                          decompressed_lines=len(rows)),
        per_leg_tape_source=dict(dir=a.ticks, files=len(ticks),
                                 total_bytes=sum(os.path.getsize(p) for p in ticks)),
        conservation=dict(legs=len(rows), scanned_for_returns=sum(1 for r in rows if r["ret"]),
            source_unavailable_no_book=sum(1 for r in rows if not r["has_receipt"]),
            floor_backed=sum(1 for r in rows if r["floor"] is not None)),
        method="see module docstring", ET_offset_hours=-4)
    json.dump(receipt, open(os.path.join(a.out,"AUDIT_RECEIPT.json"),"w"), indent=2)
    print("done ->", a.out)

if __name__=="__main__":
    main()
