#!/usr/bin/env python3
"""[READ-ONLY] Riser-side revision measurement: replay riser posts at demand-depths
{0,1,2,3,4}c below window-open, against the recorded tape. Per depth x cat:
fill-rate retained (certain = print strictly below level; at-touch = print <= level),
discount captured, and burst-FV verdict (fill level below fv_mid = adverse selection
killed). Universe: every leg with window_open price >= 50 in the last two logs."""
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ET = timezone(timedelta(hours=-4))
LOGS = ["logs/live_v3_20260703.jsonl", "logs/live_v3_20260704.jsonl"]
CAT_MAP = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
           "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
           "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}

wopen = {}      # tk -> (ts, price)
fvmid = {}      # tk -> fv_mid at burst
latch = {}      # event -> ts
fills = {}      # tk -> (ts, price)
for lp in LOGS:
    if not Path(lp).exists():
        continue
    for line in open(lp, encoding="utf-8", errors="replace"):
        if '"event"' not in line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        e, tk, d = o.get("event"), o.get("ticker") or "", o.get("details", {})
        if e == "window_open_set" and tk and tk not in wopen and (d.get("price") or 0) >= 50:
            wopen[tk] = (o["ts_epoch"], d["price"])
        elif e == "fv_burst_anchor" and tk and d.get("fv_mid") is not None:
            fvmid[tk] = d["fv_mid"]
        elif e == "match_live_detected" and d.get("event"):
            latch.setdefault(d["event"], o["ts_epoch"])
        elif e == "entry_filled" and tk and tk not in fills:
            fills[tk] = (o["ts_epoch"], d.get("fill_price"))

def cat_of(tk):
    return next((v for k, v in CAT_MAP.items() if tk.startswith(k)), "?")

def tape(tk, t0, t1):
    f = Path("analysis/trades") / (tk + ".csv")
    out = []
    if not f.exists():
        return out
    for ln in f.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        p = ln.split(",")
        if len(p) < 5:
            continue
        try:
            ts = datetime.strptime(p[0], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp()
        except Exception:
            continue
        if t0 <= ts <= t1:
            out.append((ts, int(p[2])))
    return out

DEPTHS = [0, 1, 2, 3, 4]
agg = defaultdict(lambda: defaultdict(lambda: {"n": 0, "fill_c": 0, "fill_t": 0,
                                               "fv_n": 0, "fv_good": 0}))
legs_out = []
for tk, (wts, W) in wopen.items():
    ev = tk.rsplit("-", 1)[0]
    end = latch.get(ev, wts + 4 * 3600)          # premarket window: open -> latch (or +4h)
    tp = tape(tk, wts, end)
    if not tp:
        continue
    cat = cat_of(tk)
    fv = fvmid.get(tk)
    row = {"tk": tk[-14:], "cat": cat, "W": W, "prints": len(tp), "fv_mid": fv, "depths": {}}
    for dpt in DEPTHS:
        lvl = W - dpt
        certain = next((ts for ts, pr in tp if pr < lvl), None)
        touch = next((ts for ts, pr in tp if pr <= lvl), None)
        a = agg[cat][dpt]
        a["n"] += 1
        if certain:
            a["fill_c"] += 1
        if touch:
            a["fill_t"] += 1
        good = None
        if fv is not None and touch:
            good = lvl < fv                       # bought BELOW burst-FV = adverse selection beaten
            a["fv_n"] += 1
            if good:
                a["fv_good"] += 1
        row["depths"][dpt] = {"lvl": lvl, "fill_certain": bool(certain),
                              "fill_touch": bool(touch), "below_fv": good}
    legs_out.append(row)

print(f"universe: {len(legs_out)} riser legs (window-open >=50) with tape")
print(f"\n{'cat':10s} {'depth':>5} {'N':>4} {'fill_certain':>12} {'fill_touch':>10} {'below-FV(when filled)':>22}")
for cat in sorted(agg):
    for dpt in DEPTHS:
        a = agg[cat][dpt]
        if a["n"] == 0:
            continue
        fvs = f"{a['fv_good']}/{a['fv_n']} ({100*a['fv_good']/a['fv_n']:.0f}%)" if a["fv_n"] else "—"
        print(f"{cat:10s} {dpt:>5} {a['n']:>4} {a['fill_c']:>7} ({100*a['fill_c']/a['n']:.0f}%) "
              f"{a['fill_t']:>5} ({100*a['fill_t']/a['n']:.0f}%) {fvs:>22}")
print("\nALL-CATS by depth:")
for dpt in DEPTHS:
    n = sum(agg[c][dpt]["n"] for c in agg)
    fc = sum(agg[c][dpt]["fill_c"] for c in agg)
    ft = sum(agg[c][dpt]["fill_t"] for c in agg)
    fn = sum(agg[c][dpt]["fv_n"] for c in agg)
    fg = sum(agg[c][dpt]["fv_good"] for c in agg)
    print(f"  depth {dpt}: N={n} certain {fc} ({100*fc/n:.0f}%) touch {ft} ({100*ft/n:.0f}%) "
          f"below-FV {fg}/{fn} ({100*fg/fn:.0f}% of filled)" if n and fn else
          f"  depth {dpt}: N={n} certain {fc} touch {ft} (no FV data)")
json.dump(legs_out, open("/tmp/riser_depth_legs.json", "w"))
print("\nper-leg detail -> /tmp/riser_depth_legs.json")
