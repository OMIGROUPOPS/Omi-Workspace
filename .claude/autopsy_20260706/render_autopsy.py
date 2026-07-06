#!/usr/bin/env python3
"""Render the full autopsy report from autopsy_dump.json + exchange truth + mechanism work.
Writes AUTOPSY_20260706.md (full per-game spectrum, all six categories) and prints the
headline rollups to stdout."""
import json
from collections import defaultdict, Counter
from datetime import datetime, timezone, timedelta

ET = timezone(timedelta(hours=-4))
BOOT = 1783309839.0
GOAL = 97
def hm(e):
    try: return datetime.fromtimestamp(float(e), ET).strftime("%H:%M") if e else "?"
    except: return "?"

D = json.load(open("vps/autopsy_dump.json"))
games, unfilled, violations = D["games"], D["unfilled"], D["violations"]
cogm = {c["ev"]: c for c in json.load(open("cog_mechanisms.json")) if "mech" in c}

# --- rejoin ALL violations per event (walk_cap: ticker; cog: event) ---
ev_vio = defaultdict(list)
for v in violations:
    tk = v.get("ticker") or v.get("event") or ""
    ev = tk if tk.count("-") == 1 else tk.rsplit("-", 1)[0]
    ev_vio[ev].append(v)
for g in games:
    g["violations"] = ev_vio.get(g["ev"], [])
for u in unfilled:
    u["violations"] = ev_vio.get(u["ev"], [])

# --- exchange-truth ledger ---
fills = json.load(open("vps/autopsy_truth/fills_session.json"))
setts = json.load(open("vps/autopsy_truth/settlements_session.json"))
pos = json.load(open("vps/autopsy_truth/positions.json"))
CATP = {"KXATPMATCH":"ATP_MAIN","KXWTAMATCH":"WTA_MAIN","KXATPCHALLENGERMATCH":"ATP_CHALL",
        "KXWTACHALLENGERMATCH":"WTA_CHALL","KXITFMATCH":"ITF_M","KXITFWMATCH":"ITF_W"}
def cat_of(tk): return next((v for k,v in CATP.items() if tk.startswith(k)), "?")

session_tickers = set(f["ticker"] for f in fills)
led = defaultdict(lambda: defaultdict(float))
tk_cash = defaultdict(lambda: {"buys":0.0,"sells":0.0,"fees":0.0,"rev":None})
for f in fills:
    c = cat_of(f["ticker"])
    # yes_price_dollars is the YES trade price on BOTH buy-yes and sell-no (exit) rows —
    # verified end-to-end on MILHER-MIL (buy 5@81+5@78, exit sell 5@98, revenue 500c).
    px = float(f["yes_price_dollars"]); q = float(f["count_fp"]); fee = float(f["fee_cost"])
    cash = px*q
    t = tk_cash[f["ticker"]]
    if f["action"] == "buy": led[c]["buy_cost"] += cash; t["buys"] += cash
    else: led[c]["sell_proceeds"] += cash; t["sells"] += cash
    led[c]["fees"] += fee; t["fees"] += fee
    led[c]["fills_n"] += 1
sett_by_ev = defaultdict(float); carryover = 0.0; carry_n = 0
for s in setts:
    c = cat_of(s["ticker"])
    yq = float(s["yes_count_fp"]); nq = float(s["no_count_fp"])
    yc = float(s["yes_total_cost_dollars"]); nc = float(s["no_total_cost_dollars"])
    fee = float(s["fee_cost"])
    payout = float(s.get("revenue") or 0) / 100.0   # exchange-actual payout for the settled remainder (cents)
    if s["ticker"] not in session_tickers:
        carryover += payout - yc - nc - fee; carry_n += 1
        continue
    led[c]["settle_payout"] += payout
    led[c]["settle_cost"] += yc + nc
    led[c]["settle_fees"] += fee
    led[c]["settles_n"] += 1
    tk_cash[s["ticker"]]["rev"] = payout
    tk_cash[s["ticker"]]["fees"] += fee
    sett_by_ev[s["ticker"].rsplit("-",1)[0]] += payout - yc - nc - fee

# per-ticker exchange entry VWAP (buys only) — the true basis; adopted bookings are
# mark-to-market (live_v4.py:8290) and fabricate combined>97 on bound-priced orders
tk_vwap = defaultdict(lambda: [0.0, 0.0])
for f in fills:
    if f["action"] != "buy": continue
    tk_vwap[f["ticker"]][0] += float(f["yes_price_dollars"])*100*float(f["count_fp"])
    tk_vwap[f["ticker"]][1] += float(f["count_fp"])
def xvwap(tk):
    v = tk_vwap.get(tk)
    return round(v[0]/v[1], 1) if v and v[1] else None

# per-ticker exchange-truth lifetime P&L (settled tickers only)
def tk_pnl(tk):
    t = tk_cash.get(tk)
    if t is None or t["rev"] is None: return None   # open or untraded
    return t["rev"] + t["sells"] - t["buys"] - t["fees"]

# override leg pnl/outc with exchange truth; recompute grades with the same rubric
for g in games:
    for l in g["legs"]:
        xp = tk_pnl(l["tk"])
        if xp is not None:
            l["pnl"] = round(xp, 2)
            if l["outc"] == "OPEN": l["outc"] = "settle_API"
    g["any_open"] = any(l["outc"] == "OPEN" and tk_pnl(l["tk"]) is None for l in g["legs"])
    g["pnl"] = round(sum(l["pnl"] for l in g["legs"]), 2)
    # exchange-VWAP combined (true basis) replaces log-booked combined for grading
    if g["n_legs"] == 2:
        xs = [xvwap(l["tk"]) for l in g["legs"]]
        if None not in xs:
            g["combined_log"] = g["combined"]
            g["combined"] = round(xs[0] + xs[1], 1)
            for l, x in zip(g["legs"], xs): l["xfill"] = x
    # rubric re-run (mirrors autopsy_ftr.py, exchange pnl)
    legrows = g["legs"]; n = g["n_legs"]; combined = g["combined"]
    fvs = [x["fv_capture"] for x in legrows if x.get("fv_capture") is not None]
    pnl = g["pnl"]
    settled_loss = sum(x["pnl"] for x in legrows if x["outc"].startswith("settle") and x["pnl"] < 0)
    deepneg = [x for x in legrows if x.get("fv_capture") is not None and x["fv_capture"] <= -8]
    err = []; grade = "B"
    half = (n == 1); over_par = (combined is not None and combined > 100)
    anyopen = g["any_open"]
    if half:
        if any(x["outc"].startswith("settle") and x["pnl"] < 0 for x in legrows):
            grade = "F"; err.append("half-armed naked single -> settled LOSS")
        elif any(x["outc"] in ("exit_FILL","scalp_FILL") for x in legrows) and pnl >= 0:
            grade = "D"; err.append("half-armed naked single (exited green, luck-directional)")
        else:
            grade = "D"; err.append("half-armed naked single (open/held)")
    elif over_par and combined > 105:
        grade = "D"; err.append(f"combined {combined}c >>100")
    elif over_par:
        grade = "C"; err.append(f"combined {combined}c >100 over-par")
    elif combined is not None and combined > GOAL:
        grade = "C"; err.append(f"combined {combined}c > goal {GOAL} (zero cushion)")
    elif deepneg:
        grade = "C"; err.append(f"{len(deepneg)} leg deep-neg FV fragile")
    elif fvs and all(v <= 0 for v in fvs):
        grade = "C"; err.append("zero-discount pair")
    else:
        if fvs and all(v >= 0 for v in fvs) and combined is not None and combined <= 100:
            grade = "A" if pnl >= 0 or anyopen else "B"
        else:
            grade = "B"
    if not half and settled_loss < -1 and grade in ("A","B"):
        grade = "C"; err.append(f"directional hold settled -${abs(settled_loss):.2f}")
    if grade == "A" and not g.get("w1_shape"):
        grade = "B"; err.append("A->B: lacks W1 shape (Vault 0E gate)")
    g["grade"] = grade; g["err"] = err

# riser bar (a): fill discount vs best-bid-at-post (book_bid from last v4_place before fill)
vplace_seq = defaultdict(list)
for line in open("vps/session_since_boot.jsonl", encoding="utf-8"):
    if '"v4_place"' not in line: continue
    try: o = json.loads(line)
    except: continue
    if o.get("event") != "v4_place": continue
    tk = o.get("ticker"); d = o.get("details", {})
    if tk and d.get("book_bid") is not None:
        vplace_seq[tk].append((o.get("ts_epoch", 0), d["book_bid"]))
def bid_at_post(tk, fill_ts):
    cand = [b for t, b in vplace_seq.get(tk, []) if t <= fill_ts]
    return cand[-1] if cand else None
open_by_cat = defaultdict(float); open_n = defaultdict(int)
for p in pos:
    q = float(p.get("position_fp") or 0)
    if q == 0: continue
    c = cat_of(p["ticker"])
    open_by_cat[c] += float(p.get("market_exposure_dollars") or 0)
    open_n[c] += 1

# --- riser-revision scoreboard (pre-registered bars, SCOREBOARD_20260706.md) ---
riser_legs = [(g,l) for g in games for l in g["legs"] if l.get("side") == "riser"]
faller_legs = [(g,l) for g in games for l in g["legs"] if l.get("side") == "faller"]
r_daim = sorted(l["d_aim"] for _,l in riser_legs if isinstance(l.get("d_aim"), (int,float)))
def median(v): return v[len(v)//2] if v else None
# bar (a): best-bid-at-post minus fill, per riser leg (positive = filled below the bid = discount)
r_disc = sorted(bid_at_post(l["tk"], l["fill_ts"]) - l["fill"]
                for _, l in riser_legs
                if l.get("fill") is not None and bid_at_post(l["tk"], l["fill_ts"]) is not None)
# erosion: riser fill px > first posted px (walked up before filling)
eros = [1 if (l.get("posted_first_px") is not None and l.get("fill") is not None and l["fill"] > l["posted_first_px"]) else 0
        for _,l in riser_legs]
# retention: riser fills per category vs riser posts (unfilled riser-side tickers approximated via unfilled events legs)
riser_by_cat = Counter(g["cat"] for g,_ in riser_legs)

# --- damage decomposition ---
vio_events = set(ev_vio.keys())
vio_games = [g for g in games if g["ev"] in vio_events]
clean_games = [g for g in games if g["ev"] not in vio_events]
def pnl_split(gs):
    settled = [g for g in gs if not g["any_open"]]
    return (sum(g["pnl"] for g in settled), len(settled),
            sum(g["pnl"] for g in gs if g["any_open"]), len(gs)-len(settled))
cog_cushion = sum((c.get("l2_over_bound") or 0) for c in cogm.values())

# ================= RENDER =================
out = []
A = out.append
now = datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")
A(f"# FULL AUTOPSY — post-flip session (boot 2026-07-05 23:50:39 ET → {now})")
A("")
A("**Evidence precedence: CHRONOLOGICAL AUTHORITY — newer beats older; exchange truth beats bot log.**")
A(f"Window: first honest-clock session (`per_match_clock:true`, armed state 297a7086, deploy 6770a7c 07-05). ")
A(f"Data: {len(games)} games w/ fills · {len(unfilled)} engaged-unfilled · {len(fills)} exchange fill rows · {len(setts)} settlement rows · {len(violations)} zero-tolerance violations (monitor stream, dedup, ts≥boot).")
A("")
A("**Borrow mapping (exit configs): ITF_M borrows ATP_CHALL exit tables; ITF_W borrows WTA_CHALL exit tables** (live_v4 category borrow, unchanged tonight).")
A("")
A("## Letter definitions (verbatim, Vault §0E 2026-07-06 + §0A + error-ledger lineage 07-02)")
A("- **A** — requires the W1 shape: both legs filled in Window-1 (pregame, honest clock) at combined ≤97, at/near best fillable, AND both exits REACHED in W1 (cashed or touched). An entry structurally unable to reach its band pregame caps at B regardless of price.")
A("- **B** — both legs filled, no disqualifying flaw, but lacks the W1 shape (or minor price/timing flaw).")
A("- **C** — completed pair with a real flaw: combined >97 (zero cushion — NOT a locked loss below par; exits carry the burden, risk concentrated in the expensive favorite), or zero-discount/deep-negative FV, or a directional settled loss on a completed pair.")
A("- **D** — one-sided (naked single, open/held or luck-exited green) or combined >>100.")
A("- **F** — one-sided settled at a loss, or missed/blocked entirely (blocking mechanism named).")
A("")

# headline table
A("## HEADLINE — grades × categories × dollars (settled = fully-closed games, exchange truth)")
A("")
A("| cat | A | B | C | D | F | games | pairs≤97 | W1-cash legs | BOUHAR | vio | settled P&L | open games |")
A("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
tot = Counter(); tot_pnl = 0.0
for c in ["ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL","ITF_M","ITF_W"]:
    gs = [g for g in games if g["cat"] == c]
    if not gs: continue
    gr = Counter(g["grade"] for g in gs)
    pairs = [g for g in gs if g["n_legs"] == 2]
    le97 = sum(1 for g in pairs if (g["combined"] or 999) <= 97)
    legs_all = [l for g in gs for l in g["legs"]]
    w1c = sum(1 for l in legs_all if l["w1"] == "W1_CASHED")
    bou = sum(1 for g in gs if g["bouhar"])
    vio_n = sum(len(g["violations"]) for g in gs)
    sp, sn, op, on_ = pnl_split(gs)
    tot.update(gr); tot_pnl += sp
    A(f"| {c} | {gr['A']} | {gr['B']} | {gr['C']} | {gr['D']} | {gr['F']} | {len(gs)} | {le97}/{len(pairs)} | {w1c}/{len(legs_all)} | {bou} | {vio_n} | ${sp:.2f} (n={sn}) | {on_} |")
A(f"| **TOT** | {tot['A']} | {tot['B']} | {tot['C']} | {tot['D']} | {tot['F']} | {len(games)} | | | | {len(violations)} | ${tot_pnl:.2f} | |")
A("")

# exchange ledger
A("## EXCHANGE-TRUTH LEDGER (fills API + settlements API, never the bot log)")
A("")
A("| cat | fills | buy cost | sell proceeds | settle payout | settle cost | fees | **realized** | open exposure (cost) |")
A("|---|---|---|---|---|---|---|---|---|")
treal = 0.0
for c in ["ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL","ITF_M","ITF_W"]:
    l = led[c]
    if not l: continue
    realized = l["settle_payout"] - l["settle_cost"] - l["settle_fees"] - l["fees"] + l["sell_proceeds"] - (l["buy_cost"] - l["settle_cost"] - 0)
    # realized cash-flow view: sells + settle payouts - buys - fees (open cost stays on the book)
    cash = l["sell_proceeds"] + l["settle_payout"] - l["buy_cost"] - l["fees"] - l["settle_fees"]
    treal += cash
    A(f"| {c} | {int(l['fills_n'])} | ${l['buy_cost']:.2f} | ${l['sell_proceeds']:.2f} | ${l['settle_payout']:.2f} | ${l['settle_cost']:.2f} | ${l['fees']+l['settle_fees']:.2f} | ${cash:.2f} | ${open_by_cat[c]:.2f} ({open_n[c]}) |")
A(f"| **TOT** | {len(fills)} | | | | | | **${treal:.2f}** | ${sum(open_by_cat.values()):.2f} ({sum(open_n.values())}) |")
A("")
A(f"(cash view: sells + settlement payouts − buys − all fees, SESSION-SLATE ONLY — settlements joined to session-fill tickers; open positions carried at cost ${sum(open_by_cat.values()):.2f} across {sum(open_n.values())} tickers recover as they settle. Excluded: {carry_n} carryover settlements of PRE-BOOT inventory netting ${carryover:+.2f} — not tonight's slate.)")
A("")

# W1 scoreboard
A("## W1 SCOREBOARD — the money-machine metric (first night above zero, baseline was 0/257 legs)")
A("")
for c in ["ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL","ITF_M","ITF_W"]:
    legs_all = [l for g in games if g["cat"]==c for l in g["legs"]]
    if not legs_all: continue
    w1 = Counter(l["w1"] for l in legs_all)
    bou = sum(1 for g in games if g["cat"]==c and g["bouhar"])
    pairs = sum(1 for g in games if g["cat"]==c and g["n_legs"]==2)
    n = len(legs_all)
    A(f"- **{c}**: legs={n} W1_CASHED={w1['W1_CASHED']} ({100*w1['W1_CASHED']//max(1,n)}%) W1_REACHABLE={w1['W1_REACHABLE']} W2_ONLY={w1['W2_ONLY']} | BOUHAR pairs {bou}/{pairs}")
A("")

# riser scoreboard
A("## RISER-REVISION SCOREBOARD (pre-registered bars, SCOREBOARD_20260706.md 07-05)")
A("")
A(f"- riser legs filled: {len(riser_legs)} (by cat: {dict(riser_by_cat)}); faller legs: {len(faller_legs)}")
# CHALL/ITF-only bar (a), split by erosion (walked-up-before-fill)
ci = [(g,l) for g,l in riser_legs if g["cat"] in ("ATP_CHALL","WTA_CHALL","ITF_M","ITF_W")]
ci_rows = []
for g,l in ci:
    b = bid_at_post(l["tk"], l["fill_ts"])
    if b is None or l.get("fill") is None: continue
    er = l.get("posted_first_px") is not None and l["fill"] > l["posted_first_px"]
    ci_rows.append((b - l["fill"], er))
d_all = sorted(x for x,_ in ci_rows); d_ne = sorted(x for x,e in ci_rows if not e); d_er = sorted(x for x,e in ci_rows if e)
er_n = len(d_er)
A(f"- **(a) riser fill-discount vs best-bid-at-post (CHALL/ITF): median {median(d_all)}¢ (n={len(d_all)})** — bar ≥ +2¢; **DISARM RULE (pre-registered): median shift < 1¢ → the fix MISSED and comes out. RULE FIRES on the headline number.**")
A(f"  - split: NON-ERODED fills median {median(d_ne)}¢ (n={len(d_ne)}) — the conception-site revision itself posts at/near bar; ERODED fills median {median(d_er)}¢ (n={er_n}) — the walks destroy it")
A(f"- (a-aux) riser Δaim (fill − aim): median {median(r_daim)} on n={len(r_daim)} stamped riser fills")
A(f"- **(e) erosion: {er_n}/{len(ci_rows)} CHALL/ITF riser fills walked UP above first post before filling ({100*er_n//max(1,len(ci_rows))}%)** — bar <25%: **FAIL. Pre-registration names this exact failure: 'the walk/repost paths are eating the revision and the CONCEPTION-only scope was insufficient' → triggers the walk-cap follow-up build.**")
A(f"- Verdict per the pre-registered decision rule: (a) headline fails via (e)'s mechanism — the erosion bar was built to catch this. Disposition (disarm vs walk-cap follow-up) is the operator/Plex call; the evidence says the revision works where walks don't touch it.")
A("")

# monotonicity
A("## GRADE-vs-MONEY MONOTONICITY (fully-settled games)")
A("")
mono_viol = []
for c in ["ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL","ITF_M","ITF_W"]:
    gm_money = defaultdict(list)
    for g in games:
        if g["cat"] != c or g["any_open"]: continue
        gm_money[g["grade"]].append(g)
    means = []
    line = []
    for grd in "ABCDF":
        v = gm_money.get(grd, [])
        if v:
            m = sum(x["pnl"] for x in v)/len(v)
            means.append((grd, m)); line.append(f"{grd}:n={len(v)} mean=${m:.2f}")
    ok = all(means[i][1] >= means[i+1][1] for i in range(len(means)-1))
    A(f"- **{c}**: {' | '.join(line)} → {'MONOTONE' if ok else '**VIOLATED**'}")
    if not ok:
        # name offenders: best-pnl games in the worse grade above the better grade's mean
        for i in range(len(means)-1):
            if means[i][1] < means[i+1][1]:
                worse = means[i+1][0]; better = means[i][0]
                offenders = sorted(gm_money[worse], key=lambda x: -x["pnl"])[:3]
                offs = ", ".join("{} ${:.2f}".format(x["ev"].replace("KX",""), x["pnl"]) for x in offenders)
                A(f"    - {worse} outranks {better}; top {worse} winners: {offs}")
A("")

# per-category sections
A("---")
A("# PER-GAME SPECTRUM — one row per game, grade leads (no sampling)")
A("")
A("Row format: **GRADE | event | ①participation ②combined ③per-leg fill/aim/best/stamp ④timing (T-minus honest _Th_ / sched _Ts_ / gun _Tg_, dip verdict) ⑤W1 per leg + pair ⑥result $ (exchange) ⑦violations**")
A("")
def legfmt(l):
    b = l.get("best")
    bs = f"best {b['px']}c({b['dur_s']}s,sz{b['size']})@Th{b.get('Thon_min')}" if b else "best —"
    arr = l.get("arrived","")
    dv = f"Δbest {l.get('d_px_vs_best','—')}c/{l.get('d_t_vs_best_min','—')}m {arr}" if b else "no sell-flow tape"
    return (f"{l['suf']} {l['fill']}c(aim {l.get('aim')},Δ{l.get('d_aim')},{l.get('stamp') or 'PENDING'}) "
            f"fill Th{l.get('fill_Thon_min')}/Ts{l.get('fill_Tsched_min')}/Tg{l.get('fill_Tgun_min')} "
            f"post@{l.get('posted_first_px')}c Th{l.get('post_Thon_min')} {bs} {dv} "
            f"[{l['w1']}] → {l['outc']} ${l['pnl']:.2f}")
for c in ["ATP_MAIN","WTA_MAIN","ATP_CHALL","WTA_CHALL","ITF_M","ITF_W"]:
    gs = sorted([g for g in games if g["cat"] == c], key=lambda g: ("ABCDF".index(g["grade"]), -(g["pnl"] or 0)))
    if not gs and not any(u["cat"]==c for u in unfilled): continue
    borrow = {"ITF_M": " (ATP_CHALL exit config)", "ITF_W": " (WTA_CHALL exit config)"}.get(c, "")
    A(f"## {c}{borrow} — {len(gs)} games w/ fills")
    A("")
    gr = Counter(g["grade"] for g in gs)
    pairs = [g for g in gs if g["n_legs"]==2]
    le97 = sum(1 for g in pairs if (g["combined"] or 999) <= 97)
    w1c = sum(1 for g in gs for l in g["legs"] if l["w1"]=="W1_CASHED")
    vio_n = sum(len(g["violations"]) for g in gs)
    sp, sn, op, on_ = pnl_split(gs)
    A(f"**Rollup: grades A{gr['A']}/B{gr['B']}/C{gr['C']}/D{gr['D']}/F{gr['F']} · ≤97 rate {le97}/{len(pairs)} pairs · W1-cash legs {w1c} · violations {vio_n} · settled P&L ${sp:.2f} (n={sn}) · open-game partial ${op:.2f} (n={on_})**")
    A("")
    for g in gs:
        part = ("PAIR" if g["n_legs"]==2 else "ONE-SIDED")
        comb = g["combined"]
        combf = f"{comb}c {'≤97' if (comb or 999)<=97 else ('98-99' if comb<100 else '≥100')}" if comb else "—"
        if g.get("combined_log") is not None and abs(g["combined_log"] - comb) >= 1:
            combf += f" (log-booked {g['combined_log']}c — adoption mark-to-market artifact)"
        vio_s = "; ".join(f"{v['cls']}({(v.get('detail') or '')[:60]})" for v in g["violations"]) or "—"
        fav = ""
        if comb and comb >= 100 and g.get("legs") and len(g["legs"])==2:
            fv = max(g["legs"], key=lambda x: x["fill"] or 0)
            fav = f" | FAV {fv['suf']} fill {fv['fill']}c aim {fv.get('aim')} Δaim {fv.get('d_aim')} exit@{fv.get('exit_px')} band-dist {(fv.get('exit_px') or 0)-(fv.get('fill') or 0)}c"
        mech = cogm.get("KX"+g["ev"].replace("KX",""), None) or cogm.get(g["ev"].replace("KX",""))
        mech_s = f" | cog-mech {mech['mech']}" if mech else ""
        pairw1 = "BOUHAR" if g["bouhar"] else ("W1-shape" if g["w1_shape"] else "no-W1")
        A(f"**{g['grade']}** | {g['ev'].replace('KX','')} | ① {part} ② {combf}{fav} ⑤ {pairw1} ⑥ ${g['pnl']:.2f}{' OPEN' if g['any_open'] else ''} ⑦ {vio_s}{mech_s}")
        for l in g["legs"]:
            A(f"  - ③④ {legfmt(l)}")
        if g["fader"] and not g["fader"]["filled"]:
            fd = g["fader"]
            A(f"  - fader {fd['tk'].rsplit('-',1)[-1]} UNFILLED: bound {fd['bound']}c, cheapest pre-dip {fd['cheapest_pre_px']}c leak {fd['pre_leak_min']}m, in-time bound arrival: {fd['bound_arrived_in_time']}, starve {int((fd['starv_dur_s'] or 0)/60)}m/{fd['starv_sz']}sh")
        A("")
    # F-track engaged-unfilled for this category
    uns = [u for u in unfilled if u["cat"] == c]
    if uns:
        A(f"### {c} — F-track: engaged-but-unfilled ({len(uns)} events)")
        A("")
        for u in uns:
            legbits = []
            for l in u["legs"]:
                d = l.get("dip")
                dip_s = f" dip {d['dip_px']}c@{d['dip_t'][-8:]} ours@{d['lvl_at_dip']} {'REACHED-US' if d['dip_below_our_lvl'] else 'above us'}" if d else ""
                legbits.append(f"{l['tk'].rsplit('-',1)[-1]}: {l['n_posts']} posts {l['first_px']}→{l['last_px']}c, {l['n_cancels']} cancels{dip_s}")
            vio_s = "; ".join(v["cls"] for v in u.get("violations", [])) or ""
            A(f"**F(no-fill)** | {u['ev'].replace('KX','')} | honest {u.get('honest_t')} | " + " · ".join(legbits) + (f" ⑦ {vio_s}" if vio_s else ""))
        A("")

# never-engaged skip rollup (F-track completeness)
A("---")
A("## F-TRACK COMPLETENESS — never-engaged events (skipped, no bid ever posted)")
A("")
skip_ev = defaultdict(Counter)
engaged_evs = set(g["ev"] for g in games) | set(u["ev"] for u in unfilled)
for line in open("vps/session_since_boot.jsonl", encoding="utf-8"):
    if '"skipped"' not in line: continue
    try: o = json.loads(line)
    except: continue
    d = o.get("details", {})
    ev = d.get("event") or (o.get("ticker","").rsplit("-",1)[0] if o.get("ticker") else "")
    if not ev or ev in engaged_evs: continue
    skip_ev[ev][d.get("reason") or "unknown"] += 1
percat_sk = defaultdict(Counter)
for ev, cc in skip_ev.items():
    percat_sk[cat_of(ev + "-")][cc.most_common(1)[0][0]] += 1
A(f"{len(skip_ev)} events were tracked but never engaged (dominant blocking mechanism per event):")
for cat in sorted(percat_sk):
    A(f"- **{cat}**: " + ", ".join(f"{r} ×{n}" for r, n in percat_sk[cat].most_common()))
A("")
A("(skip_no_trade = book never printed a trade — no market to join; match_already_started = legacy-clock lateness at discovery. Neither is a defect-class miss; both named per F-track spec.)")
A("")

# damage decomposition
A("---")
A("## DAMAGE DECOMPOSITION — violation cost vs clean-trade P&L (attributed, not smeared)")
A("")
vs, vsn, vo, von = pnl_split(vio_games)
cs, csn, co, con = pnl_split(clean_games)
A(f"- games carrying violations: {len(vio_games)} → settled ${vs:.2f} (n={vsn}), open partial ${vo:.2f}")
A(f"- clean games: {len(clean_games)} → settled ${cs:.2f} (n={csn}), open partial ${co:.2f}")
A(f"- combined_over_goal cushion forfeited: {cog_cushion}c-over across {len(cogm)} pairs (each ×5-lot ≈ ${cog_cushion*5/100:.2f} extra basis vs goal)")
A("")

open("AUTOPSY_20260706.md","w",encoding="utf-8").write("\n".join(out))
print(f"wrote AUTOPSY_20260706.md ({len(out)} lines)")
print(f"headline: A{tot['A']} B{tot['B']} C{tot['C']} D{tot['D']} F{tot['F']} | settled(log-view) ${tot_pnl:.2f} | exchange cash ${treal:.2f} | open cost ${sum(open_by_cat.values()):.2f}")
print(f"vio games settled ${vs:.2f} (n={vsn}) vs clean settled ${cs:.2f} (n={csn})")
print(f"riser: n={len(riser_legs)} med d_aim={median(r_daim)} erosion={sum(eros)}/{len(eros)}")
