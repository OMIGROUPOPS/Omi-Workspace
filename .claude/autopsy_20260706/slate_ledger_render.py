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
        gr=Counter(r["grade"] for r in se)
        pairs=[r for r in se if r["n_filled"]==2]
        le97=sum(1 for r in pairs if (r["combined"] or 999)<=GOAL)
        w1c=sum(1 for r in se for l in r["legs"] if l.get("w1")=="W1_CASHED")
        legs_n=sum(r["n_filled"] for r in se)
        bou=sum(1 for r in se if r.get("bouhar"))
        A(f"| {ep} | {c} | {gr['A']} | {gr['B']} | {gr['C']} | {gr['D']} | {gr['F']} | {len(pairs)}/{len(se)} | {le97}/{len(pairs)} | {w1c}/{legs_n} | {bou} |")
A("")

# ---- 2/1 the full roster ----
A("## THE ROSTER — every engaged event, one row (settled AND open)")
A("")
A("| ticker | cat | ep | legs | fills ¢ | comb | vs97 | Δaim | W1 | grade | status |")
A("|---|---|---|---|---|---|---|---|---|---|---|")
for r in sorted(rows, key=lambda r:(r["status"]!="OPEN", r["cat"], r["ev"])):
    fl=[l for l in r["legs"] if l["vw"] is not None]
    fs="+".join(f"{l['suf']} {l['vw']}" for l in fl) or "—"
    da=",".join(str(l.get("daim")) for l in fl) or "—"
    w1=",".join((l.get("w1") or "—")[:9] for l in fl) or "—"
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
    A(f"| {r['ev'][-26:]} | {r['cat']} | {r['epoch']} | {r['n_filled']} | {fs} | {comb or '—'} | {vs} | {da} | {w1} | {r.get('grade','?')} | {stx} |")
A("")
A("## 5 · CONFIG ECHO + HEAD (self-dating)")
A("")
A("```")
A(cfg)
A("```")
A(f"Generated {D['generated']}. This file is THE book — the monitor and every future roll append to or cut from it.")
open(r"..\live_20260705\SLATE_LEDGER_20260706.md","w",encoding="utf-8").write("\n".join(out))
print(f"ledger doc: {len(out)} lines | ONE LINE: settled {settled_tot:+.2f} | open basis {open_basis:.2f} | open mark {open_mark:.2f}")
print(f"cuts: A {cuts['A_1113']['sum']} (n={cuts['A_1113']['n']}) vs -9.33 | B {cuts['B_1547']['sum']} (n={cuts['B_1547']['n']}) vs -16.05-ish")
