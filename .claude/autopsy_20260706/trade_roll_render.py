#!/usr/bin/env python3
"""Render TRADE_ROLL doc from vps/trade_roll.json + config echo. Raw tables."""
import json
from collections import defaultdict, Counter

D = json.load(open("vps/trade_roll.json"))
cfg = open("vps/config_echo.txt", encoding="utf-8").read().strip()
GOAL = 97
CATS = ["ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL","ITF_M","ITF_W"]
def med(v):
    v = sorted(x for x in v if x is not None); return v[len(v)//2] if v else None

out=[]; A=out.append
A(f"# TRADE ROLL — every bot tennis position since the flip boot (generated {D['generated']})")
A("")
A("**Exchange truth throughout** (REST /fills + /settlements + /positions + /orders + live /markets book). Bot positions only — **35 manual/operator tickers excluded** (attribution=manual adoptions + non-MATCH collateral out of scope by construction).")
A("")
A("## Epoch timeline (deploy history; conception-time stamping)")
A("")
A("| epoch | window (ET) | regime |")
A("|---|---|---|")
A("| E1+E2 | context | flip (297a7086, 23:50:39 07-05) and bound-ruling (21eaad4, 19:24 07-05) BOTH precede every in-scope conception — coincident context, not separable rows |")
A("| E3a | 07-05 23:50:39 → 07-06 12:15:22 | riser ARMED (9925dd6), honest clock, pre guards/true-basis |")
A("| E3b | 07-06 12:15:22 → 15:25:58 | + guards/true-basis (b8a73a55 via d01a3cc) — riser still armed |")
A("| E4 | 07-06 15:25:58 → now | riser DISARMED (3db9af8) + guards/true-basis |")
A("")
A("(The operator's E3/E4 labels split at 12:15 because the guards/true-basis deploy landed three hours before the riser disarm — stamping honestly rather than blending. Positions spanning epochs carry `spans`.)")
A("")

# ---------- SETTLED ----------
for ep in ("E3a","E3b","E4"):
    rows=[r for r in D["settled"] if r["epoch"]==ep]
    if not rows:
        A(f"## SETTLED — {ep}: none yet"); A(""); continue
    A(f"## SETTLED ROLL — {ep} ({len(rows)} events)")
    A("")
    A("| ticker | cat | legs | fills ¢ | comb | vs97 | Δaim | W1 | grade | $ | spans |")
    A("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in sorted(rows,key=lambda r:(r["cat"],r["ev"])):
        fl=[l for l in r["legs"] if l["vw"] is not None]
        fs="+".join(f"{l['suf']} {l['vw']}" for l in fl)
        da=",".join(str(l["daim"]) for l in fl)
        w1=",".join((l["w1"] or "—")[:9] for l in fl)
        comb=r.get("combined")
        vs=("≤97" if comb and comb<=97 else "98-100" if comb and comb<=100 else ">100" if comb else "—")
        sp="+".join(r["spans"]) if len(r["spans"])>1 else ""
        A(f"| {r['ev'][-24:]} | {r['cat']} | {len(fl)} | {fs} | {comb or '—'} | {vs} | {da} | {w1} | {r.get('grade','?')} | {r.get('pnl',0):+.2f} | {sp} |")
    A("")
    # rollup per cat
    A(f"### {ep} rollup (per category; NO cross-epoch blending)")
    A("")
    A("| cat | n events | pairs | singles | both-fill rate | ≤97 on completions | med Δaim | W1-cash legs | Lane-2 $ | Lane-2 flag |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for c in CATS:
        cr=[r for r in rows if r["cat"]==c]
        if not cr: continue
        pairs=[r for r in cr if len([l for l in r["legs"] if l["vw"] is not None])==2]
        singles=len(cr)-len(pairs)
        le97=sum(1 for r in pairs if (r.get("combined") or 999)<=97)
        das=[l["daim"] for r in cr for l in r["legs"] if l.get("daim") is not None and l["vw"] is not None]
        w1c=sum(1 for r in cr for l in r["legs"] if l.get("w1")=="W1_CASHED")
        legs_n=sum(1 for r in cr for l in r["legs"] if l["vw"] is not None)
        pnl=sum(r.get("pnl",0) for r in cr)
        flag="LUCK-POLLUTED (n<30)" if len(cr)<30 else "n ok"
        A(f"| {c} | {len(cr)} | {len(pairs)} | {singles} | {len(pairs)}/{len(cr)} | {le97}/{len(pairs)} | {med(das)} | {w1c}/{legs_n} | {pnl:+.2f} | {flag} |")
    # epoch totals
    pairs=[r for r in rows if len([l for l in r["legs"] if l["vw"] is not None])==2]
    le97=sum(1 for r in pairs if (r.get("combined") or 999)<=97)
    das=[l["daim"] for r in rows for l in r["legs"] if l.get("daim") is not None and l["vw"] is not None]
    w1c=sum(1 for r in rows for l in r["legs"] if l.get("w1")=="W1_CASHED")
    legs_n=sum(1 for r in rows for l in r["legs"] if l["vw"] is not None)
    pnl=sum(r.get("pnl",0) for r in rows)
    A(f"| **{ep} TOTAL** | {len(rows)} | {len(pairs)} | {len(rows)-len(pairs)} | {len(pairs)}/{len(rows)} | {le97}/{len(pairs)} | {med(das)} | {w1c}/{legs_n} | {pnl:+.2f} | {'LUCK-POLLUTED (n<30)' if len(rows)<30 else 'n≥30'} |")
    A("")

# ---------- LIVE ----------
A(f"## LIVE ROLL — right now ({len(D['live'])} events with exposure or resting bids)")
A("")
A("| ticker | cat | epoch | basis(qty) | sibling state | achievable comb | vs97 | age(min) | flags touched | half-arm |")
A("|---|---|---|---|---|---|---|---|---|---|")
import time
from datetime import datetime, timezone, timedelta
ET=timezone(timedelta(hours=-4))
gen_ts=datetime.strptime(D["generated"][:19],"%Y-%m-%d %H:%M:%S").replace(tzinfo=ET).timestamp()
for r in sorted(D["live"],key=lambda r:(r["cat"],r["ev"])):
    filled=[l for l in r["legs"] if l["open_qty"]]
    basis=" + ".join(f"{l['suf']} {l['vw']}¢×{int(l['open_qty'])}" for l in filled) or "—"
    sibs=[]
    for l in r["legs"]:
        if l["open_qty"]: continue
        if l["resting"]: sibs.append(f"{l['suf']} resting@{l['resting'][0]['px']}")
        elif l["vw"] is not None: sibs.append(f"{l['suf']} filled+exited")
        else: sibs.append(f"{l['suf']} NEVER RESTED" if not l["resting"] else "")
    ach=r.get("achievable")
    vs=("≤97" if ach and ach<=97 else ">97" if ach else "—")
    ages=[gen_ts-l["conc_ts"] for l in r["legs"] if l.get("conc_ts")]
    age=round(min(ages)/60) if ages else "—"
    flags=[]
    if r["epoch"] in ("E3a","E3b"): flags.append("riser-armed")
    if any(l.get("reaim") for l in r["legs"]): flags.append("reaim")
    if r["epoch"]=="E3b": flags.append("guards")
    ha="**HALF-ARM**" if r.get("half_arm") else ""
    A(f"| {r['ev'][-24:]} | {r['cat']} | {r['epoch']} | {basis} | {'; '.join(sibs) or '—'} | {ach or '—'} | {vs} | {age} | {','.join(flags)} | {ha} |")
A("")
ha_n=sum(1 for r in D["live"] if r.get("half_arm"))
A(f"Half-arm (filled leg, sibling never rested — the SANARN class): **{ha_n} live events**, flagged above.")
A("")
open("TRADE_ROLL_BODY.md","w",encoding="utf-8").write("\n".join(out))
print(f"body rendered: {len(out)} lines | settled {len(D['settled'])} | live {len(D['live'])} | half-arms {ha_n}")
