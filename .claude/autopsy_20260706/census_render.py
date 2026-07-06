#!/usr/bin/env python3
"""Render ENTRY-MECHANICS CENSUS from census_dump.json -> ENTRY_CENSUS_20260706.md.
Concluded games only in the rows; split stated up front. Findings only."""
import json
from collections import Counter, defaultdict

D = json.load(open("vps/census_dump.json"))
games, phys = D["games"], D["phys"]
GOAL = 97
CATS = ["ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL","ITF_M","ITF_W"]

conc = [g for g in games if g["concluded"]]
open_g = [g for g in games if not g["concluded"]]

def med(v):
    v = sorted(x for x in v if x is not None)
    return v[len(v)//2] if v else None
def p75(v):
    v = sorted(x for x in v if x is not None)
    return v[int(len(v)*0.75)] if v else None

out = []; A = out.append
A(f"# ENTRY-MECHANICS CENSUS — concluded games, W1 + corridor (flip boot 07-05 23:50 ET → {D['generated']})")
A("")
A(f"**Split: {len(conc)} concluded / {len(open_g)} still open / {len(games)} engaged-total.** Open positions excluded from every row and rollup below.")
A("")
A("**Ground rules honored:** exchange truth for fills/conclusions (fills+markets API); size-backed sell-flow book levels via the July-5 regrade step-③ `dip_hunt` (reused verbatim); windows per Vault §5 + P3a (07-05, newest): **W1 = window-open → honest start · corridor = honest start → true tape onset** (onset via step-③ `tape_gun`; where undetectable — the P3a ITF 50-60% blind class — corridor end falls back to the latch and is flagged `onset_amb`). Exits OUT OF SCOPE (§0A standing order). Both bot sessions since flip boot included (23:50 + post-12:15 restart).")
A("")
A("**THE STANDARD:** both legs filled · each at its own best fillable price · in the window that price existed · combined ≤97 · gun accurate · grace clean. Every row below = distance from that, per axis, in the game's own tape terms.")
A("")

# ---------- HEADLINE ----------
A("## HEADLINE — category × four axes (concluded games)")
A("")
A("| cat | physics (spread¢ med / W1-dip prints med) | AX1 participation both/one/none | AX2 fill timing before/during/after dip (med miss min) | AX3 med paid-over-best W1¢ per filled leg (achievable-vs-paid med) | combined ≤97 / 98-100 / >100 | AX4 gun on/early/late/SILENT (grace viol) |")
A("|---|---|---|---|---|---|---|")
for c in CATS:
    gs = [g for g in conc if g["cat"] == c]
    if not gs: continue
    ph = phys.get(c, {})
    part = Counter("both" if g["participation"]=="both" else "one" if g["participation"].startswith("one") else "none" for g in gs)
    legs = [l for g in gs for l in g["legs"]]
    fl = [l for l in legs if l["fill_px"] is not None]
    tim = Counter(l["fill_vs_dip"] for l in fl if l["fill_vs_dip"])
    miss = med([abs(l["miss_min"]) for l in fl if l["miss_min"] is not None])
    gapw = med([l["gap_w1"] for l in fl if l["gap_w1"] is not None])
    combs = [g["combined"] for g in gs if g["combined"] is not None]
    cb = Counter("le97" if x<=97 else "98_100" if x<=100 else "gt100" for x in combs)
    ach = med([g["combined"]-g["best_achievable"] for g in gs if g["combined"] and g["best_achievable"]])
    guns = Counter((g["gun"] or {}).get("verdict","no-data") for g in gs)
    gv = sum(1 for g in gs for l in g["legs"] if (l.get("grace") or "").startswith("VIOLATION"))
    A(f"| {c} | {ph.get('median_spread_c')}¢ / {ph.get('w1_dip_prints_med')} | {part['both']}/{part['one']}/{part['none']} "
      f"| {tim.get('before',0)}/{tim.get('during',0)}/{tim.get('after',0)} ({miss}) "
      f"| {gapw}¢ ({ach}) | {cb['le97']}/{cb['98_100']}/{cb['gt100']} "
      f"| {guns.get('on',0)}/{guns.get('early',0)}/{guns.get('late',0)}/{guns.get('SILENT',0)} ({gv}) |")
A("")

# ---------- PER-CATEGORY ----------
A("---")
A("# PER-GAME ROWS — one row per concluded game, all raw columns")
A("")
A("Leg format: `SUF post@px(T-s/T-h) → fill px(T-s/T-h) | W1best px(sz,dur) gapW1 | CORbest px gapCOR | timing-verdict(miss) | grace` — unfilled legs show the block mechanism and where our bid sat at the dip.")
A("")
for c in CATS:
    gs = sorted([g for g in conc if g["cat"] == c], key=lambda g: g["ev"])
    if not gs: continue
    ph = phys.get(c, {})
    A(f"## {c} — {len(gs)} concluded ({len([g for g in games if g['cat']==c])} engaged)")
    A("")
    A(f"**Physics context: median book spread {ph.get('median_spread_c')}¢ (n={ph.get('n_spread')}); median W1-dip print count {ph.get('w1_dip_prints_med')} — a 3¢ paid-over-best here is {'thin-tape money' if (ph.get('median_spread_c') or 0)>=4 else 'a real miss on a tight book'}.**")
    A("")
    for g in gs:
        comb = g["combined"]
        combf = ("—" if comb is None else f"{comb}¢ [{'≤97' if comb<=97 else '98-100' if comb<=100 else '>100'}]")
        ach = f" best-achievable {g['best_achievable']}¢ (paid +{round(comb-g['best_achievable'],1)}¢)" if (comb and g.get("best_achievable")) else (f" best-achievable {g.get('best_achievable')}¢" if g.get("best_achievable") else "")
        gun = g.get("gun") or {}
        guns = (f"gun {gun.get('verdict')}"
                + (f" Δ{gun.get('delta_min')}m (latch {gun.get('latch_t')}, onset {gun.get('onset_t')}{' AMB' if gun.get('onset_amb') else ''})" if gun.get("delta_min") is not None else
                   f" (onset {gun.get('onset_t')}{' AMB' if gun.get('onset_amb') else ''}; shadow-would-fire {gun.get('shadow_would_fire')})" if gun.get("verdict")=="SILENT" else "")) if gun else "gun no-data"
        A(f"**{g['ev'].replace('KX','')}** | AX1 **{g['participation']}** | AX3 comb {combf}{ach} | AX4 {guns} | sched {g['sstart_t']} honest {g['hstart_t']} corridor {g['corridor_min']}m | results {g['results']}")
        for l in g["legs"]:
            w1b = l.get("w1_best"); crb = l.get("cor_best")
            w1s = f"W1best {w1b['px']}¢(sz{w1b['size_at']},{w1b['dur_s']}s)" if w1b else "W1best —"
            crs = f"CORbest {crb['px']}¢" if crb else "CORbest —"
            if l["fill_px"] is not None:
                A(f"  - {l['suf']}: post {l['post_px']}¢@Ts{l['post_Ts_min']}(Th{l['post_Th_min']}) → **fill {l['fill_px']}¢@Ts{l['fill_Ts_min']}(Th{l['fill_Th_min']})** | {w1s} gapW1 {l['gap_w1']} | {crs} gapCOR {l['gap_cor']} | {l['fill_vs_dip'] or 'no-dip-data'}({l['miss_min']}m) | grace {l['grace'] or '—'}")
            else:
                A(f"  - {l['suf']}: UNFILLED — {l['block']} | posts {l['n_posts']} first {l['post_px']}¢@Ts{l['post_Ts_min']} | {w1s} | {crs} | bid-at-dip {l['sat_at_dip']}¢ | cor-bid-lvl {l['cor_bid_lvl']}")
        A("")

    # rollup
    legs = [l for g in gs for l in g["legs"]]
    fl = [l for l in legs if l["fill_px"] is not None]
    ufl = [l for l in legs if l["fill_px"] is None]
    part = Counter(g["participation"].split("(")[0] for g in gs)
    combs = [g["combined"] for g in gs if g["combined"] is not None]
    gapw1 = [l["gap_w1"] for l in fl if l["gap_w1"] is not None]
    gapcr = [l["gap_cor"] for l in fl if l["gap_cor"] is not None]
    achg = [round(g["combined"]-g["best_achievable"],1) for g in gs if g["combined"] and g.get("best_achievable")]
    tim = Counter(l["fill_vs_dip"] for l in fl if l["fill_vs_dip"])
    blocks = Counter((l["block"] or "?").split("(")[0] for l in ufl)
    guns = Counter((g.get("gun") or {}).get("verdict","no-data") for g in gs)
    gviol = [(g["ev"], l["suf"], l["grace"]) for g in gs for l in g["legs"] if (l.get("grace") or "").startswith("VIOLATION")]
    A(f"**{c} ROLLUP** — participation both {part.get('both',0)}/{len(gs)} · one-sided {part.get('one',0)} · neither {part.get('neither',0)} (blocks: {dict(blocks)})")
    A(f"  · timing: before/during/after dip = {tim.get('before',0)}/{tim.get('during',0)}/{tim.get('after',0)}; |miss| med {med([abs(l['miss_min']) for l in fl if l['miss_min'] is not None])}m")
    A(f"  · price: paid-over-W1-best med {med(gapw1)}¢ p75 {p75(gapw1)}¢ (n={len(gapw1)}); over-corridor-best med {med(gapcr)}¢ (n={len(gapcr)}); achievable-vs-paid med {med(achg)}¢ (n={len(achg)})")
    A(f"  · combined: ≤97 {sum(1 for x in combs if x<=97)} / 98-100 {sum(1 for x in combs if 97<x<=100)} / >100 {sum(1 for x in combs if x>100)} (of {len(combs)} pairs)")
    A(f"  · gun: {dict(guns)} · grace violations: {len(gviol)} {gviol if gviol else ''}")
    A("")

open("ENTRY_CENSUS_20260706.md","w",encoding="utf-8").write("\n".join(out))
print(f"wrote ENTRY_CENSUS_20260706.md ({len(out)} lines) | concluded={len(conc)} open={len(open_g)} engaged={len(games)}")
for c in CATS:
    gs=[g for g in conc if g["cat"]==c]
    if gs: print(f"  {c}: {len(gs)} concluded")
