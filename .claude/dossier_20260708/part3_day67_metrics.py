#!/usr/bin/env python3
"""PART3 clean-3day: Jul6/Jul7 per-cat GROSS vs CLEAN from /tmp/slate_ledger_v2.json
(evening refresh 07-07 23:15 ET) + /root/post_fill_move.json (divot classes).
READ-ONLY: prints JSON to stdout, writes nothing.
Conventions:
 - fill-day ET attribution for metrics 1-3 (entry metrics belong to the fill day)
 - conception-day attribution for grade mix (ledger convention), settled rows only
 - MECHANICAL leg = ledger leg.mech non-null (flags a/b/c per BLEED_ATTRIBUTION_20260707)
   + manual strip: 07-07 naked-sweep legs ISOTOM-TOM/KUSTAG-TAG/NASLEE-LEE/TIKCHO-CHO
 - entry-vs-own-low: vw - w1_low, W1-filled legs with w1_low on record (gold census)
 - divot share: DIVOT/(DIVOT+REPRICE+NO_UNDERCUT) per post_fill_move classes
 - band-reach: pregame = exit filled W1/COR or touch W1/COR; any = any exit fill or touch
"""
import json
from collections import defaultdict
from datetime import datetime, timezone, timedelta

ET = timezone(timedelta(hours=-4))
MANUAL_STRIP_0707 = {"KXITFMATCH-26JUL07ISOTOM-TOM", "KXITFMATCH-26JUL07KUSTAG-TAG",
                     "KXITFMATCH-26JUL07NASLEE-LEE", "KXITFWMATCH-26JUL07TIKCHO-CHO"}

D = json.load(open("/tmp/slate_ledger_v2.json"))
PF = {r["tk"]: r for r in json.load(open("/root/post_fill_move.json"))}

def day(ts):
    return datetime.fromtimestamp(ts, ET).strftime("%m-%d")

def med(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n: return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0

legs = []
for r in D["rows"]:
    for l in r["legs"]:
        if not l.get("fill_ts") or l.get("vw") is None:
            continue
        mech_flags = sorted(k for k in (l.get("mech") or {}) if not k.endswith("_sh"))
        manual = l["tk"] in MANUAL_STRIP_0707
        disp = l.get("disp") or ""
        touch = l.get("touch") or {}
        pre_reach = disp in ("EXIT_FILLED_W1", "EXIT_FILLED_CORRIDOR") or touch.get("W1") or touch.get("COR")
        any_reach = disp.startswith("EXIT_FILLED") or any(touch.values())
        has_band = l.get("exit_lvl") is not None or disp.startswith("EXIT_FILLED")
        pf = PF.get(l["tk"]) or {}
        legs.append(dict(tk=l["tk"], cat=r["cat"], d=day(l["fill_ts"]),
                         mech=bool(mech_flags) or manual,
                         mech_flags=mech_flags + (["naked_sweep"] if manual else []),
                         w1f=bool(l.get("w1_filled")), vw=l["vw"], w1_low=l.get("w1_low"),
                         pre_reach=bool(pre_reach), any_reach=bool(any_reach), has_band=has_band,
                         legS=bool(l.get("w1_filled") and l.get("w1_low") is not None
                                   and l["vw"] - l["w1_low"] <= 4
                                   and disp in ("EXIT_FILLED_W1", "EXIT_FILLED_CORRIDOR")),
                         cls=pf.get("cls")))

# sanity: disp vocabulary
vocab = sorted(set((l2.get("disp") or "NONE") for r in D["rows"] for l2 in r["legs"]))
mech_vocab = sorted(set(k for r in D["rows"] for l2 in r["legs"] for k in (l2.get("mech") or {})))

out = {"disp_vocab": vocab, "mech_key_vocab": mech_vocab, "days": {}}
for dd in ("07-06", "07-07"):
    per = {}
    for cat in sorted(set(l["cat"] for l in legs)):
        sub = [l for l in legs if l["d"] == dd and l["cat"] == cat]
        if not sub: continue
        def block(ls):
            gl = [l["vw"] - l["w1_low"] for l in ls if l["w1f"] and l["w1_low"] is not None]
            dec = [l for l in ls if l["cls"] in ("DIVOT", "REPRICE", "NO_UNDERCUT")]
            nd = len(dec)
            div = sum(1 for l in dec if l["cls"] == "DIVOT")
            band = [l for l in ls if l["has_band"]]
            return {"n_fills": len(ls), "n_w1_gap": len(gl), "gap_med": med(gl),
                    "decisive": nd, "divot": div,
                    "divot_share": round(div / nd, 3) if nd else None,
                    "reprice": sum(1 for l in dec if l["cls"] == "REPRICE"),
                    "no_undercut": sum(1 for l in dec if l["cls"] == "NO_UNDERCUT"),
                    "n_band": len(band),
                    "reach_pre": sum(1 for l in band if l["pre_reach"]),
                    "reach_any": sum(1 for l in band if l["any_reach"]),
                    "n_classified": sum(1 for l in ls if l["cls"] not in (None, "NO_TAPE")),
                    "n_w1_filled": sum(1 for l in ls if l["w1f"]),
                    "legS": sum(1 for l in ls if l["legS"])}
        g = block(sub); c = block([l for l in sub if not l["mech"]])
        per[cat] = {"gross": g, "clean": c,
                    "mech_legs": [(l["tk"][-18:], ",".join(l["mech_flags"])) for l in sub if l["mech"]]}
    out["days"][dd] = per

# grade mix by CONCEPTION day, settled rows only
gm = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for r in D["rows"]:
    concs = [l.get("conc_ts") for l in r["legs"] if l.get("conc_ts")]
    if not concs or not r.get("grade"):
        continue
    if r.get("status") not in ("SETTLED", "FINAL", "settled"):
        continue
    dd = day(min(concs))
    if dd not in ("07-06", "07-07"): continue
    mech_row = any((l.get("mech") or l["tk"] in MANUAL_STRIP_0707) for l in r["legs"])
    gm[dd][r["cat"]]["g_" + r["grade"]] += 1
    gm[dd][r["cat"]]["g_total"] += 1
    if not mech_row:
        gm[dd][r["cat"]]["c_" + r["grade"]] += 1
        gm[dd][r["cat"]]["c_total"] += 1
out["grade_mix"] = {d2: {c2: dict(v) for c2, v in cats.items()} for d2, cats in gm.items()}
out["status_vocab"] = sorted(set(r.get("status") for r in D["rows"]))
print(json.dumps(out))
