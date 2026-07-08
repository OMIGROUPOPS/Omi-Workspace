#!/usr/bin/env python3
"""BELL RECOVERY 2026-07-08 (SEND-ORDER #3). READ-ONLY corpus.
Re-detect the missed-bell class with the LATCH-EQUIVALENT taker signature --
the exact flow definition the certified gun trusts (live_v4 constants):
  stage-1: >=10 prints across both legs in any rolling 60s window
  stage-2 (the bell): a second qualifying window >=60s and <=300s after
  stage-1 (sustained flow, two non-overlapping windows). First satisfaction.
Overlap validation: events WITH corpus bells get the detector too; residual
= detected - corpus bell. Recovered no-bell matches: report + W1-close cells
(AIM_V2 coverage delta). Resume: results.jsonl. Detached + watcher pattern.
"""
import gzip, json, sqlite3, sys, time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path("/root/Omi-Workspace/arb-executor")
TRADES = ROOT / "analysis" / "trades"
OUT = Path("/root/bell_recovery_20260708")
OUT.mkdir(exist_ok=True)
RESULTS = OUT / "results.jsonl"
HEART = Path("/root/bell_recovery_progress.json")
ET = timezone(timedelta(hours=-4))
BURST, WIN, GAP_MIN, TTL = 10, 60, 60, 300
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


def load_print_times_prices(tk):
    fh = open_any(TRADES / tk)
    if fh is None:
        return []
    out = []
    with fh:
        next(fh, None)
        for ln in fh:
            p = ln.rstrip("\n").split(",")
            if len(p) < 3:
                continue
            t = pts(p[0])
            if t is None:
                continue
            try:
                out.append((t, int(p[2])))
            except ValueError:
                continue
    return out


def detect_bell(times):
    """Latch-equivalent two-stage on a sorted merged print-time list."""
    n = len(times)
    if n < BURST:
        return None, 0
    # windows that qualify: for each print i, count prints in (t_i-60, t_i]
    qual = []
    j = 0
    for i in range(n):
        while times[i] - times[j] > WIN:
            j += 1
        if i - j + 1 >= BURST:
            qual.append(times[i])
    if not qual:
        return None, len(qual)
    stage1 = qual[0]
    for t in qual:
        if t - stage1 >= GAP_MIN and t - stage1 <= TTL:
            return t, len(qual)     # the bell = stage-2 confirm
        if t - stage1 > TTL:
            stage1 = t              # stage-1 evidence expired; re-arm
    return None, len(qual)


def fillable_close(prints, t0, t1):
    """last trailing-15min-min fillable read in [t0,t1] (W1-close convention)."""
    per_min = {}
    for t, px in prints:
        if t0 <= t <= t1:
            m = int(t // 60) * 60
            if m not in per_min or px < per_min[m]:
                per_min[m] = px
    if not per_min:
        return None
    last = max(per_min)
    vals = [per_min[k] for k in range(last - 14 * 60, last + 60, 60) if k in per_min]
    return min(vals) if vals else None


def main():
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
    universe = [(ev, sorted(tks)) for ev, tks in legs.items()
                if len(tks) == 2 and cat_of(ev)]
    done = set()
    if RESULTS.exists():
        for line in open(RESULTS, encoding="utf-8", errors="replace"):
            try:
                done.add(json.loads(line)["ev"])
            except Exception:
                pass
    total = len(universe)
    print("UNIVERSE", json.dumps({"events_2leg": total,
                                  "with_corpus_bell": sum(1 for e, _ in universe if e in bells),
                                  "resumed": len(done)}), flush=True)
    if "--aggregate-only" not in sys.argv:
        with open(RESULTS, "a", encoding="utf-8") as out:
            for i, (ev, tks) in enumerate(universe):
                if ev in done:
                    continue
                try:
                    pr = []
                    per_leg = {}
                    for tk in tks:
                        pp = load_print_times_prices(tk)
                        per_leg[tk] = pp
                        pr.extend(t for t, _ in pp)
                    pr.sort()
                    det, nq = detect_bell(pr)
                    rec = {"ev": ev, "cat": cat_of(ev), "n_prints": len(pr),
                           "corpus_bell": bells.get(ev), "detected": det,
                           "n_qual_windows": nq}
                    if det:
                        for tk in tks:
                            fc = fillable_close(per_leg[tk], det - 8 * 3600, det)
                            rec["close_" + tk[-3:]] = fc
                except Exception as e:
                    rec = {"ev": ev, "skip": "error:" + str(e)[:100]}
                out.write(json.dumps(rec) + "\n")
                out.flush()
                if i % 100 == 0:
                    json.dump({"ts": time.time(), "done": i, "total": total},
                              open(HEART, "w"))
    # aggregate
    rows = [json.loads(l) for l in open(RESULTS, encoding="utf-8", errors="replace")]
    rows = [r for r in rows if not r.get("skip")]
    overlap = [r for r in rows if r["corpus_bell"] and r["detected"]]
    deltas = sorted((r["detected"] - r["corpus_bell"]) / 60.0 for r in overlap)
    def pct(v, q):
        return round(v[min(len(v) - 1, int(q * len(v)))], 1) if v else None
    nobell = [r for r in rows if not r["corpus_bell"]]
    recovered = [r for r in nobell if r["detected"]]
    cover = defaultdict(int)
    for r in recovered:
        for k, v in r.items():
            if k.startswith("close_") and v is not None:
                cover["%s|%d" % (r["cat"], v)] += 1
    agg = {"n_events": len(rows),
           "overlap_validated": {"n": len(overlap),
                                 "delta_min_p10": pct(deltas, .1),
                                 "p25": pct(deltas, .25), "p50": pct(deltas, .5),
                                 "p75": pct(deltas, .75), "p90": pct(deltas, .9),
                                 "within_5min_pct": round(100 * sum(1 for d in deltas if abs(d) <= 5) / max(1, len(deltas)), 1),
                                 "corpus_bell_missed_by_detector": sum(1 for r in rows if r["corpus_bell"] and not r["detected"])},
           "no_bell_class": {"n": len(nobell), "recovered": len(recovered),
                             "recovery_pct": round(100 * len(recovered) / max(1, len(nobell)), 1),
                             "per_cat": {c: [sum(1 for r in nobell if r["cat"] == c),
                                             sum(1 for r in recovered if r["cat"] == c)]
                                         for c in sorted({r["cat"] for r in nobell})}},
           "aimv2_cell_coverage_delta": {"n_new_legs": sum(cover.values()),
                                         "n_cells_touched": len(cover),
                                         "top_cells": dict(sorted(cover.items(), key=lambda x: -x[1])[:40])}}
    json.dump(agg, open(OUT / "aggregate.json", "w"), indent=1)
    print("AGGREGATE WRITTEN", flush=True)
    (OUT / "DONE").write_text(datetime.now(ET).isoformat())


if __name__ == "__main__":
    main()
