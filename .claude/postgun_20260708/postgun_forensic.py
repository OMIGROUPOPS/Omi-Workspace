#!/usr/bin/env python3
"""POST-GUN FORENSIC 2026-07-08 (read-only). Honest-clock era (07-06 flip -> now).
a) gun coverage per cat vs truth starts (observed_starts CERTIFIED > corpus bells TAPE-DERIVED)
b) fill boundary stamps pre-gun/grace/post-grace + leak $ per class per cat
c) cancel latency at latch + cancel_fill_race census + re-place-after-latch
d) EKSLU dump  e) provenance census for S-tier clause (sibling_repost level vs aim vs 99-basis)
"""
import gzip, json, sqlite3, sys
from collections import defaultdict, Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path("/root/Omi-Workspace/arb-executor")
ET = timezone(timedelta(hours=-4))
CAT = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
       "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
       "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}
def cat_of(ev):
    for k, v in CAT.items():
        if ev.startswith(k): return v
    return None
def et(ts): return datetime.fromtimestamp(ts, ET).strftime("%m-%d %I:%M:%S %p")
def dist(v):
    v = sorted(x for x in v if x is not None)
    if not v: return None
    def p(q): return round(v[min(len(v)-1, int(q*len(v)))], 1)
    return {"n": len(v), "p10": p(.1), "p25": p(.25), "p50": p(.5), "p75": p(.75), "p90": p(.9)}

ERA0 = 1783353600  # 2026-07-06 12:00 ET
GRACE = 300

# ---- truth starts
bells, bell_src = {}, {}
for f in sorted((ROOT/"data"/"shape_corpus").glob("samples_*.jsonl")):
    for line in open(f, encoding="utf-8", errors="replace"):
        try: d = json.loads(line)
        except Exception: continue
        tk, b = d.get("tk",""), d.get("bell")
        if tk and b:
            bells[tk.rsplit("-",1)[0]] = int(b); bell_src[tk.rsplit("-",1)[0]] = "tape"
obs_n = 0
try:
    con = sqlite3.connect(str(ROOT/"tennis.db"))
    for suf, ts in con.execute("SELECT kalshi_ticker, first_inplay_at FROM observed_starts"):
        try: oe = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
        except Exception: continue
        hits = [ev for ev in bells if ev.endswith(suf) and abs(bells[ev]-oe) < 6*3600]
        if len(hits) == 1:
            bells[hits[0]] = int(oe); bell_src[hits[0]] = "OBSERVED"; obs_n += 1
    con.close()
except Exception as e:
    print("obs_err", e)

# ---- stream era jsonl
FILES = ["logs/live_v3_20260706.jsonl", "logs/live_v3_20260707.jsonl", "logs/live_v3_20260708.jsonl"]
latch = {}                      # event -> first match_live_detected ts
latch_all = defaultdict(list)
grace_armed = {}                # event -> ts
rest_cancel = defaultdict(list) # event -> [(ts, ticker, graced)]
races = []
fills = []                      # (ts, ticker, event, price, qty, source, play_type)
settled = {}                    # ticker -> (ts, pnl, qty, price)
placed = defaultdict(list)      # event -> [(ts, ticker, price)] buy placements
engaged = set()
srp = []                        # sibling_repost_placed details
ekslu = []
for fn in FILES:
    p = ROOT/fn
    if not p.exists(): continue
    for line in open(p, encoding="utf-8", errors="replace"):
        if "EKSLU" in line:
            ekslu.append(line.rstrip())
        try: d = json.loads(line)
        except Exception: continue
        e, ts = d.get("event"), d.get("ts_epoch")
        if ts is None or ts < ERA0: continue
        det = d.get("details") or {}
        tk = d.get("ticker") or ""
        if e == "match_live_detected":
            ev = det.get("event","")
            latch_all[ev].append(ts)
            if ev not in latch: latch[ev] = ts
        elif e == "match_live_grace_armed":
            ev = det.get("event","") or tk.rsplit("-",1)[0]
            grace_armed.setdefault(ev, ts)
        elif e == "match_live_resting_cancel":
            ev = det.get("event","") or tk.rsplit("-",1)[0]
            rest_cancel[ev].append((ts, tk, det.get("graced")))
        elif e == "cancel_fill_race":
            races.append((ts, tk, det))
        elif e == "entry_filled":
            ev = tk.rsplit("-",1)[0]
            fills.append((ts, tk, ev, det.get("fill_price"), det.get("qty") or det.get("new_fills") or 0,
                          det.get("source",""), det.get("play_type","")))
        elif e == "settled":
            settled[tk] = (ts, det.get("pnl_dollars"), det.get("settled_qty"), det.get("settle_price"))
        elif e in ("order_placed", "v4_place"):
            if (det.get("action") or "buy") == "buy":
                ev = tk.rsplit("-",1)[0]
                placed[ev].append((ts, tk, det.get("price")))
                engaged.add(ev)
        elif e == "sibling_repost_placed":
            srp.append(det)

# ---- (a) gun coverage
cov = defaultdict(lambda: {"n":0,"lat":0,"silent":[],"lags":[],"lags_obs":[],"nobs":0})
now = datetime.now(timezone.utc).timestamp()
for ev, b in bells.items():
    c = cat_of(ev)
    if not c or b < ERA0 or b > now - 600: continue
    if ev not in engaged: continue
    r = cov[c]; r["n"] += 1
    if bell_src[ev] == "OBSERVED": r["nobs"] += 1
    if ev in latch:
        r["lat"] += 1
        lag = (latch[ev]-b)/60.0
        r["lags"].append(lag)
        if bell_src[ev] == "OBSERVED": r["lags_obs"].append(lag)
    else:
        r["silent"].append(ev)
out_a = {}
for c, r in sorted(cov.items()):
    out_a[c] = {"n_truth_engaged": r["n"], "n_observed_certified": r["nobs"],
                "latched": r["lat"], "det_rate_pct": round(100*r["lat"]/max(1,r["n"]),1),
                "lag_min_dist": dist(r["lags"]), "lag_certified": dist(r["lags_obs"]),
                "silent_sample": r["silent"][:8], "n_silent": len(r["silent"])}

# ---- (b) fill boundary
BLACK0, BLACK1 = 1783493520, 1783524600  # 07-08 02:52 -> 11:30 ET
per_share = {}
for tk,(ts,pnl,q,sp) in settled.items():
    if pnl is not None and q: per_share[tk] = pnl/q
cls_agg = defaultdict(lambda: defaultdict(lambda: [0,0.0,0.0]))  # cat -> class -> [n, qty, pnl$]
post_grace_named = []
for ts, tk, ev, px, q, src, pt in fills:
    c = cat_of(ev)
    if not c: continue
    adopted = ("adopt" in src) or ("reconcile" in src)
    b = bells.get(ev)
    if adopted:
        klass = "ADOPTED(dead-bot/orphan booking; fill time unreliable)"
    elif b is None:
        klass = "NO-TRUTH-START"
    elif ts < b: klass = "pre-gun"
    elif ts < b + GRACE: klass = "grace"
    else:
        if ev not in latch: klass = "post-grace:LATCH-SILENT"
        elif ts < latch[ev]: klass = "post-grace:pre-latch(latch late)"
        elif ts <= latch[ev] + GRACE: klass = "post-grace:inside-latch-grace"
        else: klass = "post-grace:OUTLIVED-LATCH"
    pnl = per_share.get(tk, 0.0) * q
    a = cls_agg[c][klass]; a[0]+=1; a[1]+=q; a[2]+=pnl
    if klass.startswith("post-grace"):
        post_grace_named.append((et(ts), tk, px, q, klass, round(pnl,2),
                                 round((ts-b)/60,1), "latch@"+et(latch[ev]) if ev in latch else "no-latch"))
out_b = {c: {k: {"n":v[0],"qty":v[1],"pnl$":round(v[2],2)} for k,v in kk.items()} for c,kk in cls_agg.items()}

# ---- (c) cancel latency + races + replace-after-latch
lat_cancel = []
replaced_after = []
for ev, lts in latch.items():
    for (cts, tk, graced) in rest_cancel.get(ev, []):
        if cts >= lts: lat_cancel.append(cts-lts)
    for (pts_, tk, px) in placed.get(ev, []):
        if pts_ > lts + GRACE:
            replaced_after.append((et(pts_), tk, px, round((pts_-lts)/60,1)))
out_c = {"cancel_latency_sec_dist": dist(lat_cancel),
         "n_resting_cancels": sum(len(v) for v in rest_cancel.values()),
         "races": [{"ts": et(ts), "tk": tk, "label": det.get("label"), "filled": det.get("filled"),
                    "px": det.get("fill_price"), "cancel_ok": det.get("cancel_ok")} for ts,tk,det in races],
         "n_buy_placed_after_latch_grace": len(replaced_after),
         "replaced_sample": replaced_after[:12]}

# ---- (e) provenance census
prov = Counter(); prov_cat = defaultdict(Counter)
for det in srp:
    ev = det.get("event",""); c = cat_of(ev) or "?"
    b1 = det.get("leg1_basis"); aim = det.get("aim"); lvl = det.get("level"); goal = det.get("goal_level")
    cap = (99 - b1) if isinstance(b1,(int,float)) else None
    if lvl is None: k = "?"
    elif cap is not None and lvl >= cap - 1 and (aim is None or lvl != aim): k = "CAP-ARITHMETIC(99-basis)"
    elif aim is not None and lvl == aim: k = "AIM-DRIVEN"
    elif aim is not None and lvl == goal and goal != aim: k = "GOAL(clamped-off-aim)"
    else: k = "OTHER"
    prov[k] += 1; prov_cat[c][k] += 1

print(json.dumps({"meta": {"bells_era": sum(1 for e,b in bells.items() if ERA0<=b<=now and cat_of(e)),
                           "observed_certified_total": obs_n, "n_fills": len(fills),
                           "n_latch_events": len(latch), "n_settled": len(settled)},
                  "a_gun_coverage": out_a, "b_fill_boundary": out_b,
                  "b_post_grace_named": post_grace_named[:40],
                  "c_cancel": out_c,
                  "e_provenance": {"all": dict(prov), "by_cat": {c: dict(v) for c,v in prov_cat.items()}}},
                 indent=1))
print("\n==== EKSLU RAW (%d lines) ====" % len(ekslu))
for l in ekslu: print(l[:600])
