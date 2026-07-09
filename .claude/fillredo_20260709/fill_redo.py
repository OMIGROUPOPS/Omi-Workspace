#!/usr/bin/env python3
"""FILL RATE REDO (operator correction 07-09): spread-relative depths + traverse.
Depths per minute per leg: JOIN=bid, T1=bid-1, S1=floor(mid-spread), S2=floor(mid-2*spread).
Fill = a print <= depth within next 30 min; ttf recorded. Volume bands from
trailing-30m prints (both legs). Zones by leg's LAST QUOTED MID before bell.
TRAVERSE: touch-path stats + patient-join capture sim (downward-only ratchet
at touch-1, reset on fill; discount vs W1 close-mid). READ-ONLY corpus."""
import gzip, json, sys, time, random
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path("/root/Omi-Workspace/arb-executor")
TRADES = ROOT / "analysis" / "trades"
TICKS = ROOT / "analysis" / "premarket_ticks"
OUT = Path("/root/fill_redo_20260709")
OUT.mkdir(exist_ok=True)
RESULTS = OUT / "results.jsonl"
HEART = Path("/root/fill_redo_progress.json")
ET = timezone(timedelta(hours=-4))
W1 = 8 * 3600
CAT = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
       "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
       "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}
def cat_of(ev):
    for k, v in CAT.items():
        if ev.startswith(k):
            return v

_dc = {}
def pts(s):
    try:
        d, t, ap = s.split(" ")
        if d not in _dc:
            y, mo, dy = d.split("-")
            _dc[d] = datetime(int(y), int(mo), int(dy), tzinfo=ET).timestamp()
        hh, mm, ss = t.split(":")
        return _dc[d] + (int(hh) % 12 + (12 if ap == "PM" else 0)) * 3600 + int(mm) * 60 + int(ss)
    except Exception:
        return None

def open_any(base):
    for suf in (".csv", ".csv.gz"):
        f = base.parent / (base.name + suf)
        if f.exists():
            return (gzip.open if suf.endswith("gz") else open)(f, "rt",
                    encoding="utf-8", errors="replace")
    return None

def load_trades(tk, t0, t1):
    fh = open_any(TRADES / tk)
    if fh is None:
        return {}
    out = {}
    with fh:
        next(fh, None)
        for ln in fh:
            p = ln.rstrip("\n").split(",")
            if len(p) < 3:
                continue
            t = pts(p[0])
            if t is None or t < t0 or t > t1:
                continue
            try:
                px = int(p[2])
            except ValueError:
                continue
            m = int(t // 60) * 60
            r = out.setdefault(m, [0, px])
            r[0] += 1
            if px < r[1]:
                r[1] = px
    return out

def load_quotes(tk, t0, t1):
    fh = open_any(TICKS / tk)
    if fh is None:
        return {}
    out = {}
    with fh:
        next(fh, None)
        for ln in fh:
            p = ln.rstrip("\n").split(",")
            if len(p) < 13:
                continue
            t = pts(p[0])
            if t is None or t < t0 or t > t1:
                continue
            try:
                b = int(p[2]) if p[2] else 0
                a = int(p[12]) if p[12] else 0
            except ValueError:
                continue
            if 0 < b < a < 100:
                out[int(t // 60) * 60] = (b, a)
    return out

def zone(cell):
    if cell is None: return None
    return "<50" if cell < 50 else ("50-74" if cell < 75 else ("75-94" if cell < 95 else "OOB"))

def vband(n30):
    if n30 == 0: return "V0"
    if n30 <= 5: return "V1"
    if n30 <= 15: return "V2"
    return "V3"

DEPTHS = ["JOIN", "T1", "S1", "S2"]

def per_pair(ev, tks, bell):
    t0 = bell - W1
    minutes = list(range(int(t0 // 60) * 60, int(bell // 60) * 60, 60))
    tr = {tk: load_trades(tk, t0 - 1800, bell) for tk in tks}
    qt = {tk: load_quotes(tk, t0, bell) for tk in tks}
    rec = {"ev": ev, "cat": cat_of(ev), "legs": {}}
    grid = defaultdict(lambda: [0, 0, []])   # (zone|vband|depth) -> [n, fills, ttf_samples]
    for tk in tks:
        q = qt[tk]
        if not q:
            continue
        last_m = max(q)
        close_mid = (q[last_m][0] + q[last_m][1]) / 2.0
        z = zone(close_mid)
        if not z or z == "OOB":
            z = zone(min(close_mid, 94))
        # PART 1: grid sampling (every 3rd minute to bound cost; unbiased)
        for m in minutes[:-30:3]:
            if m not in q:
                continue
            b, a = q[m]
            mid = (b + a) / 2.0
            sp = a - b
            n30 = sum(tr[t2].get(k, [0])[0] for t2 in tks
                      for k in range(m - 29 * 60, m + 60, 60))
            vb = vband(n30)
            levels = {"JOIN": b, "T1": b - 1,
                      "S1": max(1, int(mid - sp)), "S2": max(1, int(mid - 2 * sp))}
            # forward running-min scan once
            run = 999
            hit = {d: None for d in DEPTHS}
            for i in range(1, 31):
                mm = m + i * 60
                v = tr[tk].get(mm)
                if v and v[1] < run:
                    run = v[1]
                for d in DEPTHS:
                    if hit[d] is None and run <= levels[d]:
                        hit[d] = i
                if all(h is not None for h in hit.values()):
                    break
            for d in DEPTHS:
                key = "%s|%s|%s" % (z, vb, d)
                g = grid[key]
                g[0] += 1
                if hit[d] is not None:
                    g[1] += 1
                    if len(g[2]) < 60 and random.random() < 0.3:
                        g[2].append(hit[d])
        # PART 2: touch-path + patient-join sim
        bids = [(m, q[m][0]) for m in minutes if m in q]
        if len(bids) < 10:
            continue
        bvals = [b for _, b in bids]
        path_range = max(bvals) - min(bvals)
        net = bvals[-1] - bvals[0]
        pvol = sum(abs(bvals[i] - bvals[i - 1]) for i in range(1, len(bids)))
        level = bids[0][1] - 1
        fills = []
        for m, b in bids:
            level = min(level, b - 1)
            if level < 1:
                level = 1
            v = tr[tk].get(m)
            if v and v[1] <= level:
                fills.append(level)
                level = b - 1
        discounts = [round(close_mid - p, 1) for p in fills]
        rec["legs"][tk[-3:]] = {"zone": z, "close_mid": close_mid,
                                "range": path_range, "net": net, "pvol": pvol,
                                "n_joinfills": len(fills),
                                "disc_med": (sorted(discounts)[len(discounts) // 2]
                                             if discounts else None),
                                "disc_total": round(sum(discounts), 1)}
    rec["grid"] = {k: [v[0], v[1], (sorted(v[2])[len(v[2]) // 2] if v[2] else None)]
                   for k, v in grid.items()}
    return rec

def build_universe():
    bells = {}
    for f in sorted((ROOT / "data" / "shape_corpus").glob("samples_*.jsonl")):
        for line in open(f, encoding="utf-8", errors="replace"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            tk, b = d.get("tk", ""), d.get("bell")
            if tk and b:
                bells[tk.rsplit("-", 1)[0]] = int(b)
    legs = defaultdict(set)
    for f in TRADES.glob("*.csv*"):
        tk = f.name.replace(".csv.gz", "").replace(".csv", "")
        legs[tk.rsplit("-", 1)[0]].add(tk)
    return sorted((ev, sorted(t)) for ev, t in legs.items()
                  if len(t) == 2 and ev in bells and cat_of(ev)), bells

def aggregate():
    rows = []
    for line in open(RESULTS, encoding="utf-8", errors="replace"):
        try:
            r = json.loads(line)
            if not r.get("skip"):
                rows.append(r)
        except Exception:
            pass
    agg = {"n": len(rows), "per_cat": {}}
    for c in sorted({r["cat"] for r in rows}):
        rc = [r for r in rows if r["cat"] == c]
        grid = defaultdict(lambda: [0, 0, []])
        trav = defaultdict(lambda: {"range": [], "net": [], "pvol": [],
                                    "nfills": [], "disc": [], "tot": []})
        for r in rc:
            for k, v in r.get("grid", {}).items():
                g = grid[k]
                g[0] += v[0]; g[1] += v[1]
                if v[2] is not None:
                    g[2].append(v[2])
            for leg in r.get("legs", {}).values():
                t = trav[leg["zone"]]
                t["range"].append(leg["range"]); t["net"].append(leg["net"])
                t["pvol"].append(leg["pvol"]); t["nfills"].append(leg["n_joinfills"])
                if leg["disc_med"] is not None:
                    t["disc"].append(leg["disc_med"])
                t["tot"].append(leg["disc_total"])
        def med(v): return sorted(v)[len(v) // 2] if v else None
        def p75(v): return sorted(v)[int(.75 * len(v))] if v else None
        agg["per_cat"][c] = {
            "n_pairs": len(rc),
            "grid": {k: {"n": v[0], "fill_pct": round(100 * v[1] / max(1, v[0]), 2),
                         "ttf_med_min": med(v[2])} for k, v in sorted(grid.items())},
            "traverse": {z: {"n_legs": len(t["range"]),
                             "range_med": med(t["range"]), "net_med": med(t["net"]),
                             "pathvol_med": med(t["pvol"]),
                             "joinfills_med": med(t["nfills"]),
                             "joinfills_p75": p75(t["nfills"]),
                             "disc_per_fill_med": med(t["disc"]),
                             "capture_total_med": med(t["tot"]),
                             "capture_total_p75": p75(t["tot"])}
                         for z, t in sorted(trav.items())}}
    json.dump(agg, open(OUT / "aggregate.json", "w"), indent=1)
    print("AGGREGATE WRITTEN", flush=True)

def main():
    random.seed(20260709)
    pairs, bells = build_universe()
    done = set()
    if RESULTS.exists():
        for line in open(RESULTS, encoding="utf-8", errors="replace"):
            try:
                done.add(json.loads(line)["ev"])
            except Exception:
                pass
    total = len(pairs)
    print("UNIVERSE", total, "resumed", len(done), flush=True)
    if "--aggregate-only" not in sys.argv:
        with open(RESULTS, "a", encoding="utf-8") as out:
            for i, (ev, tks) in enumerate(pairs):
                if ev in done:
                    continue
                try:
                    rec = per_pair(ev, tks, bells[ev])
                except Exception as e:
                    rec = {"ev": ev, "skip": str(e)[:80]}
                out.write(json.dumps(rec) + "\n")
                out.flush()
                if i % 50 == 0:
                    json.dump({"ts": time.time(), "done": i, "total": total},
                              open(HEART, "w"))
    aggregate()
    (OUT / "DONE").write_text(datetime.now(ET).isoformat())

if __name__ == "__main__":
    main()
