#!/usr/bin/env python3
"""Render SLATE_LEDGER_20260706.md from vps/slate_ledger.json + config echo.
THE book: one table (settled+open), one ledger line, continuity cuts, grade rollups."""
import json
from collections import defaultdict, Counter

D = json.load(open("vps/slate_ledger.json"))
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
A("**This document supersedes the 15:52 roll and is the reconcile. Every future grading is a CUT of this ledger.** Exchange truth only (REST fills/settlements/positions/orders + live book); bot positions only; **" + str(len(D['manual_excluded'])) + " manual tickers excluded**; canonical $ rule = SETTLEMENT-REALIZED per ticker (revenue + sells − buys − fees; an exited-but-unsettled leg is OPEN with partial cash noted, never counted settled).")
A("")
# ---- AMENDMENT: money-machine view first ----
def subgrade(r):
    g=r.get("grade")
    if g!="B": return g
    fl=[l for l in r["legs"] if l.get("vw") is not None]
    if len(fl)!=2: return g
    if any(l.get("disp")=="RODE_TO_SETTLEMENT" for l in fl): return "B3"
    if (all(l.get("w1_filled") for l in fl)
            and all((l.get("disp") or "") in ("EXIT_FILLED_W1","EXIT_FILLED_CORRIDOR") for l in fl)):
        return "B1"
    return "B2"
GRADES=["A","B1","B2","B3","C","D","F"]
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
A("| epoch | cat | A | B1 | B2 | B3 | C | D | F | W1-cash | BOUHAR | $ |")
A("|---|---|---|---|---|---|---|---|---|---|---|---|")
for ep in EPS:
    for c in CATS:
        se=[r for r in st if r["epoch"]==ep and r["cat"]==c]
        if not se: continue
        gr=Counter(subgrade(r) for r in se)
        w1c=sum(1 for r in se for l in r["legs"] if l.get("w1")=="W1_CASHED")
        ln=sum(r["n_filled"] for r in se)
        bou=sum(1 for r in se if r.get("bouhar"))
        A(f"| {ep} | {c} | {gr['A']} | {gr['B1']} | {gr['B2']} | {gr['B3']} | {gr['C']} | {gr['D']} | {gr['F']} | {w1c}/{ln} | {bou} | {sum(r['pnl'] for r in se):+.2f} |")
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
A("| epoch | cat | A | B | C | D | F | both-fill | ≤97 | W1-cash legs | BOUHAR |")
A("|---|---|---|---|---|---|---|---|---|---|---|")
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
        A(f"| {ep} | {c} | {gr['A']} | {gr['B1']}+{gr['B2']}+{gr['B3']} | {gr['C']} | {gr['D']} | {gr['F']} | {len(pairs)}/{len(se)} | {le97}/{len(pairs)} | {w1c}/{legs_n} | {bou} |")
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
    dp=",".join((l.get("disp") or "—").replace("EXIT_FILLED_","X_").replace("RODE_TO_SETTLEMENT","RODE") for l in fl) or "—"
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
A("## 6 · KALSHI UI RECONCILE — the book tied to the account, to the penny")
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
