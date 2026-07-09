#!/usr/bin/env python3
"""VOLUME LEDGER + FLOW CALIBRATION (operator 07-08 night). READ-ONLY corpus.
Per pair (detected-bell universe, W1 = T-8h->bell):
  vol ledger: prints + contracts, W1 total + trailing states
  H-a FILL RATE | VOLUME: P(a print >=3c below current fillable arrives in
      the next 30min | trailing-30min print count band), per cat x cell zone
  H-b SPREAD STUBBORNNESS: spread level + P(tighten >=2c in 15min) vs
      prints/min band, per cat (fav leg quotes, ticks CSVs)
  recut_cells volume augmentation via seqfloor results join
Resume: results.jsonl. Heartbeat /root/volume_ledger_progress.json."""
import gzip, json, sqlite3, sys, time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path("/root/Omi-Workspace/arb-executor")
TRADES = ROOT / "analysis" / "trades"
TICKS = ROOT / "analysis" / "premarket_ticks"
OUT = Path("/root/volume_ledger_20260709")
OUT.mkdir(exist_ok=True)
RESULTS = OUT / "results.jsonl"
HEART = Path("/root/volume_ledger_progress.json")
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
    """per-minute: [n_prints, contracts, min_px]"""
    fh = open_any(TRADES / tk)
    if fh is None:
        return {}
    out = {}
    with fh:
        next(fh, None)
        for ln in fh:
            p = ln.rstrip("\n").split(",")
            if len(p) < 4:
                continue
            t = pts(p[0])
            if t is None or t < t0 or t > t1:
                continue
            try:
                px = int(p[2]); ct = float(p[3])
            except ValueError:
                continue
            m = int(t // 60) * 60
            r = out.setdefault(m, [0, 0.0, px])
            r[0] += 1; r[1] += ct
            if px < r[2]:
                r[2] = px
    return out

def load_spread(tk, t0, t1):
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
            if b > 0 and a > 0 and a > b:
                out[int(t // 60) * 60] = a - b
    return out

def zone(cell):
    if cell is None: return None
    return "<50" if cell < 50 else ("50-74" if cell < 75 else ("75-94" if cell < 95 else "OOB"))

def vband(n30):
    if n30 == 0: return "V0_dead"
    if n30 <= 5: return "V1_1-5"
    if n30 <= 15: return "V2_6-15"
    return "V3_16+"

def per_pair(ev, tks, bell):
    t0 = bell - W1
    minutes = list(range(int(t0 // 60) * 60, int(bell // 60) * 60, 60))
    tr = {tk: load_trades(tk, t0 - 1800, bell) for tk in tks}
    vol_w1 = sum(sum(v[1] for m, v in tr[tk].items() if m >= t0) for tk in tks)
    prints_w1 = sum(sum(v[0] for m, v in tr[tk].items() if m >= t0) for tk in tks)
    # fillable series per leg + close
    fill = {}
    for tk in tks:
        f = {}
        for m in minutes:
            vals = [tr[tk][k][2] for k in range(m - 14 * 60, m + 60, 60) if k in tr[tk]]
            if vals:
                f[m] = min(vals)
        fill[tk] = f
    closes = {tk: (fill[tk][max(fill[tk])] if fill[tk] else None) for tk in tks}
    # H-a: per minute state -> event
    ha = defaultdict(lambda: [0, 0])   # (zone, vband) -> [n, fills]
    for tk in tks:
        c = closes[tk]
        z = zone(c)
        if not z or z == "OOB":
            continue
        f = fill[tk]
        for i, m in enumerate(minutes[:-30]):
            if m not in f:
                continue
            n30 = sum(tr[tk2].get(k, [0])[0] for tk2 in tks
                      for k in range(m - 29 * 60, m + 60, 60))
            target = f[m] - 3
            hit = any(tr[tk].get(k, [0, 0, 999])[2] <= target
                      for k in range(m + 60, m + 31 * 60, 60))
            key = "%s|%s" % (z, vband(n30))
            ha[key][0] += 1
            ha[key][1] += int(hit)
    # H-b: fav-leg spread stubbornness
    fav = max(tks, key=lambda tk: closes[tk] or 0) if any(closes.values()) else tks[0]
    sp = load_spread(fav, t0, bell)
    hb = defaultdict(lambda: [0, 0, []])  # vband -> [n, tightened, spreads]
    for m in minutes[:-15]:
        if m not in sp:
            continue
        n30 = sum(tr[tk2].get(k, [0])[0] for tk2 in tks
                  for k in range(m - 29 * 60, m + 60, 60))
        fut = [sp[k] for k in range(m + 60, m + 16 * 60, 60) if k in sp]
        if not fut:
            continue
        key = vband(n30)
        hb[key][0] += 1
        hb[key][1] += int(min(fut) <= sp[m] - 2)
        if len(hb[key][2]) < 50:
            hb[key][2].append(sp[m])
    return {"ev": ev, "cat": cat_of(ev), "vol_w1": round(vol_w1, 1),
            "prints_w1": prints_w1,
            "closes": {tk[-3:]: closes[tk] for tk in tks},
            "ha": {k: v for k, v in ha.items()},
            "hb": {k: [v[0], v[1], sorted(v[2])[len(v[2]) // 2] if v[2] else None]
                   for k, v in hb.items()}}

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
        vols = sorted(r["vol_w1"] for r in rc)
        def p(v, q): return round(v[min(len(v) - 1, int(q * len(v)))], 1) if v else None
        ha = defaultdict(lambda: [0, 0]); hb = defaultdict(lambda: [0, 0, []])
        for r in rc:
            for k, v in r["ha"].items():
                ha[k][0] += v[0]; ha[k][1] += v[1]
            for k, v in r["hb"].items():
                hb[k][0] += v[0]; hb[k][1] += v[1]
                if v[2] is not None:
                    hb[k][2].append(v[2])
        agg["per_cat"][c] = {
            "n_pairs": len(rc),
            "vol_w1_dist": {"p10": p(vols, .1), "p25": p(vols, .25), "p50": p(vols, .5),
                            "p75": p(vols, .75), "p90": p(vols, .9)},
            "fill_given_volume": {k: {"n": v[0],
                                      "fill_pct": round(100 * v[1] / max(1, v[0]), 2)}
                                  for k, v in sorted(ha.items())},
            "spread_by_volume": {k: {"n": v[0],
                                     "tighten2_15m_pct": round(100 * v[1] / max(1, v[0]), 2),
                                     "spread_med_of_meds": (sorted(v[2])[len(v[2]) // 2]
                                                            if v[2] else None)}
                                 for k, v in sorted(hb.items())}}
    # recut_cells volume augmentation via seqfloor join
    try:
        vol_by_ev = {r["ev"]: r["vol_w1"] for r in rows}
        cellvol = defaultdict(list)
        for line in open("/root/seqfloor_20260708/results.jsonl", errors="replace"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("skip") or r["ev"] not in vol_by_ev:
                continue
            for side in ("fav", "dog"):
                cellvol["%s|%s" % (r["cat"], r[side + "_close"])].append(vol_by_ev[r["ev"]])
        recut = json.load(open(ROOT.parent / ".claude/seqfloor_20260708/recut_cells.json"))
        aug = {}
        for c, cells in recut.items():
            aug[c] = {}
            for cell, rec in cells.items():
                vs = sorted(cellvol.get("%s|%s" % (c, cell), []))
                rec = dict(rec)
                rec["vol_w1_med"] = vs[len(vs) // 2] if vs else None
                rec["n_vol"] = len(vs)
                rec["thin_tape"] = bool(vs and vs[len(vs) // 2] < 200)
                aug[c][cell] = rec
        json.dump(aug, open(OUT / "recut_cells_volume.json", "w"), indent=1)
        agg["recut_augmented"] = True
    except Exception as e:
        agg["recut_augmented"] = "ERR " + str(e)[:80]
    json.dump(agg, open(OUT / "aggregate.json", "w"), indent=1)
    print("AGGREGATE WRITTEN", flush=True)

def main():
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
