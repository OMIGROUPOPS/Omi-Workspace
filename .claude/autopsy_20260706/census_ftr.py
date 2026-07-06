#!/usr/bin/env python3
"""[READ-ONLY] ENTRY-MECHANICS CENSUS — concluded games only, W1 + corridor.
Prior art (C45): full_tape_regrade.py step-③ dip_hunt/tape_gun reused verbatim;
autopsy_ftr.py session assembly; Vault §5 window structure (W1 premarket drift /
corridor sched-start→true onset / W2 in-match), P3a tape-relative re-derivation.
Spans TWO bot sessions since flip boot (23:50:39 07-05; restart 12:15 07-06).
Writes /tmp/census_dump.json. Run from /root/Omi-Workspace/arb-executor. NO writes."""
import json, time, base64, sys, re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter

ET = timezone(timedelta(hours=-4))
BOOT = 1783309839.0
GOAL = 97
GRACE_S = 300
LOGS = ["/tmp/session_since_boot.jsonl", "logs/live_v3_20260706.jsonl"]
CAT = {"KXATPMATCH":"ATP_MAIN","KXWTAMATCH":"WTA_MAIN","KXATPCHALLENGERMATCH":"ATP_CHALL",
       "KXWTACHALLENGERMATCH":"WTA_CHALL","KXITFMATCH":"ITF_M","KXITFWMATCH":"ITF_W"}
def cat_of(tk): return next((v for k,v in CAT.items() if tk.startswith(k)), "?")
def hm(e):
    return datetime.fromtimestamp(e, ET).strftime("%m-%d %H:%M") if e else None

# ---------- Kalshi REST ----------
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

# ---------- honest clock ----------
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

# ---------- 1. LOG PARSE (both sessions) ----------
sched={}; wopen={}; bids=defaultdict(list); log_fills={}; cancels=defaultdict(list)
latch={}; gunshadow={}; skips=defaultdict(Counter); spread_samp=defaultdict(list)
cancel_label=defaultdict(list)
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
            if ev and ev not in sched: sched[ev] = d.get("start_time")
        elif e == "window_open_set" and tk:
            if tk not in wopen or ts < wopen[tk][0]: wopen[tk] = (ts, d.get("price"))
        elif e == "order_placed" and d.get("action") == "buy" and tk and d.get("price") is not None:
            bids[tk].append((ts, d["price"]))
        elif e in ("order_canceled","order_cancelled") and tk:
            cancels[tk].append(ts)
            if d.get("label"): cancel_label[tk].append((ts, d["label"]))
        elif e == "entry_filled" and tk and tk not in log_fills:
            log_fills[tk] = (ts, d.get("fill_price"), d.get("qty"))
        elif e == "match_live_detected":
            ev = d.get("event")
            if ev and ev not in latch: latch[ev] = ts
        elif e == "gun_scale_shadow":
            ev = d.get("event")
            if ev and ev not in gunshadow: gunshadow[ev] = {"ts": ts, "tts_min": d.get("tts_min")}
        elif e == "skipped":
            evd = d.get("event") or (tk.rsplit("-",1)[0] if tk else "")
            if evd: skips[evd][d.get("reason") or "?"] += 1
        elif e == "v4_place" and tk and d.get("book_bid") and d.get("book_ask"):
            try: spread_samp[cat_of(tk)].append(int(d["book_ask"]) - int(d["book_bid"]))
            except Exception: pass
print(f"parse: bids_tk={len(bids)} fills={len(log_fills)} latch={len(latch)} sched={len(sched)}", file=sys.stderr)

# ---------- 2. EXCHANGE TRUTH ----------
api_fills = defaultdict(list); cursor=""; pages=0
while pages < 60:
    p = f"/portfolio/fills?limit=200&min_ts={int(BOOT)}" + (f"&cursor={cursor}" if cursor else "")
    r = g(p); pages += 1
    for f in r.get("fills", []): api_fills[f["ticker"]].append(f)
    cursor = r.get("cursor")
    if not cursor: break
print(f"exchange fills: {sum(len(v) for v in api_fills.values())} rows / {len(api_fills)} tickers", file=sys.stderr)

engaged_tks = sorted(set(bids) | set(api_fills))
engaged_evs = sorted(set(tk.rsplit("-",1)[0] for tk in engaged_tks))
# market results for every engaged ticker + sibling
all_tks = set(engaged_tks)
for ev in engaged_evs:
    for tk in engaged_tks:
        pass
mkt={}
tk_list = sorted(all_tks)
for i in range(0, len(tk_list), 90):
    chunk = ",".join(tk_list[i:i+90])
    r = g(f"/markets?tickers={chunk}&limit=100")
    for m in r.get("markets", []):
        mkt[m["ticker"]] = {"result": m.get("result"), "status": m.get("status")}
print(f"market meta: {len(mkt)}", file=sys.stderr)

def entry_vwap(tk):
    rows = [f for f in api_fills.get(tk, []) if f.get("action") == "buy"]
    ct = px = 0.0; first_ts = None
    for f in rows:
        c = float(f.get("count_fp") or 0); p = float(f.get("yes_price_dollars") or 0)*100
        ct += c; px += c*p
        t = datetime.fromisoformat(f["created_time"].replace("Z","+00:00")).timestamp()
        first_ts = t if first_ts is None else min(first_ts, t)
    return (round(px/ct,1), ct, first_ts) if ct else (None, 0, None)

# ---------- 3. TAPE ENGINE (step-③ verbatim) ----------
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
    fwd = {m: sum(mv[x] for x in mins if m <= x < m+600) for m in mins}
    peak = max(fwd.values())
    gun_m = next((m for m in mins if mv[m] >= 150 and fwd[m] >= 3000), None)
    amb = peak < 3000
    if gun_m is None:
        gun_m = max(mins, key=lambda m: mv[m]); amb = True
    return {"gun_ts": gun_m, "ambiguous": amb}

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
    return {"px": best, "ts": bts, "size_at": sum(c for _, p, c in sf if p == best),
            "dur_s": int(hi - lo), "prints": len(span)}

def lvl_at(tklist, t):
    lv = None
    for ts, p in tklist:
        if ts <= t: lv = p
        else: break
    return lv

def parse_start(sstr):
    if not sstr: return None
    try: return datetime.fromisoformat(sstr.replace("Z", "+00:00")).timestamp()
    except Exception: pass
    for fmt in ("%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M:%SZ"):
        try: return datetime.strptime(sstr, fmt).replace(tzinfo=timezone.utc).timestamp()
        except Exception: pass
    return None

# ---------- 4. PER-GAME CENSUS ----------
games = []
now_ts = time.time()
for ev in engaged_evs:
    cat = cat_of(ev + "-")
    if cat == "?": continue
    tks = sorted(t for t in engaged_tks if t.rsplit("-",1)[0] == ev)
    # sibling discovery even if never engaged
    ev_mkts = {t: mkt.get(t, {}) for t in tks}
    results = [m.get("result") for m in ev_mkts.values()]
    concluded = any(r in ("yes","no") for r in results)
    sstart = parse_start(sched.get(ev))
    hstart = honest_start(ev)
    ref_start = hstart or sstart
    lts = latch.get(ev)
    tape = {tk: read_tape(tk) for tk in tks}
    # true onset: earliest unambiguous gun across legs. Search window clamped to
    # [ref_start - 30min, ref_start + 8h]: P1/P3a (07-05) — onsets are LATE vs schedule
    # (median +24..+81m), never hours early; a wide left edge catches premarket volume
    # bursts as false onsets (DECOB artifact in census draft 1).
    onset = None; onset_amb = True
    def _win(rows_first):
        if ref_start: return (ref_start - 1800, ref_start + 8*3600)
        f = log_fills.get(tk, (None,))[0]
        a = f or rows_first
        return (a - 3600, a + 6*3600)
    for tk, rows in tape.items():
        if not rows: continue
        w0, w1_ = _win(rows[0][0])
        gi = tape_gun(rows, w0, w1_)
        if gi and not gi["ambiguous"]:
            if onset is None or gi["gun_ts"] < onset: onset = gi["gun_ts"]; onset_amb = False
    if onset is None:
        cand = []
        for tk, rows in tape.items():
            if rows:
                w0, w1_ = _win(rows[0][0])
                gi = tape_gun(rows, w0, w1_)
                if gi: cand.append(gi["gun_ts"])
        onset = min(cand) if cand else None
    # window boundaries (Vault §5 / P3a): W1 = t0 -> ref_start; corridor = ref_start -> onset(/latch)
    corr_end = onset or lts
    if corr_end is not None and ref_start is not None and corr_end <= ref_start:
        corr_end = None   # no corridor (onset at/before start) -- corridor metrics undefined
    legs = []
    for tk in tks:
        tkl = sorted(bids.get(tk, []))
        vw, qty, xfill_ts = entry_vwap(tk)
        t0 = (wopen.get(tk) or (None,))[0] or (tkl[0][0] if tkl else None)
        rows = tape.get(tk, [])
        w1b = dip_hunt(rows, t0, ref_start) if (rows and t0 and ref_start and ref_start > t0) else None
        crb = dip_hunt(rows, ref_start, corr_end) if (rows and ref_start and corr_end and corr_end > ref_start) else None
        # corridor bids working
        cor_lvl = lvl_at(tkl, (ref_start + (corr_end or ref_start))/2) if (tkl and ref_start) else None
        cor_alive = None
        if ref_start and tkl:
            last_cancel = max(cancels.get(tk, [0]) or [0])
            cor_alive = (lvl_at(tkl, corr_end or now_ts) is not None
                         and not (last_cancel and (xfill_ts is None) and last_cancel < (corr_end or now_ts) and last_cancel > (tkl[-1][0])))
        # timing verdict vs cheapest window
        cheapest = min([x for x in (w1b, crb) if x], key=lambda d: d["px"]) if (w1b or crb) else None
        fill_vs_dip = None
        if xfill_ts and cheapest:
            fill_vs_dip = ("before" if xfill_ts < cheapest["ts"] - 60 else
                           "during" if xfill_ts <= cheapest["ts"] + cheapest["dur_s"] + 60 else "after")
        miss_min = round((xfill_ts - cheapest["ts"])/60, 1) if (xfill_ts and cheapest) else None
        # unfilled: where our bid sat during the cheapest window
        sat_at = lvl_at(tkl, cheapest["ts"]) if (cheapest and tkl and not xfill_ts) else None
        # blocking mechanism for missing side
        block = None
        if vw is None:
            if not tkl:
                sk = skips.get(ev, Counter())
                block = "never-posted(" + (sk.most_common(1)[0][0] if sk else "no-post-no-skip-logged") + ")"
            else:
                lastc = cancel_label.get(tk, [])
                if lastc and (not cheapest or lastc[-1][0] < (cheapest["ts"] if cheapest else now_ts)):
                    block = f"pulled({lastc[-1][1]}@{hm(lastc[-1][0])})"
                elif cheapest and sat_at is not None and sat_at < cheapest["px"]:
                    block = f"priced-out(ours {sat_at}c vs traded {cheapest['px']}c)"
                elif cheapest and sat_at is not None:
                    block = f"queue-starved(ours {sat_at}c >= dip {cheapest['px']}c but unfilled)"
                else:
                    block = "resting-no-dip(tape never printed sell-flow at reach)"
        # grace: fills after latch + 300s
        grace = None
        if lts and xfill_ts:
            over = xfill_ts - (lts + GRACE_S)
            grace = "VIOLATION(+%dmin)" % round(over/60) if over > 0 else "clean"
        legs.append({"tk": tk, "suf": tk.rsplit("-",1)[-1],
                     "post_ts": tkl[0][0] if tkl else None, "post_t": hm(tkl[0][0]) if tkl else None,
                     "post_px": tkl[0][1] if tkl else None, "n_posts": len(tkl),
                     "fill_ts": xfill_ts, "fill_t": hm(xfill_ts), "fill_px": vw, "qty": qty,
                     "post_Ts_min": round((sstart - tkl[0][0])/60,1) if (sstart and tkl) else None,
                     "post_Th_min": round((hstart - tkl[0][0])/60,1) if (hstart and tkl) else None,
                     "fill_Ts_min": round((sstart - xfill_ts)/60,1) if (sstart and xfill_ts) else None,
                     "fill_Th_min": round((hstart - xfill_ts)/60,1) if (hstart and xfill_ts) else None,
                     "w1_best": w1b, "cor_best": crb,
                     "gap_w1": (round(vw - w1b["px"],1) if (vw is not None and w1b) else None),
                     "gap_cor": (round(vw - crb["px"],1) if (vw is not None and crb) else None),
                     "fill_vs_dip": fill_vs_dip, "miss_min": miss_min,
                     "sat_at_dip": sat_at, "block": block,
                     "cor_bid_lvl": cor_lvl, "grace": grace,
                     "result": ev_mkts.get(tk, {}).get("result")})
    filled = [l for l in legs if l["fill_px"] is not None]
    combined = round(sum(l["fill_px"] for l in filled), 1) if len(filled) == 2 else None
    best_ach = None
    if len(legs) == 2:
        b0 = [x for x in (legs[0]["w1_best"], legs[0]["cor_best"]) if x]
        b1 = [x for x in (legs[1]["w1_best"], legs[1]["cor_best"]) if x]
        if b0 and b1:
            best_ach = round(min(x["px"] for x in b0) + min(x["px"] for x in b1), 1)
    # gun verdict
    gun = None
    if lts and onset:
        dm = round((lts - onset)/60, 1)
        gun = {"verdict": ("early" if dm < -2 else "on" if dm <= 5 else "late"), "delta_min": dm,
               "latch_t": hm(lts), "onset_t": hm(onset), "onset_amb": onset_amb}
    elif onset and not lts:
        gs = gunshadow.get(ev)
        gun = {"verdict": "SILENT", "onset_t": hm(onset), "onset_amb": onset_amb,
               "shadow_would_fire": hm(gs["ts"]) if gs else None}
    elif lts and not onset:
        gun = {"verdict": "latch_no_tape_onset", "latch_t": hm(lts)}
    participation = ("both" if len(filled) == 2 else
                     f"one({filled[0]['suf']})" if len(filled) == 1 else "neither")
    games.append({"ev": ev, "cat": cat, "concluded": concluded,
                  "results": {t.rsplit('-',1)[-1]: (ev_mkts.get(t) or {}).get("result") for t in tks},
                  "sstart_t": hm(sstart), "hstart_t": hm(hstart),
                  "onset_t": hm(onset), "onset_amb": onset_amb, "latch_t": hm(lts),
                  "corridor_min": round((corr_end - ref_start)/60,1) if (ref_start and corr_end) else None,
                  "participation": participation, "combined": combined, "best_achievable": best_ach,
                  "gun": gun, "legs": legs,
                  "settled": all(r in ("yes","no") for r in results) if results else False})
    if len(games) % 25 == 0: print(f"..{len(games)} games", file=sys.stderr)

# category physics
phys = {}
for c in set(g_["cat"] for g_ in games):
    sp = sorted(spread_samp.get(c, []))
    dens = []
    for g_ in games:
        if g_["cat"] != c: continue
        for l in g_["legs"]:
            wb = l.get("w1_best")
            if wb and wb.get("prints"): dens.append(wb["prints"])
    phys[c] = {"median_spread_c": sp[len(sp)//2] if sp else None, "n_spread": len(sp),
               "w1_dip_prints_med": sorted(dens)[len(dens)//2] if dens else None}

json.dump({"boot": BOOT, "generated": hm(now_ts), "games": games, "phys": phys},
          open("/tmp/census_dump.json", "w"), default=str)
n_conc = sum(1 for g_ in games if g_["concluded"])
print(f"CENSUS: engaged={len(games)} concluded={n_conc} open={len(games)-n_conc} -> /tmp/census_dump.json", file=sys.stderr)
