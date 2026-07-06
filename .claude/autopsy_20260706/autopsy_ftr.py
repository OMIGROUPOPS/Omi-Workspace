#!/usr/bin/env python3
"""[READ-ONLY] AUTOPSY FULL-TAPE REGRADE — post-flip session (boot 2026-07-05 23:50:39 ET).
Adapted from .claude/nightly_20260705/full_tape_regrade.py (C45 prior art) with four additions:
  1. W1 overlay integrated (Vault §0E, honest clock from state/schedule.json)
  2. zero-tolerance violations joined per game (live_validation.jsonl, ts>=BOOT)
  3. C-row expensive-favorite columns (fav fill-vs-aim + exit-band distance)
  4. F-track rows for engaged-but-unfilled events (posted bids, no fill)
Run from /root/Omi-Workspace/arb-executor. Writes /tmp/autopsy_dump.json + /tmp/autopsy_report.txt.
NO writes to bot state."""
import json, time, base64, sys, re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter

ET = timezone(timedelta(hours=-4))
BOOT = 1783309839.0            # 2026-07-05 23:50:39 ET per POST_FLIP_AUDIT
GOAL = 97
LOGS = ["/tmp/session_since_boot.jsonl"]
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

# ---------- honest clock (w1_grading.py convention) ----------
sch = json.load(open("state/schedule.json"))["schedule"]
def honest_start(ev):
    m = re.search(r"\d{2}[A-Z]{3}\d{2}([A-Z]{6})$", ev)
    if not m: return None
    pc = m.group(1)
    for k in (pc, pc[3:] + pc[:3]):
        e = sch.get(k)
        if e and not e.get("espn_midnight"):
            try: return datetime.fromisoformat(e["start_time"].replace("Z", "+00:00")).timestamp()
            except Exception: pass
    return None

# ---------- 1. LOG PARSE ----------
sched={}; wopen={}; bids=defaultdict(list); fills={}; exitp={}; exitfill={}; settledlog={}
latch={}; vplace={}; fvburst={}; cancels=defaultdict(list); refsrc=defaultdict(Counter)
scalp={}
for LOG in LOGS:
    if not Path(LOG).exists(): continue
    for line in open(LOG, encoding="utf-8", errors="replace"):
        if '"event"' not in line: continue
        try: o = json.loads(line)
        except Exception: continue
        e = o.get("event"); tk = o.get("ticker") or ""; d = o.get("details", {}); ts = o.get("ts_epoch", 0)
        if ts < BOOT: continue
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
            rs = d.get("reference_source") or d.get("ref_source")
            if rs: refsrc[tk][rs] += 1
        elif e == "entry_filled" and tk:
            if tk not in fills:
                fills[tk] = {"ts": ts, "fill": d.get("fill_price"), "dir": d.get("direction"),
                             "play": d.get("play_type"), "qty": d.get("qty") or 0}
        elif e == "v4_exit_posted" and tk:
            exitp[tk] = {"band_x": d.get("band_x"), "exit_price": d.get("exit_price"), "cell": d.get("cell_id")}
        elif e == "exit_filled" and tk:
            exitfill[tk] = {"pnl": d.get("pnl_cents"), "exit": d.get("exit_price"), "qty": d.get("qty"), "ts": ts}
        elif e == "scalp_filled" and tk:
            scalp[tk] = {"ts": ts, "pnl": d.get("pnl_cents")}
        elif e == "settled" and tk:
            settledlog[tk] = {"settle": d.get("settle"), "pnl": d.get("pnl_cents"), "qty": d.get("settled_qty"), "ts": ts}
        elif e == "match_live_detected":
            ev = d.get("event")
            if ev and ev not in latch: latch[ev] = ts
        elif e == "fv_burst_anchor" and tk:
            fvburst[tk] = d
print(f"log parse: fills={len(fills)} bids_tk={len(bids)} sched={len(sched)} latch={len(latch)} exitfill={len(exitfill)} settled={len(settledlog)}", file=sys.stderr)

# ---------- 2. validation stream join (stamps / aim / VIOLATIONS) ----------
vstamp={}; violations=[]
if Path(VALID).exists():
    seen_vio=set()
    for line in open(VALID, encoding="utf-8", errors="replace"):
        try: o = json.loads(line)
        except Exception: continue
        if o.get("type") in ("fill","fill_regrade") and o.get("ticker"):
            cur = vstamp.get(o["ticker"], {})
            cur.update({k: o[k] for k in ("stamp","side","chain","aim_level","fill_minus_aim","conception_cell","disc_vs_open") if o.get(k) is not None})
            vstamp[o["ticker"]] = cur
        elif o.get("type") == "violation" and (o.get("ts") or 0) >= BOOT:
            if o.get("key") in seen_vio: continue
            seen_vio.add(o.get("key"))
            violations.append(o)
print(f"validation stamps: {len(vstamp)} | session violations: {len(violations)}", file=sys.stderr)

# ---------- 3. EXCHANGE TRUTH ----------
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

touched = sorted(set(fills) | set(api_fills))
mkt={}
for i in range(0, len(touched), 90):
    chunk = ",".join(touched[i:i+90])
    r = g(f"/markets?tickers={chunk}&limit=100")
    for m in r.get("markets", []):
        mkt[m["ticker"]] = {"result": m.get("result"), "status": m.get("status"), "close": m.get("close_time")}
print(f"market meta: {len(mkt)}", file=sys.stderr)

# ---------- 4. TAPE ENGINE (verbatim from full_tape_regrade.py) ----------
_dc={}
def pts(s):
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
    sf = [(t, pr, ct) for t, pr, ct, side in rows if side == "no" and t0 <= t <= t1]
    if not sf: return None
    best = min(pr for _, pr, _ in sf)
    bts = next(t for t, pr, _ in sf if pr == best)
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
ev_vio = defaultdict(list)
for v in violations:
    tk = v.get("ticker") or ""
    ev = tk if tk.count("-") == 1 else tk.rsplit("-", 1)[0]
    ev_vio[ev].append({"cls": v.get("cls"), "ts": v.get("ts"), "t": hm(v.get("ts")),
                       "price": v.get("price"), "conception_cell": v.get("conception_cell"),
                       "ceiling": v.get("ceiling"), "ref_source": v.get("ref_source"),
                       "detail": v.get("detail")})

def leg_outcome(tk, f):
    if tk in exitfill:
        return "exit_FILL", (exitfill[tk]["pnl"] or 0)/100.0, exitfill[tk].get("ts")
    if tk in scalp:
        return "scalp_FILL", (scalp[tk]["pnl"] or 0)/100.0, scalp[tk].get("ts")
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
    hstart = honest_start(ev)
    lts = latch.get(ev)
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
        end = max(entry_end, f["ts"])
        dip = dip_hunt(rows, t0, min(end, f["ts"])) if rows else None
        dip_full = dip_hunt(rows, t0, end) if rows else None
        outc, pnl, ots = leg_outcome(tk, f)
        vs = vstamp.get(tk, {})
        fv_onset = None
        if gi: fv_onset = gi["final_tick"]
        fvcap = (fv_onset - f["fill"]) if (fv_onset is not None and f["fill"] is not None) else None
        # W1 overlay (Vault 0E): honest clock
        w1 = "W2_ONLY"; exit_px = exitp.get(tk, {}).get("exit_price")
        if exit_px is None and f.get("fill") is not None and exitp.get(tk, {}).get("band_x") is not None:
            exit_px = f["fill"] + exitp[tk]["band_x"]
        if hstart and f.get("fill") is not None and f["ts"] < hstart:
            if outc in ("exit_FILL","scalp_FILL") and ots and ots < hstart:
                w1 = "W1_CASHED"
            elif exit_px is not None and any(t < hstart and px >= exit_px for t, px, _, _ in rows):
                w1 = "W1_REACHABLE"
        d = {"tk": tk, "suf": tk.rsplit("-",1)[-1], "leg_i": li+1, "fill": f["fill"], "qty": f["qty"],
             "fill_ts": f["ts"], "fill_t": hm(f["ts"]), "dir": f["dir"], "play": f["play"],
             "outc": outc, "pnl": round(pnl,2), "outc_ts": ots, "w1": w1, "exit_px": exit_px,
             "stamp": vs.get("stamp"), "side": vs.get("side"), "aim": vs.get("aim_level"),
             "d_aim": vs.get("fill_minus_aim"), "chain": vs.get("chain"),
             "conception_cell": vs.get("conception_cell"),
             "ref_sources": dict(refsrc.get(tk, {})),
             "fv_capture": fvcap, "emfb": fvburst.get(tk,{}).get("entry_minus_fv_burst"),
             "gun_ts": gi["gun_ts"] if gi else None, "gun_amb": gi["ambiguous"] if gi else None,
             "posted_first_ts": tkl[0][0] if tkl else None, "posted_first_px": tkl[0][1] if tkl else None,
             "n_posts": len(tkl), "n_cancels": len(cancels.get(tk, []))}
        d["fill_Tsched_min"] = round((sstart - f["ts"])/60,1) if sstart else None
        d["fill_Thon_min"] = round((hstart - f["ts"])/60,1) if hstart else None
        d["fill_Tgun_min"] = round((ev_gun - f["ts"])/60,1) if ev_gun else None
        d["post_Tsched_min"] = round((sstart - tkl[0][0])/60,1) if (sstart and tkl) else None
        d["post_Thon_min"] = round((hstart - tkl[0][0])/60,1) if (hstart and tkl) else None
        d["post_Tgun_min"] = round((ev_gun - tkl[0][0])/60,1) if (ev_gun and tkl) else None
        if dip:
            arr = first_bid_ge(tkl, dip["price"], dip["dip_hi"])
            d["best"] = {"px": dip["price"], "ts": dip["ts"], "t": hm(dip["ts"]),
                         "Tsched_min": round((sstart - dip["ts"])/60,1) if sstart else None,
                         "Thon_min": round((hstart - dip["ts"])/60,1) if hstart else None,
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
        elif any(x["outc"] in ("exit_FILL","scalp_FILL") for x in legrows) and pnl >= 0:
            grade = "D"; err.append("half-armed naked single (exited green, luck-directional)")
        else:
            grade = "D"; err.append("half-armed naked single (open/held)")
    elif over_par and combined > 105:
        grade = "D"; err.append(f"combined {combined}c >>100"); forfeit = combined-100
    elif over_par:
        grade = "C"; err.append(f"combined {combined}c >100 over-par"); forfeit = combined-100
    elif combined is not None and combined > GOAL:
        grade = "C"; err.append(f"combined {combined}c > goal {GOAL} (zero cushion, exits carry burden)"); forfeit = combined-GOAL
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

    # ---- W1 pair verdicts + A-gate (Vault 0E) ----
    both_w1fill = (n == 2 and hstart and all(l[1]["ts"] < hstart for l in legs))
    bouhar = (n == 2 and all(x["w1"] == "W1_CASHED" for x in legrows))
    w1_shape = bool(both_w1fill and combined is not None and combined <= GOAL
                    and all(x["w1"] in ("W1_CASHED","W1_REACHABLE") for x in legrows))
    grade_pre_w1 = grade
    if grade == "A" and not w1_shape:
        grade = "B"; err.append("A->B: lacks W1 shape (Vault 0E gate)")

    # ---- C-row expensive-favorite columns ----
    fav_cols = None
    if combined is not None and combined >= 100 and n == 2:
        fav = max(legrows, key=lambda x: x["fill"] or 0)
        fav_cols = {"fav_tk": fav["suf"], "fav_fill": fav["fill"], "fav_aim": fav["aim"],
                    "fav_d_aim": fav["d_aim"], "fav_exit_px": fav["exit_px"],
                    "fav_exit_band_dist": (fav["exit_px"] - fav["fill"]) if (fav["exit_px"] is not None and fav["fill"] is not None) else None}

    molt = {}
    for x in legrows:
        if x.get("d_px_vs_best") and x["d_px_vs_best"] > 0 and x["best"] and x["best"]["catchable"]:
            molt["fill_above_best"] = molt.get("fill_above_best", 0) + x["d_px_vs_best"] * (x["qty"] or 0)
    if fader and not fader["filled"]:
        dips = [p for p in (fader["cheapest_pre_px"], fader["cheapest_post_px"]) if p is not None]
        if dips and min(dips) <= bound:
            lock = (100 - (basis + min(dips))) * (legs[0][1]["qty"] or 0)
            molt["forfeited_completion"] = max(lock, 0)
    games.append({"ev": ev, "cat": cat, "grade": grade, "grade_pre_w1": grade_pre_w1, "err": err,
                  "forfeit": round(forfeit,1), "combined": combined, "pnl": round(pnl,2), "n_legs": n,
                  "sched_start": sstart, "sched_t": hm(sstart) if sstart else None,
                  "honest_start": hstart, "honest_t": hm(hstart) if hstart else None,
                  "gun_ts": ev_gun, "gun_t": hm(ev_gun) if ev_gun else None,
                  "gun_vs_sched_min": round((ev_gun - sstart)/60,1) if (ev_gun and sstart) else None,
                  "gun_vs_honest_min": round((ev_gun - hstart)/60,1) if (ev_gun and hstart) else None,
                  "latch_ts": lts, "legs": legrows, "fader": fader, "molt": molt,
                  "bouhar": bouhar, "w1_shape": w1_shape,
                  "violations": ev_vio.get(ev, []), "any_open": anyopen})
    if idx % 10 == 0: print(f"..{idx}/{len(sorted_evs)} {ev}", file=sys.stderr)

# ---------- 5b. F-TRACK: engaged-but-unfilled events ----------
unfilled_events = []
eng_evs = set()
for tk in set(list(bids.keys()) + list(wopen.keys())):
    eng_evs.add(tk.rsplit("-", 1)[0])
for ev in sorted(eng_evs - set(ev_fills.keys())):
    cat = cat_of(ev + "-")
    tks = sorted(t for t in set(list(bids.keys()) + list(wopen.keys())) if t.rsplit("-",1)[0] == ev)
    hstart = honest_start(ev)
    sstart = parse_start((sched.get(ev, {}) or {}).get("start"))
    row = {"ev": ev, "cat": cat, "honest_t": hm(hstart) if hstart else None,
           "sched_t": hm(sstart) if sstart else None, "legs": []}
    for tk in tks:
        tkl = sorted(bids.get(tk, []))
        rows = tape_cache.get(tk)
        if rows is None:
            rows = read_tape(tk); tape_cache[tk] = rows
        end = latch.get(ev) or hstart or sstart or (tkl[-1][0] + 3600 if tkl else BOOT + 3600)
        t0 = tkl[0][0] if tkl else BOOT
        dip = dip_hunt(rows, t0, end) if rows else None
        misses = None
        if tkl and dip:
            misses = {"dip_px": dip["price"], "dip_t": hm(dip["ts"]), "dip_dur_s": int(dip["dur_s"]),
                      "lvl_at_dip": lvl_at(tkl, dip["ts"]),
                      "dip_below_our_lvl": (lvl_at(tkl, dip["ts"]) is not None and dip["price"] <= lvl_at(tkl, dip["ts"]))}
        row["legs"].append({"tk": tk, "n_posts": len(tkl), "n_cancels": len(cancels.get(tk, []))
                            , "first_px": tkl[0][1] if tkl else None, "last_px": tkl[-1][1] if tkl else None,
                            "first_t": hm(tkl[0][0]) if tkl else None, "dip": misses})
    row["violations"] = ev_vio.get(ev, [])
    unfilled_events.append(row)
print(f"engaged-but-unfilled events: {len(unfilled_events)}", file=sys.stderr)

# ---------- 6. ROLLUPS ----------
rep = open("/tmp/autopsy_report.txt", "w", encoding="utf-8")
def W(s=""): rep.write(s + "\n")
now_et = datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")
W(f"AUTOPSY REGRADE — window {hm(BOOT)} -> {now_et} | games={len(games)} legs={sum(g['n_legs'] for g in games)} | engaged-unfilled={len(unfilled_events)} | violations={len(violations)}")
W(f"exchange fills rows: {api_n} | market meta fetched: {len(mkt)}")

gc = defaultdict(lambda: defaultdict(int)); tt = defaultdict(int)
for gm in games: gc[gm["cat"]][gm["grade"]] += 1; tt[gm["grade"]] += 1
W("\n== GRADE DISTRIBUTION (W1-gated) ==")
W(f"{'cat':10s} {'A':>3}{'B':>3}{'C':>3}{'D':>3}{'F':>3}  tot")
for c in sorted(gc):
    r = gc[c]; W(f"{c:10s} {r['A']:>3}{r['B']:>3}{r['C']:>3}{r['D']:>3}{r['F']:>3}  {sum(r.values())}")
W(f"{'TOTAL':10s} {tt['A']:>3}{tt['B']:>3}{tt['C']:>3}{tt['D']:>3}{tt['F']:>3}  {sum(tt.values())}")

W("\n== PER-CATEGORY ROLLUP ==")
for c in sorted(set(g["cat"] for g in games)):
    gms = [g for g in games if g["cat"] == c]
    pairs = [g for g in gms if g["n_legs"] == 2]
    le97 = sum(1 for g in pairs if g["combined"] is not None and g["combined"] <= 97)
    legs_all = [x for g in gms for x in g["legs"]]
    w1c = sum(1 for x in legs_all if x["w1"] == "W1_CASHED")
    w1r = sum(1 for x in legs_all if x["w1"] == "W1_REACHABLE")
    vio_n = sum(len(g["violations"]) for g in gms)
    settled = [g for g in gms if not g["any_open"]]
    spnl = sum(g["pnl"] for g in settled)
    opnl = sum(g["pnl"] for g in gms if g["any_open"])
    bouhar_n = sum(1 for g in gms if g["bouhar"])
    W(f"{c:10s} games={len(gms):>3} pairs={len(pairs):>3} le97={le97}/{len(pairs)} "
      f"W1_CASHED={w1c} W1_REACH={w1r} legs={len(legs_all)} BOUHAR={bouhar_n} "
      f"vio={vio_n} settledPnL=${spnl:.2f} (settled n={len(settled)}) partialPnL=${opnl:.2f}")

W("\n== GRADE vs MONEY MONOTONICITY (fully-settled games) ==")
gm_money = defaultdict(list)
for gm in games:
    if gm["any_open"]: continue
    gm_money[gm["grade"]].append((gm["pnl"], gm["ev"], gm["cat"]))
for grd in "ABCDF":
    v = gm_money.get(grd, [])
    if v: W(f"  {grd}: n={len(v):>3} total=${sum(x[0] for x in v):>8.2f} mean=${sum(x[0] for x in v)/len(v):>6.2f}")

W("\n== VIOLATIONS JOINED (per game) ==")
for gm in games:
    if gm["violations"]:
        W(f"  [{gm['grade']}] {gm['ev'].replace('KX','')} {gm['cat']} comb={gm['combined']} pnl=${gm['pnl']:.2f}")
        for v in gm["violations"]:
            W(f"      {v['t']} {v['cls']} {v['detail']}")
orphan_v = [v for v in violations if not any(gm["violations"] and v.get("detail") in [x["detail"] for x in gm["violations"]] for gm in games)]
ev_with = set(gm["ev"] for gm in games if gm["violations"])
all_vio_evs = set()
for v in violations:
    tk = v.get("ticker") or ""
    all_vio_evs.add(tk if tk.count("-") == 1 else tk.rsplit("-", 1)[0])
W(f"  violation events not in filled-games set: {sorted(e.replace('KX','') for e in all_vio_evs - set(gm['ev'] for gm in games))}")

W("\n== W1 SCOREBOARD (primary line) ==")
cat_w1 = defaultdict(Counter)
for gm in games:
    for x in gm["legs"]:
        cat_w1[gm["cat"]][x["w1"]] += 1
    cat_w1[gm["cat"]]["pairs"] += 1 if gm["n_legs"] == 2 else 0
    if gm["bouhar"]: cat_w1[gm["cat"]]["BOUHAR"] += 1
for cat, s in sorted(cat_w1.items()):
    legs_n = s["W1_CASHED"] + s["W1_REACHABLE"] + s["W2_ONLY"]
    W("%-10s legs=%3d  W1_CASHED=%3d (%.0f%%)  W1_REACHABLE=%3d  W2_ONLY=%3d  BOUHAR-pairs=%d/%d" % (
        cat, legs_n, s["W1_CASHED"], 100*s["W1_CASHED"]/max(1,legs_n),
        s["W1_REACHABLE"], s["W2_ONLY"], s["BOUHAR"], s["pairs"]))

rep.close()
json.dump({"boot": BOOT, "generated": now_et, "games": games, "unfilled": unfilled_events,
           "violations": violations},
          open("/tmp/autopsy_dump.json", "w"), default=str)
print("DONE -> /tmp/autopsy_report.txt /tmp/autopsy_dump.json", file=sys.stderr)
