#!/usr/bin/env python3
"""Causal-audit synthesis: per-event chain compact, exchange-truth P&L decomposition,
riser/faller discount stats, EARNED/GIFT inputs. Emits audit_rows.json + prints tables."""
import json
from collections import defaultdict

d = json.load(open("causal_audit.json"))
chains, truth = d["chains"], d["truth"]

LEDGER = {  # event-suffix -> (grade, ledger_pnl, ledger_class)
 "GIUFEL": ("F", -0.35, "half-arm STARVATION (crash-mediated)"),
 "HEICEC": ("F", -3.50, "half-arm PAIRING + deep-neg chase"),
 "HEMMOE": ("A", 1.20, "clean pair 99"),
 "KASPIR": ("D", 0.95, "half-arm PAIRING"),
 "MELCAS": ("F", -2.60, "half-arm STARVATION"),
 "RINDIA": ("D", 0.95, "half-arm PAIRING"),
 "DESVA": ("D", 0.85, "half-arm PAIRING"),
 "TIABUB": ("D", 0.00, "half-arm PAIRING (open)"),
 "HARNAS": ("D", 190.0, "manual adoption"),
 "BENAHO": ("F", -1.40, "half-arm STARVATION"),
 "ORLPOP": ("B", 1.25, "pair 99, one deep-neg leg"),
 "CLALAM": ("C", 4.65, "fragile deep-neg leg (won)"),
 "ANIKEY": ("D", 0.00, "half-arm PAIRING (open)"),
 "EALSWI": ("F", -3.70, "half-arm PAIRING"),
 "MERRYB": ("C", 0.10, "FUCKUP-3 exit-harvest pair"),
 "PAOSAK": ("D", 0.75, "half-arm PAIRING"),
 "HERPDA": ("n/a", None, "tonight"),
 "ZANSIE": ("n/a", None, "tonight"),
 "WATSHI": ("n/a", None, "tonight (exhibit)"),
 "LEGWIN": ("n/a", None, "tonight (ZT violation 102)"),
 "ZAMBRI": ("n/a", None, "tonight"),
}

def short(E):
    for p in ("KXATPCHALLENGERMATCH-26JUL04", "KXATPMATCH-26JUL04", "KXWTAMATCH-26JUL04",
              "KXITFMATCH-26JUL04", "KXITFWMATCH-26JUL04", "KXITFMATCH-26JUL03"):
        if E.startswith(p):
            return E[len(p):]
    return E

rows = []
riser_stats, faller_stats = [], []
for E, ch in chains.items():
    sE = short(E)
    # per-ticker chain facts
    legs = defaultdict(lambda: {"wopen": None, "places": [], "mech": set(), "fill": None,
                                "fill_src": None, "emfb": None, "exit_posted": None,
                                "settle": None, "dir": None})
    ev_mech = set()
    latch = None
    for c in ch:
        tk8 = c["tk"]; e = c["e"]; dd = c["d"]
        L = legs[tk8]
        if e == "window_open_set" and L["wopen"] is None:
            L["wopen"] = dd.get("price")
        elif e == "v4_place":
            L["places"].append({"tgt": dd.get("target_bid"), "src": dd.get("reference_source"),
                                "tbl": dd.get("table_src"), "cell": dd.get("cell")})
            if dd.get("direction"):
                L["dir"] = dd["direction"]
        elif e == "order_cancelled" and dd.get("label"):
            L["mech"].add(dd["label"])
        elif e == "entry_filled" and L["fill"] is None:
            L["fill"] = dd.get("fill_price"); L["fill_src"] = dd.get("source") or dd.get("play_type")
            if dd.get("direction"):
                L["dir"] = dd["direction"]
        elif e == "fv_burst_anchor":
            L["emfb"] = dd.get("entry_minus_fv_burst")
        elif e == "v4_exit_posted":
            L["exit_posted"] = dd.get("exit_price")
        elif e == "settled":
            L["settle"] = (dd.get("settle"), dd.get("pnl_cents"))
        elif e in ("premarket_walk_capped", "leg2_reshuffle_reaim", "reaim_sibling_arrival",
                   "reaim_sibling_cancel", "sibling_repost_placed", "sibling_repost_skip",
                   "match_live_grace_armed", "match_live_resting_cancel", "liquid_repost_at_touch",
                   "completion_fill"):
            ev_mech.add(e)
            L["mech"].add(e)
        elif e == "match_live_detected":
            latch = dd.get("tts_min")
    # exchange truth per event
    tr = {tk[-8:]: v for tk, v in truth.items() if tk.startswith(E + "-")}
    realized = unreal = 0.0
    manual_flag = False
    for tk8, v in tr.items():
        bq, sq = v.get("buy_qty", 0), v.get("sell_qty", 0)
        ab, asell = v.get("avg_buy") or 0, v.get("avg_sell") or 0
        if bq > 100:
            manual_flag = True
        sold_real = (asell - ab) * min(sq, bq)
        res = v.get("result")
        held = bq - min(sq, bq)
        if v.get("status") == "finalized":
            sold_real += held * ((100 - ab) if res == "yes" else (0 - ab))
            realized += sold_real
        else:
            realized += sold_real
            unreal += held * ab * 0  # open basis carried, not P&L
    realized /= 100.0
    grade, lpnl, lclass = LEDGER[sE]
    open_legs = [t for t, v in tr.items() if v.get("open_qty", 0) > 0]
    rows.append({"ev": sE, "grade": grade, "ledger_pnl": lpnl, "truth_pnl": round(realized, 2),
                 "diff": (round(realized - lpnl, 2) if lpnl is not None else None),
                 "manual": manual_flag, "open": open_legs, "latch_tts": latch,
                 "mech": sorted(ev_mech),
                 "legs": {t: {"wopen": L["wopen"], "fill": L["fill"], "dir": L["dir"],
                              "src": L["fill_src"], "emfb": L["emfb"],
                              "places": L["places"][:3], "mech": sorted(L["mech"]),
                              "settle": L["settle"],
                              "truth": tr.get(t, {})} for t, L in legs.items()}})
    # riser/faller discount stats (bot fills only, exclude manual/adoption)
    for t, L in legs.items():
        if L["fill"] is None or L["wopen"] is None:
            continue
        if L["fill_src"] in ("reconcile_adoption",) or (tr.get(t, {}).get("buy_qty", 0) > 100):
            continue
        disc = L["wopen"] - L["fill"]
        side = "riser" if (L["dir"] == "leader" or (L["fill"] or 0) >= 50) else "faller"
        (riser_stats if side == "riser" else faller_stats).append(
            {"ev": sE, "tk": t, "wopen": L["wopen"], "fill": L["fill"], "disc": disc,
             "emfb": L["emfb"]})

json.dump(rows, open("audit_rows.json", "w"), indent=1)
print("=== EXCHANGE TRUTH vs LEDGER (discrepancies) ===")
for r in rows:
    if r["diff"] is not None and abs(r["diff"]) > 0.02:
        print(f"  {r['ev']:8s} grade {r['grade']} ledger {r['ledger_pnl']:+.2f} truth {r['truth_pnl']:+.2f} diff {r['diff']:+.2f}")
print("\n=== RISER LEGS (dir=leader / >=50): window-open vs fill ===")
for x in riser_stats:
    print(f"  {x['ev']:8s} {x['tk']:9s} open {x['wopen']:>3} fill {x['fill']:>3} disc {x['disc']:+3d}  emfb {x['emfb']}")
n = len(riser_stats)
if n:
    z = sum(1 for x in riser_stats if x["disc"] <= 0)
    print(f"  risers: {n} | fills AT/ABOVE window-open (zero/negative discount): {z} | mean disc {sum(x['disc'] for x in riser_stats)/n:+.1f}c")
print("\n=== FALLER LEGS ===")
for x in faller_stats:
    print(f"  {x['ev']:8s} {x['tk']:9s} open {x['wopen']:>3} fill {x['fill']:>3} disc {x['disc']:+3d}  emfb {x['emfb']}")
n = len(faller_stats)
if n:
    z = sum(1 for x in faller_stats if x["disc"] > 0)
    print(f"  fallers: {n} | fills BELOW window-open (real discount): {z} | mean disc {sum(x['disc'] for x in faller_stats)/n:+.1f}c")
