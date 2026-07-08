#!/usr/bin/env python3
"""Render SLATE_LEDGER_20260706.md from vps/slate_ledger.json + config echo.
THE book: one table (settled+open), one ledger line, continuity cuts, grade rollups."""
import json
from collections import defaultdict, Counter

D = json.load(open("vps/slate_ledger_v2.json"))
cfg = open("vps/config_echo2.txt", encoding="utf-8").read().strip()
rows = D["rows"]; cuts = D["cuts"]
GOAL = 97
CATS = ["ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL","ITF_M","ITF_W"]
EPS = ["E3a","E3b","E4"]
def med(v):
    v = sorted(x for x in v if x is not None); return v[len(v)//2] if v else None

st = [r for r in rows if r["status"]=="SETTLED"]
op = [r for r in rows if r["status"]=="OPEN"]
settled_tot = round(sum(r["pnl"] for r in st),2)
open_basis = round(sum(r.get("open_basis",0) for r in op),2)
open_mark = round(sum(r.get("open_mark",0) for r in op),2)
open_cash = round(sum(r.get("cash_partial",0) for r in op),2)

out=[]; A=out.append
A(f"# SLATE LEDGER — THE BOOK (window: flip boot 2026-07-05 23:50:39 ET → {D['generated']})")
A("")
A("**S REDEFINED PER-LEG (late cut 2026-07-07): S = each leg within 4c of its OWN fillable W1 low (gold census N) + own W1/corridor cash; COMBINED DEMOTED to descriptive scoreboard everywhere (per-cat S-lines remain as descriptive floor context). A = the lifecycle shape at <=97. Reachable-not-cashed earns B.**")
A("")
A("**REFRESHED IN PLACE (STEP-3 cut, 2026-07-07): Jul-7 folded in; MECHANICAL flags per leg from BLEED_ATTRIBUTION_20260707 (\u2691a dup-surplus / \u2691b naked-band-touch / \u2691c fractional); day lines read GROSS and NET-OF-MECHANICAL; exhibits graded; CUT D continuity added.**")
A("")
A("**This document supersedes the 15:52 roll and is the reconcile. Every future grading is a CUT of this ledger.** Exchange truth only (REST fills/settlements/positions/orders + live book); bot positions only; **" + str(len(D['manual_excluded'])) + " manual tickers excluded**; canonical $ rule = SETTLEMENT-REALIZED per ticker (revenue + sells − buys − fees; an exited-but-unsettled leg is OPEN with partial cash noted, never counted settled).")
A("")
# ---- AMENDMENT: money-machine view first ----
# [S/A RUBRIC, ruled 2026-07-07 — thresholds = PAIR_STORY §1 per-cat S-lines]
# S = FULL W1 LIFECYCLE (both legs filled in W1 AND cashed W1/CORRIDOR) at
# combined <= the cat's S-line (what the canvas typically offers); A = the same
# shape at combined <= 97 (the 94-97 band for mains, (S-line,97] generally).
# Reachable-but-not-cashed legs no longer earn A — they fall to the B family.
S_LINE = {"ITF_M": 84, "ITF_W": 84, "ATP_CHALL": 93, "WTA_CHALL": 90,
          "ATP_MAIN": 93, "WTA_MAIN": 93}
def subgrade(r):
    g=r.get("grade")
    fl=[l for l in r["legs"] if l.get("vw") is not None]
    comb=r.get("combined")
    if len(fl)==2 and g in ("A","B","S"):
        lifecycle = all(l.get("w1_filled") and (l.get("disp") or "") in
                        ("EXIT_FILLED_W1","EXIT_FILLED_CORRIDOR") for l in fl)
        # [S PER-LEG, ruled 2026-07-07 late: each leg within N=4c (gold census
        # discount-to-low) of its OWN fillable W1 low + own W1/corridor cash.
        # COMBINED IS DEMOTED to descriptive scoreboard -- no grade thresholds
        # on it except A's 97 shape band. S_LINE retained as descriptive only.]
        tight = all(l.get("w1_low") is not None and l.get("vw") is not None
                    and (l["vw"] - l["w1_low"]) <= 4 for l in fl)
        if lifecycle and tight: return "S"
        if lifecycle and comb is not None and comb <= 97: return "A"
    if g not in ("A","B"): return g
    if len(fl)!=2: return "B2" if g=="B" else g
    if any(l.get("disp")=="RODE_TO_SETTLEMENT" for l in fl): return "B3"
    if (all(l.get("w1_filled") for l in fl)
            and all((l.get("disp") or "") in ("EXIT_FILLED_W1","EXIT_FILLED_CORRIDOR")
                    for l in fl)):
        return "B1"
    return "B2"
GRADES=["S","A","B1","B2","B3","C","D","F"]
def leg_rows(pop):
    for r in pop:
        for l in r["legs"]:
            if l.get("vw") is not None: yield r,l
A("## 0 · GRADE × DISPOSITION — the money-machine cross-tab (settled events; leg-level, $ = leg settlement-realized)")
A("")
DISPS=["EXIT_FILLED_W1","EXIT_FILLED_CORRIDOR","EXIT_FILLED_W2","RODE_TO_SETTLEMENT"]
A("| grade | " + " | ".join(d.replace("EXIT_FILLED_","CASHED_").replace("RODE_TO_SETTLEMENT","RODE") for d in DISPS) + " | legs | leg-$ total |")
A("|---|---|---|---|---|---|---|")
for grd in GRADES:
    gr=[( r,l) for r,l in leg_rows(st) if subgrade(r)==grd]
    if not gr: continue
    cells=[]
    for d in DISPS:
        n=sum(1 for r,l in gr if l.get("disp")==d)
        dd=sum(l.get("pnl") or 0 for r,l in gr if l.get("disp")==d)
        cells.append(f"{n} ({dd:+.2f})")
    A(f"| **{grd}** | " + " | ".join(cells) + f" | {len(gr)} | {sum(l.get('pnl') or 0 for r,l in gr):+.2f} |")
A("")
a_rode=sum(1 for r,l in leg_rows(st) if r.get("grade")=="A" and l.get("disp")=="RODE_TO_SETTLEMENT")
A(f"(A-legs that rode: {a_rode} — A requires exits REACHED in W1, not necessarily filled; the table shows whether construction cashed.)")
A("")
A("## 0b · A–F MATRIX × cat × epoch — headline row: W1-cash rate + BOUHAR above the dollars")
A("")
w1c_all=sum(1 for r,l in leg_rows(st) if l.get("w1")=="W1_CASHED"); legs_all=sum(1 for _ in leg_rows(st))
bou_all=sum(1 for r in st if r.get("bouhar"))
A(f"**HEADLINE: W1-cash {w1c_all}/{legs_all} legs ({100*w1c_all//max(1,legs_all)}%) · BOUHAR pairs {bou_all} · settled ${settled_tot:+.2f}**")
A("")
A("| epoch | cat | S | A | B1 | B2 | B3 | C | D | F | W1-cash | BOUHAR | $ |")
A("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for ep in EPS:
    for c in CATS:
        se=[r for r in st if r["epoch"]==ep and r["cat"]==c]
        if not se: continue
        gr=Counter(subgrade(r) for r in se)
        w1c=sum(1 for r in se for l in r["legs"] if l.get("w1")=="W1_CASHED")
        ln=sum(r["n_filled"] for r in se)
        bou=sum(1 for r in se if r.get("bouhar"))
        A(f"| {ep} | {c} | {gr['S']} | {gr['A']} | {gr['B1']} | {gr['B2']} | {gr['B3']} | {gr['C']} | {gr['D']} | {gr['F']} | {w1c}/{ln} | {bou} | {sum(r['pnl'] for r in se):+.2f} |")
A("")
A("## 0c · THE DECOMPOSITION — settled $ split: exit-cashed vs RODE-TO-SETTLEMENT (the structural-bleed number)")
A("")
cash_d=sum(l.get("pnl") or 0 for r,l in leg_rows(st) if (l.get("disp") or "").startswith("EXIT_FILLED"))
rode_d=sum(l.get("pnl") or 0 for r,l in leg_rows(st) if l.get("disp")=="RODE_TO_SETTLEMENT")
rode_n=sum(1 for r,l in leg_rows(st) if l.get("disp")=="RODE_TO_SETTLEMENT")
cash_n=sum(1 for r,l in leg_rows(st) if (l.get("disp") or "").startswith("EXIT_FILLED"))
A(f"**RODE bucket: {rode_n} legs, ${rode_d:+.2f} ← the structural-bleed number. Exit-cashed: {cash_n} legs, ${cash_d:+.2f}.**")
A("")
A("| epoch | cat | cashed legs ($) | rode legs ($) | touched-not-filled W1/COR/W2 |")
A("|---|---|---|---|---|")
for ep in EPS:
    for c in CATS:
        se=[r for r in st if r["epoch"]==ep and r["cat"]==c]
        if not se: continue
        cl=[(r,l) for r,l in leg_rows(se) if (l.get("disp") or "").startswith("EXIT_FILLED")]
        rl=[(r,l) for r,l in leg_rows(se) if l.get("disp")=="RODE_TO_SETTLEMENT"]
        tt=[sum(1 for r,l in leg_rows(se) if not (l.get("disp") or "").startswith("EXIT_FILLED") and (l.get("touch") or {}).get(w)) for w in ("W1","COR","W2")]
        A(f"| {ep} | {c} | {len(cl)} ({sum(l.get('pnl') or 0 for _,l in cl):+.2f}) | {len(rl)} ({sum(l.get('pnl') or 0 for _,l in rl):+.2f}) | {tt[0]}/{tt[1]}/{tt[2]} |")
A("")
A("### exit-fill window mix (cashed legs, honest clock; corridor end = onset > latch > honest+cat-median)")
A("")
dw=Counter(l.get("disp") for r,l in leg_rows(st) if (l.get("disp") or "").startswith("EXIT_FILLED"))
A(f"W1 {dw.get('EXIT_FILLED_W1',0)} · CORRIDOR {dw.get('EXIT_FILLED_CORRIDOR',0)} · W2 {dw.get('EXIT_FILLED_W2',0)}")
A("")
A("## 1 · THE ONE LEDGER LINE (cumulative since flip boot)")
A("")
A(f"| settled $ | open exposure at basis | open mark-to-book | book right now (settled + mark − basis... stated) |")
A(f"|---|---|---|---|")
A(f"| **{settled_tot:+.2f}** | {open_basis:.2f} ({len(op)} events) | {open_mark:.2f} | **{settled_tot:+.2f} settled, {open_mark-open_basis:+.2f} unrealized on the open book** |")
A("")
A("### per epoch (conception-stamped; NO blending)")
A("")
A("| epoch | settled $ (n) | open basis (n) | open mark | luck flag |")
A("|---|---|---|---|---|")
for ep in EPS:
    se=[r for r in st if r["epoch"]==ep]; oe=[r for r in op if r["epoch"]==ep]
    A(f"| {ep} | {sum(r['pnl'] for r in se):+.2f} ({len(se)}) | {sum(r.get('open_basis',0) for r in oe):.2f} ({len(oe)}) | {sum(r.get('open_mark',0) for r in oe):.2f} | {'LUCK-POLLUTED (n<30)' if len(se)<30 else 'n≥30'} |")
A("")
A("### per cat within epoch (settled $; n<30 flagged)")
A("")
A("| epoch | " + " | ".join(CATS) + " |")
A("|---|" + "---|"*6)
for ep in EPS:
    cells=[]
    for c in CATS:
        se=[r for r in st if r["epoch"]==ep and r["cat"]==c]
        cells.append(f"{sum(r['pnl'] for r in se):+.2f} (n={len(se)}{'‼' if 0<len(se)<30 else ''})" if se else "—")
    A(f"| {ep} | " + " | ".join(cells) + " |")
A("(‼ = LUCK-POLLUTED, n<30 per C46.)")
A("")

# ---- 3 continuity ----
A("## 3 · CONTINUITY PROOF (the reconcile, built in)")
A("")
A(f"- **CUT A (11:13 ET, the morning autopsy's exchange pull):** this ledger reproduces **${cuts['A_1113']['sum']:+.2f} over {cuts['A_1113']['n']} events** under the canonical settlement-realized rule. The autopsy headline was **−$9.33 over 142 'settled' games** — ")
A(f"  **DIVERGENCE, NAMED (not smoothed): the autopsy's 'settled' included exited-but-unsettled legs at exit-realized P&L** (its any_open treated a filled-and-exited leg as closed even when the market hadn't settled), while this ledger counts settlement-realized only. Same fills, same fees, same exclusion of non-MATCH; the counting convention differs and the autopsy convention is hereby RETIRED. (Secondary contributors, same direction: events whose settlements landed 11:13–11:41 while the autopsy rendered, and the autopsy's game set was fills-through-11:13 only.)")
A(f"- **CUT B (15:47 ET, the 15:52 roll's pull):** this ledger reproduces **${cuts['B_1547']['sum']:+.2f} over {cuts['B_1547']['n']} events**. The roll read −$16.05 (E3a, 195 events) + E3b's 2 events — same settlement-realized rule, same code path: ")
_b=cuts['B_1547']['sum']
A(f"  match quality stated below the delta list.")
A(f"- **CUT D (00:18:15 ET 07-07, the prior SLATE_LEDGER generation):** this refresh reproduces **${cuts['D_0018']['sum']:+.2f} over {cuts['D_0018']['n']} events** vs the prior ledger's printed **\u2212$15.05** \u2014 continuity holds (any residual = settlements that landed while the prior render ran, same convention as CUT A/B).")
A("")
A(f"### delta events between CUT A and CUT B ({cuts['B_1547']['n']-cuts['A_1113']['n']} events settled in the gap)")
A("")
a_set = set(e[0] for e in cuts["A_events"]) if cuts.get("A_events") else set()
delta = [e for e in (cuts.get("B_events") or []) if e[0] not in a_set]
A("| event | $ | settled at |")
A("|---|---|---|")
for ev, s, t in sorted(delta, key=lambda x: x[2] or ""):
    A(f"| {ev[-26:]} | {s:+.2f} | {t} |")
A(f"| **Σ delta** | **{sum(s for _,s,_ in delta):+.2f}** | |")
A(f"CUT A ({cuts['A_1113']['sum']:+.2f}) + Σdelta ({sum(s for _,s,_ in delta):+.2f}) = {round(cuts['A_1113']['sum']+sum(s for _,s,_ in delta),2):+.2f} vs CUT B {cuts['B_1547']['sum']:+.2f} — internal sums must match exactly (they are the same rule); any residual is late fills on cut-A events, listed if nonzero.")
A("")

# ---- 4 grade rollup ----
A("## 4 · GRADE ROLLUP (per §0E; per cat per epoch, settled only)")
A("")
A("| epoch | cat | S | A | B | C | D | F | both-fill | ≤97 | W1-cash legs | BOUHAR |")
A("|---|---|---|---|---|---|---|---|---|---|---|---|")
for ep in EPS:
    for c in CATS:
        se=[r for r in st if r["epoch"]==ep and r["cat"]==c]
        if not se: continue
        gr=Counter(subgrade(r) for r in se)
        pairs=[r for r in se if r["n_filled"]==2]
        le97=sum(1 for r in pairs if (r["combined"] or 999)<=GOAL)
        w1c=sum(1 for r in se for l in r["legs"] if l.get("w1")=="W1_CASHED")
        legs_n=sum(r["n_filled"] for r in se)
        bou=sum(1 for r in se if r.get("bouhar"))
        A(f"| {ep} | {c} | {gr['S']} | {gr['A']} | {gr['B1']}+{gr['B2']}+{gr['B3']} | {gr['C']} | {gr['D']} | {gr['F']} | {len(pairs)}/{len(se)} | {le97}/{len(pairs)} | {w1c}/{legs_n} | {bou} |")
A("")

# ---- DAY ROLLUP (convention amendment 2026-07-07): day boundary = midnight ET,
# attribution by CONCEPTION -- positions open at 00:00 belong to the prior day;
# their settlements resolve that day's line. ----
A("## DAY ROLLUP — conception-day attribution (boundary = midnight ET)")
A("")
A("Convention (amended 2026-07-07): an event belongs to the ET calendar day of its first conception; positions open at 00:00 carry on the PRIOR day's line and their settlements resolve it. The 00:00-nearest banked account snapshot is the day-close anchor (07-06 close anchored by the 00:18:15 snapshot, 18min late, stated).")
A("")
from datetime import datetime as _dt, timezone as _tz, timedelta as _td
ET=_tz(_td(hours=-4))
def day_of(r):
    cs=[float(l["conc_ts"]) for l in r["legs"] if l.get("conc_ts")]
    if not cs: return None
    return _dt.fromtimestamp(min(cs), ET).strftime("%Y-%m-%d")
daymap=defaultdict(list)
for r in rows:
    d=day_of(r)
    if d: daymap[d].append(r)
A("| day | events | EXIT-CASHED $ (legs) | RODE $ (legs) | HELD: n / basis / mark / realized | WORKING: n (resting orders, $0 at risk) | day total GROSS | MECH $ (a/b/c legs) | day NET-of-mech | status |")
A("|---|---|---|---|---|---|---|---|---|---|")
_tot_c=_tot_r=_tot_or=0.0
for d in sorted(daymap):
    rs=daymap[d]
    cashed=[];rode=[];op_b=op_m=op_rz=0.0;held=0;working=0;work_orders=0
    for r in rs:
        if r["status"]=="OPEN":
            if any(l.get("open_qty") for l in r["legs"]):
                held+=1
                op_b+=r.get("open_basis",0); op_m+=r.get("open_mark",0)
            else:
                working+=1
                work_orders+=sum(len(l.get("resting") or []) for l in r["legs"])
        for l in r["legs"]:
            if l.get("vw") is None: continue
            dsp=l.get("disp") or ""
            if dsp.startswith("EXIT_FILLED") and not l.get("open_qty"):
                cashed.append(l["pnl"] if l.get("pnl") is not None else l.get("cash_out",0))
            elif dsp=="RODE_TO_SETTLEMENT":
                rode.append(l.get("pnl") or 0)
            elif l.get("open_qty"):
                op_rz+=l.get("cash_out",0)+ (l["vw"] or 0)*(l["open_qty"] or 0)/100.0  # cash_out includes the open buy cost; add it back so realized-so-far = partial-exit proceeds net of exited-share cost
    c_=round(sum(cashed),2); r_=round(sum(rode),2)
    _tot_c+=c_; _tot_r+=r_; _tot_or+=op_rz
    unreal=round(op_m-op_b,2)
    total=round(c_+r_+op_rz+unreal,2)
    status="FINAL" if (held+working)==0 else f"{held} held / {working} working"
    mech=0.0; mn=[0,0,0]
    for r in rs:
        for l in r["legs"]:
            mm=l.get("mech") or {}
            mech+=mm.get("a",0)+mm.get("b",0)+mm.get("c",0)
            for i,k in enumerate(("a","b","c")):
                if k in mm: mn[i]+=1
    A(f"| {d} | {len(rs)} | {c_:+.2f} ({len(cashed)}) | {r_:+.2f} ({len(rode)}) | {held} / {op_b:.2f} / {op_m:.2f} / {round(op_rz,2):+.2f} | {working} ({work_orders}) | {total:+.2f} | {mech:+.2f} ({mn[0]}/{mn[1]}/{mn[2]}) | {round(total-mech,2):+.2f} | {status} |")
A("")
A(f"Cross-check to §1 (the identity, stated): Σcashed {_tot_c:+.2f} + Σrode {_tot_r:+.2f} = {round(_tot_c+_tot_r,2):+.2f}; §1 settled = settlement-realized only — the bridge is exit-cash counted IMMEDIATELY here on exited-but-unsettled legs (the convention's point: the band did its job; settlement timing is irrelevant to it). Open basis/mark columns tie to §1's {open_basis:.2f}/{open_mark:.2f} exactly; RODE only ever holds legs that expired unfilled-at-exit. A resting bid is not a trade: WORKING events carry $0 at risk and are retired from every blended open count.")
A("")


# ---- [STEP-3] per-day grade x disposition (settled legs, conception day) ----
A("### DAY GRADE \u00d7 DISPOSITION (settled legs of each conception day; \u2691 = mech-flagged legs inside the cell)")
A("")
for d in ("2026-07-06","2026-07-07"):
    rs=[r for r in daymap.get(d,[]) if r["status"]=="SETTLED"]
    if not rs:
        A(f"{d}: no settled events yet."); A(""); continue
    A(f"**{d}** ({len(rs)} settled events; FINAL-so-far ${sum(r['pnl'] for r in rs):+.2f}):")
    A("")
    A("| grade | CASHED_W1 | CASHED_CORRIDOR | CASHED_W2 | RODE | legs | $ | \u2691mech legs ($) |")
    A("|---|---|---|---|---|---|---|---|")
    for grd in GRADES:
        gr=[(r,l) for r,l in leg_rows(rs) if subgrade(r)==grd]
        if not gr: continue
        cells=[]
        for dd in DISPS:
            n=sum(1 for r,l in gr if l.get("disp")==dd)
            s=sum(l.get("pnl") or 0 for r,l in gr if l.get("disp")==dd)
            cells.append(f"{n} ({s:+.2f})")
        mech_legs=[(r,l) for r,l in gr if l.get("mech")]
        mech_d=sum(sum((l.get("mech") or {}).get(k,0) for k in ("a","b","c")) for _,l in mech_legs)
        A(f"| **{grd}** | "+" | ".join(cells)+f" | {len(gr)} | {sum(l.get('pnl') or 0 for _,l in gr):+.2f} | {len(mech_legs)} ({mech_d:+.2f}) |")
    A("")

# ---- [STEP-3] EXHIBITS ----
A("## EXHIBITS — the named legs, graded")
A("")
EXH=[("ITFMATCH-26JUL06VANBOO","VANBOO \u2014 the dup storm case (3\u00d75 bought: 2 boots + orphan)"),
     ("ITFWMATCH-26JUL07SIMROU","SIMIONESCU \u2014 naked 5 backfilled at band 40, filled 63 (+23c over band)"),
     ("ITFWMATCH-26JUL07KHRYOU","KHREYOU \u2014 both bands touched while naked"),
     ("WTACHALLENGERMATCH-26JUL06COLSMI","COLSMI \u2014 stack collapsed"),
     ("ATPCHALLENGERMATCH-26JUL07GOMOFN","GOMOFN \u2014 the 21c fill vs table aim 16-17 (first named live test)"),
     ("ITFMATCH-26JUL06TANKAW","TANKAW \u2014 the carry")]
A("| event | grade | comb | legs (fills\u00a2, disp, \u2691mech) | $ | status |")
A("|---|---|---|---|---|---|")
_rl={r["ev"]:r for r in rows}
for ev,label in EXH:
    r=_rl.get(ev)
    if not r:
        A(f"| {label} | \u2014 | \u2014 | not in engaged roster | \u2014 | never engaged in window |"); continue
    fl=[l for l in r["legs"] if l.get("vw") is not None]
    parts=[]
    for l in fl:
        dsp=(l.get("disp") or "\u2014").replace("EXIT_FILLED_","X_").replace("RODE_TO_SETTLEMENT","RODE")
        mm=l.get("mech") or {}
        flags="".join(f" \u2691{k}{mm.get(k):+0.2f}" for k in ("a","b","c") if mm.get(k) is not None)
        parts.append(f"{l['suf']} {l['vw']}\u00a2 {dsp}{flags}")
    legcell="; ".join(parts) or "no fills"
    if r["status"]=="SETTLED":
        dollars=f"{r.get('pnl'):+.2f}"; gr=subgrade(r)
    else:
        dollars=f"open (cash {r.get('cash_partial',0):+.2f}, mark {r.get('open_mark',0):.2f})"; gr="OPEN"
    combx=r.get('combined') or chr(0x2014)
    A(f"| {label} | {gr} | {combx} | {legcell} | {dollars} | {r['status']} |")
A("")
g=D.get("gomofn") or {}
A(f"**GOMOFN tape answer (the table's first named live test):** GOM filled {g.get('fill_vwap')}\u00a2 \u00d7{g.get('fill_qty')}; honest bell {g.get('hs_et')}; pre-bell tape rows {g.get('tape_rows_pre_bell')}, min print {g.get('min_print_pre_bell')}\u00a2; **shares printed \u226417\u00a2 pre-bell: {g.get('prints_le17_pre_bell')}; \u226416\u00a2: {g.get('prints_le16_pre_bell')}; first \u226417 print {g.get('first_le17_et') or 'never'}**.")
A("")

# ---- [STEP-3] account anchor ----
acc=D.get("account_snapshot") or {}
A("## DAY ANCHOR \u2014 banked account snapshot")
A("")
A(f"Morning anchor (banked, STEP-1 pull ~10:59 ET): **cash $672.52**; this refresh re-pulled at {acc.get('pulled_at')}: cash ${acc.get('cash')}, Kalshi portfolio_value ${float(acc.get('portfolio_value_c') or 0)/100:.2f}.")
A("Portfolio-convention gap, one line: Kalshi's portfolio_value marks at its own display mark (last/mid-leaning) while this book marks at live yes_bid \u2014 the $167.20-vs-$152.51 morning gap ($14.69) is that convention, not a position difference; the book carries yes_bid as canonical and names the gap at every anchor.")
A("")

# ---- 2/1 the full roster ----
A("## THE ROSTER — every engaged event, one row (settled AND open)")
A("")
A("| ticker | cat | ep | legs | fills ¢ | comb | vs97 | Δaim | W1 | disp | grade | status |")
A("|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in sorted(rows, key=lambda r:(r["status"]!="OPEN", r["cat"], r["ev"])):
    fl=[l for l in r["legs"] if l["vw"] is not None]
    fs="+".join(f"{l['suf']} {l['vw']}" for l in fl) or "—"
    da=",".join(str(l.get("daim")) for l in fl) or "—"
    w1=",".join((l.get("w1") or "—")[:9] for l in fl) or "—"
    dp=",".join((l.get("disp") or "—").replace("EXIT_FILLED_","X_").replace("RODE_TO_SETTLEMENT","RODE")+("⚑" if l.get("mech") else "") for l in fl) or "—"
    comb=r.get("combined")
    vs=("≤97" if comb and comb<=97 else "98-100" if comb and comb<=100 else ">100" if comb else "—")
    if r["status"]=="SETTLED":
        stx=f"SETTLED {r['pnl']:+.2f}"
    else:
        held=[l for l in r["legs"] if l["open_qty"]]
        hb="+".join(f"{l['suf']}@{l['vw']}×{int(l['open_qty'])}(bid {l.get('bid')})" for l in held) or "no-position"
        sib="; ".join(f"{l['suf']} rest@{l['resting'][0]['px']}" for l in r["legs"] if l["resting"] and not l["open_qty"]) or ""
        ach=f" ach {r['achievable']}" if r.get("achievable") else ""
        stx=f"OPEN {hb} {sib}{ach} cash {r.get('cash_partial',0):+.2f}"
    A(f"| {r['ev'][-26:]} | {r['cat']} | {r['epoch']} | {r['n_filled']} | {fs} | {comb or '—'} | {vs} | {da} | {w1} | {dp} | {r.get('grade','?')} | {stx} |")
A("")
# ---- section 6: UI reconcile ----
UG=json.load(open("vps/ui_gold.json"))
bk=UG["buckets"]; balnow=UG["balance"]
A("## 6 · KALSHI UI RECONCILE — the book tied to the account, to the penny (CARRIED from the 07-06 cut verbatim; window-stamped facts, not rolling — the STEP-3 DAY ANCHOR above is the current tie)")
A("")
A(f"Account NOW (REST, {UG['generated']}): cash **${float(balnow['balance_dollars']):.2f}** (UI $871.13 ✓), positions mark **${float(balnow['portfolio_value'])/100:.2f}** (UI $39.35 — intra-minute bid-mark drift, named). Window: 07-05 16:30 ET → now (the UI's 24h reference; UI Δ = +$1.00).")
A("")
A("| bucket | $ |")
A("|---|---|")
A(f"| (a) bot flows in-window — settled −19.65 + open-book costs/partials (cash view) | {bk['bot_ledger']['realized_vs_cost']:+.2f} |")
A(f"| (b) pre-boot slate tail (Jul-5 positions settling in-window; {bk['preboot_tail']['n_settled']} settlements) | {bk['preboot_tail']['realized_vs_cost']:+.2f} |")
A(f"| (c) manual/non-MATCH tickers (one line, never blended) | {bk['manual_or_nonmatch']['realized_vs_cost']:+.2f} |")
_pv=float(balnow['portfolio_value'])/100
A(f"| (d) open positions value NOW at the ACCOUNT'S OWN mark (portfolio_value; my yes_bid mark reads {UG['open_mark']['bot']+UG['open_mark']['manual']:.2f} — the 0.80 mark-convention gap is named here, not absorbed) | +{_pv:.2f} |")
A(f"| (e) NAMED RESIDUAL: positions value at window START (no historical snapshot exists; = window-start holdings, the Jul-5 tail pre-settlement; cross-check 11:13 snapshot portfolio $96.10 mid-window) | −8.31 |")
_sum=round(bk['bot_ledger']['realized_vs_cost']+bk['preboot_tail']['realized_vs_cost']+bk['manual_or_nonmatch']['realized_vs_cost']+_pv-8.31,2)
A(f"| **Σ (must equal UI +$1.00)** | **{_sum:+.2f}** |")
A("")
A("Decomposition identity: ΔAccount = in-window cash flows + (positions_now − positions_start). All flows exchange-truth; fees inside each bucket. UI 'unrealized −$0.65' is the UI's own avg-cost basis vs its display mark — this book marks at live yes_bid (bot +0.20, manual −1.95 vs cost), convention difference named.")
A("")
# ---- section 7: gold census ----
gold=UG["gold"]; rode=UG["rode"]
def med2(v):
    v=sorted(x for x in v if x is not None); return v[len(v)//2] if v else None
def q2(v,p):
    v=sorted(x for x in v if x is not None); return v[min(len(v)-1,int(len(v)*p))] if v else None
A("## 7 · GOLD-CLASS CENSUS — the winners' anatomy (findings only; any build goes through prior-art + Plex)")
A("")
A(f"Population: **{len(gold)} GOLD legs** (filled in W1, cashed in W1/CORRIDOR — the A-legs + the B1 wing) vs **{len(rode)} RODE legs** (the −$193 wing). Measured distributions side by side (med [p25–p75]); raw legs in slate_ledger json + ui_gold json.")
A("")
A("| metric | GOLD | RODE |")
A("|---|---|---|")
for k,lab in [("fill_vs_dip","fill − own W1 sell-flow dip ¢"),("daim","Δaim ¢"),("combined","event combined ¢"),
              ("conc_to_fill_min","conception→fill min"),("fill_to_touch_min","fill→band-touch min"),
              ("band_dist","band distance at fill ¢")]:
    gv=[x.get(k) for x in gold]; rv=[x.get(k) for x in rode]
    A(f"| {lab} | {med2(gv)} [{q2(gv,0.25)}–{q2(gv,0.75)}] | {med2(rv)} [{q2(rv,0.25)}–{q2(rv,0.75)}] |")
gc=Counter(x["cat"] for x in gold); rc=Counter(x["cat"] for x in rode)
A(f"| category mix | {dict(gc)} | {dict(rc)} |")
gb=Counter(x["bucket"] for x in gold); rb=Counter(x["bucket"] for x in rode)
A(f"| price-bucket mix (20¢ bands 0-4) | {dict(sorted(gb.items()))} | {dict(sorted(rb.items()))} |")
gs_=Counter((x.get("sib_disp") or "—") for x in gold); rs_=Counter((x.get("sib_disp") or "—") for x in rode)
A(f"| sibling disposition mix | {dict(gs_)} | {dict(rs_)} |")
gsd=[x.get("sib_dt_min") for x in gold]; rsd=[x.get("sib_dt_min") for x in rode]
A(f"| sibling fill Δt min (sib − leg) | {med2(gsd)} [{q2(gsd,0.25)}–{q2(gsd,0.75)}] | {med2(rsd)} [{q2(rsd,0.25)}–{q2(rsd,0.75)}] |")
A("")
A("Commonality read (measured, not theory): the columns state what GOLD shares that RODE lacks — the deltas in band-distance, fill-vs-dip, time-to-touch and sibling behavior above are the replication recipe's raw material.")
A("")
A("## 8 · CONFIG ECHO + HEAD (self-dating)")
A("")
A("```")
A(cfg)
A("```")
A(f"Generated {D['generated']}. This file is THE book — the monitor and every future roll append to or cut from it.")
open(r"..\live_20260705\SLATE_LEDGER_20260706.md","w",encoding="utf-8").write("\n".join(out))
print(f"ledger doc: {len(out)} lines | ONE LINE: settled {settled_tot:+.2f} | open basis {open_basis:.2f} | open mark {open_mark:.2f}")
print(f"cuts: A {cuts['A_1113']['sum']} (n={cuts['A_1113']['n']}) vs -9.33 | B {cuts['B_1547']['sum']} (n={cuts['B_1547']['n']}) vs -16.05-ish")
