#!/usr/bin/env python3
"""[READ-ONLY] FULL-TAPE REGRADE — every trade in the current box, time as a first-class dimension.
Window: aba83af boot (1783215170.9, Jul 4 21:32:50 ET) -> now, logs live_v3_20260704 + 20260705.
Per game: exchange-truth final outcomes, per-leg full-tape flaw hunt (best fillable moment vs our
behavior in price AND time vs BOTH clocks), regrade A-F, money-left rollup, time map.
Writes /tmp/ftr_dump.json + /tmp/ftr_report.txt. NO writes to bot state. Run from arb-executor root."""
import json, time, base64, sys, os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter

ET = timezone(timedelta(hours=-4))
BOOT = 1783215170.9
MORNING_PASS_TS = 1783262394.0   # 10:39:54 ET Jul 5 restart = morning pass boundary
GOAL = 97
LOGS = ["logs/live_v3_20260704.jsonl", "logs/live_v3_20260705.jsonl"]
VALID = "/root/Omi-Workspace/.claude/live_20260705/live_validation.jsonl"
CAT = {"KXATPMATCH":"ATP_MAIN","KXWTAMATCH":"WTA_MAIN","KXATPCHALLENGERMATCH":"ATP_CHALL",
       "KXWTACHALLENGERMATCH":"WTA_CHALL","KXITFMATCH":"ITF_M","KXITFWMATCH":"ITF_W"}
def cat_of(tk): return next((v for k,v in CAT.items() if tk.startswith(k)), "?")
def hm(e):
    return datetime.fromtimestamp(e, ET).strftime("%m-%d %H:%M:%S") if e else "?"

# ---------- Kalshi REST (read-only) ----------
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import requests
pk = serialization.load_pem_private_key(Path("kalshi.pem").read_bytes(), password=None, backend=default_backend())
B = "https://api.elections.kalshi.com/trade-api/v2"
def sgn(m, p):
    ts = str(int(time.time()*1000)); sp = "/trade-api/v2"+p.split("?")[0]
    sig = pk.sign((ts+m+sp).encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY":"f3b064d1-a02e-42a4-b2b1-132834694d23","KALSHI-ACCESS-SIGNATURE":base64.b64encode(sig).decode(),"KALSHI-ACCESS-TIMESTAMP":ts}
def g(p):
    for _ in range(4):
        try: return requests.get(B+p, headers=sgn("GET", p), timeout=30).json()
        except Exception: time.sleep(0.5)
    return {}

# ---------- 1. LOG PARSE ----------
sched={}; wopen={}; bids=defaultdict(list); fills={}; exitp={}; exitfill={}; settledlog={}
latch={}; vplace={}; fvburst={}; cancels=defaultdict(list)
for LOG in LOGS:
    if not Path(LOG).exists(): continue
    for line in open(LOG, encoding="utf-8", errors="replace"):
        if '"event"' not in line: continue
        try: o = json.loads(line)
        except Exception: continue
        e = o.get("event"); tk = o.get("ticker") or ""; d = o.get("details", {}); ts = o.get("ts_epoch", 0)
        if e == "schedule_match":
            ev = d.get("event")
            if ev: sched[ev] = {"start": d.get("start_time"), "cat": d.get("category")}
        elif e == "window_open_set" and tk:
            if tk not in wopen or ts < wopen[tk][0]: wopen[tk] = (ts, d.get("price"))
        elif e == "order_placed" and d.get("action") == "buy" and tk and d.get("price") is not None:
            bids[tk].append((ts, d["price"]))
        elif e in ("order_canceled","order_cancelled","cancel_order") and tk:
            cancels[tk].append(ts)
        elif e == "v4_place" and tk:
            vplace[tk] = d
        elif e == "entry_filled" and tk:
            if tk not in fills and ts >= BOOT:
                fills[tk] = {"ts": ts, "fill": d.get("fill_price"), "dir": d.get("direction"),
                             "play": d.get("play_type"), "qty": d.get("qty") or 0}
        elif e == "v4_exit_posted" and tk:
            exitp[tk] = {"band_x": d.get("band_x"), "exit_price": d.get("exit_price"), "cell": d.get("cell_id")}
        elif e == "exit_filled" and tk:
            exitfill[tk] = {"pnl": d.get("pnl_cents"), "exit": d.get("exit_price"), "qty": d.get("qty"), "ts": ts}
        elif e == "settled" and tk:
            settledlog[tk] = {"settle": d.get("settle"), "pnl": d.get("pnl_cents"), "qty": d.get("settled_qty"), "ts": ts}
        elif e == "match_live_detected":
            ev = d.get("event")
            if ev and ev not in latch: latch[ev] = ts
        elif e == "fv_burst_anchor" and tk:
            fvburst[tk] = d
print(f"log parse: fills={len(fills)} bids_tk={len(bids)} sched={len(sched)} latch={len(latch)} exitfill={len(exitfill)} settled={len(settledlog)}", file=sys.stderr)

# ---------- 2. validation stream join (stamps / aim) ----------
vstamp={}
if Path(VALID).exists():
    for line in open(VALID, encoding="utf-8", errors="replace"):
        try: o = json.loads(line)
        except Exception: continue
        if o.get("type") in ("fill","fill_regrade") and o.get("ticker"):
            cur = vstamp.get(o["ticker"], {})
            cur.update({k: o[k] for k in ("stamp","side","chain","aim_level","fill_minus_aim","conception_cell","disc_vs_open") if o.get(k) is not None})
            vstamp[o["ticker"]] = cur
print(f"validation stamps: {len(vstamp)}", file=sys.stderr)

# ---------- 3. EXCHANGE TRUTH ----------
# 3a. /portfolio/fills since BOOT (authoritative)
api_fills = defaultdict(list); cursor=""; pages=0
while pages < 40:
    p = f"/portfolio/fills?limit=200&min_ts={int(BOOT)}" + (f"&cursor={cursor}" if cursor else "")
    r = g(p); pages += 1
    for f in r.get("fills", []):
        api_fills[f["ticker"]].append(f)
    cursor = r.get("cursor")
    if not cursor: break
api_n = sum(len(v) for v in api_fills.values())
print(f"exchange fills rows: {api_n} across {len(api_fills)} tickers ({pages} pages)", file=sys.stderr)

# 3b. market results for every ticker touched (batched)
touched = sorted(set(fills) | set(api_fills))
mkt={}
for i in range(0, len(touched), 90):
    chunk = ",".join(touched[i:i+90])
    r = g(f"/markets?tickers={chunk}&limit=100")
    for m in r.get("markets", []):
        mkt[m["ticker"]] = {"result": m.get("result"), "status": m.get("status"), "close": m.get("close_time")}
print(f"market meta: {len(mkt)}", file=sys.stderr)

# ---------- 4. TAPE ENGINE ----------
_dc={}
def pts(s):
    # "2026-07-05 01:26:27 AM" ET -> epoch, fast
    try:
        d, t, ap = s.split(" ")
        if d not in _dc:
            y, mo, dy = d.split("-")
            _dc[d] = datetime(int(y), int(mo), int(dy), tzinfo=ET).timestamp()
        hh, mm, ss = t.split(":")
        h = int(hh) % 12 + (12 if ap == "PM" else 0)
        return _dc[d] + h*3600 + int(mm)*60 + int(ss)
    except Exception:
        return None

def read_tape(tk):
    f = Path("analysis/trades") / (tk + ".csv")
    rows = []
    if not f.exists(): return rows
    with open(f, encoding="utf-8", errors="replace") as fh:
        next(fh, None)
        for ln in fh:
            p = ln.rstrip("\n").split(",")
            if len(p) < 5: continue
            t = pts(p[0])
            if t is None: continue
            try: rows.append((t, int(p[2]), int(float(p[3])), p[4]))
            except Exception: continue
    rows.sort(key=lambda r: r[0])
    return rows

def tape_gun(rows, w0=None, w1=None):
    """true tape onset from the trade tape (night-pass convention: search fill-1h -> fill+6h):
    first minute with vol>=150 whose fwd-10min vol>=3000; fallback max-vol minute; ambiguous
    if peak fwd-10min < 3000."""
    if w0 is not None:
        rows = [r for r in rows if w0 <= r[0] <= (w1 or 1e18)]
    if not rows: return None
    mv = defaultdict(float)
    for t, pr, ct, side in rows: mv[int(t//60)*60] += ct
    mins = sorted(mv)
    fwd = {}
    for m in mins:
        fwd[m] = sum(mv[x] for x in mins if m <= x < m+600)
    peak = max(fwd.values())
    gun_m = next((m for m in mins if mv[m] >= 150 and fwd[m] >= 3000), None)
    amb = peak < 3000
    if gun_m is None:
        gun_m = max(mins, key=lambda m: mv[m]); amb = True
    pre = [r for r in rows if r[0] < gun_m]
    final_tick = pre[-1][1] if pre else None
    return {"gun_ts": gun_m, "final_tick": final_tick, "ambiguous": amb, "settle_last": rows[-1][1]}

def dip_hunt(rows, t0, t1):
    """best fillable moment for a resting maker BID: sell-flow (taker_side==no) prints in [t0,t1].
    Returns best price, its first ts, size at level, dip window (<=best+1, gap<=300s) duration."""
    sf = [(t, pr, ct) for t, pr, ct, side in rows if side == "no" and t0 <= t <= t1]
    if not sf: return None
    best = min(pr for _, pr, _ in sf)
    bts = next(t for t, pr, _ in sf if pr == best)
    # contiguous dip window at <=best+1 containing bts (gap tolerance 300s)
    near = sorted((t, pr, ct) for t, pr, ct in sf if pr <= best + 1)
    lo = hi = bts
    for t, pr, ct in reversed([x for x in near if x[0] <= bts]):
        if lo - t <= 300: lo = t
        else: break
    for t, pr, ct in [x for x in near if x[0] >= bts]:
        if t - hi <= 300: hi = t
        else: break
    span = [x for x in near if lo <= x[0] <= hi]
    return {"price": best, "ts": bts, "size_at": sum(c for _, p, c in sf if p == best),
            "dip_lo": lo, "dip_hi": hi, "dur_s": hi - lo, "prints": len(span),
            "sz_win": sum(c for _, _, c in span)}

def lvl_at(tklist, t):
    lv = None
    for ts, p in tklist:
        if ts <= t: lv = p
        else: break
    return lv

def first_bid_ge(tklist, price, until):
    for ts, p in tklist:
        if ts <= until and p >= price: return ts
    return None

def parse_start(sstr):
    if not sstr: return None
    try:
        return datetime.fromisoformat(sstr.replace("Z", "+00:00")).timestamp()
    except Exception: pass
    for fmt in ("%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M:%SZ"):
        try: return datetime.strptime(sstr, fmt).replace(tzinfo=timezone.utc).timestamp()
        except Exception: pass
    return None

# ---------- 5. PER-GAME ASSEMBLY ----------
ev_fills = defaultdict(list)
for tk, f in fills.items():
    ev_fills[tk.rsplit("-", 1)[0]].append((tk, f))

def leg_outcome(tk, f):
    """final outcome from exchange truth first, log second."""
    if tk in exitfill:
        return "exit_FILL", (exitfill[tk]["pnl"] or 0)/100.0, exitfill[tk].get("ts")
    if tk in settledlog:
        return "settle_" + str(settledlog[tk]["settle"]), (settledlog[tk]["pnl"] or 0)/100.0, settledlog[tk].get("ts")
    m = mkt.get(tk, {})
    if m.get("result") in ("yes", "no"):
        q = f["qty"] or 0; fp = f["fill"] or 0
        pnl = q*(100-fp)/100.0 if m["result"] == "yes" else -q*fp/100.0
        return "settle_" + m["result"] + "_API", pnl, None
    return "OPEN", 0.0, None

games = []
tape_cache = {}
sorted_evs = sorted(ev_fills, key=lambda e: min(f["ts"] for _, f in ev_fills[e]))
for idx, ev in enumerate(sorted_evs):
    legs = sorted(ev_fills[ev], key=lambda x: x[1]["ts"])
    cat = cat_of(ev + "-")
    sstart = parse_start((sched.get(ev, {}) or {}).get("start"))
    lts = latch.get(ev)
    # sibling (unfilled) discovery
    sibs = set()
    for pool in (bids, wopen):
        for otk in pool:
            if otk.rsplit("-", 1)[0] == ev: sibs.add(otk)
    unfilled_sibs = [t for t in sibs if t not in fills]
    all_tks = [tk for tk, _ in legs] + unfilled_sibs
    leg1_ts0 = legs[0][1]["ts"]
    guns = {}
    for tk in all_tks:
        if tk not in tape_cache: tape_cache[tk] = read_tape(tk)
        anchor = fills[tk]["ts"] if tk in fills else leg1_ts0
        if tape_cache[tk]: guns[tk] = tape_gun(tape_cache[tk], anchor - 3600, anchor + 6*3600)
    # event-level true onset = earliest unambiguous gun across legs
    ev_gun = None
    for tk, gi in guns.items():
        if gi and not gi["ambiguous"]:
            ev_gun = gi["gun_ts"] if ev_gun is None else min(ev_gun, gi["gun_ts"])
    if ev_gun is None:
        cand = [gi["gun_ts"] for gi in guns.values() if gi]
        ev_gun = min(cand) if cand else None
    entry_end = lts or ev_gun or sstart or (legs[-1][1]["ts"] + 3600)

    leg1_ts = legs[0][1]["ts"]
    combined = sum(x[1]["fill"] or 0 for x in legs) if len(legs) >= 2 else None
    legrows = []
    for li, (tk, f) in enumerate(legs):
        rows = tape_cache.get(tk, [])
        gi = guns.get(tk)
        tkl = sorted(bids.get(tk, []))
        t0 = (wopen.get(tk) or (tkl[0][0] if tkl else f["ts"]-6*3600, None))[0]
        end = max(entry_end, f["ts"])  # the moment window truly closed for this leg
        dip = dip_hunt(rows, t0, min(end, f["ts"])) if rows else None
        dip_full = dip_hunt(rows, t0, end) if rows else None
        outc, pnl, ots = leg_outcome(tk, f)
        vs = vstamp.get(tk, {})
        fv_onset = None
        if gi: fv_onset = gi["final_tick"] if gi["ambiguous"] else (gi["final_tick"])
        # fv_capture per on3 convention: onset price - fill (use final_tick = last pre-gun print)
        fvcap = (fv_onset - f["fill"]) if (fv_onset is not None and f["fill"] is not None) else None
        d = {"tk": tk, "suf": tk.rsplit("-",1)[-1], "leg_i": li+1, "fill": f["fill"], "qty": f["qty"],
             "fill_ts": f["ts"], "fill_t": hm(f["ts"]), "dir": f["dir"], "play": f["play"],
             "outc": outc, "pnl": round(pnl,2), "outc_ts": ots,
             "finalized_after_morning": bool(ots and ots > MORNING_PASS_TS) or outc.endswith("_API"),
             "stamp": vs.get("stamp"), "side": vs.get("side"), "aim": vs.get("aim_level"),
             "d_aim": vs.get("fill_minus_aim"), "chain": vs.get("chain"),
             "fv_capture": fvcap, "emfb": fvburst.get(tk,{}).get("entry_minus_fv_burst"),
             "gun_ts": gi["gun_ts"] if gi else None, "gun_amb": gi["ambiguous"] if gi else None,
             "posted_first_ts": tkl[0][0] if tkl else None, "posted_first_px": tkl[0][1] if tkl else None,
             "n_posts": len(tkl)}
        # timing vs both clocks
        d["fill_Tsched_min"] = round((sstart - f["ts"])/60,1) if sstart else None
        d["fill_Tgun_min"] = round((ev_gun - f["ts"])/60,1) if ev_gun else None
        d["post_Tsched_min"] = round((sstart - tkl[0][0])/60,1) if (sstart and tkl) else None
        d["post_Tgun_min"] = round((ev_gun - tkl[0][0])/60,1) if (ev_gun and tkl) else None
        if dip:
            arr = first_bid_ge(tkl, dip["price"], dip["dip_hi"])
            d["best"] = {"px": dip["price"], "ts": dip["ts"], "t": hm(dip["ts"]),
                         "Tsched_min": round((sstart - dip["ts"])/60,1) if sstart else None,
                         "Tgun_min": round((ev_gun - dip["ts"])/60,1) if ev_gun else None,
                         "size": dip["size_at"], "dur_s": int(dip["dur_s"]), "prints": dip["prints"],
                         "catchable": dip["dur_s"] >= 90 or dip["prints"] >= 3}
            d["d_px_vs_best"] = (f["fill"] - dip["price"]) if f["fill"] is not None else None
            d["d_t_vs_best_min"] = round((f["ts"] - dip["ts"])/60,1)
            d["lvl_at_dip"] = lvl_at(tkl, dip["ts"])
            d["arrived_ts"] = arr
            d["arrived"] = ("before_dip" if (arr and arr <= dip["dip_lo"]) else
                            "during_dip" if (arr and arr <= dip["dip_hi"]) else
                            "after_dip" if arr else "never_reached_level")
        else:
            d["best"] = None
        d["best_full"] = ({"px": dip_full["price"], "t": hm(dip_full["ts"]),
                           "Tsched_min": round((sstart - dip_full["ts"])/60,1) if sstart else None}
                          if dip_full else None)
        legrows.append(d)

    # fader analysis: the second leg (or the unfilled sibling) vs the bound set by leg-1
    fader = None
    basis = legs[0][1]["fill"] or 0
    bound = GOAL - basis
    fader_tk = legs[1][0] if len(legs) >= 2 else (unfilled_sibs[0] if unfilled_sibs else None)
    if fader_tk:
        rows = tape_cache.get(fader_tk, [])
        sf_all = [(t, pr, ct) for t, pr, ct, s in rows if s == "no"]
        pre = [(t, pr, ct) for t, pr, ct in sf_all if t < leg1_ts]
        post = [(t, pr, ct) for t, pr, ct in sf_all if leg1_ts <= t <= entry_end]
        cheap_pre = min(pre, key=lambda x: x[1]) if pre else None
        cheap_post = min(post, key=lambda x: x[1]) if post else None
        tkl = sorted(bids.get(fader_tk, []))
        # starvation: prints at <= our resting level while unfilled
        starv_s = 0; starv_sz = 0
        if tkl and fader_tk not in fills:
            hits = [(t, pr, ct) for t, pr, ct in sf_all
                    if (lvl_at(tkl, t) is not None and pr <= lvl_at(tkl, t)) and t <= entry_end]
            if hits:
                starv_s = int(hits[-1][0] - hits[0][0]); starv_sz = sum(c for _,_,c in hits)
        fader = {"tk": fader_tk, "filled": fader_tk in fills, "bound": bound,
                 "cheapest_pre_px": cheap_pre[1] if cheap_pre else None,
                 "cheapest_pre_t": hm(cheap_pre[0]) if cheap_pre else None,
                 "cheapest_pre_ts": cheap_pre[0] if cheap_pre else None,
                 "pre_leak_min": round((leg1_ts - cheap_pre[0])/60,1) if cheap_pre else None,
                 "pre_dip_le_bound": bool(cheap_pre and cheap_pre[1] <= bound),
                 "cheapest_post_px": cheap_post[1] if cheap_post else None,
                 "cheapest_post_t": hm(cheap_post[0]) if cheap_post else None,
                 "bound_arrived_in_time": bool(cheap_post and cheap_post[1] <= bound),
                 "starv_dur_s": starv_s, "starv_sz": starv_sz}

    # ---- regrade (grade3 rubric, final outcomes) ----
    n = len(legs); fvs = [x["fv_capture"] for x in legrows if x["fv_capture"] is not None]
    pnl = sum(x["pnl"] for x in legrows)
    settled_loss = sum(x["pnl"] for x in legrows if x["outc"].startswith("settle") and x["pnl"] < 0)
    deepneg = [x for x in legrows if x["fv_capture"] is not None and x["fv_capture"] <= -8]
    err = []; forfeit = 0.0; grade = "B"
    half = (n == 1); over_par = (combined is not None and combined > 100)
    anyopen = any(x["outc"] == "OPEN" for x in legrows)
    if half:
        if any(x["outc"].startswith("settle") and x["pnl"] < 0 for x in legrows):
            grade = "F"; err.append("half-armed naked single -> settled LOSS"); forfeit = abs(settled_loss)
        elif any(x["outc"] == "exit_FILL" for x in legrows) and pnl >= 0:
            grade = "D"; err.append("half-armed naked single (exited green, luck-directional)")
        else:
            grade = "D"; err.append("half-armed naked single (open/held)")
    elif over_par and combined > 105:
        grade = "D"; err.append(f"combined {combined}c >>100"); forfeit = combined-100
    elif over_par:
        grade = "C"; err.append(f"combined {combined}c >100 over-par"); forfeit = combined-100
    elif deepneg:
        grade = "C"; err.append(f"{len(deepneg)} leg deep-neg FV fragile"); forfeit = sum(abs(x["fv_capture"]) for x in deepneg)
    elif fvs and all(v <= 0 for v in fvs):
        grade = "C"; err.append("zero-discount pair"); forfeit = sum(abs(v) for v in fvs if v < 0)
    else:
        if fvs and all(v >= 0 for v in fvs) and combined is not None and combined <= 100:
            grade = "A" if pnl >= 0 or anyopen else "B"
        else:
            grade = "B"
    if not half and settled_loss < -1 and grade in ("A","B"):
        grade = "C"; err.append(f"directional hold settled -${abs(settled_loss):.2f}"); forfeit = max(forfeit, abs(settled_loss))

    # ---- money left on table ----
    molt = {}
    for x in legrows:
        if x.get("d_px_vs_best") and x["d_px_vs_best"] > 0 and x["best"] and x["best"]["catchable"]:
            molt["fill_above_best"] = molt.get("fill_above_best", 0) + x["d_px_vs_best"] * (x["qty"] or 0)
    if fader and not fader["filled"]:
        dips = [p for p in (fader["cheapest_pre_px"], fader["cheapest_post_px"]) if p is not None]
        if dips and min(dips) <= bound:
            lock = (100 - (basis + min(dips))) * (legs[0][1]["qty"] or 0)
            molt["forfeited_completion"] = max(lock, 0)
    games.append({"ev": ev, "cat": cat, "grade": grade, "err": err, "forfeit": round(forfeit,1),
                  "combined": combined, "pnl": round(pnl,2), "n_legs": n,
                  "sched_start": sstart, "sched_t": hm(sstart) if sstart else None,
                  "gun_ts": ev_gun, "gun_t": hm(ev_gun) if ev_gun else None,
                  "gun_vs_sched_min": round((ev_gun - sstart)/60,1) if (ev_gun and sstart) else None,
                  "latch_ts": lts, "legs": legrows, "fader": fader, "molt": molt,
                  "any_open": anyopen})
    if idx % 10 == 0: print(f"..{idx}/{len(sorted_evs)} {ev}", file=sys.stderr)

# ---------- 6. ROLLUPS ----------
rep = open("/tmp/ftr_report.txt", "w", encoding="utf-8")
def W(s=""): rep.write(s + "\n")
now_et = datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")
W(f"FULL-TAPE REGRADE — window {hm(BOOT)} -> {now_et} | games={len(games)} legs={sum(g['n_legs'] for g in games)}")
W(f"exchange fills rows: {api_n} | market meta fetched: {len(mkt)}")

# grade distribution + monotonicity (settled-only)
gc = defaultdict(lambda: defaultdict(int)); tt = defaultdict(int)
for gm in games: gc[gm["cat"]][gm["grade"]] += 1; tt[gm["grade"]] += 1
W("\n== GRADE DISTRIBUTION (final, regraded) ==")
W(f"{'cat':10s} {'A':>3}{'B':>3}{'C':>3}{'D':>3}{'F':>3}  tot")
for c in sorted(gc):
    r = gc[c]; W(f"{c:10s} {r['A']:>3}{r['B']:>3}{r['C']:>3}{r['D']:>3}{r['F']:>3}  {sum(r.values())}")
W(f"{'TOTAL':10s} {tt['A']:>3}{tt['B']:>3}{tt['C']:>3}{tt['D']:>3}{tt['F']:>3}  {sum(tt.values())}")

W("\n== GRADE vs MONEY MONOTONICITY (settled/exited-only games, no OPEN legs) ==")
gm_money = defaultdict(list)
for gm in games:
    if gm["any_open"]: continue
    gm_money[gm["grade"]].append(gm["pnl"])
for grd in "ABCDF":
    v = gm_money.get(grd, [])
    if v: W(f"  {grd}: n={len(v):>3} total=${sum(v):>8.2f} mean=${sum(v)/len(v):>6.2f}")
mono = [sum(v)/len(v) for grd in "ABCDF" for v in [gm_money.get(grd, [])] if v]
W(f"  monotone A->F: {'YES' if all(mono[i] >= mono[i+1] for i in range(len(mono)-1)) else 'NO'} ({['%.2f'%x for x in mono]})")

# regrade deltas: which games finalized after the morning pass
W("\n== FINALIZED SINCE MORNING PASS (outcome landed after 10:39 ET) ==")
nf = 0
for gm in games:
    fl = [x for x in gm["legs"] if x["finalized_after_morning"]]
    if fl:
        nf += 1
        W(f"  [{gm['grade']}] {gm['ev'].replace('KX','')} {gm['cat']} pnl${gm['pnl']:.2f} " +
          " | ".join(f"{x['suf']}:{x['outc']}(${x['pnl']:.2f})" for x in fl))
W(f"  games with post-morning finalizations: {nf}")

# money left on table
W("\n== MONEY LEFT ON THE TABLE (ranked) ==")
molt_agg = defaultdict(float); molt_n = defaultdict(int)
for gm in games:
    for k, v in gm["molt"].items():
        molt_agg[k] += v/100.0; molt_n[k] += 1
for k, v in sorted(molt_agg.items(), key=lambda x: -x[1]):
    W(f"  ${v:>8.2f}  {molt_n[k]:>3} games  {k}")

# ---------- TIME MAP ----------
BUCKETS = [(1e9,480,">8h"),(480,360,"8-6h"),(360,240,"6-4h"),(240,180,"4-3h"),(180,120,"3-2h"),
           (120,60,"2-1h"),(60,30,"1h-30m"),(30,20,"30-20m"),(20,0,"20m-0"),(0,-1e9,"post")]
def bkt(tmin):
    if tmin is None: return None
    for hi, lo, lab in BUCKETS:
        if lo < tmin <= hi: return lab
    return None
W("\n== TIME MAP — when the money lives vs when we act (per category) ==")
for clock in ("Tsched", "Tgun"):
    W(f"\n-- clock: {clock} (minutes before {'scheduled start' if clock=='Tsched' else 'true tape onset'}) --")
    for c in sorted(set(g["cat"] for g in games)):
        best_h = Counter(); post_h = Counter(); fill_h = Counter()
        for gm in games:
            if gm["cat"] != c: continue
            for x in gm["legs"]:
                if x["best"]: best_h[bkt(x["best"][clock+"_min"])] += 1
                post_h[bkt(x[f"post_{clock}_min"])] += 1
                fill_h[bkt(x[f"fill_{clock}_min"])] += 1
        W(f"{c}:")
        W(f"  {'bucket':>7} {'BEST':>5} {'POST':>5} {'FILL':>5}")
        for _,_,lab in BUCKETS:
            if best_h.get(lab) or post_h.get(lab) or fill_h.get(lab):
                W(f"  {lab:>7} {best_h.get(lab,0):>5} {post_h.get(lab,0):>5} {fill_h.get(lab,0):>5}")

# ---------- per-game one-row table ----------
W("\n== ONE ROW PER GAME (every tracked metric) ==")
hdr = ("grade|ev|cat|comb|pnl$|legs|leg1(fill@T-sched/T-gun,best@T,dpx,dt_min,dur_s,arr)|leg2(same)|"
       "fader(cheapest_pre@T,leak_min,bound,in_time,starv_min)|stamps|d_aims|fv_caps|molt")
W(hdr)
def legcell(x):
    if not x: return "-"
    b = x["best"]
    bs = f"best{b['px']}@{b['t'][-8:]}(T-g{b['Tgun_min']}m,{b['dur_s']}s,sz{b['size']})" if b else "best?"
    return (f"{x['fill']}c@{x['fill_t'][-8:]}(Ts{x['fill_Tsched_min']}/Tg{x['fill_Tgun_min']}) {bs} "
            f"d{x.get('d_px_vs_best','?')}c/{x.get('d_t_vs_best_min','?')}m {x.get('arrived','')}")
for gm in sorted(games, key=lambda g: (g["cat"], "ABCDF".index(g["grade"]), g["ev"])):
    l1 = legcell(gm["legs"][0]); l2 = legcell(gm["legs"][1]) if gm["n_legs"] > 1 else "-"
    fd = gm["fader"]
    fds = (f"pre{fd['cheapest_pre_px']}@{(fd['cheapest_pre_t'] or '?')[-8:]} leak{fd['pre_leak_min']}m "
           f"bnd{fd['bound']} {'INTIME' if fd['bound_arrived_in_time'] else 'LATE/NO'} "
           f"starv{round((fd['starv_dur_s'] or 0)/60)}m") if fd else "-"
    st = ",".join(str(x.get("stamp") or "?") for x in gm["legs"])
    da = ",".join(str(x.get("d_aim")) for x in gm["legs"])
    fv = ",".join(str(round(x["fv_capture"])) if x["fv_capture"] is not None else "?" for x in gm["legs"])
    mo = ";".join(f"{k}={v/100:.2f}$" for k, v in gm["molt"].items())
    W(f"{gm['grade']}|{gm['ev'].replace('KX','')}|{gm['cat']}|{gm['combined']}|{gm['pnl']}|{gm['n_legs']}|{l1}|{l2}|{fds}|{st}|{da}|{fv}|{mo}")

# ---------- English flaw lines (sub-A) ----------
W("\n== THE FLAW IN ENGLISH — one line per sub-A game ==")
def tmin_str(m):
    if m is None: return "T-?"
    if m < 0: return f"T+{abs(m):.0f}m"
    h = int(m // 60); mm = int(m % 60)
    return f"T-{h}h{mm:02d}m" if h else f"T-{mm}m"
for gm in sorted(games, key=lambda g: ("ABCDF".index(g["grade"]), g["cat"])):
    if gm["grade"] == "A": continue
    name = gm["ev"].replace("KX", "").replace("MATCH", " ")
    bits = []
    for x in gm["legs"]:
        b = x["best"]
        if b and x.get("d_px_vs_best") is not None and x["d_px_vs_best"] > 0:
            bits.append(f"{x['suf']}'s best print was {b['px']}c for {b['dur_s']}s (sz {b['size']}) at "
                        f"{tmin_str(b['Tgun_min'])} vs gun / {tmin_str(b['Tsched_min'])} sched; we filled "
                        f"{x['fill']}c {x['d_t_vs_best_min']:.0f}m later ({x.get('arrived','')})")
    fd = gm["fader"]
    if fd and fd.get("pre_dip_le_bound") and not fd["filled"]:
        bits.append(f"fader {fd['tk'].rsplit('-',1)[-1]} printed {fd['cheapest_pre_px']}c at {fd['cheapest_pre_t']}, "
                    f"{fd['pre_leak_min']:.0f}m BEFORE leg-1 set the bound {fd['bound']}c — nothing was aimed at it")
    elif fd and not fd["filled"] and fd.get("starv_dur_s", 0) > 300:
        bits.append(f"fader {fd['tk'].rsplit('-',1)[-1]} starved {fd['starv_dur_s']//60}m while {fd['starv_sz']} shares printed at/below our level")
    W(f"[{gm['grade']}] {name} ({gm['cat']}, comb {gm['combined']}, ${gm['pnl']:.2f}): " +
      ("; ".join(bits) if bits else "; ".join(gm["err"]) or "no tape-visible flaw"))

rep.close()
json.dump({"boot": BOOT, "generated": now_et, "games": games},
          open("/tmp/ftr_dump.json", "w"), default=str)
print("DONE ->/tmp/ftr_report.txt /tmp/ftr_dump.json", file=sys.stderr)
