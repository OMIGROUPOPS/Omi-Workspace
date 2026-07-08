#!/usr/bin/env python3
"""WALK/REPOST INTERACTION MODEL (read-only, findings only) — the last AIM_V2
arm bar. Inputs: tonight's aim_shadow lines with joint-shadow fields (every
placement/repost decision: actual level, anchor px, fitted shadow aims,
walkcap/exself/joint counterfactuals, posture, tts).
Per leg: decision sequence -> walked? drift, cadence, cap comparison, EROSION =
walk drift / fitted dip discount (shadow_aim50 at first decision) vs the <25%
bar; interaction = would the ruled caps / expression invariant have bound.
Output: per-cat tables (P(walked | bucket, Tbin, first-posture), erosion)."""
import json, sys
from collections import defaultdict

LOG = "/root/Omi-Workspace/arb-executor/logs/live_v3_20260707.jsonl"
CAPS = {"ATP_MAIN": 1, "WTA_MAIN": 1, "ATP_CHALL": 2, "WTA_CHALL": 2, "ITF_M": 14, "ITF_W": 20}

legs = defaultdict(list)
for line in open(LOG, encoding="utf-8", errors="replace"):
    if '"aim_shadow"' not in line or '"joint_level"' not in line:
        continue
    try:
        e = json.loads(line)
    except Exception:
        continue
    d = e["details"]
    legs[e.get("ticker", "")].append({
        "ts": e.get("ts_epoch", 0), "cat": d.get("cat") or "", "px": d.get("px"),
        "actual": d.get("actual_bid"), "aim50": d.get("shadow_aim50"),
        "posture": d.get("actual_posture"), "tts": d.get("tts_min"),
        "joint": d.get("joint_level"), "wc": d.get("walkcap_level"),
        "ex": d.get("exself_level"), "constrained": d.get("constrained")})

rows = []
for tk, ds in legs.items():
    ds.sort(key=lambda r: r["ts"])
    lv = [r["actual"] for r in ds if r["actual"] is not None]
    if not lv:
        continue
    first, last, mx = lv[0], lv[-1], max(lv)
    cat = next((r["cat"] for r in ds if r["cat"]), "?")
    # cat fallback from ticker
    if cat == "?":
        for k, v in {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
                     "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
                     "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}.items():
            if tk.startswith(k):
                cat = v
    f0 = ds[0]
    disc = (f0["px"] - f0["aim50"]) if (f0["px"] is not None and f0["aim50"] is not None) else None
    drift = mx - first
    gaps = [(b["ts"] - a["ts"]) / 60 for a, b in zip(ds, ds[1:]) if b["ts"] > a["ts"]]
    bound_any = any(r["constrained"] for r in ds)
    over_cap = drift > CAPS.get(cat, 4)
    tts0 = f0["tts"] if f0["tts"] is not None else -1
    tbin = (">4h" if tts0 > 240 else "2-4h" if tts0 > 120 else "0.5-2h" if tts0 > 30 else "<30m" if tts0 >= 0 else "?")
    bucket = min(4, int((f0["px"] or 0) // 20))
    rows.append({"tk": tk, "cat": cat, "bucket": bucket, "tbin": tbin,
                 "posture0": f0["posture"], "n_dec": len(ds), "walked": len(set(lv)) > 1,
                 "drift": drift, "disc": disc,
                 "erosion": (drift / disc if (disc and disc > 0) else None),
                 "cad_med": (sorted(gaps)[len(gaps)//2] if gaps else None),
                 "bound_any": bound_any, "over_ruled_cap": over_cap})

def pct(v, p):
    v = sorted(x for x in v if x is not None)
    return round(v[min(len(v)-1, int(len(v)*p))], 2) if v else None

out = {"n_legs": len(rows), "n_decisions": sum(r["n_dec"] for r in rows)}
percat = {}
for cat in sorted(set(r["cat"] for r in rows)):
    rr = [r for r in rows if r["cat"] == cat]
    w = [r for r in rr if r["walked"]]
    er = [r["erosion"] for r in w if r["erosion"] is not None]
    percat[cat] = {
        "legs": len(rr), "p_walked": round(100*len(w)/len(rr), 1),
        "drift_med": pct([r["drift"] for r in w], .5), "drift_p75": pct([r["drift"] for r in w], .75),
        "over_ruled_cap_pct_of_walked": round(100*sum(r["over_ruled_cap"] for r in w)/max(1,len(w)), 1),
        "cadence_med_min": pct([r["cad_med"] for r in w], .5),
        "erosion_med": pct(er, .5), "erosion_p75": pct(er, .75),
        "erosion_gt25_pct": round(100*sum(1 for e in er if e > 0.25)/max(1,len(er)), 1),
        "bound_by_joint_pct_of_walked": round(100*sum(r["bound_any"] for r in w)/max(1,len(w)), 1)}
out["per_cat"] = percat
pw = defaultdict(lambda: [0, 0])
for r in rows:
    for key in (("tbin", r["tbin"]), ("bucket", "b%d" % r["bucket"]), ("posture0", r["posture0"] or "?")):
        pw[key][0] += 1
        pw[key][1] += 1 if r["walked"] else 0
out["p_walked_by"] = {"%s=%s" % k: round(100*v[1]/v[0], 1) for k, v in sorted(pw.items()) if v[0] >= 8}
print(json.dumps(out, indent=1))
