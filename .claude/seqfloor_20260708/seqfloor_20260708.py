#!/usr/bin/env python3
"""SEQUENTIAL FLOOR 2026-07-08 (SEND-ORDER #2). READ-ONLY corpus. ENTRY ONLY.

Per detected-bell pair, per leg, W1 (T-8h -> bell), prints-only fillable
convention (min print in trailing 15 min -- pair_story unchanged):
  leg edge = W1-CLOSING fillable (last read before the bell)
             - deepest fillable in W1 (at ITS OWN time)
  sequential pair edge = fav edge + dog edge (independent times)
  implied entry combined = deepest_fav + deepest_dog
  vs the SIMULTANEOUS joint floor (pair_story lens): min_t(fav(t)+dog(t))
NO settlement columns anywhere. Bells: shape_corpus (LATCH-CAL) upgraded by
observed_starts (same as early_canvas_20260708). Resume: results.jsonl.
"""
import gzip, json, sqlite3, sys, time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path("/root/Omi-Workspace/arb-executor")
TRADES = ROOT / "analysis" / "trades"
OUT = Path("/root/seqfloor_20260708")
OUT.mkdir(exist_ok=True)
RESULTS = OUT / "results.jsonl"
HEART = Path("/root/seqfloor_progress.json")
ET = timezone(timedelta(hours=-4))
W1_S = 8 * 3600
CAT = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
       "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
       "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}


def cat_of(ev):
    for k, v in CAT.items():
        if ev.startswith(k):
            return v
    return None


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


def load_min_prints(tk, t0, t1):
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
            if m not in out or px < out[m]:
                out[m] = px
    return out


def fillable(minprints, minutes, trail=15):
    """fillable(t) = min print across trailing `trail` minutes; None if quiet."""
    out = {}
    for m in minutes:
        vals = [minprints[k] for k in range(m - (trail - 1) * 60, m + 60, 60)
                if k in minprints]
        if vals:
            out[m] = min(vals)
    return out


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
    obs = 0
    try:
        con = sqlite3.connect("file:%s?mode=ro" % (ROOT / "tennis.db"),
                              uri=True, timeout=3)
        for suf, ts in con.execute(
                "SELECT kalshi_ticker, first_inplay_at FROM observed_starts"):
            try:
                oe = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=timezone.utc).timestamp()
            except Exception:
                continue
            hits = [ev for ev in bells
                    if ev.endswith(suf) and abs(bells[ev] - oe) < 6 * 3600]
            if len(hits) == 1:
                bells[hits[0]] = int(oe)
                obs += 1
        con.close()
    except Exception:
        pass
    legs = defaultdict(list)
    for f in TRADES.glob("*.csv*"):
        tk = f.name.replace(".csv.gz", "").replace(".csv", "")
        legs[tk.rsplit("-", 1)[0]].append(tk)
    pairs = [(ev, sorted(set(tks))) for ev, tks in legs.items()
             if len(set(tks)) == 2 and ev in bells and cat_of(ev)]
    return sorted(pairs), bells, obs


def per_pair(ev, tks, bell):
    t0 = bell - W1_S
    minutes = list(range(int(t0 // 60) * 60, int(bell // 60) * 60, 60))
    series = {}
    for tk in tks:
        series[tk] = fillable(load_min_prints(tk, t0 - 15 * 60, bell), minutes)
    a, b = tks
    fa, fb = series[a], series[b]
    if not fa or not fb:
        return {"ev": ev, "skip": "no_w1_fillable_%d" % (bool(fa) + bool(fb))}
    ca, cb = fa[max(fa)], fb[max(fb)]           # W1-closing fillable
    fav, dog = (a, b) if ca >= cb else (b, a)
    fv, dv = series[fav], series[dog]
    f_close, d_close = fv[max(fv)], dv[max(dv)]
    f_deep = min(fv.values()); d_deep = min(dv.values())
    tf = min(m for m, v in fv.items() if v == f_deep)
    td = min(m for m, v in dv.items() if v == d_deep)
    joint = [fv[m] + dv[m] for m in fv if m in dv]
    return {"ev": ev, "cat": cat_of(ev), "fav": fav[-3:], "dog": dog[-3:],
            "fav_close": f_close, "dog_close": d_close,
            "fav_deep": f_deep, "dog_deep": d_deep,
            "fav_edge": f_close - f_deep, "dog_edge": d_close - d_deep,
            "pair_edge": (f_close - f_deep) + (d_close - d_deep),
            "implied_combined": f_deep + d_deep,
            "closing_combined": f_close + d_close,
            "joint_min": (min(joint) if joint else None),
            "n_co_minutes": len(joint),
            "t_fav_deep_min_to_bell": round((tf - bell) / 60),
            "t_dog_deep_min_to_bell": round((td - bell) / 60),
            "gap_min": round(abs(tf - td) / 60),
            "first_dipper": ("fav" if tf < td else ("dog" if td < tf else "tie"))}


def dist(v):
    v = sorted(x for x in v if x is not None)
    if not v:
        return None
    def p(q):
        return round(v[min(len(v) - 1, int(q * len(v)))], 1)
    return {"n": len(v), "p10": p(.1), "p25": p(.25), "p50": p(.5), "p75": p(.75)}


def bucket(fc):
    if fc < 60: return "<60"
    if fc < 70: return "60-70"
    if fc < 80: return "70-80"
    if fc < 90: return "80-90"
    return "90+"


def aggregate():
    ok, skips = [], defaultdict(int)
    for line in open(RESULTS, encoding="utf-8", errors="replace"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("skip"):
            skips[r["skip"].rsplit("_", 1)[0]] += 1
        else:
            ok.append(r)
    agg = {"n_ok": len(ok), "skips": dict(skips), "per_cat": {}, "per_bucket": {}}
    def block(rows):
        pe = [r["pair_edge"] for r in rows]
        prem = [r["joint_min"] - r["implied_combined"] for r in rows
                if r["joint_min"] is not None]
        return {
            "n": len(rows),
            "fav_edge": dist([r["fav_edge"] for r in rows]),
            "dog_edge": dist([r["dog_edge"] for r in rows]),
            "pair_edge": dist(pe),
            "implied_combined": dist([r["implied_combined"] for r in rows]),
            "closing_combined": dist([r["closing_combined"] for r in rows]),
            "joint_min_simultaneous": dist([r["joint_min"] for r in rows]),
            "doctrine_premium": dist(prem),
            "n_seq_only_no_cominute": sum(1 for r in rows if r["joint_min"] is None),
            "pct_edge_ge": {str(k): round(100 * sum(1 for e in pe if e >= k)
                                          / max(1, len(pe)), 1)
                            for k in (3, 5, 8, 12)},
            "gap_min": dist([r["gap_min"] for r in rows]),
            "fav_first_pct": round(100 * sum(1 for r in rows
                                             if r["first_dipper"] == "fav")
                                   / max(1, len(rows)), 1),
            "t_fav_deep": dist([r["t_fav_deep_min_to_bell"] for r in rows]),
            "t_dog_deep": dist([r["t_dog_deep_min_to_bell"] for r in rows]),
        }
    for c in sorted({r["cat"] for r in ok}):
        rows = [r for r in ok if r["cat"] == c]
        agg["per_cat"][c] = block(rows)
        for bk in ("<60", "60-70", "70-80", "80-90", "90+"):
            br = [r for r in rows if bucket(r["fav_close"]) == bk]
            if br:
                agg["per_bucket"]["%s|%s" % (c, bk)] = block(br)
    json.dump(agg, open(OUT / "aggregate.json", "w"), indent=1)
    print("AGGREGATE WRITTEN", flush=True)


def main():
    pairs, bells, obs = build_universe()
    done = set()
    if RESULTS.exists():
        for line in open(RESULTS, encoding="utf-8", errors="replace"):
            try:
                done.add(json.loads(line)["ev"])
            except Exception:
                pass
    total = len(pairs)
    print("UNIVERSE", json.dumps({"pairs": total, "observed_used": obs,
                                  "resumed": len(done)}), flush=True)
    if "--aggregate-only" not in sys.argv:
        with open(RESULTS, "a", encoding="utf-8") as out:
            for i, (ev, tks) in enumerate(pairs):
                if ev in done:
                    continue
                try:
                    rec = per_pair(ev, tks, bells[ev])
                except Exception as e:
                    rec = {"ev": ev, "skip": "error:" + str(e)[:100]}
                out.write(json.dumps(rec) + "\n")
                out.flush()
                if i % 50 == 0:
                    json.dump({"ts": time.time(), "done": i, "total": total},
                              open(HEART, "w"))
    aggregate()
    (OUT / "DONE").write_text(datetime.now(ET).isoformat())


if __name__ == "__main__":
    main()
